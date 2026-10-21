# Etapa 3e — clasificatorul de teme

**Data:** 2026-07-29
**Etapa precedentă:** 3d (configurațiile de lumini), fuzionată în `main`
**Etapa următoare:** 4 (fișele de teorie) — motivul pentru care aceasta se face acum

## 1. Ce rezolvă

Cinci întrebări stau demonstrabil în tema greșită. Două despre marcajul lateral și una despre marcajul de pericol izolat sunt în „construcția ambarcațiunii" și „semnale de pericol"; două despre semne de zi sunt în „construcția ambarcațiunii" și „motor și propulsie". Nu e o chestiune de gust: fiecare e legată de un catalog care spune, fără echivoc, despre ce e întrebarea.

Contează acum, și nu mai târziu, fiindcă **etapa 4 grupează fișele de teorie pe teme**. Fișa de balizaj scrisă peste gruparea de azi n-ar acoperi întrebările pe care candidatul chiar le întâlnește acolo, iar cine face drill pe „construcția ambarcațiunii" ar primi întrebări despre geamanduri fără nicio teorie în spate.

## 2. Cauza, măsurată

**Tabelul de tipare e scris în formă de dicționar; banca scrie românește flexionat.** `marcaj lateral` nu e subșir în „marcaj**ul** lateral". Măsurat pe toată banca: **9 din 27** de expresii de două cuvinte au în bancă numai forma flexionată.

| Tipar | Întrebări care au numai forma flexionată |
|---|---|
| `semnal sonor` | 9 |
| `marcaj lateral` | 5 |
| `senal navigabil` | 5 |
| `pericol de coliziune` | 4 |
| `semnal de pericol` | 4 |
| `marcaj cardinal` | 3 |
| `bord liber`, `punctul navei` | 1 fiecare |

