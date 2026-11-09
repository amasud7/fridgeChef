import pytest

from fridgechef.bm25 import idf, match_score


def test_index_statistics(index):
    assert index.N == 8
    assert index.avgdl == pytest.approx(39 / 8)
    assert index.df("garlic") == 4
    assert index.df("salmon") == 1
    assert index.df("anchovy") == 0


def test_rare_ingredient_outweighs_common_one(index):
    assert idf("salmon", index) > idf("garlic", index)
    assert idf("water", index) > idf("rice", index)


def test_match_score_matches_hand_calculation(index, corpus):
    # avgdl = 39/8, |D| = 3, so tf*(k1+1)/(tf + k1*(1 - b + b*|D|/avgdl)) = 2.2/1.853846
    # idf(rice) = ln(5.5/3.5 + 1), idf(water) = ln(7.5/1.5 + 1)
    plain_rice = corpus[2]
    score = match_score(["rice", "water"], plain_rice, index)
    assert score == pytest.approx(3.24713372750086)


def test_recipe_with_no_shared_ingredient_scores_zero(index, corpus):
    chocolate_cake = corpus[3]
    assert match_score(["salmon", "soy sauce"], chocolate_cake, index) == 0.0
    assert chocolate_cake.id not in index.candidates(["salmon", "soy sauce"])


def test_candidates_only_cover_recipes_with_an_overlap(index):
    assert index.candidates(["salmon"]) == {6}
    assert index.candidates(["rice", "salmon"]) == {1, 3, 8, 6}
    assert index.candidates(["anchovy"]) == set()


def test_adding_a_matched_ingredient_never_lowers_the_score(index, corpus):
    chicken_fried_rice = corpus[0]
    before = match_score(["chicken", "rice"], chicken_fried_rice, index)
    after = match_score(["chicken", "rice", "egg"], chicken_fried_rice, index)
    assert after > before


def test_shorter_recipe_scores_higher_on_the_same_overlap(index, corpus):
    query = ["rice", "egg"]
    egg_fried_rice = corpus[7]
    chicken_fried_rice = corpus[0]
    assert match_score(query, egg_fried_rice, index) > match_score(
        query, chicken_fried_rice, index
    )
