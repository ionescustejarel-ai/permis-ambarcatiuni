"""Guards the promises the built page makes, without a browser."""

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


def _questions(page: str) -> list[dict]:
    match = re.search(r'<script id="questions" type="application/json">(.*?)</script>',
                      page, re.DOTALL)
    return json.loads(match.group(1))["questions"]


def test_every_screen_the_navigation_offers_exists(page):
    for route in ("acasa", "teme", "lista-neagra", "examen", "diferenta"):
        assert re.search(rf'["\']?{re.escape(route)}["\']?\s*[:(]', page), route


def test_every_theme_in_the_data_has_a_romanian_label(page):
    themes = {question["theme"] for question in _questions(page)}
    for theme in themes:
        assert f'"{theme}":' in page, f"{theme} has no label in THEME_LABELS"


def test_the_disputed_items_are_split_one_per_class(page):
    disputed = [question for question in _questions(page) if question["disputed"]]
    assert disputed, "the bank should still carry the known disputed pair"
    assert all(len(question["classes"]) == 1 for question in disputed)


def test_the_safety_contour_matches_the_spec(page):
    # Anchored on both sides: a plain substring test passes for 400 and 4000
    # too, which is the whole class of typo it exists to catch.
    assert re.search(r"\bSAFETY_CONTOUR = 40\b", page)


def test_the_page_fits_in_a_single_file(page):
    assert len(page.encode("utf-8")) < 1_500_000, "keep it loadable on a phone"
