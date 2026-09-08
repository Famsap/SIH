from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import chromadb
from sentence_transformers import SentenceTransformer

# Token-based chunking with fallback
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:  # pragma: no cover
    RecursiveCharacterTextSplitter = None  # type: ignore


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    text: str
    metadata: dict[str, Any]


def _iter_processed_txt_files(processed_dir: Path) -> Iterable[Path]:
    if not processed_dir.exists():
        return []
    return sorted(processed_dir.glob("*.txt"))


def _chunk_text(text: str, *, source_stem: str) -> list[tuple[int, str]]:
    """Split text into chunks.
    Returns: list of (index, chunk_text)
    """
    if RecursiveCharacterTextSplitter is not None:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = splitter.split_text(text)
        return list(enumerate(chunks))

    # Character-based fallback
    chunk_size = 2000
    chunk_overlap = 300
    chunks: list[str] = []
    i = 0
    while i < len(text):
        end = min(len(text), i + chunk_size)
        chunks.append(text[i:end])
        if end == len(text):
            break
        i = max(0, end - chunk_overlap)

    return list(enumerate(chunks))


def ingest_processed_texts(
    *,
    processed_dir: str | Path,
    chroma_persist_dir: str | Path,
    collection_name: str = "bis_chunks",
    embedding_model_name: str = "BAAI/bge-small-en-v1.5",
    batch_size: int = 32,
    overwrite_collection: bool = False,
) -> dict[str, Any]:
    """Ingest all processed *.txt files into ChromaDB persistent storage."""

    processed_dir = Path(processed_dir)
    chroma_persist_dir = Path(chroma_persist_dir)
    chroma_persist_dir.mkdir(parents=True, exist_ok=True)

    # Modern ChromaDB PersistentClient
    client = chromadb.PersistentClient(path=str(chroma_persist_dir))

    if overwrite_collection:
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    print(f"Loading embedding model: {embedding_model_name}...")
    model = SentenceTransformer(embedding_model_name)

    all_files = list(_iter_processed_txt_files(processed_dir))
    if not all_files:
        raise ValueError(
            f"No processed .txt files found in {processed_dir}. "
            "Run scripts/ingest_sample.py first (add PDFs to data/raw/)."
        )

    total_chunks = 0
    for file_path in all_files:
        text = file_path.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            continue

        source_stem = file_path.stem
        chunked = _chunk_text(text, source_stem=source_stem)
        records: list[ChunkRecord] = []
        for chunk_index, chunk_text in chunked:
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue
            chunk_id = f"{source_stem}_{chunk_index}"
            records.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    metadata={
                        "source": file_path.name,
                        "source_stem": source_stem,
                        "chunk_index": chunk_index,
                    },
                )
            )

        if not records:
            continue

        # Embed in batches
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            ids = [r.chunk_id for r in batch]
            documents = [r.text for r in batch]
            metadatas = [r.metadata for r in batch]

            embeddings = model.encode(documents, normalize_embeddings=True).tolist()

            collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )

        total_chunks += len(records)
        print(f"Ingested {len(records)} chunks from {file_path.name}")

    return {
        "processed_dir": str(processed_dir),
        "chroma_persist_dir": str(chroma_persist_dir),
        "collection_name": collection_name,
        "embedding_model_name": embedding_model_name,
        "files_ingested": len(all_files),
        "chunks_added": total_chunks,
    }


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    data_dir = repo_root / "data"

    from dotenv import load_dotenv

    load_dotenv((repo_root / ".env").as_posix())

    result = ingest_processed_texts(
        processed_dir=data_dir / "processed",
        chroma_persist_dir=os.environ.get(
            "CHROMA_PERSIST_DIR", (data_dir / "chroma").as_posix()
        ),
        collection_name=os.environ.get("CHROMA_COLLECTION", "bis_chunks"),
        embedding_model_name=os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
        overwrite_collection=True,
    )
    print("Ingestion complete:", result)


