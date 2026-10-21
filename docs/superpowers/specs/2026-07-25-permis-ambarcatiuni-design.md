# Aplicație de pregătire pentru examenul CAA — clasele C și D

**Data:** 2026-07-25
**Status:** design aprobat, în așteptarea planului de implementare
**Beneficiar:** un candidat real la examenul ANR pentru clasele C și D

---

## 1. Obiectiv

O aplicație de învățare care duce candidatul de la zero la **≥94% acuratețe reală** pe banca oficială de întrebări a Autorității Navale Române, pentru certificatul internațional de conducător de ambarcațiune de agrement clasele C și D.

Ținta de 94% nu e arbitrară — vezi §3.

## 2. Fapte verificate despre examen

Toate confirmate din surse oficiale curente, descărcate în `sources/anr/` la 2026-07-25.

### 2.1 Cadrul legal

**Ordinul MT nr. 427 din 23 aprilie 2026** pentru aprobarea Regulamentului privind cerințele minime de pregătire și condițiile de obținere a certificatelor internaționale de conducător de ambarcațiune de agrement. Abrogă Ordinul 527/2016.

Condiții cumulative pentru înscriere (art. 3 alin. 2):
- cetățenie română / UE / SEE / Elveția, sau cetățenie străină cu drept de rezidență
- documente medicale emise cu **cel mult 6 luni** înainte: stare clinică, acuitate vizuală, acuitate auditivă, aptitudini psihologice
- **dovada absolvirii unei forme de pregătire aprobate de ANR**, corespunzătoare clasei
- vârsta minimă **18 ani**

Certificatul e valabil **10 ani**.

### 2.2 Clasele

| Clasă | Drept de conducere |
|---|---|
| A | căi navigabile interioare + toate zonele maritime |
| B | zone maritime până la 24 Mm de țărm |
| **C** | zone maritime până la **6 Mm** de țărm |
| **D** | **căi navigabile interioare** (interzis în apele maritime interioare) |

### 2.3 „Clasa S" nu există ca examen

Ordinul 427/2026 nu prevede o clasă S. Art. 4 din Regulament:

> „Orice persoană care intenționează să navigheze cu o ambarcațiune cu vele trebuie să dețină un certificat internațional de conducător de ambarcațiune de agrement emis de ANR **și să facă dovada că a absolvit cursul «Manevra ambarcațiunii cu vele»**, organizat printr-o formă de pregătire aprobată de ANR. Dreptul de a conduce ambarcațiuni cu vele se dobândește la data preschimbării certificatului."

**Consecință:** velele se obțin prin curs practic și diplomă, fără grilă. Materialele Tataru din arhivă (61 pagini) sunt suport pentru acel curs. **Aplicația nu acoperă velele.**

### 2.4 Structura probelor (Metodologia ANR în vigoare, Partea a II-a)

**Clasa C** — un singur test:

| Disciplină | Întrebări |
|---|---|
| COLREG | 10 |
| Navigație maritimă și Conducerea și manevra ambarcațiunilor cu motor | 6 |
| Marinărie | 6 |
| Prim ajutor medical | 2 |
| Legislație | 2 |
| **Total** | **26** |

Timp alocat 30 min. Barem minim **22 răspunsuri corecte**.
Examen de diferență: COLREG, 10 întrebări, 10 min, barem 8.

**Clasa D** — un singur test:

| Disciplină | Întrebări |
|---|---|
| Regulamentul de navigație pe Dunăre | 10 |
| Marinărie | 6 |
| Conducerea și manevra ambarcațiunilor cu motor | 6 |
| Prim ajutor medical | 2 |
| Legislație | 2 |
| **Total** | **26** |

Timp alocat 30 min. Barem minim **22 răspunsuri corecte**.
Examen de diferență: Regulamentul de navigație pe Dunăre, 10 întrebări, 10 min, barem 8.

Din Metodologie, art. 10: întrebările **fără răspuns marcat sunt tratate ca răspunsuri greșite**. Nu există penalizare suplimentară pentru răspuns greșit față de răspuns lipsă — deci strategia corectă la examen e să răspunzi la tot.

### 2.5 Banca oficială de întrebări

ANR publică listele complete pe portal, în format tabelar: **întrebare + 3 variante + flag de corectitudine (0/1)** pentru fiecare variantă.

