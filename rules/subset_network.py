# -*- coding: utf-8 -*-
"""Abstract layer — 12TET subset network (z-relations, P/L/R, tension).

Implements the "pattern = subset" idea from subset_theory.md:

    A Pattern holds a subset of 12TET (a pitch-class set). A chord
    progression is a walk through subset space. Tension/resolution falls
    out of the (dis)similarity between successive subsets — shared pcs,
    interval-class-vector distance, z-relations, complementation — not
    from functional labels.

This is the ABSTRACT layer: everything here is transposition- and
register-invariant. Realization (pitches, onsets, durations, velocities)
happens in the CONCRETE layer (unitmatrix / SCALE workflows).

Pure module: no engine imports, no MIDI, no I/O. Fully deterministic,
unit-testable.

References: Forte 1973 (prime forms, ICV, Z-relations), Cohn 2012 (P/L/R),
Tymoczko 2011 (voice-leading distance).
"""

from dataclasses import dataclass, field
from functools import lru_cache
from itertools import combinations
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

from rules.set_theory import SetTheoryAnalyst as _STA

# ---------------------------------------------------------------------------
# Interval-class vector + tension
# ---------------------------------------------------------------------------

# ic -> consonance weight (higher = more dissonant). Thirds/sixths consonant,
# fourth/fifth neutral, seconds/sevenths dissonant, tritone most dissonant.
IC_WEIGHT: Dict[int, float] = {
    1: 2.0,   # minor 2nd / major 7th
    2: 1.5,   # major 2nd / minor 7th
    3: 0.5,   # minor 3rd / major 6th  (consonant)
    4: 0.5,   # major 3rd / minor 6th  (consonant)
    5: 1.0,   # perfect 4th / 5th      (neutral)
    6: 3.0,   # tritone               (most dissonant)
}


def interval_vector(pcs: Iterable[int]) -> List[int]:
    """ICV of a pc-set: 6 counts of interval classes 1..6.

    Delegates to the existing rules/set_theory.py kernel.
    """
    return _STA.interval_vector(sorted(set(p % 12 for p in pcs)))


def tension(pcs: Iterable[int]) -> float:
    """Tension of a pc-set from its ICV (weighted dissonance)."""
    icv = interval_vector(pcs)
    return sum(IC_WEIGHT[i + 1] * icv[i] for i in range(6))


def icv_distance(a: Iterable[int], b: Iterable[int]) -> float:
    """Euclidean distance between two ICVs (a dissimilarity metric)."""
    va, vb = interval_vector(a), interval_vector(b)
    return sum((x - y) ** 2 for x, y in zip(va, vb)) ** 0.5


def common_tones(a: Iterable[int], b: Iterable[int]) -> int:
    """Number of shared pitch classes between two subsets."""
    return len(set(p % 12 for p in a) & set(p % 12 for p in b))


def voice_leading_distance(a: Iterable[int], b: Iterable[int]) -> int:
    """Minimal total semitone motion between two subsets (Tymoczko).

    Embedding distance: pair up the sorted pc-sets (wrapping), take the
    minimal total |Δ| over a small set of alignment offsets. Used to rank
    how "smooth" a move between patterns is.
    """
    sa = sorted(set(p % 12 for p in a))
    sb = sorted(set(p % 12 for p in b))
    best = None
    for shift in range(len(sb)):
        rot = sb[shift:] + sb[:shift]
        total = 0
        for x, y in zip(sa, rot):
            d = abs(x - y)
            total += min(d, 12 - d)
        if best is None or total < best:
            best = total
    return best if best is not None else 0


# ---------------------------------------------------------------------------
# Z-relations and complement
# ---------------------------------------------------------------------------

def _prime_key(pcs: Iterable[int]) -> Tuple[int, ...]:
    return tuple(_STA.prime_form(sorted(set(p % 12 for p in pcs))))


def complement_pcs(pcs: Iterable[int]) -> FrozenSet[int]:
    """The (12-k)-note complement of a pc-set (mod-12 universe)."""
    return frozenset(set(range(12)) - set(p % 12 for p in pcs))


# ---------------------------------------------------------------------------
# Pattern
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Pattern:
    """A named 12TET subset — the chord / pitch pool for one role+unit.

    Abstract layer: no register, no onset grid, no duration. The subset is
    the whole content; realization (concrete layer) transposes it into a
    voice register and attaches rhythm.
    """
    id: str
    subset: FrozenSet[int]
    role: str = "harmony"   # harmony | lead | bass | texture

    @property
    def pcs(self) -> FrozenSet[int]:
        return self.subset

    @property
    def icv(self) -> List[int]:
        return interval_vector(self.subset)

    @property
    def tension(self) -> float:
        return tension(self.subset)

    @property
    def prime(self) -> Tuple[int, ...]:
        return _prime_key(self.subset)

    @property
    def complement(self) -> "Pattern":
        return Pattern(f"{self.id}-comp", complement_pcs(self.subset), self.role)

    def transposed(self, semitones: int) -> "Pattern":
        return Pattern(self.id, frozenset((p + semitones) % 12 for p in self.subset),
                       self.role)

    def __repr__(self) -> str:
        return f"Pattern({self.id}, {sorted(self.subset)}, T={self.tension:.1f})"


