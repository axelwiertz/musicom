"""Tests for gear logic replicated from the 2026-08-27 surveillance scan.

Covers:
- Korg Volca Drum alt firmware: trig-condition sequencer
- AudioKit Pro Super 606: 606-style drum synthesis engine
- Groove Synthesis 3rd Wave: spectral wavetable extraction
- Hot Shower Audio bathROOMs: room reverb with slap/wash controls
"""

import numpy as np
import pytest

SR = 44100


# --------------------------------------------------------------------------- #
# Volca Drum alt firmware — trig conditions
# --------------------------------------------------------------------------- #
class TestTrigConditionSequencer:
    def test_imports(self):
        from sound.generators.trig_cond_seq import (
            TrigConditionSequencer, ELEKTRON_PROBS, GHOST_VELOCITY_MAX,
        )
        assert ELEKTRON_PROBS == (50, 62, 75, 87)
        assert GHOST_VELOCITY_MAX == 16

    def test_always_fires_every_pass(self):
        from sound.generators.trig_cond_seq import TrigConditionSequencer
        seq = TrigConditionSequencer(steps=4)
        seq.set_condition(0, "always")
        ev = seq.generate(passes=3, seed=0)
        assert len(ev) == 3

    def test_every_n(self):
        from sound.generators.trig_cond_seq import TrigConditionSequencer
        seq = TrigConditionSequencer(steps=4)
        seq.set_condition(1, "every", n=2)
        ev = seq.generate(passes=4, seed=0)
        # fires on passes 2 and 4 only
        assert len(ev) == 2

    def test_first_and_last(self):
        from sound.generators.trig_cond_seq import TrigConditionSequencer
        seq = TrigConditionSequencer(steps=4)
        seq.set_condition(0, "first")
        seq.set_condition(1, "last")
        ev = seq.generate(passes=4, seed=0)
        assert len(ev) == 2

    def test_fill_only(self):
        from sound.generators.trig_cond_seq import TrigConditionSequencer
        seq = TrigConditionSequencer(steps=4)
        seq.set_condition(2, "fill")
        assert len(seq.generate(passes=2, fill=False, seed=0)) == 0
        assert len(seq.generate(passes=2, fill=True, seed=0)) == 2

    def test_ghost_note_via_negative_accent(self):
        from sound.generators.trig_cond_seq import TrigConditionSequencer
        seq = TrigConditionSequencer(steps=4)
        seq.set_accent(0, -40)
        ev = seq.generate(passes=1, seed=0)
        _, vel, ghost = ev[0]
        assert ghost is True
        assert vel <= 16

    def test_slice_sub_steps(self):
        from sound.generators.trig_cond_seq import TrigConditionSequencer
        seq = TrigConditionSequencer(steps=4, subdivisions=4)
        seq.set_slice(0, 3)
        ev = seq.generate(passes=1, seed=0)
        fracs = sorted(e[0] for e in ev)
        # three sub-hits inside step 0, spaced by 1/3
        assert len(fracs) >= 3
        assert fracs[0] == 0.0
        assert abs(fracs[1] - 1 / 3) < 1e-6

    def test_unknown_condition_raises(self):
        from sound.generators.trig_cond_seq import TrigConditionSequencer
        seq = TrigConditionSequencer(steps=4)
        with pytest.raises(ValueError):
            seq.set_condition(0, "bogus")


