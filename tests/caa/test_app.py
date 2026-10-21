import json
import re
from pathlib import Path

import pytest

from caa.app import build_html

ROOT = Path(__file__).resolve().parents[2]
QUESTIONS = ROOT / "build" / "questions.json"
ASSETS = ROOT / "src" / "caa" / "assets"


@pytest.fixture(scope="module")
def page() -> str:
    if not QUESTIONS.is_file():
        pytest.skip("run `python -m caa.cli` first")
    return build_html(QUESTIONS, ASSETS)


# Every way a page can reach the network, not only the obvious ones. A
# protocol-relative "//cdn…" has no scheme to grep for, and a fetch() call is
# invisible to a markup-shaped check.
FORBIDDEN = (
    (r'(?:src|href)\s*=\s*["\'][^"\']*(?:https?:)?//', "absolute or protocol-relative URL"),
    (r'@import', "CSS @import"),
    (r'url\(\s*["\']?\s*(?:https?:)?//', "remote url()"),
    (r'\bwss?://', "websocket"),
    (r'\bfetch\s*\(', "fetch()"),
    (r'\bXMLHttpRequest\b', "XMLHttpRequest"),
    (r'\bsendBeacon\b', "sendBeacon"),
    (r'\bEventSource\b', "EventSource"),
    (r'\bimport\s*\(', "dynamic import()"),
)


def test_the_page_makes_no_external_requests(page):
    """It must open from disk with the network off, now and after every task."""
    for pattern, what in FORBIDDEN:
        assert not re.search(pattern, page, re.IGNORECASE), what


def test_the_questions_are_embedded(page):
    match = re.search(r'<script id="questions" type="application/json">(.*?)</script>',
                      page, re.DOTALL)
    assert match, "no embedded question payload"
    payload = json.loads(match.group(1))
    assert payload["count"] == len(payload["questions"])
    assert payload["count"] > 500


def test_the_exam_rules_are_embedded_not_retyped(page):
    match = re.search(r'<script id="rules" type="application/json">(.*?)</script>',
                      page, re.DOTALL)
    assert match, "no embedded exam rules"
    rules = json.loads(match.group(1))
    assert rules["questions"] == 26
    assert rules["pass"] == 22
    assert sum(count for _, count in rules["draw"]["C"]) == 26


def test_the_stylesheet_and_scripts_are_inlined(page):
    assert "<style>" in page
    assert page.count("<script") >= 3  # questions, rules, code
    assert "--magenta" in page
    assert "function recordAnswer" in page


def test_no_payload_can_close_its_own_script_element(page):
    """A "<" in the data would end the element early and break the page."""
    for element in ("questions", "rules", "signals", "figures", "arcs", "lights"):
        match = re.search(rf'<script id="{element}" type="application/json">(.*?)</script>',
                          page, re.DOTALL)
        assert "<" not in match.group(1), element
        json.loads(match.group(1))  # still valid JSON after escaping


# Each entry names the builder to replace, the element it fills, and a payload
# carrying a tag. Every catalogue the page embeds belongs here: the loop above
# cannot fail on real data, so this is the only place the escaping is guarded,
# and a catalogue missing from this list is a catalogue nobody is checking.
TAG_CARRYING = (
    ("signals_payload", "signals", "signals", {
        "timing": {"durations": {}, "gaps": {}, "defaultGap": 500},
        "signals": [{"id": "x", "label": "</script><b>", "instrument": "whistle",
                     "pattern": ["short"]}],
    }),
    ("figures_payload", "figures", "figures", {
        "figures": [{"id": "x", "label": "</script><b>", "system": "iala",
                     "body": {"shape": "pillar", "bands": ["black"], "border": None},
                     "light": None}],
    }),
    ("arcs_payload", "arcs", "arcs", {
        "arcs": [{"id": "x", "label": "</script><b>",
                  "sectors": [{"start": 0, "end": 90, "colour": "white"}], "caveats": {}}],
    }),
    ("lights_payload", "lights", "configs", {
        "configs": [{"id": "x", "label": "</script><b>", "note": "", "lights": []}],
    }),
    ("theory_payload", "theory", "cards", {
        "cards": [{"theme": "x", "label": "</script><b>", "statements": [{"text": "test", "classes": ["C"]}]}],
    }),
)


