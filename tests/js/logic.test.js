"use strict";

const test = require("node:test");
const assert = require("node:assert");
const {
  createProgress, recordAnswer, isSafe, unsafeIds, unsafeByTheme, daysBetween, SAFETY_SHELF_DAYS, adoptProgress,
  countLabel, wrongSince,
} = require("../../src/caa/assets/logic.js");

test("a wrong answer records the day it happened", () => {
  const state = createProgress("C");
  recordAnswer(state, "a", false, "2026-07-01");
  assert.equal(state.q.a.lastWrongDay, "2026-07-01");
});

test("a correct answer leaves the last wrong day where it was", () => {
  // The field answers "what did I get wrong lately", so a later correct answer
  // must not erase the mistake — otherwise one right answer hides it from the
  // view that exists to find it.
  const state = createProgress("C");
  recordAnswer(state, "a", false, "2026-07-01");
  recordAnswer(state, "a", true, "2026-07-05");
  assert.equal(state.q.a.lastWrongDay, "2026-07-01");
});

test("wrongSince keeps only mistakes inside the window", () => {
  const state = createProgress("C");
  recordAnswer(state, "a", false, "2026-07-20");
  recordAnswer(state, "b", false, "2026-07-01");
  const ids = wrongSince(state, QUESTIONS, 7, "2026-07-22").map((q) => q.id);
  assert.deepEqual(ids, ["a"]);
});

test("wrongSince ignores a question never answered wrong", () => {
  const state = createProgress("C");
  recordAnswer(state, "a", true, "2026-07-20");
  assert.deepEqual(wrongSince(state, QUESTIONS, 30, "2026-07-22"), []);
});

test("a progress file saved before the field existed stays valid", () => {
  // Old exports carry records with no lastWrongDay. They must import cleanly
  // and simply not appear in the recent view — not crash it, and not read as a
  // mistake made today.
  const old = {
    version: 1, examClass: "C", exams: [],
    q: { a: { seen: 1, correct: 0, streak: 0, streakStart: null, lastDay: "2026-07-01" } },
  };
  const adopted = adoptProgress(old);
  assert.notEqual(adopted, null);
  assert.deepEqual(wrongSince(adopted, QUESTIONS, 30, "2026-07-02"), []);
});

test("countLabel gives the singular phrase whole, so gender survives", () => {
  assert.equal(countLabel(1, "o regulă", "reguli"), "o regulă");
  assert.equal(countLabel(1, "un marcaj", "marcaje"), "un marcaj");
});

test("countLabel counts plainly from two to nineteen", () => {
  assert.equal(countLabel(2, "o regulă", "reguli"), "2 reguli");
  assert.equal(countLabel(19, "un arc", "arcuri"), "19 arcuri");
  assert.equal(countLabel(0, "o regulă", "reguli"), "0 reguli");
});

test("countLabel takes 'de' from twenty up, as Romanian requires", () => {
  // "20 marcaje" is wrong; "20 de marcaje" is right. No panel reaches twenty
  // today — ten configurations at class C is the most — but the bank can grow,
  // and the rule costs nothing to write correctly now.
  assert.equal(countLabel(20, "un marcaj", "marcaje"), "20 de marcaje");
  assert.equal(countLabel(100, "o regulă", "reguli"), "100 de reguli");
  assert.equal(countLabel(137, "o regulă", "reguli"), "137 de reguli");
});

test("countLabel drops 'de' again where the last two digits are 1 to 19", () => {
  // The rule is not "twenty and above". 101 takes no "de", 121 does.
  assert.equal(countLabel(101, "o regulă", "reguli"), "101 reguli");
  assert.equal(countLabel(119, "o regulă", "reguli"), "119 reguli");
  assert.equal(countLabel(121, "o regulă", "reguli"), "121 de reguli");
});

const QUESTIONS = [
  { id: "a", theme: "marinarie", classes: ["C"] },
  { id: "b", theme: "marinarie", classes: ["C"] },
  { id: "c", theme: "colreg", classes: ["C"] },
];

test("daysBetween counts whole days across month and year boundaries", () => {
  assert.equal(daysBetween("2026-07-29", "2026-07-29"), 0);
  assert.equal(daysBetween("2026-07-31", "2026-08-01"), 1);
  assert.equal(daysBetween("2025-12-31", "2026-01-01"), 1);
  assert.equal(daysBetween("2026-08-01", "2026-07-31"), -1);
});

