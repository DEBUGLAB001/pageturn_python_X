from database import get_all_books, get_reading_goal

def compute_genre_frequency(books):
    """
    Computes frequency count of books per genre using a hash map.
    """
    counts = {}
    for book in books:
        genre = (book.get("genre") or "Uncategorized").strip()
        if not genre:
            genre = "Uncategorized"

        if genre not in counts:
            counts[genre] = 0
        else:
            counts[genre] += 1

    return counts

def get_reading_statistics():
    """
    Derives reading statistics and metrics from actual stored database records.
    """
    books = get_all_books()
    total_books = len(books)
    currently_reading = sum(1 for b in books if b.get("status") == "Currently Reading")
    completed_books = sum(1 for b in books if b.get("status") == "Completed")
    want_to_read = sum(1 for b in books if b.get("status") == "Want to Read")
    total_pages_read = sum(b.get("current_page", 0) for b in books)

    goal_target = get_reading_goal()
    goal_percentage = round((completed_books / goal_target) * 100) if goal_target > 0 else 0

    genre_distribution = compute_genre_frequency(books)

    return {
        "total_books": total_books,
        "currently_reading": currently_reading,
        "completed_books": completed_books,
        "want_to_read": want_to_read,
        "total_pages_read": total_pages_read,
        "reading_goal_target": goal_target,
        "reading_goal_completed": completed_books,
        "reading_goal_percentage": goal_percentage,
        "genre_distribution": genre_distribution
    }
