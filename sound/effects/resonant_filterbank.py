"""Ten-band resonant filterbank — Erica Synths Resonant Filterbank style.

Replicable logic from the Sound On Sound review "Erica Synths Resonant
Filterbank" (October 2026): an analogue stereo 10-band fixed-frequency
band-pass filterbank (29 Hz – 11 kHz) with per-band boost/cut sliders,
per-band resonance with a bipolar feedback control (12 o'clock = no
feedback, clockwise = positive feedback, anti-clockwise = polarity-inverted
feedback), a main feedback loop that takes the combined signal of all
feedback-enabled bands back into the input, a Spread control for stereo
offset, a Filter mode in which the 10 bands are automated together to
emulate multi-mode LP/HP/BP/notch behaviour, and self-oscillation that lets
the unit work as a drone instrument.

What is replicated here (offline numpy + scipy.signal biquads):
- ``ResonantFilterbank``: 10 log-spaced fixed band-pass filters
  (29 Hz..11 kHz), per-band gain (boost/cut) and per-band resonance.
- Bipolar per-band feedback approximated by Q scaling + polarity
  inversion (the exact analogue circuit topology is not replicated —
  see docstring note below).
- Global feedback loop: sum of feedback-enabled band outputs feeds back
  into the input with a one-block delay (genuine recursive loop).
- ``spread``: stereo offset between left and right band gains
  (independent per-channel settings like the hardware's global option).
- Filter mode: LP / HP / BP / notch emulation by automating the 10 band
  gains from a cutoff (+ slope), like the hardware's Filter mode.
- ``drone``: self-oscillation with a silence/noise input -> ringing bands.
- Optional LFO modulation of band gains.

Not replicated: the analogue hardware, OLED UI, MIDI CC control, envelope
follower input, and the exact feedback circuit (approximated).

Usage:
    from sound.effects.resonant_filterbank import ResonantFilterbank

    fb = ResonantFilterbank(sample_rate=44100)
    out = fb.process(audio, mode="filter", filter_type="LP", cutoff=800.0)
    out = fb.process(audio, resonance=0.4, feedback=0.3, spread=0.5)
    drone = fb.drone(dur_sec=3.0)
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np
from scipy.signal import sosfilt, zpk2sos

__all__ = ["ResonantFilterbank", "band_centers"]

DEFAULT_SR = 44100
DEFAULT_N_BANDS = 10


def band_centers(n_bands: int = DEFAULT_N_BANDS, f_min: float = 29.0,
                 f_max: float = 11000.0) -> np.ndarray:
    """Log-spaced band-pass centre frequencies 29 Hz..11 kHz."""
    return f_min * (f_max / f_min) ** (np.arange(n_bands) / max(n_bands - 1, 1))


def _bandpass_sos(fc: float, sr: int, q: float) -> np.ndarray:
    """Second-order band-pass as second-order sections (zpk -> sos).

    Peak gain at the centre frequency is normalized to ~0 dB so the band
    passes unity at resonance centre regardless of Q (Q only narrows the
    band — the analogue unit's "howl" comes from the feedback loops, which
    are modelled separately by the global feedback path).
    """
    from scipy.signal import sosfreqz
    w0 = 2.0 * np.pi * fc / sr
    if w0 <= 0 or w0 >= np.pi:
        # degenerate: return an all-pass-ish identity section
        z, p, k = [1.0, 0.0, 0.0], [0.0, 0.0], 1.0
        return zpk2sos(z, p, k)
    z = [1.0, 0.0, -1.0]          # BP: zeros at DC and Nyquist
    # pole radius for the given Q (clamped for stability)
    r = np.exp(-w0 / (2.0 * max(q, 0.1)))
    r = min(r, 0.999)
    p = [r * np.exp(1j * w0), r * np.exp(-1j * w0)]
    sos = zpk2sos(z, p, k=1.0)
    _, h = sosfreqz(sos, worN=[w0])
    gain = float(np.abs(h[0]))
    if gain > 1e-9:
        sos = sos.copy()
        sos[0, :3] /= gain
    return sos


class ResonantFilterbank:
    """Stereo 10-band fixed-frequency resonant band-pass filterbank.

    Args:
        sample_rate: audio sample rate in Hz.
        n_bands: number of bands (10 like the hardware).
        f_min / f_max: fixed band frequency range (29..11000 Hz).
        block: block size in samples for the global feedback loop delay.
    """

    def __init__(self, sample_rate: int = DEFAULT_SR, n_bands: int = DEFAULT_N_BANDS,
                 f_min: float = 29.0, f_max: float = 11000.0, block: int = 256):
        self.sample_rate = int(sample_rate)
        self.n_bands = int(n_bands)
        self.block = max(64, int(block))
        centers = band_centers(self.n_bands, f_min, f_max)
        self.centers = centers
        self._sos = [_bandpass_sos(float(fc), self.sample_rate, q=4.0)
                     for fc in centers]

    # ------------------------------------------------------------------
    def _band_gains(self, mode: str, filter_type: str, cutoff: float,
                    slope: float) -> np.ndarray:
        """Per-band gains for the four modes."""
        centers = self.centers
        if mode == "filterbank":
            return np.ones(self.n_bands)
        if mode != "filter":
            raise ValueError(f"unknown mode {mode!r}")
        if cutoff <= 0:
            cutoff = 1.0
        logc = np.log2(centers / cutoff)
        slope = max(slope, 0.1)
        if filter_type == "LP":
            g = np.where(logc <= 0, 1.0, 2.0 ** (-slope * logc))
        elif filter_type == "HP":
            g = np.where(logc >= 0, 1.0, 2.0 ** (slope * logc))
        elif filter_type == "BP":
            g = np.exp(-0.5 * (logc / slope) ** 2)
        elif filter_type == "notch":
            g = 1.0 - 0.9 * np.exp(-0.5 * (logc / slope) ** 2)
        else:
            raise ValueError(f"unknown filter_type {filter_type!r}")
        return g

    def _apply_bands(self, x: np.ndarray, gains: np.ndarray,
                     resonance: np.ndarray, fb_on: np.ndarray,
                     feedback: float, fb_state: np.ndarray) -> np.ndarray:
        """Process one block: per-band BPF + per-band feedback + global loop.

        Returns the summed band output. ``fb_state`` holds the previous
        block's feedback sum (one-block delay loop).
        """
        n = len(x)
        if n == 0:
            return np.zeros(0), fb_state
        # global feedback into the input (delayed one block). tanh keeps the
        # loop self-limiting when feedback > 1 (self-oscillation / drone);
        # for feedback <= 1 it is ~identity on small signals.
        x_in = x + feedback * np.tanh(fb_state[:n])
        total = np.zeros(n)
        for i in range(self.n_bands):
            q = 4.0 * (1.0 + 8.0 * max(resonance[i], 0.0))
            sos = _bandpass_sos(float(self.centers[i]), self.sample_rate, q=q)
            band = sosfilt(sos, x_in)
            if resonance[i] < 0:
                band = -band          # polarity-inverted feedback character
            # per-band resonance gain: at high resonance the band howls /
            # self-oscillates (the unit's "self-oscillating filter design",
            # which lets it work as a standalone drone instrument)
            rg = 1.0 + 12.0 * max(resonance[i], 0.0) ** 2
            gi = gains[:, i] if gains.ndim == 2 else gains[i]
            total += gi * rg * band
        fb_state = np.roll(fb_state, -n)
        fb_state[-n:] = total[-n:]
        return total, fb_state

    # ------------------------------------------------------------------
    def process(self, audio: np.ndarray, mode: str = "filterbank",
                gains: Optional[List[float]] = None,
                resonance: float = 0.0, feedback: float = 0.0,
                cutoff: float = 1000.0, filter_type: str = "LP",
                slope: float = 1.0, spread: float = 0.0,
                lfo_rate: float = 0.0, lfo_depth: float = 0.0,
                seed: int = 0) -> np.ndarray:
        """Process mono or stereo audio through the filterbank.

        Args:
            audio: mono ``(n,)`` or stereo ``(n, 2)`` float array.
            mode: "filterbank" (per-band sliders) or "filter" (LP/HP/BP/
                notch emulation driven by ``cutoff``).
            gains: 10 per-band boost/cut values (0..2, 1 = unity); None =
                unity (or the filter-mode band gains).
            resonance: per-band feedback, -1..1 (bipolar). Scalar applies
                to all bands; a 10-list gives per-band values.
            feedback: global feedback loop amount 0..1 (sum of all
                feedback-enabled bands fed back into the input).
            cutoff: cutoff frequency for Filter mode.
            filter_type: LP | HP | BP | notch.
            slope: filter-mode steepness (dB per band).
            spread: stereo offset 0..1 — right channel band gains are
                interpolated from a shifted band index (independent
                per-channel settings).
            lfo_rate / lfo_depth: optional LFO modulation of band gains.
            seed: LFO phase seed.

        Returns:
            Stereo ``(n, 2)`` when ``spread > 0`` or input is stereo;
            otherwise mono ``(n,)``.
        """
        x = np.asarray(audio, dtype=np.float64)
        mono = (x.ndim == 1)
        if mono:
            x = x[:, None]
        n = len(x)

        base = self._band_gains(mode, filter_type, cutoff, slope)
        if gains is not None and mode == "filterbank":
            g = np.asarray(gains, dtype=np.float64).reshape(-1)
            if len(g) == self.n_bands:
                base = g

        if np.isscalar(resonance):
            res = np.full(self.n_bands, float(resonance))
        else:
            res = np.asarray(resonance, dtype=np.float64).reshape(-1)
            if len(res) != self.n_bands:
                raise ValueError("resonance must be scalar or 10 values")

        rng = np.random.RandomState(seed)
        lfo_phase = rng.uniform(0, 2 * np.pi, self.n_bands)

        def _process_channel(sig: np.ndarray, g_ch: np.ndarray) -> np.ndarray:
            fb_state = np.zeros(self.block)
            pieces = []
            for b0 in range(0, len(sig), self.block):
                blk = sig[b0:b0 + self.block]
                if lfo_rate > 0:
                    t0 = b0 / self.sample_rate
                    tt = t0 + np.arange(len(blk)) / self.sample_rate
                    lfo = 1.0 + lfo_depth * np.sin(
                        2 * np.pi * lfo_rate * tt[:, None] + lfo_phase[None, :])
                    g_blk = g_ch[None, :] * lfo
                else:
                    g_blk = g_ch
                out_blk, fb_state = self._apply_bands(
                    blk, g_blk, res, np.ones(self.n_bands), feedback, fb_state)
                pieces.append(out_blk)
            return np.concatenate(pieces) if pieces else np.zeros(0)

        def _spread_gains(g_ch: np.ndarray) -> np.ndarray:
            """Right channel: band gains interpolated from a shifted index."""
            shift = spread * 0.6   # up to ~0.6 band of offset
            idx = np.arange(self.n_bands) - shift
            idx = np.clip(idx, 0, self.n_bands - 1)
            lo = np.floor(idx).astype(int)
            hi = np.minimum(lo + 1, self.n_bands - 1)
            frac = idx - lo
            return g_ch[lo] * (1 - frac) + g_ch[hi] * frac

        if mono and spread <= 0:
            return _process_channel(x[:, 0], base)

        left = _process_channel(x[:, 0], base)
        if spread > 0:
            right = _process_channel(x[:, 0], _spread_gains(base))
        else:
            right = _process_channel(x[:, 1], base)

        out = np.stack([left, right], axis=1)
        peak = float(np.max(np.abs(out))) if out.size else 0.0
        if peak > 1.0:
            out = out / peak * 0.95
        return out[:, 0] if mono and spread <= 0 else out

    # ------------------------------------------------------------------
    def drone(self, dur_sec: float = 3.0, resonance: float = 0.75,
              feedback: float = 0.85, gains: Optional[List[float]] = None,
              seed: int = 1) -> np.ndarray:
        """Self-oscillating drone: rings the bands with near-zero input.

        The hardware self-oscillates thanks to the self-oscillating filter
        design; here a tiny noise seed plus high per-band resonance gain
        (rg = 1 + 12*res^2 — the band howls at high resonance) sustains
        the band resonances; the global feedback loop (feedback < 1) adds
        the shared ringing character.
        """
        n = int(self.sample_rate * dur_sec)
        rng = np.random.RandomState(seed)
        x = 1e-3 * rng.randn(n)   # near-silent excitation
        if gains is None:
            gains = [1.0] * self.n_bands   # all bands ring (rich drone)
        return self.process(x, mode="filterbank", gains=gains,
                            resonance=resonance, feedback=feedback,
                            spread=0.3)


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: filterbank mode, LP filter sweep, drone — WAV writes."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    t = np.arange(sr * 2) / sr
    saw = np.zeros_like(t)
    for f in (110.0, 220.0, 440.0, 880.0):
        for k in range(1, 12):
            saw += np.sin(2 * np.pi * f * k * t) / k
    saw = saw / np.max(np.abs(saw)) * 0.9

    fb = ResonantFilterbank(sample_rate=sr)

    y1 = fb.process(saw, mode="filterbank",
                    gains=[1.0, 1.2, 0.3, 0.3, 0.5, 0.8, 1.0, 1.0, 0.6, 0.4],
                    resonance=0.35, feedback=0.25, spread=0.4)
    p1 = os.path.join(out_dir, "resfb_filterbank.wav")
    write_wav(p1, y1, sr)
    assert os.path.getsize(p1) > 40 and float(np.max(np.abs(y1))) > 1e-3

    y2 = fb.process(saw, mode="filter", filter_type="LP", cutoff=600.0,
                    slope=2.0, resonance=0.2)
    p2 = os.path.join(out_dir, "resfb_filter_lp.wav")
    write_wav(p2, y2, sr)
    assert os.path.getsize(p2) > 40

    # spectral check: LP mode must cut energy above cutoff (power — the
    # magnitude-sum metric is fooled by resonant band-ringing smear)
    def _high_energy(y, cutoff):
        Y = np.abs(np.fft.rfft(y)) ** 2
        freqs = np.fft.rfftfreq(len(y), 1 / sr)
        return float(Y[freqs > cutoff].sum())

    e_in = _high_energy(saw, 600.0)
    e_out = _high_energy(y2, 600.0)
    assert e_out < e_in * 0.5, f"LP filter did not cut highs ({e_out:.2e} vs {e_in:.2e})"

    y3 = fb.drone(dur_sec=3.0, resonance=0.95, feedback=0.9)
    p3 = os.path.join(out_dir, "resfb_drone.wav")
    write_wav(p3, y3, sr)
    assert os.path.getsize(p3) > 40 and float(np.max(np.abs(y3))) > 1e-3

    return {
        "filterbank_stereo": {"samples": int(y1.shape[0]), "channels": 2,
                              "peak": round(float(np.max(np.abs(y1))), 4)},
        "filter_lp_600": {"peak": round(float(np.max(np.abs(y2))), 4),
                          "high_energy_out_frac": round(e_out / e_in, 4)},
        "drone": {"samples": int(y3.shape[0]),
                  "peak": round(float(np.max(np.abs(y3))), 4)},
        "centers_hz": [round(float(c), 1) for c in fb.centers],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
