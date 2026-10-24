import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "pageturn.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reseed=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS books")
        cursor.execute("DROP TABLE IF EXISTS settings")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            total_pages INTEGER NOT NULL CHECK(total_pages > 0),
            current_page INTEGER NOT NULL DEFAULT 0 CHECK(current_page >= 0),
            status TEXT NOT NULL DEFAULT 'Want to Read' CHECK(status IN ('Want to Read', 'Currently Reading', 'Completed')),
            date_added TEXT NOT NULL,
            rating INTEGER CHECK(rating IS NULL OR (rating >= 1 AND rating <= 5)),
            notes TEXT DEFAULT '',
            cover_style TEXT DEFAULT 'forest'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_books = [
            ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", 180, 180, "Completed", "2026-01-10", 5, "A classic jazz-age tragedy.", "navy"),
            ("1984", "George Orwell", "Sci-Fi", 328, 164, "Currently Reading", "2026-01-25", 4, "Chilling and remarkably prescient dystopian narrative.", "terracotta"),
            ("To Kill a Mockingbird", "Harper Lee", "Fiction", 336, 336, "Completed", "2026-02-05", 5, "Profound lessons on empathy and justice.", "forest"),
            ("Dune", "Frank Herbert", "Sci-Fi", 688, 200, "Currently Reading", "2026-02-18", 5, "Epic sci-fi worldbuilding and intricate politics.", "amber"),
            ("Pride and Prejudice", "Jane Austen", "Romance", 432, 0, "Want to Read", "2026-03-01", None, "Witty romance and societal observations.", "sage"),
            ("Atomic Habits", "James Clear", "Non-Fiction", 320, 320, "Completed", "2026-03-15", 5, "Practical guide for continuous personal growth.", "slate"),
            ("The Hobbit", "J.R.R. Tolkien", "Fantasy", 310, 93, "Currently Reading", "2026-03-28", 4, "Delightful journey across Middle-earth.", "plum"),
            ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "History", 464, 0, "Want to Read", "2026-04-02", None, "Sweeping overview of human history and biology.", "forest")
        ]

        cursor.executemany("""
            INSERT INTO books (title, author, genre, total_pages, current_page, status, date_added, rating, notes, cover_style)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_books)

    # Initialize reading goal if not present
    cursor.execute("SELECT value FROM settings WHERE key = 'reading_goal_target'")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO settings (key, value) VALUES ('reading_goal_target', '12')")

    conn.commit()
    conn.close()

def book_to_dict(row):
    if not row:
        return None
    d = dict(row)
    total = d.get("total_pages", 0)
    current = d.get("current_page", 0)
    d["progress_percentage"] = round((current / total) * 100) if total > 0 else 0
    return d

def get_all_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [book_to_dict(r) for r in rows]

def get_book_by_id(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()
    return book_to_dict(row)

def create_book(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    genre = data.get("genre", "Fiction").strip()
    total_pages = int(data.get("total_pages", 0))
    current_page = int(data.get("current_page", 0))
    rating = data.get("rating")
    rating = int(rating) if rating not in (None, "", "null") else None
    notes = data.get("notes", "").strip()
    cover_style = data.get("cover_style", "forest").strip() or "forest"

    date_added = data.get("date_added")
    if not date_added or not date_added.strip():
        date_added = datetime.now().strftime("%Y-%m-%d")
    else:
        date_added = date_added.strip()

    # Determine status consistently based on progress if not explicitly provided or invalid
    status = data.get("status")
    if current_page >= total_pages:
        status = "Completed"
        current_page = total_pages
    elif current_page > 0:
        status = "Currently Reading"
    else:
        if status not in ("Want to Read", "Currently Reading", "Completed"):
            status = "Want to Read"

    cursor.execute("""
        INSERT INTO books (title, author, genre, total_pages, current_page, status, date_added, rating, notes, cover_style)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, author, genre, total_pages, current_page, status, date_added, rating, notes, cover_style))

    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_book_by_id(book_id)

def update_book(book_id, data):
    existing = get_book_by_id(book_id)
    if not existing:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()

    title = data.get("title", existing["title"]).strip()
    author = data.get("author", existing["author"]).strip()
    genre = data.get("genre", existing["genre"]).strip()
    total_pages = int(data.get("total_pages", existing["total_pages"]))
    current_page = int(data.get("current_page", existing["current_page"]))
    
    if current_page > total_pages:
        current_page = total_pages
    if current_page < 0:
        current_page = 0

    status = data.get("status", existing["status"])
    if current_page >= total_pages and total_pages > 0:
        status = "Completed"
    elif current_page > 0 and status == "Want to Read":
        status = "Currently Reading"
    elif current_page == 0 and status == "Completed":
        status = "Want to Read"

    date_added = data.get("date_added", existing["date_added"]).strip()
    rating = data.get("rating", existing["rating"])
    rating = int(rating) if rating not in (None, "", "null") else None
    notes = data.get("notes", existing.get("notes", "")).strip()
    cover_style = data.get("cover_style", existing.get("cover_style", "forest")).strip()

    cursor.execute("""
        UPDATE books
        SET title = ?, author = ?, genre = ?, total_pages = ?, current_page = ?,
            status = ?, date_added = ?, rating = ?, notes = ?, cover_style = ?
        WHERE id = ?
    """, (title, author, genre, total_pages, current_page, status, date_added, rating, notes, cover_style, book_id))

    conn.commit()
    conn.close()
    return get_book_by_id(book_id)

def update_book_progress(book_id, current_page):
    existing = get_book_by_id(book_id)
    if not existing:
        return None

    total_pages = existing["total_pages"]
    current_page = int(current_page)

    if current_page < 0 or current_page > total_pages:
        raise ValueError(f"Current page must be between 0 and {total_pages}")

    if current_page == total_pages:
        status = "Completed"
    elif current_page > 0:
        status = "Currently Reading"
    else:
        # If set to 0, if it was Completed it resets to Want to Read
        status = "Want to Read" if existing["status"] == "Completed" else existing["status"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE books
        SET current_page = ?, status = ?
        WHERE id = ?
    """, (current_page, status, book_id))
    conn.commit()
    conn.close()

    return get_book_by_id(book_id)

def delete_book(book_id):
    existing = get_book_by_id(book_id)
    if not existing:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return True

def get_reading_goal():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'reading_goal_target'")
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            return int(row["value"])
        except ValueError:
            return 12
    return 12

def set_reading_goal(target):
    target = int(target)
    if target <= 0:
        raise ValueError("Goal target must be greater than 0")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings (key, value) VALUES ('reading_goal_target', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (str(target),))
    conn.commit()
    conn.close()
    return target
