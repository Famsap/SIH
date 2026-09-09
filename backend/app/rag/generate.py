from __future__ import annotations

import os
import re
from typing import Any, AsyncGenerator, Generator
import httpx

from app.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)
from app.rag.prompts import REFUSAL_MESSAGE, SYSTEM_PROMPT, build_rag_prompt, format_context_block
from app.rag.retrieve import RetrievedChunk


def _has_only_grounded_citations(answer: str, chunks: list[RetrievedChunk]) -> bool:
    """Allow model output only when it cites metadata from retrieved chunks."""
    allowed = {
        f"[{c.metadata.get('standard_number', c.metadata.get('is_number', ''))}, {c.metadata.get('clause_section', c.metadata.get('clause', ''))}]"
        for c in chunks
        if c.metadata.get('standard_number', c.metadata.get('is_number', '')) and c.metadata.get('clause_section', c.metadata.get('clause', ''))
    }
    citations = set(re.findall(r"\[[^\]]+\]", answer))
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    return bool(allowed and citations and citations.issubset(allowed) and all(line.endswith("]") or line.endswith(":") for line in lines))


def _generate_groq(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """Call Groq API using synchronous HTTP request."""
    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY":
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

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


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

    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")


def generate_answer(
    query: str,
    chunks: list[RetrievedChunk],
    gate_passed: bool = True,
) -> dict[str, Any]:
    """Generate grounded answer with Groq -> Ollama fallback and citation payload."""
    if not gate_passed or not chunks:
        return {
            "answer": REFUSAL_MESSAGE,
            "citations": [],
            "source_used": "none",
            "gated": True,
            "grounded": False,
        }

    context_block = format_context_block(chunks)
    prompt = build_rag_prompt(query, context_block)

    provider_used = "groq"
    answer_text = ""

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

    # Build structured citations
    citations = []
    seen = set()
    for c in chunks:
        src = c.metadata.get("source_file", c.metadata.get("source", "Standard Document"))
        standard = c.metadata.get("standard_number", c.metadata.get("is_number", ""))
        clause = c.metadata.get("clause_section", c.metadata.get("clause", ""))
        page = c.metadata.get("page_number")
        citation_key = (src, standard, clause, page)
        if citation_key not in seen:
            seen.add(citation_key)
            citations.append({
                "source_file": src,
                "standard_number": standard,
                "clause": clause,
                "page_number": page,
                "snippet": c.text[:150] + "...",
            })

    if answer_text != REFUSAL_MESSAGE and provider_used != "unavailable" and not _has_only_grounded_citations(answer_text, chunks):
        answer_text = REFUSAL_MESSAGE
        provider_used = "citation_guard"

    return {
        "answer": answer_text,
        "citations": citations,
        "source_used": provider_used,
        "gated": False,
        "grounded": answer_text != REFUSAL_MESSAGE and provider_used != "unavailable",
    }

