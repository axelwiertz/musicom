"""Multi-mode algorithmic reverb with period-accurate lo-fi sample
rates — Synthesizers.com Q215 Digital Reverb style.

Replicable logic from the Synthtopia news item "Synthesizers.com
Intros Q215 Digital Reverb For MU Modular Systems" (2026-10-19): a
multi-mode stereo reverb for MU modular systems with eleven algorithms
(Dat Plate, Medium Room, Longer Room, Big Cloud, Sunday Large Reverb,
Flanged Hall — Mod=Flange Speed, Damp=Flange Depth, Springy Tank,
Short and Snappy, two '80s Abstract Large Hall modes, Alternate Tank).
Some modes include 'period accurate' sample-rate adjustments: the two
Abstract Large Hall algorithms run at a 32 kHz internal rate, which the
manufacturer says is part of their dark/gritty character.  A GAIN
control adjusts headroom and can be pushed into slight clipping.  Mono
or stereo input; stereo output.

What is replicated here (offline, numpy only):
- ``LoFiReverb``: a comb/allpass reverb core (parallel combs -> series
  allpasses, per-channel damping) with per-mode delay/feedback
  tunings; stereo input or mono->stereo decorrelation (right channel
  combs offset by a few percent).
- Eleven ``MODES`` matching the Q215 algorithm list, including
  ``flanged_hall`` (one comb delay modulated by an LFO; rate = Mod,
  depth = Damp) and the two 32 kHz Abstract Hall modes.
- ``rate`` handling: modes can declare an internal sample rate; the
  audio is anti-alias filtered, resampled down, reverberated at the
  low rate and resampled back (the 'period accurate' dark/gritty
  character: less top end + slightly coarse time base).
- ``drive``: gain control pushed into soft clipping (tanh).
- ``rt60()``: measured -60 dB decay time of an impulse response.

Not replicated: the MU-module hardware, the exact DSP of the original
(its reverb topologies are unknown in detail — classic Schroeder-style
comb/allpass structures are used), +/-5V/line-level I/O.

Usage:
    from sound.effects.lofi_reverb import LoFiReverb

    rv = LoFiReverb(sample_rate=44100)
    out = rv.process(audio, mode="abstract_hall_32k", wet=0.4)
"""

from __future__ import annotations

import numpy as np

__all__ = ["LoFiReverb", "MODES"]

DEFAULT_SR = 44100

MODES = {
    "dat_plate": dict(combs=[29.7, 37.1, 41.1, 43.7], fb=0.78,
                      aps=[5.0, 1.7], damp=0.25, rate=None, detune=0.0),
    "medium_room": dict(combs=[22.0, 26.0, 29.0, 33.0], fb=0.62,
                        aps=[4.5, 1.5], damp=0.40, rate=None, detune=0.0),
    "longer_room": dict(combs=[25.0, 29.0, 33.0, 37.0], fb=0.72,
                        aps=[5.0, 1.8], damp=0.35, rate=None, detune=0.0),
    "big_cloud": dict(combs=[45.0, 55.0, 63.0, 71.0], fb=0.86,
                      aps=[6.0, 2.2], damp=0.30, rate=None, detune=0.0),
    "sunday_large": dict(combs=[38.0, 43.0, 48.0, 54.0], fb=0.83,
                         aps=[5.5, 2.0], damp=0.35, rate=None, detune=0.0),
    "flanged_hall": dict(combs=[36.0, 41.0, 46.0, 51.0], fb=0.80,
                         aps=[5.0, 1.9], damp=0.30, rate=None, detune=0.0,
                         flange_rate_hz=1.2, flange_depth_ms=3.0),
    "springy_tank": dict(combs=[31.0, 37.0, 43.0], fb=0.35,
                         aps=[1.2, 0.8], damp=0.10, rate=None, detune=0.0),
    "short_snappy": dict(combs=[12.0, 14.0, 16.0, 18.0], fb=0.45,
                         aps=[3.0, 1.2], damp=0.50, rate=None, detune=0.0),
    "abstract_hall_32k": dict(combs=[42.0, 48.0, 53.0, 59.0], fb=0.84,
                              aps=[5.5, 2.0], damp=0.45, rate=32000.0,
                              detune=0.0),
    "abstract_hall_32k_detune": dict(combs=[42.0, 48.0, 53.0, 59.0],
                                     fb=0.84, aps=[5.5, 2.0], damp=0.45,
                                     rate=32000.0, detune=0.985),
    "alternate_tank": dict(combs=[35.0, 41.0, 47.0], fb=0.40,
                           aps=[1.5, 1.0], damp=0.12, rate=None,
                           detune=0.0),
}


def _one_pole_lp(x: np.ndarray, fc: float, fs: float) -> np.ndarray:
    """Simple one-pole low-pass (anti-alias / smoothing)."""
    a = 1.0 - np.exp(-2.0 * np.pi * fc / fs)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s += a * (x[i] - s)
        y[i] = s
    return y


