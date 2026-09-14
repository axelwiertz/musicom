# -*- coding: utf-8 -*-
"""Pattern library — the single home for patterns, pitch-side and rhythm-side.

This is the middle layer of the architecture (see
``projects/Research/CompositionMethods/PATTERN_ARCHITECTURE.md``):

    12TET pc-set KERNEL   rules/set_theory.py       (names, ICV, Z-relations)
    PATTERN LIBRARY       rules/patterns.py         (this module)
    REALIZATION           rules/realize.py          (Pattern -> MusicEvent[])

What lives here
---------------
* :class:`Pattern` — an abstract 12TET subset plus role/tag metadata. Moved
  here from ``rules/subset_network.py`` (which re-exports it, so existing
  imports keep working) and made genuinely queryable: ``.forte`` names it,
  ``.z_partner`` finds its Z-partner, ``.roles``/``.tags`` are actually read.
* Pitch metrics — ``tension``, ``icv_distance``, ``common_tones``,
  ``voice_leading_distance``.
* Catalogues — ``standard_patterns`` (the golden, order-frozen library),
  ``chromatic_triads``, ``chromatic_tetrads``, ``diatonic_sets``,
  ``modal_sets``, ``z_pair_catalogue``, ``all_hexachords``, ``scale_pools``.
* :class:`RhythmPattern` + :class:`RhythmPatternNetwork` — the rhythm-side
  partner to the pitch side. Previously rhythm was a flat dict of 15 opaque
  ``(cycle, onsets)`` tuples with no accessors and no network.

PURITY
------
Pure module: no engine, no MIDI, no I/O, no ``musicpy``/``music21``.
Deterministic. ``tests/test_patterns_library.py`` pins this.

ORDERING CONTRACT
-----------------
``standard_patterns()`` returns its 91 patterns in a **frozen order** — the
zero-drift golden MIDI hash depends on it. Catalogue functions add patterns;
they must never reorder or renumber the standard library.
"""

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple, Union

from rules.set_theory import (
    SetTheoryAnalyst as _STA,
    all_sets_of_cardinality,
    all_z_pairs,
    forte_name as _forte_name,
    prime_form as _prime_form,
    z_partner as _kernel_z_partner,
)

# ---------------------------------------------------------------------------
# Interval-class vector + tension metrics
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

    Delegates to the canonical kernel in ``rules/set_theory.py``.
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

    ABSTRACT-layer metric: operates on pitch classes, tries all alignment
    offsets, uses the minimal (pc-wrapped) distance. Use this for ranking
    how smooth a move between two *patterns/subsets* is.

    NOTE: the CONCRETE-layer metric for actual voiced chords (absolute MIDI
    pitches, padded to equal length) is
    ``rules.voice_leading.VoiceLeadingRules.calculate_voice_leading_distance``.
    They are deliberately different: pc-space ranking vs absolute-voice sum.
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


def _prime_key(pcs: Iterable[int]) -> Tuple[int, ...]:
    return tuple(_STA.prime_form(sorted(set(p % 12 for p in pcs))))


def complement_pcs(pcs: Iterable[int]) -> FrozenSet[int]:
    """The (12-k)-note complement of a pc-set (mod-12 universe)."""
    return frozenset(set(range(12)) - set(p % 12 for p in pcs))


def _as_tuple(value: Union[str, Tuple[str, ...]]) -> Tuple[str, ...]:
    """Normalise an optional str/scalar-or-tuple metadata field to a tuple."""
    if isinstance(value, str):
        return (value,)
    return tuple(value)