| Fișier | Secțiune principală | Prim ajutor | Legislație | Rânduri |
|---|---|---|---|---|
| `Lista intrebari clasa C.pdf` | 442 | 50 | 25 | 517 |
| `Lista intrebari clasa D.pdf` | 296 | 50 | 25 | 371 |

**Un item = o combinație unică de enunț și set de variante.** Distincția e esențială: banca ANR pune același enunț cu seturi diferite de variante, ca întrebări separate. Clasa C, numerele 55, 56 și 57 sunt consecutive și au toate același enunț — „Din drumul căror nave trebuie să se abată o navă cu vele în marş?" — dar fiecare are alte trei variante și alt răspuns corect. **Gruparea numai după enunț pierde 47 de întrebări** din bancă.

| | Itemi |
|---|---|
| Comuni C și D | 267 |
| Doar C | 237 |
| Doar D | 99 |
| **Total** | **603** |

Pe secțiuni: principal 527, prim ajutor 50, legislație 26. Nicio suprapunere între secțiuni.

**Prim ajutor e identică** între cele două liste — toate cele 50 sunt comune. **Legislația nu**: 25 de itemi în fiecare listă, 24 comuni. Întrebarea despre cuantumul amenzii pentru folosirea abuzivă a mijloacelor de semnalizare are alte praguri în fiecare listă, deci sunt doi itemi distincți.

**Numerotarea din PDF are goluri reale.** La clasa C numerele merg până la 489, dar 442 de rânduri există; lipsesc, de exemplu, 154, 167 și 266 — verificat, tokenii respectivi nu apar nicăieri în document. ANR a eliminat întrebări și a păstrat numerotarea. **Nu sunt rânduri pierdute la parsare**: numărul de tokeni numerici din prima coloană coincide cu numărul de rânduri extrase (371 = 371 la clasa D, zero rânduri neparsate la clasa C).

Consecință pentru implementare: **nu se validează niciodată completitudinea prin continuitatea numerotării.** Vezi §6.3.

### 2.6 Disciplina de examen se determină din poziția în listă

Secțiunea principală a fiecărei liste e o succesiune de blocuri contigue, câte unul per disciplină de examen, dar numerotarea curge continuu peste graniță. Granițele au fost stabilite prin transferul etichetelor de modul din băncile vechi (`sources/arhiva/`, etichetate independent) și verificate: **acoperire 100%**, iar dimensiunile blocurilor coincid cu băncile vechi — COLREG 142 de rânduri, Marinărie 162, Regulament Dunăre 67.

| Clasă | Disciplină | Interval `nr` | Rânduri | Unice |
|---|---|---|---|---|
| C | COLREG | 1–142 | 142 | 139 |
| C | Navigație maritimă | 143–209 | 65 | 55 |
| C | Marinărie | 210–371 | 153 | 144 |
| C | Conducere și manevră | 372–489 | 82 | 68 |
| D | Regulament navigație Dunăre | 1–67 | 64 | 64 |
| D | Marinărie | 68–229 | 150 | 139 |
| D | Conducere și manevră | 230–347 | 82 | 68 |

Blocurile Manevră sunt identice între cele două liste (68 de întrebări, toate comune). Marinărie diferă ușor: 144 unice la C, 139 la D, 127 comune.

O singură întrebare aparține la două discipline — „Adâncimea apei se măsoară cu", prezentă și la Navigație, și la Marinărie. De aceea disciplina se modelează ca listă, nu ca valoare unică.

**Pool-urile acoperă repartiția de examen** (§2.4). La clasa C, Navigația și Manevra formează o singură disciplină de examen de 6 întrebări:

| Clasă | Disciplină de examen | Trage | Pool |
|---|---|---|---|
| C | COLREG | 10 | 142 |
| C | Navigație ∪ Manevră | 6 | 136 |
| C | Marinărie | 6 | 152 |
| C | Prim ajutor | 2 | 50 |
| C | Legislație | 2 | 25 |
| D | Regulament Dunăre | 10 | 64 |
| D | Marinărie | 6 | 149 |
| D | Conducere și manevră | 6 | 79 |
| D | Prim ajutor | 2 | 50 |
| D | Legislație | 2 | 25 |

