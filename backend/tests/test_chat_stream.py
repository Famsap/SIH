"""Tests for the SSE streaming chat endpoint (/api/chat/stream).

These tests never hit the network: retrieval and generation are patched
so the SSE framing/event contract is verified in isolation.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import sse_starlette.sse as sse_module
from app.main import app

tc = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_sse_app_status():
    """Reset sse-starlette's module-global exit event between requests.

    `AppStatus.should_exit_event` is a process-global anyio.Event bound to the
    event loop that created it.  TestClient may serve each request on a fresh
    loop, so leaving the global set leaks a loop-bound event into later tests
    ("bound to a different event loop").  Production uvicorn uses one loop for
    the app lifetime, so this is only a test-harness concern.
    """
    sse_module.AppStatus.should_exit = False
    sse_module.AppStatus.should_exit_event = None
    yield
    sse_module.AppStatus.should_exit = False
    sse_module.AppStatus.should_exit_event = None


def _parse_events(body: str) -> list[dict]:
    """Parse `event:`/`data:` SSE blocks into (event, payload) dicts.

    Normalises CRLF so the parser is robust to whichever framing the SSE
    library emits under TestClient.
    """
    events: list[dict] = []
    for block in body.replace("\r\n", "\n").split("\n\n"):
        event, data = "message", ""
        for line in block.splitlines():
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                data += line[5:].strip()
        if data:
            events.append({"event": event, "data": json.loads(data)})
    return events


class TestStreamEndpoint:

    def test_stream_returns_event_stream_content_type(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.endpoints.stream.retrieve_relevant_chunks",
            lambda q: ([], False),
        )
        resp = tc.post(
            "/api/chat/stream", json={"question": "hello", "history": []}
        )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")
        # Consume the full body so the SSE background task finalises cleanly
        # (abandoning an open stream leaks a heartbeat task into later tests).
        events = _parse_events(resp.text)
        assert len(events) >= 2

    def test_gate_failure_streams_refusal_then_done(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.endpoints.stream.retrieve_relevant_chunks",
            lambda q: ([], False),
        )
        resp = tc.post(
            "/api/chat/stream", json={"question": "hello", "history": []}
        )
        events = _parse_events(resp.text)
        messages = [e for e in events if e["event"] == "message"]
        done = [e for e in events if e["event"] == "done"]

        assert resp.status_code == 200
        assert messages, "expected at least one message event"
        assert messages[-1]["data"]["type"] == "message"
        assert len(done) == 1, "expected exactly one done event"
        done_payload = done[0]["data"]
        assert done_payload["type"] == "done"
        assert done_payload["gated"] is True
        assert done_payload["grounded"] is False
        assert done_payload["source"] == "none"
        assert done_payload["citations"] == []
        assert messages and done_payload["response"] == messages[-1]["data"]["content"]

    def test_stream_emits_incremental_tokens_and_done_payload(self, monkeypatch):
        async def fake_stream(query, chunks, gate_passed, history=None):
            yield {"type": "message", "content": "Hel"}
            yield {"type": "message", "content": "lo"}
            yield {
                "type": "done",
                "query": query,
                "response": "Hello",
                "citations": [],
                "grounded": True,
                "source": "groq",
                "gated": False,
            }

        monkeypatch.setattr(
            "app.api.v1.endpoints.stream.retrieve_relevant_chunks",
            lambda q: ([object()], True),
        )
        monkeypatch.setattr(
            "app.api.v1.endpoints.stream.stream_answer", fake_stream
        )
        resp = tc.post(
            "/api/chat/stream", json={"question": "hi", "history": []}
        )
        events = _parse_events(resp.text)
        tokens = [
            e["data"]["content"]
            for e in events
            if e["event"] == "message" and e["data"].get("type") == "message"
        ]
        done = [e for e in events if e["event"] == "done"]

        assert resp.status_code == 200
        assert tokens == ["Hel", "lo"], f"unexpected token order: {tokens}"
        assert len(done) == 1
        assert done[0]["data"]["response"] == "Hello"
        assert done[0]["data"]["grounded"] is True
        assert done[0]["data"]["source"] == "groq"

    def test_validation_rejects_empty_question(self):
        resp = tc.post(
            "/api/chat/stream",
            json={"question": "", "history": []},
        )
        assert resp.status_code == 422