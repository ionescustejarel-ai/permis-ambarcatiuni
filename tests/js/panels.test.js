"use strict";

// The panels show the current class's material, and nothing else. Until now
// nothing checked that.
//
// This is not a hypothetical. On the previous branch `arcPanel` shipped
// without its class filter, and a class D candidate opened the lights theme
// under five diagrams for material class D is never examined on. The fix
// landed with no regression test, and stage 3d then added a fourth panel — so
// gutting `configsForClass` to `return LIGHTS.configs` still passed every
// Python and Node test in the project.
//
// ui.js cannot be loaded whole here: its last two lines boot the application
// against a real DOM. The class filters are pure functions of the catalogue
// and the questions, so the test takes their source out of ui.js and runs it.
// That is the real code rather than a restatement of it — though it is the
// source file, not the copy inlined into the page. The page-parsing tests
// cover the gap between the two.

const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ASSETS = path.join(__dirname, "..", "..", "src", "caa", "assets");
const PAGE = path.join(__dirname, "..", "..", "build", "permis-ambarcatiuni.html");
const missing = fs.existsSync(PAGE) ? false : "build the page first: python -m caa.app";

// Each of these declarations ends with a brace in the first column.
function declaration(source, name) {
  const start = source.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `ui.js no longer declares ${name}`);
  const end = source.indexOf("\n}", start);
  assert.notEqual(end, -1, `cannot find the end of ${name}`);
  return source.slice(start, end + 2);
}

function catalogues() {
  const html = fs.readFileSync(PAGE, "utf8");
  const found = {};
  for (const [, id, body] of html.matchAll(
    /<script id="([^"]+)" type="application\/json">([\s\S]*?)<\/script>/g
  )) {
    found[id] = JSON.parse(body);
  }
  return found;
}

function filters() {
  const ui = fs.readFileSync(path.join(ASSETS, "ui.js"), "utf8");
  const data = catalogues();
  const context = {
    DATA: data.questions,
    FIGURES: data.figures,
    ARCS: data.arcs,
    LIGHTS: data.lights,
    SIGNALS: data.signals,
    THEORY: data.theory,
  };
  vm.createContext(context);
  vm.runInContext(declaration(fs.readFileSync(path.join(ASSETS, "logic.js"), "utf8"), "forClass"),
    context);
  for (const name of ["figuresForClass", "arcsForClass", "configsForClass",
                      "signalsForClass", "statementsForClass"]) {
    vm.runInContext(declaration(ui, name), context);
  }
  return context;
}

// key on the question -> the filter that must agree with it
const PANELS = [
  { key: "figure", filter: "figuresForClass" },
  { key: "arc", filter: "arcsForClass" },
  { key: "config", filter: "configsForClass" },
  { key: "signal", filter: "signalsForClass" },
];

test("a panel offers only what the class is asked about", { skip: missing }, () => {
  const data = catalogues();
  const context = filters();

  for (const panel of PANELS) {
    for (const examClass of ["C", "D"]) {
      const shown = context[panel.filter](examClass).map((entry) => entry.id);
      // What the class is actually examined on, computed here rather than
      // taken from the function under test.
      const asked = new Set(
        data.questions.questions
          .filter((question) => question.classes.includes(examClass))
          .map((question) => question[panel.key])
          .filter(Boolean)
      );
      assert.deepEqual(
        [...shown].sort(),
        [...asked].sort(),
        `${panel.filter}(${examClass}) does not match what class ${examClass} is asked`
      );
    }
  }
});

test("the figures panel shows its own theme's drawings, not the class's whole set",
  { skip: missing }, () => {
  // Stage 4c. figuresForClass was class-only, which was correct while exactly
  // one theme registered figurePanel. The day-shapes theme then registered it
  // too — and without the theme argument that page offered nine buoys under
  // "Marcajele clasei tale", where a cone and a cylinder are the whole
  // subject. Two themes carry figures; each must show only its own.
  const data = catalogues();
  const context = filters();

  const asked = (theme, examClass) => new Set(
    data.questions.questions
      .filter((q) => q.theme === theme && q.classes.includes(examClass))
      .map((q) => q.figure)
      .filter(Boolean)
  );

  for (const theme of ["geamanduri-si-balizaj", "semne-si-forme-ziua"]) {
    for (const examClass of ["C", "D"]) {
      const shown = context.figuresForClass(examClass, theme).map((f) => f.id);
      assert.deepEqual([...shown].sort(), [...asked(theme, examClass)].sort(),
        `figuresForClass(${examClass}, ${theme})`);
    }
  }
  // And the two themes really do hold different drawings, so the loop above
  // could not be satisfied by a filter that ignores its theme.
  const buoys = context.figuresForClass("C", "geamanduri-si-balizaj").map((f) => f.id);
  const shapes = context.figuresForClass("C", "semne-si-forme-ziua").map((f) => f.id);
  assert.ok(buoys.length > 0 && shapes.length > 0, "both themes carry drawings");
  assert.deepEqual(buoys.filter((id) => shapes.includes(id)), [],
    "no drawing belongs to both themes");
});

