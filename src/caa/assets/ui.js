"use strict";

// Rendering and events. Every decision belongs to logic.js; this file owns the
// DOM and nothing else. Verified in a real browser, not unit-tested.

const STORAGE_KEY = "permis-ambarcatiuni/v1";

const DATA = JSON.parse(document.getElementById("questions").textContent);
const RULES = JSON.parse(document.getElementById("rules").textContent);

const SIGNALS = JSON.parse(document.getElementById("signals").textContent);
const SIGNAL_BY_ID = Object.fromEntries(SIGNALS.signals.map((s) => [s.id, s]));

const FIGURES = JSON.parse(document.getElementById("figures").textContent);
const FIGURE_BY_ID = Object.fromEntries(FIGURES.figures.map((f) => [f.id, f]));

const ARCS = JSON.parse(document.getElementById("arcs").textContent);
const ARC_BY_ID = Object.fromEntries(ARCS.arcs.map((a) => [a.id, a]));

const LIGHTS = JSON.parse(document.getElementById("lights").textContent);
const CONFIG_BY_ID = Object.fromEntries(LIGHTS.configs.map((c) => [c.id, c]));

const ROSES = JSON.parse(document.getElementById("roses").textContent);
const SCHEMAS = JSON.parse(document.getElementById("schemas").textContent);
const THEORY = JSON.parse(document.getElementById("theory").textContent);

const SYSTEM_LABELS = {
  iala: "Sistem IALA",
  dunare: "Balizaj dunărean",
  "day-shape": "Semn de zi",
};

const GLYPHS = { long: "▬", short: "▪", "very-short": "·", stroke: "●" };

// The written wording is what the exam marks, so the pattern is shown as well
// as played: the strip works with the sound off and reinforces the words.
// A figure belongs to the classes of the questions that describe it. The two
// buoyage systems contradict each other — left is a green cone on the Danube
// and port is a red cylinder at IALA region A — so a candidate must never see
// the other system's mark beside their own.
// The theme narrows it further. Until stage 4c this filter was class-only,
// which was correct while exactly one theme showed the panel. Registering it
// on a second theme made it show every mark of the class on both: nine buoys
// under "Marcajele clasei tale" on the day-shapes theme, where a cone and a
// cylinder are the whole subject. A panel that ignores its theme is only ever
// one registration away from being wrong.
function figuresForClass(examClass, theme) {
  const asked = forClass(DATA.questions, examClass)
    .filter((question) => theme === undefined || question.theme === theme);
  const wanted = new Set(asked.map((question) => question.figure).filter(Boolean));
  return FIGURES.figures.filter((figure) => wanted.has(figure.id));
}

function figureCard(figure) {
  return el("figure", { class: "figurecard" },
    drawFigure(figure, 84),
    el("figcaption", {},
      el("span", {}, figure.label),
      el("span", { class: "system" }, SYSTEM_LABELS[figure.system] || figure.system)));
}

function figurePanel(theme) {
  const shown = figuresForClass(App.state.examClass, theme);
  if (shown.length === 0) return null;

  // A cone hoisted at the bow is a semn, not a marcaj: the heading follows
  // the theme rather than calling every drawing a buoy.
  const wrap = el("details", { class: "mediapanel figurepanel" },
    el("summary", {}, theme === "semne-si-forme-ziua"
      ? `Semnele clasei tale · ${countLabel(shown.length, "un semn", "semne")}`
      : `Marcajele clasei tale · ${countLabel(shown.length, "un marcaj", "marcaje")}`));
  const grid = el("div", { class: "figuregrid" });
  for (const figure of shown) grid.append(figureCard(figure));
  wrap.append(grid);

  // Each note is shown only when the panel contains what it talks about. The
  // cardinal sentence read as a puzzle on class D, which has no cardinal at
  // all, and the flashing one is pointless where nothing carries a light.
  const notes = [];
  if (shown.some((figure) => figure.id.startsWith("cardinal-"))) {
    notes.push("Cardinalele apar fără semn de vârf: banca întreabă doar dungile de pe corp.");
  }
  if (shown.some((figure) => figure.light)) {
    notes.push("Ritmul clipirii e ales ca lumina să se vadă; regulamentul spune doar „intermitentă”.");
  }
  if (notes.length) wrap.append(el("p", { class: "note" }, notes.join(" ")));
  return wrap;
}


function arcCard(arc) {
  const openings = arc.sectors.map((sector) => `${sectorSpan(sector)}°`).join(" + ");
  return el("figure", { class: "arccard" },
    drawArc(arc, 92),
    el("figcaption", {},
      el("span", {}, arc.label),
      // The number as well as the picture: the drawing makes it memorable,
      // the figure makes it exact, and the exam marks the number.
      el("span", { class: "opening figure" }, openings)));
}

