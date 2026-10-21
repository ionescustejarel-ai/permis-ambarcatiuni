# Etapa 5b — roza compasului

**Data:** 2026-07-30
**Etapa precedentă:** 5a (o afirmație poate purta un desen), fuzionată în `main` la `754b9f9`
**Cerere (proprietarul proiectului, 2026-07-30):** „fă roza compasului".

## 1. Ce rezolvă

Tema „Compas și drumuri" are 26 de întrebări, 9 afirmații și **niciun desen** — singura temă pur geometrică din aplicație în care nimic nu se vede. Toate cele nouă afirmații vorbesc despre unghiuri: măsurate de la ce, până la ce.

Un candidat citește *„drumul e unghiul din planul orizontului adevărat măsurat de la direcția nord până la axul prova"* și trebuie să-și închipuie figura. Figura e desenabilă, și e aceeași pentru jumătate din card.

## 2. Ce se desenează, și de ce e permis

Două intrări, un fel nou de desen: `rose`.

**`rose:unghiuri`** — cum se măsoară. Un cerc cu nordul sus, silueta navei în centru cu axul prova, un reper costier pe margine, și trei unghiuri:

| Unghiul | De la | Până la | Sursa |
|---|---|---|---|
| drum | direcția nord | axul prova | „măsurat de la direcția nord adevărat până la axul prova al navei" |
| relevment | direcția nord | linia de vizare la reper | „…până la linia de vizare la reperul costier" |
| relevment prova | **axul prova** | linia de vizare | „măsurat de la axul prova al navei până la direcția de vizare" |

Excepția — relevmentul prova, singurul care nu pleacă de la nord — e chiar lucrul pe care desenul îl face evident dintr-o privire.

Unghiurile din figură sunt **ilustrative și nenumerotate**. Desenul predă *de unde până unde*, nu o valoare; a scrie un număr pe el ar fi o cifră pe care banca n-o dă.

**`rose:cadrane`** — unde cad valorile. Cercul cu cele patru direcții la gradele pe care banca le afirmă (N 000, E 090, S 180, W 270), cele patru cadrane numite, și în fiecare exemplul pe care banca îl dă: NE 034, SE 112, SW 234, NW 328.

Fiecare număr de pe acest desen e un număr al băncii.

## 3. Ce NU se desenează

**Carturile.** Afirmația 8 spune că N e cardinal, SW intercardinal, SSE inter-intercardinal, iar „E la N" intermediar. Banca **numește punctele, dar nu le dă niciodată azimutul**: ca să-l așez pe SSE la 157°5 ar trebui să aduc sistemul în 32 de puncte, care nu e în bancă. Rămâne text.

E aceeași linie ca la noduri: cea mai tentantă imagine e cea pe care ar trebui s-o inventez.

## 4. Mecanismul

Felul `rose` se adaugă unde 5a a lăsat loc: un catalog nou `src/caa/rose.py`, un randor `src/caa/assets/rose.js`, un `case` în dispecerul din `statementDrawing`, o intrare în dicționarul regulii de audit `theory-drawing`, un payload și un marcaj în șablon.

Catalogul **nu se leagă de întrebări**, spre deosebire de marcaje, arcuri și configurații. Un desen de rozetă nu ilustrează o întrebare anume, ci regula scrisă peste ele; legătura lui e afirmația care-l cere, iar aceea e legată de sursele ei. Lanțul e deja păzit.

Cele două desene se atașează afirmațiilor 1–3 (definițiile) și 6–7 (gradele și cadranele). Ambele teme sunt clasa C, iar invarianta de la 5a verifică asta singură.

## 5. Verificarea

**Python.** Regula `theory-drawing` acoperă felul nou prin construcție. Nou: geometria e pură și se testează — unghiul dintre două direcții, poziția unui punct pe cerc.

**Node.** Randorul produce elementele așteptate; invarianta de clasă de la 5a acoperă atașarea.

**Mutații** din script Python, pe stare comisă: un id de rozetă inexistent pică auditul; inversarea sensului de măsurare în geometrie pică testul ei.

**Browser (controller), 390 px, ambele teme de culoare.** Ambele desene apar în cardul compasului la clasa C; tema nu există la clasa D; textul de pe desen se citește la lățimea unui telefon; consolă curată.

## 6. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/rose.py` | catalogul, două intrări |
| `src/caa/assets/rose.js` | randorul |
| `src/caa/assets/index.html` | marcajele pentru payload și script |
| `src/caa/app.py` | cablarea |
| `src/caa/audit.py` | felul `rose` în regula existentă |
| `src/caa/theory.py` | referințele pe cele două afirmații |
| `src/caa/assets/ui.js` | `case "rose"` în dispecer |
| `tests/caa/test_rose.py` | geometria |
| `tests/js/panels.test.js` | randarea |
