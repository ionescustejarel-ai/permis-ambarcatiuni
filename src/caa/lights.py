"""What each type of vessel carries, as data.

Stage 3c drew what a light covers. This draws what a vessel wears: which
lights, where on the hull, and in what order going up. The bank asks it
eighteen times across twelve distinct configurations, and answers one of them
two different ways: the sailing vessel, the commonest type in the bank,
carries two extra all-round lights at class D and none at class C.

Three things in the model come from the source rather than from convenience.

`colours` is a tuple because one lantern can show more than one colour. The
combined lantern shows red, green and white at once; the sidelights are a
pair drawn as a single marker; and the anchor light has no colour stated
anywhere in the bank, so it carries none and is drawn in a neutral tint, the
same way stage 3c draws a sector whose source names no colour.

`ANY` is a station because five configurations give only a vertical order —
"în poziţie verticală", "într-un loc corespunzător" — and never a position
along the hull. Putting those at the mast would be inventing a fact the bank
does not state.

`SIDE` and `BOW` are separate because the bank separates them: a towed vessel
carries "luminile din borduri", one towed alongside carries them "la
extremitatea prova". Drawn alike, the two configurations would be one picture
and the distinction the exam asks about would disappear.

Colours that *are* named come from the bank's own definitions, not from
COLREG: the masthead light is white because the bank defines it as "o lumină
albă aşezată deasupra axului longitudinal", the quote stage 3c catalogues.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

from caa import catalogue
from caa.normalize import normalize_key

# Where a lantern hangs. Every value is something the source actually says,
# except ANY, which is what the source says when it says nothing.
MAST: Final = "mast"      # "la catarg", "la măr", "în partea superioară a catargului"
SIDE: Final = "side"      # "luminile din borduri", unqualified
BOW: Final = "bow"        # "la extremitatea prova"
STERN: Final = "stern"    # "în pupa", "de la pupa"
ANY: Final = "any"        # no position given at all

STATIONS: Final[frozenset[str]] = frozenset({MAST, SIDE, BOW, STERN, ANY})


@dataclass(frozen=True)
class Placed:
    """One lantern: its colours, where it hangs, and how high up that station.

    `colours` empty means the source names none. `level` is the order within a
    single station, 0 at the bottom, and stays 0 wherever the source stacks
    nothing.
    """

    colours: tuple[str, ...]
    station: str
    level: int = 0


@dataclass(frozen=True)
class Config:
    id: str
    label: str  # Romanian: this reaches the interface
    lights: tuple[Placed, ...]
    sources: tuple[str, ...]
    # A qualifier the source states and a drawing cannot: "dacă este posibil".
    note: str = ""


CONFIGS: Final[tuple[Config, ...]] = (
    Config(
        id="vele-in-mars",
        label="Navă cu vele în marș",
        lights=(
            Placed(colours=("red", "green"), station=SIDE),
            Placed(colours=("white",), station=STERN),
        ),
        sources=(
            "Luminile din borduri şi lumina din pupa sunt luminile pe care le poartă o navă:",
            "Ce lumini poartă o navă cu vele în marş?",
        ),
    ),
    Config(
        id="vele-felinar-combinat",
        label="Navă cu vele — felinarul combinat",
        lights=(
            # One lantern showing all three: the source reunites them, it does not stack them.
            Placed(colours=("red", "green", "white"), station=MAST),
        ),
        sources=(
            "La măr sau în partea superioară a catargului, în locul cel mai vizibil, trebuie să "
            "poarte felinarul combinat o navă cu vele în marş, cu o lungime mai mică de:",
            "Unde trebuie să poarte felinarul combinat o navă cu vele în marş mai mică de 20 m?",
            "Luminile din borduri şi lumina din pupa, reunite într-un felinar este purtat de :",
            "luminile din borduri şi lumina din pupa, pe care le poate reuni într-un felinar.",
        ),
        note="Sursa spune „le poate reuni”: felinarul e o alternativă la cele trei lumini separate, nu o obligație.",
    ),
    Config(
        # Only the two supplementary lights: that is what the question asks for.
        id="vele-lumini-suplimentare",
        label="Navă cu vele — luminile suplimentare",
        lights=(
            Placed(colours=("red",), station=MAST, level=1),
            Placed(colours=("green",), station=MAST),
        ),
        sources=(
            "la măr sau la partea superioară a catargului o lumină roişie deasupra unei lumini "
            "verzi, vizibile pe tot orizontul.",
        ),
    ),
    Config(
        id="propulsie-mecanica-mica",
        label="Navă mică cu propulsie mecanică",
        lights=(
            Placed(colours=("white",), station=ANY),
            Placed(colours=("red", "green"), station=SIDE),
        ),
        sources=(
            "o lumină albă vizibilă peste tot orizontul şi dacă este posibil şi luminile din "
            "borduri.",
        ),
        note="Luminile din borduri numai „dacă este posibil”.",
    ),
    Config(
        # The masthead light is white by the bank's own definition, quoted at stage 3c.
        id="traulare-nu-in-mars",
        label="Navă care traulează, nu în marș",
        lights=(
            Placed(colours=("green",), station=ANY, level=1),
            Placed(colours=("white",), station=ANY),
            # Higher than the green and abaft it, which the layout guarantees: the mast
            # sits aft of the amidships staff and above its top level.
            Placed(colours=("white",), station=MAST),
        ),
        sources=(
            "Două lumini suprapuse, vizibile pe tot orizontul, lumina superioară verde şi ce "
            "inferioară albă, o lumină de catarg aşezată la o înălţime mai mare decât lumina "
            "verde şi înapoia acesteia sunt luminile purtate de:",
        ),
    ),
    Config(
        id="impinsa-inainte",
        label="Navă împinsă înainte",
        lights=(
            Placed(colours=("red", "green"), station=BOW),
        ),
        sources=(
            "trebuie să poarte la extremitatea prova luminile din borduri.",
        ),
    ),
    Config(
        # Same lights as the sailing vessel under way. The bank asks them separately,
        # so they stay separate entries: a candidate who notices has learnt something true.
        id="remorcata",
        label="Navă remorcată",
        lights=(
            Placed(colours=("red", "green"), station=SIDE),
            Placed(colours=("white",), station=STERN),
        ),
        sources=(
            "Ce lumini trebuie să poarte obiectele sau navele remorcate, altele decât cele cu "
            "forma nedefinită?",
        ),
    ),
    Config(
        # BOW, not SIDE: the source says „la extremitatea prova” and that is the only
        # thing telling this configuration apart from the one above.
        id="remorcata-la-ureche",
        label="Navă remorcată la ureche",
        lights=(
            Placed(colours=("red", "green"), station=BOW),
            Placed(colours=("white",), station=STERN),
        ),
        sources=(
            "lumina de pupa şi luminile din borduri la extremitatea prova.",
        ),
    ),
    Config(
        id="manevra-redusa-nu-in-mars",
        label="Capacitate de manevră redusă, nu în marș",
        lights=(
            Placed(colours=("red",), station=ANY, level=2),
            Placed(colours=("white",), station=ANY, level=1),
            Placed(colours=("red",), station=ANY),
        ),
        sources=(
            "Trei lumini în poziţie verticală din care luminile de sus şi de jos roşii şi lumina "
            "din mijloc albă sunt luminile purtate de o navă:",
        ),
    ),
    Config(
        id="manevra-redusa-la-ancora",
        label="Capacitate de manevră redusă, la ancoră",
        lights=(
            Placed(colours=("red",), station=ANY, level=2),
            Placed(colours=("white",), station=ANY, level=1),
            Placed(colours=("red",), station=ANY),
            # The anchor light: the bank never states its colour, in any of the six
            # questions that mention it, so this one carries none.
            Placed(colours=(), station=STERN),
        ),
        sources=(
            "Luminile roşu-alb-roşu dispuse pe verticală, lumina de ancoră de la pupa sunt "
            "luminile purtate de o navă:",
        ),
    ),
    Config(
        # Class D only, and the whole reason the panel filters by class: at class C the
        # same vessel carries no masthead pair at all.
        id="vele-in-mars-D",
        label="Navă cu vele în marș",
        lights=(
            Placed(colours=("red",), station=MAST, level=1),
            Placed(colours=("green",), station=MAST),
            Placed(colours=("red", "green"), station=SIDE),
            Placed(colours=("white",), station=STERN),
        ),
        sources=(
            "Două lumini obişnuite sau clare suprapuse vizibile din toate părţile, din care "
            "lumina superioară trebuie să fie roşie, iar lumina inferioară verde. Aceste lumini "
            "trebuie să fie dispuse, într-un loc corespunzător în partea superioară sau în vârful "
            "catargului la distanţă de cel puţin 1 m una de cealaltă. Luminile din borduri verde "
            "şi roşu şi lumina albă de pupa",
            "Două lumini, obişnuite sau clare suprapuse vizibile din toate părţile din care "
            "lumina superioară trebuie să fie roşie, iar lumina inferioară verde; aceste lumini "
            "trebuie să fie dispuse într-un loc corespunzător, în partea superioară sau în vârful "
            "catargului, la o distanţă de cel puţin 1 m una de cealaltă. Luminile din borduri "
            "verde/roşu obişnuite şi lumina albă obişnuită de pupa",
        ),
    ),
    Config(
        id="mica-lumina-alba",
        label="Ambarcațiune mică — o lumină albă",
        lights=(
            Placed(colours=("white",), station=ANY),
        ),
        sources=(
            "O lumină albă obişnuită dispusă într-un loc corespunzător şi la o astfel de înălţime "
            "încăt să fie vizibilă din toate părţile",
            "O lumină albă obişnuită, dispusă într-un loc corespunzător şi la o înălţime de la "
            "care să fie vizibilă din toate părţile",
        ),
        note="Aceeași lumină în două situații pe care banca le întreabă separat: legată la mal și autopropulsată sub 7 m, în marș.",
    ),
)

# Texts that ask what a vessel carries but give nothing to draw. Each one
# states why, so a future edition of the bank forces a written decision.
NOT_A_CONFIG: Final[dict[str, str]] = {
    "dacă nu poartă luminile unei nave cu vele, să fie pregătiră să arate o lanternă "
    "electrică sau un felinar cu lumină albă.": (
        "Tocmai absența unei lumini fixe e răspunsul: nava cu rame arată o lanternă la "
        "nevoie."
    ),
    "trebuie să fie gata să arate în orice moment o lanternă electrică sau un felinar "
    "aprins cu o lumină albă.": (
        "La fel, pentru nava cu vele sub 7 m: o pregătire, nu o dispunere."
    ),
    "luminile unei nave cu propulsie mecanică în marş plus o lumină galbenă cu "
    "sclipiri vizibilă pe tot orizontul.": (
        "Trimite la o configurație pe care banca n-o descrie: singura navă cu propulsie "
        "mecanică desenată aici e cea mică, „peste 7 m şi 7 Nd”."
    ),
    "Trebuie să arate o lumină albă obişnuită vizibilă din toate părţile la apropierea "
    "altor nave": (
        "Barca cu rame arată lumina „la apropierea altor nave”, nu o poartă aprinsă. "
        "Exact acel calificativ desparte răspunsul corect de distractorul de alături, "
        "care e aceeași lumină fără nicio condiție — deci o siluetă cu lumina "
        "desenată pe ea ar arăta tocmai răspunsul greșit. La clasa C aceeași barcă "
        "e exclusă din același motiv."
    ),
    "Luminile unei ambarcaţiuni mici autopropulsate ce navigă izolat şi a cărei "
    "lungime nu depăşeşte 20 m": (
        "Trimitere fără bază în bancă."
    ),
}


# A configuration question is about lights, asks what a vessel carries, and is
# not one of the things stage 3c already owns. All three conditions are load
# bearing — see `looks_like_config`.
ABOUT_LIGHTS: Final = re.compile(r"lumin|felinar")

CONFIG_SHAPE: Final = re.compile(
    r"ce lumini|luminile purtate de|lumini(le)? suplimentare|poate purta"
    r"|ce felinare|trebuie sa poarte|trebuie sa arate|trebuie sa aiba"
)

# A stem that opens by listing lights and asks who carries them.
CONFIG_OPENING: Final = re.compile(r"^(doua|trei|patru|luminile) ")

# Visibility ranges are a number, and arc definitions belong to stage 3c.
# Without this guard the net takes both and the question gets two figures.
NOT_A_CONFIG_SHAPE: Final = re.compile(
    r"la ce distanta|mile marine"
    r"|arc de (orizont|cerc|\d)|pe un arc de|cate \d+ ?5? in fiecare bord"
)


def looks_like_config(stem: str, answer: str) -> bool:
    """True when a question asks what lights a vessel carries.

    The `ABOUT_LIGHTS` test is not decoration. "trebuie să poarte" and
    "trebuie să aibă" introduce day shapes, life jackets, knots, load-line
    marks and sound-signalling equipment exactly as naturally as lights, and
    without it the net takes 32 questions instead of 23. The first measurement
    missed that because it ran only over the two light themes — and a
    recognizer that depends on the theme is precisely what this project cannot
    afford, since the theme classifier has known errors and a misfiled
    question would then pass the audit in silence.
    """
    fields = (normalize_key(stem), normalize_key(answer))
    if any(NOT_A_CONFIG_SHAPE.search(text) for text in fields):
        return False
    if not any(ABOUT_LIGHTS.search(text) for text in fields):
        return False
    if any(CONFIG_SHAPE.search(text) for text in fields):
        return True
    return CONFIG_OPENING.search(fields[0]) is not None


def _sourced() -> list[tuple[str, tuple[str, ...]]]:
    return [(config.id, config.sources) for config in CONFIGS]


def _by_key() -> dict[str, str]:
    return catalogue.index_by_source(_sourced())


def drawn_texts() -> set[str]:
    """The normalized texts the catalogue draws."""
    return set(_by_key())


def resolve(entries: Iterable[tuple[str, str, str]]) -> dict[str, str]:
    """Maps question id -> configuration id, matching the stem or the answer.

    Both fields are passed because the bank asks it both ways round: some
    questions describe the lights and ask for the vessel, others name the
    vessel and ask for the lights. Two of them share an answer word for word
    — "luminile din borduri şi lumina de pupa." belongs to the sailing vessel
    and to the towed vessel alike — so those two bind through their stems.
    """
    return catalogue.resolve(_by_key(), entries)


def payload() -> dict[str, object]:
    """The catalogue shaped for the page."""
    return {
        "configs": [
            {
                "id": config.id,
                "label": config.label,
                "note": config.note,
                "lights": [
                    {
                        "colours": list(light.colours),
                        "station": light.station,
                        "level": light.level,
                    }
                    for light in config.lights
                ],
            }
            for config in CONFIGS
        ],
    }
