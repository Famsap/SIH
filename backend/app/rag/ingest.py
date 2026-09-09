"""Build a persistent, clause-aware BIS ChromaDB index.

From backend/: python -m app.rag.ingest --reset --query "packaged drinking water"
"""
from __future__ import annotations

import argparse
import hashlib
import logging
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import chromadb
import fitz
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from app.config import CHROMA_COLLECTION, CHROMA_PERSIST_DIR, EMBEDDING_MODEL

LOG = logging.getLogger("bis_ingest")
SUFFIXES = {".pdf", ".txt", ".md"}
IS_RE = re.compile(r"\bIS\s*:?[\s-]*(\d{1,5}(?::\d{4})?)\b", re.I)
CLAUSE_RE = re.compile(r"^\s*((?:\d+(?:\.\d+){0,8}|(?:clause|section)\s+\d+(?:\.\d+){0,8}))\.?\s+.+$", re.I)
PAGE_MARKER_RE = re.compile(r"\[\[PAGE:\s*(\d+)\]\]\s*", re.I)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(c for c in text if c in "\n\t" or unicodedata.category(c)[0] != "C")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def read_source(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        with fitz.open(path) as pdf:
            return "\n\n".join(f"[[PAGE: {number}]]\n{page.get_text('text')}" for number, page in enumerate(pdf, 1))
    return path.read_text(encoding="utf-8", errors="replace")


def source_title(text: str, fallback: str) -> str:
    for line in text.splitlines()[:30]:
        line = line.strip().lstrip("#").strip()
        if len(line) > 4:
            return line[:300]
    return fallback.replace("_", " ").replace("-", " ").title()


def sections(text: str):
    """Yield `(clause, content)` while retaining clause headers with content."""
    clause, lines = "", []
    for line in text.splitlines():
        match = CLAUSE_RE.match(line)
        if match:
            if lines and "\n".join(lines).strip():
                yield clause, "\n".join(lines).strip()
            clause, lines = match.group(1), [line]
        else:
            lines.append(line)
    if lines and "\n".join(lines).strip():
        yield clause, "\n".join(lines).strip()


def split_recursive(text: str, size: int, overlap: int) -> list[str]:
    """Character splitter preferring paragraphs, lines, sentences, then words."""
    output, remaining = [], text.strip()
    while remaining:
        if len(remaining) <= size:
            output.append(remaining)
            break
        cut = -1
        for separator in ("\n\n", "\n", ". ", " "):
            found = remaining.rfind(separator, 0, size + 1)
            if found > size // 2:
                cut = found + len(separator)
                break
        cut = cut if cut > 0 else size
        chunk = remaining[:cut].strip()
        if chunk:
            output.append(chunk)
        tail = chunk[-overlap:] if overlap else ""
        remaining = (tail + remaining[cut:]).strip()
        if len(output) > 1 and remaining == output[-1]:
            break
    return output


def load_chunks(input_dir: Path, chunk_size: int, overlap: int) -> list[tuple[str, str, dict]]:
    paths = [p for p in sorted(input_dir.rglob("*")) if p.is_file() and p.suffix.lower() in SUFFIXES]
    LOG.info("Found %d supported source file(s)", len(paths))
    if not paths:
        raise ValueError(f"No .pdf, .txt, or .md source files in {input_dir}")
    records: list[tuple[str, str, dict]] = []
    now = datetime.now(timezone.utc).isoformat()
    for path in paths:
        try:
            text = normalise(read_source(path))
        except Exception as exc:
            LOG.warning("Skipping %s: %s", path.name, exc)
            continue
        if not text:
            LOG.warning("Skipping empty source: %s", path.name)
            continue
        standard = IS_RE.search(text)
        metadata_base = {
            "source": path.name,
            "source_file": path.name,
            "source_path": path.relative_to(input_dir.parent).as_posix(),
            "title": source_title(text, path.stem),
            "document_type": path.suffix.lstrip(".").upper(),
            "is_number": f"IS {standard.group(1)}" if standard else "",
            "standard_number": f"IS {standard.group(1)}" if standard else "",
            "ingested_at": now,
        }
        index = 0
        for clause, section in sections(text):
            for content in split_recursive(section, chunk_size, overlap):
                page_match = PAGE_MARKER_RE.search(content)
                content = PAGE_MARKER_RE.sub("", content).strip()
                if not content:
                    continue
                digest = hashlib.sha256(f"{path}|{index}|{content}".encode()).hexdigest()[:24]
                metadata = {**metadata_base, "clause": clause, "clause_section": clause, "chunk_index": index}
                if page_match:
                    metadata["page_number"] = int(page_match.group(1))
                records.append((f"bis_{digest}", content, metadata))
                index += 1
        LOG.info("Loaded %s: %d chunk(s)", path.name, index)
    if not records:
        raise ValueError("No readable non-empty documents could be indexed.")
    return records


def main() -> None:
    root = repo_root()
    load_dotenv(root / ".env")
    parser = argparse.ArgumentParser(description="Build persistent BIS ChromaDB vectors.")
    parser.add_argument("--input-dir", type=Path, default=root / "data" / "processed")
    parser.add_argument("--chroma-dir", type=Path, default=Path(CHROMA_PERSIST_DIR))
    parser.add_argument("--collection", default=CHROMA_COLLECTION)
    parser.add_argument("--embedding-model", default=EMBEDDING_MODEL)
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--reset", action="store_true", help="Delete target collection before indexing.")
    parser.add_argument("--query", default="BIS standard information")
    args = parser.parse_args()
    if args.chunk_size < 1 or not 0 <= args.chunk_overlap < args.chunk_size:
        parser.error("chunk overlap must be non-negative and smaller than chunk size")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    records = load_chunks(args.input_dir.resolve(), args.chunk_size, args.chunk_overlap)
    LOG.info("Created %d total chunk(s)", len(records))
    args.chroma_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(args.chroma_dir.resolve()))
    if args.reset:
        try:
            client.delete_collection(args.collection)
            LOG.info("Deleted collection %s", args.collection)
        except Exception:
            pass
    collection = client.get_or_create_collection(args.collection, metadata={"hnsw:space": "cosine"})
    LOG.info("Loading embedding model %s", args.embedding_model)
    model = SentenceTransformer(args.embedding_model)
    for start in range(0, len(records), 32):
        batch = records[start:start + 32]
        collection.upsert(
            ids=[r[0] for r in batch], documents=[r[1] for r in batch], metadatas=[r[2] for r in batch],
            embeddings=model.encode([r[1] for r in batch], normalize_embeddings=True).tolist(),
        )
        LOG.info("Persisted %d/%d vectors", min(start + len(batch), len(records)), len(records))
    LOG.info("Index complete: %d persisted vector(s)", collection.count())

    result = collection.query(
        query_embeddings=model.encode([args.query], normalize_embeddings=True).tolist(),
        n_results=min(3, collection.count()), include=["documents", "metadatas", "distances"],
    )
    LOG.info("Verification query: %s", args.query)
    for rank, (doc, meta, distance) in enumerate(zip(result["documents"][0], result["metadatas"][0], result["distances"][0]), 1):
        LOG.info("Result %d | distance=%.4f | %s | clause=%s | %s", rank, distance, meta.get("is_number", ""), meta.get("clause", ""), doc[:160].replace("\n", " "))


if __name__ == "__main__":
    main()
