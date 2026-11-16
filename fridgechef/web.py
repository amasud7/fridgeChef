"""Flask front end for ingredient-based recipe search."""

from pathlib import Path

from flask import Flask, render_template, request

from .index import RecipeIndex
from .normalize import parse_query
from .ranker import search

DEFAULT_DATA = Path(__file__).resolve().parents[1] / "data" / "sample_recipes.csv"
MISSING_LIMITS = [1, 2, 3, 5]
TOP_K = 8

app = Flask(__name__)

# Built once at import rather than per request: the postings lists and average
# document length do not depend on the query.
index = RecipeIndex.from_csv(DEFAULT_DATA)


@app.route("/")
def home():
    """Render the search form, and the ranking underneath it once there is a query.

    Everything the page needs is in the query string, so a search can be
    bookmarked or shared and the back button steps through past fridges.
    """
    submitted = "submitted" in request.args
    raw = request.args.get("ingredients", "").strip()
    limit = request.args.get("max_missing", "3")

    # An unchecked checkbox sends nothing, which on its own is indistinguishable
    # from a first visit. The hidden submitted field tells the two apart.
    assume_staples = ("staples" in request.args) if submitted else True

    query = parse_query(raw)
    results = []
    unrecognized = []
    if query:
        unrecognized = [term for term in query if not index.df(term)]
        results = search(
            query,
            index,
            top_k=TOP_K,
            max_missing=int(limit) if limit.isdigit() else None,
            assume_staples=assume_staples,
        )

    return render_template(
        "index.html",
        raw=raw,
        query=query,
        results=results,
        unrecognized=unrecognized,
        searched=bool(query),
        limit=limit if limit.isdigit() else "any",
        limits=MISSING_LIMITS,
        assume_staples=assume_staples,
        total=index.N,
    )


if __name__ == "__main__":
    # 5050 rather than 5000, which AirPlay Receiver holds on macOS.
    app.run(port=5050, debug=True)
