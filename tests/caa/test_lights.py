import json
from pathlib import Path

import pytest

from caa.lights import (
    ANY,
    BOW,
    CONFIGS,
    MAST,
    NOT_A_CONFIG,
    SIDE,
    STATIONS,
    STERN,
    drawn_texts,
    looks_like_config,
    payload,
    resolve,
)
from caa.normalize import normalize_key

BANK = Path(__file__).resolve().parents[2] / "build" / "questions.json"
COLOURS = {"white", "green", "red", "yellow"}


@pytest.fixture(scope="module")
def bank():
    if not BANK.is_file():
        pytest.skip("run `python -m caa.cli` first")
    return json.loads(BANK.read_text(encoding="utf-8"))["questions"]


def by_id(config_id):
    return next(config for config in CONFIGS if config.id == config_id)


def test_the_catalogue_has_twelve_configurations_with_unique_ids():
    assert len(CONFIGS) == 12
    assert len({config.id for config in CONFIGS}) == 12


def test_every_configuration_is_well_formed():
    for config in CONFIGS:
        assert config.id and config.label and config.sources, config.id
        assert config.lights, config.id
        for light in config.lights:
            assert light.station in STATIONS, config.id
            assert light.level >= 0, config.id
            assert set(light.colours) <= COLOURS, config.id


def test_no_configuration_puts_two_lanterns_in_one_place():
    """Two lights at the same station and level would draw on top of each other."""
    for config in CONFIGS:
        slots = [(light.station, light.level) for light in config.lights]
        assert len(slots) == len(set(slots)), config.id


def test_every_quote_is_byte_identical_to_the_bank(bank):
    """normalize_key is blind to punctuation, so it cannot catch a retyped quote."""
    corpus = {question["q"] for question in bank}
    corpus |= {option for question in bank for option in question["opts"]}
    for config in CONFIGS:
        for source in config.sources:
            assert source in corpus, f"{config.id}: {source[:60]!r}"
    for text in NOT_A_CONFIG:
        assert text in corpus, text[:60]


def test_no_two_configurations_claim_the_same_quote():
    """The index is keyed on the text: a shared quote would silently shadow one."""
    seen = {}
    for config in CONFIGS:
        for source in config.sources:
            assert source not in seen, f"{config.id} and {seen.get(source)}"
            seen[source] = config.id


def test_the_towed_vessel_and_the_sailing_vessel_bind_through_their_stems():
    """Both answer 'luminile din borduri şi lumina de pupa.' word for word.

    Quoting that answer would give the two configurations one key between
    them, and whichever was built second would take both questions. The stems
    differ, so the catalogue binds on those.
    """
    shared = "luminile din borduri şi lumina de pupa."
    for config_id in ("vele-in-mars", "remorcata"):
        assert shared not in by_id(config_id).sources


def test_the_sailing_vessel_is_not_the_same_at_the_two_classes():
    """The whole reason the panel filters by class."""
    at_c = by_id("vele-in-mars")
    at_d = by_id("vele-in-mars-D")
    masthead = lambda config: [light for light in config.lights if light.station == MAST]
    assert masthead(at_c) == []
    assert [light.colours for light in masthead(at_d)] == [("red",), ("green",)]
    assert [light.level for light in masthead(at_d)] == [1, 0]


def test_the_supplementary_lights_are_red_over_green():
    """The source says 'o lumină roişie deasupra unei lumini verzi'."""
    lights = {light.level: light.colours for light in by_id("vele-lumini-suplimentare").lights}
    assert lights[1] == ("red",)
    assert lights[0] == ("green",)


def test_the_combined_lantern_is_one_lantern_showing_three_colours():
    """'reunite într-un felinar' — one lantern, not three lights stacked."""
    lights = by_id("vele-felinar-combinat").lights
    assert len(lights) == 1
    assert lights[0].station == MAST
    assert set(lights[0].colours) == {"red", "green", "white"}


