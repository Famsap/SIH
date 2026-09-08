from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import functools

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION,
    EMBEDDING_MODEL,
    RETRIEVAL_TOP_K,
    RETRIEVAL_MAX_DISTANCE,
    STRICT_RETRIEVAL_GATE,
)


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    distance: float
    is_valid: bool


@functools.lru_cache(maxsize=1)
def get_embedding_model(model_name: str = EMBEDDING_MODEL) -> SentenceTransformer:
    """Cache the sentence transformer embedding model."""
    return SentenceTransformer(model_name)


@functools.lru_cache(maxsize=1)
def get_chroma_collection(
    persist_dir: str = CHROMA_PERSIST_DIR,
    collection_name: str = CHROMA_COLLECTION,
):
    """Cache the Chroma persistent collection client."""
    client = chromadb.PersistentClient(path=persist_dir)
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


def retrieve_relevant_chunks(
    query: str,
    top_k: int = RETRIEVAL_TOP_K,
    max_distance: float = RETRIEVAL_MAX_DISTANCE,
    strict_gate: bool = STRICT_RETRIEVAL_GATE,
) -> tuple[list[RetrievedChunk], bool]:
    """Retrieve top-k chunks from ChromaDB and apply anti-hallucination gating.

    Returns:
        (chunks, gate_passed): list of RetrievedChunk and boolean flag whether gate passed.
    """
    if not query.strip():
        return [], False

    model = get_embedding_model()
    collection = get_chroma_collection()

    count = collection.count()
    if count == 0:
        return [], False

    query_embedding = model.encode([query], normalize_embeddings=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    retrieved: list[RetrievedChunk] = []
    for doc_id, doc_text, meta, dist in zip(ids, docs, metas, distances):
        is_valid = dist <= max_distance
        retrieved.append(
            RetrievedChunk(
                chunk_id=doc_id,
                text=doc_text,
                metadata=meta or {},
                distance=dist,
                is_valid=is_valid,
            )
        )

    valid_chunks = [c for c in retrieved if c.is_valid]
    gate_passed = len(valid_chunks) > 0 if strict_gate else len(retrieved) > 0

    return (valid_chunks if strict_gate else retrieved, gate_passed)

