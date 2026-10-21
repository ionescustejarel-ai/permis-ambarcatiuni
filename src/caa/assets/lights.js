"use strict";

// What a vessel carries, drawn in profile with the bow to the right. Profile
// is the only projection that shows both things the source gives: the order
// of stacked lights, and how far forward or aft they sit.
//
// A lantern is a small disc. One that shows more than one colour — the
// combined lantern, the pair of sidelights — is split into equal wedges, one
// per colour, using the same geometry stage 3c built for arcs. A lantern
// whose source names no colour gets a single neutral disc.

const LIGHT_NS = "http://www.w3.org/2000/svg";
const LIGHT_RADIUS = 3.4;

// A hull, not a drawing of a particular vessel: flat deck, sloping ends, bow
// to the right. Anything more specific would suggest the configuration
// belongs to that kind of boat.
const LIGHT_HULL = "M 18 58 L 104 58 L 98 67 L 26 67 Z";

function lightNode(tag, attrs) {
  const node = document.createElementNS(LIGHT_NS, tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  return node;
}

function lightMarker(colours, x, y) {
  const group = lightNode("g", {});
  // An empty list still draws one disc: "the source names no colour" is a
  // fact about the light, not an absence of light.
  const names = colours.length ? colours : [null];
  const step = 360 / names.length;
  names.forEach((name, index) => {
    group.append(lightNode("path", {
      d: sectorPath({ start: index * step, end: (index + 1) * step }, LIGHT_RADIUS, x, y),
      fill: name ? LIGHT_PAINT[name] : LIGHT_NEUTRAL,
      "fill-opacity": name ? 1 : 0.3,
      stroke: "currentColor",
      "stroke-width": 0.5,
    }));
  });
  return group;
}

function drawConfig(config, width) {
  const root = lightNode("svg", {
    viewBox: "0 0 120 80", width: width, height: (width * 80) / 120,
    role: "img", "aria-label": config.label,
  });
  const placed = lightPlacement(config);

  // Staffs first, then the hull over them, then the lanterns on top.
  for (const light of placed) {
    root.append(lightNode("line", {
      x1: light.x, y1: DECK_Y, x2: light.x, y2: light.y,
      stroke: "currentColor", "stroke-width": 0.7, "stroke-opacity": 0.45,
    }));
  }
  root.append(lightNode("path", {
    d: LIGHT_HULL, fill: "var(--paper)", stroke: "currentColor", "stroke-width": 1.2,
  }));
  for (const light of placed) root.append(lightMarker(light.colours, light.x, light.y));

  return root;
}
