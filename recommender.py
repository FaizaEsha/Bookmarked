"""
recommender.py
---------------
The heart of Bookmarked: a content-based book recommender.

Pipeline:
1. Ingestion   -> take ~3 book titles / preferences from the user
2. Scoring     -> convert text into TF-IDF vectors
3. Similarity  -> compare the user's profile vector to every book using
                  cosine similarity
4. Filtering   -> rank all candidates and return the Top 3

No neural networks, embeddings, or collaborative filtering -- just
TF-IDF + cosine similarity, as specified.
"""

import os
import re
import difflib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "books.csv")


# ---------- text cleaning ----------

def clean_text(text: str) -> str:
    """Lowercase, remove punctuation/digits noise, collapse whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_document(genre: str, description: str) -> str:
    """Combine a book's genre + description into one text document.
    Genre is repeated to give it a bit more weight in the TF-IDF space.
    """
    genre_clean = clean_text(genre)
    description_clean = clean_text(description)
    return f"{genre_clean} {genre_clean} {description_clean}"


# ---------- recommender ----------

class BookRecommender:
    def __init__(self, dataset_path: str = DATASET_PATH):
        self.df = pd.read_csv(dataset_path)
        self.df["document"] = self.df.apply(
            lambda row: build_document(row["genre"], row["description"]), axis=1
        )

        # Step 2: Scoring (TF-IDF) -- rare/specific words get more weight,
        # common words get less, automatically.
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.book_vectors = self.vectorizer.fit_transform(self.df["document"])

    def _find_matching_book(self, query: str):
        """Match a user-provided title to a book in the dataset."""
        query_clean = query.strip().lower()
        if not query_clean:
            return None

        exact = self.df[self.df["title"].str.lower() == query_clean]
        if not exact.empty:
            return exact.iloc[0]

        partial = self.df[self.df["title"].str.lower().str.contains(query_clean, na=False)]
        if not partial.empty:
            return partial.iloc[0]

        # fuzzy match against the start of each title, for typos like
        # "hary poter" or "percy jakson"
        best_score, best_index = 0.0, None
        for i, title_lower in enumerate(self.df["title"].str.lower()):
            prefix = title_lower[: len(query_clean) + 5]
            score = difflib.SequenceMatcher(None, query_clean, prefix).ratio()
            if score > best_score:
                best_score, best_index = score, i

        if best_index is not None and best_score >= 0.72:
            return self.df.iloc[best_index]

        return None

    def _build_user_document(self, preferences):
        """Step 1: Ingestion. Turn ~3 preferences into one text document."""
        matched_titles = []
        combined_text_parts = []

        for pref in preferences:
            match = self._find_matching_book(pref)
            if match is not None:
                matched_titles.append(match["title"])
                combined_text_parts.append(match["document"])
            else:
                combined_text_parts.append(clean_text(pref))

        return " ".join(combined_text_parts), matched_titles

    def _explain(self, user_vector, book_index):
        """Short explanation grounded in actual shared TF-IDF terms."""
        feature_names = self.vectorizer.get_feature_names_out()
        user_row = user_vector.toarray()[0]
        book_row = self.book_vectors[book_index].toarray()[0]

        shared = [i for i in range(len(feature_names)) if user_row[i] > 0 and book_row[i] > 0]
        shared.sort(key=lambda i: book_row[i], reverse=True)
        top_terms = [feature_names[i] for i in shared[:3]]

        if top_terms:
            return f"Shares strong thematic overlap with your preferences around: {', '.join(top_terms)}."
        return "Shares general genre and stylistic similarity with your preferences."

    def recommend(self, preferences, top_n: int = 3):
        """Steps 1-4 end to end. Returns top_n recommendations."""
        preferences = [p for p in preferences if p and p.strip()]
        if not preferences:
            return {"error": "Please provide at least one book or preference."}

        user_document, matched_titles = self._build_user_document(preferences)
        if not user_document.strip():
            return {"error": "Could not understand the provided preferences."}

        # Step 2 (continued): vectorize the user profile
        user_vector = self.vectorizer.transform([user_document])

        # Step 3: Similarity
        similarities = cosine_similarity(user_vector, self.book_vectors)[0]

        exclude_titles = set(t.lower() for t in matched_titles)
        scored = [
            (idx, score) for idx, score in enumerate(similarities)
            if self.df.iloc[idx]["title"].lower() not in exclude_titles
        ]

        # Step 4: Filtering (rank + keep Top N)
        scored.sort(key=lambda x: x[1], reverse=True)
        top_matches = scored[:top_n]

        if not top_matches or top_matches[0][1] == 0:
            return {"error": "No suitable recommendations found for these preferences. Try different books."}

        results = []
        for rank, (idx, score) in enumerate(top_matches, start=1):
            row = self.df.iloc[idx]
            results.append({
                "rank": rank,
                "title": row["title"],
                "author": row["author"],
                "genre": row["genre"],
                "match_percentage": round(float(score) * 100, 1),
                "why": self._explain(user_vector, idx),
            })

        return {
            "based_on": matched_titles if matched_titles else preferences,
            "recommendations": results,
        }


if __name__ == "__main__":
    import json
    engine = BookRecommender()
    print(json.dumps(engine.recommend(["Harry Potter", "The Hobbit", "Percy Jackson"]), indent=2))