### 2.9 De ce extragerea e pe grilă, la nivel de caracter

Extragerea pe blocuri de text produce două clase de defect, ambele măsurate pe datele reale înainte de a fi eliminate:

1. **Text din alt rând.** Un rând din `lista_C` a primit conținut de la 500 de puncte mai jos pe aceeași pagină; varianta „dispozitiv de manevra" a ieșit `ddeis ppoez cithive ud,e b mabaanleev, rbainte,tacheti,la`.
2. **Coloane ascunse.** `lista_D` are o coloană de 2 puncte lățime la x≈380, purtând valori dintr-un strat nefolosit — antetul ei arată „Tipul", „Dificultate" și „CURL" întrețesute. Valoarea se lipește de primul cuvânt al variantei și ajunge în textul afișat: „Perioada cuprinsă între apusul şi răsăritul **1** soarelui". **62 de celule afectate, dintre care 17 erau răspunsul corect.**

Ambele tabele sunt rulate, deci liniile de chenar dau grila exactă. Atribuirea **per caracter** rezolvă a doua clasă prin construcție — fiecare cifră intrusă își are centrul în coloana ascunsă — iar grila pe două axe o rezolvă pe prima.

`dedupe_chars` din pdfplumber a fost încercat și respins: **strică text legitim** („conducătorii" devine „conducători") și nici nu prinde toate cazurile.

**Garanția de integritate:** fiecare fragment extras trebuie să apară ca subșir în textul brut al paginii sale. Verificarea nu poate da fals pozitiv — text absent din pagină e prin definiție un defect. Cu extragerea pe grilă găsește zero defecte; cu cea pe blocuri găsea 63.

### 2.8 Cele două liste se contrazic o singură dată

Enunț identic, variante identice, răspuns corect diferit:

```
Boturile sunt:
  lista C nr 291:  *capete de parâmă vegetală ... pentru fixarea provizorie a unei parâme
  lista D nr 149:  *știfturi de siguranță ale unei chei de împreunare
```

Banca veche din arhivă marchează varianta cu știfturi, deci e de acord cu lista D.

**Decizie (proprietarul proiectului, 2026-07-25): se păstrează ambele, separat pe clasă.** Examenul fiecărei clase se generează din lista clasei respective, deci răspunsul care trece examenul e cel din lista candidatului. Item-ul primește `disputed=true`, iar interfața semnalează explicit că autoritatea se contrazice acolo.

Regula generală: dezacord **între** liste → împărțire pe clase. Contradicție **în interiorul** aceleiași liste, sau rând fără exact un răspuns marcat → conflict real, întrebarea se exclude și build-ul pică. După aplicarea acestei reguli nu mai rămâne niciun conflict nerezolvat.

### 2.7 Ce înseamnă asta pentru arhiva existentă

Arhiva `ambarcatiuni originale.rar` conține o bancă de întrebări veche (5 fișiere, 520 întrebări brute) și materiale de teorie.

- **89%** din întrebările arhivei se regăsesc în listele oficiale
- **225 de întrebări oficiale lipsesc din arhivă**
- arhiva reflectă structura veche a examenului (COLREG 8 în loc de 10) și **nu conține deloc** disciplinele Prim ajutor și Legislație — 4 din 26 de întrebări, 15% din test
- arhiva conține doar răspunsul corect, nu și distractorii

**Decizie:** banca de întrebări din arhivă se aruncă integral. Arhiva rămâne utilă doar ca **material de predare** (manual, slide-uri, prim ajutor).

## 3. De ce ținta e 94%

Baremul 22/26 combinat cu tragerea aleatoare din cei 603 itemi. Probabilitate binomială de promovare:

| Acuratețe reală | P(un examen) | P(și C și D) |
|---|---|---|
| 80% | 38% | 15% |
| 85% | 65% | 42% |
| 88% | 81% | 65% |
| 90% | 89% | 79% |
| 92% | 95% | 90% |
| **94%** | **98%** | **97%** |
| 95% | 99% | 98% |

„Știu cam 85%" = 65% șansă de promovare, 42% pentru ambele clase. Nu se poate compensa printr-o zonă puternică, pentru că nu candidatul alege ce pică.

Tradus în întrebări concrete, presupunând restul băncii solid și o întrebare nesigură = 50% șansă:

