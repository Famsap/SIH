from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

# ── CPU throttling guard ──────────────────────────────────────────
# Numeric/tokenizer libraries default to "every core", which oversubscribes
# the CPU during embedding + LLM inference and triggers throttling. These
# env vars must be set *before* numpy/torch/transformers load, so they are
# defined here at import time. OS-level values take precedence if present.
EMBEDDING_THREADS = os.getenv("EMBEDDING_THREADS", "2")
for _thread_var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_thread_var, EMBEDDING_THREADS)

# Cap concurrent LLM calls: bursts queue instead of pegging every core.
MAX_CONCURRENT_GENERATIONS = max(1, int(os.getenv("MAX_CONCURRENT_GENERATIONS", "2")))

# Warm the embedding model + Chroma client at API startup so the first user
# request doesn't trigger a slow, CPU-heavy load inside the request path.
PRELOAD_EMBEDDING_MODEL = os.getenv("PRELOAD_EMBEDDING_MODEL", "true").lower() == "true"

BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
).split(",")

OMNIROUTE_BASE_URL = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
OMNIROUTE_API_KEY = os.getenv("OMNIROUTE_API_KEY", "")
OMNIROUTE_MODEL = os.getenv("OMNIROUTE_MODEL", "auto")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# NOTE: llama-3.3-70b-versatile was retired from Groq's model catalog; the key
# currently provisions gpt-oss / compound / qwen chat models instead.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# CHROMA_PERSIST_DIR resolution:
#   New convention (repo-root relative):  "data/chroma"
#   Legacy convention (backend/ CWD relative): "../data/chroma"
# Legacy values begin with ".." and must be resolved against the process CWD
# (the documented dev flow runs from backend/). Everything else resolves
# against the repo root, so launching from any directory works.
_CHROMA_PERSIST_DIR_RAW = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")
if _CHROMA_PERSIST_DIR_RAW.startswith(".."):
    CHROMA_PERSIST_DIR = str((Path.cwd() / _CHROMA_PERSIST_DIR_RAW).resolve())
else:
    CHROMA_PERSIST_DIR = str((REPO_ROOT / _CHROMA_PERSIST_DIR_RAW).resolve())
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "bis_standards")

RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
RETRIEVAL_MAX_DISTANCE = float(os.getenv("RETRIEVAL_MAX_DISTANCE", "0.55"))

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "700"))
STRICT_RETRIEVAL_GATE = os.getenv("STRICT_RETRIEVAL_GATE", "true").lower() == "true"

