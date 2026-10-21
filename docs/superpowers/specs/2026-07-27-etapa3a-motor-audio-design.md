# Etapa 3a — motorul audio

**Data:** 2026-07-27
**Etapa precedentă:** 2 (aplicația), fuzionată în `main`
**Spec-părinte:** `2026-07-25-permis-ambarcatiuni-design.md` §10.1

## 1. Ce rezolvă

Banca oficială descrie semnalele sonore în cuvinte: *„un sunet lung urmat de două sunete scurte"*. Candidatul le memorează ca text, fără să le fi auzit vreodată. Motorul audio le redă, ca formularea scrisă — pe care o cere examenul — să se lege de ceva.

**Examenul e scris.** Sunetul e mnemonic, nu antrenament auditiv. Asta decide tot ce urmează: nu există drill de ascultare, iar fiecare buton de redare are alături banda vizuală a tiparului, ca să funcționeze și cu sunetul oprit.

## 2. Câte întrebări atinge

Măsurat pe banca livrată (603 itemi), **13 răspunsuri corecte descriu un tipar redabil**:

| Temă | Întrebări |
|---|---|
| Semnale sonore | 10 |
| Vizibilitate redusă | 2 |
| **Reguli de drum** | **1** |

Ultima e proba că acoperirea se verifică pe **toată banca**, nu pe temele audio. Avertizarea din cinci sunete scurte trăiește la *Reguli de drum* fiindcă acolo o pune enunțul ei; o regulă care ar scana doar temele audio ar rata-o și n-ar spune nimic.

## 3. Catalogul

`src/caa/signals.py`, lângă `exam.py` — același tipar ca regulile de examen: date Python, auditate la build, emise în pagină ca `<script id="signals" type="application/json">`. Nu se retastează în JS.

Fiecare intrare poartă tiparul **și citatele verbatim** pe care le codifică:

```python
Signal(
    id="manevra-redusa-vizibilitate",
    label="Capacitate de manevră redusă, pe vizibilitate redusă",
    instrument=WHISTLE,
    pattern=(LONG, SHORT, SHORT),
    sources=(
        "un sunete lung urmat de 2 sunete scurte la intervale nu mai mari de 2 minute.",
        "un sunet lung urmat de 2 sunete scurte, la intervale ce nu vor fi mai mari de 2 minute.",
        "un sunet lung urmat de două sunete scurte, la intervale nu mai mari de 2 minute.",
    ),
)
```

`sources` e **tuplu, nu șir**: același semnal apare în bancă cu trei formulări, dintre care una conține greșeala de tipar „un **sunete** lung". Textul sursei nu se corectează niciodată — se citează cum este, ca potrivirea să rămână exactă.

### 3.1 Intrările

Zece intrări acoperă 12 din cele 13 întrebări.

| id | instrument | tipar | citat-sursă (verbatim) |
|---|---|---|---|
| `sunet-scurt` | fluier | 1 scurt | „un sunet a cărui durată este de aproximativ o secundă." |
| `sunet-lung` | fluier | 1 lung | „un sunet a cărui durată este de 4-6 secunde." |
| `vin-la-tribord` | fluier | 1 scurt | „un sunet scurt." |
| `vin-la-babord` | fluier | 2 scurte | „două sunete scurte." |
| `masina-inapoi` | fluier | 3 scurte | „trei sunete scurte." |
| `avertizare` | fluier | 5 scurte | „un semnal de avertizare compus din cinci sunete scurte." |
| `acord-depasire` | fluier | lung, scurt, lung, scurt | „un sunet lung, un sunet scurt, un sunet lung şi unul scurt (litera C)" |
| `manevra-redusa-vizibilitate` | fluier | lung, scurt, scurt | trei citate, vezi mai sus |
| `serie-foarte-scurte` | fluier | 6 × ¼ s | „O serie de cel puţin 6 sunete cu o durată de circa ¼ de secundă fiecare" |
| `doua-lovituri-clopot` | clopot | 2 bătăi | „Înseamnă două lovituri de clopot" |

### 3.2 Excepția

A treisprezecea întrebare **nu intră în catalog**:

> „O serie de sunete de clopot" sau „sunete lungi" cu alte mijloace acustice repetate

Sursa nu dă nici numărul, nici durata. Orice redare ar inventa un fapt de regulament. Intră în `NOT_A_PATTERN` cu motivul scris în cod, iar auditul o cere acolo explicit — tăcerea nu e o opțiune.

### 3.3 Legătura cu întrebările e derivată

Catalogul **nu conține id-uri de întrebări**. Id-urile sunt hash-uri de conținut; scrise de mână s-ar rupe la primul rebuild. Build-ul potrivește fiecare `source` cu răspunsurile corecte din bancă și scrie `signal` pe întrebările găsite. Potrivirea e pe răspunsul corect **întreg**, normalizat cu `normalize_key`, nu pe fragment — un fragment ar prinde întrebări vecine.

## 4. Auditul

Două reguli blocante noi în `audit.py`, în stilul celor existente: constatarea oprește build-ul și `questions.json` nu se scrie.

**R1 — fiecare citat există.** Fiecare `source` din catalog se regăsește printre răspunsurile corecte ale băncii. Zero potriviri = ANR a schimbat textul → build picat, cu id-ul intrării și citatul orfan în raport.

**R2 — fiecare tipar e acoperit.** Orice răspuns corect din bancă având **formă** de tipar sonor e fie acoperit de o intrare, fie trecut în `NOT_A_PATTERN`. Necunoscut = build picat.

