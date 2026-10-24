def binary_search_lower_bound(sorted_books, target_date):
    """
    Finds the first index where book['date_added'] >= target_date.
    Uses binary search over sorted date entries.
    """
    low = 0
    high = len(sorted_books)
    while low < high:
        mid = (low + high) // 2
        if sorted_books[mid]["date_added"] < target_date:
            low = mid + 1
        else:
            high = mid
    return low

def binary_search_upper_bound(sorted_books, target_date):
    """
    Finds the insertion point (exclusive upper bound) where all elements before this index
    have book['date_added'] <= target_date.
    """
    low = 0
    high = len(sorted_books)
    while low < high:
        mid = (low + high) // 2
        if sorted_books[mid]["date_added"] < target_date:
            low = mid + 1
        else:
            high = mid
    return low

def filter_books_by_date_range(books, start_date=None, end_date=None):
    """
    Filters a book collection by date added using binary search range selection.
    The input books are sorted by `date_added` before applying binary search bounds.
    """
    if not books:
        return []
    if not start_date and not end_date:
        return books

    # Ensure books are sorted by date_added for binary search
    sorted_books = sorted(books, key=lambda b: b.get("date_added", ""))
    n = len(sorted_books)

    start_idx = 0
    if start_date and start_date.strip():
        start_idx = binary_search_lower_bound(sorted_books, start_date.strip())

    end_idx = n
    if end_date and end_date.strip():
        end_idx = binary_search_upper_bound(sorted_books, end_date.strip())

    if start_idx >= end_idx:
        return []

    return sorted_books[start_idx:end_idx]
