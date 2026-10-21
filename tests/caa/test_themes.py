import json
import re
from pathlib import Path

import pytest

from caa.dedup import Question
from caa.normalize import normalize_key
from caa.structure import Discipline, Section
from caa.themes import FALLBACK_THEME, THEMES, assign_themes, theme_distribution


def question(text, section=Section.MAIN):
    return Question(
        id="qtest",
        question=text,
        options=("a", "b", "c"),
        correct=0,
        section=section,
        disciplines=(("C", Discipline.COLREG),),
        classes=("C",),
    )


def _theme_of(text, section=Section.MAIN):
    return assign_themes([question(text, section)])[0].theme


def test_first_aid_section_maps_directly_to_its_theme():
    assert _theme_of("Care este durata maximă a masajului?", Section.FIRST_AID) == "prim-ajutor"


def test_legislation_section_maps_directly_to_its_theme():
    assert _theme_of("Care fapte constituie infracțiune?", Section.LEGISLATION) == "legislatie"


def test_sound_signals_are_recognised():
    assert _theme_of('Ce se înţelege prin expresia "sunet lung"?') == "semnale-sonore"


def test_buoys_are_recognised():
    assert _theme_of("Care este culoarea unei geamanduri de bifurcaţie ?") == "geamanduri-si-balizaj"


def test_skyjet_wins_over_the_broader_manoeuvre_rule():
    assert _theme_of("Conducerea de motociclete nautice (skyjet) este supusă limitelor") == "motovehicule-nautice"


def test_unmatched_questions_get_the_fallback_theme():
    assert _theme_of("Căror nave li se aplică prevederile Colreg-1972?") == FALLBACK_THEME


def _themed(text, options, correct=0, section=Section.MAIN):
    item = Question(
        id="qtest",
        question=text,
        options=options,
        correct=correct,
        section=section,
        disciplines=(("C", Discipline.COLREG),),
        classes=("C",),
    )
    return assign_themes([item])[0].theme


def test_a_distractor_does_not_steal_a_question_from_its_stem():
    """Verbatim from the bank: the same stem, two different sets of options.

    Both are about a boat's armament. Matching stem and options together sent
    the first to the lights theme and the second to the compass theme, because
    of a wrong answer each happened to carry.
    """
    stem = "In categoria obiectelor de armament destinate pentru vitalitatea bărcii, intra si:"
    assert _themed(stem, ("trusa cu medicamente", "trusa cu scule de marangozerie",
                          "felinar de vânt")) == "parame-noduri-ancore"
    assert _themed(stem, ("trusa cu medicamente", "pene, cuie, câlți",
                          "compasul de barca")) == "parame-noduri-ancore"


def test_the_options_still_place_a_question_whose_stem_says_nothing():
    """The second pass is what keeps 131 questions out of the fallback."""
    assert _themed("Rodanțele sunt:", ("apărătoare ale macaralelor", "apărătoare ale gașelor",
                                       "dispozitive de vitalitate")) == "parame-noduri-ancore"


def test_a_compass_point_is_not_buoyage():
    """"cardinal" belongs to both vocabularies; the stem says which one."""
    assert _themed("Cartul N este un cart:",
                   ("intercardinal;", "cardinal;", "inter-intercardinal;")
                   ) == "navigatie-compas-si-drumuri"


def test_the_course_rule_survives_the_definite_article():
    """"drum adevarat" is not a substring of "drumul adevarat"."""
    assert _theme_of("Drumul adevărat al navei este:") == "navigatie-compas-si-drumuri"
    assert _theme_of("Drumul magnetic al navei este") == "navigatie-compas-si-drumuri"
    assert _theme_of("Drumul giro al navei este") == "navigatie-compas-si-drumuri"


def test_a_free_lane_still_belongs_to_the_steering_rules():
    """The widened course pattern must not swallow "drum liber"."""
    assert _theme_of("Cine are drum liber la intalnirea din sens opus?") == "reguli-de-drum"


def test_the_correct_answer_promotes_lights_to_the_special_rule():
    """The stem describes an arrangement; only the right answer names the vessel."""
    stem = ("Trei lumini în poziţie verticală din care luminile de sus şi de jos roşii "
            "şi lumina din mijloc albă sunt luminile purtate de o navă:")
    options = ("nestăpână pe manevra sa.",
               "cu capacitate de manevră redusă când nu este în marş.",
               "stânjenită de pescajul ei când nu este în marş.")
    assert _themed(stem, options, correct=1) == "lumini-situatii-speciale"


