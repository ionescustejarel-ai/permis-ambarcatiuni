from pathlib import Path

import pytest

pytestmark = pytest.mark.anr

from caa.extract import RawRow, extract_rows
from caa.structure import Discipline, LocatedRow, Section, locate_rows

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def located_c() -> list[LocatedRow]:
    return locate_rows(extract_rows(ROOT / "sources" / "anr" / "lista_C.pdf", source="C"))


@pytest.fixture(scope="module")
def located_d() -> list[LocatedRow]:
    return locate_rows(extract_rows(ROOT / "sources" / "anr" / "lista_D.pdf", source="D"))


def _count(rows, **criteria):
    return sum(1 for row in rows if all(getattr(row, k) == v for k, v in criteria.items()))


def test_section_sizes_match_the_reference(located_c, located_d):
    assert _count(located_c, section=Section.MAIN) == 442
    assert _count(located_c, section=Section.FIRST_AID) == 50
    assert _count(located_c, section=Section.LEGISLATION) == 25

    assert _count(located_d, section=Section.MAIN) == 296
    assert _count(located_d, section=Section.FIRST_AID) == 50
    assert _count(located_d, section=Section.LEGISLATION) == 25


def test_discipline_block_sizes_match_the_reference(located_c, located_d):
    assert _count(located_c, discipline=Discipline.COLREG) == 142
    assert _count(located_c, discipline=Discipline.NAVIGATIE) == 65
    assert _count(located_c, discipline=Discipline.MARINARIE) == 153
    assert _count(located_c, discipline=Discipline.MANEVRA) == 82

    assert _count(located_d, discipline=Discipline.RND) == 64
    assert _count(located_d, discipline=Discipline.MARINARIE) == 150
    assert _count(located_d, discipline=Discipline.MANEVRA) == 82


def test_every_main_row_gets_a_discipline(located_c, located_d):
    for row in [*located_c, *located_d]:
        assert row.discipline, f"row {row.source}{row.nr} has no discipline"


def test_discipline_boundaries_are_exact(located_c):
    by_nr = {row.nr: row for row in located_c if row.section == Section.MAIN}
    assert by_nr[142].discipline == Discipline.COLREG
    assert by_nr[143].discipline == Discipline.NAVIGATIE
    assert by_nr[209].discipline == Discipline.NAVIGATIE
    assert by_nr[210].discipline == Discipline.MARINARIE
    assert by_nr[371].discipline == Discipline.MARINARIE
    # 372-407 is a gap in the source numbering — those numbers do not exist —
    # so 371 and 408 are adjacent rows and this pair IS the boundary.
    assert by_nr[408].discipline == Discipline.MANEVRA


def test_non_main_sections_take_their_discipline_from_the_section(located_c):
    first_aid = [row for row in located_c if row.section == Section.FIRST_AID]
    legislation = [row for row in located_c if row.section == Section.LEGISLATION]
    assert {row.discipline for row in first_aid} == {Discipline.PRIM_AJUTOR}
    assert {row.discipline for row in legislation} == {Discipline.LEGISLATIE}


def test_first_aid_section_starts_with_the_known_question(located_c):
    first_aid = [row for row in located_c if row.section == Section.FIRST_AID]
    assert first_aid[0].nr == 1
    assert first_aid[0].question.startswith("Care este durata maximă a masajului")


def test_a_number_outside_every_range_is_rejected():
    rows = [
        RawRow(nr=9999, question="q", options=("a", "b", "c"), flags=("1", "0", "0"), source="C", page=1)
    ]
    with pytest.raises(ValueError, match="no discipline range"):
        locate_rows(rows)


def test_more_than_three_sections_is_rejected():
    rows = [
        RawRow(nr=n, question="q", options=("a", "b", "c"), flags=("1", "0", "0"), source="C", page=1)
        for n in [1, 2, 1, 2, 1, 2, 1]
    ]
    with pytest.raises(ValueError, match="expected 3 sections"):
        locate_rows(rows)