def test_the_anchor_light_carries_no_colour():
    """The bank never states it, in any of the six questions that mention it."""
    stern = [light for light in by_id("manevra-redusa-la-ancora").lights if light.station == STERN]
    assert [light.colours for light in stern] == [()]


def test_towed_alongside_carries_its_sidelights_at_the_bow():
    """'la extremitatea prova' is the only thing telling it from a plain tow."""
    assert {light.station for light in by_id("remorcata-la-ureche").lights} == {BOW, STERN}
    assert {light.station for light in by_id("remorcata").lights} == {SIDE, STERN}


def test_the_trawler_stacks_green_over_white_with_the_masthead_light_apart():
    stacked = {light.level: light.colours
               for light in by_id("traulare-nu-in-mars").lights if light.station == ANY}
    assert stacked == {1: ("green",), 0: ("white",)}
    assert [light.station for light in by_id("traulare-nu-in-mars").lights].count(MAST) == 1


def test_the_recognizer_and_the_catalogue_agree_on_the_bank(bank):
    """Every question the net catches is drawn or excused, and the net catches all of them."""
    drawn = drawn_texts()
    excused = {normalize_key(text) for text in NOT_A_CONFIG}
    caught, gaps = [], []
    for question in bank:
        answer = question["opts"][question["correct"]]
        if not looks_like_config(question["q"], answer):
            continue
        caught.append(question)
        keys = {normalize_key(question["q"]), normalize_key(answer)}
        if not (keys & drawn or keys & excused):
            gaps.append(question["q"])
    assert len(caught) == 23
    assert gaps == []


def test_the_recognizer_needs_the_text_to_be_about_lights(bank):
    """Without that, it takes 32: day shapes, life jackets, knots, load lines.

    Measured once on the two light themes alone, the net looked exact. A
    recognizer that leans on the theme is what this project cannot have — the
    theme classifier has known errors, so a configuration filed under the
    wrong theme would slip past the audit without a word.
    """
    day_shape = (
        "Ce semn trebuie să poarte o navă care navigă în acelaşi timp cu vele "
        "şi cu ajutorul unui aparat propulsor?"
    )
    assert not looks_like_config(day_shape, "la prova, în locul cel mai vizibil, un con cu vârful în jos.")
    assert not looks_like_config("Nodul trebuie sa aiba urmatoarele proprietati:", "usor de facut")


def test_a_visibility_range_is_not_a_configuration():
    """Those are a number, not a picture, and stay out of both 3c and 3d."""
    assert not looks_like_config(
        "La ce distanţă trebuie să fie vizibile luminile din borduri?", "1 milă marină."
    )


def test_an_arc_definition_is_not_a_configuration():
    """Stage 3c owns those; catching them here would double-draw the question."""
    assert not looks_like_config(
        "Lumina neîntreruptă pe un arc de orizont de 360° este:", "lumină vizibilă pe tot orizontul."
    )


def test_resolve_matches_the_stem_as_well_as_the_answer():
    """Both fields carry the binding quote, depending on which way the bank asks."""
    from_stem = "Ce lumini poartă o navă cu vele în marş?"
    from_answer = "trebuie să poarte la extremitatea prova luminile din borduri."
    found = resolve([("q1", from_stem, "un raspuns oarecare"), ("q2", "un enunt oarecare", from_answer)])
    assert found == {"q1": "vele-in-mars", "q2": "impinsa-inainte"}


def test_the_payload_carries_every_configuration_with_its_lights_and_note():
    data = payload()
    assert len(data["configs"]) == 12
    first = {entry["id"]: entry for entry in data["configs"]}["propulsie-mecanica-mica"]
    assert first["note"].startswith("Luminile din borduri numai")
    assert {"colours", "station", "level"} <= set(first["lights"][0])
    assert json.dumps(data, ensure_ascii=False)


def test_three_configurations_carry_a_note_and_the_rest_do_not():
    """A note states what the source qualifies and the drawing cannot show."""
    assert sum(1 for config in CONFIGS if config.note) == 3


