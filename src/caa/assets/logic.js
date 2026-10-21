"use strict";

// Pure logic: no DOM, no storage, no clock of its own. Everything that varies
// — today's date, randomness — is passed in, so the same input always gives
// the same output and `node --test` can drive it directly.

const PROGRESS_VERSION = 1;

function createProgress(examClass) {
  return { version: PROGRESS_VERSION, examClass: examClass, q: {}, exams: [] };
}

// Whole days from `a` to `b`, negative when `b` is earlier. ISO date strings
// parse as UTC midnight, so the division is exact — no DST to stumble on.
function daysBetween(a, b) {
  return (Date.parse(b) - Date.parse(a)) / 86400000;
}

// Romanian counts in three shapes, not two: o regulă, cinci reguli, douăzeci
// *de* reguli. The threshold is not simply twenty — it reads the last two
// digits, so 101 reguli takes no "de" while 121 de reguli does. The singular is
// passed whole rather than built, because the article carries gender: "o
// regulă" but "un marcaj".
function countLabel(n, singular, plural) {
  if (n === 1) return singular;
  const rest = n % 100;
  const needsDe = n >= 20 && !(rest >= 1 && rest <= 19);
  return needsDe ? `${n} de ${plural}` : `${n} ${plural}`;
}

// Safety has a shelf life. The exam is sat weeks after the studying, and a
// question confirmed in July says nothing about September; past this many
// days it returns to the unsafe pool and costs one correct answer to renew —
// the streak is already there, so renewal is cheaper than first learning.
const SAFETY_SHELF_DAYS = 30;

// A question counts as safe only after two correct answers in a row, on two
// different days. Answering correctly twice in one sitting proves recall, not
// retention, and the exam is sat weeks after the studying.
function recordAnswer(state, id, correct, today) {
  const record = state.q[id]
    || { seen: 0, correct: 0, streak: 0, streakStart: null, lastDay: null, lastWrongDay: null };
  record.seen += 1;
  if (correct) {
    record.correct += 1;
    if (record.streak === 0) record.streakStart = today;
    record.streak += 1;
  } else {
    record.streak = 0;
    record.streakStart = null;
    record.lastWrongDay = today;
  }
  record.lastDay = today;
  state.q[id] = record;
  return state;
}

// Safe means: at least two correct answers in a row, the streak has outlived
// the day it started on, and the knowledge is not stale. Dates are ISO strings,
// so ">" compares them chronologically.
//
// ">" and not "!==" on purpose. If a device clock ever runs backwards between
// sessions, "!==" would read two out-of-order dates as two different days and
// mark the question safe; ">" leaves it unsafe. Both are wrong about the clock,
// but only one is wrong in the direction that costs marks in the exam hall.
//
// Age must sit in [0, shelf]: a clock running backwards makes the age negative,
// and that reads as expired rather than as eternally fresh — the same direction
// the ">" above already chose.
function isSafe(state, id, today) {
  const record = state.q[id];
  if (!record) return false;
  if (!(record.streak >= 2 && record.streakStart !== null && record.lastDay > record.streakStart)) {
    return false;
  }
  const age = daysBetween(record.lastDay, today);
  return age >= 0 && age <= SAFETY_SHELF_DAYS;
}

// These two take whatever list they are given and do not know about exam
// classes. Callers filter first — the dashboard would miscount otherwise.
function unsafeIds(state, questions, today) {
  return questions.filter((question) => !isSafe(state, question.id, today)).map((question) => question.id);
}

function unsafeByTheme(state, questions, today) {
  const counts = {};
  for (const question of questions) {
    if (isSafe(state, question.id, today)) continue;
    counts[question.theme] = (counts[question.theme] || 0) + 1;
  }
  return counts;
}

// Of the questions given, those whose last wrong answer is no older than
// `days`. A later correct answer does not clear the date: the question is
// "what did I get wrong lately", and one right answer must not hide a mistake
// from the view that exists to find it. A record saved before this field
// existed carries no date and simply does not appear — the window is a filter
// over the practice list, never a second opinion about what must be practised.
function wrongSince(state, questions, days, today) {
  return questions.filter((question) => {
    const record = state.q[question.id];
    if (!record || !record.lastWrongDay) return false;
    const age = daysBetween(record.lastWrongDay, today);
    return age >= 0 && age <= days;
  });
}

