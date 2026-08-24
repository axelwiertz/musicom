"""Tests for gear logic replicated from the 2026-08-24 surveillance scan.

Covers:
- Minimal Audio Lucid: scale-locked granular FX
- Rapid Flow miniGRID: micro-timing shift sequencer
- Parish Audio: overlapping-band parametric compressor
"""

import numpy as np
import pytest

SR = 44100


# --------------------------------------------------------------------------- #
# Lucid — scale-locked granular
# --------------------------------------------------------------------------- #
class TestScaleLockedGranular:
    def test_imports(self):
        from sound.effects.scale_locked_granular import (
            ScaleLockedGranular, SCALES, _quantize_to_scale,
        )
        assert "minor" in SCALES and "major" in SCALES
        # 55 Hz (A1) quantized to A minor (root 57 = A3 -> 220 Hz) lands on A
        assert _quantize_to_scale(0.0, SCALES["minor"]) == 0.0

    def test_unknown_scale_raises(self):
        from sound.effects.scale_locked_granular import ScaleLockedGranular
        with pytest.raises(ValueError):
            ScaleLockedGranular(scale_name="nope")

    def test_scale_lock_pitch(self):
        from sound.effects.scale_locked_granular import ScaleLockedGranular
        gl = ScaleLockedGranular(sample_rate=SR, scale_name="minor",
                                 root_midi=57)
        # 216 Hz is slightly flat of A3 (220); lock should pull to 220
        locked = gl.lock_freq_to_scale(216.0)
        assert locked == pytest.approx(220.0, abs=1.0)

    def test_process_shapes_output(self):
        from sound.effects.scale_locked_granular import ScaleLockedGranular
        gl = ScaleLockedGranular(sample_rate=16000, scale_name="major",
                                 root_midi=60, seed=3)
        t = np.linspace(0, 0.5, 8000, endpoint=False)
        x = np.sin(2 * np.pi * 440 * t)
        out = gl.process(x, bpm=120, grain_size_ms=80, density=8,
                         mode="stretch", wet=1.0)
        assert len(out) == len(x)
        assert np.max(np.abs(out)) > 0.01
        assert not np.allclose(out, x)

    def test_scrub_differs_from_stretch(self):
        from sound.effects.scale_locked_granular import ScaleLockedGranular
        gl = ScaleLockedGranular(sample_rate=16000, scale_name="major",
                                 root_midi=60, seed=3)
        t = np.linspace(0, 0.5, 8000, endpoint=False)
        x = np.sin(2 * np.pi * 220 * t) + 0.3 * np.sin(2 * np.pi * 330 * t)
        a = gl.process(x, bpm=120, density=8, mode="stretch", wet=1.0)
        b = gl.process(x, bpm=120, density=8, mode="scrub", wet=1.0)
        assert not np.allclose(a, b)

    def test_harmonic_delay_has_tail(self):
        from sound.effects.scale_locked_granular import ScaleLockedGranular
        gl = ScaleLockedGranular(sample_rate=16000, scale_name="major",
                                 root_midi=60)
        t = np.linspace(0, 0.2, 3200, endpoint=False)
        x = np.sin(2 * np.pi * 440 * t)
        out = gl.harmonic_grain_delay(x, bpm=120, degrees=[0, 7, 12], mix=0.8)
        # energy should appear after the input ends (delayed taps)
        assert np.sqrt(np.mean(out[len(x) // 2:] ** 2)) > 1e-4


# --------------------------------------------------------------------------- #
# miniGRID — micro-timing shift sequencer
# --------------------------------------------------------------------------- #
class TestMicroTimingSequencer:
    def test_imports(self):
        from sound.generators.micro_timing_seq import (
            MicroTimingSequencer, SHUFFLE_STYLES, VINTAGE_OFFSETS,
        )
        assert len(SHUFFLE_STYLES) == 7  # 7 vintage machines
        assert "mpc60" in SHUFFLE_STYLES and "tr909" in SHUFFLE_STYLES
        assert len(VINTAGE_OFFSETS) == len(SHUFFLE_STYLES)

    def test_shift_moves_events(self):
        from sound.generators.micro_timing_seq import MicroTimingSequencer
        seq = MicroTimingSequencer(bpm=120)
        seq.add_lane(note=36, steps=[1, 0, 0, 0] * 4, lane_id=0, shift_ms=0.0)
        seq.add_lane(note=42, steps=[1, 0, 0, 0] * 4, lane_id=1, shift_ms=+20.0)
        ev0 = seq.render(bars=1)
        t0 = [e[0] for e in ev0 if e[1] == 36][0]
        t1 = [e[0] for e in ev0 if e[1] == 42][0]
        assert t1 - t0 == pytest.approx(0.020, abs=1e-3)

    def test_shift_clamped_to_64ms(self):
        from sound.generators.micro_timing_seq import MicroTimingSequencer
        seq = MicroTimingSequencer(bpm=120)
        seq.add_lane(note=36, steps=[1, 0, 0, 0] * 4, lane_id=0, shift_ms=0.0)
        seq.add_lane(note=42, steps=[1, 0, 0, 0] * 4, lane_id=1, shift_ms=999.0)
        assert seq.lanes[1]["shift_ms"] == 64.0

    def test_shuffle_styles_differ(self):
        from sound.generators.micro_timing_seq import MicroTimingSequencer
        seq = MicroTimingSequencer(bpm=120)
        seq.add_lane(note=36, steps=[1, 0, 0, 0] * 4, lane_id=0)
        seq.set_shuffle("tr909", amount=1.0)
        t_tr = [e[0] for e in seq.render(bars=1)]
        seq.set_shuffle("mpc60", amount=1.0)
        t_mpc = [e[0] for e in seq.render(bars=1)]
        assert not np.allclose(t_tr, t_mpc)

    def test_mute_removes_lane(self):
        from sound.generators.micro_timing_seq import MicroTimingSequencer
        seq = MicroTimingSequencer(bpm=120)
        seq.add_lane(note=36, steps=[1, 0, 0, 0] * 4, lane_id=0)
        seq.add_lane(note=42, steps=[1, 0, 0, 0] * 4, lane_id=1, muted=True)
        ev = seq.render(bars=1)
        assert all(e[1] == 36 for e in ev)

    def test_unknown_shuffle_raises(self):
        from sound.generators.micro_timing_seq import MicroTimingSequencer
        seq = MicroTimingSequencer()
        with pytest.raises(ValueError):
            seq.set_shuffle("nope")


# --------------------------------------------------------------------------- #
# Parish Audio — overlapping-band parametric compressor
# --------------------------------------------------------------------------- #
class TestOverlapCompressor:
    def test_imports(self):
        from sound.effects.overlap_comp import OverlapCompressor, CompBand
        assert OverlapCompressor is not None

    def test_max_10_bands(self):
        from sound.effects.overlap_comp import OverlapCompressor, CompBand
        comp = OverlapCompressor(SR)
        for i in range(10):
            comp.add_band(CompBand(freq=200 + i * 500))
        with pytest.raises(ValueError):
            comp.add_band(CompBand(freq=1000))

    def test_invalid_detect_raises(self):
        from sound.effects.overlap_comp import CompBand
        with pytest.raises(ValueError):
            CompBand(detect="bogus")

    def test_compression_reduces_level(self):
        from sound.effects.overlap_comp import OverlapCompressor, CompBand
        comp = OverlapCompressor(SR)
        comp.add_band(CompBand(freq=1000, width=2.0, threshold_db=-30,
                               ratio=8, makeup_db=0.0))
        rng = np.random.RandomState(0)
        x = rng.randn(SR // 2) * 0.5
        y = comp.process(x)
        assert np.sqrt(np.mean(y ** 2)) < np.sqrt(np.mean(x ** 2))

    def test_band_detection_vs_full(self):
        from sound.effects.overlap_comp import OverlapCompressor, CompBand
        # a band triggered only by its own narrow region should react less to
        # a signal far outside its band than a band detecting full-range
        comp1 = OverlapCompressor(SR)
        comp1.add_band(CompBand(freq=100, width=0.5, threshold_db=-24, ratio=8))
        comp2 = OverlapCompressor(SR)
        comp2.add_band(CompBand(freq=100, width=0.5, threshold_db=-24, ratio=8,
                                detect="full"))
        t = np.linspace(0, 0.25, SR // 4, endpoint=False)
        # 5 kHz content: far from the 100 Hz band
        x = 0.4 * np.sin(2 * np.pi * 5000 * t)
        y1 = comp1.process(x)
        y2 = comp2.process(x)
        # full-range detection compresses more of the 5 kHz signal
        assert np.sqrt(np.mean(y2 ** 2)) < np.sqrt(np.mean(y1 ** 2))

    def test_sidechain_detection(self):
        from sound.effects.overlap_comp import OverlapCompressor, CompBand
        comp = OverlapCompressor(SR)
        comp.add_band(CompBand(freq=1000, width=2.0, threshold_db=-20, ratio=6,
                               detect="sidechain"))
        t = np.linspace(0, 0.25, SR // 4, endpoint=False)
        x = 0.3 * np.sin(2 * np.pi * 1000 * t)
        # sidechain below threshold (after band filtering) vs well above it
        sc_quiet = 0.1 * np.sin(2 * np.pi * 60 * t)
        sc_loud = 1.0 * np.sin(2 * np.pi * 60 * t)
        y_quiet = comp.process(x, sidechain=sc_quiet)
        y_loud = comp.process(x, sidechain=sc_loud)
        assert np.sqrt(np.mean(y_loud ** 2)) < np.sqrt(np.mean(y_quiet ** 2))
