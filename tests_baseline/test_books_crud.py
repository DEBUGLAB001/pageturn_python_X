import pytest

def test_create_book_success(client):
    payload = {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "genre": "Sci-Fi",
        "total_pages": 288,
        "current_page": 0,
        "status": "Want to Read",
        "date_added": "2026-04-10",
        "rating": 5,
        "notes": "Classic dystopian masterpiece.",
        "cover_style": "terracotta"
    }
    res = client.post("/api/books", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["book"]["title"] == "Brave New World"
    assert data["book"]["author"] == "Aldous Huxley"
    assert data["book"]["status"] == "Want to Read"
    assert data["book"]["progress_percentage"] == 0

def test_create_book_validation_errors(client):
    # Missing title
    res1 = client.post("/api/books", json={"title": "", "author": "Huxley", "genre": "Sci-Fi", "total_pages": 200})
    assert res1.status_code == 400

    # Total pages <= 0
    res2 = client.post("/api/books", json={"title": "Test", "author": "Test", "genre": "Sci-Fi", "total_pages": 0})
    assert res2.status_code == 400

    # Current page > total pages
    res3 = client.post("/api/books", json={"title": "Test", "author": "Test", "genre": "Sci-Fi", "total_pages": 100, "current_page": 150})
    assert res3.status_code == 400

    # Rating out of range
    res4 = client.post("/api/books", json={"title": "Test", "author": "Test", "genre": "Sci-Fi", "total_pages": 100, "rating": 6})
    assert res4.status_code == 400

def test_get_books_and_get_by_id(client):
    res = client.get("/api/books")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["books"]) >= 8

    first_book_id = data["books"][0]["id"]
    res_single = client.get(f"/api/books/{first_book_id}")
    assert res_single.status_code == 200
    assert res_single.get_json()["book"]["id"] == first_book_id

    # Non-existent book
    res_404 = client.get("/api/books/99999")
    assert res_404.status_code == 404

def test_update_and_delete_book(client):
    # Create book to edit and delete
    create_res = client.post("/api/books", json={
        "title": "Temp Book",
        "author": "Temp Author",
        "genre": "Fiction",
        "total_pages": 150,
        "current_page": 10
    })
    book_id = create_res.get_json()["book"]["id"]

    # Update book
    update_res = client.put(f"/api/books/{book_id}", json={
        "title": "Updated Temp Book",
        "author": "Temp Author",
        "genre": "Fiction",
        "total_pages": 160,
        "current_page": 40
    })
    assert update_res.status_code == 200
    assert update_res.get_json()["book"]["title"] == "Updated Temp Book"
    assert update_res.get_json()["book"]["current_page"] == 40

    # Delete book
    del_res = client.delete(f"/api/books/{book_id}")
    assert del_res.status_code == 200

    # Verify gone
    check_res = client.get(f"/api/books/{book_id}")
    assert check_res.status_code == 404
