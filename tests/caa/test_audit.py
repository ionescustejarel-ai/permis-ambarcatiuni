from dataclasses import replace
from pathlib import Path

import pytest

from caa import arcs, figures, signals
from caa.audit import EXAM_DRAW, REFERENCE, render_report, run_audit
from caa.dedup import DedupConflict, Question
from caa.structure import Discipline, Section

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "sources" / "anr"


def good_question(qid="q1", theme="semnale-sonore"):
    return Question(
        id=qid,
        question="Ce este sunetul scurt?",
        options=("aproximativ 1 secunda", "4-6 secunde", "10 secunde"),
        correct=0,
        section=Section.MAIN,
        disciplines=(("C", Discipline.COLREG),),
        classes=("C",),
        theme=theme,
    )


def test_a_disputed_item_bound_to_both_classes_is_reported():
    from dataclasses import replace as _replace

    item = _replace(good_question(), disputed=True, classes=("C", "D"))
    report = run_audit([item], [], reference_counts())
    assert "disputed-class" in rules_of(report)


def reference_counts():
    return {"C": REFERENCE["rows_c"], "D": REFERENCE["rows_d"]}


def rules_of(report):
    return {finding.rule for finding in report.findings}


def test_reference_values_are_the_ones_measured_on_2026_07_25():
    assert REFERENCE["rows_c"] == 517
    assert REFERENCE["rows_d"] == 371
    assert REFERENCE["total"] == 603
    assert REFERENCE["shared"] == 267
    assert REFERENCE["disputed"] == 2


def test_exam_draw_sums_to_26_for_both_classes():
    for exam_class, groups in EXAM_DRAW.items():
        assert sum(count for _, count in groups) == 26, exam_class


def test_empty_option_is_reported():
    broken = replace(good_question(), options=("a", "", "c"))
    report = run_audit([broken], [], reference_counts())
    assert "options" in rules_of(report)
    assert not report.ok


def test_out_of_range_correct_index_is_reported():
    report = run_audit([replace(good_question(), correct=5)], [], reference_counts())
    assert "correct-index" in rules_of(report)


def test_empty_question_text_is_reported():
    report = run_audit([replace(good_question(), question="   ")], [], reference_counts())
    assert "empty-question" in rules_of(report)


def test_item_without_a_discipline_is_reported():
    report = run_audit([replace(good_question(), disciplines=())], [], reference_counts())
    assert "discipline" in rules_of(report)


def test_item_without_an_exam_class_is_reported():
    report = run_audit([replace(good_question(), classes=())], [], reference_counts())
    assert "class" in rules_of(report)


def test_two_identical_options_are_reported():
    """A question whose right answer's text also appears unflagged is unanswerable."""
    broken = replace(good_question(), options=("acelasi", "acelasi", "altul"))
    report = run_audit([broken], [], reference_counts())
    assert "duplicate-options" in rules_of(report)


def test_a_duplicate_id_is_reported():
    report = run_audit(
        [good_question(qid="qsame"), replace(good_question(qid="qsame"), question="alta")],
        [],
        reference_counts(),
    )
    assert "duplicate-id" in rules_of(report)


def test_missing_theme_is_reported():
    report = run_audit([good_question(theme=None)], [], reference_counts())
    assert "theme" in rules_of(report)


def test_dedup_conflict_fails_the_audit():
    conflict = DedupConflict(key="k", question="Q", correct_texts=("a", "b"))
    report = run_audit([good_question()], [conflict], reference_counts())
    assert "dedup-conflict" in rules_of(report)
    assert not report.ok


def test_row_count_mismatch_is_reported():
    report = run_audit([good_question()], [], {"C": 500, "D": 371})
    assert "row-count" in rules_of(report)


def test_total_mismatch_is_reported():
    report = run_audit([good_question()], [], reference_counts())
    assert "totals" in rules_of(report)


def test_insufficient_discipline_pool_is_reported():
    # A single COLREG question cannot satisfy a draw of 10.
    report = run_audit([good_question()], [], reference_counts())
    assert "exam-pool" in rules_of(report)