# Every light of every configuration, read off the quoted source text rather
# than off the catalogue. Derived from the code it checks, this table would
# assert that the data equals itself; derived from the bank, it fails the
# moment a colour is swapped, a station mis-assigned or a level transposed.
# Colours within one lantern are a set: which wedge is drawn first is a
# drawing choice, while the level carries the "red above green" fact.
EXPECTED = {
    # "luminile din borduri şi lumina de pupa."
    "vele-in-mars": {("green|red", SIDE, 0), ("white", STERN, 0)},
    # "…pe care le poate reuni într-un felinar", "la măr sau la partea
    # superioară a catargului" — one lantern, three colours.
    "vele-felinar-combinat": {("green|red|white", MAST, 0)},
    # "o lumină roişie deasupra unei lumini verzi"
    "vele-lumini-suplimentare": {("red", MAST, 1), ("green", MAST, 0)},
    # "o lumină albă vizibilă peste tot orizontul şi dacă este posibil şi
    # luminile din borduri." — the white light gets no position.
    "propulsie-mecanica-mica": {("white", ANY, 0), ("green|red", SIDE, 0)},
    # "lumina superioară verde şi ce inferioară albă, o lumină de catarg
    # aşezată la o înălţime mai mare decât lumina verde şi înapoia acesteia"
    "traulare-nu-in-mars": {("green", ANY, 1), ("white", ANY, 0), ("white", MAST, 0)},
    # "trebuie să poarte la extremitatea prova luminile din borduri."
    "impinsa-inainte": {("green|red", BOW, 0)},
    # "luminile din borduri şi lumina de pupa."
    "remorcata": {("green|red", SIDE, 0), ("white", STERN, 0)},
    # "lumina de pupa şi luminile din borduri la extremitatea prova."
    "remorcata-la-ureche": {("white", STERN, 0), ("green|red", BOW, 0)},
    # "luminile de sus şi de jos roşii şi lumina din mijloc albă"
    "manevra-redusa-nu-in-mars": {("red", ANY, 2), ("white", ANY, 1), ("red", ANY, 0)},
    # "roşu-alb-roşu dispuse pe verticală, lumina de ancoră de la pupa" —
    # and the bank never says what colour an anchor light is.
    "manevra-redusa-la-ancora": {
        ("red", ANY, 2), ("white", ANY, 1), ("red", ANY, 0), ("", STERN, 0),
    },
    # "lumina superioară trebuie să fie roşie, iar lumina inferioară verde…
    # în vârful catargului… Luminile din borduri verde şi roşu şi lumina albă
    # de pupa"
    "vele-in-mars-D": {
        ("red", MAST, 1), ("green", MAST, 0), ("green|red", SIDE, 0), ("white", STERN, 0),
    },
    # "O lumină albă obişnuită dispusă într-un loc corespunzător"
    "mica-lumina-alba": {("white", ANY, 0)},
}


def shape(config):
    """A configuration as comparable facts: which colours, where, how high."""
    return {("|".join(sorted(light.colours)), light.station, light.level)
            for light in config.lights}


def test_every_configuration_carries_exactly_the_lights_its_source_states():
    """The one test that would catch a wrong colour anywhere in the catalogue.

    Before this, seven of the twelve had no assertion on their contents at
    all: red-white-red could have shipped as white-red-white and every test
    stayed green.
    """
    assert {config.id for config in CONFIGS} == set(EXPECTED)
    for config in CONFIGS:
        assert shape(config) == EXPECTED[config.id], config.id


def test_five_questions_are_excused_and_the_reasons_are_written():
    """A duplicated key in the literal would silently collapse two into one."""
    assert len(NOT_A_CONFIG) == 5
    for text, reason in NOT_A_CONFIG.items():
        assert reason.strip(), text[:50]


def test_the_towed_vessel_resolves_through_its_own_stem():
    """The negative test above passes on an empty sources tuple; this does not."""
    stem = "Ce lumini trebuie să poarte obiectele sau navele remorcate, altele decât cele cu forma nedefinită?"
    assert resolve([("q1", stem, "un raspuns oarecare")]) == {"q1": "remorcata"}
