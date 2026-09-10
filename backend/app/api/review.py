from __future__ import annotations

import re
import zipfile
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

import fitz
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()

MAX_FILE_SIZE = 3 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png", ".webp", ".gif"}
IS_PATTERN = re.compile(r"\bIS(?:\s|[-_/])?(?:ISO\s*)?\d{3,6}(?:[-:]\d{4})?\b", re.IGNORECASE)
DATE_PATTERN = re.compile(r"\b(?:0?[1-9]|[12]\d|3[01])[-/.](?:0?[1-9]|1[0-2])[-/.](?:19|20)\d{2}\b")
YEAR_FIRST_DATE_PATTERN = re.compile(r"\b(?:19|20)\d{2}[-/.](?:0?[1-9]|1[0-2])[-/.](?:0?[1-9]|[12]\d|3[01])\b")
FIELD_PATTERNS = {
    "Document or report number": re.compile(r"\b(?:report|certificate|license|licence|application)\s*(?:no|number|#|id)?\s*[:#-]?\s*[A-Z0-9][A-Z0-9./_-]{3,}\b", re.IGNORECASE),
    "Issue date": re.compile(r"\b(?:issue|issued|date of issue|issued on)\b", re.IGNORECASE),
    "Expiry or validity date": re.compile(r"\b(?:expir|valid until|validity|renewal)\w*\b", re.IGNORECASE),
    "Applicant or manufacturer": re.compile(r"\b(?:applicant|manufacturer|firm|company|organisation|organization)\b", re.IGNORECASE),
}


def _docx_text(content: bytes) -> str:
    with zipfile.ZipFile(BytesIO(content)) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
    return re.sub(r"<[^>]+>", " ", xml).replace("&amp;", "&")


def _extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        document = fitz.open(stream=content, filetype="pdf")
        try:
            return "\n".join(page.get_text() for page in document)
        finally:
            document.close()
    if suffix == ".docx":
        return _docx_text(content)
    if suffix == ".txt":
        return content.decode("utf-8", errors="replace")
    return ""


def _date_values(text: str) -> list[date]:
    values: list[date] = []
    for match in DATE_PATTERN.findall(text) + YEAR_FIRST_DATE_PATTERN.findall(text):
        try:
            parts = re.split(r"[-/.]", match)
            if len(parts[0]) == 4:
                values.append(date(int(parts[0]), int(parts[1]), int(parts[2])))
            else:
                values.append(date(int(parts[2]), int(parts[1]), int(parts[0])))
        except ValueError:
            continue
    return values


@router.post("/review")
async def review_document(file: UploadFile = File(...)):
    filename = file.filename or "upload"
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Supported files: PDF, DOCX, TXT, JPG, JPEG, PNG, WEBP, or GIF.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The selected file is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Files must be smaller than 3 MB.")

    try:
        text = _extract_text(filename, content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="This file could not be read. Try exporting it again.") from exc

    normalized = " ".join(text.split())
    is_image = suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    standards = sorted({match.upper() for match in IS_PATTERN.findall(normalized)})
    detected_dates = _date_values(normalized)
    today = date.today()
    has_expired_date = any(value < today for value in detected_dates) and bool(re.search(r"expir|valid until|validity", normalized, re.IGNORECASE))
    checks = []

    if is_image:
        checks.append({"label": "Image received", "status": "review", "detail": "Image accepted. Text fields need visual or OCR verification."})
        checks.append({"label": "IS reference", "status": "review", "detail": "Image text was not automatically read; confirm the IS number manually."})
    else:
        checks.append({"label": "Readable content", "status": "pass" if normalized else "review", "detail": f"{len(normalized):,} characters extracted." if normalized else "No readable text was detected."})
        checks.append({"label": "IS reference", "status": "pass" if standards else "review", "detail": ", ".join(standards) if standards else "No IS number was detected."})

    for label, pattern in FIELD_PATTERNS.items():
        found = bool(pattern.search(normalized)) if normalized else False
        checks.append({"label": label, "status": "pass" if found else "review", "detail": "Detected in the file." if found else "Not detected; verify this field."})

    checks.append({"label": "Expiry date", "status": "review" if has_expired_date else "pass", "detail": "A past validity or expiry date was detected." if has_expired_date else "No expired validity date detected; confirm the official date."})
    if len(standards) > 1:
        checks.append({"label": "IS reference consistency", "status": "review", "detail": "Multiple IS references found; confirm that they apply to the same product and revision."})

    return {
        "filename": filename,
        "file_type": suffix[1:].upper(),
        "size_bytes": len(content),
        "review_status": "preliminary_review",
        "standards": standards,
        "dates_found": [value.isoformat() for value in detected_dates],
        "checks": checks,
        "disclaimer": "Preliminary review only. This is not BIS approval, legal advice, certification, or a validity decision.",
        "checked_at": datetime.now().isoformat(timespec="seconds"),
    }