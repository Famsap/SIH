"""Tests for FastAPI HTTP endpoints — health, chat, citation contract."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from app.main import app


tc = TestClient(app)


class TestHealthEndpoint:
    """Verify /health returns system status with sub-service details."""

    def test_health_returns_200(self):
        resp = tc.get("/health")
        assert resp.status_code == 200

    def test_health_has_services(self):
        resp = tc.get("/health")
        data = resp.json()
        assert "status" in data
        assert "services" in data
        assert isinstance(data["services"], dict)

    def test_health_reports_chroma(self):
        resp = tc.get("/health")
        services = resp.json()["services"]
        assert "chroma" in services
        assert "vectors" in services["chroma"]
        assert "status" in services["chroma"]

    def test_health_reports_embedding(self):
        resp = tc.get("/health")
        services = resp.json()["services"]
        assert "embedding" in services
        assert "model" in services["embedding"]

    def test_health_reports_ollama(self):
        resp = tc.get("/health")
        services = resp.json()["services"]
        assert "ollama" in services
        assert "status" in services["ollama"]

    def test_health_reports_groq(self):
        resp = tc.get("/health")
        services = resp.json()["services"]
        assert "groq" in services
        assert "status" in services["groq"]


class TestChatEndpoint:
    """Verify POST /api/chat returns correct response contract."""

    def test_chat_returns_200(self):
        resp = tc.post("/api/chat", json={"question": "What is IS 1417?", "history": []})
        assert resp.status_code == 200

    def test_chat_response_has_required_fields(self):
        resp = tc.post("/api/chat", json={"question": "What is IS 1417?", "history": []})
        data = resp.json()
        assert "query" in data
        assert "response" in data
        assert "citations" in data
        assert "grounded" in data
        assert data["query"] == "What is IS 1417?"

    def test_chat_citations_have_required_fields(self):
        resp = tc.post("/api/chat", json={"question": "What is IS 1417?", "history": []})
        citations = resp.json()["citations"]
        assert len(citations) > 0, "Should have at least one citation"
        for c in citations:
            assert "source_file" in c
            assert "standard_number" in c
            assert "clause" in c
            assert "snippet" in c
            assert "source_url" in c, "Citation missing source_url"

    def test_chat_empty_question_returns_422(self):
        resp = tc.post("/api/chat", json={"question": "", "history": []})
        assert resp.status_code == 422, "Empty question should be rejected"

    def test_chat_history_included(self):
        history = [
            {"role": "user", "content": "What is IS 1417?"},
            {"role": "assistant", "content": "IS 1417 is about gold assays."},
        ]
        resp = tc.post("/api/chat", json={"question": "What about silver?", "history": history})
        assert resp.status_code == 200