def test_excessive_fallback_share_is_reported():
    questions = [good_question(qid=f"q{i}", theme="vocabular-si-principii") for i in range(10)]
    report = run_audit(questions, [], reference_counts())
    assert "fallback-share" in rules_of(report)


def test_a_source_quote_that_no_longer_exists_fails_the_build(monkeypatch):
    """ANR rewords an answer -> the build stops instead of attaching to nothing."""
    from caa import audit
    from caa.signals import SHORT, Signal, WHISTLE

    orphan = Signal(id="orfan", label="Orfan", instrument=WHISTLE,
                    pattern=(SHORT,), sources=("un sunet care nu exista in banca.",))
    monkeypatch.setattr(audit, "SIGNALS", (orphan,))

    report = run_audit([good_question()], [], reference_counts())

    assert "signal-source" in rules_of(report)


def test_a_source_quote_that_exists_raises_no_finding(monkeypatch):
    """The mirror of the test above: the rule must not fire on a match."""
    from caa import audit
    from caa.signals import SHORT, Signal, WHISTLE

    # good_question's correct answer is "aproximativ 1 secunda".
    present = Signal(id="prezent", label="Prezent", instrument=WHISTLE,
                     pattern=(SHORT,), sources=("aproximativ 1 secunda",))
    monkeypatch.setattr(audit, "SIGNALS", (present,))

    report = run_audit([good_question()], [], reference_counts())

    assert "signal-source" not in rules_of(report)


def test_an_uncovered_sound_pattern_fails_the_build(monkeypatch):
    """A signal the bank gains later must demand a decision, not vanish."""
    from caa import audit

    # Patched on caa.signals, not caa.audit: the coverage rule reads the
    # catalogue through played_answers(), which resolves SIGNALS in the
    # signals module's own namespace. Patching audit.SIGNALS left the real
    # catalogue in play and the test passed for the wrong reason.
    monkeypatch.setattr(signals, "SIGNALS", ())
    monkeypatch.setattr(audit, "NOT_A_PATTERN", {})
    item = replace(good_question(), options=("patru sunete scurte.", "b", "c"), correct=0)

    report = run_audit([item], [], reference_counts())

    findings = [f for f in report.findings if f.rule == "signal-coverage"]
    assert findings
    assert "patru sunete scurte." in findings[0].detail


def test_a_pattern_listed_as_an_exception_does_not_fail_the_build(monkeypatch):
    from caa import audit

    monkeypatch.setattr(signals, "SIGNALS", ())
    monkeypatch.setattr(audit, "NOT_A_PATTERN", {"patru sunete scurte.": "no count in source"})
    item = replace(good_question(), options=("patru sunete scurte.", "b", "c"), correct=0)

    report = run_audit([item], [], reference_counts())

    assert "signal-coverage" not in rules_of(report)


def test_an_arc_quote_that_no_longer_exists_fails_the_build(monkeypatch):
    from caa import audit
    from caa.arcs import Arc, Sector

    orphan = Arc(id="orfan", label="Orfan", sectors=(Sector(0, 90, "white"),),
                 sources=("un arc care nu exista in banca.",))
    monkeypatch.setattr(audit, "ARCS", (orphan,))

    report = run_audit([good_question()], [], reference_counts())

    assert "arc-source" in rules_of(report)


def test_an_arc_quote_that_exists_raises_no_finding(monkeypatch):
    from caa import audit
    from caa.arcs import Arc, Sector

    # good_question's stem is "Ce este sunetul scurt?".
    present = Arc(id="prezent", label="Prezent", sectors=(Sector(0, 90, "white"),),
                  sources=("Ce este sunetul scurt?",))
    monkeypatch.setattr(audit, "ARCS", (present,))

    report = run_audit([good_question()], [], reference_counts())

    assert "arc-source" not in rules_of(report)


def test_an_undrawn_arc_fails_the_build(monkeypatch):
    from caa import audit

    monkeypatch.setattr(arcs, "ARCS", ())
    monkeypatch.setattr(audit, "NOT_AN_ARC", {})
    item = replace(good_question(),
                   question="""Ce se înţelege prin expresia „lumină de veghe"?""",
                   options=("o lumină pe un arc de 90°.", "b", "c"), correct=0)

    report = run_audit([item], [], reference_counts())

    findings = [f for f in report.findings if f.rule == "arc-coverage"]
    assert findings
    assert "un arc de 90" in findings[0].detail


