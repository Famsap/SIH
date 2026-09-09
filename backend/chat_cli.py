#!/usr/bin/env python3
"""Interactive terminal chat for the BIS RAG pipeline.

Usage (from backend/):
    .venv/bin/python chat_cli.py

Type your question, press Enter. Type 'quit' or Ctrl-C to exit.
"""
from __future__ import annotations

import sys
import os
from pathlib import Path

# Ensure repo root is on sys.path so app.* imports work from any CWD
_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION,
    EMBEDDING_MODEL,
)
from app.rag.retrieve import retrieve_relevant_chunks
from app.rag.generate import generate_answer

BOLD  = "\033[1m"
CYAN  = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED   = "\033[31m"
DIM   = "\033[2m"
RESET = "\033[0m"


def print_banner():
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════════╗
║        ManakSetu — BIS Standards RAG Chat            ║
║   Type a question about Indian Standards and press   ║
║   Enter.  Type {GREEN}quit{CYAN} or press {GREEN}Ctrl-C{CYAN} to exit.        ║
╚══════════════════════════════════════════════════════╝{RESET}

{DIM}  Embedding : {EMBEDDING_MODEL}
  Collection: {CHROMA_COLLECTION}
  ChromaDB  : {CHROMA_PERSIST_DIR}{RESET}
""")


def print_citations(citations: list[dict]):
    if not citations:
        return
    print(f"\n{BOLD}📚 Citations:{RESET}")
    for i, c in enumerate(citations, 1):
        std = c.get("standard_number", "")
        clause = c.get("clause", "")
        src = c.get("source_file", "")
        snippet = c.get("snippet", "")
        label = f"{std}, {clause}" if std and clause else src
        print(f"  {DIM}{i}.{RESET} 📄 {BOLD}{label}{RESET}  {DIM}({src}){RESET}")
        if snippet:
            # Show first 200 chars of snippet, cleaned up
            clean = snippet.replace("\n", " ")[:200]
            print(f"     {DIM}\"{clean}\"{RESET}")


def main():
    import chromadb
    from app.config import RETRIEVAL_MAX_DISTANCE

    print_banner()

    # Quick index check
    try:
        c = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        col = c.get_collection(CHROMA_COLLECTION)
        print(f"{GREEN}✓{RESET} ChromaDB connected: {col.count()} vectors loaded\n")
    except Exception as e:
        print(f"{RED}✗{RESET} ChromaDB error: {e}")
        print(f"  {YELLOW}Run ingestion first: cd backend && python -m app.rag.ingest{RESET}")
        sys.exit(1)

    while True:
        try:
            question = input(f"{BOLD}{CYAN}You ❯ {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}Goodbye!{RESET}")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print(f"{DIM}Goodbye!{RESET}")
            break

        # Retrieve
        print(f"\n{DIM}Retrieving from BIS corpus...{RESET}")
        chunks, gate_passed = retrieve_relevant_chunks(question)

        if not gate_passed:
            print(f"{YELLOW}⚠ Gate failed — no relevant chunks found (distance > {RETRIEVAL_MAX_DISTANCE}){RESET}\n")
            continue

        # Show retrieved chunks summary
        print(f"{GREEN}✓{RESET} Retrieved {len(chunks)} chunk(s):")
        for i, ch in enumerate(chunks, 1):
            std = ch.metadata.get("standard_number", "")
            clause = ch.metadata.get("clause_section", ch.metadata.get("clause", ""))
            dist = ch.distance
            print(f"  {DIM}{i}. [{std} {clause}] distance={dist:.4f}{RESET}")
        print()

        # Generate
        print(f"{DIM}Generating answer...{RESET}")
        result = generate_answer(question, chunks, gate_passed=gate_passed)

        answer = result["answer"]
        source = result.get("source_used", "unknown")

        print(f"\n{BOLD}{GREEN}ManakSetu ❯{RESET}")
        # Word-wrap the answer nicely
        for line in answer.split("\n"):
            print(f"  {line}")

        # Source indicator
        if source == "unavailable":
            print(f"\n{YELLOW}⚠ LLM not configured — showing retrieval-only results{RESET}")
            print(f"  {DIM}Set GROQ_API_KEY in .env or install Ollama for generated answers{RESET}")
        else:
            print(f"\n{DIM}  Generated via: {source}{RESET}")

        # Citations
        print_citations(result.get("citations", []))
        print()


if __name__ == "__main__":
    main()
