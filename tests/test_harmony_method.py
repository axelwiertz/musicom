# -*- coding: utf-8 -*-
"""P0 gate — HarmonizationMethod (harmonisation as a selectable method).

Pins HARMONIZATION_METHOD_PLAN.md P0:
  * ``HarmonyPlan`` / ``Chord`` abstract layer (per-bar chords, cycling, slice);
  * the four harmonisers produce real plans + concrete harmony notes;
  * ``realize_spine`` snaps strong beats to the PER-BAR chord when a plan is set
    (backward-compatible: no plan == the legacy single-chord snap);
  * the default fillers stay byte-neutral without a plan, and per-bar with one;
  * ``compose(harmonizer=...)`` changes the harmony and still validates.
"""

import hashlib
import tempfile

import pytest

from structures import MusicEvent
from rules.harmony import QUALITY_INTERVALS
from workflows.cell_engine import CellContext, ROLE_FILLERS
from workflows.harmony_plan import Chord, HarmonyPlan
from workflows.method_contract import RawNote
from workflows.realize_spine import realize
from workflows.harmony_method import (
    HARMONIZERS, harmonizer_plan, plan_from_method, profile_for_method,
)

C_MAJOR = [0, 2, 4, 5, 7, 9, 11]


def _ctx(chord=(60, 64, 67), register=(60, 84), section_len=1920,
         section_bars=1, harmony_plan=None):
    return CellContext(
        key="C", pattern="major", chord_tones=chord,
        register=register, density=1.0, root_midi=48,
        section_bars=section_bars, section_len=section_len, bar_ticks=1920,
        harmony_plan=harmony_plan,
    )


# ---------------------------------------------------------------------------
# HarmonyPlan / Chord (abstract object)
# ---------------------------------------------------------------------------

def test_chord_derives_tones_from_quality():
    assert Chord(48, "maj").chord_tones() == (48, 52, 55)
    assert Chord(48, "min").chord_tones() == (48, 51, 55)
    assert Chord(48, "maj", tones=(60, 64, 67)).chord_tones() == (60, 64, 67)


def test_harmony_plan_cycles_and_slices():
    plan = HarmonyPlan(chords=(Chord(48, "maj"), Chord(53, "maj")))
    assert plan.chord_at(0).root_midi == 48
    assert plan.chord_at(1).root_midi == 53
    assert plan.chord_at(2).root_midi == 48          # cycles
    sub = plan.slice(1, 2)
    assert [c.root_midi for c in sub.chords] == [53, 48]


def test_harmony_plan_single_is_degenerate_legacy():
    plan = HarmonyPlan.single((48, 52, 55), root_midi=48, quality="maj")
    assert plan.n_bars == 1
    assert plan.chord_at(0).chord_tones() == (48, 52, 55)
    assert plan.chord_at(9).chord_tones() == (48, 52, 55)   # holds anywhere


# ---------------------------------------------------------------------------
# Harmoniser plans (abstract layer)
# ---------------------------------------------------------------------------

def test_functional_plan_is_per_bar_iv_vi_iv():
    plan = harmonizer_plan("functional", "C", ["A", "B"], [4, 4])
    assert plan.n_bars == 8
    # C = 48; I-V-vi-IV in C: C G A F -> offsets 0,7,9,5 over base 48
    expected = (48, 55, 57, 53) * 2
    assert plan.roots == expected
    assert plan.chord_at(0).degree == "I"
    assert plan.chord_at(1).degree == "V"
    assert plan.chord_at(2).quality == "min"          # vi = A minor


def test_abstract_plan_walks_in_key_and_homes():
    plan = harmonizer_plan("abstract", "C", ["A"], [8], seed=7)
    assert plan.n_bars == 8
    # every walked subset lands on diatonic C-major pitch classes
    for c in plan.chords:
        for t in c.chord_tones():
            assert t % 12 in C_MAJOR
    # the walk starts on the tonic subset (maj0 -> C major triad)
    assert plan.chord_at(0).chord_tones() == (48, 52, 55)
    # deterministic for the same seed
    plan2 = harmonizer_plan("abstract", "C", ["A"], [8], seed=7)
    assert plan.roots == plan2.roots


def test_satb_and_chordarp_fall_back_to_functional_plan():
    for name in ("satb", "chordarp"):
        plan = harmonizer_plan(name, "C", ["A"], [4])
        assert plan.n_bars == 4
        assert list(plan.roots) == [48, 55, 57, 53]     # I V vi IV


# ---------------------------------------------------------------------------
# realize_spine — per-bar snap (backward-compatible)
# ---------------------------------------------------------------------------

def test_realize_snaps_strong_beats_to_per_bar_chord():
    plan = HarmonyPlan(chords=(Chord(48, "maj"), Chord(53, "maj")))  # C -> F
    ctx = _ctx(chord=(48, 52, 55), register=(48, 72), section_len=3840,
               section_bars=2, harmony_plan=plan)
    # strong beat in bar 0 -> C chord tone
    p0 = [e.pitch for e in realize([RawNote(pitch_index=0.5, onset=0.0)],
                                   ctx, "lead", grid=240).events if e.pitch > 0][0]
    # strong beat in bar 1 -> F chord tone
    p1 = [e.pitch for e in realize([RawNote(pitch_index=0.5, onset=1920.0)],
                                   ctx, "lead", grid=240).events if e.pitch > 0][0]
    assert p0 in (48, 52, 55)
    assert p1 in (53, 57, 60)
    assert p0 != p1


def test_realize_no_plan_still_uses_single_chord():
    ctx = _ctx(chord=(60, 64, 67))                    # no harmony_plan
    pitch = [e.pitch for e in realize([RawNote(pitch_index=0.5, onset=0.0)],
                                      ctx, "lead", grid=240).events
             if e.pitch > 0][0]
    assert pitch in (60, 64, 67)                      # legacy snap unchanged


