import re
from pathlib import Path

import fitz
import pytest

pytestmark = pytest.mark.anr

from caa.extract import RawRow, extract_rows

ROOT = Path(__file__).resolve().parents[2]
LISTA_C = ROOT / "sources" / "anr" / "lista_C.pdf"
LISTA_D = ROOT / "sources" / "anr" / "lista_D.pdf"

# One row in lista_C genuinely renders a blank middle flag cell — verified in
# the source, not an extraction artefact. It still marks exactly one option, so
# later stages keep the question. Keyed by (source, nr, page) because `nr`
# restarts in each section and lista_C holds three rows numbered 6.
KNOWN_BLANK_FLAG_ROWS = {("C", 6, 24)}


@pytest.fixture(scope="module")
def rows_c() -> list[RawRow]:
    return extract_rows(LISTA_C, source="C")


@pytest.fixture(scope="module")
def rows_d() -> list[RawRow]:
    return extract_rows(LISTA_D, source="D")


def test_extracts_the_reference_row_count(rows_c, rows_d):
    assert len(rows_c) == 517
    assert len(rows_d) == 371


def test_every_row_has_three_options_and_three_flags(rows_c, rows_d):
    for row in [*rows_c, *rows_d]:
        assert len(row.options) == 3
        assert len(row.flags) == 3


def test_flags_are_binary_strings(rows_c, rows_d):
    for row in [*rows_c, *rows_d]:
        if (row.source, row.nr, row.page) in KNOWN_BLANK_FLAG_ROWS:
            continue
        assert set(row.flags) <= {"0", "1"}, f"row {row.source}{row.nr} p{row.page}"


def test_every_row_marks_exactly_one_correct_option(rows_c, rows_d):
    for row in [*rows_c, *rows_d]:
        assert sum(1 for flag in row.flags if flag == "1") == 1, f"{row.source}{row.nr}"


def test_first_question_of_lista_c_is_read_verbatim(rows_c):
    first = rows_c[0]
    assert first.nr == 1
    assert first.question == "Căror nave li se aplică prevederile Colreg-1972?"
    assert first.flags == ("0", "0", "1")


def test_hidden_column_values_stay_out_of_the_option_text(rows_d):
    """lista_D carries a 2pt column whose digits used to glue onto option text."""
    first = rows_d[0]
    assert first.options[0] == "circa ½ s"
    assert not first.options[0].startswith("1")


def test_no_cell_pulls_text_from_another_row(rows_c):
    """A row in lista_C used to absorb text from 500pt further down the page."""
    row = next(r for r in rows_c if r.nr == 355 and r.page == 16)
    assert row.question == "Cabestanul este :"
    assert row.options[1] == "dispozitiv de manevra"


def test_baseline_jitter_does_not_reorder_characters(rows_d):
    """A trailing digit sits 0.5pt higher; deriving order from y0 moved it first."""
    row = next(r for r in rows_d if r.nr == 28 and r.page == 2)
    assert row.options[1] == "Obişnuită, 1370"
    assert row.options[2] == "Obişnuită, 1350"


def test_every_extracted_fragment_exists_in_the_page(rows_c, rows_d):
    """The integrity guarantee: extraction never invents text."""
    squash = lambda text: re.sub(r"\s+", "", text)
    for path, rows in ((LISTA_C, rows_c), (LISTA_D, rows_d)):
        document = fitz.open(path)
        pages = {i + 1: squash(document[i].get_text()) for i in range(len(document))}
        for row in rows:
            for text in (row.question, *row.options):
                squashed = squash(text)
                if len(squashed) >= 12:
                    assert squashed in pages[row.page], f"{row.source}{row.nr}: {text!r}"


def test_whitespace_inside_cells_is_collapsed(rows_c):
    for row in rows_c:
        assert "\n" not in row.question
        assert "  " not in row.question


def test_source_is_recorded(rows_c, rows_d):
    assert {row.source for row in rows_c} == {"C"}
    assert {row.source for row in rows_d} == {"D"}
