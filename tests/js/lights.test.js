"use strict";

// The first test in this project that actually draws something.
//
// Everything else about the renderers is indirect: page.test.js proves the
// scripts parse, logic.test.js proves the coordinates are right. Neither can
// see a lantern painted the wrong colour, a pair of lights collapsed into
// one, or a figure that contradicts the bank — and a mark drawn wrong has
// shipped here before, caught only by opening a browser.
//
// So this runs the real renderer over the catalogue the build emits, against
// a DOM stub small enough to read back, and checks the facts the exam turns
// on.

const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ASSETS = path.join(__dirname, "..", "..", "src", "caa", "assets");
const PAGE = path.join(__dirname, "..", "..", "build", "permis-ambarcatiuni.html");
const missing = fs.existsSync(PAGE) ? false : "build the page first: python -m caa.app";

const NEUTRAL = "currentColor";
const MAST_X = 46; // logic.js STATION_X.mast — the only station this file names

function element(tag) {
  return {
    tag,
    attrs: {},
    kids: [],
    setAttribute(name, value) { this.attrs[name] = String(value); },
    append(...children) { this.kids.push(...children); },
  };
}

// The three renderer assets share globals through the page, so they get one
// context rather than a module each.
function load() {
  const context = { document: { createElementNS: (ns, tag) => element(tag) }, Object, Math };
  vm.createContext(context);
  for (const file of ["logic.js", "arcs.js", "lights.js"]) {
    vm.runInContext(fs.readFileSync(path.join(ASSETS, file), "utf8"), context, file);
  }
  return {
    drawConfig: context.drawConfig,
    // A top-level const is a lexical binding, not a property of the context,
    // so it has to be read from inside.
    paint: vm.runInContext("LIGHT_PAINT", context),
  };
}

function configs() {
  const html = fs.readFileSync(PAGE, "utf8");
  for (const [, id, body] of html.matchAll(
    /<script id="([^"]+)" type="application\/json">([\s\S]*?)<\/script>/g
  )) {
    if (id === "lights") return JSON.parse(body).configs;
  }
  throw new Error("no lights catalogue in the built page");
}

function descendants(node, out = []) {
  out.push(node);
  for (const kid of node.kids) descendants(kid, out);
  return out;
}

// A lantern is a group of wedges, and its centre has to be read back out of
// the first wedge's path. The two path shapes differ: a wedge starts at the
// centre and draws a line out to the rim, while a lantern of a single colour
// is a whole circle, whose path starts at the top of the rim instead. Taking
// the opening point as the centre either way is wrong by one radius, and
// wrong only for some lanterns — which is worse than being wrong for all.
function centre(d) {
  const [, x, y] = d.match(/^M ([\d.]+) ([\d.]+)/);
  if (d.includes(" L ")) return [Number(x), Number(y)];
  const [, radius] = d.match(/A ([\d.]+) /);
  return [Number(x), Number(y) + Number(radius)];
}

function lanterns(svg) {
  return descendants(svg)
    .filter((node) => node.tag === "g")
    .map((group) => {
      const [x, y] = centre(group.kids[0].attrs.d);
      return {
        wedges: group.kids.length,
        fills: group.kids.map((kid) => kid.attrs.fill),
        x,
        y,
      };
    });
}

function drawn() {
  const { drawConfig, paint } = load();
  const byId = {};
  for (const config of configs()) byId[config.id] = lanterns(drawConfig(config, 148));
  return { byId, paint };
}

test("every configuration draws exactly the lanterns it declares", { skip: missing }, () => {
  const { drawConfig } = load();
  const all = configs();
  assert.equal(all.length, 12);
  for (const config of all) {
    const svg = drawConfig(config, 148);
    assert.equal(svg.attrs["aria-label"], config.label, config.id);
    const drawnLanterns = lanterns(svg);
    assert.equal(drawnLanterns.length, config.lights.length, config.id);
    for (const lantern of drawnLanterns) {
      assert.ok(!lantern.fills.includes(undefined), `${config.id}: a colour resolved to undefined`);
    }
  }
});

