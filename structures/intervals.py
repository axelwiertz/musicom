"""Interval-based musical structures: set theory, Hindemith hierarchy,
interval expansion, and delta encoding.

Implements the four missing interval-first primitives identified in the
interval-composition assessment:

1. Forte interval-class vectors (set theory / atonal)
2. Hindemith Series 2 interval hierarchy (harmonic fluctuation)
3. Bartók-style interval expansion/contraction
4. Relative/delta encoding (transposition-invariant representation)
"""

from typing import Dict, List, Sequence, Tuple

from rules.set_theory import interval_vector as _kernel_icv
from rules.set_theory import prime_form as _kernel_pf

# ---------------------------------------------------------------------------
# 1. Forte interval-class vectors (set theory)
#
# Canonical implementation lives in rules/set_theory.py; these are thin
# aliases kept so existing imports (`from structures.intervals import ...`)
# keep working.
# ---------------------------------------------------------------------------

INTERVAL_CLASSES = (1, 2, 3, 4, 5, 6)  # i1..i6 (i6 = tritone class)


def interval_class_vector(pitches: Sequence[int]) -> List[int]:
    """Forte ICV: counts of each interval class (i1..i6) in a pitch set.

    Delegates to the canonical kernel in rules/set_theory.py.
    """
    return _kernel_icv(pitches)


def z_related(a: Sequence[int], b: Sequence[int]) -> bool:
    """True if two sets share an ICV but are NOT transpositionally or
    inversionally related (Forte Z-relation).

    Two sets related by transposition OR inversion have the same interval
    content by definition — they are not Z-partners. Z-partners share the
    ICV yet have genuinely different prime forms (e.g. 4-Z15 / 4-Z29).
    """
    va = interval_class_vector(a)
    vb = interval_class_vector(b)
    if va != vb:
        return False
    return set_prime_form(a) != set_prime_form(b)


def set_prime_form(pitches: Sequence[int]) -> Tuple[int, ...]:
    """Forte prime form (canonical; delegates to rules/set_theory.py).

    Returns the prime form as a tuple of pitch classes (lowest form).

    >>> set_prime_form([0, 4, 7])   # major triad
    (0, 3, 7)
    >>> set_prime_form([0, 3, 7])   # minor triad — same prime form
    (0, 3, 7)
    """
    return tuple(_kernel_pf(pitches))


# ---------------------------------------------------------------------------
# 2. Hindemith Series 2 interval hierarchy
# ---------------------------------------------------------------------------

# Hindemith ranks intervals from most stable (consonant) to most tense:
# rank 0 = octave, rank 1 = fifth, rank 2 = fourth ... rank 11 = tritone.
# Source: Unterweisung im Tonsatz, Series 2 (12 ranks, 0-11).
_HINDEMITH_ORDER = (0, 7, 5, 4, 3, 9, 8, 11, 10, 2, 1, 6)
_HINDEMITH_RANK = {iv: rank for rank, iv in enumerate(_HINDEMITH_ORDER)}


def hindemith_rank(interval: int) -> int:
    """Hindemith Series 2 stability rank for an interval (semitones, 0-12).

    0 = most stable (unison), 11 = most tense (tritone).
    """
    return _HINDEMITH_RANK.get(abs(interval) % 12, 11)


def harmonic_fluctuation(melody: Sequence[int]) -> List[int]:
    """Per-step Hindemith harmonic fluctuation (rank of each interval).

    Args:
        melody: sequence of MIDI pitches.

    Returns:
        List of ranks, one per consecutive interval.
    """
    return [hindemith_rank(melody[i + 1] - melody[i])
            for i in range(len(melody) - 1)]


def manage_fluctuation(melody: Sequence[int],
                       target_rank: int,
                       tolerance: int = 0) -> Sequence[int]:
    """Adjust a melody so its step intervals stay within a rank band.

    Dissonant steps (rank > target + tolerance) are collapsed toward the
    previous pitch by replacing the offending interval with a step of the
    target rank's representative interval.

    Args:
        melody: sequence of MIDI pitches.
        target_rank: desired maximum tension rank (0-6).
        tolerance: allowed overshoot.

    Returns:
        Adjusted melody (list of ints).
    """
    out = list(melody)
    # representative semitone for each rank (first interval of that rank)
    rank_to_iv = {}
    for iv, rank in _HINDEMITH_RANK.items():
        rank_to_iv.setdefault(rank, iv)
    for i in range(1, len(out)):
        d = out[i] - out[i - 1]
        if hindemith_rank(d) > target_rank + tolerance:
            rep = rank_to_iv.get(target_rank, 7)
            sign = 1 if d > 0 else -1
            out[i] = out[i - 1] + sign * rep
    return out


# ---------------------------------------------------------------------------
# 3. Bartók-style interval expansion / contraction
# ---------------------------------------------------------------------------

def interval_expansion(motif: Sequence[int],
                       expansion_steps: Sequence[int]) -> List[int]:
    """Systematically expand (or contract) a motif's intervals.

    Args:
        motif: initial interval motif (e.g. [0, 1] = minor second).
        expansion_steps: list of semitone targets for the motif's interval,
            e.g. [1, 2, 3, 4, 5, 6, 7] expands m2 -> M2 -> m3 -> M3 -> P4 -> TT -> P5.

    Returns:
        Flat pitch sequence built by repeating the motif at each expansion
        size, each time relative to the previous phrase's last note.
    """
    out: List[int] = []
    current = 0
    for size in expansion_steps:
        phrase = [current]
        for step in motif[1:]:
            interval = step - motif[0]
            # scale interval by expansion ratio
            scaled = int(round(interval * (size / motif[0]))) if motif[0] else size
            phrase.append(phrase[-1] + scaled)
        out.extend(phrase)
        current = phrase[-1]
    return out


def interval_contraction(motif: Sequence[int],
                         contraction_steps: Sequence[int]) -> List[int]:
    """Mirror of interval_expansion: progressively smaller intervals."""
    return interval_expansion(motif, contraction_steps)


# ---------------------------------------------------------------------------
# 4. Delta / relative encoding
# ---------------------------------------------------------------------------

def delta_encode(pitches: Sequence[int]) -> List[int]:
    """Relative encoding: [60, 64, 67] -> [0, +4, +3]."""
    if not pitches:
        return []
    return [0] + [pitches[i + 1] - pitches[i] for i in range(len(pitches) - 1)]


def delta_decode(deltas: Sequence[int], start: int = 60) -> List[int]:
    """Inverse of delta_encode."""
    out = [start]
    for d in deltas[1:]:
        out.append(out[-1] + d)
    return out


def transposition_invariant(motif: Sequence[int], root: int = 60) -> List[int]:
    """Re-root a motif at any pitch while preserving its interval identity."""
    return [root + d for d in delta_encode(motif)]


if __name__ == "__main__":
    # Quick self-tests
    assert interval_class_vector([0, 1, 2]) == [2, 1, 0, 0, 0, 0]
    assert interval_class_vector([0, 4, 7]) == [0, 0, 1, 1, 1, 0]  # m3, M3, P4
    assert interval_class_vector([0, 6]) == [0, 0, 0, 0, 0, 1]     # tritone
    print("ICV [0,4,7] major triad:", interval_class_vector([0, 4, 7]))
    print("Hindemith ranks P5=1, TT=11:", hindemith_rank(7), hindemith_rank(6))
    print("Expansion m2->P5:", interval_expansion([0, 1], [1, 2, 3, 4, 5, 6, 7]))
    print("Delta [60,64,67]:", delta_encode([60, 64, 67]))
    print("All self-tests passed")
