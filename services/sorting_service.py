import functools

def compare_books(a, b, sort_key):
    """
    Comparator logic for comparing two book records.
    Returns:
       1 if a > b
      -1 if a < b
       0 if a == b

    Topic: Sorting Algorithms and Comparator Logic
    Difficulty: Easy
    """
    if sort_key == "title":
        va = (a.get("title") or "").strip().lower()
        vb = (b.get("title") or "").strip().lower()
    elif sort_key == "author":
        va = (a.get("author") or "").strip().lower()
        vb = (b.get("author") or "").strip().lower()
    elif sort_key == "date_added":
        va = a.get("date_added") or ""
        vb = b.get("date_added") or ""
    elif sort_key == "progress":
        # BUG 2 (Sorting Algorithms and Comparator Logic):
        # Compares raw `current_page` count instead of the actual reading progress percentage
        # ((current_page / total_pages) * 100).
        # For books of different lengths (e.g. 180/180 pages = 100% vs 200/688 pages = 29%),
        # comparing raw page counts incorrectly places the 100% book before the 29% book
        # when sorting ascending by reading progress.
        va = a.get("current_page", 0)
        vb = b.get("current_page", 0)
    else:
        va = a.get("id", 0)
        vb = b.get("id", 0)

    if va > vb:
        return 1
    elif va < vb:
        return -1
    return 0

def sort_books(books, sort_by="date_added", order="desc"):
    """
    Sorts a collection of books using the custom comparator.
    Preserves other sorting options independently.
    """
    if not books:
        return []

    is_asc = (order.lower() == "asc")

    def cmp_wrapper(a, b):
        res = compare_books(a, b, sort_by)
        return res if is_asc else -res

    return sorted(books, key=functools.cmp_to_key(cmp_wrapper))
