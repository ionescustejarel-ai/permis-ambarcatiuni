import json
import re
from pathlib import Path

import pytest

from caa.schema import SCHEMAS, payload

BANK = Path(__file__).resolve().parents[2] / "build" / "questions.json"

# Every view the catalogue may name. A typo would draw an empty box, which
# reads as a rendering glitch rather than as a missing picture.
VIEWS = {"sectiune-lung", "sectiune-trans", "plan-carma", "plan-vant"}


@pytest.fixture(scope="module")
def bank():
    if not BANK.is_file():
        pytest.skip("run `python -m caa.cli` first")
    return json.loads(BANK.read_text(encoding="utf-8"))["questions"]


def test_every_schema_has_a_distinct_id_and_a_known_view():
    ids = [entry.id for entry in SCHEMAS]
    assert len(ids) == len(set(ids)), ids
    for entry in SCHEMAS:
        assert entry.view in VIEWS, f"{entry.id}: unknown view {entry.view!r}"


def test_a_side_is_a_board_the_bank_names():
    """"tribord" and "babord" are the bank's own words; anything else is mine."""
    for entry in SCHEMAS:
        assert entry.side in (None, "tribord", "babord"), f"{entry.id}: {entry.side!r}"


def test_no_schema_prints_a_number(bank):
    """The bank gives none of these drawings a measurement.

    The keel has no length, the frames no count — "la intervale egale" is all
    the bank says — and the leeway no angle. A figure on any of these would be
    answering a question nobody asked, which is the line the compass points
    and the knots are already on the far side of.
    """
    for entry in SCHEMAS:
        for text in (entry.label, entry.note or ""):
            assert not re.search(r"\d", text), f"{entry.id}: {text!r}"


# Verbs I conjugate to hold a caption together. Everything else on a drawing
# has to be a word the bank writes — inverted from the first draft of this
# test, which whitelisted the nouns and so checked only words it already
# trusted: renaming `varange` to an invented `crevaliere` sailed straight
# through, because an invented word was simply not on the list.
MINE = {"prelungește", "micșorează"}


def test_every_word_on_a_drawing_is_the_banks_own(bank):
    """The nouns on a diagram have to be the bank's, not a shipwright's.

    Checked against the whole bank rather than one theme: `chila` is written
    in construction questions and `derivă` in weather ones, and the drawings
    sit on statements in both.
    """
    corpus = " ".join(
        question["q"] + " " + " ".join(question["opts"]) for question in bank
    ).lower()
    for entry in SCHEMAS:
        for text in (entry.label, entry.note or ""):
            for word in re.findall(r"[\wăâîșțĂÂÎȘȚ]+", text.lower()):
                if word in MINE:
                    continue
                assert word in corpus, f"{entry.id}: {word!r} is on no question"


def test_the_payload_carries_every_schema():
    data = payload()
    assert {entry["id"] for entry in data["schemas"]} == {entry.id for entry in SCHEMAS}
    assert json.dumps(data, ensure_ascii=False)
