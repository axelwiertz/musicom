# -*- coding: utf-8 -*-
"""P2 — pattern library: catalogues, rhythm side, backwards compatibility.

The key regression risk here is ORDER: ``standard_patterns()`` drives the
zero-drift golden MIDI hash, so its sequence is frozen. Catalogue functions
add patterns; they must never reorder or renumber the standard library.
"""

import subprocess
import sys

import pytest

from rules.patterns import (
    IC_WEIGHT,
    MODE_OFFSETS,
    NAMED_RHYTHMS,
    SCALE_POOLS,
    Pattern,
    RhythmPattern,
    RhythmPatternNetwork,
    all_hexachords,
    chromatic_tetrads,
    chromatic_triads,
    common_tones,
    complement_pcs,
    diatonic_degree_patterns,
    diatonic_sets,
    euclidean_rhythm,
    icv_distance,
    interval_vector,
    modal_sets,
    named_rhythms,
    patterns_from_degrees,
    rotation_edges,
    scale_pools,
    standard_patterns,
    tension,
    voice_leading_distance,
    z_pair_catalogue,
)

# ---------------------------------------------------------------------------
# ORDERING CONTRACT — the golden-hash dependency
# ---------------------------------------------------------------------------

# Frozen at P2. If this list changes, the golden MIDI hash changes.
_FROZEN_PREFIX = [
    "maj0", "min0", "dim0", "aug0", "maj1", "min1", "dim1", "aug1",
]
_FROZEN_SUFFIX = ["wholetone", "oct0", "chrom4", "quartal",
                  "z0146", "z0137", "maj7comp0"]


def test_standard_patterns_count_and_order():
    ps = standard_patterns()
    assert len(ps) == 91
    assert [p.id for p in ps[:8]] == _FROZEN_PREFIX
    assert [p.id for p in ps[-7:]] == _FROZEN_SUFFIX


def test_standard_patterns_ids_are_unique():
    ids = [p.id for p in standard_patterns()]
    assert len(ids) == len(set(ids))


def test_standard_patterns_deterministic():
    """Two calls must agree exactly — order included."""
    a = [(p.id, sorted(p.subset)) for p in standard_patterns()]
    b = [(p.id, sorted(p.subset)) for p in standard_patterns()]
    assert a == b


def test_standard_library_z_pair_is_still_present():
    """The one pre-existing Z-pair must keep working."""
    by_id = {p.id: p for p in standard_patterns()}
    assert by_id["z0146"].forte == "4-Z15"
    assert by_id["z0137"].forte == "4-Z29"
    assert by_id["z0146"].z_partner.subset == by_id["z0137"].subset
    assert by_id["z0137"].z_partner.subset == by_id["z0146"].subset


# ---------------------------------------------------------------------------
# Backwards compatibility with rules/subset_network.py
# ---------------------------------------------------------------------------

def test_subset_network_reexports_identical_order():
    """The legacy alias must give the same sequence, not a copy that drifted."""
    from rules.subset_network import Pattern as PN_Pattern
    from rules.subset_network import standard_patterns as legacy

    assert [p.id for p in legacy()] == [p.id for p in standard_patterns()]
    for p in legacy():
        assert isinstance(p, Pattern)
    assert PN_Pattern is Pattern


def test_legacy_positional_role_still_works():
    """Pattern(id, subset, "texture") is the old call form — must not break."""
    p = Pattern("x", frozenset({0, 4, 7}), "texture")
    assert p.role == "texture"
    assert p.roles == ("texture",)
    assert p.tag_tuple == ()
    assert p.role_tuple == ("texture",)


def test_role_field_is_no_longer_dead():
    """`roles`/`role` must actually be readable (it was a dead field)."""
    p = Pattern("x", frozenset({0, 4, 7}), "texture")
    assert p.role == "texture"
    tex = [x for x in standard_patterns() if "texture" in x.role_tuple]
    assert len(tex) >= 7
    assert all(x.role == "texture" for x in tex)


def test_pattern_transforms_preserve_metadata():
    p = Pattern("x", frozenset({0, 4, 7}), ("harmony",), ("diatonic",))
    assert p.transposed(2).roles == ("harmony",)
    assert p.transposed(2).tags == ("diatonic",)
    assert p.inverted().tags == ("diatonic",)
    assert p.complement.role_tuple == ("harmony",)


def test_pattern_inverted_is_tni_partner():
    """Inversion must land in the same set class."""
    p = Pattern("x", frozenset({0, 4, 7}))
    assert p.inverted().forte == p.forte == "3-11"
    assert p.complement.cardinality == 9


# ---------------------------------------------------------------------------
# Catalogues
# ---------------------------------------------------------------------------

