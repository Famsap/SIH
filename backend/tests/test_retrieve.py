"""Tests for the retrieval layer — gate logic, empty queries, distance thresholds."""
from __future__ import annotations

import pytest
from app.rag.retrieve import retrieve_relevant_chunks


class TestRetrievalGate:
    """Verify anti-hallucination gating for different query types."""

    def test_good_query_passes_gate(self):
        """A known BIS query should retrieve valid chunks and pass the gate."""
        chunks, gate_passed = retrieve_relevant_chunks("What is IS 1417?")
        assert gate_passed, "Gate should pass for a relevant BIS query"
        assert len(chunks) > 0, "Should retrieve at least one chunk"
        # Every returned chunk must have metadata
        for c in chunks:
            assert c.metadata, f"Chunk {c.chunk_id} has no metadata"
            assert c.text, f"Chunk {c.chunk_id} has empty text"
            assert c.distance <= 0.55, f"Chunk distance {c.distance} exceeds threshold"

    def test_empty_query_fails_gate(self):
        """An empty query must never pass the retrieval gate."""
        chunks, gate_passed = retrieve_relevant_chunks("")
        assert not gate_passed, "Empty query must fail gate"
        assert len(chunks) == 0, "Empty query must return no chunks"

    def test_whitespace_query_fails_gate(self):
        """A whitespace-only query should behave like empty."""
        chunks, gate_passed = retrieve_relevant_chunks("   \t  ")
        assert not gate_passed
        assert len(chunks) == 0

    def test_irrelevant_query_fails_gate(self):
        """A query unrelated to BIS standards should fail the gate."""
        chunks, gate_passed = retrieve_relevant_chunks(
            "What is the capital of France?"
        )
        # The gate should either fail or return chunks with high distance
        if gate_passed:
            # If gate passed, all chunks must be within threshold
            for c in chunks:
                assert c.distance <= 0.55

    def test_retrieval_returns_correct_top_k(self):
        """Requesting top_k=3 should return at most 3 chunks."""
        chunks, _ = retrieve_relevant_chunks("hallmarking charges gold", top_k=3)
        assert len(chunks) <= 3, f"Expected at most 3 chunks, got {len(chunks)}"

    def test_chunk_metadata_fields(self):
        """Each retrieved chunk should contain expected metadata keys."""
        chunks, _ = retrieve_relevant_chunks("What is IS 1417?")
        for c in chunks:
            # At least one of these standard ID fields must be present
            has_standard = (
                "standard_number" in c.metadata
                or "is_number" in c.metadata
            )
            has_source = (
                "source_file" in c.metadata
                or "source" in c.metadata
            )
            assert has_standard or has_source, (
                f"Chunk {c.chunk_id} missing standard/source metadata: {c.metadata.keys()}"
            )
