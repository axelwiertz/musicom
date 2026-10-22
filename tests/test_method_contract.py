# -*- coding: utf-8 -*-
"""P0 gate — method contract + realization spine.

Pins METHOD_CONTRACT_PLAN.md P0:
  * ``DefaultMethod`` reproduces the legacy fillers exactly (byte-neutral);
  * ``realize()`` turns raw notes into a validated, grid-locked, in-key unit;
  * ``registry_method()`` resolves honestly (default / spec-only / P1-pending).
"""

import pytest

from structures import MusicEvent
from workflows.cell_engine import CellContext, ROLE_FILLERS, _unit_from_events
from workflows.method_contract import (
    DefaultMethod, RawNote, registry_method,
)
from workflows.realize_spine import realize
from workflows.pitch_audit import audit_voice

C_MAJOR = [0, 2, 4, 5, 7, 9, 11]


def _ctx(voice_idx=0, instrument="Flute", chord=(60, 64, 67),
         register=(60, 84), section_len=1920):
    return CellContext(
        key="C", pattern="major", chord_tones=chord,
        register=register, density=1.0, root_midi=48,
        section_bars=1, section_len=section_len, bar_ticks=1920,
        voice_idx=voice_idx, instrument_name=instrument,
    )


# ---------------------------------------------------------------------------
# DefaultMethod byte-neutrality
# ---------------------------------------------------------------------------

def test_default_method_resolves_role_by_position():
    assert DefaultMethod().resolve_role(_ctx(0)) == "lead"
    assert DefaultMethod().resolve_role(_ctx(1)) == "pad"
    assert DefaultMethod().resolve_role(_ctx(2)) == "bass"
    assert DefaultMethod().resolve_role(_ctx(3)) == "arp"


def test_default_method_generate_matches_legacy_fillers():
    for role in ("lead", "pad", "bass", "arp"):
        ctx = _ctx({"lead": 0, "pad": 1, "bass": 2, "arp": 3}[role])
        dm = DefaultMethod()
        got = [(e.pitch, e.volume, e.start_tick, e.end_tick)
               for e in dm.generate(ctx, role)]
        want = [(e.pitch, e.volume, e.start_tick, e.end_tick)
                for e in ROLE_FILLERS[role](ctx)]
        assert got == want, role


def test_realize_passthrough_is_byte_neutral_to_legacy_fill():
    """DefaultMethod output (MusicEvents) through realize() == legacy unit."""
    ctx = _ctx(0)
    dm = DefaultMethod()
    role = dm.resolve_role(ctx)
    events = dm.generate(ctx, role)
    # spine path
    spine_unit = realize(events, ctx, role)
    # legacy path (what compose() fills today)
    legacy_unit = _unit_from_events(events, ctx.section_len)
    got = [(e.pitch, e.volume, e.start_tick, e.end_tick)
           for e in spine_unit.events]
    want = [(e.pitch, e.volume, e.start_tick, e.end_tick)
            for e in legacy_unit.events]
    assert got == want


def test_default_method_drum_guard_raises():
    # voice 4 = rhythm, but a non-drum instrument -> no role -> ValueError
    ctx = _ctx(4, instrument="Flute")
    with pytest.raises(ValueError):
        DefaultMethod().resolve_role(ctx)


# ---------------------------------------------------------------------------
# realize() on raw notes
# ---------------------------------------------------------------------------

def test_realize_raw_notes_grid_locked_and_in_key():
    raw = [
        RawNote(pitch_index=0.55, onset=123.4, velocity=90),  # off-grid
        RawNote(pitch_index=0.3, onset=500.0, velocity=90),
        RawNote(pitch_index=0.9, onset=960.0, velocity=90),   # strong beat
    ]
    unit = realize(raw, _ctx(0), "lead", grid=240)
    notes = [e for e in unit.events if e.pitch > 0]
    assert len(notes) == 3
    assert all(e.start_tick % 240 == 0 for e in notes)
    r = audit_voice(unit.events, C_MAJOR, strong_grid=(0, 960))
    assert r.passes, r.summary()
    assert r.untagged_out_of_scale == 0
    assert r.strong_violations == 0


def test_realize_strong_beat_snaps_to_chord():
    # onset 0 = strong beat -> must land on a chord tone (60/64/67)
    raw = [RawNote(pitch_index=0.5, onset=0.0, velocity=90)]
    unit = realize(raw, _ctx(0), "lead", grid=240)
    pitch = [e.pitch for e in unit.events if e.pitch > 0][0]
    assert pitch in (60, 64, 67)


def test_realize_weak_beat_snaps_to_scale_only():
    # onset 480 = weak beat (off strong grid (0,960)) -> in-scale, not forced chord
    raw = [RawNote(pitch_index=0.5, onset=480.0, velocity=90)]
    unit = realize(raw, _ctx(0), "lead", grid=240)
    pitch = [e.pitch for e in unit.events if e.pitch > 0][0]
    assert pitch % 12 in C_MAJOR


def test_realize_dedups_collisions():
    # two raw notes that snap to the same (onset, pitch) -> one survives
    raw = [
        RawNote(pitch_index=0.49, onset=240.0, velocity=90),
        RawNote(pitch_index=0.51, onset=250.0, velocity=90),  # same snap target
    ]
    unit = realize(raw, _ctx(0), "lead", grid=240)
    notes = [e for e in unit.events if e.pitch > 0]
    assert len(notes) == 1


def test_realize_preserves_zero_drift():
    raw = [RawNote(pitch_index=0.5, onset=120.0, velocity=90)]
    unit = realize(raw, _ctx(0), "lead", grid=240)
    assert max(e.end_tick for e in unit.events) == 1920


def test_realize_rejects_unknown_pattern():
    ctx = _ctx(0)
    ctx = CellContext(key="C", pattern="nonsense", chord_tones=(60, 64, 67),
                      register=(60, 84), density=1.0, section_len=1920)
    with pytest.raises(ValueError):
        realize([RawNote()], ctx, "lead")


# ---------------------------------------------------------------------------
# registry_method()
# ---------------------------------------------------------------------------

def test_registry_method_default():
    assert isinstance(registry_method("default"), DefaultMethod)


def test_registry_method_spec_only_not_in_registry():
    with pytest.raises(KeyError):
        registry_method("065")  # Twelve-Tone Serial — prose only, no code


def test_registry_method_spec_only_in_registry_no_code():
    with pytest.raises(NotImplementedError):
        registry_method("026")  # DPSM — registered but mod_path None


def test_registry_method_implemented_but_adapter_pending():
    with pytest.raises(NotImplementedError):
        registry_method("023")  # tendency-masking — has code, adapter is P1