def test_a_distractor_cannot_promote_lights_to_the_special_rule():
    """Only the correct answer promotes. The same options, a different key."""
    stem = ("Trei lumini în poziţie verticală din care luminile de sus şi de jos roşii "
            "şi lumina din mijloc albă sunt luminile purtate de o navă:")
    options = ("o navă cu vele în marş.",
               "cu capacitate de manevră redusă când nu este în marş.",
               "o navă cu rame.")
    assert _themed(stem, options, correct=0) == "lumini-propulsie-mecanica"


def test_promotion_does_not_reach_outside_its_declared_pair():
    """"cardinal" in the right answer must not drag a compass point to buoyage."""
    assert _themed("Cartul N este un cart:",
                   ("intercardinal;", "cardinal;", "inter-intercardinal;"),
                   correct=1) == "navigatie-compas-si-drumuri"


def test_every_question_receives_a_theme():
    questions = assign_themes(
        [question("orice text fara cuvinte cheie"), question("Ce este sunetul scurt?")]
    )
    assert all(item.theme is not None for item in questions)


def _rules_matching(text):
    """Every rule whose pattern hits the text, in THEMES order."""
    haystack = normalize_key(text)
    return [slug for slug, pattern in THEMES if re.search(pattern, haystack)]


def test_the_earlier_rule_wins_when_two_rules_match():
    """Rule order is load-bearing: 174 questions in the real bank match 2+ rules."""
    text = "Când relevmentul compas la o navă care se apropie nu variază, există pericol de coliziune?"
    assert _rules_matching(text) == ["reguli-de-drum", "navigatie-compas-si-drumuri"]
    assert _theme_of(text) == "reguli-de-drum"


def test_the_earlier_rule_wins_across_three_candidates():
    text = "Ce culoare are lumina geamandurii de babord?"
    assert _rules_matching(text) == [
        "geamanduri-si-balizaj",
        "lumini-propulsie-mecanica",
        "constructia-ambarcatiunii",
    ]
    assert _theme_of(text) == "geamanduri-si-balizaj"


def test_distribution_counts_themes():
    questions = assign_themes(
        [question("Ce este sunetul scurt?"), question("Ce este sunetul lung?")]
    )
    assert theme_distribution(questions)["semnale-sonore"] == 2


BANK = Path(__file__).resolve().parents[2] / "build" / "questions.json"


@pytest.fixture(scope="module")
def bank():
    if not BANK.is_file():
        pytest.skip("run `python -m caa.cli` first")
    return json.loads(BANK.read_text(encoding="utf-8"))["questions"]


def test_an_inflected_head_still_matches_its_pattern():
    """The bank writes "marcajul lateral"; the table used to say "marcaj lateral".

    Not a substring, so three buoyage questions and a pile of others fell
    through to whichever later rule their text happened to trip.
    """
    assert _theme_of("Marcajul lateral de tribord din regiunea A are ca semn de vârf:") \
        == "geamanduri-si-balizaj"
    assert _theme_of("Când se emit semnalele sonore de manevră?") == "semnale-sonore"
    assert _theme_of("Ce este semnalul de pericol dat cu braţele?") \
        == "semnale-de-pericol-si-salvare"


def test_an_ending_does_not_swallow_a_verb():
    """`semnal\\w* sonor` matches "semnaliza sonor", which is a different word.

    Measured: with the wildcard, a question about traffic separation zones
    moved to sound signals by following one of its own distractors — the
    defect the stem-decides rule exists to prevent.
    """
    stem = "Cum trebuie să se navige în zone vecine cu extremităţile unei zone de separare a traficului?"
    options = (
        "se va naviga în direcţia generală a traficului.",
        "se vor semnaliza sonor şi vizual intenţiile de schimbare de drum.",
        "cu atenţie deosebită.",
    )
    assert _themed(stem, options, 2) != "semnale-sonore"


def test_the_isolated_danger_mark_is_buoyage():
    """"pericol izolat" was in no pattern at all, so it landed in distress signals."""
    assert _theme_of("Marcajul de pericol izolat are ca semn de vârf:") \
        == "geamanduri-si-balizaj"


