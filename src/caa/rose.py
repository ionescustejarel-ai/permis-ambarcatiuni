"""The compass rose, as data.

The compass theme is twenty-six questions and nine statements, every one of
them about an angle: measured from what, to what. It is the only purely
geometric theme in the application and, until this catalogue, the only one
with nothing drawn — a candidate reading "unghiul din planul orizontului
adevărat măsurat de la direcția nord adevărat până la axul prova al navei"
had to build the picture in their head.

One rose per definition, and one for the values. The first draft drew all
three angles on a single circle so they could be compared — and the three
labels overlapped into a smudge, measured in the browser. A circle of this
size holds one named angle, so each definition takes its own, and the
contrast the drawing exists for shows up as three consecutive rules whose
third arc visibly starts at the bow instead of at north.

What is deliberately absent: the points of the compass. The bank says N is
cardinal, SW intercardinal, SSE inter-intercardinal and "E la N"
intermediary — it names them, and never gives a single bearing for any of
them. Placing SSE at 157°5 would mean importing the thirty-two point system,
which is not in the bank. That classification stays in prose, for the same
reason the knots stay undrawn: the most tempting picture is the one that
would have to be invented.

Bearings follow the convention `bearingPoint` already fixed for the arcs:
zero is up the screen, clockwise. Two drawings disagreeing about which way
090 points would be worse than either being wrong alone.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Ray:
    """A labelled direction out of the centre.

    `bearing` is degrees clockwise from up. `figure` marks a label the bank
    states as a number — those are set in the tabular face the rest of the
    application uses for figures the exam marks.
    """

    bearing: float
    label: str
    figure: bool = False


@dataclass(frozen=True)
class Angle:
    """An angle drawn as a thin arc between two directions.

    Measured from `start` to `end`, clockwise, and labelled with what it is
    called rather than how large it is: the drawing teaches where an angle
    begins, and the bank gives no number for these.
    """

    start: float
    end: float
    label: str


@dataclass(frozen=True)
class Rose:
    id: str
    label: str
    rays: tuple[Ray, ...] = ()
    angles: tuple[Angle, ...] = ()
    # Drawn only where the rule is about a line of sight to something.
    mark: float | None = None
    # The ship's bow axis, when the rule measures to or from it.
    bow: float | None = None


# The bow at 055 and the mark at 130 are illustrative, and nothing on the
# drawing claims otherwise: no number is printed beside either angle. The
# figure teaches which direction an angle starts from, which is the whole of
# what the three definitions differ about. Shared across the three roses so
# the same ship and the same mark are recognisable from one to the next.
_BOW: Final = 55.0
_MARK: Final = 130.0

ROSES: Final[tuple[Rose, ...]] = (
    Rose(
        id="drum",
        label="Drumul: de la nord la axul prova",
        bow=_BOW,
        rays=(Ray(0, "N"),),
        angles=(Angle(0, _BOW, "drum"),),
    ),
    Rose(
        id="relevment",
        label="Relevmentul: de la nord la linia de vizare",
        mark=_MARK,
        rays=(Ray(0, "N"),),
        angles=(Angle(0, _MARK, "relevment"),),
    ),
    Rose(
        id="relevment-prova",
        label="Relevmentul prova: de la axul prova, nu de la nord",
        bow=_BOW,
        mark=_MARK,
        rays=(Ray(0, "N"),),
        angles=(Angle(_BOW, _MARK, "relevment prova"),),
    ),
    Rose(
        id="cadrane",
        label="Unde cad valorile",
        rays=(
            Ray(0, "N · 000", figure=True),
            Ray(90, "E · 090", figure=True),
            Ray(180, "S · 180", figure=True),
            Ray(270, "W · 270", figure=True),
            # One example per quadrant, each the bank's own correct answer.
            Ray(34, "NE · 034", figure=True),
            Ray(112, "SE · 112", figure=True),
            Ray(234, "SW · 234", figure=True),
            Ray(328, "NW · 328", figure=True),
        ),
    ),
)


def payload() -> dict[str, object]:
    """The catalogue shaped for the page."""
    return {
        "roses": [
            {
                "id": rose.id,
                "label": rose.label,
                "rays": [
                    {"bearing": ray.bearing, "label": ray.label, "figure": ray.figure}
                    for ray in rose.rays
                ],
                "angles": [
                    {"start": angle.start, "end": angle.end, "label": angle.label}
                    for angle in rose.angles
                ],
                "mark": rose.mark,
                "bow": rose.bow,
            }
            for rose in ROSES
        ],
    }
