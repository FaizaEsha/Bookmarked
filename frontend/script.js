// Bookmarked — frontend logic
// Served by app.py, so API calls are same-origin (no base URL needed).

// ---------- View switching ----------
const views = {
  home: document.getElementById("view-home"),
  results: document.getElementById("view-results"),
  how: document.getElementById("view-how"),
};

const navLinks = document.querySelectorAll(".nav-link");

function showView(name) {
  Object.entries(views).forEach(([key, el]) => {
    el.hidden = key !== name;
  });
  navLinks.forEach((link) => {
    link.classList.toggle("active", link.dataset.view === name);
  });
}

navLinks.forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    showView(link.dataset.view);
  });
});

document.getElementById("back-to-search").addEventListener("click", () => {
  showView("home");
});

// ---------- Autocomplete: load supported titles ----------
(async function loadTitles() {
  try {
    const res = await fetch(`/api/titles`);
    const data = await res.json();
    const datalist = document.getElementById("book-titles");
    data.titles.forEach((title) => {
      const option = document.createElement("option");
      option.value = title;
      datalist.appendChild(option);
    });
  } catch (err) {
    // Autocomplete is a nice-to-have; fail silently if the backend isn't up yet.
  }
})();

// ---------- Form handling ----------
const form = document.getElementById("preference-form");
const formError = document.getElementById("form-error");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const inputs = Array.from(document.querySelectorAll(".pref-input"));
  const values = inputs.map((input) => input.value.trim()).filter(Boolean);

  if (values.length === 0) {
    formError.hidden = false;
    return;
  }
  formError.hidden = true;

  showView("results");
  setResultsState("loading");

  try {
    const response = await fetch(`/api/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ books: values }),
    });

    const data = await response.json();

    if (data.error) {
      showEmptyState(data.error);
      return;
    }

    renderResults(data);
  } catch (err) {
    showEmptyState(
      "Couldn't reach the recommendation engine. Make sure the backend server is running."
    );
  }
});

// ---------- Results rendering ----------
function setResultsState(state) {
  document.getElementById("results-loading").hidden = state !== "loading";
  document.getElementById("results-content").hidden = state !== "content";
  document.getElementById("results-empty").hidden = state !== "empty";
}

function showEmptyState(message) {
  document.getElementById("results-empty-message").textContent = message;
  setResultsState("empty");
}

function renderResults(data) {
  document.getElementById("based-on-list").textContent = data.based_on.join(" · ");

  const cardsContainer = document.getElementById("results-cards");
  cardsContainer.innerHTML = "";

  data.recommendations.forEach((book, i) => {
    const card = document.createElement("div");
    card.className = "book-card";
    card.style.animationDelay = `${i * 80}ms`;

    card.innerHTML = `
      <div class="book-rank">0${book.rank}</div>
      <div class="book-title">${escapeHtml(book.title)}</div>
      <div class="book-author">${escapeHtml(book.author)}</div>
      <div class="book-genre">${escapeHtml(book.genre)}</div>
      <div class="book-match">${book.match_percentage}% match</div>
      <div class="book-why-label">Why this book?</div>
      <div class="book-why">${escapeHtml(book.why)}</div>
    `;

    cardsContainer.appendChild(card);
  });

  setResultsState("content");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