def test_a_day_shape_with_no_colour_is_still_a_day_shape():
    """The table asked for "con negru"; the bank writes "un con cu vârful în jos"."""
    assert _theme_of(
        "La prova, în locul cel mai vizibil, un con cu vârful în jos este semnul "
        "purtat pe timp de zi de:"
    ) == "semne-si-forme-ziua"
    assert _theme_of(
        "O navă care navigă cu vele folosind în acelaşi timp şi motor, ziua în marş, "
        "trebuie să poarte:"
    ) == "semne-si-forme-ziua"


def test_a_fog_signal_is_filed_with_fog():
    """Sound signals are matched before everything, so fog lost its own questions.

    A candidate studying restricted visibility must find the signal that goes
    with it. Restricted visibility therefore comes first.
    """
    assert _theme_of("Ce semnale sonore emite o navă cu vele pe vizibilitate redusă?") \
        == "vizibilitate-redusa"


def test_a_manoeuvring_signal_is_not_a_fog_signal():
    """The other half of the same reorder: it says nothing about fog."""
    assert _theme_of("Când se emit semnalele sonore de manevră?") == "semnale-sonore"


def test_the_fairway_is_a_place_and_not_a_mark():
    """Buoyage is about marks. Where fishing gear may not be laid is not one.

    The real options matter: the stem matches nothing, so the second pass
    reads them, and the correct answer says "În şenalul navigabil". With any
    inflected `senal navigabil` in the buoyage rule this question becomes a
    buoyage question, which is the move this test exists to forbid. Dummy
    options would never run that pass, and the first version of this test
    proved nothing.
    """
    assert _themed(
        "Unde este interzis de a se instala plase sau alte unelte de pescuit fixe?",
        ("În şenalul navigabil", "În porturi", "În zonele de agrement"),
        0,
    ) != "geamanduri-si-balizaj"


def test_no_pattern_is_written_in_a_form_the_bank_never_uses(bank):
    """The lint that outlives this stage.

    Repairing nine patterns does not stop a tenth being written in dictionary
    form. This reads the table itself and fails on any two-word literal whose
    head appears inflected in the bank while the literal does not match — the
    exact condition that hid five questions.
    """
    texts = [normalize_key(q["q"] + " " + " ".join(q["opts"])) for q in bank]
    unusable = []
    for _, pattern in THEMES:
        for alternative in pattern.split("|"):
            alternative = alternative.strip()
            if " " not in alternative or not re.fullmatch(r"[a-z ]+", alternative):
                continue
            # "s o s" is a normalized abbreviation, not a Romanian phrase: a
            # single-letter head makes the inflection probe match junk — it
            # found "varful in suS O Sfera" and called it an inflection.
            if any(len(word) == 1 for word in alternative.split()):
                continue
            head, rest = alternative.split(" ", 1)
            inflected = re.compile(rf"\b{head}\w+ {re.escape(rest)}")
            literal = re.compile(rf"\b{re.escape(alternative)}")
            if any(inflected.search(t) and not literal.search(t) for t in texts):
                unusable.append(alternative)
    assert unusable == [], f"written in dictionary form: {unusable}"


def test_freeboard_is_matched_by_its_stem_and_not_by_a_distractor():
    """The bank writes only "Bordul liber"; the bare literal never matched it.

    The question sat in the right theme by luck — a distractor mentioning
    "pescajul navei" caught the second pass. Luck is not a classifier.
    """
    assert _theme_of('"Bordul liber" este :') == "constructia-ambarcatiunii"


def test_the_ships_sides_still_have_their_own_word():
    """`borduri` was dropped from the hull rule while repairing `bord liber`.

    Eighteen questions carry the word; the hull rule is where a stem that says
    nothing else about lights belongs.
    """
    assert _theme_of("Ce sunt bordurile?") == "constructia-ambarcatiunii"


def test_a_position_finding_stem_beats_a_buoyage_distractor():
    """The bank writes "determinarea punctului navei"; the literal missed it.

    With the stem unmatched, the distractor "geamanduri, balize, scondri"
    filed a coastal-navigation question under buoyage. The correct answer is
    "faruri". Same defect class as the R.N.D. question in the spec.
    """
    assert _themed(
        "Reperele costiere utilizate pentru determinarea punctului navei pot fi",
        ("geamanduri, balize, scondri", "alte nave aflate la ancoră", "faruri"),
        2,
    ) == "navigatie-harti-si-pozitie"


