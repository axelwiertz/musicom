# -*- coding: utf-8 -*-
"""Tests for the canonical humanization layer (concrete → absolute).

Covers transformers/humanize.py (HumanizeProfile, profile_for_style,
humanize_events, HumanizeTransformer) and workflows/humanize.py
(humanize_composer). Pins the four invariants: zero-drift, no backtracking,
boundary clamp, and determinism — plus pitch/velocity correctness.
"""

import numpy as np
import pytest

from structures import MusicEvent, MusicUnit
from structures.matrix import UnitMatrix
from transformers.humanize import (
    HumanizeProfile,
    HumanizeTransformer,
    profile_for_style,
    ticks_from_ms,
    humanize_events,
)


def _note(pitch, start, end, vol=100):
    return MusicEvent(pitch=pitch, volume=vol, start_tick=start, end_tick=end)


def _landmark(span):
    return MusicEvent(pitch=0, volume=0, start_tick=span, end_tick=span)


def _unit(events, span):
    return MusicUnit(events=list(events) + [_landmark(span)])


# ---------------------------------------------------------------------------
# profile / style derivation
# ---------------------------------------------------------------------------

def test_ticks_from_ms_is_tempo_correct():
    # 480 ticks/beat at 120 BPM: 1 beat = 0.5 s = 500 ms → 480 ticks
    # so 1 ms ≈ 0.96 ticks. At 60 BPM, 1 ms ≈ 0.48 ticks.
    assert ticks_from_ms(500.0, 120.0) == pytest.approx(480.0)
    assert ticks_from_ms(500.0, 60.0) == pytest.approx(240.0)
    assert ticks_from_ms(10.0, 120.0) == pytest.approx(9.6, abs=0.01)


def test_profile_for_style_groove_tighter_than_organic():
    groove = profile_for_style("techno")
    organic = profile_for_style("jazz")
    assert groove.timing_sigma_ms < organic.timing_sigma_ms
    assert groove.phrase_corr < organic.phrase_corr


def test_profile_for_style_fallback_and_instrument_dna():
    p = profile_for_style("some_unknown_style")
    assert p.timing_sigma_ms == 7.0  # STYLE_HUMANIZE_DEFAULT
    # instrument DNA (4-tuple) overrides timing/velocity/layback/duration
    q = profile_for_style("jazz", (3.0, 2.0, 8.0, 0.01))
    assert q.timing_sigma_ms == 3.0
    assert q.velocity_sigma == 2.0
    assert q.layback_ms == 8.0
    assert q.duration_sigma == 0.01
    # None entries are ignored
    r = profile_for_style("jazz", (None, None, 9.0, None))
    assert r.timing_sigma_ms == 11.0  # jazz value kept
    assert r.layback_ms == 9.0


def test_profile_for_style_hyphen_and_underscore_normalized():
    assert profile_for_style("hip_hop").timing_sigma_ms == profile_for_style("hip-hop").timing_sigma_ms


# ---------------------------------------------------------------------------
# event-level invariants
# ---------------------------------------------------------------------------

def _events_on_grid(n=16, grid=240, span=3840):
    return [_note(60 + (i % 3) * 4, i * grid, i * grid + 200) for i in range(n)]


def test_humanize_events_preserves_pitch_and_landmark():
    span = 1920
    events = [_note(60, 0, 400), _note(64, 480, 900), _landmark(span)]
    prof = HumanizeProfile(timing_sigma_ms=10.0, velocity_sigma=8.0)
    rng = np.random.default_rng(1)
    out, stats = humanize_events(events, prof, rng, span, bpm=120.0)
    # pitches unchanged (order preserved), landmark untouched
    assert [e.pitch for e in out] == [60, 64, 0]
    assert out[-1].start_tick == span and out[-1].end_tick == span
    assert stats["n_notes"] == 2


def test_humanize_events_no_backtracking():
    span = 3840
    events = _events_on_grid(16, 240, span)
    prof = HumanizeProfile(timing_sigma_ms=12.0, velocity_sigma=10.0)
    rng = np.random.default_rng(42)
    out, _ = humanize_events(events, prof, rng, span, bpm=120.0)
    starts = [e.start_tick for e in out if e.pitch != 0]
    assert starts == sorted(starts), "forward-clamp violated: onset moved before previous"