| Întrebări nesigure din 603 | Acuratețe efectivă | P(un examen) | P(examen + diferență) |
|---|---|---|---|
| 20 | 98,3% | 100% | 99,9% |
| **40** | **96,7%** | **99,9%** | **99,5%** |
| 60 | 95,0% | 99,2% | 98,1% |
| 80 | 93,4% | 97,4% | 95,0% |

Ținta operațională: **cel mult 40 de întrebări nesigure.**

Aceasta e justificarea metricii din §7.

## 4. Non-obiective

Explicit în afara scopului:

- clasele A și B (6, respectiv 4 probe separate, COLREG în engleză)
- navigația cu vele / cursul „Manevra ambarcațiunii cu vele"
- conturi de utilizator, sincronizare între dispozitive, backend
- conținut care ține locul cursului obligatoriu aprobat de ANR — aplicația e complement, nu substitut
- orice fel de întrebare fabricată sau distractor generat; **doar conținut oficial ANR**

## 5. Arhitectură

Un singur fișier `permis-ambarcatiuni.html`, self-contained, offline, funcțional pe telefon. Progres în `localStorage`. Zero server, zero cont.

```
sources/anr/*.pdf  ──▶  src/caa/  ──▶  questions.json  ──┐
                            │                            ├──▶  permis-ambarcatiuni.html
sources/arhiva/*   ──▶  (teorie, manual)  ──▶  themes.json ──┘         │
                                                                       ▼
                                                                  localStorage
                                                                  (progres)
```

Trei straturi separate în interiorul fișierului:

1. **Date** — JSON inline, generat, niciodată editat de mână
2. **Motoare** — quiz, SRS, audio, SVG; fiecare independent testabil
3. **UI** — consumă motoarele, nu atinge datele direct

Separarea contează pentru monetizarea ulterioară: stratul de date se mută pe un backend fără rescrierea UI-ului.

## 6. Pipeline de date

### 6.1 Pachetul de build `src/caa/`

Re-rulabil. Dacă ANR actualizează listele, se re-rulează și rezultă versiunea nouă.

Etape:

1. **Extragere pe grila de chenar, la nivel de caracter**, cu `pymupdf`. Ambele tabele sunt rulate, deci liniile de chenar dau grila exactă de celule și fiecare glifă se atribuie după centrul ei. Coloanele se identifică după lățime, nu după index, pentru că cele două liste au layout-uri diferite (9 coloane rulate la C, 11 la D). Extragerea își verifică propriul rezultat: fiecare fragment produs trebuie să apară ca subșir în textul brut al paginii lui. Golurile din numerotare sunt reale în sursă și **nu** trebuie „reparate". Vezi §2.9.
2. **Segmentare pe secțiuni** — numerotarea repornește de la 1 la fiecare disciplină. Trei secțiuni per fișier: principală, Prim ajutor, Legislație.
3. **Normalizare** — diacriticele sunt inconsistente între secțiuni (`ţ` vs `ț`, secțiuni fără diacritice deloc). Se păstrează textul original pentru afișare și se generează o cheie normalizată pentru dedup.
4. **Dedup și marcare de clasă** — o întrebare prezentă în ambele liste primește `class: ["C","D"]`.
5. **Atribuire de temă** — exact o temă primară per întrebare (§8).
6. **Audit** (§6.3).

### 6.2 Model de date

```json
{
  "id": "q7f3a91c40e28",
  "q": "Ce se înţelege prin expresia \"sunet lung\"?",
  "opts": ["un sunet a cărui durată este de 1-2 secunde.",
           "un sunet a cărui durată este de 4-6 secunde.",
           "un sunet a cărui durată este de 10 secunde."],
  "correct": 1,
  "theme": "semnale-sonore",
  "section": "principal",
  "disciplines": {"C": ["COLREG"]},
  "classes": ["C"],
  "disputed": false,
  "media": { "type": "audio", "spec": { "pattern": [["long", 5000]] } }
}
```

Trei decizii de model:

- **`id` e derivat din textul normalizat al întrebării** (sha256 trunchiat), nu din poziție. Progresul din `localStorage` e indexat pe el și trebuie să supraviețuiască unui rebuild care adaugă sau scoate alte întrebări. Un id pozițional ar șterge progresul la fiecare actualizare a listelor ANR.
- **`disciplines` e o mapare clasă → discipline**, nu listă plată. O întrebare poate aparține unei discipline la clasa C și alteia la clasa D (§2.6); cu o listă plată, simularea de examen ar număra-o la două discipline pentru aceeași clasă.
- **`id` include și setul de variante**, nu doar enunțul. Trei întrebări pot împărți același enunț (§2.5); dacă id-ul ar deriva numai din enunț, s-ar suprascrie reciproc în progresul salvat. La itemii disputați (§2.8) intră în id și clasa.
- **`disputed`** marchează itemii unde cele două liste oficiale dau răspunsuri diferite. Interfața trebuie să semnaleze asta vizibil.
- `media` e opțional și **declarativ** — descrie ce trebuie generat, nu conține asset. Motorul audio/SVG interpretează `spec`.

Disciplina și tema sunt axe diferite: disciplina răspunde la „ce se trage la examen", tema la „ce învăț acum". Întrebările despre lumini apar și la COLREG, și la Regulamentul Dunării, dar se învață împreună.

### 6.3 Reguli de audit

Build-ul eșuează, nu avertizează, dacă:

- o întrebare nu are exact 3 variante
- o întrebare nu are exact 1 variantă marcată corectă
- textul întrebării sau al vreunei variante e gol
- două variante ale aceleiași întrebări au text identic — întrebarea n-ar putea fi răspunsă corect prin citire
- două întrebări au același `id`
- o întrebare nu are temă atribuită
- totalurile nu se potrivesc cu valorile de referință măsurate la 2026-07-26: 517 / 371 rânduri, 504 / 366 itemi pe clasă, 267 comuni, 603 în total, 2 disputați, pe secțiuni 527 / 50 / 26. O diferență înseamnă ori un parser stricat, ori o listă actualizată de ANR — ambele cer intervenție umană, nu trecere silențioasă
- două întrebări cu text identic au răspunsuri corecte diferite (conflict de dedup)
- o disciplină de examen are pool mai mic decât numărul de întrebări trase la examen (§2.6)

**Ce NU e regulă de audit:** continuitatea numerotării. Golurile sunt reale în sursă (§2.5) și o verificare pe ele ar pica build-ul pe date corecte.

Regula de bază, preluată din proiectul Grile Admitere: **nu se livrează nimic fără audit verde.** Un răspuns greșit în aplicație e mai rău decât lipsa aplicației.

Raportul de audit se scrie în `build/audit-report.md` la fiecare rulare.

## 7. Testare și progres

### 7.1 Metrica principală

Dashboard-ul afișează **numărul de întrebări nesigure**, nu media procentuală. O cifră mare, cu ținta sub 40.

Media procentuală e liniștitoare și mincinoasă — ascunde exact tipul de gaură care pică examenul.

**Definiția „sigur":** o întrebare iese din lista nesigure doar după **două răspunsuri corecte consecutive, la distanță de cel puțin o zi**. Un răspuns corect din prima poate fi noroc de 1-din-3.

Orice răspuns greșit readuce întrebarea în lista nesigure, indiferent de istoric.

### 7.2 Moduri

1. **Drill pe temă** — întrebările temei în ordine amestecată, feedback imediat cu explicație
2. **Simulare examen** — exact 26 de întrebări în repartiția oficială din §2.4, cronometru 30 min, **fără feedback până la final**. Raport final: promovat/picat la pragul 22, lista greșelilor, trimitere la temele corespunzătoare
3. **Lista neagră** — doar întrebările nesigure. Aici se câștigă examenul
4. **Examen de diferență** — 10 întrebări COLREG (clasa C) sau RND (clasa D), 10 min, barem 8

### 7.3 Urmărire pe clase

C și D se urmăresc separat. Întrebările comune se învață o dată și contează la ambele. Aplicația afișează explicit suprapunerea: *„din cele 26 ale clasei D, N le știi deja de la C"*.

**Traseul real, dat de examenul de diferență (§12.1):** un examen complet pentru prima clasă (26 întrebări), apoi examenul de diferență pentru a doua (10 întrebări din disciplina distinctivă — COLREG pentru C, Regulamentul de navigație pe Dunăre pentru D). Aplicația trebuie să reflecte acest traseu, nu două parcursuri complete paralele:

