import json
from pathlib import Path

import pytest

from caa.figures import (
    DAY_SHAPE, DUNARE, FIGURES, IALA, NOT_A_FIGURE,
    looks_like_figure, payload, resolve,
)

BANK = Path(__file__).resolve().parents[2] / "build" / "questions.json"

SHAPES = {"pillar", "cone-up", "cone-down", "cylinder", "sphere", "two-spheres", "pennant"}
COLOURS = {"black", "yellow", "green", "red", "white", "blue"}


@pytest.fixture(scope="module")
def bank():
    if not BANK.is_file():
        pytest.skip("run `python -m caa.cli` first")
    data = json.loads(BANK.read_text(encoding="utf-8"))
    return data["questions"]


def test_the_catalogue_has_twelve_figures_with_unique_ids():
    assert len(FIGURES) == 12
    assert len({figure.id for figure in FIGURES}) == 12


def test_every_figure_is_well_formed():
    for figure in FIGURES:
        assert figure.id and figure.label and figure.sources, figure.id
        assert figure.system in (IALA, DUNARE, DAY_SHAPE), figure.id
        assert figure.body.shape in SHAPES, figure.id
        assert figure.body.bands, figure.id
        for colour in figure.body.bands:
            assert colour in COLOURS, f"{figure.id}: {colour}"
        if figure.body.border is not None:
            assert figure.body.border in COLOURS, figure.id
        if figure.light is not None:
            assert figure.light.colour in COLOURS, figure.id
            assert figure.light.rhythm == "intermitenta", figure.id


def test_the_cardinals_carry_no_topmark_and_no_light():
    """The bank asks only about their body stripes; drawing more has no quote."""
    for figure_id in ("cardinal-est", "cardinal-nord", "cardinal-vest"):
        figure = next(f for f in FIGURES if f.id == figure_id)
        assert figure.body.shape == "pillar"
        assert figure.light is None


def test_the_east_and_west_cardinals_are_not_the_same_figure():
    """Their stripe order is the whole difficulty; a copy-paste would erase it."""
    east = next(f for f in FIGURES if f.id == "cardinal-est")
    west = next(f for f in FIGURES if f.id == "cardinal-vest")
    assert east.body.bands == ("black", "yellow", "black")
    assert west.body.bands == ("yellow", "black", "yellow")


def test_every_quote_is_byte_identical_to_the_bank(bank):
    """Byte for byte, not normalized.

    The audit compares through `normalize_key`, which strips punctuation and
    is therefore blind to a curly quotation mark retyped straight. That
    happened once at stage 3a and nothing caught it.
    """
    texts = {item["q"] for item in bank} | {item["opts"][item["correct"]] for item in bank}
    quoted = [source for figure in FIGURES for source in figure.sources]
    quoted.extend(NOT_A_FIGURE)
    assert [text for text in quoted if text not in texts] == []


def test_no_two_figures_claim_the_same_source():
    quoted = [source for figure in FIGURES for source in figure.sources]
    assert len(quoted) == len(set(quoted))
    assert not set(quoted) & set(NOT_A_FIGURE)


def test_the_recognizer_and_the_catalogue_agree_on_the_bank(bank):
    """The property the audit needs, stated over questions rather than quotes.

    A source quote need not look like a mark on its own: four of them are bare
    answers — "negru-galben-negru;" among them — and the language that marks
    them out lives in the stem. Asserting it of the quotes forced the net wide
    enough to swallow two ship-light questions, which belong to stage 3c.

    What must hold is that the recognizer and the catalogue see the same
    fourteen questions. Either direction failing is a real defect: a bound
    question the recognizer misses means the coverage rule guards nothing, and
    a recognized question the catalogue does not bind fails the build.
    """
    recognized = {
        item["id"] for item in bank
        if looks_like_figure(item["q"]) or looks_like_figure(item["opts"][item["correct"]])
    }
    bound = set(resolve(
        (item["id"], item["q"], item["opts"][item["correct"]]) for item in bank
    ))
    assert bound == recognized
    assert len(bound) == 14


def test_a_rule_about_marks_does_not_look_like_a_figure():
    assert not looks_like_figure("Marcajele laterale din sistemul de balizaj semnalizează")
    assert not looks_like_figure("2 Mm.")


def test_resolve_matches_the_stem_as_well_as_the_answer():
    """Half the marks are described in the question, not in the answer."""
    entries = [
        ("q1", "Un cilindru negru reprezintă semnul purtat de o navă:", "stânjenită de pescajul său."),
        ("q2", "Marcajul de pericol izolat are ca semn de vârf:", "doua bule suprapuse de culoare neagra."),
    ]
    assert resolve(entries) == {"q1": "semn-cilindru-negru", "q2": "pericol-izolat"}


def test_resolve_matches_on_the_whole_field_not_a_fragment():
    entries = [("q1", "Ce spune despre un cilindru roșu si altele?", "un cilindru roșu, dar numai ziua.")]
    assert resolve(entries) == {}


def test_the_two_buoyage_systems_stay_apart():
    """A green cone is left on the Danube and a red cylinder is port at IALA."""
    left = next(f for f in FIGURES if f.id == "geamandura-stanga")
    port = next(f for f in FIGURES if f.id == "topmark-babord-a")
    assert left.system == DUNARE and left.body.shape == "cone-up"
    assert port.system == IALA and port.body.shape == "cylinder"


def test_the_payload_carries_every_figure():
    data = payload()
    assert len(data["figures"]) == 12
    assert {f["id"] for f in data["figures"]} == {f.id for f in FIGURES}
    json.dumps(data, ensure_ascii=False)


def test_the_catalogue_covers_fourteen_questions(bank):
    entries = ((item["id"], item["q"], item["opts"][item["correct"]]) for item in bank)
    assert len(resolve(entries)) == 14


def test_a_question_whose_two_fields_name_different_figures_raises():
    """Silence would drop one of them, and picking the stem is not a policy."""
    stem = "Un cilindru negru reprezintă semnul purtat de o navă:"
    answer = "un cilindru roșu."
    with pytest.raises(ValueError, match="semn-cilindru-negru.*topmark-babord-a"):
        resolve([("q1", stem, answer)])


def test_the_same_figure_named_by_both_fields_is_not_a_conflict():
    stem = "Un cilindru negru reprezintă semnul purtat de o navă:"
    assert resolve([("q1", stem, stem)]) == {"q1": "semn-cilindru-negru"}
