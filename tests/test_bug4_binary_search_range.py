import pytest

def test_binary_search_date_range_boundary(client):
    """
    Verifies that binary search range filtering includes books on the end_date boundary.

    Topic: Binary Search Boundary and Insertion-Point Logic
    Difficulty: Hard
    """
    # In seed data:
    # "To Kill a Mockingbird": 2026-02-05
    # "Dune": 2026-02-18
    # "Pride and Prejudice": 2026-03-01
    # "Atomic Habits": 2026-03-15 (on the boundary)
    res = client.get("/api/books?start_date=2026-02-01&end_date=2026-03-15")
    assert res.status_code == 200
    data = res.get_json()
    titles = [b["title"] for b in data["books"]]

    assert "Atomic Habits" in titles, (
        f"Binary search boundary failed: expected 'Atomic Habits' (added 2026-03-15) to be included in date range up to 2026-03-15, but found: {titles}"
    )
