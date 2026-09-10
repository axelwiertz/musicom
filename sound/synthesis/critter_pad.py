"""Pad partial bank with "Critters" stochastic partial — Crow Hill Brackish Pads style.

Replicable logic from the Sound On Sound review of Crow Hill Company
"Brackish Pads" (SOS September 2026, 5/5 stars):

  * Each patch is **three sampled partials**: a *Basic* layer, a *Complex* layer
    and a dedicated *Critters* partial; partials are re-balanced with three
    sliders.
  * The instrument's identity is **unpredictable note modulation plus
    microtonal shifts** — "a sense of unstable pitch-wobble creating a
    disturbing undertow ... hints at a badly maintained Mellotron".
  * Four **Pump Triggers** (coloured keys) fire different envelopes linked to a
    compressor; a *Cassette* control dials in lo-fi wear; a *Splosh* reverb
    adds solidity.

What is replicated here:
- ``Partial``: a layer spec (waveform mix, detune cents, octave, envelope,
  noise, wobble) rendered to audio — the Basic/Complex/Critters roles.
- ``PadPartialBank``: three layers with independent balance sliders.
- ``Critters``: the stochastic partial — clusters of detuned partials triggered
  from a Poisson process (per-note random density), each cluster given a
  microtonal offset drawn from a configurable set (default quarter-tones,
  +/-50 cents), micro-scheduled, with a slow random drift per cluster. This is
  the "unpredictable note modulation + microtonal shift" engine.
- ``pump_envelope``: the four Pump Triggers -> four attack/decay envelopes.
- ``cassette``: lo-fi wear (band-limit, wow/flutter, tape hiss, asymmetric
  compression) as an amount-driven degradation stage.
- ``splosh``: cheap reverb that adds "solidity" by mixing an early-reflection
  tail.

Not replicated: the 16 sampled patch sets and their 1.25 GB of content, the
Csound/engine internals of the original.

Usage:
    from sound.synthesis.critter_pad import PadPartialBank, Critters

    bank = PadPartialBank(sample_rate=44100)
    wav = bank.render_note(freq=110.0, duration=4.0, seed=3)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "Partial",
    "Critters",
    "PadPartialBank",
    "pump_envelope",
    "cassette",
    "splosh",
    "MICROTONAL_SETS",
]

# Microtonal offset sets (cents) for the Critters partial.
MICROTONAL_SETS: Dict[str, Tuple[float, ...]] = {
    "quarter-tone": (-50.0, 0.0, 50.0),
    "eighth-tone": (-25.0, 0.0, 25.0),
    "just-ish": (-13.7, 0.0, 15.6, 31.2, -31.2),
    "chromatic-drift": (-100.0, -55.0, -30.0, 0.0, 42.0, 88.0),
}


def _wobble(n: int, rate: float, depth: float, sr: int, rng) -> np.ndarray:
    """Random-walk LFO (unstable pitch-wobble, not a clean sine)."""
    steps = max(4, int(n / max(1, int(sr / max(1.0, rate * 20)))))
    knots = rng.standard_normal(steps)
    walk = np.cumsum(knots)
    walk -= walk.mean()
    peak = np.max(np.abs(walk)) + 1e-9
    curve = np.interp(np.linspace(0, steps - 1, n),
                      np.arange(steps), walk / peak)
    return depth * curve


class Partial:
    """One pad layer: detuned wave mix + envelope + optional stochastic content."""

    def __init__(self, name: str = "basic", waveform: str = "saw",
                 detune_cents: Sequence[float] = (0.0,),
                 levels: Optional[Sequence[float]] = None,
                 octave: int = 0, attack: float = 0.8, release: float = 2.0,
                 wobble_cents: float = 6.0, noise: float = 0.02,
                 critters: bool = False):
        self.name = name
        self.waveform = waveform
        self.detune_cents = tuple(float(c) for c in detune_cents)
        self.levels = tuple(levels) if levels else tuple(
            [1.0 / len(self.detune_cents)] * len(self.detune_cents))
        self.octave = int(octave)
        self.attack = float(attack)
        self.release = float(release)
        self.wobble_cents = float(wobble_cents)
        self.noise = float(noise)
        self.critters = bool(critters)

    # -- helpers ------------------------------------------------------------
    def _osc(self, freq: float, n: int, sr: int) -> np.ndarray:
        tt = np.arange(n) / sr
        ph = 2 * np.pi * freq * tt
        if self.waveform == "saw":
            return 2.0 * (ph / (2 * np.pi) % 1.0) - 1.0
        if self.waveform == "pulse":
            return np.where(ph / (2 * np.pi) % 1.0 < 0.5, 1.0, -1.0)
        if self.waveform == "tri":
            return 2.0 * np.abs(2.0 * (ph / (2 * np.pi) % 1.0) - 1.0) - 1.0
        return np.sin(ph)

    def _env(self, n: int, sr: int) -> np.ndarray:
        a = max(1, int(self.attack * sr))
        r = max(1, int(self.release * sr))
        env = np.ones(n)
        env[:min(a, n)] = np.linspace(0.0, 1.0, min(a, n))
        if r < n:
            env[n - r:] = np.linspace(1.0, 0.0, r)
        return env

    def render(self, freq: float, duration: float, sr: int = 44100,
               rng: Optional[np.random.Generator] = None) -> np.ndarray:
        rng = rng or np.random.default_rng(0)
        n = int(duration * sr)
        f0 = freq * (2.0 ** self.octave)
        pitch_bend = _wobble(n, rate=0.8, depth=self.wobble_cents, sr=sr, rng=rng)
        out = np.zeros(n)
        for cents, lvl in zip(self.detune_cents, self.levels):
            # integrate the (possibly per-sample) detune so phase stays smooth
            r = 2.0 ** ((np.asarray(cents) + pitch_bend) / 1200.0)
            phase = np.cumsum(2 * np.pi * f0 * r / sr)
            if self.waveform == "saw":
                w = 2.0 * (phase / (2 * np.pi) % 1.0) - 1.0
            elif self.waveform == "pulse":
                w = np.where(phase / (2 * np.pi) % 1.0 < 0.5, 1.0, -1.0)
            elif self.waveform == "tri":
                w = 2.0 * np.abs(2.0 * (phase / (2 * np.pi) % 1.0) - 1.0) - 1.0
            else:
                w = np.sin(phase)
            out += lvl * w
        out *= self._env(n, sr)
        if self.noise > 0:
            out += self.noise * rng.standard_normal(n) * self._env(n, sr)
        return out


class Critters:
    """Stochastic microtonal partial: Poisson-triggered detuned clusters."""

    def __init__(self, sample_rate: int = 44100, density: float = 2.0,
                 partials_per_cluster: Tuple[int, int] = (3, 7),
                 microtonal_set: str = "quarter-tone",
                 drift_cents: float = 25.0, cluster_len: float = 2.0):
        self.sr = int(sample_rate)
        self.density = float(density)                # clusters per second
        self.partials_per_cluster = partials_per_cluster
        self.microtonal_set = microtonal_set
        self.set_cents = MICROTONAL_SETS.get(microtonal_set,
                                             MICROTONAL_SETS["quarter-tone"])
        self.drift_cents = float(drift_cents)
        self.cluster_len = float(cluster_len)

    def trigger_times(self, duration: float, seed: int = 0) -> np.ndarray:
        """Poisson process of cluster onsets over ``duration`` seconds."""
        rng = np.random.default_rng(seed)
        expected = max(0, int(duration * self.density * 2))
        if expected == 0:
            return np.zeros(0)
        gaps = rng.exponential(1.0 / max(1e-6, self.density), expected)
        times = np.cumsum(gaps)
        return times[times < duration]

    def render(self, freq: float, duration: float, seed: int = 0,
               sr: Optional[int] = None) -> np.ndarray:
        sr = sr or self.sr
        n = int(duration * sr)
        out = np.zeros(n)
        rng = np.random.default_rng(seed)
        for t0 in self.trigger_times(duration, seed=seed):
            n_parts = int(rng.integers(self.partials_per_cluster[0],
                                       self.partials_per_cluster[1] + 1))
            clen = int(min(self.cluster_len, duration - t0) * sr)
            if clen <= 8:
                continue
            start = int(t0 * sr)
            env = np.hanning(clen) ** 1.5
            cluster = np.zeros(clen)
            for _ in range(n_parts):
                cents = float(rng.choice(self.set_cents))
                cents += rng.uniform(-1.0, 1.0) * self.drift_cents * 0.15
                ratio = 2.0 ** ((cents + rng.uniform(-self.drift_cents,
                                                     self.drift_cents)) / 1200.0)
                f = freq * float(rng.choice([0.5, 1.0, 1.0, 2.0, 3.0])) * ratio
                if f >= sr * 0.45:
                    continue
                phase = np.cumsum(2 * np.pi * f / sr * np.ones(clen))
                cluster += np.sin(phase) * rng.uniform(0.2, 1.0)
            cluster /= max(1, n_parts) ** 0.5
            seg = cluster * env
            out[start:start + len(seg)] += seg
        return out


class PadPartialBank:
    """Basic + Complex + Critters layers with balance sliders (Brackish Pads)."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)
        self.basic = Partial("basic", "saw", detune_cents=(-7, 0, 7),
                             octave=0, attack=1.2, release=2.4,
                             wobble_cents=4.0, noise=0.015)
        self.complex = Partial("complex", "tri", detune_cents=(-14, 3, 19),
                               octave=0, attack=1.8, release=3.0,
                               wobble_cents=11.0, noise=0.03)
        self.critters = Critters(sample_rate=sample_rate)
        self.balance: Dict[str, float] = {"basic": 0.7, "complex": 0.5,
                                          "critters": 0.45}

    def render_note(self, freq: float = 110.0, duration: float = 4.0,
                    seed: int = 0) -> np.ndarray:
        rng = np.random.default_rng(seed)
        a = self.basic.render(freq, duration, self.sr, rng)
        b = self.complex.render(freq, duration, self.sr, rng)
        c = self.critters.render(freq, duration, seed=seed, sr=self.sr)
        mixed = (self.balance["basic"] * a
                 + self.balance["complex"] * b
                 + self.balance["critters"] * c)
        peak = np.max(np.abs(mixed)) + 1e-9
        return (mixed / peak * 0.8).astype(np.float64)

    def render_with_processing(self, freq: float = 110.0, duration: float = 4.0,
                               seed: int = 0, cassette_amount: float = 0.4,
                               splosh_mix: float = 0.25,
                               pump: Optional[int] = None) -> np.ndarray:
        wav = self.render_note(freq, duration, seed)
        if cassette_amount > 0:
            wav = cassette(wav, self.sr, amount=cassette_amount)
        if splosh_mix > 0:
            wav = splosh(wav, self.sr, mix=splosh_mix)
        if pump is not None:
            wav = wav * pump_envelope(len(wav), self.sr, pump)
        return wav


