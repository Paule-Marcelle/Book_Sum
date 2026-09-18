"""Structures de données partagées par le pipeline de résumé."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Sentence:
    text: str
    page: int
    index: int  # position globale dans le livre (pour le score de position)
    score: float = 0.0


@dataclass
class Section:
    title: str
    sentences: list[Sentence] = field(default_factory=list)
    summary_sentences: list[Sentence] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(s.text for s in self.sentences)


@dataclass
class Chapter:
    title: str
    sections: list[Section] = field(default_factory=list)
    summary_sentences: list[Sentence] = field(default_factory=list)

    @property
    def all_sentences(self) -> list[Sentence]:
        return [s for sec in self.sections for s in sec.sentences]

    @property
    def start_page(self) -> int | None:
        sents = self.all_sentences
        return sents[0].page if sents else None


@dataclass
class Book:
    title: str
    chapters: list[Chapter] = field(default_factory=list)

    @property
    def all_sentences(self) -> list[Sentence]:
        return [s for ch in self.chapters for s in ch.all_sentences]


@dataclass
class SummaryResult:
    express: str  # ~1 page, résumé global très court
    standard: str  # 5-10 pages
    detailed: str  # 20-30 pages
    by_chapter: list[tuple[str, str]]  # (titre chapitre, résumé)
    key_points: list[str]
    sourced_excerpts: list[tuple[str, int]]  # (phrase, page)
