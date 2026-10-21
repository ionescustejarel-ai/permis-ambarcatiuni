"""Builds the single-file application.

Everything the page needs is inlined: the question bank, the exam rules, the
stylesheet and both scripts. The result opens from disk with the network off,
which is the point — the candidate studies on a phone, on a boat, on a train.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from caa.arcs import payload as arcs_payload
from caa.exam import EXAM_DRAW, EXAM_RULES
from caa.figures import payload as figures_payload
from caa.rose import payload as rose_payload
from caa.schema import payload as schema_payload
from caa.lights import payload as lights_payload
from caa.signals import payload as signals_payload
from caa.theory import payload as theory_payload

_MARKER = re.compile(
    r"/\*(STYLE|LOGIC|UI|AUDIO|FIGDRAW|ARCDRAW|LIGHTDRAW|ROSEDRAW|SCHEMADRAW"
    r"|QUESTIONS|RULES|SIGNALS|FIGURES|ARCS|LIGHTS|ROSES|SCHEMAS|THEORY)\*/"
)


def _rules_payload() -> dict[str, object]:
    """The exam rules, shaped for JSON: tuples become lists."""
    difference = EXAM_RULES["difference"]
    return {
        "questions": EXAM_RULES["questions"],
        "minutes": EXAM_RULES["minutes"],
        "pass": EXAM_RULES["pass"],
        "draw": {
            exam_class: [[list(disciplines), count] for disciplines, count in groups]
            for exam_class, groups in EXAM_DRAW.items()
        },
        "difference": {
            "questions": difference["questions"],
            "minutes": difference["minutes"],
            "pass": difference["pass"],
            "disciplines": {
                exam_class: list(disciplines)
                for exam_class, disciplines in difference["disciplines"].items()
            },
        },
    }


def _inline_json(text: str) -> str:
    """Makes a JSON document safe to sit inside a <script> element.

    A "<" anywhere in the payload can end the element early — a single
    "</script>" in a future edition of the question lists would break the page
    silently. Escaping it as \\u003c is still valid JSON and the parser is none
    the wiser. Today's bank contains no "<" at all; this keeps it that way by
    construction rather than by luck.
    """
    # chr(92), not a "<" literal: Python would decode that escape at parse
    # time and hand `.replace` the very character it is meant to remove, turning
    # this whole defence into a no-op that no test could see. Six characters are
    # wanted in the output — backslash, u, 0, 0, 3, c.
    return text.replace("<", chr(92) + "u003c")


def build_html(questions_path: Path, assets_dir: Path) -> str:
    """Returns the complete page as a string.

    Substitution is a single pass over the pristine template. Replacing markers
    one after another on a growing string would rescan already-inserted assets,
    so a stylesheet or script that merely mentions a later marker in a comment
    would have that mention overwritten instead of the real placeholder.
    """
    template = (assets_dir / "index.html").read_text(encoding="utf-8")
    questions_text = questions_path.read_text(encoding="utf-8")
    questions = json.loads(questions_text)["questions"]
    content = {
        "STYLE": (assets_dir / "app.css").read_text(encoding="utf-8"),
        "LOGIC": (assets_dir / "logic.js").read_text(encoding="utf-8"),
        "AUDIO": (assets_dir / "audio.js").read_text(encoding="utf-8"),
        "UI": (assets_dir / "ui.js").read_text(encoding="utf-8"),
        "FIGDRAW": (assets_dir / "figures.js").read_text(encoding="utf-8"),
        "ARCDRAW": (assets_dir / "arcs.js").read_text(encoding="utf-8"),
        "ROSEDRAW": (assets_dir / "rose.js").read_text(encoding="utf-8"),
        "SCHEMADRAW": (assets_dir / "schema.js").read_text(encoding="utf-8"),
        "LIGHTDRAW": (assets_dir / "lights.js").read_text(encoding="utf-8"),
        "QUESTIONS": _inline_json(questions_text),
        "RULES": _inline_json(json.dumps(_rules_payload(), ensure_ascii=False)),
        "SIGNALS": _inline_json(json.dumps(signals_payload(), ensure_ascii=False)),
        "FIGURES": _inline_json(json.dumps(figures_payload(), ensure_ascii=False)),
        "ARCS": _inline_json(json.dumps(arcs_payload(), ensure_ascii=False)),
        "LIGHTS": _inline_json(json.dumps(lights_payload(), ensure_ascii=False)),
        "ROSES": _inline_json(json.dumps(rose_payload(), ensure_ascii=False)),
        "SCHEMAS": _inline_json(json.dumps(schema_payload(), ensure_ascii=False)),
        "THEORY": _inline_json(json.dumps(theory_payload(questions), ensure_ascii=False)),
    }
    return _MARKER.sub(lambda match: content[match.group(1)], template)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the single-file application.")
    parser.add_argument("--questions", type=Path, default=Path("build/questions.json"))
    parser.add_argument("--assets", type=Path, default=Path("src/caa/assets"))
    parser.add_argument("--out", type=Path, default=Path("build/permis-ambarcatiuni.html"))
    args = parser.parse_args(argv)

    if not args.questions.is_file():
        print(f"lipseste {args.questions} — ruleaza intai `python -m caa.cli`")
        return 1

    page = build_html(args.questions, args.assets)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"OK: {len(page.encode('utf-8')) // 1024} KB -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