# ------------------------------------------------------------ character stages
def pump_envelope(n: int, sr: int, which: int = 0) -> np.ndarray:
    """Four Pump Triggers: distinct attack/decay shapes (0..3)."""
    specs = ((0.005, 0.25), (0.02, 0.9), (0.15, 1.8), (0.4, 3.2))
    a, r = specs[int(which) % 4]
    an = max(1, int(a * sr))
    rn = max(1, int(r * sr))
    env = np.ones(n)
    env[:min(an, n)] = np.linspace(0.0, 1.0, min(an, n))
    if rn < n:
        env[n - rn:] = np.linspace(1.0, 0.0, rn)
    return env


def cassette(audio: np.ndarray, sr: int = 44100, amount: float = 0.5) -> np.ndarray:
    """Lo-fi tape wear: band-limit, wow/flutter, hiss, asymmetric squash."""
    x = np.asarray(audio, dtype=np.float64).reshape(-1)
    amt = float(np.clip(amount, 0.0, 1.0))
    n = len(x)
    if n == 0:
        return x
    # wow / flutter: slow + fast delay modulation via interpolated resample
    tt = np.arange(n) / sr
    wow = 0.004 * amt * np.sin(2 * np.pi * 0.7 * tt)
    flut = 0.0012 * amt * np.sin(2 * np.pi * 6.3 * tt)
    warp = (tt + wow + flut) * sr
    idx = np.clip(warp, 0, n - 1)
    i0 = np.floor(idx).astype(int)
    frac = idx - i0
    y = (1 - frac) * x[i0] + frac * x[np.minimum(i0 + 1, n - 1)]
    # band-limit highs (head loss) with a one-pole
    a = 1.0 - np.exp(-2 * np.pi * (4000.0 + 8000.0 * (1 - amt)) / sr)
    lp = np.empty(n)
    z = 0.0
    for i in range(n):
        z += a * (y[i] - z)
        lp[i] = z
    y = lp
    # hiss
    rng = np.random.default_rng(0)
    y = y + 0.012 * amt * rng.standard_normal(n)
    # asymmetric squash (tape compression)
    y = np.tanh(y * (1.0 + 1.5 * amt)) / (1.0 + 0.7 * amt)
    return y