@pytest.mark.parametrize("builder, element, key, payload", TAG_CARRYING)
def test_the_escaping_holds_for_a_payload_that_carries_a_tag(
    monkeypatch, builder, element, key, payload
):
    """The loop above cannot fail on today's data, so it cannot guard anything.

    No payload the build produces contains a "<" at all, which means dropping
    `_inline_json` from any of them would leave every assertion in that loop
    still true. This forces the case the escaping exists for.

    The order of the assertions matters. The element regex is non-greedy, so
    an unescaped "</script>" inside the data ends the match early and the
    captured text comes out short — and free of "<". Parsing it is what
    catches that: truncated JSON does not load.
    """
    if not QUESTIONS.is_file():
        pytest.skip("run `python -m caa.cli` first")
    from caa import app as app_module

    if builder == "theory_payload":
        monkeypatch.setattr(app_module, builder, lambda questions=None: payload)
    else:
        monkeypatch.setattr(app_module, builder, lambda: payload)

    built = build_html(QUESTIONS, ASSETS)
    match = re.search(rf'<script id="{element}" type="application/json">(.*?)</script>',
                      built, re.DOTALL)
    data = json.loads(match.group(1))
    # The tag id and the payload key are not the same word for every
    # catalogue: the configurations live under "configs" in a block tagged
    # "lights". Conflating them made the synthetic payload disagree with
    # the real schema.
    assert data[key][0]["label"] == "</script><b>", "the tag survived as data"
    assert "<" not in match.group(1)


def test_an_asset_mentioning_a_marker_does_not_clobber_it(tmp_path):
    """Substitution runs once over the template, so assets are never rescanned."""
    (tmp_path / "index.html").write_text(
        "<style>/*STYLE*/</style><script>/*LOGIC*/</script><script>/*AUDIO*/</script><script>/*UI*/</script>"
        '<script id="questions">/*QUESTIONS*/</script><script id="rules">/*RULES*/</script>',
        encoding="utf-8")
    # The stylesheet talks about a marker that has not been substituted yet.
    (tmp_path / "app.css").write_text("/* the /*RULES*/ block carries the exam rules */",
                                      encoding="utf-8")
    (tmp_path / "logic.js").write_text("// logic", encoding="utf-8")
    (tmp_path / "audio.js").write_text("// audio", encoding="utf-8")
    (tmp_path / "ui.js").write_text("// ui", encoding="utf-8")
    (tmp_path / "figures.js").write_text("// figures", encoding="utf-8")
    (tmp_path / "arcs.js").write_text("// arcs", encoding="utf-8")
    (tmp_path / "lights.js").write_text("// lights", encoding="utf-8")
    (tmp_path / "rose.js").write_text("// rose", encoding="utf-8")
    (tmp_path / "schema.js").write_text("// schema", encoding="utf-8")
    questions = tmp_path / "q.json"
    questions.write_text('{"count": 0, "questions": []}', encoding="utf-8")

    page = build_html(questions, tmp_path)

    assert "the /*RULES*/ block carries the exam rules" in page, "the mention was clobbered"
    assert '"questions": []' in page, "the real placeholder was not filled"


def test_the_page_declares_romanian_and_a_viewport(page):
    assert 'lang="ro"' in page
    assert 'name="viewport"' in page


def test_the_signal_catalogue_is_embedded(page):
    match = re.search(r'<script id="signals" type="application/json">(.*?)</script>',
                      page, re.DOTALL)
    assert match, "no embedded signal catalogue"
    data = json.loads(match.group(1))
    assert data["timing"]["durations"]["short"] == 1000
    assert data["timing"]["defaultGap"] == 500
    assert len(data["signals"]) == 10


