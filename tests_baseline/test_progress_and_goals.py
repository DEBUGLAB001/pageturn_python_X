import pytest

def test_reading_progress_update_and_status_transition(client):
    # Create a book with 200 pages and 0 read
    res = client.post("/api/books", json={
        "title": "Progress Test Book",
        "author": "Tester",
        "genre": "Fiction",
        "total_pages": 200,
        "current_page": 0,
        "status": "Want to Read"
    })
    book_id = res.get_json()["book"]["id"]

    # 1. Update to 50 pages -> status becomes Currently Reading, progress = 25%
    patch_res1 = client.patch(f"/api/books/{book_id}/progress", json={"current_page": 50})
    assert patch_res1.status_code == 200
    book_data1 = patch_res1.get_json()["book"]
    assert book_data1["current_page"] == 50
    assert book_data1["status"] == "Currently Reading"
    assert book_data1["progress_percentage"] == 25

    # 2. Update to 200 pages -> status becomes Completed, progress = 100%
    patch_res2 = client.patch(f"/api/books/{book_id}/progress", json={"current_page": 200})
    assert patch_res2.status_code == 200
    book_data2 = patch_res2.get_json()["book"]
    assert book_data2["current_page"] == 200
    assert book_data2["status"] == "Completed"
    assert book_data2["progress_percentage"] == 100

def test_reading_progress_validation(client):
    # Book with 100 pages
    res = client.post("/api/books", json={
        "title": "Validation Test Book",
        "author": "Tester",
        "genre": "Fiction",
        "total_pages": 100
    })
    book_id = res.get_json()["book"]["id"]

    # Negative page
    res_neg = client.patch(f"/api/books/{book_id}/progress", json={"current_page": -1})
    assert res_neg.status_code == 400

    # Over total pages
    res_over = client.patch(f"/api/books/{book_id}/progress", json={"current_page": 101})
    assert res_over.status_code == 400

    # Missing current_page field
    res_empty = client.patch(f"/api/books/{book_id}/progress", json={})
    assert res_empty.status_code == 400

def test_reading_goals_api(client):
    # GET goal
    get_res = client.get("/api/goal")
    assert get_res.status_code == 200
    assert "target" in get_res.get_json()

    # PUT valid goal
    put_res = client.put("/api/goal", json={"target": 18})
    assert put_res.status_code == 200
    assert put_res.get_json()["target"] == 18

    # Verify updated goal returned by GET
    get_res2 = client.get("/api/goal")
    assert get_res2.get_json()["target"] == 18

    # PUT invalid goal (0 or negative)
    bad_res1 = client.put("/api/goal", json={"target": 0})
    assert bad_res1.status_code == 400
    bad_res2 = client.put("/api/goal", json={"target": -5})
    assert bad_res2.status_code == 400
