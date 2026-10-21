import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.anr

from caa.arcs import ARCS
from caa.audit import EXAM_DRAW, REFERENCE
from caa.cli import build_all, to_json
from caa.figures import FIGURES
from caa.signals import SIGNALS
from caa.structure import Discipline

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "sources" / "anr"


@pytest.fixture(scope="module")
def result():
    return build_all(SOURCES)


@pytest.fixture(scope="module")
def built(result):
    """The parsed JSON payload from to_json(questions)."""
    questions, _ = result
    return json.loads(to_json(questions))


def test_a_failing_audit_blocks_the_build(tmp_path, monkeypatch):
    """The gate itself: a finding must stop the build and write no questions.json.

    The real sources pass, so this path is unreachable end to end — it is forced
    here because an unexercised gate is not a gate.
    """
    from caa import cli
    from caa.audit import AuditFinding, AuditReport

    monkeypatch.setattr(
        cli,
        "run_audit",
        lambda *args, **kwargs: AuditReport(
            findings=(AuditFinding("totals", "forced"),), distribution={}
        ),
    )
    stale = tmp_path / "questions.json"
    stale.write_text("din rularea anterioara", encoding="utf-8")

    code = cli.main(["--sources", str(SOURCES), "--out", str(tmp_path)])

    assert code == 1
    assert not stale.exists(), "a failed build must not leave a valid-looking artefact"
    assert "PICAT" in (tmp_path / "audit-report.md").read_text(encoding="utf-8")


def test_audit_passes_on_the_real_sources(result):
    _, report = result
    assert report.ok, "\n".join(f"{f.rule}: {f.detail}" for f in report.findings)


def test_produces_the_expected_number_of_questions(result):
    questions, _ = result
    assert len(questions) == REFERENCE["total"]


def test_first_aid_is_identical_in_both_lists(result):
    questions, _ = result
    first_aid = [q for q in questions if q.theme == "prim-ajutor"]
    assert len(first_aid) == REFERENCE["first_aid"]
    assert all(q.classes == ("C", "D") for q in first_aid)


def test_legislation_is_shared_except_one_question_per_class(result):
    """One penalty question lists different amounts in each official list."""
    questions, _ = result
    legislation = [q for q in questions if q.theme == "legislatie"]
    assert len(legislation) == REFERENCE["legislation"]
    assert sum(1 for q in legislation if "C" in q.classes) == 25
    assert sum(1 for q in legislation if "D" in q.classes) == 25
    assert sum(1 for q in legislation if q.classes == ("C", "D")) == 24


def test_disputed_items_are_bound_to_exactly_one_class(result):
    questions, _ = result
    disputed = [q for q in questions if q.disputed]
    assert len(disputed) == REFERENCE["disputed"]
    assert all(len(q.classes) == 1 for q in disputed)
    assert {q.classes[0] for q in disputed} == {"C", "D"}


def test_every_exam_subject_has_a_large_enough_pool(result):
    questions, _ = result
    for exam_class, groups in EXAM_DRAW.items():
        for disciplines, needed in groups:
            pool = sum(
                1
                for q in questions
                if exam_class in q.classes
                and any(d in q.disciplines_for(exam_class) for d in disciplines)
            )
            assert pool >= needed, f"class {exam_class} {disciplines}: {pool} < {needed}"


def test_colreg_belongs_to_class_c_only(result):
    questions, _ = result
    colreg = [q for q in questions if ("C", Discipline.COLREG) in q.disciplines]
    assert colreg, "no COLREG questions found"
    assert all(q.classes == ("C",) or q.classes == ("C", "D") for q in colreg)
    assert not any(("D", Discipline.COLREG) in q.disciplines for q in questions)


def test_ids_are_unique(result):
    questions, _ = result
    assert len({q.id for q in questions}) == len(questions)


def test_json_round_trips_with_the_expected_shape(result):
    questions, _ = result
    payload = json.loads(to_json(questions))
    assert payload["count"] == len(questions)
    assert payload["reference_date"] == "2026-07-26"
    sample = payload["questions"][0]
    assert set(sample) == {
        "id", "q", "opts", "correct", "theme", "section",
        "signal", "figure", "arc", "config", "disciplines", "classes", "disputed",
    }
    assert len(sample["opts"]) == 3
    assert sample["opts"][sample["correct"]]


def test_build_is_deterministic(result):
    questions, _ = result
    again, _ = build_all(SOURCES)
    assert to_json(questions) == to_json(again)


def test_the_bank_carries_the_signal_ids(result):
    questions, _ = result
    payload = json.loads(to_json(questions))
    with_signal = [q for q in payload["questions"] if q["signal"]]
    assert len(with_signal) == 12, "twelve questions are covered by the catalogue"
    assert {q["signal"] for q in with_signal} <= {signal.id for signal in SIGNALS}


def test_every_question_has_the_signal_field(result):
    """Absent and null are different: a missing key would break the page."""
    questions, _ = result
    payload = json.loads(to_json(questions))
    assert all("signal" in q for q in payload["questions"])


def test_the_bank_carries_the_figure_ids(result):
    questions, _ = result
    payload = json.loads(to_json(questions))
    with_figure = [q for q in payload["questions"] if q["figure"]]
    assert len(with_figure) == 14, "fourteen questions describe a mark"
    assert {q["figure"] for q in with_figure} == {figure.id for figure in FIGURES}


def test_every_question_has_the_figure_field(result):
    questions, _ = result
    payload = json.loads(to_json(questions))
    assert all("figure" in q for q in payload["questions"])


def test_the_bank_carries_the_arc_ids(result):
    questions, _ = result
    payload = json.loads(to_json(questions))
    with_arc = [q for q in payload["questions"] if q["arc"]]
    assert len(with_arc) == 10, "ten questions define a light by its arc"
    assert {q["arc"] for q in with_arc} == {arc.id for arc in ARCS}


def test_every_question_has_the_arc_field(result):
    questions, _ = result
    payload = json.loads(to_json(questions))
    assert all("arc" in q for q in payload["questions"])


def test_the_build_binds_eighteen_questions_to_a_configuration(built):
    bound = [item for item in built["questions"] if item.get("config")]
    assert len(bound) == 18
    assert len({item["config"] for item in bound}) == 12


def test_the_sailing_vessel_binds_to_a_different_configuration_at_each_class(built):
    by_config = {}
    for item in built["questions"]:
        config = item.get("config")
        if config and config.startswith("vele-in-mars"):
            by_config.setdefault(config, set()).update(item["classes"])
    assert by_config["vele-in-mars"] == {"C"}
    assert by_config["vele-in-mars-D"] == {"D"}


def test_no_question_carries_both_an_arc_and_a_configuration(built):
    """Two figures for one question would be two answers to the same picture."""
    both = [item["id"] for item in built["questions"] if item.get("arc") and item.get("config")]
    assert both == []