# ---------------------------------------------------------------------------
# Pattern
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Pattern:
    """A named 12TET subset — the chord / pitch pool for one role+unit.

    Abstract layer: no register, no onset grid, no duration. The subset is
    the whole content; realization (concrete layer, ``rules/realize.py``)
    transposes it into a voice register and attaches rhythm.
    """

    id: str
    subset: FrozenSet[int]
    # str is accepted at runtime and normalised to a 1-tuple in __post_init__
    # (legacy positional form ``Pattern(id, subset, "texture")``).
    roles: Union[str, Tuple[str, ...]] = ("harmony",)
    tags: Union[str, Tuple[str, ...]] = ()
    label: str = ""

    def __post_init__(self) -> None:
        # Accept the legacy positional ``Pattern(id, subset, "texture")`` form
        # and normalise to a tuple. Frozen dataclass -> object.__setattr__.
        object.__setattr__(self, "roles", _as_tuple(self.roles))
        object.__setattr__(self, "tags", _as_tuple(self.tags))

    # -- backwards compatibility -------------------------------------------
    @property
    def role_tuple(self) -> Tuple[str, ...]:
        """Roles as a tuple (normalised form)."""
        r = self.roles
        return r if isinstance(r, tuple) else (r,)

    @property
    def tag_tuple(self) -> Tuple[str, ...]:
        """Tags as a tuple (normalised form)."""
        t = self.tags
        return t if isinstance(t, tuple) else (t,)

    @property
    def role(self) -> str:
        """First role (legacy single-role accessor)."""
        rt = self.role_tuple
        return rt[0] if rt else "harmony"

    @property
    def pcs(self) -> FrozenSet[int]:
        return self.subset

    # -- set-theoretic queries --------------------------------------------
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
    def forte(self) -> str:
        """Forte set-class name, e.g. ``"3-11"`` or ``"4-Z15"``."""
        try:
            return _forte_name(self.subset)
        except KeyError:
            return ""

    @property
    def cardinality(self) -> int:
        return len(self.subset)

    @property
    def z_partner(self) -> Optional["Pattern"]:
        """The Z-partner pattern, or ``None`` (see kernel ``z_partner``)."""
        partner = _kernel_z_partner(self.subset)
        if partner is None:
            return None
        return Pattern(f"{self.id}-z", frozenset(partner), self.role_tuple,
                       self.tag_tuple + ("z-partner",))

    # -- transforms --------------------------------------------------------
    @property
    def complement(self) -> "Pattern":
        return Pattern(f"{self.id}-comp", complement_pcs(self.subset),
                       self.roles, self.tags)

    def transposed(self, semitones: int) -> "Pattern":
        return Pattern(self.id,
                       frozenset((p + semitones) % 12 for p in self.subset),
                       self.roles, self.tags)

    def inverted(self) -> "Pattern":
        """Inversion about pitch class 0 (TnI partner of the same class)."""
        return Pattern(self.id,
                       frozenset((12 - p) % 12 for p in self.subset),
                       self.roles, self.tags)

    def __repr__(self) -> str:
        return f"Pattern({self.id}, {sorted(self.subset)}, T={self.tension:.1f})"


# ---------------------------------------------------------------------------
# Standard library — ORDER IS FROZEN (golden MIDI hash depends on it)
# ---------------------------------------------------------------------------

