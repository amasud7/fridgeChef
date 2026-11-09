from fridgechef.normalize import normalize, parse_query


def test_garlic_variants_collapse_to_one_term():
    assert normalize("Garlic Cloves") == "garlic"
    assert normalize("garlic clove") == "garlic"
    assert normalize("fresh minced garlic") == "garlic"


def test_plurals_are_singularized():
    assert normalize("Tomatoes") == "tomato"
    assert normalize("large eggs") == "egg"
    assert normalize("potatoes") == "potato"


def test_case_and_extra_whitespace_are_ignored():
    assert normalize("  SOY   Sauce ") == "soy sauce"


def test_multiword_ingredient_stays_a_single_term():
    assert normalize("extra virgin olive oil") == "olive oil"
    assert normalize("boneless skinless chicken breasts") == "chicken"


def test_ground_beef_keeps_its_qualifier():
    assert normalize("ground beef") == "ground beef"


def test_descriptor_is_kept_when_nothing_else_remains():
    assert normalize("fresh") == "fresh"


def test_parse_query_splits_on_commas_and_newlines():
    assert parse_query("chicken, rice\ngarlic") == ["chicken", "rice", "garlic"]


def test_parse_query_drops_duplicates_and_blanks():
    assert parse_query("Eggs, eggs, , large egg") == ["egg"]