# Stage 4c: three meaning collisions, measured on all 603 questions. The
# water/rope sense of "curent" placed eight rope questions in meteorology
# (zero correct); "longitudin" matched "planul longitudinal" and dragged the
# hull skeleton into charts; "ceat" matched "mai înceată". The ninth rope
# move is the new volt(ele|elor) pattern's, not the curent removal's. The
# full effect of the repair is 16 moves, all read, all correct — pinned here
# so a future pattern edit that disturbs any of them fails loudly.
MOVED_AT_4C = {
    "Unde se păstrează parâmele pentru uzul curent?": "parame-noduri-ancore",
    "Voltele în cadrul lucrărilor de matelotaj sunt:": "parame-noduri-ancore",
    "Voltele se pot face la :": "parame-noduri-ancore",
    "Palancurile sunt:": "parame-noduri-ancore",
    "La ce folosește un palanc dublu?": "parame-noduri-ancore",
    "Vinciul este :": "parame-noduri-ancore",
    "Mandarul simplu este:": "parame-noduri-ancore",
    "Paramele de bumbac sunt folosite la confectionarea manevrelor curente?": "parame-noduri-ancore",
    "Parâmele de vegetale și sintetice sunt folosite la confecționarea manevrelor curente?": "parame-noduri-ancore",
    "Chila reprezintă:": "constructia-ambarcatiunii",
    "Coastele reprezintă elemente de construcție ale navei dispuse în planul:": "constructia-ambarcatiunii",
    "Elementele de osatura transversale, fixate pe chila la intervale egale , se numesc": "constructia-ambarcatiunii",
    "Elementele de osatură transversale, fixate pe chilă la intervale egale, se numesc": "constructia-ambarcatiunii",
    "Mişcarea transversală a unei nave în jurul unei axe longitudinale reprezintă:": "constructia-ambarcatiunii",
    "Varangele reprezintă elemente de construcție ale navei dispuse în planul:": "constructia-ambarcatiunii",
    "Cu cât viteza de deplasare este mai mare": "vocabular-si-principii",
}



def test_the_sixteen_corrected_placements_hold(bank):
    themed = {q["q"]: q["theme"] for q in bank}
    for stem, expected in MOVED_AT_4C.items():
        assert stem in themed, f"question no longer in the bank: {stem[:50]!r}"
        assert themed[stem] == expected, f"{stem[:50]!r} -> {themed[stem]}"


def test_the_rope_sense_of_curent_is_not_weather():
    assert _theme_of("Unde se păstrează parâmele pentru uzul curent?") \
        == "parame-noduri-ancore"


def test_the_longitudinal_plane_is_not_a_chart():
    assert _theme_of("Chila reprezintă:") == "constructia-ambarcatiunii"
    assert _theme_of("Latitudinea geografică este") == "navigatie-harti-si-pozitie"


def test_a_slow_turn_is_not_fog():
    """"mai înceată" contained "ceat"; a rudder question lived in fog for it."""
    assert _themed(
        "Cu cât viteza de deplasare este mai mare",
        (
            "presiunea apei asupra penei cârmei va fi mai mare, iar schimbarea direcţiei mai rapidă",
            "presiunea apei asupra penei cârmei va fi mai mică, iar schimbarea direcţiei mai înceată",
            "viteza nu influenţează rapiditatea schimbării direcţiei de navigaţie",
        ),
        0,
    ) != "vizibilitate-redusa"

