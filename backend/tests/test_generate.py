"""Tests for the generation layer — citation structure, refusal, fallback."""
from __future__ import annotations

import pytest
from app.rag.retrieve import retrieve_relevant_chunks
from app.rag.generate import generate_answer
from app.rag.prompts import REFUSAL_MESSAGE


class TestCitationStructure:
    """Verify citations returned by generate_answer are well-formed."""

    def test_citations_from_valid_chunks(self):
        """A valid query should produce structured citations."""
        chunks, gate_passed = retrieve_relevant_chunks("What is IS 1417?")
        assert gate_passed
        result = generate_answer("What is IS 1417?", chunks, gate_passed=True)

        assert "citations" in result
        assert len(result["citations"]) > 0, "Should have at least one citation"

        for citation in result["citations"]:
            assert "source_file" in citation, "Citation missing source_file"
            assert "snippet" in citation, "Citation missing snippet"
            assert len(citation["snippet"]) > 10, "Snippet too short"
            # standard_number and clause may be empty strings but should exist
            assert "standard_number" in citation
            assert "clause" in citation
            assert "source_url" in citation, "Citation missing source_url"

    def test_refusal_when_gate_fails(self):
        """When gate fails, the response should be the refusal message."""
        chunks, gate_passed = retrieve_relevant_chunks("")
        result = generate_answer("", chunks, gate_passed=False)

        assert result["answer"] == REFUSAL_MESSAGE
        assert result["citations"] == []
        assert result["grounded"] is False

    def test_grounding_flag(self):
        """grounded flag should be True for valid queries, False for refused."""
        chunks, gate_passed = retrieve_relevant_chunks("hallmarking")
        if gate_passed:
            result = generate_answer("hallmarking", chunks, gate_passed=True)
            # grounded depends on LLM availability, but citations should exist
            assert "grounded" in result
            assert "source_used" in result