// Splits the themes against the safety contour, for the chart the dashboard
// draws. Every theme is listed, including ones with nothing unsafe left: a
// theme that vanishes gives the candidate no credit for having learned it, and
// in the limit the whole chart would empty out with nothing to show for it.
//
// The contour is inclusive — exactly `contour` unsafe questions is still clear
// water, matching section 3 of the spec, which puts the pass probability above
// 99% at 40.
function themeSoundings(state, questions, contour, today) {
  const counts = unsafeByTheme(state, questions, today);
  const rows = [...new Set(questions.map((question) => question.theme))]
    .map((theme) => [theme, counts[theme] || 0])
    .sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
  return {
    above: rows.filter(([, count]) => count > contour),
    below: rows.filter(([, count]) => count <= contour),
  };
}

function forClass(questions, examClass) {
  return questions.filter((question) => question.classes.indexOf(examClass) !== -1);
}

function forTheme(questions, examClass, theme) {
  return forClass(questions, examClass).filter((question) => question.theme === theme);
}

function blacklist(state, questions, examClass, today) {
  return forClass(questions, examClass).filter((question) => !isSafe(state, question.id, today));
}

// Unsafe questions first: the candidate's time is worth more where the
// knowledge is missing. The split is a decision, not presentation, so it lives
// here where a test can drive it — the caller passes the state and the source
// of randomness rather than the module reaching for either.
function drillOrder(state, questions, random, today) {
  const unsafe = questions.filter((question) => !isSafe(state, question.id, today));
  const safe = questions.filter((question) => isSafe(state, question.id, today));
  return shuffled(unsafe, random).concat(shuffled(safe, random));
}

// Fisher-Yates with an injected source, so a test can pin the order.
function shuffled(items, random) {
  const copy = items.slice();
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1));
    const swap = copy[i];
    copy[i] = copy[j];
    copy[j] = swap;
  }
  return copy;
}

// Import is the migration path. Every version upgrade this application ever
// needs lives here, one block per version — nowhere else touches a foreign
// state. Returns null rather than throwing: the caller shows what went wrong
// and leaves the current state alone.
function adoptProgress(raw) {
  if (typeof raw !== "object" || raw === null) return null;
  if (typeof raw.version !== "number" || raw.version < 1 || raw.version > PROGRESS_VERSION) {
    return null;
  }
  if (raw.examClass !== "C" && raw.examClass !== "D") return null;
  if (typeof raw.q !== "object" || raw.q === null || Array.isArray(raw.q)) return null;
  if (!Array.isArray(raw.exams)) return null;
  // The shapes inside matter as much as the shapes outside. A hand-edited
  // file with a null exam entry passes every check above, survives the
  // confirmation, persists — and then every reload crashes before the
  // navigation exists, leaving a blank app only DevTools can recover. The
  // app's own export can never produce such a file; this guards the one that
  // did not come from the app.
  const shaped = (value) => typeof value === "object" && value !== null && !Array.isArray(value);
  if (!raw.exams.every(shaped)) return null;
  if (!Object.values(raw.q).every(shaped)) return null;

  const adopted = {
    version: PROGRESS_VERSION,
    examClass: raw.examClass,
    q: raw.q,
    exams: raw.exams,
  };
  // Optional, and only the values that mean something; anything else reads
  // as "auto" by being absent.
  if (raw.theme === "light" || raw.theme === "dark") adopted.theme = raw.theme;
  return adopted;
}

function _pool(questions, examClass, wanted) {
  return forClass(questions, examClass).filter((question) => {
    const mine = (question.disciplines && question.disciplines[examClass]) || [];
    return wanted.some((name) => mine.indexOf(name) !== -1);
  });
}

