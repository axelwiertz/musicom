"""
Pitch Class Set Theory Analysis — canonical set-theory kernel.
Based on Straus, Forte, and the documents in in/Docs (Analyzing Atonal Music).

This module is the SINGLE canonical implementation of normal form, prime
form, interval-class vector, Forte naming and Z-relation lookup. Other
modules delegate here:

    structures/intervals.py   (set_prime_form, interval_class_vector, z_related)
    rules/subset_network.py   (interval_vector, Pattern.prime)
    rules/patterns.py         (Pattern.forte, Pattern.z_partner)

Do not add a second implementation elsewhere — import from here.

PURITY INVARIANT
----------------
This module is pure: no engine imports, no MIDI, no I/O, and crucially no
``musicpy``/``music21``. The static Forte name table lives in
``rules/forte_table.py`` (generated at build time, pure data) precisely so
that naming a set class never requires a heavy dependency at runtime.
``tests/test_set_theory_kernel.py`` pins this.
"""

from typing import Dict, FrozenSet, Iterable, List, Optional, Tuple
import itertools

from rules.forte_table import FORTE_NAMES, FORTE_PRIME_FORMS

# Universe of pitch classes.
PITCH_CLASSES: Tuple[int, ...] = tuple(range(12))

# Cardinalities for which set classes are enumerated (pairs through the
# self-complementary 10-note sets; complements of 2..6).
CARDINALITY_RANGE: Tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 10)


# ---------------------------------------------------------------------------
# Normal form / prime form / interval-class vector
# ---------------------------------------------------------------------------

def normal_form(pcs: Iterable[int]) -> List[int]:
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
    def normal_form(pcs: Iterable[int]) -> List[int]:
        return normal_form(pcs)

    @staticmethod
    def prime_form(pcs: Iterable[int]) -> List[int]:
        """Canonical Prime Form (transposed to 0 and most left-packed)."""
        return prime_form(pcs)

    @staticmethod
    def interval_vector(pcs: Iterable[int]) -> List[int]:
        """ICV of a pc-set: counts of interval classes 1 through 6."""
        return interval_vector(pcs)


def interval_vector(pcs: Iterable[int]) -> List[int]:
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


def prime_form(pcs: Iterable[int]) -> List[int]:
    """Canonical prime form (transposed to 0, most left-packed).

    Uses the modern Rahn/Straus normal-order rule. For six set classes this
    picks a different representative than Forte's original tables; the Forte
    *name* for such a set is still correct (see ``forte_name`` and
    ``rules/forte_table.py``).
    """
    if not pcs:
        return []
    nf = normal_form(pcs)
    # nf is already 0-based; compute the inversion's normal form
    inv = normal_form([(12 - p) % 12 for p in nf])
    # Choose the more "left-packed" one (element-wise, smaller wins)
    if inv < nf:
        return inv
    return nf


# ---------------------------------------------------------------------------
# Canonical keys — for hashing, grouping and set-class identity
# ---------------------------------------------------------------------------

def _canonical_pcs(pcs: Iterable[int]) -> Tuple[int, ...]:
    """Sorted unique pitch classes, deduplicated mod 12."""
    return tuple(sorted(set(p % 12 for p in pcs)))


def icv_signature(pcs: Iterable[int]) -> Tuple[int, ...]:
    """The interval-class vector as a hashable tuple.

    Two sets with equal ``icv_signature`` have identical interval content;
    if their prime forms differ they are Z-related. Hashable, so it can key
    a dict when grouping a catalogue by colour.
    """
    return tuple(interval_vector(pcs))


def set_class_key(pcs: Iterable[int]) -> Tuple[int, ...]:
    """A convention-neutral Tn/TnI invariant key for a set class.

    The lexicographically smallest sorted tuple across all 12 transpositions
    of the set *and* of its inversion. Unlike :func:`prime_form` this does not
    commit to any particular representative convention, so it can be used to
    match set classes across libraries that disagree (Forte vs Rahn).
    """
    s = _canonical_pcs(pcs)
    if not s:
        return ()
    best: Optional[Tuple[int, ...]] = None
    for t in range(12):
        for variant in (s, tuple((12 - x) % 12 for x in s)):
            cand = tuple(sorted((x + t) % 12 for x in variant))
            if best is None or cand < best:
                best = cand
    return best if best is not None else ()


# ---------------------------------------------------------------------------
# Forte names
# ---------------------------------------------------------------------------

