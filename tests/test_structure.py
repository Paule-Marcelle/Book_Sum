from app.structure import build_chapter_ranges, detect_chapters_from_toc


def test_build_chapter_ranges_covers_whole_book():
    starts = [("Chapitre 1", 1), ("Chapitre 2", 10), ("Chapitre 3", 25)]
    ranges = build_chapter_ranges(starts, total_pages=30)
    assert ranges == [
        ("Chapitre 1", 1, 10),
        ("Chapitre 2", 10, 25),
        ("Chapitre 3", 25, 31),
    ]


def test_build_chapter_ranges_empty_falls_back_to_whole_book():
    ranges = build_chapter_ranges([], total_pages=50)
    assert ranges == [("Livre entier", 1, 51)]


def test_detect_chapters_from_toc_filters_top_level():
    toc = [
        (1, "Chapitre 1", 1),
        (2, "Section 1.1", 2),
        (1, "Chapitre 2", 10),
        (2, "Section 2.1", 11),
    ]
    result = detect_chapters_from_toc(toc)
    assert result == [("Chapitre 1", 1), ("Chapitre 2", 10)]
