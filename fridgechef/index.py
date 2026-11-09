"""Inverted index over normalized recipe ingredients."""

import csv
import json
from dataclasses import dataclass

from .normalize import normalize


@dataclass(frozen=True)
class Recipe:
    id: int
    name: str
    minutes: int
    ingredients: tuple[str, ...]


def load_recipes(path) -> list[Recipe]:
    """Read recipes from CSV, normalizing and de-duplicating each ingredient list."""
    recipes = []
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            name = row["name"].strip()
            ingredients = []
            for raw in json.loads(row["ingredients"]):
                term = normalize(raw)
                if term and term not in ingredients:
                    ingredients.append(term)
            if not name or not ingredients:
                continue
            recipes.append(
                Recipe(int(row["id"]), name, int(row["minutes"]), tuple(ingredients))
            )
    return recipes


class RecipeIndex:
    """Document frequencies and postings for a recipe collection.

    Each recipe is a document and each normalized ingredient is a term. An
    ingredient either appears in a recipe or it does not, so every term
    frequency is 1 and a document's length is its number of ingredients.
    """

    def __init__(self, recipes: list[Recipe]):
        self.recipes = {recipe.id: recipe for recipe in recipes}
        self.doc_len = {recipe.id: len(recipe.ingredients) for recipe in recipes}
        self.postings: dict[str, set[int]] = {}
        for recipe in recipes:
            for term in recipe.ingredients:
                self.postings.setdefault(term, set()).add(recipe.id)
        self.N = len(self.recipes)
        self.avgdl = sum(self.doc_len.values()) / self.N if self.N else 0.0

    @classmethod
    def from_csv(cls, path) -> "RecipeIndex":
        return cls(load_recipes(path))

    def df(self, term: str) -> int:
        """Number of recipes containing the term."""
        return len(self.postings.get(term, ()))

    def candidates(self, terms: list[str]) -> set[int]:
        """Ids of recipes sharing at least one ingredient with the query.

        Scoring is restricted to this set so a query never touches the whole
        collection.
        """
        found: set[int] = set()
        for term in terms:
            found |= self.postings.get(term, set())
        return found
