# -*- coding: utf-8 -*-
"""Tests for the singing-voice synthesis engine.

Verifies the core source-filter claims that make the timbre "voice-like":
- a real glottal-pulse source (asymmetric, not a flat impulse train)
- vowel formants shape the spectrum with the correct contrast (/i/ bright,
  /u/ dark)
- a singer's formant adds the 2.5-3.5 kHz "ring"
- vibrato and note envelope keep output bounded and non-silent
- the instrument registers and exposes synthesis defaults
"""
import sys

import numpy as np
import pytest

sys.path.insert(0, "/opt/data/projects/Instruments")

from sound.synthesis.singing_voice import (       # noqa: E402
    SingingVoice, VOICE_TYPES, VOWEL_FORMANTS, render_phrase_wav,
)

SR = 44100


def _band_energy(wav, lo, hi):
    N = len(wav)
    spec = np.abs(np.fft.rfft(wav * np.hanning(N))) ** 2
    freqs = np.fft.rfftfreq(N, 1.0 / SR)
    return float(np.sum(spec[(freqs >= lo) & (freqs <= hi)]))


def test_render_note_returns_bounded_audio():
    v = SingingVoice(sample_rate=SR, voice_type="alto")
    wav = v.render_note(69, 0.5, "a")
    assert wav.ndim == 1
    assert len(wav) == int(0.5 * SR)
    assert np.max(np.abs(wav)) <= 1.0 + 1e-6
    assert np.sqrt(np.mean(wav ** 2)) > 0.01, "note must not be silent"


def test_vowels_have_distinct_formant_energy():
    """The acoustic basis of vowel identity: /i/ is bright (F2 high), /u/ dark."""
    v = SingingVoice(sample_rate=SR, voice_type="alto")
    aa = v.render_note(57, 1.0, "a")
    ii = v.render_note(57, 1.0, "i")
    uu = v.render_note(57, 1.0, "u")
    # /i/ has the highest F2 (2.2 kHz), /u/ the lowest (870 Hz)
    e_a = _band_energy(aa, 2000, 3000)
    e_i = _band_energy(ii, 2000, 3000)
    e_u = _band_energy(uu, 2000, 3000)
    assert e_i > e_a > e_u, f"expected /i/ > /a/ > /u/ in 2-3 kHz, got {e_i:.1e} {e_a:.1e} {e_u:.1e}"


def test_voice_type_changes_timbre():
    """A soprano (short tract, high formants) is brighter than a bass at the
    same fundamental — the acoustic basis of voice type."""
    sop = SingingVoice(sample_rate=SR, voice_type="soprano")
    bas = SingingVoice(sample_rate=SR, voice_type="bass")
    w_s = sop.render_note(57, 1.0, "a", vibrato_semitones=0.0)
    w_b = bas.render_note(57, 1.0, "a", vibrato_semitones=0.0)
    # high-frequency energy (above 4 kHz) should be stronger for the soprano
    assert _band_energy(w_s, 4000, 8000) > _band_energy(w_b, 4000, 8000)


def test_glottal_source_has_spectral_tilt():
    """The glottal pulse rolls off high harmonics (-dB/oct), unlike a flat
    impulse train (which would be ~0)."""
    v = SingingVoice(sample_rate=SR, voice_type="alto")
    wav = v.render_note(57, 1.5, "a", vibrato_semitones=0.0, shimmer=0.0)
    spec = np.abs(np.fft.rfft(wav * np.hanning(len(wav)))) + 1e-12
    freqs = np.fft.rfftfreq(len(wav), 1.0 / SR)
    band = (freqs >= 500) & (freqs <= 5000)
    x = np.log2(freqs[band])
    y = 20 * np.log10(spec[band])
    slope = np.polyfit(x, y, 1)[0]          # dB/octave
    assert slope < -6.0, f"expected spectral rolloff, got {slope:.1f} dB/oct"


def test_singers_formant_adds_ring():
    v = SingingVoice(sample_rate=SR, voice_type="tenor")
    wav = v.render_note(57, 1.5, "a", vibrato_semitones=0.0, shimmer=0.0)
    # energy present in the singer's-formant band (2.5-3.5 kHz)
    assert _band_energy(wav, 2500, 3500) > 1e-3


def test_render_phrase_concatenates():
    v = SingingVoice(sample_rate=SR, voice_type="alto")
    notes = [(60, 0.3, "a"), (62, 0.3, "e"), (64, 0.6, "i")]
    wav = v.render_phrase(notes)
    expected = int((0.3 + 0.3 + 0.6) * SR)
    # crossfade shortens by ~15ms x 2 joins; allow tolerance
    assert abs(len(wav) - expected) < int(0.05 * SR)
    assert np.max(np.abs(wav)) <= 1.0 + 1e-6


def test_vowel_fallback_for_unknown():
    v = SingingVoice(sample_rate=SR, voice_type="alto")
    wav = v.render_note(69, 0.2, "not_a_vowel")
    assert len(wav) == int(0.2 * SR)


def test_render_phrase_wav_writes_file(tmp_path):
    out = tmp_path / "phrase.wav"
    render_phrase_wav([(67, 0.3, "a"), (69, 0.3, "o")], str(out),
                      voice_type="tenor")
    assert out.exists()
    assert out.stat().st_size > 1000


def test_voice_profiles_are_complete():
    for name, prof in VOICE_TYPES.items():
        assert prof.f0_center > 0
        assert prof.formant_scale > 0
        assert prof.singer_formant_hz > 1000


def test_vowel_table_has_all_five_formants():
    for v, f in VOWEL_FORMANTS.items():
        assert len(f) == 5, v
        assert f[0] < f[1] < f[2], f"{v}: F1<F2<F3 must hold"


# ----------------------------------------------------------- instrument ----

def test_instrument_registers():
    from instrument_registry import HUMAN_VOICE, by_name, by_program
    assert HUMAN_VOICE.name == "Human Voice"
    assert HUMAN_VOICE.family == "Vocal"
    assert HUMAN_VOICE.midi_program == 53
    assert HUMAN_VOICE.synthesis == "singing_voice"
    assert HUMAN_VOICE.synthesis_defaults["voice_type"] in VOICE_TYPES
    assert by_program(53).name == "Human Voice"
    assert by_name("human voice").name == "Human Voice"


def test_instrument_range_covers_voice_types():
    from instrument_registry import HUMAN_VOICE
    assert HUMAN_VOICE.range_min <= 55     # a tenor/bass low note fits
    assert HUMAN_VOICE.range_max >= 76     # an alto high note fits
    assert HUMAN_VOICE.in_sweet_spot(69)   # A4 is the core register