TRIAD_INTERVALS: Dict[str, Tuple[int, ...]] = {
    "maj": (0, 4, 7),
    "min": (0, 3, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
}

TETRAD_INTERVALS: Dict[str, Tuple[int, ...]] = {
    "maj7": (0, 4, 7, 11),
    "min7": (0, 3, 7, 10),
    "dom7": (0, 4, 7, 10),
    "dim7": (0, 3, 6, 9),
    "m7b5": (0, 3, 6, 10),
}


def _triad(root: int, kind: str) -> FrozenSet[int]:
    return frozenset((root + i) % 12 for i in TRIAD_INTERVALS[kind])


def _tetrad(root: int, kind: str) -> FrozenSet[int]:
    return frozenset((root + i) % 12 for i in TETRAD_INTERVALS[kind])


def standard_patterns() -> List[Pattern]:
    """Diatonic anchor set: triads/tetrads on C + symmetric anchors.

    >>> len(standard_patterns())
    91

    DO NOT reorder, renumber or remove entries — the zero-drift golden hash
    is computed from a walk over this exact sequence.
    """
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


def diatonic_degree_patterns(tonic_pc: int = 0) -> Dict[str, str]:
    """Map scale-degree names to pattern ids in the standard library.

    Major scale on tonic_pc: I ii iii IV V vi vii(dim) -> pattern id.
    Returns e.g. {"I": "maj0", "V": "maj7", "vi": "min9"} for tonic C.
    """
    offs = [0, 2, 4, 5, 7, 9, 11]
    names = ["I", "ii", "iii", "IV", "V", "vi", "vii"]
    kinds = ["maj", "min", "min", "maj", "maj", "min", "dim"]
    out: Dict[str, str] = {}
    for name, off, kind in zip(names, offs, kinds):
        root = (tonic_pc + off) % 12
        target = _triad(root, kind)
        for p in standard_patterns():
            if p.subset == target:
                out[name] = p.id
                break
    return out


def patterns_from_degrees(tonic_pc: int = 0,
                          degrees: Sequence[str] = ("I", "V", "vi", "IV")
                          ) -> List[Pattern]:
    """Concrete Pattern objects for a degree progression (pop I-V-vi-IV)."""
    ids = diatonic_degree_patterns(tonic_pc)
    lib = {p.id: p for p in standard_patterns()}
    return [lib[ids[d]] for d in degrees]


# ---------------------------------------------------------------------------
# Catalogues — the library made queryable
# ---------------------------------------------------------------------------

def chromatic_triads() -> List[Pattern]:
    """All 48 triads: 4 qualities x 12 roots.

    >>> len(chromatic_triads())
    48
    """
    return [Pattern(f"{kind}{root}", _triad(root, kind), tags=("chromatic",))
            for root in range(12) for kind in ("maj", "min", "dim", "aug")]


def chromatic_tetrads() -> List[Pattern]:
    """All 60 tetrads: 5 qualities x 12 roots.

    >>> len(chromatic_tetrads())
    60
    """
    return [Pattern(f"{kind}{root}", _tetrad(root, kind), tags=("chromatic",))
            for root in range(12)
            for kind in ("maj7", "min7", "dom7", "dim7", "m7b5")]


# the seven modes, as scale-degree offsets from the tonic
MODE_OFFSETS: Dict[str, Tuple[int, ...]] = {
    "ionian":     (0, 2, 4, 5, 7, 9, 11),
    "dorian":     (0, 2, 3, 5, 7, 9, 10),
    "phrygian":   (0, 1, 3, 5, 7, 8, 10),
    "lydian":     (0, 2, 4, 6, 7, 9, 11),
    "mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "aeolian":    (0, 2, 3, 5, 7, 8, 10),
    "locrian":    (0, 1, 3, 5, 6, 8, 10),
}


def diatonic_sets(tonic_pc: int = 0) -> List[Pattern]:
    """The 7 triads and 7 tetrads of the major scale on *tonic_pc*.

    This is what ``standard_patterns`` gives ids for; here you get the
    Pattern objects themselves, tagged ``"diatonic"``.

    >>> len(diatonic_sets())
    14
    """
    offs = (0, 2, 4, 5, 7, 9, 11)
    kinds = ("maj", "min", "min", "maj", "maj", "min", "dim")
    seventh = ("maj7", "min7", "min7", "maj7", "dom7", "min7", "m7b5")
    roman = ("I", "ii", "iii", "IV", "V", "vi", "vii")
    out: List[Pattern] = []
    for rn, off, k, s in zip(roman, offs, kinds, seventh):
        root = (tonic_pc + off) % 12
        out.append(Pattern(f"dia_{rn}_{root}", _triad(root, k),
                           roles=("harmony",), tags=("diatonic",),
                           label=f"{rn} triad"))
        out.append(Pattern(f"dia_{rn}7_{root}", _tetrad(root, s),
                           roles=("harmony",), tags=("diatonic",),
                           label=f"{rn} seventh"))
    return out


def modal_sets(tonic_pc: int = 0, mode: Optional[str] = None) -> List[Pattern]:
    """The modes as patterns — one per mode, or a single named mode.

    This is System A's "mode" concept done properly: a mode is a 7-note
    pc-set, so it is just a subset like any other and composes with the
    set-theoretic machinery (it has a Forte name — the diatonic collection
    is 7-35).

    >>> len(modal_sets())
    7
    >>> modal_sets(mode="dorian")[0].forte
    '7-35'
    """
    if mode is not None:
        key = mode.strip().lower()
        if key not in MODE_OFFSETS:
            raise KeyError(
                f"unknown mode {mode!r}; expected one of {sorted(MODE_OFFSETS)}"
            )
        modes = [(key, MODE_OFFSETS[key])]
    else:
        modes = sorted(MODE_OFFSETS.items())
    return [
        Pattern(f"{name}{tonic_pc}",
                frozenset((tonic_pc + o) % 12 for o in offs),
                roles=("texture",), tags=("modal", name), label=name)
        for name, offs in modes
    ]


def z_pair_catalogue(cardinality: Optional[int] = None
                     ) -> List[Tuple[Pattern, Pattern]]:
    """The true Forte Z-pairs, as ``(Pattern, Pattern)`` tuples.

    This is the catalogue the architecture was missing: previously only one
    pair (``z0146``/``z0137``) was discoverable, making "swap a chord for its
    Z-partner — same tension, fresh harmony" effectively unusable. All 15
    documented hexachord pairs are here, plus the tetrad, pentad, heptad and
    octad pairs.

    >>> len(z_pair_catalogue())
    23
    >>> len(z_pair_catalogue(6))
    15
    """
    out: List[Tuple[Pattern, Pattern]] = []
    for a, b in all_z_pairs(cardinality):
        sa, sb = sorted(a), sorted(b)
        fa = _forte_name(sa)
        fb = _forte_name(sb)
        out.append((
            Pattern(f"z_{fa}", frozenset(a), tags=("z-pair",)),
            Pattern(f"z_{fb}", frozenset(b), tags=("z-pair",)),
        ))
    return out


def all_hexachords() -> List[Pattern]:
    """All 50 hexachord set classes (complements included).

    >>> len(all_hexachords())
    50
    """
    return [
        Pattern(f"hex_{_forte_name(list(pf))}", frozenset(pf),
                roles=("texture",), tags=("hexachord",))
        for pf in all_sets_of_cardinality(6)
    ]


# named scale pools that are not diatonic modes
SCALE_POOLS: Dict[str, Tuple[int, ...]] = {
    "wholetone":  (0, 2, 4, 6, 8, 10),
    "octatonic":  (0, 1, 3, 4, 6, 7, 9, 10),
    "pentatonic": (0, 2, 4, 7, 9),
    "blues":      (0, 3, 5, 6, 7, 10),
    "lydian_dominant": (0, 2, 4, 6, 7, 9, 10),
    "harmonic_minor":  (0, 2, 3, 5, 7, 8, 11),
    "melodic_minor":   (0, 2, 3, 5, 7, 9, 11),
    "hungarian_minor": (0, 2, 3, 6, 7, 8, 11),
}


def scale_pools(tonic_pc: int = 0, name: Optional[str] = None) -> List[Pattern]:
    """Symmetric and exotic scale pools (wholetone, octatonic, blues, ...).

    >>> len(scale_pools())
    8
    """
    if name is not None:
        key = name.strip().lower()
        if key not in SCALE_POOLS:
            raise KeyError(
                f"unknown scale pool {name!r}; expected {sorted(SCALE_POOLS)}"
            )
        pools = [(key, SCALE_POOLS[key])]
    else:
        pools = sorted(SCALE_POOLS.items())
    return [
        Pattern(f"{nm}{tonic_pc}",
                frozenset((tonic_pc + o) % 12 for o in offs),
                roles=("texture",), tags=("scale-pool", nm), label=nm)
        for nm, offs in pools
    ]


# ---------------------------------------------------------------------------
# Rhythm side — the pattern library's partner for pitch
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RhythmPattern:
    """An onset-cycle rhythm: *cycle* pulses per bar, onsets within it.

    Replaces the opaque ``(cycle, onsets)`` tuple in
    ``structures/timegrid.MusicRhythmPattern`` with a real type that has
    accessors, a density measure and rotation semantics (clave direction
    matters musically, so ``is_rotation_of`` reports it separately from
    equality).
    """

    id: str
    cycle: int
    onsets: Tuple[int, ...]
    tags: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.tags, str):
            object.__setattr__(self, "tags", (self.tags,))
        object.__setattr__(self, "onsets", tuple(int(o) for o in self.onsets))

    @property
    def density(self) -> float:
        """Onsets per pulse (0..1)."""
        return len(self.onsets) / float(self.cycle) if self.cycle else 0.0

    def rotated(self, n: int) -> "RhythmPattern":
        """Rotate the onset set by *n* pulses (wraps within the cycle)."""
        if not self.cycle:
            return self
        shifted = tuple(sorted((o + n) % self.cycle for o in self.onsets))
        return RhythmPattern(f"{self.id}+{n}", self.cycle, shifted, self.tags)

    def is_rotation_of(self, other: "RhythmPattern") -> bool:
        """True if *other* is some rotation of this pattern."""
        if self.cycle != other.cycle or len(self.onsets) != len(other.onsets):
            return False
        target = tuple(sorted(self.onsets))
        return any(tuple(sorted(other.rotated(n).onsets)) == target
                   for n in range(self.cycle))

    def onsets_in_bar(self, bar_ticks: int = 1920) -> List[int]:
        """Absolute ticks of each onset inside one bar."""
        step = bar_ticks / float(self.cycle) if self.cycle else 0.0
        return [int(round(o * step)) for o in self.onsets]

    def __repr__(self) -> str:
        return f"RhythmPattern({self.id}, {self.cycle}, {self.onsets})"