def test_an_arc_listed_as_an_exception_does_not_fail_the_build(monkeypatch):
    from caa import audit

    monkeypatch.setattr(arcs, "ARCS", ())
    monkeypatch.setattr(audit, "NOT_AN_ARC", {"o lumină pe un arc de 90°.": "no colour given"})
    item = replace(good_question(),
                   question="""Ce se înţelege prin expresia „lumină de veghe"?""",
                   options=("o lumină pe un arc de 90°.", "b", "c"), correct=0)

    report = run_audit([item], [], reference_counts())

    assert "arc-coverage" not in rules_of(report)


def test_a_caveat_keyed_on_a_foreign_quote_fails_the_build(monkeypatch):
    """A note that can never be shown is worse than no note."""
    from caa import audit
    from caa.arcs import Arc, Sector

    stray = Arc(id="stray", label="Stray", sectors=(Sector(0, 90, "white"),),
                sources=("Ce este sunetul scurt?",),
                caveats={"un text care nu e sursa lui": "nota orfana"})
    monkeypatch.setattr(audit, "ARCS", (stray,))

    report = run_audit([good_question()], [], reference_counts())

    assert "arc-caveat" in rules_of(report)


def test_report_renders_markdown_with_the_distribution():
    report = run_audit([good_question()], [], reference_counts())
    text = render_report(report)
    assert "# Raport de audit" in text
    assert "semnale-sonore" in text


def test_two_questions_sharing_an_id_do_not_share_their_coverage():
    """The rule is about an answer, so a question id must not decide it.

    Keyed by id, one question matching a catalogue entry marked its
    id-twin covered too, and a genuinely unplayable signal passed in
    silence. `_check_ids` co-fires on that input, which is exactly why the
    gap was invisible: the build still failed, for another reason.
    """
    from caa.audit import _check_signal_coverage

    covered = replace(good_question(qid="dup"), options=("un sunet scurt.", "b", "c"), correct=0)
    uncovered = replace(good_question(qid="dup"), options=("patru sunete scurte.", "b", "c"), correct=0)

    findings = _check_signal_coverage([covered, uncovered])

    assert [f.detail for f in findings] == ["dup: no signal for 'patru sunete scurte.'"]


def test_a_figure_quote_that_no_longer_exists_fails_the_build(monkeypatch):
    from caa import audit
    from caa.figures import Body, Figure, IALA

    orphan = Figure(id="orfan", label="Orfan", system=IALA,
                    body=Body(shape="pillar", bands=("black",)),
                    sources=("un marcaj care nu exista in banca.",))
    monkeypatch.setattr(audit, "FIGURES", (orphan,))

    report = run_audit([good_question()], [], reference_counts())

    assert "figure-source" in rules_of(report)


def test_a_figure_quote_that_exists_raises_no_finding(monkeypatch):
    """The mirror: the rule must stay silent on a match, and it matches the stem."""
    from caa import audit
    from caa.figures import Body, Figure, IALA

    # good_question's stem is "Ce este sunetul scurt?".
    present = Figure(id="prezent", label="Prezent", system=IALA,
                     body=Body(shape="pillar", bands=("black",)),
                     sources=("Ce este sunetul scurt?",))
    monkeypatch.setattr(audit, "FIGURES", (present,))

    report = run_audit([good_question()], [], reference_counts())

    assert "figure-source" not in rules_of(report)


def test_an_undrawn_mark_fails_the_build(monkeypatch):
    from caa import audit

    monkeypatch.setattr(figures, "FIGURES", ())
    monkeypatch.setattr(audit, "NOT_A_FIGURE", {})
    item = replace(good_question(), options=("un cilindru violet.", "b", "c"), correct=0)

    report = run_audit([item], [], reference_counts())

    findings = [f for f in report.findings if f.rule == "figure-coverage"]
    assert findings
    assert "un cilindru violet." in findings[0].detail


