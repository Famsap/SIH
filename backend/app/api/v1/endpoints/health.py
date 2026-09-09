from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, status

from app.config import CHROMA_COLLECTION
from app.rag.retrieve import get_chroma_collection

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, object]:
	try:
		chunk_count = await asyncio.to_thread(lambda: get_chroma_collection().count())
	except Exception as exc:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail="ChromaDB is unavailable.",
		) from exc
	return {
		"status": "ok",
		"chroma": "ok",
		"collection": CHROMA_COLLECTION,
		"chunk_count": chunk_count,
	}

__all__ = ["router"]