def forte_name(pcs: Iterable[int]) -> str:
    """The Forte set-class name for a pitch-class set.

    ``{0,4,7}`` -> ``"3-11"``, ``{0,1,4,6}`` -> ``"4-Z15"``. Z-related sets
    carry the ``Z`` infix. Raises ``KeyError`` for cardinalities outside
    2..10 (empty, singleton and 11-note sets have no Forte class of their
    own: 11-note sets are complements of singletons).

    The table is generated at build time from music21's authoritative Forte
    list (see ``scripts/gen_forte_table.py``) and baked into
    ``rules/forte_table.py`` as pure data — this function needs no dependency.
    """
    pf = tuple(prime_form(pcs))
    if len(pf) < 2:
        raise KeyError(
            f"no Forte set class for cardinality {len(pf)} "
            f"(set {sorted(set(p % 12 for p in pcs))})"
        )
    try:
        return FORTE_NAMES[pf]
    except KeyError:
        # Fall back to a convention-neutral lookup: the kernel picked a
        # representative whose prime form may not be the table key, but the
        # set class is still in the table under *some* key. Rebuild the key
        # from the set class and scan (rare; only for unusual inputs).
        for key, name in FORTE_NAMES.items():
            if set_class_key(key) == set_class_key(pcs):
                return name
        raise


def pcs_from_forte(name: str) -> FrozenSet[int]:
    """Inverse of :func:`forte_name` — ``"4-Z15"`` -> ``frozenset({0,1,4,6})``.

    Accepts the ``Z`` infix case-insensitively and tolerates whitespace.
    Returns the *prime form* as a frozenset of pitch classes (register-free).
    """
    key = name.strip().upper()
    if key not in FORTE_PRIME_FORMS:
        available = sorted(FORTE_PRIME_FORMS)
        raise KeyError(
            f"unknown Forte set class {name!r}; "
            f"expected one of {len(available)} names like '3-11' or '4-Z15'"
        )
    return frozenset(FORTE_PRIME_FORMS[key])


def all_sets_of_cardinality(k: int) -> List[Tuple[int, ...]]:
    """Every distinct set class of cardinality *k*, as prime-form tuples.

    Sorted lexicographically. Cardinalities 2..10 are supported:
    ``len(all_sets_of_cardinality(3)) == 12``,
    ``len(all_sets_of_cardinality(6)) == 50``.
    """
    if k not in CARDINALITY_RANGE:
        raise ValueError(
            f"cardinality must be one of {list(CARDINALITY_RANGE)}, got {k}"
        )
    classes = {
        tuple(prime_form(list(combo)))
        for combo in itertools.combinations(PITCH_CLASSES, k)
    }
    return sorted(classes)


def z_partner(pcs: Iterable[int]) -> Optional[FrozenSet[int]]:
    """The Z-partner of a pitch-class set, or ``None`` if it has none.

    Z-related sets share an identical interval-class vector but are neither
    transpositions nor inversions of one another — same colour, different
    notes. This is the lookup that makes "swap a chord for its Z-partner"
    usable without building a whole :class:`~rules.subset_network.PatternNetwork`.

    Returns a frozenset of pitch classes in normal form, or ``None``. For
    sets whose complement is the Z-partner, the complement is returned.
    """
    s = _canonical_pcs(pcs)
    if len(s) < 2:
        return None
    target = icv_signature(s)
    mine = set_class_key(s)
    for k in CARDINALITY_RANGE:
        for candidate in all_sets_of_cardinality(k):
            if set_class_key(candidate) == mine:
                continue
            if icv_signature(candidate) == target:
                return frozenset(candidate)
    return None


def z_related(a: Iterable[int], b: Iterable[int]) -> bool:
    """True if *a* and *b* are Z-related (same ICV, different set class)."""
    sa, sb = _canonical_pcs(a), _canonical_pcs(b)
    if set_class_key(sa) == set_class_key(sb):
        return False
    return icv_signature(sa) == icv_signature(sb)


def all_z_pairs(k: Optional[int] = None) -> List[Tuple[FrozenSet[int], FrozenSet[int]]]:
    """Every Z-pair, optionally restricted to cardinality *k*.

    Each pair appears once, ordered by prime form. Cardinality 6 has the
    fifteen classic hexachord Z-pairs; cardinality 4 has the canonical
    4-Z15 / 4-Z29. Total across cardinalities 2..10: **23 pairs**.
    """
    cards = [k] if k is not None else list(CARDINALITY_RANGE)
    out: List[Tuple[FrozenSet[int], FrozenSet[int]]] = []
    for card in cards:
        groups: Dict[Tuple[int, ...], List[Tuple[int, ...]]] = {}
        for pf in all_sets_of_cardinality(card):
            groups.setdefault(icv_signature(pf), []).append(pf)
        for icv in sorted(groups):
            members = sorted(groups[icv])
            if len(members) < 2:
                continue
            if len(members) == 2:
                out.append((frozenset(members[0]), frozenset(members[1])))
            else:
                # >2 sets sharing an ICV: emit every unordered combination so
                # no relation is silently dropped.
                for a, b in itertools.combinations(members, 2):
                    out.append((frozenset(a), frozenset(b)))
    return out