// An arc belongs to the classes of the questions that define it, exactly as a
// mark does. Every arc question is a class C one, while the theme that hosts
// this panel also carries fourteen class D questions on vessel lights — so
// without the filter a class D candidate opens their theme under five diagrams
// for material they are never examined on. The arcs are not wrong for them,
// they are simply not theirs.
function arcsForClass(examClass) {
  const wanted = new Set(
    forClass(DATA.questions, examClass).map((question) => question.arc).filter(Boolean)
  );
  return ARCS.arcs.filter((arc) => wanted.has(arc.id));
}

function arcPanel() {
  const shown = arcsForClass(App.state.examClass);
  if (shown.length === 0) return null;

  const wrap = el("details", { class: "mediapanel arcpanel" },
    el("summary", {},
      `Pe ce arc se vede fiecare lumină · ${countLabel(shown.length, "un arc", "arcuri")}`));
  const grid = el("div", { class: "arcgrid" });
  for (const arc of shown) grid.append(arcCard(arc));
  wrap.append(grid);
  wrap.append(el("p", { class: "note" },
    "Nava e văzută de sus, cu prova în sus și tribordul în dreapta. "
    + "Orientarea e aleasă ca desenul să se citească; regulamentul dă doar unghiurile."));
  return wrap;
}

// A configuration belongs to the classes of the questions that name it, exactly
// as a mark or an arc does.
function configsForClass(examClass) {
  const wanted = new Set(
    forClass(DATA.questions, examClass).map((question) => question.config).filter(Boolean)
  );
  return LIGHTS.configs.filter((config) => wanted.has(config.id));
}

function configCard(config) {
  return el("figure", { class: "configcard" },
    drawConfig(config, 148),
    el("figcaption", {},
      el("span", {}, config.label),
      config.note ? el("span", { class: "qualifier" }, config.note) : null));
}

function configPanel() {
  const shown = configsForClass(App.state.examClass);
  if (shown.length === 0) return null;

  const wrap = el("details", { class: "mediapanel configpanel" },
    el("summary", {}, "Ce lumini poartă fiecare navă · "
      + countLabel(shown.length, "o configurație", "configurații")));
  const grid = el("div", { class: "configgrid" });
  for (const config of shown) grid.append(configCard(config));
  wrap.append(grid);
  wrap.append(el("p", { class: "note" },
    "Nava e văzută din profil, cu prova la dreapta. Regulament e numai ordinea pe verticală "
    + "și pozițiile pe care banca le spune; unde sursa nu dă poziția, lumina stă pe catargul "
    + "scurt de la mijloc. Luminile de bord se desenează ca o pereche."));
  return wrap;
}

function patternStrip(signal) {
  return el("span", { class: "pattern", "aria-hidden": "true" },
    signal.pattern.map((kind) => GLYPHS[kind]).join(" "));
}

// Extracted for the same reason its three siblings are: panels.test.js lifts
// these filters out of this file and regression-tests them. On an earlier
// branch `arcPanel` shipped with its filter missing and every test in the
// project stayed green — a class D candidate read five diagrams of material
// they are never examined on. Inlined here, gutting this filter would be
// invisible in exactly the same way.
function statementsForClass(theme, examClass) {
  const card = THEORY.cards.find((entry) => entry.theme === theme);
  if (!card) return [];
  return card.statements.filter(
    (statement) => statement.classes.indexOf(examClass) !== -1
  );
}

// The theme's first layer, per the parent spec: theory, then media, then
// drill. Collapsed by default — on a phone, an open card of twenty rules
// would push the drill three screens down; closed, the theme opens straight
// onto its questions with the theory one gesture away. <details> needs no
// state, no key handling and no guard: the element is native.
function theoryPanel(theme) {
  const shown = statementsForClass(theme, App.state.examClass);
  if (shown.length === 0) return null;

  const box = el("details", { class: "theorypanel" },
    el("summary", {}, `Teoria temei · ${countLabel(shown.length, "o regulă", "reguli")}`));
  const list = el("ul", {});
  for (const statement of shown) {
    list.append(el("li", {}, statement.text, statementDrawing(statement)));
  }
  box.append(list);
  return box;
}

// A rule the bank itself ties to a picture gets the picture beside it. The
// reference is "kind:id", so the catalogue is named rather than guessed; an
// unknown kind draws nothing rather than throwing, and the audit has already
// refused to build an id that does not exist.
function statementDrawing(statement) {
  if (!statement.drawing) return null;
  const [kind, id] = statement.drawing.split(":");
  if (kind === "arc") {
    const arc = ARCS.arcs.find((entry) => entry.id === id);
    return arc ? arcCard(arc) : null;
  }
  if (kind === "rose") {
    const rose = ROSES.roses.find((entry) => entry.id === id);
    return rose ? roseCard(rose) : null;
  }
  if (kind === "schema") {
    const schema = SCHEMAS.schemas.find((entry) => entry.id === id);
    return schema ? schemaCard(schema) : null;
  }
  return null;
}