# The 15 named rhythms from structures/timegrid.py, promoted to real objects.
NAMED_RHYTHMS: Dict[str, Tuple[int, Tuple[int, ...]]] = {
    "Tresillo":    (8, (0, 3, 6)),
    "Shiko":       (16, (0, 4, 6, 10, 12)),
    "Soukous":     (16, (0, 3, 6, 10, 11)),
    "Son Clave":   (16, (0, 3, 6, 10, 12)),
    "Rumba":       (16, (0, 3, 7, 10, 12)),
    "Bossa Nova":  (16, (0, 3, 6, 10, 13)),
    "Gahu":        (16, (0, 3, 6, 10, 14)),
    "Samba":       (16, (0, 3, 5, 7, 10, 12, 14)),
    "Fume-fume":   (12, (0, 2, 4, 7, 9)),
    "Bembe":       (12, (0, 2, 4, 5, 7, 9, 11)),
    "Steve Reich": (12, (0, 1, 2, 4, 5, 7, 9, 10)),
    "One":         (8, (0,)),
    "Two":         (8, (0, 4)),
    "Three":       (12, (0, 4, 8)),
    "Four":        (16, (0, 4, 8, 12)),
}

# tag each named rhythm by feel for catalogue queries
_RHYTHM_TAGS: Dict[str, Tuple[str, ...]] = {
    "Tresillo":    ("clave", "ternary"),
    "Shiko":       ("clave",),
    "Soukous":     ("clave", "afro"),
    "Son Clave":   ("clave", "afro"),
    "Rumba":       ("clave", "afro"),
    "Bossa Nova":  ("clave", "latin"),
    "Gahu":        ("afro",),
    "Samba":       ("latin", "afro"),
    "Fume-fume":   ("afro", "ternary"),
    "Bembe":       ("afro", "ternary"),
    "Steve Reich": ("aksak", "phase"),
    "One":         ("pulse",),
    "Two":         ("pulse",),
    "Three":       ("pulse", "ternary"),
    "Four":        ("pulse",),
}


