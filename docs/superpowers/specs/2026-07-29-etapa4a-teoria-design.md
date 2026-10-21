# Etapa 4a — teoria: mecanismul și primele trei teme

**Data:** 2026-07-29
**Etapa precedentă:** 3f (progresul durabil), fuzionată în `main`
**Spec-părinte:** `2026-07-25-permis-ambarcatiuni-design.md` §9
**Decizii de scope (proprietarul proiectului, 2026-07-29):** mecanism + cele mai mari 3 teme comune acum, restul în 4b/4c pe loturi; **fără** testul de temă și deblocarea la 90% din §9 — abaterea e asumată aici.

## 1. Ce rezolvă

Aplicația are drill, simulare, figuri, sunete — dar nicio teorie. Candidatul învață exclusiv din greșeli, întrebare cu întrebare. Spec-ul părinte cere stratul care lipsește: **cardul de teorie scurt** — „regula, nu enumerarea" — cu regula care îl ține onest: *fiecare afirmație trebuie să răspundă la cel puțin o întrebare din banca oficială; ce nu răspunde la nimic e balast și iese.*

Etapa 4a construiește mecanismul și îl umple pentru cele mai mari trei teme, comune ambelor clase:

| Temă | Întrebări | C | D | comune |
|---|---|---|---|---|
| Parâme, noduri, ancore | 131 | 106 | 105 | 80 |
| Prim ajutor | 50 | 50 | 50 | 50 |
| Construcția ambarcațiunii | 29 | 24 | 19 | 14 |

210 întrebări din 603 — mai mult de o treime din bancă — capătă teorie într-o singură etapă.

## 2. Teoria e al cincilea catalog

Aceeași disciplină ca semnalele, marcajele, arcurile și configurațiile: **date Python, citate verbatim, audit blocant.** `src/caa/theory.py`, construit pe `caa.catalogue`:

```python
Statement(
    text="Nodul bun se face ușor, se desface ușor, ține sub sarcină și nu strică parâma.",
    sources=(
        "usor de facut,usor de desfacut,rezistent,nu deterioreaza parama",
    ),
)
```

- `text` — regula, în cuvintele mele, română, ajunge în interfață. **Primul conținut ne-verbatim din aplicație** — de aceea are trei porți, nu una (§4).
- `sources` — citatele din bancă (enunț întreg sau răspuns corect întreg, la octet) pe care afirmația le predă. Tuplu gol = balast prin definiție = build picat.

```python
Card(theme="parame-noduri-ancore", statements=(<afirmațiile temei, ca mai sus>,))
```

O temă, un card. Cardul nu conține id-uri de întrebări și nu declară clase — amândouă se derivă (§3).

Conținutul se scrie **din** manualele din `sources/arhiva/` (manualul conducătorului, marinărie, navigație) și se **validează împotriva** băncii, cum cere spec-ul părinte. Ce spune manualul dar banca nu întreabă, nu intră.

## 3. Clasele se derivă, nu se declară

La build, clasele unei afirmații = reuniunea claselor întrebărilor din care vin citatele ei. O afirmație cu toate citatele din întrebări doar-C nu apare la clasa D — filtrarea pe clasă e la **toate** panourile, regulă veche a proiectului, iar aici vine gratis din citate, fără nicio decizie de mână.

Deriverea trăiește în build (`cli.py`/`theory.py`), nu în JS: pagina primește claselele gata calculate în payload.

## 4. Cele trei porți ale onestității

Textul afirmațiilor e proza mea — nu poate fi verificat la octet. De aceea:

1. **`theory-source`** (audit, blocant): fiecare citat există în bancă, la octet — ca la celelalte patru cataloage. ANR reformulează → build picat.
2. **`theory-theme`** (audit, blocant): fiecare citat al unei afirmații aparține unei întrebări **din tema cardului**. O regulă despre noduri sprijinită pe o întrebare de meteo e mis-shelved mecanic, nu stilistic. Regula validează implicit și că `card.theme` e o temă reală.
3. **Review de conținut adversarial** (proces, la review-ul de task): pentru fiecare afirmație, reviewerul primește afirmația lângă citatele ei și întrebarea unică: *afirmația susține ceva ce citatele ei nu susțin?* O afirmație care generalizează dincolo de citate se taie sau se leagă de citate în plus.

