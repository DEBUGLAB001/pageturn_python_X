import pytest

def test_genre_frequency_counting(client):
    """
    Verifies that the genre distribution hash map accurately counts book occurrences per genre.

    Topic: Hash Maps and Frequency Counting
    Difficulty: Easy
    """
    res = client.get("/api/statistics")
    assert res.status_code == 200
    data = res.get_json()
    dist = data["statistics"]["genre_distribution"]

    # In seed data:
    # "Pride and Prejudice" is Romance (exactly 1 book)
    # "The Great Gatsby" and "To Kill a Mockingbird" are Fiction (exactly 2 books)
    assert dist.get("Romance") == 1, (
        f"Hash map frequency counting failed: expected Romance count of 1, but got {dist.get('Romance')}"
    )
    assert dist.get("Fiction") == 2, (
        f"Hash map frequency counting failed: expected Fiction count of 2, but got {dist.get('Fiction')}"
    )
