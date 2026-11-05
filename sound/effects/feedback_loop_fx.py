# -*- coding: utf-8 -*-
"""Echo with the effects *inside the feedback loop*, plus a codec-degradation
model — XLN Audio RC-20 Retro Color V2 style.

Replicable logic from the RC-20 V2 update (MusicTech weekly plugin round-up,
2026-11-04): the headline change is an internal **Echo** module where the
other modules (Wobble, Distort, Space, …) are applied *to the delay's
feedback path* rather than to the output, so each repeat gets progressively
more wobbled / distorted / band-limited; Echo can also run as a granular
delay with reverse and pitch controls.  The **Loss** module gained a
**Codec** mode — "MP3-style compression and digital degradation" — and Space
grew 32 reverb types.  (The 32 reverb *types* are content; the reverb DSP is
already covered by ``fdn_reverb`` / ``shimmer_reverb``.)

What this module implements (numpy, sample-accurate feedback loop):

- ``FeedbackLoopFX``: fractional-delay echo line with a chain evaluated
  **inside** the loop, once per repeat:
    * ``wobble`` — wow (0.5 Hz) + flutter (6.3 Hz) + slow random drift
      modulating the read position, in cents;
    * ``distort`` — tanh drive with repeat-dependent build-up;
    * ``space`` — loop band-limiting (the RC-20 "Space" tonal stage);
    * ``codec`` — bit-depth / bandwidth reduction derived from a bitrate,
      so every pass through the loop loses more fidelity (the "generation
      loss" character of re-encoding);
    * ``smear`` — a short all-pass diffuser that blurs transients per repeat.
  Feedback is gain-compensated and clamped below unity, so long tails decay
  instead of exploding.
- ``spectral_codec``: offline STFT model of lossy coding — band-limit to a
  bitrate-dependent cutoff and quantise log-magnitudes on a bitrate-dependent
  step, resynthesised with the original phase.  This is what "Codec mode"
  sounds like when applied to a whole track rather than per repeat.

Not replicated: the exact RC-20 module set/presets, the 32 reverb types, the
granular/reverse Echo modes beyond a reverse-read option.

Usage::

    from sound.effects.feedback_loop_fx import FeedbackLoopFX, spectral_codec
    fx = FeedbackLoopFX(44100, delay_ms=375, feedback=0.62, codec=True)
    wet = fx.process(x)
"""

from __future__ import annotations

import numpy as np

TWO_PI = 2.0 * np.pi


def _one_pole_lp(x: np.ndarray, cutoff: float, sr: int) -> np.ndarray:
    a = float(np.exp(-TWO_PI * cutoff / sr))
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1.0 - a) * x[i] + a * acc
        y[i] = acc
    return y


def spectral_codec(x: np.ndarray, sr: int = 44100, bitrate_kbps: float = 96.0,
                   n_fft: int = 1024, hop: int = 256) -> np.ndarray:
    """Lossy-codec model: band-limit + log-magnitude quantisation + OLA.

    ``bitrate_kbps`` 32..320.  Lower bitrate → lower cutoff and coarser
    magnitude quantisation (the two audible artefacts of transform coding).
    """
    x = np.asarray(x, dtype=float)
    mono = x.ndim == 1
    if not mono:
        return np.stack([spectral_codec(ch, sr, bitrate_kbps, n_fft, hop)
                         for ch in x])
    br = float(np.clip(bitrate_kbps, 32.0, 320.0))
    cutoff = float(np.clip(2500.0 + br * 55.0, 4000.0, 20000.0))
    step_db = float(np.clip(190.0 / br, 0.6, 6.0))

    win = np.hanning(n_fft)
    pad = np.concatenate([np.zeros(n_fft), x, np.zeros(n_fft)])
    n_frames = 1 + (len(pad) - n_fft) // hop
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    mask = freqs <= cutoff
    out = np.zeros(len(pad) + n_fft)
    wsum = np.zeros_like(out)
    for k in range(n_frames):
        s = k * hop
        seg = pad[s:s + n_fft] * win
        if len(seg) < n_fft:
            seg = np.pad(seg, (0, n_fft - len(seg)))
        X = np.fft.rfft(seg)
        mag = np.abs(X)
        ph = np.angle(X)
        db = 20.0 * np.log10(mag + 1e-9)
        db = np.round(db / step_db) * step_db          # coarse quantisation
        mag_q = np.where(mask, 10.0 ** (db / 20.0), 0.0)
        y = np.fft.irfft(mag_q * np.exp(1j * ph), n=n_fft) * win
        out[s:s + n_fft] += y
        wsum[s:s + n_fft] += win ** 2
    nz = wsum > 1e-3 * wsum.max()
    out[nz] /= wsum[nz]
    out = out[n_fft:n_fft + len(x)]
    if len(out) < len(x):
        out = np.pad(out, (0, len(x) - len(out)))
    return out


