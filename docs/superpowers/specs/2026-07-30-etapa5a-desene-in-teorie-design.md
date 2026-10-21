# Etapa 5a — o afirmație poate purta un desen

**Data:** 2026-07-30
**Etapa precedentă:** 4e (teoria pentru ultimele teme), fuzionată în `main` la `22ee724`
**Aprobare (proprietarul proiectului, 2026-07-30):** etapă mică pentru mecanism, pe cel mai ieftin caz posibil; roza compasului rămâne pentru o etapă proprie.

## 1. Ce rezolvă

Teoria e text pur. Aplicația desenează de la etapa 3b — 12 marcaje, 5 arcuri, 12 configurații de lumini — dar desenele aparțin **întrebărilor** și se adună în panouri pe temă, sub teorie. Nicio afirmație nu poate arăta ceva.

Măsurat: din 201 de afirmații, doar **10** citează o întrebare care are deja un desen. Deci problema nu e cablarea a ceea ce există; e că teoria n-a fost gândită să poarte imagini deloc.

Etapa asta adaugă capacitatea, și o dovedește pe singurul caz care nu cere niciun desen nou.

## 2. Cazul: sectorul depășirii e un arc pe care aplicația îl desenează deja

Regula din cardul „Reguli de drum" spune, cu cuvintele băncii:

> când vine dintr-o direcţie mai mare de **22°5 dinapoia traversului** celeilalte nave, astfel încât noaptea se vede numai **lumina din pupa** şi luminile din bordurile navei ajunsă din urmă

Traversul e la 90° și 270°. Cu 22°5 înapoia lui, sectorul din care ajungi din urmă se întinde de la 112,5° la 247,5° — **exact** arcul `lumina-de-pupa` din catalog, singurul de 135° de acolo.

Nu e o coincidență pe care o construiesc eu: **banca însăși face legătura**, spunând că noaptea vezi tocmai lumina din pupa. Desenul există, regula îl numește, și nimic nu le-a pus vreodată împreună.

Costul unui desen nou: **zero.**

## 3. Mecanismul

`Statement` primește un câmp opțional:

```python
drawing: str | None = None      # "arc:lumina-de-pupa"
```

Prefixat cu felul desenului, nu doar id-ul. Un câmp numit `arc` ar trebui redenumit la prima roză a compasului; un id fără fel ar cere ghicit din ce catalog vine. Cu prefix, dispecerul din `ui.js` e un `switch` de trei rânduri, iar etapele următoare adaugă un fel, nu rescriu un câmp.

Payload-ul duce câmpul mai departe când există. Nimic altceva din formă nu se schimbă: sursele rămân neexpediate, clasele rămân derivate.

**Randorul se refolosește neatins.** `arcCard(arc)` desenează deja sectorul cu eticheta lui și cu deschiderea în grade. Eticheta „Lumina de pupa" nu e redundantă lângă regula depășirii — e chiar puntea pe care o face banca.

## 4. Regula pe care o învață proiectul a treia oară

Un desen arătat unei clase care nu e examinată pe el e defectul reparat la `arcPanel` (3c), la `figurePanel` (4c) și la `signalPanel` (4d). Aici pericolul revine pe o cale nouă: o afirmație vizibilă la clasa D ar putea referi un arc pe care clasa D nu-l vede niciodată — toate arcurile sunt clasa C.

Cazul de față e curat prin construcție (afirmația derivă `('C',)`), dar **norocul nu e o garanție**. Etapa adaugă un test: pentru fiecare afirmație cu desen, fiecare clasă care vede afirmația trebuie să vadă și desenul. Nu o listă de excepții — o invariantă.

## 5. Verificarea

**Python.** O regulă de audit blocantă, `theory-drawing`: desenul referit trebuie să existe în catalogul felului său. Un id scris greșit nu ajunge în pagină.

**Node.** Testul de consistență pe clase din §4. Plus randarea: o afirmație cu desen produce figura, una fără nu produce nimic în plus.

**Mutații** din script Python cu `assert src.count(old) == 1`, pe stare comisă: schimbarea id-ului în unul inexistent trebuie să pice auditul; mutarea desenului pe o afirmație comună ambelor clase trebuie să pice testul de clase.

**Browser (controller), 390 px.** Arcul apare în cardul „Reguli de drum" la clasa C, în interiorul panoului strâns; **nu apare la clasa D**, unde afirmația nici nu există; desenul din panoul de arcuri al temei luminilor e neschimbat; consolă curată.

## 6. Ce rămâne neatins, deliberat

- **Roza compasului** și celelalte desene propuse — etape proprii. Aici se dovedește doar mecanismul.
- **Nodurile.** Banca întreabă despre nouă noduri și le cere doar categoria, niciodată forma. Un desen de nod ar fi cea mai utilă imagine din aplicație și singura pe care ar trebui s-o inventez. Nu se desenează.
- **Conținutul teoriei.** Nicio afirmație nu-și schimbă textul, sursele sau clasele.
- **Panourile de media.** Rămân cum sunt; un desen în teorie nu-l scoate din panoul temei.

## 7. Fișiere

| Fișier | Rol |
|---|---|
| `src/caa/theory.py` | câmpul `drawing`, payload, referința pe afirmația depășirii |
| `src/caa/audit.py` | regula `theory-drawing` |
| `src/caa/assets/ui.js` | dispecerul de desen în `theoryPanel` |
| `src/caa/assets/app.css` | așezarea figurii în listă |
| `tests/caa/test_theory.py` | existența desenului, forma payload-ului |
| `tests/js/panels.test.js` | consistența pe clase, randarea |
