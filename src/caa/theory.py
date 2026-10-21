"""The theory cards: the rule, not the enumeration.

The statements are written in my words — the first non-verbatim content in
this application — and each carries the verbatim bank quotes it teaches.
The parent spec's honesty rule holds them together: a statement must answer
at least one official question, and one that answers nothing is ballast and
goes. Two audit rules enforce what can be enforced mechanically (the quotes
exist byte-exact, and belong to the card's own theme); what cannot — whether
the prose claims more than its quotes support — is the task reviewer's
single question.

Classes are derived, never declared: a statement inherits the union of its
source questions' classes, so a fact the bank only asks at class C never
shows at class D. The bank answers "Boturile sunt:" differently at the two
classes, and the two statements that pair produces are the proof this works.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from caa.normalize import normalize_key


@dataclass(frozen=True)
class Statement:
    """One rule, and the bank text that makes it true."""

    text: str  # Romanian: this reaches the interface
    sources: tuple[str, ...]
    # A drawing this rule can be seen in, written "kind:id" — the kind names
    # the catalogue, so the page dispatches without guessing which one an id
    # came from and a later kind is an addition rather than a rename. Only
    # drawings the bank already earns: nothing here is invented to illustrate.
    drawing: str | None = None


@dataclass(frozen=True)
class Card:
    theme: str
    statements: tuple[Statement, ...]


THEORY: Final[tuple[Card, ...]] = (
    Card(
        theme="constructia-ambarcatiunii",
        statements=(
            Statement(
                text=(
                    "Scheletul navei stă pe chilă — piesa fundamentală de rezistență, așezată în plan "
                    "diametral de la prova la pupa. Etrava îi prelungește chila în prova, etamboul în "
                    "pupa."
                ),
                sources=(
                    "Piesa fundamentala de rezistenta a oricărei nave, situata în plan "
                    "diametral , de la prova la pupa, se numește",
                    "Piesa de rezistenta situata in extremitatea prova, constituind o "
                    "prelungire a chilei , se numeşte",
                    "Piesa de rezistenta situata în extremitatea prova , constituind o "
                    "prelungire a chilei , se numește",
                    "prelungirea chilei în pupa",
                    "prelungirea chilei în prova",
                    "chila",
                ),
                drawing="schema:chila",
            ),
            Statement(
                text=(
                    "Cu fața spre prova, tribordul e la dreapta și babordul la stânga."
                ),
                sources=(
                    "Un observator care sta pe puntea navei cu fata spre prova , are în dreapta",
                    "Un observator care sta pe puntea navei cu fata spre prova , are în stânga",
                    "bordul tribord",
                    "bordul babord",
                ),
            ),
            Statement(
                text=(
                    "Pescajul se măsoară pe verticală, de la linia de bază la linia de plutire; navele "
                    "cu pescaj de cel puțin 1 m poartă scări de pescaj."
                ),
                sources=(
                    "distanța măsurată pe verticală, de la linia de bază până la linia de "
                    "plutire",
                    "Scări de pescaj poartă navele care au pescajul de cel puţin :",
                    "1 m",
                ),
            ),
            Statement(
                text=(
                    "Bordul liber e distanța de la planul de încărcare maximă până la puntea "
                    "superioară, în punctul ei cel mai de jos; flotabilitatea e proprietatea navei de a"
                    " pluti, la pescajul mediu determinat, cu încărcătura sa."
                ),
                sources=(
                    "Distanţa măsurată între planul de încărcare maximă şi suprafaţa punţii superioare "
                    "în punctul ei cel mai de jos, sau în lipsa punţii, punctul cel mai de jos al "
                    "părţii superioare a bordului fix",
                    "proprietatea navei de a pluti, la pescajul mediu determinat, cu încărcătura sa",
                ),
            ),
            Statement(
                text=(
                    "Învelișul exterior — bordajul — e alcătuit din file, rândurile de scânduri sau de "
                    "table; sabordurile sunt deschideri dreptunghiulare în bordaj, cu destinații "
                    "diferite."
                ),
                sources=(
                    "Fiecare rând de scânduri sau de table al învelișului ( bordajului ) "
                    "exterior se numește :",
                    "deschideri în bordaj de forma dreptunghiulara, cu destinații diferite.",
                    "fila",
                ),
            ),
            Statement(
                text=(
                    "Ramele se sprijină pe furcheți — piese metalice în formă de furcă — sau pe cuie de"
                    " strapazan bătute vertical în marginea bordajului; puntirile bărcii sunt în prova "
                    "și în pupa."
                ),
                sources=(
                    "piese metalice în forma de furca pe care se sprijină ramele ambarcațiunii",
                    "un cui de lemn bătut în marginea bordajului , vertical de care se prinde "
                    "rama",
                    "Unde se afla puntirile bărcii?",
                    "in prova și în pupa",
                ),
            ),
            Statement(
                text=(
                    "Orificiul rotund prin care trece axul cârmei — sau axul elicei — se numește "
                    "etambreu."
                ),
                sources=(
                    "Orificiul rotund prin care trece axul cârmei se numeşte",
                    "Orificiul rotund prin care trece axul cârmei se numește",
                    "Orificiul rotund prin care trece axul elicii de propulsie se numeşte",
                    "etambreul axului cârmei",
                    "etambreu",
                    "etambreul axului elicii",
                ),
            ),
            Statement(
                text=(
                    "Elicea abate pupa: la marș înainte în bordul pasului elicei, cu prova girând în "
                    "bordul opus; la marș înapoi invers."
                ),
                # The bow and stern thrusters used to be a third clause here. Stage
                # 4e's `guvernar` pattern moved that question to the manoeuvring
                # theme, where a steering aid belongs, and the fact went with it.
                sources=(
                    "în bordul pasului elicei, iar prova are tendinţa să gireze în bordul opus pasului "
                    "elicei",
                    "în bordul opus pasului elicei, iar prova va gira în bordul pasului elicei",
                ),
            ),
            Statement(
                text=(
                    "Chila e elementul de rezistență dispus în planul longitudinal al navei."
                ),
                sources=(
                    "element de rezistenta dispus în planul longitudinal al navei",
                ),
            ),
            Statement(
                text=(
                    "Coastele și varangele sunt elemente de construcție dispuse în planul "
                    "transversal. Coastele, mai exact, sunt elementele de osatură transversale "
                    "fixate pe chilă la intervale egale."
                ),
                sources=(
                    "Coastele reprezintă elemente de construcție ale navei dispuse în planul:",
                    "Varangele reprezintă elemente de construcție ale navei dispuse în planul:",
                    "Elementele de osatura transversale, fixate pe chila la intervale egale , se "
                    "numesc",
                    "Elementele de osatură transversale, fixate pe chilă la intervale egale, se "
                    "numesc",
                ),
                drawing="schema:osatura",
            ),
            Statement(
                text=(
                    "Ruliul e mișcarea transversală a navei în jurul axei longitudinale."
                ),
                sources=(
                    "Mişcarea transversală a unei nave în jurul unei axe longitudinale "
                    "reprezintă:",
                    "ruliu",
                ),
            ),
            Statement(
                text=(
                    "Locul unde se îmbină două file se numește cusătură."
                ),
                # That answer belongs to both stems, which is why the sourcing probe leaves
                # it alone; both questions are this statement's, so C and D are both right.
                sources=(
                    "Locul de îmbinare a filelor se numește",
                    "Locul de îmbinare a filelor lăcrimare se numeşte",
                    "cusătura",
                ),
            ),
            Statement(
                text=(
                    "Dama e scobitura din marginea superioară a bordajului, în care se așază rama."
                ),
                sources=(
                    "Dama reprezintă",
                    "o scobitura în marginea superioara a bordajului , în care se introduce "
                    "rama",
                ),
            ),
        ),
    ),
    Card(
        theme="prim-ajutor",
        statements=(
            Statement(
                text=(
                    "Ordinea măsurilor de prim ajutor: oprești hemoragia, faci respirație artificială, "
                    "masaj cardiac, pansezi rănile, imobilizezi fracturile. La mai multe victime, întâi"
                    " cea în starea cea mai gravă."
                ),
                sources=(
                    "oprirea hemoragiei, respirație artificială, masaj cardiac, pansarea rănilor, "
                    "imobilizarea fracturilor",
                    "victimei în starea cea mai gravă",
                ),
            ),
            Statement(
                text=(
                    "Primul gest după o coliziune: degajezi căile respiratorii și asiguri respirația — "
                    "pe loc, cât mai urgent. Obturarea vine de la corpi străini intrați în nasul sau "
                    "gura victimei."
                ),
                sources=(
                    "degajarea căilor respiratorii și asigurarea funcției respiratorii",
                    "la locul producerii coliziunii, cât mai urgent",
                    "intrarea unor corpi străini în nasul sau gura victimei",
                ),
            ),
            Statement(
                text=(
                    "La victima fără cunoștință verifici întâi pulsul și respirația; pulsul se caută "
                    "lângă mărul lui Adam, în scobitura dintre trahee și mușchii gâtului."
                ),
                sources=(
                    "se verifică existența pulsului și a respirației",
                    "lângă mărul lui Adam, în scobitura dintre trahee și mușchii gâtului",
                ),
            ),
            Statement(
                text=(
                    "Masajul cardio-respirator se face numai victimelor fără puls și fără respirație, "
                    "cel mult 10–15 minute; când pulsul revine, încetezi compresiile și duci victima la"
                    " spital."
                ),
                sources=(
                    "care nu au puls și nu respiră",
                    "10 - 15 min",
                    "încetați compresiile exterioare ale pieptului",
                    "luați măsuri pentru transportarea ei la spital",
                ),
            ),
            Statement(
                text=(
                    "Victima cu puls dar fără respirație primește respirație artificială; dacă gura "
                    "rămâne încleștată, se face prin nările victimei."
                ),
                sources=(
                    "prin executarea respirației artificiale",
                    "prin nările victimei",
                ),
            ),
            Statement(
                text=(
                    "La orice rană cu hemoragie, întâi oprești sângerarea — cea mai periculoasă e "
                    "pierderea rapidă de sânge. Zona rănită se ține mai sus decât corpul, iar cine a "
                    "pierdut mult sânge stă cu picioarele mai sus; transportul se face imediat după "
                    "oprirea hemoragiei."
                ),
                sources=(
                    "oprirea hemoragiei",
                    "hemoragia care determină o pierdere rapidă a sângelui",
                    "astfel încât zona să fie mai sus decât nivelul corpului",
                    "cu picioarele situate mai sus decât restul corpului",
                    "imediat după oprirea hemoragiei",
                ),
            ),
            Statement(
                text=(
                    "Hemoragiile la trunchi și cap se opresc cu comprese sterile și pansamente "
                    "compresive; cea nazală — strângând ambele nări cu degetele, aproximativ 5–10 "
                    "minute."
                ),
                sources=(
                    "compreselor sterile și a pansamentelor compresive",
                    "își strânge ambele nări cu degetele timp de aproximativ 5-10 minute",
                ),
            ),
            Statement(
                text=(
                    "Garoul se aplică la hemoragii arteriale, deasupra plăgii, cel mult 2 ore, cu bilet"
                    " care notează ora și minutul aplicării."
                ),
                sources=(
                    "deasupra plăgii",
                    "maximum 2 ore",
                    "ora și minutul aplicării garoului",
                ),
            ),
            Statement(
                text=(
                    "Corpii străini nu se extrag din plagă — riști să agravezi. Dezinfectezi cu apă "
                    "oxigenată sau iod, pansamentul poartă compresă de tifon steril, iar la plăgi "
                    "tăiate oprești hemoragia și duci victima la spital."
                ),
                sources=(
                    "renunțăm la asemenea manevră întrucât riscăm să agravăm starea victimei",
                    "apă oxigenată sau iod",
                    "dezinfectarea rănilor",
                    "o compresă de tifon steril",
                    "se oprește hemoragia și se transportă victima la spital",
                ),
            ),
            Statement(
                text=(
                    "Bandajul acoperă rana, împiedică intrarea corpilor străini și poate opri "
                    "hemoragia."
                ),
                sources=(
                    "acoperă rănile, eventual opresc hemoragiile",
                    "să împiedice intrarea corpilor străini în rană",
                ),
            ),
            Statement(
                text=(
                    "Fractura de membru se recunoaște după poziția nefirească și mișcarea nenaturală; "
                    "la fractura deschisă pielea e străpunsă și se vede osul."
                ),
                sources=(
                    "poziția nefirească a membrului respectiv miscarea nenaturală",
                    "prin mișcarea nenaturală a membrului fracturat",
                    "pielea este străpunsă în zona fracturii și se vede osul",
                ),
            ),
            Statement(
                text=(
                    "Fractura se imobilizează ca să eviți complicațiile: atela — rigidă și destul de "
                    "lungă cât să cuprindă articulațiile de deasupra și de dedesubt — sau, în lipsă, "
                    "eșarfe și triunghiuri de pânză."
                ),
                sources=(
                    "imobilizați zona fracturată",
                    "cât mai rigidă și suficient de lungă pentru a cuprinde articulațiile superioară și"
                    " inferioară a membrului fracturat",
                    "cu atele, chiar improvizate",
                    "cu eșarfe și triunghiuri de pânză",
                ),
            ),
            Statement(
                text=(
                    "Cazuri anume: laba piciorului se imobilizează de la degete până la genunchi; la "
                    "claviculă, brațul se suspendă într-o eșarfă legată de gât; la entorsa gleznei — "
                    "bandaj elastic strâns, eventual și gheață."
                ),
                sources=(
                    "cu atele sau bandaj, cât mai rigide, de la degete până la genunchi",
                    "suspendați brațul într-o eșarfă sau chingă delată de gât",
                    "se aplică un bandaj elastic strâns, eventual se aplică și gheață",
                ),
            ),
            Statement(
                text=(
                    "La leziuni ale coloanei vertebrale, dacă nu există un alt pericol, nu miști "
                    "victima din poziția în care se află până la sosirea serviciilor de urgență; la "
                    "traumatism de cap: bandajezi plăgile, degajezi căile respiratorii, așezi victima "
                    "pe o suprafață plană."
                ),
                sources=(
                    "dacă nu există un alt pericol, nu se mișcă accidentatul din poziția în care se "
                    "află până la sosirea serviciilor de urgență",
                    "dacă este posibil, victima nu trebuie mișcată până la sosirea medicului",
                    "bandajarea plăgilor, degajarea căilor respiratorii, așezarea victimei pe o "
                    "suprafață plană",
                ),
            ),
            Statement(
                text=(
                    "Scoți victimele fără să le agravezi leziunile, iar transportul se poate face cu "
                    "orice vehicul dacă starea permite; arsurile multiple pe cap și membre cer "
                    "transport imediat la o unitate medicală. Primul ajutor se acordă până la sosirea "
                    "ambulanței."
                ),
                sources=(
                    "să nu le agravați leziunile",
                    "Cu orice vehicul, dacă situația victimei permite acest lucru",
                    "trebuie să fie transportată imediat la o unitate medicală",
                    "acordarea primului ajutor până la sosirea cadrelor de pe ambulanță",
                ),
            ),
        ),
    ),
    Card(
        theme="parame-noduri-ancore",
        statements=(
            Statement(
                text=(
                    "Parâma crește din fir — elementul de bază: mai multe fire răsucite dau sfilata, "
                    "trei șuvițe răsucite dau parâma simplă (lanțana), iar parâma intrată în compunerea"
                    " alteia mai groase se numește cordon. Structura urcă, în ordine, de la fir la "
                    "sfilată, șuviță, lanțană, cordon și garlin."
                ),
                sources=(
                    "Care este elementul de baza la structura oricărui tip de parâma",
                    "o sfilata",
                    "parâmă simplă sau lanƫanã",
                    "cordon",
                    "firul, sfilata, șuvița, lanțana, cordonul, garlinul.",
                ),
            ),
            Statement(
                text=(
                    "Fabricarea începe cu bătaia — îndepărtarea materialelor străine — apoi "
                    "pieptănarea, care separă firele și lasă stupa, și toarcerea, răsucirea firelor "
                    "spre dreapta."
                ),
                sources=(
                    "îndepărtarea materialelor străine din materia prima",
                    "separarea firelor după lungime și eliberarea produsului secundar, numit stupa",
                    "operațiunea prin care firele sunt răsucite spre dreapta",
                ),
            ),
            Statement(
                text=(
                    "După material: parâme vegetale (cânepă, in, bumbac, iută — sizalul e din frunze de"
                    " cactus), sintetice (capron, relon, nailon, polipropilenă) și metalice (sârmă de "
                    "oțel zincat de 0,2–0,6 mm, cu inimă vegetală pentru protecție)."
                ),
                sources=(
                    "din fire de cânepă, in, bumbac, iuta",
                    "parame vegetale confectionate din frunze de cactus",
                    "din fire de capron, relon, nailon, polipropilena",
                    "din fire de sarma de otel zincat cu grosimi de 0,2-0,6mm",
                    "parâmele metalice",
                    "parâmele vegetale",
                ),
            ),
            Statement(
                text=(
                    "Cânepa merge la manevre curente, bărci și arboradă — dar nu la saulele "
                    "ambarcațiunilor sport, unde se folosesc bumbacul și sinteticele; baloanele și "
                    "paietele se fac numai din parâme uzate."
                ),
                sources=(
                    "la confecționarea manevrelor curente, la bărci și la arborada",
                    "Parâmele de cânepă sunt folosite la confecționarea saulelor la ambarcațiuni sport "
                    "și de agrement?",
                    "Paramele de bumbac sunt folosite la confectionarea saulelor la ambarcatiuni sport "
                    "si de agrement ?",
                    "Parâmele sintetice sunt folosite la confecționarea saulelor la ambarcațiuni sport "
                    "și de agrement ?",
                    "Parâmele vegetale și sintetice uzate sunt folosite la confecționarea baloanelor și"
                    " paietelor?",
                    "Parâmele vegetale și sintetice sunt folosite la confecționarea baloanelor și "
                    "paietelor?",
                ),
            ),
            Statement(
                text=(
                    "Caracteristicile parâmei: grosimea (circumferința, la vegetale și sintetice), "
                    "greutatea (kilograme pe metru liniar), rezistența (sarcina la care se rupe), "
                    "flexibilitatea (îndoirea fără schimbarea structurii) și elasticitatea."
                ),
                sources=(
                    "grosimea, greutatea, rezistenta, flexibilitatea, elasticitatea",
                    "prin măsurarea circumferinței ei",
                    "grosimea",
                    "prin măsurarea greutății în kilograme a unui metru liniar din parâma respectiva",
                    "rezistența parâmei",
                    "flexibilitatea parâmei",
                ),
            ),
            Statement(
                text=(
                    "Dimensiunile cu nume: merlinul — subțire, pentru înfășurări și patronări; lusinul "
                    "— mai fin decât merlinul; saula — 15–40 mm, pentru bandulă sau pavilion; garlinul "
                    "— 100–620 mm, pentru legare sau remorcare; grandeea — 25–120 mm."
                ),
                sources=(
                    "o parâmă subțire confecționată din trei sfilate, folosită la înfășurare, legături "
                    "și patronări",
                    "o lantana subtire de 7-8mm folosita la infasurari si patronari de parame groase",
                    "o lanțană mai fină decât merlinul, folosită la patronări și înfășurări fine",
                    "o parâmă cu grosimea de 15-40mm folosită la bandulă sau la pavilion",
                    "o parâmă cu grosimea de 100-620mm folosită la legarea sau remorcarea navei",
                    "o lanƫanã cu circumferința de 25-120mm cusuta pe marginea unei vele sau tenzi "
                    "pentru a o întări.",
                    "o lantana cu circumferinta de 25-120mm",
                ),
            ),
            Statement(
                text=(
                    "La primirea parâmelor vegetale verifici culoarea și mirosul; umezeala le "
                    "alterează. Patronarea înfășoară capetele ca să nu se destrame."
                ),
                sources=(
                    "culoarea și mirosul",
                    "Umezeala alterează parâmele vegetale?",
                    "înfășurarea capetelor ca sa nu se destrame",
                ),
            ),
            Statement(
                text=(
                    "Păstrarea parâmelor vegetale se face ferindu-le de umezeală și de radiația solară."
                ),
                sources=(
                    "umezeala și radiația solara",
                ),
            ),
            Statement(
                text=(
                    "Păstrarea parâmelor vegetale se face ferindu-le de umezeală."
                ),
                sources=(
                    "umezeala",
                ),
            ),
            Statement(
                text=(
                    "Matisirea împreunează două capete de parâmă sau face o gașă; rodanțele sunt "
                    "apărătoarele gașelor, iar sbirul e un inel de parâmă matisit, de prins un palanc "
                    "pe o parâmă sau pe un scondru."
                ),
                sources=(
                    "împreunarea a doua capete de parâma sau realizarea unei gașe",
                    "Apărătoarele gașelor mici la parâme se numesc",
                    "apărătoare ale gașelor",
                    "inel de parâmă confecționat prin matisire care servește la prinderea unui "
                    "palanc pe o parâmă sau pe un scondru",
                    "rodanțe",
                ),
            ),
            Statement(
                text=(
                    "Nodul bun se face ușor, se desface ușor, e rezistent și nu deteriorează parâma."
                ),
                sources=(
                    "usor de facut,usor de desfacut,rezistent,nu deterioreaza parama",
                ),
            ),
            Statement(
                text=(
                    "Nodurile de împreunare leagă două capete de grosimi apropiate — latul, pescarul, "
                    "văcarul; cele de legătură fixează un capăt — al ancorei, scaunul simplu (folosit "
                    "la legarea ambarcațiunii), scota; cele de cârlig prind parâma de cârligul "
                    "macaralei — gura de știucă; iar capelatura, schela, bandula și piciorul de câine "
                    "sunt noduri speciale."
                ),
                sources=(
                    "nodurile folosite la împreunarea a doua capete de parâmă de grosimi "
                    "aproximativ egale",
                    "nodurile folosite la fixarea unui capăt de parâmă.",
                    "nodurile folosite la legarea unui capăt de parâmă de cârligul unei "
                    "macarale",
                    "nodul de bandula, nodul picior de câine",
                    "Nodul lat este un nod:",
                    "Nodul de pescar este un nod:",
                    "Nodul de văcar este un nod:",
                    "Nodul de ancora este un nod:",
                    "Nodul de scaun simplu este un nod:",
                    "legarea ambarcațiunii de instalațiile",
                    "Nodul de scota este un nod:",
                    "Nodul gura de știucă este un nod:",
                    "Nodul de capelatura este un nod:",
                    "Nodul de schelă este un nod:",
                    "de cârlig",
                ),
            ),
            Statement(
                text=(
                    "Volta fixează parâma de punctele de legare ale bordului: babalele — fontă sau "
                    "oțel, simple ori duble — iau voltele; tacheții, mai mici, le țin locul la navele "
                    "mici și la parâmele subțiri."
                ),
                sources=(
                    "legăturile prin care parâmele se fixează la dispozitivele de legare existente la "
                    "bord",
                    "luarea voltelor cu parâme",
                    "Piesele metalice mai mici , care servesc la luarea voltelor cu parâme mai subțiri "
                    "se numesc",
                    "La navele mici locul babalelor poate fi luat de",
                ),
            ),
            Statement(
                text=(
                    "Boturile sunt capete de parâmă vegetală sau de lanț, fixate solid în punte, pentru"
                    " fixarea provizorie a unei parâme."
                ),
                sources=(
                    "capete de parâmă vegetala sau de lanț fixate cu unul din capete solid în punte "
                    "pentru fixarea provizorie a unei parâme.",
                ),
            ),
            Statement(
                text=(
                    "Boturile sunt știfturile de siguranță ale unei chei de împreunare."
                ),
                sources=(
                    "stifturi de siguranta ale unei chei de impreunare.",
                ),
            ),
            Statement(
                text=(
                    "Parâma se ghidează prin urechi — dispozitive speciale fixate în bordaj sau în "
                    "punte — și prin turnicheți, piesele metalice de ghidare cu minimum de frecare."
                ),
                sources=(
                    "Dispozitivele de construcție speciala , fixate în bordaj , cu rol de ghidare a "
                    "parâmei se numesc",
                    "Dispozitivele de construcție speciala , fixate în punte , cu rol de ghidare a "
                    "parâmei se numesc",
                    "turnichetii sunt piese metalice de ghidarea parâmelor, cu minimum de frecare",
                ),
            ),
            Statement(
                text=(
                    "Barbetele sunt capete de parâmă fixate la prova și la pupa bărcii, pentru legare "
                    "sau remorcat; legăturile ambarcațiunii sunt parâma prova și parâma pupa."
                ),
                sources=(
                    "pentru legare sau remorcat",
                    "capete de parâmă fixate la prova și la pupa bărcii.",
                    "parâma prova şi pupa",
                ),
            ),
            Statement(
                text=(
                    "Macaralele sunt dispozitive de tip scripete, pentru ridicat greutăți sau schimbat "
                    "direcția de tracțiune; cabestanul e mecanismul de punte cu ax vertical, acționat "
                    "manual sau electro-mecanic, pentru virarea ancorei sau manevrarea parâmelor."
                ),
                sources=(
                    "dispozitive de genul scripeților, folosite pentru ridicarea unor greutăți sau "
                    "pentru schimbarea direcției de tracțiune a unei parâme",
                    "Mecanism de punte, pentru virarea ancorei sau manevrarea parâmelor, acționat "
                    "manual sau electro-mecanic, cu ax vertical",
                ),
            ),
            Statement(
                text=(
                    "Ancora se compune din fus, brațe cu gheare, diamant — locul unde brațele se "
                    "împreunează cu fusul — plus inel și traversă."
                ),
                sources=(
                    "fus, diamant, brațe și gheare.",
                    "locul de împreunare a brațelor cu fusul",
                    "brațe , fus , diamant , inel , traversa",
                ),
            ),
            Statement(
                text=(
                    "Tipuri de ancoră: Amiralitate — cu fus nearticulat; Hall — cu fus articulat; "
                    "ancora cu patru brațe se folosește la fluviu și pe ape interioare."
                ),
                sources=(
                    "cu fus nearticulat",
                    "cu fus articulat.",
                    "la fluviu și ape interioare",
                ),
            ),
            Statement(
                text=(
                    "Instalația de ancorare fixează nava într-o poziție determinată, în afara căii "
                    "navigabile; din ea fac parte ancora, nara de ancoră și ghidajele de lanț, stopa de"
                    " lanț, vinciul și nara de punte."
                ),
                sources=(
                    "instalația cu care se realizează fixarea într-o poziție bine determinată a navei.",
                    "reprezintă un ansamblu de piese și mecanisme destinate pentru menținerea navei "
                    "într-o zona în afara caii navigabile, sau într-o poziție stabila, de către "
                    "comandantul navei.",
                    "ancora, nara de ancora și ghidajele de lanț.",
                    "stopa de lanț, vinciul de ancoră și nara de punte.",
                ),
            ),
            Statement(
                text=(
                    "La lanțul de ancoră, calibrul e grosimea măsurată la mijlocul zalei; podul zalei "
                    "mărește rezistența la întindere și împiedică încurcarea; vârtejul leagă cheia de "
                    "împreunare a ancorei de cea a lanțului."
                ),
                sources=(
                    "grosimea la mijlocul zalei",
                    "mărește rezistenta la întindere și împiedica încurcarea",
                    "piesa de legătură inte cheia de împreunare a ancorei și cea a lanțului de ancora",
                ),
            ),
            Statement(
                text=(
                    "La ancorare, lungimea parâmei sau lanțului e de 3–5 ori adâncimea; dacă ancora se "
                    "târăște pe fund, grapează. Locul bun de ancorare e ferit de curenți, valuri și "
                    "vânt, permite plecarea rapidă oricând și nu deranjează alte ambarcațiuni."
                ),
                sources=(
                    "lungimea parâmei/lanţului la ancoră trebuie să fie de 3-5 ori adâncimea",
                    "ancora se târăște pe fundul apei",
                    "să fie un loc ferit de efectele curenţilor, valurilor şi vântului",
                    "să permită plecarea rapidă a navei de la ancoră, în orice condiţii, ziua sau "
                    "noaptea",
                    "să permită o ancorare-plecare uşoară, fără să deranjeze alte ambarcaţiuni",
                ),
            ),
            Statement(
                text=(
                    "La remorcare, lungimea remorcii se alege astfel încât nava remorcată să nu suporte"
                    " curentul respins de elicea remorcherului."
                ),
                sources=(
                    "se va alege astfel încât nava remorcată să nu suporte curentul respins de elicea "
                    "navei remorcher",
                ),
            ),
            Statement(
                text=(
                    "Armamentul de navigație al bărcii cuprinde compasul de barcă; la navigație și "
                    "semnalizare intră pistolul de semnalizare, pavilioanele de semnalizare cu brațele "
                    "și bastonul de pavilion."
                ),
                sources=(
                    "compas de barca",
                    "pistol de semnalizare",
                    "pavilioane de semnalizare cu brațele.",
                    "bastonul de pavilion cu pavilionul",
                ),
            ),
            Statement(
                text=(
                    "Armamentul de vitalitate: ghiordelul, ispolul, dopurile de lemn, penele, cuiele și"
                    " câlții, trusa cu scule de marangozerie."
                ),
                sources=(
                    "ghiordelul",
                    "ispolul",
                    "dopuri de lemn",
                    "pene, cuie, câlți",
                    "trusa cu scule de marangozerie",
                ),
            ),
            Statement(
                text=(
                    "Palancurile sunt dispozitive compuse din una sau mai multe macarale, cu câte "
                    "unul sau mai multe raiuri, prin care trece o parâmă numită curent; palancul "
                    "dublu servește la ridicarea greutăților și la instalațiile de gruie."
                ),
                sources=(
                    "dispozitive compuse din una sau mai multe macarale cu cate unul sau mai multe "
                    "raiuri, prin care se trece o parâmă denumită curent",
                    "pentru ridicarea greutăților și la instalațiile de gruie.",
                ),
            ),
            Statement(
                text=(
                    "Mandarul simplu e un dispozitiv de ridicat alcătuit dintr-o macara fixă prin "
                    "care trece o parâmă."
                ),
                sources=(
                    "dispozitiv de ridicat alcătuit dintr-o macara fixa, prin care trece o parâmă",
                ),
            ),
            Statement(
                text=(
                    "Vinciul e un mecanism de ridicat sau tras, manual sau acționat mecanic, cu ax "
                    "orizontal, folosit la bord la virarea ancorei, a manevrelor unei bigi, a "
                    "curenților palancurilor și ai gruielor de barcă."
                ),
                sources=(
                    "mecanism de ridicat sau tras, manual sau acționat mecanic, cu ax orizontal "
                    "utilizat la bord pentru virarea ancorei, manevrelor unei bigi, a curenților "
                    "palancurilor gruelor de barcă",
                ),
            ),
            Statement(
                text=(
                    "Voltele sunt legăturile prin care parâmele se fixează la dispozitivele "
                    "speciale de legare; se pot face la babale, tacheți și cavile."
                ),
                sources=(
                    "legături prin care se fixează parâmele la dispozitive speciale de legare",
                    "baba, tacheti, cavile",
                ),
            ),
            Statement(
                text=(
                    "Parâmele pentru uzul curent se păstrează pe punte."
                ),
                sources=(
                    "Unde se păstrează parâmele pentru uzul curent?",
                    "pe punte",
                ),
            ),
            Statement(
                text=(
                    "Manevrele curente se confecționează din parâme vegetale și sintetice."
                ),
                sources=(
                    "Parâmele de vegetale și sintetice sunt folosite la confecționarea manevrelor "
                    "curente?",
                ),
            ),
            Statement(
                text=(
                    "Parâmele de bumbac nu se folosesc la confecționarea manevrelor curente."
                ),
                sources=(
                    "Paramele de bumbac sunt folosite la confectionarea manevrelor curente?",
                ),
            ),
            Statement(
                text=(
                    "Macaraua se compune din căpățână, rai și sbir; raiul e rola care se învârte liber în "
                    "jurul unui ax."
                ),
                sources=(
                    "Părțile componente ale unei macarale sunt:",
                    "căpățâna, raiul, sbirul",
                    "Raiul unei macarale este:",
                    "o rola care se învârtește liber în jurul unui ax",
                ),
            ),
            Statement(
                text=(
                    "Gruiul e un dispozitiv curbat de ridicat greutăți și bărci, cu rază de acțiune și "
                    "capacitate de ridicare mai mici decât ale bigilor și granicelor."
                ),
                sources=(
                    "Gruiul este:",
                    "dispozitiv de ridicare a greutatilor și a bãrcilor având o formã curbatã,o "
                    "razã relativ micã de actiune comparativ cu bigile și granicele și o "
                    "capacitate de ridicare scãzutã",
                ),
            ),
        ),
    ),
    Card(
        theme="geamanduri-si-balizaj",
        statements=(
            Statement(
                text=(
                    "Marcajele laterale semnalizează limitele laterale ale șenalului navigabil."
                ),
                sources=(
                    "Limitele laterale ale șenalului navigabil",
                ),
            ),
            Statement(
                text=(
                    "În regiunea A regula „verde la tribord, roșu la babord” se aplică în sensul de "
                    "larg către coastă. În regiunea B culorile sunt inversate: tribord roșu, babord "
                    "verde."
                ),
                sources=(
                    "in sensul de larg către coastă;",
                    "tribord-roșu, babord-verde",
                ),
            ),
            Statement(
                text=(
                    "Pe tot parcursul navigabil al fluviului, șenalul e balizat după sistemul lateral."
                ),
                sources=(
                    "Lateral",
                ),
            ),
            Statement(
                text=(
                    "Pe Dunăre, geamandurile verzi cu lumină verde intermitentă balizează partea stângă"
                    " a șenalului și pericolele de la malul stâng; cele roșii cu lumină roșie "
                    "intermitentă marchează limitele șenalului și direcția sa, balizând partea dreaptă "
                    "și pericolele de la malul drept."
                ),
                sources=(
                    "Geamandurile de culoare verde cu lumină verde intermitentă balizează :",
                    "Partea stângă a şenalului şi pericolele de la malul stâng",
                    "Ce semnificaţie au geamandurile de culoare roşie cu lumina roşie intermitentă ?",
                    "Marchează limitele şenalului şi direcţia sa, balizând partea dreaptă a şenalului "
                    "şi pericolele de la malul drept",
                ),
            ),
            Statement(
                text=(
                    "Geamandurile, școndrii și jaloanele pentru dreapta sau pentru stânga marchează "
                    "limita șenalului și pericolele de la malul respectiv; cele de joncțiune și de "
                    "bifurcație semnalizează joncțiunea și bifurcația șenalului și, în plus, balizează "
                    "pericolele de navigație din șenal."
                ),
                sources=(
                    "Limita şenalului şi pericolele de la malul respectiv",
                    "Semnalizează joncţiunea şi bifurcaţia şenalului şi în afară de aceasta balizează "
                    "pericolele de navigaţie din şenal",
                ),
            ),
            Statement(
                text=(
                    "Cine constată avarierea unei instalații de semnalizare — o lumină stinsă, o "
                    "geamandură deplasată, un semnal distrus — anunță fără întârziere căpitănia de port"
                    " cea mai apropiată."
                ),
                sources=(
                    "Orice conducător de navă, dacă constată avarierea unei instalaţii de semnalizare "
                    "(stingerea unei lumini, deplasarea unei geamanduri, distrugerea unui semnal etc.) "
                    "este obligat :",
                    "Să anunţe fără întârziere căpitănia de port cea mai apropiată asupra avarierii "
                    "instalaţiei de semnalizare respectivă",
                ),
            ),
            Statement(
                text=(
                    "Plasele și uneltele de pescuit întinse ziua în apropierea șenalului se "
                    "semnalizează cu flotoare sau pavilioane galbene, în număr suficient cât să le "
                    "arate poziția."
                ),
                sources=(
                    "Flotoare sau pavilioane galbene, în număr suficient pentru a indica poziţia lor",
                ),
            ),
            Statement(
                text=(
                    "Pe Dunăre, școndrii pentru dreapta sunt roșii și cei pentru stânga verzi, iar "
                    "jaloanele de aliniament indică axa traversării."
                ),
                # The colours live only in the answers, and each answer names exactly one
                # question in this theme, so both halves are cited.
                sources=(
                    "Şcondrii pentru dreapta au culoarea :",
                    "Roşie",
                    "Şcondri pentru stânga au culoarea :",
                    "Verde",
                    "Jaloanele de aliniament indică :",
                    "Axa traversării",
                ),
            ),
        ),
    ),
    Card(
        theme="semnale-sonore",
        statements=(
            Statement(
                text=(
                    "Sunetul scurt durează aproximativ o secundă, iar sunetul lung 4–6 secunde."
                ),
                sources=(
                    "un sunet a cărui durată este de aproximativ o secundă.",
                    "un sunet a cărui durată este de 4-6 secunde.",
                ),
            ),
            Statement(
                text=(
                    "Sunetul scurt durează circa 1 secundă, iar sunetul lung circa 4 secunde."
                ),
                sources=(
                    "Circa 1 secundă",
                    "Circa 4 secunde",
                ),
            ),
            Statement(
                text=(
                    "Semnalele de manevră: un sunet scurt — vin la tribord; două sunete scurte — vin la"
                    " babord; trei sunete scurte — am mașina înapoi."
                ),
                sources=(
                    "un sunet scurt.",
                    "două sunete scurte.",
                    "trei sunete scurte.",
                ),
            ),
            Statement(
                text=(
                    "Semnalele sonore de manevră se emit când navele se văd unele pe altele și se pot "
                    "completa cu semnale luminoase."
                ),
                sources=(
                    "când navele se văd unele pe altele.",
                    "cu semnale luminoase.",
                ),
            ),
            Statement(
                text=(
                    "Nava care își dă acordul la depășire răspunde cu un sunet lung, unul scurt, un "
                    "sunet lung și unul scurt — litera C."
                ),
                sources=(
                    "un sunet lung, un sunet scurt, un sunet lung şi unul scurt (litera C)",
                ),
            ),
            Statement(
                text=(
                    "O serie de sunete foarte scurte înseamnă cel puțin 6 sunete de circa un sfert de "
                    "secundă fiecare, la interval de circa un sfert de secundă, și semnalizează pericol"
                    " iminent de abordaj."
                ),
                sources=(
                    "O serie de cel puţin 6 sunete cu o durată de circa ¼ de secundă fiecare",
                    "circa ¼ s",
                    "Este în pericol iminent de abordaj",
                ),
            ),
            Statement(
                text=(
                    "O serie de bătăi de clopot înseamnă două lovituri de clopot."
                ),
                sources=(
                    "Înseamnă două lovituri de clopot",
                ),
            ),
            Statement(
                text=(
                    "Nava în pericol care cere ajutor poate emite semnale sonore: o serie de sunete de "
                    "clopot sau sunete lungi cu alte mijloace acustice, repetate."
                ),
                sources=(
                    "Atunci când o navă este în pericol şi vrea să ceară ajutor, poate emite "
                    "semnale sonore ?",
                    "“O serie de sunete de clopot” sau “sunete lungi” cu alte mijloace acustice "
                    "repetate",
                    "Da",
                ),
            ),
            Statement(
                text=(
                    "Nava între 12 și 100 m poartă un fluier și un clopot. Sub 12 m nu e obligată să "
                    "aibă echipamentul prescris, dar trebuie să poată emite un semnal sonor eficace "
                    "prin alt mijloc."
                ),
                sources=(
                    "un fluier şi un clopot.",
                    "navele sub 12 m lungime nu sunt obligate să aibă la bord echipamentul de "
                    "semnalizare prescris, în lipsa lui să fie dotate cu un alt mijloc de emitere a "
                    "unui semnal sonor eficace.",
                ),
            ),
            Statement(
                text=(
                    "La apropierea de un cot dintr-un șenal sau o cale de acces îngustă, nava emite un "
                    "semnal lung și navigă cu prudență și vigilență."
                ),
                sources=(
                    "să emită un semnal lung şi să navige cu prudenţă şi vigilenţă.",
                ),
            ),
        ),
    ),
    Card(
        theme="lumini-situatii-speciale",
        statements=(
            Statement(
                text=(
                    "Lumina de remorcaj trebuie să se vadă la 2 Mm pentru navele sub 12 m și pentru "
                    "cele între 12 și 50 m, și la 3 Mm pentru cele peste 50 m."
                ),
                sources=(
                    "La ce distanţă trebuie să se vadă lumina de remorcaj pentru navele cu o lungime "
                    "mai mică de 12 m?",
                    "La ce distanţă trebuie să se vadă lumina de remorcaj pentru navele cu o lungime "
                    "între 12 şi 50 m?",
                    "La ce distanţă trebuie să se vadă lumina de remorcaj pentru navele cu o lungime "
                    "mai mare de 50 m?",
                ),
            ),
            Statement(
                text=(
                    "Lumina albă pe tot orizontul a unei nave sau a unui obiect de formă nedefinită, "
                    "parțial în imersiune, care e remorcat, trebuie să se vadă la 3 Mm."
                ),
                sources=(
                    "La ce distanţă trebuie să se vadă lumina albă vizibilă pe tot orizontul, a unei "
                    "nave sau obiect de formă nedefinită, parţial în imersiune, care este remorcat?",
                ),
            ),
            Statement(
                text=(
                    "Navele sub 7 m nu sunt obligate să poarte lumini de navă ancorată, în afară de "
                    "cazul când ancorează într-un canal navigabil îngust, într-o pasă de intrare în "
                    "port sau într-o radă de ancorare."
                ),
                sources=(
                    "când sunt la ancoră dar nu într-un canal navigabil îngust, pase de intrare în port"
                    " sau rade de ancorare.",
                ),
            ),
            Statement(
                text=(
                    "Navelor eșuate sub 12 m nu li se cer luminile și semnele speciale de navă eșuată; "
                    "unde sunt cerute, se instalează în locul cel mai vizibil."
                ),
                sources=(
                    "nave cu lungime mai mică de 12 m.",
                    "în locul cel mai vizibil.",
                ),
            ),
            Statement(
                text=(
                    "Nava cu pernă de aer în exploatare fără pescaj poartă luminile unei nave cu "
                    "propulsie mecanică în marș, plus o lumină galbenă cu sclipiri vizibilă pe tot "
                    "orizontul."
                ),
                sources=(
                    "luminile unei nave cu propulsie mecanică în marş plus o lumină galbenă cu sclipiri"
                    " vizibilă pe tot orizontul.",
                ),
            ),
            Statement(
                text=(
                    "Ambarcațiunile mici autopropulsate de până la 20 m care remorchează sau duc în "
                    "cuplu alte ambarcațiuni mici poartă luminile unei ambarcațiuni mici autopropulsate"
                    " care navigă izolat."
                ),
                sources=(
                    "Luminile unei ambarcaţiuni mici autopropulsate ce navigă izolat şi a cărei lungime"
                    " nu depăşeşte 20 m",
                ),
            ),
        ),
    ),
    Card(
        theme="lumini-propulsie-mecanica",
        statements=(
            Statement(
                text=(
                    "Luminile se poartă de la apusul la răsăritul soarelui; semnele, pe timpul zilei. "
                    "Regulile despre lumini și semne se respectă pe orice vreme, iar luminile mai pot "
                    "fi purtate și ziua pe vizibilitate redusă sau ori de câte ori măsura e necesară."
                ),
                sources=(
                    "de la apusul la răsăritul soarelui.",
                    "pe timpul zilei.",
                    "pe orice vreme.",
                    "semne.",
                    "de la răsăritul la apusul soarelui, pe timp cu vizibilitate redusă, în toate "
                    "împrejurările în care această măsură este necesară.",
                ),
            ),
            Statement(
                text=(
                    "Distanțele de vizibilitate, la navele sub 12 m: luminile de catarg 2 Mm, luminile "
                    "din borduri 1 Mm, lumina din pupa 2 Mm."
                ),
                sources=(
                    "La ce distanţă trebuie să se vadă luminile de la catarge pentru navele cu "
                    "lungimea mai mică de 12 m?",
                    "La ce distanţă trebuie să se vadă luminile din borduri pentru navele cu o "
                    "lungime mai mică de 12 m?",
                    "La ce distanţă trebuie să se vadă lumina din pupa pentru navele cu o "
                    "lungime mai mică de 12 m?",
                    "1 Mm.",
                ),
            ),
            Statement(
                text=(
                    "La navele între 12 și 50 m, luminile din borduri și lumina din pupa se văd la 2 "
                    "Mm; luminile de catarg ale navelor între 12 și 20 m se văd la 3 Mm."
                ),
                sources=(
                    "La ce distanţă trebuie să se vadă luminile din borduri pentru navele cu o "
                    "lungime între 12 şi 50 m?",
                    "La ce distanţă trebuie să se vadă lumina din pupa pentru navele cu o "
                    "lungime între 12 şi 50 m?",
                    "La ce distanţă trebuie să se vadă luminile de la catarge pentru navele cu "
                    "lungimea între 12 şi 20 m?",
                    "3 Mm.",
                ),
            ),
            Statement(
                text=(
                    "Lumina albă, roșie, verde sau galbenă vizibilă pe întreg orizontul se vede la 2 Mm"
                    " — banca o cere așa și pentru navele între 12 și 50 m, și pentru cele între 12 și "
                    "20 m."
                ),
                sources=(
                    "La ce distanţă trebuie să se vadă lumina albă, roşie, verde sau galbenă "
                    "vizibilă pe întreg orizontul, pentru navele cu lungimea între 12 şi 50 m?",
                    "La 2 Mm se văd luminile albe, roşii, verzi sau galbene pe întreg orizontul "
                    "la navele:",
                    "cu lungimea între 12 şi 20 m.",
                ),
            ),
            Statement(
                text=(
                    "Lumina cu sclipiri e o lumină cu sclipiri regulate, cu frecvența de 120 de "
                    "sclipiri pe minut sau mai mult."
                ),
                sources=(
                    "o lumină cu sclipiri regulate cu frecvenţa de 120 sclipiri pe minut sau mai mult.",
                    "lumină cu sclipiri.",
                ),
            ),
            Statement(
                text=(
                    "Nava cu vele sub 7 m și nava cu rame care nu poartă luminile unei nave cu vele "
                    "trebuie să fie gata să arate în orice moment o lanternă electrică sau un felinar "
                    "aprins cu lumină albă."
                ),
                sources=(
                    "trebuie să fie gata să arate în orice moment o lanternă electrică sau un felinar "
                    "aprins cu o lumină albă.",
                    "7 m.",
                    "dacă nu poartă luminile unei nave cu vele, să fie pregătiră să arate o lanternă "
                    "electrică sau un felinar cu lumină albă.",
                ),
            ),
            Statement(
                text=(
                    "Felinarul combinat e pentru nava cu vele în marș mai mică de 20 m."
                ),
                sources=(
                    "20 m.",
                ),
            ),
            Statement(
                text=(
                    "Semnalele luminoase care repetă manevra se dau la interval de cel puțin 10 "
                    "secunde."
                ),
                sources=(
                    "la cel puţin 10 secunde.",
                ),
            ),
            Statement(
                text=(
                    "Un stat poate stabili prescripții speciale despre numărul luminilor de poziție și "
                    "al semnalelor luminoase, cu condiția să nu poată fi confundate cu Regulamentul."
                ),
                sources=(
                    "Guvernul unui stat poate stabili prescripţiile speciale cu privire la "
                    "numărul luminilor de poziţie, a semnalelor luminoase, prescripţii care să "
                    "fie astfel încât să facă imposibilă confundarea lor cu Regulamentul?",
                    "da.",
                ),
            ),
            Statement(
                text=(
                    "Lumina alternativă a unui far înseamnă culori diferite în sectoare strict "
                    "delimitate; lumina în izofază, durată de lumină egală cu durata de întuneric."
                ),
                sources=(
                    "culori diferite în sectoare strict delimitate",
                    "durata de lumina este egală cu durata de întuneric",
                ),
            ),
            Statement(
                text=(
                    "E interzis să folosești lumini sau proiectoare care s-ar putea confunda cu "
                    "luminile și semnalele din R.N.D., care le-ar dăuna vizibilitatea sau care ar orbi,"
                    " punând în pericol navigația ori circulația terestră."
                ),
                sources=(
                    "Este interzis a se folosi lumini sau proiectoare astfel ca ele să poată fi "
                    "confundate cu luminile sau semnalele menţionate în R.N.D. sau care pot dăuna "
                    "asupra vizibilităţii acestor lumini sau semnale, sau ca ele să producă o orbire "
                    "care constituie un pericol pentru navigaţie ori pentru circulaţia terestră",
                ),
            ),
            Statement(
                text=(
                    "Lumini și semnale neprevăzute în R.N.D. se pot folosi numai pentru comunicări "
                    "între nave sau între navă și uscat, cu condiția să nu se confunde cu cele "
                    "prevăzute."
                ),
                sources=(
                    "Da, numai pentru comunicări între nave, între nave şi uscat, cu condiţia să nu se "
                    "confunde cu luminile şi semnalele prevăzute de R.N.D",
                ),
            ),
            Statement(
                text=(
                    "Noaptea, nava în pericol care cere ajutor agită circular o lumină."
                ),
                sources=(
                    "Agită circular o lumină",
                ),
            ),
            Statement(
                text=(
                    "Lumina de coastă de pe malul drept are suport alb, lumină roșie intermitentă și un"
                    " panou pătrat roșu mărginit de două benzi orizontale albe; cea de pe malul stâng, "
                    "suport alb, lumină verde intermitentă și un panou rombic, verde sus și alb jos. "
                    "Amândouă indică direcția aproximativă a șenalului față de mal și servesc ca punct "
                    "de reper."
                ),
                sources=(
                    "Suport de culoare albă, lumină de culoare roşie intermitentă şi un panou pătrat "
                    "roşu, mărginit de două benzi orizontale albe",
                    "Suport de culoare albă, lumină de culoare verde intermitentă şi un panou de formă "
                    "rombică, piturat jumătate verde-partea de sus şi jumătate alb-partea de jos",
                    "Direcţia aproximativă a şenalului în raport cu malul şi serveşte în acelaşi timp "
                    "ca punct de reper",
                ),
            ),
            Statement(
                text=(
                    "Lumina de coastă de bifurcație are două panouri triunghiulare albe, unul deasupra "
                    "celuilalt și opuse la vârf, cel de sus mărginit cu bandă roșie și cel de jos cu "
                    "bandă verde, și lumină albă intermitentă."
                ),
                sources=(
                    "Două panouri triunghiulare albe, unul deasupra celuilalt şi opuse la vârf, cel de "
                    "deasupra mărginit cu bandă roşie cel de jos cu bandă verde, lumină albă "
                    "intermitentă",
                ),
            ),
            Statement(
                text=(
                    "Lumina albă din pupa e o lumină obișnuită, vizibilă pe un arc de 135°."
                ),
                sources=(
                    "Obişnuită, 1350",
                ),
            ),
        ),
    ),
    Card(
        theme="semne-si-forme-ziua",
        statements=(
            Statement(
                text=(
                    "Nava care navigă în același timp cu vele și cu un aparat propulsor poartă la "
                    "prova, în locul cel mai vizibil, un con cu vârful în jos."
                ),
                sources=(
                    "La prova, în locul cel mai vizibil, un con cu vârful în jos este semnul purtat pe "
                    "timp de zi de:",
                    "o navă care navigă în acelaşi timp cu vele şi cu ajutorul unui aparat propulsor.",
                    "la prova, în locul cel mai vizibil, un con cu vârful în jos.",
                ),
            ),
            Statement(
                text=(
                    "Nava cu vele care folosește în același timp motorul poartă ziua un con negru cu "
                    "vârful în jos, amplasat cât mai sus posibil, într-un loc cât mai vizibil."
                ),
                sources=(
                    "Un con negru cu vârful în jos, amplasat cât mai sus posibil şi într-un loc unde va"
                    " fi cel mai vizibil",
                ),
            ),
        ),
    ),
    Card(
        theme="navigatie-compas-si-drumuri",
        statements=(
            Statement(
                text=(
                    "Drumul navei e unghiul din planul orizontului adevărat, măsurat de la o "
                    "direcție nord până la axul prova; nordul folosit îi dă numele — adevărat, "
                    "magnetic, compas sau giro."
                ),
                sources=(
                    "Unghiul din planul orizontului adevărat măsurat de la direcția nord adevărat "
                    "până la axul prova al navei",
                    "unghiul din planul orizontului adevărat măsurat de la direcția nord compas "
                    "până la axul prova al navei",
                    "Unghiul din planul orizontului adevărat măsurat de la direcția nord giro până "
                    "la axul prova al navei",
                    "Unghiul din planul orizontului adevărat măsurat de la direcția nord magnetic "
                    "până la axul prova al nave",
                ),
                drawing="rose:drum",
            ),
            Statement(
                text=(
                    "Relevmentul la un reper costier e unghiul din planul orizontului adevărat, "
                    "măsurat de la o direcție nord până la linia de vizare la reper; ca la "
                    "drumuri, nordul folosit îi dă numele."
                ),
                sources=(
                    "Unghiul din planul orizontului adevărat măsurat de la direcția nord adevărat "
                    "până la linia de vizare la reperul costier",
                    "Unghiul din planul orizontului adevărat măsurat de la direcția nord compas "
                    "până la linia de vizare la reperul costier",
                    "Unghiul din planul orizontului adevărat măsurat de la direcția nord magnetic "
                    "până la linia de vizare la reperul costier",
                ),
                drawing="rose:relevment",
            ),
            Statement(
                text=(
                    "Relevmentul prova se măsoară de la axul prova al navei până la direcția de "
                    "vizare la reper, nu de la o direcție nord."
                ),
                sources=(
                    "Unghiul din planul orizontului adevărat măsurat de la axul prova al navei "
                    "până la direcția de vizare la reperul costier",
                ),
                # The exception among the three definitions, and the one a
                # drawing settles at a glance: this angle alone does not start
                # at north. The rose carries all three so they can be compared.
                drawing="rose:relevment-prova",
            ),
            Statement(
                text=(
                    "Acul magnetic al compasului de la bord se orientează pe direcția nord compas."
                ),
                sources=(
                    "Acul magnetic al compasului magnetic de la bordul ambarcațiunii se "
                    "orientează pe direcția:",
                    "Acul magnetic al compasului magnetic de la bordul navei se orientează pe "
                    "direcția",
                ),
            ),
            Statement(
                text=(
                    "Linia de credință a compasului materializează axul longitudinal al "
                    "ambarcațiunii."
                ),
                sources=(
                    "Linia de credința a compasului magnetic de la bord materializează:",
                    "Linia de credință a compasului magnetic de la bord materializează",
                    "Axul longitudinal al navei",
                    "axul longitudinal al ambarcațiunii;",
                ),
            ),
            Statement(
                text=(
                    "Drumul adevărat 000° duce nava spre nord, 090° spre est, 180° spre sud, "
                    "270° spre vest."
                ),
                sources=(
                    "Drumul adevărat al ambarcațiunii este egal cu 000 grade; rezulta ca "
                    "ambarcațiunea se deplasează către:",
                    "Drumul adevărat al ambarcațiunii este egal cu 090 grade; rezulta ca "
                    "ambarcațiunea se deplasează către:",
                    "Drumul adevărat al ambarcațiunii este egal cu 180 grade; rezulta ca "
                    "ambarcațiunea se deplasează către:",
                    "Drumul adevărat al ambarcațiunii este egal cu 270 grade; rezulta ca "
                    "ambarcațiunea se deplasează către:",
                    "Nord",
                    "Est;",
                    "Sud;",
                    "Vest;",
                ),
            ),
            Statement(
                text=(
                    "Cadranul de orizont în care se află drumul compas arată care dintre "
                    "variantele oferite e cea corectă: de exemplu, 034° e drum din cadranul NE, "
                    "112° din SE, 234° din SW, iar 328° din NW."
                ),
                sources=(
                    "Drumul compas al ambarcațiunii se afla cuprins în cadranul NE de orizont. "
                    "Care din următoarele valori de drum compas este corectă?",
                    "Drumul compas al ambarcațiunii se afla cuprins în cadranul SE de orizont. "
                    "Care din următoarele valori de drum compas este corectă?",
                    "Drumul compas al ambarcațiunii se afla cuprins în cadranul SW de orizont. "
                    "Care din următoarele valori de drum compas este corectă?",
                    "Drumul compas al ambarcațiunii se afla cuprins în cadranul NW de orizont. "
                    "Care din următoarele valori de drum compas este corectă?",
                    "Dc = 034 grade;",
                    "Dc = 112 grade;",
                    "Dc = 234 grade;",
                    "Dc = 328 grade.",
                ),
                drawing="rose:cadrane",
            ),
            Statement(
                text=(
                    "Carturile: N e cart cardinal, SW intercardinal, SSE inter-intercardinal, "
                    "iar E la N intermediar."
                ),
                sources=(
                    "Cartul N este un cart:",
                    "Cartul SW este un cart:",
                    "Cartul SSE este un cart:",
                    "Cartul E la N este un cart:",
                    "cardinal;",
                    "intercardinal;",
                    "inter-intercardinal;",
                    "intermediar",
                ),
            ),
            Statement(
                text=(
                    "Poziția navei se poate determina, printre altele, prin măsurători de "
                    "relevmente; un relevment compas care nu variază apreciabil la o navă "
                    "care se apropie înseamnă pericol de coliziune."
                ),
                sources=(
                    "Poziția navei se poate determina, printre altele, prin măsurători de",
                    "Când relevmentul compas la o navă care se apropie nu variază în mod "
                    "apreciabil, se consideră :",
                    "relevmente",
                    "pericol de coliziune.",
                ),
            ),
        ),
    ),
    Card(
        theme="reguli-de-drum",
        statements=(
            Statement(
                text=(
                    "Ierarhia cedării: nava cu propulsie mecanică în marș se abate din "
                    "drumul navelor cu vele; nava cu vele în marș se abate din drumul "
                    "navelor nestăpâne pe manevra lor, al celor cu capacitate de "
                    "manevră redusă și al celor în curs de pescuit."
                ),
                sources=(
                    "Din drumul căror nave trebuie să se abată o navă cu propulsie mecanică în "
                    "marş?",
                    "navelor care nu sunt stăpâne pe manevra lor.",
                    "navelor cu capacitate de manevră redusă.",
                    "navelor în curs de pescuit.",
                    "navelor cu vele.",
                ),
            ),
            Statement(
                text=(
                    "Nava stânjenită de pescajul său se abate din drumul navelor "
                    "nestăpâne pe manevra lor."
                ),
                sources=(
                    "Din drumul căror nave trebuie să se abată o navă stânjenită de pescajul "
                    "său?",
                    "navelor nestăpâne pe manevra lor.",
                ),
            ),
            Statement(
                text=(
                    "Când se întâlnesc două ambarcațiuni mici, una autopropulsată și "
                    "una nepropulsată, cedează drumul cea autopropulsată."
                ),
                sources=(
                    "Cine cedează drumul în cazul întâlnirii dintre două ambarcaţiuni mici, "
                    "dintre care una este autopropulsată şi cealaltă nepropulsată ?",
                    "Ambarcaţiunea autopropulsată",
                ),
            ),
            Statement(
                text=(
                    "Între două nave cu vele: cu vântul din borduri diferite, se abate "
                    "cea care primește vântul din babord; cu vântul din același bord, "
                    "nava din vânt se abate din drumul celei de sub vânt."
                ),
                sources=(
                    "nava care primeşte vântul din babord trebuie să se abată din "
                    "drumul navei care primeşte vântul din tribord.",
                    "nava care este în vânt se va abate din drumul navei de sub vânt.",
                ),
            ),
            Statement(
                text=(
                    "Depășitorul cedează: orice navă care ajunge din urmă alta se abate "
                    "din drumul ei. Ajungi din urmă când vii dintr-o direcție mai mare "
                    "de 22°5 înapoia traversului celeilalte — noaptea i-ai vedea doar "
                    "lumina din pupa și luminile din borduri; iar dacă nu poți stabili "
                    "cu siguranță, te consideri navă care ajunge din urmă și manevrezi "
                    "în consecință."
                ),
                sources=(
                    "nava care ajunge din urmă.",
                    "orice navă care ajunge din urmă o altă navă trebuie să se abată "
                    "din drumul navei ajunsă din urmă.",
                    "când vine dintr-o direcţie mai mare de 22°5 dinapoia traversului "
                    "celeilalte nave, astfel încât noaptea se vede numai lumina din "
                    "pupa şi luminile din bordurile navei ajunsă din urmă.",
                    "să se considere navă care ajunge din urmă şi să manevreze în "
                    "consecinţă.",
                ),
                # The bank draws this link itself: 22°5 abaft the beam is 112,5°
                # to 247,5°, and its own answer says that at night you would see
                # only the stern light — which is the arc of exactly that span,
                # already in the catalogue. No new drawing, and no invention.
                drawing="arc:lumina-de-pupa",
            ),
            Statement(
                text=(
                    "Nava care nu e obligată să se abată își menține drumul și viteza; "
                    "manevrează abia când îi devine evident că nava obligată să se "
                    "abată nu o face."
                ),
                sources=(
                    "trebuie să-şi menţină drumul şi viteza.",
                    "imediat ce i se pare evident faptul că nava care are obligaţia de "
                    "a se abate din drumul său nu face manevra.",
                ),
            ),
            Statement(
                text=(
                    "Existența pericolului de coliziune se stabilește cu toate "
                    "mijloacele disponibile, potrivite împrejurărilor; pericolul există "
                    "când relevmentul compas la nava care se apropie nu variază în mod "
                    "apreciabil."
                ),
                sources=(
                    "orice navă trebuie să folosească toate mijloacele disponibile "
                    "corespunzătoare împrejurărilor şi condiţiilor extrene, pentru a stabili "
                    "dacă există un pericol de coliziune.",
                    "Orice navă trebuie să folosească toate mijloacele disponibile "
                    "corespunzătoare împrejurărilor şi condiţiilor externe pentru a stabili "
                    "dacă există:",
                    "când relevmentul compas la o navă care se apropie nu variază în mod "
                    "apreciabil.",
                    "un pericol de coliziune.",
                ),
            ),
            Statement(
                text=(
                    "Schimbarea de drum care evită coliziunea se face cu mult timp "
                    "înainte, e substanțială și nu duce la o altă situație de foarte "
                    "mare apropiere."
                ),
                sources=(
                    "manevra se va face cu mult timp înainte, să fie substanţială şi să "
                    "nu conducă la o altă situaţie de foarte mare apropiere.",
                ),
            ),
            Statement(
                text=(
                    "Abaterile de la prevederile Regulamentului sunt permise când "
                    "există pericol de navigație, risc de coliziune ori împrejurări "
                    "deosebite; nava care se îndoiește de intențiile celei care "
                    "traversează șenalul emite cinci sunete scurte."
                ),
                sources=(
                    "Când există riscul unei coliziuni, precum şi în toate împrejurările "
                    "deosebite sunt permise:",
                    "când există pericol de navigaţie, riscul unei coliziuni, precum şi în "
                    "toate împrejurările deosebite.",
                    "un semnal de avertizare compus din cinci sunete scurte.",
                    "abaterea de la prevederile Regulamentului.",
                ),
            ),
            Statement(
                text=(
                    "Două nave sunt „în vedere” numai când una dintre ele poate fi observată vizual de "
                    "cealaltă."
                ),
                sources=(
                    "Când două nave se consideră în vedere?",
                    "numai când una dintre ele poate fi observată vizual de către cealaltă.",
                    "Când una dintre nave poate fi observată vizual de către cealaltă navă, se "
                    "consideră:",
                    "nave aflate în vedere.",
                ),
            ),
            Statement(
                text=(
                    "Într-o schemă de separare a traficului nava merge pe banda corespunzătoare direcției "
                    "generale și se ține cât mai departe de linia sau zona de separare; intră și iese pe "
                    "la una din extremități, iar dacă o face din altă parte, sub un unghi cât mai mic "
                    "față de direcția traficului. Ancorarea se evită atât în schemă, cât și în zonele "
                    "învecinate. Navele care nu folosesc schema se îndepărtează cât mai mult de zona de "
                    "separare, iar în vecinătatea extremităților se navighează cu atenție deosebită."
                ),
                # The stems here are questions, not statements; each fact lives in its own
                # answer, so both halves of every pair are cited.
                sources=(
                    "Nava trebuie să navige pe banda de navigaţie corespunzătoare în direcţia "
                    "generală a traficului şi să se îndepărteze,în măsura posibilului, de linia "
                    "sau zona de separare a sensurilor de trafic atunci când trebuie să navige:",
                    "în interiorul unei scheme de separare a traficului.",
                    "Cum trebuie să se angajeze o navă pentru intrarea sau ieşirea dintr-o "
                    "schemă de separare a traficului?",
                    "ca regulă generală pe la una din extremităţi,dar atunci când se angajează "
                    "să intre sau să iasă,din orice parte,să facă manevra sub unghi cât mai mic "
                    "faţă de direcţia traficului.",
                    "Este permisă ancorarea în schemele de separare a traficului?",
                    "se va evita în măsura maximă a posibilului ancorarea atât în schema de "
                    "separare, cât şi în zonele învecinate acesteia.",
                    "Cum trebuie să navige navele care nu folosesc o schemă de separare a "
                    "traficului?",
                    "să se îndepărteze cât mai mult de zona de separare a traficului.",
                    "Cum trebuie să se navige în zone vecine cu extremităţile unei zone de "
                    "separare a traficului?",
                    "cu atenţie deosebită.",
                ),
            ),
            Statement(
                text=(
                    "Zonele de trafic costier nu se folosesc în mod normal pentru traficul direct: fac "
                    "excepție navele sub 20 m, cele cu vele și cele angajate în pescuit, iar oricine le "
                    "poate folosi pentru evitarea unui pericol evident. De la regula schemelor de "
                    "separare sunt exceptate navele cu capacitate de manevră redusă angajate în "
                    "menținerea siguranței navigației, iar reglementările schemelor sunt adoptate de "
                    "Organizație."
                ),
                sources=(
                    "Zonele de navigaţie costieră pot fi folosite pentru traficul costier?",
                    "în mod normal nu trebuie folosite pentru traficul direct, cu excepţia "
                    "navelor mai mici de 20 m lungime şi a navelor cu vele.",
                    "Ce nave pot folosi zonele de navigaţie de trafic costier?",
                    "navele cu o lungime mai mică de 20 m, navele cu vele şi navele angajate în "
                    "operaţiuni de pescuit.",
                    "Când pot folosi navele zonele de navigaţie de trafic costier?",
                    "pentru evitarea unui pericol evident.",
                    "Care sunt navele exceptate de la prevederile regulii referitoare la "
                    "navigaţie în schemele de separare a traficului?",
                    "navele cu capacitate de manevră redusă, angajate în manevra de menţinere a "
                    "siguranţei navigaţiei.",
                    "Schemelor de separare a traficului li se aplică reglementările referitoare "
                    "la schemele de separare a traficului, adoptate de:",
                    "Organizaţie.",
                ),
            ),
        ),
    ),
    Card(
        theme="vizibilitate-redusa",
        statements=(
            Statement(
                text=(
                    "Regulile de conducere pe vizibilitate redusă se aplică navelor "
                    "care nu se văd una pe alta și care navigă înăuntrul sau în "
                    "apropierea zonelor cu vizibilitate redusă."
                ),
                sources=(
                    "navelor care nu se văd una pe alta şi care navigă înlăuntrul "
                    "sau în apropierea zonelor de vizibilitate redusă.",
                ),
            ),
            Statement(
                text=(
                    "Pe vizibilitate redusă se navigă cu viteză de siguranță, "
                    "adaptată împrejurărilor existente și condițiilor de "
                    "vizibilitate."
                ),
                sources=(
                    "cu o viteză de siguranţă adaptată împrejurărilor existente şi "
                    "condiţiilor de vizibilitate redusă.",
                ),
            ),
            Statement(
                text=(
                    "Veghea — vizuală și auditivă — se asigură în permanență, cu "
                    "toate mijloacele disponibile, potrivit împrejurărilor și "
                    "condițiilor existente, ca să permită o apreciere completă a "
                    "situației."
                ),
                sources=(
                    "trebuie să se asigure în permanenţă o veghe vizuală şi "
                    "auditivă corespunzătoare, folosind în acelaşi timp toate "
                    "mijloacele disponibile, potrivit cu împrejurările şi "
                    "condiţiile existente, în aşa fel încât să permită o "
                    "apreciere completă a situaţiei.",
                ),
            ),
            Statement(
                text=(
                    "Pe vizibilitate redusă, nava cu vele, nava cu capacitate de "
                    "manevră redusă și nava stânjenită de pescaj emit același "
                    "semnal: un sunet lung urmat de două sunete scurte, la "
                    "intervale de cel mult 2 minute."
                ),
                sources=(
                    "Ce semnale sonore emite o navă cu vele pe vizibilitate redusă?",
                    "Ce semnal sonor emite o navă cu capacitatea de manevră redusă pe "
                    "vizibilitate redusă?",
                    "Ce semnale sonore vor emite navele stânjenite de pescajul lor pe "
                    "vizibilitate redusă?",
                    "un sunet lung urmat de 2 sunete scurte, la intervale ce nu vor fi mai mari "
                    "de 2 minute.",
                    "un sunete lung urmat de 2 sunete scurte la intervale nu mai mari de 2 "
                    "minute.",
                    "un sunet lung urmat de două sunete scurte, la intervale nu mai mari de 2 "
                    "minute.",
                ),
            ),
            Statement(
                text=(
                    "Nava sub 12 m care nu poate emite semnalele prescrise de "
                    "Regulament emite un alt semnal sonor eficace, la intervale "
                    "de cel mult 2 minute."
                ),
                sources=(
                    "Ce obligaţii are o navă mai mică de12 m, pe vizibilitate "
                    "redusă, în cazul în care nu poate emite semnale prescrise "
                    "de Regulament?",
                    "să emită un semnal sonor eficace la intervale care să nu "
                    "depăşească 2 minute.",
                ),
            ),
            Statement(
                text=(
                    "Semnalele pentru vizibilitate redusă se emit atât ziua, "
                    "cât și noaptea, înăuntrul sau în apropierea zonei în care "
                    "vizibilitatea este redusă."
                ),
                sources=(
                    "atât ziua cât şi noaptea, pe vizibilitate redusă.",
                    "înlăuntrul sau în apropierea zonei în care vizibilitatea "
                    "este redusă.",
                ),
            ),
            Statement(
                text=(
                    "Semnalizarea prevăzută pentru noapte la nave se poartă, în "
                    "plus, și ziua, pe vizibilitate redusă: ceață, ninsoare etc."
                ),
                sources=(
                    "Semnalizarea prevăzută pentru noapte la nave trebuie să fie "
                    "purtată, în plus, şi ziua , în condiţii de :",
                    # The stem is a fill-in-the-blank and says nothing about fog
                    # or snow on its own; that half of the rule lives only in
                    # the answer. Both, as the sub-12 m statement above does.
                    "Vizibilitate redusă : ceaţă, ninsoare etc",
                ),
            ),
        ),
    ),
    Card(
        theme="meteo-si-hidrologie",
        statements=(
            Statement(
                text=(
                    "Manevra navei e influențată de vânt, valuri, curent și adâncimile "
                    "mici."
                ),
                sources=(
                    "Ce fenomene hidrologice şi meteorologice pot influenţa manevra "
                    "navei?",
                    "vântul, valurile, curentul, adâncimi mici",
                ),
            ),
            Statement(
                text=(
                    "Vântul dinaintea traversului micșorează viteza și dă derivă de vânt "
                    "— din prova tribord, deriva e la babord; vântul din travers dă "
                    "derivă de vânt."
                ),
                sources=(
                    "Dacă vântul bate dinaintea traversului acesta produce",
                    "micșorarea vitezei și derivă de vânt",
                    "Dacă vântul bate din prova tribord acesta produce",
                    "micșorarea vitezei și derivă de vânt la babord",
                    "Dacă vântul bate din travers acesta produce",
                    "derivă de vânt",
                ),
                drawing="schema:deriva",
            ),
            Statement(
                text=(
                    "La acostare se ține cont tot timpul de vânt și de curent: forța lor "
                    "se folosește în ajutorul manevrei, nu manevra împotriva lor."
                ),
                sources=(
                    "La manevra de acostare, pe lângă calităţile manevriere ale navei, "
                    "tot timpul se va ţine cont de vânt şi curent urmărindu-se",
                    "ca forţa acestora să fie folosită în ajutorul manevrei şi nu manevra "
                    "săse împotrivească acestora",
                ),
            ),
            Statement(
                text=(
                    "La «om la apă», când nu se vede clar cum lucrează curentul și "
                    "vântul, se vine inițial cu prova pe direcția inversă a rezultantei, "
                    "căutând efectul minim de derivă, și apropierea de cel căzut se face "
                    "cu viteză scăzută."
                ),
                sources=(
                    # The precondition — that the drift is not readable — is in
                    # the stem alone; the answer gives only the manoeuvre.
                    "În cazul în care nu putem observa în mod clar felul cum acţionează "
                    "curentul şi vântul în cazul manevrei de ,,Om la apă”",
                    "venim iniţial cu prova pe direcţia inversă a rezultantei, căutând "
                    "efectul minim de derivă şi ne apropiem de cel căzut în apă cu viteza "
                    "scăzută",
                ),
            ),
            Statement(
                text=(
                    "La întâlniri se reduce viteza în întâmpinarea valurilor navei din "
                    "sens opus; depășirile se fac la distanță cât mai mare de nava "
                    "depășită, fără a-i face valuri, cu atenție la valurile din siajul "
                    "ei."
                ),
                sources=(
                    "va reduce viteza în întâmpinarea valurilor provocate de nava ce vine "
                    "din sens opus şi va adopta o viteză corespunzătoare evitării "
                    "răsturnării",
                    "la o distanță cât mai mare de nava depăşită, viteza se adaptează "
                    "situaţiei, urmărind a nu face valuri pentru nava depăşită, dar "
                    "acordând atenţia necesară întâmpinării valurilor din siajul acesteia",
                ),
            ),
            Statement(
                text=(
                    "«Nava cu vele» e nava care navigă cu vele — chiar dacă are o mașină "
                    "proprie, cu condiția ca aceasta să nu fie folosită."
                ),
                sources=(
                    "o navă care navigă cu vele, chiar dacă are o maşină proprie, cu "
                    "condiţia ca aceasta să nu fie folosită.",
                    "O navă care navigă cu vele, chiar dacă are o maşină proprie, cu "
                    "condiţia ca aceasta să nu fie folosită, reprezintă:",
                    "o navă cu vele.",
                ),
            ),
        ),
    ),
    Card(
        theme="navigatie-harti-si-pozitie",
        statements=(
            Statement(
                text=(
                    "Latitudinea geografică e arcul de meridian măsurat de la ecuator până "
                    "la paralelul locului; longitudinea, arcul de ecuator măsurat de la "
                    "meridianul Greenwich până la meridianul locului."
                ),
                sources=(
                    # Fill-in-the-blank stems state no fact by themselves; the fact is
                    # in the answer, so both are cited for each of the two terms.
                    "Latitudinea geografică este",
                    "Arcul de meridian măsurat de la ecuatorul terestru până la paralelul "
                    "locului",
                    "Longitudinea geografică este",
                    "Arcul de ecuator măsurat de la meridianul Greenwich până la meridianul "
                    "locului",
                ),
            ),
            Statement(
                text=(
                    "Deplasarea schimbă coordonatele după emisferă: spre nord, latitudinea "
                    "crește în emisfera nordică și scade în cea sudică; spre vest, "
                    "longitudinea scade în emisfera estică și crește în cea vestică."
                ),
                sources=(
                    # Each of the four clauses pairs a stem (hemisphere + direction)
                    # with its own answer (which way the coordinate moves); checked
                    # individually against its own question so no pair is inverted.
                    "În emisfera nordică, dacă nava se deplasează spre Nord",
                    "latitudinea punctului de plecare este mai mică decât latitudinea "
                    "punctului de sosire",
                    "În emisfera sudica, dacă nava se deplasează spre Nord",
                    "latitudinea punctului de plecare este mai mare decât latitudinea "
                    "punctului de sosire",
                    # The bank's own typo: "In", no diacritic.
                    "In emisfera estică, dacă nava se deplasează spre vest",
                    "longitudinea punctului de sosire este mai mică decât longitudinea "
                    "punctului de plecare",
                    "În emisfera vestică, dacă nava se deplasează spre vest",
                    "longitudinea punctului de plecare este mai mică decât longitudinea "
                    "punctului de sosire",
                ),
            ),
            Statement(
                text=(
                    "Harta marină e o hartă tematică ce figurează detaliat întinderile de "
                    "apă; scara ei numerică e raportul dintre lungimea unitară de pe Pământ "
                    "și corespondentul ei pe hartă."
                ),
                sources=(
                    "Harta marină este",
                    "o hartă tematică care figurează aspecte detaliate ale întinderilor de "
                    "apă de pe o anumită suprafață a scoarței terestre",
                    "Scara numerică a unei hărți este",
                    "Raportul dintre lungimea unitară de pe Pământ și corespondentul pe "
                    "hartă",
                ),
            ),
            Statement(
                text=(
                    "Polii geografici sunt cele două puncte în care axa de rotație "
                    "intersectează suprafața Pământului."
                ),
                sources=(
                    "Polii geografici sunt",
                    "Cele două puncte în care axa de rotație intersectează suprafața "
                    "Pământului",
                ),
            ),
            Statement(
                text=(
                    "Punctul navei se poate determina cu repere costiere — de pildă "
                    "farurile."
                ),
                sources=(
                    # The answer, "faruri", is a single generic word that would fix
                    # nothing on its own; the stem alone carries the subject and
                    # already pins this to its one question.
                    "Reperele costiere utilizate pentru determinarea punctului navei pot "
                    "fi",
                    "faruri",
                ),
            ),
            Statement(
                text=(
                    "Adâncimea apei se măsoară cu sonda; viteza ambarcațiunii, cu lochul."
                ),
                sources=(
                    # Same reasoning as above: "sonda" and "Lochul" are short, generic
                    # answers that fix nothing extra; the stems alone identify the
                    # three questions this teaches.
                    # The stems are fill-in-the-blank: "sonda" and "lochul" live
                    # in the answers alone, and they are what the statement says.
                    "Adâncimea apei se măsoară cu",
                    "sonda",
                    "Viteza ambarcațiunii se măsoară cu:",
                    "lochul.",
                    "Viteza unei ambarcațiuni se măsoară cu",
                    "Lochul",
                ),
            ),
        ),
    ),
    Card(
        # Five questions, every one asked at both classes.
        theme="motovehicule-nautice",
        statements=(
            Statement(
                text=(
                    "Skyjetul se conduce numai ziua, numai în porțiunile stabilite și marcate ale căilor "
                    "navigabile interioare, și poartă numere de înmatriculare vizibile date de căpitănie."
                ),
                # Three of the five stems are the same sentence with a different ending, so
                # the answers are what say which limit is which.
                sources=(
                    "Conducerea de motovehicule nautice (skyjet-uri) este supusă următoarelor "
                    "limite",
                    "este permisă numai ziua",
                    "Conducerea de skyjet pe căile navigabile interioare",
                    "este permisă numai în porţiunile stabilite şi marcate",
                    "Conducerea de skyjet este supusă următoarelor limite",
                    "pe skyjet trebuie să se aplice numere de înmatriculare vizibile acordate "
                    "de căpitănie",
                ),
            ),
            Statement(
                text=(
                    "Conducătorul și însoțitorul poartă veste de salvare, iar motorul trebuie fie să se "
                    "oprească automat la căderea conducătorului, fie să treacă automat pe cea mai mică "
                    "viteză, vehiculul oprindu-se sau descriind un cerc."
                ),
                sources=(
                    "Conducerea de motociclete nautice (skyjet) este supusă următoarelor "
                    "limite:",
                    "conducătorul şi însoţitorul trebuie să poarte veste de salvare",
                    "Conducerea de motovehicule nautice (skyjet) este supusă următoarelor "
                    "limite",
                    "motorul trebuie sau să se oprească automat la căderea conducătorului, sau "
                    "să fie cuplat automat pe cea mai mică viteză, în timp ce vehiculul trebuie "
                    "să se oprească sau să descrie o traiectorie circulară",
                ),
            ),
        ),
    ),
    Card(
        # Twenty-seven questions after stage 4e sent the steering gear here.
        theme="manevra-cu-motor",
        statements=(
            Statement(
                text=(
                    "Cârma se compune din pană și eche; echea e piesa în formă de bară sau de sector care "
                    "se fixează în capul penei cârmei."
                ),
                sources=(
                    'Cârma se compune din :',
                    'pană și eche',
                    'Echea reprezintă:',
                    'o piesa sub forma unei bare sau a unui sector ce se fixează în capul penei cârmei.',
                ),
            ),
            Statement(
                text=(
                    "Troțele sunt cablurile fixate de cârmă cu ajutorul cărora se guvernează."
                ),
                # Its own statement on purpose: the bank asks this only at class C, and
                # folded into the sentence above it would ride the shared questions to class
                # D.
                sources=(
                    'Cablurile fixate de cârma , cu ajutorul cărora se guvernează se numesc',
                    'troƫe',
                ),
            ),
            Statement(
                text=(
                    "Instalația de guvernare e ansamblul de piese și mecanisme care asigură respectarea "
                    "drumului impus sau schimbarea direcției de înaintare; produce momentul girației. Se "
                    "compune din timonă sau manipulator electric, servomotor la navele mari, transmisia "
                    "timonă-servomotor-cârmă și cârma propriu-zisă, timona fiind ea însăși un element al "
                    "instalației de guvernare."
                ),
                # The C and D variants differ only in diacritics and in the bank's own
                # typos; both are cited so the statement reaches both classes honestly.
                sources=(
                    'Instalația de guvernare:',
                    'reprezintă un ansamblu de piese și mecanisme care trebuie sa asigure respectarea drumului impus navei sau schimbarea direcției de înaintare a navei.',
                    'Instalatia de guvernare:',
                    'reprezinta un ansamblu de piese si mecanisme care trebuie sa asigure respectarea drumului impus navei sau schimbarea directiei navei.',
                    'Instalația de guvernare a navei reprezintă:',
                    'un complex de mecanisme care, acționate separat sau în comun, produce momentul girației (schimbarea direcției de înaintare a navei)',
                    'Instalatia de guvernare a navei reprezinta:',
                    'un complex de mecanisme care, actionate separat sau in comun, produce momentul giratiei (schimbarea diretiei de inaintare a navei)',
                    'Instalaţia de guvernare se compune din',
                    'timona sau manipulatorul electric; servomotorul la navele mari; sistemul de transmisie timonă-servomotor-cârmă; cârma propiu-zisă',
                    'Timona reprezintă un element component al instalației de :',
                    'guvernare',
                ),
            ),
            Statement(
                text=(
                    "Guvernarea se îmbunătățește prin mărirea suprafeței penei cârmei și poate fi ajutată "
                    "de propulsoare prova și pupa, bowthruster și sternthruster, montate în corpul "
                    "ambarcațiunii."
                ),
                # The thruster fact used to sit in the construction card; stage 4e moved its
                # question here, and the fact came with it.
                sources=(
                    'Guvernarea poate fi îmbunătăţită de:',
                    'mărimea suprafeţei penei cârmei',
                    'Guvernarea clasică poate fi ajutată prin instalarea în corpul ambarcaţiunii de',
                    'propulsoare prova şi pupa (bowtruster și sterntruster)',
                ),
            ),
            Statement(
                text=(
                    "La deplasarea înapoi, prova se orientează în bordul opus celui în care s-a pus "
                    "cârma, iar pupa în sensul punerii cârmei."
                ),
                sources=(
                    'La deplasarea înapoi a bărcii, efectul cârmei determină',
                    'orientarea provei în bordul opus celui în care s-a pus cârma şi a pupei în sensul punerii cârmei',
                ),
                drawing="schema:carma-inapoi",
            ),
            Statement(
                text=(
                    "Mărimea forței care lucrează pe timonă ține de puterea motorului, de cât din elice e "
                    "în apă și de tipul și pasul ei. Timona nu se lasă liberă la nicio viteză: forțele "
                    "turbionare din sistemul de guvernare pot roti barca brusc și o pot face instabilă."
                ),
                sources=(
                    '"Mărimea’’ forţei ce acţionează asupra timonei este influenţată de',
                    'puterea motorului, de câtă porţiune din elice este în apă, de tipul şi pasul elicei',
                    'Conducătorul ambarcațiunii:',
                    'nu ar trebui să dea drumul timonei la nici un fel de viteză, din cauza forţelor turbionare prezente în sistemul de guvernare, barca ar putea să înceapă să se rotească rapid şi să devină instabilă',
                ),
            ),
            Statement(
                text=(
                    "Acostarea și plecarea cer cunoașterea calităților manevriere ale navei și deprinderi "
                    "marinărești. Cu bordul, nava se apropie de cheu sub un unghi ascuțit, ca să atenueze "
                    "impactul provei. La o altă navă se acostează în bordul de sub vânt și cât mai spre "
                    "centru, după ce aceea reduce viteza și ține direcția fără abatere. La mal neamenajat "
                    "se merge cu vigilență sporită, protejând elicea și cârma. Se folosesc baloane de "
                    "protecție polivinilice umplute cu aer."
                ),
                sources=(
                    'Manevrele de acostare și plecare:',
                    'prezintă grad sporit de dificultate, solicitând cunoaşterea calităţilor manevriere ale navei și deprinderi marinăreşti',
                    'În cazul acostării cu bordul:',
                    'nava se apropie de cheu sub un unghi ascuţit, pentru a atenua impactul provei cu cheul',
                    'Acostarea ambarcaţiunii la o navă se face în următoarele condiţii',
                    'nava la care urmează a se acosta reduce viteza și păstrează direcţia fără abatere, iar ambarcaţiunea va acosta totdeauna în bordul de sub vânt şi cât mai spre centrul navei',
                    'Acostarea ambarcaţiunii la mal neamenajat',
                    'se face cu vigilenţă sporită, protejând elicea şi cârma',
                    'La acostare se folosesc',
                    'baloane de protecţie polivinilice umplute cu aer',
                ),
            ),
            Statement(
                text=(
                    "Înainte de plecarea de la acostare: verifici butonul de oprire de urgență, pornind "
                    "motorul, trăgând saula și văzând dacă se oprește, și ții saula legată de haine sau "
                    "de vestă; strângi mecanismele care prind motorul de barcă și toată aparatura din "
                    "sistemul de guvernare; lași la țărm materialul în plus, iar ce rămâne la bord îl "
                    "depozitezi în siguranță; și parcurgi până la capăt algoritmul de verificări."
                ),
                # Four questions share one stem, so only the answers tell them apart; citing
                # the stem would bind all four to whichever statement claimed it first.
                sources=(
                    'Înainte de a părăsi locul de acostare',
                    'Înainte de a părăsi locul de acostare:',
                    'verificaţi funcţionarea butonului pentru oprire de urgenţă, daţi drumul motorului, trageţi saula şi vedeţi dacă motorul se opreşte; asiguraţi-vă că saula este bine legată de hainele sau vesta dumneavoastră de salvare',
                    'asiguraţi-vă că toate mecanismele folosite pentru a ataşa motorul de barcă sunt bine strânse şi la locul lor, procedaţi la fel pentru toată aparatura din sistemul de guvernare',
                    'îndepărtaţi orice material în plus din barca şi lăsaţi-l la ţărm; dacă aveţi nevoie de el la bord, asiguraţi-vă că este depozitat în siguranţă',
                    'asiguraţi-vă că operaţiunile de pe algoritmul verificărilor dumneavoastră au fost parcurse',
                ),
            ),
            Statement(
                text=(
                    "La manevra de om la apă se ține cont de efectul vântului și al curentului asupra "
                    "ambarcațiunii și asupra persoanei căzute, astfel încât barca să nu derive peste om."
                ),
                sources=(
                    'Manevra de ”Om la apă“ este o manevră clasică de recuperare care se efectuează',
                    'ţinând cont de efectul vântului şi curentului asupra ambarcaţiunii şi persoanei căzute în apă, astfel încât ambarcaţiunea să nu derive peste omul din apă',
                ),
            ),
            Statement(
                text=(
                    "Când e nevoie de timp pentru a aprecia situația și a evita o coliziune, cea mai "
                    "bună manevră e reducerea vitezei sau oprirea completă, stopând mașinile ori "
                    "punându-le înapoi."
                ),
                # Its own statement, like the troțe one above and for the same reason:
                # the bank asks this only at class C, while the man-overboard question
                # beside it is asked at both. Folded together, a class C rule rode the
                # shared question to class D — and the class-folding sweep cannot see
                # that, because it needs single-class sources on both sides.
                sources=(
                    'Care este manevra cea mai indicată pentru a se câştiga mai mult timp pentru aprecierea situaţiei, atunci când trebuie să se evite o coliziune?',
                    'reducerea vitezei sau opirea completă, stopând maşinile ori punându-le înapoi.',
                ),
            ),
            Statement(
                text=(
                    "Nava cu capacitate de manevră redusă e aceea a cărei capacitate de manevră e "
                    "limitată prin natura lucrărilor sale și care, din acest motiv, nu se poate îndepărta "
                    "din drumul altei nave."
                ),
                # Class C only, and the fishing definition below is class D only: the bank
                # asks each at one class, so they stay apart.
                sources=(
                    'Ce se înţelege prin expresia "navă cu capacitate de manevră redusă"?',
                    'o navă a cărei capacitate de manevră conform Regulamentului este limitată prin natura lucrărilor sale şi care, în consecinţă, nu se poate îndepărta din drumul altei nave.',
                ),
            ),
            Statement(
                text=(
                    "Nava care pescuiește e orice navă care pescuiește cu plasa, cu cârmaca, cu traul sau "
                    "cu alte mijloace de pescuit care îi reduc capacitatea de manevră."
                ),
                sources=(
                    'Ce se înţelege prin termenul “navă care pescuieşte” ?',
                    'Orice navă care pescuieşte cu ajutorul plasei, a cârmacei, cu traul sau alte mijloace de pescuit care-i reduc capacitatea de manevră',
                ),
            ),
        ),
    ),
    Card(
        # Twenty-three questions after stage 4e sent the steering gear away.
        theme="motor-si-propulsie",
        statements=(
            Statement(
                text=(
                    "Propulsoarele sunt zbaturile, ramele și elicele, iar rotația elicei generează în "
                    "același timp propulsie și guvernare."
                ),
                sources=(
                    'In categoria propulsoarelor intra:',
                    'zbaturile, ramele, elicele.',
                    'Prin rotaţia elicei se generează efect de',
                    'propulsie şi guvernare',
                ),
            ),
            Statement(
                text=(
                    "Pasul elicei e spațiul parcurs de marginea ei exterioară de-a lungul axei de rotație "
                    "într-o rotație completă. Numărul de ture pe minut e RPM, iar RPM înmulțit cu pasul "
                    "dă spațiul parcurs de ambarcațiune într-un minut."
                ),
                sources=(
                    'Pasul elicei reprezintă:',
                    'spaţiul parcurs de marginea exterioară a elicei în mişcarea de translaţie efectuată de-a lungul axei de rotaţie în timpul unei rotaţii complete',
                    'Numărul de ture pe care îl efectuează o elice în mişcarea sa de rotaţie într-un interval de timp de un minut reprezintă',
                    'numărul de rotaţii al elicei pe minut (RPM)',
                    'Înmulţind rotaţiile pe minut (RPM) cu pasul elicei, se obţine:',
                    'spaţiul parcurs de ambarcaţiune într-un minut',
                ),
            ),
            Statement(
                text=(
                    "Elicea are pas dreapta dacă la mersul înainte se învârte la dreapta, și pas stânga "
                    "dacă se învârte la stânga."
                ),
                sources=(
                    'Elicea are pas dreapta dacă:',
                    'la mersul înainte al ambarcaţiunii elicea se învârte la dreapta',
                    'Elicea are pas stânga dacă:',
                    'la mersul înainte al ambarcaţiunii elicea se învârte la stânga',
                ),
            ),
            Statement(
                text=(
                    "Mărimea și forma elicei depind de puterea motorului, de mărimea corpului și de "
                    "scopul bărcii, tracțiune sau viteză. La alegere se ține cont de viteza probabilă a "
                    "bărcii, de felul în care o vei folosi și de testarea pasului; se verifică turația "
                    "maximă a motorului, viteza bărcii, ventilația elicei, abilitatea de glisare și "
                    "presiunea de răcire."
                ),
                sources=(
                    'Mărimea şi forma elicei depinde de',
                    'puterea motorului, mărimea corpului ambarcaţiunii şi scopul pentru care este destinată barca, tracţiune sau viteză',
                    'Pentru alegerea elicei care să corespundă exigenţelor dvs. trebuie să ţineţi cont de următoarele elemente',
                    'viteza probabilă a bărcii, care este cea mai bună elice pentru designul şi viteza bărcii dumneavoastră; modul în care doriţi să folosiţi barca; testarea pasului elicei',
                    'Alegerea celei mai bune elice şi a înălţimii motorului necesită verificarea câtorva lucruri precum',
                    'turaţia maximă a motorului; viteza bărcii; ventilaţia elicei; abilitatea de glisare a bărcii; presiunea de răcire',
                ),
            ),
            Statement(
                text=(
                    "Înclinarea motorului schimbă asieta și controlul. Înclinat în jos la capătul cursei, "
                    "afundă pupa, iar la ambarcațiunile mici se vede apuparea; dacă pupa intră adânc la "
                    "viteză mare, barca se poate roti brusc și arunca pasagerii peste bord. Înclinat în "
                    "sus la viteză mare, forțele turbionare acționează brusc și se poate pierde "
                    "controlul, iar un motor înclinat în sus frânează mai slab și cere mai mult spațiu de "
                    "oprire. Indicatorul înclinării ține motorul la unghiul dinainte ales."
                ),
                # Five questions, five different stems: each fact is in its own answer, so
                # both halves of every pair are cited.
                sources=(
                    'Când motorul este înclinat în jos la capătul cursei',
                    'pupa bărcii va intra mai adânc în apă, la ambarcaţiunile mai mici se observă apuparea',
                    'Dacă pupa intră adânc în apă, datorită înclinării motorului la viteze mari',
                    'barca ar putea să înceapă să se rotească rapid şi să se arunce pasagerii peste bord',
                    'Dacă înclinaţi motorul în sus la viteze mari',
                    'forţele turbionare vor acţiona brusc şi pot cauza pierderea controlului ambarcaţiunii',
                    'Un motor înclinat în sus',
                    'are o abilitate de frânare mai redusă decât unul înclinat în jos şi este nevoie de mai mult spaţiu pentru a opri barca',
                    'Indicatorul înclinării este folosit',
                    'sa orienteze motorul la un unghi predeterminat pentru o performanţă mai bună în navigaţie',
                ),
            ),
            Statement(
                text=(
                    "Motorul atașabil se montează cu placa anticavitație la nivelul chilei. O "
                    "ambarcațiune echipată cu motoare mai puternice decât cele pentru care a fost "
                    "proiectată este greu de controlat, iar folosirea constantă în regim de mare viteză "
                    "cere verificări mai dese ale instalațiilor de elevare, de guvernare și de "
                    "cuplare-accelerare, precum și ale elicei."
                ),
                sources=(
                    'Motorul ataşabil al unei ambarcaţiuni se montează',
                    'având placa anticavitație la nivelul chilei ambarcaţiunii',
                    'O ambarcaţiune este dificil de controlat în timpul navigaţiei dacă este',
                    'echipată cu motoare de puteri mai mari decât cea pentru care a fost proiectată (,,overpower’’)',
                    'În cazul în care ambarcaţiunea dvs. este utilizată în regim de mare viteză în mod constant, este nevoie:',
                    'să fie verificate instalaţiile de elevare a motorului, de guvernare şi de cuplare-accelerare, precum şi elicea/elicele, la intervale mai scurte de timp',
                ),
            ),
            Statement(
                text=(
                    "Oprirea se face reducând viteza treptat, dacă nu e vreun motiv să procedezi altfel: "
                    "reducerea bruscă lasă valul de pupa să lovească oglinda bărcii și să se reverse "
                    "înăuntru. Manevrabilitatea e capacitatea bărcii de a-și menține direcția sau de a o "
                    "schimba cu ajutorul cârmei și al elicei, iar viteza e cu atât mai mare cu cât "
                    "suprafața udată la viteză maximă e mai mică."
                ),
                sources=(
                    'Manevra de oprire se execută astfel',
                    'in cazul în care nu exista nici un motiv sa faceţi altfel, reduceţi în mod gradat viteza, deoarece reducerea brusca poate face ca valul de pupa sa se lovească de oglinda bărcii și sa se reverse în interior',
                    'În ce constă manevrabilitatea bărcii?',
                    'manevrabilitatea constă în capacitatea bărcii de a-şi menţine direcţia de înaintare sau de a schimba această direcţie cu ajutorul cârmei şi elicei',
                    'În funcţie de tipul cocii, viteza bărcii este cu atât mai mare cu cât',
                    'suprafaţa udată la viteza maximă este mai mică',
                ),
            ),
            Statement(
                text=(
                    "Nava cu propulsie mecanică e orice navă pusă în mișcare de o mașină, iar orificiul "
                    "rotund prin care trece axul elicei de propulsie e etambreul axului elicei."
                ),
                # Both are class C questions, so this derives class C alone.
                sources=(
                    'Ce se înţelege prin "navă cu propulsie mecanică"?',
                    'orice navă pusă în mişcare de către o maşină.',
                    'Orificiul rotund prin care trece axul elicei de propulsie se numește',
                    'etambreul axului elicei',
                ),
            ),
        ),
    ),
    Card(
        # Twenty-four of these twenty-six questions ask for an amount or a deadline.
        # Reciting them one per statement would be the enumeration this file exists
        # to avoid, so they are grouped by band: the fine rises with the danger to
        # navigation.
        theme="legislatie",
        statements=(
            Statement(
                text=(
                    "Amenzile urcă odată cu pericolul pentru navigație. Hârtiile lipsă costă cel mai "
                    "puțin: 2.000-5.000 lei pentru nearborarea pavilionului național în apele naționale "
                    "navigabile și pentru refuzul de a prezenta documentul de atestare reprezentanților "
                    "ANR."
                ),
                # Both stems name the deed and the shared answer carries the amount; the
                # answer is cited once because it is the same string for both.
                sources=(
                    'Care este sancțiunea pentru nearborarea la la bordul navei a pavilionului național în apele naționale navigabile ale României?',
                    'amendă de la 2.000 la 5.000 lei',
                    'Care este sancțiunea pentru refuzul prezentării documentului de atestare reprezentanților ANR?',
                ),
            ),
            Statement(
                text=(
                    "Uneltele care încurcă navigația: 10.000-30.000 lei pentru plase ori unelte fixe de "
                    "pescuit așezate în apele naționale navigabile, în rade, porturi, canale sau șenale, "
                    "și 10.000-20.000 lei pentru folosirea nejustificată sau neregulamentară a "
                    "mijloacelor de semnalizare de la bord."
                ),
                sources=(
                    'Care este sancțiunea pentru așezarea de plase ori unelte fixe de pescuit în apele naționale navigabile precum și în rade, portur,i canale sau senale navigabile?',
                    'amendă de la 10.000 la 30.000 lei',
                    'Care este sancțiunea pentru folosirea mijloacelor de semnalizare de la bord în mod nejustificat sau neadecvat regulamentelor de navigație?',
                    'amendă de la 10.000 la 20.000 lei',
                ),
            ),
            Statement(
                text=(
                    "Faptele care pun în pericol navigația sau apa costă 20.000-50.000 lei: navigația în "
                    "zone nepermise și nerespectarea Avizelor către navigatori. Poluarea apelor naționale "
                    "navigabile cu hidrocarburi costă 20.000-40.000 lei."
                ),
                sources=(
                    'Care este sancțiunea pentru navigația în zone nepermise a unei nave?',
                    'amendă de la 20.000 la 50.000 lei',
                    'Care este sancțiunea pentru nerespectarea ”Avizelor către navigatori”?',
                    'Care este sancțiunea pentru poluarea apelor naționale navigabile cu hidrocarburi?',
                    'amendă de la 20.000 la 40.000 lei',
                ),
            ),
            Statement(
                text=(
                    "Cine se pune de-a curmezișul controlului plătește după cât de departe merge: "
                    "20.000-30.000 lei pentru refuzul de a se supune controlului ANR, și 30.000-50.000 "
                    "lei pentru refuzul de a se supune cercetărilor sau de a pune la dispoziție "
                    "documentele și datele necesare investigării."
                ),
                sources=(
                    'Cum se sancționează refuzul de a se supune controlului ANR',
                    'amendă de la 20.000 la 30.000 lei',
                    'Cum se sancționează refuzul de a se supune cercetărilor întreprinse de ANR sau de a pune la dispoziția ANR documentele și datele necesare investigării:',
                    'amendă de la 30.000 la 50.000 lei',
                ),
            ),
            Statement(
                text=(
                    "Cea mai mare amendă e pentru tăcere: 40.000-50.000 lei dacă nu anunți evenimentele "
                    "de navigație ale propriei nave, adică abordaje, coliziuni, incendii, poluare sau "
                    "scufundare."
                ),
                sources=(
                    'Care este sancțiunea pentru neanunțarea de către conducătorul unei nave cu privire la evenimentele de navigație ale propriei nave cum ar fi: abordaje, coliziuni, incendii, poluare, scufundare?',
                    'amendă de la 40.000 la 50.000 lei',
                ),
            ),
            Statement(
                text=(
                    "Sunt infracțiuni faptele care lovesc în siguranța navigației: schimbarea poziției, "
                    "scoaterea din funcțiune, avarierea gravă sau distrugerea unui semnal de navigație; "
                    "împiedicarea personalului navigant în atribuțiile de serviciu; blocarea șenalului "
                    "navigabil, a unei dane sau a bazinului portuar cu neexecutarea ordinului de "
                    "deblocare. Ultrajul împotriva personalului operativ al căpităniei e infracțiune dacă "
                    "persoana e în exercițiul funcțiunii, iar luarea în stăpânire a unei platforme fixe, "
                    "dacă s-a produs prin violență sau amenințare cu violența. Preluarea fără drept a "
                    "comenzii unei nave se agravează dacă a fost făcută pentru a devia nava de la "
                    "itinerarul său."
                ),
                sources=(
                    "Care din următoarele fapte constituie infracțiune?",
                    "schimbarea poziției, scoaterea din funcțiune, avarierea gravă sau "
                    "distrugerea unui semnal de navigație",
                    "Care dintre următoarele fapte constituie infracțiune?",
                    "împiedicarea îndeplinirii atribuțiilor de serviciu ale personalului "
                    "navigant",
                    "Ce reprezintă blocarea șenalului navigabil a unei dane sau a bazinului "
                    "portuar și neexecutarea ordinului căpitanului portului privind măsurile de "
                    "deblocare?",
                    "Ultrajul săvârșit împotriva personalului operativ al căpităniei portului, "
                    "constituie infracțiune?",
                    "da, dacă persoana se află în exercițiul funcțiunii",
                    "Luarea în stăpânire a unei platforme fixe sau exercitarea controlului "
                    "asupra acesteia constituie infracțiune?",
                    "da, dacă s a produs prin violență ori amenințare cu violența",
                    "Care este cauza agravantă a infracțiunii de preluare fără drept a comenzii "
                    "sau controlului unei nave?",
                    "dacă fost făcută în scopul devierii navei de la itinerarul său",
                    "infracțiune",
                ),
            ),
            Statement(
                text=(
                    "Sunt contravenții exploatarea în scopuri comerciale a unei ambarcațiuni de agrement "
                    "neautorizate în acest sens, care e contravenție la regimul siguranței navigației, și "
                    "folosirea unui nume, număr de identificare sau port de înmatriculare neaprobat de "
                    "autoritatea competentă. Nepredarea documentului de atestare în 5 zile de la "
                    "comunicarea deciziei de suspendare sau anulare se sancționează cu 100-500 lei."
                ),
                sources=(
                    'Exploatarea în scopuri comerciale a ambarcațiunii de agrement, cu excepția celor autorizate în acest sens, constituie:',
                    'contravenție la regimul siguranței navigației',
                    'Folosirea de către proprietar a unui nume, număr de identificare sau port de înmatriculare ce nu a fost aprobat de Autoritatea competentă constituie:',
                    'contravenție',
                    'Nepredarea la ANR în termen de 5 zile de la comunicarea deciziei de suspendare sau anulare a documentului de atestare se sancționează:',
                    'amendă de la 100 la 500 lei',
                ),
            ),
            Statement(
                text=(
                    "Termenul care revine e de 15 zile: pentru înmatricularea navei de către proprietar, "
                    "pentru depunerea actului de naționalitate la căpitănie după suspendarea dreptului de "
                    "arborare a pavilionului, și pentru transcrierea contractului de construcție în "
                    "registrul navelor în construcție, socotit de la începerea construcției."
                ),
                sources=(
                    'Care este termenul în care proprietarul unei nave are obligația de a înmatricula nava?',
                    '15 zile',
                    'Care este termenul limită pentru depunerea la căpitănia portului a actului de naționalitate de către proprietar în cazul suspendării dreptului de arborare a pavilionului român?',
                    '15 zile de la comunicarea deciziei',
                    'În ce termen trebuie transcris contractul de construcție al unei nave în registrul de evidență al navelor în construcție?',
                    '15 zile de la începerea construcției',
                ),
            ),
            Statement(
                text=(
                    "Contravențiile se constată de personalul împuternicit al ANR, și pot fi constatate "
                    "atât fără oprirea navei, cât și în lipsa contravenientului, dacă fapta e probată cu "
                    "un mijloc tehnic."
                ),
                sources=(
                    'Constatarea contravențiilor și aplicarea sancțiunilor prevăzute de HG 1704/2024 se face de către:',
                    'personalul împuternicit al ANR',
                    'Se poate constata contravenția fără oprirea navei?',
                    'Se poate constata contravenția în lipsa contravenientului?',
                    'da, dacă săvârșirea contravenției este probată cu un mijloc tehnic',
                ),
            ),
        ),
    ),
    Card(
        # Twenty-nine questions, thirteen of them asked only at class D — the Danube
        # regulation is class D's own ground.
        theme="regulament-dunare",
        statements=(
            Statement(
                text=(
                    "R.N.D. își definește termenii larg: prin navă înțelege navele de navigație "
                    "interioară, inclusiv ambarcațiunile mici și bacurile, precum și aparatele plutitoare "
                    "și navele maritime. Ambarcațiune mică e orice navă sub 20 m, în afară de cele care "
                    "remorchează, împing sau duc cuplat nave care nu sunt ambarcațiuni mici, de bacuri și "
                    "de navele autorizate să transporte peste 12 pasageri."
                ),
                sources=(
                    'Ce se înţelege prin "navă" în sensul R.N.D. ?',
                    'Navele de navigaţie interioară, inclusiv ambarcaţiunile mici şi bacurile, precum şi aparatele plutitoare şi navele maritime',
                    'Ce se înţelege prin “ambarcaţiune mică”, în sensul R.N.D. ?',
                    'Orice navă cu lungimea corpului mai mică de 20 m, cu excepţia ambarcaţiunior mici care remorchează, împing sau duc cuplat nave, altele decât ambarcaţiuni mici, precum şi a bacurilor şi navelor autorizate să transporte mai mult de 12 pasageri',
                ),
            ),
            Statement(
                text=(
                    "O navă e în marș când nu e ancorată, nici legată la mal, nici eșuată; e în "
                    "staționare când e ancorată sau legată la mal, direct ori indirect. Ziua ține de la "
                    "răsăritul la apusul soarelui, noaptea de la apus la răsărit, iar amonte e sensul "
                    "spre izvor."
                ),
                sources=(
                    'Ce se înţelege prin "marş" în sensul R.N.D. :',
                    'Când o navă, un material plutitor asamblat sau o instalaţie plutitoare, nu este direct, nici în ancoră, nici legată la mal şi nici eşuată',
                    'Ce se înţelege prin termenul de "în staţionare" folosit în R.N.D. ?',
                    'O navă, un material plutitor asamblat sau o instalaţie plutitoare atunci când este, în mod direct sau indirect ancorată sau legată la mal',
                    'Ce se înţelege prin termenul "zi" folosit în R.N.D ?',
                    'Perioada cuprinsă între răsăritul şi apusul soarelui',
                    'Ce se înţelege prin termenul de “noapte” în sensul R.N.D. ?',
                    'Perioada cuprinsă între apusul şi răsăritul soarelui',
                    'Amonte pe calea navigabilă este sensul :',
                    'Spre izvor',
                ),
            ),
            Statement(
                text=(
                    "Pe apele maritime și pe apele învecinate accesibile navelor maritime se aplică "
                    "COLREG 1972, nu R.N.D."
                ),
                # The one class C question in this theme: it marks where the Danube
                # regulation stops and the sea rules begin.
                sources=(
                    'Tuturor navelor aflate în largul mării ori pe toate apele învecinate accesibile navelor maritime li se aplică prevederile:',
                    'COLREG-1972.',
                ),
            ),
            Statement(
                text=(
                    "În categoria ecluzelor intră și avanporturile: suprafețele de apă dinăuntrul și "
                    "dinafara sasurilor, care servesc legării la cheu, înșiruirii și așteptării navelor. "
                    "Ordinea ecluzării e navele administrației, cele plecate în misiuni excepționale, "
                    "cele avariate grav — care au prioritate fără să stea la rând — pompierii și salvarea "
                    "aflate în drum spre accident, apoi celelalte nave."
                ),
                sources=(
                    'În categoria ecluzelor intră:',
                    'ecluzele şi suprafeţele de apă dinăuntrul şi dinafara sasurilor ecluzelor care servesc legării la cheu, înşiruirii şi aşteptării navelor –avanporturile de ecluză',
                    'Ordinea ecluzării este',
                    'navele administraţiei; navele care sunt plecate pentru îndeplinirea unor misiuni excepţionale; navele avariate grav au prioritate la ecluzare în faţa celorlalte, fără a sta la rând; navele de pompieri şi de salvare aflate în drum spre locul accidentului; celelalte nave',
                ),
            ),
            Statement(
                text=(
                    "Înainte de pătrunderea în ecluză parâmele se țin din scurt și nimic din echipament "
                    "nu depășește limitele navei; ancorele se ridică la post și se asigură; navele cu "
                    "stație de emisie-recepție stau comutate pe canalul ecluzei. La trecerea prin "
                    "avanport și la intrare viteza se micșorează atât cât oprirea sigură să fie posibilă "
                    "cu cabluri, parâme și alte măsuri potrivite, ca să fie exclusă coliziunea cu porțile "
                    "ecluzei sau cu dispozitivele de protecție."
                ),
                # Two questions share the stem 'Înainte de pătrunderea în ecluză' with
                # nearly the same answer; only one is cited, and the other is its duplicate.
                sources=(
                    'Înainte de pătrunderea în ecluză',
                    'la bordul ambarcaţiunilor parâmele trebuie ţinute din scurt şi componentele echipamentului trebuie să nu depăşească limitele navei',
                    'În zona de ecluzare:',
                    'ancorele trebuie să fie ridicate la post şi asigurate',
                    'În zona de ecluze navele care sunt dotate cu o instalaţie de emisie–recepţie',
                    'trebuie să aibă comutat la recepţie canalul ecluzei',
                    'La trecerea prin avanporturi de ecluză şi la intrarea în ecluze, navele trebuie:',
                    'să-şi micşoreze viteza, pentru a fi posibilă în orice condiţii o oprire sigură cu ajutorul cablurilor de oţel, parâmelor şi a altor măsuri potrivite, astfel încât să fie exclusă o coliziune cu porţile ecluzei sau cu dispozitivele de protecţie.',
                ),
            ),
            Statement(
                text=(
                    "În camera ecluzei nava se ține între limitele marcate pe pereți, trancheții trebuie "
                    "să plutească dacă nu sunt strâns fixați de navă, iar ambarcațiunile mici păstrează "
                    "suficientă distanță față de celelalte nave."
                ),
                sources=(
                    "În camerele ecluzei",
                    "navele trebuie să se menţină în interiorul limitelor, în cazul în care pe "
                    "pereţii ecluzelor sunt marcate graniţe/limite",
                    "În camerele ecluzei:",
                    "se folosesc trancheţi care trebuie să fie flotabili, dacă nu sunt legaţi "
                    "strâns-fixaţi de navă",
                    "În timpul ecluzării, în camerele ecluzelor",
                    "ambarcaţiunile mici trebuie să păstreze suficientă distanţă faţă de alte "
                    "nave",
                ),
            ),
            Statement(
                text=(
                    "În timpul ecluzării e interzis să urce sau să coboare pasageri fără permisiunea "
                    "personalului ecluzei, e interzisă curățarea și măturarea navelor și a corpurilor "
                    "flotante, și e interzisă folosirea propulsiei mecanice și a instalației de guvernare "
                    "prova după legarea navei, până la permisiunea de ieșire — cu excepția unor fracțiuni "
                    "scurte de timp, din motive de siguranță. Depășirea e interzisă în zona de ecluzare; "
                    "se trece pe lângă navele care așteaptă numai când urmează să fii ecluzat înainte sau "
                    "ca să ocupi un spațiu liber aflat la îndemână."
                ),
                # Three of these share the stem 'În timpul ecluzării, în camerele
                # ecluzelor', so only the answers tell them apart.
                sources=(
                    'În timpul ecluzării, în camerele ecluzelor',
                    'este interzis să se lase pasagerii să urce sau să coboare fără permisiunea personalului ecluzei',
                    'este interzisă curăţarea şi maturarea navelor şi corpurilor flotante',
                    'este interzis să se folosească după legarea navei și până la permiterea ieşirii atât propulsia mecanică, cât și instalaţia de guvernare prova; din motive de siguranţă acest lucru este permis numai pentru fracţiuni scurte de timp',
                    'În zona de ecluzare este interzisă depăşirea, navele au voie să treacă pe lângă alte nave care aşteaptă în ecluză:',
                    'numai atunci când ambarcaţiunile trebuie să fie ecluzate înainte sau pentru a se poziţiona în spaţiile libere aflate la îndemână',
                ),
            ),
            Statement(
                text=(
                    "Personalul de supraveghere a ecluzelor poate emite ordine care completează regulile "
                    "sau se abat de la ele, din motive de siguranță și de fluidizare a circulației, iar "
                    "conducătorii trebuie să le urmeze în zona de ecluzare."
                ),
                sources=(
                    'Din motive de siguranţă şi fluidizare a circulaţiei, pentru accelerarea traversării şi pentru exploatarea în plin a ecluzelor',
                    'personalul de supraveghere a ecluzelor poate emite ordine care să completeze regulile iniţial prevăzute sau care se abat de la acestea, iar conducătorii navelor trebuie să urmeze aceste ordine în zona de ecluzare',
                ),
            ),
            Statement(
                text=(
                    "Conducătorii navelor remorcate se conformează ordinelor conducătorului de convoi, "
                    "iar angajarea cu o navă în intervalele dintre unitățile unui convoi remorcat e "
                    "interzisă. Trecerile înguste se parcurg în timpul cel mai scurt posibil, iar mărcile "
                    "care indică linia maximă de încărcare le poartă toate navele fluviale, în afară de "
                    "micile ambarcațiuni."
                ),
                # Four yes/no questions: the stems carry the facts and the bare 'Da' answers
                # nothing on its own, so only the qualified answer is cited.
                sources=(
                    'Conducătorii navelor remorcate trebuie să se conformeze ordinelor conducătorului convoiului ?',
                    'Este interzis a se angaja cu o navă în intervalele dintre unităţile unui convoi remorcat ?',
                    'Toate navele trebuie să treacă în timpul cel mai scurt posibil trecerile înguste ?',
                    'Toate navele fluviale trebuie să aibă mărci care indică linia maximă de încărcare ?',
                    'Da, exclusiv micile ambarcaţiuni',
                ),
            ),
            Statement(
                text=(
                    "Pentru evitarea unui pericol iminent conducătorul ia toate măsurile cerute de "
                    "împrejurări, chiar dacă se îndepărtează de la dispozițiile R.N.D., și poate lua "
                    "orice măsură de precauție ca să nu pună în pericol viața persoanelor sau să provoace "
                    "pagube altor nave, chiar dacă regulamentul nu prevede nimic special."
                ),
                # Both answers are the bare 'Da', which fixes nothing; the stems carry the
                # rule.
                sources=(
                    'Pentru evitarea unui pericol iminent, conducătorii trebuie să ia toate măsurile cerute de împrejurări, chiar dacă se îndepărtează de la dispoziţiile R.N.D.?',
                    'În scopul evitării de a pune în pericol viaţa persoanelor sau de a provoca pagube altor nave, conducătorii pot lua toate măsurile de precauţie, chiar dacă nu sunt prevăzute dispoziţii speciale în R.N.D. ?',
                ),
            ),
        ),
    ),
    Card(
        # Fifteen questions: the signals that call for help, and what the boat must
        # carry to give it.
        theme="semnale-de-pericol-si-salvare",
        statements=(
            Statement(
                text=(
                    "Semnalul de pericol din Codul Internațional de Semnale este „N.C”."
                ),
                sources=(
                    'Care este semnalul de pericol din Codul Internaţional de Semnale?',
                    '"N.C"',
                ),
            ),
            Statement(
                text=(
                    "Mai trec drept semnale de pericol fuzeele sau faclele de mână care produc lumină "
                    "roșie, un pavilion având deasupra sau dedesubt o bulă ori un obiect asemănător, și "
                    "mișcările lente și repetate de sus în jos ale brațelor întinse lateral."
                ),
                # Two questions share the stem 'Care poate fi considerat semnal de
                # pericol?', so the answers are what tell them apart.
                sources=(
                    'Care poate fi considerat semnal de pericol?',
                    'fuzee sau facle de mână care produc lumină roşie.',
                    'un pavilion având deasupra sau dedesubt o bulă sau un obiect asemănător.',
                    'Ce este semnalul de pericol dat cu braţele?',
                    'mişcări lente şi repetate de sus în jos a braţelor întinse lateral.',
                ),
            ),
            Statement(
                text=(
                    "Semnele aprobate transmise prin sisteme de radiocomunicații sunt semnale de pericol; "
                    "semnalele transmise de SART-urile mijloacelor de salvare sunt însă doar semnale de "
                    "atragere a atenției."
                ),
                # The two sit in one statement on purpose: read apart they are easy to swap,
                # and the bank asks each with the other as a distractor.
                sources=(
                    'Ce semnificaţie au semnele aprobate transmise prin sisteme de radiocomunicaţii?',
                    'sunt considerate semnale de pericol.',
                    'Ce semnificaţie au semnalele transmise de SART-urile mijlocelor de salvare?',
                    'sunt considerate semnale de atragere a atenţiei.',
                ),
            ),
            Statement(
                text=(
                    "Din armamentul de salvare din inventarul bărcii fac parte vestele de salvare, "
                    "colacii de salvare, trusa cu medicamente și butoiașul cu apă potabilă. Saula "
                    "„ține-te bine” se întâlnește la bărcile de salvare."
                ),
                # Five questions open with almost the same words about the boat's inventory,
                # so the answers carry the content; the saula question has a C and a D
                # spelling.
                sources=(
                    'veste de salvare',
                    'colaci de salvare',
                    'trusa cu medicamente',
                    'butoias cu apă potabilă',
                    'Saula "tin-te bine" se întâlnește la :',
                    'bărcile de salvare',
                    'Saula "tin-te" bine se intalneste la :',
                    'barcile de salvare',
                ),
            ),
            Statement(
                text=(
                    "Vesta de salvare e mijlocul individual de salvare din inventarul ambarcațiunii: "
                    "scoate la suprafață persoana căzută în apă chiar în stare de inconștiență și îi "
                    "menține gura deasupra nivelului apei."
                ),
                sources=(
                    'Vesta de salvare este:',
                    'mijloc individual de salvare care face parte din inventarul ambarcațiunii',
                    'Vesta de salvare asigura:',
                    'ieșirea la suprafață a persoanei căzute în apă, chiar în stare de inconștiență, și menține gura acesteia deasupra nivelului apei',
                ),
            ),
        ),
    ),
    Card(
        # What is left after stage 4e sent twenty-four questions home. These still do
        # not share a subject, so the card teaches only where a rule exists and
        # leaves the isolated facts to the drill.
        theme="vocabular-si-principii",
        statements=(
            Statement(
                text=(
                    "Regulamentul nu scutește nava, comandantul sau armatorul de urmările unei neglijențe "
                    "în aplicarea lui ori în luarea măsurilor cerute de buna practică marinărească. "
                    "Prevederile COLREG 1972 se aplică tuturor navelor aflate în largul mării și pe apele "
                    "învecinate accesibile navelor maritime."
                ),
                # The bare 'nu.' answers two different questions in this theme, so it is not
                # cited; the stems carry the rule.
                sources=(
                    'Când este exonerată o navă, comanantul sau armatorul de consecinţele unei neglijenţe sau de neluarea tuturor măsurilor cerute de o bună practică marinărească?',
                    'dispoziţiile Regulamentului nu scutesc nava, comandantul sau armatorul de consecinţele unei neglijenţe oarecare în ceea ce priveşte aplicarea Regulamentului sau în ceea ce priveşte luarea tuturor măsurilor cerute de o bună practică marinărească.',
                    'Dispoziţiile Regulamentului scutesc nava, comandantul sau armatorul de consecinţele unei neglijenţe oarecare în ceea ce priveşte aplicarea Regulamentului sau în ceea ce priveşte luarea tuturor măsurilor cerute de o bună practică marinărească?',
                    'Căror nave li se aplică prevederile Colreg-1972?',
                    'tuturor navelor aflate în largul mării ori pe toate apele învecinate accesibile navelor maritime.',
                ),
            ),
            Statement(
                text=(
                    "Prescripțiile speciale stabilite de autoritatea competentă pentru rade, porturi, "
                    "fluvii, lacuri și căi de navigație interioară accesibile navelor maritime rămân în "
                    "picioare: Regulamentul nu le împiedică aplicarea, dar ele trebuie să fie cât mai "
                    "conforme cu el."
                ),
                sources=(
                    'Cum influenţează prevederile Regulamentului prescripţiile speciale referitoare la navigaţia în rade, porturi, pe fluvii, lacuri sau căi de navigaţie interioară accesibile navelor maritime?',
                    'dispoziţiile regulamentului nu trebuie să împiedice aplicarea prescripţiilor speciale stabilite de către autoritatea competentă, dar asemenea prescripţii speciale trebuie să fie cât mai conforme cu prezentele reguli.',
                    'Dispozițiile Regulamentului împiedică aplicarea prescripțiilor speciale stabilite de către autoritatea competentă referitoare la navigația în rade, porturi, pe fluvii, lacuri sau căi de navigaţie interioară accesibile navelor maritime?',
                ),
            ),
            Statement(
                text=(
                    "Manevra de evitare a unei coliziuni se execută hotărât, din timp și conform bunei "
                    "practici marinărești; dacă împrejurările permit, schimbarea de drum sau de viteză "
                    "trebuie să fie destul de mare ca să fie percepută imediat de orice navă care o "
                    "observă vizual sau pe radar, iar trecerea să se facă la o distanță de siguranță."
                ),
                sources=(
                    'Cum trebuie să se execute o manevră pentru evitarea unei coliziuni?',
                    'hotărât, din timp şi conform cu buna practică marinărească.',
                    'Cum trebuie să se execute schimbările de drum şi/sau de viteză pentru evitarea ueni coliziuni?',
                    'dacă împrejurările permit, să fie destul de mare, pentru a putea fi percepută imediat de orice navă care o observă vizual sau cu radarul.',
                    'Manevra de evitare între nave se va efectua astfel încât să permită trecerea la:',
                    'o distanţă de siguranţă.',
                ),
            ),
            Statement(
                text=(
                    "Viteza de siguranță e aceea care permite acțiunea corectă și eficace pentru "
                    "prevenirea unei coliziuni și oprirea navei pe o distanță potrivită împrejurărilor și "
                    "condițiilor."
                ),
                sources=(
                    'Pentru a se putea acţiona corect şi eficace pentru prevenirea unei coliziuni şi pentru ca nava să poată fi oprită pe o distanţă corespunzătoare împrejurărilor şi condiţiilor, se impune menţiunea de a naviga cu:',
                    'viteză de siguranţă.',
                ),
            ),
            Statement(
                text=(
                    "În șenal sau într-o cale navigabilă îngustă se navighează cât mai aproape de "
                    "marginea exterioară din dreapta, atunci când se poate; benzile de separație se "
                    "întretaie pe cât posibil perpendicular față de direcția generală a traficului."
                ),
                sources=(
                    'Cum se navigă în şenal sau cale navigabilă îngustă?',
                    'cât mai aproape posibil de marginea exterioară din dreapta şenalului sau căii de acces respective, atunci când aceasta se poate face.',
                    'Cum trebuie să întretaie o navă benzile de separaţie, când este obligată să o facă?',
                    'pe cât posibil perpendicular faţă de direcţia generală a traficului.',
                ),
            ),
            Statement(
                text=(
                    "Schiul nautic pe căile navigabile interioare e permis numai în zonele stabilite și "
                    "marcate, la fel ca orice activitate în care persoanele sunt trase de o ambarcațiune. "
                    "Cine nu e pregătit să opereze o barcă de mare viteză nu ar trebui să încerce fără "
                    "instruire prealabilă și fără o aplicație practică alături de un conducător "
                    "experimentat: pierderea controlului poate duce la accidente grave."
                ),
                sources=(
                    'Schiul nautic pe căile navigabile interioare este permis',
                    'numai în zonele stabilite şi marcate, acest lucru fiind valabil şi pentru activităţi în care persoanele sunt trase de o ambarcaţiune fără schiuri nautice sau pe altfel de obiecte',
                    'O persoană care nu este pregătită pentru operarea unei bărci de mare viteză',
                    'nu ar trebui să încerce să conducă fără o instruire prealabilă şi o aplicaţie practică cu un conducător experimentat sau un dealer, pierderea controlului ar putea avea ca rezultat accidente grave',
                ),
            ),
            Statement(
                text=(
                    "Ambarcațiunile mici care navigă izolat, convoaiele remorcate și formațiunile în "
                    "cuplu compuse numai din ambarcațiuni mici sunt obligate să nu jeneze mișcările și "
                    "manevrele celorlalte nave. Conducătorul care se află lângă o navă avariată ale cărei "
                    "persoane sunt în pericol, sau care poate deveni un obstacol pentru navigație, dă "
                    "asistență imediat, în măsura în care nu-și pune în pericol propria navă."
                ),
                # Both class D only.
                sources=(
                    'Ambarcaţiunile mici care navigă izolat şi convoaiele remorcate sau formaţiunile în cuplu compuse numai din ambarcaţiuni mici, sunt obligate :',
                    'Să nu jeneze mişcările şi manevrele celorlalte nave',
                    'Ce obligaţii aveţi dacă sunteţi conducătorul unei nave şi vă găsiţi în apropierea altei nave avariate, ale cărei persoane sunt în pericol sau nava poate deveni un obstacol pentru navigaţie ?',
                    'În măsura în care nu puneţi în pericol siguranţa propriei nave, daţi asistenţă imediat',
                ),
            ),
            Statement(
                text=(
                    "Un sunet lung emis pe vizibilitate bună înseamnă „Atenție”. Nava în pericol care "
                    "cere ajutor arată ziua un semnal vizual: agită circular un pavilion sau orice alt "
                    "obiect asemănător."
                ),
                # Both class D only.
                sources=(
                    'Emiterea de către o navă a unui semnal fonic lung pe vizibilitate bună are semnificaţia de :',
                    'Atenţie',
                    'Navele care sunt în pericol şi cer ajutor, ce semnal vizual arată ziua ?',
                    'Agită circular un pavilion sau orice alt obiect asemănător',
                ),
            ),
            Statement(
                text=(
                    "Mațagonirea e operațiunea de îndepărtare a ruginii și a stratului de vopsea de sub "
                    "care iese rugina. A doua mână de vopsea nu se dă până nu s-a uscat prima, iar "
                    "obiectele din alamă și bronz nu se piturează."
                ),
                # The bare 'nu' answers both of the last two, so it fixes nothing and is not
                # cited; each stem carries its own rule.
                sources=(
                    'Mațagonirea reprezintă:',
                    'operațiunea de îndepărtare a ruginii și a stratului de vopsea sub care se afla rugina.',
                    'Se poate da a doua mana de vopsea, dacă nu s-a uscat primul strat de vopsea?',
                    'Obiectele din alama și bronz se piturează?',
                ),
            ),
            Statement(
                text=(
                    "Cu cât viteza de deplasare e mai mare, cu atât presiunea apei pe pana cârmei e mai "
                    "mare, iar schimbarea direcției mai rapidă."
                ),
                # The one uncited question in this theme with a rule behind it rather than
                # an isolated fact. It sits here because the classifier leaves it here; the
                # rudder statements it belongs beside are in the manoeuvring card.
                sources=(
                    "Cu cât viteza de deplasare este mai mare",
                    "presiunea apei asupra penei cârmei va fi mai mare, iar schimbarea "
                    "direcţiei mai rapidă",
                ),
            ),
        ),
    ),
)


def statement_classes(statement: Statement, questions, theme: str) -> tuple[str, ...]:
    """The classes of the questions this statement teaches, sorted.

    Matching is by normalized whole field — stem or correct answer — the same
    convention every catalogue uses, and **restricted to the card's own
    theme**. Without that restriction a short quote reaches across the bank:
    "Da" is the correct answer to thirteen questions in five themes, so a
    statement resting on it inherited class C from a rope question and shipped
    a class D rule to a class C candidate. The audit could not see it — both
    its rules check the quote, not the derivation.

    Derived rather than declared: a wrong class here now needs a wrong
    question inside the very theme the card names.
    """
    wanted = {normalize_key(source) for source in statement.sources}
    classes: set[str] = set()
    for question in questions:
        if question.get("theme") != theme:
            continue
        fields = (question["q"], question["opts"][question["correct"]])
        if any(normalize_key(field) in wanted for field in fields):
            classes.update(question["classes"])
    return tuple(sorted(classes))


def payload(questions) -> dict[str, object]:
    """The cards shaped for the page: prose and classes, no quotes.

    The interface never shows a source, so shipping every one of them would
    grow the page for nothing. The audit holds the quotes; the page holds
    what the candidate reads.
    """
    return {
        "cards": [
            {
                "theme": card.theme,
                "statements": [
                    {
                        "text": statement.text,
                        "classes": list(statement_classes(statement, questions, card.theme)),
                        # Absent, not null, when there is nothing to draw: the
                        # page tests for the key and most statements have none.
                        **({"drawing": statement.drawing} if statement.drawing else {}),
                    }
                    for statement in card.statements
                ],
            }
            for card in THEORY
        ],
    }