// A state with one question answered correctly on two different days.
function safeOn(streakStart, lastDay) {
  return { version: 1, examClass: "C", exams: [],
           q: { q1: { seen: 2, correct: 2, streak: 2, streakStart, lastDay } } };
}

test("safety lasts thirty days and not thirty-one", () => {
  const state = safeOn("2026-07-01", "2026-07-02");
  assert.ok(isSafe(state, "q1", "2026-08-01"), "day 30 is still safe");
  assert.ok(!isSafe(state, "q1", "2026-08-02"), "day 31 is not");
});

test("a clock running backwards leaves the question unsafe", () => {
  // The same direction the streak rule already chose: of two ways to be wrong
  // about the clock, pick the one that does not cost marks in the exam hall.
  const state = safeOn("2026-07-01", "2026-07-02");
  assert.ok(!isSafe(state, "q1", "2026-07-01"));
});

test("reconfirming an expired question costs one answer, not two", () => {
  const state = safeOn("2026-05-01", "2026-05-02");
  assert.ok(!isSafe(state, "q1", "2026-07-29"), "long expired");
  recordAnswer(state, "q1", true, "2026-07-29");
  assert.ok(isSafe(state, "q1", "2026-07-29"), "one correct answer renews it");
});

test("a wrong answer still breaks the streak entirely", () => {
  const state = safeOn("2026-05-01", "2026-05-02");
  recordAnswer(state, "q1", false, "2026-07-29");
  recordAnswer(state, "q1", true, "2026-07-29");
  assert.ok(!isSafe(state, "q1", "2026-07-29"), "same-day streak is recall, not retention");
});

test("adoptProgress accepts its own export and nothing stranger", () => {
  const good = createProgress("D");
  assert.deepEqual(adoptProgress(JSON.parse(JSON.stringify(good))), good);
  assert.equal(adoptProgress(null), null);
  assert.equal(adoptProgress("text"), null);
  assert.equal(adoptProgress({}), null);
  assert.equal(adoptProgress({ ...good, version: 2 }), null, "a future version is not ours to guess at");
  assert.equal(adoptProgress({ ...good, examClass: "S" }), null, "class S has no exam");
  assert.equal(adoptProgress({ ...good, q: [] }), null, "records are an object, not a list");
  assert.equal(adoptProgress({ ...good, exams: {} }), null);
});

test("adoptProgress keeps a valid theme and drops a corrupt one", () => {
  const good = createProgress("C");
  assert.equal(adoptProgress({ ...good, theme: "dark" }).theme, "dark");
  assert.equal(adoptProgress({ ...good, theme: "mov" }).theme, undefined);
});

test("a fresh answer sheet marks nothing as safe", () => {
  const state = createProgress("C");
  assert.equal(isSafe(state, "a", "2026-07-26"), false);
  assert.deepEqual(unsafeIds(state, QUESTIONS, "2026-07-26").sort(), ["a", "b", "c"]);
});

test("one correct answer is not enough", () => {
  const state = recordAnswer(createProgress("C"), "a", true, "2026-07-26");
  assert.equal(isSafe(state, "a", "2026-07-26"), false);
});

test("two correct answers on the same day are not enough", () => {
  let state = recordAnswer(createProgress("C"), "a", true, "2026-07-26");
  state = recordAnswer(state, "a", true, "2026-07-26");
  assert.equal(isSafe(state, "a", "2026-07-26"), false, "same-day repetition proves recall, not retention");
});

test("two correct answers on different days make it safe", () => {
  let state = recordAnswer(createProgress("C"), "a", true, "2026-07-26");
  state = recordAnswer(state, "a", true, "2026-07-27");
  assert.equal(isSafe(state, "a", "2026-07-27"), true);
});

test("a wrong answer undoes safety no matter the history", () => {
  let state = createProgress("C");
  state = recordAnswer(state, "a", true, "2026-07-26");
  state = recordAnswer(state, "a", true, "2026-07-27");
  state = recordAnswer(state, "a", false, "2026-07-28");
  assert.equal(isSafe(state, "a", "2026-07-28"), false);
});

test("recovering after a mistake needs two more days", () => {
  let state = createProgress("C");
  state = recordAnswer(state, "a", false, "2026-07-26");
  state = recordAnswer(state, "a", true, "2026-07-27");
  assert.equal(isSafe(state, "a", "2026-07-27"), false);
  state = recordAnswer(state, "a", true, "2026-07-28");
  assert.equal(isSafe(state, "a", "2026-07-28"), true);
});

