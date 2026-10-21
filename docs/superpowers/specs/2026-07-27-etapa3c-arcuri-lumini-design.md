# Etapa 3c — arcurile de vizibilitate ale luminilor

**Data:** 2026-07-27
**Etapa precedentă:** 3b (geamanduri și semne de zi), fuzionată în `main`
**Spec-părinte:** `2026-07-25-permis-ambarcatiuni-design.md` §10.2

## 1. Ce rezolvă

Banca definește fiecare lumină de navigație prin **arcul pe care se vede**: *„o lumină albă aşezată deasupra axului longitudinal al navei, arătând o lumină neîntreruptă pe un arc de orizont de 225°"*. Candidatul memorează numere — 225, 135, 112°5 — fără să-și poată imagina ce acoperă. Un sector desenat în jurul navei le face evidente dintr-o privire, și tot el arată de ce lumina de pupa și cea de remorcaj au același arc dar culori diferite.

## 2. Câte întrebări atinge

**5 figuri, legate de 10 întrebări, toate clasa C.** Recunoscătorul din §5 le prinde pe toate zece, cu **zero fals-pozitive** și **zero suprapunere** cu catalogul de marcaje de la 3b.

| Figură | Arc | Culoare |
|---|---|---|
| Lumina de catarg | 225°, câte 112°5 în fiecare bord de la prova | albă |
| Lumina de pupa | 135°, câte 67°5 în fiecare bord | albă |
| Luminile de bord | 112°5 fiecare | verde la tribord, roșie la babord |
| Lumina de remorcaj | 135°, ca cea de pupa | galbenă |
| Vizibilă pe tot orizontul | 360° | — |

## 3. Proiecția

**Nava văzută de sus, cu prova în sus.** E singura proiecție în care un arc înseamnă ceva: în profil, 225° nu se vede. Sectorul se desenează în jurul unei siluete simple, iar relevmentele se măsoară din prova, în sensul acelor de ceasornic.

Această orientare — prova în sus, tribordul în dreapta — e o convenție de prezentare, nu un fapt din regulament, și se declară ca atare.

## 4. Catalogul

`src/caa/arcs.py`, același tipar ca `signals.py` și `figures.py`: date Python, auditate la build, emise în pagină ca `<script id="arcs" type="application/json">`.

```python
Arc(
    id="lumina-de-catarg",
    label="Lumina de catarg",
    sectors=(Sector(start=247.5, end=112.5, colour="white"),),
    sources=(<cele două citate, verbatim>,),
)
```

Un sector se dă prin **relevmente din prova, în grade, sens orar, de la 0 la 360** — tribordul spre valori mici, babordul spre mari. Deschiderea e `(end - start) mod 360`, iar `0` înseamnă cerc întreg.

O singură convenție, nu două. Relevmentele cu semn (±112,5) se citesc mai ușor din sursă, dar atunci lumina de pupa se scrie 112,5 → −112,5 trecând prin spate, iar regula de trecere prin zero devine două cazuri în loc de unul. Cu 0–360, singura subtilitate e modulo, și e în funcția testată.

Citit din sursă: *„câte 67°5 în fiecare bord"* pentru lumina de pupa devine 112,5 → 247,5 (adică 180 ± 67,5), iar *„câte 112°5"* pentru catarg devine 247,5 → 112,5, care trece prin prova.

### 4.1 Legarea

Ca la 3b: citatul se compară cu **enunțul întreg sau cu răspunsul corect întreg**, normalizate. Ambele apar: unele întrebări descriu arcul în enunț și cer numele luminii, altele cer definiția și o dau în răspuns. Catalogul nu conține id-uri de întrebări.

Fiecare figură are **exact două citate** — cele două întrebări care o privesc, în cele două sensuri.

### 4.2 Contradicția din bancă, tratată pe față

Banca dă **două arcuri diferite pentru lumina de catarg**:

> „…arătând o lumină neîntreruptă pe un arc de orizont de **22°5** astfel ca să arate 22°5 înapoia traversului fiecărui bord este:" → *lumina de catarg.*

> „Ce se înţelege prin expresia «lumină de catarg»?" → *…pe un arc de orizont de **225°**, astfel ca să arate 22°5 înapoia traversului fiecărui bord.*

225° e valoarea din COLREG și din al doilea răspuns; 22°5 e o cifră pierdută la tipar. **Figura arată 225°.**

Verificat pe sursă că greșeala **nu schimbă răspunsul la examen**: distractorii primei întrebări sunt *lumina de pupa* și *lumina de remorcaj*, ambele la pupa și ambele la 135°, deci discriminantul e „deasupra axului longitudinal", nu arcul.

Ca figura să nu pară că se contrazice cu enunțul, catalogul poartă un **avertisment legat de citatul respectiv**:

```python
caveats={
    # Cheia e citatul ÎNTREG, exact cum apare în bancă — nu un fragment.
    "Lumina albă aşezată deasupra axului longitudinal al navei, arătând o "
    "lumină neîntreruptă pe un arc de orizont de 22°5 astfel ca să arate 22°5 "
    "înapoia traversului fiecărui bord este:": (
        "Enunțul are aici o cifră pierdută la tipar: arcul e 225°, cum scrie "
        "și răspunsul celeilalte întrebări din aceeași listă. Răspunsul corect "
        "nu se schimbă."
    ),
}
```

Nota apare **numai** lângă acea întrebare. Textul sursei rămâne neatins, iar cheia unui avertisment trebuie să fie unul dintre citatele figurii — verificat de audit, altfel ar putea rămâne orfan la o reformulare.

