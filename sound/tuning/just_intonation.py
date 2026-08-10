"""Just Intonation microtonal tuning system — KHÔRA-style.

Implements pure integer frequency ratios, consonance metrics (Tenney height),
and chord generators (Genesis, Metabole, Topos, Skia) for microtonal drone
and harmonic exploration.

Reference: surveillance report Aug 2026, KHÔRA synth.

Usage:
    from sound.tuning.just_intonation import JustIntonation, JIChordGenerator

    ji = JustIntonation(root_freq=220.0)
    pitches = ji.scale('major')  # [1/1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]
    freqs = ji.scale_freqs('major')  # [220, 247.5, 275, 293.3, 330, 366.7, 412.5]

    gen = JIChordGenerator()
    chord = gen.genesis(pitches[:5])  # consonant JI subset
"""

import numpy as np
from math import log2, gcd
from typing import List, Tuple, Optional
from fractions import Fraction

__all__ = ["JustIntonation", "JIChordGenerator", "tenney_height", "consonance_score"]


# Standard JI intervals (ratio, cents, name)
JI_INTERVALS = {
    "unison": (1, 1, 0),
    "minor_second": (16, 15, 111.7),
    "major_second": (9, 8, 203.9),
    "minor_third": (6, 5, 315.6),
    "major_third": (5, 4, 386.3),
    "perfect_fourth": (4, 3, 498.0),
    "tritone": (7, 5, 582.5),
    "perfect_fifth": (3, 2, 702.0),
    "minor_sixth": (8, 5, 813.7),
    "major_sixth": (5, 3, 884.4),
    "minor_seventh": (9, 5, 1017.6),
    "major_seventh": (15, 8, 1088.3),
    "octave": (2, 1, 1200.0),
}


class JustIntonation:
    """Just Intonation tuning system with pure integer ratios.

    Parameters
    ----------
    root_freq : float
        Root frequency in Hz (default 220 Hz = A3).
    """

    def __init__(self, root_freq: float = 220.0):
        self.root_freq = root_freq

    def ratio_to_freq(self, num: int, den: int) -> float:
        """Convert JI ratio to frequency."""
        return self.root_freq * num / den

    def scale(self, name: str) -> List[Tuple[int, int]]:
        """Return JI scale as list of (numerator, denominator) ratios.

        Parameters
        ----------
        name : str
            Scale name: 'major', 'minor', 'pentatonic', 'chromatic'.

        Returns
        -------
        list of (num, den) tuples
        """
        scales = {
            "major": [(1,1), (9,8), (5,4), (4,3), (3,2), (5,3), (15,8)],
            "minor": [(1,1), (9,8), (6,5), (4,3), (3,2), (8,5), (9,5)],
            "pentatonic": [(1,1), (9,8), (5,4), (3,2), (5,3)],
            "chromatic": [(1,1), (16,15), (9,8), (6,5), (5,4), (4,3),
                          (7,5), (3,2), (8,5), (5,3), (9,5), (15,8)],
        }
        if name not in scales:
            raise ValueError(f"Unknown scale: {name}. Use: {list(scales.keys())}")
        return scales[name]

    def scale_freqs(self, name: str) -> List[float]:
        """Return JI scale as list of frequencies in Hz."""
        ratios = self.scale(name)
        return [self.ratio_to_freq(n, d) for n, d in ratios]

    def interval_name(self, num: int, den: int) -> str:
        """Return name for a JI interval ratio."""
        ratio = num / den
        # find closest named interval
        closest = min(JI_INTERVALS.items(), key=lambda x: abs(x[1][2] - 1200*log2(ratio)))
        return closest[0]

    def simplify_ratio(self, num: int, den: int) -> Tuple[int, int]:
        """Simplify ratio to lowest terms."""
        g = gcd(num, den)
        return num // g, den // g


def tenney_height(num: int, den: int) -> float:
    """Compute Tenney height (complexity) of a JI interval.

    Tenney height = log2(numerator × denominator).
    Lower = simpler/more consonant.

    Parameters
    ----------
    num, den : int
        Numerator and denominator of the ratio.

    Returns
    -------
    float
        Tenney height (bits).
    """
    return log2(num * den)