function playButton(signal, text) {
  return el("button", { class: "play", onclick: () => Audio2.play(signal, SIGNALS.timing) },
    "▶ ", text || signal.label);
}

// A screen that owns something outliving its own markup — so far only the
// exam's timer — registers how to stop it here. Without this an abandoned exam
// keeps ticking against a page that no longer exists, and at its deadline it
// grades itself, writes a result the candidate never sat, and replaces whatever
// screen they had moved on to.
let releaseScreen = null;

const App = {
  state: null,
  route: "acasa",

  // Which slice of the practice list is on screen. A view preference for this
  // visit only: it has no business in the progress file, and an import must
  // not carry one candidate's filter into another's history.
  wrongWindow: null,

  today() {
    const now = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  },

  load() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
      // A progress record from an older shape is discarded rather than guessed at.
      if (saved && saved.version === PROGRESS_VERSION) return saved;
    } catch (error) {
      // Corrupt storage is not worth recovering; start clean.
    }
    return createProgress("C");
  },

  // Storage can throw: quota exceeded, or a browser with storage switched off.
  // Unguarded, that exception escapes the click handler that called it and
  // aborts the drill mid-answer with nothing on screen to explain it. Say it
  // once, then let the session continue unsaved rather than break.
  save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(App.state));
    } catch (error) {
      showStorageWarning();
    }
  },

  setClass(examClass) {
    App.state.examClass = examClass;
    App.save();
    App.go(App.route);
  },

  go(route) {
    App.route = route;
    // Each screen installs its own key handler; clear the previous one or a
    // drill's number keys keep firing after you have navigated away.
    document.onkeydown = null;
    // Sound belongs to the screen that started it.
    Audio2.stop();
    if (releaseScreen) {
      releaseScreen();
      releaseScreen = null;
    }
    const app = document.getElementById("app");
    app.replaceChildren();
    const [name, argument] = route.split(":");
    const screen = SCREENS[name];
    if (typeof screen !== "function") {
      // A blank page with an error only in the console is the worst way to
      // fail: the reader sees nothing and reports nothing useful. Say it on
      // screen and leave the navigation usable.
      app.append(el("p", { class: "eyebrow" }, "Ecran indisponibil"));
      app.append(el("h1", {}, `Nu există un ecran „${name}”.`));
      app.append(el("p", {}, "Folosește bara de jos ca să continui."));
      renderNav();
      return;
    }
    screen(app, argument);
    renderNav();
  },
};

const THEME_LABELS = {
  "vocabular-si-principii": "Vocabular și principii",
  "parame-noduri-ancore": "Parâme, noduri, ancore",
  "constructia-ambarcatiunii": "Construcția ambarcațiunii",
  "lumini-propulsie-mecanica": "Lumini de navigație",
  "lumini-situatii-speciale": "Lumini — situații speciale",
  "semne-si-forme-ziua": "Semne și forme pe timp de zi",
  "geamanduri-si-balizaj": "Geamanduri și balizaj",
  "semnale-sonore": "Semnale sonore",
  "semnale-de-pericol-si-salvare": "Semnale de pericol și salvare",
  "reguli-de-drum": "Reguli de drum",
  "vizibilitate-redusa": "Vizibilitate redusă",
  "regulament-dunare": "Regulamentul Dunării",
  "navigatie-compas-si-drumuri": "Compas și drumuri",
  "navigatie-harti-si-pozitie": "Hărți și poziție",
  "meteo-si-hidrologie": "Meteorologie și hidrologie",
  "motor-si-propulsie": "Motor și propulsie",
  "manevra-cu-motor": "Manevra cu motor",
  "motovehicule-nautice": "Motovehicule nautice",
  "prim-ajutor": "Prim ajutor",
  "legislatie": "Legislație",
};

const THEME_TOGGLE_LABELS = { auto: "automată", light: "luminoasă", dark: "întunecată" };
const THEME_CYCLE = { auto: "dark", dark: "light", light: "auto" };

// "auto" is the absence of an override: the attribute comes off and the
// media query decides again, exactly as before this button existed.
function applyTheme(state) {
  const choice = state.theme || "auto";
  if (choice === "auto") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = choice;
}

function themeToggle() {
  const current = App.state.theme || "auto";
  return el("button", {
    onclick: () => {
      const next = THEME_CYCLE[current];
      if (next === "auto") delete App.state.theme;
      else App.state.theme = next;
      App.save();
      applyTheme(App.state);
      App.go(App.route);
    },
  }, `Temă: ${THEME_TOGGLE_LABELS[current]}`);
}

function labelOf(theme) {
  return THEME_LABELS[theme] || theme;
}