def named_rhythms() -> List[RhythmPattern]:
    """The 15 named rhythms as :class:`RhythmPattern` objects.

    >>> len(named_rhythms())
    15
    """
    return [RhythmPattern(name, cycle, onsets, _RHYTHM_TAGS.get(name, ()))
            for name, (cycle, onsets) in sorted(NAMED_RHYTHMS.items())]


def euclidean_rhythm(k: int, n: int, rotation: int = 0) -> RhythmPattern:
    """Bjorklund's Euclidean rhythm: *k* onsets spread over *n* pulses.

    The same algorithm as ``generators.rhythm.euclidian``, expressed as a
    :class:`RhythmPattern` so it composes with the rhythm network.

    >>> euclidean_rhythm(3, 8).onsets
    (0, 3, 6)
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= k <= n:
        raise ValueError("k must satisfy 0 <= k <= n")
    onsets: List[int] = []
    for i in range(n):
        # Bresenham/floor formulation: exact Euclidean distribution
        if (i * k) % n < k:
            onsets.append(i)
    pat = RhythmPattern(f"E({k},{n})", n, tuple(onsets), ("euclidean",))
    return pat.rotated(rotation) if rotation else pat


def rotation_edges(p: RhythmPattern) -> List[Tuple[int, RhythmPattern]]:
    """Every non-trivial rotation of *p*, with its rotation amount."""
    return [(n, p.rotated(n)) for n in range(1, p.cycle)]


class RhythmPatternNetwork:
    """Rhythm analogue of :class:`~rules.subset_network.PatternNetwork`.

    Edges connect rhythms that are musically related:

    ``rot``      one is a rotation of the other (same onsets, shifted)
    ``compl``    onset sets are complementary within the same cycle
    ``pulse``    same cycle and share every pulse of the sparser one
    ``dens``     close in density (|Δdensity| <= 0.1), same cycle

    Before this, rhythm was a flat dict of 15 tuples with no relations at
    all — the rhythm side had no partner for the pitch network.
    """

    ROT = "rot"
    COMPL = "compl"
    PULSE = "pulse"
    DENS = "dens"

    def __init__(self, patterns: Sequence[RhythmPattern]):
        self.patterns: Dict[str, RhythmPattern] = {p.id: p for p in patterns}
        self.edges: Dict[str, List[Tuple[str, str, float]]] = {
            p.id: [] for p in patterns
        }
        self._build()

    def _build(self) -> None:
        ids = list(self.patterns)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = self.patterns[ids[i]], self.patterns[ids[j]]
                for rel, w in self._relations(a, b):
                    self.edges[a.id].append((b.id, rel, w))
                    self.edges[b.id].append((a.id, rel, w))

    @staticmethod
    def _relations(a: RhythmPattern, b: RhythmPattern
                   ) -> List[Tuple[str, float]]:
        out: List[Tuple[str, float]] = []
        if a.cycle == b.cycle:
            if a.is_rotation_of(b):
                out.append((RhythmPatternNetwork.ROT, 0.5))
            elif set(a.onsets) | set(b.onsets) == set(range(a.cycle)) and \
                    not (set(a.onsets) & set(b.onsets)):
                out.append((RhythmPatternNetwork.COMPL, 1.5))
            elif set(a.onsets) <= set(b.onsets) or set(b.onsets) <= set(a.onsets):
                out.append((RhythmPatternNetwork.PULSE, 0.75))
            elif abs(a.density - b.density) <= 0.1:
                out.append((RhythmPatternNetwork.DENS, 1.0))
        return out

    def neighbors(self, pid: str) -> List[Tuple[str, str, float]]:
        """Related rhythms, sorted by increasing weight (closest first)."""
        return sorted(self.edges.get(pid, []), key=lambda e: e[2])

    def by_tag(self, tag: str) -> List[RhythmPattern]:
        return [p for p in self.patterns.values() if tag in p.tags]


__all__ = [
    # metrics
    "IC_WEIGHT", "interval_vector", "tension", "icv_distance",
    "common_tones", "voice_leading_distance", "complement_pcs",
    # pattern type + standard library
    "Pattern", "standard_patterns", "diatonic_degree_patterns",
    "patterns_from_degrees", "TRIAD_INTERVALS", "TETRAD_INTERVALS",
    # pitch catalogues
    "chromatic_triads", "chromatic_tetrads", "diatonic_sets", "modal_sets",
    "MODE_OFFSETS", "z_pair_catalogue", "all_hexachords", "scale_pools",
    "SCALE_POOLS",
    # rhythm
    "RhythmPattern", "RhythmPatternNetwork", "named_rhythms",
    "euclidean_rhythm", "rotation_edges", "NAMED_RHYTHMS",
]
