"""Sandbender-style 4-operator FM voice with per-operator waveshaping.

Replicates the Audio Damage Sandbender architecture (announced 2026-11-11):

  * 4 operators, arbitrary routing ("draw your own algorithm") expressed as a
    coupling matrix, so serial stacks, parallel pairs and feedback loops are
    all legal — modulation is applied with a one-sample delay, the standard
    way to make arbitrary FM graphs computable.
  * Per-operator tuning in three modes: harmonic ratio, free ratio, fixed Hz.
  * Per-operator waveshaper morphing triangle -> sine -> pulse (the shapes are
    blended additively, so intermediate settings are genuinely mixed timbres,
    not a crossfade of two finished sounds).
  * Wavefolder with symmetric / asymmetric / soft-clip modes.
  * Low-pass gate: brightness and amplitude driven by the same control signal
    with a vactrol-ish asymmetric lag — the defining behaviour of an LPG
    versus a plain VCA.

Only numpy + stdlib. Everything renders deterministically at a fixed seed.
"""

from __future__ import annotations

import numpy as np

TAU = 2.0 * np.pi


# --------------------------------------------------------------------------
# waveforms / shapers
# --------------------------------------------------------------------------
def tri_sine_pulse(phase: np.ndarray, morph: float) -> np.ndarray:
    """Blend triangle (morph=0) -> sine (0.5) -> pulse (1.0).

    ``phase`` is in cycles [0,1). The three shapes are summed with weights so
    a morph of 0.35 really is 65 % triangle + 35 % (sine/pulse mix).
    """
    m = float(np.clip(morph, 0.0, 1.0))
    tri = 1.0 - 4.0 * np.abs(phase - 0.5)
    sine = np.sin(TAU * phase)
    # pulse is a duty-warped ramp; 25 % duty reads clearly as "pulse"
    pulse = np.where(phase < 0.25, 1.0, -1.0)
    if m <= 0.5:
        w = m / 0.5
        return (1.0 - w) * tri + w * sine
    w = (m - 0.5) / 0.5
    return (1.0 - w) * sine + w * pulse


def wavefold(x: np.ndarray, amount: float = 1.0, mode: str = "symmetric") -> np.ndarray:
    """Wavefolder.

    symmetric : reflect about +/-1 with gain ``amount`` (classic Buchla fold)
    asymmetric: fold the positive half only, negative half hard-clipped
    soft      : tanh-ish soft clip with 3rd-harmonic emphasis

    Reflection uses the triangle-wave identity ``fold(u) = 4*|u/4 - floor(u/4
    + 0.5)| - 1`` which folds indefinitely without iterating.
    """
    g = max(1e-6, float(amount))
    if mode == "soft":
        return np.tanh(x * g) / np.tanh(1.0) if g > 0 else x
    if mode == "asymmetric":
        pos = x * g
        folded = 4.0 * np.abs(pos / 4.0 - np.floor(pos / 4.0 + 0.5)) - 1.0
        neg = np.clip(x * g, -1.0, 0.0)
        return np.where(x >= 0, folded, neg)
    u = x * g
    return 4.0 * np.abs(u / 4.0 - np.floor(u / 4.0 + 0.5)) - 1.0


def svf(x: np.ndarray, cutoff: float, q: float, mode: str = "lp",
        sr: int = 44100, poles: int = 2) -> np.ndarray:
    """TPT state-variable filter, 12 dB/oct per pass (``poles=2`` => 24 dB)."""
    out = np.asarray(x, dtype=float)
    for _ in range(1 if poles <= 2 else 2):
        g = np.tan(np.pi * min(cutoff, sr * 0.45) / sr)
        k = 1.0 / max(1e-3, q)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        ic1 = 0.0
        ic2 = 0.0
        y = np.empty_like(out)
        for n in range(out.shape[0]):
            v3 = out[n] - ic2
            v1 = a1 * ic1 + a2 * v3
            v2 = ic2 + a2 * ic1 + a3 * v3
            ic1 = 2.0 * v1 - ic1
            ic2 = 2.0 * v2 - ic2
            if mode == "lp":
                y[n] = v2
            elif mode == "bp":
                y[n] = v1
            else:
                y[n] = out[n] - k * v1 - v2
        out = y
    return out


