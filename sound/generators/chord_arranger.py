"""Chord-driven three-track generative arranger — Midicake UNA style.

Replicable logic from the Synthtopia item "Midicake UNA Combines Generative
Sequencing With Hands-On MIDI Control" (2026-10-19): UNA is a hardware MIDI
composer that turns incoming keyboard chords into an evolving three-part
arrangement — a chord/rhythm track, an arpeggiated melody track and a bass
track that follows the harmony. Pattern tools include ratchets, trills,
swing, probability, accents and Euclidean-style muting; an "8 + 16"
modulation system (8 macro knobs + 16-step modulation lanes) animates the
parameters so sequences evolve on their own.

What is replicated here (pure MIDI-event level, no audio DSP):
- ``ChordDrivenArranger``: chord progression in -> three coordinated event
  tracks (chord/rhythm, melody, bass) on a step grid (16 steps/bar,
  bar = 1920 ticks at 480 tpq / 4/4 — the Musicom convention).
- Chord track: block / strum / euclidean / drone rhythmic patterns over the
  chord tones; Euclidean-style muting gates the hits.
- Melody track: arpeggiator modes (up / down / updown / random) over chord
  tones + per-step probability, octave range, trills and ratchets.
- Bass track: root/fifth patterns that follow the harmony.
- Pattern tools: ratchet (step subdivision into 2..4 hits), trill (rapid
  alternation with a neighbour chord tone), swing (even-step delay),
  probability (per-step drop), accent (velocity accent pattern),
  euclidean muting (step gating mask).
- Modulation bus: 8 named macros (density, probability, swing, accent,
  ratchet, octave, gate, spread) + 16-step lanes for probability, velocity,
  gate and octave; everything seeded and deterministic.

Not replicated: the hardware box, CONNECT app, MIDI clock I/O, dual TRS MIDI
outs and patch chains (device/UI concerns). Events render to a standard
MIDI file through ``MicrotonalExporter`` so the nightly production pipeline
can consume them directly.

Usage:
    from sound.generators.chord_arranger import ChordDrivenArranger

    a = ChordDrivenArranger(bpm=120, bars=4, seed=7)
    events = a.generate([(60, "maj7"), (57, "min7"), (53, "maj7"), (55, "dom7")])
    # events: list of {pitch, start_tick, duration_ticks, vel, channel, track}
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

__all__ = ["ChordDrivenArranger", "euclidean_mask", "QUALITIES", "MACROS"]

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------

TPB = 480          # ticks per beat (Musicom standard)
BEATS_PER_BAR = 4
BAR_TICKS = TPB * BEATS_PER_BAR          # 1920
STEPS_PER_BAR = 16
STEP_TICKS = BAR_TICKS // STEPS_PER_BAR  # 120

CHORD_CHANNEL = 0
MELODY_CHANNEL = 1
BASS_CHANNEL = 2

QUALITIES: Dict[str, List[int]] = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "dom7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim": [0, 3, 6],
    "dim7": [0, 3, 6, 9],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "5": [0, 7],
}

MACROS: List[str] = [
    "density",   # 0..1  — how many hits the euclidean/rhythm patterns get
    "probability",  # 0..1 — per-step chance to play (melody/bass)
    "swing",     # 0..1  — delay of even steps
    "accent",    # 0..1  — strength of accented hits
    "ratchet",   # 0..1  — maps to 1..4 subdivisions
    "octave",    # -2..2 — transpose of melody/bass
    "gate",      # 0..1  — note duration fraction of the step
    "spread",    # 0..1  — chord voicing inversion (root position -> spread up)
]


def euclidean_mask(steps: int, pulses: int, rotation: int = 0) -> List[int]:
    """Bjorklund-style euclidean rhythm: ``pulses`` hits over ``steps``.

    Returns a list of 0/1 of length ``steps`` (1 = hit), rotated by
    ``rotation`` positions. This is the "Euclidean-style muting / rhythm"
    tool shared by all three tracks.
    """
    if pulses <= 0:
        return [0] * steps
    if pulses >= steps:
        return [1] * steps
    pattern = []
    counts = [0] * pulses
    remainders = [pulses] * pulses
    level = steps
    divisor = pulses
    while True:
        quot, rem = divmod(level, divisor)
        for i in range(divisor):
            counts[i] += quot
            remainders[i] = rem
        if rem == 0:
            break
        level, divisor = divisor, rem
    # build pattern by interleaving
    idx = 0
    for i in range(pulses):
        for _ in range(counts[i]):
            pattern.append(1)
            idx += 1
        if i < len(remainders) and remainders[i] > 0:
            pattern.append(0)
            idx += 1
    pattern = pattern[:steps]
    while len(pattern) < steps:
        pattern.append(0)
    if rotation:
        pattern = pattern[rotation:] + pattern[:rotation]
    return pattern


def _chord_tones(root: int, quality: str, lo: int = 48, hi: int = 84) -> List[int]:
    """Pitch set for ``root``+``quality`` inside [lo, hi] (midi)."""
    intervals = QUALITIES.get(quality, QUALITIES["maj"])
    tones = []
    for oct_ in range(-2, 4):
        for iv in intervals:
            p = root + 12 * oct_ + iv
            if lo <= p <= hi:
                tones.append(p)
    return sorted(set(tones))


def _neighbor(tone: int, pool: List[int], up: bool) -> int:
    """Next pitch above/below ``tone`` inside ``pool`` (for trills)."""
    if up:
        cands = [p for p in pool if p > tone]
        return cands[0] if cands else tone
    cands = [p for p in pool if p < tone]
    return cands[-1] if cands else tone


class ChordDrivenArranger:
    """Three-track generative arranger driven by a chord progression.

    Args:
        bpm: tempo for tick math (grid only; no audio rendered here).
        bars: number of bars to arrange (chords cycle if shorter).
        steps_per_bar: step resolution of the grid.
        seed: RNG seed — everything is deterministic per seed.
    """

    def __init__(self, bpm: int = 120, bars: int = 8,
                 steps_per_bar: int = STEPS_PER_BAR, seed: int = 0):
        self.bpm = int(bpm)
        self.bars = int(bars)
        self.steps_per_bar = int(steps_per_bar)
        self.step_ticks = BAR_TICKS // self.steps_per_bar
        self.seed = int(seed)

    # ------------------------------------------------------------------
    # pattern tools (all operate on the 16-step grid of one bar)
    # ------------------------------------------------------------------
    def _swing(self, start: int, dur: int, swing: float) -> int:
        """Delay an even step by ``swing`` * step duration."""
        if swing <= 0:
            return start
        step = (start - (start % self.step_ticks)) // self.step_ticks
        if step % 2 == 1:
            return start + int(self.step_ticks * min(swing, 1.0) * 0.5)
        return start

    def _ratchet_hits(self, n: int) -> List[int]:
        """Split one step into ``n`` hit positions (ticks inside the step)."""
        if n <= 1:
            return [0]
        return [int(round(self.step_ticks * i / n)) for i in range(n)]

    # ------------------------------------------------------------------
    # track builders
    # ------------------------------------------------------------------
    def _chord_track(self, tones: List[int], rng: random.Random,
                     macros: Dict[str, float], lanes: Dict[str, List[float]],
                     bar_start: int) -> List[dict]:
        events: List[dict] = []
        steps = self.steps_per_bar
        density = macros["density"]
        pulses = max(1, int(round(steps * (0.25 + 0.75 * density))))
        mask = euclidean_mask(steps, pulses, rotation=rng.randint(0, 3))
        kind = rng.choice(["block", "strum", "euclid", "drone"])
        gate = macros["gate"]
        spread = macros["spread"]

        if kind == "block":
            dur = int(self.step_ticks * (2 + 10 * gate))
            t = bar_start
            for p in tones:
                vel = 70 + int(20 * macros["accent"])
                events.append({"pitch": p, "start_tick": t, "duration_ticks": dur,
                               "vel": vel, "channel": CHORD_CHANNEL, "track": "chord"})
        elif kind == "strum":
            for i, p in enumerate(tones):
                t = bar_start + i * self.step_ticks
                dur = int(self.step_ticks * (2 + 8 * gate))
                vel = 60 + int(25 * i / max(1, len(tones) - 1) * (0.5 + macros["accent"]))
                events.append({"pitch": p, "start_tick": t, "duration_ticks": dur,
                               "vel": int(vel), "channel": CHORD_CHANNEL, "track": "chord"})
        elif kind == "euclid":
            base = tones[:2] if rng.random() < 0.5 else tones
            for s in range(steps):
                if not mask[s]:
                    continue
                t = bar_start + s * self.step_ticks
                for p in base:
                    dur = int(self.step_ticks * (0.5 + gate))
                    events.append({"pitch": p, "start_tick": t, "duration_ticks": dur,
                                   "vel": 72 + int(18 * macros["accent"]),
                                   "channel": CHORD_CHANNEL, "track": "chord"})
        else:  # drone
            root = tones[0]
            fifth = root + 7 if root + 7 in tones else (tones[0] if tones else root)
            for p, mult in ((root, 1.0), (fifth, 0.5)):
                dur = int(BAR_TICKS * mult * (0.5 + 0.5 * gate))
                events.append({"pitch": p, "start_tick": bar_start,
                               "duration_ticks": dur, "vel": 64,
                               "channel": CHORD_CHANNEL, "track": "chord"})

        # euclidean-style muting: gate all chord events with the mask
        if kind in ("block", "strum", "drone"):
            step_of = lambda t: (t - bar_start) // self.step_ticks
            kept = []
            for ev in events:
                s = step_of(ev["start_tick"])
                if mask[s % steps]:
                    kept.append(ev)
            events = kept

        # voicing spread: invert the chord upward (alternate inversion)
        if spread > 0.05 and len(events) > 1:
            ps = sorted({e["pitch"] for e in events})
            if len(ps) >= 3:
                inv = int(round(spread * 12))
                target = ps[0] + 12 + inv
                # lift the top note(s) an octave toward the target voicing
                for ev in events:
                    if ev["pitch"] == max(ps) and rng.random() < spread:
                        ev["pitch"] += 12
        return events

    def _melody_track(self, tones: List[int], rng: random.Random,
                      macros: Dict[str, float], lanes: Dict[str, List[float]],
                      bar_start: int) -> List[dict]:
        events: List[dict] = []
        steps = self.steps_per_bar
        mode = rng.choice(["up", "down", "updown", "random"])
        base_prob = macros["probability"]
        ratchet = int(round(macros["ratchet"] * 3)) + 1   # 1..4
        oct_ = int(round(macros["octave"]))
        swing = macros["swing"]

        arp: List[int] = []
        if mode == "up":
            arp = tones
        elif mode == "down":
            arp = list(reversed(tones))
        elif mode == "updown":
            arp = tones + list(reversed(tones))[1:-1]
        else:
            arp = [rng.choice(tones) for _ in range(steps)]
        if not arp:
            return events

        for s in range(steps):
            prob = base_prob * (0.4 + 0.6 * lanes["probability"][s])
            if rng.random() > prob:
                continue
            t = bar_start + s * self.step_ticks
            t = self._swing(t, self.step_ticks, swing)
            base = arp[s % len(arp)] + 12 * oct_
            # trill: alternate with a neighbour tone at ratchet rate
            if macros["accent"] > 0.6 and ratchet >= 3 and rng.random() < 0.35:
                nb = _neighbor(base, [p + 12 * oct_ for p in tones], up=True)
                hits = self._ratchet_hits(2)
                for off in hits:
                    p = base if off == 0 else nb
                    dur = int(self.step_ticks * (0.5 + 0.5 * lanes["gate"][s]) / 2)
                    vel = 70 + int(15 * lanes["velocity"][s])
                    events.append({"pitch": p, "start_tick": t + off,
                                   "duration_ticks": max(dur, 1), "vel": vel,
                                   "channel": MELODY_CHANNEL, "track": "melody"})
                continue
            # ratchet: subdivide the step
            hits = self._ratchet_hits(ratchet if rng.random() < 0.25 else 1)
            for off in hits:
                p = base + (12 if rng.random() < 0.15 else 0)  # occasional octave leap
                dur = int(self.step_ticks * (0.5 + 0.5 * lanes["gate"][s]) / len(hits))
                vel = int(64 + 26 * lanes["velocity"][s] * (1 + macros["accent"]))
                events.append({"pitch": p, "start_tick": t + off,
                               "duration_ticks": max(dur, 1), "vel": min(vel, 120),
                               "channel": MELODY_CHANNEL, "track": "melody"})
        return events

    def _bass_track(self, root: int, rng: random.Random,
                    macros: Dict[str, float], lanes: Dict[str, List[float]],
                    bar_start: int) -> List[dict]:
        events: List[dict] = []
        steps = self.steps_per_bar
        pulses = max(2, int(round(steps * (0.25 + 0.75 * macros["density"]))))
        mask = euclidean_mask(steps, pulses, rotation=rng.randint(0, 2))
        oct_ = int(round(macros["octave"]))
        root_p = root - 12 + 12 * oct_  # bass sits an octave down
        for s in range(steps):
            if not mask[s]:
                continue
            if rng.random() > macros["probability"] * (0.5 + 0.5 * lanes["probability"][s]):
                continue
            t = bar_start + s * self.step_ticks
            t = self._swing(t, self.step_ticks, macros["swing"])
            p = root_p
            # occasional fifth walk on off-beats
            if s % 4 == 2 and rng.random() < 0.4:
                p = root_p + 7
            dur = int(self.step_ticks * (1.2 + 1.3 * lanes["gate"][s]))
            vel = int(70 + 20 * lanes["velocity"][s] * (0.5 + macros["accent"]))
            events.append({"pitch": p, "start_tick": t, "duration_ticks": dur,
                           "vel": min(vel, 115), "channel": BASS_CHANNEL, "track": "bass"})
        return events

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def generate(self, chords: List[Tuple[int, str]],
                 macros: Optional[Dict[str, float]] = None) -> List[dict]:
        """Generate a three-track arrangement from ``chords``.

        Args:
            chords: list of ``(root_midi, quality)``, e.g. ``(60, "maj7")``.
                Bars beyond the list cycle back through it.
            macros: optional overrides for the 8 macro knobs (values 0..1,
                ``octave`` allowed -2..2). Defaults are mid-range seeded.

        Returns:
            List of note dicts ``{pitch, start_tick, duration_ticks, vel,
            channel, track}`` sorted by time. Chord=ch0, melody=ch1,
            bass=ch2 (two MIDI outs on UNA, three musical tracks here).
        """
        if not chords:
            raise ValueError("chords must be a non-empty list of (root, quality)")
        rng = random.Random(self.seed)
        defaults = {
            "density": rng.uniform(0.4, 0.8),
            "probability": rng.uniform(0.55, 0.85),
            "swing": rng.uniform(0.0, 0.4),
            "accent": rng.uniform(0.2, 0.7),
            "ratchet": rng.uniform(0.1, 0.6),
            "octave": rng.uniform(0.0, 1.0),
            "gate": rng.uniform(0.4, 0.8),
            "spread": rng.uniform(0.0, 0.6),
        }
        if macros:
            defaults.update(macros)
        macros = defaults

        # 16-step modulation lanes per target (the "+16" of the 8+16 system)
        lanes = {k: [rng.uniform(0.3, 1.0) for _ in range(self.steps_per_bar)]
                 for k in ("probability", "velocity", "gate", "octave")}

        events: List[dict] = []
        for bar in range(self.bars):
            root, quality = chords[bar % len(chords)]
            tones = _chord_tones(root, quality, lo=48, hi=84)
            if len(tones) < 2:
                tones = [root, root + 4, root + 7]
            bar_start = bar * BAR_TICKS
            events += self._chord_track(tones, rng, macros, lanes, bar_start)
            events += self._melody_track(tones, rng, macros, lanes, bar_start)
            events += self._bass_track(root, rng, macros, lanes, bar_start)

        events.sort(key=lambda e: (e["start_tick"], e["channel"]))
        return events

    # ------------------------------------------------------------------
    def to_midi(self, events: List[dict], path: str) -> str:
        """Write events to a standard MIDI file via MicrotonalExporter."""
        from sound.utils.midi import MicrotonalExporter
        MicrotonalExporter(ticks_per_beat=TPB).build_midi_with_pitch_bends(
            events, path)
        return path


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: C-Am-F-G progression, 4 bars -> 3 tracks + MIDI file."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    arr = ChordDrivenArranger(bpm=120, bars=4, seed=11)
    chords = [(60, "maj7"), (57, "min7"), (53, "maj7"), (55, "dom7")]
    events = arr.generate(chords)
    by_track = {}
    for ev in events:
        by_track.setdefault(ev["track"], []).append(ev)
    mid = os.path.join(out_dir, "una_arrangement.mid")
    arr.to_midi(events, mid)
    assert os.path.getsize(mid) > 40, "empty/corrupt MIDI"
    assert events, "no events generated"
    for t in ("chord", "melody", "bass"):
        assert by_track.get(t), f"track {t} empty"
    summary = {t: len(v) for t, v in by_track.items()}
    summary["midi_bytes"] = os.path.getsize(mid)
    summary["total_events"] = len(events)
    # sample events for the report
    summary["sample"] = events[0]
    return summary


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2, default=str))
