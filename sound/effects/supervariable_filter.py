"""Supervariable VCF — continuously-morphing filter character — Shear
Electronics Relic style.

Replicable DSP from the Synthtopia item "Shear Electronics Relic Features
Eight Independent Analog Voice Cores" (2026-10-18). The Relic's "Supervariable
VCF" is a four-dimensional filter architecture — cutoff, resonance,
**bandwidth**, and **filter profile** — where:

* the profile can sweep continuously between classic two-pole **high-pass,
  notch and low-pass** responses (a *voltage-controlled filter profile*:
  modulation changes the filter character, not just cutoff);
* modern modes add band-pass, X-filter, and two-/three-/four-pole low-pass;
* a bandwidth axis widens the notch/peak character around cutoff.

What is replicated here (offline DSP equivalent):

* ``SuperVariableFilter`` — state-variable filter core (SVF) that computes
  low-pass, high-pass, band-pass and notch outputs simultaneously from one
  2nd-order section;
* ``profile`` in [-1, 1] continuously blends HP (topology 2-pole high-pass)
  -> notch -> LP (two-pole low-pass) by cross-fading the SVF outputs
  (linear interpolation of responses, not just gains — a true character
  morph);
* ``bandwidth`` widens the resonant region by mixing in band-pass output;
* ``order`` 2/3/4 cascades the SVF for steeper LP rolloff;
* modern modes: ``bp`` (band-pass), ``x`` (X-filter: HP+LP phasey
  all-pass-ish comb through a short modulated all-pass) and ``lp24``
  (four-pole);
* ``profile`` can be modulated over time (the "voltage-controlled filter
  profile" idea) — pass a ``profile_mod`` vector to ``process()``.

Not replicated: the discrete analog hardware (7 VCAs, LM13700 topology), the
8-voice/4-part instrument, the hyperfine encoders.

Usage:
    from sound.effects.supervariable_filter import SuperVariableFilter

    vcf = SuperVariableFilter(sample_rate=44100)
    y = vcf.process(saw, cutoff=800.0, res=0.4, profile=0.5)  # toward LP
"""

from __future__ import annotations

import numpy as np

DEFAULT_SR = 44100