def consonance_score(ratios: List[Tuple[int, int]]) -> float:
    """Compute consonance score for a set of JI ratios.

    Average Tenney height of all pairwise intervals.
    Lower = more consonant.

    Parameters
    ----------
    ratios : list of (num, den)
        JI ratios relative to root.

    Returns
    -------
    float
        Average Tenney height (lower = more consonant).
    """
    if len(ratios) < 2:
        return 0.0
    heights = []
    for i in range(len(ratios)):
        for j in range(i+1, len(ratios)):
            n1, d1 = ratios[i]
            n2, d2 = ratios[j]
            # interval = ratio2 / ratio1
            interval_num = n2 * d1
            interval_den = d2 * n1
            g = gcd(interval_num, interval_den)
            interval_num //= g
            interval_den //= g
            heights.append(tenney_height(interval_num, interval_den))
    return np.mean(heights) if heights else 0.0


class JIChordGenerator:
    """Generate JI chords using algorithmic rules (KHÔRA-style).

    Methods:
    - genesis: pick low-integer consonant ratios from a set
    - metabole: retain common tones, regenerate rest
    - topos: transpose all ratios by scalar
    - skia: select modal/dark subsets
    """

    def genesis(self, ratios: List[Tuple[int, int]], size: int = 5) -> List[Tuple[int, int]]:
        """Genesis chord: pick the most consonant subset.

        Selects ratios with lowest average Tenney height (simplest intervals).

        Parameters
        ----------
        ratios : list of (num, den)
            Available JI ratios.
        size : int
            Target chord size.

        Returns
        -------
        list of (num, den)
            Selected consonant subset.
        """
        if len(ratios) <= size:
            return ratios
        # score each subset (brute force for small sets)
        from itertools import combinations
        best = None
        best_score = float('inf')
        for subset in combinations(ratios, size):
            score = consonance_score(list(subset))
            if score < best_score:
                best_score = score
                best = subset
        return list(best) if best else ratios[:size]

    def metabole(self, old_chord: List[Tuple[int, int]],
                 new_pool: List[Tuple[int, int]],
                 retain: int = 2) -> List[Tuple[int, int]]:
        """Metabole chord: retain common tones, fill from pool.

        Keeps `retain` notes from old chord, adds new notes from pool
        to maintain voice leading.

        Parameters
        ----------
        old_chord : list of (num, den)
            Previous chord.
        new_pool : list of (num, den)
            Available ratios for new chord.
        retain : int
            Number of notes to retain from old chord.

        Returns
        -------
        list of (num, den)
            New chord with voice leading.
        """
        retained = old_chord[:retain]
        needed = len(old_chord) - retain
        # pick from pool excluding retained
        available = [r for r in new_pool if r not in retained]
        new_notes = available[:needed]
        return retained + new_notes

    def topos(self, chord: List[Tuple[int, int]],
              scalar_num: int, scalar_den: int) -> List[Tuple[int, int]]:
        """Topos chord: transpose all ratios by scalar.

        Multiplies each ratio by scalar (in JI space).

        Parameters
        ----------
        chord : list of (num, den)
            Input chord.
        scalar_num, scalar_den : int
            Transposition ratio.

        Returns
        -------
        list of (num, den)
            Transposed chord.
        """
        result = []
        for n, d in chord:
            new_n = n * scalar_num
            new_d = d * scalar_den
            g = gcd(new_n, new_d)
            result.append((new_n // g, new_d // g))
        return result

    def skia(self, ratios: List[Tuple[int, int]],
             size: int = 5) -> List[Tuple[int, int]]:
        """Skia chord: select modal/dark subset.

        Prefers minor thirds, minor sixths, and lower integers.

        Parameters
        ----------
        ratios : list of (num, den)
            Available ratios.
        size : int
            Target chord size.

        Returns
        -------
        list of (num, den)
            Dark/modal subset.
        """
        # score each ratio by "darkness" (minor intervals + low complexity)
        def darkness_score(ratio):
            n, d = ratio
            cents = 1200 * log2(n / d)
            # prefer minor intervals (300-400 cents, 800-900 cents)
            minor_bonus = 0
            if 300 <= cents <= 400 or 800 <= cents <= 900:
                minor_bonus = -2.0
            # prefer low complexity
            complexity = tenney_height(n, d)
            return complexity + minor_bonus

        scored = [(r, darkness_score(r)) for r in ratios]
        scored.sort(key=lambda x: x[1])
        return [r for r, _ in scored[:size]]
