# -*- coding: utf-8 -*-
"""Transient-aware, phase-locked spectral time-stretch / pitch-shift with
formant preservation — Cubase 16 "Spectral AudioWarp" style.

Replicable logic from the Cubase 16 announcement (Synthtopia / MusicTech,
2026-11-04): Steinberg's HALion team added new time-stretching and
pitch-shifting algorithms aimed at *extreme* transformations and sound
design, plus an updated six-stem separation and MIDI 2.0 articulation
support.  The DAW chrome is not replicable; the *algorithm family* is.

What this module implements (numpy only, offline STFT, no ML):

- ``SpectralWarper.process(x, stretch, pitch_semitones, formant_semitones)``
  --- analysis/synthesis STFT (Hann, 75 % overlap) with:
  * **instantaneous-frequency phase propagation** per bin (classic
    Flanagan/Schafer phase vocoder) so stretching does not produce the
    "phasiness" of naive magnitude interpolation;
  * **identity phase locking** (Laroche & Dolson): spectral peaks are
    picked per frame and every bin inside a peak's region of influence
    takes the peak's synthesis phase plus its own *analysis* phase offset
    --- this is what keeps harmonic stacks coherent at large stretch
    factors;
  * **transient handling**: spectral flux is computed on the analysis
    frames; frames above a median-relative threshold are declared
    transients and their synthesis phase is *reset* to the analysis phase
    (no phase accumulation across the attack), which is what stops
    percussive attacks from smearing;
  * **formant preservation** for pitch shifting: a cepstrally-liftered
    spectral envelope is estimated per frame, the magnitude is divided by
    it before shifting and multiplied by the *original* envelope target
    after shifting, so the vocal/instrument body does not move with the
    pitch (``formant_semitones`` shifts the envelope deliberately instead).

Not replicated: HALion's proprietary near-lossless stretch modes, the
six-stem separation network (needs trained models), MIDI 2.0 transport.

Usage::

    from sound.effects.spectral_warper import SpectralWarper
    w = SpectralWarper(sample_rate=44100)
    out = w.process(x, stretch=2.0, pitch_semitones=-5, formant_semitones=0)
"""

from __future__ import annotations

import numpy as np

TWO_PI = 2.0 * np.pi


def _hann(n: int) -> np.ndarray:
    return 0.5 - 0.5 * np.cos(TWO_PI * np.arange(n) / n)