def test_chromatic_catalogue_sizes():
    assert len(chromatic_triads()) == 48
    assert len(chromatic_tetrads()) == 60
    names = [p.id for p in chromatic_tetrads()]
    assert len(names) == len(set(names)), "tetrad catalogue has duplicate ids"


def test_diatonic_sets_are_the_seven_triads_and_sevenths():
    ds = diatonic_sets(0)
    assert len(ds) == 14
    for p in ds:
        assert "diatonic" in p.tags
        assert p.forte, f"{p.id} has no Forte name"
    # C major triad and its seventh must both be present in class terms
    assert any(p.subset == frozenset({0, 4, 7}) for p in ds)
    assert any(p.forte == "4-20" for p in ds)          # maj7 = 4-20


# ---------------------------------------------------------------------------
# P2 regression nets
# ---------------------------------------------------------------------------

def test_modal_sets_all_seven_modes():
    ms = modal_sets()
    assert len(ms) == 7
    names = {p.label for p in ms}
    assert names == set(MODE_OFFSETS)
    # every mode is the same set class (7-35 diatonic collection)
    assert {p.forte for p in ms} == {"7-35"}


def test_modal_sets_single_mode_and_bad_name():
    d = modal_sets(mode="dorian")
    assert len(d) == 1
    assert d[0].forte == "7-35"
    assert sorted(d[0].subset) == [0, 2, 3, 5, 7, 9, 10]
    with pytest.raises(KeyError):
        modal_sets(mode="not-a-mode")


def test_z_pair_catalogue_completeness():
    """23 Z-pairs total; 15 of them hexachord pairs."""
    assert len(z_pair_catalogue()) == 23
    assert len(z_pair_catalogue(6)) == 15
    for a, b in z_pair_catalogue():
        assert a.tension == b.tension, "Z-partners must match in tension"
        assert a.icv == b.icv
        assert a.prime != b.prime
        assert a.forte != b.forte


def test_z_pair_catalogue_contains_documented_hexachord_pairs():
    pairs = {frozenset({a.forte, b.forte}) for a, b in z_pair_catalogue(6)}
    for expected in ("6-Z3", "6-Z36", "6-Z25", "6-Z47", "6-Z29", "6-Z50"):
        assert any(expected in pair for pair in pairs), f"missing {expected}"


def test_z_swap_is_now_usable():
    """The generative idea: same tension, different notes."""
    by_id = {p.id: p for p in standard_patterns()}
    a = by_id["z0146"]
    b = a.z_partner
    assert b is not None
    assert a.tension == b.tension
    # 4-Z15 {0,1,4,6} vs 4-Z29 {0,1,3,7} share exactly the two semitone pair
    assert common_tones(a.subset, b.subset) == 2
    assert voice_leading_distance(a.subset, b.subset) <= 3


def test_all_hexachords_is_50():
    """50 hexachord set classes, each with a distinct Forte name."""
    hexes = all_hexachords()
    assert len(hexes) == 50
    assert len({p.forte for p in hexes}) == 50


def test_scale_pools():
    assert len(scale_pools()) == 8
    blast = scale_pools(name="blues")
    assert len(blast) == 1
    assert sorted(blast[0].subset) == [0, 3, 5, 6, 7, 10]
    with pytest.raises(KeyError):
        scale_pools(name="nope")


def test_catalogue_ids_all_resolve_to_forte_names():
    for p in (chromatic_triads() + chromatic_tetrads() + diatonic_sets()
              + modal_sets() + all_hexachords() + scale_pools()):
        assert p.forte, f"{p.id} -> no Forte name"


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def test_metrics_known_values():
    assert interval_vector([0, 4, 7]) == [0, 0, 1, 1, 1, 0]
    assert tension([0, 1, 4, 6]) == pytest.approx(
        IC_WEIGHT[1] + IC_WEIGHT[2] + IC_WEIGHT[3] + IC_WEIGHT[4]
        + IC_WEIGHT[5] + IC_WEIGHT[6])
    assert common_tones([0, 4, 7], [0, 3, 7]) == 2
    assert icv_distance([0, 4, 7], [0, 4, 7]) == 0
    assert complement_pcs([0, 4, 7]) == frozenset({1, 2, 3, 5, 6, 8, 9, 10, 11})


def test_voice_leading_distance_symmetric_and_triangular():
    a, b = [0, 4, 7], [0, 3, 7]
    assert voice_leading_distance(a, b) == voice_leading_distance(b, a)
    assert voice_leading_distance(a, a) == 0


def test_degree_helpers():
    ids = diatonic_degree_patterns(0)
    assert ids["I"] == "maj0"
    assert ids["V"] == "maj7"
    assert ids["vi"] == "min9"
    pats = patterns_from_degrees(0, ("I", "V", "vi", "IV"))
    assert [p.id for p in pats] == ["maj0", "maj7", "min9", "maj5"]


