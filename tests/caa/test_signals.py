import json
from pathlib import Path

import pytest

from caa.signals import (
    BELL, DEFAULT_GAP, DURATIONS, GAPS, LONG, NOT_A_PATTERN, SHORT, SIGNALS,
    STROKE, VERY_SHORT, WHISTLE, looks_like_pattern, payload, resolve,
)

BANK = Path(__file__).resolve().parents[2] / "build" / "questions.json"


@pytest.fixture(scope="module")
def bank_answers() -> set[str]:
    if not BANK.is_file():
        pytest.skip("run `python -m caa.cli` first")
    data = json.loads(BANK.read_text(encoding="utf-8"))
    return {item["opts"][item["correct"]] for item in data["questions"]}


def test_every_quote_is_byte_identical_to_the_bank(bank_answers):
    """Byte-for-byte, not normalized.

    The audit's own rule compares through `normalize_key`, which strips
    punctuation — so it is blind to a quote whose curly “ ” were retyped as
    straight " ". That happened once here, on the NOT_A_PATTERN key, and
    nothing caught it. This is the only check that can.
    """
    quoted = [source for signal in SIGNALS for source in signal.sources]
    quoted.extend(NOT_A_PATTERN)
    altered = [text for text in quoted if text not in bank_answers]
    assert altered == []


def test_no_two_signals_claim_the_same_source(bank_answers):
    """A colliding source would silently shadow the earlier signal in the index."""
    quoted = [source for signal in SIGNALS for source in signal.sources]
    assert len(quoted) == len(set(quoted))
    assert not set(quoted) & set(NOT_A_PATTERN), "a quote is both played and excused"


def test_every_signal_has_an_id_a_label_and_at_least_one_source():
    for signal in SIGNALS:
        assert signal.id and signal.label and signal.sources
        assert signal.instrument in (WHISTLE, BELL)


def test_ids_are_unique():
    ids = [signal.id for signal in SIGNALS]
    assert len(ids) == len(set(ids))


def test_every_pattern_element_has_a_duration():
    for signal in SIGNALS:
        assert signal.pattern, signal.id
        for element in signal.pattern:
            assert element in DURATIONS, f"{signal.id}: {element}"


def test_only_the_bell_strikes():
    """A bell stroke is not a short sound; the whistle never strikes."""
    for signal in SIGNALS:
        strikes = STROKE in signal.pattern
        assert strikes == (signal.instrument == BELL), signal.id


def test_the_durations_come_from_the_bank():
    assert DURATIONS[SHORT] == 1000
    assert DURATIONS[LONG] == 4500
    assert DURATIONS[VERY_SHORT] == 250
    assert GAPS[VERY_SHORT] == 250
    assert DEFAULT_GAP == 500


def test_every_source_looks_like_a_pattern():
    """The recognition net must not be narrower than the catalogue itself."""
    for signal in SIGNALS:
        for source in signal.sources:
            assert looks_like_pattern(source), f"{signal.id}: {source!r}"


def test_the_excluded_answer_also_looks_like_a_pattern():
    """Otherwise the exception would be dead weight nobody needs."""
    for text in NOT_A_PATTERN:
        assert looks_like_pattern(text)


def test_a_plain_answer_does_not_look_like_a_pattern():
    assert not looks_like_pattern("un fluier şi un clopot.")
    assert not looks_like_pattern("cu semnale luminoase.")


def test_resolve_matches_on_the_whole_answer_not_a_fragment():
    answers = [
        ("q1", "un sunet scurt."),
        ("q2", "un sunet scurt, dar numai ziua."),
    ]
    assert resolve(answers) == {"q1": "vin-la-tribord"}


def test_resolve_ignores_diacritics_and_punctuation():
    assert resolve([("q1", "UN  SUNET   SCURT")]) == {"q1": "vin-la-tribord"}


def test_the_payload_carries_the_timing_and_every_signal():
    data = payload()
    assert len(data["signals"]) == len(SIGNALS)
    assert data["timing"]["defaultGap"] == DEFAULT_GAP
    assert data["timing"]["durations"][SHORT] == 1000
    json.dumps(data, ensure_ascii=False)  # serializable as-is
