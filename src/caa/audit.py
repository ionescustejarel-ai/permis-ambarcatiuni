"""Validation rules for the generated question set.

The audit never repairs anything. It reports, and the CLI turns any
finding into a failed build. A wrong answer shipped to a candidate is
worse than no application at all.

Deliberately NOT a rule: continuity of the `Nr` column. The gaps are real
in the source documents, and checking them would fail the build on
correct data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from caa.arcs import (
    ARCS, ARC_SHAPE, NOT_AN_ARC, drawn_texts as arc_texts, looks_like_arc,
    resolve as resolve_arcs,
)
from caa.dedup import DedupConflict, Question
from caa.exam import EXAM_DRAW
from caa.figures import DAY_SHAPE, NOT_A_FIGURE, FIGURES, drawn_texts, looks_like_figure, resolve as resolve_figures
from caa import catalogue, lights
from caa.lights import resolve as resolve_configs
from caa.normalize import normalize_key
from caa import rose, schema as schema_cat, theory
from caa.signals import NOT_A_PATTERN, SIGNALS, looks_like_pattern, played_answers, resolve as resolve_signals
from caa.structure import Section
from caa.themes import FALLBACK_THEME, theme_distribution, themes_for_subject

REFERENCE: Final[dict[str, int]] = {
    "rows_c": 517,
    "rows_d": 371,
    "items_c": 504,
    "items_d": 366,
    "shared": 267,
    "only_c": 237,
    "only_d": 99,
    "total": 603,
    "disputed": 2,
    "main": 527,
    "first_aid": 50,
    "legislation": 26,
}

_MAX_FALLBACK_SHARE: Final = 0.25

@dataclass(frozen=True)
class AuditFinding:
    """One rule violation."""

    rule: str
    detail: str


@dataclass(frozen=True)
class AuditReport:
    """Result of a full audit pass."""

    findings: tuple[AuditFinding, ...] = ()
    distribution: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.findings


def _check_shape(questions: list[Question]) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for item in questions:
        if len(item.options) != 3 or any(not option.strip() for option in item.options):
            findings.append(AuditFinding("options", f"{item.id}: {item.options!r}"))
        if not 0 <= item.correct <= 2:
            findings.append(AuditFinding("correct-index", f"{item.id}: {item.correct}"))
        if not item.question.strip():
            findings.append(AuditFinding("empty-question", item.id))
        if item.theme is None:
            findings.append(AuditFinding("theme", f"{item.id}: no theme assigned"))
        if not item.disciplines:
            findings.append(AuditFinding("discipline", f"{item.id}: no discipline"))
        if len({option.strip().casefold() for option in item.options}) != 3:
            # Two identical options make a question unanswerable by reading it:
            # picking the one that is not flagged fails you for the right text.
            findings.append(AuditFinding("duplicate-options", f"{item.id}: {item.options!r}"))
        if not item.classes:
            findings.append(AuditFinding("class", f"{item.id}: no exam class"))
        if item.disputed and len(item.classes) != 1:
            findings.append(
                AuditFinding("disputed-class", f"{item.id}: {item.classes!r}")
            )
    return findings


def _check_ids(questions: list[Question]) -> list[AuditFinding]:
    """Ids are the schema's promise to everything downstream; enforce it here.

    Saved progress is keyed by id, so a collision silently merges two questions'
    history. This was asserted only by a test, and a test is not the gate.
    """
    seen: dict[str, str] = {}
    findings: list[AuditFinding] = []
    for item in questions:
        if item.id in seen:
            findings.append(
                AuditFinding("duplicate-id", f"{item.id}: {seen[item.id]!r} / {item.question!r}")
            )
        seen[item.id] = item.question
    return findings


def _check_totals(questions: list[Question], row_counts: dict[str, int]) -> list[AuditFinding]:
    findings: list[AuditFinding] = []

    for source, key in (("C", "rows_c"), ("D", "rows_d")):
        actual = row_counts.get(source)
        if actual != REFERENCE[key]:
            findings.append(
                AuditFinding("row-count", f"list {source}: got {actual}, expected {REFERENCE[key]}")
            )

    by_section = lambda name: sum(1 for item in questions if item.section == name)
    expectations = (
        ("total", len(questions), REFERENCE["total"]),
        ("items_c", sum(1 for i in questions if "C" in i.classes), REFERENCE["items_c"]),
        ("items_d", sum(1 for i in questions if "D" in i.classes), REFERENCE["items_d"]),
        ("shared", sum(1 for i in questions if i.classes == ("C", "D")), REFERENCE["shared"]),
        ("only_c", sum(1 for i in questions if i.classes == ("C",)), REFERENCE["only_c"]),
        ("only_d", sum(1 for i in questions if i.classes == ("D",)), REFERENCE["only_d"]),
        ("disputed", sum(1 for i in questions if i.disputed), REFERENCE["disputed"]),
        ("main", by_section(Section.MAIN), REFERENCE["main"]),
        ("first_aid", by_section(Section.FIRST_AID), REFERENCE["first_aid"]),
        ("legislation", by_section(Section.LEGISLATION), REFERENCE["legislation"]),
    )
    for label, actual, expected in expectations:
        if actual != expected:
            findings.append(AuditFinding("totals", f"{label}: got {actual}, expected {expected}"))
    return findings


def _check_exam_pools(questions: list[Question]) -> list[AuditFinding]:
    """Every exam subject must hold at least as many questions as it draws."""
    findings: list[AuditFinding] = []
    for exam_class, groups in EXAM_DRAW.items():
        for disciplines, needed in groups:
            pool = sum(
                1
                for item in questions
                if exam_class in item.classes
                and any(name in item.disciplines_for(exam_class) for name in disciplines)
            )
            if pool < needed:
                findings.append(
                    AuditFinding(
                        "exam-pool",
                        f"class {exam_class} {'+'.join(disciplines)}: pool {pool}, draws {needed}",
                    )
                )
    return findings


def _check_fallback_share(questions: list[Question]) -> list[AuditFinding]:
    main = [item for item in questions if item.section == Section.MAIN]
    if not main:
        return []
    fallback = sum(1 for item in main if item.theme == FALLBACK_THEME)
    share = fallback / len(main)
    if share > _MAX_FALLBACK_SHARE:
        return [
            AuditFinding(
                "fallback-share",
                f"{fallback}/{len(main)} = {share:.0%} above the {_MAX_FALLBACK_SHARE:.0%} limit",
            )
        ]
    return []


def _answer_texts(questions: list[Question]) -> list[str]:
    """Correct answers, skipping the ones `_check_shape` already reports."""
    return [
        item.options[item.correct]
        for item in questions
        if 0 <= item.correct < len(item.options)
    ]


def _quotable_texts(questions: list[Question]) -> list[str]:
    """Every field a catalogue may quote: the question as well as the answer."""
    return [item.question for item in questions] + _answer_texts(questions)


def _source_findings(rule: str, sourced, texts: list[str]) -> list[AuditFinding]:
    """One shape for all three catalogues: a quote the bank no longer holds."""
    return [
        AuditFinding(rule, f"{entry_id}: no text matches {source!r}")
        for entry_id, source in catalogue.orphan_sources(sourced, texts)
    ]


def _check_signal_sources(questions: list[Question]) -> list[AuditFinding]:
    """Every catalogue quote must still exist in the bank.

    The catalogue quotes the bank verbatim. If ANR reworded an answer, the
    quote stops matching and the signal would silently attach to nothing —
    so the build stops here instead.
    """
    # Answers only: a sound pattern is never stated in a question.
    return _source_findings(
        "signal-source", [(s.id, s.sources) for s in SIGNALS], _answer_texts(questions)
    )


def _check_signal_coverage(questions: list[Question]) -> list[AuditFinding]:
    """Every answer shaped like a signal is either played or excused.

    The net is wider than the catalogue on purpose: a signal the bank gains
    in a future edition lands here and demands a decision, rather than
    passing unnoticed because nobody thought to look for it.

    The question the rule asks is about an *answer*, so it is settled on the
    answer text alone. Going through `resolve`, which is keyed by question id,
    let two questions sharing an id share their coverage: one of them matching
    a catalogue entry marked the other one covered too, and a genuinely
    unplayable signal passed in silence. `_check_ids` happens to co-fire on
    that input today, but a rule that only holds because a neighbouring rule
    catches the same case is not a rule.
    """
    played = played_answers()
    excused = {normalize_key(text) for text in NOT_A_PATTERN}
    findings: list[AuditFinding] = []
    for item in questions:
        # `_check_shape` reports an out-of-range index; indexing here would
        # raise before it ever got the chance.
        if not (0 <= item.correct < len(item.options)):
            continue
        answer = item.options[item.correct]
        if not looks_like_pattern(answer):
            continue
        if normalize_key(answer) in played or normalize_key(answer) in excused:
            continue
        findings.append(
            AuditFinding("signal-coverage", f"{item.id}: no signal for {answer!r}")
        )
    return findings


def _check_figure_sources(questions: list[Question]) -> list[AuditFinding]:
    """Every catalogue quote must still exist in the bank.

    Both fields are searched, because a mark is described in the question as
    often as in the answer.
    """
    return _source_findings(
        "figure-source", [(f.id, f.sources) for f in FIGURES], _quotable_texts(questions)
    )


def _check_figure_coverage(questions: list[Question]) -> list[AuditFinding]:
    """Every question describing a mark is drawn by some entry, or excused.

    Settled on the texts, not on the question id: going through an id-keyed
    mapping let two questions sharing an id share their coverage at stage 3a.

    The two fields are pooled deliberately, and the limit that follows is
    stated rather than hidden. Coverage is a property of the *question*: the
    language that identifies one as being about a mark is usually not the text
    the catalogue quotes. "Corpul balizei marcajului cardinal de Est este
    piturat în dungi orizontale…" is what the recognizer sees, while the quote
    that binds it is its answer, "negru-galben-negru;". Requiring each
    describing field to be a catalogue text in its own right was tried and
    failed the build on six correct questions.

    What this does not catch: a question that names a drawn mark in one field
    and a second, undrawn one in the other. The recognizer cannot tell a mark
    from mark-adjacent language, so no cheap rule separates that case from the
    six above. `test_a_second_undrawn_mark_in_the_other_field_is_not_caught`
    pins the behaviour so nobody tightens it without measuring again.
    """
    drawn = drawn_texts()
    excused = {normalize_key(text) for text in NOT_A_FIGURE}
    findings: list[AuditFinding] = []
    for item in questions:
        # `_check_shape` reports an out-of-range index; indexing here would
        # raise before it ever got the chance.
        if not (0 <= item.correct < len(item.options)):
            continue
        fields = (item.question, item.options[item.correct])
        describing = catalogue.announcing(fields, looks_like_figure)
        if not describing:
            continue
        keys = {normalize_key(text) for text in fields}
        if keys & drawn or keys & excused:
            continue
        # Name a field that actually describes a mark, not whichever came
        # second: a finding quoting the innocent neighbour sends the reader to
        # excuse the wrong text.
        findings.append(
            AuditFinding("figure-coverage", f"{item.id}: no figure for {describing[0]!r}")
        )
    return findings


def _check_arc_sources(questions: list[Question]) -> list[AuditFinding]:
    """Every catalogue quote must still exist in the bank."""
    return _source_findings(
        "arc-source", [(a.id, a.sources) for a in ARCS], _quotable_texts(questions)
    )


def _check_arc_coverage(questions: list[Question]) -> list[AuditFinding]:
    """Every question defining a light by its arc is drawn, or excused.

    Settled on the texts, like the figure rule: a question id cannot decide
    it. Pooled across the two fields on purpose — the language that marks a
    question as an arc definition is often not the text the catalogue quotes.
    """
    drawn = arc_texts()
    excused = {normalize_key(text) for text in NOT_AN_ARC}
    findings: list[AuditFinding] = []
    for item in questions:
        # `_check_shape` reports an out-of-range index; indexing here would
        # raise before it ever got the chance.
        if not (0 <= item.correct < len(item.options)):
            continue
        answer = item.options[item.correct]
        if not looks_like_arc(item.question, answer):
            continue
        keys = {normalize_key(item.question), normalize_key(answer)}
        if keys & drawn or keys & excused:
            continue
        # Name a field that actually announces an arc, not whichever came
        # second. At stage 3b the finding quoted the answer unconditionally,
        # and a gap in the stem sent the reader to excuse the wrong text.
        described = catalogue.announcing(
            (item.question, answer), lambda text: ARC_SHAPE.search(normalize_key(text))
        )
        # Non-empty today because `looks_like_arc` gates on the same pattern
        # over the same two fields — but that is an invariant nobody stated,
        # and an edit that decoupled the two would turn a finding into an
        # IndexError that stops the build for the wrong reason.
        if not described:
            continue
        findings.append(
            AuditFinding("arc-coverage", f"{item.id}: no arc for {described[0]!r}")
        )
    return findings


def _check_arc_caveats(questions: list[Question]) -> list[AuditFinding]:
    """A caveat must key on one of its own arc's quotes.

    Keyed on anything else it is a note the interface will never find an
    occasion to show, and the reader is left with a figure that looks like it
    contradicts the question in front of them.
    """
    findings: list[AuditFinding] = []
    for arc in ARCS:
        for key in arc.caveats:
            if key not in arc.sources:
                findings.append(
                    AuditFinding("arc-caveat", f"{arc.id}: caveat on a foreign quote {key!r}")
                )
    return findings


def _check_config_sources(questions: list[Question]) -> list[AuditFinding]:
    """Every catalogue quote must still exist in the bank."""
    return _source_findings(
        "config-source",
        [(config.id, config.sources) for config in lights.CONFIGS],
        _quotable_texts(questions),
    )


def _check_config_coverage(questions: list[Question]) -> list[AuditFinding]:
    """Every question asking what a vessel carries is drawn, or excused.

    Settled on the texts, like the figure and arc rules: a question id cannot
    decide it. The two fields are pooled because the language that marks a
    question as a configuration question is often not the text the catalogue
    quotes — "Ce lumini poartă o navă cu vele în marş?" is what the recognizer
    sees, and for the towed vessel it is also the binding quote, while for the
    pushed vessel the quote is the answer instead.
    """
    drawn = lights.drawn_texts()
    excused = {normalize_key(text) for text in lights.NOT_A_CONFIG}
    findings: list[AuditFinding] = []
    for item in questions:
        # `_check_shape` reports an out-of-range index; indexing here would
        # raise before it ever got the chance.
        if not (0 <= item.correct < len(item.options)):
            continue
        answer = item.options[item.correct]
        if not lights.looks_like_config(item.question, answer):
            continue
        keys = {normalize_key(item.question), normalize_key(answer)}
        if keys & drawn or keys & excused:
            continue
        # Quote a field that is actually about lights. The stem of a question
        # whose answer is bare — "20 m." — would otherwise send whoever reads
        # the report to excuse a measurement.
        described = catalogue.announcing(
            (item.question, answer),
            lambda text: lights.ABOUT_LIGHTS.search(normalize_key(text)),
        )
        if not described:
            continue
        findings.append(
            AuditFinding("config-coverage", f"{item.id}: no configuration for {described[0]!r}")
        )
    return findings


def _check_theme_subject(questions: list[Question]) -> list[AuditFinding]:
    """A question a catalogue can identify must sit in a theme for that subject.

    This is the only part of the theme assignment that can be checked at all:
    54 of the 603 questions are bound to a catalogue, and for those the subject
    is a fact rather than a reading. The other 549 are not judged here, and no
    rule should pretend otherwise.
    """
    fields = [(item.id, item.question, item.options[item.correct])
              for item in questions if 0 <= item.correct < len(item.options)]
    answers = [(item.id, item.options[item.correct])
               for item in questions if 0 <= item.correct < len(item.options)]

    figure_of = resolve_figures(fields)
    signal_of = resolve_signals(answers)
    arc_of = resolve_arcs(fields)
    config_of = resolve_configs(fields)
    day_shapes = {figure.id for figure in FIGURES if figure.system == DAY_SHAPE}

    findings: list[AuditFinding] = []
    for item in questions:
        figure = figure_of.get(item.id)
        if figure is not None:
            subject = "day-shape" if figure in day_shapes else "buoy"
        elif item.id in signal_of:
            subject = "signal"
        elif item.id in arc_of or item.id in config_of:
            subject = "light"
        else:
            continue
        allowed = themes_for_subject(subject)
        if item.theme not in allowed:
            findings.append(AuditFinding(
                "theme-subject",
                f"{item.id}: a {subject} question is in {item.theme!r}, "
                f"not in {sorted(allowed)}",
            ))
    return findings


def _check_theory_sources(questions: list[Question]) -> list[AuditFinding]:
    """Every quote a statement carries must still exist in the bank.

    The statements are prose; the quotes are their only tether to the bank.
    A quote ANR reworded leaves the statement claiming something no question
    asks, which is the ballast the parent spec forbids — and a statement with
    no quote at all is that ballast by definition, so it fails here rather
    than merely in a test.

    Built on `caa.catalogue` like the other four catalogues' source rules: a
    fifth hand-rolled copy of the same loop is the duplication this project
    already paid down once.
    """
    findings = [
        AuditFinding("theory-source", f"{card.theme}: statement with no source: {statement.text[:60]!r}")
        for card in theory.THEORY
        for statement in card.statements
        if not statement.sources
    ]
    entries = [
        (card.theme, statement.sources)
        for card in theory.THEORY
        for statement in card.statements
    ]
    findings.extend(_source_findings("theory-source", entries, _quotable_texts(questions)))
    return findings


def _check_theory_themes(questions: list[Question]) -> list[AuditFinding]:
    """Every quote must belong to a question of the card's own theme.

    Shelving is content: a rope rule sourced from a weather question would
    put true facts where the candidate is not studying them. The check also
    catches a card naming a theme that does not exist, whose quotes then
    belong to nothing.
    """
    by_theme: dict[str, set[str]] = {}
    for item in questions:
        if not (0 <= item.correct < len(item.options)):
            continue
        keys = by_theme.setdefault(item.theme or "", set())
        keys.add(normalize_key(item.question))
        keys.add(normalize_key(item.options[item.correct]))
    findings: list[AuditFinding] = []
    for card in theory.THEORY:
        themed = by_theme.get(card.theme, set())
        for statement in card.statements:
            for source in statement.sources:
                if normalize_key(source) not in themed:
                    findings.append(AuditFinding(
                        "theory-theme",
                        f"{card.theme}: quote from outside the theme: {source[:60]!r}",
                    ))
    return findings


def _check_theory_drawings() -> list[AuditFinding]:
    """A statement's drawing must exist in the catalogue its kind names.

    The reference is a string, so a typo is silent: the page would simply
    render nothing beside the rule, and every test that counts statements
    would still pass. Checked here, at the build, rather than discovered by
    somebody opening the theme.
    """
    catalogues = {
        "arc": {entry.id for entry in ARCS},
        "figure": {entry.id for entry in FIGURES},
        "config": {entry.id for entry in lights.CONFIGS},
        "signal": {entry.id for entry in SIGNALS},
        "rose": {entry.id for entry in rose.ROSES},
        "schema": {entry.id for entry in schema_cat.SCHEMAS},
    }
    findings = []
    for card in theory.THEORY:
        for statement in card.statements:
            if not statement.drawing:
                continue
            kind, _, ident = statement.drawing.partition(":")
            known = catalogues.get(kind)
            if known is None:
                findings.append(AuditFinding(
                    "theory-drawing",
                    f"{card.theme}: unknown drawing kind {kind!r} in {statement.drawing!r}",
                ))
            elif ident not in known:
                findings.append(AuditFinding(
                    "theory-drawing",
                    f"{card.theme}: no {kind} called {ident!r}",
                ))
    return findings


def run_audit(
    questions: list[Question],
    conflicts: list[DedupConflict],
    row_counts: dict[str, int],
) -> AuditReport:
    """Runs every rule and collects the findings."""
    findings: list[AuditFinding] = []
    findings.extend(_check_shape(questions))
    findings.extend(
        AuditFinding("dedup-conflict", f"{item.question!r}: {item.correct_texts!r}")
        for item in conflicts
    )
    findings.extend(_check_ids(questions))
    findings.extend(_check_totals(questions, row_counts))
    findings.extend(_check_exam_pools(questions))
    findings.extend(_check_fallback_share(questions))
    findings.extend(_check_signal_sources(questions))
    findings.extend(_check_signal_coverage(questions))
    findings.extend(_check_figure_sources(questions))
    findings.extend(_check_figure_coverage(questions))
    findings.extend(_check_arc_sources(questions))
    findings.extend(_check_arc_coverage(questions))
    findings.extend(_check_arc_caveats(questions))
    findings.extend(_check_config_sources(questions))
    findings.extend(_check_config_coverage(questions))
    findings.extend(_check_theme_subject(questions))
    findings.extend(_check_theory_sources(questions))
    findings.extend(_check_theory_themes(questions))
    findings.extend(_check_theory_drawings())
    return AuditReport(findings=tuple(findings), distribution=theme_distribution(questions))


def render_report(report: AuditReport) -> str:
    """Renders the audit result as markdown."""
    lines = ["# Raport de audit", ""]
    lines.append("**Stare:** " + ("TRECUT" if report.ok else "PICAT"))
    lines.append("")

    lines.append("## Distribuția pe teme")
    lines.append("")
    # The limit of the theme-subject rule, stated where the reader is: only
    # the catalogue-bound questions have a knowable subject, so only those are
    # checked. Left unsaid, this table reads as though every theme were.
    lines.append(
        "Tema e verificată de audit doar pentru întrebările legate de un catalog "
        "(semnale, marcaje, arcuri, configurații — 54 din 603); pentru rest nu "
        "există un adevăr față de care să fie judecată."
    )
    lines.append("")
    lines.append("| Temă | Întrebări |")
    lines.append("|---|---|")
    for theme, count in sorted(report.distribution.items(), key=lambda pair: -pair[1]):
        lines.append(f"| {theme} | {count} |")
    lines.append("")

    lines.append("## Constatări")
    lines.append("")
    if report.ok:
        lines.append("Niciuna.")
    else:
        lines.append("| Regulă | Detaliu |")
        lines.append("|---|---|")
        for finding in report.findings:
            lines.append(f"| {finding.rule} | {finding.detail} |")
    lines.append("")
    return "\n".join(lines)