def test_humanize_events_boundary_clamp():
    span = 1920
    events = [_note(60, 0, 1900)]  # note near the seam
    prof = HumanizeProfile(timing_sigma_ms=15.0, duration_scale=1.2)
    rng = np.random.default_rng(7)
    out, _ = humanize_events(events, prof, rng, span, bpm=120.0)
    for e in out:
        if e.pitch != 0:
            assert e.end_tick <= span
            assert e.start_tick < span


def test_humanize_events_velocity_bounds():
    span = 1920
    events = [_note(60, i * 240, i * 240 + 200, vol=100) for i in range(8)]
    prof = HumanizeProfile(velocity_sigma=30.0, velocity_min=20, velocity_max=127)
    rng = np.random.default_rng(3)
    out, _ = humanize_events(events, prof, rng, span, bpm=120.0)
    for e in out:
        if e.pitch != 0:
            assert 20 <= e.volume <= 127


def test_humanize_events_deterministic():
    span = 1920
    events = _events_on_grid(16, 120, span)
    prof = HumanizeProfile(timing_sigma_ms=9.0, velocity_sigma=7.0)
    a, _ = humanize_events(events, prof, np.random.default_rng(99), span, bpm=120.0)
    b, _ = humanize_events(events, prof, np.random.default_rng(99), span, bpm=120.0)
    assert [(e.pitch, e.volume, e.start_tick, e.end_tick) for e in a] == \
           [(e.pitch, e.volume, e.start_tick, e.end_tick) for e in b]


def test_humanize_events_moves_offsets_off_grid():
    span = 3840
    events = _events_on_grid(32, 120, span)
    prof = HumanizeProfile(timing_sigma_ms=12.0, velocity_sigma=6.0)
    rng = np.random.default_rng(11)
    out, _ = humanize_events(events, prof, rng, span, bpm=120.0)
    orig = [e.start_tick for e in events]
    new = [e.start_tick for e in out if e.pitch != 0]
    # with a wide sigma, at least one onset must move off its grid point
    assert any(o != n for o, n in zip(orig, new))


def test_humanize_transformer():
    span = 1920
    unit = _unit([_note(60, 0, 400), _note(64, 480, 900)], span)
    t = HumanizeTransformer(profile=HumanizeProfile(timing_sigma_ms=8.0), seed=5, bpm=120.0)
    out = t.transform(unit, span=span)
    assert len(out.events) == 3  # 2 notes + landmark
    assert out.events[-1].pitch == 0
    assert t.last_stats["n_notes"] == 2


# ---------------------------------------------------------------------------
# composer-level integration (workflows/humanize.py)
# ---------------------------------------------------------------------------

def _build_composer():
    from workflows.unitmatrix_composer import UnitMatrixComposer

    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=3, num_sections=2)
    composer.add_voice("Lead", program=74, channel=0)
    composer.add_voice("Bass", program=33, channel=1)
    composer.add_voice("Drums", program=0, channel=9)
    composer.add_section("A", bars=2)
    composer.add_section("B", bars=2)
    BAR = 1920
    lead_a = _unit([_note(72, i * 240, i * 240 + 200) for i in range(16)], 2 * BAR)
    bass_a = _unit([_note(48, b * BAR, b * BAR + 900) for b in range(2)], 2 * BAR)
    drum_a = _unit([_note(36, b * BAR, b * BAR + 120) for b in range(2)], 2 * BAR)
    lead_b = _unit([_note(74, i * 240, i * 240 + 200) for i in range(16)], 2 * BAR)
    bass_b = _unit([_note(50, b * BAR, b * BAR + 900) for b in range(2)], 2 * BAR)
    drum_b = _unit([_note(36, b * BAR, b * BAR + 120) for b in range(2)], 2 * BAR)
    for name, unit in [("Lead", lead_a), ("Bass", bass_a), ("Drums", drum_a)]:
        composer.fill_voice_section(name, "A", unit)
    for name, unit in [("Lead", lead_b), ("Bass", bass_b), ("Drums", drum_b)]:
        composer.fill_voice_section(name, "B", unit)
    return composer


