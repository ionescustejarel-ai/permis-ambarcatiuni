# Etapa 4e — teoria pentru ultimele teme

**Data:** 2026-07-30
**Etapa precedentă:** 4d (panourile se pliază, limbajul spune ce înseamnă), fuzionată în `main` la `6cb6eb5`
**Aprobare (proprietarul proiectului, 2026-07-30):** mutările de clasificare măsurate mai jos, apoi teoria.

Etapa care închide teoria. După ea, **toate cele 603 întrebări stau într-o temă care are card** — dar asta nu înseamnă că fiecare întrebare e citată; vezi §6.

---

## 1. Întâi tema-coș

Vocabularul are 54 de întrebări și e singurul loc din aplicație unde „tema" nu înseamnă nimic: înăuntru stau laolaltă regula COLREG 10 despre schemele de separare a traficului, instalația de guvernare, macaraua, școndrii dunăreni și principiul lui Arhimede. Teoria scrisă peste așa ceva ar fi o listă, nu o regulă.

Treisprezece dintre ele aparțin altor teme, și tiparele care le duc acolo sunt aceleași ca la 4c — vocabular care lipsea din tabel, nu semantică nouă:

| Adăugat la | Tipar | Ce recuperează |
|---|---|---|
| `geamanduri-si-balizaj` | `scondr\|jalon` | școndrii pentru dreapta/stânga, jaloanele de aliniament — marcaje dunărene, iar cardul temei vorbește deja despre ele |
| `reguli-de-drum` | `separare a traficului\|trafic costier\|in vedere` | opt întrebări de COLREG 10 plus definiția „nave aflate în vedere" |
| `manevra-cu-motor` | `guvernar` | instalația de guvernare, în șase variante de enunț |
| `parame-noduri-ancore` | `macara\|raiul\|sbir\|biga\|granic\|grui` | gruiul, macaraua, raiul — dispozitive de ridicat, exact ca palancul și vinciul la 4c |
| `constructia-ambarcatiunii` | `fil(a\|e\|ele\|elor)\b\|bordaj\|dama\b` | filele bordajului, dama — cardul temei le pomenește deja |

**Măsurat pe toate cele 603: 27 de mutări, fiecare citită, toate corecte.** Vocabularul scade de la 54 la 32 și devine o temă despre care se poate scrie cinstit.

> **Măsurat și lăsat afară:** tiparele pentru vopsit și mațagonire. Vopsitul e întreținere, nu construcție, iar temă de întreținere nu există — deci mutarea ar fi fost o opinie, nu o corectură. Rămân în vocabular, unde pot fi predate ca ce sunt: lucruri de matelotaj diverse.

## 2. Coliziunea cu teoria existentă, și rezolvarea ei

Regula `theory-theme` cere ca fiecare citat să stea în tema cardului care îl folosește. O întrebare mutată care e deja citată **pică build-ul**. Măsurat: din cele 27, exact una se ciocnește.

Cardul `constructia-ambarcatiunii` citează răspunsul „propulsoare prova şi pupa (bowtruster și sterntruster)", iar `guvernar` duce acea întrebare la manevră.

Rezolvarea nu e să ocolesc tiparul: **`manevra-cu-motor` primește card la etapa asta.** Faptul despre propulsoarele prova-pupa se mută în cardul nou, iar afirmația din construcție rămâne cu efectul elicei — tot ce mai citează celelalte două surse ale ei. Nimic nu se pierde; un fapt se așază unde îi e locul.

## 3. Pericolul de class-folding e mic aici, și asta schimbă unde mă uit

Măsurat pe cele patru teme mari ale lotului: **nicio pereche de enunțuri cvasi-identice între clase cu răspunsuri diferite.** Aproape totul e comun — legislația are 24 din 26 de întrebări la ambele clase, motovehiculele 5 din 5.

E opusul lotului 4b, unde totul era mono-clasă. Sonda va fi tăcută, și **asta nu e o veste bună în sine** — înseamnă doar că riscul s-a mutat: la etapa asta pericolul e **enumerarea** (§4) și **citarea** (§5), nu amestecul claselor.

Excepția: `regulament-dunare` are 13 întrebări numai-D și una numai-C. Firesc — RND e regulamentul Dunării. Acele treisprezece derivă `('D',)` prin construcție.

## 4. Legislația, sau cum să nu scrii un tabel de amenzi

Douăzeci și patru din cele 26 de întrebări de legislație cer un cuantum: *amendă de la 20.000 la 50.000 lei*. Un card cu douăsprezece afirmații care recită sume ar fi exact enumerarea pe care docstring-ul lui `theory.py` o interzice — „regula, nu enumerarea".

Dar banca chiar asta întreabă. Deci regula trebuie găsită, nu inventată, și ea există: **cuantumul urcă odată cu pericolul pentru navigație.**