def test_the_figure_catalogue_is_embedded(page):
    match = re.search(r'<script id="figures" type="application/json">(.*?)</script>',
                      page, re.DOTALL)
    assert match, "no embedded figure catalogue"
    data = json.loads(match.group(1))
    assert len(data["figures"]) == 12
    east = next(f for f in data["figures"] if f["id"] == "cardinal-est")
    assert east["body"]["bands"] == ["black", "yellow", "black"]


def test_the_arc_catalogue_is_embedded(page):
    match = re.search(r'<script id="arcs" type="application/json">(.*?)</script>',
                      page, re.DOTALL)
    assert match, "no embedded arc catalogue"
    data = json.loads(match.group(1))
    assert len(data["arcs"]) == 5
    masthead = next(a for a in data["arcs"] if a["id"] == "lumina-de-catarg")
    assert masthead["sectors"] == [{"start": 247.5, "end": 112.5, "colour": "white"}]


def test_the_audio_engine_is_inlined(page):
    assert "const Audio2 = {" in page, "the engine is not in the page"
    assert "new AudioContext()" in page


def test_the_engine_smuggles_in_no_media_file(page):
    """The FORBIDDEN list guards URLs; this guards file extensions."""
    for extension in (".mp3", ".wav", ".ogg", ".m4a", ".opus"):
        assert extension not in page, extension


def test_the_engine_is_ordered_after_the_logic_it_calls(page):
    """audio.js calls signalTimeline; inlined before logic.js it would throw."""
    assert page.index("function signalTimeline") < page.index("const Audio2 = {")


def test_the_figure_renderer_is_inlined(page):
    assert "function drawFigure" in page
    assert "http://www.w3.org/2000/svg" in page, "SVG needs its namespace"


def test_the_renderer_is_ordered_after_the_bands_it_draws(page):
    assert page.index("function figureBands") < page.index("function drawFigure")


def test_no_image_file_is_smuggled_in(page):
    for extension in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        assert extension not in page, extension


def test_the_arc_renderer_is_inlined(page):
    assert "function drawArc" in page
    assert "http://www.w3.org/2000/svg" in page


def test_the_arc_renderer_is_ordered_after_the_geometry_it_uses(page):
    assert page.index("function sectorPath") < page.index("function drawArc")


def test_the_page_carries_the_configuration_catalogue(page):
    assert 'id="lights"' in page
    assert "vele-in-mars-D" in page
    match = re.search(r'<script id="lights" type="application/json">(.*?)</script>',
                      page, re.DOTALL)
    assert match, "no embedded lights catalogue"
    data = json.loads(match.group(1))
    assert len(data["configs"]) == 12


def test_the_page_carries_the_configuration_renderer(page):
    assert "drawConfig" in page


def test_the_configuration_renderer_is_ordered_after_both_things_it_uses(page):
    """It is the first renderer that depends on two earlier scripts, not one.

    `drawConfig` calls `lightPlacement` and `sectorPath` from logic.js and
    reads `LIGHT_PAINT` from arcs.js. Nothing else would notice a reordering:
    the page-parsing test compiles each block on its own, so an identifier
    that resolves across a <script> boundary only fails when a browser calls
    the function.
    """
    assert page.index("function lightPlacement") < page.index("function drawConfig")
    assert page.index("function sectorPath") < page.index("function drawConfig")
    assert page.index("LIGHT_PAINT = {") < page.index("function lightMarker")


def test_the_page_carries_the_theory(page):
    match = re.search(r'<script id="theory" type="application/json">(.*?)</script>',
                      page, re.DOTALL)
    assert match, "no embedded theory"
    data = json.loads(match.group(1))
    # Counted against the catalogue rather than a literal, so a stage that adds
    # cards does not need to remember this file.
    from caa.theory import THEORY

    assert len(data["cards"]) == len(THEORY)
    assert {card["theme"] for card in data["cards"]} == {card.theme for card in THEORY}
    # classes arrived derived: the C/D contradiction pair is split
    ropes = next(c for c in data["cards"] if c["theme"] == "parame-noduri-ancore")
    boturi = [s["classes"] for s in ropes["statements"] if s["text"].startswith("Boturile")]
    assert sorted(map(tuple, boturi)) == [("C",), ("D",)]
