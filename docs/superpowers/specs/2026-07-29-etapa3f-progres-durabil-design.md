# Etapa 3f — progresul durabil și finisaje

**Data:** 2026-07-29
**Etapa precedentă:** 3e (clasificatorul de teme), fuzionată în `main`
**Origine:** analiza completă a aplicației din 2026-07-29; toate cele șase puncte aprobate explicit, cu ordinea valorică stabilită
**Etapa următoare:** 4 (fișele de teorie)

## 1. Ce rezolvă

Aplicația e corectă dar fragilă în jurul unui singur lucru: **progresul candidatului trăiește exclusiv în localStorage**. Un istoric șters, un telefon schimbat, un fișier mutat în alt folder sau orice viitor bump de `PROGRESS_VERSION` (la mismatch, `App.load` aruncă tot) șterge săptămâni de studiu fără avertisment. Restul punctelor sunt finisaje măsurate la analiză: siguranța permanentă contrazice propriul raționament din cod despre retenție, raportul de examen nu arată răspunsul corect, examenul de diferență nu-și spune direcția, tema întunecată n-are comutator, iar o temă fără întrebări crapă ecranul.

Numai JavaScript și CSS. Pipeline-ul Python, banca și auditul nu se ating.

## 2. Export și import de progres

**Export.** Buton pe Acasă: „Salvează progresul". Descarcă `permis-progres-YYYY-MM-DD.json` — exact obiectul `App.state`, serializat. Fără dependențe: `Blob` + `URL.createObjectURL` + un `<a download>` temporar; funcționează de pe disc, cu rețeaua oprită.

**Import.** Buton alături: „Încarcă progresul", un `<input type="file">` ascuns. Fișierul se citește, se validează și **înlocuiește starea în întregime** — înlocuire, nu contopire: două stări divergente contopite ar produce un istoric pe care nu l-a trăit nimeni. Înlocuirea cere confirmare **în pagină** (buton în doi pași — „Sigur? Înlocuiește tot progresul"), nu `window.confirm`: aplicația nu are niciun dialog modal și nu începe acum.

**Importul este migrarea.** Validarea trăiește în `logic.js` ca funcție pură, `adoptProgress(raw) -> state | null`:
- `version` numeric și `<= PROGRESS_VERSION`; versiunile viitoare adaugă aici pașii de upgrade, per versiune
- `examClass` în `{C, D}`; `q` obiect; `exams` listă
- orice altceva → `null`, iar interfața spune pe ecran ce n-a mers, fără să atingă starea curentă

`PROGRESS_VERSION` rămâne 1 — nimic din etapa asta nu schimbă forma stării.

## 3. Siguranța expiră

`isSafe` primește al treilea parametru: `isSafe(state, id, today)`. O întrebare e sigură dacă are seria de azi **și** confirmarea e recentă:

```
streak >= 2  &&  lastDay > streakStart  &&  0 <= daysBetween(lastDay, today) <= 30
```

- `SAFETY_SHELF_DAYS = 30`, constantă declarată, nu număr îngropat.
- `daysBetween(a, b)` — funcție pură nouă peste datele ISO existente.
- **Reconfirmarea costă un singur răspuns corect**, nu doi: seria e deja ≥ 2, un răspuns corect azi împinge `lastDay` la zi și siguranța revine. Uitarea completă (răspuns greșit) rupe seria și cere din nou două zile, ca acum.
- **Ceasul dat înapoi lasă întrebarea nesigură** (`0 <=` respins) — aceeași direcție aleasă deja în comentariul lui `isSafe`: dintre două erori despre ceas, o alegem pe cea care nu costă puncte în sala de examen.
- Toți apelanții (`blacklist`, `drillOrder`, `unsafeIds`, `themeSoundings`, tabloul de bord, drill-ul) primesc `App.today()`. Semnătura veche cu doi parametri dispare, nu rămâne cu default — un apel uitat ar reintroduce tăcut siguranța veșnică.

## 4. Răspunsul corect, în raportul de examen

În „Ce ai greșit", sub fiecare întrebare, **textul răspunsului corect**, nu doar link-ul spre temă. Candidatul care a picat vrea să vadă acolo ce era corect; drumul spre drill rămâne.

## 5. Direcția examenului de diferență

Extragerea folosește disciplina distinctivă a **clasei curente** — deci e diferența *spre* clasa curentă. Se spune: butonul de pe Acasă devine „Examen de diferență — spre clasa C" (clasa curentă), iar titlul ecranului la fel. Nicio schimbare de logică.

## 6. Comutator de temă

`state.theme ∈ {"auto", "light", "dark"}`, implicit `"auto"` (câmp absent = `"auto"`, deci stările vechi rămân valide fără bump de versiune). Un buton pe Acasă ciclează cele trei stări și scrie `data-theme` pe `<html>`.

CSS: paletele devin adresabile — blocul `@media (prefers-color-scheme: dark)` rămâne pentru `auto`, iar `:root[data-theme="dark"]` / `:root[data-theme="light"]` forțează explicit. Variabilele întunecate apar de două ori (media query + selector); e duplicarea minimă fără preprocesor, și se scrie un comentariu care leagă cele două locuri.

## 7. Garda pe tema goală

`SCREENS.tema` crapă azi pentru o temă fără întrebări la clasa curentă — inaccesibil din interfață (lista de teme le exclude), dar o rută tastată de mână sau o ediție viitoare a băncii îl expune. Drill-ul primește garda: zero întrebări → mesaj în pagină („Nicio întrebare pentru clasa ta la tema asta"), navigația rămâne utilizabilă. Tiparul există deja pentru ecranul inexistent.

## 8. Verificarea

**Node (pure).** `adoptProgress` pe stări valide, corupte, cu versiune viitoare, cu clasă inexistentă; `daysBetween` peste granițe de lună și an; expirarea — sigură la 30, nesigură la 31, nesigură cu ceasul înapoi, reconfirmarea dintr-un singur răspuns; garda pe listă goală.

**Browser.** Export → fișier descărcat cu conținutul stării; import valid → starea înlocuită și tabloul de bord re-randat; import corupt → mesaj, starea neatinsă; confirmarea în doi pași; comutatorul de temă în toate cele trei stări (și persistența lui); răspunsul corect vizibil în raport după un examen picat; eticheta diferenței; consola curată, 390 px fără overflow, tastatura.

## 9. În afara scopului, deliberat

- **Sincronizare între dispozitive, cloud, QR** — exportul pe fișier e suficient pentru un singur candidat.
- **Curbă de uitare graduală** (intervale crescânde, SM-2) — un prag fix de 30 de zile e verificabil și explicabil; algoritmica adaptivă nu se justifică pentru un examen cu dată fixă.
- **Migrări de versiune reale** — nu există încă o versiune 2; `adoptProgress` doar rezervă locul.
- **Reproiectarea raportului de examen** — se adaugă răspunsul corect, nu se rescrie ecranul.

## 10. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/assets/logic.js` | `adoptProgress`, `daysBetween`, `isSafe` cu expirare, `SAFETY_SHELF_DAYS` |
| `src/caa/assets/ui.js` | export/import + confirmare, apelanții lui `isSafe`, raportul, eticheta diferenței, comutatorul, garda |
| `src/caa/assets/app.css` | paletele adresabile, butoanele noi |
| `tests/js/logic.test.js` | tot §8 Node |
