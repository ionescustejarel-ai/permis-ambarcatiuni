"""Locates each raw row inside the structure of its source document.

Two things are determined here, both from position:

1. Section — each list holds three consecutive sections and the `Nr`
   column restarts at 1 at every boundary. Order is fixed by the source
   documents: main, first aid, legislation.

2. Discipline — the main section is itself a sequence of contiguous
   exam-discipline blocks, but the numbering runs continuously across
   them, so blocks are identified by `Nr` range. The ranges below were
   derived by transferring the module labels of the older, independently
   labelled question banks in sources/arhiva/ onto the official lists,
   and verified: 100% coverage, block sizes matching the old banks
   (COLREG 142 rows, Marinarie 162, RND 67).

Ranges are reference data. If a build fails because a row falls outside
every range, ANR changed the lists — reverify, do not widen the range to
make the build pass.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from caa.extract import RawRow


class Section:
    """Section identifiers, used as plain strings downstream."""

    MAIN: Final = "principal"
    FIRST_AID: Final = "prim-ajutor"
    LEGISLATION: Final = "legislatie"


class Discipline:
    """Exam discipline identifiers."""

    COLREG: Final = "COLREG"
    NAVIGATIE: Final = "NAVIGATIE"
    MARINARIE: Final = "MARINARIE"
    MANEVRA: Final = "MANEVRA"
    RND: Final = "RND"
    PRIM_AJUTOR: Final = "PRIM_AJUTOR"
    LEGISLATIE: Final = "LEGISLATIE"


_SECTION_ORDER: Final = (Section.MAIN, Section.FIRST_AID, Section.LEGISLATION)

_SECTION_DISCIPLINES: Final = {
    Section.FIRST_AID: Discipline.PRIM_AJUTOR,
    Section.LEGISLATION: Discipline.LEGISLATIE,
}

DISCIPLINE_RANGES: Final[dict[str, tuple[tuple[str, int, int], ...]]] = {
    "C": (
        (Discipline.COLREG, 1, 142),
        (Discipline.NAVIGATIE, 143, 209),
        (Discipline.MARINARIE, 210, 371),
        (Discipline.MANEVRA, 372, 489),
    ),
    "D": (
        (Discipline.RND, 1, 67),
        (Discipline.MARINARIE, 68, 229),
        (Discipline.MANEVRA, 230, 347),
    ),
}


@dataclass(frozen=True)
class LocatedRow:
    """A raw row tagged with its section and exam discipline."""

    nr: int
    question: str
    options: tuple[str, str, str]
    flags: tuple[str, str, str]
    source: str
    page: int
    section: str
    discipline: str


def _discipline_for(source: str, nr: int) -> str:
    for name, low, high in DISCIPLINE_RANGES[source]:
        if low <= nr <= high:
            return name
    raise ValueError(f"no discipline range covers list {source} nr={nr}")


def locate_rows(rows: list[RawRow]) -> list[LocatedRow]:
    """Tags each row with its section and discipline.

    Raises:
        ValueError: if the sequence does not yield exactly 3 sections, or
            if a main-section row falls outside every discipline range.
    """
    result: list[LocatedRow] = []
    section_index = 0
    previous_nr = 0

    for row in rows:
        if row.nr <= previous_nr:
            section_index += 1
            if section_index >= len(_SECTION_ORDER):
                raise ValueError(
                    f"expected 3 sections, found a 4th starting at nr={row.nr}"
                )
        previous_nr = row.nr
        section = _SECTION_ORDER[section_index]
        discipline = _SECTION_DISCIPLINES.get(section) or _discipline_for(row.source, row.nr)
        result.append(
            LocatedRow(
                nr=row.nr,
                question=row.question,
                options=row.options,
                flags=row.flags,
                source=row.source,
                page=row.page,
                section=section,
                discipline=discipline,
            )
        )

    if section_index != len(_SECTION_ORDER) - 1:
        raise ValueError(f"expected 3 sections, found {section_index + 1}")
    return result
