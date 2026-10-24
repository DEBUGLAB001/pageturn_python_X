import pytest

def test_sorting_by_reading_progress(client):
    """
    Verifies that sorting by reading progress uses completion percentage rather than raw page count.

    Topic: Sorting Algorithms and Comparator Logic
    Difficulty: Easy
    """
    res = client.get("/api/books?sort_by=progress&order=asc")
    assert res.status_code == 200
    data = res.get_json()
    books = data["books"]

    # In seed data:
    # "Dune" has 200/688 pages (~29% complete)
    # "The Great Gatsby" has 180/180 pages (100% complete)
    # In ascending sort by reading progress, Dune (29%) MUST precede Gatsby (100%).
    dune_idx = next((i for i, b in enumerate(books) if b["title"] == "Dune"), None)
    gatsby_idx = next((i for i, b in enumerate(books) if b["title"] == "The Great Gatsby"), None)

    assert dune_idx is not None, "Expected 'Dune' in books list"
    assert gatsby_idx is not None, "Expected 'The Great Gatsby' in books list"
    assert dune_idx < gatsby_idx, (
        f"Sorting comparator failed: expected 'Dune' (29% progress) to appear before 'The Great Gatsby' (100% progress) in ascending sort, but Dune was at index {dune_idx} and Gatsby was at index {gatsby_idx}"
    )
