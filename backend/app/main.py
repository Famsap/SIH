from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    BACKEND_CORS_ORIGINS,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION,
    EMBEDDING_MODEL,
    RETRIEVAL_MAX_DISTANCE,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GROQ_MODEL,
    PRELOAD_EMBEDDING_MODEL,
)
from app.api.v1.api import api_router
from app.api.v1.endpoints import chat as chat_v1


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Preload expensive singletons so the first user request is instant.

    Without this, the sentence-transformer (~130 MB) loads *inside* the first
    request, stalling the threadpool and spiking CPU at request time.
    """
    if PRELOAD_EMBEDDING_MODEL:

        def _warmup() -> None:
            from app.rag.retrieve import get_chroma_collection, get_embedding_model

            get_embedding_model()    # load & cache sentence-transformer once
            get_chroma_collection()  # open the persistent Chroma client/collection

        try:
            await asyncio.to_thread(_warmup)
        except Exception as exc:  # startup must never take the API down
            print(f"[startup] model warm-up skipped: {exc}")

    yield


app = FastAPI(
    title="ManakSetu API",
    description="AI-powered assistant for Indian Standards and BIS services",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in BACKEND_CORS_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Legacy /api/chat alias so the Next.js frontend keeps working unchanged.
# Both paths share the same upgraded v1 chat handler (multi-turn history,
# source + gated fields, citation source_urls).
app.include_router(chat_v1.router, prefix="/api")


@app.get("/", tags=["System"])
def root():
    return {"ok": True, "service": "manaksetu-backend", "api_version": "v1"}


@app.get("/health")
def health():
    """System readiness check — reports Chroma, embedding model, Ollama, and Groq status."""
    import httpx
    import chromadb

    report = {
        "status": "ok",
        "services": {},
    }

    # ── ChromaDB ──────────────────────────────────────────────
    chroma_info = {"status": "ok", "vectors": 0, "collection": CHROMA_COLLECTION}
    try:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        col = client.get_collection(CHROMA_COLLECTION)
        chroma_info["vectors"] = col.count()
    except Exception as e:
        chroma_info["status"] = "error"
        chroma_info["error"] = str(e)
        report["status"] = "degraded"
    report["services"]["chroma"] = chroma_info

    # ── Embedding model ───────────────────────────────────────
    embed_info = {"status": "ok", "model": EMBEDDING_MODEL}
    try:
        from app.rag.retrieve import get_embedding_model
        get_embedding_model()  # triggers lazy load + cache
    except Exception as e:
        embed_info["status"] = "error"
        embed_info["error"] = str(e)
        report["status"] = "degraded"
    report["services"]["embedding"] = embed_info

    # ── Ollama ────────────────────────────────────────────────
    ollama_info = {"status": "unknown", "model": OLLAMA_MODEL, "url": OLLAMA_BASE_URL}
    try:
        with httpx.Client(timeout=3.0) as client:
            r = client.get(f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags")
            if r.status_code == 200:
                models = [m.get("name", "") for m in r.json().get("models", [])]
                ollama_info["status"] = "ok"
                ollama_info["available_models"] = models
                ollama_info["model_ready"] = any(OLLAMA_MODEL in m for m in models)
            else:
                ollama_info["status"] = "error"
                ollama_info["error"] = f"HTTP {r.status_code}"
    except Exception as e:
        ollama_info["status"] = "unreachable"
        ollama_info["error"] = str(e)
    report["services"]["ollama"] = ollama_info

    # ── Groq ──────────────────────────────────────────────────
    from app.config import GROQ_API_KEY
    groq_info = {"model": GROQ_MODEL}
    unset_keys = {"", "YOUR_GROQ_API_KEY", "replace_with_your_groq_api_key"}
    if GROQ_API_KEY and GROQ_API_KEY.strip() not in unset_keys:
        groq_info["status"] = "configured"
    else:
        groq_info["status"] = "not_configured"
        report["status"] = "degraded"
    report["services"]["groq"] = groq_info

    return report

