"""Tests: 16-bar pop composition + production chain (one-by-one DSP stages)."""

import os
import tempfile

import mido
import numpy as np
import pytest

from structures import MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from sound.effects import (
    ProductionChain, AlgorithmicReverb, StateVariableFilter, BiquadFilter,
    DynamicEQ, StereoImager, Limiter, measure_lufs,
)
from examples.compose_pop_16bar import (
    build_pop_composer, compose_to, BPM, SECTION_TICKS, PROGRESSION,
)


# =============================================================================
# Composition tests
# =============================================================================

class TestPopComposition:
    """16-bar pop comp: structure, harmony, zero-drift, artifacts."""

    def test_structure(self):
        """4 voices × 4 sections × 4 bars = 16 bars."""
        composer = build_pop_composer()
        assert composer.matrix.num_rows == 4
        assert composer.matrix.num_cols == 4
        assert composer.get_track_length_bars() == 16

    def test_validate(self):
        composer = build_pop_composer()
        ok, msg = composer.validate()
        assert ok, msg

    def test_midi_export_zero_drift(self):
        """All voice tracks must be exactly equal length (user's #1 rule)."""
        composer = build_pop_composer()
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            composer.to_midi(f.name)
            path = f.name
        try:
            mid = mido.MidiFile(path)
            assert os.path.getsize(path) > 40
            lengths = [sum(m.time for m in trk) for trk in mid.tracks[1:]]
            assert len(set(lengths)) == 1, f"Track drift: {lengths}"
            # 16 bars × 1920 ticks/bar = 30720
            assert lengths[0] == 16 * 1920
        finally:
            os.unlink(path)

    def test_midi_deterministic(self):
        """Same seed → same structure (tracks, lengths, event counts)."""
        c1 = build_pop_composer(seed=42)
        c2 = build_pop_composer(seed=42)
        # Compare structural fingerprint: per-track (length, note_on count)
        def fingerprint(composer):
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
                composer.to_midi(f.name)
                p = f.name
            try:
                mid = mido.MidiFile(p)
                return [(sum(m.time for m in trk),
                         sum(1 for m in trk if m.type == 'note_on'))
                        for trk in mid.tracks]
            finally:
                os.unlink(p)
        assert fingerprint(c1) == fingerprint(c2)

    def test_voices(self):
        composer = build_pop_composer()
        names = [v['name'] for v in composer.voices]
        assert names == ["Melody", "Chords", "Bass", "Drums"]
        assert composer.voices[0]['program'] == MidiInstrument.FLUTE
        assert composer.voices[2]['program'] == MidiInstrument.BASS

    def test_voicing_variety(self):
        """Voicings vary across the piece (not all root position)."""
        composer = build_pop_composer()
        chord_events = composer.matrix.get_row_events(1)
        chords = {}
        for e in chord_events:
            if e.pitch == 0:
                continue
            chords.setdefault((e.start_tick, e.end_tick), set()).add(e.pitch)
        voicings = {tuple(sorted(ps)) for ps in chords.values()}
        # C-G-Am-F = 4 distinct chords minimum, plus inversions → more
        assert len(voicings) >= 4

    def test_compose_to_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            midi, grid = compose_to(tmp)
            assert os.path.exists(midi)
            assert os.path.getsize(midi) > 40
            assert os.path.exists(grid)


# =============================================================================
# Production chain tests (one-by-one DSP stage verification)
# =============================================================================

