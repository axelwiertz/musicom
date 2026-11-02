# -*- coding: utf-8 -*-
"""BangZilla Wave Theory-style waveform->melody MIDI generator.

Replicable logic from the BangZilla Wave Theory launch (Sound On Sound news
2026-10-30, with Boxed Ear): a MIDI plug-in that "generates melodic lines
based on the shape of an imported waveform".  Load a single-cycle wavetable
(or use one of the 100+ built-ins / import Serum/Vital .wav tables), pick a
key and scale, and the plug-in turns the wave's shape into an evolving
melody that stays locked to key and tempo.  It has four parallel sequencer
lanes, each with its own length and speed, plus note-probability and timing
controls, and a central quantiser that can follow the chords you play.

What is replicated here:

- ``WaveMelodyGenerator``: takes any single-cycle waveform (numpy array;
  built-ins include saw, sine, triangle, square, PWM-ish and an inharmonic
  "gong" table; external tables can be passed directly).  Four parallel
  lanes, each with its own step count (length) and speed multiplier
  (subdivisions of the 16th-note grid).
- Wave-shape -> note mapping: each step maps to a phase position in the
  waveform; the instantaneous wave amplitude (plus its slope, for an
  "energy" reading) is mapped through an octave range onto a scale degree,
  so high crests of the wave become high notes and troughs become low ones.
  ``direction`` lets the scan run forward, backward or bounce.
- Always in key: every note is quantised to the selected key/scale; the
  scale can be fixed or follow a chord progression (each bar's chord picks
  the quantisation set, matching the plug-in's chord-following quantiser).
- Per-lane note probability and timing jitter, per the plug-in's
  "experiment with note probability, timing" controls.
- ``to_midi_events`` returns (pitch, start_frac_of_bar, dur_frac, velocity)
  tuples ready for the musicom engine.

Not replicated: the plug-in GUI, the 100+ preset wavetable library content
(any table can be passed in), and the 16 memory slots / preset capture.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List, Optional, Tuple

# --- scales as semitone intervals from the root ----------------------------
SCALES: Dict[str, List[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "pentatonic": [0, 2, 4, 7, 9],
    "minor_pentatonic": [0, 3, 5, 7, 10],
    "blues": [0, 3, 5, 6, 7, 10],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "chromatic": list(range(12)),
}


def build_wavetable(kind: str = "saw", size: int = 2048) -> np.ndarray:
    """Build a single-cycle wavetable of ``size`` samples.

    Built-ins mirror the sort of shapes Wave Theory ships: saw, sine,
    triangle, square, a pulse-width 25% wave, an asymmetric "distorted" saw
    and an inharmonic gong-like table.  External tables (e.g. read from a
    Serum/Vital .wav) can be passed straight into ``WaveMelodyGenerator``.
    """
    x = np.linspace(0.0, 1.0, size, endpoint=False)
    if kind == "sine":
        return np.sin(2 * np.pi * x)
    if kind == "saw":
        return 2.0 * x - 1.0
    if kind == "triangle":
        return 4.0 * np.abs(x - 0.5) - 1.0
    if kind == "square":
        return np.where(x < 0.5, 1.0, -1.0)
    if kind == "pulse25":
        return np.where(x < 0.25, 1.0, -1.0)
    if kind == "dist_saw":
        s = 2.0 * x - 1.0
        return np.tanh(3.0 * s + 0.6 * s ** 2)
    if kind == "gong":
        # inharmonic partial stack: 1, 2.76, 5.4, 8.9 (bell-like ratios)
        out = np.zeros(size)
        for ratio, amp in ((1.0, 1.0), (2.76, 0.45), (5.4, 0.2), (8.93, 0.1)):
            out += amp * np.sin(2 * np.pi * ratio * x + 0.3)
        return out / np.abs(out).max()
    raise ValueError(f"unknown wavetable kind {kind!r}")


class WaveMelodyGenerator:
    """Turn a waveform's shape into scale-locked melodic lines.

    Four parallel lanes each scan the waveform with their own length and
    speed.  The instantaneous amplitude of the wave at each step's phase
    position is mapped to a pitch in an octave range, then quantised to the
    active scale (fixed or chord-following).  Probability skips notes,
    jitter loosens timing.
    """

    def __init__(self, wavetable: Optional[np.ndarray] = None,
                 kind: str = "saw", root: int = 60, scale: str = "major",
                 octave_range: int = 2, base_octave: int = 3) -> None:
        if wavetable is None:
            wavetable = build_wavetable(kind)
        self.wavetable = np.asarray(wavetable, dtype=float)
        assert self.wavetable.ndim == 1 and len(self.wavetable) > 16
        self.root = root % 12
        self.scale = scale
        self.octave_range = octave_range
        self.base_octave = base_octave
        self.chords: Optional[List[int]] = None   # chord-follow mode: root per bar
        self.probability = 1.0
        self.jitter_ms = 0.0
        self.direction = "forward"   # forward | backward | bounce

    def set_chord_progression(self, chord_roots: List[int]) -> None:
        """Chord-following quantiser: one scale root per bar."""
        self.chords = [r % 12 for r in chord_roots]

    # --- the core wave->note mapping --------------------------------------
    def _wave_to_pitch(self, phase: float, slope: float,
                       degree_energy: float) -> int:
        """Map wave amplitude + slope at ``phase`` to a scale degree pitch.

        The amplitude in -1..1 is mapped onto ``octave_range`` octaves of the
        active scale starting at ``base_octave``; the absolute slope of the
        wave adds an "energy" boost (steeper parts of the wave read higher),
        which makes the melody track both level and motion of the waveform.
        """
        amp = np.clip(self._amp(phase), -1.0, 1.0)
        amp01 = (amp + 1.0) * 0.5
        # energy from slope (0..1), blended 15%
        energy = amp01 + 0.15 * min(1.0, abs(slope))
        intervals = SCALES[self.scale]
        n_deg = len(intervals) * self.octave_range
        idx = int(np.clip(energy * n_deg, 0, n_deg - 1))
        octave = idx // len(intervals)
        deg = idx % len(intervals)
        return 12 * (self.base_octave + octave) + self.root + intervals[deg]

    def _amp(self, phase: float) -> float:
        """Sample the wavetable at normalised phase 0..1 (linear interp)."""
        p = np.mod(phase, 1.0) * (len(self.wavetable) - 1)
        i0 = int(np.floor(p))
        i1 = min(i0 + 1, len(self.wavetable) - 1)
        frac = p - i0
        return (1.0 - frac) * self.wavetable[i0] + frac * self.wavetable[i1]

    def _slope(self, phase: float) -> float:
        """Approximate |dw/dphase| at ``phase`` via central difference."""
        p = np.mod(phase, 1.0) * (len(self.wavetable) - 1)
        i0 = int(np.floor(p))
        i1 = min(i0 + 1, len(self.wavetable) - 1)
        return abs(self.wavetable[i1] - self.wavetable[i0])

    # --- lane scanning -------------------------------------------------------
    def generate(self, bars: int = 8, steps_per_bar: int = 4, seed: int = 0,
                 lane_lengths: Optional[List[int]] = None,
                 lane_speeds: Optional[List[float]] = None) -> List[Tuple[int, float, float, float]]:
        """Generate notes across ``bars``.

        Each lane scans the waveform with its own length (number of steps in
        its loop) and speed (subdivision of the 16th-note grid).  Returns a
        list of ``(pitch, start_frac, dur_frac, velocity)`` where
        ``start_frac``/``dur_frac`` are in units of one bar.
        """
        rng = np.random.default_rng(seed)
        if lane_lengths is None:
            lane_lengths = [32, 16, 8, 4]           # lane 0 fastest, lane 3 slowest
        if lane_speeds is None:
            lane_speeds = [4.0, 2.0, 1.0, 0.5]      # 16ths per lane step
        n_lanes = min(4, len(lane_lengths))
        events: List[Tuple[int, float, float, float]] = []
        bar_ticks = 16                              # 16 sixteenths per bar
        for bar in range(bars):
            for lane in range(n_lanes):
                L = lane_lengths[lane]
                speed = lane_speeds[lane]
                lane_phase0 = rng.random() * len(self.wavetable)
                for step in range(L):
                    if rng.random() > self.probability:
                        continue
                    # phase position along the wave for this step
                    if self.direction == "forward":
                        phase = (lane_phase0 + step / L) % 1.0
                    elif self.direction == "backward":
                        phase = (lane_phase0 - step / L) % 1.0
                    else:  # bounce
                        tri = 1.0 - abs(2.0 * (step / L) - 1.0)
                        phase = (lane_phase0 + tri) % 1.0
                    start_frac = (bar + (step * speed) / bar_ticks) / bars
                    jitter = rng.normal(0.0, self.jitter_ms / 1000.0)
                    start_frac = max(0.0, min(1.0, start_frac + jitter / bars))
                    # chord-following quantiser: the root in force is the one
                    # of the bar this note ACTUALLY lands in
                    land_bar = int(np.floor(start_frac * bars))
                    root = self.chords[land_bar % len(self.chords)] if self.chords \
                        else self.root
                    prev_root, self.root = self.root, root
                    try:
                        pitch = self._wave_to_pitch(phase, self._slope(phase), 0.0)
                    finally:
                        self.root = prev_root
                    vel = 0.5 + 0.5 * abs(self._amp(phase))
                    dur = min(0.9, 0.25 * speed / bars)
                    events.append((pitch, start_frac, dur, vel))
        events.sort(key=lambda e: e[1])
        return events

    def to_midi(self, events: List[Tuple[int, float, float, float]],
                bpm: float = 120.0, bars: int = 8) -> List[Tuple[int, int, int, int]]:
        """Convert generated events to absolute-tick MIDI note tuples.

        Returns ``(pitch, start_tick, dur_ticks, velocity)`` at the musicom
        resolution (ticks_per_beat=480, 4 beats per bar -> 1920 ticks/bar).
        """
        bar_ticks = 1920
        out = []
        for pitch, start_frac, dur_frac, vel in events:
            start = int(round(start_frac * bars * bar_ticks))
            dur = max(1, int(round(dur_frac * bars * bar_ticks)))
            out.append((int(pitch), start, dur, int(np.clip(vel * 127, 1, 127))))
        return out


def demo() -> None:
    """Generate a melody from a gong wavetable and print the note stream."""
    gen = WaveMelodyGenerator(kind="gong", root=0, scale="minor",
                              octave_range=2, base_octave=3)
    gen.probability = 0.9
    gen.jitter_ms = 4.0
    gen.set_chord_progression([0, 3, 5, 4])     # i - III - v - iv in A minor
    events = gen.generate(bars=8, seed=11)
    midi = gen.to_midi(events, bpm=100, bars=8)
    pitches = sorted({e[0] for e in midi})
    # chord-following: each bar has its own root, so verify per-bar in-key
    # against the UNROUNDED event fractions (rounded ticks can straddle a
    # bar boundary by one tick)
    roots = [0, 3, 5, 4] * 2
    off_scale = []
    for pitch, start_frac, _, _ in events:
        land_bar = int(np.floor(start_frac * 8))
        root = roots[land_bar % len(roots)]
        if (pitch - root) % 12 not in SCALES["minor"]:
            off_scale.append((pitch, land_bar))
    print(f"wave_melody demo: {len(midi)} MIDI notes over 8 bars")
    print(f"  pitch range {min(pitches)}..{max(pitches)}, "
          f"{len(pitches)} distinct pitches")
    print(f"  off-scale notes: {off_scale} (must be empty -> always in key)")
    print(f"  first 5 MIDI: {midi[:5]}")
    assert len(midi) > 0
    assert off_scale == [], "all notes must be quantised to the per-bar scale"
    assert all(d > 0 for _, _, d, _ in midi)
    print("demo OK")


if __name__ == "__main__":
    demo()
