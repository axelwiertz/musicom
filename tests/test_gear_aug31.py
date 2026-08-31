"""Tests for gear logic replicated from the 2026-08-31 surveillance scan.

Covers:
- Asterism: param-lock step sequencer with ratchet + freeze-aware randomization
- Cherry Audio Memorymode 2: stacked-oscillator Memorymoog-style voice
- Bitwig Studio 6.1 Sampler: auto tempo/pitch detection + sample slicer + play modes
"""

import numpy as np
import pytest

SR = 44100


# --------------------------------------------------------------------------- #
# Asterism — param-lock step sequencer
# --------------------------------------------------------------------------- #
class TestParamLockSequencer:
    def test_imports(self):
        from sound.generators.param_lock_seq import ParamLockSequencer
        seq = ParamLockSequencer(steps=16, subdivisions=4)
        assert seq.steps == 16 and seq.subdivisions == 4

    def test_lock_overrides_base(self):
        from sound.generators.param_lock_seq import ParamLockSequencer
        seq = ParamLockSequencer(steps=4)
        seq.set_base(pitch=60, velocity=100)
        seq.set_active(1)
        seq.lock_param(1, pitch=72)
        ev = seq.generate(seed=0)
        assert len(ev) == 1
        _, params = ev[0]
        assert params["pitch"] == 72       # locked
        assert params["velocity"] == 100   # base fallback

    def test_ratchet_produces_sub_hits(self):
        from sound.generators.param_lock_seq import ParamLockSequencer
        seq = ParamLockSequencer(steps=16, subdivisions=4)
        seq.set_active(11)
        seq.set_ratchet(11, 4)
        ev = seq.generate(seed=0)
        assert len(ev) == 4
        fracs = sorted(e[0] for e in ev)
        assert fracs[0] == 11.0
        assert fracs[1] == 11.25
        assert fracs[3] == 11.75

    def test_randomize_respects_freeze(self):
        from sound.generators.param_lock_seq import ParamLockSequencer
        seq = ParamLockSequencer(steps=4)
        seq.set_base(pitch=60, velocity=100)
        seq.lock_param(1, velocity=127)
        seq.randomize({"velocity": (40, 90)}, seed=1, frozen=["velocity"])
        assert seq.base["velocity"] == 100       # frozen untouched
        assert seq.locks[1]["velocity"] == 127   # frozen lock untouched
        seq.randomize({"pitch": (48, 60)}, seed=2)
        assert 48 <= seq.base["pitch"] < 60      # unlocked rolled

    def test_inactive_steps_silent(self):
        from sound.generators.param_lock_seq import ParamLockSequencer
        seq = ParamLockSequencer(steps=4)
        seq.set_base(velocity=100)
        seq.set_active(0)
        assert len(seq.generate(seed=0)) == 1

    def test_bad_ratchet_raises(self):
        from sound.generators.param_lock_seq import ParamLockSequencer
        seq = ParamLockSequencer(steps=4, subdivisions=4)
        with pytest.raises(ValueError):
            seq.set_ratchet(0, 5)


# --------------------------------------------------------------------------- #
# Memorymode 2 — stacked-oscillator Memorymoog-style voice
# --------------------------------------------------------------------------- #
class TestMemorymoogVoice:
    def test_imports(self):
        from sound.synthesis.memorymoog_synth import MemorymoogVoice, WHOLE_TONE_CENTS
        assert WHOLE_TONE_CENTS == 200.0

    def test_render_shapes_and_normalized(self):
        from sound.synthesis.memorymoog_synth import MemorymoogVoice
        v = MemorymoogVoice(sample_rate=SR)
        a = v.render_note(220.0, 0.5, doubling=1)
        assert len(a) == int(0.5 * SR)
        assert np.max(np.abs(a)) == pytest.approx(1.0, abs=1e-3)

    def test_whole_tone_offsets_differ_from_unison(self):
        from sound.synthesis.memorymoog_synth import MemorymoogVoice
        v = MemorymoogVoice(sample_rate=SR)
        v.detune_mode = "unison"
        u = v._osc_detune(0)
        v.detune_mode = "whole_tone"
        w = v._osc_detune(0)
        assert u != w
        assert w == -200.0

    def test_doubling_stacks_voices(self):
        from sound.synthesis.memorymoog_synth import MemorymoogVoice
        v = MemorymoogVoice(sample_rate=SR)
        single = v.render_note(220.0, 0.3, doubling=1)
        single2 = v.render_note(220.0, 0.3, doubling=1)
        triple = v.render_note(220.0, 0.3, doubling=3)
        assert len(single) == len(triple)
        # deterministic rendering (reproducibility contract)
        assert np.array_equal(single, single2)
        # doubling adds per-voice detune -> a different, chorused waveform
        assert not np.array_equal(single, triple)
        assert np.max(np.abs(triple - single)) > 0.05

    def test_lowpass_attenuates_high_freq(self):
        from sound.synthesis.memorymoog_synth import MemorymoogVoice
        v = MemorymoogVoice(sample_rate=SR)
        v.cutoff = 300.0
        low = v._lowpass4(np.sin(2 * np.pi * 3000 * np.arange(4410) / SR))
        # steady-state RMS of a 3000 Hz tone through a 300 Hz LP is small
        assert np.sqrt(np.mean(low[1000:] ** 2)) < 0.2