// A theme may open with one or more reference panels. A table rather than a
// chain of ifs: the second entry is what makes the difference, and a third
// will not need a new branch. Each theme maps to a list of builders, appended
// in order, because "lumini-propulsie-mecanica" carries two: arcs first, since
// they explain the lights the configurations are made of.
const THEME_PANELS = {
  "semnale-sonore": [theoryPanel, signalPanel],
  "geamanduri-si-balizaj": [theoryPanel, figurePanel],
  "semne-si-forme-ziua": [theoryPanel, figurePanel],
  // Arcs before configurations: they explain the lights the configurations
  // are made of. Theory before both, as the parent spec orders the layers.
  "lumini-propulsie-mecanica": [theoryPanel, arcPanel, configPanel],
  "lumini-situatii-speciale": [theoryPanel],
  "parame-noduri-ancore": [theoryPanel],
  "prim-ajutor": [theoryPanel],
  "constructia-ambarcatiunii": [theoryPanel],
  "vocabular-si-principii": [theoryPanel],
  "semnale-de-pericol-si-salvare": [theoryPanel],
  "regulament-dunare": [theoryPanel],
  "legislatie": [theoryPanel],
  "motor-si-propulsie": [theoryPanel],
  "manevra-cu-motor": [theoryPanel],
  "motovehicule-nautice": [theoryPanel],
  "navigatie-compas-si-drumuri": [theoryPanel],
  "reguli-de-drum": [theoryPanel],
  "vizibilitate-redusa": [theoryPanel],
  "meteo-si-hidrologie": [theoryPanel],
  "navigatie-harti-si-pozitie": [theoryPanel],
};

const SAFETY_CONTOUR = 40;