def test_a_mark_listed_as_an_exception_does_not_fail_the_build(monkeypatch):
    from caa import audit

    monkeypatch.setattr(figures, "FIGURES", ())
    monkeypatch.setattr(audit, "NOT_A_FIGURE", {"un cilindru violet.": "no colour in the source"})
    item = replace(good_question(), options=("un cilindru violet.", "b", "c"), correct=0)

    report = run_audit([item], [], reference_counts())

    assert "figure-coverage" not in rules_of(report)


def test_a_mark_described_in_the_stem_is_covered(monkeypatch):
    """Coverage must read the stem, or half the marks read as undrawn."""
    from caa import audit
    from caa.figures import Body, Figure, DAY_SHAPE

    stem = "Un cilindru negru reprezintă semnul purtat de o navă:"
    drawn = Figure(id="cilindru", label="Cilindru", system=DAY_SHAPE,
                   body=Body(shape="cylinder", bands=("black",)), sources=(stem,))
    monkeypatch.setattr(figures, "FIGURES", (drawn,))
    monkeypatch.setattr(audit, "FIGURES", (drawn,))
    item = replace(good_question(), question=stem)

    report = run_audit([item], [], reference_counts())

    assert "figure-coverage" not in rules_of(report)


def test_a_mark_named_only_in_the_stem_and_undrawn_fails_the_build(monkeypatch):
    """The test above cannot tell a read stem from an unread one.

    Its answer never looks like a mark, so an implementation that dropped the
    stem entirely would also report nothing and also pass. This one fails
    unless the stem is genuinely read.
    """
    from caa import audit

    monkeypatch.setattr(figures, "FIGURES", ())
    monkeypatch.setattr(audit, "NOT_A_FIGURE", {})
    item = replace(good_question(), question="Un cilindru violet reprezintă ceva:")

    report = run_audit([item], [], reference_counts())

    findings = [f for f in report.findings if f.rule == "figure-coverage"]
    assert findings
    assert "Un cilindru violet reprezintă ceva:" in findings[0].detail, (
        "the finding must name the text that is missing, not its neighbour"
    )


def test_a_second_undrawn_mark_in_the_other_field_is_not_caught(monkeypatch):
    """A stated limit, pinned so nobody tightens it without measuring.

    Coverage asks whether the *question* is drawn, because the language that
    identifies a question as being about a mark is usually not the text the
    catalogue quotes: the recognizer sees "…este piturat în dungi orizontale…"
    while the binding quote is the answer, "negru-galben-negru;". Judging each
    describing field on its own was tried and failed the build on six correct
    questions.

    The cost is here: a question naming a drawn mark in one field and a
    different, undrawn one in the other passes. Nothing cheap separates that
    from the six, because the recognizer cannot tell a mark from mark-adjacent
    language.
    """
    from caa import audit
    from caa.figures import Body, Figure, DAY_SHAPE

    stem = "Un cilindru negru reprezintă semnul purtat de o navă:"
    drawn = Figure(id="cilindru", label="Cilindru", system=DAY_SHAPE,
                   body=Body(shape="cylinder", bands=("black",)), sources=(stem,))
    monkeypatch.setattr(figures, "FIGURES", (drawn,))
    monkeypatch.setattr(audit, "FIGURES", (drawn,))
    monkeypatch.setattr(audit, "NOT_A_FIGURE", {})
    item = replace(good_question(), question=stem,
                   options=("un cilindru violet.", "b", "c"), correct=0)

    report = run_audit([item], [], reference_counts())

    assert "figure-coverage" not in rules_of(report)


def test_an_arc_named_only_in_the_stem_is_reported_by_its_stem(monkeypatch):
    """The finding must quote the field that actually announces the arc.

    Every other fixture here has the answer announcing it, so an
    implementation that named the answer unconditionally — the defect the
    figure rule shipped with at stage 3b — passes them all unchanged.
    """
    from caa import audit

    monkeypatch.setattr(arcs, "ARCS", ())
    monkeypatch.setattr(audit, "NOT_AN_ARC", {})
    stem = "Lumina de veghe se vede pe un arc de 90° și este:"
    item = replace(good_question(), question=stem)

    report = run_audit([item], [], reference_counts())

    findings = [f for f in report.findings if f.rule == "arc-coverage"]
    assert findings
    assert stem in findings[0].detail, (
        "the finding names the answer, not the field that announced the arc"
    )


