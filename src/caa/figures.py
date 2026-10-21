"""The marks the official bank describes, as data.

Each entry carries the shape, the bands and the light *and* the verbatim bank
text it encodes. The audit checks both directions: a quote that no longer
appears fails the build, and a question describing a mark that no entry draws
fails it too.

Two systems live here and they contradict each other. On the Danube the
left-hand mark is a green cone; at IALA region A the port-hand mark is a red
cylinder. Every figure declares its system, and the application filters by
exam class before rendering — a figure shown to the wrong class teaches the
wrong answer. Day shapes belong to neither: a black cone point-down means the
same thing in both, and the bank asks about it under both classes.

Only what the bank asks is drawn. The cardinals appear with their painted body
and no topmark, because the questions ask only about the stripes; the topmarks
are separate figures because they are asked separately. The South cardinal is
absent from both lists and so is absent here.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

from caa import catalogue
from caa.normalize import normalize_key

IALA: Final = "iala"
DUNARE: Final = "dunare"
DAY_SHAPE: Final = "day-shape"

FLASHING: Final = "intermitenta"  # the only rhythm the bank names


@dataclass(frozen=True)
class Device:
    """A mark carried in the middle of another, with its own frame."""

    shape: str
    fill: str
    border: str | None = None


@dataclass(frozen=True)
class Body:
    """The painted object. `bands` reads top to bottom.

    `border` frames the body itself; `device` is a separate mark set in its
    centre. The supervision pennant needs both kept apart: the source frames
    the *rhombus* in blue, not the flag, and drawing the blue around the flag
    instead teaches a mark that does not exist.
    """

    shape: str
    bands: tuple[str, ...]
    border: str | None = None
    device: "Device | None" = None


@dataclass(frozen=True)
class Light:
    colour: str
    rhythm: str


@dataclass(frozen=True)
class Figure:
    id: str
    label: str  # Romanian: this reaches the interface
    system: str
    body: Body
    sources: tuple[str, ...]
    light: Light | None = None


FIGURES: Final[tuple[Figure, ...]] = (
    # --- IALA, class C ---------------------------------------------------
    Figure(
        id="cardinal-est",
        label="Cardinal Est",
        system=IALA,
        body=Body(shape="pillar", bands=("black", "yellow", "black")),
        sources=("negru-galben-negru;",),
    ),
    Figure(
        id="cardinal-vest",
        label="Cardinal Vest",
        system=IALA,
        body=Body(shape="pillar", bands=("yellow", "black", "yellow")),
        sources=("galben-negru-galben;",),
    ),
    Figure(
        id="cardinal-nord",
        label="Cardinal Nord",
        system=IALA,
        body=Body(shape="pillar", bands=("black", "yellow")),
        sources=("negru-galben.",),
    ),

    Figure(
        id="topmark-tribord-a",
        label="Semn de vârf — tribord, regiunea A",
        system=IALA,
        body=Body(shape="cone-up", bands=("green",)),
        sources=("Un con verde cu vârful în sus;",),
    ),
    Figure(
        id="topmark-babord-a",
        label="Semn de vârf — babord, regiunea A",
        system=IALA,
        body=Body(shape="cylinder", bands=("red",)),
        sources=("un cilindru roșu.",),
    ),
    Figure(
        id="pericol-izolat",
        label="Semn de vârf — pericol izolat",
        system=IALA,
        body=Body(shape="two-spheres", bands=("black",)),
        sources=("doua bule suprapuse de culoare neagra.",),
    ),
    # --- Dunăre, class D --------------------------------------------------
    Figure(
        id="geamandura-stanga",
        label="Geamandură pentru stânga",
        system=DUNARE,
        body=Body(shape="cone-up", bands=("green",)),
        light=Light(colour="green", rhythm=FLASHING),
        sources=("De formă conică, piturată în verde, lumina de culoare verde intermitentă",),
    ),
    Figure(
        id="geamandura-dreapta",
        label="Geamandură pentru dreapta",
        system=DUNARE,
        body=Body(shape="cylinder", bands=("red",)),
        light=Light(colour="red", rhythm=FLASHING),
        sources=("De formă cilindrică, piturată în roşu, lumina de culoare roşie intermitentă",),
    ),
    Figure(
        id="geamandura-bifurcatie",
        label="Geamandură de bifurcație",
        system=DUNARE,
        body=Body(shape="sphere", bands=("green", "red", "green", "red")),
        light=Light(colour="white", rhythm=FLASHING),
        sources=(
            "De formă sferică vopsită (piturată) în verde-roşu-verde-roşu, "
            "lumină de culoare albă intermitentă",
        ),
    ),
    # --- Day shapes, both classes ----------------------------------------
    Figure(
        id="semn-cilindru-negru",
        label="Cilindru negru — navă stânjenită de pescaj",
        system=DAY_SHAPE,
        body=Body(shape="cylinder", bands=("black",)),
        # Quoted from the question, not the answer: this one shows the mark and
        # asks what it means.
        sources=("Un cilindru negru reprezintă semnul purtat de o navă:",),
    ),
    Figure(
        id="semn-con-jos",
        label="Con cu vârful în jos — vele și motor",
        system=DAY_SHAPE,
        body=Body(shape="cone-down", bands=("black",)),
        # Three questions, three wordings, one mark. Two class C and one class
        # D, which is why a day shape cannot be filtered by system alone.
        sources=(
            "la prova, în locul cel mai vizibil, un con cu vârful în jos.",
            "La prova, în locul cel mai vizibil, un con cu vârful în jos este "
            "semnul purtat pe timp de zi de:",
            "Un con negru cu vârful în jos, amplasat cât mai sus posibil şi "
            "într-un loc unde va fi cel mai vizibil",
        ),
    ),
    Figure(
        id="flamura-supraveghere",
        label="Flamură de supraveghere fluvială",
        system=DAY_SHAPE,
        body=Body(shape="pennant", bands=("white",),
                  device=Device(shape="rhombus", fill="white", border="blue")),
        light=Light(colour="blue", rhythm=FLASHING),
        sources=(
            "Ziua arborează o flamură albă în centrul căreia se găseşte un romb "
            "alb încadrat cu un chenar albastru şi arată o lumină albastră intermitentă",
        ),
    ),
)

# Texts that read like a mark but cannot be drawn from what they say. Empty on
# today's bank — the recognizer below is exact on it — but kept so a future
# edition forces a written decision instead of a silent miss.
NOT_A_FIGURE: Final[dict[str, str]] = {}

# A mark is a painted object or something hoisted, not a light carried by a
# vessel. Anchoring on the marking verbs keeps the visibility ranges and the
# ship lights out; those belong to stage 3c.
#
# Applies to a *question* — its stem and its answer — never to a source quote
# on its own. Four of the quotes are bare answers, "negru-galben-negru;" among
# them, and the language that identifies them as marks lives in their stem. A
# net wide enough to catch those quotes alone was tried: adding a run of colour
# words pulled in two ship-light questions, exactly the class this anchoring
# exists to exclude.
FIGURE_SHAPE: Final = re.compile(
    r"(piturat|vopsit)\w*\s+(in|cu)\b"
    r"|semn de varf"
    r"|de forma (conic|cilindric|sferic)"
    r"|\bun (con|cilindru|romb)\b"
    r"|arboreaza"
)


def looks_like_figure(text: str) -> bool:
    """True when a text describes a mark rather than a rule about one."""
    return bool(FIGURE_SHAPE.search(normalize_key(text)))


def _sourced() -> list[tuple[str, tuple[str, ...]]]:
    return [(figure.id, figure.sources) for figure in FIGURES]


def _by_key() -> dict[str, str]:
    return catalogue.index_by_source(_sourced())


def drawn_texts() -> set[str]:
    """The normalized texts the catalogue draws."""
    return set(_by_key())


def resolve(entries: Iterable[tuple[str, str, str]]) -> dict[str, str]:
    """Maps question id -> figure id.

    Each entry is (question id, stem, correct answer) and both fields are
    tried, whole. Marks are described in the question as often as in the
    answer — "Un cilindru negru reprezintă semnul purtat de o navă:" shows the
    mark and asks its meaning — so matching answers alone loses half of them.

    The match is on a whole field, never a fragment: an answer that merely
    contains a quoted phrase is a different answer.

    A question whose two fields name different figures raises. No such question
    exists today, and the alternative was worse than an exception: taking the
    stem because it was written first is not a policy, and the losing figure
    would have been dropped without a word. If a future edition creates one,
    somebody has to decide which mark the question is about.
    """
    return catalogue.resolve(_by_key(), entries)


def payload() -> dict[str, object]:
    """The catalogue shaped for the page."""
    return {
        "figures": [
            {
                "id": figure.id,
                "label": figure.label,
                "system": figure.system,
                "body": {
                    "shape": figure.body.shape,
                    "bands": list(figure.body.bands),
                    "border": figure.body.border,
                    "device": None if figure.body.device is None else {
                        "shape": figure.body.device.shape,
                        "fill": figure.body.device.fill,
                        "border": figure.body.device.border,
                    },
                },
                "light": None if figure.light is None
                else {"colour": figure.light.colour, "rhythm": figure.light.rhythm},
            }
            for figure in FIGURES
        ],
    }
