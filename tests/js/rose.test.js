"use strict";

// The compass rose, drawn against the same DOM stub lights.test.js uses.
//
// What matters here is not that a circle appears — it is that the angle each
// rose draws starts where its rule says it starts. A drawing that measured
// the fore bearing from north instead of from the bow would look perfectly
// plausible and teach the one thing the statement exists to correct.

const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ASSETS = path.join(__dirname, "..", "..", "src", "caa", "assets");
const PAGE = path.join(__dirname, "..", "..", "build", "permis-ambarcatiuni.html");
const missing = fs.existsSync(PAGE) ? false : "build the page first: python -m caa.app";

function element(tag) {
  return {
    tag,
    attrs: {},
    kids: [],
    text: undefined,
    set textContent(value) { this.text = value; },
    get textContent() { return this.text; },
    setAttribute(name, value) { this.attrs[name] = String(value); },
    append(...children) { this.kids.push(...children); },
  };
}

function load() {
  const context = { document: { createElementNS: (ns, tag) => element(tag) }, Object, Math };
  vm.createContext(context);
  for (const file of ["logic.js", "rose.js"]) {
    vm.runInContext(fs.readFileSync(path.join(ASSETS, file), "utf8"), context, file);
  }
  return {
    drawRose: context.drawRose,
    bearingPoint: context.bearingPoint,
    centre: [vm.runInContext("ROSE_CX", context), vm.runInContext("ROSE_CY", context)],
  };
}

function roses() {
  const html = fs.readFileSync(PAGE, "utf8");
  for (const [, id, body] of html.matchAll(
    /<script id="([^"]+)" type="application\/json">([\s\S]*?)<\/script>/g
  )) {
    if (id === "roses") return JSON.parse(body).roses;
  }
  throw new Error("no roses catalogue in the built page");
}

function descendants(node, out = []) {
  out.push(node);
  for (const kid of node.kids) descendants(kid, out);
  return out;
}

test("an angle arc starts and ends on the bearings its rule names",
  { skip: missing }, () => {
  const { drawRose, bearingPoint, centre } = load();
  const [cx, cy] = centre;
  let checked = 0;

  for (const rose of roses()) {
    const nodes = descendants(drawRose(rose, 100));
    const arcs = nodes.filter((n) => n.tag === "path" && (n.attrs.d || "").includes(" A "));
    assert.equal(arcs.length, rose.angles.length, `${rose.id}: wrong number of angle arcs`);

    rose.angles.forEach((angle, index) => {
      // The path is "M x1 y1 A r r 0 f 1 x2 y2": its ends are the two bearings.
      const numbers = arcs[index].attrs.d.match(/-?[\d.]+/g).map(Number);
      const [x1, y1] = [numbers[0], numbers[1]];
      const radius = numbers[2];
      const [x2, y2] = [numbers[numbers.length - 2], numbers[numbers.length - 1]];
      const expectStart = bearingPoint(angle.start, radius, cx, cy).map(Number);
      const expectEnd = bearingPoint(angle.end, radius, cx, cy).map(Number);
      assert.ok(Math.hypot(x1 - expectStart[0], y1 - expectStart[1]) < 0.05,
        `${rose.id}: ${angle.label} does not start at ${angle.start}`);
      assert.ok(Math.hypot(x2 - expectEnd[0], y2 - expectEnd[1]) < 0.05,
        `${rose.id}: ${angle.label} does not end at ${angle.end}`);
      checked += 1;
    });
  }
  assert.ok(checked >= 3, "the definition roses are not being drawn");
});

test("the fore bearing is the one angle that does not start at north",
  { skip: missing }, () => {
  // The whole reason this drawing exists. If it ever starts at north the
  // picture agrees with the two rules above it and contradicts its own.
  const fore = roses().find((rose) => rose.id === "relevment-prova");
  assert.ok(fore, "the fore-bearing rose is gone");
  assert.equal(fore.angles.length, 1);
  assert.notEqual(fore.angles[0].start, 0, "the fore bearing must not start at north");
  assert.equal(fore.angles[0].start, fore.bow, "it starts at the bow, by definition");

  for (const id of ["drum", "relevment"]) {
    const rose = roses().find((entry) => entry.id === id);
    assert.equal(rose.angles[0].start, 0, `${id} is measured from north`);
  }
});

test("every rose label the renderer prints comes from the catalogue",
  { skip: missing }, () => {
  const { drawRose } = load();
  for (const rose of roses()) {
    const printed = descendants(drawRose(rose, 100))
      .filter((n) => n.tag === "text")
      .map((n) => n.textContent);
    const allowed = new Set([
      ...rose.rays.map((r) => r.label),
      ...rose.angles.map((a) => a.label),
      "reper", "prova",
    ]);
    for (const label of printed) {
      assert.ok(allowed.has(label), `${rose.id}: the renderer invented ${label!== undefined ? JSON.stringify(label) : "nothing"}`);
    }
  }
});