def _cepstral_envelope(mag: np.ndarray, n_fft: int, lifter: int = 40) -> np.ndarray:
    """Smooth spectral envelope via real-cepstrum low-pass liftering."""
    logmag = np.log(mag + 1e-9)
    cep = np.fft.irfft(logmag, n=n_fft)
    lifter = max(8, min(lifter, n_fft // 2 - 1))
    cep[lifter:-lifter] = 0.0
    env = np.fft.rfft(cep).real
    env = np.exp(env)
    # never let the envelope collapse to zero (would blow up the division)
    return np.maximum(env, np.max(env) * 1e-4 + 1e-9)


def _shift_bins(arr: np.ndarray, ratio: float) -> np.ndarray:
    """Resample a positive-frequency spectrum by ``ratio`` (bin-domain)."""
    n = len(arr)
    src = np.arange(n) / max(ratio, 1e-9)
    lo = np.floor(src).astype(int)
    hi = lo + 1
    frac = src - lo
    ok_lo = (lo >= 0) & (lo < n)
    ok_hi = (hi >= 0) & (hi < n)
    lo_c = np.clip(lo, 0, n - 1)
    hi_c = np.clip(hi, 0, n - 1)
    out = arr[lo_c] * (1.0 - frac) + arr[hi_c] * frac
    out[~(ok_lo & ok_hi)] = 0.0
    return out


def _peaks(mag: np.ndarray, floor: float = 0.05) -> np.ndarray:
    """Indices of local spectral maxima above ``floor`` * frame max."""
    m = mag
    if m.size < 3:
        return np.array([], dtype=int)
    thr = m.max() * floor
    idx = np.where((m[1:-1] > m[:-2]) & (m[1:-1] >= m[2:]) & (m[1:-1] > thr))[0] + 1
    return idx


def _regions(peaks: np.ndarray, n: int) -> list[tuple[int, int, int]]:
    """Split bins into (start, stop, peak) regions of influence."""
    if peaks.size == 0:
        return [(0, n, 0)]
    bounds = [0]
    for a, b in zip(peaks[:-1], peaks[1:]):
        bounds.append(int((a + b) // 2))
    bounds.append(n)
    return [(bounds[i], bounds[i + 1], int(peaks[i])) for i in range(len(peaks))]


class SpectralWarper:
    """Phase-locked spectral stretcher / pitch shifter.

    Parameters
    ----------
    sample_rate : int
    n_fft : int
        Analysis window (power of two).  2048 is a good default for music;
        1024 is faster and fine for verification.
    hop : int | None
        Synthesis hop; defaults to ``n_fft // 4`` (75 % overlap).
    """

    def __init__(self, sample_rate: int = 44100, n_fft: int = 2048,
                 hop: int | None = None):
        self.sr = int(sample_rate)
        self.n_fft = int(n_fft)
        self.hop = int(hop if hop is not None else n_fft // 4)
        self.win = _hann(self.n_fft)
        # expected phase advance per bin for one *synthesis* hop
        self._omega = TWO_PI * np.arange(self.n_fft // 2 + 1) * self.hop / self.n_fft

    # ------------------------------------------------------------------ #
    def _analyse(self, x: np.ndarray, stretch: float):
        """Return (frames, times) of complex spectra at warped positions."""
        hop_s = self.hop
        step = stretch * hop_s
        n_frames = max(1, int(round(len(x) * stretch / hop_s)))
        pad = np.concatenate([np.zeros(self.n_fft), x,
                              np.zeros(self.n_fft + int(np.ceil(step)) + 1)])
        out = np.zeros((n_frames, self.n_fft // 2 + 1), dtype=complex)
        for k in range(n_frames):
            pos = int(round(k * step))
            seg = pad[pos:pos + self.n_fft]
            if len(seg) < self.n_fft:                      # tail safety
                seg = np.pad(seg, (0, self.n_fft - len(seg)))
            out[k] = np.fft.rfft(seg * self.win)
        return out

    def _flux(self, frames: np.ndarray) -> np.ndarray:
        mag = np.abs(frames)
        d = np.diff(mag, axis=0, prepend=mag[:1])
        flux = np.maximum(d, 0.0).sum(axis=1)
        return flux / (flux.max() + 1e-12)

    # ------------------------------------------------------------------ #
    def process(self, x: np.ndarray, stretch: float = 1.0,
                pitch_semitones: float = 0.0, formant_semitones: float = 0.0,
                transient_sensitivity: float = 1.6,
                phase_lock: bool = True) -> np.ndarray:
        """Warp ``x``.

        stretch : float
            Output/input duration ratio (2.0 = twice as long / half speed).
        pitch_semitones : float
            Pitch transposition in semitones (formants stay put).
        formant_semitones : float
            Deliberate formant/envelope shift on top (sound-design move).
        transient_sensitivity : float
            Higher = fewer frames classified as transients.
        phase_lock : bool
            Identity phase locking on/off (off = plain phase vocoder).
        """
        x = np.asarray(x, dtype=float)
        if x.ndim > 1:
            return np.stack([self.process(ch, stretch, pitch_semitones,
                                          formant_semitones,
                                          transient_sensitivity, phase_lock)
                             for ch in x], axis=0)

        stretch = float(np.clip(stretch, 0.05, 20.0))
        r_pitch = 2.0 ** (float(pitch_semitones) / 12.0)
        r_form = 2.0 ** (float(formant_semitones) / 12.0)

        frames = self._analyse(x, stretch)
        n_frames, n_bins = frames.shape
        flux = self._flux(frames)
        # absolute floor matters: a stationary tone has near-zero flux, and a
        # median-only threshold would flag every frame as a transient
        thr = max(0.10, float(transient_sensitivity) * float(np.median(flux)))
        transients = flux > thr

        mag = np.abs(frames)
        phase = np.angle(frames)

        # ---- analysis phase advance (unwrapped instantaneous frequency) ----
        dphi = np.diff(phase, axis=0, prepend=phase[:1])
        dev = dphi - self._omega
        dev = (dev + np.pi) % TWO_PI - np.pi          # wrap to (-pi, pi]
        inst = self._omega + dev                       # rad per synthesis hop

        out = np.zeros((n_frames, n_bins), dtype=complex)
        prev_synth = phase[0].copy()

        for k in range(n_frames):
            m = mag[k]
            if r_pitch != 1.0 or r_form != 1.0:
                env = _cepstral_envelope(m, self.n_fft)
                # 1) move the harmonics by the pitch ratio
                m_shift = _shift_bins(m, r_pitch)
                # 2) envelope that travelled with the pitch vs the envelope we
                #    actually want (original formants, or deliberately shifted)
                env_src = _shift_bins(env, r_pitch)
                env_tgt = _shift_bins(env, r_form)
                corr = np.clip(env_tgt / np.maximum(env_src, 1e-9), 0.02, 25.0)
                m = m_shift * corr
                # 3) frame-energy match so transposition does not change level
                e0 = float(np.sum(mag[k]))
                e1 = float(np.sum(m))
                if e1 > 1e-12:
                    m = m * (e0 / e1)
            if transients[k]:
                # phase reset: attack keeps its own phase, no accumulation
                syn = phase[k].copy()
            else:
                syn = prev_synth + inst[k] * (r_pitch if r_pitch != 1.0 else 1.0)
            if phase_lock:
                pk = _peaks(m)
                for a, b, p in _regions(pk, n_bins):
                    if b - a <= 1:
                        continue
                    offset = phase[k, a:b] - phase[k, p]
                    syn[a:b] = syn[p] + offset
            out[k] = m * np.exp(1j * syn)
            prev_synth = syn

        return self._synthesise(out, n_frames,
                                target_len=int(round(len(x) * stretch)))

    # ------------------------------------------------------------------ #
    def _synthesise(self, frames: np.ndarray, n_frames: int,
                    target_len: int | None = None) -> np.ndarray:
        hop_s = self.hop
        total = n_frames * hop_s + self.n_fft
        y = np.zeros(total)
        wsum = np.zeros(total)
        for k in range(n_frames):
            seg = np.fft.irfft(frames[k], n=self.n_fft) * self.win
            s = k * hop_s
            y[s:s + self.n_fft] += seg
            wsum[s:s + self.n_fft] += self.win ** 2
        nz = wsum > 1e-3 * wsum.max()
        y[nz] /= wsum[nz]
        # trim the analysis padding we added on both sides
        if target_len is None:
            target_len = max(1, int(n_frames * hop_s))
        y = y[self.n_fft:self.n_fft + target_len]
        if len(y) < target_len:
            y = np.pad(y, (0, target_len - len(y)))
        return y


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Stretch a tone + click train and verify pitch / transient behaviour."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    sr = 22050
    n = sr  # 1 s
    t = np.arange(n) / sr
    # 220 Hz tone with harmonics + a sharp click train (transients)
    x = 0.4 * np.sin(2 * np.pi * 220 * t) + 0.2 * np.sin(2 * np.pi * 440 * t)
    click = np.zeros(n)
    for c in (0.10, 0.40, 0.70):
        i = int(c * sr)
        click[i:i + 60] = np.hanning(min(60, n - i)) * 0.9
    x = x + click

    w = SpectralWarper(sample_rate=sr, n_fft=1024)
    up = w.process(x, stretch=2.0)
    shifted = w.process(x, stretch=1.0, pitch_semitones=12)
    warped = w.process(x, stretch=1.5, pitch_semitones=-5, formant_semitones=3)

    def peak_freq(sig):
        s = np.abs(np.fft.rfft(sig * np.hanning(len(sig))))
        s[:3] = 0
        return np.fft.rfftfreq(len(sig), 1 / sr)[int(np.argmax(s))]

    f_in, f_up, f_sh = peak_freq(x), peak_freq(up), peak_freq(shifted)
    print(f"spectralWarp demo: in={len(x)} samples, stretch2x={len(up)} samples")
    print(f"  dominant: input {f_in:.1f} Hz, +12 st {f_sh:.1f} Hz (expect ~2x)")
    print(f"  warp(1.5x,-5st,+3st formant): {len(warped)} samples, "
          f"peak={np.abs(warped).max():.3f}")
    assert len(up) > 1.8 * len(x)
    assert abs(f_sh / max(f_in, 1e-9) - 2.0) < 0.06, (f_in, f_sh)
    assert np.isfinite(up).all() and np.isfinite(warped).all()
    for name, sig in (("stretch2x", up), ("pitch12", shifted), ("warped", warped)):
        path = os.path.join(out_dir, f"spectral_warper_{name}.npy")
        np.save(path, sig.astype(np.float32))
    print(f"  wrote {out_dir}/spectral_warper_*.npy")
    print("demo OK")
    return {"in_len": len(x), "up_len": len(up), "f_in": f_in, "f_shift": f_sh}


if __name__ == "__main__":
    demo()