(`s o s` apărea și el în măsurarea inițială cu 3 — fals pozitiv al sondei: un cap de un singur caracter potrivește „vârful în su**s o s**feră". Nu e expresie română, e abreviere normalizată; lint-ul sare peste cuvintele de o literă.)

Fișierul cunoaște deja capcana — are un `drum\w*` scris anume și un comentariu despre „drum adevărat" vs „drumul adevărat". Reparația s-a oprit acolo unde a durut prima dată. Aceeași capcană m-a prins de trei ori în propriile scripturi de verificare la etapa 3d.

## 3. Ce NU se atinge

**Principiul „enunțul decide".** Tema se alege după enunț; opțiunile vorbesc doar când enunțul nu spune nimic, iar răspunsul corect are un singur cuvânt de spus, la perechea declarată din `_PROMOTIONS`. Alternativele au fost măsurate și respinse de două ori — o dată pentru enunțuri mute (10 mutări, 5 greșite) și o dată pentru promovare după poziția regulii (36 de mutări, majoritatea greșite). Rămâne exact așa.

Etapa asta întărește regulile pe care enunțul le consultă, nu ordinea în care e consultat.

## 4. Cele patru schimbări

### 4.1 Terminații explicite, nu `\w*`

Prima variantă a fost `marcaj\w* (lateral|cardinal)`. Măsurată, s-a dovedit greșită: `semnal\w* sonor` prinde **„semnaliza sonor"** — transformă substantivul în verb. Efectul concret: o întrebare despre zonele de separare a traficului se muta la semnale sonore, urmând un **distractor**, adică exact ce combate principiul de la §3.

Deci se scriu terminațiile pe care limba le are, nu un joker:

```
marcaj(ul|e|ele)? (lateral|cardinal)
semnal(ul|e|ele)? sonor
semnal(ul|e|ele)? de pericol
pericol(ul)? de coliziune
risc(ul)? de coliziune
```

Verificat: prinde „semnalele sonore", „semnalul sonor", „semnale sonore", „semnal sonor"; **nu** prinde „semnaliza sonor" sau „semnalizare sonoră".

### 4.2 Două goluri reale de tipar

`pericol izolat` lipsește cu totul din balizaj, deși e unul dintre marcajele pe care banca le întreabă.

Semnele de zi cer `con(uri)? negr`, dar banca scrie „un con cu vârful în jos" și „ziua în marș", fără culoare. Două întrebări cad prin plasă până la `prova`, în construcția ambarcațiunii. Se adaugă `con cu varful`, `semnul purtat`, `ziua in mars`.

### 4.3 `senal navigabil` iese din balizaj

Șenalul navigabil e un **loc**, nu un marcaj. Cu terminații flexionate, tiparul ar fi tras în balizaj o întrebare despre unde e interzis să instalezi plase de pescuit. Balizajul e despre semne; locul aparține regulamentului.

### 4.4 Vizibilitatea redusă înaintea semnalelor sonore

Cu `semnal sonor` reparat, cinci întrebări despre semnale pe ceață ieșeau din tema „vizibilitate redusă" — regula de sunet e mai sus în ordine. **O întrebare despre semnalul de ceață aparține acolo unde se învață ceața.** Se mută `vizibilitate-redusa` înaintea lui `semnale-sonore`.

Efectul secundar e tot o ameliorare: „Când se emit semnalele sonore de manevră?" iese din ceață, unde ajunsese din greșeală, fiindcă nu e semnal de ceață.

## 5. Regula de audit

`theme-subject`, blocantă ca toate celelalte. **O întrebare legată de un catalog trebuie să stea într-o temă permisă pentru catalogul ei.**

| Legătura | Teme permise | De ce mai mult de una |
|---|---|---|
| figură, geamandură | `geamanduri-si-balizaj` | — |
| figură, semn de zi | `semne-si-forme-ziua` | — |
| semnal sonor | `semnale-sonore`, `vizibilitate-redusa`, `reguli-de-drum` | semnalul de ceață se învață cu ceața; semnalul din cinci sunete scurte, la îndoială asupra intențiilor altei nave, se învață cu regulile de drum — acolo îl predă și COLREG |
| arc de vizibilitate | `lumini-propulsie-mecanica`, `lumini-situatii-speciale` | banca împarte luminile în două teme și întreabă arcuri în amândouă |
| configurație de lumini | aceleași două | idem |

Regula nu are nevoie de id-uri de întrebări: legătura e deja scrisă de build, iar felul figurii vine din `FIGURES[...].system`.

## 6. Testul pe tabelul însuși

Reparația celor 9 tipare nu împiedică al zecelea. Deci un test care **citește `THEMES`** și cade dacă o expresie de două cuvinte e scrisă în formă de dicționar, fără grup de terminații. Păzește toate cele 27, nu doar pe cele de azi, și e singura piesă care supraviețuiește următoarei ediții a băncii.

## 7. Efectul măsurat

Rulat pe banca livrată, cu toate cele patru schimbări:

- **14 întrebări își schimbă tema**, toate în bine (§7.1)
- **în afara temei permise: 5 → 0** din cele 54 cu subiect cert
- **tema-coș `vocabular-si-principii`: 59 → 56**; balizaj 19 → 21, semne de zi 5 → 7, hărți 16 → 17
- restul de 589 rămân neatinse

### 7.1 Toate cele 14

| Din | În | Întrebarea |
|---|---|---|
| construcția ambarcațiunii | semne și forme ziua | „La prova… un con cu vârful în jos este semnul purtat pe timp de zi" |
| construcția ambarcațiunii | geamanduri și balizaj | „Marcajul lateral de tribord din regiunea A…" |
| construcția ambarcațiunii | geamanduri și balizaj | „Marcajul lateral de babord din regiunea A…" |
| motor și propulsie | semne și forme ziua | „O navă care navigă cu vele folosind în același timp și motor, ziua în marș…" |
| semnale de pericol | geamanduri și balizaj | „Marcajul de pericol izolat are ca semn de vârf:" |
| meteo și hidrologie | reguli de drum | „Cum trebuie să manevreze două nave cu vele care se apropie…" (×2) |
| regulament Dunăre | semnale sonore | „…este în pericol și vrea să ceară ajutor, poate emite semnale sonore?" |
| semnale sonore | vizibilitate redusă | „Ce semnal sonor emite o navă cu capacitatea de manevră redusă…" |
| vizibilitate redusă | semnale sonore | „Când se emit semnalele sonore de manevră?" |
| vocabular și principii | semnale de pericol | „Ce este semnalul de pericol dat cu brațele?" |
| vocabular și principii | semnale de pericol | „Care este semnalul de pericol din Codul Internațional…" |
| vocabular și principii | semnale de pericol | „Ce semnificație au semnele aprobate transmise prin sisteme…" |
| geamanduri și balizaj | hărți și poziție | „Reperele costiere utilizate pentru determinarea punctului navei…" |

Cea din regulamentul Dunării merită numită separat: enunțul ei nu potrivea nimic, iar tema venea dintr-un **distractor** care spunea „R.N.D.". Acum enunțul ei propriu decide. E chiar defectul pe care regula de la §3 există să-l prevină, scăpat printr-o gaură de flexiune.

## 8. Verificarea

**Python.** Cele 13 mutări, fiecare numită și așteptată explicit; regula de audit demonstrată că mușcă pentru fiecare dintre cele cinci feluri de legătură; testul pe tabel; și verificarea că terminațiile nu înghit verbe — `semnaliza sonor` nu e `semnalul sonor`.

**Fără browser.** Etapa nu atinge nicio linie de interfață. Panourile filtrează pe clasă și pe temă exact ca înainte; se schimbă doar în ce temă cade o întrebare.

## 9. În afara scopului, deliberat

- **Cele 549 de întrebări fără subiect cert.** Auditul garantează 54 din 603 — 9%. Orice regulă pentru restul ar fi o părere prezentată ca fapt. Se scrie explicit în raportul de audit, ca nimeni să nu creadă că tema e verificată peste tot.
- **Tema-coș.** 56 de întrebări rămân la `vocabular-si-principii`. Unele chiar aparțin acolo; altele n-au un tipar care să le prindă. Nu se forțează.
- **Numărul de teme.** Nu se adaugă și nu se contopește nicio temă. „Lumini de navigație" și „Lumini în situații speciale" rămân două, deși materia lor se leagă.

## 10. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/themes.py` | terminațiile, cele două goluri, ordinea, `senal` scos |
| `src/caa/audit.py` | +1 regulă blocantă `theme-subject` |
| `tests/caa/test_themes.py` | cele 13 mutări, testul pe tabel, terminațiile |
| `tests/caa/test_audit.py` | regula, demonstrată pe fiecare fel de legătură |
