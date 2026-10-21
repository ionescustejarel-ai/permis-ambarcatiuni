"use strict";

// The built page is the deliverable, and until now nothing ever parsed it.
// The Python tests match patterns in its text; the tests beside this one load
// logic.js on its own. So a syntax error in ui.js, audio.js or figures.js
// shipped a page that renders nothing at all, with every one of the two
// hundred tests still green — which is exactly what happened: a Romanian
// closing quotation mark typed as a straight " ended a string early, and the
// whole application went blank.

const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const PAGE = path.join(__dirname, "..", "..", "build", "permis-ambarcatiuni.html");

// A skip states its reason: a test that quietly passes on a missing artefact
// is the failure this file exists to prevent.
const missing = fs.existsSync(PAGE) ? false : "build the page first: python -m caa.app";

test("every script the page inlines parses as JavaScript", { skip: missing }, () => {
  const html = fs.readFileSync(PAGE, "utf8");
  // The data blocks carry type="application/json" and are not code.
  const blocks = [...html.matchAll(
    /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g
  )];

  assert.ok(blocks.length >= 3, `expected the inlined scripts, found ${blocks.length}`);
  blocks.forEach((block, index) => {
    // Compiles without running: the page expects a browser, and this only
    // needs to know the parser accepts it.
    assert.doesNotThrow(() => new vm.Script(block[1]), `script block ${index} does not parse`);
  });
});

test("every JSON the page inlines parses as JSON", { skip: missing }, () => {
  const html = fs.readFileSync(PAGE, "utf8");
  const blocks = [...html.matchAll(
    /<script id="([^"]+)" type="application\/json">([\s\S]*?)<\/script>/g
  )];

  assert.ok(blocks.length >= 3, `expected the embedded catalogues, found ${blocks.length}`);
  for (const [, id, body] of blocks) {
    assert.doesNotThrow(() => JSON.parse(body), `the ${id} payload does not parse`);
  }
});

// The placement unit tests use invented configurations. This one runs the real
// catalogue, as the build emits it, through the same function: a lantern that
// lands on top of another, or under the deck, would be invisible in a way no
// synthetic example can reveal.
const logic = require(path.join(__dirname, "..", "..", "src", "caa", "assets", "logic.js"));

function catalogue(id) {
  const html = fs.readFileSync(PAGE, "utf8");
  // Same literal pattern the tests above use, rather than one built from a
  // string: one less layer of escaping to get wrong.
  for (const [, name, body] of html.matchAll(
    /<script id="([^"]+)" type="application\/json">([\s\S]*?)<\/script>/g
  )) {
    if (name === id) return JSON.parse(body);
  }
  throw new Error(`no catalogue tagged ${id} in the built page`);
}

test("every configuration the build ships places without collisions", { skip: missing }, () => {
  const { configs } = catalogue("lights");
  assert.equal(configs.length, 12);
  for (const config of configs) {
    const placed = logic.lightPlacement(config);
    const spots = placed.map((light) => `${light.x},${light.y}`);
    assert.equal(new Set(spots).size, spots.length, `${config.id}: two lanterns in one spot`);
    for (const light of placed) {
      assert.ok(light.y < logic.DECK_Y, `${config.id}: a lantern below the deck`);
    }
  }
});

test("the trawler's masthead light is abaft and above its green", { skip: missing }, () => {
  // "o lumină de catarg aşezată la o înălţime mai mare decât lumina verde şi
  // înapoia acesteia" — checked on the shipped entry, not on a stand-in.
  const { configs } = catalogue("lights");
  const placed = logic.lightPlacement(configs.find((c) => c.id === "traulare-nu-in-mars"));
  const green = placed.find((light) => light.colours.includes("green"));
  const masthead = placed.find((light) => light.station === "mast");
  assert.ok(masthead.x < green.x, "the mast must sit aft of the green");
  assert.ok(masthead.y < green.y, "the masthead light must sit above the green");
});
