from flask import Blueprint, request, jsonify
from database import (
    get_all_books,
    get_book_by_id,
    create_book,
    update_book,
    update_book_progress,
    delete_book,
    get_reading_goal,
    set_reading_goal
)
from services.search_service import linear_search_books
from services.sorting_service import sort_books
from services.statistics_service import get_reading_statistics
from services.range_service import filter_books_by_date_range

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/books", methods=["GET"])
def get_books():
    """
    Returns filtered and sorted books based on query parameters:
    q: search string for title and author
    status: 'Want to Read', 'Currently Reading', 'Completed'
    genre: genre name
    start_date: YYYY-MM-DD
    end_date: YYYY-MM-DD
    sort_by: 'title', 'author', 'date_added', 'progress'
    order: 'asc', 'desc'
    """
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    genre = request.args.get("genre", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    sort_by = request.args.get("sort_by", "date_added").strip()
    order = request.args.get("order", "desc").strip()

    books = get_all_books()

    # 1. Date Range Filtering (Binary Search based)
    if start_date or end_date:
        books = filter_books_by_date_range(books, start_date=start_date, end_date=end_date)

    # 2. Linear Search (Title and Author)
    if q:
        books = linear_search_books(books, q)

    # 3. Status Filtering
    if status and status.lower() != "all":
        books = [b for b in books if b.get("status", "").lower() == status.lower()]

    # 4. Genre Filtering
    if genre and genre.lower() != "all":
        books = [b for b in books if b.get("genre", "").lower() == genre.lower()]

    # 5. Sorting (Comparator based)
    books = sort_books(books, sort_by=sort_by, order=order)

    return jsonify({
        "success": True,
        "books": books,
        "count": len(books)
    })

@api_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({"success": False, "error": "Book not found"}), 404
    return jsonify({"success": True, "book": book})

@api_bp.route("/books", methods=["POST"])
def add_book():
    data = request.get_json() or {}

    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    genre = data.get("genre", "").strip()
    total_pages = data.get("total_pages")

    if not title:
        return jsonify({"success": False, "error": "Title is required"}), 400
    if not author:
        return jsonify({"success": False, "error": "Author is required"}), 400
    if not genre:
        return jsonify({"success": False, "error": "Genre is required"}), 400

    try:
        total_pages = int(total_pages)
        if total_pages <= 0:
            return jsonify({"success": False, "error": "Total pages must be greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Total pages must be a valid integer"}), 400

    current_page = data.get("current_page", 0)
    try:
        current_page = int(current_page)
        if current_page < 0 or current_page > total_pages:
            return jsonify({"success": False, "error": f"Current page must be between 0 and {total_pages}"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Current page must be a valid integer"}), 400

    rating = data.get("rating")
    if rating not in (None, "", "null"):
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return jsonify({"success": False, "error": "Rating must be between 1 and 5"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Rating must be an integer between 1 and 5"}), 400

    new_book = create_book(data)
    return jsonify({"success": True, "book": new_book}), 201

@api_bp.route("/books/<int:book_id>", methods=["PUT"])
def edit_book(book_id):
    existing = get_book_by_id(book_id)
    if not existing:
        return jsonify({"success": False, "error": "Book not found"}), 404

    data = request.get_json() or {}
    title = data.get("title", existing["title"]).strip()
    author = data.get("author", existing["author"]).strip()
    genre = data.get("genre", existing["genre"]).strip()
    total_pages = data.get("total_pages", existing["total_pages"])

    if not title:
        return jsonify({"success": False, "error": "Title cannot be empty"}), 400
    if not author:
        return jsonify({"success": False, "error": "Author cannot be empty"}), 400
    if not genre:
        return jsonify({"success": False, "error": "Genre cannot be empty"}), 400

    try:
        total_pages = int(total_pages)
        if total_pages <= 0:
            return jsonify({"success": False, "error": "Total pages must be greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Total pages must be a valid integer"}), 400

    current_page = data.get("current_page", existing["current_page"])
    try:
        current_page = int(current_page)
        if current_page < 0 or current_page > total_pages:
            return jsonify({"success": False, "error": f"Current page must be between 0 and {total_pages}"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Current page must be a valid integer"}), 400

    updated = update_book(book_id, data)
    return jsonify({"success": True, "book": updated})

@api_bp.route("/books/<int:book_id>/progress", methods=["PATCH"])
def set_progress(book_id):
    existing = get_book_by_id(book_id)
    if not existing:
        return jsonify({"success": False, "error": "Book not found"}), 404

    data = request.get_json() or {}
    if "current_page" not in data:
        return jsonify({"success": False, "error": "current_page field is required"}), 400

    try:
        current_page = int(data["current_page"])
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "current_page must be an integer"}), 400

    total_pages = existing["total_pages"]
    if current_page < 0 or current_page > total_pages:
        return jsonify({"success": False, "error": f"Current page must be between 0 and {total_pages}"}), 400

    updated = update_book_progress(book_id, current_page)
    return jsonify({"success": True, "book": updated})

@api_bp.route("/books/<int:book_id>", methods=["DELETE"])
def remove_book(book_id):
    existing = get_book_by_id(book_id)
    if not existing:
        return jsonify({"success": False, "error": "Book not found"}), 404

    delete_book(book_id)
    return jsonify({"success": True, "message": "Book deleted successfully"})

@api_bp.route("/statistics", methods=["GET"])
def get_stats():
    stats = get_reading_statistics()
    return jsonify({"success": True, "statistics": stats})

@api_bp.route("/goal", methods=["GET"])
def get_goal():
    target = get_reading_goal()
    return jsonify({"success": True, "target": target})

@api_bp.route("/goal", methods=["PUT"])
def update_goal():
    data = request.get_json() or {}
    target = data.get("target")
    try:
        target = int(target)
        if target <= 0:
            return jsonify({"success": False, "error": "Target must be greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Target must be a valid positive integer"}), 400

    saved_target = set_reading_goal(target)
    return jsonify({"success": True, "target": saved_target})
