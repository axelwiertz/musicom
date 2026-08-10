"""Tests for replicable gear logic added from the Aug 2026 surveillance report.

Covers:
- KHÔRA: just intonation scales, Tenney height, chord generators
- Vowel Blender: formant filters, vowel blending, XY pad
- ANUKARI: mass-spring physical modeling
- SynthEdit: modular node-graph DSP
- VST Classics: tape delay, sample player, drum machine
"""

import numpy as np
import pytest
from scipy.signal import butter, lfilter

SR = 44100


# --------------------------------------------------------------------------- #
# KHÔRA — Just Intonation
# --------------------------------------------------------------------------- #
class TestJustIntonation:
    def test_imports(self):
        from sound.tuning import JustIntonation, JIChordGenerator
        assert JustIntonation is not None
        assert JIChordGenerator is not None

    def test_scale_major(self):
        from sound.tuning import JustIntonation
        ji = JustIntonation(root_freq=220.0)
        ratios = ji.scale("major")
        assert ratios[0] == (1, 1)
        assert (3, 2) in ratios  # perfect fifth
        assert (5, 4) in ratios  # major third

    def test_scale_freqs(self):
        from sound.tuning import JustIntonation
        ji = JustIntonation(root_freq=220.0)
        freqs = ji.scale_freqs("major")
        assert freqs[0] == pytest.approx(220.0)
        assert freqs[4] == pytest.approx(330.0)  # 3/2 * 220

    def test_tenney_height(self):
        from sound.tuning import tenney_height
        # unison = log2(1) = 0
        assert tenney_height(1, 1) == pytest.approx(0.0)
        # octave = log2(2) = 1
        assert tenney_height(2, 1) == pytest.approx(1.0)
        # fifth 3/2 = log2(6) ≈ 2.585
        assert tenney_height(3, 2) == pytest.approx(np.log2(6))

    def test_consonance_score(self):
        from sound.tuning import consonance_score
        consonant = [(1, 1), (3, 2)]  # fifth
        dissonant = [(1, 1), (15, 8)]  # major 7th
        assert consonance_score(consonant) < consonance_score(dissonant)

    def test_chord_generators(self):
        from sound.tuning import JustIntonation, JIChordGenerator
        ji = JustIntonation(220.0)
        gen = JIChordGenerator()
        ratios = ji.scale("major")

        # genesis picks simplest subset
        chord = gen.genesis(ratios, size=4)
        assert len(chord) == 4
        assert (1, 1) in chord  # root always most consonant

        # metabole retains common tones
        old = [(1, 1), (3, 2)]
        pool = [(5, 4), (4, 3), (5, 3)]
        new = gen.metabole(old, pool, retain=1)
        assert new[0] == (1, 1)

        # topos transposes
        transposed = gen.topos([(1, 1), (3, 2)], 5, 4)
        assert transposed[0] == (5, 4)  # (1*5, 1*4)

        # skia picks dark subset
        dark = gen.skia(ratios, size=3)
        assert len(dark) == 3


# --------------------------------------------------------------------------- #
# Vowel Blender — formant filters
# --------------------------------------------------------------------------- #
class TestVowelFilterBank:
    def test_imports(self):
        from sound.effects import VowelFilterBank, VOWEL_FORMANTS
        assert VOWEL_FORMANTS["a"] == (730.0, 1090.0, 2440.0)

    def test_process_changes_audio(self):
        from sound.effects import VowelFilterBank
        vfb = VowelFilterBank(SR)
        t = np.linspace(0, 0.5, int(0.5 * SR))
        audio = np.sin(2 * np.pi * 200 * t) + 0.5 * np.sin(2 * np.pi * 900 * t)
        filtered = vfb.process(audio, "a")
        assert not np.allclose(filtered, audio)
        assert np.max(np.abs(filtered)) > 0.01

    def test_blend_between_vowels(self):
        from sound.effects import VowelFilterBank
        vfb = VowelFilterBank(SR)
        t = np.linspace(0, 0.5, int(0.5 * SR))
        audio = np.sin(2 * np.pi * 200 * t) + np.sin(2 * np.pi * 900 * t)
        v_a = vfb.process(audio, "a")
        v_i = vfb.process(audio, "i")
        blend = vfb.blend(audio, "a", "i", amount=0.5)
        expected = 0.5 * v_a + 0.5 * v_i
        assert np.allclose(blend, expected)

    def test_xy_position(self):
        from sound.effects import VowelFilterBank
        vfb = VowelFilterBank(SR)
        t = np.linspace(0, 0.5, int(0.5 * SR))
        audio = np.sin(2 * np.pi * 300 * t) + np.sin(2 * np.pi * 1200 * t)
        out = vfb.xy_position(audio, x=0.5, y=0.5)
        assert np.max(np.abs(out)) > 0.01

    def test_unknown_vowel(self):
        from sound.effects import VowelFilterBank
        vfb = VowelFilterBank(SR)
        with pytest.raises(ValueError):
            vfb.process(np.zeros(100), "zz")


