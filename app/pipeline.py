"""Orchestration complète : PDF -> texte -> structure -> résumé
hiérarchique multi-niveaux (section 9, 11 et 12 du cahier des charges).
"""
from __future__ import annotations

from app import cleaner, parser, splitter, structure, summarizer
from app.models import Book, Chapter, Section, SummaryResult


def build_book(pdf_bytes: bytes, title: str, ocr: bool = True) -> Book:
    """Parse le PDF et construit l'arbre Book -> Chapter -> Section -> Sentence."""
    pages = parser.extract_pages(pdf_bytes, ocr=ocr)
    cleaned_pages = cleaner.clean_pages(pages)

    toc = parser.extract_toc(pdf_bytes)
    chapter_starts = structure.detect_chapters_from_toc(toc)
    if not chapter_starts:
        pattern_hits = structure.detect_chapters_from_patterns(cleaned_pages)
        chapter_starts = [(chap_title, page_idx + 1) for chap_title, page_idx in pattern_hits]

    ranges = structure.build_chapter_ranges(chapter_starts, len(cleaned_pages))

    chapters: list[Chapter] = []
    global_index = 0
    for chap_title, start_page, end_page in ranges:
        sentences = []
        for page_num in range(start_page, min(end_page, len(cleaned_pages) + 1)):
            page_text = cleaned_pages[page_num - 1]
            if not page_text:
                continue
            if page_num == start_page and page_text.startswith(chap_title):
                page_text = page_text[len(chap_title):].strip()
            page_sentences = splitter.split_page_into_sentences(page_text, page_num, global_index)
            sentences.extend(page_sentences)
            global_index += len(page_sentences)

        if not sentences:
            continue
        section = Section(title=chap_title, sentences=sentences)
        chapters.append(Chapter(title=chap_title, sections=[section]))

    return Book(title=title, chapters=chapters)


def summarize_book(book: Book, mode: str = summarizer.MODE_STRICT) -> SummaryResult:
    """Produit un résumé hiérarchique à plusieurs niveaux de granularité."""
    for chapter in book.chapters:
        for section in chapter.sections:
            section.summary_sentences = summarizer.extract_summary(
                section.sentences, ratio=0.15, min_sentences=3, max_sentences=60, mode=mode
            )
        chapter.summary_sentences = _sorted_by_index(
            [s for section in chapter.sections for s in section.summary_sentences]
        )

    all_chapter_summaries = _sorted_by_index(
        [s for chapter in book.chapters for s in chapter.summary_sentences]
    )

    detailed_sentences = summarizer.extract_summary(
        all_chapter_summaries, ratio=0.55, min_sentences=1, mode=mode
    )
    standard_sentences = summarizer.extract_summary(
        detailed_sentences, ratio=0.4, min_sentences=1, mode=mode
    )
    express_sentences = summarizer.extract_summary(
        standard_sentences, ratio=0.25, min_sentences=3, max_sentences=20, mode=mode
    )

    by_chapter = [(chapter.title, _format_paragraph(chapter.summary_sentences)) for chapter in book.chapters]
    key_points = [s.text for s in express_sentences]
    sourced_excerpts = [(s.text, s.page) for s in standard_sentences]

    return SummaryResult(
        express=_format_paragraph(express_sentences),
        standard=_format_paragraph(standard_sentences),
        detailed=_format_paragraph(detailed_sentences),
        by_chapter=by_chapter,
        key_points=key_points,
        sourced_excerpts=sourced_excerpts,
    )


def _sorted_by_index(sentences):
    return sorted(sentences, key=lambda s: s.index)


def _format_paragraph(sentences) -> str:
    return " ".join(s.text for s in _sorted_by_index(sentences))
