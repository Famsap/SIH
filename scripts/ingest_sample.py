from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF


def parse_pdf(file_path: Path) -> str:
    """Extract text from a local PDF file."""
    parts: list[str] = []
    with fitz.open(file_path) as pdf:
        for page in pdf:
            parts.append(page.get_text())
    return "\n".join(parts).strip()


def iter_pdfs(raw_dir: Path) -> list[Path]:
    if not raw_dir.exists():
        return []
    return sorted([p for p in raw_dir.glob("**/*.pdf") if p.is_file()])


if __name__ == "__main__":
    print("Starting local ingestion (no internet required)...")

    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    pdfs = iter_pdfs(raw_dir)
    if not pdfs:
        raise SystemExit(
            "No PDFs found in data/raw/. "
            "Please add one or more BIS PDFs there and re-run."
        )

    # In MVP we just process the first PDF. You can extend this to loop all PDFs.
    pdf_path = pdfs[0]
    print(f"Using PDF: {pdf_path}")

    extracted_text = parse_pdf(pdf_path)
    preview = extracted_text[:300].replace("\n", " ")
    print("Extracted Text Preview:\n", preview)

    out_txt = processed_dir / f"{pdf_path.stem}_extracted.txt"
    out_txt.write_text(extracted_text, encoding="utf-8")
    print("Extraction complete. Saved:", out_txt)


