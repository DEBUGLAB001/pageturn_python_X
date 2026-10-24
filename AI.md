# PageTurn

## Description
PageTurn is a personal reading tracker and bookshelf management web application built with Python and Flask. The application enables users to catalog books, track page progress, filter by genre or date added, search titles and authors, and set annual reading goals with real-time statistics. Application initialization is handled in `app.py` via the `create_app()` factory, binding to `0.0.0.0:5000`. Persistence is managed through SQLite in `database.py` (`pageturn.db`). Dedicated services handle business logic: `services/search_service.py` executes linear search queries, `services/sorting_service.py` handles custom comparator-based sorting, `services/statistics_service.py` calculates reading metrics and genre distributions via hash maps, and `services/range_service.py` performs binary-search-based date-range filtering. The frontend is served via `templates/index.html` and managed by vanilla JavaScript in `static/js/app.js` with responsive CSS styling in `static/css/style.css`.

## Repository Structure
```
.
├── app.py                      # Flask application factory and server entry point
├── challenge.json              # Challenge metadata and runtime configuration
├── database.py                 # SQLite database schema, operations, and seed data
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── routes/
│   ├── api_routes.py           # REST API endpoints for books, goals, and stats
│   └── view_routes.py          # View route serving index.html
├── services/
│   ├── range_service.py        # Binary search date-range filtering logic
│   ├── search_service.py       # Linear search implementation for books
│   ├── sorting_service.py      # Book sorting and comparator logic
│   └── statistics_service.py   # Reading statistics and genre frequency counting
├── static/
│   ├── css/
│   │   └── style.css           # Styling, design tokens, and responsive layout
│   └── js/
│       └── app.js              # Client state, dynamic rendering, and API interaction
└── templates/
    ├── 404.html                # Not found error page
    ├── 500.html                # Server error page
    └── index.html              # Main application template and modal markup
```

## Bugs and Bug Locations

1. Incorrect Author Matching in Linear Search
- Bug location: `services/search_service.py`, within `linear_search_books()` on lines 23–24.
- How to observe it: Enter an author surname such as `"Orwell"` or `"Austen"` into the search field or make a `GET /api/books?q=Orwell` request.
- Failure: Valid books matching the author are omitted from results because the author match checks exact equality (`q == author`) rather than substring containment (`q in author`).
- Expected: Linear search should return any book where the query string is contained within the title or author case-insensitively.

2. Inverted Reading Progress Comparator Logic
- Bug location: `services/sorting_service.py`, within `compare_books()` on lines 30–31.
- How to observe it: Select "Sort: Reading Progress", set the sort direction to Ascending, and view the book list or make a `GET /api/books?sort_by=progress&order=asc` request.
- Failure: Books with 100% completion (such as *The Great Gatsby* at 180/180 pages) appear before books with lower completion percentages (such as *Dune* at 200/688 pages, 29%) because the comparator compares raw `current_page` integers instead of completion percentage.
- Expected: Sorting by progress in ascending order should order books strictly by completion percentage `(current_page / total_pages * 100)` from lowest to highest.

3. Off-by-One Hash Map Frequency Counting in Genre Insights
- Bug location: `services/statistics_service.py`, within `compute_genre_frequency()` on lines 20–23.
- How to observe it: Examine the "Genre Insights" section on the dashboard or inspect the `genre_distribution` field returned by `GET /api/statistics`.
- Failure: Any genre represented by a single book (such as Romance or Non-Fiction) displays a count of `0` books, and all genre counts are undercounted by one because new genres in the frequency dictionary are initialized to `0` instead of `1` upon first discovery.
- Expected: The genre frequency hash map should initialize new genre occurrences to count `1` (or increment existing counts), displaying accurate counts for every genre in the library.

4. Binary Search Upper Boundary Exclusion in Date Range Filter
- Bug location: `services/range_service.py`, within `binary_search_upper_bound()` on line 34.
- How to observe it: Filter books by setting "From" to `2026-02-01` and "To" to `2026-03-15`, or call `GET /api/books?start_date=2026-02-01&end_date=2026-03-15`.
- Failure: Books added on the exact end date boundary (*Atomic Habits*, added on `2026-03-15`) are excluded because the binary search condition uses strict `<` instead of `<=`, setting `high = mid` on equality and causing the upper bound slice index to drop boundary records.
- Expected: The binary search upper bound should include books whose `date_added` matches `end_date`, correctly capturing the full closed interval `[start_date, end_date]`.