class FeedbackLoopFX:
    """Tape-ish echo whose character modules live inside the feedback path."""

    def __init__(self, sample_rate: int = 44100, delay_ms: float = 375.0,
                 feedback: float = 0.6, mix: float = 0.35,
                 wobble_cents: float = 6.0, wobble_rate: float = 0.5,
                 flutter_rate: float = 6.3, drive: float = 0.15,
                 tone_hz: float = 6000.0, smear: float = 0.15,
                 codec: bool = False, codec_bitrate: float = 96.0,
                 reverse: bool = False):
        self.sr = int(sample_rate)
        self.delay_s = max(0.005, delay_ms / 1000.0)
        self.feedback = float(np.clip(feedback, 0.0, 0.97))
        self.mix = float(np.clip(mix, 0.0, 1.0))
        self.wobble_cents = float(wobble_cents)
        self.wobble_rate = float(wobble_rate)
        self.flutter_rate = float(flutter_rate)
        self.drive = float(drive)
        self.tone_hz = float(tone_hz)
        self.smear = float(smear)
        self.codec = bool(codec)
        self.codec_bitrate = float(codec_bitrate)
        self.reverse = bool(reverse)

    # ------------------------------------------------------------------ #
    def _read(self, buf: np.ndarray, pos: float, n: int) -> np.ndarray:
        """Fractional read of ``n`` samples ending at ``pos`` (loop buffer)."""
        idx = (np.arange(n) + pos) % len(buf)
        lo = np.floor(idx).astype(int)
        frac = idx - lo
        return buf[lo] * (1 - frac) + buf[(lo + 1) % len(buf)] * frac

    def process(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        if x.ndim > 1:
            return np.stack([self.process(ch) for ch in x])
        n = len(x)
        dly = int(round(self.delay_s * self.sr))
        # feedback buffer with a little headroom for modulation
        buf_len = dly + int(0.02 * self.sr) + 8
        buf = np.zeros(buf_len)
        out = np.zeros(n)
        rng = np.random.default_rng(12345)
        drift = 0.0
        # pre-generate modulation (in samples)
        t = np.arange(n) / self.sr
        wobble = (self.wobble_cents / 1200.0) * np.sin(TWO_PI * self.wobble_rate * t)
        flutter = (self.wobble_cents / 1200.0) * 0.25 * np.sin(TWO_PI * self.flutter_rate * t)
        # all-pass diffuser state
        ap_len = max(2, int(0.0035 * self.sr))
        ap_buf = np.zeros(ap_len)
        ap_i = 0
        g_ap = float(np.clip(self.smear, 0.0, 0.7))
        tone_a = float(np.exp(-TWO_PI * self.tone_hz / self.sr))
        tone_acc = 0.0
        bits = int(np.clip(round(4 + self.codec_bitrate / 16.0), 4, 16)) \
            if self.codec else 16
        q = 1.0 / (2 ** (bits - 1))
        codec_lp_a = float(np.exp(-TWO_PI * min(self.codec_bitrate * 55.0 + 2500.0,
                                                self.sr * 0.45) / self.sr))
        codec_acc = 0.0
        fb = self.feedback
        # gentle per-repeat gain compensation for the nonlinear stages
        comp = 1.0 / (1.0 + 0.5 * self.drive)

        for i in range(n):
            drift += rng.normal(0.0, 1e-4)
            drift = float(np.clip(drift * 0.9995, -3e-3, 3e-3))
            mod = (wobble[i] + flutter[i] + drift) * dly
            rp = (i - dly + mod) % buf_len
            y = float(buf[int(rp)]) if not self.reverse else \
                float(buf[int((rp + dly / 2) % buf_len)])
            # --- in-loop character chain (once per repeat) ---------------
            if self.drive > 0:
                y = np.tanh(y * (1.0 + 4.0 * self.drive)) * comp
            tone_acc = (1.0 - tone_a) * y + tone_a * tone_acc
            y = tone_acc
            if self.codec:
                codec_acc = (1.0 - codec_lp_a) * y + codec_lp_a * codec_acc
                y = np.round(codec_acc / q) * q
            if g_ap > 0:
                delayed = ap_buf[ap_i]
                v = y + g_ap * delayed
                ap_buf[ap_i] = v
                ap_i = (ap_i + 1) % ap_len
                y = delayed - g_ap * v
            buf[int(rp)] = x[i] + y * fb
            out[i] = x[i] * (1.0 - self.mix) + y * self.mix
        peak = np.abs(out).max()
        if peak > 0.99:
            out *= 0.99 / peak
        return out

    # ------------------------------------------------------------------ #
    def impulse(self, seconds: float = 3.0, amp: float = 0.9) -> np.ndarray:
        n = int(seconds * self.sr)
        x = np.zeros(n)
        x[0] = amp
        return self.process(x)


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Impulse tail, per-repeat degradation and an offline codec pass."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    sr = 22050

    clean = FeedbackLoopFX(sr, delay_ms=200, feedback=0.7, mix=1.0,
                           wobble_cents=0, drive=0, smear=0, tone_hz=18000)
    dirty = FeedbackLoopFX(sr, delay_ms=200, feedback=0.7, mix=1.0,
                           wobble_cents=25, drive=0.4, smear=0.3,
                           codec=True, codec_bitrate=48, tone_hz=5000)
    hc = clean.impulse(1.5)
    hd = dirty.impulse(1.5)
    dly = int(0.200 * sr)
    peaks_c = [float(np.abs(hc[k * dly:(k + 1) * dly]).max()) for k in range(1, 7)]
    peaks_d = [float(np.abs(hd[k * dly:(k + 1) * dly]).max()) for k in range(1, 7)]
    print(f"feedback-loop demo: delay={dly} samples, fb=0.7")
    print("  clean repeat peaks: " + ", ".join(f"{p:.3f}" for p in peaks_c))
    print("  dirty repeat peaks: " + ", ".join(f"{p:.3f}" for p in peaks_d))

    # codec on a bright signal
    t = np.arange(sr) / sr
    bright = 0.4 * np.sin(2 * np.pi * 440 * t) + 0.25 * np.sin(2 * np.pi * 8800 * t)
    coded = spectral_codec(bright, sr, bitrate_kbps=48)
    hf_in = float(np.abs(np.fft.rfft(bright))[np.argmax(np.fft.rfftfreq(sr, 1 / sr) > 8000)])
    spec_in = np.abs(np.fft.rfft(bright))
    spec_out = np.abs(np.fft.rfft(coded))
    f = np.fft.rfftfreq(sr, 1 / sr)
    hf_in = float(spec_in[(f > 7000)].sum())
    hf_out = float(spec_out[(f > 7000)].sum())
    print(f"  codec 48 kbps: HF energy 7k+ {hf_in:.1f} -> {hf_out:.1f} "
          f"({20 * np.log10(hf_out / hf_in + 1e-12):.1f} dB)")
    print(f"  codec RMS {np.sqrt(np.mean(coded ** 2)):.3f} (in "
          f"{np.sqrt(np.mean(bright ** 2)):.3f}), finite={np.isfinite(coded).all()}")

    assert peaks_c[0] > peaks_c[-1] > 0, peaks_c          # decaying tail
    assert np.isfinite(hc).all() and np.isfinite(hd).all()
    assert hf_out < hf_in * 0.5, (hf_in, hf_out)          # band-limited
    assert np.abs(hd).max() <= 1.0
    for name, sig in (("clean", hc), ("dirty", hd), ("coded", coded)):
        np.save(os.path.join(out_dir, f"feedback_loop_{name}.npy"),
                sig.astype(np.float32))
    print(f"  wrote {out_dir}/feedback_loop_*.npy")
    print("demo OK")
    return {"peaks_clean": peaks_c, "peaks_dirty": peaks_d,
            "hf_in": hf_in, "hf_out": hf_out}


if __name__ == "__main__":
    demo()