def splosh(audio: np.ndarray, sr: int = 44100, mix: float = 0.25,
           decay: float = 0.55) -> np.ndarray:
    """Small 'Splosh' reverb: sparse early reflections + short comb tail."""
    x = np.asarray(audio, dtype=np.float64).reshape(-1)
    n = len(x)
    taps = [int(sr * t) for t in (0.013, 0.021, 0.034, 0.047, 0.061)]
    wet = np.zeros(n)
    for i, tap in enumerate(taps):
        if tap < n:
            wet[tap:] += (0.8 ** i) * x[:n - tap]
    d = int(sr * 0.031)
    fb = np.clip(decay, 0.0, 0.9)
    buf = np.zeros(d, dtype=np.float64)
    idx = 0
    z = 0.0
    tail = np.empty(n)
    for i in range(n):
        dl = buf[idx]
        z += 0.45 * (dl - z)
        v = wet[i] + fb * z
        buf[idx] = v
        idx = (idx + 1) % d
        tail[i] = z
    return (1.0 - mix) * x + mix * (wet + tail)


def demo() -> str:
    sr = 22050
    bank = PadPartialBank(sample_rate=sr)
    wav = bank.render_note(freq=110.0, duration=3.0, seed=3)
    print(f"pad note: len={len(wav)} peak={np.max(np.abs(wav)):.3f} "
          f"rms={np.sqrt(np.mean(wav ** 2)):.4f}")
    assert np.all(np.isfinite(wav)) and np.max(np.abs(wav)) > 0.2

    # rebalancing the partials must change the sound
    bank.balance["critters"] = 0.0
    no_critters = bank.render_note(freq=110.0, duration=3.0, seed=3)
    bank.balance["critters"] = 0.45
    with_critters = bank.render_note(freq=110.0, duration=3.0, seed=3)
    print("critters partial changes output:",
          not np.allclose(no_critters, with_critters))
    assert not np.allclose(no_critters, with_critters)

    # the Critters layer is stochastic and microtonal
    cr = Critters(sample_rate=sr, density=3.0)
    a = cr.render(220.0, 2.0, seed=1, sr=sr)
    b = cr.render(220.0, 2.0, seed=2, sr=sr)
    print(f"critters: seed1 rms={np.sqrt(np.mean(a**2)):.4f} "
          f"seed2 rms={np.sqrt(np.mean(b**2)):.4f} "
          f"triggers={len(cr.trigger_times(2.0, seed=1))} "
          f"microtonal_set={cr.microtonal_set}")
    assert not np.allclose(a, b)

    full = bank.render_with_processing(freq=110.0, duration=3.0, seed=5,
                                       cassette_amount=0.5, splosh_mix=0.3,
                                       pump=2)
    print(f"cassette+splosh+pump: peak={np.max(np.abs(full)):.3f} "
          f"finite={np.all(np.isfinite(full))} len={len(full)}")
    assert np.all(np.isfinite(full))
    print("  critter_pad demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
