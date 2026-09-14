# -*- coding: utf-8 -*-
"""P1 — set-theory kernel: Forte names, Z-relations, enumeration, purity.

The reference values here are independent music-theory facts (Forte 1973,
Straus), not values copied out of the implementation.
"""

import subprocess
import sys
from itertools import combinations

import pytest

from rules.set_theory import (
    CARDINALITY_RANGE,
    all_sets_of_cardinality,
    all_z_pairs,
    forte_name,
    icv_signature,
    interval_vector,
    normal_form,
    pcs_from_forte,
    prime_form,
    set_class_key,
    z_partner,
    z_related,
)

# ---------------------------------------------------------------------------
# Existing kernel behaviour (regression: must not change)
# ---------------------------------------------------------------------------

def test_prime_form_known_values():
    assert prime_form([0, 4, 7]) == [0, 3, 7]        # major triad = 3-11
    assert prime_form([0, 3, 7]) == [0, 3, 7]        # minor triad = 3-11
    assert prime_form([0, 3, 6]) == [0, 3, 6]        # dim triad = 3-10
    assert prime_form([0, 4, 8]) == [0, 4, 8]        # aug triad = 3-12
    assert prime_form([0, 1, 4, 6]) == [0, 1, 4, 6]  # 4-Z15


def test_interval_vector_known_values():
    # subset_theory.md identities
    assert interval_vector([0, 4, 7]) == [0, 0, 1, 1, 1, 0]
    assert interval_vector([0, 3, 6, 9]) == [0, 0, 4, 0, 0, 2]   # 4-28 dim7
    assert interval_vector([0, 1, 4, 6]) == [1, 1, 1, 1, 1, 1]   # 4-Z15


def test_prime_form_is_tn_tni_invariant():
    """Every transposition and inversion must map to the same prime form."""
    for k in (3, 4, 5):
        for combo in list(combinations(range(12), k))[:120]:
            pf = tuple(prime_form(list(combo)))
            for t in range(12):
                tr = [(p + t) % 12 for p in combo]
                assert tuple(prime_form(tr)) == pf
            inv = [(12 - p) % 12 for p in combo]
            assert tuple(prime_form(inv)) == pf


def test_set_class_count_is_220():
    """Total set classes of cardinality 2..10 is 220 (Forte/Straus)."""
    assert sum(len(all_sets_of_cardinality(k)) for k in CARDINALITY_RANGE) == 220


@pytest.mark.parametrize(
    "k,expected",
    [(2, 6), (3, 12), (4, 29), (5, 38), (6, 50),
     (7, 38), (8, 29), (9, 12), (10, 6)],
)
def test_set_class_counts_per_cardinality(k, expected):
    assert len(all_sets_of_cardinality(k)) == expected


def test_cardinality_symmetry():
    """Complementary cardinalities have equal class counts."""
    for k in (2, 3, 4, 5):
        assert len(all_sets_of_cardinality(k)) == len(all_sets_of_cardinality(12 - k))


# ---------------------------------------------------------------------------
# Forte names
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "pcs,expected",
    [
        ([0, 4, 7], "3-11"),        # major triad
        ([0, 3, 7], "3-11"),        # minor triad (same class)
        ([0, 3, 6], "3-10"),        # diminished triad
        ([0, 4, 8], "3-12"),        # augmented triad
        ([0, 1, 4, 6], "4-Z15"),
        ([0, 1, 3, 7], "4-Z29"),
        ([0, 3, 6, 9], "4-28"),     # fully diminished seventh
        ([0, 4, 7, 11], "4-20"),    # major seventh
        ([0, 2, 4, 5, 7, 9, 11], "7-35"),   # diatonic collection
        ([0, 2, 4, 6, 8, 10], "6-35"),      # whole-tone
    ],
)
def test_forte_name_known_values(pcs, expected):
    assert forte_name(pcs) == expected


def test_forte_name_is_transposition_invariant():
    for pcs in ([0, 4, 7], [0, 1, 4, 6], [0, 2, 4, 5, 7, 9, 11]):
        base = forte_name(pcs)
        for t in range(12):
            assert forte_name([(p + t) % 12 for p in pcs]) == base


def test_forte_name_rejects_singletons_and_empty():
    with pytest.raises(KeyError):
        forte_name([0])
    with pytest.raises(KeyError):
        forte_name([])
    with pytest.raises(KeyError):
        forte_name(range(11))


def test_pcs_from_forte_roundtrip_all_220():
    """Every set class round-trips name -> pcs -> name."""
    for k in CARDINALITY_RANGE:
        for pf in all_sets_of_cardinality(k):
            name = forte_name(list(pf))
            back = pcs_from_forte(name)
            assert forte_name(sorted(back)) == name, f"{pf} -> {name}"


def test_pcs_from_forte_tolerates_case_and_space():
    assert pcs_from_forte("4-z15") == pcs_from_forte("4-Z15")
    assert pcs_from_forte("  4-Z15  ") == pcs_from_forte("4-Z15")
    assert sorted(pcs_from_forte("3-11")) == [0, 3, 7]


