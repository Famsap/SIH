#!/usr/bin/env python3
"""Interactive terminal chat for the BIS RAG pipeline.

Usage (from backend/):
    .venv/bin/python chat_cli.py
    .venv/bin/python chat_cli.py --export chat_log.json

Type your question, press Enter. Type 'quit' or Ctrl-C to exit.
Commands: history, export [filename], quit
"""
from __future__ import annotations

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

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
MAGENTA = "\033[35m"
RESET = "\033[0m"
UNDERLINE = "\033[4m"


def print_banner():
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════╗
║           ManakSetu — BIS Standards RAG Chat                 ║
║                                                              ║
║  Type a question about Indian Standards and press Enter.     ║
║  {GREEN}quit{CYAN} = exit  |  {GREEN}history{CYAN} = show past Q&A  |  {GREEN}export{CYAN} = save log  ║
╚══════════════════════════════════════════════════════════════╝{RESET}

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
        url = c.get("source_url", "")
        label = f"{std}, {clause}" if std and clause else src
        print(f"  {DIM}{i}.{RESET} 📄 {BOLD}{label}{RESET}  {DIM}({src}){RESET}")
        if snippet:
            clean = snippet.replace("\n", " ")[:200]
            print(f"     {DIM}\"{clean}\"{RESET}")
        if url:
            print(f"     {UNDERLINE}{MAGENTA}{url}{RESET}")


def print_history(history: list[dict]):
    """Show all past Q&A turns."""
    if not history:
        print(f"{DIM}  No conversation history yet.{RESET}")
        return
    print(f"\n{BOLD}📜 Conversation History ({len(history) // 2} turns):{RESET}")
    turn_num = 0
    for turn in history:
        if turn["role"] == "user":
            turn_num += 1
            print(f"\n  {BOLD}{CYAN}Q{turn_num}:{RESET} {turn['content'][:120]}")
        elif turn["role"] == "assistant":
            print(f"  {BOLD}{GREEN}A{turn_num}:{RESET} {turn['content'][:120]}...")
            if turn.get("source"):
                print(f"  {DIM}    via: {turn['source']}{RESET}")


def export_history(history: list[dict], filepath: str):
    """Export full conversation history to JSON."""
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "tool": "ManakSetu chat_cli.py",
        "collection": CHROMA_COLLECTION,
        "total_turns": len(history),
        "conversation": history,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    print(f"{GREEN}✓{RESET} Exported {len(history)} turns to {BOLD}{filepath}{RESET}")


def main():
    import chromadb
    from app.config import RETRIEVAL_MAX_DISTANCE

    parser = argparse.ArgumentParser(description="ManakSetu interactive BIS chat CLI")
    parser.add_argument("--export", "-e", type=str, default=None,
                        help="Path to export chat history as JSON on exit")
    args = parser.parse_args()

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

    history = []  # Track full conversation with metadata

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
        if question.lower() == "history":
            print_history(history)
            continue
        if question.lower().startswith("export"):
            parts = question.split(maxsplit=1)
            filename = parts[1] if len(parts) > 1 else f"manaksetu_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_history(history, filename)
            continue

        # Retrieve
        print(f"\n{DIM}Retrieving from BIS corpus...{RESET}")
        chunks, gate_passed = retrieve_relevant_chunks(question)

        if not gate_passed:
            print(f"{YELLOW}⚠ Gate failed — no relevant chunks found (distance > {RETRIEVAL_MAX_DISTANCE}){RESET}\n")
            history.append({"role": "user", "content": question, "timestamp": datetime.now().isoformat()})
            history.append({"role": "assistant", "content": "Gate failed — no relevant BIS documents found.", "source": "gate_blocked", "timestamp": datetime.now().isoformat()})
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
        citations = result.get("citations", [])

        print(f"\n{BOLD}{GREEN}ManakSetu ❯{RESET}")
        for line in answer.split("\n"):
            print(f"  {line}")

        # Source indicator
        if source == "unavailable":
            print(f"\n{YELLOW}⚠ LLM not configured — showing retrieval-only results{RESET}")
            print(f"  {DIM}Set GROQ_API_KEY in .env or install Ollama for generated answers{RESET}")
        else:
            print(f"\n{DIM}  Generated via: {source}{RESET}")

        # Citations
        print_citations(citations)

        # Record in history
        history.append({"role": "user", "content": question, "timestamp": datetime.now().isoformat()})
        history.append({
            "role": "assistant",
            "content": answer,
            "source": source,
            "citations_count": len(citations),
            "grounded": result.get("grounded", False),
            "timestamp": datetime.now().isoformat(),
        })
        print()

    # Auto-export if --export was given
    if args.export and history:
        export_history(history, args.export)


if __name__ == "__main__":
    main()