test("counts are reported per theme", () => {
  let state = createProgress("C");
  state = recordAnswer(state, "a", true, "2026-07-26");
  state = recordAnswer(state, "a", true, "2026-07-27");
  assert.deepEqual(unsafeByTheme(state, QUESTIONS, "2026-07-27"), { marinarie: 1, colreg: 1 });
});

test("attempts are tallied even when the answer is wrong", () => {
  let state = recordAnswer(createProgress("C"), "a", false, "2026-07-26");
  assert.equal(state.q.a.seen, 1);
  assert.equal(state.q.a.correct, 0);
});

test("two questions never share a record", () => {
  let state = createProgress("C");
  state = recordAnswer(state, "a", true, "2026-07-26");
  state = recordAnswer(state, "b", false, "2026-07-26");
  assert.equal(state.q.a.correct, 1);
  assert.equal(state.q.b.correct, 0);
  assert.equal(state.q.a.streak, 1);
  assert.equal(state.q.b.streak, 0);
});

test("a clock running backwards does not grant safety", () => {
  // Failing toward "still needs practice" is the only acceptable direction.
  let state = createProgress("C");
  state = recordAnswer(state, "a", true, "2026-07-30");
  state = recordAnswer(state, "a", true, "2026-07-28");
  assert.equal(state.q.a.streak, 2);
  assert.equal(isSafe(state, "a", "2026-07-28"), false);
});

const {
  forClass, forTheme, blacklist, drillOrder, drawExam, drawDifference, recordSitting, grade,
} = require("../../src/caa/assets/logic.js");

const RULES = {
  questions: 26,
  pass: 22,
  draw: {
    C: [[["COLREG"], 10], [["NAVIGATIE", "MANEVRA"], 6], [["MARINARIE"], 6],
        [["PRIM_AJUTOR"], 2], [["LEGISLATIE"], 2]],
    D: [[["RND"], 10], [["MARINARIE"], 6], [["MANEVRA"], 6],
        [["PRIM_AJUTOR"], 2], [["LEGISLATIE"], 2]],
  },
  difference: { questions: 10, pass: 8, disciplines: { C: ["COLREG"], D: ["RND"] } },
};

function bank() {
  const made = [];
  const add = (discipline, examClass, count) => {
    for (let i = 0; i < count; i += 1) {
      made.push({
        id: `${examClass}-${discipline}-${i}`,
        theme: discipline.toLowerCase(),
        classes: [examClass],
        disciplines: { [examClass]: [discipline] },
      });
    }
  };
  add("COLREG", "C", 30); add("NAVIGATIE", "C", 20); add("MANEVRA", "C", 20);
  add("MARINARIE", "C", 20); add("PRIM_AJUTOR", "C", 10); add("LEGISLATIE", "C", 10);
  add("RND", "D", 30); add("MARINARIE", "D", 20); add("MANEVRA", "D", 20);
  add("PRIM_AJUTOR", "D", 10); add("LEGISLATIE", "D", 10);
  return made;
}

const fixedRandom = () => 0.42;

test("a class only ever sees its own questions", () => {
  const only = forClass(bank(), "C");
  assert.ok(only.length > 0);
  assert.ok(only.every((q) => q.classes.includes("C")));
});

test("a disputed pair never shows both sides to one class", () => {
  const disputed = [
    { id: "x", theme: "t", classes: ["C"], disciplines: { C: ["MARINARIE"] }, disputed: true },
    { id: "y", theme: "t", classes: ["D"], disciplines: { D: ["MARINARIE"] }, disputed: true },
  ];
  assert.deepEqual(forClass(disputed, "C").map((q) => q.id), ["x"]);
  assert.deepEqual(forClass(disputed, "D").map((q) => q.id), ["y"]);
});

test("a theme drill stays inside the theme and the class", () => {
  const drill = forTheme(bank(), "C", "colreg");
  assert.ok(drill.length > 0);
  assert.ok(drill.every((q) => q.theme === "colreg" && q.classes.includes("C")));
});

test("the blacklist holds exactly what is not yet safe", () => {
  const questions = bank();
  let state = createProgress("C");
  const first = forClass(questions, "C")[0];
  state = recordAnswer(state, first.id, true, "2026-07-26");
  state = recordAnswer(state, first.id, true, "2026-07-27");
  const list = blacklist(state, questions, "C", "2026-07-27");
  assert.ok(!list.some((q) => q.id === first.id));
  assert.equal(list.length, forClass(questions, "C").length - 1);
});

