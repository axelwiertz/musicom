# -*- coding: utf-8 -*-
"""P1 gate — tiered pitch discipline + tagged chromatic ornaments.

Pins the VOICE_ROLE_WORKFLOW_PLAN.md P1 invariant:
  every pitched note is EITHER
    (a) in-scale AND in-chord,  OR
    (b) tagged chromatic_ornament AND resolves by step to a scale tone
        within 1 grid step

Three gates (same as the module demos, but as permanent regression tests):
  1. a tagged chromatic passing tone -> 0 un-tagged, 1 tagged+resolving, PASS
  2. a tagged ornament whose target never arrives -> tagged non-resolving, FAIL
  3. an un-tagged out-of-scale note -> un-tagged, FAIL
Plus unit tests for classify_weight, tiered_quantize, the ornament
constructors, and resolve_by_step.
"""

import pytest

from sound.synthesis.scale_quantizer import (
    ScaleQuantizer, STRONG_GRID, StructuralNote, classify_weight,
)
from rules.ornament import (
    approach_note, chromatic_neighbor, chromatic_passing_tone,
    is_chromatic, is_step, resolve_by_step, secondary_leading_tone,
)
from workflows.pitch_audit import audit_voice

C_MAJOR = [0, 2, 4, 5, 7, 9, 11]


# ---------------------------------------------------------------------------
# classify_weight
# ---------------------------------------------------------------------------

def test_classify_weight_grid_default():
    assert classify_weight(0, STRONG_GRID["4/4"]) == "strong"       # beat 1
    assert classify_weight(960, STRONG_GRID["4/4"]) == "strong"     # beat 3
    assert classify_weight(480, STRONG_GRID["4/4"]) == "weak"       # beat 2
    assert classify_weight(1440, STRONG_GRID["4/4"]) == "weak"      # beat 4


def test_classify_weight_wraps_across_bars():
    # onset 1920 == bar 2 beat 1 -> strong
    assert classify_weight(1920, STRONG_GRID["4/4"]) == "strong"
    assert classify_weight(1920 + 480, STRONG_GRID["4/4"]) == "weak"


def test_classify_weight_tag_overrides_grid():
    # fork 1: method tag wins over the grid default
    assert classify_weight(480, STRONG_GRID["4/4"], tagged_weight="strong") == "strong"
    assert classify_weight(0, STRONG_GRID["4/4"], tagged_weight="weak") == "weak"


def test_classify_weight_other_time_sigs():
    assert classify_weight(0, STRONG_GRID["3/4"]) == "strong"
    assert classify_weight(480, STRONG_GRID["3/4"]) == "weak"       # beat 2 of 3/4


# ---------------------------------------------------------------------------
# tiered_quantize
# ---------------------------------------------------------------------------

def test_tiered_quantize_strong_snaps_to_scale_and_chord():
    sq = ScaleQuantizer(root=60, scale="major")
    # 61 (C#) is chromatic in C major; strong snaps to scale (62 D) then chord
    out = sq.tiered_quantize(61.0, weight="strong", chord_tones=[60, 64, 67])
    assert out in (60, 64, 67)              # chord tone
    assert out % 12 in C_MAJOR              # and in scale


def test_tiered_quantize_weak_snaps_to_scale_only():
    sq = ScaleQuantizer(root=60, scale="major")
    # weak note snaps to nearest scale degree (62 D), chord tones don't force it
    out = sq.tiered_quantize(61.0, weight="weak", chord_tones=[60, 64, 67])
    assert out % 12 in C_MAJOR
    # D is not a chord tone of C major — proves chord snap was NOT applied
    assert out % 12 not in (0, 4, 7)


def test_tiered_quantize_weak_without_chord_returns_scale_degree():
    sq = ScaleQuantizer(root=60, scale="major")
    out = sq.tiered_quantize(61.0, weight="weak")
    assert out % 12 in C_MAJOR


def test_structural_note_tags():
    n = StructuralNote(pitch=61, weight="weak", ornament="passing",
                       start_tick=240, end_tick=480)
    assert n.pitch == 61 and n.weight == "weak" and n.ornament == "passing"


# ---------------------------------------------------------------------------
# ornaments
# ---------------------------------------------------------------------------

def test_chromatic_passing_tone_ascending():
    n = chromatic_passing_tone(60, 62, 240, 480)   # C -> C# -> D
    assert n["pitch"] == 61                        # C# (midpoint)
    assert n["ornament"] == "passing"
    assert n["resolve_pitch"] == 62
    assert is_chromatic(61, C_MAJOR)
    assert resolve_by_step(61, 62, C_MAJOR)


