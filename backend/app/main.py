from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import BACKEND_CORS_ORIGINS
from app.api.chat import router as chat_router

app = FastAPI(
    title="ManakSetu API",
    description="AI-powered assistant for Indian Standards and BIS services",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in BACKEND_CORS_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/")
def root():
    return {"ok": True, "service": "manaksetu-backend"}


@app.get("/health")
def health():
    return {"status": "ok"}

