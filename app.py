"""
app.py
------
Runs the whole Bookmarked app: serves the frontend (frontend/) and the
recommendation API from a single Flask process.

Run with:
    python app.py

Then open:
    http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify

from recommender import BookRecommender

app = Flask(__name__, static_folder="frontend", static_url_path="")
engine = BookRecommender()


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}
    preferences = data.get("books", [])

    if not isinstance(preferences, list):
        return jsonify({"error": "books must be a list of strings"}), 400

    return jsonify(engine.recommend(preferences)), 200


@app.route("/api/titles", methods=["GET"])
def titles():
    """All book titles in the dataset, used for the search autocomplete."""
    return jsonify({"titles": sorted(engine.df["title"].tolist())})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