test("a drawn exam has the official shape", () => {
  const drawn = drawExam(bank(), "C", RULES, fixedRandom);
  assert.equal(drawn.length, 26);
  const count = (name) => drawn.filter((q) => q.disciplines.C.includes(name)).length;
  assert.equal(count("COLREG"), 10);
  assert.equal(count("MARINARIE"), 6);
  assert.equal(count("PRIM_AJUTOR"), 2);
  assert.equal(count("LEGISLATIE"), 2);
  assert.equal(count("NAVIGATIE") + count("MANEVRA"), 6);
});

test("no question is drawn twice in one exam", () => {
  const drawn = drawExam(bank(), "D", RULES, fixedRandom);
  assert.equal(new Set(drawn.map((q) => q.id)).size, 26);
});

test("the difference exam draws only the distinctive discipline", () => {
  const drawn = drawDifference(bank(), "C", RULES, fixedRandom);
  assert.equal(drawn.length, 10);
  assert.ok(drawn.every((q) => q.disciplines.C.includes("COLREG")));
});

test("grading counts correct answers and applies the pass mark", () => {
  const drawn = [{ id: "a", correct: 1 }, { id: "b", correct: 0 }, { id: "c", correct: 2 }];
  const result = grade(drawn, { a: 1, b: 1, c: 2 }, 2);
  assert.equal(result.correct, 2);
  assert.equal(result.total, 3);
  assert.equal(result.passed, true);
  assert.deepEqual(result.wrong, ["b"]);
});

test("an unanswered question counts as wrong", () => {
  // Methodology article 10: unmarked answers are treated as wrong answers.
  const drawn = [{ id: "a", correct: 1 }, { id: "b", correct: 0 }];
  const result = grade(drawn, { a: 1 }, 2);
  assert.equal(result.correct, 1);
  assert.equal(result.passed, false);
  assert.deepEqual(result.wrong, ["b"]);
});

test("the first option answered correctly counts as correct", () => {
  // Guards against a truthy check: answer 0 is a real answer, not "unanswered".
  const result = grade([{ id: "a", correct: 0 }], { a: 0 }, 1);
  assert.equal(result.correct, 1);
  assert.equal(result.passed, true);
  assert.deepEqual(result.wrong, []);
});

test("a wrong answer in a sitting takes a safe question back to unsafe", () => {
  // Section 7.1: any wrong answer returns the question to the unsafe list,
  // whatever its history. A sitting is not exempt.
  let state = recordAnswer(createProgress("C"), "a", true, "2026-07-25");
  state = recordAnswer(state, "a", true, "2026-07-26");
  assert.equal(isSafe(state, "a", "2026-07-26"), true, "precondition: the question starts safe");

  const drawn = [{ id: "a", correct: 1 }];
  recordSitting(state, drawn, { a: 0 }, "2026-07-27");

  assert.equal(isSafe(state, "a", "2026-07-27"), false);
  assert.equal(state.q["a"].streak, 0);
});

test("a correct answer in a sitting builds the streak like any other", () => {
  let state = recordAnswer(createProgress("C"), "a", true, "2026-07-26");
  recordSitting(state, [{ id: "a", correct: 1 }], { a: 1 }, "2026-07-27");
  assert.equal(isSafe(state, "a", "2026-07-27"), true);
  assert.equal(state.q["a"].seen, 2);
});

test("an abandoned sitting does not demote the questions never reached", () => {
  // The grader counts silence as wrong; retention must not. A candidate who
  // runs out of time at question 6 has said nothing about questions 7 to 26.
  let state = recordAnswer(createProgress("C"), "a", true, "2026-07-25");
  state = recordAnswer(state, "a", true, "2026-07-26");
  const drawn = [{ id: "a", correct: 1 }, { id: "b", correct: 0 }];

  recordSitting(state, drawn, {}, "2026-07-27");

  assert.equal(isSafe(state, "a", "2026-07-26"), true, "an untouched question keeps its history");
  assert.equal(state.q["b"], undefined, "and gains none");
});

