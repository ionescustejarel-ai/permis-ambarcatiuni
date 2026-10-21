import json
from pathlib import Path

import pytest

from caa.arcs import ARCS, NOT_AN_ARC, looks_like_arc, payload, resolve

BANK = Path(__file__).resolve().parents[2] / "build" / "questions.json"
COLOURS = {"white", "green", "red", "yellow"}


@pytest.fixture(scope="module")
def bank():
    if not BANK.is_file():
        pytest.skip("run `python -m caa.cli` first")
    return json.loads(BANK.read_text(encoding="utf-8"))["questions"]


def span(sector):
    """The opening in degrees, mirroring what logic.js computes."""
    value = (sector.end - sector.start) % 360
    return 360.0 if value == 0 else value


def test_the_catalogue_has_five_arcs_with_unique_ids():
    assert len(ARCS) == 5
    assert len({arc.id for arc in ARCS}) == 5


def test_every_arc_is_well_formed():
    for arc in ARCS:
        assert arc.id and arc.label and arc.sources, arc.id
        assert arc.sectors, arc.id
        for sector in arc.sectors:
            assert 0 <= sector.start <= 360, arc.id
            assert 0 <= sector.end <= 360, arc.id
            assert sector.colour is None or sector.colour in COLOURS, arc.id


def test_the_openings_are_the_ones_the_bank_states():
    """The numbers the exam asks for, read off the catalogue."""
    openings = {arc.id: [span(sector) for sector in arc.sectors] for arc in ARCS}
    assert openings["lumina-de-catarg"] == [225.0]
    assert openings["lumina-de-pupa"] == [135.0]
    assert openings["lumina-de-remorcaj"] == [135.0]
    assert openings["lumini-de-bord"] == [112.5, 112.5]
    assert openings["tot-orizontul"] == [360.0]


def test_the_masthead_arc_is_225_not_the_lost_digit():
    """One stem says 22°5; the other question and COLREG say 225."""
    masthead = next(arc for arc in ARCS if arc.id == "lumina-de-catarg")
    assert span(masthead.sectors[0]) == 225.0


def test_the_sidelights_are_green_to_starboard_and_red_to_port():
    """Swapping them is the one mistake that would fail the candidate."""
    sides = next(arc for arc in ARCS if arc.id == "lumini-de-bord")
    starboard = next(s for s in sides.sectors if s.colour == "green")
    port = next(s for s in sides.sectors if s.colour == "red")
    # Starboard is to the right of the bow: bearings just above 0.
    assert starboard.start == 0 and starboard.end == 112.5
    # Port is to the left: bearings just below 360.
    assert port.start == 247.5 and port.end == 360


def test_every_quote_is_byte_identical_to_the_bank(bank):
    """Byte for byte, not normalized: normalize_key is blind to punctuation."""
    texts = {item["q"] for item in bank} | {item["opts"][item["correct"]] for item in bank}
    quoted = [source for arc in ARCS for source in arc.sources]
    quoted.extend(NOT_AN_ARC)
    quoted.extend(key for arc in ARCS for key in arc.caveats)
    assert [text for text in quoted if text not in texts] == []


def test_every_caveat_belongs_to_a_quote_of_its_own_arc():
    """A caveat keyed on anything else is a note that will never be shown."""
    for arc in ARCS:
        for key in arc.caveats:
            assert key in arc.sources, f"{arc.id}: {key!r}"


def test_no_two_arcs_claim_the_same_source():
    quoted = [source for arc in ARCS for source in arc.sources]
    assert len(quoted) == len(set(quoted))


def test_the_recognizer_and_the_catalogue_agree_on_the_bank(bank):
    """Stated over questions, not over quotes.

    A quote need not look like an arc on its own — the property that matters
    is that the recognizer and the catalogue see the same ten questions.
    Either direction failing is a real defect.
    """
    recognized = {
        item["id"] for item in bank
        if looks_like_arc(item["q"], item["opts"][item["correct"]])
    }
    bound = set(resolve(
        (item["id"], item["q"], item["opts"][item["correct"]]) for item in bank
    ))
    assert bound == recognized
    assert len(bound) == 10


def test_a_question_about_a_vessel_is_not_an_arc_question():
    """These belong to the vessel-configuration catalogue of stage 3d."""
    assert not looks_like_arc(
        "Ce lumini trebuie să poarte o navă cu pernă de aer în exploatare fără pescaj?",
        "luminile unei nave cu propulsie mecanică în marş plus o lumină galbenă cu "
        "sclipiri vizibilă pe tot orizontul.")
    assert not looks_like_arc(
        "La ce distanţă trebuie să se vadă lumina albă vizibilă pe tot orizontul, "
        "a unei nave?", "3 Mm.")


def test_the_flashing_light_is_not_claimed_at_all():
    """Its source gives a rate, not an arc, so nothing should reach for it."""
    assert not looks_like_arc(
        'Ce se înţelege prin expresia "lumină cu sclipiri"?',
        "o lumină cu sclipiri regulate cu frecvenţa de 120 sclipiri pe minut sau mai mult.")


def test_resolve_matches_the_stem_as_well_as_the_answer():
    """Both branches, each proved by an entry the other cannot explain.

    The first entry's stem is a registered quote and its answer is not; the
    second is the other way round. With only the first, removing the
    answer-matching branch entirely left this test green — the definitions
    are split evenly between the two fields, so half the catalogue would
    have stopped binding with nothing here to notice.
    """
    entries = [
        # Stem is a source; the answer is not registered anywhere.
        ("q1", "Lumina neîntreruptă pe un arc de orizont de 360° este:",
         "lumină vizibilă pe întreg orizontul."),
        # Stem is not a source; the answer is.
        ("q2", 'Ce se înţelege prin expresia "lumină de remorcaj"?',
         "o lumină galbenă aşezată cât mai aproape posibil de pupa, arătând o "
         "lumină neîntreruptă pe un arc de cerc de 135°, câte 67°5 în fiecare bord."),
    ]
    assert resolve(entries) == {"q1": "tot-orizontul", "q2": "lumina-de-remorcaj"}


def test_the_stern_and_towing_lights_differ_only_by_colour():
    """They share an arc, and that is exactly why the pair is drawn.

    Nothing else pins their colours: both openings read 135°, so swapping
    white and yellow between them would pass every other test here.
    """
    stern = next(arc for arc in ARCS if arc.id == "lumina-de-pupa")
    towing = next(arc for arc in ARCS if arc.id == "lumina-de-remorcaj")
    assert [span(s) for s in stern.sectors] == [span(s) for s in towing.sectors]
    assert stern.sectors[0].colour == "white"
    assert towing.sectors[0].colour == "yellow"


def test_the_payload_carries_every_arc_and_its_caveats():
    data = payload()
    assert len(data["arcs"]) == 5
    masthead = next(a for a in data["arcs"] if a["id"] == "lumina-de-catarg")
    assert len(masthead["caveats"]) == 1
    json.dumps(data, ensure_ascii=False)