# Stage 4e: the catch-all theme held questions that belong elsewhere — COLREG's
# traffic-separation rule, the steering gear, the lifting tackle, the Danube's
# schondri, the planks of the hull. Cleaning it moved twenty-nine questions in
# all, twenty-nine of them, each one read. Generated by replaying the old table against the shipped
# bank rather than typed from memory: at stage 4c the equivalent table shipped
# with ten of sixteen entries and nothing noticed.
MOVED_AT_4E = {
    # -> constructia-ambarcatiunii
    "Dama reprezintă": "constructia-ambarcatiunii",
    "Locul de îmbinare a filelor lăcrimare se numeşte": "constructia-ambarcatiunii",
    "Locul de îmbinare a filelor se numește": "constructia-ambarcatiunii",
    # -> geamanduri-si-balizaj
    "Jaloanele de aliniament indică :": "geamanduri-si-balizaj",
    "Şcondri pentru stânga au culoarea :": "geamanduri-si-balizaj",
    "Şcondrii pentru dreapta au culoarea :": "geamanduri-si-balizaj",
    # -> manevra-cu-motor
    "Care este manevra cea mai indicată pentru a se câştiga mai mult timp pentru aprecierea situaţiei, atunci când trebuie să se evite o coliziune?": "manevra-cu-motor",
    "Guvernarea clasică poate fi ajutată prin instalarea în corpul ambarcaţiunii de": "manevra-cu-motor",
    "Guvernarea poate fi îmbunătăţită de:": "manevra-cu-motor",
    "Instalatia de guvernare a navei reprezinta:": "manevra-cu-motor",
    "Instalatia de guvernare:": "manevra-cu-motor",
    "Instalaţia de guvernare se compune din": "manevra-cu-motor",
    "Instalația de guvernare a navei reprezintă:": "manevra-cu-motor",
    "Instalația de guvernare:": "manevra-cu-motor",
    # -> parame-noduri-ancore
    "Gruiul este:": "parame-noduri-ancore",
    "Părțile componente ale unei macarale sunt:": "parame-noduri-ancore",
    "Raiul unei macarale este:": "parame-noduri-ancore",
    # -> reguli-de-drum
    "Care sunt navele exceptate de la prevederile regulii referitoare la navigaţie în schemele de separare a traficului?": "reguli-de-drum",
    "Ce nave pot folosi zonele de navigaţie de trafic costier?": "reguli-de-drum",
    "Cum trebuie să navige navele care nu folosesc o schemă de separare a traficului?": "reguli-de-drum",
    "Cum trebuie să se angajeze o navă pentru intrarea sau ieşirea dintr-o schemă de separare a traficului?": "reguli-de-drum",
    "Cum trebuie să se navige în zone vecine cu extremităţile unei zone de separare a traficului?": "reguli-de-drum",
    "Când două nave se consideră în vedere?": "reguli-de-drum",
    "Când pot folosi navele zonele de navigaţie de trafic costier?": "reguli-de-drum",
    "Când una dintre nave poate fi observată vizual de către cealaltă navă, se consideră:": "reguli-de-drum",
    "Este permisă ancorarea în schemele de separare a traficului?": "reguli-de-drum",
    "Nava trebuie să navige pe banda de navigaţie corespunzătoare în direcţia generală a traficului şi să se îndepărteze,în măsura posibilului, de linia sau zona de separare a sensurilor de trafic atunci când trebuie să navige:": "reguli-de-drum",
    "Schemelor de separare a traficului li se aplică reglementările referitoare la schemele de separare a traficului, adoptate de:": "reguli-de-drum",
    "Zonele de navigaţie costieră pot fi folosite pentru traficul costier?": "reguli-de-drum",
}

def test_the_corrected_placements_hold(bank):
    assert len(MOVED_AT_4E) == 29, "the measured effect of the fix was 29 moves"
    themed = {q["q"]: q["theme"] for q in bank}
    for stem, expected in MOVED_AT_4E.items():
        assert stem in themed, f"question no longer in the bank: {stem[:50]!r}"
        assert themed[stem] == expected, f"{stem[:50]!r} -> {themed[stem]}"


def test_a_schondru_is_a_danube_mark_not_vocabulary():
    assert _theme_of("Şcondri pentru stânga au culoarea :") == "geamanduri-si-balizaj"


def test_the_steering_gear_is_manoeuvring_not_vocabulary():
    assert _theme_of("Instalația de guvernare:") == "manevra-cu-motor"


def test_the_hull_planks_are_construction_not_vocabulary():
    r"""Measured: the word boundary on `dama` is inert on today's bank — removing
    it fails nothing. It stays as a guard, and this test pins the placement
    rather than the boundary. What did bite was writing the boundary wrong:
    the first draft of this pattern carried a backspace character instead of
    \b, matched nothing, and moved none of the three hull questions. This
    docstring is raw for the same reason — unraw, it held a backspace too."""
    assert _theme_of("Dama reprezintă") == "constructia-ambarcatiunii"
