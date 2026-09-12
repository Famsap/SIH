"""SSE streaming chat endpoint.

Protocol (Server-Sent Events):

    event: message
    data: {"type": "message", "content": "<token>"}

    event: done
    data: {"type": "done", "query", "response", "citations", "grounded",
           "source", "gated"}

Consumers should render message events incrementally and apply the final
`done` payload (citations / grounded / source / gated) when it arrives.
"""
from __future__ import annotations

import asyncio
import json
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.rag.generate import stream_answer
from app.rag.retrieve import retrieve_relevant_chunks

router = APIRouter()


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4_000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=30)


@router.post("/chat/stream")
async def stream_chat(req: ChatRequest) -> EventSourceResponse:
    """Stream a grounded RAG answer + citations over Server-Sent Events."""

    async def event_source():
        # Mirror the JSON endpoint's error surface, but as an SSE error event
        # so a half-open stream never leaves the client hanging silently.
        try:
            chunks, gate_passed = await asyncio.to_thread(
                retrieve_relevant_chunks, req.question
            )
        except Exception as exc:
            yield {
                "event": "error",
                "data": json.dumps(
                    {"type": "error", "message": f"RAG service is temporarily unavailable: {exc}"}
                ),
            }
            return

        async for payload in stream_answer(
            req.question,
            chunks,
            gate_passed,
            history=[turn.model_dump() for turn in req.history],
        ):
            if payload["type"] == "done":
                yield {"event": "done", "data": json.dumps(payload)}
            else:
                yield {"event": "message", "data": json.dumps(payload)}

    return EventSourceResponse(event_source())


__all__ = ["router"]