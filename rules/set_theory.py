"""
Pitch Class Set Theory Analysis — canonical set-theory kernel.
Based on Straus, Forte, and the documents in in/Docs (Analyzing Atonal Music).

This module is the SINGLE canonical implementation of normal form, prime
form, and interval-class vector. Other modules delegate here:

    structures/intervals.py   (set_prime_form, interval_class_vector, z_related)
    rules/subset_network.py   (interval_vector, Pattern.prime)

Do not add a second implementation elsewhere — import from here.
"""

from typing import List, Tuple, Sequence
import itertools

def normal_form(pcs: Sequence[int]) -> List[int]:
    """Arranges pitch classes into their most compact form (Forte normal order)."""
    unique = sorted(set([p % 12 for p in pcs]))
    n = len(unique)
    if n == 0:
        return []
    if n == 1:
        return unique
    best_form: List[int] = []
    min_span = 13

    # Test every rotation
    for i in range(n):
        rotation = unique[i:] + [p + 12 for p in unique[:i]]
        span = rotation[-1] - rotation[0]
        if span < min_span:
            min_span = span
            best_form = rotation
        elif span == min_span and best_form:
            # Tie-breaker: check smaller intervals from the bottom
            for j in range(n - 2, 0, -1):
                span_j_best = (best_form[j] - best_form[0])
                span_j_curr = (rotation[j] - rotation[0])
                if span_j_curr < span_j_best:
                    best_form = rotation
                    break
                elif span_j_curr > span_j_best:
                    break
    # Transpose to 0-based (normal form usually reported 0-based).
    return [(p - best_form[0]) % 12 for p in best_form]


class SetTheoryAnalyst:
    """Analytical engine for atonal pitch class sets."""

    @staticmethod
    def normal_form(pcs: Sequence[int]) -> List[int]:
        return normal_form(pcs)

    @staticmethod
    def prime_form(pcs: Sequence[int]) -> List[int]:
        """Canonical Prime Form (transposed to 0 and most left-packed)."""
        if not pcs:
            return []

        nf = normal_form(pcs)
        # nf is already 0-based; compute the inversion's normal form
        inv = normal_form([(12 - p) % 12 for p in nf])

        # Choose the more "left-packed" one (element-wise, smaller wins)
        if inv < nf:
            return inv
        return nf

    @staticmethod
    def interval_vector(pcs: Sequence[int]) -> List[int]:
        """ICV of a pc-set: counts of interval classes 1 through 6."""
        return interval_vector(pcs)


def interval_vector(pcs: Sequence[int]) -> List[int]:
    """Interval Class Vector: 6 counts of interval classes 1..6.

    Index 0 = ic1 (minor 2nd), ..., index 5 = ic6 (tritone).
    """
    vector = [0] * 6
    unique = sorted(set([p % 12 for p in pcs]))
    for p1, p2 in itertools.combinations(unique, 2):
        interval = abs(p1 - p2) % 12
        if interval > 6:
            interval = 12 - interval
        if interval > 0:
            vector[interval - 1] += 1
    return vector


def prime_form(pcs: Sequence[int]) -> List[int]:
    """Module-level alias for SetTheoryAnalyst.prime_form."""
    return SetTheoryAnalyst.prime_form(pcs)
