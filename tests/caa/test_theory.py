import json
from pathlib import Path

import pytest

from caa.normalize import normalize_key
from caa.theory import THEORY, payload, statement_classes

BANK = Path(__file__).resolve().parents[2] / "build" / "questions.json"


@pytest.fixture(scope="module")
def bank():
    if not BANK.is_file():
        pytest.skip("run `python -m caa.cli` first")
    return json.loads(BANK.read_text(encoding="utf-8"))["questions"]


def card(theme):
    return next(c for c in THEORY if c.theme == theme)


# A statement shown at both classes, citing a single-class question whose
# cross-class twin answers differently, teaches one class the other's answer.
# That shipped once: the vegetable-rope storage rule taught class D to keep
# ropes from solar radiation, which is exactly the option class D's exam marks
# wrong. Each entry here has been read and cleared by hand; a candidate that
# is not on this list fails the build until somebody reads it too.
CLEARED_CLASS_FOLDING = {
    # (theme, statement.text[:40]) -> why pooling the two classes is safe here.
    # Read, not assumed.
    ("parame-noduri-ancore", "Cânepa merge la manevre curente, bărci ș"):
        "the class C sources say synthetics serve sport halyards and worn rope "
        "serves fenders; the class D source says cotton serves halyards. "
        "Different facts, both true at both classes, neither contradicting the "
        "other's exam answer",
}


def _pooled_single_class_sources(statement, questions, theme):
    """Per class, the normalized sources carried only by that class's questions.

    A statement is a class-folding candidate when it pools facts the bank
    states separately per class — which is what it means for the C set and the
    D set to be non-empty and share nothing. When they DO share a source, the
    two lists are merely spelling one answer with different diacritics, and
    normalize_key has already made them the same fact.

    Two earlier definitions were measured and dropped. Stem similarity at 75%
    reported eight candidates where there are one: the bank asks its
    definitions in series — bătaia, pieptănarea, toarcerea — and those stems
    differ by a word while their answers differ entirely, so the exception
    list became a rubber stamp. Requiring an identical stem missed the real
    hazard of stage 4b, where the long blast is 4–6 seconds at class C and
    about 4 at class D under two differently worded questions.
    """
    per = {"C": set(), "D": set()}
    for source in statement.sources:
        key = normalize_key(source)
        for question in questions:
            if question["theme"] != theme or len(question["classes"]) != 1:
                continue
            fields = (question["q"], question["opts"][question["correct"]])
            if any(normalize_key(field) == key for field in fields):
                per[question["classes"][0]].add(key)
    return per


def test_the_theory_covers_its_themes():
    assert sorted(c.theme for c in THEORY) == [
        "constructia-ambarcatiunii", "geamanduri-si-balizaj", "legislatie",
        "lumini-propulsie-mecanica", "lumini-situatii-speciale", "manevra-cu-motor",
        "meteo-si-hidrologie", "motor-si-propulsie", "motovehicule-nautice",
        "navigatie-compas-si-drumuri", "navigatie-harti-si-pozitie",
        "parame-noduri-ancore", "prim-ajutor", "regulament-dunare", "reguli-de-drum",
        "semnale-de-pericol-si-salvare", "semnale-sonore", "semne-si-forme-ziua",
        "vizibilitate-redusa", "vocabular-si-principii"
    ]
    assert sum(len(c.statements) for c in THEORY) == 201


def test_no_statement_is_ballast():
    """The parent spec's honesty rule: a statement with nothing to answer is out."""
    for c in THEORY:
        for statement in c.statements:
            assert statement.text.strip(), c.theme
            assert statement.sources, f"{c.theme}: {statement.text[:50]!r}"


def test_every_quote_is_byte_identical_to_the_bank(bank):
    """normalize_key is blind to punctuation, so it cannot catch a retyped quote."""
    corpus = {q["q"] for q in bank}
    corpus |= {o for q in bank for o in q["opts"]}
    for c in THEORY:
        for statement in c.statements:
            for source in statement.sources:
                assert source in corpus, f"{c.theme}: {source[:60]!r}"


