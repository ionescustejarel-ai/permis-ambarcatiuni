"""Assigns exactly one primary learning theme to each question.

Discipline answers "what the exam draws"; theme answers "what I study
now". They are different axes: light questions appear under both COLREG
and the Danube regulation, but they are learned together.

Rules are ordered and the first match wins, so specific rules must come
before general ones: skyjet before manoeuvring, buoys before lights.

The first-aid and legislation sections bypass the rules entirely — they
are distinct exam disciplines, so their section already is their theme.

Matching runs against the normalized question text plus its options, so
diacritic variants and punctuation never affect the outcome.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace
from typing import Final

from caa.dedup import Question
from caa.normalize import normalize_key
from caa.structure import Section

FALLBACK_THEME: Final = "vocabular-si-principii"

_SECTION_THEMES: Final = {
    Section.FIRST_AID: "prim-ajutor",
    Section.LEGISLATION: "legislatie",
}

# Ordered: the first matching pattern wins.
#
# Two-word phrases carry the endings Romanian actually puts on them. Written
# in dictionary form they never matched: the bank says "marcajul lateral", and
# "marcaj lateral" is not a substring of it. Nine of the twenty-seven were
# written that way and five questions were filed by whichever later rule their
# text happened to trip.
#
# The endings are spelled out rather than left to `\w*`. The wildcard turns a
# noun into a verb — `semnal\w* sonor` matches "semnaliza sonor" — and that
# moved a question about traffic separation zones into sound signals, following
# one of its own distractors.
#
# Measured and rejected, stage 4e: patterns for painting and rust removal
# (matagonir, pitureaza, vopsea). They would land in construction, but
# painting a hull is maintenance, and this bank has no maintenance theme —
# the move would have been an opinion wearing the classifier's authority.
# They stay in the catch-all, where they can be taught as what they are.
# Measured and rejected, stage 4c: the genitive carm(a|ei) at the manoeuvre
# rule. It moves six questions — four correctly, but it also pulls the two
# etambreu questions out of construction, because their stem "Orificiul
# rotund prin care trece axul cârmei" names the rudder while asking about
# the hull. One extra correct move does not pay for two broken ones.
THEMES: Final[tuple[tuple[str, str], ...]] = (
    ("motovehicule-nautice", r"skyjet|sky jet|motociclet[ae] nautic|motovehicul"),
    # Ahead of sound signals on purpose: a fog signal is studied with fog, and
    # sound signals match first on everything otherwise.
    ("vizibilitate-redusa", r"vizibilitate redus|\bceat"),
    ("semnale-sonore", r"sunet|semnal(ul|e|ele)? sonor|fluier|clopot|gong|acustic"),
    # `senal navigabil` used to be here. The fairway is a place, not a mark:
    # with the endings repaired it would have pulled in a question about where
    # fishing gear may not be laid.
    ("geamanduri-si-balizaj",
     r"geamandur|baliz|marcaj(ul|e|ele)? (lateral|cardinal)|cardinal|piturat|pericol izolat|scondr|jaloan"),
    # The bank writes "un con cu vârful în jos" with no colour at all, so
    # asking for "con negru" let two day-shape questions fall through to
    # `prova` in the hull rule, sixteen rules further down.
    ("semne-si-forme-ziua",
     r"\bbile\b|\bbila\b|con(uri)? negr|cilindr|romb|semne de zi"
     r"|con cu varful|semnul purtat|ziua in mars"),
    ("lumini-situatii-speciale", r"lumin.*(remorc|pesc|ancor|esuat|fara comanda|capacitate de manevra redusa)|remorc.*lumin"),
    ("lumini-propulsie-mecanica", r"lumin|felinar|sclipir|intermitent|far "),
    ("reguli-de-drum",
     r"cedeaz|se abat|drum liber|prioritat|ajunge din urma|traverseaz"
     r"|pericol(ul)? de coliziune|risc(ul)? de coliziune"
     r"|separare a traficului|trafic(ul)? costier|in vedere"),
    ("semnale-de-pericol-si-salvare",
     r"semnal(ul|e|ele)? de pericol|primejdie|s o s|mayday|racheta|colac"
     r"|vesta de salvare|salvar"),
    ("regulament-dunare", r"r n d|amonte|aval|ecluz|convoi|cale navigabila interioara"),
    # `drum\w*` and not `drum`: the bank asks "Drumul adevărat al navei este:",
    # and "drum adevarat" is not a substring of "drumul adevarat" — the three
    # course definitions fell through to whichever rule their text happened to
    # trip. "drum liber" stays with the steering rules, which are matched first.
    ("navigatie-compas-si-drumuri",
     r"compas|declinati|deviati|relevment|drum\w* (adevarat|magnetic|giro)|cart"),
    ("navigatie-harti-si-pozitie", r"hart|sonda|adancimea apei|punct(ul|ului)? navei|carti pilot|avize pentru navigatori|loch|latitudine|longitudine"),
    ("meteo-si-hidrologie", r"vant|valuri|meteo|presiune atmosferic|furtun|beaufort|maree"),
    ("motor-si-propulsie", r"elice|motor|carburant|racire|bujii|turati|ventilati"),
    ("manevra-cu-motor", r"acostar|plecare de la|om la apa|viraj|glisar|planar|remorcaj|timon|carma|guvernar"),
    ("parame-noduri-ancore", r"param|nod |gase|matis|ancor|lant|babal|barbet|rodant|cheie de impreunare|armament|palanc|mandar|vinci(ul|uri)|volt(ele|elor)|matelotaj|macara|raiul|sbir|big(i|ile)|granic|grui"),
    ("constructia-ambarcatiunii", r"prova|pupa|tribord|babord|carena|bord(ul)? liber|pescaj|deplasament|copastie|etrav|puntea|borduri|chil(a|ei)|coaste|varang|ruliu|fil(a|e|ele|elor)\b|bordaj|dama\b"),
)

_COMPILED: Final = tuple((slug, re.compile(pattern)) for slug, pattern in THEMES)


def _first_match(haystack: str) -> str | None:
    for slug, pattern in _COMPILED:
        if pattern.search(haystack):
            return slug
    return None


# The one place where a rule can swallow the narrower rule above it, because
# the word that tells them apart is not in the stem. Both lights rules match
# "lumin"; only the special one names a towing, fishing, anchored or
# restricted vessel — and "Trei lumini în poziţie verticală… sunt luminile
# purtate de o navă:" names that vessel in its correct answer, not in the
# question. So for this pair, and only this pair, the right answer may promote
# the match from the general rule to the specific one.
#
# Kept to a declared pair on purpose. Comparing rule positions in general was
# measured and rejected: THEMES is ordered specific-before-general inside a
# family, not across families, so "cardinal" in an answer dragged the compass
# questions back to buoyage and "manevrelor curente" sent a rope question to
# meteorology — 36 moves, most of them wrong.
_PROMOTIONS: Final = {"lumini-propulsie-mecanica": "lumini-situatii-speciale"}


def _match_theme(question: Question) -> str:
    """The stem decides; the options only speak when the stem says nothing.

    Matching stem and options together lets a *wrong* answer choose the theme.
    Five variants of one question about a boat's armament landed in four
    different themes on the bank as first shipped, each following whichever
    distractor it happened to carry: "felinar de vânt" sent one to the lights
    theme, "compasul de barca" another to the compass theme, "veste de salvare"
    a third to distress signals. Only the variant whose distractors fired no
    earlier rule reached the theme its own stem asks for.

    Reading the options is still worth doing when the stem alone says nothing:
    "Rodanțele sunt:" carries no keyword and its options do. So they are a
    second pass, not part of the first — 131 questions are placed this way and
    keep their theme, while 53 whose real theme a distractor had overridden get
    it back.

    The correct answer gets one say, on the single pair in `_PROMOTIONS` where
    the stem cannot tell the two rules apart. Everywhere else the stem's verdict
    stands: a free pass over the correct answer was measured twice and rejected
    twice, once for questions whose stem says nothing (ten moved, five wrong)
    and once for promotion by rule position (thirty-six moved, most wrong).
    """
    stem = _first_match(normalize_key(question.question))
    if stem is not None:
        promoted = _PROMOTIONS.get(stem)
        if promoted is not None:
            answer = question.options[question.correct]
            with_answer = _first_match(normalize_key(f"{question.question} {answer}"))
            if with_answer == promoted:
                return promoted
        return stem
    everything = _first_match(normalize_key(f"{question.question} {' '.join(question.options)}"))
    return everything or FALLBACK_THEME


def assign_themes(questions: list[Question]) -> list[Question]:
    """Returns copies of the questions with `theme` filled in."""
    result: list[Question] = []
    for item in questions:
        theme = _SECTION_THEMES.get(item.section) or _match_theme(item)
        result.append(replace(item, theme=theme))
    return result


def theme_distribution(questions: list[Question]) -> dict[str, int]:
    """Counts questions per theme, for the audit report."""
    return dict(Counter(item.theme for item in questions if item.theme))


# Where a question belongs when a catalogue already says what it is about.
# Only these have a knowable answer — 54 of 603. For the rest there is no
# ground truth, and a rule invented for them would be an opinion wearing the
# audit's authority.
_LIGHT_THEMES: Final = frozenset({"lumini-propulsie-mecanica", "lumini-situatii-speciale"})

SUBJECT_THEMES: Final[dict[str, frozenset[str]]] = {
    "buoy": frozenset({"geamanduri-si-balizaj"}),
    "day-shape": frozenset({"semne-si-forme-ziua"}),
    # Three, and each is earned. A fog signal is studied with fog. The five
    # short blasts a vessel sounds when it doubts another's intentions are
    # studied with the steering rules — which is where COLREG teaches them,
    # and what that question's own stem asks about.
    "signal": frozenset({"semnale-sonore", "vizibilitate-redusa", "reguli-de-drum"}),
    # The bank splits the lights into two themes and asks arcs and
    # configurations under both.
    "light": _LIGHT_THEMES,
}


def themes_for_subject(subject: str) -> frozenset[str]:
    """The themes a question about `subject` may sit in."""
    return SUBJECT_THEMES[subject]
