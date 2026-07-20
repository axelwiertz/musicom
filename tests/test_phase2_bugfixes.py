"""Phase 2 regression tests: each asserts a previously-broken behavior is fixed.

If any of these fail, a Phase 2 bug has regressed.
"""
import os
import tempfile

from structures import MusicUnit, MusicEvent
from structures.unit import MusicEvent as _MusicEvent  # same class, explicit path
from rules.counterpoint import Counterpoint
from generators.chain import MarkovChainGenerator
from generators.stochastic import StochasticGenerator
from utilities.config import Config


# --- T2.5: MusicEvent.duration with start_tick == 0 --------------------------
def test_duration_zero_start_tick():
    e = MusicEvent(pitch=60, volume=100, start_tick=0, end_tick=480)
    assert e.duration == 480          # was 0 before the fix
    e2 = MusicEvent(pitch=60, volume=100, start_tick=480, end_tick=960)
    assert e2.duration == 480
    # zero-length / rest still reports 0
    assert MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=0).duration == 0

    unit = MusicUnit(events=[
        MusicEvent(60, 100, 0, 480),
        MusicEvent(62, 100, 480, 960),
    ])
    assert unit.durations == [480, 480]


# --- T2.1: Counterpoint.has_crossing_voices ---------------------------------
def test_counterpoint_crossing_detected():
    # v1 starts below v2, then rises above v2 -> a crossing.
    v1 = MusicUnit(events=[MusicEvent(60, 100, 0, 480), MusicEvent(72, 100, 480, 960)])
    v2 = MusicUnit(events=[MusicEvent(64, 100, 0, 480), MusicEvent(65, 100, 480, 960)])
    assert Counterpoint(v1, v2).has_crossing_voices() is True


def test_counterpoint_no_crossing():
    # v1 stays below v2 throughout -> no crossing.
    v1 = MusicUnit(events=[MusicEvent(60, 100, 0, 480), MusicEvent(62, 100, 480, 960)])
    v2 = MusicUnit(events=[MusicEvent(67, 100, 0, 480), MusicEvent(69, 100, 480, 960)])
    assert Counterpoint(v1, v2).has_crossing_voices() is False


# --- T2.2: no phantom unit.append() -----------------------------------------
def test_markov_generate_unit_from_sequence():
    gen = MarkovChainGenerator(train=[(0,), (1,), (2,)], start=0, length=4)
    unit = gen.generate_unit_from_sequence([0, 1, 2], duration=480, onset_interval=480)
    assert isinstance(unit, MusicUnit)
    assert unit.pitches == [60, 62, 64]
    assert unit.durations == [480, 480, 480]


def test_stochastic_generate():
    gen = StochasticGenerator(length=5, pitch_set=[60, 62, 64], duration_set=[240, 480])
    unit = gen.generate()
    assert isinstance(unit, MusicUnit)
    assert len(unit) == 5
    assert all(p in (60, 62, 64) for p in unit.pitches)
    # absolute ticks strictly increase (no zero-length overlap chaos)
    starts = [e.start_tick for e in unit.events]
    assert starts == sorted(starts)


# --- T2.4: cross-platform config path ---------------------------------------
def test_config_default_path_cross_platform():
    assert '\\' not in Config.DEFAULT_PATH or os.sep == '\\'
    assert Config.DEFAULT_PATH.endswith('Music')
    assert tempfile.gettempdir() in Config.DEFAULT_PATH