test("answering option 0 in a sitting is an answer, not silence", () => {
  // Guards against a truthy check on the chosen index, the same trap `grade`
  // has its own test for.
  const state = createProgress("C");
  recordSitting(state, [{ id: "a", correct: 0 }], { a: 0 }, "2026-07-26");
  assert.equal(state.q["a"].correct, 1);
  assert.equal(state.q["a"].streak, 1);
});

test("a pool too small to fill a group fails loudly", () => {
  const thin = [
    { id: "1", classes: ["C"], disciplines: { C: ["COLREG"] } },
    { id: "2", classes: ["C"], disciplines: { C: ["COLREG"] } },
  ];
  const rules = { draw: { C: [[["COLREG"], 10]] } };
  assert.throws(() => drawExam(thin, "C", rules, () => 0.5), /pool prea mic/);
});

test("a drill puts unsafe questions before safe ones", () => {
  const questions = [
    { id: "a", theme: "t", classes: ["C"] },
    { id: "b", theme: "t", classes: ["C"] },
    { id: "c", theme: "t", classes: ["C"] },
  ];
  let state = createProgress("C");
  state = recordAnswer(state, "b", true, "2026-07-26");
  state = recordAnswer(state, "b", true, "2026-07-27");
  const order = drillOrder(state, questions, () => 0.5, "2026-07-27");
  assert.equal(order[order.length - 1].id, "b", "the only safe question goes last");
  assert.equal(order.length, 3);
});

test("re-sorting after a wrong answer moves the question back to the front", () => {
  // The case a once-computed order gets wrong: a safe question demoted
  // mid-session must not stay parked behind the ones already known.
  const questions = [
    { id: "a", theme: "t", classes: ["C"] },
    { id: "b", theme: "t", classes: ["C"] },
  ];
  let state = createProgress("C");
  state = recordAnswer(state, "b", true, "2026-07-26");
  state = recordAnswer(state, "b", true, "2026-07-27");
  assert.equal(drillOrder(state, questions, () => 0.5, "2026-07-27").at(-1).id, "b");

  state = recordAnswer(state, "b", false, "2026-07-28");
  state = recordAnswer(state, "a", true, "2026-07-26");
  state = recordAnswer(state, "a", true, "2026-07-27");
  const after = drillOrder(state, questions, () => 0.5, "2026-07-27");
  assert.equal(after[0].id, "b", "the demoted question comes first now");
  assert.equal(after.at(-1).id, "a");
});

const { sectorSpan, sectorPath } = require("../../src/caa/assets/logic.js");

const MASTHEAD = { start: 247.5, end: 112.5 };
const STERN = { start: 112.5, end: 247.5 };
const STARBOARD = { start: 0, end: 112.5 };
const ALL_ROUND = { start: 0, end: 360 };

function largeArcFlag(d) {
  const match = d.match(/A [\d.]+ [\d.]+ 0 (\d) 1/);
  assert.ok(match, `no arc command in ${d}`);
  return Number(match[1]);
}

test("the opening is measured clockwise from the bow, crossing zero if it must", () => {
  assert.equal(sectorSpan(MASTHEAD), 225);
  assert.equal(sectorSpan(STERN), 135);
  assert.equal(sectorSpan(STARBOARD), 112.5);
});

test("a sector that returns to its own start is the whole circle", () => {
  assert.equal(sectorSpan(ALL_ROUND), 360);
  assert.equal(sectorSpan({ start: 90, end: 90 }), 360);
});

test("an arc wider than a half turn tells the browser to take the long way", () => {
  // Wrong, the browser draws the complement: 225 comes out as 135, which is
  // another question's answer.
  assert.equal(largeArcFlag(sectorPath(MASTHEAD, 40, 50, 50)), 1);
  assert.equal(largeArcFlag(sectorPath(STERN, 40, 50, 50)), 0);
  assert.equal(largeArcFlag(sectorPath(STARBOARD, 40, 50, 50)), 0);
});

test("the whole circle is drawn as two half turns", () => {
  // One arc from a point back to itself draws nothing at all.
  const d = sectorPath(ALL_ROUND, 40, 50, 50);
  assert.equal((d.match(/A /g) || []).length, 2);
  assert.ok(!d.includes("L "), "a full circle has no radius to draw");
});

test("bearing zero points at the top of the picture", () => {
  // Bow up is a presentation choice, but the geometry must follow it.
  const d = sectorPath({ start: 0, end: 90 }, 40, 50, 50);
  assert.ok(d.startsWith("M 50 50 L 50.00 10.00"), d);
});

