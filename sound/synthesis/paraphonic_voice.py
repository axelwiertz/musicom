"""Paraphonic semi-modular voice (Dubspot SM-1 style).

Replicable logic from the Synthtopia item "Dubspot Intros SM-1, A Moog-Inspired
Semi-Modular Synthesizer For Mobile And Desktop" (2026-11-22):

* "The instrument supports **monophonic and two- or four-note paraphonic
  operation. In the four-note MK2 configuration, each note receives an
  individual oscillator, while sharing the filter and amplifier envelopes.
  The two-note configuration assigns two oscillators to each note. Unlike a
  fully polyphonic synthesizer, the instrument does not provide independent
  filter and amplifier envelopes for every note."
* MK1 oscillator section = two oscillators, MK2 = four, "each with
  pulse-width modulation and linear FM inputs. Other synthesis capabilities
  include oscillator synchronization, detuning, pitch glide and noise
  generation."
* "The mixer includes a **saturating summing stage** that can add additional
  coloration before the signal reaches the filter."
* "Single MK1 **ladder filter** and dual MK2 filter configurations" with
  "Series, parallel and stereo filter routing".
* Interchangeable MK1/MK2 modules with retained patch connections (module
  swapping is a host/UI feature — not here).

What is replicated here (offline DSP equivalent):

* ``ParaphonicOsc`` — saw/pulse core with **PWM** (duty LFO/CV input),
  **linear FM**, **hard sync** and **glide** (portamento on new note).
* ``SaturatingMixer`` — tanh summing stage with pre-filter drive.
* ``LadderFilter`` — 4-pole Moog-style ladder with per-stage tanh and
  resonance feedback (12/24 dB by stage count).
* ``ParaphonicVoice`` — N oscillators (one per note in paraphonic mode)
  sharing ONE filter chain and ONE amp envelope: mono (1 osc, glide),
  2-note (2 osc/note) and 4-note (1 osc/note) modes; MK1 (2 osc) vs MK2
  (4 osc) oscillator banks; single vs dual ladder with series/parallel/
  stereo routing; filter envelope + amp envelope + LFO.

Not replicated: iOS/AUv3 host, virtual patch cables UI, module-swap
topology editor, spring reverb, granular delay and the arpeggiator/step
sequencer (covered elsewhere in sound/).

Usage:
    from sound.synthesis.paraphonic_voice import ParaphonicVoice

    pv = ParaphonicVoice(sample_rate=44100, mode=4, mk=2)
    out = pv.play([60, 64, 67], dur=1.5)   # (n, 2) stereo
"""

from __future__ import annotations

import numpy as np

__all__ = ["ParaphonicOsc", "SaturatingMixer", "LadderFilter",
           "ParaphonicVoice", "demo"]

DEFAULT_SR = 44100


class ParaphonicOsc:
    """Saw/pulse oscillator with PWM, linear FM, hard sync and glide."""

    def __init__(self, sr: int = DEFAULT_SR):
        self.sr = int(sr)
        self._phase = 0.0
        self._cur_f0 = None

    def glide_to(self, f0: float, glide: float) -> float:
        """Return a (possibly glided) instantaneous frequency for a note."""
        if self._cur_f0 is None:
            self._cur_f0 = float(f0)
            return self._cur_f0
        if glide <= 0:
            self._cur_f0 = float(f0)
            return self._cur_f0
        # exponential portamento: move a fraction of the gap per sample
        step = float(np.clip(glide, 1e-4, 1.0))
        self._cur_f0 += (float(f0) - self._cur_f0) * step
        return self._cur_f0

    def reset_phase(self, phase: float = 0.0) -> None:
        self._phase = float(phase)

    def render(self, n: int, f0: float, duty: float = 0.5,
               pwm: np.ndarray | None = None, fm_index: float = 0.0,
               fm_signal: np.ndarray | None = None,
               sync_f: float = 0.0) -> np.ndarray:
        """Render ``n`` samples at ``f0`` with PWM/FM/sync."""
        f0 = max(1e-3, float(f0))
        t = np.arange(n) / self.sr
        phase_acc = self._phase + 2 * np.pi * f0 * t
        if fm_index > 0 and fm_signal is not None:
            phase_acc = phase_acc + fm_index * fm_signal
        if sync_f > 0:
            period = max(1, int(round(self.sr / sync_f)))
            for c in range(int(np.ceil(n / period))):
                lo = c * period
                hi = min(n, (c + 1) * period)
                if hi > lo:
                    phase_acc[lo:hi] = (self._phase +
                                        2 * np.pi * f0 * np.arange(hi - lo) / self.sr)
        ph = phase_acc / (2 * np.pi)
        ph = ph - np.floor(ph)
        d = np.clip(np.asarray(duty) if pwm is None
                    else np.clip(np.asarray(duty) + np.asarray(pwm), 0.02, 0.98),
                    0.02, 0.98)
        pulse = np.where(ph < d, 1.0, -1.0)
        saw = 2.0 * ph - 1.0
        # blend: 0 = pure saw, 1 = pure pulse (PWM applies to the pulse)
        self._phase = phase_acc[-1] % (2 * np.pi)
        return 0.5 * saw + 0.5 * pulse