test("the two classes really are offered different material", { skip: missing }, () => {
  // Without this the test above passes on a filter that ignores its argument,
  // as long as both classes happen to be asked the same things. They are not:
  // class D is examined on no visibility arcs at all, and the sailing vessel
  // is a different configuration at each class.
  const context = filters();

  assert.deepEqual(context.arcsForClass("D").map((a) => a.id), []);
  assert.ok(context.arcsForClass("C").length > 0, "class C is examined on arcs");

  const configs = (examClass) => context.configsForClass(examClass).map((c) => c.id);
  assert.ok(configs("C").includes("vele-in-mars"), "class C gets the plain sailing vessel");
  assert.ok(!configs("C").includes("vele-in-mars-D"), "class C must not get the class D one");
  assert.ok(configs("D").includes("vele-in-mars-D"), "class D gets its own sailing vessel");
  assert.ok(!configs("D").includes("vele-in-mars"), "class D must not get the class C one");

  // Signals are the sharpest case in the app: the two classes share none.
  const signals = (examClass) => context.signalsForClass(examClass).map((s) => s.id).sort();
  assert.deepEqual(signals("D"), ["doua-lovituri-clopot", "serie-foarte-scurte"]);
  assert.equal(signals("C").length, 8);
  assert.deepEqual(signals("C").filter((id) => signals("D").includes(id)), [],
    "the two classes are examined on disjoint signals");
});


test("every theme with theory offers only its class's statements", { skip: missing }, () => {
  const data = catalogues();
  const context = filters();

  for (const card of data.theory.cards) {
    for (const examClass of ["C", "D"]) {
      const shown = context.statementsForClass(card.theme, examClass).map((s) => s.text);
      const expected = card.statements
        .filter((s) => s.classes.includes(examClass))
        .map((s) => s.text);
      assert.deepEqual(shown, expected, `${card.theme} / ${examClass}`);
    }
  }
  // Every card the build ships, and at least one theme where the two classes
  // differ — otherwise a filter that ignores its argument would satisfy the
  // loop above. The count lives in the Python suite, which owns it; repeating
  // it here in prose only bred a stale comment, twice.
  assert.ok(data.theory.cards.length > 0, "the page ships no theory at all");
  const differing = data.theory.cards.filter((card) =>
    context.statementsForClass(card.theme, "C").length !==
    context.statementsForClass(card.theme, "D").length);
  assert.ok(differing.length > 0, "no theme distinguishes the classes");
});

test("an unknown theme yields nothing rather than throwing", { skip: missing }, () => {
  // This used to name a real theme that had no card yet — first
  // meteo-si-hidrologie, then motor-si-propulsie — and each stage that gave
  // that theme a card broke the test. After stage 4e no theme is without
  // theory, so the case is now a slug that is asserted not to be one: if a
  // theme by this name is ever added, the test says so instead of quietly
  // testing nothing.
  const data = catalogues();
  const context = filters();
  const absent = "tema-care-nu-exista";
  assert.ok(!data.theory.cards.some((card) => card.theme === absent),
    `${absent} is now a real theme; pick another name for this test`);

  assert.deepEqual(context.statementsForClass(absent, "C"), []);
  assert.deepEqual(context.statementsForClass(undefined, "C"), []);
});

