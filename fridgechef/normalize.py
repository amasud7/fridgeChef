"""Canonicalize ingredient strings so recipes and queries share a vocabulary."""

import re

DESCRIPTORS = {
    "fresh",
    "chopped",
    "minced",
    "diced",
    "sliced",
    "shredded",
    "boneless",
    "skinless",
    "frozen",
    "canned",
    "cooked",
    "uncooked",
    "raw",
    "large",
    "small",
    "medium",
    "ripe",
}

ALIASES = {
    "garlic clove": "garlic",
    "clove garlic": "garlic",
    "chicken breast": "chicken",
    "chicken thigh": "chicken",
    "salmon fillet": "salmon",
    "scallion": "green onion",
    "spring onion": "green onion",
    "extra virgin olive oil": "olive oil",
    "all-purpose flour": "flour",
    "long grain rice": "rice",
    "white rice": "rice",
    "granulated sugar": "sugar",
    "kosher salt": "salt",
    "table salt": "salt",
}

_PUNCTUATION = re.compile(r"[^a-z0-9\s-]")
_SPLIT_QUERY = re.compile(r"[,\n]")


def _singularize(token: str) -> str:
    if len(token) <= 3 or token.endswith("ss"):
        return token
    if token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith("oes"):
        return token[:-2]
    if token.endswith("s"):
        return token[:-1]
    return token


def normalize(ingredient: str) -> str:
    """Reduce an ingredient phrase to a single canonical term.

    Lowercases, drops descriptor words, singularizes each remaining token, and
    applies the alias table. The whole phrase stays one term, so "soy sauce" is
    a single vocabulary entry rather than two.
    """
    tokens = _PUNCTUATION.sub(" ", ingredient.lower()).split()
    kept = [t for t in tokens if t not in DESCRIPTORS] or tokens
    term = " ".join(_singularize(t) for t in kept)
    return ALIASES.get(term, term)


def parse_query(text: str) -> list[str]:
    """Split a comma or newline separated fridge list into normalized terms."""
    terms = []
    for piece in _SPLIT_QUERY.split(text):
        term = normalize(piece)
        if term and term not in terms:
            terms.append(term)
    return terms
