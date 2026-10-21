"use strict";

// The compass rose. Plan view, north up, clockwise — the same convention the
// arcs use, through the same `bearingPoint`, so the two drawings cannot drift
// apart about which way 090 lies.
//
// Nothing here invents a number. The bearings come from the catalogue, which
// takes them from the bank; the two illustrative directions carry no label at
// all, because the bank gives them no value.
//
// The box is wider than the circle needs. Rim labels sit at radius 49 and the
// widest is "W · 270": centred on a 120-wide box it ran off the left edge,
// which the browser clips without complaining.

const ROSE_NS = "http://www.w3.org/2000/svg";
const ROSE_CX = 70;
const ROSE_CY = 60;
const ROSE_R = 40;

function roseNode(tag, attrs, text) {
  const node = document.createElementNS(ROSE_NS, tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  if (text !== undefined) node.textContent = text;
  return node;
}

// An arc of the given radius from one bearing to the other, clockwise. Used
// for the angle marks, which are open curves rather than filled wedges: a
// filled sector would read as a light's coverage, which is a different idea
// on the same shape.
function roseAnglePath(start, end, radius) {
  const span = ((end - start) % 360 + 360) % 360;
  const [x1, y1] = bearingPoint(start, radius, ROSE_CX, ROSE_CY);
  const [x2, y2] = bearingPoint(end, radius, ROSE_CX, ROSE_CY);
  return `M ${x1} ${y1} A ${radius} ${radius} 0 ${span > 180 ? 1 : 0} 1 ${x2} ${y2}`;
}

function drawRose(rose, size) {
  const root = roseNode("svg", {
    viewBox: "0 0 140 136", width: size, height: size * 0.97,
    role: "img", "aria-label": rose.label,
  });

  root.append(roseNode("circle", {
    cx: ROSE_CX, cy: ROSE_CY, r: ROSE_R,
    fill: "none", stroke: "currentColor", "stroke-opacity": 0.35, "stroke-width": 0.8,
  }));

  // The angles first, so the rays and the hull sit above them.
  rose.angles.forEach((angle, index) => {
    const radius = 15 + index * 9;
    root.append(roseNode("path", {
      d: roseAnglePath(angle.start, angle.end, radius),
      fill: "none", stroke: "var(--magenta)", "stroke-width": 1, "stroke-opacity": 0.85,
    }));
    // The label rides the middle of its own arc, pushed out far enough to
    // clear the curve it names.
    const span = ((angle.end - angle.start) % 360 + 360) % 360;
    const [lx, ly] = bearingPoint(angle.start + span / 2, radius + 6, ROSE_CX, ROSE_CY);
    root.append(roseNode("text", {
      x: lx, y: ly, "font-size": 6.5, fill: "var(--magenta)",
      "text-anchor": "middle", "dominant-baseline": "middle",
    }, angle.label));
  });

  for (const ray of rose.rays) {
    const [ex, ey] = bearingPoint(ray.bearing, ROSE_R, ROSE_CX, ROSE_CY);
    root.append(roseNode("line", {
      x1: ROSE_CX, y1: ROSE_CY, x2: ex, y2: ey,
      stroke: "currentColor", "stroke-opacity": 0.45, "stroke-width": 0.7,
    }));
    const [tx, ty] = bearingPoint(ray.bearing, ROSE_R + 9, ROSE_CX, ROSE_CY);
    root.append(roseNode("text", {
      x: tx, y: ty, "font-size": 6, fill: "currentColor",
      "text-anchor": "middle", "dominant-baseline": "middle",
      "font-family": ray.figure ? "var(--figures)" : "inherit",
    }, ray.label));
  }

  // The line of sight, dashed, to a mark on the horizon.
  if (rose.mark !== null && rose.mark !== undefined) {
    const [mx, my] = bearingPoint(rose.mark, ROSE_R, ROSE_CX, ROSE_CY);
    root.append(roseNode("line", {
      x1: ROSE_CX, y1: ROSE_CY, x2: mx, y2: my,
      stroke: "currentColor", "stroke-width": 0.8, "stroke-dasharray": "2 1.5",
    }));
    root.append(roseNode("circle", { cx: mx, cy: my, r: 2.2, fill: "currentColor" }));
    const [lx, ly] = bearingPoint(rose.mark, ROSE_R + 10, ROSE_CX, ROSE_CY);
    root.append(roseNode("text", {
      x: lx, y: ly, "font-size": 5.5, fill: "currentColor",
      "text-anchor": "middle", "dominant-baseline": "middle",
    }, "reper"));
  }

  // The hull last, pointing along its own axis, so the bow is unmistakably
  // the thing the course is measured to.
  if (rose.bow !== null && rose.bow !== undefined) {
    const [bx, by] = bearingPoint(rose.bow, ROSE_R, ROSE_CX, ROSE_CY);
    root.append(roseNode("line", {
      x1: ROSE_CX, y1: ROSE_CY, x2: bx, y2: by,
      stroke: "currentColor", "stroke-width": 1.2,
    }));
    root.append(roseNode("path", {
      d: "M 0 -7 L 3.5 3 L 0 1.5 L -3.5 3 Z",
      transform: `translate(${ROSE_CX} ${ROSE_CY}) rotate(${rose.bow})`,
      fill: "var(--paper)", stroke: "currentColor", "stroke-width": 1.2,
    }));
    const [lx, ly] = bearingPoint(rose.bow, ROSE_R + 10, ROSE_CX, ROSE_CY);
    root.append(roseNode("text", {
      x: lx, y: ly, "font-size": 5.5, fill: "currentColor",
      "text-anchor": "middle", "dominant-baseline": "middle",
    }, "prova"));
  }

  return root;
}

function roseCard(rose) {
  return el("figure", { class: "rosecard" },
    drawRose(rose, 190),
    el("figcaption", {}, rose.label));
}