test("bearing ninety points to the right, which is starboard", () => {
  const d = sectorPath({ start: 90, end: 180 }, 40, 50, 50);
  assert.ok(d.startsWith("M 50 50 L 90.00 50.00"), d);
});

const { themeSoundings } = require("../../src/caa/assets/logic.js");

const CHART = [
  { id: "a1", theme: "parame", classes: ["C"] },
  { id: "a2", theme: "parame", classes: ["C"] },
  { id: "b1", theme: "lumini", classes: ["C"] },
];

test("a theme with nothing unsafe left still appears, at zero", () => {
  let state = createProgress("C");
  state = recordAnswer(state, "b1", true, "2026-07-26");
  state = recordAnswer(state, "b1", true, "2026-07-27");
  const { above, below } = themeSoundings(state, CHART, 40, "2026-07-27");
  assert.deepEqual(above, []);
  assert.deepEqual(below, [["parame", 2], ["lumini", 0]]);
});

test("the contour is inclusive: exactly the threshold is still clear water", () => {
  const questions = Array.from({ length: 41 }, (_, i) => ({ id: `q${i}`, theme: "t", classes: ["C"] }));
  let state = createProgress("C");
  assert.deepEqual(themeSoundings(state, questions, 41, "2026-07-26").above, [], "41 of 41 at a contour of 41");
  assert.deepEqual(themeSoundings(state, questions, 40, "2026-07-26").above, [["t", 41]], "41 is above a contour of 40");
});

test("the split is deterministic when counts tie", () => {
  const questions = [
    { id: "x", theme: "zebra", classes: ["C"] },
    { id: "y", theme: "alfa", classes: ["C"] },
  ];
  const state = createProgress("C");
  const once = themeSoundings(state, questions, 40, "2026-07-26").below.map(([theme]) => theme);
  const twice = themeSoundings(state, questions, 40, "2026-07-26").below.map(([theme]) => theme);
  assert.deepEqual(once, twice);
  assert.deepEqual(once, ["alfa", "zebra"], "ties break on the theme name");
});

test("the per-theme counts always sum to the blacklist", () => {
  let state = createProgress("C");
  state = recordAnswer(state, "a1", true, "2026-07-26");
  state = recordAnswer(state, "a1", true, "2026-07-27");
  const { above, below } = themeSoundings(state, CHART, 40, "2026-07-27");
  const total = [...above, ...below].reduce((sum, [, count]) => sum + count, 0);
  assert.equal(total, blacklist(state, CHART, "C", "2026-07-27").length);
});

const { signalTimeline, signalDuration } = require("../../src/caa/assets/logic.js");

const TIMING = {
  durations: { short: 1000, long: 4500, "very-short": 250, stroke: 600 },
  gaps: { "very-short": 250 },
  defaultGap: 500,
};

test("a single sound has no gap around it", () => {
  const timeline = signalTimeline({ pattern: ["short"] }, TIMING);
  assert.deepEqual(timeline, [{ kind: "short", ms: 1000 }]);
});

test("gaps sit between sounds, never at the ends", () => {
  const timeline = signalTimeline({ pattern: ["short", "short", "short"] }, TIMING);
  assert.deepEqual(timeline.map((step) => step.kind),
                   ["short", null, "short", null, "short"]);
  assert.equal(signalDuration(timeline), 1000 * 3 + 500 * 2);
});

test("the letter C alternates long and short", () => {
  const timeline = signalTimeline({ pattern: ["long", "short", "long", "short"] }, TIMING);
  assert.deepEqual(timeline.filter((step) => step.kind).map((step) => step.ms),
                   [4500, 1000, 4500, 1000]);
});

test("the very short series uses its own quarter-second interval", () => {
  const timeline = signalTimeline({ pattern: Array(6).fill("very-short") }, TIMING);
  const gaps = timeline.filter((step) => step.kind === null);
  assert.equal(gaps.length, 5);
  assert.ok(gaps.every((step) => step.ms === 250), "the bank states the interval, not the default");
  assert.equal(signalDuration(timeline), 250 * 6 + 250 * 5);
});

test("an unknown sound kind fails loudly", () => {
  assert.throws(() => signalTimeline({ pattern: ["whisper"] }, TIMING), /whisper/);
});

const { figureBands } = require("../../src/caa/assets/logic.js");

