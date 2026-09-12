"""Hermetic tests for provider streaming: Groq retry + Groq -> Ollama fallback.

No network access: ``httpx.AsyncClient`` (and ``asyncio.sleep``) are replaced
with fakes that mimic the Groq / Ollama wire protocols, and the Groq API key
is stubbed to a test value so the tests are deterministic in any environment.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import httpx
import pytest

import app.rag.generate as gen


def _groq_data_line(text: str) -> str:
    return f'data: {{"choices": [{{"delta": {{"content": "{text}"}}}}]}}'


class _FakeStream:
    """Async-context response returned from ``FakeStreamClient.stream()``."""

    def __init__(self, *, status: int = 200, lines: list | None = None, raise_on_open: Exception | None = None):
        self.status = status
        self._lines = lines or []
        self._raise_on_open = raise_on_open

    def raise_for_status(self) -> None:
        if self._raise_on_open is not None:
            raise self._raise_on_open
        if self.status >= 400:
            req = httpx.Request("POST", "https://llm.example/fake")
            raise httpx.HTTPStatusError(
                f"HTTP {self.status}",
                request=req,
                response=httpx.Response(self.status, request=req),
            )

    async def __aenter__(self) -> "_FakeStream":
        return self

    async def __aexit__(self, *exc) -> bool:
        return False

    async def aiter_lines(self):
        for line in self._lines:
            if isinstance(line, Exception):
                raise line
            yield line


class FakeStreamClient:
    """Drop-in for ``httpx.AsyncClient`` — one scripted response per attempt.

    Each ``_stream_*`` try creates a new client instance, so the instance
    counter doubles as the retry-attempt index.
    """

    instances_created = 0
    script: list[_FakeStream] = []

    def __init__(self, *args, **kwargs):
        FakeStreamClient.instances_created += 1
        self.attempt = FakeStreamClient.instances_created - 1

    async def __aenter__(self) -> "FakeStreamClient":
        return self

    async def __aexit__(self, *exc) -> bool:
        return False

    def stream(self, method: str, url: str, **kwargs) -> _FakeStream:
        script = FakeStreamClient.script
        return script[self.attempt] if self.attempt < len(script) else script[-1]


def _patch_httpx(monkeypatch: pytest.MonkeyPatch, script: list[_FakeStream]) -> list[float]:
    """Point ``httpx.AsyncClient`` at the fake, stub the key, record backoff sleeps."""
    monkeypatch.setattr(FakeStreamClient, "script", script)
    monkeypatch.setattr(FakeStreamClient, "instances_created", 0)
    monkeypatch.setattr(gen.httpx, "AsyncClient", FakeStreamClient)
    monkeypatch.setattr(gen, "GROQ_API_KEY", "test-key")

    sleeps: list[float] = []

    async def _fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(gen.asyncio, "sleep", _fake_sleep)
    return sleeps


def _chunk(text: str = "Hallmarking is regulated under the BIS Act.", standard: str = "IS 1417", clause: str = "2.7"):
    return SimpleNamespace(
        chunk_id="c1",
        text=text,
        distance=0.1,
        is_valid=True,
        metadata={
            "source_file": "bis-docs/hallmarking.txt",
            "standard_number": standard,
            "clause_section": clause,
            "page_number": 3,
            "url": "",
        },
    )


async def _collect(agen):
    return [item async for item in agen]


def _collect_run(agen) -> list:
    return asyncio.run(_collect(agen))


def _message_events(events) -> list[dict]:
    return [e for e in events if e["type"] == "message"]


# ---------------------------------------------------------------------------
# Groq retry semantics
# ---------------------------------------------------------------------------


def test_groq_rate_limit_retried_before_first_token(monkeypatch: pytest.MonkeyPatch):
    script = [
        _FakeStream(status=429),
        _FakeStream(lines=[_groq_data_line("hel"), _groq_data_line("lo"), "data: [DONE]"]),
    ]
    sleeps = _patch_httpx(monkeypatch, script)
    monkeypatch.setattr(gen, "GROQ_STREAM_RETRIES", 2)

    tokens = _collect_run(gen._stream_groq("q"))

    assert tokens == ["hel", "lo"]
    assert FakeStreamClient.instances_created == 2
    assert sleeps == [1.0]  # GROQ_RETRY_BACKOFF_SECONDS * (attempt + 1)


def test_groq_auth_failure_not_retried(monkeypatch: pytest.MonkeyPatch):
    _patch_httpx(monkeypatch, [_FakeStream(status=401)])
    monkeypatch.setattr(gen, "GROQ_STREAM_RETRIES", 3)

    with pytest.raises(httpx.HTTPStatusError):
        _collect_run(gen._stream_groq("q"))

    assert FakeStreamClient.instances_created == 1


def test_groq_mid_stream_failure_not_retried(monkeypatch: pytest.MonkeyPatch):
    # First token arrives, then the connection drops: retrying would duplicate
    # "hel", so the error must propagate without another attempt.
    script = [_FakeStream(lines=[_groq_data_line("hel"), httpx.RemoteProtocolError("stream died")])]
    _patch_httpx(monkeypatch, script)
    monkeypatch.setattr(gen, "GROQ_STREAM_RETRIES", 3)

    with pytest.raises(httpx.RemoteProtocolError):
        _collect_run(gen._stream_groq("q"))

    assert FakeStreamClient.instances_created == 1


# ---------------------------------------------------------------------------
# stream_answer dispatch / fallback semantics
# ---------------------------------------------------------------------------


def test_groq_empty_completion_falls_back_to_ollama(monkeypatch: pytest.MonkeyPatch):
    _patch_httpx(monkeypatch, [_FakeStream(lines=["data: [DONE]"])])
    monkeypatch.setattr(gen, "GROQ_STREAM_RETRIES", 2)

    async def fake_ollama(prompt, system_prompt=None):
        yield "of"
        yield "fline"

    monkeypatch.setattr(gen, "_stream_ollama", fake_ollama)

    events = _collect_run(gen.stream_answer("q", [_chunk()], gate_passed=True))
    done = events[-1]

    assert [e["content"] for e in _message_events(events)] == ["of", "fline"]
    assert done["source"] == "ollama"
    assert done["response"] == "offline"
    assert done["grounded"] is True


def test_mid_stream_groq_failure_surfaces_partial_text(monkeypatch: pytest.MonkeyPatch):
    _patch_httpx(monkeypatch, [_FakeStream(lines=[_groq_data_line("hel"), httpx.RemoteProtocolError("died")])])
    monkeypatch.setattr(gen, "GROQ_STREAM_RETRIES", 2)

    async def fake_ollama(prompt, system_prompt=None):
        yield "NEVER"

    monkeypatch.setattr(gen, "_stream_ollama", fake_ollama)

    events = _collect_run(gen.stream_answer("q", [_chunk()], gate_passed=True))
    done = events[-1]

    assert [e["content"] for e in _message_events(events)] == ["hel"]
    assert done["source"] == "groq"
    assert done["response"] == "hel"
    assert done["grounded"] is True


def test_all_providers_fail_degrades_to_refusal(monkeypatch: pytest.MonkeyPatch):
    _patch_httpx(monkeypatch, [_FakeStream(status=429), _FakeStream(status=429)])
    monkeypatch.setattr(gen, "GROQ_STREAM_RETRIES", 2)

    async def fake_ollama(prompt, system_prompt=None):
        if False:  # keep the function an async generator (has a yield site)
            yield "never"
        raise RuntimeError("ollama down")

    monkeypatch.setattr(gen, "_stream_ollama", fake_ollama)

    events = _collect_run(gen.stream_answer("q", [_chunk()], gate_passed=True))
    done = events[-1]

    assert _message_events(events) == []
    assert done["response"] == gen.REFUSAL_MESSAGE
    assert done["source"] == "unavailable"
    assert done["grounded"] is False


def test_ollama_streams_tokens(monkeypatch: pytest.MonkeyPatch):
    _patch_httpx(
        monkeypatch,
        [
            _FakeStream(
                lines=[
                    '{"response": "t1", "done": false}',
                    '{"response": "t2", "done": true}',
                ]
            )
        ],
    )

    tokens = _collect_run(gen._stream_ollama("q"))

    assert tokens == ["t1", "t2"]