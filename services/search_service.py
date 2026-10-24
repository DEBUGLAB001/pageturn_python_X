def linear_search_books(books, query):
    """
    Performs linear search over books matching title or author.
    """
    if not query or not query.strip():
        return books

    q = query.strip().lower()
    results = []

    for book in books:
        title = (book.get("title") or "").lower()
        author = (book.get("author") or "").lower()

        if q in title or q == author:
            results.append(book)

    return results
