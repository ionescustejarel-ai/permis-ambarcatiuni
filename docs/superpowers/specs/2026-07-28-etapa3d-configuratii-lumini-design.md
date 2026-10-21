# Etapa 3d — configurațiile de lumini pe tipuri de navă

**Data:** 2026-07-28
**Etapa precedentă:** 3c (arcurile de vizibilitate), fuzionată în `main`
**Spec-părinte:** `2026-07-25-permis-ambarcatiuni-design.md` §10.2

## 1. Ce rezolvă

Etapa 3c a desenat *ce acoperă* fiecare lumină. Aceasta desenează *ce poartă fiecare navă*: unde stau luminile pe corp și în ce ordine pe verticală. E ultima bucată vizuală a băncii și cea mai încâlcită, fiindcă sursa amestecă descrieri complete cu trimiteri și cu instrucțiuni care nu descriu nicio dispunere.

## 2. Câte întrebări atinge

Măsurat pe banca livrată, dintre cele 75 de întrebări despre lumini: 10 sunt deja legate de arcuri (etapa 3c), 12 sunt distanțe de vizibilitate, 30 sunt reguli, iar **23 descriu ce poartă o navă**. Dintre acestea:

- **12 configurații distincte, legate de 18 întrebări**
- **5 întrebări rămân nedesenate**, fiecare cu motivul scris (§5)

| Configurație | Clasă | Lumini |
|---|---|---|
| Navă cu vele în marș | C | borduri + pupa |
| Navă cu vele, felinar combinat | C | borduri și pupa reunite într-un felinar, la catarg |
| Navă cu vele, lumini suplimentare | C | roșu deasupra verde, pe tot orizontul, la catarg |
| Navă cu propulsie mecanică, mică | C | alb pe tot orizontul + borduri |
| Navă care traulează, nu în marș | C | verde deasupra alb pe tot orizontul + catarg mai sus și înapoi |
| Navă împinsă înainte | C | borduri, la extremitatea prova |
| Navă remorcată | C | borduri + pupa |
| Navă remorcată la ureche | C | pupa + borduri la extremitatea prova |
| Capacitate de manevră redusă, nu în marș | C | roșu-alb-roșu pe verticală |
| Capacitate de manevră redusă, la ancoră | C | roșu-alb-roșu pe verticală + lumină de ancoră la pupa |
| Navă cu vele în marș | **D** | roșu deasupra verde la catarg + borduri + pupa |
| Ambarcațiune mică, lumină albă | **D** | o singură lumină albă pe tot orizontul |

**Nava cu vele are două răspunsuri.** La clasa C poartă lumini de bord și lumină de pupa; la clasa D poartă în plus **două lumini suprapuse, roșu peste verde, la catarg**. Aceeași navă, două regulamente — la fel ca sistemele de balizaj la 3b, dar de data asta pe cel mai comun tip de navă din bancă. Filtrarea pe clasă nu e o rafinare, e condiția ca figura să nu mintă.

**Două configurații diferite au aceleași lumini.** Nava cu vele în marș și nava remorcată poartă amândouă borduri plus pupa. Nu e o eroare de catalog: banca le întreabă separat, deci rămân intrări separate, fiecare cu citatele ei. Un candidat care observă că sunt identice a învățat ceva adevărat.

## 3. Proiecția

**Nava văzută din profil, cu prova la dreapta.** E singura vedere care arată deodată cele două lucruri pe care le dă sursa: **ordinea pe verticală** — „două lumini suprapuse, lumina superioară roșie", „trei lumini în poziție verticală" — și **poziția față-spate** — „la extremitatea prova", „cât mai aproape posibil în pupa", „la catarg".

Luminile de bord se desenează ca o pereche mică la prova, cu culorile lor, fiindcă din profil una singură ar fi vizibilă în realitate. Asta e o licență de desen și se declară ca atare: la 3c există deja figura care arată corect arcul fiecăreia.

Orientarea — prova la dreapta — e convenție de prezentare, nu regulament.

## 4. Catalogul

`src/caa/lights.py`, același tipar ca `signals.py`, `figures.py` și `arcs.py`, construit pe `caa.catalogue`: date Python, auditate la build, emise în pagină ca `<script id="lights" type="application/json">`.

O configurație e o **listă de lumini plasate**, nu un desen:

```python
Config(
    id="vele-in-mars-D",
    label="Navă cu vele în marș",
    lights=(
        Placed(colours=("red",),         station=MAST, level=1),
        Placed(colours=("green",),       station=MAST, level=0),
        Placed(colours=("red", "green"), station=SIDE),
        Placed(colours=("white",),       station=STERN),
    ),
    sources=(<citatele întrebărilor ei, verbatim>,),
)
```

`station` spune unde pe corp, cu exact cinci valori, fiecare fiind ceva ce sursa chiar spune:

| `station` | Ce spune banca |
|---|---|
| `MAST` | „la catarg”, „la măr”, „în partea superioară a catargului” |
| `SIDE` | „luminile din borduri”, fără altă precizare |
| `BOW` | „la extremitatea prova” |
| `STERN` | „în pupa”, „de la pupa” |
| `ANY` | **nimic** — „într-un loc corespunzător”, „în poziţie verticală” |

**`ANY` e adăugarea pe care măsurarea a impus-o.** La cinci configurații sursa dă numai ordinea pe verticală și niciodată poziția față-spate. Fără `ANY`, fiecare dintre acele lumini ar fi trebuit pusă la catarg — o poziție pe care banca n-o afirmă. Se desenează pe un catarg scurt la mijloc, iar panoul declară că numai ordinea pe verticală e regulament.

**`SIDE` și `BOW` sunt distincte fiindcă banca le distinge.** Nava remorcată poartă „luminile din borduri”; cea remorcată la ureche le poartă „la extremitatea prova”. Desenate la fel, cele două configurații ar ieși identice și exact diferența pe care o întreabă examenul ar dispărea din imagine.

**`colours` e un tuplu, nu o culoare**, din trei motive citite în sursă: felinarul combinat e o singură lanternă care arată roșu, verde și alb deodată; luminile de bord sunt o pereche desenată ca un singur marcaj; iar lumina de ancoră **n-are culoare declarată nicăieri în bancă** — verificat pe toate cele șase întrebări care o pomenesc — deci se desenează într-un ton neutru, ca sectoarele fără culoare de la 3c. Tuplu gol înseamnă „sursa nu spune”.

`level` dă ordinea pe verticală în aceeași stație, **0 fiind cea de jos** și valoarea implicită acolo unde sursa nu suprapune nimic. Așa „roșu deasupra verde” e un dat din catalog, nu o coincidență de coordonate scrise de mână.

Un câmp `note` poartă calificativul pe care sursa îl pune și desenul nu-l poate arăta: „dacă este posibil” la luminile din borduri ale navei mici cu propulsie mecanică, „poate reuni” la felinarul combinat, și cele trei situații deosebite (legată la mal, cu rame, sub 7 m) care împart aceeași unică lumină albă.

Luminile sunt aceleași pe care le catalogă etapa 3c. 3d le **compune**, nu le redescrie: culorile și numele vin de acolo.

### 4.1 Legarea

Ca la 3b și 3c: citatul se compară cu **enunțul întreg sau cu răspunsul corect întreg**, prin `caa.catalogue.resolve`. Ambele apar — unele întrebări descriu luminile în enunț și cer tipul de navă, altele invers. Catalogul nu conține id-uri de întrebări.

## 5. Ce nu se desenează, și de ce

Cinci întrebări rămân nedesenate. Fiecare intră în `NOT_A_CONFIG` cu motivul scris, ca auditul să ceară o decizie dacă banca se schimbă.

**Două descriu o pregătire, nu o dispunere:**

> „…să fie pregătiră să arate o lanternă electrică sau un felinar cu lumină albă." (navă cu rame)
> „trebuie să fie gata să arate în orice moment o lanternă electrică sau un felinar aprins cu o lumină albă." (navă cu vele sub 7 m)

Tocmai absența unei lumini fixe e răspunsul. O siluetă cu o lumină albă desenată pe ea ar spune contrariul.

**Una arată lumina numai la nevoie:**

> „Trebuie să arate o lumină albă obişnuită vizibilă din toate părţile la apropierea altor nave” (barcă cu rame, clasa D)

Calificativul „la apropierea altor nave” e **singurul lucru** care desparte răspunsul corect de distractorul de alături, care e aceeași lumină fără nicio condiție. O siluetă cu lumina desenată pe ea ar arăta tocmai răspunsul greșit. La clasa C, aceeași barcă e exclusă din același motiv — aceeași regulă, la ambele clase.


**Două trimit la configurații pe care banca nu le descrie:**

> „luminile unei nave cu propulsie mecanică în marş plus o lumină galbenă cu sclipiri…" (navă cu pernă de aer)
> „Luminile unei ambarcaţiuni mici autopropulsate ce navigă izolat şi a cărei lungime nu depăşeşte 20 m" (ambarcațiune care remorchează)

Verificat pe bancă: **singura configurație de navă cu propulsie mecanică pe care sursa o dă e cea pentru ambarcațiuni mici**, „mai mare de 7 m și viteza peste 7 Nd". Trimiterea navei cu pernă de aer nu are restricție de mărime, iar configurația generală — catarg, borduri, pupa — există în COLREG dar **nu în banca aceasta**. A doua trimitere nu are bază nici măcar aproximativ.

De aceea **nu există mecanism de compunere**: ar fi o unealtă fără nicio piesă de prins. Dacă o ediție viitoare a băncii adaugă configurația de bază, atunci merită construit — și auditul va cere decizia, fiindcă întrebarea va fi tot în excepții.

## 6. Auditul

Două reguli blocante, construite pe `caa.catalogue` ca celelalte trei cataloage: `config-source` și `config-coverage`.