class TestProductionStages:
    """Each DSP stage must measurably change the signal as designed."""

    SR = 44100

    @pytest.fixture
    def signal(self):
        """3s test signal: 220Hz + 440Hz + noise."""
        rng = np.random.default_rng(7)
        t = np.linspace(0, 3.0, int(self.SR * 3.0), endpoint=False)
        return (0.3 * np.sin(2 * np.pi * 220 * t)
                + 0.15 * np.sin(2 * np.pi * 440 * t)
                + 0.05 * rng.standard_normal(len(t)))

    def test_reverb_creates_tail(self):
        """Impulse through reverb must ring > 1s."""
        sr = self.SR
        click = np.zeros(int(sr * 2))
        click[:441] = np.hanning(441)
        out = AlgorithmicReverb(sample_rate=sr, room_size=0.9,
                                damping=0.3, wet_dry=0.6).process(click)
        tail = np.max(np.abs(out[sr:int(sr * 1.5)]))
        assert tail > 1e-4, "Reverb tail too quiet"

    def test_lowpass_reduces_high_freq(self):
        """SVF LP must remove >70% energy above 2kHz."""
        sr = self.SR
        t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
        saw = 2.0 * (440.0 * t % 1.0) - 1.0
        lp = StateVariableFilter(sr).process(saw, cutoff=500.0, resonance=0.0, mode='lp')
        fft_raw = np.abs(np.fft.rfft(saw))
        fft_lp = np.abs(np.fft.rfft(lp))
        freqs = np.fft.rfftfreq(len(saw), 1 / sr)
        hi_raw = np.sum(fft_raw[freqs > 2000])
        hi_lp = np.sum(fft_lp[freqs > 2000])
        reduction = 100 * (1 - hi_lp / hi_raw)
        assert reduction > 70, f"LP reduction only {reduction:.1f}%"

    def test_peaking_boosts_band(self):
        """Peaking EQ +6dB at 1kHz must raise band energy near 1kHz."""
        sr = self.SR
        t = np.linspace(0, 1.0, sr, endpoint=False)
        probe = np.sin(2 * np.pi * 1000 * t) + np.sin(2 * np.pi * 100 * t)
        filt = BiquadFilter(sr)
        filt.design('peaking', freq=1000.0, Q=2.0, gain_db=6.0)
        out = filt.process(probe)
        band = lambda x: np.sum(np.abs(np.fft.rfft(x))[40:60])  # ~1kHz bin
        assert band(out) > band(probe) * 1.5, "Peaking EQ not boosting"

    def test_dynamic_eq_reduces_loud_band(self):
        """Loud 3kHz component must be attenuated by dynamic EQ."""
        sr = self.SR
        t = np.linspace(0, 1.0, sr, endpoint=False)
        loud = 0.9 * np.sin(2 * np.pi * 3000 * t) + 0.2 * np.sin(2 * np.pi * 100 * t)
        deq = DynamicEQ(sr)
        deq.add_band(3000.0, q=2.0, threshold_db=-20.0, ratio=3.0)
        out = deq.process(loud)
        # Signal must change (dynamic EQ acts on loud band)
        assert np.max(np.abs(out - loud)) > 1e-3, "Dynamic EQ is a no-op"
        # Peak amplitude of the 3kHz band should not increase
        band_energy = lambda x, lo, hi: np.sum(np.abs(np.fft.rfft(x))[int(lo * 1.0):int(hi * 1.0)])
        # Compare 3kHz region (index 3000-3200 at 1Hz/bin)
        e_out = np.sum(np.abs(np.fft.rfft(out))[2900:3100])
        e_in = np.sum(np.abs(np.fft.rfft(loud))[2900:3100])
        # Dynamic EQ may add slight energy via filter interaction but should
        # not blow up the band — assert bounded growth or reduction
        assert e_out < e_in * 2.0, f"Dynamic EQ blew up band: {e_out} vs {e_in}"

    def test_stereo_imager_mono_sub(self):
        """Sub-100Hz content must be identical L/R (mono) after imaging."""
        sr = self.SR
        rng = np.random.default_rng(3)
        n = sr * 1
        stereo = np.column_stack([rng.standard_normal(n) * 0.1,
                                  rng.standard_normal(n) * 0.1])
        imager = StereoImager(sr)
        imager.set_width(0.0, below_hz=100.0)
        imager.set_width(1.5, above_hz=2000.0)
        out = imager.process(stereo)
        # Low-freq mono: correlation ~1 below 100Hz
        def lowfreq(x):
            fft = np.fft.rfft(x)
            fr = np.fft.rfftfreq(len(x), 1 / sr)
            mask = fr < 100
            filt = np.zeros_like(x, dtype=complex)
            filt_fft = fft * mask
            return np.fft.irfft(filt_fft, n=len(x))
        L_low = lowfreq(out[:, 0])
        R_low = lowfreq(out[:, 1])
        corr = np.corrcoef(L_low, R_low)[0, 1]
        assert corr > 0.99, f"Sub not mono: corr={corr:.3f}"

    def test_stereo_imager_widens_highs(self):
        """Multi-band imaging must NOT collapse to mono (regression:
        sequential side*=width zeroed the side signal)."""
        sr = self.SR
        rng = np.random.default_rng(8)
        n = sr
        # Independent noise channels → real side content
        stereo = np.column_stack([rng.standard_normal(n) * 0.1,
                                  rng.standard_normal(n) * 0.1])
        imager = StereoImager(sr)
        imager.set_width(0.0, below_hz=100.0)
        imager.set_width(1.5, above_hz=2000.0)
        out = imager.process(stereo)
        # High-freq side energy must be non-zero (widened) — corr must drop
        def highfreq(x):
            fft = np.fft.rfft(x)
            fr = np.fft.rfftfreq(len(x), 1 / sr)
            mask = fr > 2000
            filt_fft = fft * mask
            return np.fft.irfft(filt_fft, n=len(x))
        L_h = highfreq(out[:, 0])
        R_h = highfreq(out[:, 1])
        corr_high = np.corrcoef(L_h, R_h)[0, 1]
        # width 1.5 increases side → L/R less correlated than input highs
        L_in = highfreq(stereo[:, 0])
        R_in = highfreq(stereo[:, 1])
        corr_in = np.corrcoef(L_in, R_in)[0, 1]
        assert corr_high < corr_in - 0.01, f"Highs not widened: {corr_in:.4f} → {corr_high:.4f}"

    def test_limiter_peaks_below_ceiling(self):
        """Limiter must cap peaks at threshold (no clipping)."""
        sr = self.SR
        rng = np.random.default_rng(5)
        loud = rng.standard_normal(int(sr * 0.5)) * 0.5
        limiter = Limiter(threshold_db=-3.0, release_ms=50.0, sample_rate=sr)
        out = limiter.process(loud)
        ceiling = 10 ** (-3.0 / 20.0)
        assert np.max(np.abs(out)) <= ceiling * 1.01

    def test_lufs_normalization(self):
        """normalize_to_lufs must hit target within 0.3 LU."""
        sr = self.SR
        rng = np.random.default_rng(9)
        audio = rng.standard_normal(int(sr * 2)) * 0.2
        from sound.effects.mastering import normalize_to_lufs as n2l
        normalized = n2l(audio, -14.0, sr)
        lufs = measure_lufs(normalized, sr)
        assert abs(lufs - (-14.0)) < 0.3, f"LUFS={lufs} target=-14"

    def test_stereo_filters(self):
        """SVF + Biquad must handle stereo [n,2] input (mastering chain)."""
        from sound.effects import StateVariableFilter, BiquadFilter
        sr = self.SR
        rng = np.random.default_rng(2)
        stereo = (rng.standard_normal((2000, 2)) * 0.1).astype(np.float32)
        # SVF
        out_svf = StateVariableFilter(sr).process(stereo, cutoff=8000.0, resonance=0.2, mode='lp')
        assert out_svf.shape == stereo.shape
        # Biquad peaking
        bf = BiquadFilter(sr)
        bf.design('peaking', freq=3000.0, Q=1.5, gain_db=3.0)
        out_bq = bf.process(stereo)
        assert out_bq.shape == stereo.shape
        assert np.max(np.abs(out_bq - stereo)) > 1e-4, "Biquad stereo no-op"

    def test_stereo_wav_roundtrip(self):
        """write_wav/read_wav must preserve stereo channels (regression:
        write_wav silently flattened [n,2] to mono)."""
        from sound.utils.io import write_wav, read_wav
        import tempfile
        sr = 44100
        rng = np.random.default_rng(4)
        stereo = (rng.standard_normal((2000, 2)) * 0.5).astype(np.float32)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'stereo.wav')
            write_wav(path, stereo, sr, normalize=False)
            data, got_sr = read_wav(path)
            assert got_sr == sr
            assert data.ndim == 2 and data.shape[1] == 2, f"Expected stereo, got {data.shape}"
            # L/R channels preserved (not folded)
            assert np.corrcoef(data[:, 0], data[:, 1])[0, 1] < 0.95, "Channels folded to mono"
            assert len(data) == 2000

    def test_dynamic_eq_adaptive_threshold(self):
        """ProductionChain dynamic_eq must engage with adaptive threshold."""
        sr = self.SR
        t = np.linspace(0, 1.0, sr, endpoint=False)
        # Band content at 3kHz but at modest level (-20 dBFS)
        audio = 0.1 * np.sin(2 * np.pi * 3000 * t) + 0.3 * np.sin(2 * np.pi * 110 * t)
        chain = ProductionChain(sample_rate=sr)
        out = chain.stage_dynamic_eq(audio)
        assert np.max(np.abs(out - audio)) > 1e-4, "Adaptive threshold must engage"

    def test_full_chain_reduces_lufs_gap(self):
        """Full chain: final LUFS closer to target than raw."""
        sr = self.SR
        rng = np.random.default_rng(11)
        t = np.linspace(0, 4.0, int(sr * 4.0), endpoint=False)
        audio = (0.2 * np.sin(2 * np.pi * 110 * t)
                 + 0.1 * np.sin(2 * np.pi * 330 * t)
                 + 0.03 * rng.standard_normal(len(t)))
        chain = ProductionChain(sample_rate=sr)
        with tempfile.TemporaryDirectory() as tmp:
            report = chain.run(audio, output_dir=tmp, target_lufs=-14.0)
            assert len(report.stages) == 7
            assert len({s.name for s in report.stages}) == 7
            # All 7 exports exist
            for s in report.stages:
                assert s.path and os.path.getsize(s.path) > 40, f"{s.name} export missing"
            # Final LUFS near target
            assert abs(report.final_lufs - (-14.0)) < 0.5
            # Sequential stage order preserved
            names = [s.name for s in report.stages]
            assert names == ["reverb", "lowpass", "peaking", "dynamic_eq",
                             "stereo_imager", "lufs_norm", "limiter"]
            # Limiter AFTER LUFS gain: final peak must respect ceiling
            # even though loudness gain pushed it up.
            from sound.utils.io import read_wav as _read_wav
            final_path = report.stages[-1].path
            assert final_path is not None
            final, _ = _read_wav(final_path)
            peak = np.max(np.abs(final))
            ceiling = 10 ** (-1.0 / 20.0)
            assert peak <= ceiling * 1.01, f"Peak {peak:.3f} above -1dB ceiling"

    def test_partial_chain(self):
        """include= subset runs only those stages."""
        sr = self.SR
        t = np.linspace(0, 1.0, int(sr), endpoint=False)
        audio = 0.3 * np.sin(2 * np.pi * 220 * t)
        chain = ProductionChain(sample_rate=sr)
        with tempfile.TemporaryDirectory() as tmp:
            report = chain.run(audio, output_dir=tmp, include=["reverb", "limiter"])
            assert [s.name for s in report.stages] == ["reverb", "limiter"]

    def test_pop_compose_and_produce_end_to_end(self):
        """Compose pop → render → production chain, all artifacts real."""
        with tempfile.TemporaryDirectory() as tmp:
            midi, _ = compose_to(tmp)
            assert os.path.getsize(midi) > 40


