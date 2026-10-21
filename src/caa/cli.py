"""Runs the full build: PDFs in, questions.json and an audit report out.

Exit code 1 on any audit finding. Nothing downstream may consume a
questions.json produced by a failed run.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from caa.arcs import resolve as resolve_arcs
from caa.audit import AuditReport, render_report, run_audit
from caa.dedup import Question, build_questions
from caa.extract import extract_rows
from caa.figures import resolve as resolve_figures
from caa.lights import resolve as resolve_configs
from caa.signals import resolve
from caa.structure import locate_rows
from caa.themes import assign_themes

_REFERENCE_DATE = "2026-07-26"


def build_all(sources_dir: Path) -> tuple[list[Question], AuditReport]:
    """Runs every pipeline stage over the two official lists."""
    rows_c = extract_rows(sources_dir / "lista_C.pdf", source="C")
    rows_d = extract_rows(sources_dir / "lista_D.pdf", source="D")
    row_counts = {"C": len(rows_c), "D": len(rows_d)}

    located = locate_rows(rows_c) + locate_rows(rows_d)
    questions, conflicts = build_questions(located)
    questions = assign_themes(questions)
    questions.sort(key=lambda item: (item.section, item.theme or "", item.id))

    report = run_audit(questions, conflicts, row_counts)
    return questions, report


def to_json(questions: list[Question]) -> str:
    """Serializes the question set for the application bundle."""
    signal_of = resolve((item.id, item.options[item.correct]) for item in questions)
    figure_of = resolve_figures(
        (item.id, item.question, item.options[item.correct]) for item in questions
    )
    arc_of = resolve_arcs(
        (item.id, item.question, item.options[item.correct]) for item in questions
    )
    config_of = resolve_configs(
        (item.id, item.question, item.options[item.correct]) for item in questions
    )
    payload = {
        "reference_date": _REFERENCE_DATE,
        "count": len(questions),
        "questions": [
            {
                "id": item.id,
                "q": item.question,
                "opts": list(item.options),
                "correct": item.correct,
                "theme": item.theme,
                "section": item.section,
                "signal": signal_of.get(item.id),
                "figure": figure_of.get(item.id),
                "arc": arc_of.get(item.id),
                "config": config_of.get(item.id),
                "disciplines": {
                    exam_class: list(item.disciplines_for(exam_class))
                    for exam_class in item.classes
                },
                "classes": list(item.classes),
                "disputed": item.disputed,
            }
            for item in questions
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build questions.json from the ANR lists.")
    parser.add_argument("--sources", type=Path, default=Path("sources/anr"))
    parser.add_argument("--out", type=Path, default=Path("build"))
    args = parser.parse_args(argv)

    # Clear the previous artefact BEFORE running anything. A consumer that
    # checks for the file rather than the exit code must not be served stale
    # data, and the build can also fail by raising — ExtractionError, a
    # ValueError from locate_rows, a missing PDF — which would skip any cleanup
    # placed after the pipeline.
    args.out.mkdir(parents=True, exist_ok=True)
    questions_path = args.out / "questions.json"
    questions_path.unlink(missing_ok=True)

    questions, report = build_all(args.sources)

    (args.out / "audit-report.md").write_text(render_report(report), encoding="utf-8")

    if not report.ok:
        print(f"AUDIT PICAT: {len(report.findings)} constatari", file=sys.stderr)
        for finding in report.findings[:20]:
            print(f"  {finding.rule}: {finding.detail}", file=sys.stderr)
        print(f"Raport complet: {args.out / 'audit-report.md'}", file=sys.stderr)
        return 1

    questions_path.write_text(to_json(questions), encoding="utf-8")
    print(f"OK: {len(questions)} intrebari -> {questions_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
