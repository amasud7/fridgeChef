# Fridge Chef

CSCE 470 course project. Fridge Chef is an ingredient-based recipe search engine: you
type what is in your fridge and it ranks recipes by how well they fit. Each recipe is
treated as a document, each normalized ingredient as a term, and the fridge list as the
query. Recipes are scored with BM25, then penalized for every ingredient they still
need, so a dish you can cook tonight outranks one that needs a trip to the store.

**Team:** Ayad Masud, Aryan Vemuri, Taro Omori

## Checkpoint 2 status

Implemented:

- ingredient normalization shared by recipes and queries (`fridgechef/normalize.py`)
- inverted index with document frequencies and candidate retrieval (`fridgechef/index.py`)
- BM25 scoring written from scratch (`fridgechef/bm25.py`)
- idf-weighted missing-ingredient penalty, staple handling, and coverage (`fridgechef/ranker.py`)
- a command line demo (`fridgechef/cli.py`)
- 23 tests over a hand-built corpus and the sample dataset (`tests/`)

Not done yet: ingredient substitutions, a rating-based tie-breaker, "did you mean"
suggestions for ingredients outside the vocabulary, indexing the full Food.com dataset,
and the web interface for Checkpoint 3.

## Setup

Python 3.10 or newer. The ranking code uses only the standard library; pytest is the
one dependency.

```bash
git clone <repo-url> && cd fridgeChef
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

There is no install step — `pytest.ini` puts the repo root on the path, so both of the
commands below are run from the repository root.

## Running the tests

```bash
pytest -v
```

The tests use `tests/conftest.py`, an eight-recipe corpus small enough to verify the
rankings by hand, plus the committed sample dataset. No download is required.

## Running the demo

```bash
python -m fridgechef.cli --ingredients "chicken breast, rice, garlic, soy sauce, eggs" --top 5
```

```
fridge: chicken, rice, garlic, soy sauce, egg

1. chicken fried rice  score=3.97  coverage=0.58  30 min
   uses:    chicken, rice, egg, soy sauce, garlic
   missing: green onion, sesame oil
2. egg fried rice  score=3.91  coverage=0.70  15 min
   uses:    rice, egg, soy sauce
   missing: green onion
3. teriyaki chicken bowl  score=3.40  coverage=0.55  35 min
   uses:    chicken, rice, soy sauce, garlic
   missing: brown sugar, ginger
4. steamed white rice  score=2.26  coverage=1.00  20 min
   uses:    rice
5. garlic butter chicken  score=1.10  coverage=0.48  25 min
   uses:    chicken, garlic
   missing: parsley
```

Other options: `--data` to point at a different recipe CSV, `--max-missing` to hide
recipes needing too many extras, `--lam` to change the penalty weight, and
`--no-staples` to stop assuming salt, oil, flour and butter are on hand.

## Algorithm

Ingredient strings are lowercased, stripped of descriptor words such as *fresh* or
*boneless*, singularized, and passed through an alias table, so `"Garlic Cloves"`,
`"garlic clove"`, and `"fresh minced garlic"` all become the term `garlic`. A whole
phrase stays one term, so `soy sauce` is a single vocabulary entry. Only recipes in the
union of the query terms' postings lists are scored.

```
idf(t)      = ln((N - df(t) + 0.5) / (df(t) + 0.5) + 1)

match(Q, D) = sum over t in Q and D of
              idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * |D| / avgdl))

Missing(D)  = ingredients(D) - Q - staples
penalty(D)  = sum over m in Missing(D) of idf(m)
final(Q, D) = match(Q, D) - lam * penalty(D)

coverage(D) = sum of idf over matched non-staple ingredients
            / sum of idf over all non-staple ingredients of D
```

A recipe's ingredients form a set, so `tf` is always 1 and `|D|` is the number of
distinct ingredients. The idf term gives rare ingredients like salmon or tahini far more
weight than salt or water, and weighting the penalty by idf means missing one rare
ingredient costs more than missing one common one. Defaults are `k1 = 1.2`, `b = 0.75`,
and `lam = 0.5`.

Results are sorted by final score, then by fewer missing ingredients, then by recipe id,
which keeps the output deterministic for testing.

## Data

`data/sample_recipes.csv` holds 32 recipes written by hand in the same column layout as
the Food.com export (`id, name, minutes, ingredients`), with raw ingredient strings so
normalization has real work to do. It is committed so the tests and demo run with no
setup.

The full dataset for later checkpoints is Food.com Recipes and User Interactions
(~230K recipes), which is too large to commit here:
<https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions>
