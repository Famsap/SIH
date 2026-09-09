from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, status

from app.rag.retrieve import get_chroma_collection

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, object]:
    try:
        chunk_count = await asyncio.to_thread(lambda: get_chroma_collection().count())
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="ChromaDB is unavailable.") from exc
    return {"status": "ok", "chroma": "ok", "collection": "bis_standards", "chunk_count": chunk_count}
