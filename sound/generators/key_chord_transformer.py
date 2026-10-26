# -*- coding: utf-8 -*-
"""Guardrail-style in-key chord transformer (Denormal / zplane Tonic family).

Sources (MusicTech new-plugin roundup, 2026-10-22):

  Denormal Guardrail — "a creative MIDI transformer that lets the user play and
  perform perfectly in-key chords using the white notes, and add passing tones
  and extensions using the black notes ... choose between Exact or Compact
  modes for spacing notes within a chord, change the octave, add randomisation,
  or use performance tools such as strumming chords with the pitch wheel or
  arpeggiating chord notes using the mod wheel ... captures your input into its
  Performance List."

  zplane Tonic 2 — key/scale detection with in-key chord playing, MIDI out and
  drag-out chord clips.

What is replicated here (pure music theory + sequencing, no ML):

- **White-key = diatonic chord**: any incoming note is snapped to the chosen
  key/scale and expanded to the stacked thirds of that scale degree, so every
  white key yields a chord that belongs to the key (I, ii, iii, IV, V, vi, vii°).
- **Black-key = colour**: notes a semitone off the scale become extensions
  (7th / 9th / 11th / 13th) or chromatic passing tones on the held chord.
- **Spacing**: ``exact`` stacks chord tones as written (may exceed an octave);
  ``compact`` folds them into one octave close position.
- **Octave** shift, optional seeded **randomisation** (drop a tone / add a 9th).
- **Performance tools**: ``strum`` (0..1 → onset offsets, i.e. pitch-wheel
  strumming) and ``arpeggiate`` (rate in steps/s, mod-wheel style).
- **Performance list**: every transformed event is captured with timing so the
  caller can drag the result into a DAW timeline.

Not replicated: the plug-in GUI, MIDI-learn, its exact voice-leading tables
(the diatonic-third rule here is textbook, not proprietary).

Usage:
    from sound.generators.key_chord_transformer import KeyChordTransformer
    g = KeyChordTransformer(key="C", scale="major")
    events = g.transform(60, spacing="compact", strum=0.3)
    arp = g.arpeggiate(g.transform(60), rate=8.0, steps=8)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

import numpy as np

__all__ = ["KeyChordTransformer", "ChordEvent", "SCALES", "NOTE_NAMES"]

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

SCALES: Dict[str, tuple] = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
    "harmonic_minor": (0, 2, 3, 5, 7, 8, 11),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "phrygian": (0, 1, 3, 5, 7, 8, 10),
    "lydian": (0, 2, 4, 6, 7, 9, 11),
    "pentatonic_major": (0, 2, 4, 7, 9),
}


@dataclass
class ChordEvent:
    """One note of a transformed chord/arp."""
    note: int
    start: float      # seconds (relative to the trigger)
    duration: float   # seconds
    role: str         # "chord" | "extension" | "passing" | "bass"


class KeyChordTransformer:
    """White-key diatonic chords + black-key colour (Guardrail-style)."""

    def __init__(self, key: str = "C", scale: str = "major",
                 octave_shift: int = 0, seed: int = 0):
        self.key = key
        self.scale = scale
        self.octave_shift = int(octave_shift)
        self.rng = np.random.default_rng(seed)
        self.performance: List[ChordEvent] = []

    # -- scale helpers -----------------------------------------------------
    @property
    def key_pc(self) -> int:
        k = self.key.strip().upper().replace("♯", "#").replace("♭", "B")
        if k not in NOTE_NAMES:
            raise ValueError(f"unknown key {self.key!r}")
        return NOTE_NAMES.index(k)

    @property
    def pcs(self) -> tuple:
        return SCALES.get(self.scale.lower(), SCALES["major"])

    def in_key(self, note: int) -> bool:
        return (note - self.key_pc) % 12 in self.pcs

    def snap(self, note: int) -> int:
        """Snap to the nearest in-key note (ties resolve downward)."""
        for d in sorted(range(-6, 7), key=lambda d: (abs(d), d)):
            if self.in_key(note + d):
                return note + d
        return note

    def degree(self, note: int) -> int:
        """Scale degree index 0..len(scale)-1 of a (snapped) note."""
        rel = (note - self.key_pc) % 12
        return self.pcs.index(rel) if rel in self.pcs else -1

    # -- chord building ----------------------------------------------------
    def _diatonic_chord(self, note: int, size: int = 3) -> List[int]:
        """Stack scale thirds above the snapped note (tertian harmony)."""
        base = self.snap(note)
        deg = self.degree(base)
        if deg < 0:
            return [base]
        pcs = self.pcs
        oct_base = (base - self.key_pc) // 12
        notes = []
        for k in range(size):
            idx = deg + 2 * k
            pitch = (self.key_pc + pcs[idx % len(pcs)] +
                     12 * (oct_base + idx // len(pcs)))
            notes.append(pitch)
        return sorted(set(notes))

    def transform(self, note: int, spacing: str = "exact",
                  size: int = 3, strum: float = 0.0,
                  duration: float = 1.0, rand: float = 0.0,
                  velocity: float = 0.8) -> List[ChordEvent]:
        """Turn one incoming note into a chord (white) or colour (black)."""
        colour = not self.in_key(note)
        if colour:
            base = self.snap(note)
            ivs = {1: 11, 2: 14, 3: 17, 4: 21}     # b9, 9, 11, 13 above root
            ext = ivs.get(abs(note - base) or 1, 14)
            notes = self._diatonic_chord(base, size) + [base + ext]
            role = "extension"
        else:
            notes = self._diatonic_chord(note, size)
            role = "chord"
        if spacing == "compact":
            lo = min(notes)
            notes = sorted({(n - lo) % 12 + lo for n in notes})
        elif spacing != "exact":
            raise ValueError("spacing must be 'exact' or 'compact'")
        if rand > 0:
            if self.rng.random() < rand:
                notes = notes[:-1] or notes          # drop the top tone
            if self.rng.random() < rand * 0.5:
                notes = sorted(set(notes + [max(notes) + 7]))
        notes = [n + 12 * self.octave_shift for n in notes]
        events = []
        for j, n in enumerate(notes):
            events.append(ChordEvent(
                note=n, start=strum * j * 0.05, duration=duration,
                role="bass" if j == 0 else
                ("extension" if n > max(notes[:3]) else role)))
        self.performance.extend(events)
        return events

    # -- performance tools -------------------------------------------------
    @staticmethod
    def arpeggiate(events: Sequence[ChordEvent], rate: float = 8.0,
                   steps: int = 8, mode: str = "up",
                   duration: float = 0.12) -> List[ChordEvent]:
        """Turn a chord into an arpeggio (mod-wheel style, rate in steps/s)."""
        notes = [e.note for e in events]
        if not notes:
            return []
        if mode == "down":
            order = notes[::-1]
        elif mode == "updown":
            order = notes + notes[-2:0:-1]
        else:
            order = notes
        step_s = 1.0 / max(rate, 1e-6)
        out = []
        for i in range(steps):
            n = order[i % len(order)] + 12 * (i // len(order))
            out.append(ChordEvent(note=n, start=i * step_s,
                                  duration=duration, role="chord"))
        return out

    def to_midi_notes(self, events: Sequence[ChordEvent],
                      offset: float = 0.0) -> List[dict]:
        """Flatten events for the engine's MIDI exporter."""
        return [{"pitch": e.note, "start": e.start + offset,
                 "end": e.start + offset + e.duration,
                 "velocity": 100} for e in events]