def test_a_caveat_keyed_on_another_arcs_quote_fails_the_build(monkeypatch):
    """Scoped to its own arc, not to the catalogue as a whole.

    With one arc in the catalogue the two readings are indistinguishable.
    Checking against the union of every arc's quotes — the obvious
    simplification — lets this case through in silence, and the note never
    reaches the question it was written for.
    """
    from caa import audit
    from caa.arcs import Arc, Sector

    first = Arc(id="intai", label="Întâi", sectors=(Sector(0, 90, "white"),),
                sources=("Ce este sunetul scurt?",))
    second = Arc(id="al-doilea", label="Al doilea", sectors=(Sector(0, 180, "red"),),
                 sources=("aproximativ 1 secunda",),
                 caveats={"Ce este sunetul scurt?": "nota pusă pe citatul altei figuri"})
    monkeypatch.setattr(audit, "ARCS", (first, second))

    report = run_audit([good_question()], [], reference_counts())

    findings = [f for f in report.findings if f.rule == "arc-caveat"]
    assert findings, "a caveat on another arc's quote was accepted"
    assert "al-doilea" in findings[0].detail


# Capture config questions at import time, before any monkeypatching
def _capture_config_questions() -> list[Question]:
    """Create test questions from current config sources."""
    from caa import lights
    questions: list[Question] = []
    for i, config in enumerate(lights.CONFIGS):
        for j, source in enumerate(config.sources):
            questions.append(replace(good_question(), id=f"config_q{i}_{j}", question=source))
    return questions


_CONFIG_QUESTIONS = _capture_config_questions()


def _questions() -> list[Question]:
    """Test questions containing all config source texts for audit tests."""
    return _CONFIG_QUESTIONS


def _conflicts() -> list[DedupConflict]:
    """The `conflicts` argument of run_audit: none of them, for these tests."""
    return []


def test_a_configuration_quote_the_bank_lost_is_reported(monkeypatch):
    """Reworded by ANR, the quote binds nothing and the figure attaches to no one."""
    from caa import lights

    ghost = lights.Config(
        id="fantoma",
        label="Fantomă",
        lights=(lights.Placed(colours=("white",), station=lights.STERN),),
        sources=("un text pe care banca nu îl are",),
    )
    monkeypatch.setattr(lights, "CONFIGS", lights.CONFIGS + (ghost,))
    report = run_audit(_questions(), _conflicts(), reference_counts())
    findings = [finding for finding in report.findings if finding.rule == "config-source"]
    assert findings
    assert any("fantoma" in finding.detail for finding in findings)


def test_a_configuration_question_nobody_draws_is_reported(monkeypatch):
    """The rule the whole stage rests on: no silent gap between bank and catalogue."""
    from caa import lights

    monkeypatch.setattr(lights, "CONFIGS", ())
    monkeypatch.setattr(lights, "NOT_A_CONFIG", {})
    report = run_audit(_questions(), _conflicts(), reference_counts())
    rules = {finding.rule for finding in report.findings}
    assert "config-coverage" in rules


def test_an_excused_configuration_question_is_not_reported(monkeypatch):
    """NOT_A_CONFIG is the written decision, so it must actually silence the rule."""
    from caa import lights

    excused = dict.fromkeys(
        text for config in lights.CONFIGS for text in config.sources
    )
    monkeypatch.setattr(lights, "CONFIGS", ())
    monkeypatch.setattr(lights, "NOT_A_CONFIG", {**lights.NOT_A_CONFIG, **excused})
    report = run_audit(_questions(), _conflicts(), reference_counts())
    assert not [f for f in report.findings if f.rule == "config-coverage"]


def test_the_coverage_finding_quotes_a_field_that_is_about_lights(monkeypatch):
    """Naming the innocent neighbour sends the reader to excuse the wrong text."""
    from caa import lights

    monkeypatch.setattr(lights, "CONFIGS", ())
    monkeypatch.setattr(lights, "NOT_A_CONFIG", {})
    report = run_audit(_questions(), _conflicts(), reference_counts())
    covered = [f for f in report.findings if f.rule == "config-coverage"]
    # Without this the test passes on an empty report: a loop over findings
    # that do not exist checks nothing, and removing the rule it guards would
    # leave it green.
    assert covered, "the coverage rule produced no finding to inspect"
    for finding in covered:
        assert "lumin" in finding.detail.lower() or "felinar" in finding.detail.lower()


