# -*- coding: utf-8 -*-
"""Tests for the evolution engine (workflows/evolution.py) — build step 3.

Covers (plan §3):
- Fitness terms: tonal gravity in [0,1], on-grid, stepwise, variety,
  groove stability — each mathematically sound.
- Hard gates: zero-drift violation rejected, silent voice rejected.
- Selection: rule judge picks highest fitness; tie → first.
- Full evolve_anchor run: K candidates, winner, evolution.json audit trail,
  deterministic per seed, zero-drift MIDI, provenance.
- Style weights: flamenco weighs grid higher than ambient.
"""
import hashlib
import json
import os
import sys

import pytest

sys.path.insert(0, "/opt/data/projects/Instruments")

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.evolution import (
    FitnessWeights, STYLE_WEIGHTS,
    tonal_gravity, on_grid_ratio, stepwise_motion, rhythm_variety,
    groove_stability, evaluate_fitness, hard_gates, rule_judge,
    build_anchor_unit, evolve_anchor, EvolutionResult,
)


BAR = 1920


def _unit_with_pcs(pitch_classes):
    """MusicUnit with one event per pitch class (octave 4)."""
    u = MusicUnit()
    for i, pc in enumerate(pitch_classes):
        u.add_event(MusicEvent(60 + pc, 90, i * 240, i * 240 + 200))
    u.add_event(MusicEvent(0, 0, len(pitch_classes) * 240, len(pitch_classes) * 240))
    return u


# ------------------------------------------------------------ fitness ------

def test_tonal_gravity_range():
    u = _unit_with_pcs([0, 4, 7])  # C major triad
    g = tonal_gravity(u, "C")
    assert 0.0 <= g <= 1.0
    # a C-major triad is more "C" than a tritone pair
    g2 = tonal_gravity(_unit_with_pcs([0, 6]), "C")
    assert g > g2


def test_tonal_gravity_transposes():
    # same triad, D major key: C triad should score lower in D than C key
    u = _unit_with_pcs([0, 4, 7])
    gC = tonal_gravity(u, "C")
    gD = tonal_gravity(u, "D")
    assert gC > gD


def test_on_grid_ratio():
    u = MusicUnit()
    u.add_event(MusicEvent(60, 90, 0, 200))
    u.add_event(MusicEvent(62, 90, 240, 440))   # on 8th grid
    u.add_event(MusicEvent(64, 90, 120, 320))   # off grid
    assert on_grid_ratio(u) == pytest.approx(2 / 3)


def test_stepwise_motion():
    step = _unit_with_pcs([0, 2, 4])       # whole steps
    leap = _unit_with_pcs([0, 12, 24])     # octaves
    assert stepwise_motion(step) > stepwise_motion(leap)
    assert stepwise_motion(step) == pytest.approx(1.0)


def test_rhythm_variety_and_groove():
    u = _unit_with_pcs([0, 2, 4, 7])
    assert 0.0 <= rhythm_variety(u) <= 1.0
    assert 0.0 <= groove_stability(u) <= 1.0
    # steady groove (all same interval) is more stable than varied
    steady = MusicUnit()
    for i in range(8):
        steady.add_event(MusicEvent(60, 90, i * 480, i * 480 + 200))
    varied = MusicUnit()
    for i, gap in enumerate([480, 960, 480, 240, 480, 960, 480]):
        varied.add_event(MusicEvent(60, 90, i * 480 + gap, i * 480 + gap + 200))
    assert groove_stability(steady) > groove_stability(varied)


def test_evaluate_fitness_total_in_range():
    u = build_anchor_unit(36, 4, 4, 240)
    r = evaluate_fitness(u, key="C")
    assert 0.0 <= r["total"] <= 1.0
    assert set(r["terms"]) == {"tonal_gravity", "on_grid", "stepwise_motion",
                               "rhythm_variety", "groove_stability"}


def test_style_weights_differ():
    assert STYLE_WEIGHTS["flamenco"].on_grid > STYLE_WEIGHTS["ambient"].on_grid
    assert STYLE_WEIGHTS["techno"].groove_stability > STYLE_WEIGHTS["ambient"].groove_stability


# ---------------------------------------------------------- hard gates -----

