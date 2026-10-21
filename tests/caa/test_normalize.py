from caa.normalize import normalize_key, question_id


def test_strips_romanian_diacritics():
    assert normalize_key("Adâncimea apei se măsoară cu") == "adancimea apei se masoara cu"


def test_treats_both_comma_and_cedilla_forms_as_equal():
    # U+0219 (s with comma) and U+015F (s with cedilla) both appear in the PDFs.
    assert normalize_key("navigașie") == normalize_key("navigaşie")
    assert normalize_key("menține") == normalize_key("menţine")


def test_ignores_punctuation_and_case():
    assert normalize_key("Adancimea apei se masoara cu:") == normalize_key(
        "adancimea apei se masoara cu"
    )


def test_collapses_runs_of_separators_into_one_space():
    # Regression guard: replacing separators one-by-one leaves double spaces
    # and inflates the unique-question count.
    assert normalize_key("ancora , cu patru brate") == "ancora cu patru brate"
    assert normalize_key("nava - 12 m") == "nava 12 m"


def test_collapses_whitespace():
    assert normalize_key("  doua   cuvinte  ") == "doua cuvinte"


def test_digits_are_preserved():
    assert normalize_key("Colreg-1972?") == "colreg 1972"


def test_question_id_is_stable_and_well_formed():
    first = question_id("Adâncimea apei se măsoară cu")
    second = question_id("Adancimea apei se masoara cu:")
    assert first == second
    assert first.startswith("q")
    assert len(first) == 13


def test_different_questions_get_different_ids():
    assert question_id("Prima intrebare") != question_id("A doua intrebare")