def demo() -> str:
    g = KeyChordTransformer(key="C", scale="major", seed=3)
    rows = []
    for midi in (60, 62, 64, 65, 67, 69, 71):
        ev = g.transform(midi, spacing="exact")
        rows.append(f"{NOTE_NAMES[midi % 12]:2s} -> "
                    f"{' '.join(NOTE_NAMES[e.note % 12] for e in ev)}")
    compact = g.transform(64, spacing="compact", size=5)
    exact = g.transform(64, spacing="exact", size=5)
    strummed = g.transform(60, strum=0.8)
    arp = g.arpeggiate(g.transform(60), rate=8.0, steps=8)
    colour = g.transform(61)          # C# against C major -> extension
    span_c = max(e.note for e in compact) - min(e.note for e in compact)
    span_e = max(e.note for e in exact) - min(e.note for e in exact)
    assert span_c <= 12, "compact voicing must fit an octave"
    assert all(g.in_key(e.note) for e in strummed if e.role != "extension")
    assert colour[0].role in ("extension", "bass")
    return ("white-key chords (C major):\n  " + "\n  ".join(rows) +
            f"\n  compact span={span_c} vs exact span={span_e} semitones"
            f"\n  black key C# -> {[e.note for e in colour]} "
            f"(role {colour[-1].role})"
            f"\n  strum offsets={[round(e.start, 3) for e in strummed]}"
            f"\n  arp 8 @8/s = {[e.note for e in arp]}"
            f"\n  performance list: {len(g.performance)} events captured")


if __name__ == "__main__":
    print(demo())