Forma o recunoaște o expresie regulată din `signals.py`, aplicată răspunsului normalizat — numeral urmat de „sunet(e)"/„lovituri"/„bătăi", ori „sunet scurt"/„sunet lung", ori „serie de sunete". E o plasă largă intenționat: pe banca de azi prinde exact cele 13, iar dacă mai prinde ceva în viitor, cere o decizie în loc să rateze un semnal nou. Fals-pozitivele se închid scriindu-le în `NOT_A_PATTERN`, cu motiv — costul e o linie, iar alternativa e tăcerea.

Ambele reguli trebuie să pice când sunt scoase. Nu se acceptă o regulă care nu mușcă.

## 5. Motorul

`src/caa/assets/audio.js`. Web Audio API, sinteză, **zero fișiere** — la fel ca restul aplicației, pagina rămâne una singură și funcționează offline.

### 5.1 Durate

| Element | Valoare | Sursa |
|---|---|---|
| sunet scurt | 1000 ms | banca: „aproximativ o secundă" |
| sunet lung | 4500 ms | banca: „4-6 secunde" (lista C) și „circa 4 secunde" (lista D) — 4500 încape în ambele |
| sunet foarte scurt | 250 ms | banca: „circa ¼ de secundă" |
| interval în seria foarte scurtă | 250 ms | banca: „circa ¼ s" |
| **pauză între sunetele unui grup** | **500 ms** | **constantă de prezentare, NU regulament** |

Ultimul rând contează. Regulamentul din bancă nu dă pauza dintre sunetele unui semnal. 500 ms e ales ca tiparul să fie lizibil la ureche, și se declară ca atare în cod și în interfață — aplicația nu are voie să lase impresia că e un fapt din lege.

### 5.2 Timbre

Două, nu trei. **Fluier** și **clopot**.

Spec-ul-părinte (§10.1) cerea și gong. Verificat pe bancă: „gong" apare **o singură dată în tot corpusul, și doar ca distractor**; la fel „sirena". Niciun răspuns corect nu cere gongul. Un al treilea timbru n-ar avea ce învăța pe nimeni.

- **Fluier:** undă dreptunghiulară filtrată trece-jos, atac scurt, susținere plată. Un fluier de navă e un ton aspru, nu un fluierat pur.
- **Clopot:** sinus plus armonice inarmonice, stingere exponențială rapidă.

### 5.3 Ce e logică pură și ce nu

Expandarea `pattern` → cronologie `[[tip, ms], …]` stă în `logic.js`, unde o conduce `node --test`. `audio.js` primește cronologia și programează oscilatoarele; nu decide nimic.

Aceeași linie ca la etapa 2, trasă din același motiv: defectele acelei etape au căzut toate în cusătura dintre module corecte, netestabilă. Aici cusătura e subțire prin construcție.

## 6. Interfața

**Panou pe temă.** Tema *Semnale sonore* primește sus un panou cu toate cele zece semnale: eticheta, banda vizuală, buton de redare. Se răsfoiește ca o listă de referință.

**Buton la întrebare.** Cele 12 întrebări acoperite primesc buton de redare în drill, **numai după ce candidatul a răspuns**. Înainte ar da răspunsul.

**Banda vizuală** însoțește fiecare buton: `▬` lung, `▪` scurt. Funcționează cu sunetul oprit și întărește formularea scrisă, care e cea notată la examen.

**Nimic în simulare.** Acolo nu există feedback până la final; un buton de redare ar fi feedback.

**Un singur semnal deodată.** Apăsarea altui buton îl oprește pe cel în curs — două semnale suprapuse nu seamănă cu niciunul.

`AudioContext` se creează la prima apăsare, nu la încărcarea paginii: browserele blochează audio fără gest al utilizatorului, iar butonul e chiar gestul.

## 7. Verificarea

**Python.** Forma catalogului, cele două reguli de audit (fiecare demonstrată că mușcă), rezolvarea citatelor la întrebări reale.

**Node.** Expandarea tiparului: „trei sunete scurte" → 3 rafale de 1000 ms separate de 500 ms, durata totală, seria de șase foarte scurte, tiparul literei C.

**Browser, cu `OfflineAudioContext`.** Semnalul se randează într-un buffer, se numără rafalele non-tăcute și li se măsoară durata. „Trei sunete scurte" trebuie să producă **exact 3 rafale de ~1 s**. Asta verifică sunetul propriu-zis, nu declarația că sună bine.

## 8. În afara scopului, deliberat

- **Gongul și sirena** — apar doar în răspunsuri greșite (§5.2).
- **Drill de ascultare** — examenul e scris; ar fi o modalitate nouă de exercițiu, nu o acoperire a băncii.
- **Fișiere audio** — pagina rămâne una singură, fără assets.
- **Semnalul de pericol cu clopot** — sursa nu dă numărul (§3.2).
- **Reglaj de volum** — volumul sistemului e suficient.

## 9. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/signals.py` | catalogul + `NOT_A_PATTERN` |
| `src/caa/audit.py` | R1, R2 |
| `src/caa/cli.py` | scrie `signal` pe întrebări |
| `src/caa/app.py` | emite `<script id="signals">` |
| `src/caa/assets/logic.js` | `signalTimeline(signal)` |
| `src/caa/assets/audio.js` | sinteza, un semnal deodată |
| `src/caa/assets/ui.js` | panoul temei, butonul din drill |
| `src/caa/assets/app.css` | banda vizuală, butonul |
| `tests/caa/test_signals.py`, `tests/js/logic.test.js` | testele |
