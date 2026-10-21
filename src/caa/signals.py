"""The sound signals the official bank describes, as data.

Each entry carries the declarative pattern *and* the verbatim answer text it
encodes. The audit checks both directions: a quote that no longer appears in
the bank fails the build, and an answer shaped like a signal that no entry
covers fails it too. Neither drift can happen quietly.

Durations come from the bank itself, which defines its own terms: a short
sound is "aproximativ o secundă", a long one "4-6 secunde" in the class C
list and "circa 4 secunde" in the class D list, and the very short series
runs at "circa ¼ de secundă" per sound and per interval.

The gap between the sounds of one signal does NOT come from the bank. It is
chosen so the pattern is legible to the ear, and the interface says so.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

from caa import catalogue
from caa.normalize import normalize_key

# Sound kinds.
SHORT: Final = "short"
LONG: Final = "long"
VERY_SHORT: Final = "very-short"
STROKE: Final = "stroke"  # a bell stroke, not a short sound

# Instruments. Two, not three: "gong" appears once in the whole corpus and
# only inside a distractor, as does "sirena". No correct answer needs either.
WHISTLE: Final = "whistle"
BELL: Final = "bell"

DURATIONS: Final[dict[str, int]] = {
    SHORT: 1000,       # bank: "aproximativ o secundă"
    LONG: 4500,        # bank: "4-6 secunde" (C) and "circa 4 secunde" (D)
    VERY_SHORT: 250,   # bank: "circa ¼ de secundă"
    STROKE: 600,       # presentation: long enough for the bell to ring out
}

GAPS: Final[dict[str, int]] = {
    VERY_SHORT: 250,   # bank: "circa ¼ s" between the sounds of the series
}

# Presentation, not regulation. The bank never states the interval inside a
# signal; this is chosen for legibility and labelled as such in the interface.
DEFAULT_GAP: Final = 500


@dataclass(frozen=True)
class Signal:
    """One playable signal, with the bank text it stands for."""

    id: str
    label: str  # Romanian: this reaches the interface
    instrument: str
    pattern: tuple[str, ...]
    sources: tuple[str, ...]


SIGNALS: Final[tuple[Signal, ...]] = (
    Signal(
        id="sunet-scurt",
        label="Sunet scurt",
        instrument=WHISTLE,
        pattern=(SHORT,),
        sources=("un sunet a cărui durată este de aproximativ o secundă.",),
    ),
    Signal(
        id="sunet-lung",
        label="Sunet lung",
        instrument=WHISTLE,
        pattern=(LONG,),
        sources=("un sunet a cărui durată este de 4-6 secunde.",),
    ),
    Signal(
        id="vin-la-tribord",
        label="Vin la tribord",
        instrument=WHISTLE,
        pattern=(SHORT,),
        sources=("un sunet scurt.",),
    ),
    Signal(
        id="vin-la-babord",
        label="Vin la babord",
        instrument=WHISTLE,
        pattern=(SHORT, SHORT),
        sources=("două sunete scurte.",),
    ),
    Signal(
        id="masina-inapoi",
        label="Am mașina înapoi",
        instrument=WHISTLE,
        pattern=(SHORT, SHORT, SHORT),
        sources=("trei sunete scurte.",),
    ),
    Signal(
        id="avertizare",
        label="Avertizare — nu înțeleg intențiile",
        instrument=WHISTLE,
        pattern=(SHORT, SHORT, SHORT, SHORT, SHORT),
        sources=("un semnal de avertizare compus din cinci sunete scurte.",),
    ),
    Signal(
        id="acord-depasire",
        label="Acord la depășire (litera C)",
        instrument=WHISTLE,
        pattern=(LONG, SHORT, LONG, SHORT),
        sources=("un sunet lung, un sunet scurt, un sunet lung şi unul scurt (litera C)",),
    ),
    Signal(
        id="manevra-redusa-vizibilitate",
        label="Capacitate de manevră redusă, pe vizibilitate redusă",
        instrument=WHISTLE,
        pattern=(LONG, SHORT, SHORT),
        # The same signal, three wordings in the bank. The first carries a
        # typo — "un sunete lung" — which is quoted as it stands: correcting
        # it here would break the match it exists to make.
        sources=(
            "un sunete lung urmat de 2 sunete scurte la intervale nu mai mari de 2 minute.",
            "un sunet lung urmat de 2 sunete scurte, la intervale ce nu vor fi mai mari de 2 minute.",
            "un sunet lung urmat de două sunete scurte, la intervale nu mai mari de 2 minute.",
        ),
    ),
    Signal(
        id="serie-foarte-scurte",
        label="Serie de sunete foarte scurte — pericol de abordaj",
        instrument=WHISTLE,
        pattern=(VERY_SHORT,) * 6,
        sources=("O serie de cel puţin 6 sunete cu o durată de circa ¼ de secundă fiecare",),
    ),
    Signal(
        id="doua-lovituri-clopot",
        label="Serie de bătăi de clopot",
        instrument=BELL,
        pattern=(STROKE, STROKE),
        sources=("Înseamnă două lovituri de clopot",),
    ),
)

# Answers that look like a signal but cannot be played without inventing
# regulation. Written down rather than left to slip through the coverage rule.
NOT_A_PATTERN: Final[dict[str, str]] = {
    '“O serie de sunete de clopot” sau “sunete lungi” cu alte mijloace acustice repetate':
        "the source gives neither a count nor a duration",
}

# A deliberately wide net over the normalized answer: better to demand a
# decision on something harmless than to miss a signal the bank gains later.
PATTERN_SHAPE: Final = re.compile(
    r"(un|doua|trei|patru|cinci|sase|[1-9]) (sunet|sunete|lovitur|batai|bataie)"
    r"|sunet (scurt|lung)"
    r"|serie de sunete"
    r"|(batai|lovituri) de clopot"
)


def looks_like_pattern(text: str) -> bool:
    """True when an answer is shaped like a sound signal."""
    return bool(PATTERN_SHAPE.search(normalize_key(text)))


def _sourced() -> list[tuple[str, tuple[str, ...]]]:
    return [(signal.id, signal.sources) for signal in SIGNALS]


def _by_key() -> dict[str, str]:
    return catalogue.index_by_source(_sourced())


def played_answers() -> set[str]:
    """The normalized answer texts the catalogue can play.

    The audit's coverage rule asks a question about an answer, not about a
    question, so it needs this set rather than `resolve`'s id-keyed mapping.
    Both read the same index, so neither can drift from the other.
    """
    return set(_by_key())


def resolve(answers: Iterable[tuple[str, str]]) -> dict[str, str]:
    """Maps question id -> signal id.

    The match is on the whole correct answer, not a fragment: "un sunet
    scurt." and "un sunet scurt, dar numai ziua." are different answers, and
    a fragment match would put the second under the first's signal.
    """
    return catalogue.resolve(_by_key(), answers)


def payload() -> dict[str, object]:
    """The catalogue shaped for the page."""
    return {
        "timing": {
            "durations": dict(DURATIONS),
            "gaps": dict(GAPS),
            "defaultGap": DEFAULT_GAP,
        },
        "signals": [
            {
                "id": signal.id,
                "label": signal.label,
                "instrument": signal.instrument,
                "pattern": list(signal.pattern),
            }
            for signal in SIGNALS
        ],
    }
