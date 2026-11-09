import pytest

from fridgechef.normalize import parse_query
from fridgechef.ranker import search

FULL_FRIDGE = ["chicken", "rice", "egg", "soy sauce", "garlic", "green onion"]


def by_id(results, recipe_id):
    return next(r for r in results if r.recipe_id == recipe_id)


def test_best_match_is_ranked_first(index):
    results = search(FULL_FRIDGE, index)
    assert results[0].recipe_id == 1
    assert results[0].missing_ingredients == []
    assert results[0].coverage == pytest.approx(1.0)


def test_recipe_short_one_ingredient_is_still_returned(index):
    without_onion = [t for t in FULL_FRIDGE if t != "green onion"]
    result = by_id(search(without_onion, index), 1)
    assert result.missing_ingredients == ["green onion"]
    assert result.final_score < by_id(search(FULL_FRIDGE, index), 1).final_score
    assert 0 < result.coverage < 1


def test_raising_lambda_only_penalizes_recipes_with_missing_ingredients(index):
    query = ["egg", "milk", "cheese"]
    low = {r.recipe_id: r.final_score for r in search(query, index, lam=0.0)}
    high = {r.recipe_id: r.final_score for r in search(query, index, lam=2.0)}
    assert high[5] == pytest.approx(low[5])
    assert high[4] < low[4]


def test_staples_are_not_counted_as_missing(index):
    assumed = by_id(search(["rice"], index), 3)
    assert assumed.missing_ingredients == []
    explicit = by_id(search(["rice"], index, assume_staples=False), 3)
    assert explicit.missing_ingredients == ["water", "salt"]


def test_max_missing_zero_returns_only_makeable_recipes(index):
    results = search(["rice", "egg", "soy sauce", "green onion"], index, max_missing=0)
    assert [r.recipe_id for r in results] == [8, 3]
    assert all(r.missing_ingredients == [] for r in results)


def test_top_k_limits_the_result_count(index):
    assert len(search(["garlic", "egg", "rice"], index, top_k=2)) == 2


def test_repeated_searches_give_identical_results(index):
    query = ["chicken", "rice", "garlic"]
    assert search(query, index) == search(query, index)


def test_search_over_the_sample_dataset(sample_index):
    query = parse_query("chicken, rice, garlic")
    results = search(query, sample_index, top_k=5)
    assert results
    scores = [r.final_score for r in results]
    assert scores == sorted(scores, reverse=True)
    for result in results:
        assert set(result.used_ingredients) & set(query)