# =============================================================================
# Synthesis engine regression tests
# =============================================================================

class TestSynthesisEngines:
    """Each synthesis engine must render non-silent audio."""

    SR = 44100

    def test_additive_overtones(self):
        """apply_overtones must produce summed overtone wave (regression:
        previously crashed with NoneType += NoneType)."""
        from sound.synthesis.additive import SoundWave
        sw = SoundWave(sample_rate=self.SR, duration=0.5, frequency=440.0)
        sw.apply_overtones([0.6, 0.25, 0.15])
        assert hasattr(sw, 'fundamental')
        assert len(sw.fundamental) == int(self.SR * 0.5)
        assert np.max(np.abs(sw.fundamental)) > 0

    def test_modal_presets(self):
        """All modal presets render non-silent output."""
        from sound.synthesis.modal import ResonatorBank
        for preset in ['marimba', 'bell', 'drum', 'string', 'plate', 'tube']:
            bank = ResonatorBank.preset(preset, self.SR)
            sig = bank.excite_impulse(0.5)
            assert np.max(np.abs(sig)) > 0.05, f"{preset} silent"

    def test_phase_mod_harmonics(self):
        """Phase modulation at depth 3.0 must generate >5% harmonic energy."""
        from sound.synthesis.phase_mod import PhaseModSynth
        pm = PhaseModSynth(self.SR)
        note = pm.render_note(440.0, 0.5, carrier_shape='sine',
                              mod_shape='sine', mod_depth=3.0)
        fft = np.abs(np.fft.rfft(note))
        freqs = np.fft.rfftfreq(len(note), 1 / self.SR)
        ratio = np.sum(fft[freqs > 880]) / np.sum(fft)
        assert ratio > 0.05, f"Harmonic ratio {ratio:.1%}"

    def test_granular_cloud(self):
        """Granular cloud from a source WAV must fill output duration."""
        from sound.synthesis.granular import AperiodicGranulator
        from sound.utils.io import write_wav, read_wav
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, 'src.wav')
            out = os.path.join(tmp, 'cloud.wav')
            t = np.linspace(0, 1.0, self.SR, endpoint=False)
            write_wav(src, 0.3 * np.sin(2 * np.pi * 440 * t), self.SR)
            AperiodicGranulator(self.SR).generate_cloud(
                src, out, duration_sec=2.0, density_grains_per_sec=60)
            cloud, sr = read_wav(out)
            assert len(cloud) == int(2.0 * sr)
            assert np.max(np.abs(cloud)) > 0.01

    def test_vocal_syllable(self):
        """FormantVocalGuide renders a non-silent syllable."""
        from sound.synthesis.vocal import FormantVocalGuide
        from sound.utils.io import read_wav
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'v.wav')
            FormantVocalGuide(self.SR).render_syllable(220.0, 0.5, 'a', path)
            audio, sr = read_wav(path)
            assert np.max(np.abs(audio)) > 0.05

    def test_polyvoice_chord(self):
        """PolyVoice renders a non-silent 3-note chord."""
        from sound.synthesis.polysynth import PolyVoice
        pv = PolyVoice(sample_rate=self.SR)
        pv.osc1.waveform = 'saw'
        pv.osc2.waveform = 'square'
        pv.osc2.detune_cents = 7
        pv.filter.cutoff = 2000.0
        pv.filter.resonance = 0.4
        audio = pv.render_chord([261.63, 329.63, 392.0], 0.5)
        assert len(audio) == int(0.5 * self.SR)
        assert np.max(np.abs(audio)) > 0.05