def test_the_coverage_finding_quotes_the_answer_when_the_stem_is_neutral():
    """The field selection, exercised the other way round.

    Every other test here puts the light-bearing text in the stem, so all of
    them would pass on a rule that quoted `item.question` unconditionally.
    That is the bug that shipped once already, at stage 3b, for the arcs: a
    finding naming the innocent neighbour sends whoever reads the report to
    excuse the wrong text. Here the stem says nothing about lights and the
    answer says everything.
    """
    from caa import lights

    # Invented, not quoted: a real answer would be drawn already and the rule
    # would rightly stay silent, which would test nothing.
    stem = "Ce trebuie să poarte o navă de probă?"
    answer = "o lumină de probă aşezată la extremitatea prova."
    assert lights.looks_like_config(stem, answer), "the recognizer must still catch it"

    item = replace(
        good_question(), id="doar-raspunsul", question=stem,
        options=(answer, "alt raspuns", "inca unul"), correct=0,
    )
    report = run_audit([item], [], reference_counts())
    covered = [f for f in report.findings if f.rule == "config-coverage"]
    assert len(covered) == 1
    assert answer in covered[0].detail
    assert stem not in covered[0].detail


def test_a_configuration_quote_that_exists_raises_no_finding():
    """The mirror the other three catalogues each have."""
    report = run_audit(_questions(), _conflicts(), reference_counts())
    assert not [f for f in report.findings if f.rule == "config-source"]


@pytest.fixture(scope="module")
def bank_questions():
    from caa.cli import build_all
    questions, _ = build_all(SOURCES)
    return questions


def test_a_bound_question_in_a_foreign_theme_fails_the_build():
    """A buoyage question filed under the hull is what this stage exists for."""
    from caa import audit

    item = replace(
        good_question(),
        id="ratacita",
        question="Marcajul lateral de tribord din regiunea A are ca semn de vârf:",
        options=("Un con verde cu vârful în sus;", "b", "c"),
        correct=0,
        theme="constructia-ambarcatiunii",
    )
    report = run_audit([item], [], reference_counts())
    findings = [f for f in report.findings if f.rule == "theme-subject"]
    assert findings
    assert "geamanduri-si-balizaj" in findings[0].detail


def test_every_theme_the_map_allows_is_accepted():
    """A signal may sit in three themes, and all three must really pass.

    The first version of this test invented its answer text, so the item
    bound to no catalogue, took the rule's `continue` branch, and passed for
    every theme the map could possibly hold — the eighth vacuous test of this
    project. The answer is now the catalogue's own quote, and the test proves
    the item binds before it proves anything else: in a foreign theme it must
    draw a finding, or the silence that follows means nothing.
    """
    from caa.themes import SUBJECT_THEMES

    def sitting_in(theme):
        item = replace(
            good_question(),
            id=f"semnal-{theme}",
            question="Ce este un sunet scurt?",
            options=("un sunet a cărui durată este de aproximativ o secundă.", "b", "c"),
            correct=0,
            theme=theme,
        )
        report = run_audit([item], [], reference_counts())
        return [f for f in report.findings if f.rule == "theme-subject"]

    assert sitting_in("prim-ajutor"), "the item no longer binds; the test below is void"
    for theme in SUBJECT_THEMES["signal"]:
        assert not sitting_in(theme), theme


def test_a_question_no_catalogue_binds_is_not_judged():
    """54 of 603 have a knowable subject; the rule must stay silent on the rest."""
    item = replace(
        good_question(),
        id="fara-subiect",
        question="Ce este un nod?",
        options=("a", "b", "c"),
        correct=0,
        theme="prim-ajutor",
    )
    report = run_audit([item], [], reference_counts())
    assert not [f for f in report.findings if f.rule == "theme-subject"]


@pytest.mark.anr
def test_the_real_bank_satisfies_the_rule(bank_questions):
    """The whole point: on the delivered bank this rule is silent."""
    report = run_audit(bank_questions, [], reference_counts())
    assert not [f for f in report.findings if f.rule == "theme-subject"]


