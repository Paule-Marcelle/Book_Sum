from app.cleaner import clean_pages


def test_removes_hyphen_line_breaks():
    pages = ["Cette technologie permet de\ndévelop-\nper des solutions."] * 6
    cleaned = clean_pages(pages)
    assert "dévelop-\nper" not in cleaned[0]
    assert "développer" in cleaned[0]


def test_removes_repeated_header_footer():
    pages = [f"MON LIVRE\nContenu de la page {i} qui est suffisamment long.\n{i}" for i in range(1, 8)]
    cleaned = clean_pages(pages)
    for page in cleaned:
        assert "MON LIVRE" not in page


def test_removes_page_numbers():
    pages = [
        f"Contenu principal numero {i}, suffisamment long pour ne pas etre un numero de page.\n{i}"
        for i in range(1, 7)
    ]
    cleaned = clean_pages(pages)
    for i, page in enumerate(cleaned, start=1):
        assert not page.strip().endswith(str(i))
