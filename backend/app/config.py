from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
).split(",")

OMNIROUTE_BASE_URL = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
OMNIROUTE_API_KEY = os.getenv("OMNIROUTE_API_KEY", "")
OMNIROUTE_MODEL = os.getenv("OMNIROUTE_MODEL", "auto")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR", str(REPO_ROOT / "data" / "chroma")
)
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "bis_standards")

RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
RETRIEVAL_MAX_DISTANCE = float(os.getenv("RETRIEVAL_MAX_DISTANCE", "0.55"))

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "700"))
STRICT_RETRIEVAL_GATE = os.getenv("STRICT_RETRIEVAL_GATE", "true").lower() == "true"