// A question can sit in two of these groups within one class — the authority
// lists "Adâncimea apei se măsoară cu" under both Marinărie and Navigație for
// class C. `used` makes sure it is drawn once; the consequence is that a drawn
// exam cannot be broken down per discipline after the fact without
// double-counting that one item. The draw itself is exact.
function _take(questions, examClass, groups, random) {
  const chosen = [];
  const used = Object.create(null);
  for (const [wanted, count] of groups) {
    const pool = _pool(questions, examClass, wanted).filter((q) => !used[q.id]);
    const take = shuffled(pool, random).slice(0, count);
    // A short pool would otherwise ship a 25-question "official" exam in
    // silence. Today every group has more than ten times what it needs; this
    // makes a future bank edit fail loudly instead of quietly.
    if (take.length !== count) {
      throw new Error(
        `pool prea mic pentru ${wanted.join("+")} la clasa ${examClass}: ` +
        `${take.length} din ${count}`
      );
    }
    for (const question of take) {
      used[question.id] = true;
      chosen.push(question);
    }
  }
  return shuffled(chosen, random);
}

function drawExam(questions, examClass, rules, random) {
  return _take(questions, examClass, rules.draw[examClass], random);
}

function drawDifference(questions, examClass, rules, random) {
  const disciplines = rules.difference.disciplines[examClass];
  return _take(questions, examClass, [[disciplines, rules.difference.questions]], random);
}

// A sitting is evidence like any other, so section 7.1 applies to it whole:
// "orice răspuns greşit readuce întrebarea în lista nesigure, indiferent de
// istoric". Without this the dashboard would keep calling a question safe
// straight after the candidate got it wrong under exam conditions — the most
// exam-like evidence the application ever collects, thrown away.
//
// Only questions the candidate actually answered are recorded. `grade` counts
// an unanswered question as wrong because the methodology does, but silence is
// not the same evidence as a wrong answer: a sitting abandoned at question 6
// would otherwise demote twenty questions nobody ever read.
function recordSitting(state, drawn, answers, today) {
  for (const question of drawn) {
    const chosen = answers[question.id];
    if (chosen === undefined) continue;
    recordAnswer(state, question.id, chosen === question.correct, today);
  }
  return state;
}

// Methodology article 10: a question left unanswered is treated as wrong, so
// the sensible strategy is to answer everything. The grader mirrors that.
function grade(drawn, answers, passMark) {
  const wrong = drawn.filter((question) => answers[question.id] !== question.correct);
  return {
    correct: drawn.length - wrong.length,
    total: drawn.length,
    passed: drawn.length - wrong.length >= passMark,
    wrong: wrong.map((question) => question.id),
  };
}

// A signal is a list of sounds; the gaps between them are derived, never
// stored. The interval belongs after a sound, not around it, so a one-sound
// signal has no trailing silence to sit through.
//
// The very short series carries its own interval because the bank states it
// ("circa ¼ s"). Every other gap is the default, which is a presentation
// choice and not a fact from the regulation.
function signalTimeline(signal, timing) {
  const steps = [];
  signal.pattern.forEach((kind, index) => {
    const ms = timing.durations[kind];
    if (ms === undefined) throw new Error(`durată necunoscută pentru "${kind}"`);
    steps.push({ kind: kind, ms: ms });
    if (index < signal.pattern.length - 1) {
      const gap = timing.gaps[kind];
      steps.push({ kind: null, ms: gap === undefined ? timing.defaultGap : gap });
    }
  });
  return steps;
}

function signalDuration(timeline) {
  return timeline.reduce((total, step) => total + step.ms, 0);
}

// The bank gives a cardinal's stripes "de sus în jos", and which way round
// they go is the whole difficulty — East and West are the same three colours
// in opposite order. So the order is computed here, where a test can drive it,
// and the renderer only draws what it is handed.
//
// Heights are fractions of the body, not pixels: the same figure is drawn at
// one size in the panel and another beside a question.
function figureBands(figure) {
  const bands = figure.body.bands;
  if (!bands || bands.length === 0) throw new Error("figura fără bands");
  const height = 1 / bands.length;
  return bands.map((colour, index) => ({ colour: colour, top: index * height, height: height }));
}