def test_humanize_composer_keeps_zero_drift():
    from workflows.humanize import humanize_composer

    composer = _build_composer()
    assert composer.validate()[0]  # pre-humanize gate
    summary = humanize_composer(composer, style="jazz", seed=123, bpm=120.0)
    ok, msg = composer.validate()
    assert ok, f"zero-drift broken after humanization: {msg}"
    assert set(summary) == {"Lead", "Bass", "Drums"}
    assert all(s["n_notes"] > 0 for s in summary.values())


def test_humanize_composer_deterministic():
    from workflows.humanize import humanize_composer

    c1 = _build_composer()
    c2 = _build_composer()
    humanize_composer(c1, style="jazz", seed=123, bpm=120.0)
    humanize_composer(c2, style="jazz", seed=123, bpm=120.0)
    assert c1.to_midi_bytes() == c2.to_midi_bytes()


def test_humanize_composer_different_seed_differs():
    from workflows.humanize import humanize_composer

    c1 = _build_composer()
    c2 = _build_composer()
    humanize_composer(c1, style="jazz", seed=1, bpm=120.0)
    humanize_composer(c2, style="jazz", seed=2, bpm=120.0)
    assert c1.to_midi_bytes() != c2.to_midi_bytes()


def test_humanize_composer_explicit_profiles_win():
    from workflows.humanize import humanize_composer

    composer = _build_composer()
    tight = HumanizeProfile(timing_sigma_ms=0.0, velocity_sigma=0.0,
                            duration_scale=1.0, duration_sigma=0.0, layback_ms=0.0)
    summary = humanize_composer(composer, style="jazz", seed=1, bpm=120.0,
                                profiles={"Lead": tight, "Bass": tight, "Drums": tight})
    # zero jitter → identical to original grid
    assert all(s["max_abs_shift_ticks"] == 0 for s in summary.values())
    assert composer.validate()[0]


def test_humanize_composer_no_backtracking_per_voice():
    from workflows.humanize import humanize_composer

    composer = _build_composer()
    humanize_composer(composer, style="jazz", seed=42, bpm=120.0)
    for voice in composer.voices:
        row_events = composer.matrix.get_row_events(voice["row"])
        starts = [e.start_tick for e in row_events if getattr(e, "pitch", 0) != 0]
        assert starts == sorted(starts)


# ---------------------------------------------------------------------------
# dual-version export (workflows/humanize.py::export_dual)
# ---------------------------------------------------------------------------

def _offsets_off_grid(midi_path):
    import mido  # READING ONLY (analysis)
    mid = mido.MidiFile(str(midi_path))
    off = 0
    total = 0
    for tr in mid.tracks[1:]:
        t = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0 and m.note > 0:
                total += 1
                if t % 120 != 0 and t % 240 != 0:
                    off += 1
    return off, total


def test_export_dual_writes_perfect_and_humanized(tmp_path):
    from workflows.humanize import export_dual

    composer = _build_composer()
    perfect = tmp_path / "x-perfect.mid"
    humanized = tmp_path / "x-humanized.mid"
    hz = export_dual(composer, perfect, humanized, style="jazz", seed=123, bpm=120.0)

    assert perfect.exists() and humanized.exists()
    assert perfect.stat().st_size > 40 and humanized.stat().st_size > 40
    assert set(hz) == {"Lead", "Bass", "Drums"}

    # perfect == the un-humanized composer bytes (grid-locked, no jitter)
    fresh = _build_composer()
    assert perfect.read_bytes() == fresh.to_midi_bytes()

    # humanized differs from perfect
    assert humanized.read_bytes() != perfect.read_bytes()

    # grid audit: perfect 0 off-grid, humanized > 0 (jitter ran)
    p_off, p_tot = _offsets_off_grid(perfect)
    h_off, h_tot = _offsets_off_grid(humanized)
    assert p_tot == h_tot          # same note count
    assert p_off == 0, "perfect version must stay grid-locked"
    assert h_off > 0, "humanized version must move onsets off-grid"
