"""Smoke tests for surveillance 2026-09-07 gear replicas.

Klatt-cascade formant voice (klattsch-style) and pitch-tracked three-band
sub-harmonic generator (Penteo 8 Synthesized LFE-style).
"""
import numpy as np

from sound.synthesis.formant_voice import (
    FormantVoiceSynth, PHONES, text_to_phones, render_text_line)
from sound.effects.subharmonic import (
    SubHarmonicGenerator, SubBand, pitch_frame)

SR = 22050


# ------------------------------------------------------------- formant voice
def test_formant_vowel_peaks():
    v = FormantVoiceSynth(sample_rate=SR)
    for ph, lo1, hi1, lo2, hi2 in (("aa", 500, 950, 700, 1500),
                                   ("iy", 150, 500, 1800, 2700)):
        wav = v.render_phones([(ph, None)] * 3, f0=140.0)
        assert wav.dtype == np.float32
        assert np.max(np.abs(wav)) > 0.2
        spec = np.abs(np.fft.rfft(wav))
        fr = np.fft.rfftfreq(len(wav), 1.0 / SR)
        p1 = fr[(fr >= lo1) & (fr <= hi1)]
        m1 = spec[(fr >= lo1) & (fr <= hi1)]
        assert len(p1) > 0
        assert lo1 <= p1[np.argmax(m1)] <= hi1


def test_formant_text_to_speech():
    wav = render_text_line("hello world", f0=120.0, sr=SR)
    assert len(wav) > 1000
    assert np.max(np.abs(wav)) > 0.2
    assert np.sqrt(np.mean(wav ** 2)) > 0.01


def test_formant_pitch_curve_changes_output():
    v = FormantVoiceSynth(sample_rate=SR)
    a = v.render_phones([("aa", None)] * 3, f0=140.0)
    b = v.render_phones([("aa", 200.0), ("aa", 280.0), ("aa", 400.0)],
                        f0=140.0)
    assert not np.allclose(a, b)


def test_formant_phones_and_kana():
    assert "a" in PHONES and "i" in PHONES and "u" in PHONES
    v = FormantVoiceSynth(sample_rate=SR)
    wav = v.render_phones([("a", 180.0), ("i", 180.0), ("u", 180.0)])
    assert len(wav) > 0 and np.max(np.abs(wav)) > 0.2
    phones = text_to_phones("hey you")
    assert all(p in PHONES for p, _ in phones)


# ------------------------------------------------------------ subharmonic
def test_subharmonic_adds_sub_energy():
    sr = 44100
    parts = []
    for f0, seg_dur in ((55.0, 0.7), (110.0, 0.7), (82.41, 0.6)):
        n = int(sr * seg_dur)
        tt = np.arange(n) / sr
        parts.append(np.sin(2 * np.pi * f0 * tt)
                     + 0.5 * np.sin(2 * np.pi * 2 * f0 * tt))
    bass = np.concatenate(parts)
    bass = np.pad(bass, (0, max(0, 88200 - len(bass))))

    def band_energy(x, lo, hi):
        w = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(len(x)) / len(x))
        spec = np.abs(np.fft.rfft(x * w))
        fr = np.fft.rfftfreq(len(x), 1.0 / sr)
        m = (fr >= lo) & (fr <= hi)
        return float(np.sum(spec[m] ** 2))

    shg = SubHarmonicGenerator(sample_rate=sr)
    sub = shg.process(bass, depth=1.0)
    assert len(sub) == len(bass)
    assert np.all(np.isfinite(sub))
    assert band_energy(sub, 20, 60) > 2.0 * band_energy(bass, 20, 60)
    assert band_energy(sub, 27, 28) > band_energy(bass, 27, 28) * 10.0


def test_subharmonic_band_mute():
    sr = 44100
    tt = np.arange(int(sr * 0.8)) / sr
    bass = np.sin(2 * np.pi * 150.0 * tt)  # sub-octave 75 Hz -> 'low' band
    shg = SubHarmonicGenerator(sample_rate=sr)
    full = shg.process(bass, depth=1.0)
    shg.bands[1].muted = True
    muted = shg.process(bass, depth=1.0)
    assert not np.allclose(full, muted)
    assert np.max(np.abs(muted)) < np.max(np.abs(full)) + 1e-9


def test_subharmonic_pitch_frame():
    sr = 44100
    tt = np.arange(2048) / sr
    f0 = pitch_frame(np.sin(2 * np.pi * 110.0 * tt), sr)
    assert 105.0 < f0 < 115.0
    f0b = pitch_frame(np.random.default_rng(0).standard_normal(2048), sr)
    assert f0b == 0.0  # noise -> unpitched
