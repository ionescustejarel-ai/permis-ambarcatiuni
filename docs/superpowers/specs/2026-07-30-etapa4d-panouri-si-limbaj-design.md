# Etapa 4d — panourile se pliază, iar limbajul spune ce înseamnă

**Data:** 2026-07-30
**Etapa precedentă:** 4c (teoria pentru blocul de navigație), fuzionată în `main` la `35a336d`
**Aprobări (proprietarul proiectului):** plierea panourilor de media (2026-07-29); redenumirea stării întrebărilor, filtrul pe timp și cele patru reparații din auditul de limbaj (2026-07-30).

Etapa are două jumătăți care ating același fișier și de-aia merg împreună: **cât spațiu ocupă interfața** și **ce înțelege candidatul din ea**. Nu se atinge nicio afirmație, nicio figură, niciun citat. `theory.py` rămâne neschimbat.

---

# Partea I — panourile de media

## 1. Ce rezolvă

Teoria se pliază de la 4a: costă **43 px** și se deschide cu un gest. Panourile de media nu se pliază. Măsurat în build-ul de azi, pe 390×844:

| Clasa | Tema | Panouri | Drill-ul începe la |
|---|---|---|---|
| C | Lumini de navigație | teorie 43 + arcuri 573 + configurații 1005 | **1693 px** |
| C | Semnale sonore | teorie 43 + semnale 629 | 719 px |
| C | Geamanduri și balizaj | teorie 43 + figuri 546 | 637 px |
| D | Lumini de navigație | teorie 43 + configurații 403 | 494 px |
| D | Semnale sonore | teorie 43 + semnale 629 | 719 px |
| C | Semne și forme ziua | teorie 43 + figuri 201 | 292 px |

Ecranul are 844 px. Pe tema luminilor la clasa C candidatul derulează **două ecrane pline** de diagrame înainte de prima întrebare — de fiecare dată, inclusiv a douăzecea oară, când diagramele nu-i mai spun nimic.

Ordinea teorie → media → drill rămâne. Costul ei implicit dispare: patru sumare ≈ **150 px** în loc de 1693.

## 2. Defectul găsit la măsurare: semnalele n-au filtru pe clasă

`signalPanel()` iterează `SIGNALS.signals` — toate. De-asta panoul are **exact 629 px la ambele clase**, deși banca le examinează pe seturi **complet disjuncte**:

| | Semnale examinate |
|---|---|
| Clasa C (8) | sunet scurt, sunet lung, vin la tribord, vin la babord, mașina înapoi, acord depășire, avertizare, manevră pe vizibilitate redusă |
| Clasa D (2) | două lovituri de clopot, serie de sunete foarte scurte |
| Comune | **niciunul** |

Un candidat de clasa D ascultă azi 8 semnale pe care nu le are la examen, cu cele 2 ale lui îngropate între ele.

E **a treia instanță a aceleiași clase de defect**: `arcPanel` a livrat fără filtru la 3c, `figurePanel` filtra pe clasă dar nu pe temă la 4c. Testul care ar fi prins-o **există și e bun** — `PANELS` din `panels.test.js` compară fiecare filtru cu ce întreabă banca — dar lista lui numește doar `figuresForClass`, `arcsForClass`, `configsForClass`. **Semnalele n-au intrat niciodată în listă fiindcă nu exista funcția de intrat.**

Deci reparația e în două părți, și a doua contează mai mult: `signalsForClass(examClass)` scrisă după modelul surorilor ei, **și adăugată în `PANELS`** — de unde testul existent o acoperă automat, fără test nou.

## 3. Plierea

Toate patru panourile devin `<details>` strânse, ca teoria: element nativ, fără stare, fără gestionare de taste. Titlul din `<h2>` devine textul din `<summary>`, plus numărul de elemente.

| Panou | Sumar |
|---|---|
| `figurePanel` | „Marcajele clasei tale · 6 marcaje" / „Semnele clasei tale · 2 semne" (titlul urmează tema, ca la 4c) |
| `arcPanel` | „Pe ce arc se vede fiecare lumină · 5 arcuri" |
| `configPanel` | „Ce lumini poartă fiecare navă · 10 configurații" |
| `signalPanel` | „Ascultă semnalele · 8 semnale" |

**Toate patru, nu doar cele mari.** Semnele de zi costă 201 px, dar un panou care se pliază pe trei teme și nu pe a patra e o regulă pe care candidatul o învață greșit. Uniformitatea e ea însăși funcția.

## 4. Pluralul, o dată pentru toate

`theoryPanel` alege azi între „o regulă" și „N reguli" cu un ternar scris pe loc. Patru panouri noi ar însemna cinci ternare și cinci locuri unde româna se poate strica.

