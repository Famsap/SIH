"""(Re)validation harness for the RAG pipeline."""
from app.config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION,
    EMBEDDING_MODEL,
    RETRIEVAL_MAX_DISTANCE,
    STRICT_RETRIEVAL_GATE,
)

print("Config OK:")
print("  CHROMA_PERSIST_DIR:", CHROMA_PERSIST_DIR)
print("  COLLECTION:", CHROMA_COLLECTION)
print("  EMBEDDING:", EMBEDDING_MODEL)
print("  MAX_DIST:", RETRIEVAL_MAX_DISTANCE)
print("  STRICT:", STRICT_RETRIEVAL_GATE)

import chromadb

c = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
col = c.get_collection(CHROMA_COLLECTION)
print(f"  Vectors: {col.count()}")

from app.rag.retrieve import retrieve_relevant_chunks
from app.rag.generate import generate_answer

# Test 1: Good query
c1, g1 = retrieve_relevant_chunks("What is IS 1417?")
assert g1, "gate should pass for good query"
assert len(c1) == 5, f"expected 5 chunks, got {len(c1)}"
print("Test 1 (good query): PASS -", len(c1), "chunks, gate passed")

# Test 2: Empty query
c2, g2 = retrieve_relevant_chunks("")
assert not g2, "gate should fail for empty query"
print("Test 2 (empty query): PASS - 0 chunks, gate failed")

# Test 3: Full generate flow (LLM unavailable but pipeline works)
r = generate_answer("What is IS 1417?", c1, gate_passed=g1)
assert r["citations"], "should have citations from chunks"
print(
    "Test 3 (generate): PASS -",
    len(r["citations"]),
    "citations, source_used:",
    r["source_used"],
)

# Test 4/5: HTTP endpoint
from fastapi.testclient import TestClient
from app.main import app

tc = TestClient(app)
resp = tc.get("/health")
assert resp.status_code == 200
print("Test 4 (health): PASS")
resp2 = tc.post("/api/chat", json={"question": "What are the hallmarking charges?", "history": []})
assert resp2.status_code == 200
j = resp2.json()
assert j["citations"], "should have citations"
print("Test 5 (chat endpoint): PASS -", len(j["citations"]), "citations")

print()
print("ALL TESTS PASSED OK")