"use strict";

// Inline SVG, built node by node. No files: the page stays a single document
// that works with the network off.
//
// Every colour here is a plain name from the catalogue, resolved to a hex
// value once. The bank names colours, not shades; these are chosen to read on
// both the light and the dark background and are a presentation choice.
const PAINT = {
  black: "#1A1A1A",
  yellow: "#E8C21A",
  green: "#1E7A4C",
  red: "#C0392B",
  white: "#F2F2F2",
  blue: "#2B6CB0",
};

const SVG_NS = "http://www.w3.org/2000/svg";

function svg(tag, attrs) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  return node;
}

// Each shape returns the outline the bands are clipped to, in a 100x100 box.
const OUTLINES = {
  pillar: () => svg("rect", { x: 35, y: 10, width: 30, height: 80 }),
  cylinder: () => svg("rect", { x: 30, y: 20, width: 40, height: 60 }),
  "cone-up": () => svg("polygon", { points: "50,15 75,85 25,85" }),
  "cone-down": () => svg("polygon", { points: "25,15 75,15 50,85" }),
  sphere: () => svg("circle", { cx: 50, cy: 50, r: 32 }),
  "two-spheres": () => svg("path", {
    d: "M 50 12 a 17 17 0 1 1 0 34 a 17 17 0 1 1 0 -34 "
     + "M 50 54 a 17 17 0 1 1 0 34 a 17 17 0 1 1 0 -34",
  }),
  pennant: () => svg("polygon", { points: "20,20 85,50 20,80" }),
};

// Inner marks, keyed the same way as OUTLINES. Only one exists today, but the
// catalogue names its shape, and a renderer that ignores the name while the
// schema advertises it is a schema that lies: a second device of another shape
// would come out a rhombus, with nothing to flag it.
const DEVICE_OUTLINES = {
  rhombus: () => svg("polygon", { points: "40,50 50,36 60,50 50,64" }),
};

function drawFigure(figure, size) {
  const root = svg("svg", {
    viewBox: "0 0 100 100", width: size, height: size,
    role: "img", "aria-label": figure.label,
  });

  const outline = OUTLINES[figure.body.shape];
  if (outline === undefined) throw new Error(`formă necunoscută: ${figure.body.shape}`);

  // The bands are drawn as full-width rectangles and clipped to the outline,
  // so one band rule serves every shape: a sphere's stripes curve with it and
  // a cone's narrow towards the point, with no per-shape geometry.
  // Unique per call, not per figure: the same mark is drawn in the panel and
  // again beside a question, and two elements sharing an id is invalid markup
  // whose url(#…) resolves to whichever came first.
  drawFigure.seq = (drawFigure.seq || 0) + 1;
  const clipId = `clip-${figure.id}-${drawFigure.seq}`;
  const clip = svg("clipPath", { id: clipId });
  clip.append(outline());
  root.append(clip);

  const group = svg("g", { "clip-path": `url(#${clipId})` });
  for (const band of figureBands(figure)) {
    group.append(svg("rect", {
      x: 0, y: band.top * 100, width: 100, height: band.height * 100,
      fill: PAINT[band.colour] || band.colour,
    }));
  }
  root.append(group);

  // The outline again, unfilled, so the shape reads against a background of
  // its own colour — a white pennant on paper is otherwise invisible.
  const edge = outline();
  edge.setAttribute("fill", "none");
  edge.setAttribute("stroke", figure.body.border ? PAINT[figure.body.border] : "currentColor");
  edge.setAttribute("stroke-width", figure.body.border ? 4 : 1.5);
  root.append(edge);

  // A mark set in the middle of another, with its own frame. The supervision
  // pennant is the only one: the source frames the *rhombus* in blue, so
  // painting the blue around the flag instead — which is what happened before
  // this existed — draws a mark the regulation does not describe.
  const device = figure.body.device;
  if (device !== null && device !== undefined) {
    const shape = DEVICE_OUTLINES[device.shape];
    if (shape === undefined) throw new Error(`însemn necunoscut: ${device.shape}`);
    const inner = shape();
    inner.setAttribute("fill", PAINT[device.fill] || device.fill);
    if (device.border) {
      inner.setAttribute("stroke", PAINT[device.border] || device.border);
      inner.setAttribute("stroke-width", 3);
    }
    root.append(inner);
  }

  if (figure.light !== null && figure.light !== undefined) {
    const lamp = svg("circle", { cx: 50, cy: 6, r: 5, fill: PAINT[figure.light.colour] });
    lamp.setAttribute("class", "lamp");
    root.append(lamp);
  }
  return root;
}