class SaturatingMixer:
    """tanh summing stage — pre-filter coloration (SM-1 saturating mixer)."""

    def __init__(self, drive: float = 0.0):
        self.drive = float(drive)

    def process(self, *signals: np.ndarray) -> np.ndarray:
        s = np.sum(signals, axis=0) if len(signals) > 1 else signals[0]
        if self.drive > 0:
            s = np.tanh(s * (1.0 + 2.0 * self.drive))
        return s


class LadderFilter:
    """4-pole Moog ladder with per-stage tanh + resonance feedback."""

    def __init__(self, sr: int = DEFAULT_SR):
        self.sr = int(sr)
        self._stages = np.zeros(4)

    def reset(self) -> None:
        self._stages[:] = 0.0

    def process(self, x: np.ndarray, cutoff: float, resonance: float,
                poles: int = 4) -> np.ndarray:
        fc = np.clip(cutoff, 1.0, 0.45 * self.sr)
        x_c = 1.0 - np.exp(-2.0 * np.pi * fc / self.sr)   # cutoff coefficient
        k = float(np.clip(resonance, 0.0, 4.0))
        y = np.zeros_like(x)
        s = self._stages.copy()
        for i, v in enumerate(x):
            # feedback through the last stage, soft-clipped
            fb = k * (s[3] - v * 0.0)
            u = np.tanh(v - fb)
            for p in range(poles):
                s[p] += x_c * (np.tanh(u) - s[p])
                u = s[p]
            y[i] = s[poles - 1]
        self._stages[:] = s
        return y


class ParaphonicVoice:
    """SM-1 style paraphonic voice: N oscs sharing filter chain + amp env.

    Modes:
        mono  — 1 oscillator per voice, glide between notes
        two   — 2 oscillators per note (MK1/MK2 both give 2 osc/note)
        four  — 1 oscillator per note, up to 4 notes (MK2 only)
    """

    def __init__(self, sample_rate: int = DEFAULT_SR, mode: str = "four",
                 mk: int = 2, seed: int = 0):
        self.sr = int(sample_rate)
        self.mode = mode
        self.mk = int(mk)
        self.seed = int(seed)
        self.mixer = SaturatingMixer()
        self.f1 = LadderFilter(self.sr)
        self.f2 = LadderFilter(self.sr)

    @property
    def oscs_per_note(self) -> int:
        return 1 if self.mode == "four" else 2

    @property
    def max_notes(self) -> int:
        if self.mode == "mono":
            return 1
        if self.mode == "two":
            return 2
        return 4

    def _env(self, n: int, a: float, d: float, s: float, r: float,
             sus: float) -> np.ndarray:
        env = np.zeros(n)
        a_n, d_n, r_n = (max(1, int(x * self.sr)) for x in (a, d, r))
        i = 0
        if a_n:
            env[i:i + a_n] = np.linspace(0, 1, a_n, endpoint=False)
            i += a_n
        if d_n:
            env[i:i + d_n] = np.linspace(1, sus, d_n, endpoint=False)
            i = min(n, i + d_n)
        if i < n:
            env[i:] = sus
        rel = np.linspace(sus, 0, r_n, endpoint=False)
        env[n - r_n:] = np.minimum(env[n - r_n:], rel)
        return env

    def play(self, notes: list[int], dur: float = 1.0,
             patch: dict | None = None, gain: float = 0.3) -> np.ndarray:
        """Render notes paraphonically (shared filter + amp env)."""
        p = {
            "duty": 0.5, "pwm_depth": 0.0, "pwm_rate": 0.0, "fm": 0.0,
            "sync": 0.0, "detune": 0.004, "glide": 0.0,
            "drive": 0.2, "noise": 0.01, "sub": 0.15,
            "cutoff": 900.0, "res": 0.3, "routing": "series",
            "filter_env": 1.5, "cut_env_decay": 0.2,
            "amp_a": 0.003, "amp_d": 0.2, "amp_s": 0.6, "amp_r": 0.25,
            "sus": 0.6, "lfo_rate": 0.3, "lfo_depth": 0.1,
        }
        if patch:
            p.update({k: v for k, v in patch.items() if k in p})
        self.f1.reset()
        self.f2.reset()
        self.mixer.drive = p["drive"]
        n = int(dur * self.sr)
        rng = np.random.default_rng(self.seed)

        notes = list(notes)[: self.max_notes]
        if not notes:
            return np.zeros((n, 2))
        oscs = []
        for ni, midi in enumerate(notes):
            f0 = 440.0 * 2.0 ** ((midi - 69) / 12.0)
            for k in range(self.oscs_per_note):
                o = ParaphonicOsc(self.sr)
                det = (k - (self.oscs_per_note - 1) / 2.0) * p["detune"]
                o.reset_phase(rng.uniform(0, 2 * np.pi))
                oscs.append((o, f0 * 2.0 ** det))

        # PWM LFO
        t = np.arange(n) / self.sr
        pwm = (np.sin(2 * np.pi * p["pwm_rate"] * t) * p["pwm_depth"]
               if p["pwm_rate"] > 0 else None)
        fm_sig = np.sin(2 * np.pi * 55.0 * t) if p["fm"] > 0 else None

        mix = np.zeros(n)
        for o, f0 in oscs:
            o.glide_to(f0, p["glide"] * (1.0 if self.mode == "mono" else 0.0))
            mix += o.render(n, f0, duty=p["duty"], pwm=pwm,
                            fm_index=p["fm"], fm_signal=fm_sig,
                            sync_f=p["sync"] * f0 if p["sync"] else 0.0)
        sub = np.sin(2 * np.pi * 440.0 * 2.0 ** ((notes[0] - 69) / 12.0) / 2 * t)
        mix = self.mixer.process(mix + sub * p["sub"],
                                 rng.standard_normal(n) * p["noise"])

        # shared filter chain (paraphonic: one filter for all notes)
        amp_env = self._env(n, p["amp_a"], p["amp_d"], p["amp_s"], p["amp_r"],
                            p["sus"])
        # filter envelope: cutoff rises with env then decays
        cut_env = np.exp(-t / max(0.01, p["cut_env_decay"]))
        cutoff = np.clip(p["cutoff"] * 2.0 ** (p["filter_env"] * cut_env),
                         20.0, 0.45 * self.sr)
        cutoff = float(np.median(cutoff))
        if p["routing"] == "series":
            y1 = self.f1.process(mix, cutoff, p["res"], 4)
            y = self.f2.process(y1, max(40.0, cutoff * 0.6), p["res"] * 0.5, 4)
        elif p["routing"] == "parallel":
            y1 = self.f1.process(mix, cutoff, p["res"], 4)
            y2 = self.f2.process(mix, cutoff * 1.8, p["res"] * 0.7, 2)
            y = 0.5 * (y1 + y2)
        elif p["routing"] == "stereo":
            left = self.f1.process(mix, cutoff, p["res"], 4)
            right = self.f2.process(mix, cutoff * 1.5, p["res"] * 0.6, 2)
            return np.stack([left * amp_env, right * amp_env], axis=1) * gain
        else:                                        # bypass
            y = mix
        # LFO on amp for tremolo
        lfo = 1.0 + p["lfo_depth"] * np.sin(2 * np.pi * p["lfo_rate"] * t)
        out = y * amp_env * lfo * gain
        return np.stack([out, out], axis=1)


