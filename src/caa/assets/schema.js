"use strict";

// One routine per view. They share a box and a label helper and nothing else,
// because a hull in section and a propeller seen from astern have no geometry
// in common — forcing them through one vocabulary would cost more to read
// than the four drawings are worth.
//
// Nothing is measured here. Where the bank gives a distance the drawing shows
// the two things it runs between and names them; where it gives none, no
// number appears.

const SCHEMA_NS = "http://www.w3.org/2000/svg";
const SCHEMA_INK = "currentColor";
const SCHEMA_MARK = "var(--magenta)";

function schemaNode(tag, attrs, text) {
  const node = document.createElementNS(SCHEMA_NS, tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  if (text !== undefined) node.textContent = text;
  return node;
}

function schemaText(x, y, text, options = {}) {
  return schemaNode("text", {
    x, y, "font-size": options.size || 6,
    fill: options.mark ? SCHEMA_MARK : SCHEMA_INK,
    "text-anchor": options.anchor || "middle",
    "dominant-baseline": "middle",
  }, text);
}

// An arrow along a straight run, with the head at the far end.
function schemaArrow(x1, y1, x2, y2, mark) {
  const angle = Math.atan2(y2 - y1, x2 - x1);
  const head = 3.2;
  const paint = mark ? SCHEMA_MARK : SCHEMA_INK;
  const wing = (turn) => [
    (x2 - head * Math.cos(angle + turn)).toFixed(2),
    (y2 - head * Math.sin(angle + turn)).toFixed(2),
  ];
  const [ax, ay] = wing(0.45);
  const [bx, by] = wing(-0.45);
  return [
    schemaNode("line", { x1, y1, x2, y2, stroke: paint, "stroke-width": 1.1 }),
    schemaNode("path", { d: `M ${x2} ${y2} L ${ax} ${ay} L ${bx} ${by} Z`, fill: paint }),
  ];
}

// The hull in profile: keel along the bottom, stem forward, sternpost aft.
// Bow to the right, the same way the light configurations face.
function viewSectiuneLung(root) {
  root.append(schemaNode("path", {
    d: "M 22 52 L 100 52 L 112 40 L 112 26 L 26 26 L 18 40 Z",
    fill: "none", stroke: SCHEMA_INK, "stroke-width": 1, "stroke-opacity": 0.45,
  }));
  // The keel: the one line the statement calls fundamental.
  root.append(schemaNode("line", {
    x1: 22, y1: 52, x2: 100, y2: 52, stroke: SCHEMA_MARK, "stroke-width": 2.2,
  }));
  root.append(schemaNode("line", {
    x1: 100, y1: 52, x2: 112, y2: 40, stroke: SCHEMA_MARK, "stroke-width": 2.2,
  }));
  root.append(schemaNode("line", {
    x1: 22, y1: 52, x2: 18, y2: 40, stroke: SCHEMA_MARK, "stroke-width": 2.2,
  }));
  root.append(schemaText(61, 60, "chila", { mark: true }));
  root.append(schemaText(112, 20, "etrava", { mark: true, size: 5.5 }));
  root.append(schemaText(16, 20, "etamboul", { mark: true, size: 5.5 }));
  root.append(schemaText(112, 66, "prova", { size: 5.5, anchor: "end" }));
  root.append(schemaText(18, 66, "pupa", { size: 5.5, anchor: "start" }));
}

// The hull in cross-section: the frames and floors that lie across it.
function viewSectiuneTrans(root) {
  // The planking, drawn as the outline the strakes make up.
  root.append(schemaNode("path", {
    d: "M 30 26 L 34 50 Q 65 62 96 50 L 100 26",
    fill: "none", stroke: SCHEMA_INK, "stroke-width": 1.6,
  }));
  root.append(schemaText(104, 30, "bordaj", { size: 5.5, anchor: "start" }));
  root.append(schemaText(104, 38, "din file", { size: 5, anchor: "start" }));

  // Frames up the sides, floors across the bottom. Three of each: enough to
  // read "at equal intervals", and the bank never says how many there are.
  for (const dx of [-18, 0, 18]) {
    root.append(schemaNode("path", {
      d: `M ${47 + dx * 0.82} 28 Q ${52 + dx * 0.9} 48 ${65 + dx} 55`,
      fill: "none", stroke: SCHEMA_MARK, "stroke-width": 1, "stroke-opacity": 0.75,
    }));
  }
  root.append(schemaNode("line", {
    x1: 40, y1: 53, x2: 90, y2: 53, stroke: SCHEMA_MARK, "stroke-width": 1.6,
  }));
  root.append(schemaText(65, 20, "coaste", { mark: true }));
  root.append(schemaText(65, 62, "varange", { mark: true }));
}

// Seen from above, bow up: the rudder put over one way, the bow swinging the
// other, the stern following the rudder.
//
// The way the boat is travelling has to be on the drawing, not only in the
// caption. Going ahead the bow turns towards the rudder and going astern away
// from it — mirror images — so a picture without the direction of travel
// teaches whichever of the two the reader happens to assume.
function viewPlanCarma(root, schema) {
  const starboard = schema.side === "tribord";
  const sign = starboard ? 1 : -1;
  root.append(schemaNode("path", {
    d: "M 65 16 L 76 36 L 76 62 L 54 62 L 54 36 Z",
    fill: "var(--paper)", stroke: SCHEMA_INK, "stroke-width": 1.2,
  }));
  // Making sternway: a hollow arrow down the hull's own axis.
  root.append(...schemaArrow(65, 30, 65, 56, false));
  root.append(schemaText(65, 24, "merge înapoi", { size: 5 }));
  // The rudder, hinged at the stern and put over towards `side`.
  root.append(schemaNode("line", {
    x1: 65, y1: 62, x2: 65 + sign * 9, y2: 72,
    stroke: SCHEMA_MARK, "stroke-width": 2.4,
  }));
  root.append(schemaText(65 + sign * 20, 73, "cârma", { mark: true, size: 5.5 }));

  // Bow away from the rudder, stern towards it.
  root.append(...schemaArrow(65 - sign * 14, 22, 65 - sign * 30, 22, true));
  root.append(schemaText(65 - sign * 22, 14, "prova", { mark: true, size: 5.5 }));
  root.append(...schemaArrow(65 + sign * 14, 58, 65 + sign * 30, 58, true));
  root.append(schemaText(65 + sign * 22, 50, "pupa", { mark: true, size: 5.5 }));
}

// Seen from above, bow up: wind from the starboard bow, drift to port.
function viewPlanVant(root, schema) {
  const toPort = schema.side === "babord";
  root.append(schemaNode("path", {
    d: "M 65 20 L 76 40 L 76 66 L 54 66 L 54 40 Z",
    fill: "var(--paper)", stroke: SCHEMA_INK, "stroke-width": 1.2,
  }));
  // The wind, blowing in from ahead of the beam on the starboard bow.
  root.append(...schemaArrow(104, 14, 82, 33, false));
  root.append(schemaText(108, 8, "vânt", { size: 5.5, anchor: "end" }));
  root.append(schemaText(112, 22, "prova tribord", { size: 5, anchor: "end" }));

  // The drift it gives, across the hull towards the other board.
  const target = toPort ? 26 : 104;
  root.append(...schemaArrow(65, 78, target, 78, true));
  root.append(schemaText((65 + target) / 2, 87, "derivă", { mark: true, size: 5.5 }));
  root.append(schemaText((65 + target) / 2, 94, schema.side, { mark: true, size: 5 }));
}

const SCHEMA_VIEWS = {
  "sectiune-lung": viewSectiuneLung,
  "sectiune-trans": viewSectiuneTrans,
  "plan-carma": viewPlanCarma,
  "plan-vant": viewPlanVant,
};

function drawSchema(schema, size) {
  const root = schemaNode("svg", {
    viewBox: "0 0 130 100", width: size, height: size * 0.77,
    role: "img", "aria-label": schema.label,
  });
  const view = SCHEMA_VIEWS[schema.view];
  if (!view) return root;
  view(root, schema);
  return root;
}

function schemaCard(schema) {
  const figure = el("figure", { class: "schemacard" },
    drawSchema(schema, 210),
    el("figcaption", {}, schema.label));
  if (schema.note) figure.append(el("p", { class: "schemanote" }, schema.note));
  return figure;
}