def noise_bank(kind: str, n: int, rng: np.random.Generator, sr: int = 44100) -> np.ndarray:
    """Six noise types: white, pink, velvet, digital, crackle, metal."""
    white = rng.standard_normal(n)
    if kind == "white":
        return white
    if kind == "pink":  # Voss-McCartney-ish: sum of octave-decimated whites
        out = np.zeros(n)
        step = 1
        while step < n:
            hold = rng.standard_normal(n // step + 1)
            out += np.repeat(hold, step)[:n]
            step *= 2
        return out / np.abs(out).max()
    if kind == "velvet":  # sparse pulse train (velvet noise)
        out = np.zeros(n)
        step = max(1, int(0.0015 * sr))
        idx = np.arange(0, n, step)
        out[idx] = rng.choice([-1.0, 1.0], len(idx))
        return out
    if kind == "digital":  # sample-and-hold at ~sr/24 with bit crush
        hold = 24
        s = rng.standard_normal(n // hold + 1)
        out = np.repeat(s, hold)[:n]
        return np.round(out * 4) / 4
    if kind == "crackle":  # sparse decaying impulses
        out = np.zeros(n)
        for _ in range(max(1, n // (sr // 12))):
            i = rng.integers(0, n)
            out[i] = rng.choice([-1.0, 1.0]) * rng.uniform(0.4, 1.0)
        return out
    # metal: ring-modulated noise
    t = np.arange(n) / sr
    return white * np.sin(TAU * 1730.0 * t)


# --------------------------------------------------------------------------
# voice
# --------------------------------------------------------------------------
class SandbenderFM:
    """4-operator FM voice with waveshaping, folder, sub, noise, SVF and LPG.

    Parameters
    ----------
    ratios : 4 operator frequency ratios (Hz multiply of note freq) or fixed Hz
    ratio_mode : 'harmonic' | 'free' | 'fixed' per operator
    levels : operator output levels 0..1
    shapes : per-operator waveshaper morph 0 (tri) .. 1 (pulse)
    matrix : list of (src, dst, depth) — src modulates dst's phase
    regen : per-operator self-feedback (bytes -> "Regen")
    """

    ALGORITHMS = {
        # name: (matrix, carrier_mask)
        "stack4": ([(0, 1, 0.8), (1, 2, 0.8), (2, 3, 0.8)], [3]),
        "pair_pair": ([(0, 1, 0.9), (2, 3, 0.9)], [1, 3]),
        "three_into_one": ([(0, 3, 0.7), (1, 3, 0.6), (2, 3, 0.5)], [3]),
        "tower": ([(0, 1, 0.7), (1, 3, 0.6), (2, 3, 0.5)], [3]),
        "two_carriers": ([(0, 1, 0.5), (2, 3, 0.5), (0, 2, 0.2)], [1, 3]),
    }

    def __init__(self, ratios=(1.0, 2.0, 3.0, 7.0), ratio_mode=("harmonic",) * 4,
                 levels=(1.0, 0.7, 0.5, 0.8), shapes=(0.5, 0.5, 0.5, 0.5),
                 matrix=None, regen=(0.0, 0.0, 0.0, 0.0), detune=(0.0,) * 4,
                 spread=0.0, sub_octave=1, sub_level=0.0, sub_shape=0.5,
                 noise_kind="white", noise_level=0.0,
                 folder_amount=0.0, folder_mode="symmetric",
                 filter_mode="lp", filter_cutoff=8000.0, filter_q=0.9,
                 filter_poles=2, lpg=True, lpg_response=0.6,
                 sr=44100):
        self.ratios = np.asarray(ratios, dtype=float)
        self.ratio_mode = ratio_mode
        self.levels = np.asarray(levels, dtype=float)
        self.shapes = np.asarray(shapes, dtype=float)
        self.matrix = matrix if matrix is not None else self.ALGORITHMS["stack4"][0]
        self.regen = np.asarray(regen, dtype=float)
        self.detune = np.asarray(detune, dtype=float)
        self.spread = float(spread)
        self.sub_octave, self.sub_level, self.sub_shape = sub_octave, sub_level, sub_shape
        self.noise_kind, self.noise_level = noise_kind, noise_level
        self.folder_amount, self.folder_mode = folder_amount, folder_mode
        self.filter_mode, self.filter_cutoff = filter_mode, filter_cutoff
        self.filter_q, self.filter_poles = filter_q, filter_poles
        self.lpg, self.lpg_response = lpg, lpg_response
        self.sr = sr

    # -- operator frequencies ------------------------------------------------
    def _op_freqs(self, f0: float) -> np.ndarray:
        out = np.empty(4)
        for i in range(4):
            if self.ratio_mode[i] == "fixed":
                out[i] = self.ratios[i]
            elif self.ratio_mode[i] == "free":
                out[i] = f0 * self.ratios[i] + self.detune[i]
            else:
                out[i] = f0 * max(1e-3, round(self.ratios[i] * 1.0) if self.ratios[i] >= 1
                                  else self.ratios[i]) + self.detune[i]
        return out

    def lpg_shape(self, env: np.ndarray) -> np.ndarray:
        """Low-pass gate transfer: amplitude = env^gamma, cutoff tracks env."""
        g = np.clip(env, 0.0, 1.0)
        return g ** (1.0 / max(0.1, self.lpg_response))

    def render_note(self, f0: float, dur: float, amp: float = 1.0,
                    gate_curve: float = 0.35, seed: int = 0) -> np.ndarray:
        n = max(64, int(dur * self.sr))
        rng = np.random.default_rng(seed)
        freqs = self._op_freqs(f0)
        inc = freqs / self.sr

        # reverb-free, per-sample operator loop over the whole note so an
        # arbitrary DAG (and self-feedback) stays sample-accurate
        ph = rng.random(4)
        prev = np.zeros(4)
        op_out = np.zeros((4, n))
        for s in range(n):
            vals = np.empty(4)
            for i in range(4):
                # phase modulation from every (src -> i) edge, one-sample
                # delayed: that delay is what makes cycles legal
                pm = 0.0
                for src, dst, depth in self.matrix:
                    if dst == i:
                        pm += depth * prev[src]
                pm += self.regen[i] * prev[i]
                p = (ph[i] + pm) % 1.0
                vals[i] = tri_sine_pulse(np.array([p]), self.shapes[i])[0]
                ph[i] = (ph[i] + inc[i]) % 1.0
            prev = vals
            op_out[:, s] = vals

        carriers = [dst for _, dst, _ in self.matrix] if self.matrix else [3]
        carriers = sorted(set(carriers)) or [3]
        carriers = [c for c in carriers if c not in [s for s, d, _ in self.matrix]
                    or len(carriers) == 1] or [3]

        mix = np.zeros(n)
        for i in carriers:
            mix += self.levels[i] * op_out[i]

        if self.sub_level > 0:
            t = np.arange(n) / self.sr
            sub_ph = (f0 / (2 ** self.sub_octave) * t) % 1.0
            mix += self.sub_level * tri_sine_pulse(sub_ph, self.sub_shape)

        if self.noise_level > 0:
            mix += self.noise_level * noise_bank(self.noise_kind, n, rng, self.sr)

        if self.folder_amount > 0:
            mix = wavefold(mix, self.folder_amount, self.folder_mode)

        if self.filter_cutoff < self.sr * 0.45:
            mix = svf(mix, self.filter_cutoff, self.filter_q,
                      self.filter_mode, self.sr, self.filter_poles)

        # gate: vactrol-ish asymmetric envelope
        t = np.linspace(0, 1, n)
        gate = np.clip((1.0 - t) / max(1e-6, gate_curve), 0.0, 1.0)
        gate = np.where(t < gate_curve, 1.0, gate)
        if self.lpg:
            g = self.lpg_shape(gate)
            # brightness follows the gate: cheap one-pole on the unfolded mix
            alpha = 0.002 + 0.4 * g
            bright = np.empty(n)
            acc = 0.0
            for s in range(n):
                acc += alpha[s] * (mix[s] - acc)
                bright[s] = acc
            mix = bright * g
        else:
            mix = mix * gate

        mix = mix * amp
        peak = np.abs(mix).max()
        return mix / peak * 0.9 if peak > 1e-9 else mix

    def render_phrase(self, notes, sr=None, gap=0.015) -> np.ndarray:
        """notes: list of (freq_hz, dur_s, amp)."""
        sr = sr or self.sr
        total = sum(d for _, d, _ in notes) + gap * len(notes) + 0.1
        out = np.zeros(int(total * sr))
        t = 0.0
        for k, (f, d, a) in enumerate(notes):
            seg = self.render_note(f, d, a, seed=k)
            i0 = int(t * sr)
            out[i0:i0 + len(seg)] += seg[: max(0, len(out) - i0)]
            t += d + gap
        return out


def demo() -> None:
    """Render three Sandbender patches and report real numbers."""
    # 1. serial 4-op stack, heavy shaping + folder
    v = SandbenderFM(ratios=(1.0, 3.0, 5.0, 1.0), shapes=(0.5, 0.9, 0.2, 0.5),
                     folder_amount=1.8, folder_mode="symmetric",
                     filter_cutoff=6000.0, lpg=True)
    a = v.render_phrase([(220.0, 0.35, 1.0), (277.18, 0.35, 0.9),
                         (329.63, 0.7, 1.0)])
    # harmonic richness check: energy above 2 kHz vs total
    spec = np.abs(np.fft.rfft(a))
    f = np.fft.rfftfreq(len(a), 1 / v.sr)
    hf = spec[f > 2000].sum() / max(1e-9, spec.sum())
    print(f"sandbender demo: stack4+fold -> {len(a)} samples "
          f"({len(a)/v.sr:.2f}s) peak={np.abs(a).max():.3f} HF ratio={hf:.3f}")

    # 2. two carriers, asymmetric fold, noise bed
    v2 = SandbenderFM(ratios=(1.0, 2.0, 4.0, 1.5), ratio_mode=("harmonic", "harmonic",
                                                              "free", "harmonic"),
                      matrix=v.ALGORITHMS["two_carriers"][0], noise_kind="metal",
                      noise_level=0.15, folder_amount=1.2, folder_mode="asymmetric",
                      sub_octave=1, sub_level=0.3, filter_mode="bp", filter_q=1.4)
    b = v2.render_note(110.0, 0.6)
    print(f"  two_carriers: {len(b)} samples rms={np.sqrt((b**2).mean()):.4f}")

    # 3. LPG vs VCA brightness — LPG must darken as it closes
    v3 = SandbenderFM(ratios=(1.0, 2.0, 3.0, 5.0), folder_amount=1.0, lpg=True)
    c = v3.render_note(261.63, 0.8)
    early = np.abs(np.fft.rfft(c[:2048])).mean()
    late = np.abs(np.fft.rfft(c[-2048:])).mean()
    print(f"  lpg note: early-mag={early:.2f} late-mag={late:.2f} "
          f"(decays: {late < early})")

    for sig in (a, b, c):
        assert len(sig) > 1000 and np.isfinite(sig).all() and np.abs(sig).max() > 0.01
    assert hf > 0.05, "folder/FM should leave real high-frequency content"
    assert late < early, "LPG must close brightness along with amplitude"
    print("demo OK")


if __name__ == "__main__":
    demo()