// Bearings run from the bow, clockwise, 0 to 360. The opening therefore has
// to wrap: the masthead light spans 247.5 to 112.5 straight through the bow.
// A sector that ends where it starts is the whole circle, not nothing.
function sectorSpan(sector) {
  const span = ((sector.end - sector.start) % 360 + 360) % 360;
  return span === 0 ? 360 : span;
}

// The bow points up, so bearing 0 is straight up the screen and 90 is to the
// right. That orientation is a presentation choice; the regulation says
// nothing about which way a picture faces.
// Public because the compass rose needs the same convention: two drawings
// disagreeing about which way 090 points would be worse than either being
// wrong on its own.
function bearingPoint(bearing, radius, cx, cy) {
  const radians = (bearing * Math.PI) / 180;
  return [
    (cx + radius * Math.sin(radians)).toFixed(2),
    (cy - radius * Math.cos(radians)).toFixed(2),
  ];
}

function sectorPath(sector, radius, cx, cy) {
  const span = sectorSpan(sector);

  // A full circle has no two distinct ends, so a single arc from a point back
  // to itself draws nothing. Two half turns do — and a full circle has no
  // radius to draw, unlike a slice.
  if (span === 360) {
    const [x0, y0] = bearingPoint(0, radius, cx, cy);
    const [x1, y1] = bearingPoint(180, radius, cx, cy);
    return `M ${x0} ${y0} A ${radius} ${radius} 0 1 1 ${x1} ${y1} `
         + `A ${radius} ${radius} 0 1 1 ${x0} ${y0} Z`;
  }

  const [x1, y1] = bearingPoint(sector.start, radius, cx, cy);
  const [x2, y2] = bearingPoint(sector.end, radius, cx, cy);
  // Over a half turn the browser must be told to take the long way round.
  // Left at 0, it draws the complement instead: a 225° sector comes out 135°,
  // which happens to be another light's arc and another question's answer.
  const largeArc = span > 180 ? 1 : 0;
  return `M ${cx} ${cy} L ${x1} ${y1} `
       + `A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;
}

// The vessel is drawn in profile with the bow to the right, so a larger x is
// further forward. Only two things here are regulation: the vertical order
// within a station, and the positions the bank names. Everything else is
// presentation, declared as such in the panel.
//
// The order of the stations along the hull is load bearing in one place. The
// trawler's masthead light must sit "la o înălţime mai mare decât lumina
// verde şi înapoia acesteia" — higher than the green and abaft it — and the
// green is at the amidships staff, since its source gives it no position. So
// the mast is aft of ANY, and its lowest light is above ANY's highest.
const DECK_Y = 58;
const STATION_X = { stern: 26, mast: 46, any: 62, side: 82, bow: 100 };
const STATION_BASE_Y = { stern: 50, mast: 20, any: 44, side: 50, bow: 50 };
const LEVEL_STEP = 11;

function lightPlacement(config) {
  return config.lights.map((light) => {
    // `in` walks the prototype chain, so "toString" would pass and the
    // lantern would come out at x = a function, y = NaN, without a word.
    if (!Object.prototype.hasOwnProperty.call(STATION_X, light.station)) {
      throw new Error(`stație necunoscută: ${light.station}`);
    }
    return {
      colours: light.colours,
      station: light.station,
      level: light.level || 0,
      x: STATION_X[light.station],
      y: STATION_BASE_Y[light.station] - LEVEL_STEP * (light.level || 0),
    };
  });
}

if (typeof module !== "undefined") {
  module.exports = {
    PROGRESS_VERSION, createProgress, recordAnswer, isSafe, unsafeIds, unsafeByTheme, themeSoundings,
    forClass, forTheme, blacklist, drillOrder, shuffled, drawExam, drawDifference,
    recordSitting, grade, signalTimeline, signalDuration, figureBands, sectorSpan, sectorPath, bearingPoint,
    lightPlacement, STATION_X, STATION_BASE_Y, LEVEL_STEP, DECK_Y,
    daysBetween, SAFETY_SHELF_DAYS, adoptProgress, countLabel, wrongSince,
  };
}