def test_hard_gates_zero_drift():
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=2, num_sections=2)
    c.add_voice("V1", program=0, channel=0)
    c.add_voice("V2", program=0, channel=1)
    c.add_section("A", bars=1)
    c.add_section("B", bars=1)
    # V1 section A unit overflows its 1920-tick cell (2000 ticks, no landmark)
    bad = MusicUnit()
    bad.add_event(MusicEvent(60, 90, 0, 2000))
    c.fill_voice_section("V1", "A", bad)
    ok_unit = MusicUnit()
    ok_unit.add_event(MusicEvent(60, 90, 0, 400))
    ok_unit.add_event(MusicEvent(0, 0, 1920, 1920))
    c.fill_voice_section("V1", "B", ok_unit)
    # V2 fully ok (both cells 1920)
    c.fill_voice_section("V2", "A", ok_unit.clone())
    c.fill_voice_section("V2", "B", ok_unit.clone())
    viols = hard_gates(c)
    assert any("zero-drift" in v for v in viols)


def test_hard_gates_silent_voice():
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("V", program=0, channel=0)
    c.add_section("A", bars=1)
    silent = MusicUnit()
    silent.add_event(MusicEvent(0, 0, 1920, 1920))
    c.fill_voice_section("V", "A", silent)
    viols = hard_gates(c)
    assert any("silent" in v for v in viols)


def test_hard_gates_pass_clean():
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("V", program=0, channel=0)
    c.add_section("A", bars=1)
    u = build_anchor_unit(36, 1, 4, 0)
    c.fill_voice_section("V", "A", u)
    assert hard_gates(c) == []


# ----------------------------------------------------------- selection -----

def test_rule_judge_picks_best():
    cands = [
        {"fitness": {"total": 0.3}},
        {"fitness": {"total": 0.9}},
        {"fitness": {"total": 0.5}},
    ]
    assert rule_judge(cands) == 1


def test_rule_judge_tie_first():
    cands = [
        {"fitness": {"total": 0.7}},
        {"fitness": {"total": 0.7}},
    ]
    assert rule_judge(cands) == 0


# -------------------------------------------------------- evolve_anchor -----

@pytest.fixture(scope="module")
def evo():
    return evolve_anchor(style="pop", key="C", bpm=120, seed=42, n_variants=4)


def test_evolution_result_shape(evo):
    assert isinstance(evo, EvolutionResult)
    assert evo.style == "pop"
    assert evo.key == "C"
    assert evo.seed == 42


def test_evolution_winner_and_candidates(evo):
    assert len(evo.candidates) >= 2
    assert evo.winner["fitness"]["total"] > 0
    assert "density" in evo.winner and "offset" in evo.winner
    # winner is the highest-fitness viable candidate
    best = max(c["fitness"]["total"] for c in evo.candidates if c["gates"] == "pass")
    assert evo.winner["fitness"]["total"] == pytest.approx(best)


def test_evolution_midi_valid(evo):
    assert os.path.exists(evo.midi_path)
    assert os.path.getsize(evo.midi_path) > 40
    import mido
    m = mido.MidiFile(evo.midi_path)
    lens = [sum(msg.time for msg in t) for t in m.tracks[1:]]
    assert len(set(lens)) == 1, f"track drift: {lens}"


def test_evolution_json_audit(evo):
    assert os.path.exists(evo.evolution_path)
    data = json.loads(open(evo.evolution_path).read())
    assert data["seed"] == 42
    assert data["judge"] == "rule"
    assert data["generations"]
    assert "winner" in data
    assert data["winner"]["fitness"] > 0
    assert all("gates" in c for c in data["candidates"])


def test_evolution_deterministic():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r1 = evolve_anchor(seed=7, out_dir=td)
        r2 = evolve_anchor(seed=7, out_dir=td)
        h1 = hashlib.sha256(open(r1.midi_path, "rb").read()).hexdigest()
        h2 = hashlib.sha256(open(r2.midi_path, "rb").read()).hexdigest()
        assert h1 == h2


def test_evolution_custom_judge():
    """A judge callback that always picks the last candidate."""
    def last_judge(cands):
        return len(cands) - 1
    r = evolve_anchor(seed=3, n_variants=4, judge=last_judge)
    assert r.winner["variant"] == r.candidates[-1]["variant"]
