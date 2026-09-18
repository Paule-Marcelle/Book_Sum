"""Extraction du texte brut d'un PDF, page par page.

Utilise PyMuPDF pour le texte natif. Si une page ne contient pas de texte
exploitable (PDF scanné), bascule sur l'OCR (Tesseract) pour cette page.
"""
from __future__ import annotations

import io

import fitz  # PyMuPDF

MIN_CHARS_PER_PAGE = 20  # en dessous de ce seuil, on considère la page "scannée"


def extract_pages(pdf_bytes: bytes, ocr: bool = True, ocr_lang: str = "fra") -> list[str]:
    """Retourne une liste de textes, un par page (index 0 = page 1)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: list[str] = []

    for page in doc:
        text = page.get_text("text").strip()
        if len(text) < MIN_CHARS_PER_PAGE and ocr:
            text = _ocr_page(page, ocr_lang) or text
        pages.append(text)

    doc.close()
    return pages


def _ocr_page(page: "fitz.Page", lang: str) -> str | None:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return None

    pix = page.get_pixmap(dpi=300)
    image = Image.open(io.BytesIO(pix.tobytes("png")))
    try:
        return pytesseract.image_to_string(image, lang=lang)
    except pytesseract.TesseractNotFoundError:
        return None


def extract_toc(pdf_bytes: bytes) -> list[tuple[int, str, int]]:
    """Retourne la table des matières native du PDF si elle existe.

    Chaque entrée : (niveau, titre, numéro de page 1-indexé).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    toc = doc.get_toc(simple=True)
    doc.close()
    return [(level, title.strip(), page) for level, title, page in toc]