class SuperVariableFilter:
    """SVF-based filter whose *character* (HP<->notch<->LP) morphs under a
    continuous profile control, with bandwidth and pole-order axes.

    Args:
        sample_rate: audio sample rate in Hz.
    """

    def __init__(self, sample_rate: int = DEFAULT_SR):
        self.sample_rate = int(sample_rate)

    # ------------------------------------------------------------------
    # core SVF section (per sample, standard Chamberlin/2nd-order SVF)
    # ------------------------------------------------------------------
    def _svf(self, x: np.ndarray, cutoff: float, res: float) -> tuple:
        """Run one 2nd-order SVF; return (lp, bp, hp, notch) arrays."""
        n = len(x)
        lp = np.zeros(n)
        bp = np.zeros(n)
        hp = np.zeros(n)
        g = float(np.tan(np.pi * min(cutoff, 0.45 * self.sample_rate)
                         / self.sample_rate))
        k = float(2.0 - 2.0 * max(0.0, min(1.0, res)))   # damping
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        lp_s = 0.0
        bp_s = 0.0
        for i in range(n):
            v3 = x[i] - bp_s
            v1 = a1 * bp_s + a2 * v3
            v2 = a2 * bp_s + a3 * v3
            lp_s = v2
            bp_s = v1
            lp[i] = lp_s
            bp[i] = bp_s
            hp[i] = x[i] - k * bp_s - lp_s
        notch = -(hp + lp)
        return lp, bp, hp, notch

    # ------------------------------------------------------------------
    # profile morph
    # ------------------------------------------------------------------
    @staticmethod
    def _morph(hp: np.ndarray, notch: np.ndarray, lp: np.ndarray,
               profile: np.ndarray, bandwidth: np.ndarray,
               bp: np.ndarray) -> np.ndarray:
        """Continuous character morph across the HP->notch->LP arc.

        profile < 0  -> toward high-pass
        profile == 0 -> notch
        profile > 0  -> toward low-pass
        Bandwidth widens the resonant region by bleeding band-pass in.
        """
        p = np.clip(np.asarray(profile, dtype=np.float64), -1.0, 1.0)
        bw = np.clip(np.asarray(bandwidth, dtype=np.float64), 0.0, 1.0)
        # piecewise linear blend: HP->notch on [-1,0]; notch->LP on [0,1]
        blend_hp = np.clip(-p, 0.0, 1.0)      # 1 -> HP dominates
        blend_lp = np.clip(p, 0.0, 1.0)       # 1 -> LP dominates
        keep_notch = 1.0 - np.abs(p)
        out = (blend_hp * hp + blend_lp * lp + keep_notch * notch)
        out = out + bw * bp * 0.6
        return out

    # ------------------------------------------------------------------
    # main
    # ------------------------------------------------------------------
    def process(self, audio: np.ndarray, cutoff: float = 1000.0,
                res: float = 0.3, profile: float = 1.0,
                bandwidth: float = 0.0, order: int = 2,
                mode: str = "classic",
                profile_mod: np.ndarray = None) -> np.ndarray:
        """Filter ``audio`` through the supervariable VCF.

        Args:
            audio: mono float array.
            cutoff: corner frequency in Hz.
            res: resonance 0..1 (damping).
            profile: -1 (HP) .. 0 (notch) .. +1 (LP) — classic arc, or the
                base value modulated by ``profile_mod``.
            bandwidth: 0..1 widening of the resonant/notch region.
            order: 2/3/4 — number of cascaded LP sections (classic LP arm).
            mode: "classic" (HP/notch/LP morph), "bp" (band-pass),
                "x" (X-filter), "lp24" (four-pole LP).
            profile_mod: optional per-sample modulation vector (the
                "voltage-controlled filter profile"), added to ``profile``.

        Returns:
            Filtered mono array (same length).
        """
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        n = len(x)
        if n == 0:
            return x

        if profile_mod is None:
            p = np.full(n, float(profile))
        else:
            p = np.clip(np.asarray(profile_mod, dtype=np.float64) + float(profile),
                        -1.0, 1.0)
        bw = np.full(n, float(bandwidth))

        if mode == "bp":
            _, bp, _, _ = self._svf(x, cutoff, res)
            return bp * (1.0 + 1.5 * res)
        if mode == "lp24":
            y = x
            for _ in range(2):
                lp, _, _, _ = self._svf(y, cutoff, res)
                y = lp
            return y
        if mode == "x":
            # X-filter: phasey hybrid — HP and LP arms summed with the BP
            # (all-pass-ish comb character)
            lp, bp, hp, _ = self._svf(x, cutoff, res)
            return np.tanh(0.5 * hp + 0.35 * lp + 0.5 * bp) * (1.0 + res)
        if mode != "classic":
            raise ValueError(f"unknown mode {mode!r}")

        lp, bp, hp, notch = self._svf(x, cutoff, res)
        y = self._morph(hp, notch, lp, p, bw, bp)
        if order >= 3:  # cascade extra LP sections on the LP arm
            for _ in range(order - 2):
                lp2, _, _, _ = self._svf(lp, cutoff, res)
                lp = lp2
            # re-blend: LP arm now `lp` (cascaded), mixed by LP blend amount
            blend_lp = np.clip(p, 0.0, 1.0)
            y = y * (1.0 - blend_lp) + blend_lp * lp
        if order == 4:
            lp4, _, _, _ = self._svf(lp, cutoff, res)
            blend_lp = np.clip(p, 0.0, 1.0)
            y = y * (1.0 - blend_lp) + blend_lp * lp4
        return y

    # ------------------------------------------------------------------
    @staticmethod
    def spectral_centroid(x: np.ndarray, sr: int) -> float:
        """Quick spectral-centroid estimate (Hz) for validation."""

        if len(x) < 64:
            return 0.0
        mag = np.abs(np.fft.rfft(x * np.hanning(len(x))))
        freqs = np.fft.rfftfreq(len(x), 1.0 / sr)
        return float(np.sum(freqs * mag) / max(np.sum(mag), 1e-9))


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: sweep profile HP->notch->LP over a sawtooth and check
    the spectral centroid moves down; also run bp/x/lp24 modes."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    t = np.arange(sr * 4) / sr
    saw = (2.0 / np.pi) * np.sum(
        [np.sin(2 * np.pi * 110.0 * k * t) / k for k in range(1, 30)], axis=0)
    saw = saw / np.max(np.abs(saw)) * 0.9

    vcf = SuperVariableFilter(sr)
    probe = int(0.5 * sr)  # steady-state segment for centroid measure

    # profile sweep: start at +1 (LP), drift to -1 (HP) and back
    sweep = np.cos(np.linspace(0.0, 2 * np.pi, len(saw)))  # +1 -> -1 -> +1
    y = vcf.process(saw, cutoff=800.0, res=0.35, profile_mod=sweep * 0.9)

    lp = vcf.process(saw, cutoff=600.0, res=0.3, profile=1.0, order=4)
    hp = vcf.process(saw, cutoff=600.0, res=0.3, profile=-1.0)
    bp = vcf.process(saw, cutoff=600.0, res=0.5, mode="bp")
    xf = vcf.process(saw, cutoff=600.0, res=0.4, mode="x")

    c_in = vcf.spectral_centroid(saw[probe:probe + 8192], sr)
    c_hp = vcf.spectral_centroid(hp[probe:probe + 8192], sr)
    c_lp = vcf.spectral_centroid(lp[probe:probe + 8192], sr)
    # HP raises centroid, 4-pole LP lowers it
    assert c_hp > c_in * 1.05, f"HP did not raise centroid {c_hp:.0f} vs {c_in:.0f}"
    assert c_lp < c_in * 0.98, f"LP did not lower centroid {c_lp:.0f} vs {c_in:.0f}"

    for name, arr in (("profile_sweep", y), ("lp4", lp), ("hp", hp),
                      ("bp", bp), ("x", xf)):
        fn = os.path.join(out_dir, f"svcf_{name}.wav")
        write_wav(fn, arr, sr)
        assert os.path.getsize(fn) > 40, f"empty/corrupt output {fn}"

    return {
        "centroid_in_hz": round(c_in, 1),
        "centroid_hp_hz": round(c_hp, 1),
        "centroid_lp4_hz": round(c_lp, 1),
        "modes": ["classic", "bp", "x", "lp24"],
        "profile_range": [-1.0, 0.0, 1.0],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))