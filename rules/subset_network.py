# -*- coding: utf-8 -*-
"""Abstract layer — 12TET subset network (z-relations, P/L/R, tension).

Deprecated alias module. The pattern library and all its metrics now live in
:mod:`rules.patterns` (see ``PATTERN_ARCHITECTURE.md``); this module is kept
so the existing imports keep working:

    from rules.subset_network import PatternNetwork, standard_patterns

Everything here is re-exported from :mod:`rules.patterns`, so ``Pattern`` and
``standard_patterns()`` are *literally the same objects* — no duplicate
implementation, no divergence risk. New code should import from
``rules.patterns`` directly.

The graph type that used to live here is now
:class:`rules.patterns.PatternNetworkHost`; ``PatternNetwork`` is retained as
an alias name for compatibility.

Pure module: no engine imports, no MIDI, no I/O. Fully deterministic.
"""

from rules.patterns import (
    IC_WEIGHT,
    Pattern,
    complement_pcs,
    common_tones,
    diatonic_degree_patterns,
    interval_vector,
    icv_distance,
    patterns_from_degrees,
    standard_patterns,
    tension,
    voice_leading_distance,
)

# Edge relation types (unchanged names/values — they are part of the API).
TN = "tn"            # transposition (same prime form)
INV = "inv"          # inversion
Z = "z"              # z-related (same ICV, different prime form)
COMPL = "compl"      # complementation (max contrast, matched tension)
PLR = "plr"          # parsimonious (P/L/R-style, VL <= 2)
VL = "vl"            # generic voice-leading move

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple


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
        inversional = PatternNetwork._prime_key(inv_b) == a.prime
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
            if PatternNetwork._prime_key(a.complement.subset) == b.prime:
                out.append((COMPL, 2.0))
        # parsimonious: small voice-leading between triads (P/L/R style)
        if len(a.subset) <= 4 and len(b.subset) <= 4 and not same_shape:
            vl = voice_leading_distance(a.subset, b.subset)
            if vl <= 2:
                out.append((PLR, 0.5 + 0.5 * vl))
            elif vl <= 4:
                out.append((VL, 0.5 + 0.5 * vl))
        return out

    @staticmethod
    def _prime_key(pcs) -> Tuple[int, ...]:
        from rules.set_theory import prime_form
        return tuple(prime_form(list(pcs)))

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


__all__ = [
    "IC_WEIGHT", "Pattern", "PatternNetwork", "Edge",
    "TN", "INV", "Z", "COMPL", "PLR", "VL",
    "interval_vector", "tension", "icv_distance", "common_tones",
    "voice_leading_distance", "complement_pcs",
    "standard_patterns", "diatonic_degree_patterns", "patterns_from_degrees",
]