const SCREENS = {
  acasa(root) {
    const mine = forClass(DATA.questions, App.state.examClass);
    const unsafe = blacklist(App.state, DATA.questions, App.state.examClass, App.today()).length;

    root.append(classSwitch());
    root.append(classNote());
    root.append(themeToggle());
    root.append(el("p", { class: "eyebrow" }, "De exersat"));
    root.append(el("p", { class: "figure sounding", "data-danger": unsafe > SAFETY_CONTOUR ? "yes" : "no" },
      String(unsafe)));
    root.append(el("p", { class: "outof" }, `din ${mine.length} pentru clasa ${App.state.examClass}`));
    // The rule was only ever taught by accident, in the one message a candidate
    // sees after answering correctly twice in the same day. Said once, here,
    // under the number it explains.
    root.append(el("p", { class: "rule" },
      "O întrebare trece la știute după două răspunsuri corecte la rând, în două "
      + "zile diferite — un răspuns greșit o ia de la capăt. După 30 de zile fără "
      + "s-o revezi, se întoarce la exersat."));

    const { above, below } = themeSoundings(App.state, mine, SAFETY_CONTOUR, App.today());

    // Each band is drawn only when something is in it; an empty block reads as
    // a missing element rather than as good news.
    //
    // The dashed line is a depth contour and the bands either side of it are
    // shoals and clear water — a metaphor that until now lived only in the CSS
    // class names, leaving the candidate a bare numeral to decode.
    if (above.length) {
      root.append(el("p", { class: "rule" },
        `Temele de deasupra conturului au mai mult de ${SAFETY_CONTOUR} `
        + "de întrebări de exersat."));
      root.append(soundings(above, "shoal"));
    }
    root.append(el("div", { class: "contour" },
      el("span", {}, `contur de siguranță · ${SAFETY_CONTOUR}`)));
    if (below.length) root.append(soundings(below, "clear"));

    const other = App.state.examClass === "C" ? "D" : "C";
    const shared = mine.filter((question) => question.classes.indexOf(other) !== -1);
    const sharedSafe = shared.filter((question) => isSafe(App.state, question.id, App.today())).length;
    root.append(el("p", { class: "overlap" },
      `${shared.length} dintre ele sunt comune cu clasa ${other}` +
      // The noun stays in the phrase: "1 deja știute" was the old bug, and
      // "25 de deja știute" would be the new one without it.
      (sharedSafe
        ? ` — ${countLabel(sharedSafe, "o întrebare deja știută", "întrebări deja știute")}.`
        : ".")));

    // Scoped to the current class like every other figure here. A cross-class
    // list under class-D numbers would read as class-D history.
    const exams = App.state.exams
      .filter((exam) => exam.examClass === App.state.examClass)
      .slice(-3)
      .reverse();
    if (exams.length) {
      root.append(el("h2", {}, "Ultimele simulări"));
      const list = el("div", { class: "themes" });
      for (const exam of exams) {
        list.append(el("div", { class: "theme", "data-clear": exam.passed ? "yes" : "no" },
          el("span", {}, exam.day),
          el("span", { class: "figure" }, `${exam.correct} / ${exam.total}`)));
      }
      root.append(list);
    }

    root.append(el("h2", {}, "Progresul tău"));
    root.append(progressCard());

    root.append(el("p", {},
      el("button", { class: "finish", onclick: () => App.go("diferenta") },
        `Examen de diferență — spre clasa ${App.state.examClass}`)));
    root.append(el("p", { class: "rule" },
      "Examenul de diferență e pentru cine deține deja cealaltă clasă: cu clasa D "
      + "dai COLREG ca să obții C, cu clasa C dai RND — Regulamentul de navigație "
      + "pe Dunăre — ca să obții D."));
  },

  teme(root) {
    const mine = forClass(DATA.questions, App.state.examClass);
    const themes = [...new Set(mine.map((question) => question.theme))].sort(
      (a, b) => labelOf(a).localeCompare(labelOf(b), "ro")
    );
    root.append(el("p", { class: "eyebrow" }, "Teme"));
    root.append(el("h1", {}, "Ce înveți acum"));
    // The counts come from logic.js rather than being re-derived here; the
    // definition of "unsafe" belongs in one place.
    const unsafeCounts = unsafeByTheme(App.state, mine, App.today());
    const list = el("div", { class: "themes" });
    for (const theme of themes) {
      const questions = forTheme(DATA.questions, App.state.examClass, theme);
      const unsafe = unsafeCounts[theme] || 0;
      const row = el("button",
        { class: "theme", "data-clear": unsafe === 0 ? "yes" : "no",
          onclick: () => App.go(`tema:${theme}`) },
        el("span", {}, labelOf(theme)),
        el("span", { class: "figure" }, `${unsafe} / ${questions.length}`));
      list.append(row);
    }
    root.append(list);
  },

  tema(root, theme) {
    // The drill owns its own container: startDrill replaces the children of
    // whatever it is given on every question, which would wipe the panels.
    // A panel may decline: the arcs are asked only at class C, so for class D
    // the theme opens straight into its own questions rather than with a
    // reference to material that class is never examined on.
    for (const build of THEME_PANELS[theme] || []) {
      const panel = build(theme);
      if (panel) root.append(panel);
    }
    const stage = el("div", {});
    root.append(stage);
    startDrill(stage, forTheme(DATA.questions, App.state.examClass, theme), labelOf(theme));
  },

  "lista-neagra"(root) {
    const all = blacklist(App.state, DATA.questions, App.state.examClass, App.today());
    if (all.length === 0) {
      root.append(el("p", { class: "eyebrow" }, "De exersat"));
      root.append(el("h1", {}, "Nimic de exersat"));
      root.append(el("p", {}, "Toate întrebările clasei sunt știute."));
      return;
    }

    // A view over the practice list, in the shape the Romanian car-theory apps
    // use — everything, or only what went wrong lately. The window narrows what
    // is shown and never adds a question the list does not already hold.
    // The day counts go through countLabel like every other number in the app.
    // Written by hand, the first draft of the empty message read "ultimele 7 de
    // zile" — the exact mistake the helper exists to prevent.
    const windows = [
      { days: null, label: "Toate" },
      { days: 7, label: `Greșite în ${countLabel(7, "o zi", "zile")}` },
      { days: 30, label: `Greșite în ${countLabel(30, "o zi", "zile")}` },
    ];
    const chosen = windows.find((w) => w.days === App.wrongWindow) || windows[0];
    const shown = chosen.days === null
      ? all
      : wrongSince(App.state, all, chosen.days, App.today());

    const bar = el("div", { class: "windowbar" });
    for (const view of windows) {
      const button = el("button",
        { onclick: () => { App.wrongWindow = view.days; App.go(App.route); } },
        view.label);
      if (view.days === chosen.days) button.setAttribute("aria-current", "true");
      bar.append(button);
    }
    root.append(bar);

    if (shown.length === 0) {
      root.append(el("p", {},
        `Nimic greșit în ultimele ${countLabel(chosen.days, "o zi", "zile")}.`));
      return;
    }
    // The drill gets its own container, exactly as the theme screen does:
    // startDrill replaces the children of whatever it is handed, on every
    // question, and would wipe the bar above after the first answer.
    const stage = el("div", {});
    root.append(stage);
    startDrill(stage, shown, "De exersat");
  },

  examen(root) {
    startExam(root, drawExam(DATA.questions, App.state.examClass, RULES, Math.random),
              RULES.minutes, RULES.pass, "Simulare de examen");
  },

  diferenta(root) {
    startExam(root, drawDifference(DATA.questions, App.state.examClass, RULES, Math.random),
              RULES.difference.minutes, RULES.difference.pass,
              `Examen de diferență — spre clasa ${App.state.examClass}`);
  },
};

function soundings(entries, band) {
  const wrap = el("div", { class: "soundings", "data-band": band });
  for (const [theme, count] of entries) {
    wrap.append(el("button", { class: "sounding-dot", onclick: () => App.go(`tema:${theme}`) },
      el("span", { class: "figure" }, String(count)),
      el("span", { class: "sounding-label" }, labelOf(theme))));
  }
  return wrap;
}

