from __future__ import annotations

from typing import Any

SYSTEM_PROMPT = """You are ManakSetu (मानकसेतु), an authoritative AI assistant for Indian Standards (Bureau of Indian Standards / BIS).
Your duty is to provide precise, accurate, and faithful information about Indian Standards (IS codes), conformity assessment schemes, hallmarking, CRS, and BIS certification processes based ONLY on the verified context provided below.

STRICT CONSTRAINTS (ANTI-HALLUCINATION RULES):
1. Rely EXCLUSIVELY on the provided Context excerpts.
2. If the answer cannot be determined from the context, clearly state: "I do not have sufficient information in the verified BIS documentation to answer this question. Please refer to the official BIS portal (bis.gov.in)."
3. Never invent IS code numbers, clause numbers, testing limits, or fee structures.
4. Format citations cleanly with IS Number, title or clause reference whenever applicable.
5. Provide structured answers with clear headings or bullet points where appropriate.
"""


def format_context_block(chunks: list[Any]) -> str:
    """Format retrieved chunks into a standardized context block for the LLM."""
    if not chunks:
        return "No relevant documentation found in the database."

    formatted_entries = []
    for idx, chunk in enumerate(chunks, 1):
        source = chunk.metadata.get("source", "Unknown Document")
        source_stem = chunk.metadata.get("source_stem", "")
        chunk_idx = chunk.metadata.get("chunk_index", "")
        header = f"--- [DOCUMENT {idx}: {source} (Ref: {source_stem}_{chunk_idx})] ---"
        formatted_entries.append(f"{header}\n{chunk.text.strip()}\n")

    return "\n".join(formatted_entries)


def build_rag_prompt(query: str, context_block: str) -> str:
    """Combine user query and retrieved context into user turn."""
    return f"""CONTEXT INFORMATION:
{context_block}

USER QUESTION:
{query}

Please provide a comprehensive and accurate answer based strictly on the above context:"""