Se extrage în `logic.js`, unde stă logica pură și unde testele o ating direct. Româna cere trei forme, nu două: **1** marcaj, **2–19** marcaje, **20+** *de* marcaje. Niciun panou nu ajunge azi la 20 (maximul e 10 configurații la clasa C), dar regula se scrie corect acum, cu test, fiindcă „20 marcaje" e greșeală de română și banca poate crește. Teoria trece și ea pe helper.

---

# Partea II — limbajul

Auditul de limbaj (read-only, 2026-07-30) a găsit că textele **nu sunt AI slop**: sunt concrete, active, fără umplutură. Problema e alta — **trei termeni care duc greul nu sunt definiți nicăieri**, iar unul dintre ei sună a verdict despre candidat.

## 5. „Nesigure" dispare

Cuvântul apare în bara de jos, ca titlu pe ecranul principal, ca număr mare și în feedback. Regula reală, din `logic.js`: două răspunsuri corecte în două zile diferite, expirând după 30 de zile. **Nimic din asta nu scrie în interfață**, iar „nesigur" se citește ca autoevaluare — *întrebări la care nu mă simt sigur* — nu ca stare pe care o calculează aplicația.

Cum fac alții, cercetat: chestionarele auto DRPCIV numesc lista **„întrebări greșite"** și o filtrează pe timp (azi / 7 zile / 30 de zile / tot istoricul); Anki numește stările după treaba planificatorului (*New / Learning / Review*); Quizlet folosește *Not studied / Still learning / Mastered*; Khan Academy urcă pe cinci trepte. **Niciuna nu-i spune candidatului că el e „nesigur".** Ori numesc evenimentul, ori pasul următor, ori progresul câștigat.

Decizia (proprietarul proiectului): **numim acțiunea.**

| Azi | După |
|---|---|
| „Întrebări nesigure" (titlu, ecran principal) | **„De exersat"** |
| „Nesigure" (bara de jos, titlu listă) | **„De exersat"** |
| „Nicio întrebare nesigură" | **„Nimic de exersat"** |
| „Corect. Întrebarea e sigură." | **„Corect. Întrebarea e știută."** |
| „Greșit. Întrebarea e nesigură." | **„Greșit. Rămâne la exersat."** |
| „— N deja sigure." (comune cu cealaltă clasă) | **„— N deja știute."** |

Expirarea devine firească: întrebarea *se întoarce la exersat*, nu *devine nesigură*.

**Numai textele se schimbă.** `isSafe`, `blacklist`, `unsafeByTheme` și ruta `lista-neagra` rămân cum sunt — sunt nume interne, nu ajung la candidat, iar redenumirea lor ar umfla diff-ul fără să câștige nimic.

## 6. Regula se spune, o dată, unde se vede

Sub numărul de pe ecranul principal:

> O întrebare trece la știute după două răspunsuri corecte, în două zile diferite. După 30 de zile fără s-o revezi, se întoarce la exersat.

Azi regula se predă din întâmplare, într-un singur mesaj („Corect, dar tot azi. Îți mai trebuie un răspuns corect într-o altă zi.") care apare doar dacă răspunzi corect a doua oară în aceeași zi. Cine nu nimerește situația nu află regula niciodată.

## 7. Filtrul pe timp

Peste lista de exersat, ca **vedere**, nu ca înlocuitor al mecanicii: butoane pentru *toate* / *greșite în ultimele 7 zile* / *greșite în ultimele 30 de zile*.

Asta cere un câmp nou. Starea reține azi `lastDay` — ultima zi în care ai răspuns, corect **sau** greșit — deci nu poate răspunde la „ce am greșit recent". Se adaugă `lastWrongDay`, scris în `recordAnswer` când răspunsul e greșit.

**Compatibil cu progresul deja salvat**, în ambele sensuri: `adoptProgress` trece `raw.q` mai departe ca atare, iar un câmp absent înseamnă doar că întrebarea nu apare în vederea de 7 zile. Fișierele vechi rămân valide, cele noi se citesc de versiunile vechi. `PROGRESS_VERSION` nu se schimbă.

Vederea filtrată nu schimbă ce e de exersat — schimbă doar ce se afișează. Când filtrul nu lasă nimic, ecranul o spune („Nimic greșit în ultimele 7 zile.") în loc să arate o listă goală.

## 8. Celelalte trei găuri din audit

**Numărul gol „40".** Pe ecranul principal, între cele două grupuri de teme, stă un `40` fără etichetă. În cod e `SAFETY_CONTOUR`, iar clasele CSS spun toată povestea — `sounding`, `shoal`, `clear`, `contour`: e un contur de adâncime de pe hartă, temele deasupra sunt bancuri, cele dedesubt apă liberă. **Metafora există numai în numele claselor CSS.** Capătă o etichetă care o spune, iar temele de deasupra se citesc ca fiind peste contur. Metafora nautică e vocea aplicației și rămâne; devine doar vizibilă.

**Clasa C și clasa D.** Prima decizie a candidatului, fără un cuvânt de explicație. Sursa e verificată — `sources/anr/ordin_regulament.pdf`, art. cu definițiile claselor, verbatim:

> c) **clasa C** — certificat care dă dreptul titularului să conducă ambarcaţiuni de agrement în zonele maritime care să nu depăşească o distanţă de **maximum 6 Mm faţă de ţărm**;
> d) **clasa D** — certificat care dă dreptul titularului să conducă ambarcaţiuni de agrement **pe căi navigabile interioare**.
> (2) Posesorului certificatului […] clasa D îi este **interzis a naviga în apele maritime interioare**.

