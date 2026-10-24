import pytest

def test_linear_search_author_matching(client):
    """
    Verifies that linear search matches books by author substring (e.g. searching 'Orwell' matches 'George Orwell').

    Topic: Linear Search
    Difficulty: Easy
    """
    res = client.get("/api/books?q=Orwell")
    assert res.status_code == 200
    data = res.get_json()
    titles = [b["title"] for b in data["books"]]
    assert "1984" in titles, (
        f"Linear search failed to find book by author substring 'Orwell'. Found: {titles}"
    )
