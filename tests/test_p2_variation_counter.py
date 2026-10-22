# -*- coding: utf-8 -*-
"""P2 gate — variation operators + the countermelody role.

Pins VOICE_ROLE_WORKFLOW_PLAN.md P2:
  * variation transforms are pure, deterministic, landmark-preserving;
  * a lead+counter two-voice fixture has 0 collisions, 0 un-tagged
    out-of-scale violations, and counter onsets never double the lead
    (contrast + complementary density).
"""

import pytest

from structures import MusicEvent
from workflows.variation import (
    density_scale, displace, invert, retrograde, transpose,
)
from sound.generators.harmony_writer import HarmonyWriter
from workflows.pitch_audit import audit_voice

C_MAJOR = [0, 2, 4, 5, 7, 9, 11]


def _events():
    return [
        MusicEvent(60, 90, 0, 480),      # C
        MusicEvent(64, 90, 480, 960),    # E
        MusicEvent(67, 90, 960, 1440),   # G
        MusicEvent(0, 0, 1920, 1920),    # terminal landmark
    ]


# ---------------------------------------------------------------------------
# variation operators
# ---------------------------------------------------------------------------

def test_invert_around_axis():
    out = invert(_events(), 60)
    assert [e.pitch for e in out] == [60, 56, 53, 0]
    assert [e.start_tick for e in out] == [0, 480, 960, 1920]  # times intact


def test_transpose():
    out = transpose(_events(), 12)
    assert [e.pitch for e in out] == [72, 76, 79, 0]


def test_retrograde_reverses_time_and_preserves_landmark():
    out = retrograde(_events(), 1920)
    assert [e.pitch for e in out] == [67, 64, 60, 0]
    # G (960-1440) -> start 480; E -> 960; C -> 1440; landmark -> 1920
    assert [e.start_tick for e in out] == [480, 960, 1440, 1920]
    assert out[-1].end_tick == 1920


def test_density_scale_thins_evenly():
    out = density_scale(_events(), 0.5)
    assert [e.pitch for e in out if e.pitch > 0] == [60, 67]


def test_density_scale_rejects_invalid_factor():
    with pytest.raises(ValueError):
        density_scale(_events(), 1.5)


def test_displace_shifts_onsets_preserves_duration():
    out = displace(_events(), 240)
    assert [e.start_tick for e in out if e.pitch > 0] == [240, 720, 1200]
    assert [e.end_tick - e.start_tick for e in out if e.pitch > 0] == [480, 480, 480]


def test_transforms_are_pure():
    src = _events()
    invert(src, 60)
    transpose(src, 12)
    retrograde(src, 1920)
    density_scale(src, 0.5)
    displace(src, 240)
    assert [e.pitch for e in src] == [60, 64, 67, 0]
    assert [e.start_tick for e in src] == [0, 480, 960, 1920]


# ---------------------------------------------------------------------------
# counter role
# ---------------------------------------------------------------------------

def _lead_half_notes():
    """C-major lead on strong beats (half-note spacing) -> gaps to fill."""
    melody = []
    for i, p in enumerate([60, 62, 64, 65, 67, 69, 71, 72]):
        t = i * 960
        melody.append({"pitch": p, "volume": 100,
                       "start_tick": t, "end_tick": t + 480})
    return melody


def test_counterline_no_collision_no_untagged():
    hw = HarmonyWriter(key="C")
    lead = _lead_half_notes()
    ctr = hw.counterline(lead, grid=240, register=(48, 60),
                         mode="independent", seed=0)
    lead_onsets = {e["start_tick"] for e in lead}
    ctr_onsets = {e["start_tick"] for e in ctr}
    assert ctr, "counter must not be empty when the lead has gaps"
    assert lead_onsets & ctr_onsets == set(), "counter doubles a lead onset"
    r = audit_voice(ctr, C_MAJOR, strong_grid=(0, 960))
    assert r.passes, r.summary()
    assert r.untagged_out_of_scale == 0
    assert r.collisions == 0


def test_counterline_has_contour_not_drone():
    hw = HarmonyWriter(key="C")
    ctr = hw.counterline(_lead_half_notes(), grid=240, register=(48, 60),
                         mode="independent", seed=0)
    assert len({e["pitch"] for e in ctr}) >= 3


def test_counterline_transform_mode_is_in_key():
    hw = HarmonyWriter(key="C")
    ctr = hw.counterline(_lead_half_notes(), grid=240, register=(48, 60),
                         mode="transform", seed=0)
    assert ctr
    r = audit_voice(ctr, C_MAJOR, strong_grid=(0, 960))
    assert r.passes, r.summary()
    # transform derives from the lead contour, so it must not collide either
    lead_onsets = {e["start_tick"] for e in _lead_half_notes()}
    assert lead_onsets & {e["start_tick"] for e in ctr} == set()


def test_counterline_contrast_no_pitch_class_doubling():
    """The counter never sounds the lead's pitch class at the same time."""
    hw = HarmonyWriter(key="C")
    lead = _lead_half_notes()
    ctr = hw.counterline(lead, grid=240, register=(48, 60),
                         mode="independent", seed=0)
    for c in ctr:
        sounding = {e["pitch"] % 12 for e in lead
                    if e["start_tick"] <= c["start_tick"] < e["end_tick"]}
        assert (c["pitch"] % 12) not in sounding


def test_counterline_deterministic():
    hw = HarmonyWriter(key="C")
    a = hw.counterline(_lead_half_notes(), mode="independent", seed=3)
    b = hw.counterline(_lead_half_notes(), mode="independent", seed=3)
    assert a == b


def test_harmonize_role_dispatch():
    hw = HarmonyWriter(key="C")
    lead = _lead_half_notes()
    counter = hw.harmonize(lead, role="counter", seed=0)
    assert "counter" in counter
    harmony = hw.harmonize(lead)  # default = harmony
    assert "counter" not in harmony and harmony
    with pytest.raises(ValueError):
        hw.harmonize(lead, role="bogus")


def test_counterline_rejects_bad_mode():
    with pytest.raises(ValueError):
        HarmonyWriter(key="C").counterline(_lead_half_notes(), mode="nope")