const EAST = { body: { shape: "pillar", bands: ["black", "yellow", "black"] } };
const WEST = { body: { shape: "pillar", bands: ["yellow", "black", "yellow"] } };
// North is the only cardinal in the bank whose stripes are not a palindrome,
// which makes it the only one that can catch an inverted order. East and West
// both read the same reversed, so tests built on them passed happily with the
// bands reversed — verified, and the reason this fixture exists.
const NORTH = { body: { shape: "pillar", bands: ["black", "yellow"] } };
const BIFURCATION = { body: { shape: "sphere", bands: ["green", "red", "green", "red"] } };
const PLAIN = { body: { shape: "cone-up", bands: ["green"] } };

test("bands read from the top down, in the order the bank gives them", () => {
  // Compared against the input rather than a literal, so the assertion cannot
  // drift away from the fixture it is meant to describe.
  const bands = figureBands(NORTH);
  assert.deepEqual(bands.map((band) => band.colour), NORTH.body.bands);
  assert.ok(bands[0].top < bands[1].top, "the first colour named sits highest");
});

test("a repeated colour is a position, not a duplicate to collapse", () => {
  const bands = figureBands(BIFURCATION);
  assert.deepEqual(bands.map((band) => band.colour), BIFURCATION.body.bands);
  assert.equal(bands.length, 4);
});

test("east and west are not the same figure", () => {
  // The whole difficulty of the cardinals is which way round they go.
  assert.notDeepEqual(figureBands(EAST).map((b) => b.colour),
                      figureBands(WEST).map((b) => b.colour));
});

test("bands divide the body evenly and cover all of it", () => {
  const bands = figureBands(EAST);
  assert.equal(bands.length, 3);
  bands.forEach((band, index) => {
    assert.ok(Math.abs(band.top - index / 3) < 1e-9, `band ${index} starts at ${band.top}`);
    assert.ok(Math.abs(band.height - 1 / 3) < 1e-9);
  });
  const last = bands[bands.length - 1];
  assert.ok(Math.abs(last.top + last.height - 1) < 1e-9, "the bands reach the bottom");
});

test("a single colour fills the whole body", () => {
  assert.deepEqual(figureBands(PLAIN), [{ colour: "green", top: 0, height: 1 }]);
});

test("a body with no bands fails loudly", () => {
  assert.throws(() => figureBands({ body: { shape: "pillar", bands: [] } }), /bands/);
});


// Reads a bearing back out of a point on the circle, so a test can state
// where an arc ends rather than what its coordinates happen to format as.
function bearingOf(x, y, cx, cy) {
  return (Math.atan2(x - cx, cy - y) * 180 / Math.PI + 360) % 360;
}

test("the arc ends where the sector ends, not where it started", () => {
  // Nothing above constrains this. The flag depends only on the span, and the
  // orientation tests pin the radius line's start point, which sits earlier in
  // the string — so an endpoint computed from sector.start instead of
  // sector.end draws a bare line with no wedge at all, and every other test
  // here stays green.
  for (const sector of [MASTHEAD, STERN, STARBOARD]) {
    const d = sectorPath(sector, 40, 50, 50);
    const end = d.match(/A [\d.]+ [\d.]+ 0 \d 1 (-?[\d.]+) (-?[\d.]+)/);
    assert.ok(end, `no arc command in ${d}`);
    const bearing = bearingOf(Number(end[1]), Number(end[2]), 50, 50);
    assert.ok(Math.abs(bearing - sector.end) < 0.01,
              `arc ends at ${bearing.toFixed(2)}°, the sector at ${sector.end}°`);
  }
});

test("the radius line starts where the sector starts", () => {
  for (const sector of [MASTHEAD, STERN, STARBOARD]) {
    const d = sectorPath(sector, 40, 50, 50);
    const start = d.match(/L (-?[\d.]+) (-?[\d.]+)/);
    const bearing = bearingOf(Number(start[1]), Number(start[2]), 50, 50);
    assert.ok(Math.abs(bearing - sector.start % 360) < 0.01,
              `radius drawn at ${bearing.toFixed(2)}°, the sector starts at ${sector.start}°`);
  }
});

test("a half turn does not take the long way", () => {
  // The boundary of the flag rule, which no real light sits on.
  assert.equal(sectorSpan({ start: 0, end: 180 }), 180);
  assert.equal(largeArcFlag(sectorPath({ start: 0, end: 180 }, 40, 50, 50)), 0);
});

