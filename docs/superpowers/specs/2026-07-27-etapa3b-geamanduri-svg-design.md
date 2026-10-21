# Etapa 3b — geamanduri și semne de zi

**Data:** 2026-07-27
**Etapa precedentă:** 3a (motorul audio), fuzionată în `main`
**Spec-părinte:** `2026-07-25-permis-ambarcatiuni-design.md` §10.2

## 1. Ce rezolvă

Banca descrie marcajele în cuvinte: *„piturat în dungi orizontale dispuse de sus în jos: negru-galben-negru"*. Candidatul memorează un șir de culori fără să fi văzut vreodată obiectul. La cardinale, **dificultatea întreagă e ordinea dungilor** — Est și Vest se confundă exact acolo — iar o imagine rezolvă fix asta.

Se desenează doar ce cere banca. Cardinala Sud nu apare nicăieri în cele două liste, deci nu se desenează: aceeași disciplină ca la etapa 3a, unde al treisprezecelea semnal sonor a fost exclus pe față fiindcă sursa nu-i dă durata.

## 2. Câte întrebări atinge

**12 figuri distincte, legate de 14 întrebări.** Recunoscătorul din §4 le găsește pe toate paisprezece, cu **zero fals-pozitive** pe banca de azi.

| Sistem | Figuri | Clasă |
|---|---|---|
| IALA | cardinal E, V, N; semn de vârf tribord și babord regiunea A; pericol izolat | C |
| Dunăre | bifurcație, stânga, dreapta | D |
| Semne de zi | cilindru negru, con cu vârful în jos, flamură de supraveghere | C și D |

**Cele două sisteme de balizaj sunt disjuncte pe clase** — verificat: nicio întrebare de balizaj nu e comună. Asta contează, fiindcă ele se contrazic: în sistemul dunărean stânga e **conică verde**, iar în IALA regiunea A babordul e **cilindru roșu**. O figură fără sistemul declarat ar fi greșită pentru una dintre clase.

**Semnele de zi, în schimb, traversează clasele.** Conul cu vârful în jos e întrebat la C de două ori și la D o dată, cu trei formulări diferite. Un semn de zi e același semn în ambele sisteme.

## 3. Catalogul

`src/caa/figures.py`, același tipar ca `signals.py`: date Python, auditate la build, emise în pagină ca `<script id="figures" type="application/json">`.

```python
Figure(
    id="cardinal-est",
    label="Cardinal Est",
    system=IALA,
    body=Body(shape=PILLAR, bands=("black", "yellow", "black")),
    light=None,
    sources=("negru-galben-negru;",),
)
```

### 3.1 Legarea se face pe enunț SAU pe răspuns

Aici etapa 3b diferă de 3a. La audio, tiparul sonor stătea întotdeauna în răspunsul corect. Marcajele nu: unele întrebări **descriu figura în enunț** și cer înțelesul —

> „Un cilindru negru reprezintă semnul purtat de o navă:" → *stânjenită de pescajul său.*

— iar altele o descriu în răspuns:

> „Marcajul de pericol izolat are ca semn de vârf:" → *doua bule suprapuse de culoare neagra.*

Potrivirea compară deci citatul cu **enunțul întreg** și cu **răspunsul corect întreg**, ambele normalizate cu `normalize_key`. Pe fragment ar prinde întrebări vecine.

Ca la 3a, catalogul **nu conține id-uri de întrebări**: sunt hash-uri de conținut și s-ar rupe la rebuild. Clasele fiecărei figuri ies din întrebările pe care le prinde citatul ei, deci filtrarea pe clasă e derivată, nu declarată.

### 3.2 Se desenează exact ce descrie citatul

Cardinalele apar cu **corpul vopsit și fără semn de vârf** — banca le întreabă doar dungile. Semnele de vârf sunt figuri separate, fiindcă banca le întreabă separat, pentru marcajele laterale și pentru pericolul izolat.

Nu se completează desenul cu ce mai poartă în realitate o geamandură cardinală. Nu ar fi regulament inventat — conurile cardinale sunt standard IALA — dar ar fi conținut fără citat în spate, iar auditul din §4 nu l-ar mai putea verifica.

### 3.3 Schema

| Câmp | Valori |
|---|---|
| `system` | `iala`, `dunare`, `day-shape` |
| `body.shape` | `pillar`, `cylinder`, `sphere`, `cone-up`, `cone-down`, `two-spheres`, `pennant` |
| `body.bands` | culori, **de sus în jos**; un singur element pentru corp monocrom |
| `body.border` | culoare sau absent — încadrează **corpul**; niciun marcaj de azi nu-l folosește |
| `body.device` | însemn purtat în centrul corpului, cu forma, umplerea și chenarul lui — doar flamura |
| `light` | `{colour, rhythm}` sau absent; singurul ritm din bancă e `intermitenta` |

## 4. Auditul

Două reguli blocante, la fel ca la 3a: constatarea oprește build-ul și `questions.json` nu se scrie.