test("every card the build ships is registered for a panel", { skip: missing }, () => {
  // Writing a card is two steps, and the second is silent when skipped. The
  // day-shapes theme had no THEME_PANELS entry from c651ffc until stage 4c:
  // three drawings existed, were built into the page, and were never once
  // rendered. Nothing failed. Measured again on this branch — deleting the
  // compass entry, or mistyping one slug, left the whole suite green while a
  // nine-rule card vanished from the app.
  const ui = fs.readFileSync(path.join(ASSETS, "ui.js"), "utf8");
  const start = ui.indexOf("const THEME_PANELS = {");
  assert.notEqual(start, -1, "ui.js no longer declares THEME_PANELS");
  const end = ui.indexOf("\n};", start);
  assert.notEqual(end, -1, "cannot find the end of THEME_PANELS");

  // Evaluated, not pattern-matched: the builders become named stubs so the
  // test reads the real object, including which builder each theme lists.
  const names = ["theoryPanel", "figurePanel", "arcPanel", "configPanel", "signalPanel"];
  const context = {};
  for (const name of names) context[name] = () => name;
  vm.createContext(context);
  vm.runInContext(ui.slice(start, end + 3) + "\nTHEME_PANELS;", context);
  const panels = vm.runInContext("THEME_PANELS", context);

  for (const card of catalogues().theory.cards) {
    const builders = panels[card.theme];
    assert.ok(builders, `theme ${card.theme} has a theory card and no panel entry`);
    assert.ok(builders.map((b) => b()).includes("theoryPanel"),
      `theme ${card.theme} is registered but not for its theory`);
  }
  // And no entry names a theme that does not exist, which is how a typo hides.
  const themes = new Set(catalogues().questions.questions.map((q) => q.theme));
  for (const slug of Object.keys(panels)) {
    assert.ok(themes.has(slug), `THEME_PANELS registers unknown theme ${slug}`);
  }
});