- prima clasă = toate temele ei
- a doua clasă = doar disciplina distinctivă, restul fiind deja acoperit

Care clasă se dă prima rămâne o alegere a candidatului; aplicația o expune ca setare, cu recomandarea implicită **C prima**: banca ei e mai mare (504 față de 366 de itemi), iar din cei 603 itemi **237 apar doar la C și doar 99 doar la D** — deci pornind cu C rămân de învățat mult mai puțini pentru a doua clasă.

## 8. Taxonomia temelor

Derivată din banca oficială, nu inventată. Cifrele de mai jos sunt orientative (obținute cu etichetare multiplă în analiza preliminară); atribuirea finală e o singură temă primară per întrebare, la etapa 1.

| Temă | ~Întrebări | C | D |
|---|---|---|---|
| Vocabular și principii generale | ~134 | se stabilește la etapa 1 | se stabilește la etapa 1 |
| Parâme, noduri, ancore, armament | 233 | 121 | 112 |
| Prim ajutor | 50 (oficial) | 50 | 50 |
| Construcția și părțile ambarcațiunii | 125 | 92 | 33 |
| Semnale de pericol și salvare | 77 | 45 | 32 |
| Lumini — remorcaj, pescuit, ancoră, eșuat | 74 | 50 | 24 |
| Motor și propulsie | 71 | 37 | 34 |
| Meteo și hidrologie | 67 | 40 | 27 |
| Regulament Dunăre — definiții, ecluzare | 56 | 19 | 37 |
| Geamanduri și balizaj | 52 | 31 | 21 |
| Legislație și sancțiuni | 25 (oficial) | 25 | 25 |
| Manevra ambarcațiunii cu motor | 46 | 27 | 19 |
| Navigație — compas, drumuri, relevmente | 31 | 28 | 3 |
| Semnale sonore | 22 | 15 | 7 |
| Semne și forme ziua | 21 | 12 | 9 |
| Reguli de drum — cine cedează | 21 | 18 | 3 |
| Navigație — hărți, sondă, poziție | 21 | 13 | 8 |
| Lumini — nave cu propulsie mecanică | 20 | 17 | 3 |
| Vizibilitate redusă | 15 | 13 | 2 |
| Motovehicule nautice (skyjet) | 10 | 5 | 5 |

**Ordinea de parcurgere respectă dependențele:** vocabular (prova/pupa/tribord/babord) → lumini → reguli de drum. N-are sens să înveți cine cedează dacă nu știi ce e tribordul.

**Ordinea de scriere a teoriei o dau volumele:** Parâme/noduri/ancore, Prim ajutor și Construcția ambarcațiunii sunt cele mai mari blocuri și apar la ambele clase.

## 9. Experiența de învățare

Fiecare temă are patru straturi, în ordine:

1. **Card de teorie scurt** — regula, nu enumerarea. „Conurile geamandurii cardinale arată unde e apa bună" bate o listă de patru culori memorate mecanic.
2. **Media generată din spec** — SVG și audio, unde tema o cere
3. **Drill** pe întrebările temei, feedback imediat
4. **Test de temă** — 90% pentru deblocarea temei următoare

**Regula care ține teoria onestă:** fiecare afirmație din cardul de teorie trebuie să răspundă la cel puțin o întrebare din banca oficială. Ce nu răspunde la nimic e balast și iese. Teoria se scrie **din** manual și slide-uri, dar se **validează împotriva** băncii.

## 10. Motoarele media

O parte substanțială din bancă e intrinsec audio-vizuală. Numărând etichetările peste ambele liste (cu suprapuneri între C și D, deci nu întrebări unice): **94 despre lumini, 73 despre geamanduri și semne, 22 despre semnale sonore**. Numărul de întrebări unice afectate se stabilește la etapa 1, odată cu dedup-ul — ordinul de mărime e ~150.

**Nu se folosesc fișiere media.** Regulamentul dă specificația exactă, deci elementele se generează. Zero assets, fișier mic, fiecare element derivat din regulament și deci verificabil.

### 10.1 Motor audio (Web Audio API)

Definiții din COLREG, prezente ca atare în bancă:
- „sunet scurt" = aproximativ 1 secundă
- „sunet lung" = 4-6 secunde

