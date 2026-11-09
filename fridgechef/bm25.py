"""BM25 scoring of recipes against the ingredients a user has."""

import math

from .index import Recipe, RecipeIndex

K1 = 1.2
B = 0.75


def idf(term: str, index: RecipeIndex) -> float:
    """Inverse document frequency of an ingredient.

        idf(t) = ln((N - df(t) + 0.5) / (df(t) + 0.5) + 1)

    The trailing +1 keeps the value positive even for an ingredient that appears
    in nearly every recipe, so staples such as salt contribute very little
    instead of going negative.
    """
    df = index.df(term)
    return math.log((index.N - df + 0.5) / (df + 0.5) + 1)


def match_score(
    query_terms: list[str],
    recipe: Recipe,
    index: RecipeIndex,
    k1: float = K1,
    b: float = B,
) -> float:
    """BM25 score for the overlap between a query and a recipe.

        match(Q, D) = sum over t in Q and D of
            idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * |D| / avgdl))

    Term frequency is 1 for every ingredient a recipe lists, so the saturation
    term is constant per recipe; the length normalization is what makes a short
    recipe score higher than a long one on the same matched ingredients.
    """
    available = set(query_terms)
    length = index.doc_len[recipe.id]
    saturation = 1.0 + k1 * (1 - b + b * length / index.avgdl)
    weight = (k1 + 1) / saturation
    return sum(
        idf(term, index) * weight for term in recipe.ingredients if term in available
    )