# --------------------------------------------------------------------------- #
# Super 606 — drum synthesis engine
# --------------------------------------------------------------------------- #
class TestDrumSynth606:
    def test_imports(self):
        from sound.synthesis.drum_synth_606 import DrumSynth606, FLAM_TYPES
        assert "medium" in FLAM_TYPES and "ahead" in FLAM_TYPES

    def test_kick_is_pitched_and_swept(self):
        from sound.synthesis.drum_synth_606 import DrumSynth606
        ds = DrumSynth606(sample_rate=SR)
        k = ds.kick(decay=0.3, xl=True)
        assert len(k) > 0
        assert np.max(np.abs(k)) == pytest.approx(1.0, abs=1e-3)
        # energy concentrated early (decaying hit)
        assert np.mean(k[: len(k) // 4] ** 2) > np.mean(k[len(k) // 2:] ** 2)

    def test_xl_kick_longer_than_normal(self):
        from sound.synthesis.drum_synth_606 import DrumSynth606
        ds = DrumSynth606(sample_rate=SR)
        assert len(ds.kick(decay=0.4, xl=True)) > len(ds.kick(decay=0.4))

    def test_snare_has_noise_and_body(self):
        from sound.synthesis.drum_synth_606 import DrumSynth606
        ds = DrumSynth606(sample_rate=SR)
        s = ds.snare()
        assert np.max(np.abs(s)) == pytest.approx(1.0, abs=1e-3)

    def test_hat_closed_shorter_than_open(self):
        from sound.synthesis.drum_synth_606 import DrumSynth606
        ds = DrumSynth606(sample_rate=SR)
        assert len(ds.hat(closed=True)) < len(ds.hat(closed=False))

    def test_clap_multi_burst(self):
        from sound.synthesis.drum_synth_606 import DrumSynth606
        ds = DrumSynth606(sample_rate=SR)
        c = ds.clap()
        assert np.max(np.abs(c)) == pytest.approx(1.0, abs=1e-3)

    def test_flam_types(self):
        from sound.synthesis.drum_synth_606 import DrumSynth606
        ds = DrumSynth606(sample_rate=SR)
        s = ds.snare()
        f = ds.flam(s, kind="wide")
        assert len(f) > len(s)  # offset adds length

    def test_render_sequence_grid(self):
        from sound.synthesis.drum_synth_606 import DrumSynth606
        ds = DrumSynth606(sample_rate=SR)
        steps = [120, 0, 0, 0, 90, 0, 0, 0,
                 110, 0, 0, 0, 95, 0, 0, 0]
        beat = ds.render_sequence(steps, bpm=120.0)
        assert np.max(np.abs(beat)) == pytest.approx(1.0, abs=1e-3)
        # rest steps contribute nothing; beat has 4 hits
        assert np.count_nonzero(beat) > 0


# --------------------------------------------------------------------------- #
# 3rd Wave — spectral wavetable extraction
# --------------------------------------------------------------------------- #
class TestSpectralWavetable:
    def test_imports(self):
        from sound.synthesis.spectral_wavetable import (
            SpectralWavetableExtractor, hanning,
        )
        w = hanning(64)
        assert w.shape == (64,)
        assert np.all(w >= 0.0) and np.all(w <= 1.0)

    def test_extract_shape(self):
        from sound.synthesis.spectral_wavetable import SpectralWavetableExtractor
        rng = np.random.default_rng(0)
        t = np.arange(SR) / SR
        src = np.sin(2 * np.pi * np.cumsum(220 * (1 + 0.01 * np.sin(t))) / SR)
        ext = SpectralWavetableExtractor(fft_size=1024, hop=256)
        wt = ext.extract(src, n_frames=8)
        assert wt.shape == (8, 512)
        # rows normalized to [-1, 1]
        assert np.max(np.abs(wt)) <= 1.0 + 1e-6

    def test_oscillator_produces_audio(self):
        from sound.synthesis.spectral_wavetable import SpectralWavetableExtractor
        rng = np.random.default_rng(1)
        t = np.arange(22050) / 22050
        src = np.sin(2 * np.pi * np.cumsum(220 * (1 + 0.02 * np.sin(t))) / 22050)
        ext = SpectralWavetableExtractor(fft_size=1024, hop=256)
        wt = ext.extract(src, n_frames=4)
        osc = ext.wavetable_oscillator(wt, freq=220.0, sr=22050, dur=0.2)
        assert len(osc) == 4410
        assert np.sqrt(np.mean(osc ** 2)) > 0.01

    def test_short_audio_raises(self):
        from sound.synthesis.spectral_wavetable import SpectralWavetableExtractor
        ext = SpectralWavetableExtractor(fft_size=1024)
        with pytest.raises(ValueError):
            ext.extract(np.zeros(100))

    def test_deterministic_with_seed(self):
        from sound.synthesis.spectral_wavetable import SpectralWavetableExtractor
        rng = np.random.default_rng(3)
        t = np.arange(22050) / 22050
        src = np.sin(2 * np.pi * np.cumsum(220 * (1 + 0.02 * np.sin(t))) / 22050)
        ext = SpectralWavetableExtractor(fft_size=1024, hop=256)
        a = ext.extract(src, n_frames=8, seed=9)
        b = ext.extract(src, n_frames=8, seed=9)
        assert np.array_equal(a, b)


# --------------------------------------------------------------------------- #
# bathROOMs — room reverb
# --------------------------------------------------------------------------- #
class TestRoomReverb:
    def test_imports(self):
        from sound.effects.room_reverb import RoomReverb, comb, allpass
        x = np.zeros(200)
        x[0] = 1.0
        y = comb(x, 20, 0.5)
        assert len(y) == 200 and y[20] > 0
        a = allpass(x, 10, 0.5)
        assert len(a) == 200

    def test_process_shapes_output(self):
        from sound.effects.room_reverb import RoomReverb
        rev = RoomReverb(sample_rate=16000)
        x = np.sin(2 * np.pi * 440 * np.arange(8000) / 16000) * np.exp(-np.arange(8000) / 800)
        out = rev.process(x, position=0.5, surface=0.5, slap=0.3, wash=0.5, mix=0.4)
        assert len(out) == len(x)
        assert np.max(np.abs(out)) > 0.01

    def test_far_setting_rings_longer(self):
        from sound.effects.room_reverb import RoomReverb
        rev = RoomReverb(sample_rate=16000, room_size=0.7)
        x = np.zeros(16000)
        x[:80] = 1.0
        near = rev.process(x, position=0.1, surface=0.5, slap=0.0, wash=0.3, mix=1.0)
        far = rev.process(x, position=0.9, surface=0.9, slap=0.5, wash=0.7, mix=1.0)
        tail_near = np.sqrt(np.mean(near[8000:] ** 2))
        tail_far = np.sqrt(np.mean(far[8000:] ** 2))
        assert tail_far > tail_near

    def test_mix_controls_dry_wet(self):
        from sound.effects.room_reverb import RoomReverb
        rev = RoomReverb(sample_rate=16000)
        x = np.sin(2 * np.pi * 440 * np.arange(4000) / 16000)
        dry = rev.process(x, mix=0.0)
        assert np.allclose(dry, x, atol=1e-6)
        wet = rev.process(x, mix=1.0)
        assert not np.allclose(wet, x, atol=1e-3)
