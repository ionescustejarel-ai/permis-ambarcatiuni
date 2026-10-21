# Etapa 4b — teoria pentru temele cu desen

**Data:** 2026-07-29
**Etapa precedentă:** 4a (teoria: mecanismul și primele trei teme), fuzionată în `main`
**Decizie de scope (proprietarul proiectului, 2026-07-29):** lotul = temele care au deja media desenată; restul în 4c/4d.
**Livrat:** patru carduri (al cincilea, semnele de zi, retras la review — vezi §1).

## 1. Ce rezolvă

Temele cu figuri, arcuri, siluete sau sunete au desenul — și nicio regulă scrisă. Candidatul vede geamandura cardinală desenată, aude semnalul de un sunet scurt, are silueta navei cu vele, dar nu i se spune niciodată **regula** din spatele lor. Etapa 4a a construit stratul care lipsea; 4b îl duce acolo unde desenul îl așteaptă.

| Temă | Întrebări | Media pe care o completează |
|---|---|---|
| Lumini de navigație | 59 | 8 arcuri + 14 configurații |
| Geamanduri și balizaj | 21 | 9 marcaje |
| Semnale sonore | 19 | 8 semnale audio |
| Lumini în situații speciale | 16 | 2 arcuri + 4 configurații |
| **Total** | **115** | |

După 4b, aplicația va avea teorie pentru **325 din 603 de întrebări — 54% din bancă.**

> **Corectat după review:** cardul „Semne și forme ziua” a fost scris și apoi retras — afirmațiile lui repetau figuri ale căror etichete poartă deja înțelesul, iar regula §4 interzice redescrierea desenului. Rămâne însă o datorie reală pentru 4c: **conul de la vele-și-motor are plasament diferit pe clase** („la prova” la C, „cât mai sus posibil” la D). Plasamentul nu e în desen, nu e în etichetă, și e chiar discriminatorul întrebării — deci intră în teorie, nu în figură.

Ordinea din spec-ul părinte §9 se completează în sfârșit pe aceste teme: **teorie → media → drill.**

## 2. Riscul de class-folding, măsurat

Toate întrebările lotului sunt **mono-clasă** — nicio întrebare nu e comună. Prima mea citire a fost că asta face class-folding-ul imposibil; e **fals, și exact pe dos**: fiecare întrebare fiind specifică unei clase, gemenii cross-clasă cu răspunsuri diferite trăiesc tocmai aici.

Măsurat pe lotul de 122 de întrebări analizat inițial: **3 perechi de enunțuri aproape identice între clase, dintre care exact una cu răspuns diferit** — nava cu vele în marș (C: lumini de bord + pupa; D: în plus, roșu peste verde la catarg). E contradicția pe care etapa 3d a rezolvat-o deja împărțind configurațiile pe clase, și teoria o va împărți la fel.

O afirmație care citează numai întrebări de clasă C derivă `('C',)` — sigur prin construcție. Pericolul apare doar dacă amestec surse din ambele clase pe un subiect unde răspunsurile diferă. Aici, acel subiect e unul singur și e cunoscut.

## 3. Sonda de class-folding devine test

Recomandarea review-ului final de la 4a: automatizează **jumătatea structurală** a măturării, fiindcă bugetul de citire nu scalează la 17 teme rămase.

`test_no_statement_pools_facts_the_bank_states_per_class` — o afirmație e candidat când citează surse purtate **numai** de clasa C și surse purtate **numai** de clasa D, fără nimic comun: exact ce înseamnă a pune laolaltă fapte pe care banca le dă separat. Când cele două mulțimi *au* ceva comun, listele doar scriu același răspuns cu diacritice diferite. Testul **compară mulțimea candidaților cu o listă declarată de excepții**, fiecare cu motivul scris de mâna mea.

> **Corectat după implementare:** două definiții anterioare au fost măsurate și abandonate. Similaritatea de enunț la 0,75 raporta opt candidați unde e unul — banca își pune definițiile în serii (bătaia / pieptănarea / toarcerea), iar acele enunțuri diferă printr-un cuvânt și răspunsurile complet. Cerința de enunț identic rata tocmai pericolul acestui lot: sunetul lung e 4–6 s la clasa C și circa 4 s la D, sub două enunțuri formulate diferit.

