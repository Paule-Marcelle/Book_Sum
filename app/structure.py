"""Détection de la structure du livre (chapitres) : via la table des
matières native du PDF si disponible, sinon via des motifs regex appliqués
au début de chaque page nettoyée.
"""
from __future__ import annotations

import re

CHAPTER_PATTERNS = [
    re.compile(r"^chapitre\s+\d+", re.IGNORECASE),
    re.compile(r"^chapter\s+\d+", re.IGNORECASE),
    re.compile(r"^chapitre\s+[ivxlcdm]+\b", re.IGNORECASE),
    re.compile(r"^partie\s+\d+", re.IGNORECASE),
    re.compile(r"^\d{1,3}[.\s]+[A-ZÀ-Ý]"),  # "1. Introduction"
]


def detect_chapters_from_toc(
    toc: list[tuple[int, str, int]], top_level_only: bool = True
) -> list[tuple[str, int]]:
    """À partir de la TOC PyMuPDF, retourne [(titre, page_debut)] pour les
    entrées de premier niveau (chapitres), triées par page.
    """
    if not toc:
        return []
    min_level = min(level for level, _, _ in toc) if top_level_only else None
    entries = [
        (title, page)
        for level, title, page in toc
        if (min_level is None or level == min_level) and page > 0
    ]
    return sorted(entries, key=lambda e: e[1])


def detect_chapters_from_patterns(pages: list[str]) -> list[tuple[str, int]]:
    """Repère les débuts de chapitre en cherchant les motifs connus en
    tête de page (texte déjà nettoyé). Retourne [(titre, page_index_0based)].
    """
    found: list[tuple[str, int]] = []
    for idx, page_text in enumerate(pages):
        head = page_text[:80].strip()
        for pattern in CHAPTER_PATTERNS:
            match = pattern.match(head)
            if match:
                title = head[: head.find(".", match.end())] if "." in head[: match.end() + 40] else head[:60]
                found.append((title.strip() or f"Chapitre {len(found) + 1}", idx))
                break
    return found


def build_chapter_ranges(
    chapter_starts: list[tuple[str, int]], total_pages: int
) -> list[tuple[str, int, int]]:
    """Convertit une liste [(titre, page_debut_1indexed)] en plages
    [(titre, page_debut, page_fin_exclusive)] couvrant tout le livre.
    """
    if not chapter_starts:
        return [("Livre entier", 1, total_pages + 1)]

    ranges = []
    for i, (title, start) in enumerate(chapter_starts):
        end = chapter_starts[i + 1][1] if i + 1 < len(chapter_starts) else total_pages + 1
        if end > start:
            ranges.append((title, start, end))
    return ranges