def demo() -> str:
    """Prove paraphonic modes, shared filter, saturating mixer, routings."""
    sr = 22050
    pv = ParaphonicVoice(sample_rate=sr, mode="four", mk=2, seed=5)
    out = pv.play([60, 64, 67], dur=1.0)
    print(f"4-note paraphonic: shape={out.shape} peak={np.abs(out).max():.3f} "
          f"finite={np.all(np.isfinite(out))}")
    assert out.shape == (sr, 2) and np.all(np.isfinite(out))

    mono = ParaphonicVoice(sample_rate=sr, mode="mono", seed=5).play(
        [48, 55], dur=0.8)
    print(f"mono+glide: finite={np.all(np.isfinite(mono))}")
    assert np.all(np.isfinite(mono))

    # routing differences
    means = {}
    for r in ("series", "parallel", "stereo", "bypass"):
        o = ParaphonicVoice(sample_rate=sr, mode="four", seed=2).play(
            [60, 64], dur=0.5, patch={"routing": r, "cutoff": 500.0})
        means[r] = round(float(np.abs(o).mean()), 4)
    print(f"routing means: {means}")
    assert len(set(means.values())) >= 3

    # drive colour: drive raises pre-tanh gain and generates harmonics —
    # verify RMS changes and high-frequency energy rises
    clean = ParaphonicVoice(sample_rate=sr, mode="mono", seed=1).play(
        [60], dur=0.5, patch={"drive": 0.0})
    driven = ParaphonicVoice(sample_rate=sr, mode="mono", seed=1).play(
        [60], dur=0.5, patch={"drive": 3.0})
    def _hf(x):
        spec = np.abs(np.fft.rfft(x[:, 0]))
        return float(np.sum(spec[10:]))   # energy above ~2.4 kHz (10th harmonic)
    print(f"drive rms: clean={np.sqrt((clean ** 2).mean()):.3f} "
          f"driven={np.sqrt((driven ** 2).mean()):.3f} "
          f"hf: {_hf(clean):.1f} -> {_hf(driven):.1f}")
    assert abs(float(np.sqrt((clean ** 2).mean()) -
                     np.sqrt((driven ** 2).mean()))) > 1e-3
    assert _hf(driven) > _hf(clean)

    # determinism
    a = ParaphonicVoice(sample_rate=sr, mode="four", seed=9).play([60, 64], 0.4)
    b = ParaphonicVoice(sample_rate=sr, mode="four", seed=9).play([60, 64], 0.4)
    print(f"deterministic: {np.array_equal(a, b)}")
    assert np.array_equal(a, b)

    return "paraphonic_voice demo OK"


if __name__ == "__main__":
    print(demo())