Ce e și ce nu e: e **triaj**, nu poartă. Nu poate scora cazul semantic — „radiația solară" care trage spre distractorul „razele solare" a cerut un om, la 4a. Dar scurtează lista de citit de la toate afirmațiile la o mână, iar un candidat **nou** pică build-ul până când cineva îl citește și îl trece în listă cu un motiv.

Lista are azi o singură intrare, curățată manual la 4a.

## 4. Conținutul

Aceeași disciplină ca 4a, fără excepție: afirmații în proza mea, fiecare purtând citatele verbatim (enunț întreg sau răspuns corect întreg, la octet) pe care le predă; clasele derivate din întrebările-sursă; `theory-source` și `theory-theme` blocante; **review adversarial de conținut** la review-ul de task — afirmația lângă citatele ei, cu întrebarea: *susține ceva ce citatele ei nu susțin?*

Ținta de lucru, din structura măsurată: lumini de navigație ~12–16 afirmații, geamanduri ~6–8, semnale sonore ~5–7, lumini situații speciale ~4–6. Numărul nu e fixat de spec — auditul impune trasabilitatea, nu volumul.

**Teoria nu redescrie desenul.** Arcurile spun *cât* acoperă o lumină, configurațiile *ce poartă* fiecare navă, marcajele *cum arată* geamandura. Teoria spune ce nu se poate desena: când se aprind luminile, de ce cardinala are conurile în sensul apei bune, ce distinge un semnal de manevră de unul de ceață. Ce e deja în figură nu se repetă în text.

## 5. Interfața

Patru intrări noi în `THEME_PANELS`, teoria **prima** peste tot:

| Temă | Azi | După |
|---|---|---|
| Lumini de navigație | `[arcPanel, configPanel]` | `[theoryPanel, arcPanel, configPanel]` |
| Geamanduri și balizaj | `[figurePanel]` | `[theoryPanel, figurePanel]` |
| Semnale sonore | `[signalPanel]` | `[theoryPanel, signalPanel]` |
| Lumini în situații speciale | — | `[theoryPanel]` |

Nicio funcție nouă: `theoryPanel` servește toate temele, cum a fost proiectat la 4a.

Două capcane notate la 4a se închid acum, fiindcă acum se plătesc:

- **`theoryPanel` primește tema ca argument.** Azi și-o ia din `App.route.split(":")[1]`, deși apelantul `tema(root, theme)` o are deja. Corect azi fiindcă ruta se setează sincron înaintea dispatch-ului și e singurul apelant — dar e o dependență de stare globală pe care n-o vreau cu zece teme înregistrate. Constructorii din `THEME_PANELS` se apelează `build(theme)`; cei patru existenți ignoră argumentul.
- **Pluralul din rezumat.** „Teoria temei · N reguli" va citi „1 reguli" de îndată ce o temă lasă o singură afirmație la o clasă — plauzibil, și chiar întâmplat: clasa D are exact o afirmație la „Lumini în situații speciale”. Devine „o regulă" / „N reguli".

## 6. Verificarea

**Python.** Aceleași invariante ca 4a (formă, octet, temă, derivarea claselor, payload), plus sonda de class-folding cu lista ei de excepții.

**Node.** `statementsForClass` pe temele noi, în `panels.test.js`; pluralul, ca funcție pură dacă merită extras, altfel prin browser.

**Browser (controller).** Panoul pe toate temele cu carduri, **primul, înaintea panoului de media**; strâns implicit; filtrat pe clasă; nava cu vele arată regula ei la fiecare clasă; „o regulă" la singular unde apare; nimic în simulare; 390 px; consolă curată.

## 7. În afara scopului, deliberat

- **Celelalte teme** (278 de întrebări, inclusiv semnele de zi) — 4c/4d.
- **Panouri de media pentru „Lumini în situații speciale"** — tema găzduiește 2 arcuri și 4 configurații fără panou propriu, moștenire de la 3d, unde s-a decis că un singur loc de referință e destul. Rămâne așa; 4b adaugă doar teoria.
- **Sonda semantică.** Testul găsește candidați structurali. Ce susține o afirmație dincolo de citatele ei rămâne treaba review-ului de conținut.

## 8. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/theory.py` | +4 carduri |
| `src/caa/assets/ui.js` | intrările în `THEME_PANELS`, `build(theme)`, pluralul |
| `tests/caa/test_theory.py` | sonda de class-folding + lista de excepții |
| `tests/js/panels.test.js` | temele noi |