Recunoscătorul cere trei lucruri deodată. Întâi, textul să fie **despre lumini** (`lumin|felinar`). Apoi, să întrebe ce poartă o navă:

```
ce lumini | luminile purtate de | luminile suplimentare | poate purta
| ce felinare | trebuie sa poarte | trebuie sa arate | trebuie sa aiba
```

sau enunțul să înceapă prin a enumera lumini (`doua|trei|patru|luminile …`). Și, în fine, o **gardă negativă** pe distanțele de vizibilitate și pe definițiile de arc, care aparțin etapei 3c.

**Cerința „despre lumini” nu e de prisos.** Fără ea, recunoscătorul prinde **32 de întrebări, nu 23**: „trebuie să poarte” și „trebuie să aibă” apar la fel de firesc despre semnele de zi, vestele de salvare, nodurile, mărcile de încărcare și echipamentul de semnalizare sonoră. Prima măsurare a ratat asta fiindcă rulase numai peste cele două teme de lumini — și un recunoscător care depinde de temă e exact ce nu vrem, câtă vreme clasificatorul de teme are deja greșeli cunoscute.

Recunoscătorul caută întrebări care cer ce poartă o navă:

```
ce lumini | luminile purtate de | luminile suplimentare | poate purta
| ce felinare | trebuie sa poarte | trebuie sa arate | trebuie sa aiba
```

sau un enunț care începe prin a enumera lumini (`doua|trei|patru|luminile …`), cu **gardă negativă** pe distanțele de vizibilitate și pe definițiile de arc, care aparțin etapei 3c.

Măsurat pe banca livrată: prinde **exact cele 23**, dintre care 18 legate și 5 în excepții. Zero neclasificate, zero suprapunere cu cataloagele anterioare.

## 7. Interfața

**Panou pe tema *Lumini de navigație***, sub panoul de arcuri adăugat la 3c, cu configurațiile **clasei curente**. **Figura lângă întrebare**, în drill, **după răspuns**. **Nimic în simulare.**

**Tabela `THEME_PANELS` trebuie să accepte mai multe panouri pe temă.** Azi mapează o temă la un singur constructor, iar etapa 3c a înregistrat deja `arcPanel` pe exact această temă: înregistrat naiv, panoul de configurații l-ar înlocui în tăcere pe cel de arcuri. Valoarea devine o listă, iar ecranul adaugă ce primește, în ordine — arcurile întâi, fiindcă ele explică luminile din care sunt făcute configurațiile. Tot niciun `if` nou. Ca la 3c, un panou care n-are ce arăta nu se randează deloc. Aici ambele clase au conținut — **clasa C are 10 configurații (14 întrebări), clasa D are 2 (4 întrebări)** — dar regula rămâne, fiindcă o ediție viitoare poate goli una dintre ele.

## 8. Verificarea

**Python.** Forma catalogului, cele două reguli de audit demonstrate că mușcă, rezolvarea citatelor pe întrebări reale, comparație **la octet** cu banca, și verificarea că nicio configurație nu declară două lumini în aceeași stație pe același nivel.

**Node.** Așezarea luminilor: pentru fiecare configurație, ordinea pe verticală într-o stație și repartiția pe stații, calculate din catalog — funcția pură care traduce `station` plus `level` în coordonate.

**Browser.** Se extrag pozițiile și culorile efectiv randate și se confirmă, pentru fiecare configurație: **roșul deasupra verdelui** unde sursa o cere, verdele la tribord, luminile la prova acolo unde banca spune „la extremitatea prova". Plus: panoul filtrat pe clasă — **nava cu vele arată diferit la C față de D**, ceea ce e proba centrală a etapei — figura absentă în simulare, 390 px fără overflow, temă întunecată peste pragul WCAG AA, parcurgere cu tastatura, consolă curată.

## 9. În afara scopului, deliberat

- **Cele 4 întrebări din §5.**
- **Distanțele de vizibilitate** (12 întrebări în mile marine) — o cifră, nu o imagine.
- **Cele 30 de reguli** din tema luminilor — text, nu dispunere.
- **Vederea din prova.** Ar arăta ambele lumini de bord deodată, dar ar pierde poziția față-spate și n-ar putea arăta lumina de pupa. Profilul dă mai mult din ce cere banca.

## 10. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/lights.py` | **nou** — catalogul, excepțiile, recunoscătorul, `resolve`, `payload` |
| `src/caa/audit.py` | +2 reguli blocante |
| `src/caa/cli.py` | scrie `config` pe întrebări |
| `src/caa/app.py` | emite `<script id="lights">` |
| `src/caa/assets/logic.js` | `lightPlacement(config)` — pură |
| `src/caa/assets/lights.js` | **nou** — construcția SVG |
| `src/caa/assets/ui.js` | panoul temei, figura din drill |
| `src/caa/assets/app.css` | panoul |
| `tests/caa/test_lights.py`, `tests/js/logic.test.js` | testele |
