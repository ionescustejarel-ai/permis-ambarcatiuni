"use strict";

// A light's arc, drawn around a vessel seen from above. Plan view is the only
// projection in which an arc means anything: in profile, 225° is invisible.
//
// Colours are the plain names the catalogue uses, resolved once. A sector
// whose source names no colour — "vizibilă pe întreg orizontul" is a property,
// not a colour — is drawn in a neutral tint rather than a made-up one.
//
// These are the same physical lights that stage 3d composes, so the arc and
// configuration renderers share this one object rather than keeping a copy
// each. figures.js still holds its own palette: it needs the buoy colours
// too, and its four overlapping values are a third place these can drift.
// Folding all three into one belongs in its own change, not in this one.
const LIGHT_PAINT = {
  white: "#F2F2F2",
  green: "#1E7A4C",
  red: "#C0392B",
  yellow: "#E8C21A",
};
const LIGHT_NEUTRAL = "currentColor";

const ARC_NS = "http://www.w3.org/2000/svg";
const ARC_CX = 50;
const ARC_CY = 50;
const ARC_RADIUS = 38;

function arcNode(tag, attrs) {
  const node = document.createElementNS(ARC_NS, tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  return node;
}

function drawArc(arc, size) {
  const root = arcNode("svg", {
    viewBox: "0 0 100 100", width: size, height: size,
    role: "img", "aria-label": arc.label,
  });

  for (const sector of arc.sectors) {
    const wedge = arcNode("path", { d: sectorPath(sector, ARC_RADIUS, ARC_CX, ARC_CY) });
    const paint = sector.colour ? LIGHT_PAINT[sector.colour] : LIGHT_NEUTRAL;
    wedge.setAttribute("fill", paint);
    wedge.setAttribute("fill-opacity", sector.colour ? 0.55 : 0.25);
    // Outlined in ink, not in its own colour. Measured on the light theme: a
    // white sector against the paper has a contrast ratio of 1.06, which is to
    // say invisible, and three of the five arcs are white — the stern light,
    // the masthead light and the all-round one. Filling them darker would lie
    // about the colour of the light; an outline is how a chart draws a sector
    // whose tint is paler than the page.
    wedge.setAttribute("stroke", LIGHT_NEUTRAL);
    wedge.setAttribute("stroke-width", 0.8);
    wedge.setAttribute("stroke-opacity", 0.5);
    root.append(wedge);
  }

  // The hull last, so it sits above the sectors: a simple pointed shape, bow
  // up, small enough that the arc around it stays the subject.
  root.append(arcNode("path", {
    d: "M 50 34 L 56 46 L 56 62 L 44 62 L 44 46 Z",
    fill: "var(--paper)", stroke: "currentColor", "stroke-width": 1.5,
  }));

  return root;
}
