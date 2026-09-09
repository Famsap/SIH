from __future__ import annotations

import asyncio
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.rag.generate import generate_answer
from app.rag.retrieve import retrieve_relevant_chunks

router = APIRouter()


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class Citation(BaseModel):
    source_file: str
    standard_number: str = ""
    clause: str = ""
    page_number: int | None = None
    snippet: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4_000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=30)


class ChatResponse(BaseModel):
    query: str
    response: str
    citations: list[Citation]
    grounded: bool


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Keep vector retrieval and model calls off the FastAPI event loop."""
    try:
        chunks, gate_passed = await asyncio.to_thread(retrieve_relevant_chunks, req.question)
        result = await asyncio.to_thread(generate_answer, req.question, chunks, gate_passed)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RAG service is temporarily unavailable.") from exc
    return ChatResponse(
        query=req.question,
        response=result["answer"],
        citations=[Citation(**citation) for citation in result.get("citations", [])],
        grounded=result.get("grounded", not result.get("gated", False)),
    )
