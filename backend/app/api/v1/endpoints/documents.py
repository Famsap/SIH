from __future__ import annotations

import asyncio
import threading
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel

from app.config import CHROMA_COLLECTION, CHROMA_PERSIST_DIR, EMBEDDING_MODEL, REPO_ROOT
from app.rag.ingest import FILENAME_IS_RE, SUFFIXES, rebuild_index
from app.rag.retrieve import get_chroma_collection

router = APIRouter(prefix="/documents")
RAW_DIR = REPO_ROOT / "data" / "raw"
_index_lock = threading.Lock()


class DocumentMetadata(BaseModel):
	source_file: str
	standard_id: str
	year: str
	document_type: str
	title: str = ""
	source_url: str = ""
	chunk_count: int = 0


class IndexJob(BaseModel):
	status: str
	source_file: str
	detail: str


def _validated_filename(filename: str | None) -> str:
	name = Path(filename or "").name
	if not name or Path(name).suffix.lower() not in SUFFIXES or not FILENAME_IS_RE.match(Path(name).stem):
		raise HTTPException(status_code=422, detail="Filename must be IS_<number>_<year>[_Description].pdf|txt|md.")
	return name


def _reindex_all() -> None:
	with _index_lock:
		rebuild_index(RAW_DIR, Path(CHROMA_PERSIST_DIR), CHROMA_COLLECTION, EMBEDDING_MODEL, reset=False)
		get_chroma_collection.cache_clear()


def _document_rows() -> list[DocumentMetadata]:
	collection = get_chroma_collection()
	payload = collection.get(include=["metadatas"])
	counts: dict[str, tuple[dict, int]] = {}
	for metadata in payload.get("metadatas", []):
		meta = metadata or {}
		standard_id = str(meta.get("standard_id", meta.get("standard_number", "")))
		if standard_id:
			previous = counts.get(standard_id, (meta, 0))
			counts[standard_id] = (previous[0], previous[1] + 1)
	return [
		DocumentMetadata(
			source_file=str(metadata.get("source_file", metadata.get("source", ""))),
			standard_id=standard_id,
			year=str(metadata.get("year", "")),
			document_type=str(metadata.get("document_type", "")),
			title=str(metadata.get("title", "")),
			source_url=str(metadata.get("source_url", "")),
			chunk_count=chunk_count,
		)
		for standard_id, (metadata, chunk_count) in sorted(counts.items())
	]


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED, response_model=IndexJob)
async def create_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> IndexJob:
	filename = _validated_filename(file.filename)
	target = (RAW_DIR / filename).resolve()
	if target.exists():
		raise HTTPException(status_code=409, detail="A document with this filename already exists.")
	content = await file.read()
	if not content:
		raise HTTPException(status_code=422, detail="Uploaded document is empty.")
	await asyncio.to_thread(RAW_DIR.mkdir, parents=True, exist_ok=True)
	await asyncio.to_thread(target.write_bytes, content)
	background_tasks.add_task(_reindex_all)
	return IndexJob(status="queued", source_file=filename, detail="Saved; background indexing has been queued.")


@router.get("/", response_model=list[DocumentMetadata])
async def list_documents(offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)) -> list[DocumentMetadata]:
	return (await asyncio.to_thread(_document_rows))[offset:offset + limit]


@router.delete("/{standard_id}")
async def delete_document(standard_id: str) -> dict[str, str | int]:
	if not standard_id.startswith("IS ") or ":" not in standard_id:
		raise HTTPException(status_code=422, detail="standard_id must use the form IS <number>:<year>.")

	def purge() -> int:
		collection = get_chroma_collection()
		payload = collection.get(where={"standard_id": standard_id}, include=[])
		ids = payload.get("ids", [])
		if ids:
			collection.delete(ids=ids)
		return len(ids)

	deleted = await asyncio.to_thread(purge)
	if not deleted:
		raise HTTPException(status_code=404, detail="No indexed chunks found for this standard_id.")
	return {"standard_id": standard_id, "deleted_chunks": deleted}

__all__ = ["router"]
