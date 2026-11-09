from pathlib import Path

import pytest

from fridgechef.index import Recipe, RecipeIndex

SAMPLE_CSV = Path(__file__).resolve().parents[1] / "data" / "sample_recipes.csv"

CORPUS = [
    Recipe(1, "chicken fried rice", 30,
           ("chicken", "rice", "egg", "soy sauce", "garlic", "green onion")),
    Recipe(2, "garlic chicken", 25, ("chicken", "garlic", "butter", "salt")),
    Recipe(3, "plain rice", 20, ("rice", "water", "salt")),
    Recipe(4, "chocolate cake", 60,
           ("flour", "sugar", "cocoa", "egg", "butter", "baking powder")),
    Recipe(5, "omelette", 10, ("egg", "milk", "salt", "pepper", "cheese")),
    Recipe(6, "salmon teriyaki", 25,
           ("salmon", "soy sauce", "sugar", "ginger", "garlic")),
    Recipe(7, "tomato pasta", 30,
           ("pasta", "tomato", "garlic", "olive oil", "basil")),
    Recipe(8, "egg fried rice", 15,
           ("rice", "egg", "soy sauce", "green onion", "oil")),
]


@pytest.fixture
def corpus():
    return list(CORPUS)


@pytest.fixture
def index(corpus):
    return RecipeIndex(corpus)


@pytest.fixture
def sample_index():
    return RecipeIndex.from_csv(SAMPLE_CSV)
