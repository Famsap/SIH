from __future__ import annotations

from typing import Any, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.rag.retrieve import retrieve_relevant_chunks
from app.rag.generate import generate_answer

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
    question: str = Field(..., min_length=1)
    history: list[ChatTurn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    query: str
    response: str
    citations: list[Citation]
    grounded: bool


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Full RAG Q&A endpoint:

    1. Embeds question and queries ChromaDB persistent collection.
    2. Applies anti-hallucination similarity distance gating.
    3. Builds grounded context and executes Groq (or Ollama fallback).
    4. Returns grounded answer and structured citations.
    """
    chunks, gate_passed = retrieve_relevant_chunks(req.question)
    result = generate_answer(req.question, chunks, gate_passed=gate_passed)

    return ChatResponse(
        query=req.question,
        response=result["answer"],
        citations=[Citation(**c) for c in result.get("citations", [])],
        grounded=result.get("grounded", not result.get("gated", False)),
    )


@router.get("/chat/health")
def chat_health():
    return {"status": "ok"}