const { lightPlacement, STATION_BASE_Y, DECK_Y } = require("../../src/caa/assets/logic.js");

const CONFIG = {
  id: "traulare-nu-in-mars",
  lights: [
    { colours: ["green"], station: "any", level: 1 },
    { colours: ["white"], station: "any", level: 0 },
    { colours: ["white"], station: "mast", level: 0 },
  ],
};

test("a higher level sits higher on the screen", () => {
  const placed = lightPlacement(CONFIG);
  const [green, white] = placed;
  assert.equal(green.x, white.x);
  assert.ok(green.y < white.y, "level 1 must be above level 0");
});

test("the masthead light is abaft the amidships staff and above all of it", () => {
  // The trawler's source: "o lumină de catarg aşezată la o înălţime mai mare
  // decât lumina verde şi înapoia acesteia". The bow points right, so abaft
  // is a smaller x. Both relations are the drawing's whole claim.
  const placed = lightPlacement(CONFIG);
  const green = placed.find((light) => light.station === "any" && light.level === 1);
  const masthead = placed.find((light) => light.station === "mast");
  assert.ok(masthead.x < green.x, "the mast must sit aft of the amidships staff");
  assert.ok(masthead.y < green.y, "the masthead light must sit above the green");
});

test("the bow extremity is forward of the usual sidelight position", () => {
  // Towed alongside carries them "la extremitatea prova"; a plain tow does
  // not. Drawn at the same place, the two configurations would be one figure.
  const placed = lightPlacement({
    lights: [
      { colours: ["red", "green"], station: "bow", level: 0 },
      { colours: ["red", "green"], station: "side", level: 0 },
    ],
  });
  assert.ok(placed[0].x > placed[1].x, "the bow must be forward of the sides");
});

test("every light sits above the deck", () => {
  const placed = lightPlacement(CONFIG);
  for (const light of placed) assert.ok(light.y < DECK_Y, light.station);
});

test("an unknown station is an error, not a light at zero", () => {
  assert.throws(
    () => lightPlacement({ lights: [{ colours: ["white"], station: "crowsnest" }] }),
    /crowsnest/
  );
});

test("a light with no level given sits at the bottom of its station", () => {
  const placed = lightPlacement({ lights: [{ colours: ["white"], station: "stern" }] });
  assert.equal(placed[0].y, STATION_BASE_Y.stern);
});

test("a station inherited from Object.prototype is unknown too", () => {
  // `in` walks the prototype chain, so "toString" passed the guard and the
  // function returned x = a function and y = NaN — a lantern drawn nowhere,
  // in silence. Unreachable from the catalogue, whose stations are fixed
  // Python constants, but the guard is here precisely to be the thing that
  // does not depend on that staying true.
  for (const station of ["toString", "constructor", "valueOf"]) {
    assert.throws(
      () => lightPlacement({ lights: [{ colours: ["white"], station }] }),
      new RegExp(station)
    );
  }
});

test("adoptProgress rejects a file whose insides would brick the boot", () => {
  // Final review's scenario: {"exams":[null]} passed validation, persisted,
  // and then every reload crashed before the navigation existed — a blank
  // app only DevTools could recover. The validator now looks inside.
  const good = createProgress("C");
  assert.equal(adoptProgress({ ...good, exams: [null] }), null);
  assert.equal(adoptProgress({ ...good, exams: [[]] }), null);
  assert.equal(adoptProgress({ ...good, q: { "c-01": 5 } }), null);
  assert.equal(adoptProgress({ ...good, q: { "c-01": null } }), null);
  // and the shapes the app itself writes still pass
  const lived = { ...good,
    exams: [{ day: "2026-07-29", examClass: "C", correct: 24, total: 26, passed: true }],
    q: { "c-01": { seen: 2, correct: 2, streak: 2, streakStart: "2026-07-01", lastDay: "2026-07-02" } } };
  assert.notEqual(adoptProgress(lived), null);
});

test("adoptProgress rejects the shapes review found untested", () => {
  const good = createProgress("C");
  assert.equal(adoptProgress({ ...good, q: null }), null);
  assert.equal(adoptProgress({ ...good, version: 0 }), null);
  assert.equal(adoptProgress({ ...good, version: "1" }), null, "a numeric string is not a version");
  assert.equal(adoptProgress({ ...good, theme: "auto" }).theme, undefined,
    "auto is expressed by absence, never stored");
});
