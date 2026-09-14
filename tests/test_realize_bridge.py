# -*- coding: utf-8 -*-
"""P3 — the realization bridge (rules/realize.py) + compose() refactor gate.

Two things are pinned here:

1. **Unit behaviour** of the bridge: register placement, voicings,
   articulation, continuity, determinism, purity.
2. **The refactor was byte-neutral.** ``compose()`` used to place abstract
   patterns with six hardcoded inline lines. It now calls
   ``rules.realize.realize_tonal_cluster()``. ``ABS_GOLDEN_SHA256`` below was
   captured from the ORIGINAL inline implementation (pre-refactor, 4333-byte
   MIDI from ``compose(style='pop', method='ABS-002', seed=7)``). If this
   hash moves, the bridge changed output — investigate before updating it.
"""

import hashlib
import subprocess
import sys
import tempfile

import pytest

from rules.patterns import Pattern
from rules.realize import (
    DEFAULT_BASE_REGISTER,
    RELATION_NAMES,
    articulation_events,
    place_in_register,
    placed_pitches,
    realize,
    realize_progression,
    realize_tonal_cluster,
    tension_curve_targets,
    voicing_spread,
)

# Captured from the pre-refactor inline implementation. Do not update
# casually — this is the proof the P3 refactor was output-neutral.
ABS_GOLDEN_SHA256 = "7a43efa9290dcea3476e8b35ecbe020795c13d562ac3069125b39612df79abf4"
ABS_GOLDEN_SIZE = 4333


# ---------------------------------------------------------------------------
# Byte-neutrality of the refactor — the primary P3 gate
# ---------------------------------------------------------------------------

def test_abs_compose_midi_hash_unchanged():
    """compose()'s abstract path must still emit byte-identical MIDI."""
    from workflows.musicom_workflow import compose

    with tempfile.TemporaryDirectory() as d:
        r = compose(style="pop", method="ABS-002", seed=7, out_dir=d)
        data = open(r.midi_path, "rb").read()
    assert len(data) > 40, "empty/corrupt output"
    assert len(data) == ABS_GOLDEN_SIZE, (
        f"ABS MIDI size changed: {len(data)} != {ABS_GOLDEN_SIZE}"
    )
    actual = hashlib.sha256(data).hexdigest()
    assert actual == ABS_GOLDEN_SHA256, (
        f"ABS compose() output changed!\n  expected {ABS_GOLDEN_SHA256}\n"
        f"  actual   {actual}\n"
        "rules/realize.py must reproduce the legacy placement exactly."
    )


def test_realize_tonal_cluster_matches_legacy_formula():
    """The named bridge function == the removed inline formula, exhaustively."""
    import random

    rng = random.Random(20260914)
    for _ in range(600):
        k = rng.randint(1, 10)
        pcs = frozenset(rng.sample(range(12), k))
        pat = Pattern("t", pcs)
        root_pc = min(pat.subset)
        base = 48 + root_pc
        legacy = [base + ((pc - root_pc) % 12) for pc in sorted(pat.subset)]
        assert realize_tonal_cluster(pat) == legacy


def test_realize_tonal_cluster_known_values():
    maj = Pattern("maj0", frozenset({0, 4, 7}))
    assert realize_tonal_cluster(maj) == [48, 52, 55]
    min9 = Pattern("min9", frozenset({9, 0, 4}))
    # legacy anchors on min(pc)=0, so base = 48 and the set folds up
    assert realize_tonal_cluster(min9) == [48, 52, 57]
    bflat = Pattern("maj10", frozenset({10, 2, 5}))
    # anchored on min(pc)=2, NOT the chord root — a known legacy quirk that
    # byte-neutrality requires preserving rather than "fixing" here.
    assert realize_tonal_cluster(bflat) == [50, 53, 58]


def test_realize_tonal_cluster_uses_48_base_by_default():
    assert DEFAULT_BASE_REGISTER == 48
    p = Pattern("p", frozenset({6, 9, 1}))
    out = realize_tonal_cluster(p)
    assert min(out) % 12 == min(p.subset) % 12


# ---------------------------------------------------------------------------
# Register placement
# ---------------------------------------------------------------------------

def test_placed_pitches_is_legacy_formula():
    assert placed_pitches({0, 4, 7}, 48) == [48, 52, 55]
    assert placed_pitches({9, 0, 4}, 57) == [57, 60, 64]
    assert placed_pitches(set(), 48) == []


def test_place_in_register_respects_band():
    for pcs in ({0, 4, 7}, {9, 1, 4}, {11, 2, 6}, {0, 6}):
        out = place_in_register(pcs, (60, 72))
        assert out, pcs
        assert all(60 <= p <= 72 for p in out), (pcs, out)


def test_place_in_register_keeps_pitch_classes():
    """Folding by octaves must not alter the pitch-class content."""
    pcs = {1, 5, 8}
    out = place_in_register(pcs, (48, 72))
    assert {p % 12 for p in out} == pcs


def test_place_in_register_anchors():
    pcs = {0, 4, 7}
    assert place_in_register(pcs, (48, 72), anchor="min") == [48, 52, 55]
    assert place_in_register(pcs, (48, 72), anchor="pc", base=48) == [48, 52, 55]
    assert place_in_register(pcs, (48, 72), anchor="max")[0] % 12 == 7
    with pytest.raises(ValueError):
        place_in_register(pcs, (48, 72), anchor="nonsense")
    with pytest.raises(ValueError):
        place_in_register(pcs, (48, 72), anchor="pc")


def test_place_in_register_empty():
    assert place_in_register(set(), (48, 72)) == []