Ce NU e regulă: acoperirea băncii de către teorie. Spec-ul părinte cere direcția afirmații→bancă, nu invers; o întrebare fără teorie e un gol de conținut pentru 4b, nu o eroare de build.

## 5. Interfața

**Panoul de teorie e primul strat al temei** — §9 dă ordinea: teorie → media → drill. `THEME_PANELS` are deja liste; `theoryPanel` intră **primul** în lista temei lui.

Panoul e un `<details>` nativ, **strâns implicit**, cu rezumatul „Teoria temei · N reguli":
- pe telefon, 25 de reguli deschise ar împinge drill-ul cu trei ecrane mai jos; strâns, tema se deschide direct pe întrebări, cu teoria la un gest distanță
- `<details>` nu cere stare, JS sau gardă de tastatură — elementul e nativ focusabil și anunțat corect

Afirmațiile se afișează filtrate pe clasa curentă; un card rămas fără afirmații pentru clasa curentă nu se randează deloc (regula existentă a panourilor). **Nimic în simulare** și nimic lângă răspunsuri în drill — teoria e fișă de referință, legarea per-întrebare o au deja figurile și semnalele.

## 6. Abaterile de la spec-ul părinte, asumate

- **Fără test de temă și fără deblocare la 90%.** Aplicația a evoluat pe alt model de progresie: lista neagră + conturul 40 + expirarea siguranței. Gărduirea ar forța o ordine pe un singur candidat care se poate autodirija. Decis de proprietarul proiectului.
- **Teoria strânsă implicit**, nu strat obligatoriu înaintea drill-ului — același motiv.

## 7. Ce măsoară dimensiunea conținutului

Numărul de afirmații per card **nu e fixat de spec** — auditul impune trasabilitatea, nu numărul. Ținta de lucru, din structura măsurată a temelor: parâme ~25–35 (ancore 24 î, noduri 16, armament 9, parâme 9, restul de 67 se cartografiază la scrierea planului), prim ajutor ~15–20, construcția ~10–15. Planul poartă conținutul complet, generat cu citatele extrase din `build/questions.json`, nu retastate.

## 8. Verificarea

**Python.** Forma catalogului (temă reală, afirmații nevide, citate nevide); byte-exact contra băncii; regula `theory-theme` demonstrată că mușcă (citat mutat pe card străin → constatare); deriverea claselor (afirmație cu citate doar-C nu poartă D); ambele reguli de audit cu mutații pe stare comisă.

**Browser (controller).** Panoul prezent pe cele trei teme și absent pe oricare alta; strâns implicit, deschidere/închidere cu tastatura; filtrat pe clasă (o afirmație doar-C invizibilă la D); nimic în simulare; 390 px; consolă curată.

## 9. În afara scopului, deliberat

- **Celelalte 17 teme** — 4b/4c, pe loturi, cu același mecanism.
- **Testul de temă** — renunțat (§6).
- **Legarea teoriei per-întrebare în drill** — fișa e pe temă; drill-ul are deja media legată.
- **Căutare/index în teorie** — trei carduri nu justifică.

## 10. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/theory.py` | **nou** — `Statement`, `Card`, `THEORY`, validare, payload |
| `src/caa/audit.py` | +2 reguli blocante (`theory-source`, `theory-theme`) |
| `src/caa/cli.py` | nimic (teoria nu se leagă per-întrebare) |
| `src/caa/app.py` | emite `<script id="theory">` |
| `src/caa/assets/index.html` | marcatorul `/*THEORY*/` |
| `src/caa/assets/ui.js` | `theoryPanel`, primul în listele celor trei teme |
| `src/caa/assets/app.css` | panoul |
| `tests/caa/test_theory.py` | **nou** |