// The fourth panel, and the third time this defect has shipped. The two
// classes are examined on disjoint sets of signals — eight at class C, two at
// class D, none shared — so an unfiltered panel gave every candidate eight
// recordings that are not theirs, with their own two buried among them.
// arcPanel shipped with this same gap at stage 3c and figurePanel at 4c; the
// regression test existed both times and never covered signals, because there
// was no function to name in it.
function signalsForClass(examClass) {
  const wanted = new Set(
    forClass(DATA.questions, examClass).map((question) => question.signal).filter(Boolean)
  );
  return SIGNALS.signals.filter((signal) => wanted.has(signal.id));
}

function signalPanel() {
  const shown = signalsForClass(App.state.examClass);
  if (shown.length === 0) return null;

  const wrap = el("details", { class: "mediapanel signalpanel" },
    el("summary", {}, `Ascultă semnalele · ${countLabel(shown.length, "un semnal", "semnale")}`));
  for (const signal of shown) {
    wrap.append(el("div", { class: "signal" }, playButton(signal), patternStrip(signal)));
  }
  wrap.append(el("p", { class: "note" },
    "Pauza dintre sunete, ca și sunetul fluierului și al clopotului, sunt alese "
    + "ca tiparul să se distingă. Regulamentul dă doar duratele."));
  return wrap;
}

// Choosing a class is the first thing the candidate does, and until now the two
// buttons said nothing about what they mean. The wording follows the order that
// defines the certificates and adds nothing to it — no lengths, no engine
// powers, no ages, none of which the source states here.
function classNote() {
  return el("p", { class: "rule" },
    "Clasa C — ambarcațiuni de agrement în zonele maritime, până la 6 Mm de țărm. "
    + "Clasa D — pe căi navigabile interioare; cu clasa D nu ai voie în apele "
    + "maritime interioare.");
}

function classSwitch() {
  const wrap = el("div", { class: "classswitch" });
  for (const examClass of ["C", "D"]) {
    const button = el("button", { onclick: () => App.setClass(examClass) }, `Clasa ${examClass}`);
    if (App.state.examClass === examClass) button.setAttribute("aria-current", "true");
    wrap.append(button);
  }
  return wrap;
}