test("the theme dispatch hands every panel builder its theme", { skip: missing }, () => {
  // The regression this pins: reverting `build(theme)` to `build()` hands
  // theoryPanel an undefined theme, statementsForClass finds no card, the
  // panel declines, and the theory silently vanishes from every theme —
  // with every other test green. The builders are argument-sensitive by
  // design (next test), so the call site is the single point of failure.
  const ui = fs.readFileSync(path.join(ASSETS, "ui.js"), "utf8");
  assert.match(
    ui,
    /for \(const build of THEME_PANELS\[theme\] \|\| \[\]\) \{\s*\n\s*const panel = build\(theme\);/,
    "App.tema no longer passes the theme to its panel builders"
  );
});

test("every panel folds, counts, and is actually rendered", { skip: missing }, () => {
  // The stage's whole point, and nothing guarded it: reverting one panel from
  // <details> to <section> left all 96 tests green while the lights theme went
  // back to a 1693px wall of diagrams before the first question. The same shape
  // as arcPanel at 3c, figurePanel at 4c and signalPanel here — written, and
  // never checked. Read from source, because these builders need a live DOM.
  const ui = fs.readFileSync(path.join(ASSETS, "ui.js"), "utf8");

  for (const name of ["figurePanel", "arcPanel", "configPanel", "signalPanel"]) {
    const body = declaration(ui, name);
    assert.match(body, /el\("details", \{ class: "mediapanel /,
      `${name} no longer builds a folding panel`);
    assert.doesNotMatch(body, /\bopen\b/, `${name} must not open itself by default`);
    assert.match(body, /countLabel\(/, `${name} counts without the Romanian helper`);
  }
  assert.doesNotMatch(ui, /el\("section", \{ class: "\w+panel"/,
    "a panel is still built as a plain section");

  // A drill wipes the children of whatever it is handed on every question, so
  // anything placed above one needs its own container. That cost the window
  // bar once already.
  // The lookbehind skips the declaration, whose own parameter is named root.
  assert.ok(/function startDrill\(/.test(ui), "startDrill is gone; this guard is stale");
  assert.doesNotMatch(ui, /(?<!function )startDrill\(root,/,
    "a screen hands the drill its own root, which wipes whatever sits above it");

  // classNote is written; this is what makes sure it is also shown.
  assert.match(ui, /root\.append\(classNote\(\)\)/, "the class explanation is never rendered");
});

test("a statement's drawing is one its own classes are examined on", { skip: missing }, () => {
  // The fourth time this project has had to say it: arcPanel shipped without a
  // class filter at 3c, figurePanel without a theme one at 4c, signalPanel with
  // no filter at all at 4d. Now a statement can reference a drawing directly,
  // and the same mistake has a new road in — every arc in the catalogue is a
  // class C arc, so a rule shown at class D must never point at one.
  // Today's single reference is class C and safe by construction; luck is not
  // a guarantee, so this is an invariant rather than a cleared list.
  const data = catalogues();
  const context = filters();

  // Kinds whose entries are examined material: each one is bound to questions,
  // so a class either meets it or never does, and showing the wrong one is the
  // defect above.
  const forClass = {
    arc: (cls) => context.arcsForClass(cls).map((a) => a.id),
    figure: (cls) => data.questions.questions
      .filter((q) => q.classes.includes(cls)).map((q) => q.figure).filter(Boolean),
    config: (cls) => context.configsForClass(cls).map((c) => c.id),
    signal: (cls) => context.signalsForClass(cls).map((s) => s.id),
  };
  // Kinds that illustrate a rule rather than reproduce examined material. A
  // compass rose is not something a class is or is not asked about — it draws
  // the definition the statement already carries, and the statement's own
  // classes are the gate. Declared here rather than skipped silently, so a
  // kind added later cannot slip through unclassified.
  const conceptual = new Set(["rose", "schema"]);

  let checked = 0;
  for (const card of data.theory.cards) {
    for (const statement of card.statements) {
      if (!statement.drawing) continue;
      checked += 1;
      const [kind, id] = statement.drawing.split(":");
      assert.ok(forClass[kind] || conceptual.has(kind),
        `drawing kind ${kind} is neither class-bound nor declared conceptual`);
      if (!forClass[kind]) continue;
      for (const cls of statement.classes) {
        assert.ok(forClass[kind](cls).includes(id),
          `${card.theme}: a statement shown at class ${cls} draws ${statement.drawing}, `
          + `which class ${cls} is never examined on`);
      }
    }
  }
  assert.ok(checked > 0, "no statement carries a drawing; this test proves nothing");
});

test("the retired word never comes back into the interface", { skip: missing }, () => {
  // "nesigur" read as a verdict about the candidate rather than a state the app
  // computes, and the rule behind it was never written down. Both are fixed;
  // this keeps the word from creeping back in the next hurried edit. Only text
  // that reaches the page is checked — the code still calls its own internals
  // unsafeIds and blacklist, which no candidate ever sees.
  // Comments are stripped first, and that is not cosmetic: without it a
  // Romanian `// lista "nesigure" ramane calculata la fel` fails a test about
  // the interface. logic.js carries exactly such a line today.
  const ui = fs.readFileSync(path.join(ASSETS, "ui.js"), "utf8")
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/^[ \t]*\/\/.*$/gm, "");
  const offenders = [];
  for (const match of ui.matchAll(/"([^"\n]*)"|`([^`\n]*)`/g)) {
    const text = match[1] ?? match[2];
    if (/nesigur/i.test(text)) offenders.push(text);
  }
  assert.deepEqual(offenders, [], "these strings still say 'nesigur'");

  // Deliberately no second check against the built page. Every word the
  // candidate reads is produced by JS at runtime, so once the inlined scripts
  // are stripped the page holds a <title> and three fragments of CSS — an
  // assertion over that cannot fail from a UI regression, and one that cannot
  // fail is worse than none. The source check above is the real guard.
});

test("theoryPanel needs its theme argument and declines without one", { skip: missing }, () => {
  // The other half of the guard above: proves the argument matters, so the
  // source assertion is pinning a live wire and not a stylistic choice.
  const ui = fs.readFileSync(path.join(ASSETS, "ui.js"), "utf8");
  const data = catalogues();
  const context = {
    THEORY: data.theory,
    App: { state: { examClass: "C" } },
    el(tag, attrs, ...children) {
      return { tag, children, append(...more) { this.children.push(...more); } };
    },
  };
  vm.createContext(context);
  // theoryPanel counts in Romanian through logic.js, like every panel does.
  vm.runInContext(declaration(fs.readFileSync(path.join(ASSETS, "logic.js"), "utf8"), "countLabel"),
    context);
  vm.runInContext(declaration(ui, "statementsForClass"), context);
  // A statement may carry a drawing; the panel asks for one on every line.
  vm.runInContext(declaration(ui, "statementDrawing"), context);
  vm.runInContext(declaration(ui, "theoryPanel"), context);

  const themed = vm.runInContext('theoryPanel("parame-noduri-ancore")', context);
  assert.notEqual(themed, null, "a theme with statements must yield a panel");
  const bare = vm.runInContext("theoryPanel(undefined)", context);
  assert.equal(bare, null, "an undefined theme must yield no panel, not a crash");
});