# --------------------------------------------------------------------------- #
# ANUKARI — mass-spring physical modeling
# --------------------------------------------------------------------------- #
class TestMassSpring:
    def test_imports(self):
        from sound.synthesis import MassSpringSystem, Body, Spring
        assert MassSpringSystem is not None

    def test_pluck_rings(self):
        from sound.synthesis import MassSpringSystem
        ms = MassSpringSystem(SR)
        audio = ms.render_pluck(duration=0.5, freq=440.0)
        assert len(audio) == int(0.5 * SR)
        # should have a fundamental near 440
        spectrum = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / SR)
        peak_idx = np.argmax(spectrum[1:]) + 1
        assert abs(freqs[peak_idx] - 440.0) < 80.0  # approximate

    def test_multi_body(self):
        from sound.synthesis import MassSpringSystem
        ms = MassSpringSystem(SR)
        b1 = ms.add_body(pos=(0.0, 0.0, 0.0))
        b2 = ms.add_body(pos=(0.05, 0.0, 0.0))
        b3 = ms.add_body(pos=(0.1, 0.0, 0.0))
        ms.add_spring(b1, b2, stiffness=500.0, damping=0.01)
        ms.add_spring(b2, b3, stiffness=500.0, damping=0.01)
        ms.excite(b2, impulse=(0.0, 0.5, 0.0))
        audio = ms.render_mic(b3, duration=0.3)
        assert np.max(np.abs(audio)) > 0.01

    def test_fixed_body_stays(self):
        from sound.synthesis import MassSpringSystem
        ms = MassSpringSystem(SR)
        anchor = ms.add_body(pos=(0.0, 0.0, 0.0), fixed=True)
        free = ms.add_body(pos=(0.1, 0.0, 0.0))
        ms.add_spring(anchor, free, stiffness=100.0, damping=0.05)
        ms.excite(free, impulse=(0.0, 0.1, 0.0))
        ms._step(1.0 / SR)
        assert np.all(anchor.pos == 0.0)  # fixed body doesn't move


# --------------------------------------------------------------------------- #
# SynthEdit — modular node graph
# --------------------------------------------------------------------------- #
class TestModularGraph:
    def test_imports(self):
        from sound.modular import ModularGraph, OscNode, GainNode, OutNode
        assert ModularGraph is not None

    def test_osc_through_gain_to_out(self):
        from sound.modular import ModularGraph, OscNode, GainNode, OutNode
        g = ModularGraph(SR)
        osc = g.add(OscNode(freq=440.0, waveform="sine"))
        gain = g.add(GainNode(gain=0.5))
        out = g.add(OutNode())
        g.connect(osc, "out", gain, "in")
        g.connect(gain, "out", out, "in")
        audio = g.render(duration=0.1)
        assert len(audio) == int(0.1 * SR)
        assert np.max(np.abs(audio)) > 0.1  # normalized

    def test_topo_order_correct(self):
        """Output node should come after source in topo sort."""
        from sound.modular import ModularGraph, OscNode, GainNode, OutNode
        g = ModularGraph(SR)
        osc = g.add(OscNode(freq=440.0))
        out = g.add(OutNode())
        g.connect(osc, "out", out, "in")
        order = g._topo_sort()
        assert order.index(osc) < order.index(out)

    def test_mix_two_sources(self):
        from sound.modular import ModularGraph, OscNode, MixNode, OutNode
        g = ModularGraph(SR)
        o1 = g.add(OscNode(freq=440.0, waveform="sine"))
        o2 = g.add(OscNode(freq=880.0, waveform="sine"))
        mix = g.add(MixNode(gains=[0.5, 0.5]))
        out = g.add(OutNode())
        g.connect(o1, "out", mix, "in0")
        g.connect(o2, "out", mix, "in1")
        g.connect(mix, "out", out, "in")
        audio = g.render(duration=0.1)
        assert np.max(np.abs(audio)) > 0.1

    def test_filter_node(self):
        from sound.modular import ModularGraph, OscNode, FilterNode, OutNode
        g = ModularGraph(SR)
        osc = g.add(OscNode(freq=440.0, waveform="saw"))
        filt = g.add(FilterNode(cutoff=500.0))
        out = g.add(OutNode())
        g.connect(osc, "out", filt, "in")
        g.connect(filt, "out", out, "in")
        audio = g.render(duration=0.1)
        assert np.max(np.abs(audio)) > 0.1

    def test_delay_node(self):
        from sound.modular import ModularGraph, OscNode, DelayNode, OutNode
        g = ModularGraph(SR)
        osc = g.add(OscNode(freq=440.0, waveform="sine"))
        delay = g.add(DelayNode(delay_seconds=0.05, feedback=0.3))
        out = g.add(OutNode())
        g.connect(osc, "out", delay, "in")
        g.connect(delay, "out", out, "in")
        audio = g.render(duration=0.2)
        assert len(audio) == int(0.2 * SR)