# ---------------------------------------------------------------------------
# Pattern network
# ---------------------------------------------------------------------------

# Edge relation types
TN = "tn"            # transposition (same prime form)
INV = "inv"          # inversion
Z = "z"              # z-related (same ICV, different prime form)
COMPL = "compl"      # complementation (max contrast, matched tension)
PLR = "plr"          # parsimonious (P/L/R-style, VL <= 2)
VL = "vl"            # generic voice-leading move


@dataclass(frozen=True)
class Edge:
    a: str
    b: str
    rel: str
    weight: float = 1.0   # lower = closer/smoother


class PatternNetwork:
    """Graph of patterns; edges = musical relations (z, P/L/R, complement).

    The tension/resolution logic of a progression lives in the graph:
    walking a low-weight edge = smooth/resolved move, a high-weight edge =
    tense/contrasting move.
    """

    def __init__(self, patterns: Sequence[Pattern]):
        self.patterns = {p.id: p for p in patterns}
        self.edges: Dict[str, List[Edge]] = {p.id: [] for p in patterns}
        self._build()

    # -- construction -------------------------------------------------------
    def _build(self) -> None:
        ids = list(self.patterns)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = self.patterns[ids[i]], self.patterns[ids[j]]
                rels = self._relations(a, b)
                for rel, w in rels:
                    e = Edge(a.id, b.id, rel, w)
                    self.edges[a.id].append(e)
                    self.edges[b.id].append(Edge(b.id, a.id, rel, w))

    @staticmethod
    def _relations(a: Pattern, b: Pattern) -> List[Tuple[str, float]]:
        """All musical relations between two patterns, with closeness weight."""
        out: List[Tuple[str, float]] = []
        same_shape = a.prime == b.prime
        inv_b = frozenset((12 - p) % 12 for p in b.subset)
        inversional = _prime_key(inv_b) == a.prime
        if same_shape:
            out.append((TN, 0.5))                       # same shape, shifted
        elif inversional:
            out.append((INV, 1.5))                      # inversion of shape
        elif a.icv == b.icv:
            # true Z-relation: same interval content, different prime form,
            # and NOT related by transposition/inversion
            out.append((Z, 1.0))                        # z-partners / same color
        if a.icv == b.icv and not same_shape:
            # complement pairs: maximal contrast, matched tension profile
            if _prime_key(a.complement.subset) == b.prime:
                out.append((COMPL, 2.0))
        # parsimonious: small voice-leading between triads (P/L/R style)
        if len(a.subset) <= 4 and len(b.subset) <= 4 and not same_shape:
            vl = voice_leading_distance(a.subset, b.subset)
            if vl <= 2:
                out.append((PLR, 0.5 + 0.5 * vl))
            elif vl <= 4:
                out.append((VL, 0.5 + 0.5 * vl))
        return out

    # -- queries ------------------------------------------------------------
    def neighbors(self, pid: str) -> List[Edge]:
        return sorted(self.edges.get(pid, []), key=lambda e: e.weight)

    def tension_of(self, pid: str) -> float:
        return self.patterns[pid].tension

    # -- paths --------------------------------------------------------------
    def walk(self, start: str, length: int, rng=None,
             tension_curve: Optional[Sequence[float]] = None,
             home: Optional[str] = None) -> List[str]:
        """Walk the network: a chord progression as a pattern sequence.

        Smooth default: from the current node prefer the lowest-weight edge
        (parsimonious / transposition). If a tension_curve is given, pick
        the neighbor whose tension best matches the curve target at each
        step (tension = f(position in form)). If `home` is given, bias
        toward returning to it at the end (resolution).
        """
        import random
        rng = rng or random.Random()
        if start not in self.patterns:
            raise KeyError(f"unknown pattern {start!r}; have {sorted(self.patterns)}")
        seq = [start]
        cur = start
        for step in range(1, length):
            nbrs = self.neighbors(cur)
            if not nbrs:
                break
            if tension_curve is not None and step < len(tension_curve):
                target = tension_curve[step]
                scored = []
                for e in nbrs:
                    t = self.patterns[e.b].tension
                    # prefer low edge weight AND closeness to tension target
                    score = e.weight + abs(t - target)
                    scored.append((score, e.b))
                scored.sort(key=lambda x: x[0])
                pool = [pid for _, pid in scored[:3]]
                nxt = rng.choice(pool)
            elif home is not None and step >= length - 2 and home in (
                    e.b for e in nbrs):
                nxt = home  # cadence back home at the end
            else:
                pool = [e.b for e in nbrs[:3]]
                nxt = rng.choice(pool)
            seq.append(nxt)
            cur = nxt
        return seq