- 2.000–5.000 lei — hârtii: pavilionul nearborat, refuzul de a arăta documentul de atestare
- 10.000–30.000 lei — plase și unelte fixe de pescuit în șenal, radă, port
- 20.000–50.000 lei — navigația în zone nepermise, nerespectarea Avizelor către navigatori, poluarea, refuzul controlului ANR
- 40.000–50.000 lei — neanunțarea evenimentelor de navigație: abordaj, incendiu, poluare, scufundare

Grupate pe benzi, cele douăsprezece sume devin patru afirmații care se și țin minte. Restul cardului: **infracțiune față de contravenție** (avarierea unui semnal de navigație și blocarea șenalului sunt infracțiuni; exploatarea comercială neautorizată și numele neaprobat sunt contravenții), **termenul de 15 zile** care revine de trei ori (înmatriculare, act de naționalitate, contract de construcție), și cine constată — personalul împuternicit al ANR.

Aceeași disciplină peste tot: unde banca dă o listă, caut regula din spatele ei; dacă nu există, afirmația citează faptele grupate, nu una pe rând.

## 5. Regula de citare se aplică din prima, nu la review

Etapa 4c a plătit-o de trei ori, iar măturarea finală a găsit încă 26 de cazuri. Regula, întreagă:

> Citește **doar** citatele afirmației. Susțin ele tot ce spune?

Un enunț cu spațiu liber („Care este sancțiunea pentru…") nu spune nimic singur — faptul e în răspuns. Un răspuns poate da doar jumătate din regulă — condiția e în enunț. „Citează enunțul când răspunsul e scurt" spune **care** întrebare e legată, nu că răspunsul devine opțional.

Legislația e plină de exact acest tipar: enunțul numește fapta, răspunsul dă suma. **Amândouă.**

**Sonda `scratchpad/close_sourcing.py` se rulează înainte de review, nu după** — se auto-limitează (adaugă răspunsul doar dacă e unic în tema cardului, deci „da"/„nu" rămân afară) și lasă pentru citire umană doar cazurile ambigue.

## 6. Ce înseamnă, cinstit, „100%"

După 4e fiecare temă are card, deci fiecare întrebare stă într-o temă cu teorie. **Nu** înseamnă că fiecare întrebare e citată de o afirmație.

Regula rămâne cea de la 4a: o afirmație fără nimic de răspuns e balast și iese. Reciproca e permisă — o întrebare izolată, fără o regulă în spate, rămâne necitată. Vocabularul curățat va avea astfel de întrebări (anemometrul, principiul lui Arhimede, temperatura în grade Celsius), și e corect să rămână așa: drill-ul le predă, teoria n-are ce adăuga.

Cifra care se raportează la final e **numărul de întrebări citate**, măsurat din build, nu „100%".

## 7. Lotul

Șapte carduri noi, plus extinderi la cele patru carduri care primesc întrebări mutate.

| Temă | Întrebări | Note |
|---|---|---|
| Vocabular și principii | 32 | după curățare |
| Regulament Dunăre | 29 | 16 C / 28 D, 13 numai-D |
| Manevra cu motor | 27 | +guvernarea, +bowthrusterul mutat |
| Legislație | 26 | 24 din 26 comune; benzi de amenzi |
| Motor și propulsie | 23 | |
| Semnale de pericol și salvare | 15 | semnalele + armamentul de salvare |
| Motovehicule nautice | 5 | toate comune; cinci limite |

Extinderi: `reguli-de-drum` (+10), `constructia-ambarcatiunii` (+3), `parame-noduri-ancore` (+3), `geamanduri-si-balizaj` (+2).

## 8. Verificarea

**Python.** Invariantele 4a–4c acoperă cardurile noi prin construcție: formă, octet, temă, derivarea claselor, payload, sonda de class-folding. Nou: tabelul celor 27 de mutări devine test de regresie, ca cel de 16 de la 4c.

**Node.** Garda de la 4d verifică automat că fiecare card are intrare în `THEME_PANELS` cu `theoryPanel` — deci un card nou nerregistrat pică suita, ceea ce la 4c nu se întâmpla.

**Mutații** din script Python cu `assert src.count(old) == 1`, pe stare comisă.

**Review adversarial de conținut** la fiecare card, cu accent pe legislație: sumele și încadrările sunt exact ce pică un candidat dacă le scriu greșit.

**Browser (controller), 390 px, ambele clase.** Panoul pe fiecare temă nouă, strâns, filtrat pe clasă; cele 13 afirmații numai-D de la regulamentul Dunării nu apar la clasa C; consolă curată.

## 9. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/themes.py` | cele 5 rânduri de tipar + nota despre vopsit, măsurat și respins |
| `src/caa/theory.py` | +7 carduri, +extinderile, mutarea bowthrusterului |
| `src/caa/assets/ui.js` | 7 intrări noi în `THEME_PANELS` |
| `tests/caa/test_themes.py` | regresia celor 27 de mutări |
| `tests/caa/test_theory.py` | lista temelor și totalul |
