# Etapa 4c — teoria pentru blocul de navigație

**Data:** 2026-07-29
**Etapa precedentă:** 4b (teoria pentru temele cu desen), fuzionată în `main` la `c5155c8`
**Decizie de scope (proprietarul proiectului, 2026-07-29):** lotul = blocul de navigație — compas și drumuri, reguli de drum, meteo și hidrologie, hărți și poziție, vizibilitate redusă. Plierea panourilor de media e aprobată ca **etapă separată, după 4c**. Fixul de clasificare de mai jos a fost raportat și aprobat („da, dar mai verifică înainte") — verificarea e în §2.

## 1. Întâi datoriile, apoi conținutul

Ledger-ul fixează ordinea, și primele două task-uri nu sunt teorie:

- **Testul pe `THEME_PANELS` / `build(theme)`** — azi, revenirea constructorilor la `build()` fără argument ar goli panoul de teorie pe toate temele cu carduri, cu toate cele 347 de teste verzi. Browserul e singurul care ar observa. Se închide **primul**, ca orice card nou din 4c să se nască păzit.
- **Conul de la vele-și-motor** — datoria scrisă în spec-ul 4b §1: plasamentul conului diferă pe clase („la prova" la C, „cât mai sus posibil" la D), nu e în desen, nu e în etichetă, și e chiar discriminatorul întrebării. Devine un card mic pentru „Semne și forme ziua", cu **două afirmații despărțite pe clase** — exact modelul „Boturile" de la 4a. Cardul retras la review-ul 4b a fost retras pentru că redescria desenul; ăsta spune singurul lucru pe care desenul nu-l spune.

Regulile câștigate la 4b se aplică din prima zi: **citează enunțul când răspunsul e scurt** („da"/„nu" apar și în acest lot: parâmele de bumbac/vegetale) și **clasele se derivă numai în tema cardului** (deja în cod).

## 2. Fixul de clasificare, măsurat pe toată banca

Citirea lotului a găsit **trei coliziuni de sens** în tabelul de la 3e, plus vocabular lipsă. Fiecare a fost măsurată pe toate cele 603 de întrebări, cu replay-ul fidel al lui `_match_theme` (0 nepotriviri față de build înainte de orice schimbare):

| Defect | Ce prinde greșit | Fix |
|---|---|---|
| `curent` (meteo) | „manevre **curente**", „uzul **curent**", „parâmă denumită **curent**" — sensul de parâmă; plasează 8 întrebări, 0 corecte | se scoate; meteo rămâne pe `vant\|valuri\|meteo\|…` |
| `longitudin` (hărți) | „planul **longitudinal**" — termen de construcție; trage chila, coastele, varangele, ruliul la hărți | `latitudine\|longitudine` — banca folosește doar formele `latitudinea`/`longitudinea`, pe care le conține |
| `ceat` (vizibilitate) | „mai **înceată**" — de-asta o întrebare despre presiunea apei pe pana cârmei zăcea la vizibilitate redusă | `\bceat` |
| vocabular lipsă | mandar, palanc, vinci, volte, matelotaj n-au niciun tipar; chila, coastele, varangele, ruliul nici atât | parâme: `+palanc\|mandar\|vinci(ul\|uri)\|volt(ele\|elor)\|matelotaj`; construcție: `+chil(a\|ei)\|coaste\|varang\|ruliu` |

Formele flexionate sunt cele **măsurate în bancă** (`vinciul`/`vinciuri`, `voltele`/`voltelor`), nu forme de dicționar — prima schiță cu `vinci\b` nu se potrivea cu nimic. `tangaj` apare o singură dată, ca opțiune a întrebării de ruliu, și nu mută nimic — nu se adaugă. Capcanele verificate: `chil(a|ei)` nu prinde „e**chil**ibru", `coaste` nu prinde „coasta" (malul, la balizaj), `latitudine` nu prinde „longitudinal".

**Rezultat: 16 mutări, fiecare citită, toate corecte.** 8 meteo→parâme (dispozitivele de matelotaj și parâmele), 4 hărți→construcție (chila, coastele, varangele, ruliul), 2 vocabular→construcție (elementele de osatură), 1 vocabular→parâme (voltele), 1 vizibilitate→vocabular (întrebarea de cârmă, care n-avea ce căuta acolo). Tabelul celor 16 devine **test de regresie** în `test_themes.py`.

> **Măsurat și respins:** genitivul `carm(a|ei)` la manevră. Mută 6: 4 corect, dar 2 **greșit** — „Orificiul rotund prin care trece axul cârmei" (etambreul) e întrebare de construcție al cărei enunț conține „cârmei", și fixul ar smulge-o din tema ei. Aceeași lecție ca promovarea pe poziție de la 3e: o mutare în plus nu justifică două stricate. Rămâne documentat aici și în comentariul tabelului.

> **Corectat după implementare:** două afirmații de mai sus s-au dovedit greșite
> la execuție. `curent` plasează **8** întrebări greșit, nu 9 — a noua mutare
> (voltele) o face tiparul nou `volt(ele|elor)`. Iar tema semnelor de zi **nu
> avea nicio intrare** în `THEME_PANELS`, nu `[figurePanel]`: cele trei desene
> ale ei nu fuseseră vizibile niciodată, din `c651ffc`. Reparația a scos la
> iveală că `figurePanel` filtra doar pe clasă, deci pe a doua temă ar fi arătat
> toate geamandurile ca marcaje ale temei — vezi `1349648`.

## 3. Consecința mutărilor: cardurile de la 4a se extind

Parâmele primesc 9 întrebări noi (palanc, mandar, vinci, volte, matelotaj, bumbac/vegetale), construcția 6 (chila, coastele, varangele, ruliul, osatura) — teme care **au deja teorie**, dar ale căror carduri n-au auzit de subiectele astea. Fără extindere, panoul de teorie al parâmelor ar tăcea exact despre întrebările proaspăt sosite.

Se adaugă ~4–6 afirmații: dispozitivele de ridicat (palanc = macarale cu raiuri prin care trece curentul; mandar = macara fixă; vinci = ax orizontal pentru virat) și voltele; osatura (chila longitudinală, coastele și varangele transversale, ruliul în jurul axei longitudinale). Materialul de bumbac la manevre curente diferă pe clase (C: vegetale și sintetice **da**; D: bumbac **nu**) — afirmații despărțite, iar sonda de class-folding le veghează automat, fiindcă iterează tot `THEORY`.

## 4. Lotul, după fix

| Temă | Întrebări | Clase |
|---|---|---|
| Compas și drumuri | 26 | toate C |
| Reguli de drum | 21 | 20 C, 1 D |
| Meteo și hidrologie | 13 | 6 C, 7 comune |
| Hărți și poziție | 13 | 11 C, 2 comune |
| Vizibilitate redusă | 10 | 9 C, 1 D |
| **Total** | **83** | |

După 4c (cu mutările și cardul conului): teorie pentru **~430 din 603 — ~71% din bancă**. Cifra exactă o dă build-ul; auditul impune trasabilitatea, nu volumul.

Compasul e integral clasa C — clasa D nici nu vede tema, deci cardul nu are ce împărți. Reguli de drum și vizibilitate au câte **o singură** întrebare D (autopropulsata cedează nepropulsatei; semnalizarea de noapte purtată și ziua) — fiecare devine afirmație proprie, altfel un candidat D ar învăța reguli care nu-i apar la examen și invers.

## 5. Conținutul

Aceeași disciplină ca 4a/4b: afirmații în proza mea, citate verbatim la octet (enunț întreg sau răspuns corect întreg), clase derivate în tema cardului, `theory-source`/`theory-theme` blocante, review adversarial de conținut la fiecare task.

Ținte de lucru din structura măsurată:

- **Compas și drumuri (~8–10):** drumul = unghi de la o direcție nord la axul prova; relevmentul = de la nord la linia de vizare; cele patru nord-uri (adevărat, magnetic, compas, giro) dau patru drumuri; relevmentul **prova** se măsoară de la axul prova, nu de la nord; linia de credință materializează axul longitudinal; carturile (cardinal, intercardinal, inter-intercardinal, intermediar); cadranele și valorile de drum; N=000/E=090/S=180/W=270; relevment constant la navă care se apropie = pericol de coliziune.
- **Reguli de drum (~7–9):** cine cedează (mecanica → vele → pescuit → capacitate redusă → nestăpâne); între vele: vânt din borduri diferite → cedează cea cu vânt din babord; același bord → cea din vânt; depășitorul cedează, definiția depășirii (>22°5 înapoia traversului); nava cu drum liber își menține drumul și viteza și manevrează abia când devine evident că cealaltă n-o face; abaterile de la Regulament permise la pericol; cinci sunete scurte la îndoială. Afirmația D separată: autopropulsata cedează nepropulsatei.
- **Meteo și hidrologie (~4–6):** vântul din prova/dinaintea traversului micșorează viteza și dă derivă; din travers dă derivă; la acostare forța vântului și curentului se folosește în ajutorul manevrei; la „om la apă" fără vizibilitatea derivei — prova pe direcția inversă a rezultantei; fenomenele care influențează manevra.
- **Hărți și poziție (~5–7):** latitudinea = arc de meridian de la ecuator, longitudinea = arc de ecuator de la Greenwich; regula emisferelor (spre N crește latitudinea în emisfera nordică etc.); harta marină și scara; poziția prin relevmente la repere costiere (faruri); sonda măsoară adâncimea, lochul viteza.
- **Vizibilitate redusă (~4–5):** cui i se aplică regulile; viteza de siguranță; veghea permanentă vizuală și auditivă; semnalul comun — un sunet lung + două scurte la ≤2 minute (vele, capacitate redusă, stânjenite de pescaj — trei enunțuri, același răspuns: **se citează enunțurile**); sub 12 m — semnal eficace la ≤2 minute; semnalele se emit zi și noapte, înăuntrul sau lângă zonă. Afirmația D separată: semnalizarea de noapte purtată și ziua pe ceață/ninsoare.
- **Semne și forme ziua (2):** conul cu vârful în jos la vele-și-motor — la C „la prova, în locul cel mai vizibil"; la D „cât mai sus posibil" (formularea exactă o dă banca; despărțite pe clase).

Numerele nu sunt fixate de spec. Teoria nu redescrie desenul și nu citează întrebările rătăcite în temă de pasul pe opțiuni (o întrebare de separare a traficului care stă la meteo printr-un distractor rămâne fără citat — nu e material de card meteo).

## 6. Interfața

Șase intrări noi/modificate în `THEME_PANELS`, teoria prima:

| Temă | Azi | După |
|---|---|---|
| Compas și drumuri | — | `[theoryPanel]` |
| Reguli de drum | — | `[theoryPanel]` |
| Meteo și hidrologie | — | `[theoryPanel]` |
| Hărți și poziție | — | `[theoryPanel]` |
| Vizibilitate redusă | — | `[theoryPanel]` |
| Semne și forme ziua | **nimic** | `[theoryPanel, figurePanel]` |

Nicio funcție nouă: `theoryPanel(theme)` servește orice temă, cum a fost proiectat la 4a. Extinderea cardurilor de parâme/construcție nu schimbă interfața.

## 7. Verificarea

**Python.** Invariantele 4a/4b (formă, octet, temă, derivare, payload) acoperă cardurile noi prin construcție; sonda de class-folding iterează tot `THEORY` și orice candidat nou pică build-ul până e citit și trecut în listă cu motiv. Nou: testul de regresie pe cele 16 mutări (temă așteptată pentru fiecare întrebare mutată) + un test că `\bceat` nu prinde „înceată" și `latitudine` nu prinde „longitudinal". Lint-ul existent pe tabel (`test_no_pattern_is_written_in_a_form_the_bank_never_uses`) rămâne blocant.

**Node.** Testul `THEME_PANELS`/`build(theme)` din Task 0 (căderea lui se demonstrează întâi: revenirea la `build()` trebuie să-l pice **pe el**, nu doar să pice ceva); `statementsForClass` pe temele noi în `panels.test.js`.

**Browser (controller).** Panoul pe toate temele noi, primul, strâns implicit, filtrat pe clasă; compasul invizibil la clasa D; afirmația D unică apare doar la D pe reguli de drum și vizibilitate; conul arată plasamente diferite pe clase; nimic în simulare; 390 px; consolă curată.

**Mutații** din script pe stare comisă, cu motivul căderii citit — regula casei.

## 8. În afara scopului, deliberat

- **Genitivul `carm(a|ei)`** — măsurat, respins (§2). Rătăcirile rămase produse de pasul pe opțiuni sunt limita declarată la 3e, nu defect nou.
- **Plierea panourilor de media** — etapă proprie, aprobată, imediat după 4c.
- **Temele rămase pentru 4d** (~173 de întrebări): vocabular (54), regulament Dunăre (29), legislație (26), motor (25), manevră cu motor (19), semnale de pericol și salvare (15), motovehicule nautice (5).

## 9. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/themes.py` | cele 4 rânduri de tipar + comentariul cu `carm(a|ei)` respins |
| `src/caa/theory.py` | +6 carduri (5 navigație + conul), +extinderile parâme/construcție |
| `src/caa/assets/ui.js` | intrările în `THEME_PANELS` |
| `tests/caa/test_themes.py` | regresia celor 16 mutări + coliziunile |
| `tests/caa/test_theory.py` | actualizarea numerelor de carduri/afirmații |
| `tests/js/panels.test.js` | testul `THEME_PANELS`/`build(theme)` + temele noi |
