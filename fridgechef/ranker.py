"""Rank recipes by what a user has, penalizing what they would still need."""

from dataclasses import dataclass

from .bm25 import B, K1, idf, match_score
from .index import Recipe, RecipeIndex

STAPLES = {
    "salt",
    "pepper",
    "black pepper",
    "water",
    "sugar",
    "flour",
    "oil",
    "vegetable oil",
    "olive oil",
    "butter",
}

LAMBDA = 0.5


@dataclass
class Result:
    recipe_id: int
    name: str
    final_score: float
    match_score: float
    penalty: float
    coverage: float
    used_ingredients: list[str]
    missing_ingredients: list[str]
    minutes: int


def _coverage(
    recipe: Recipe, available: set[str], staples: set[str], index: RecipeIndex
) -> float:
    """Share of a recipe's non-staple ingredient weight the user already has."""
    required = [term for term in recipe.ingredients if term not in staples]
    total = sum(idf(term, index) for term in required)
    if not total:
        return 1.0
    have = sum(idf(term, index) for term in required if term in available)
    return have / total


def search(
    query_ingredients: list[str],
    index: RecipeIndex,
    top_k: int = 10,
    k1: float = K1,
    b: float = B,
    lam: float = LAMBDA,
    max_missing: int | None = None,
    assume_staples: bool = True,
) -> list[Result]:
    """Rank recipes for a fridge list.

        Missing(D) = ingredients(D) - Q - staples
        penalty(D) = sum over m in Missing(D) of idf(m)
        final(Q, D) = match(Q, D) - lam * penalty(D)

    Weighting the penalty by idf means a recipe short one rare ingredient is
    pushed down further than one short a common ingredient. Ties break on fewer
    missing ingredients and then recipe id, so the ordering is deterministic.
    """
    available = set(query_ingredients)
    staples = STAPLES if assume_staples else set()
    results = []
    for recipe_id in index.candidates(query_ingredients):
        recipe = index.recipes[recipe_id]
        missing = [
            term
            for term in recipe.ingredients
            if term not in available and term not in staples
        ]
        if max_missing is not None and len(missing) > max_missing:
            continue
        match = match_score(query_ingredients, recipe, index, k1, b)
        penalty = sum(idf(term, index) for term in missing)
        results.append(
            Result(
                recipe_id=recipe.id,
                name=recipe.name,
                final_score=match - lam * penalty,
                match_score=match,
                penalty=penalty,
                coverage=_coverage(recipe, available, staples, index),
                used_ingredients=[
                    term for term in recipe.ingredients if term in available
                ],
                missing_ingredients=missing,
                minutes=recipe.minutes,
            )
        )
    results.sort(
        key=lambda r: (-r.final_score, len(r.missing_ingredients), r.recipe_id)
    )
    return results[:top_k]
