"""Tests for SP-024 Bowed String physical modeling synthesis."""

import numpy as np
import pytest
from scipy.io import wavfile

from sound.synthesis.bowed import BowedString
from sound.synthesis import BowedString as BowedStringPkg  # import via package __init__


SR = 44100


# --------------------------------------------------------------------------- #
# basic properties
# --------------------------------------------------------------------------- #
class TestBowedStringBasic:
    def test_import_from_package(self):
        """BowedString re-exported from sound.synthesis."""
        assert BowedStringPkg is BowedString

    def test_output_shape_and_dtype(self):
        bs = BowedString(SR)
        audio = bs.render(freq=440.0, duration=0.5)
        assert audio.ndim == 1
        assert audio.dtype == np.float32
        assert len(audio) == int(SR * 0.5)

    def test_output_normalized(self):
        """Peak should be close to 1.0 after normalization."""
        bs = BowedString(SR)
        audio = bs.render(freq=220.0, duration=0.5)
        assert np.max(np.abs(audio)) == pytest.approx(1.0, abs=0.1)

    def test_no_clipping(self):
        """No sample should exceed [-1, 1]."""
        bs = BowedString(SR)
        audio = bs.render(freq=330.0, duration=0.5, bow_velocity=0.3, bow_force=2.0)
        assert np.all(np.abs(audio) <= 1.0)

    def test_non_empty(self):
        """Output should not be all zeros (silence)."""
        bs = BowedString(SR)
        audio = bs.render(freq=440.0, duration=0.3)
        assert np.max(np.abs(audio)) > 0.01

    def test_dc_removed(self):
        """DC offset should be negligible."""
        bs = BowedString(SR)
        audio = bs.render(freq=440.0, duration=0.5)
        assert abs(np.mean(audio)) < 0.01


# --------------------------------------------------------------------------- #
# pitch correctness
# --------------------------------------------------------------------------- #
class TestBowedStringPitch:
    def test_fundamental_present(self):
        """Target frequency should be present as a significant spectral peak.

        Bowed strings have strong harmonics, so the fundamental may not be
        the global peak — we check it's within the top harmonics near the
        target frequency.
        """
        bs = BowedString(SR)
        freq = 220.0
        audio = bs.render(freq=freq, duration=1.0)
        spectrum = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / SR)
        # find the peak closest to the target frequency (within ±10 Hz)
        mask = np.abs(freqs - freq) < 15.0
        if mask.any():
            near_fund = spectrum[mask]
            # fundamental region should have at least 10% of max spectral energy
            assert np.max(near_fund) > 0.1 * np.max(spectrum), \
                f"fundamental at {freq} Hz not strong enough"
        else:
            # if no bin within range, find nearest and check it's not empty
            nearest_idx = np.argmin(np.abs(freqs - freq))
            assert spectrum[nearest_idx] > 0.05 * np.max(spectrum)

    def test_render_note_pitch(self):
        """render_note uses A4=440 Hz correctly — check fundamental present."""
        bs = BowedString(SR)
        audio_a4 = bs.render_note(69, duration=0.5)
        spectrum = np.abs(np.fft.rfft(audio_a4))
        freqs = np.fft.rfftfreq(len(audio_a4), 1.0 / SR)
        mask = np.abs(freqs - 440.0) < 15.0
        assert np.max(spectrum[mask]) > 0.1 * np.max(spectrum), \
            "440 Hz fundamental not strong enough"

    def test_higher_pitch_is_higher(self):
        """A higher MIDI note should produce a higher fundamental."""
        bs = BowedString(SR)
        low = bs.render_note(57, duration=0.5)  # A3 220
        high = bs.render_note(69, duration=0.5)  # A4 440
        spec_low = np.abs(np.fft.rfft(low))
        spec_high = np.abs(np.fft.rfft(high))
        freqs = np.fft.rfftfreq(len(low), 1.0 / SR)
        peak_low = freqs[np.argmax(spec_low[1:]) + 1]
        peak_high = freqs[np.argmax(spec_high[1:]) + 1]
        assert peak_high > peak_low


# --------------------------------------------------------------------------- #
# sustain (the key reason we're using bowed strings)
# --------------------------------------------------------------------------- #
class TestBowedStringSustain:
    def test_sustains_full_duration(self):
        """Bowed string should maintain energy throughout the note."""
        bs = BowedString(SR)
        audio = bs.render(freq=440.0, duration=2.0)
        # check last 25% has meaningful energy
        tail = audio[int(len(audio) * 0.75):]
        rms_tail = np.sqrt(np.mean(tail ** 2))
        rms_head = np.sqrt(np.mean(audio[:int(len(audio) * 0.25)] ** 2))
        assert rms_tail > 0.01, f"tail RMS {rms_tail:.6f} too low — not sustaining"
        # tail should be at least 20% of head energy
        assert rms_tail > 0.2 * rms_head, "energy drops too fast"

    def test_low_silence_ratio(self):
        """Overall silence ratio should be low (contrast with Karplus-Strong)."""
        bs = BowedString(SR)
        audio = bs.render(freq=220.0, duration=2.0)
        silent = np.sum(np.abs(audio) < 0.001)
        silence_ratio = silent / len(audio)
        assert silence_ratio < 0.3, f"silence ratio {silence_ratio:.1%} too high"


# --------------------------------------------------------------------------- #
# parameter sensitivity
# --------------------------------------------------------------------------- #
class TestBowedStringParameters:
    def test_higher_bow_velocity_changes_output(self):
        """Different bow velocity should produce different spectral content."""
        bs = BowedString(SR)
        low = bs.render(freq=440.0, duration=0.5, bow_velocity=0.1)
        high = bs.render(freq=440.0, duration=0.5, bow_velocity=0.3)
        # both normalized to peak 1, but RMS differs due to different
        # harmonic content / duty cycle
        assert not np.allclose(low, high)

    def test_envelope_bow_velocity(self):
        """Time-varying bow_velocity envelope should work."""
        bs = BowedString(SR)
        env = np.linspace(0.05, 0.3, int(SR * 0.5))
        audio = bs.render(freq=440.0, duration=0.5, bow_velocity=env)
        assert len(audio) == len(env)
        assert np.max(np.abs(audio)) > 0.01

    def test_bow_position_affects_timbre(self):
        """Different bow positions should produce different spectra."""
        bs = BowedString(SR)
        near_bridge = bs.render(freq=440.0, duration=0.5, bow_position=0.1)
        near_nut = bs.render(freq=440.0, duration=0.5, bow_position=0.3)
        assert not np.allclose(near_bridge, near_nut)

    def test_different_freq_different_output(self):
        """Different frequencies should produce different audio."""
        bs = BowedString(SR)
        a = bs.render(freq=220.0, duration=0.5)
        b = bs.render(freq=330.0, duration=0.5)
        assert not np.allclose(a, b)


# --------------------------------------------------------------------------- #
# stereo integration via io
# --------------------------------------------------------------------------- #
class TestBowedStringIO:
    def test_wav_roundtrip(self, tmp_path):
        """Render + write + read should preserve audio."""
        bs = BowedString(SR)
        audio = bs.render(freq=440.0, duration=0.5)
        from sound.utils.io import write_wav, read_wav
        path = tmp_path / "bowed.wav"
        write_wav(str(path), audio, SR)
        read_back, _ = read_wav(str(path))
        assert len(read_back) == len(audio)
        assert np.max(np.abs(read_back)) > 0.01
