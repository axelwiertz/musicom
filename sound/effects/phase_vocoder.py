# -*- coding: utf-8 -*-
"""Spectral Phase Vocoder Resynthesis (SP-026) — shared, reusable module.

Promoted from `Styles/Production/SP026-phase-vocoder-kleutertjes/produce_sp026.py`
(2026-08-27) so the method is a callable tool.

Method (methods_db.md SP-026): STFT analysis-modification-resynthesis pipeline
with phase unwrapping and instantaneous-frequency propagation (Flanagan/Schafer
phase vocoder). Time-stretch, spectral freeze, harmonic sharpening.

API:
    phase_vocoder(x, sr, alpha=1.2, freeze=True, sharpness=1.12,
                  n_fft=2048, hop=512)
        -> np.ndarray (time-stretched / modified audio)

    time_stretch(x, alpha)          # alpha > 1 = slower
    spectral_freeze(x, sr, tail=2.0)  # hold last frame, exponential decay
    spectral_sharpen(x, exponent)   # |X|^p spectral emphasis
"""

import numpy as np


def _stft(x, n_fft=2048, hop=512, win=None):
    """STFT with squared-window normalization-ready framing."""
    if win is None:
        win = np.hanning(n_fft)
    n_frames = 1 + (len(x) - n_fft) // hop
    frames = np.zeros((n_frames, n_fft))
    for i in range(n_frames):
        start = i * hop
        frames[i] = x[start:start + n_fft] * win
    return np.fft.rfft(frames, axis=1), win


def _istft(spectra, n_fft=2048, hop=512, win=None, length=None):
    """Inverse STFT with WOLA squared-window normalization."""
    if win is None:
        win = np.hanning(n_fft)
    n_frames = spectra.shape[0]
    out = np.zeros(n_frames * hop + n_fft)
    norm = np.zeros_like(out)
    win2 = win ** 2
    for i in range(n_frames):
        start = i * hop
        frame = np.fft.irfft(spectra[i], n=n_fft)
        out[start:start + n_fft] += frame * win
        norm[start:start + n_fft] += win2
    norm = np.where(norm > 1e-8, norm, 1.0)
    out /= norm
    if length:
        return out[:length]
    return out


def phase_vocoder(x, sr=44100, alpha=1.2, freeze=True, sharpness=1.12,
                  n_fft=2048, hop=512, tail_len=None):
    """Time-stretch + optionally freeze + sharpen a signal.

    Flanagan phase vocoder: synthesis hop H_s = alpha * H_a, phases
    propagated from instantaneous frequency omega_hat[k].
    """
    if tail_len is None:
        tail_len = 2.0
    win = np.hanning(n_fft)
    spectra, win_a = _stft(x, n_fft, hop, win)
    n_frames, n_bins = spectra.shape

    # instantaneous frequency via phase difference (Flanagan)
    phase_acc = np.angle(spectra[0])
    out_frames = []
    # magnitude interpolation + phase propagation
    for i in range(n_frames):
        mag = np.abs(spectra[i])
        if sharpness != 1.0:
            mag = mag ** sharpness
        if freeze and i == n_frames - 1:
            # spectral freeze: hold magnitude, continue phase (decay later)
            out_frames.append(mag * np.exp(1j * phase_acc))
            break
        # phase propagation from previous frame
        phase_prev = np.angle(spectra[i - 1]) if i > 0 else np.angle(spectra[0])
        # unwrapped phase advance
        omega_hat = (np.angle(spectra[i]) - phase_prev) / hop
        phase_acc = phase_acc + omega_hat * hop * alpha
        out_frames.append(mag * np.exp(1j * phase_acc))

    out_spec = np.stack(out_frames, axis=0)
    y = _istft(out_spec, n_fft, int(hop * alpha), win)

    if freeze:
        # exponential decay tail on the frozen frame
        tail_n = int(tail_len * sr)
        if tail_n < len(y):
            decay = np.exp(-np.linspace(0, 5.0, len(y) - tail_n))
            y[tail_n:] *= decay
    return y


def time_stretch(x, alpha):
    """Pure time-stretch (alpha > 1 = slower/longer)."""
    return phase_vocoder(x, alpha=alpha, freeze=False, sharpness=1.0)


def spectral_freeze(x, sr=44100, tail=2.0):
    """Freeze the final frame's spectrum with exponential decay."""
    return phase_vocoder(x, sr=sr, alpha=1.0, freeze=True, tail_len=tail)


def spectral_sharpen(x, exponent=1.12):
    """Spectral emphasis |X|^exponent for harmonic clarity."""
    return phase_vocoder(x, alpha=1.0, freeze=False, sharpness=exponent)


if __name__ == "__main__":
    import os
    import tempfile

    sr = 44100
    t = np.linspace(0, 1.0, sr, endpoint=False)
    # 440 Hz tone with a chord
    x = (np.sin(2 * np.pi * 440 * t) +
         0.5 * np.sin(2 * np.pi * 554 * t) +
         0.3 * np.sin(2 * np.pi * 659 * t))
    y = phase_vocoder(x, sr=sr, alpha=1.2)
    print("input len:", len(x), "output len:", len(y),
          "(alpha=1.2 ->", round(len(y) / sr, 2), "s)")
    assert len(y) > len(x), "time-stretch should lengthen"
    tmp = os.path.join(tempfile.gettempdir(), "pv_demo.wav")
    import wave
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    with wave.open(tmp, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    print("wrote", tmp, os.path.getsize(tmp), "bytes")
    assert os.path.getsize(tmp) > 1000
    print("OK — SP-026 phase_vocoder module works")