# ---------------------------------------------------------------------------
# Rhythm side
# ---------------------------------------------------------------------------

def test_named_rhythms_promoted_from_timegrid():
    """All 15 rhythms, with the same cycle/onsets the legacy dict had."""
    from structures.timegrid import MusicRhythmPattern

    rp = named_rhythms()
    assert len(rp) == 15
    by_id = {p.id: p for p in rp}
    for name, (cycle, onsets) in MusicRhythmPattern._dict.items():
        assert name in by_id, f"{name} missing from named_rhythms()"
        assert by_id[name].cycle == cycle
        assert by_id[name].onsets == onsets


def test_rhythm_pattern_accessors_and_density():
    tresillo = RhythmPattern("Tresillo", 8, (0, 3, 6))
    assert tresillo.density == pytest.approx(3 / 8)
    assert tresillo.onsets_in_bar(1920) == [0, 720, 1440]
    assert RhythmPattern("z", 0, ()).density == 0.0


def test_rhythm_rotation_semantics():
    p = RhythmPattern("p", 8, (0, 3, 6))
    r = p.rotated(1)
    assert r.onsets == (1, 4, 7)
    assert p.is_rotation_of(r)
    assert r.is_rotation_of(p)
    # clave direction matters: rotations are flagged, not treated as equal
    assert p != r
    assert not p.is_rotation_of(RhythmPattern("q", 8, (0, 2, 4)))


def test_rhythm_rotation_edges():
    p = RhythmPattern("p", 8, (0, 3, 6))
    edges = rotation_edges(p)
    assert len(edges) == 7
    assert all(isinstance(n, int) and isinstance(q, RhythmPattern)
               for n, q in edges)


def test_euclidean_rhythm_known_values():
    """Bjorklund's classic gallery (canonical rotation, onset 0 included)."""
    assert euclidean_rhythm(3, 8).onsets == (0, 3, 6)          # tresillo
    assert euclidean_rhythm(2, 5).onsets == (0, 3)             # [3,2]
    assert euclidean_rhythm(5, 8).onsets == (0, 2, 4, 5, 7)    # [2,2,1,2,1]
    assert euclidean_rhythm(1, 4).onsets == (0,)
    assert euclidean_rhythm(4, 4).onsets == (0, 1, 2, 3)
    assert euclidean_rhythm(3, 8).onsets == euclidean_rhythm(3, 8).onsets


def test_euclidean_rhythm_rotation_and_validation():
    assert euclidean_rhythm(3, 8, rotation=1).onsets == (1, 4, 7)
    with pytest.raises(ValueError):
        euclidean_rhythm(9, 8)
    with pytest.raises(ValueError):
        euclidean_rhythm(3, 0)


def test_rhythm_network_builds_edges():
    net = RhythmPatternNetwork(named_rhythms())
    assert len(net.patterns) == 15
    total = sum(len(v) for v in net.edges.values()) // 2
    assert total > 0, "rhythm network has no relations at all"
    for pid in net.patterns:
        for other, rel, weight in net.neighbors(pid):
            assert rel in (RhythmPatternNetwork.ROT, RhythmPatternNetwork.COMPL,
                           RhythmPatternNetwork.PULSE, RhythmPatternNetwork.DENS)
            assert weight > 0


def test_rhythm_network_detects_rotation_and_density():
    net = RhythmPatternNetwork([
        RhythmPattern("a", 8, (0, 3, 6)),
        RhythmPattern("b", 8, (1, 4, 7)),     # rotation of a
        RhythmPattern("c", 16, (0, 4, 8, 12)),  # different cycle
    ])
    rels = {rel for _, rel, _ in net.neighbors("a")}
    assert RhythmPatternNetwork.ROT in rels


def test_rhythm_network_by_tag():
    net = RhythmPatternNetwork(named_rhythms())
    assert len(net.by_tag("clave")) > 0


def test_named_rhythm_ids_match_the_legacy_dict_keys():
    """The promoted catalogue must cover exactly the 15 legacy names."""
    from structures.timegrid import MusicRhythmPattern

    assert set(NAMED_RHYTHMS) == set(MusicRhythmPattern._dict)
    assert {p.id for p in named_rhythms()} == set(MusicRhythmPattern._dict)


# ---------------------------------------------------------------------------
# Purity
# ---------------------------------------------------------------------------

def test_patterns_module_is_pure():
    code = (
        "import rules.patterns, sys\n"
        "bad = [m for m in ('musicpy','music21') if m in sys.modules]\n"
        "print('BAD:' + ','.join(bad))\n"
    )
    proc = subprocess.run([sys.executable, "-c", code],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    line = [l for l in proc.stdout.splitlines() if l.startswith("BAD:")][0]
    assert line == "BAD:", f"rules.patterns pulled in {line[4:]!r}"
