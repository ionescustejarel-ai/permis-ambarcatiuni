"use strict";

// Web Audio synthesis. No files: the page stays a single document that works
// with the network off.
//
// The frequencies below are presentation choices, not regulation. COLREG
// Annex III gives a whistle band for small vessels; a tone inside it sounds
// like a ship rather than a test tone, which is the whole point of hearing
// the signal at all. Nothing in the bank states a pitch.
const WHISTLE_HZ = 400;
const BELL_HZ = 800;
const BELL_PARTIAL = 2.76;  // an inharmonic partial: what makes a bell a bell

const Audio2 = {
  context: null,
  playing: null,
  // Counts presses, so a scheduling deferred by resume() can tell whether it
  // is still the one the candidate is waiting for. Without it, two presses
  // while the context is still starting both schedule, and the first one's
  // nodes go untracked — playing over the second, unstoppable.
  generation: 0,

  // Created on the first press, never on load: browsers refuse audio without
  // a user gesture, and the button is that gesture.
  ensure() {
    if (this.context === null) this.context = new AudioContext();
    return this.context;
  },

  stop() {
    if (this.playing === null) return;
    for (const node of this.playing) {
      try { node.stop(); } catch (error) { /* already finished */ }
    }
    this.playing = null;
  },

  play(signal, timing) {
    // One signal at a time: two overlapping signals sound like neither.
    this.stop();
    const context = this.ensure();
    const token = (this.generation += 1);
    const start = () => {
      if (token !== this.generation) return;  // a later press took over
      this.playing = schedule(context, signal, timing, context.currentTime);
    };

    // A suspended context has a clock that is not running. Scheduling against
    // it and hoping resume() lands in time is how the first press comes out
    // silent — and resume() returns a promise, so ignoring it also turns any
    // refusal into an unhandled rejection nobody sees.
    if (context.state === "suspended") {
      context.resume().then(start, () => { this.playing = null; });
    } else {
      start();
    }
    return signalDuration(signalTimeline(signal, timing));
  },

  // Renders the same schedule offline, so a test can count the bursts and
  // measure them instead of trusting that it sounded right.
  render(signal, timing, OfflineContext) {
    const seconds = signalDuration(signalTimeline(signal, timing)) / 1000 + 0.5;
    const context = new OfflineContext(1, Math.ceil(44100 * seconds), 44100);
    schedule(context, signal, timing, 0);
    return context.startRendering();
  },
};

function schedule(context, signal, timing, startAt) {
  const nodes = [];
  let at = startAt;
  for (const step of signalTimeline(signal, timing)) {
    const seconds = step.ms / 1000;
    if (step.kind !== null) {
      nodes.push(...(signal.instrument === "bell"
        ? bell(context, at, seconds)
        : whistle(context, at, seconds)));
    }
    at += seconds;
  }
  return nodes;
}

function whistle(context, at, seconds) {
  const oscillator = context.createOscillator();
  oscillator.type = "square";
  oscillator.frequency.value = WHISTLE_HZ;

  // A square wave raw is harsh and thin; rolling the top off leaves the body
  // of a ship's whistle.
  const filter = context.createBiquadFilter();
  filter.type = "lowpass";
  filter.frequency.value = 1200;

  const gain = context.createGain();
  gain.gain.setValueAtTime(0, at);
  gain.gain.linearRampToValueAtTime(0.28, at + 0.02);
  gain.gain.setValueAtTime(0.28, at + seconds - 0.03);
  gain.gain.linearRampToValueAtTime(0, at + seconds);

  oscillator.connect(filter).connect(gain).connect(context.destination);
  oscillator.start(at);
  oscillator.stop(at + seconds);
  return [oscillator];
}

function bell(context, at, seconds) {
  const nodes = [];
  for (const [ratio, level] of [[1, 0.3], [BELL_PARTIAL, 0.12]]) {
    const oscillator = context.createOscillator();
    oscillator.type = "sine";
    oscillator.frequency.value = BELL_HZ * ratio;

    const gain = context.createGain();
    gain.gain.setValueAtTime(level, at);
    // Exponential, not linear: a struck bell decays that way, and
    // exponentialRamp cannot reach zero, so it lands just above it.
    gain.gain.exponentialRampToValueAtTime(0.0001, at + seconds);

    oscillator.connect(gain).connect(context.destination);
    oscillator.start(at);
    oscillator.stop(at + seconds);
    nodes.push(oscillator);
  }
  return nodes;
}
