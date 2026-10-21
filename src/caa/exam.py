"""Exam rules as data, so Python and the application cannot drift apart.

Every number here comes from Part II of the ANR methodology, quoted in
section 2.4 of the design spec. The audit reads them to size its pools; the
application reads the same values, serialized into the page at build time.
Nothing retypes them.
"""

from __future__ import annotations

from typing import Final

from caa.structure import Discipline

# Per exam class: which disciplines are pooled together, and how many
# questions the exam draws from that pool. At class C, navigation and
# manoeuvring form a single 6-question subject.
EXAM_DRAW: Final[dict[str, tuple[tuple[tuple[str, ...], int], ...]]] = {
    "C": (
        ((Discipline.COLREG,), 10),
        ((Discipline.NAVIGATIE, Discipline.MANEVRA), 6),
        ((Discipline.MARINARIE,), 6),
        ((Discipline.PRIM_AJUTOR,), 2),
        ((Discipline.LEGISLATIE,), 2),
    ),
    "D": (
        ((Discipline.RND,), 10),
        ((Discipline.MARINARIE,), 6),
        ((Discipline.MANEVRA,), 6),
        ((Discipline.PRIM_AJUTOR,), 2),
        ((Discipline.LEGISLATIE,), 2),
    ),
}

EXAM_RULES: Final[dict[str, object]] = {
    "questions": 26,
    "minutes": 30,
    "pass": 22,
    "difference": {
        "questions": 10,
        "minutes": 10,
        "pass": 8,
        # Moving between classes is examined only on the distinctive discipline.
        "disciplines": {"C": (Discipline.COLREG,), "D": (Discipline.RND,)},
    },
}