## 5. Auditul

Două reguli blocante, ca la 3a și 3b, plus una nouă cerută de §4.2.

**R1 — fiecare citat există** printre enunțurile sau răspunsurile corecte ale băncii.

**R2 — fiecare întrebare despre un arc e acoperită** sau trecută în `NOT_AN_ARC` cu motiv.

**R3 — fiecare avertisment se leagă de un citat al figurii sale.** O cheie care nu e sursă a figurii e o notă care nu se va afișa niciodată.

Recunoscătorul, aplicat pe enunț plus răspuns normalizate:

```
arc de (orizont|cerc|\d) | pe un arc de | cate \d+ ?5? in fiecare bord
| vizibil\w* pe (tot|intreg) orizontul
```

cu o **gardă negativă** pe enunț:

```
ce lumini | luminile purtate de | lumini(le)? suplimentare | poate purta | la ce distanta
```

Măsurat pe banca livrată: prinde **exact cele 10**, respinge 5 — trei configurații de navă, care aparțin etapei 3d, și două distanțe de vizibilitate. Fără garda negativă prindea 12, cu 3 fals-pozitive.

`NOT_AN_ARC` rămâne gol azi. **Lumina cu sclipiri nu e o excepție**: recunoscătorul nu o prinde deloc, fiindcă sursa îi dă un ritm — *„120 de sclipiri pe minut sau mai mult"* — și niciun arc. Nu se desenează, fiindcă un sector ar adăuga un fapt pe care sursa nu-l afirmă.

## 6. Randarea

`sectorSpan(sector)` și `sectorPath(sector, radius)` stau în `logic.js`.

**De ce e aici defectul cel mai plauzibil al etapei.** Un arc SVG cere steagul `large-arc`: peste 180° trebuie `1`, sub `0`. Pus greșit, browserul desenează **complementul** — un sector de 225° apare ca 135°, adică fix răspunsul altei întrebări din bancă. Un candidat ar învăța pe dos, iar desenul ar arăta perfect plauzibil. De aceea:

- `sectorSpan` întoarce deschiderea în grade, testabilă direct pe cele cinci figuri;
- `sectorPath` întoarce calea, iar testul verifică steagul `large-arc` pentru fiecare, inclusiv la 360°, care se desenează din două jumătăți fiindcă un arc complet cu start = end e degenerat.

`src/caa/assets/arcs.js` primește sectoarele și construiește nodurile SVG: silueta, sectoarele, gradația. Nu decide nimic.

**Zero fișiere**, ca peste tot în aplicație.

## 7. Interfața

**Panou pe tema *Lumini de navigație***, cu cele cinci figuri. Măsurat: opt din cele zece întrebări stau acolo, celelalte două la *Lumini — situații speciale*, deci panoul are un singur loc firesc. Figura apare oricum lângă întrebare indiferent de temă, fiindcă legarea se face pe text. **Figura lângă întrebare**, în drill, **după răspuns**. **Nimic în simulare.**

Sub fiecare figură, deschiderea în cifre — „225°" — fiindcă asta e ce se notează la examen; desenul o face memorabilă, textul o face exactă.

Avertismentul din §4.2 apare doar lângă întrebarea al cărei citat îl poartă, nu în panou.

Panourile se adaugă în tabela `THEME_PANELS` introdusă la 3b; nu se mai scrie niciun `if` nou.

## 8. Verificarea

**Python.** Forma catalogului, cele trei reguli de audit demonstrate că mușcă, rezolvarea citatelor pe întrebări reale, comparație **la octet** cu banca.

**Node.** Deschiderea fiecărui sector, steagul `large-arc` pentru fiecare figură, și cazul degenerat de 360°.

**Browser.** Se extrag atributele `d` ale sectoarelor randate și se confirmă unghiul efectiv desenat pentru fiecare figură — nu aspectul. Plus: panoul filtrat pe clasă, avertismentul afișat exact lângă întrebarea cu `22°5` și nicăieri altundeva, figura absentă în simulare, 390 px fără overflow, temă întunecată peste pragul WCAG AA, și parcurgere **cu tastatura**.

**Pagina construită se parsează** — garda adăugată la 3b rămâne obligatorie: un fișier nou inserat e exact felul în care o eroare de sintaxă a livrat o dată o aplicație albă cu toate testele verzi.

## 9. În afara scopului, deliberat

- **Configurațiile de lumini pe tipuri de navă** — etapa 3d. Alt randor (profil, nu plan), și date mult mai încâlcite: unele răspunsuri spun doar „să fie gata să arate o lanternă", altele trimit la luminile altei nave fără să le descrie. Acolo apare și contradicția C/D pentru nava cu vele.
- **Distanțele de vizibilitate** (12 întrebări în mile marine) — o cifră, nu o imagine.
- **Lumina cu sclipiri** — ritm, nu arc (§5).

## 10. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/arcs.py` | **nou** — catalogul, excepțiile, recunoscătorul, `resolve`, `payload` |
| `src/caa/audit.py` | +3 reguli blocante |
| `src/caa/cli.py` | scrie `arc` pe întrebări |
| `src/caa/app.py` | emite `<script id="arcs">` |
| `src/caa/assets/logic.js` | `sectorSpan`, `sectorPath` |
| `src/caa/assets/arcs.js` | **nou** — construcția SVG |
| `src/caa/assets/ui.js` | panoul temei, figura din drill, avertismentul |
| `src/caa/assets/app.css` | panoul |
| `tests/caa/test_arcs.py`, `tests/js/logic.test.js` | testele |