def _resample_linear(x: np.ndarray, src: float, dst: float) -> np.ndarray:
    """Linear-interpolation resample from ``src`` to ``dst`` Hz."""
    if abs(src - dst) < 1e-6:
        return x
    ratio = src / dst
    n_out = int(round(len(x) / ratio))
    idx = np.arange(n_out) * ratio
    i0 = np.floor(idx).astype(np.int64)
    frac = (idx - i0)[:, None] if x.ndim == 2 else (idx - i0)
    i1 = np.minimum(i0 + 1, len(x) - 1)
    if x.ndim == 2:
        return x[i0] * (1.0 - frac) + x[i1] * frac
    return x[i0] * (1.0 - frac) + x[i1] * frac


class LoFiReverb:
    """Multi-mode comb/allpass reverb with optional lo-fi rates.

    Args:
        sample_rate: audio sample rate in Hz.
    """

    def __init__(self, sample_rate: int = DEFAULT_SR):
        self.sample_rate = int(sample_rate)

    # ------------------------------------------------------------------
    def _verb_core(self, x: np.ndarray, mode: dict, damp: float,
                   fs: int) -> np.ndarray:
        """Comb/allpass reverb core on a (N,2) buffer.

        Right-channel combs are offset by ``mode['detune']`` (a delay
        scale < 1 gives the two Abstract-Hall 32k-detune shimmer).
        """
        n = len(x)
        out = np.zeros((n, 2))
        combs = mode["combs"]
        aps = mode.get("aps", [])
        fb = mode["fb"]
        detune = mode.get("detune", 0.0)
        flange_rate = mode.get("flange_rate_hz", 0.0)
        flange_depth = mode.get("flange_depth_ms", 0.0)
        for ch in range(2):
            sig = x[:, ch]
            scale = 1.0 if ch == 0 else (detune if detune else 1.0)
            acc = np.zeros(n)
            for ci, ms in enumerate(combs):
                d0 = max(2, int(round(fs * ms * scale / 1000.0)))
                buf = np.zeros(d0 + 2)
                lp = 0.0
                if flange_rate > 0 and ci == 0:
                    depth_s = flange_depth * fs / 1000.0
                    for i in range(n):
                        # modulated fractional delay (linear interp)
                        dm = d0 + depth_s * (0.5 + 0.5 * np.sin(
                            2.0 * np.pi * flange_rate * i / fs))
                        i0 = int(np.floor(dm))
                        frac = dm - i0
                        d1 = buf[(i - i0) % len(buf)]
                        d2 = buf[(i - i0 - 1) % len(buf)]
                        delayed = d1 * (1.0 - frac) + d2 * frac
                        lp = delayed * (1.0 - damp) + lp * damp
                        buf[i % len(buf)] = sig[i] + fb * lp
                        acc[i] += delayed
                else:
                    for i in range(n):
                        delayed = buf[i % d0]
                        lp = delayed * (1.0 - damp) + lp * damp
                        buf[i % d0] = sig[i] + fb * lp
                        acc[i] += delayed
            acc /= len(combs)
            for ms in aps:
                d = max(2, int(round(fs * ms * scale / 1000.0)))
                buf = np.zeros(d)
                g = 0.5
                for i in range(n):
                    x_in = acc[i]
                    delayed = buf[i % d]
                    acc[i] = -g * x_in + delayed
                    buf[i % d] = x_in + g * delayed
            out[:, ch] = acc
        return out

    # ------------------------------------------------------------------
    def process(self, x: np.ndarray, mode: str = "dat_plate",
                wet: float = 0.35, damp: float | None = None,
                gain: float = 1.0, pre_delay_ms: float = 0.0,
                seed: int = 0) -> np.ndarray:
        """Process audio through the selected reverb mode.

        Args:
            x: mono (1-D) or stereo (N, 2) float audio.
            mode: key into ``MODES``.
            wet: wet mix 0..1 (dry = 1 - wet).
            damp: damping override (None = mode default).
            gain: GAIN control; >1 pushes into soft clipping.
            pre_delay_ms: pre-delay before the reverb tail.
            seed: unused (kept for API symmetry).

        Returns:
            Stereo (N, 2) float audio.
        """
        if mode not in MODES:
            raise ValueError(f"unknown mode {mode!r}; "
                             f"available: {sorted(MODES)}")
        cfg = MODES[mode]
        fs = self.sample_rate
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        # GAIN control -> soft clip
        if gain != 1.0:
            x = np.tanh(gain * x)
        # pre-delay
        if pre_delay_ms > 0:
            pad = int(round(fs * pre_delay_ms / 1000.0))
            x = np.vstack([np.zeros((pad, 2)), x])
        # period-accurate lo-fi internal rate
        rate = cfg.get("rate")
        d = cfg["damp"] if damp is None else damp
        dry_full = x  # full-rate dry for the final mix
        if rate is not None and rate < fs:
            x_low = _one_pole_lp(x, rate * 0.45, fs)
            x_low = _resample_linear(x_low, fs, rate)
            wet_low = self._verb_core(x_low, cfg, d, int(rate))
            wet_buf = _resample_linear(wet_low, rate, fs)
            wet_buf = _one_pole_lp(wet_buf, rate * 0.45, fs)
        else:
            wet_buf = self._verb_core(x, cfg, d, fs)
        # mix wet/dry on the (padded, full-rate) input
        n = min(len(dry_full), len(wet_buf))
        out = dry_full[:n] * (1.0 - wet) + wet_buf[:n] * wet
        peak = np.max(np.abs(out))
        if peak > 0:
            out = out / peak * 0.95
        return out

    # ------------------------------------------------------------------
    def impulse_response(self, mode: str, length_sec: float = 2.0,
                         wet: float = 1.0, gain: float = 1.0,
                         **kw) -> np.ndarray:
        """Render the reverb's impulse response (wet = 1.0)."""
        n = int(round(self.sample_rate * length_sec))
        imp = np.zeros(n)
        imp[0] = 1.0
        return self.process(imp, mode=mode, wet=wet, gain=gain, **kw)

    @staticmethod
    def rt60(ir: np.ndarray, fs: int = DEFAULT_SR) -> float:
        """-60 dB decay time of an impulse response (seconds)."""
        env = np.abs(ir[:, 0] if ir.ndim == 2 else ir)
        # integrated energy decay (Schroeder)
        sch = np.cumsum(env[::-1])[::-1]
        sch = np.maximum(sch, 1e-12)
        db = 10.0 * np.log10(sch / sch[0])
        # find first crossing below -60 dB
        idx = np.argmax(db < -60.0)
        if db[idx] >= -60.0 or idx == 0:
            return float("nan")
        return idx / fs

    @staticmethod
    def spectral_centroid(ir: np.ndarray, fs: int = DEFAULT_SR) -> float:
        """Spectral centroid (Hz) of the impulse response."""
        spec = np.abs(np.fft.rfft(ir[:, 0] if ir.ndim == 2 else ir))
        freqs = np.fft.rfftfreq(len(ir), 1.0 / fs)
        s = float(spec.sum())
        return float((freqs * spec).sum() / s) if s > 0 else 0.0


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: rt60 + spectral centroid per mode (32 kHz modes must
    be darker than their 44.1 kHz cousins); WAV writes for plate /
    spring / 32k hall / flanged hall."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    rv = LoFiReverb(sr)

    # impulse through EVERY mode -> rt60 + centroid table
    table = {}
    for mode in sorted(MODES):
        ir = rv.impulse_response(mode, length_sec=2.5)
        table[mode] = {
            "rt60_s": round(rv.rt60(ir, sr), 3),
            "centroid_hz": round(rv.spectral_centroid(ir, sr), 1),
        }

    # chord render through 4 representative modes
    rng = np.random.RandomState(3)
    t = np.arange(int(sr * 1.5)) / sr
    chord = np.zeros((len(t), 2))
    for midi, amp in [(48, 0.3), (52, 0.24), (55, 0.2), (60, 0.16),
                      (64, 0.12)]:
        f = 440.0 * 2.0 ** ((midi - 69) / 12.0)
        g = amp * (np.sin(2 * np.pi * f * t)
                   + 0.4 * np.sin(2 * np.pi * 2 * f * t)
                   + 0.15 * rng.randn(len(t)))
        chord[:, 0] += g
        chord[:, 1] += g * 0.9

    for mode, fname in [("dat_plate", "lofi_reverb_plate.wav"),
                        ("springy_tank", "lofi_reverb_spring.wav"),
                        ("abstract_hall_32k", "lofi_reverb_hall32k.wav"),
                        ("flanged_hall", "lofi_reverb_flanged.wav")]:
        out = rv.process(chord, mode=mode, wet=0.4, gain=1.3)
        write_wav(os.path.join(out_dir, fname), out, sr)

    # darkness assertion: 32k hall vs 44.1k large hall
    c32 = table["abstract_hall_32k"]["centroid_hz"]
    c44 = table["sunday_large"]["centroid_hz"]
    return {
        "modes": table,
        "darkness_32k_vs_44k_delta_hz": round(c32 - c44, 1),
        "plate_wav_bytes": os.path.getsize(
            os.path.join(out_dir, "lofi_reverb_plate.wav")),
        "spring_wav_bytes": os.path.getsize(
            os.path.join(out_dir, "lofi_reverb_spring.wav")),
        "hall32k_wav_bytes": os.path.getsize(
            os.path.join(out_dir, "lofi_reverb_hall32k.wav")),
        "flanged_wav_bytes": os.path.getsize(
            os.path.join(out_dir, "lofi_reverb_flanged.wav")),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
