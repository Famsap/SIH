from __future__ import annotations

import os
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
from app.rag.prompts import SYSTEM_PROMPT, build_rag_prompt, format_context_block
from app.rag.retrieve import RetrievedChunk


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
            "answer": (
                "I do not have sufficient information in the verified BIS documentation "
                "to answer this question accurately. Please refer to the official Bureau of Indian Standards portal at https://www.bis.gov.in."
            ),
            "citations": [],
            "source_used": "none",
            "gated": True,
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
            # If both LLMs are unreachable (e.g. no internet and Ollama not started),
            # return context summary faithfully without crashing
            answer_text = (
                f"Retrieved {len(chunks)} relevant excerpt(s) from Indian Standards database:\n\n"
                + "\n\n---\n\n".join([f"**Excerpt from {c.metadata.get('source', 'document')}:**\n{c.text[:400]}..." for c in chunks[:3]])
            )
            provider_used = "local_raw_context"

    # Build structured citations
    citations = []
    seen = set()
    for c in chunks:
        src = c.metadata.get("source", "Standard Document")
        stem = c.metadata.get("source_stem", "")
        if src not in seen:
            seen.add(src)
            citations.append({
                "source": src,
                "title": stem.replace("_", " ").title(),
                "snippet": c.text[:150] + "...",
                "score": round(1.0 - c.distance, 3) if hasattr(c, "distance") else 1.0,
            })

    return {
        "answer": answer_text,
        "citations": citations,
        "source_used": provider_used,
        "gated": False,
    }