test("the sailing vessel is drawn differently at the two classes", { skip: missing }, () => {
  // The proof the whole stage turns on. At class D the vessel carries two
  // all-round lights at the masthead, red over green; at class C it carries
  // none at all. One figure for both would be wrong for one of them.
  const { byId, paint } = drawn();

  const masthead = byId["vele-in-mars-D"]
    .filter((lantern) => lantern.x === MAST_X)
    .sort((a, b) => a.y - b.y);
  assert.equal(masthead.length, 2);
  assert.deepEqual(masthead.map((lantern) => lantern.fills[0]), [paint.red, paint.green]);

  assert.ok(
    byId["vele-in-mars"].every((lantern) => lantern.x !== MAST_X),
    "class C carries no masthead lantern"
  );
});

test("a lantern shows every colour its source names, and no more", { skip: missing }, () => {
  const { byId, paint } = drawn();

  // "reunite într-un felinar" — one lantern, three colours, not three lights.
  const combined = byId["vele-felinar-combinat"];
  assert.equal(combined.length, 1);
  assert.equal(combined[0].wedges, 3);

  // The sidelights are a pair drawn as a single marker.
  const pair = byId["remorcata"].find((lantern) => lantern.wedges === 2);
  assert.ok(pair, "the sidelights are drawn as one two-coloured lantern");
  assert.deepEqual([...pair.fills].sort(), [paint.green, paint.red].sort());
});

test("the anchor light is drawn without a colour", { skip: missing }, () => {
  // The bank never states one, in any of the six questions that mention it.
  // Painting it white would be reading COLREG into a source that is silent.
  const { byId } = drawn();
  const stern = byId["manevra-redusa-la-ancora"].filter((lantern) => lantern.wedges === 1
    && lantern.fills[0] === NEUTRAL);
  assert.equal(stern.length, 1);
});

test("towed alongside carries its sidelights further forward", { skip: missing }, () => {
  // "la extremitatea prova" is the only thing telling the two tows apart, so
  // if the drawing puts them in the same place the distinction is lost.
  const { byId } = drawn();
  const alongside = byId["remorcata-la-ureche"].find((lantern) => lantern.wedges === 2);
  const plain = byId["remorcata"].find((lantern) => lantern.wedges === 2);
  assert.ok(alongside.x > plain.x, "the bow extremity must be forward of the usual position");
});

test("the four colours are told apart from each other", { skip: missing }, () => {
  // Every other test here compares a drawn fill against the same palette the
  // renderer painted from, so all of them pass if two colours become the same
  // hex — a mutation that made green identical to red slipped through the
  // whole file. Red and green are the one pair a candidate must never confuse.
  const { paint } = drawn();
  const values = Object.values(paint);
  assert.equal(new Set(values).size, values.length, "two lights share a colour");
  assert.ok(!values.includes(NEUTRAL), "a named colour is drawn as the unnamed tint");
});

test("each colour name is the hue it claims to be", { skip: missing }, () => {
  // Distinctness is not enough: swapping the red and green hexes leaves every
  // test in this file green, because each one compares a drawn fill against
  // the same palette the renderer painted from. That swap would invert
  // red-over-green on the class D sailing vessel and invert port and
  // starboard on every pair of sidelights, in both panels at once.
  const { paint } = drawn();
  const channels = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));

  const [r1, g1, b1] = channels(paint.red);
  assert.ok(r1 > g1 && r1 > b1, `${paint.red} is not a red`);
  const [r2, g2, b2] = channels(paint.green);
  assert.ok(g2 > r2 && g2 > b2, `${paint.green} is not a green`);
  const [r3, g3, b3] = channels(paint.yellow);
  assert.ok(r3 > b3 && g3 > b3, `${paint.yellow} is not a yellow`);
  const white = channels(paint.white);
  assert.ok(Math.min(...white) > 200 && Math.max(...white) - Math.min(...white) < 24,
    `${paint.white} is not a white`);
});
