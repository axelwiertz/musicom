"""Scale quantizer + probability engine — VAEMI Synterra-style.

Generative pitch engine: quantize arbitrary values to scale members,
probability-weighted random generation, MIDI scale mode constriction.

Usage:
    sq = ScaleQuantizer(root=60, scale="major")
    sq.quantize(63)  # -> 64 (nearest major scale degree)

    pe = ProbabilityEngine(scale_quantizer=sq, seed=42)
    notes = pe.generate(16)  # list of 16 MIDI pitches in scale
"""

import numpy as np
from typing import Dict, List, Optional, Set, Tuple
import random
from dataclasses import dataclass

__all__ = ["ScaleQuantizer", "ProbabilityEngine", "ScaleModeMIDI",
           "STRONG_GRID", "classify_weight", "StructuralNote"]

# Scale intervals in semitones from root
_SCALES = {
    "major":      [0, 2, 4, 5, 7, 9, 11],
    "minor":      [0, 2, 3, 5, 7, 8, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "chromatic":  list(range(12)),
    "dorian":     [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
}

# Default strong-beat grids (tick offsets within one bar that count as
# "strong"; VOICE_ROLE_WORKFLOW_PLAN.md §9-Q1). A style may override via
# STYLE_REGISTRY[style]["strong_beats"] — e.g. backbeat pop/rock/soul flips
# to beats 2 & 4 = (480, 1440).
STRONG_GRID: Dict[str, Tuple[int, ...]] = {
    "4/4":  (0, 960),        # beats 1 & 3 (downbeats)
    "2/4":  (0,),            # beat 1 only
    "3/4":  (0,),            # beat 1 only
    "6/8":  (0, 960),        # two dotted-quarter pulses
    "12/8": (0, 960),
}


def classify_weight(onset_tick: int, strong_grid: Tuple[int, ...],
                    bar_ticks: int = 1920,
                    tagged_weight: Optional[str] = None) -> str:
    """Structural weight of a note onset: "strong" or "weak".

    Default is derived from the onset grid — a note whose onset falls on a
    strong-grid tick within its bar is Strong, else Weak. A method MAY tag a
    note (``tagged_weight`` in ("strong", "weak")) to override the grid
    default (fork 1 of the plan). No tag -> grid default.
    """
    if tagged_weight in ("strong", "weak"):
        return tagged_weight
    return "strong" if (onset_tick % bar_ticks) in strong_grid else "weak"


@dataclass
class StructuralNote:
    """A note carrying its structural weight + optional ornament tag.

    This is the "tag path" of the tiered pitch discipline: a method emits a
    StructuralNote with ``weight`` (strong/weak) and, when it is a deliberate
    chromatic ornament, ``ornament`` (passing/neighbor/approach/leading_tone).
    The audit (workflows.pitch_audit) reads these tags to apply the
    tagged-ornament exemption.
    """
    pitch: int
    weight: str = "strong"           # "strong" | "weak"
    ornament: Optional[str] = None   # None | passing|neighbor|approach|leading_tone
    start_tick: int = 0
    end_tick: int = 0
    volume: int = 100


class ScaleQuantizer:
    """Quantize arbitrary pitch values to nearest member of a scale."""

    def __init__(self, root: int = 60, scale: str = "major"):
        if scale not in _SCALES:
            raise ValueError(f"Unknown scale: {scale}. Use: {list(_SCALES)}")
        self.root = root
        self.scale = scale
        self._intervals = _SCALES[scale]

    def scale_pitches(self, octave_low: int = 0, octave_high: int = 10) -> List[int]:
        """All MIDI pitches in scale across octave range."""
        pitches = []
        for octave in range(octave_low, octave_high + 1):
            for iv in self._intervals:
                pitches.append(self.root + iv + 12 * (octave - self.root // 12))
        return sorted(set(p for p in pitches if 0 <= p <= 127))

    def quantize(self, value: float) -> int:
        """Snap a semitone value to nearest scale member (tie -> higher)."""
        # Candidate pitches: each interval at the octave floor/ceil around value
        floor_oct = int(np.floor((value - self.root) / 12.0))
        best: int = self.root
        best_dist = float("inf")
        for octave in (floor_oct, floor_oct + 1):
            for iv in self._intervals:
                pitch = self.root + iv + 12 * octave
                dist = abs(pitch - value)
                if dist < best_dist or (dist == best_dist and pitch > best):
                    best_dist = dist
                    best = pitch
        return best

    def is_in_scale(self, pitch: int) -> bool:
        """Check if a MIDI pitch belongs to this scale."""
        pc = ((pitch - self.root) % 12 + 12) % 12
        return pc in self._intervals

    def tiered_quantize(self, value: float, weight: str = "strong",
                        chord_tones: Optional[List[int]] = None) -> int:
        """Weight-aware snap (VOICE_ROLE_WORKFLOW_PLAN.md §3).

        Strong notes snap to the nearest scale degree, THEN (if ``chord_tones``
        given) to the nearest chord tone — a hard in-scale AND in-chord snap.
        Weak notes snap to the nearest scale degree only; a weak note MAY be
        left chromatic by the ornament layer (rules.ornament), which is a
        separate, tagged pass — this method never emits chromatic pitches on
        its own.

        ``weight`` is one of "strong"/"weak" (see ``classify_weight``).
        """
        pitch = self.quantize(value)
        if weight == "strong" and chord_tones:
            pitch = min(chord_tones, key=lambda c: abs(c - pitch))
        return pitch


class ProbabilityEngine:
    """Weighted random note generator constrained to a scale."""

    def __init__(self, scale_quantizer: ScaleQuantizer,
                 tendency_target: Optional[int] = None,
                 tendency_strength: float = 0.3,
                 avoid_repeats: int = 2,
                 seed: Optional[int] = None):
        self.sq = scale_quantizer
        self.tendency_target = tendency_target
        self.tendency_strength = tendency_strength
        self.avoid_repeats = avoid_repeats
        self._rng = random.Random(seed)
        self._recent: List[int] = []

    def generate(self, steps: int, max_step: int = 5) -> List[int]:
        """Generate `steps` MIDI pitches, all in scale, stepwise-biased."""
        pitches = self.sq.scale_pitches()
        if not pitches:
            return []

        current = self._rng.choice(pitches) if not self._recent else self._recent[-1]
        result = [current]

        for _ in range(steps - 1):
            candidates = [p for p in pitches
                          if abs(p - current) <= max_step
                          and p not in self._recent[-self.avoid_repeats:]]
            if not candidates:
                candidates = pitches

            if self.tendency_target is not None:
                weights = []
                for p in candidates:
                    dist = abs(p - self.tendency_target)
                    w = max(0.1, 1.0 - dist / 24.0) * self.tendency_strength
                    w += (1.0 - self.tendency_strength)
                    weights.append(w)
                total = sum(weights)
                r = self._rng.random() * total
                cum = 0.0
                chosen = candidates[-1]
                for c, w in zip(candidates, weights):
                    cum += w
                    if r <= cum:
                        chosen = c
                        break
            else:
                chosen = self._rng.choice(candidates)

            result.append(chosen)
            current = chosen
            self._recent.append(chosen)

        return result


class ScaleModeMIDI:
    """MIDI Scale Mode: constrain output to a reference pitch set."""

    def __init__(self):
        self._ref_set: Set[int] = set()

    def add_reference_pitches(self, pitches: List[int]):
        """Set the allowed pitch set (from incoming MIDI chord)."""
        self._ref_set = set(pitches)

    def constrain(self, pitch: int) -> int:
        """Snap pitch to nearest member of reference set."""
        if not self._ref_set:
            return pitch
        return min(self._ref_set, key=lambda p: abs(p - pitch))

    def is_allowed(self, pitch: int) -> bool:
        return pitch in self._ref_set