// The candidate's progress lives in this browser's storage and nowhere else.
// Export writes it to a file; import replaces it wholesale — merging two
// diverged histories would fabricate one nobody lived. Import is also the
// only migration path a future version bump has.
function progressCard() {
  const status = el("p", { class: "note", role: "status" });

  function exportProgress() {
    const blob = new Blob([JSON.stringify(App.state)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = el("a", { href: url, download: `permis-progres-${App.today()}.json` });
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    status.textContent = "Progresul a fost salvat în fișier.";
  }

  const picker = el("input", { type: "file", accept: ".json,application/json", hidden: true });
  let pending = null;

  picker.addEventListener("change", () => {
    const file = picker.files[0];
    picker.value = "";
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      let parsed = null;
      try {
        parsed = JSON.parse(reader.result);
      } catch (error) {
        // Fall through: adoptProgress(null) is null.
      }
      const adopted = adoptProgress(parsed);
      if (!adopted) {
        status.textContent = "Fișierul nu e un progres salvat de aplicația asta.";
        return;
      }
      pending = adopted;
      showConfirmation();
    };
    // A file that vanishes between picking and reading is rare, but a silent
    // screen is the one answer the interface never gives.
    reader.onerror = () => {
      status.textContent = "Fișierul nu a putut fi citit.";
    };
    reader.readAsText(file);
  });

  // The confirmation is the second step of the same gesture, in the page: a
  // modal would block, and a single-click replace would be a mis-tap away
  // from erasing weeks of study.
  function showConfirmation() {
    status.replaceChildren(
      "Înlocuiește tot progresul de aici cu cel din fișier? ",
      el("button", { class: "finish", onclick: confirmImport }, "Da, înlocuiește"),
      " ",
      el("button", { onclick: () => { pending = null; status.textContent = ""; } }, "Renunță"),
    );
  }

  function confirmImport() {
    App.state = pending;
    pending = null;
    App.save();
    applyTheme(App.state);
    App.go("acasa");
  }

  return el("div", { class: "progresscard" },
    el("button", { onclick: exportProgress }, "Salvează progresul"),
    el("button", { onclick: () => picker.click() }, "Încarcă progresul…"),
    picker,
    status);
}

function startDrill(root, questions, title) {
  // A theme with nothing for this class must say so, not throw. Unreachable
  // from the theme list, which filters — but a hand-typed route or a future
  // edition of the bank reaches it directly.
  if (questions.length === 0) {
    root.append(el("p", { class: "eyebrow" }, title));
    root.append(el("h1", {}, "Nicio întrebare pentru clasa ta la tema asta."));
    return;
  }

  let order = drillOrder(App.state, questions, Math.random, App.today());
  let index = 0;
  let answered = false;

  function draw() {
    root.replaceChildren();
    const question = order[index];
    root.append(el("p", { class: "eyebrow" }, `${title} · ${index + 1} / ${order.length}`));
    root.append(el("h1", {}, question.q));
    if (question.disputed) {
      root.append(el("p", { class: "note" },
        "Cele două liste oficiale dau răspunsuri diferite aici. Se afișează varianta din lista clasei tale."));
    }
    const buttons = [];
    question.opts.forEach((text, position) => {
      const button = el("button", { class: "option", onclick: () => answer(position) },
        el("span", { class: "key" }, String(position + 1)), el("span", {}, text));
      buttons.push(button);
      root.append(button);
    });
    const status = el("p", { class: "status" });
    root.append(status);

    function answer(chosen) {
      if (answered) return;
      answered = true;
      const correct = chosen === question.correct;
      recordAnswer(App.state, question.id, correct, App.today());
      App.save();
      buttons.forEach((button, position) => {
        button.setAttribute("disabled", "disabled");
        if (position === question.correct) button.dataset.verdict = "correct";
        else if (position === chosen) button.dataset.verdict = "wrong";
      });
      status.textContent = statusLine(question.id, correct);
      status.append(" ", el("button", { class: "next", onclick: next }, "Următoarea"));
      const signal = SIGNAL_BY_ID[question.signal];
      if (signal) status.append(" ", playButton(signal, "Ascultă"));
      const figure = FIGURE_BY_ID[question.figure];
      if (figure) status.append(" ", drawFigure(figure, 64));
      const arc = ARC_BY_ID[question.arc];
      if (arc) {
        status.append(" ", drawArc(arc, 72));
        // A caveat belongs to one quote, so it is shown only where that quote
        // is what the candidate is reading. The masthead question whose stem
        // lost a digit would otherwise look as though the drawing were wrong.
        const caveat = arc.caveats[question.q] || arc.caveats[question.opts[question.correct]];
        if (caveat) status.append(el("p", { class: "note" }, caveat));
      }
      const config = CONFIG_BY_ID[question.config];
      if (config) {
        status.append(" ", drawConfig(config, 132));
        if (config.note) status.append(el("p", { class: "note" }, config.note));
      }
    }

    function next() {
      answered = false;
      index += 1;
      if (index >= order.length) {
        // A lap is over, so re-sort. Answers given during the lap moved
        // questions between safe and unsafe; without this the order would keep
        // reflecting how things stood when the screen opened, and a question
        // demoted by a wrong answer would sit behind the ones already known.
        order = drillOrder(App.state, questions, Math.random, App.today());
        index = 0;
      }
      draw();
    }

    document.onkeydown = (event) => {
      if (!answered && ["1", "2", "3"].includes(event.key)) answer(Number(event.key) - 1);
      else if (answered && !onControl(event) && (event.key === "Enter" || event.key === " ")) {
        event.preventDefault();
        next();
      }
    };
  }

  // Each line says something true at the moment it is shown, and says what is
  // still missing rather than only whether the answer was right.
  function statusLine(id, correct) {
    if (!correct) return "Greșit. Rămâne la exersat.";
    if (isSafe(App.state, id, App.today())) return "Corect. Întrebarea e știută.";
    const record = App.state.q[id];
    if (record.streak >= 2) {
      return "Corect, dar tot azi. Îți mai trebuie un răspuns corect într-o altă zi.";
    }
    return "Corect. Îți mai trebuie un răspuns corect, într-o altă zi.";
  }

  draw();
}

function startExam(root, drawn, minutes, passMark, title) {
  const answers = {};
  let index = 0;
  let deadline = Date.now() + minutes * 60 * 1000;
  let ticking = null;
  let done = false;

  // Walking out of a sitting is a mis-tap on a phone, not a decision worth
  // grading. The answers already given are evidence like any other and count
  // toward retention — without this, a candidate who answers five questions
  // wrong and then taps "Acasă" keeps all five marked safe, and the dashboard
  // goes on contradicting section 7.1. The sitting itself is deliberately not
  // filed: a "5 din 26" in the history would describe an exam nobody sat.
  releaseScreen = () => {
    clearInterval(ticking);
    if (done) return;
    recordSitting(App.state, drawn, answers, App.today());
    App.save();
  };

  function remaining() {
    return Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
  }

  function drawQuestion() {
    root.replaceChildren();
    const question = drawn[index];
    const header = el("p", { class: "eyebrow" }, `${title} · ${index + 1} / ${drawn.length}`);
    const clock = el("span", { class: "figure clock" }, "");
    header.append(" · ", clock);
    root.append(header);
    root.append(el("h1", {}, question.q));

    question.opts.forEach((text, position) => {
      const button = el("button",
        { class: "option", "aria-pressed": answers[question.id] === position ? "true" : "false",
          onclick: () => { answers[question.id] = position; advance(); } },
        el("span", { class: "key" }, String(position + 1)), el("span", {}, text));
      if (answers[question.id] === position) button.dataset.chosen = "yes";
      root.append(button);
    });

    const bar = el("div", { class: "examnav" },
      el("button", { class: "next", onclick: () => { index = (index - 1 + drawn.length) % drawn.length; drawQuestion(); } }, "Înapoi"),
      el("button", { class: "next", onclick: advance }, "Mai departe"),
      el("button", { class: "finish", onclick: finish }, "Termin acum"));
    root.append(bar);

    document.onkeydown = (event) => {
      if (["1", "2", "3"].includes(event.key)) { answers[question.id] = Number(event.key) - 1; advance(); }
      else if (event.key === "Enter" && !onControl(event)) advance();
    };

    function tick() {
      const left = remaining();
      clock.textContent = `${String(Math.floor(left / 60)).padStart(2, "0")}:${String(left % 60).padStart(2, "0")}`;
      if (left === 0) finish();
    }
    tick();
    clearInterval(ticking);
    ticking = setInterval(tick, 250);
  }

  function advance() {
    if (index === drawn.length - 1) finish();
    else { index += 1; drawQuestion(); }
  }

  // Reachable from three places — the last question, "Termin acum", and the
  // timer. Grading twice would file the same sitting twice.
  function finish() {
    if (done) return;
    done = true;
    clearInterval(ticking);
    releaseScreen = null;
    document.onkeydown = null;
    const result = grade(drawn, answers, passMark);
    recordSitting(App.state, drawn, answers, App.today());
    App.state.exams.push({
      day: App.today(), examClass: App.state.examClass,
      correct: result.correct, total: result.total, passed: result.passed,
    });
    App.save();
    report(result);
  }

  function report(result) {
    root.replaceChildren();
    root.append(el("p", { class: "eyebrow" }, title));
    root.append(el("h1", { class: "verdict", "data-passed": result.passed ? "yes" : "no" },
      `${result.correct} din ${result.total}`));
    root.append(el("p", {}, result.passed
      ? `Promovat. Baremul e ${passMark}.`
      : "Nepromovat. Îți trebuiau "
        + `${countLabel(passMark, "un răspuns corect", "răspunsuri corecte")}.`));

    if (result.wrong.length) {
      root.append(el("h2", {}, "Ce ai greșit"));
      const list = el("div", { class: "themes" });
      for (const id of result.wrong) {
        const question = drawn.find((item) => item.id === id);
        list.append(el("button",
          { class: "theme", onclick: () => App.go(`tema:${question.theme}`) },
          el("span", {}, question.q),
          el("span", { class: "correct-answer" }, `Corect: ${question.opts[question.correct]}`),
          el("span", { class: "figure" }, labelOf(question.theme))));
      }
      root.append(list);
    }
    root.append(el("p", {}, el("button", { class: "next", onclick: () => App.go("acasa") }, "Înapoi acasă")));
  }

  drawQuestion();
}

// Keys starting with "on" become listeners; everything else is an attribute.
// No current attribute name begins with "on", so the shortcut is unambiguous.
// A key press that landed on a control belongs to that control, not to the
// screen's own shortcut. Without this the shortcut wins twice over: Enter on
// the drill's "Ascultă" button skipped the question instead of playing the
// signal — silently, so a keyboard candidate could never hear a signal at all
// — and Enter on "Termin acum" advanced the exam instead of ending it.
function onControl(event) {
  return event.target instanceof HTMLElement
    && event.target.closest("button, a, input, select, textarea") !== null;
}

function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attrs || {})) {
    if (name.startsWith("on")) node.addEventListener(name.slice(2), value);
    // An absent attribute and one set to "false" are the same to HTML: present
    // means true. `disabled: false` must therefore not set anything at all.
    else if (value !== false && value !== null && value !== undefined) {
      node.setAttribute(name, value);
    }
  }
  node.append(...children.filter((child) => child !== null && child !== undefined));
  return node;
}

