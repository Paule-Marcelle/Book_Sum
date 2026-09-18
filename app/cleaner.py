"""Nettoyage du texte extrait : headers/footers répétés, numéros de page,
césures de fin de ligne, espaces superflus.
"""
from __future__ import annotations

import re
from collections import Counter

PAGE_NUMBER_RE = re.compile(r"^\s*[\divxlcIVXLC]{1,6}\s*$")
HYPHEN_BREAK_RE = re.compile(r"(\w)-\n(\w)")
MULTI_SPACE_RE = re.compile(r"[ \t]+")
MULTI_NEWLINE_RE = re.compile(r"\n{3,}")


def clean_pages(pages: list[str]) -> list[str]:
    """Nettoie une liste de textes de pages et retire les headers/footers
    répétés sur l'ensemble du livre (ex: titre du livre en pied de page).
    """
    repeated = _detect_repeated_lines(pages)
    return [_clean_single_page(p, repeated) for p in pages]


def _detect_repeated_lines(pages: list[str], min_ratio: float = 0.4) -> set[str]:
    """Une ligne considérée comme header/footer si elle apparaît (quasi)
    identique sur une proportion significative des pages.
    """
    if len(pages) < 5:
        return set()

    counter: Counter[str] = Counter()
    for page in pages:
        lines = {line.strip() for line in page.splitlines() if line.strip()}
        # on ne regarde que les 2 premières et 2 dernières lignes (zone header/footer)
        edge_lines = list(page.splitlines())
        candidates = {l.strip() for l in edge_lines[:2] + edge_lines[-2:] if l.strip()}
        counter.update(candidates & lines)

    threshold = max(3, int(len(pages) * min_ratio))
    return {line for line, count in counter.items() if count >= threshold}


def _clean_single_page(text: str, repeated_lines: set[str]) -> str:
    text = HYPHEN_BREAK_RE.sub(r"\1\2", text)

    kept_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in repeated_lines:
            continue
        if PAGE_NUMBER_RE.match(stripped):
            continue
        kept_lines.append(stripped)

    joined = " ".join(kept_lines)
    joined = MULTI_SPACE_RE.sub(" ", joined)
    return joined.strip()
