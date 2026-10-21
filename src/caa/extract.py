"""Extracts raw table rows from the official ANR question-list PDFs.

This is the only module aware of the PDF library. Everything downstream
works on RawRow instances.

Both documents draw ruled tables, so the ruling lines give an exact cell
grid and every glyph can be placed by its own centre. Character-level
placement is deliberate, not incidental: lista_D carries a 2pt-wide column
at x=380 holding values from an unused layer, and the PDF text layer glues
those digits onto the first word of the option beside them. Placing whole
words puts the merged token's centre inside the option column and the digit
ends up in the displayed text; placing characters keeps each digit in the
hidden column where it belongs.

The two-axis grid also prevents a cell from absorbing text elsewhere on the
page — one row of lista_C used to pick up content 500pt further down.

The `Nr` column contains gaps: the authority removed questions and kept the
numbering. Never treat a gap as a parsing failure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import fitz

_WHITESPACE = re.compile(r"\s+")
_RULE_TOLERANCE = 2.0
_TEXT_MIN_WIDTH = 100.0
_FLAG_MIN_WIDTH = 20.0
_FLAG_MAX_WIDTH = 60.0
_VERIFY_MIN_LENGTH = 12


class ExtractionError(RuntimeError):
    """Raised when extracted text cannot be found in its source page."""


@dataclass(frozen=True)
class RawRow:
    """One question row exactly as it appears in a source PDF."""

    nr: int
    question: str
    options: tuple[str, str, str]
    flags: tuple[str, str, str]
    source: str
    page: int


def _cluster(values: list[float], tolerance: float) -> list[float]:
    """Merges near-identical coordinates; ruled borders are drawn twice."""
    merged: list[float] = []
    for value in sorted(values):
        if not merged or value - merged[-1] > tolerance:
            merged.append(value)
        else:
            merged[-1] = (merged[-1] + value) / 2
    return merged


def _rules(page) -> tuple[list[float], list[float]]:
    """Returns the page's horizontal and vertical ruling coordinates."""
    horizontals: list[float] = []
    verticals: list[float] = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] == "re":
                rect = item[1]
                if rect.height < 2:
                    horizontals.append((rect.y0 + rect.y1) / 2)
                if rect.width < 2:
                    verticals.append((rect.x0 + rect.x1) / 2)
            elif item[0] == "l":
                start, end = item[1], item[2]
                if abs(start.y - end.y) < 1:
                    horizontals.append((start.y + end.y) / 2)
                if abs(start.x - end.x) < 1:
                    verticals.append((start.x + end.x) / 2)
    return (
        _cluster(horizontals, _RULE_TOLERANCE),
        _cluster(verticals, _RULE_TOLERANCE),
    )


def _band(edges: list[float], value: float) -> int | None:
    """Index of the band containing value, or None if outside the grid."""
    for index in range(len(edges) - 1):
        if edges[index] <= value < edges[index + 1]:
            return index
    return None


def _layout(verticals: list[float]) -> dict[str, object]:
    """Maps ruled columns onto the eight fields, by width not by index.

    The two lists differ: lista_C rules 9 columns, lista_D rules 11 because
    of its hidden column and two spacers.
    """
    wide = [
        i for i in range(len(verticals) - 1)
        if verticals[i + 1] - verticals[i] >= _TEXT_MIN_WIDTH
    ]
    narrow = [
        i for i in range(len(verticals) - 1)
        if _FLAG_MIN_WIDTH <= verticals[i + 1] - verticals[i] <= _FLAG_MAX_WIDTH
    ]
    # Both counts are exact, not minimums: `narrow[1:4]` assumes the flags are
    # the three columns right after the number. A narrow column appearing
    # between them would silently shift the mapping, so an unexpected layout
    # must fail loudly instead.
    if len(wide) != 4 or len(narrow) != 4:
        widths = [round(verticals[i + 1] - verticals[i], 1) for i in range(len(verticals) - 1)]
        raise ExtractionError(f"unrecognised column layout, widths {widths}")
    return {
        "nr": narrow[0],
        "question": wide[0],
        "options": wide[1:4],
        "flags": narrow[1:4],
    }


def _page_rows(page, source: str, number: int) -> list[RawRow]:
    horizontals, verticals = _rules(page)
    if len(horizontals) < 2 or len(verticals) < 2:
        # A page with no ruled table carries no rows. Anything ruled must map,
        # so `_layout` raises rather than skipping the page silently: a page
        # dropped without a signal would be baked in as correct the next time
        # someone re-baselines REFERENCE against a new edition of the lists.
        return []
    layout = _layout(verticals)

    # The grid decides which cell a glyph belongs to. The document decides the
    # order they are read in — characters are appended as encountered, never
    # re-sorted. Deriving the order from rounded coordinates instead produced a
    # defect the source does not have: in lista_D row 28 the trailing digit of
    # "1370" sits 0.49pt higher than the rest of its line, so rounding put it in
    # an earlier bucket and it came out as "0Obişnuită, 137".
    buckets: dict[tuple[int, int], list[str]] = {}
    for block in page.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                for char in span["chars"]:
                    x0, y0, x1, y1 = char["bbox"]
                    column = _band(verticals, (x0 + x1) / 2)
                    row = _band(horizontals, (y0 + y1) / 2)
                    if column is None or row is None:
                        continue
                    buckets.setdefault((row, column), []).append(char["c"])

    def cell(row: int, column: int) -> str:
        return _WHITESPACE.sub(" ", "".join(buckets.get((row, column), []))).strip()

    rows: list[RawRow] = []
    for row in range(len(horizontals) - 1):
        nr = cell(row, layout["nr"])
        if not nr.isdigit():
            continue  # header or spacer band
        rows.append(
            RawRow(
                nr=int(nr),
                question=cell(row, layout["question"]),
                options=tuple(cell(row, c) for c in layout["options"]),
                flags=tuple(cell(row, c) for c in layout["flags"]),
                source=source,
                page=number,
            )
        )
    return rows


def _verify(rows: list[RawRow], pages: dict[int, str]) -> None:
    """Every fragment must occur verbatim in its own page.

    Know what this does NOT guarantee. The test is page-wide, not cell-scoped,
    so it catches text pulled in from elsewhere but is blind to characters
    reordered within one cell: a scrambled fragment can still be a substring of
    the page. That class is prevented at the source instead — `_page_rows`
    keeps the document's own character order rather than deriving one.
    """
    squash = lambda text: _WHITESPACE.sub("", text)
    defects = [
        f"{row.source}{row.nr} p{row.page}: {text!r}"
        for row in rows
        for text in (row.question, *row.options)
        if len(squash(text)) >= _VERIFY_MIN_LENGTH and squash(text) not in pages[row.page]
    ]
    if defects:
        joined = "\n  ".join(defects[:10])
        raise ExtractionError(
            f"{len(defects)} fragment(s) absent from their source page:\n  {joined}"
        )


def extract_rows(pdf_path: Path, source: str) -> list[RawRow]:
    """Reads every question row from one official list.

    Args:
        pdf_path: path to lista_C.pdf or lista_D.pdf.
        source: "C" or "D" — which exam class this list belongs to.

    Returns:
        Rows in document order.

    Raises:
        ExtractionError: if any produced text is absent from its page.
    """
    document = fitz.open(pdf_path)
    rows: list[RawRow] = []
    pages: dict[int, str] = {}
    for number, page in enumerate(document, start=1):
        pages[number] = _WHITESPACE.sub("", page.get_text())
        rows.extend(_page_rows(page, source, number))
    _verify(rows, pages)
    return rows
