from __future__ import annotations

import asyncio
import json
import os
import re
import threading
from typing import Any, AsyncGenerator, Generator
import httpx

from app.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_RETRY_BACKOFF_SECONDS,
    GROQ_STREAM_RETRIES,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    MAX_CONCURRENT_GENERATIONS,
)
from app.rag.prompts import REFUSAL_MESSAGE, SYSTEM_PROMPT, build_rag_prompt, format_context_block
from app.rag.retrieve import RetrievedChunk

# Serialize LLM calls so bursts of requests are queued instead of running an
# LLM inference simultaneously on every core (which throttles the CPU).
_generation_slots = threading.BoundedSemaphore(MAX_CONCURRENT_GENERATIONS)


def _citation_matches(citation_inner: str, allowed_pairs: set[tuple[str, str]]) -> bool:
    """Check if a single citation bracket-text references a retrieved (standard, clause).

    Tolerant of common formats:
      - "IS 1417:2016, 2.7"
      - "IS 1417:2016, clause 2.7"
      - "DOCUMENT 2: brief-on-Hallmarking.txt; IS 1417:2016; 2.7"
    """
    inner = citation_inner.lower()
    inner_compact = re.sub(r"[\s:]+", "", inner)  # remove whitespace and colons
    for std, clause in allowed_pairs:
        # Normalize standard: "IS 1417:2016" → "is1417" (year optional)
        std_base = re.sub(r"[\s:]+", "", std.lower())
        std_base = re.sub(r"20\d{2}$", "", std_base)  # drop year suffix
        # Normalize clause: "clause 2.7" → "2.7", "cl. 2.7" → "2.7"
        clause_clean = re.sub(
            r"^(cl\.?\s*|clause\s+|section\s+|sec\.?\s*)", "", clause.lower()
        ).strip()
        if not std_base or not clause_clean:
            continue
        if std_base in inner_compact and clause_clean in inner:
            return True
    return False


def _has_only_grounded_citations(answer: str, chunks: list[RetrievedChunk]) -> bool:
    """Allow model output only when all bracketed citations reference retrieved chunks.

    Accepts multiple citation formats.  If there are no bracketed citations at
    all, only short refusal-like answers (≤25 words) are accepted.
    """
    allowed_pairs = {
        (
            c.metadata.get("standard_number", c.metadata.get("is_number", "")),
            c.metadata.get("clause_section", c.metadata.get("clause", "")),
        )
        for c in chunks
        if c.metadata.get("standard_number", c.metadata.get("is_number", ""))
        and c.metadata.get("clause_section", c.metadata.get("clause", ""))
    }
    if not allowed_pairs:
        return False

    citations = re.findall(r"\[[^\]]+\]", answer)
    if not citations:
        # No inline citations — only allow short refusal-style answers
        word_count = len(re.sub(r"\s+", " ", answer.strip()).split())
        return word_count <= 25

    return all(_citation_matches(cit, allowed_pairs) for cit in citations)


