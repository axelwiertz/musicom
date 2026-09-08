#!/usr/bin/env python3
"""
Project 013: Consonant synthesis prototype.

Generates unvoiced sibilants using shaped white noise:
- /s/: high, sharp, front constriction. Energy mostly 5-11 kHz.
- /sh/ (/ʃ/): lower, darker, postalveolar. Energy mostly 2-7 kHz.
Also generates /sa/ by prepending /s/ to vowel /a/ formant synthesis.

Output:
  s_test.wav
  sh_test.wav
  sa_test.wav
"""

import os
import sys
import wave
from pathlib import Path

sys.path.append('/opt/data/.local/lib/python3.13/site-packages')

import numpy as np
from scipy import signal

FS = 44100
OUT_DIR = Path('/opt/data/projects/013-vocal-research/Prototypes')
RNG = np.random.default_rng(13013)


def normalize(x: np.ndarray, peak: float = 0.95) -> np.ndarray:
    """Peak normalize float audio."""
    x = np.asarray(x, dtype=np.float64)
    m = np.max(np.abs(x)) if x.size else 0.0
    if m < 1e-12:
        return x
    return (x / m) * peak


def save_wav(path: str | Path, data: np.ndarray, fs: int = FS) -> None:
    """Save mono 16-bit PCM WAV using standard library."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    audio = np.clip(data, -1.0, 1.0)
    pcm = (audio * 32767.0).astype(np.int16)
    with wave.open(str(path), 'wb') as fh:
        fh.setnchannels(1)
        fh.setsampwidth(2)
        fh.setframerate(fs)
        fh.writeframes(pcm.tobytes())


def white_noise(duration: float, fs: int = FS) -> np.ndarray:
    return RNG.normal(0.0, 1.0, int(round(duration * fs)))


def butter_filter(x: np.ndarray, fs: int, kind: str, cutoff, order: int = 6) -> np.ndarray:
    """Stable Butterworth filter via second-order sections."""
    sos = signal.butter(order, cutoff, btype=kind, fs=fs, output='sos')
    return signal.sosfilt(sos, x)


def envelope(n: int, fs: int, attack: float = 0.01, release: float = 0.03, sustain: float = 1.0) -> np.ndarray:
    """Linear attack/release envelope."""
    env = np.full(n, sustain, dtype=np.float64)
    a = min(int(round(attack * fs)), n)
    r = min(int(round(release * fs)), n)
    if a > 0:
        env[:a] *= np.linspace(0.0, 1.0, a)
    if r > 0:
        env[-r:] *= np.linspace(1.0, 0.0, r)
    return env


def consonant_s(duration: float = 0.18, fs: int = FS) -> np.ndarray:
    """
    /s/ spectral model.
    White noise high-pass at 5 kHz, with mild 7.5 kHz resonance.
    Perceived as thin/bright hiss.
    """
    n = white_noise(duration, fs)
    hp = butter_filter(n, fs, 'highpass', 5000, order=6)
    # Add narrow-ish emphasis near 7.5 kHz for alveolar groove noise.
    b, a = signal.iirpeak(7500, Q=1.2, fs=fs)
    bright = signal.lfilter(b, a, hp)
    y = 0.75 * hp + 0.55 * bright
    y *= envelope(len(y), fs, attack=0.035, release=0.045)
    return normalize(y, 0.65)


def consonant_sh(duration: float = 0.22, fs: int = FS) -> np.ndarray:
    """
    /sh/ (/ʃ/) spectral model.
    White noise band-pass 2-7 kHz, with broad 3 kHz and 4.5 kHz emphasis.
    Perceived as darker/wider hiss than /s/.
    """
    n = white_noise(duration, fs)
    bp = butter_filter(n, fs, 'bandpass', (2000, 7000), order=6)
    b1, a1 = signal.iirpeak(3000, Q=0.9, fs=fs)
    b2, a2 = signal.iirpeak(4500, Q=1.0, fs=fs)
    low_hush = signal.lfilter(b1, a1, bp)
    mid_hush = signal.lfilter(b2, a2, bp)
    y = 0.55 * bp + 0.65 * low_hush + 0.45 * mid_hush
    y *= envelope(len(y), fs, attack=0.04, release=0.055)
    return normalize(y, 0.65)


def vowel_a(duration: float = 0.55, fs: int = FS, f0: float = 220.0) -> np.ndarray:
    """Simple sung /a/ using saw carrier plus A vowel formants F1/F2/F3."""
    t = np.arange(int(round(duration * fs))) / fs
    vib = 1.0 + 0.012 * np.sin(2.0 * np.pi * 5.5 * t)
    phase = 2.0 * np.pi * np.cumsum(f0 * vib) / fs
    carrier = signal.sawtooth(phase, width=0.52)

    # Formant bank: A as in skill docs: (730, 1090, 2440).
    formants = [(730, 8.5, 1.0), (1090, 10.0, 0.75), (2440, 14.0, 0.38)]
    y = np.zeros_like(carrier)
    for freq, q, gain in formants:
        b, a = signal.iirpeak(freq, Q=q, fs=fs)
        y += gain * signal.lfilter(b, a, carrier)

    y *= envelope(len(y), fs, attack=0.025, release=0.08)
    return normalize(y, 0.72)


def make_sa(fs: int = FS) -> np.ndarray:
    """Build /sa/: 170 ms /s/, 12 ms overlap/crossfade into 550 ms /a/."""
    s = consonant_s(0.17, fs)
    a = vowel_a(0.55, fs)
    overlap = int(round(0.012 * fs))
    if overlap <= 0:
        return normalize(np.concatenate([s, a]), 0.92)
    fade_out = np.linspace(1.0, 0.0, overlap)
    fade_in = np.linspace(0.0, 1.0, overlap)
    joined = np.concatenate([
        s[:-overlap],
        s[-overlap:] * fade_out + a[:overlap] * fade_in,
        a[overlap:],
    ])
    return normalize(joined, 0.92)


def spectral_centroid(x: np.ndarray, fs: int = FS) -> float:
    """Simple whole-file spectral centroid for sanity check."""
    mag = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freqs = np.fft.rfftfreq(len(x), 1.0 / fs)
    denom = np.sum(mag) + 1e-12
    return float(np.sum(freqs * mag) / denom)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    s = consonant_s()
    sh = consonant_sh()
    sa = make_sa()

    save_wav(OUT_DIR / 's_test.wav', s)
    save_wav(OUT_DIR / 'sh_test.wav', sh)
    save_wav(OUT_DIR / 'sa_test.wav', sa)

    print('generated:')
    print(f'  {OUT_DIR / "s_test.wav"}  centroid={spectral_centroid(s):.0f} Hz')
    print(f'  {OUT_DIR / "sh_test.wav"} centroid={spectral_centroid(sh):.0f} Hz')
    print(f'  {OUT_DIR / "sa_test.wav"} duration={len(sa) / FS:.3f} s')


if __name__ == '__main__':
    main()