# ---------------------------------------------------------------------------
# Default fillers — byte-neutral without plan, per-bar with one
# ---------------------------------------------------------------------------

def test_lead_filler_byte_neutral_without_plan():
    ctx = _ctx(chord=(48, 52, 55), section_len=7680, section_bars=4)
    evs = ROLE_FILLERS["lead"](ctx)
    pitches = [e.pitch for e in evs]
    # legacy literal: chord_tones[b % 3] + 12, b = 0..7
    assert pitches == [60, 64, 67, 60, 64, 67, 60, 64]
    assert [e.start_tick for e in evs] == [b * 960 for b in range(8)]


def test_fillers_per_bar_use_plan_chords():
    plan = HarmonyPlan(chords=(Chord(48, "maj"), Chord(53, "maj")))  # C -> F
    ctx = _ctx(chord=(48, 52, 55), register=(0, 127), section_len=3840,
               section_bars=2, harmony_plan=plan)
    # bass roots follow the plan
    assert [e.pitch for e in ROLE_FILLERS["bass"](ctx)] == [48, 53]
    # pad splits into per-bar sustained chords
    pad = ROLE_FILLERS["pad"](ctx)
    assert len(pad) == 6                              # 3 tones x 2 bars
    bar0 = {e.pitch for e in pad if e.start_tick == 0}
    bar1 = {e.pitch for e in pad if e.start_tick == 1920}
    assert bar0 == {48, 52, 55}
    assert bar1 == {53, 57, 60}


# ---------------------------------------------------------------------------
# Concrete voice-leaders (SATB / ChordArp)
# ---------------------------------------------------------------------------

def test_satb_voice_produces_in_key_events():
    from workflows.harmony_method import SATBHarmonizer
    lead = [{"pitch": 72, "volume": 100, "start_tick": 0, "end_tick": 480},
            {"pitch": 71, "volume": 100, "start_tick": 480, "end_tick": 960},
            {"pitch": 67, "volume": 100, "start_tick": 960, "end_tick": 1440},
            {"pitch": 69, "volume": 100, "start_tick": 1440, "end_tick": 1920}]
    plan = HarmonyPlan.single((48, 52, 55), root_midi=48, quality="maj")
    evs = SATBHarmonizer().voice(plan, key="C", seed=0, lead=lead)
    assert evs
    assert all(e.pitch > 0 for e in evs)
    assert all(e.pitch % 12 in C_MAJOR for e in evs)  # diatonic triads


def test_chordarp_voice_produces_chord_track_events():
    from workflows.harmony_method import ChordArpHarmonizer
    plan = harmonizer_plan("functional", "C", ["A"], [4])
    evs = ChordArpHarmonizer().voice(plan, key="C", seed=1)
    assert evs
    assert all(e.pitch > 0 for e in evs)
    # chord-track events carry absolute ticks within the 4-bar span
    assert max(e.end_tick for e in evs) <= 4 * 1920


def test_functional_voice_is_sustained_pad_per_bar():
    from workflows.harmony_method import FunctionalHarmonizer
    plan = harmonizer_plan("functional", "C", ["A"], [2])
    evs = FunctionalHarmonizer().voice(plan)
    assert len(evs) == 2 * 3                          # 2 bars x 3 tones


# ---------------------------------------------------------------------------
# Registry + honest gaps
# ---------------------------------------------------------------------------

def test_harmonizer_registry_rejects_unknown():
    with pytest.raises(ValueError):
        harmonizer_plan("nope", "C", ["A"], [4])


def test_profiles_tag_sources_and_semantics():
    assert profile_for_method("002").source == "method"
    assert profile_for_method("012").phase_semantics == "rhythm"
    assert profile_for_method("040").harmonizer == "satb"


def test_plan_from_method_honest_stub():
    # template-source method -> tells you to harmonise from template
    with pytest.raises(NotImplementedError):
        plan_from_method("012", "C", ["A"], [4])
    # method-source method -> P1 adapter gap
    with pytest.raises(NotImplementedError):
        plan_from_method("002", "C", ["A"], [4])
    # unknown method -> no profile
    with pytest.raises(KeyError):
        plan_from_method("065", "C", ["A"], [4])


# ---------------------------------------------------------------------------
# End-to-end: compose(harmonizer=...) changes harmony, still validates
# ---------------------------------------------------------------------------

def test_compose_with_harmonizer_differs_and_validates():
    from workflows.musicom_workflow import compose

    with tempfile.TemporaryDirectory() as d:
        r_default = compose(style="pop", method="001", seed=7, out_dir=d,
                            humanize=False)
        default_bytes = open(r_default.midi_path, "rb").read()
    with tempfile.TemporaryDirectory() as d:
        r_func = compose(style="pop", method="001", seed=7, out_dir=d,
                         humanize=False, harmonizer="functional")
        func_bytes = open(r_func.midi_path, "rb").read()
    with tempfile.TemporaryDirectory() as d:
        r_abs = compose(style="pop", method="001", seed=7, out_dir=d,
                        humanize=False, harmonizer="abstract")
        abs_bytes = open(r_abs.midi_path, "rb").read()

    for data in (default_bytes, func_bytes, abs_bytes):
        assert len(data) > 40, "empty/corrupt MIDI"
    # the harmonizer changes the harmony (not byte-identical to the default)
    assert hashlib.sha256(default_bytes).digest() != hashlib.sha256(func_bytes).digest()
    assert hashlib.sha256(func_bytes).digest() != hashlib.sha256(abs_bytes).digest()
