def linear_search_books(books, query):
    """
    Performs linear search over books matching title or author.

    Topic: Linear Search
    Difficulty: Easy
    """
    if not query or not query.strip():
        return books

    q = query.strip().lower()
    results = []

    for book in books:
        title = (book.get("title") or "").lower()
        author = (book.get("author") or "").lower()

        # BUG 1 (Linear Search):
        # The linear search predicate checks title with substring containment (`q in title`),
        # but checks author with exact string equality (`q == author`) instead of substring (`q in author`).
        # This causes valid searches by author surname or partial author name (e.g., 'Orwell', 'Austen', 'Tolkien')
        # to fail to match books written by 'George Orwell', 'Jane Austen', 'J.R.R. Tolkien'.
        if q in title or q == author:
            results.append(book)

    return results
