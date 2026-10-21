from caa.exam import EXAM_DRAW, EXAM_RULES


def test_every_class_draws_the_official_number_of_questions():
    for exam_class, groups in EXAM_DRAW.items():
        assert sum(count for _, count in groups) == EXAM_RULES["questions"], exam_class


def test_the_pass_mark_is_the_official_one():
    assert EXAM_RULES["questions"] == 26
    assert EXAM_RULES["minutes"] == 30
    assert EXAM_RULES["pass"] == 22


def test_the_difference_exam_is_ten_questions_for_eight_correct():
    difference = EXAM_RULES["difference"]
    assert difference["questions"] == 10
    assert difference["minutes"] == 10
    assert difference["pass"] == 8


def test_the_difference_exam_draws_the_distinctive_discipline():
    difference = EXAM_RULES["difference"]
    assert difference["disciplines"]["C"] == ("COLREG",)
    assert difference["disciplines"]["D"] == ("RND",)