@pytest.mark.parametrize("subject,base_question,wrong_theme", [
    (
        "buoy",
        replace(
            good_question(),
            id="q0032ae4e7e12",
            question="Corpul balizei marcajului cardinal de Est este piturat în dungi orizontale dispuse de sus în jos astfel:",
            options=("negru-galben-negru;", "b", "c"),
        ),
        "prim-ajutor",
    ),
    (
        "day-shape",
        replace(
            good_question(),
            id="q0e66324bca12",
            question="Un cilindru negru reprezintă semnul purtat de o navă:",
            options=("stânjenită de pescajul său.", "b", "c"),
        ),
        "semnale-sonore",
    ),
    (
        "signal",
        replace(
            good_question(),
            id="q726d94eb7b27",
            question="Ce semnale pot da navele care navigă prin şenal şi se îndoiesc de intenţiile navei care traversează şenalul?",
            options=("un semnal de avertizare compus din cinci sunete scurte.", "b", "c"),
        ),
        "constructia-ambarcatiunii",
    ),
    (
        "light",
        replace(
            good_question(),
            id="q03e2a6f00084",
            question="Lumina neîntreruptă pe un arc de orizont de 360° este:",
            options=("lumină vizibilă pe întreg orizontul.", "b", "c"),
        ),
        "prim-ajutor",
    ),
])
def test_each_subject_in_a_foreign_theme_produces_a_finding(subject, base_question, wrong_theme):
    """For each subject, filing in a wrong theme produces a finding."""
    item = replace(base_question, theme=wrong_theme)
    report = run_audit([item], [], reference_counts())
    findings = [f for f in report.findings if f.rule == "theme-subject"]
    assert findings, f"Expected theme-subject finding for {subject} in theme {wrong_theme}"
    assert subject in findings[0].detail


# Theory audit helpers
import functools
from unittest.mock import patch as mock_patch


@functools.lru_cache(maxsize=1)
def _bank_questions_list():
    """Cached module-level helper to build the bank questions once."""
    from caa.cli import build_all
    questions, _ = build_all(SOURCES)
    return questions


def _audit_with_theory(cards):
    """Run audit with a patched theory.THEORY, returning the full report."""
    from caa import theory
    with mock_patch.object(theory, "THEORY", cards):
        return run_audit(_bank_questions_list(), [], reference_counts())


@pytest.mark.anr
def test_a_theory_quote_the_bank_lost_is_reported():
    """Reworded by ANR, the quote proves nothing and the statement floats free."""
    from caa import theory

    ghost = theory.Card(
        theme="parame-noduri-ancore",
        statements=(theory.Statement(text="O regulă.", sources=("un text inexistent",)),),
    )
    report = _audit_with_theory((ghost,))
    findings = [f for f in report.findings if f.rule == "theory-source"]
    assert findings
    assert "un text inexistent" in findings[0].detail


@pytest.mark.anr
def test_a_theory_quote_from_a_foreign_theme_is_reported():
    """A knot rule resting on a first-aid question is shelved wrong."""
    from caa import theory

    foreign_quote = next(
        q.options[q.correct] for q in _bank_questions_list()
        if q.theme == "prim-ajutor"
    )
    card = theory.Card(
        theme="parame-noduri-ancore",
        statements=(theory.Statement(text="O regulă.", sources=(foreign_quote,)),),
    )
    report = _audit_with_theory((card,))
    findings = [f for f in report.findings if f.rule == "theory-theme"]
    assert findings
    # The detail must name the CARD's theme — the shelf the quote fails to sit
    # on — not the quote's own home. The first version of this assertion
    # checked `.rule` instead of `.detail`, which made it a substring test on
    # the literal "theory-theme": always true, guarding nothing.
    assert "parame-noduri-ancore" in findings[0].detail
    assert "prim-ajutor" not in findings[0].detail


@pytest.mark.anr
def test_the_real_theory_satisfies_both_rules():
    report = run_audit(_bank_questions_list(), [], reference_counts())
    assert not [f for f in report.findings if f.rule.startswith("theory-")]