**R1 — fiecare citat există.** Fiecare `source` se regăsește printre enunțurile sau răspunsurile corecte ale băncii. Zero potriviri = ANR a schimbat textul → build picat.

**R2 — fiecare figură e acoperită.** Orice întrebare recunoscută ca descriind un marcaj e fie legată de o intrare, fie trecută în `NOT_A_FIGURE` cu motiv.

Recunoscătorul, aplicat pe enunț plus răspunsul corect normalizate:

```
(piturat|vopsit)\w*\s+(in|cu)\b | semn de varf | de forma (conic|cilindric|sferic)
| \bun (con|cilindru|romb)\b | arboreaza
```

Măsurat pe banca livrată: prinde **exact cele 14**, niciuna în plus. Spre deosebire de audio, nu are nevoie de nicio excepție — dar `NOT_A_FIGURE` există oricum, fiindcă o ediție viitoare poate aduce o formulare care seamănă fără să fie desenabilă, iar atunci decizia trebuie scrisă, nu presupusă.

O plasă mai largă a fost măsurată și respinsă: cerând doar formă plus culoare, prindea 17, dintre care 7 fals-pozitive — raze de vizibilitate și lumini purtate de navă, care aparțin etapei 3c.

## 5. Randarea

`figureBands(figure)` stă în `logic.js` și întoarce benzile **ordonate de sus în jos**, cu culoare și înălțime relativă. Ordinea e conținutul examinat, deci ea trebuie să fie testabilă: testul *„cardinalul Est citește negru, galben, negru de sus în jos"* pică dacă ordinea se inversează.

`src/caa/assets/figures.js` primește figura și benzile calculate, citește conturul din `figure.body.shape` — și, când există, însemnul interior din `figure.body.device.shape` — și construiește nodurile SVG. Nu decide nimic: formele vin din catalog, ordinea din `figureBands`. O formă pe care nu o cunoaște aruncă, ca să nu deseneze tăcut altceva.

**Zero fișiere.** SVG-ul se construiește în pagină, ca și sunetul. Nicio imagine, niciun font.

**Lumina intermitentă se animă**, cu perioadă declarată drept constantă de prezentare — banca spune „intermitentă", nu dă frecvența. Animația respectă `prefers-reduced-motion`, media query pe care pagina îl are deja: sub el, lumina rămâne aprinsă.

## 6. Interfața

**Panou pe tema *Geamanduri și balizaj***, cu figurile clasei curente. **Figura lângă întrebare**, în drill, **după răspuns** — înainte ar da răspunsul. **Nimic în simulare.**

Fiecare figură poartă eticheta ei și, sub ea, sistemul din care face parte. Un candidat de clasa C nu trebuie să vadă niciodată geamandura conică verde dunăreană alături de marcajele IALA, iar filtrarea derivată din §3.1 se ocupă de asta.

**Opt din cele paisprezece întrebări stau azi în alte teme** — trei în *Construcția ambarcațiunii*, una în *Motor și propulsie*, una în *Semnale de pericol*. Nu blochează nimic: legarea se face pe text, nu pe temă, deci figura apare lângă întrebare oriunde ar sta ea. Panoul rămâne pe tema de balizaj. Clasificatorul de teme merită o trecere separată, în afara acestei etape.

## 7. Verificarea

**Python.** Forma catalogului, cele două reguli de audit demonstrate că mușcă, rezolvarea citatelor la întrebări reale, comparație **la octet** cu banca — normalizarea șterge punctuația și e oarbă la ghilimele, lecție plătită la 3a.

**Node.** Ordinea benzilor pentru fiecare figură cu corp vopsit, forma conturului, absența luminii unde citatul nu o dă.

**Browser.** Se extrag atributele SVG efectiv randate și se confirmă, pentru fiecare figură, formele, culorile și **ordinea de sus în jos**. Plus: panoul filtrat corect pe clasă, figura absentă în simulare, `prefers-reduced-motion` oprește clipirea — și parcurgerea **cu tastatura**, nu doar cu click-uri, fiindcă la 3a exact asta a ascuns un buton inaccesibil.

## 8. În afara scopului, deliberat

- **Cardinala Sud** — banca nu o cere.
- **Luminile de navă** — etapa 3c, alt randor: siluetă, poziții, arcuri de vizibilitate.
- **Razele de vizibilitate** (13 întrebări cu distanțe în Mm) — o cifră, nu o imagine.
- **Fișiere imagine.**

## 9. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/figures.py` | catalogul, `NOT_A_FIGURE`, recunoscătorul, `resolve`, `payload` |
| `src/caa/audit.py` | R1, R2 |
| `src/caa/cli.py` | scrie `figure` pe întrebări |
| `src/caa/app.py` | emite `<script id="figures">` |
| `src/caa/assets/logic.js` | `figureBands(figure)` |
| `src/caa/assets/figures.js` | construcția SVG |
| `src/caa/assets/ui.js` | panoul temei, figura din drill |
| `src/caa/assets/app.css` | panoul, animația luminii |
| `tests/caa/test_figures.py`, `tests/js/logic.test.js` | testele |