def test_every_quote_belongs_to_a_question_of_its_own_theme(bank):
    """A knot rule resting on a weather question is shelved wrong, mechanically."""
    for c in THEORY:
        themed = {q["q"] for q in bank if q["theme"] == c.theme}
        themed |= {q["opts"][q["correct"]] for q in bank if q["theme"] == c.theme}
        for statement in c.statements:
            for source in statement.sources:
                assert source in themed, f"{c.theme}: {source[:60]!r}"


def test_classes_derive_from_the_source_questions(bank):
    """The C/D contradiction pair: the bank answers 'boturile' differently per class."""
    ropes = card("parame-noduri-ancore")
    boturi = [s for s in ropes.statements if s.text.startswith("Boturile")]
    assert len(boturi) == 2
    derived = sorted(statement_classes(s, bank, "parame-noduri-ancore") for s in boturi)
    assert derived == [("C",), ("D",)]


def test_first_aid_is_shared_by_both_classes(bank):
    for statement in card("prim-ajutor").statements:
        assert statement_classes(statement, bank, "prim-ajutor") == ("C", "D"), statement.text[:50]


def test_no_statement_pools_facts_the_bank_states_per_class(bank):
    """The structural half of the sweep, automated.

    A statement that pools a class C fact with a different class D fact
    teaches each class the other's answer. That shipped once: the vegetable
    rope storage rule taught class D to keep ropes from solar radiation,
    which is exactly the option class D's exam marks wrong.

    This is triage, not a gate. It cannot judge whether the pooled facts
    actually contradict — "radiația solară" pulling a candidate toward the
    distractor "razele solare" needed a human — but it shortens the reading
    from every statement in the file to the handful that pool anything at all,
    and
    it fails on any candidate nobody has cleared.
    """
    found = set()
    for entry in THEORY:
        for statement in entry.statements:
            per = _pooled_single_class_sources(statement, bank, entry.theme)
            if per["C"] and per["D"] and not (per["C"] & per["D"]):
                found.add((entry.theme, statement.text[:40]))
    assert found == set(CLEARED_CLASS_FOLDING), (
        f"unread: {found - set(CLEARED_CLASS_FOLDING)}; "
        f"stale: {set(CLEARED_CLASS_FOLDING) - found}"
    )


def test_the_payload_carries_every_statement_of_every_card(bank):
    """Counted per card, not in total.

    The first version looped over whatever the payload held and asserted on
    each — so a payload that dropped two of the three cards, or emptied one,
    passed the whole suite. Only the browser pass would have noticed.
    """
    data = payload(bank)
    shipped = {c["theme"]: len(c["statements"]) for c in data["cards"]}
    assert shipped == {c.theme: len(c.statements) for c in THEORY}


def test_the_payload_carries_classes_and_round_trips(bank):
    data = payload(bank)
    # Not a count against THEORY: payload() is a comprehension over it, so that
    # assertion cannot fail. The page-versus-source check lives in test_app.py,
    # which parses the built HTML; this one checks the shape of each entry.
    assert data["cards"]
    for c in data["cards"]:
        assert c["theme"]
        for statement in c["statements"]:
            assert statement["text"]
            assert statement["classes"], statement["text"][:50]
    assert json.dumps(data, ensure_ascii=False)


def test_the_payload_contains_no_sources(bank):
    """The page needs the prose and the classes; shipping the quotes would double
    the payload for nothing the interface ever shows."""
    data = payload(bank)
    for c in data["cards"]:
        for statement in c["statements"]:
            assert "sources" not in statement


def test_the_derivation_looks_only_inside_its_own_theme(bank):
    """The scoping is inert on today's data, which is why it needs pinning.

    A source of "Da" is the correct answer to thirteen questions across five
    themes; unscoped, the distress-signal statement inherited class C from a
    rope question and shipped a class D rule to class C candidates. The quote
    was replaced too, so scoped and unscoped now agree on all 88 statements —
    remove the theme filter today and every test stays green. This one does
    not: a statement asked for a foreign theme's classes must derive none.
    """
    ropes = card("parame-noduri-ancore").statements[0]
    assert statement_classes(ropes, bank, "parame-noduri-ancore")
    assert statement_classes(ropes, bank, "prim-ajutor") == ()
    assert statement_classes(ropes, bank, "meteo-si-hidrologie") == ()