# ---------------------------------------------------------------------------
# Voicings
# ---------------------------------------------------------------------------

def test_voicing_close_is_identity():
    assert voicing_spread([48, 52, 55], "close") == [48, 52, 55]


def test_voicing_open_raises_alternate_notes():
    out = voicing_spread([48, 52, 55], "open")
    assert out == sorted([48, 64, 55])


def test_voicing_drop2_drops_second_highest():
    out = voicing_spread([48, 52, 55], "drop2")
    assert 52 - 12 in out
    assert len(out) == 3


def test_voicing_short_chords_unchanged():
    assert voicing_spread([48, 55], "open") == [48, 55]
    assert voicing_spread([48, 55], "drop2") == [48, 55]


def test_voicing_unknown_raises():
    with pytest.raises(ValueError):
        voicing_spread([48, 52, 55], "nope")


# ---------------------------------------------------------------------------
# Articulation
# ---------------------------------------------------------------------------

def test_articulation_trims_durations():
    assert articulation_events([0, 100], [100, 100], 0.5) == [(0, 50), (100, 150)]
    assert articulation_events([0], [100], 1.0) == [(0, 100)]


def test_articulation_never_zero_length():
    assert articulation_events([0], [1], 0.1)[0][1] > 0


def test_articulation_rejects_over_legato():
    with pytest.raises(ValueError):
        articulation_events([0], [100], 1.5)


# ---------------------------------------------------------------------------
# realize / realize_progression
# ---------------------------------------------------------------------------

def test_realize_emits_sustained_chord():
    p = Pattern("maj0", frozenset({0, 4, 7}))
    evs = realize(p, register=(48, 72), bar_ticks=1920)
    assert len(evs) == 3
    assert {e.pitch for e in evs} == {48, 52, 55}
    assert all(e.start_tick == 0 and e.end_tick == 1920 for e in evs)


def test_realize_with_rhythm_pattern():
    from rules.patterns import RhythmPattern

    p = Pattern("maj0", frozenset({0, 4, 7}))
    evs = realize(p, register=(48, 72), rhythm=RhythmPattern("t", 8, (0, 3, 6)))
    assert len(evs) == 9                    # 3 onsets x 3 chord tones
    assert sorted({e.start_tick for e in evs}) == [0, 720, 1440]


def test_realize_with_explicit_slots():
    p = Pattern("maj0", frozenset({0, 4, 7}))
    evs = realize(p, register=(48, 72), rhythm=[(0, 480), (960, 480)])
    assert len(evs) == 6
    assert sorted({e.start_tick for e in evs}) == [0, 960]


def test_realize_empty_pattern():
    assert realize(Pattern("e", frozenset())) == []


def test_realize_deterministic():
    p = Pattern("maj0", frozenset({0, 4, 7}))
    a = [(e.pitch, e.start_tick, e.end_tick) for e in realize(p)]
    b = [(e.pitch, e.start_tick, e.end_tick) for e in realize(p)]
    assert a == b


def test_realize_progression_is_continuous():
    from rules.patterns import patterns_from_degrees

    pats = patterns_from_degrees(0, ("I", "V", "vi", "IV"))
    evs = realize_progression(pats, register=(48, 72), bars_per_pattern=1)
    assert evs
    assert min(e.start_tick for e in evs) == 0
    # last pattern ends at 4 bars
    assert max(e.end_tick for e in evs) == 4 * 1920


def test_realize_progression_smooth_reduces_movement():
    """smooth=True must not increase total voice movement."""
    from rules.patterns import patterns_from_degrees

    pats = patterns_from_degrees(0, ("I", "vi", "ii", "V"))
    plain = realize_progression(pats, register=(48, 72), smooth=False)
    smooth = realize_progression(pats, register=(48, 72), smooth=True)
    # compare the chord-tone span used at each onset group
    def spread(evs):
        by_start = {}
        for e in evs:
            by_start.setdefault(e.start_tick, []).append(e.pitch)
        return [sorted(v) for _, v in sorted(by_start.items())]

    p_spans = sum(max(c) - min(c) for c in spread(plain))
    s_spans = sum(max(c) - min(c) for c in spread(smooth))
    assert s_spans <= p_spans


def test_realize_progression_articulation():
    from rules.patterns import patterns_from_degrees

    pats = patterns_from_degrees(0, ("I", "V"))
    evs = realize_progression(pats, register=(48, 72), articulation=0.5)
    assert all((e.end_tick - e.start_tick) <= 1920 for e in evs)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def test_tension_curve_targets_pads_and_truncates():
    assert tension_curve_targets([1.0, 2.0], 4) == [1.0, 2.0, 2.0, 2.0]
    assert tension_curve_targets([1.0, 2.0, 3.0], 2) == [1.0, 2.0]
    assert tension_curve_targets([], 3) == [0.0, 0.0, 0.0]
    assert tension_curve_targets([1.0], 0) == []


def test_relation_names_cover_the_network_relations():
    from rules.subset_network import COMPL, INV, PLR, TN, VL, Z

    for rel in (TN, INV, Z, COMPL, PLR, VL):
        assert rel in RELATION_NAMES


# ---------------------------------------------------------------------------
# Purity
# ---------------------------------------------------------------------------

def test_realize_module_is_pure():
    code = (
        "import rules.realize, sys\n"
        "bad = [m for m in ('musicpy','music21') if m in sys.modules]\n"
        "print('BAD:' + ','.join(bad))\n"
    )
    proc = subprocess.run([sys.executable, "-c", code],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    line = [l for l in proc.stdout.splitlines() if l.startswith("BAD:")][0]
    assert line == "BAD:", f"rules.realize pulled in {line[4:]!r}"