Linia de sub butoane spune asta pe scurt, în cuvintele sursei: clasa C ține de mare, până la 6 Mm de țărm; clasa D ține de căile navigabile interioare. **Nu se adaugă nimic ce sursa nu spune** — nici lungimi, nici puteri de motor, nici vârste.

**Trei nume pentru examen.** Bara de jos zice „Examen", ecranul „Simulare de examen", istoricul „Ultimele simulări". Rămâne un singur cuvânt-rădăcină: bara de jos „**Simulare**", titlul ecranului „Simulare de examen · 1 / 26", istoricul „Ultimele simulări".

**Examenul de diferență nu spune cui folosește.** Butonul păstrează eticheta lui corectă, iar sursa confirmă din nou disciplina clasei **ținte** (`ordin_regulament.pdf`, verbatim):

> Clasa C […] b) deţine certificatul […] **clasa D** şi va susţine un examen de diferenţă la **COLREG** — Regulamentul internaţional pentru prevenirea abordajelor pe mare.
> Clasa D […] b) deţine certificatul […] **clasa C** şi va susţine un examen de diferenţă la **RND** — Regulamentul de navigaţie pe Dunăre.

Linia de sub buton spune cui îi folosește: cine deține deja cealaltă clasă. Se poate numi și materia, fiindcă sursa o dă — COLREG spre C, RND spre D.

---

## 9. Ce rămâne neatins

- **Conținutul**: nicio afirmație, nicio figură, niciun citat. `theory.py` neatins.
- **Mecanica siguranței**: două zile, 30 de zile, `isSafe` neschimbat. Se schimbă numele, nu regula.
- **Ordinea** teorie → media → drill.
- **Refuzul panourilor goale**: fiecare panou întoarce `null` când clasa n-are ce vedea; `signalPanel` capătă și el calea asta prin filtrul nou.
- **Sunetul**: butoanele de redare trăiesc într-un `<details>` strâns; se verifică în browser că redarea merge după deschidere.

## 10. Verificarea

**Node.** `signalsForClass` intră în `PANELS` și e acoperită de testul existent. `countLabel` și `lastWrongDay` primesc teste proprii — inclusiv pragul de 20 pentru „de", și un progres vechi fără câmpul nou, care trebuie să rămână valid. Testul de înregistrare a panourilor din 4c rămâne.

**Mutații** (script Python, `assert src.count(old) == 1`, pe stare comisă): golirea filtrului de semnale trebuie să pice testul `PANELS`; ștergerea pragului „de" trebuie să pice testul de plural; scoaterea lui `lastWrongDay` din `recordAnswer` trebuie să pice testul filtrului.

**Un lint pentru cuvântul retras.** După redenumire, „nesigur" nu mai are voie să apară în niciun text livrat candidatului. Un test citește `ui.js` și pică dacă string-ul reapare — altfel se strecoară înapoi la prima adăugare grăbită. Comentariile din cod n-au treabă cu el; lint-ul se uită la literalele care ajung în pagină.

**Browser (controller), 390 px, ambele clase.** Fiecare panou strâns implicit, cu numărul corect în sumar; drill-ul pe tema luminilor la clasa C sub 200 px; clasa D vede exact 2 semnale, clasa C exact 8; un semnal se aude după deschiderea panoului; cuvântul „nesigur" nu apare nicăieri; regula se citește sub număr; eticheta conturului se vede; filtrul de 7 zile arată gol pe un progres nou, și corect după un răspuns greșit; consolă curată; fără scroll orizontal.

## 11. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/assets/logic.js` | `countLabel`, `lastWrongDay` în `recordAnswer`, selecția pentru filtru |
| `src/caa/assets/ui.js` | `signalsForClass`; cele patru panouri devin `<details>`; textele redenumite; regula, eticheta conturului, linia claselor, linia examenului de diferență; butoanele filtrului |
| `tests/js/logic.test.js` | `countLabel`, `lastWrongDay`, compatibilitatea progresului vechi |
| `tests/js/panels.test.js` | `signalsForClass` în `PANELS`; lint-ul pe cuvântul retras |