// A sub-route belongs under the nav item it was reached from: a theme drill
// sits under Teme, the difference exam under Simulare. Without this, both leave
// the whole bar unmarked and the reader loses their place.
const NAV_PARENT = { tema: "teme", diferenta: "examen" };

function navItemFor(route) {
  const name = route.split(":")[0];
  return NAV_PARENT[name] || name;
}

function renderNav() {
  document.querySelector("nav.bar")?.remove();
  const nav = el("nav", { class: "bar" });
  const items = [["acasa", "Acasă"], ["teme", "Teme"], ["lista-neagra", "De exersat"], ["examen", "Simulare"]];
  const current = navItemFor(App.route);
  for (const [route, label] of items) {
    const button = el("button", { onclick: () => App.go(route) }, label);
    if (current === route) button.setAttribute("aria-current", "page");
    nav.append(button);
  }
  document.body.append(nav);
}

// Shown once, in place, rather than as an alert — a modal would block the very
// interaction the candidate is in the middle of.
function showStorageWarning() {
  if (document.getElementById("storage-warning")) return;
  document.body.prepend(el("p", { id: "storage-warning", class: "warning", role: "status" },
    "Progresul nu poate fi salvat în acest browser. Poți continua, dar nu se reține nimic."));
}

App.state = App.load();
applyTheme(App.state);
App.go("acasa");