# --------------------------------------------------------------------------- #
# Bitwig 6.1 Sampler — auto detection + slicing + play modes
# --------------------------------------------------------------------------- #
class TestSampleSlicer:
    def test_imports(self):
        from sound.generators.sample_slicer import SampleSlicer, Slice, auto_tempo, auto_pitch
        assert Slice(0, 100).length == 100

    def test_auto_pitch_detects_fundamental(self):
        from sound.generators.sample_slicer import auto_pitch
        sr = 22050
        t = np.arange(sr) / sr
        src = np.sin(2 * np.pi * 110 * t)
        f = auto_pitch(src, sr)
        assert abs(f - 110.0) < 1.0

    def test_auto_tempo_detects_bpm(self):
        from sound.generators.sample_slicer import auto_tempo
        sr = 22050
        dur = 2.0
        n = int(dur * sr)
        audio = np.zeros(n)
        for start in np.arange(0, dur, 0.375):  # 160 BPM
            i0 = int(start * sr)
            burst = np.random.default_rng(int(start * 100)).uniform(-1, 1, int(0.05 * sr))
            burst *= np.exp(-np.arange(len(burst)) / (0.015 * sr))
            audio[i0:i0 + len(burst)] += burst
        bpm = auto_tempo(audio, sr)
        assert 150.0 <= bpm <= 170.0

    def test_detect_onsets_and_slice(self):
        from sound.generators.sample_slicer import SampleSlicer
        sr = 22050
        n = sr
        t = np.arange(n) / sr
        # two bursts -> two onsets
        audio = np.zeros(n)
        for start in (0.0, 0.5):
            i0 = int(start * sr)
            audio[i0:i0 + 1102] = np.sin(2 * np.pi * 440 * np.arange(1102) / sr)
        slicer = SampleSlicer(sample_rate=sr)
        onsets = slicer.detect_onsets(audio)
        slices = slicer.slice_at(audio, onsets)
        assert len(onsets) >= 2
        assert len(slices) == len(onsets)
        assert slices[0].start == 0
        assert slices[-1].end == n

    def test_play_modes(self):
        from sound.generators.sample_slicer import SampleSlicer, Slice
        slicer = SampleSlicer(sample_rate=SR)
        src = np.linspace(0, 1, 100)
        sl = Slice(0, 100)
        fwd = slicer.render_slice(src, sl, mode="forward")
        rev = slicer.render_slice(src, sl, mode="reverse")
        assert np.array_equal(fwd, rev[::-1])
        lp = slicer.render_slice(src, sl, mode="loop", max_dur=0.005)
        assert len(lp) > len(fwd)  # looped past the single pass

    def test_render_grid_mixes_slices(self):
        from sound.generators.sample_slicer import SampleSlicer, Slice
        slicer = SampleSlicer(sample_rate=SR)
        src = np.sin(2 * np.pi * 440 * np.arange(SR) / SR)
        slices = [Slice(0, 2205), Slice(2205, 4410)]
        out = slicer.render_grid(src, slices, steps=8, mode="oneshot")
        assert out.dtype == np.float32
        assert len(out) == 8 * int(0.125 * SR)
        assert np.count_nonzero(out) > 0