def test_pcs_from_forte_unknown_raises():
    with pytest.raises(KeyError):
        pcs_from_forte("99-99")
    with pytest.raises(KeyError):
        pcs_from_forte("not-a-name")


def test_forte_names_are_unique():
    from rules.forte_table import FORTE_NAMES

    names = list(FORTE_NAMES.values())
    assert len(names) == len(set(names)) == 220


# ---------------------------------------------------------------------------
# Z-relations
# ---------------------------------------------------------------------------

def test_all_z_pairs_totals_23():
    """23 Z-pairs across cardinalities 2..10 (1 tetrad, 3 pentad, 15 hexachord,
    3 heptad, 1 octad)."""
    pairs = all_z_pairs()
    assert len(pairs) == 23
    from collections import Counter

    assert Counter(len(a) for a, _ in pairs) == {6: 15, 5: 3, 7: 3, 4: 1, 8: 1}


def test_fifteen_hexachord_z_pairs():
    """subset_theory.md documents exactly 15 hexachord Z-pairs."""
    assert len(all_z_pairs(6)) == 15
    names = {frozenset({forte_name(sorted(a)), forte_name(sorted(b))})
             for a, b in all_z_pairs(6)}
    for expected in ("6-Z3", "6-Z36", "6-Z29", "6-Z50", "6-Z44"):
        assert any(expected in pair for pair in names), expected


def test_canonical_z_pair_4z15_4z29():
    assert z_partner([0, 1, 4, 6]) == frozenset({0, 1, 3, 7})
    assert z_partner([0, 1, 3, 7]) == frozenset({0, 1, 4, 6})
    assert z_related([0, 1, 4, 6], [0, 1, 3, 7])


def test_z_pairs_share_icv_and_differ_in_class():
    for a, b in all_z_pairs():
        assert icv_signature(a) == icv_signature(b)
        assert set_class_key(a) != set_class_key(b)
        assert prime_form(sorted(a)) != prime_form(sorted(b))


def test_z_partner_none_for_non_z_sets():
    assert z_partner([0, 4, 7]) is None       # 3-11 has no Z-partner
    assert z_partner([0, 2, 4, 6, 8, 10]) is None  # 6-35 whole-tone
    assert not z_related([0, 4, 7], [0, 3, 7])     # Tn-related, not Z


def test_z_partner_is_symmetric_all_23():
    for a, b in all_z_pairs():
        assert z_partner(sorted(a)) == b
        assert z_partner(sorted(b)) == a


def test_z_related_ignores_register_and_transposition():
    # transposition of a Z-set is still Z-related to the partner
    a = [(p + 7) % 12 for p in (0, 1, 4, 6)]
    assert z_related(a, [0, 1, 3, 7])


# ---------------------------------------------------------------------------
# Keys and purity
# ---------------------------------------------------------------------------

def test_icv_signature_hashable():
    assert icv_signature([0, 4, 7]) == (0, 0, 1, 1, 1, 0)
    assert len({icv_signature([0, 4, 7]) for _ in range(3)}) == 1


def test_set_class_key_ignores_convention():
    """Forte and Rahn representatives of 5-20 must share a key."""
    forte_rep = (0, 1, 3, 7, 8)     # Forte's own normal order
    rahn_rep = (0, 1, 5, 6, 8)      # modern rule
    assert set_class_key(forte_rep) == set_class_key(rahn_rep)


def test_icv_between_2_and_10_is_self_consistent():
    """ICV entry count matches k*(k-1)/2 (one per unordered pair)."""
    for k in CARDINALITY_RANGE:
        for pf in all_sets_of_cardinality(k)[:12]:
            assert sum(interval_vector(list(pf))) == k * (k - 1) // 2


def test_kernel_is_import_pure():
    """rules.set_theory must not require musicpy/music21."""
    code = (
        "import rules.set_theory, sys\n"
        "bad = [m for m in ('musicpy','music21') if m in sys.modules]\n"
        "print('BAD:' + ','.join(bad))\n"
    )
    proc = subprocess.run([sys.executable, "-c", code],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    line = [l for l in proc.stdout.splitlines() if l.startswith("BAD:")][0]
    assert line == "BAD:", f"kernel pulled in {line[4:]!r}"


def test_forte_table_is_pure_data():
    """The generated table must not pull in musicpy/music21."""
    code = (
        "import rules.forte_table as t, sys\n"
        "print('NAMES:', len(t.FORTE_NAMES))\n"
        "print('HEAVY:', [m for m in ('musicpy','music21') if m in sys.modules])\n"
    )
    proc = subprocess.run([sys.executable, "-c", code],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert "NAMES: 220" in proc.stdout
    assert "HEAVY: []" in proc.stdout


def test_normal_form_handles_edge_cases():
    assert normal_form([]) == []
    assert normal_form([7]) == [7]
    # normal order of {0,4,7} is itself (span 7 beats 8 and 9); it is
    # prime_form — not normal_form — that reweights to [0,3,7].
    assert normal_form([0, 0, 4, 4, 7]) == [0, 4, 7]
    assert prime_form([0, 0, 4, 4, 7]) == [0, 3, 7]