# --------------------------------------------------------------------------- #
# VST Classics — tape delay, sample player, drum machine
# --------------------------------------------------------------------------- #
class TestTapeDelay:
    def test_delay_adds_echo(self):
        from sound.effects import TapeDelay
        td = TapeDelay(SR)
        t = np.linspace(0, 0.5, int(0.5 * SR))
        audio = np.sin(2 * np.pi * 440 * t)
        delayed = td.process(audio, delay_seconds=0.1, feedback=0.3)
        assert len(delayed) >= len(audio)  # input + delay tail
        assert not np.allclose(delayed[:len(audio)], audio)

    def test_delay_has_tail(self):
        """After a short input, output should extend beyond via feedback."""
        from sound.effects import TapeDelay
        td = TapeDelay(SR)
        n = int(0.1 * SR)
        t = np.linspace(0, 0.1, n)
        audio = np.sin(2 * np.pi * 440 * t)
        delayed = td.process(audio, delay_seconds=0.05, feedback=0.5)
        # tail energy after input ends
        tail = delayed[n:]
        assert np.sqrt(np.mean(tail ** 2)) > 1e-4


class TestSamplePlayer:
    def test_load_play(self):
        from sound.effects import SamplePlayer
        sp = SamplePlayer(SR)
        sample = np.sin(np.linspace(0, 20, 1000))
        sp.load(sample)
        audio = sp.play(duration=0.1)
        assert len(audio) == int(0.1 * SR)
        assert np.max(np.abs(audio)) > 0.01

    def test_pitch_shift(self):
        """Pitch shift 2.0 should double the zero-crossing rate."""
        from sound.effects import SamplePlayer
        sp = SamplePlayer(SR)
        t = np.linspace(0, 0.2, int(0.2 * SR))
        sample = np.sin(2 * np.pi * 440 * t)
        sp.load(sample)
        a1 = sp.play(duration=0.1, pitch_shift=1.0)
        a2 = sp.play(duration=0.1, pitch_shift=2.0)
        # count zero crossings
        z1 = np.sum(np.diff(np.sign(a1)) != 0)
        z2 = np.sum(np.diff(np.sign(a2)) != 0)
        assert z2 > z1


class TestDrumMachine:
    def test_play_pattern(self):
        from sound.effects import DrumMachine
        dm = DrumMachine(SR, bpm=120.0)
        pattern = ["kick", "", "snare", "", "hat", "", "kick", "snare"]
        audio = dm.play_pattern(pattern, steps_per_bar=8, bars=1)
        assert len(audio) > 0
        assert np.max(np.abs(audio)) > 0.01

    def test_kick_snare_hat_exist(self):
        from sound.effects import DrumMachine
        dm = DrumMachine(SR)
        for name in ("kick", "snare", "hat"):
            sample = dm.get_sample(name)
            assert len(sample) > 100
            assert np.max(np.abs(sample)) > 0.01


# --------------------------------------------------------------------------- #
# Stereo WAV round-trip (io.py regression — previous bug)
# --------------------------------------------------------------------------- #
class TestStereoTapeIO:
    def test_stereo_roundtrip(self, tmp_path):
        from sound.utils.io import write_wav, read_wav
        sr = 44100
        t = np.linspace(0, 0.1, int(0.1 * sr))
        left = np.sin(2 * np.pi * 440 * t)
        right = np.sin(2 * np.pi * 550 * t)
        stereo = np.column_stack([left, right])
        path = str(tmp_path / "stereo.wav")
        write_wav(path, stereo, sr)
        data, sr_out = read_wav(path)
        assert data.ndim == 2
        assert data.shape[0] == len(t)
        assert data.shape[1] == 2
        # left channel preserved
        assert np.corrcoef(data[:, 0], left)[0, 1] > 0.99
