import json
import re
from pathlib import Path

import pytest

from caa.rose import ROSES, payload

BANK = Path(__file__).resolve().parents[2] / "build" / "questions.json"


@pytest.fixture(scope="module")
def bank():
    if not BANK.is_file():
        pytest.skip("run `python -m caa.cli` first")
    return json.loads(BANK.read_text(encoding="utf-8"))["questions"]


def test_every_rose_has_a_distinct_id():
    ids = [rose.id for rose in ROSES]
    assert len(ids) == len(set(ids)), ids


def test_bearings_stay_on_the_circle():
    """Anything outside [0, 360) draws somewhere the reader cannot follow."""
    for rose in ROSES:
        for ray in rose.rays:
            assert 0 <= ray.bearing < 360, f"{rose.id}: ray at {ray.bearing}"
        for angle in rose.angles:
            assert 0 <= angle.start < 360 and 0 <= angle.end < 360, f"{rose.id}: {angle}"
        for bearing in (rose.mark, rose.bow):
            assert bearing is None or 0 <= bearing < 360, f"{rose.id}: {bearing}"


def test_every_number_printed_on_a_rose_is_the_banks_own(bank):
    """The rule that keeps a drawing honest, made mechanical.

    A rose is the first drawing in this project that prints numbers rather
    than shapes, and a printed number is a claim. Every one of them — the four
    cardinal bearings and the four quadrant examples — has to be a figure the
    bank itself gives, or the picture is teaching something no question asks.
    """
    corpus = " ".join(
        question["q"] + " " + " ".join(question["opts"]) for question in bank
    )
    for rose in ROSES:
        for ray in rose.rays:
            for number in re.findall(r"\d+", ray.label):
                assert number in corpus, f"{rose.id}: {number!r} is on no question"


def test_the_definition_roses_print_no_number_at_all(bank):
    """Their two directions are illustrative, so a number would be invention.

    The bow and the mark are placed where they read clearly, not where any
    source puts them. The drawing says which direction an angle starts from;
    the moment it printed a value it would be answering a question nobody
    asked.
    """
    for rose in ROSES:
        if not rose.angles:
            continue
        printed = [
            label
            for label in [ray.label for ray in rose.rays] + [a.label for a in rose.angles]
            if re.search(r"\d", label)
        ]
        assert printed == [], f"{rose.id}: {printed}"


def test_an_angle_is_labelled_with_its_name(bank):
    for rose in ROSES:
        for angle in rose.angles:
            assert angle.label.strip(), rose.id
            assert angle.start != angle.end, f"{rose.id}: {angle.label} spans nothing"


def test_the_payload_carries_every_rose():
    data = payload()
    assert {entry["id"] for entry in data["roses"]} == {rose.id for rose in ROSES}
    assert json.dumps(data, ensure_ascii=False)
