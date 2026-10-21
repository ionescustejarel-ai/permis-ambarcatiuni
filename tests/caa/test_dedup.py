from caa.dedup import DedupConflict, build_questions
from caa.structure import Discipline, LocatedRow, Section


def row(nr, question, options, flags, source="C", section=Section.MAIN, discipline=Discipline.COLREG):
    return LocatedRow(
        nr=nr,
        question=question,
        options=options,
        flags=flags,
        source=source,
        page=1,
        section=section,
        discipline=discipline,
    )


def test_single_row_becomes_one_question():
    questions, conflicts = build_questions(
        [row(1, "Ce este sunetul scurt?", ("1 s", "5 s", "10 s"), ("1", "0", "0"))]
    )
    assert conflicts == []
    assert len(questions) == 1
    assert questions[0].question == "Ce este sunetul scurt?"
    assert questions[0].correct == 0
    assert questions[0].classes == ("C",)
    assert questions[0].disciplines == (("C", Discipline.COLREG),)
    assert questions[0].disputed is False


def test_same_question_in_both_lists_is_merged_and_marked_for_both_classes():
    questions, conflicts = build_questions(
        [
            row(1, "Adâncimea apei se măsoară cu", ("lochul", "sonda", "barometrul"), ("0", "1", "0"),
                source="C", discipline=Discipline.NAVIGATIE),
            row(9, "Adancimea apei se masoara cu:", ("lochul;", "sonda;", "barometrul."), ("0", "1", "0"),
                source="D", discipline=Discipline.MARINARIE),
        ]
    )
    assert conflicts == []
    assert len(questions) == 1
    assert questions[0].classes == ("C", "D")
    assert questions[0].disciplines == (("C", Discipline.NAVIGATIE), ("D", Discipline.MARINARIE))
    assert questions[0].disciplines_for("C") == (Discipline.NAVIGATIE,)
    assert questions[0].disciplines_for("D") == (Discipline.MARINARIE,)


def test_duplicates_with_reordered_options_are_merged():
    questions, conflicts = build_questions(
        [
            row(1, "Ce este sunetul lung?", ("1 s", "4-6 s", "10 s"), ("0", "1", "0"), source="C"),
            row(2, "Ce este sunetul lung?", ("4-6 s", "1 s", "10 s"), ("1", "0", "0"), source="D"),
        ]
    )
    assert conflicts == []
    assert len(questions) == 1
    assert questions[0].classes == ("C", "D")


def test_same_stem_with_different_options_stays_two_questions():
    questions, conflicts = build_questions(
        [
            row(55, "Din drumul căror nave?", ("viteza mica", "nestapane pe manevra", "petroliere"),
                ("0", "1", "0")),
            row(56, "Din drumul căror nave?", ("frigorifice", "petroliere", "manevra redusa"),
                ("0", "0", "1")),
        ]
    )
    assert conflicts == []
    assert len(questions) == 2
    assert {q.correct for q in questions} == {1, 2}


def test_same_stem_with_different_options_gets_distinct_ids():
    questions, _ = build_questions(
        [
            row(55, "Din drumul căror nave?", ("viteza mica", "nestapane pe manevra", "petroliere"),
                ("0", "1", "0")),
            row(56, "Din drumul căror nave?", ("frigorifice", "petroliere", "manevra redusa"),
                ("0", "0", "1")),
        ]
    )
    assert len({q.id for q in questions}) == 2


def test_lists_disagreeing_on_the_answer_are_kept_separately_per_class():
    questions, conflicts = build_questions(
        [
            row(291, "Boturile sunt:", ("capete de parama", "sigurante ale axului", "stifturi"),
                ("1", "0", "0"), source="C", discipline=Discipline.MARINARIE),
            row(149, "Boturile sunt:", ("capete de parama", "sigurante ale axului", "stifturi"),
                ("0", "0", "1"), source="D", discipline=Discipline.MANEVRA),
        ]
    )
    assert conflicts == []
    assert len(questions) == 2
    assert all(q.disputed for q in questions)
    assert {q.classes for q in questions} == {("C",), ("D",)}
    assert {q.correct for q in questions} == {0, 2}
    assert len({q.id for q in questions}) == 2
    # Each split item carries only its own class's discipline — no leakage.
    assert {q.disciplines for q in questions} == {
        (("C", Discipline.MARINARIE),),
        (("D", Discipline.MANEVRA),),
    }


def test_one_list_contradicting_itself_is_a_conflict():
    questions, conflicts = build_questions(
        [
            row(1, "Ce este sunetul lung?", ("1 s", "4-6 s", "10 s"), ("0", "1", "0"), source="C"),
            row(2, "Ce este sunetul lung?", ("1 s", "4-6 s", "10 s"), ("1", "0", "0"), source="C"),
        ]
    )
    assert questions == []
    assert len(conflicts) == 1
    assert isinstance(conflicts[0], DedupConflict)
    assert set(conflicts[0].correct_texts) == {"4 6 s", "1 s"}


def test_row_without_exactly_one_correct_flag_is_a_conflict():
    questions, conflicts = build_questions(
        [row(6, "Intrebare stricata", ("a", "b", "c"), ("1", "1", "0"))]
    )
    assert questions == []
    assert len(conflicts) == 1


def test_a_blank_flag_is_not_malformed_when_one_option_is_marked():
    # lista_C has exactly one row whose middle flag cell renders empty. It still
    # marks exactly one correct option, so the question is kept.
    questions, conflicts = build_questions(
        [row(6, "Ultrajul savarsit...", ("da", "nu", "doar ziua"), ("1", "", "0"))]
    )
    assert conflicts == []
    assert len(questions) == 1
    assert questions[0].correct == 0


def test_ids_are_stable_across_calls():
    rows = [row(1, "Ce este sunetul scurt?", ("1 s", "5 s", "10 s"), ("1", "0", "0"))]
    first, _ = build_questions(rows)
    second, _ = build_questions(rows)
    assert first[0].id == second[0].id


def test_an_excluded_row_never_reaches_the_bank():
    """lista_D nr 84 p5 renders one option twice; it is dropped by policy."""
    from caa.dedup import EXCLUDED_ROWS

    assert ("D", 84, 5) in EXCLUDED_ROWS
    excluded = LocatedRow(
        nr=84,
        question="Un observator...",
        options=("bordul tribord", "bordul tribord", "cuplul maestru"),
        flags=("0", "1", "0"),
        source="D",
        page=5,
        section=Section.MAIN,
        discipline=Discipline.MARINARIE,
    )
    questions, conflicts = build_questions([excluded])
    assert questions == []
    assert conflicts == []


def test_the_id_does_not_depend_on_which_row_comes_first():
    """Ids key saved progress, so they cannot follow document order."""
    a = row(1, "Adâncimea apei se măsoară cu", ("Şalupa", "sonda", "barometrul"),
            ("0", "1", "0"), source="C")
    b = row(9, "Adancimea apei se masoara cu:", ("salupa;", "sonda;", "barometrul."),
            ("0", "1", "0"), source="D")
    forward, _ = build_questions([a, b])
    backward, _ = build_questions([b, a])
    assert len(forward) == len(backward) == 1
    assert forward[0].id == backward[0].id


def test_theme_is_not_assigned_yet():
    questions, _ = build_questions(
        [row(1, "Ce este sunetul scurt?", ("1 s", "5 s", "10 s"), ("1", "0", "0"))]
    )
    assert questions[0].theme is None
