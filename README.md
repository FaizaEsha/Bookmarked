# 📚 Bookmarked

**Find your next read.**

A content-based book recommendation engine — tell it three books you love, and it uses TF‑IDF and cosine similarity to find what to read next. No collaborative filtering, no black-box neural nets, just clean, interpretable similarity math wrapped in a UI that doesn't feel like a school project.

---

## ✨ What it does

Type in a few books you've enjoyed. Bookmarked reads each one's genre and description, turns them into weighted numerical vectors, and compares that against every book in its dataset to surface the three closest matches — along with a short, honest explanation of *why* each one was picked.

- 🔍 **Live autocomplete** as you type, pulled straight from the dataset
- 🧠 **Typo-tolerant matching** — `hary poter` still resolves to *Harry Potter and the Sorcerer's Stone*
- 🎯 **Grounded explanations** — the "why this book" line is generated from real shared TF‑IDF terms, not a canned sentence
- 🚫 **Graceful failure** — unrelated gibberish input returns an honest "no suitable recommendations" instead of faking a result
- 🎨 A full, from-scratch frontend — because a recommender engine deserves better than a terminal print statement

## 🧩 How it works

```
User Input (1–3 books)
        ↓
TF-IDF Vectorization        → genre + description become weighted vectors
        ↓
Cosine Similarity           → compare the user's profile against every book
        ↓
Rank & Filter                → sort by score, keep the Top 3
        ↓
Frontend Results
```

Genre is weighted more heavily than description in the vector space, so recommendations stay thematically tight rather than drifting on loose descriptive language alone.

## 🛠️ Tech stack

| Layer | Tools |
|---|---|
| Recommendation engine | Python, `scikit-learn` (TF‑IDF + cosine similarity), `pandas` |
| Backend / API | Flask |
| Frontend | HTML, CSS, vanilla JS — no framework, no build step |

## 📂 Project structure

```
bookmarked/
├── data/
│   └── books.csv        # title, author, genre, description (~70 books)
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── app.py                # Flask app — serves the frontend + the API
├── recommender.py        # TF-IDF + cosine similarity engine
├── requirements.txt
└── README.md
```

`recommender.py` holds all the recommendation logic in isolation; `app.py` just exposes it over HTTP and serves the static frontend. The frontend never touches Python directly — it only talks to the API.

## 🚀 Getting started

```bash
git clone https://github.com/<your-username>/bookmarked.git
cd bookmarked
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** — one process serves both the app and the API.

## 🧪 Try it

Bookmarked only recognizes the ~70 books in `data/books.csv` (it's content-based, so it can't reason about titles it's never seen). A few to get started:

`Harry Potter and the Sorcerer's Stone` · `The Hobbit` · `1984` · `Dune` · `Pride and Prejudice` · `Gone Girl` · `Sapiens: A Brief History of Humankind`

A full set of ready-to-paste test combos (fantasy, dystopian, sci-fi, classics, thrillers) and edge cases — typos, unknown titles, total nonsense — is included in [`test-inputs.pdf`](./test-inputs.pdf).

## ⚠️ Limitations

This is a content-based recommender — it only understands the genre and description text in the dataset. It doesn't use ratings, purchase history, or collaborative filtering, so:

- Recommendations are only as good as the dataset's metadata.
- Titles outside the dataset are matched using raw typed text, which is a weaker signal than a real match.
- Two thematically similar books described in very different vocabulary may not score highly against each other.

## 🌱 About

Built as Project 3 (AI Recommendation Logic) for the DecodeLabs AI Engineering Internship — a hands-on exercise in feature extraction and similarity-based ranking, taken a step further with a proper frontend.

## ✍️ Author

**Faiza Ahmed Esha**
