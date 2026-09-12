from fastapi import APIRouter

from app.api.v1.endpoints import chat, documents, health, stream

api_router = APIRouter()
api_router.include_router(chat.router, tags=["RAG chat"])
api_router.include_router(stream.router, tags=["RAG chat"])
api_router.include_router(documents.router, tags=["BIS documents"])
api_router.include_router(health.router, tags=["System"])