# ---------------------------------------------------------------------------
# Standard pattern library (diatonic + chromatic anchors)
# ---------------------------------------------------------------------------

def _triad(root: int, kind: str) -> FrozenSet[int]:
    iv = {"maj": (0, 4, 7), "min": (0, 3, 7), "dim": (0, 3, 6),
          "aug": (0, 4, 8)}[kind]
    return frozenset((root + i) % 12 for i in iv)


def _tetrad(root: int, kind: str) -> FrozenSet[int]:
    iv = {"maj7": (0, 4, 7, 11), "min7": (0, 3, 7, 10), "dom7": (0, 4, 7, 10),
          "dim7": (0, 3, 6, 9), "m7b5": (0, 3, 6, 10)}[kind]
    return frozenset((root + i) % 12 for i in iv)


def standard_patterns() -> List[Pattern]:
    """Diatonic anchor set: triads/tetrads on C + symmetric anchors."""
    ps: List[Pattern] = []
    for root in range(12):
        ps.append(Pattern(f"maj{root}", _triad(root, "maj")))
        ps.append(Pattern(f"min{root}", _triad(root, "min")))
        ps.append(Pattern(f"dim{root}", _triad(root, "dim")))
        ps.append(Pattern(f"aug{root}", _triad(root, "aug")))
    for root in range(12):
        ps.append(Pattern(f"maj7{root}", _tetrad(root, "maj7")))
        ps.append(Pattern(f"min7{root}", _tetrad(root, "min7")))
        ps.append(Pattern(f"dom7{root}", _tetrad(root, "dom7")))
    # symmetric anchors (whole-tone, octatonic, chromatic subsets)
    ps.append(Pattern("wholetone", frozenset({0, 2, 4, 6, 8, 10}), "texture"))
    ps.append(Pattern("oct0", frozenset({0, 1, 3, 4, 6, 7, 9, 10}), "texture"))
    ps.append(Pattern("chrom4", frozenset({0, 1, 2, 3}), "texture"))
    ps.append(Pattern("quartal", frozenset({0, 5, 10, 3}), "texture"))
    # Forte Z-pair 4-Z15 / 4-Z29 (same ICV [1,1,1,1,1,1], different shape) —
    # the canonical example of same-color-different-notes variation.
    ps.append(Pattern("z0146", frozenset({0, 1, 4, 6}), "texture"))   # 4-Z15
    ps.append(Pattern("z0137", frozenset({0, 1, 3, 7}), "texture"))   # 4-Z29
    # complement pair: 4-28 dim7 (self-complement) + 8-28; and 4-note set +
    # its 8-note complement for explicit COMPL edges (e.g. maj7 tetrad pool)
    ps.append(Pattern("maj7comp0", complement_pcs(_tetrad(0, "maj7")), "texture"))
    return ps


# ---------------------------------------------------------------------------
# Convenience: resolve a common progression as subset ids (C-major anchor)
# ---------------------------------------------------------------------------

def diatonic_degree_patterns(tonic_pc: int = 0) -> Dict[str, str]:
    """Map scale-degree names to pattern ids in the standard library.

    Major scale on tonic_pc: I ii iii IV V vi vii(dim) -> pattern id.
    Returns e.g. {"I": "maj0", "V": "maj7", "vi": "min9"} for tonic C.
    """
    # major scale intervals on the tonic; degree index -> scale offset
    offs = [0, 2, 4, 5, 7, 9, 11]
    names = ["I", "ii", "iii", "IV", "V", "vi", "vii"]
    kinds = ["maj", "min", "min", "maj", "maj", "min", "dim"]
    out: Dict[str, str] = {}
    for name, off, kind in zip(names, offs, kinds):
        root = (tonic_pc + off) % 12
        for p in standard_patterns():
            if p.subset == _triad(root, kind):
                out[name] = p.id
                break
    return out


def patterns_from_degrees(tonic_pc: int = 0,
                          degrees: Sequence[str] = ("I", "V", "vi", "IV")
                          ) -> List[Pattern]:
    """Concrete Pattern objects for a degree progression (e.g. pop I-V-vi-IV)."""
    ids = diatonic_degree_patterns(tonic_pc)
    lib = {p.id: p for p in standard_patterns()}
    return [lib[ids[d]] for d in degrees]
