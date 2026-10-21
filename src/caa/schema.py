"""Diagrams that are neither a mark, an arc, a light nor a compass rose.

Four pictures the theory asks for and nothing yet draws:

* the hull in section, which carries five statements at once — the keel in
  the diametral plane with the stem forward and the sternpost aft, and the
  frames and floors in the transversal plane, planked with strakes;
* the rudder's effect going astern, where the bow swings one way and the
  stern the other, and the two halves of the answer are easy to swap;
* the leeway a wind ahead of the beam gives, where the bank is specific
  about the side: from the starboard bow, the drift is to port;
* the propeller's hand, seen from astern.

Each drawing names a `view`, and the renderer has one function per view.
That is deliberately not a general diagram language: four pictures with
almost nothing in common are clearer as four small routines than as one
vocabulary that has to be learnt before either can be read.

Every label here is a word the bank uses. Where the bank gives no position
— the frames are "la intervale egale" and it never says how many — the
drawing shows enough to read the idea and claims no count.

Drawn and then removed: the propeller's hand. The bank says it turns "la
dreapta" going ahead and never says from where you are looking, and a
rotation cannot be drawn without a viewpoint. Supplying one would have put
an invention at the centre of the picture — and a reader who imagined
standing forward instead of aft would have learnt the opposite. The words
carry that rule as well as any circle could.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Schema:
    """One diagram.

    `side` is the board a movement or a rotation happens towards, where the
    bank names one: "tribord" or "babord". `view` picks the routine that
    draws it, and the routines are enumerated in rose-free JS rather than
    composed from primitives here.
    """

    id: str
    label: str
    view: str
    side: str | None = None
    note: str | None = None


SCHEMAS: Final[tuple[Schema, ...]] = (
    Schema(
        id="chila",
        label="Chila, în plan diametral, de la prova la pupa",
        view="sectiune-lung",
        note="Etrava prelungește chila în prova, etamboul în pupa.",
    ),
    Schema(
        id="osatura",
        label="Coastele și varangele, în plan transversal",
        view="sectiune-trans",
        note="Fixate pe chilă la intervale egale; învelișul e bordajul, "
             "din file.",
    ),
    Schema(
        # The bank gives this one twice, mirrored: going ahead the bow turns
        # towards the rudder, going astern away from it. Drawn astern because
        # that is the half a candidate gets wrong.
        id="carma-inapoi",
        label="La deplasarea înapoi: prova în bordul opus cârmei",
        view="plan-carma",
        side="tribord",
        note="Cârma la tribord, prova la babord, pupa la tribord.",
    ),
    Schema(
        id="deriva",
        label="Vânt din prova tribord: derivă la babord",
        view="plan-vant",
        side="babord",
        note="Vântul dinaintea traversului micșorează și viteza.",
    ),
)


def payload() -> dict[str, object]:
    """The catalogue shaped for the page."""
    return {
        "schemas": [
            {
                "id": schema.id,
                "label": schema.label,
                "view": schema.view,
                "side": schema.side,
                "note": schema.note,
            }
            for schema in SCHEMAS
        ],
    }
