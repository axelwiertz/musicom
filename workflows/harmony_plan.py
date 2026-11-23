# -*- coding: utf-8 -*-
"""HarmonyPlan — the abstract-layer output: WHAT chords, per bar.

HARMONIZATION_METHOD_PLAN.md P0. The canonical per-bar chord skeleton shared by
the abstract layer (ABS-* subset walks, functional Roman-numeral templates) and
the concrete layer (SATB/comp/arp voice-leaders + ``realize_spine``).

Today ``CellContext.chord_tones`` is a SINGLE chord per SECTION — that is the
reason two nightly compositions harmonise near-identically. A ``HarmonyPlan``
generalises that to one chord per BAR; a 1-bar plan is the backward-compatible
degenerate case.

Pure module — engine deps only (``rules.harmony`` for quality intervals).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from rules.harmony import QUALITY_INTERVALS

__all__ = ["Chord", "HarmonyPlan"]


@dataclass(frozen=True)
class Chord:
    """One harmonic slice: root + quality (+ optional explicit chord tones)."""

    root_midi: int
    quality: str = "maj"
    degree: str = ""                 # Roman numeral (informational)
    tension: float = 0.0             # per-bar tension target (ABS / curve use)
    tones: Tuple[int, ...] = ()      # explicit chord tones; empty -> derive

    def chord_tones(self) -> Tuple[int, ...]:
        """Absolute chord tones. Explicit ``tones`` wins, else derive quality."""
        if self.tones:
            return self.tones
        iv = QUALITY_INTERVALS.get(self.quality, QUALITY_INTERVALS["maj"])
        return tuple(self.root_midi + i for i in iv)


@dataclass(frozen=True)
class HarmonyPlan:
    """Per-bar chord sequence (the abstract-layer artifact)."""

    chords: Tuple[Chord, ...]

    def chord_at(self, bar: int) -> Chord:
        """The chord active in ``bar`` (cycles if the plan is shorter)."""
        if not self.chords:
            raise ValueError("empty HarmonyPlan")
        return self.chords[bar % len(self.chords)]

    @property
    def n_bars(self) -> int:
        return len(self.chords)

    @property
    def roots(self) -> Tuple[int, ...]:
        return tuple(c.root_midi for c in self.chords)

    def slice(self, start: int, n: int) -> "HarmonyPlan":
        """A sub-plan of ``n`` bars beginning at absolute bar ``start``."""
        return HarmonyPlan(chords=tuple(self.chord_at(start + i) for i in range(n)))

    @classmethod
    def single(cls, chord_tones, root_midi=None, quality="maj",
               degree="", tension=0.0) -> "HarmonyPlan":
        """One chord held for the whole section (the legacy degenerate case)."""
        tones = tuple(chord_tones)
        root = root_midi if root_midi is not None else (tones[0] if tones else 48)
        return cls(chords=(Chord(root, quality, degree, tension, tones),))
