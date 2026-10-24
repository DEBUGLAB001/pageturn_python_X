/* ==========================================================================
   PageTurn — Reading & Book Tracker Frontend Application Logic
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    filters: {
      q: "",
      status: "all",
      genre: "all",
      start_date: "",
      end_date: "",
      sort_by: "date_added",
      order: "desc"
    },
    books: [],
    statistics: null,
    editingBookId: null,
    progressBook: null
  };

  // DOM Elements
  const bookshelfGrid = document.getElementById("bookshelf-grid");
  const emptyState = document.getElementById("bookshelf-empty-state");
  const booksCountBadge = document.getElementById("books-count-badge");

  // Search & Filter Controls
  const inputSearch = document.getElementById("input-search");
  const btnClearSearch = document.getElementById("btn-clear-search");
  const statusSegButtons = document.querySelectorAll(".seg-btn");
  const selectGenreFilter = document.getElementById("select-genre-filter");
  const inputDateStart = document.getElementById("input-date-start");
  const inputDateEnd = document.getElementById("input-date-end");
  const btnClearDates = document.getElementById("btn-clear-dates");
  const selectSortBy = document.getElementById("select-sort-by");
  const btnToggleSortOrder = document.getElementById("btn-toggle-sort-order");
  const iconSortDesc = document.getElementById("icon-sort-desc");
  const iconSortAsc = document.getElementById("icon-sort-asc");
  const btnResetFilters = document.getElementById("btn-reset-filters");

  // Statistics & Goal Elements
  const statTotalBooks = document.getElementById("stat-total-books");
  const statReadingBooks = document.getElementById("stat-reading-books");
  const statCompletedBooks = document.getElementById("stat-completed-books");
  const statPagesRead = document.getElementById("stat-pages-read");

  const goalCompletedCount = document.getElementById("goal-completed-count");
  const goalTargetCount = document.getElementById("goal-target-count");
  const goalProgressFill = document.getElementById("goal-progress-fill");
  const goalPercentText = document.getElementById("goal-percent-text");
  const goalRemainingText = document.getElementById("goal-remaining-text");
  const navGoalPill = document.getElementById("nav-goal-pill");

  const continueReadingContent = document.getElementById("continue-reading-content");
  const continueReadingDate = document.getElementById("continue-reading-date");
  const genreDistributionContainer = document.getElementById("genre-distribution-container");

  // Modals
  const modalBook = document.getElementById("modal-book");
  const modalBookTitle = document.getElementById("modal-book-title");
  const formBook = document.getElementById("form-book");
  const bookFormId = document.getElementById("book-form-id");
  const bookInputTitle = document.getElementById("book-input-title");
  const bookInputAuthor = document.getElementById("book-input-author");
  const bookInputGenre = document.getElementById("book-input-genre");
  const bookInputTotalPages = document.getElementById("book-input-total-pages");
  const bookInputCurrentPage = document.getElementById("book-input-current-page");
  const bookInputStatus = document.getElementById("book-input-status");
  const bookInputDateAdded = document.getElementById("book-input-date-added");
  const bookInputRating = document.getElementById("book-input-rating");
  const bookInputNotes = document.getElementById("book-input-notes");

  const modalProgress = document.getElementById("modal-progress");
  const formProgress = document.getElementById("form-progress");
  const progressBookId = document.getElementById("progress-book-id");
  const progressBookTitle = document.getElementById("progress-book-title");
  const progressBookAuthor = document.getElementById("progress-book-author");
  const progressInputPage = document.getElementById("progress-input-page");
  const progressPreviewPages = document.getElementById("progress-preview-pages");
  const progressPreviewPercent = document.getElementById("progress-preview-percent");
  const progressPreviewFill = document.getElementById("progress-preview-fill");

  const modalGoal = document.getElementById("modal-goal");
  const formGoal = document.getElementById("form-goal");
  const goalInputTarget = document.getElementById("goal-input-target");

  const modalDelete = document.getElementById("modal-delete");
  const deleteBookId = document.getElementById("delete-book-id");
  const deleteBookTitle = document.getElementById("delete-book-title");
  const btnConfirmDelete = document.getElementById("btn-confirm-delete");

  // Toasts Container
  const toastContainer = document.getElementById("toast-container");

  // ==========================================
  // Toast System
  // ==========================================
  function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = `toast ${type === "error" ? "toast-error" : ""}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  // ==========================================
  // Modal Management
  // ==========================================
  function openModal(modal) {
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeModal(modal) {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  // Close modals on Esc or Backdrop click
  document.querySelectorAll(".modal-backdrop").forEach(backdrop => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) closeModal(backdrop);
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-backdrop.open").forEach(closeModal);
    }
  });

  document.getElementById("btn-close-book-modal").addEventListener("click", () => closeModal(modalBook));
  document.getElementById("btn-cancel-book-modal").addEventListener("click", () => closeModal(modalBook));

  document.getElementById("btn-close-progress-modal").addEventListener("click", () => closeModal(modalProgress));
  document.getElementById("btn-cancel-progress-modal").addEventListener("click", () => closeModal(modalProgress));

  document.getElementById("btn-close-goal-modal").addEventListener("click", () => closeModal(modalGoal));
  document.getElementById("btn-cancel-goal-modal").addEventListener("click", () => closeModal(modalGoal));

  document.getElementById("btn-close-delete-modal").addEventListener("click", () => closeModal(modalDelete));
  document.getElementById("btn-cancel-delete").addEventListener("click", () => closeModal(modalDelete));

  // ==========================================
  // Data Fetching & Rendering
  // ==========================================
  async function fetchBooks() {
    try {
      const params = new URLSearchParams();
      if (state.filters.q) params.set("q", state.filters.q);
      if (state.filters.status && state.filters.status !== "all") params.set("status", state.filters.status);
      if (state.filters.genre && state.filters.genre !== "all") params.set("genre", state.filters.genre);
      if (state.filters.start_date) params.set("start_date", state.filters.start_date);
      if (state.filters.end_date) params.set("end_date", state.filters.end_date);
      if (state.filters.sort_by) params.set("sort_by", state.filters.sort_by);
      if (state.filters.order) params.set("order", state.filters.order);

      const res = await fetch(`/api/books?${params.toString()}`);
      const data = await res.json();
      if (data.success) {
        state.books = data.books;
        renderBookshelf();
      }
    } catch (err) {
      console.error("Error loading books:", err);
      showToast("Could not load bookshelf records.", "error");
    }
  }

  async function fetchStatistics() {
    try {
      const res = await fetch("/api/statistics");
      const data = await res.json();
      if (data.success) {
        state.statistics = data.statistics;
        renderStatistics();
      }
    } catch (err) {
      console.error("Error loading statistics:", err);
    }
  }

  function renderBookshelf() {
    const count = state.books.length;
    booksCountBadge.textContent = `${count} ${count === 1 ? "book" : "books"}`;

    // Update Reset button visibility
    const hasActiveFilters = Boolean(
      state.filters.q ||
      state.filters.status !== "all" ||
      state.filters.genre !== "all" ||
      state.filters.start_date ||
      state.filters.end_date
    );
    btnResetFilters.style.display = hasActiveFilters ? "inline-flex" : "none";

    if (count === 0) {
      bookshelfGrid.innerHTML = "";
      emptyState.style.display = "flex";
      return;
    }

    emptyState.style.display = "none";
    bookshelfGrid.innerHTML = state.books.map(book => createBookCardHTML(book)).join("");

    // Attach card event listeners
    bookshelfGrid.querySelectorAll(".btn-update-progress").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id, 10);
        openProgressModalForBook(id);
      });
    });

    bookshelfGrid.querySelectorAll(".btn-edit-book").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id, 10);
        openEditBookModal(id);
      });
    });

    bookshelfGrid.querySelectorAll(".btn-delete-book").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id, 10);
        openDeleteModal(id, btn.dataset.title);
      });
    });
  }

  function createBookCardHTML(book) {
    const total = book.total_pages || 1;
    const current = book.current_page || 0;
    const pct = book.progress_percentage !== undefined ? book.progress_percentage : Math.round((current / total) * 100);

    let statusClass = "status-want";
    if (book.status === "Currently Reading") statusClass = "status-reading";
    else if (book.status === "Completed") statusClass = "status-completed";

    let ratingStars = "";
    if (book.rating) {
      ratingStars = "★".repeat(book.rating) + "☆".repeat(5 - book.rating);
    }

    const coverStyle = book.cover_style || "forest";

    return `
      <article class="book-card" data-book-id="${book.id}">
        <div class="book-card-cover cover-${coverStyle}">
          <span class="cover-genre-tag">${escapeHTML(book.genre || "Book")}</span>
          <div class="cover-title-group">
            <h4 class="cover-book-title">${escapeHTML(book.title)}</h4>
            <span class="cover-book-author">by ${escapeHTML(book.author)}</span>
          </div>
        </div>
        <div class="book-card-body">
          <div class="book-card-meta-top">
            <span class="status-badge ${statusClass}">${escapeHTML(book.status)}</span>
            ${ratingStars ? `<span class="book-card-rating" title="Rating: ${book.rating}/5">${ratingStars}</span>` : ""}
            <span class="book-card-date">${escapeHTML(book.date_added)}</span>
          </div>
          <div class="book-card-progress">
            <div class="progress-labels">
              <span>Page ${current} of ${total}</span>
              <span class="progress-pct">${pct}%</span>
            </div>
            <div class="progress-bar-track">
              <div class="progress-bar-fill progress-forest" style="width: ${Math.min(pct, 100)}%;"></div>
            </div>
          </div>
          <div class="book-card-actions">
            <button class="btn-card-action btn-update btn-update-progress" data-id="${book.id}">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
              Progress
            </button>
            <button class="btn-card-action btn-edit-book" data-id="${book.id}" title="Edit book details">Edit</button>
            <button class="btn-card-action btn-delete btn-delete-book" data-id="${book.id}" data-title="${escapeHTML(book.title)}" title="Delete book">Delete</button>
          </div>
        </div>
      </article>
    `;
  }

  function renderStatistics() {
    if (!state.statistics) return;
    const s = state.statistics;

    statTotalBooks.textContent = s.total_books;
    statReadingBooks.textContent = s.currently_reading;
    statCompletedBooks.textContent = s.completed_books;
    statPagesRead.textContent = s.total_pages_read.toLocaleString();

    // Goal
    goalCompletedCount.textContent = s.reading_goal_completed;
    goalTargetCount.textContent = s.reading_goal_target;
    const goalPct = Math.min(s.reading_goal_percentage, 100);
    goalProgressFill.style.width = `${goalPct}%`;
    goalPercentText.textContent = `${s.reading_goal_percentage}% completed`;

    const remaining = Math.max(0, s.reading_goal_target - s.reading_goal_completed);
    if (navGoalPill) {
      navGoalPill.textContent = `${s.reading_goal_percentage}%`;
    }

    // Continue Reading Section
    renderContinueReading();

    // Genre Insights
    renderGenreInsights(s.genre_distribution);
  }

  function renderContinueReading() {
    const readingBooks = state.books.filter(b => b.status === "Currently Reading");
    if (readingBooks.length === 0) {
      continueReadingDate.textContent = "";
      continueReadingContent.innerHTML = `
        <div class="featured-empty">
          <p>No book is currently in progress. Select a title from your bookshelf to begin reading.</p>
        </div>
      `;
      return;
    }

    // Pick book with highest reading progress percentage
    readingBooks.sort((a, b) => {
      const pa = (a.current_page / a.total_pages) || 0;
      const pb = (b.current_page / b.total_pages) || 0;
      return pb - pa;
    });

    const activeBook = readingBooks[0];
    const pct = activeBook.progress_percentage !== undefined ? activeBook.progress_percentage : Math.round((activeBook.current_page / activeBook.total_pages) * 100);
    const coverStyle = activeBook.cover_style || "amber";

    continueReadingDate.textContent = `Started ${activeBook.date_added}`;
    continueReadingContent.innerHTML = `
      <div class="featured-book-item">
        <div class="featured-book-cover cover-${coverStyle}">
          <span class="cover-genre-tag">${escapeHTML(activeBook.genre)}</span>
          <div class="cover-title-group">
            <strong style="font-size: 13px; line-height: 1.2;">${escapeHTML(activeBook.title)}</strong>
          </div>
        </div>
        <div class="featured-book-info">
          <h4 class="featured-book-title">${escapeHTML(activeBook.title)}</h4>
          <span class="featured-book-author">by ${escapeHTML(activeBook.author)}</span>
          <div class="featured-book-progress-wrap">
            <div class="featured-progress-stats">
              <span>Page ${activeBook.current_page} of ${activeBook.total_pages}</span>
              <span class="fw-semibold text-forest">${pct}% complete</span>
            </div>
            <div class="progress-bar-track">
              <div class="progress-bar-fill progress-amber" style="width: ${Math.min(pct, 100)}%;"></div>
            </div>
          </div>
          <div>
            <button id="btn-continue-reading-action" class="btn btn-primary btn-sm">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-right: 6px;"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
              Update Reading Progress
            </button>
          </div>
        </div>
      </div>
    `;

    document.getElementById("btn-continue-reading-action")?.addEventListener("click", () => {
      openProgressModalForBook(activeBook.id);
    });
  }

  function renderGenreInsights(distribution) {
    if (!distribution || Object.keys(distribution).length === 0) {
      genreDistributionContainer.innerHTML = `<span class="text-muted text-sm">No genre data available yet.</span>`;
      return;
    }

    const items = Object.entries(distribution).sort((a, b) => b[1] - a[1]);
    genreDistributionContainer.innerHTML = items.map(([genre, count]) => `
      <div class="genre-chip" title="${count} ${count === 1 ? 'book' : 'books'} in ${escapeHTML(genre)}">
        <span>${escapeHTML(genre)}</span>
        <span class="genre-chip-badge">${count}</span>
      </div>
    `).join("");
  }

  function escapeHTML(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // ==========================================
  // Filter & Search Controls Listeners
  // ==========================================
  let searchTimeout = null;
  inputSearch.addEventListener("input", () => {
    btnClearSearch.style.display = inputSearch.value ? "inline-block" : "none";
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      state.filters.q = inputSearch.value;
      fetchBooks();
    }, 250);
  });

  btnClearSearch.addEventListener("click", () => {
    inputSearch.value = "";
    btnClearSearch.style.display = "none";
    state.filters.q = "";
    fetchBooks();
  });

  statusSegButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      statusSegButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.filters.status = btn.dataset.status;
      fetchBooks();
    });
  });

  selectGenreFilter.addEventListener("change", () => {
    state.filters.genre = selectGenreFilter.value;
    fetchBooks();
  });

  function handleDateChange() {
    state.filters.start_date = inputDateStart.value;
    state.filters.end_date = inputDateEnd.value;
    btnClearDates.style.display = (inputDateStart.value || inputDateEnd.value) ? "inline-block" : "none";
    fetchBooks();
  }

  inputDateStart.addEventListener("change", handleDateChange);
  inputDateEnd.addEventListener("change", handleDateChange);

  btnClearDates.addEventListener("click", () => {
    inputDateStart.value = "";
    inputDateEnd.value = "";
    btnClearDates.style.display = "none";
    state.filters.start_date = "";
    state.filters.end_date = "";
    fetchBooks();
  });

  selectSortBy.addEventListener("change", () => {
    state.filters.sort_by = selectSortBy.value;
    fetchBooks();
  });

  btnToggleSortOrder.addEventListener("click", () => {
    const isDesc = state.filters.order === "desc";
    state.filters.order = isDesc ? "asc" : "desc";
    btnToggleSortOrder.dataset.order = state.filters.order;
    iconSortDesc.style.display = isDesc ? "none" : "block";
    iconSortAsc.style.display = isDesc ? "block" : "none";
    fetchBooks();
  });

  btnResetFilters.addEventListener("click", () => {
    state.filters.q = "";
    state.filters.status = "all";
    state.filters.genre = "all";
    state.filters.start_date = "";
    state.filters.end_date = "";

    inputSearch.value = "";
    btnClearSearch.style.display = "none";
    statusSegButtons.forEach(b => b.classList.toggle("active", b.dataset.status === "all"));
    selectGenreFilter.value = "all";
    inputDateStart.value = "";
    inputDateEnd.value = "";
    btnClearDates.style.display = "none";

    fetchBooks();
  });

  document.getElementById("btn-empty-clear-filters")?.addEventListener("click", () => {
    btnResetFilters.click();
  });

  // ==========================================
  // Add / Edit Book Modal
  // ==========================================
  document.getElementById("btn-open-add-book").addEventListener("click", () => {
    openAddBookModal();
  });
  document.getElementById("btn-empty-add-book")?.addEventListener("click", () => {
    openAddBookModal();
  });

  function openAddBookModal() {
    state.editingBookId = null;
    modalBookTitle.textContent = "Add New Book";
    formBook.reset();
    bookFormId.value = "";
    bookInputDateAdded.value = new Date().toISOString().split("T")[0];
    document.querySelector('input[name="cover_style"][value="forest"]').checked = true;
    clearFormErrors();
    openModal(modalBook);
    bookInputTitle.focus();
  }

  function openEditBookModal(bookId) {
    const book = state.books.find(b => b.id === bookId);
    if (!book) return;

    state.editingBookId = bookId;
    modalBookTitle.textContent = "Edit Book";
    clearFormErrors();

    bookFormId.value = book.id;
    bookInputTitle.value = book.title;
    bookInputAuthor.value = book.author;
    bookInputGenre.value = book.genre;
    bookInputTotalPages.value = book.total_pages;
    bookInputCurrentPage.value = book.current_page;
    bookInputStatus.value = book.status;
    bookInputDateAdded.value = book.date_added;
    bookInputRating.value = book.rating || "";
    bookInputNotes.value = book.notes || "";

    const style = book.cover_style || "forest";
    const radio = document.querySelector(`input[name="cover_style"][value="${style}"]`);
    if (radio) radio.checked = true;

    openModal(modalBook);
    bookInputTitle.focus();
  }

  function clearFormErrors() {
    document.querySelectorAll(".form-error").forEach(el => el.textContent = "");
  }

  formBook.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearFormErrors();

    const title = bookInputTitle.value.trim();
    const author = bookInputAuthor.value.trim();
    const genre = bookInputGenre.value.trim();
    const totalPages = parseInt(bookInputTotalPages.value, 10);
    const currentPage = parseInt(bookInputCurrentPage.value || "0", 10);

    let hasError = false;
    if (!title) {
      document.getElementById("error-title").textContent = "Title is required.";
      hasError = true;
    }
    if (!author) {
      document.getElementById("error-author").textContent = "Author is required.";
      hasError = true;
    }
    if (isNaN(totalPages) || totalPages <= 0) {
      document.getElementById("error-total-pages").textContent = "Total pages must be greater than 0.";
      hasError = true;
    }
    if (isNaN(currentPage) || currentPage < 0 || currentPage > totalPages) {
      document.getElementById("error-current-page").textContent = `Current page must be between 0 and ${totalPages}.`;
      hasError = true;
    }

    if (hasError) return;

    const payload = {
      title,
      author,
      genre,
      total_pages: totalPages,
      current_page: currentPage,
      status: bookInputStatus.value,
      date_added: bookInputDateAdded.value,
      rating: bookInputRating.value ? parseInt(bookInputRating.value, 10) : null,
      notes: bookInputNotes.value.trim(),
      cover_style: document.querySelector('input[name="cover_style"]:checked')?.value || "forest"
    };

    try {
      let res;
      if (state.editingBookId) {
        res = await fetch(`/api/books/${state.editingBookId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      } else {
        res = await fetch("/api/books", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      }

      const data = await res.json();
      if (data.success) {
        closeModal(modalBook);
        showToast(state.editingBookId ? "Book details updated." : "Book added to your shelf.");
        await fetchBooks();
        await fetchStatistics();
      } else {
        showToast(data.error || "Failed to save book.", "error");
      }
    } catch (err) {
      console.error(err);
      showToast("An error occurred while saving the book.", "error");
    }
  });

  // ==========================================
  // Progress Modal
  // ==========================================
  function openProgressModalForBook(bookId) {
    const book = state.books.find(b => b.id === bookId);
    if (!book) return;

    state.progressBook = book;
    progressBookId.value = book.id;
    progressBookTitle.textContent = book.title;
    progressBookAuthor.textContent = `by ${book.author}`;
    progressInputPage.max = book.total_pages;
    progressInputPage.value = book.current_page;
    document.getElementById("error-progress-page").textContent = "";

    updateProgressPreview(book.current_page, book.total_pages);
    openModal(modalProgress);
    progressInputPage.focus();
  }

  function updateProgressPreview(current, total) {
    current = Math.max(0, Math.min(current, total));
    const pct = total > 0 ? Math.round((current / total) * 100) : 0;
    progressPreviewPages.textContent = `Page ${current} of ${total}`;
    progressPreviewPercent.textContent = `${pct}%`;
    progressPreviewFill.style.width = `${pct}%`;
  }

  progressInputPage.addEventListener("input", () => {
    if (!state.progressBook) return;
    const current = parseInt(progressInputPage.value || "0", 10);
    updateProgressPreview(current, state.progressBook.total_pages);
  });

  window.adjustProgressPage = function(delta) {
    if (!state.progressBook) return;
    let current = parseInt(progressInputPage.value || "0", 10) + delta;
    current = Math.max(0, Math.min(current, state.progressBook.total_pages));
    progressInputPage.value = current;
    updateProgressPreview(current, state.progressBook.total_pages);
  };

  window.setProgressPageToTotal = function() {
    if (!state.progressBook) return;
    progressInputPage.value = state.progressBook.total_pages;
    updateProgressPreview(state.progressBook.total_pages, state.progressBook.total_pages);
  };

  formProgress.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.progressBook) return;

    const current = parseInt(progressInputPage.value, 10);
    const total = state.progressBook.total_pages;

    if (isNaN(current) || current < 0 || current > total) {
      document.getElementById("error-progress-page").textContent = `Page must be between 0 and ${total}.`;
      return;
    }

    try {
      const res = await fetch(`/api/books/${state.progressBook.id}/progress`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_page: current })
      });
      const data = await res.json();
      if (data.success) {
        closeModal(modalProgress);
        showToast("Reading progress updated.");
        await fetchBooks();
        await fetchStatistics();
      } else {
        document.getElementById("error-progress-page").textContent = data.error || "Update failed.";
      }
    } catch (err) {
      console.error(err);
      showToast("Error updating reading progress.", "error");
    }
  });

  // ==========================================
  // Reading Goal Modal
  // ==========================================
  document.getElementById("btn-open-goal")?.addEventListener("click", () => {
    openGoalModal();
  });
  document.getElementById("btn-edit-goal-trigger")?.addEventListener("click", () => {
    openGoalModal();
  });

  function openGoalModal() {
    if (state.statistics) {
      goalInputTarget.value = state.statistics.reading_goal_target;
    }
    document.getElementById("error-goal-target").textContent = "";
    openModal(modalGoal);
    goalInputTarget.focus();
  }

  formGoal.addEventListener("submit", async (e) => {
    e.preventDefault();
    const target = parseInt(goalInputTarget.value, 10);
    if (isNaN(target) || target <= 0) {
      document.getElementById("error-goal-target").textContent = "Goal target must be greater than 0.";
      return;
    }

    try {
      const res = await fetch("/api/goal", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target })
      });
      const data = await res.json();
      if (data.success) {
        closeModal(modalGoal);
        showToast(`Annual goal set to ${target} books.`);
        await fetchStatistics();
      } else {
        document.getElementById("error-goal-target").textContent = data.error || "Update failed.";
      }
    } catch (err) {
      console.error(err);
      showToast("Could not update goal target.", "error");
    }
  });

  // ==========================================
  // Delete Book Modal
  // ==========================================
  function openDeleteModal(bookId, bookTitle) {
    deleteBookId.value = bookId;
    deleteBookTitle.textContent = `"${bookTitle}"`;
    openModal(modalDelete);
  }

  btnConfirmDelete.addEventListener("click", async () => {
    const bookId = parseInt(deleteBookId.value, 10);
    if (!bookId) return;

    try {
      const res = await fetch(`/api/books/${bookId}`, {
        method: "DELETE"
      });
      const data = await res.json();
      if (data.success) {
        closeModal(modalDelete);
        showToast("Book removed from shelf.");
        await fetchBooks();
        await fetchStatistics();
      } else {
        showToast(data.error || "Could not delete book.", "error");
      }
    } catch (err) {
      console.error(err);
      showToast("Error deleting book.", "error");
    }
  });

  // ==========================================
  // MINICOM Dialogue Slider
  // ==========================================
  const minicomDialogues = [
    "Hi, I'm MINICOM! Your bookshelf is looking peaceful today.<br>Pick a book, flip some pages, and keep your reading streak alive! <span id='btn-dialogue-next' class='dialogue-arrow' title='Next message'>▶</span>",
    "Quiet reading corner tip:<br>Even 15 minutes a day finishes over 20 books a year! <span id='btn-dialogue-next' class='dialogue-arrow' title='Next message'>▶</span>",
    "Looking for your next read?<br>Filter by genre or track your progress across chapters! <span id='btn-dialogue-next' class='dialogue-arrow' title='Next message'>▶</span>"
  ];

  let currentDialogueIndex = 0;
  const dialogueEl = document.getElementById("minicom-dialogue");
  const counterEl = document.getElementById("bubble-slide-counter");
  const dots = document.querySelectorAll(".bubble-dots .b-dot");

  function setDialogue(index) {
    currentDialogueIndex = (index + minicomDialogues.length) % minicomDialogues.length;
    if (dialogueEl) {
      dialogueEl.innerHTML = minicomDialogues[currentDialogueIndex];
      // re-attach arrow listener
      dialogueEl.querySelector("#btn-dialogue-next")?.addEventListener("click", () => {
        setDialogue(currentDialogueIndex + 1);
      });
    }
    if (counterEl) {
      counterEl.textContent = `${currentDialogueIndex + 1} of ${minicomDialogues.length}`;
    }
    dots.forEach((dot, idx) => {
      dot.classList.toggle("active", idx === currentDialogueIndex);
    });
  }

  dots.forEach(dot => {
    dot.addEventListener("click", () => {
      const idx = parseInt(dot.dataset.slide, 10);
      setDialogue(idx);
    });
  });

  dialogueEl?.querySelector("#btn-dialogue-next")?.addEventListener("click", () => {
    setDialogue(currentDialogueIndex + 1);
  });


  // ==========================================
  // Initial Boot
  // ==========================================
  fetchBooks();
  fetchStatistics();
});
