"""The arcs on which the navigation lights are visible, as data.

The bank defines each light by the arc it covers, and the candidate memorises
the numbers — 225, 135, 112°5 — without being able to picture them. A sector
drawn around a vessel seen from above makes them obvious, and shows at a
glance why the stern light and the towing light share an arc but not a colour.

Bearings run from the bow, clockwise, 0 to 360: starboard towards small
values, port towards large. The opening is `(end - start) mod 360`, and 0
means the whole circle. One convention, not two — signed bearings read more
naturally from the source, but then the stern light spans 112.5 to -112.5
through the back and crossing zero becomes two cases instead of one.

Only what the bank asks is drawn. The flashing light is absent: its source
gives a rate, "120 de sclipiri pe minut sau mai mult", and no arc at all.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Final

from caa import catalogue
from caa.normalize import normalize_key


@dataclass(frozen=True)
class Sector:
    """An arc of visibility, in bearings from the bow, clockwise.

    `colour` is absent where the source names none: "lumină vizibilă pe
    întreg orizontul" is a property, not a colour.
    """

    start: float
    end: float
    colour: str | None = None


@dataclass(frozen=True)
class Arc:
    id: str
    label: str  # Romanian: this reaches the interface
    sectors: tuple[Sector, ...]
    sources: tuple[str, ...]
    # Keyed on one of this arc's own sources: the note is shown beside that
    # question and nowhere else.
    caveats: dict[str, str] = field(default_factory=dict)


_MASTHEAD_TYPO: Final = (
    "Lumina albă aşezată deasupra axului longitudinal al navei, arătând o lumină "
    "neîntreruptă pe un arc de orizont de 22°5 astfel ca să arate 22°5 înapoia "
    "traversului fiecărui bord este:"
)

ARCS: Final[tuple[Arc, ...]] = (
    Arc(
        id="lumina-de-catarg",
        label="Lumina de catarg",
        # 225°: 112°5 either side of the bow, so the sector crosses zero.
        sectors=(Sector(start=247.5, end=112.5, colour="white"),),
        sources=(
            _MASTHEAD_TYPO,
            "o lumină albă aşezată deasupra axului longitudinal al navei, arătând o "
            "lumină neîntreruptă pe un arc de orizont de 225°, astfel ca să arate 22°5 "
            "înapoia traversului fiecărui bord.",
        ),
        caveats={
            _MASTHEAD_TYPO: (
                "Enunțul are aici o cifră pierdută la tipar: arcul e 225°, cum scrie "
                "și răspunsul celeilalte întrebări din aceeași listă. Răspunsul corect "
                "nu se schimbă."
            ),
        },
    ),
    Arc(
        id="lumina-de-pupa",
        label="Lumina de pupa",
        # 135°: 67°5 either side of astern.
        sectors=(Sector(start=112.5, end=247.5, colour="white"),),
        sources=(
            "Lumina albă aşezată cât mai aproape posibil în pupa, arătând o lumină "
            "neîntreruptă pe un arc de 135° câte 67°5 în fieare bord este:",
            "o lumină aşezată cât mai aproape posibil în pupa, arătând o lumină "
            "neîntreruptă pe un arc de 135°, câte 67°5 în fiecare bord.",
        ),
    ),
    Arc(
        id="lumina-de-remorcaj",
        label="Lumina de remorcaj",
        # The stern light's arc, in yellow: the pair is easiest to tell apart
        # when both are drawn.
        sectors=(Sector(start=112.5, end=247.5, colour="yellow"),),
        sources=(
            "o lumină galbenă aşezată cât mai aproape posibil de pupa, arătând o "
            "lumină neîntreruptă pe un arc de cerc de 135°, câte 67°5 în fiecare bord.",
            "Lumina galbenă aşezată cât mai aproape posibil în pupa arătând o lumină "
            "de 135°, câte 67°5 în fiecare bord este:",
        ),
    ),
    Arc(
        id="lumini-de-bord",
        label="Luminile de bord",
        # Two sectors, and which is which is the whole point: green to
        # starboard, red to port, each 112°5 from ahead.
        sectors=(
            Sector(start=0, end=112.5, colour="green"),
            Sector(start=247.5, end=360, colour="red"),
        ),
        sources=(
            "lumină verde din tribord şi lumină roşie din babord, vizibile pe un arc "
            "de 112°5, adică la prova până la 22°5 înapoia traversului.",
            "Lumină verde din tribord şi lumină roşie din babord, vizibile pe un arc "
            "de 112°5 adică de la prova până la 22°5 înapoia traversului, reprezintă "
            "ceea ce se înţelege prin expresia:",
        ),
    ),
    Arc(
        id="tot-orizontul",
        label="Vizibilă pe tot orizontul",
        # No colour: the source names a property, not a colour.
        sectors=(Sector(start=0, end=360),),
        sources=(
            "Lumina neîntreruptă pe un arc de orizont de 360° este:",
            "lumină neîntreruptă pe un arc de de orizont de 360°",
        ),
    ),
)

# Texts that read like an arc but cannot be drawn from what they say. Empty on
# today's bank, kept so a future edition forces a written decision.
NOT_AN_ARC: Final[dict[str, str]] = {}

# An arc is announced: "arc de X", "câte X în fiecare bord", or the settled
# phrase for the full circle.
ARC_SHAPE: Final = re.compile(
    r"arc de (orizont|cerc|\d)"
    r"|pe un arc de"
    r"|cate \d+ ?5? in fiecare bord"
    r"|vizibil\w* pe (tot|intreg) orizontul"
)

# What lights a vessel carries is a different question: the answer is a vessel
# type or a list of lights, never an arc. Those belong to stage 3d, and the
# visibility ranges are a number rather than a picture. Without this guard the
# net took twelve questions instead of ten.
NOT_A_DEFINITION: Final = re.compile(
    r"ce lumini|luminile purtate de|lumini(le)? suplimentare|poate purta|la ce distanta"
)


def looks_like_arc(stem: str, answer: str) -> bool:
    """True when a question defines a light by the arc it covers."""
    if NOT_A_DEFINITION.search(normalize_key(stem)):
        return False
    return any(ARC_SHAPE.search(normalize_key(text)) for text in (stem, answer))


def _sourced() -> list[tuple[str, tuple[str, ...]]]:
    return [(arc.id, arc.sources) for arc in ARCS]


def _by_key() -> dict[str, str]:
    return catalogue.index_by_source(_sourced())


def drawn_texts() -> set[str]:
    """The normalized texts the catalogue draws."""
    return set(_by_key())


def resolve(entries: Iterable[tuple[str, str, str]]) -> dict[str, str]:
    """Maps question id -> arc id, matching the stem or the answer, whole.

    Both fields are passed because an arc is defined in the question as often
    as in the answer: five of the ten definitions bind through one, five
    through the other.
    """
    return catalogue.resolve(_by_key(), entries)


def payload() -> dict[str, object]:
    """The catalogue shaped for the page."""
    return {
        "arcs": [
            {
                "id": arc.id,
                "label": arc.label,
                "sectors": [
                    {"start": sector.start, "end": sector.end, "colour": sector.colour}
                    for sector in arc.sectors
                ],
                "caveats": dict(arc.caveats),
            }
            for arc in ARCS
        ],
    }