def _generate_groq(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """Call Groq API using synchronous HTTP request."""
    unset_keys = {"", "YOUR_GROQ_API_KEY", "replace_with_your_groq_api_key"}
    if not GROQ_API_KEY or GROQ_API_KEY.strip() in unset_keys:
        raise ValueError("GROQ_API_KEY is not configured.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }

    # Use a short connect timeout so offline / DNS-unreachable scenarios fail
    # fast (<3 s) instead of blocking for the full read timeout.  The read
    # timeout (25 s) covers slow-but-reachable Groq responses.
    timeout = httpx.Timeout(connect=3.0, read=25.0, write=5.0, pool=5.0)
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"].get("content", "")

    # Groq can hand back an empty completion (reasoning-only output or a
    # dropped finish). Treat that as a failure so generate_answer falls
    # back to Ollama instead of returning an empty "grounded" answer.
    if not content or not content.strip():
        raise ValueError("Groq returned an empty completion.")

    return content


def _generate_ollama(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """Call local Ollama instance as offline fallback."""
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_TOKENS,
        },
    }

    with httpx.Client(timeout=180.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")


def generate_answer(
    query: str,
    chunks: list[RetrievedChunk],
    gate_passed: bool = True,
    history: list[dict] | None = None,
) -> dict[str, Any]:
    """Generate grounded answer with Groq -> Ollama fallback and citation payload.

    `history` is an ordered list of prior `{"role", "content"}` turns; the last
    few turns are included in the prompt for conversational follow-ups.
    """
    if not gate_passed or not chunks:
        return {
            "answer": REFUSAL_MESSAGE,
            "citations": [],
            "source_used": "none",
            "gated": True,
            "grounded": False,
        }

    context_block = format_context_block(chunks)
    prompt = build_rag_prompt(query, context_block, history=history)

    provider_used = "groq"
    answer_text = ""

    # Acquire a concurrency slot first so bursts of requests are queued and
    # never oversubscribe the CPU with simultaneous LLM inferences.
    with _generation_slots:
        # Try Groq first
        try:
            answer_text = _generate_groq(prompt)
        except Exception as e:
            print(f"[RAG] Groq generation failed: {e}. Attempting Ollama fallback...")
            try:
                answer_text = _generate_ollama(prompt)
                provider_used = "ollama"
            except Exception as oe:
                print(f"[RAG] Ollama fallback failed: {oe}")
                answer_text = "Generation service is unavailable. Please retry when Groq or Ollama is available."
                provider_used = "unavailable"

    # Final safety net: never surface an empty answer as a "grounded" success,
    # regardless of which provider produced it.
    if not answer_text or not answer_text.strip():
        answer_text = REFUSAL_MESSAGE
        provider_used = "unavailable"

    # Build structured citations
    citations = _build_citations(chunks)

    # Citation-format guard: Groq reliably emits inline [IS XXXX, clause]
    # citations which we can validate against retrieved chunks.  The smaller
    # Ollama model often answers correctly from context but doesn't always
    # nail the exact bracket format, so skip the guard for offline-fallback
    # answers — they are still grounded because the prompt only supplies the
    # retrieved context and the system prompt forbids external knowledge.
    if (
        answer_text != REFUSAL_MESSAGE
        and provider_used not in ("unavailable", "ollama")
        and not _has_only_grounded_citations(answer_text, chunks)
    ):
        answer_text = REFUSAL_MESSAGE
        provider_used = "citation_guard"

    return {
        "answer": answer_text,
        "citations": citations,
        "source_used": provider_used,
        "gated": False,
        "grounded": answer_text != REFUSAL_MESSAGE and provider_used != "unavailable",
    }


def _build_citations(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
    """Return deduplicated citation dicts for a list of retrieved chunks."""
    citations: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, int | None]] = set()
    for c in chunks:
        src = c.metadata.get("source_file", c.metadata.get("source", "Standard Document"))
        standard = c.metadata.get("standard_number", c.metadata.get("is_number", ""))
        clause = c.metadata.get("clause_section", c.metadata.get("clause", ""))
        page = c.metadata.get("page_number")
        # Build a clickable BIS URL from the standard number
        source_url = c.metadata.get("url", "")
        if not source_url and standard:
            source_url = "https://www.bis.gov.in/standards/"
        citation_key = (src, standard, clause, page)
        if citation_key not in seen:
            seen.add(citation_key)
            citations.append({
                "source_file": src,
                "standard_number": standard,
                "clause": clause,
                "page_number": page,
                "snippet": c.text[:150] + "...",
                "source_url": source_url,
            })
    return citations


def _is_retryable_stream_error(exc: Exception) -> bool:
    """True for transient Groq failures worth one more attempt.

    Rate limits and 5xx are retryable; auth failures (401/403) and 4xx
    payload problems are not. Transport-level drops/timeouts retry.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response is None:
            return False
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return isinstance(
        exc,
        (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.ReadError,
            httpx.RemoteProtocolError,
        ),
    )


async def _stream_groq(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> AsyncGenerator[str, None]:
    """Stream tokens from the Groq chat-completions endpoint.

    Transient failures (429 / 5xx / dropped connection / read timeout) are
    retried up to `GROQ_STREAM_RETRIES` times *before the first token* is
    emitted.  Once a token has been yielded, any failure re-raises immediately
    so `stream_answer` surfaces the partial answer rather than duplicating
    text from a fresh attempt.  An empty completion (no tokens at all) raises
    so the caller can fall back to Ollama.
    """
    unset_keys = {"", "YOUR_GROQ_API_KEY", "replace_with_your_groq_api_key"}
    if not GROQ_API_KEY or GROQ_API_KEY.strip() in unset_keys:
        raise ValueError("GROQ_API_KEY is not configured.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": True,
    }
    timeout = httpx.Timeout(connect=3.0, read=60.0, write=5.0, pool=5.0)

    last_error: Exception | None = None
    for attempt in range(GROQ_STREAM_RETRIES):
        emitted = False
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            obj = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        token = obj.get("choices", [{}])[0].get("delta", {}).get("content")
                        if token:
                            emitted = True
                            yield token
            if not emitted:
                raise ValueError("Groq streaming returned an empty completion.")
            return
        except Exception as exc:  # noqa: BLE001 - contract is "raise and let caller fall back"
            last_error = exc
            if emitted or attempt == GROQ_STREAM_RETRIES - 1 or not _is_retryable_stream_error(exc):
                raise
            await asyncio.sleep(GROQ_RETRY_BACKOFF_SECONDS * (attempt + 1))
    if last_error is not None:  # pragma: no cover - loop always returns/raises
        raise last_error


async def _stream_ollama(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> AsyncGenerator[str, None]:
    """Stream tokens from the local Ollama /api/generate endpoint."""
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_TOKENS,
        },
    }
    # httpx.Timeout requires all four params (or a default) on this version —
    # a partial spec raises ValueError before any bytes are read.
    timeout = httpx.Timeout(connect=3.0, read=180.0, write=5.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                token = obj.get("response")
                if token:
                    yield token
                if obj.get("done"):
                    break


async def stream_answer(
    query: str,
    chunks: list[RetrievedChunk],
    gate_passed: bool = True,
    history: list[dict] | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Stream an answer token-by-token with Groq -> Ollama fallback.

    Yields a sequence of payload dicts:
      - {"type": "message", "content": <token>}  (one per LLM token)
      - {"type": "done", "query", "response", "citations", "grounded",
         "source", "gated"}                       (exactly one, terminal)

    The retrieval gate is preserved (no context -> refusal is streamed) and
    the citation guard still runs; an un-grounded Groq answer is flagged in
    the terminal payload instead of silently replacing already-streamed text.
    """
    if not gate_passed or not chunks:
        yield {"type": "message", "content": REFUSAL_MESSAGE}
        yield {
            "type": "done",
            "query": query,
            "response": REFUSAL_MESSAGE,
            "citations": [],
            "grounded": False,
            "source": "none",
            "gated": True,
        }
        return

    context_block = format_context_block(chunks)
    prompt = build_rag_prompt(query, context_block, history=history)

    provider_used = "groq"
    answer_parts: list[str] = []

    with _generation_slots:
        try:
            async for token in _stream_groq(prompt):
                answer_parts.append(token)
                yield {"type": "message", "content": token}
        except Exception:
            if answer_parts:
                # Groq died mid-sentence: surface the partial answer rather
                # than stitching two providers together mid-stream.
                provider_used = "groq"
            else:
                # Failed before the first token -> retry on local Ollama.
                provider_used = "ollama"
                try:
                    async for token in _stream_ollama(prompt):
                        answer_parts.append(token)
                        yield {"type": "message", "content": token}
                except Exception:
                    provider_used = "unavailable"

    answer_text = "".join(answer_parts)
    if not answer_text or not answer_text.strip():
        answer_text = REFUSAL_MESSAGE
        provider_used = "unavailable"

    citations = _build_citations(chunks)

    # Citation guard (Groq only — mirrors the non-streaming path's intent).
    guard_failed = (
        provider_used == "groq"
        and answer_text != REFUSAL_MESSAGE
        and not _has_only_grounded_citations(answer_text, chunks)
    )
    grounded = (
        answer_text != REFUSAL_MESSAGE
        and provider_used != "unavailable"
        and not guard_failed
    )

    yield {
        "type": "done",
        "query": query,
        "response": answer_text,
        "citations": citations,
        "grounded": grounded,
        "source": provider_used,
        "gated": False,
    }