Tipare din bancă: 1 scurt („vin la tribord"), 2 scurte („vin la babord"), 3 scurte („am mașina înapoi"), 5 scurte (avertizare), 1 lung + 2 scurte (navă cu capacitate de manevră redusă, navă cu vele pe vizibilitate redusă), lung-scurt-lung-scurt (acord la depășire — litera C în Morse).

Spec declarativ: `{ "pattern": [["short",1000],["gap",500],["short",1000]] }`.
Timbre distincte pentru fluier, clopot și gong.

### 10.2 Motor SVG

Geamanduri desenate din specificație: formă (conică, cilindrică, sferică), culoare, dungi, semn de vârf, ritm de sclipire. Exemplu: cardinal Vest = galben-negru-galben, două conuri vârf la vârf, 9 sclipiri.

Lumini de navă: siluetă, poziții, culori, ritm, animate pe fundal de noapte.

## 11. Ordinea de implementare

| # | Etapă | Livrabil |
|---|---|---|
| 1 | `caa/` (pachetul de build) + audit | `questions.json` validat |
| 2 | Shell HTML + motor quiz + simulare + progres | **aplicație folosibilă** |
| 3 | Motor audio + SVG | acoperire audio-vizuală |
| 4 | Teoria pe teme | ~20 carduri |

**După etapa 2 candidatul are deja un instrument real** — banca oficială completă, simulare cu barem, tracking al întrebărilor nesigure. Etapele 3 și 4 îmbunătățesc învățarea, nu o condiționează.

## 12. Riscuri și întrebări deschise

| # | Problemă | Stare |
|---|---|---|
| 1 | Sensul „examenului de diferență" | **Rezolvat** (confirmat de proprietarul proiectului, 2026-07-25): se dă la trecerea de la o categorie la alta. Deci C+D înseamnă un examen complet de 26 de întrebări plus unul de diferență de 10, nu două examene complete. Documentele ANR nu definesc termenul explicit — dacă apare o divergență la înscriere, se reverifică la căpitănie. |
| 2 | Termen de livrare | **Rezolvat:** fără presiune de calendar, dar aplicația trebuie făcută. Se construiește complet, pe etape, fără scurtături de tip „livrăm doar simularea". |
| 3 | Cursul aprobat ANR obligatoriu (art. 3 alin. 2 lit. c) | **Rezolvat:** situația e acoperită. Aplicația rămâne complement la curs, nu substitut. |
| 4 | Manualul de 157 de pagini e scan color rotit 90°, fără strat de text | Necesită OCR cu dezrotire. Slide-urile (Navigație 30p, Marinărie 29p + 46p) au text extractibil și sunt mult mai ieftin de folosit. Strategie: pornim de la slide-uri, OCR pe manual doar unde slide-urile nu ajung. |
| 5 | ANR poate actualiza listele de întrebări | Mitigat prin `caa/` (pachetul de build) re-rulabil. De reverificat sursa înainte de examen. |
| 6 | ~~Parserul pierde rânduri~~ | **Infirmat prin verificare** (2026-07-25). Golurile din numerotare sunt reale în sursă; extracția e completă. Riscul inversat — o regulă de audit pe continuitatea numerotării ar fi picat build-ul pe date corecte. Vezi §2.5 și §6.3. |
| 7 | Cele două liste conțin duplicate interne (37 la C, 25 la D) | Întrebări cu text identic apar de mai multe ori în aceeași listă, uneori cu variantele în altă ordine. Dedup-ul din §6.1 le colapsează; dacă două duplicate au răspunsuri corecte diferite, build-ul trebuie să eșueze, nu să aleagă unul. |

## 13. Surse

Descărcate 2026-07-25 în `sources/anr/`:

- Ordinul MT nr. 427/23.04.2026 — `ordin_regulament.pdf`
- Metodologia de organizare și desfășurare a examenelor de evaluare a competenței — `metodologie_2026.pdf`
- Lista întrebări clasa C — `lista_C.pdf`
- Lista întrebări clasa D — `lista_D.pdf`
- Programare sesiuni CAA 2026 — `programare_2026.pdf`

Pagina-sursă: portalul ANR, secțiunea „CAA (conducător ambarcațiune agrement)".

Materiale de teorie în `sources/arhiva/` (din `ambarcatiuni originale.rar`).
