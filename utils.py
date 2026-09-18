"""Utility functions for text processing, PDF extraction, and sanitization."""

import io
import re
from typing import Any
import pypdf
from config import MAX_CHAR_LIMIT, MIN_RESUME_CHAR_WARN


def extract_text_from_pdf(pdf_source: Any) -> tuple[str, str | None]:
    """
    Extracts text from a PDF file stream, bytes, or file path using pypdf.
    
    Returns:
        tuple (extracted_text: str, warning_message: str | None)
    """
    try:
        if isinstance(pdf_source, bytes):
            reader = pypdf.PdfReader(io.BytesIO(pdf_source))
        elif hasattr(pdf_source, "read"):
            # File-like object (e.g. Streamlit UploadedFile)
            pdf_bytes = pdf_source.read()
            # Reset seek if needed
            if hasattr(pdf_source, "seek"):
                pdf_source.seek(0)
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        else:
            reader = pypdf.PdfReader(pdf_source)

        text_parts = []
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text_parts.append(page_text.strip())

        full_text = "\n\n".join(part for part in text_parts if part)
        
        # Normalize excessive whitespace
        full_text = re.sub(r"[ \t]+", " ", full_text)
        full_text = re.sub(r"\n{3,}", "\n\n", full_text).strip()

        warning = None
        if len(full_text) < MIN_RESUME_CHAR_WARN:
            warning = (
                f"Extracted resume text is unusually short ({len(full_text)} characters). "
                "The PDF might be scanned, image-based, or password-protected. "
                "Consider pasting text or using a text-selectable PDF."
            )

        return full_text, warning

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}") from e


def truncate_text(text: str, limit: int = MAX_CHAR_LIMIT) -> tuple[str, bool]:
    """
    Truncates text to limit characters if needed.
    
    Returns:
        tuple (processed_text: str, was_truncated: bool)
    """
    if len(text) > limit:
        return text[:limit] + "\n\n[...Content truncated due to length...]", True
    return text, False


def sanitize_text_for_pdf(text: str) -> str:
    """
    Sanitizes text by replacing Unicode characters (smart quotes, em-dashes,
    special bullets, emojis) with safe ASCII/Latin-1 equivalents for fpdf2.
    """
    replacements = {
        "\u2018": "'",  # Left single quotation mark
        "\u2019": "'",  # Right single quotation mark
        "\u201c": '"',  # Left double quotation mark
        "\u201d": '"',  # Right double quotation mark
        "\u2014": " -- ",  # Em dash
        "\u2013": " - ",   # En dash
        "\u2026": "...",   # Ellipsis
        "\u2022": "* ",    # Bullet point
        "\u25cf": "* ",    # Black circle bullet
        "\u25aa": "* ",    # Black small square
        "\u200b": "",      # Zero-width space
        "\u00a0": " ",     # Non-breaking space
        "\u2122": "(TM)",  # Trademark
        "\u00a9": "(C)",   # Copyright
        "\u00ae": "(R)",   # Registered
    }

    for orig, target in replacements.items():
        text = text.replace(orig, target)

    # Encode to latin-1 with replacement to eliminate exotic unicode/emojis
    clean_text = text.encode("latin-1", "replace").decode("latin-1")
    return clean_text


def compute_aggregate_scores(history: list[dict]) -> dict[str, float]:
    """
    Computes average scores for relevance, depth, structure, clarity, and overall
    from the interview history list.
    """
    if not history:
        return {"relevance": 0.0, "depth": 0.0, "structure": 0.0, "clarity": 0.0, "overall": 0.0}

    totals = {"relevance": 0.0, "depth": 0.0, "structure": 0.0, "clarity": 0.0}
    count = 0

    for item in history:
        score = item.get("score")
        if score:
            if isinstance(score, dict):
                totals["relevance"] += score.get("relevance", 0)
                totals["depth"] += score.get("depth", 0)
                totals["structure"] += score.get("structure", 0)
                totals["clarity"] += score.get("clarity", 0)
            elif hasattr(score, "relevance"):
                totals["relevance"] += score.relevance
                totals["depth"] += score.depth
                totals["structure"] += score.structure
                totals["clarity"] += score.clarity
            count += 1

    if count == 0:
        return {"relevance": 0.0, "depth": 0.0, "structure": 0.0, "clarity": 0.0, "overall": 0.0}

    averages = {k: round(v / count, 2) for k, v in totals.items()}
    averages["overall"] = round(sum(averages.values()) / 4.0, 2)
    return averages