def test_chromatic_passing_tone_descending():
    n = chromatic_passing_tone(62, 60, 240, 480)   # D -> C# -> C
    assert n["pitch"] == 61
    assert n["resolve_pitch"] == 60


def test_chromatic_passing_tone_requires_whole_step():
    with pytest.raises(ValueError):
        chromatic_passing_tone(60, 61, 0, 240)     # semitone gap -> error


def test_chromatic_neighbor_above_and_below():
    up = chromatic_neighbor(60, above=True, start_tick=0, end_tick=240)
    dn = chromatic_neighbor(60, above=False, start_tick=0, end_tick=240)
    assert up["pitch"] == 61 and up["resolve_pitch"] == 60   # C Db C
    assert dn["pitch"] == 59 and dn["resolve_pitch"] == 60   # C B C
    assert up["ornament"] == "neighbor"


def test_approach_note():
    n = approach_note(62, 240, 480)              # C# -> D
    assert n["pitch"] == 61
    assert n["ornament"] == "approach"
    assert n["resolve_pitch"] == 62
    assert resolve_by_step(61, 62, C_MAJOR)


def test_secondary_leading_tone():
    n = secondary_leading_tone(67, 240, 480)     # F# -> G
    assert n["pitch"] == 66
    assert n["ornament"] == "leading_tone"
    assert n["resolve_pitch"] == 67
    assert resolve_by_step(66, 67, C_MAJOR)


def test_resolve_by_step_rejects_non_scale_target():
    assert not resolve_by_step(61, 63, C_MAJOR)  # 63 D# not in C major
    assert not resolve_by_step(66, 68, C_MAJOR)  # 68 G# not in C major


def test_resolve_by_step_rejects_non_step_interval():
    assert not resolve_by_step(60, 67, C_MAJOR)  # 60->67 is a fifth


# ---------------------------------------------------------------------------
# audit gates
# ---------------------------------------------------------------------------

def _bar():
    return [
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
        chromatic_passing_tone(60, 62, 240, 480),     # C# resolving -> D
        {"pitch": 62, "volume": 90, "start_tick": 480, "end_tick": 720, "weight": "strong"},
        {"pitch": 64, "volume": 90, "start_tick": 720, "end_tick": 960, "weight": "weak"},
    ]


def test_audit_tagged_passing_tone_passes():
    r = audit_voice(_bar(), C_MAJOR, strong_grid=(0, 960))
    assert r.passes
    assert r.tagged_ornaments == 1
    assert r.tagged_resolving == 1
    assert r.tagged_non_resolving == 0
    assert r.untagged_out_of_scale == 0


def test_audit_non_resolving_ornament_fails():
    notes = [
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
        approach_note(62, 240, 480),   # C# -> D but D never arrives
        {"pitch": 64, "volume": 90, "start_tick": 480, "end_tick": 720, "weight": "strong"},
    ]
    r = audit_voice(notes, C_MAJOR, strong_grid=(0, 960))
    assert not r.passes
    assert r.tagged_non_resolving == 1
    assert r.tagged_ornaments == 1


def test_audit_untagged_chromatic_fails():
    notes = [
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
        {"pitch": 61, "volume": 90, "start_tick": 240, "end_tick": 480, "weight": "weak"},  # C# un-tagged
        {"pitch": 62, "volume": 90, "start_tick": 480, "end_tick": 720, "weight": "strong"},
    ]
    r = audit_voice(notes, C_MAJOR, strong_grid=(0, 960))
    assert not r.passes
    assert r.untagged_out_of_scale == 1


def test_audit_strong_out_of_chord_fails():
    # strong note D(62) is in-scale but NOT a C-major chord tone -> strong violation
    notes = [
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
        {"pitch": 62, "volume": 90, "start_tick": 960, "end_tick": 1200, "weight": "strong"},
    ]
    r = audit_voice(notes, C_MAJOR, chord_pcs_by_bar={0: [0, 4, 7]},
                    strong_grid=(0, 960))
    assert not r.passes
    assert r.strong_violations == 1


def test_audit_silent_landmarks_ignored():
    # pitch 0 landmarks must not count as chromatic violations
    from structures import MusicEvent
    notes = [
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
        MusicEvent(0, 0, 1920, 1920),   # silent terminal landmark
    ]
    r = audit_voice(notes, C_MAJOR, strong_grid=(0, 960))
    assert r.passes
    assert r.audible == 1


def test_audit_dedup_counts_collisions():
    notes = [
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
    ]
    r = audit_voice(notes, C_MAJOR, strong_grid=(0, 960))
    assert r.collisions == 1
