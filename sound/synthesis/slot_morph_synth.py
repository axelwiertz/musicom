"""Slot-morphing subtractive voice (Currents & Nostalgia style).

Replicates the Unusable Engineering "Currents & Nostalgia" architecture
(synthtopia, 2026-11-11). The instrument's idea is that modulation does not
patch an LFO into a parameter — it stores *whole configurations* in slots and
then sequences or sweeps between them:

  * OSC slot system: up to 8 saved (oscillator waveform + waveform-mixer
    balance + detune) configurations.
  * FILTER slot system: up to 8 saved (cutoff, resonance, drive, type) configs.
  * The two systems run at independent rates and independent patterns
    (step or sweep), and those rates may go into the audio range, where the
    "sequence" becomes a modulation oscillator and the slot crossfade becomes
    timbral sideband generation rather than a stepped change.
  * Parameter locks hold individual fields fixed while the rest morph.

Implementation detail worth noting: a slot step is a hard switch (no
interpolation) while a sweep is a linear crossfade between neighbouring slots;
both are driven by a single phase accumulator per system, so audio-rate
operation needs no special case — you simply let the phase wrap thousands of
times per second.

The oscillators are saw-core with a per-oscillator tolerance spread, matching
the "component tolerance" variation control.
"""

from __future__ import annotations

import numpy as np

TAU = 2.0 * np.pi


def saw_core(phase: np.ndarray, tolerance: float = 0.0) -> np.ndarray:
    """Poly-blep-free saw core: phase ramp with a tolerance-shifted reset.

    ``tolerance`` skews the ramp so two oscillators never align perfectly —
    the audible effect in the real instrument is a slow beating/unison shift
    rather than detune.
    """
    p = (phase * (1.0 + tolerance)) % 1.0
    return 2.0 * p - 1.0


def waveform(kind: str, phase: np.ndarray) -> np.ndarray:
    if kind == "saw":
        return saw_core(phase)
    if kind == "tri":
        return 1.0 - 4.0 * np.abs((phase % 1.0) - 0.5)
    if kind == "pulse":
        return np.where((phase % 1.0) < 0.5, 1.0, -1.0)
    if kind == "square":          # pulse at 25 % duty
        return np.where((phase % 1.0) < 0.25, 1.0, -1.0)
    raise ValueError(f"unknown waveform {kind!r}")


def ladder_lp(x: np.ndarray, cutoff: np.ndarray, resonance: np.ndarray,
              drive: np.ndarray | None = None) -> np.ndarray:
    """4-pole ladder with per-sample cutoff/resonance (needs sample-accurate
    coefficients because the modulation can run at audio rate)."""
    n = len(x)
    y = np.empty(n)
    s = np.zeros(4)
    for i in range(n):
        g = np.tan(np.pi * min(0.45, cutoff[i] / 44100.0))
        G = g / (1.0 + g)
        d = 1.0 if drive is None else drive[i]
        u = np.tanh(x[i] * d)
        # ZDF ladder, feedback from stage 4 output
        k = 4.0 * resonance[i] * G ** 3
        u = (u - k * s[3]) / (1.0 + k)
        for st in range(4):
            v = (u - s[st]) * G
            out = v + s[st]
            s[st] = out + v
            u = out
        y[i] = u
    return y


class SlotSystem:
    """A set of stored configurations with its own rate/pattern/phase."""

    def __init__(self, slots, keys, rate_hz: float = 2.0, pattern: str = "step",
                 crossfade: float = 0.15, direction: int = 1, locked=None):
        self.slots = [dict(s) for s in slots]
        self.keys = list(keys)
        self.rate_hz = float(rate_hz)
        self.pattern = pattern                # 'step' | 'sweep' | 'random'
        self.crossfade = float(crossfade)
        self.direction = direction
        self.locked = set(locked or ())
        self.phase = 0.0
        self.current = 0.0                    # float index into slots
        self.rng = np.random.default_rng(0)

    def advance(self, n_samples: int, sr: int) -> np.ndarray:
        """Return an (n, len(keys)) array of parameter trajectories."""
        n_slots = len(self.slots)
        step = self.rate_hz / sr
        ph = (self.phase + step * np.arange(1, n_samples + 1)) % n_slots
        self.phase = ph[-1]

        if self.pattern == "step":
            idx = np.floor(ph).astype(int)
            blend = np.zeros(n_samples)
        elif self.pattern == "random":
            idx = np.floor(ph).astype(int)
            blend = np.zeros(n_samples)
            order = self.rng.permutation(n_slots)
            idx = np.array([order[i % n_slots] for i in idx])
        else:  # sweep: continuous crossfade, direction respected
            pos = ph if self.direction > 0 else (n_slots - 1 - ph) % n_slots
            idx = np.floor(pos).astype(int) % n_slots
            blend = (pos % 1.0)
            if self.crossfade < 1.0:
                # sharpen the fade into a plateau-then-move motion
                blend = np.clip((blend - (1.0 - self.crossfade)) / self.crossfade,
                                0.0, 1.0)

        nxt = (idx + 1) % n_slots
        out = np.empty((n_samples, len(self.keys)))
        for kidx, key in enumerate(self.keys):
            if key in self.locked:
                out[:, kidx] = float(self.slots[0][key])
                continue
            a = np.array([float(self.slots[i][key]) for i in idx])
            b = np.array([float(self.slots[i][key]) for i in nxt])
            out[:, kidx] = a + (b - a) * blend
        return out


class SlotMorphSynth:
    """Two saw-core oscillators + slot-sequenced oscillator and filter sets."""

    def __init__(self, sr: int = 44100, osc_slots=None, filter_slots=None,
                 osc_rate: float = 3.0, filter_rate: float = 0.7,
                 osc_pattern: str = "sweep", filter_pattern: str = "step",
                 osc_locked=None, filter_locked=None,
                 osc_tolerance: float = 0.004, filter_drive: float = 1.4):
        self.sr = sr
        self.osc_slots = osc_slots or [
            {"wave": 0, "mix": 0.5, "detune": 0.0},
            {"wave": 2, "mix": 0.5, "detune": 7.0},
            {"wave": 1, "mix": 0.2, "detune": -5.0},
            {"wave": 3, "mix": 0.8, "detune": 12.0},
        ]
        self.filter_slots = filter_slots or [
            {"cutoff": 3000.0, "res": 0.15, "drive": 1.2},
            {"cutoff": 900.0, "res": 0.6, "drive": 1.8},
            {"cutoff": 6000.0, "res": 0.05, "drive": 1.0},
            {"cutoff": 1800.0, "res": 0.4, "drive": 2.4},
        ]
        # numeric index per waveform, resolved per sample by nearest integer
        self.wave_names = ["saw", "tri", "pulse", "square"]
        self.osc_sys = SlotSystem(
            [{"wave": self.wave_names[
                int(s["wave"]) % len(self.wave_names)], "mix": s["mix"],
              "detune": s["detune"]} for s in self.osc_slots],
            ["mix", "detune"], rate_hz=osc_rate, pattern=osc_pattern,
            locked=osc_locked)
        self.wave_seq = SlotSystem(
            [{"wave": float(int(s["wave"]) % len(self.wave_names))}
             for s in self.osc_slots],
            ["wave"], rate_hz=osc_rate, pattern=osc_pattern,
            locked=[k for k in (osc_locked or []) if k == "wave"])
        self.flt_sys = SlotSystem(self.filter_slots, ["cutoff", "res", "drive"],
                                  rate_hz=filter_rate, pattern=filter_pattern,
                                  locked=filter_locked)
        self.osc_tolerance = osc_tolerance
        self.filter_drive = filter_drive

    def render(self, f0: float, dur: float, amp: float = 1.0,
               key_scale: float = 1.0) -> np.ndarray:
        """key_scale mimics keyboard-responsive slot rate (higher = faster)."""
        n = max(128, int(dur * self.sr))
        self.osc_sys.rate_hz *= key_scale
        self.wave_seq.rate_hz *= key_scale
        self.flt_sys.rate_hz *= key_scale
        try:
            osc = self.osc_sys.advance(n, self.sr)          # mix, detune
            waves = self.wave_seq.advance(n, self.sr)[:, 0]
            flt = self.flt_sys.advance(n, self.sr)          # cutoff res drive
        finally:
            self.osc_sys.rate_hz /= key_scale
            self.wave_seq.rate_hz /= key_scale
            self.flt_sys.rate_hz /= key_scale

        t = np.arange(n) / self.sr
        p1 = (f0 * t) % 1.0
        p2 = (f0 * 2 ** (osc[:, 1] / 12.0) * t) % 1.0

        sig = np.zeros(n)
        # per-sample waveform selection: a genuine audio-rate timbre switch
        for wi, name in enumerate(self.wave_names):
            mask = np.abs(waves - wi) < 0.5
            if mask.any():
                sig[mask] += (1.0 - osc[mask, 0]) * waveform(name, p1[mask])
                sig[mask] += osc[mask, 0] * waveform(name, p2[mask])
        # component-tolerance variation: second core skewed slightly
        sig = 0.5 * sig + 0.5 * saw_core(p1, self.osc_tolerance)

        cutoff = np.clip(flt[:, 0], 60.0, self.sr * 0.42)
        res = np.clip(flt[:, 1], 0.0, 0.95)
        drive = flt[:, 2] * self.filter_drive
        y = ladder_lp(sig, cutoff, res, drive)

        env = np.exp(-np.linspace(0, 3.2, n))
        y = y * env * amp
        peak = np.abs(y).max()
        return y / peak * 0.9 if peak > 1e-9 else y

    def render_phrase(self, notes, gap: float = 0.02) -> np.ndarray:
        total = sum(d for _, d in notes) + gap * len(notes) + 0.1
        out = np.zeros(int(total * self.sr))
        t = 0.0
        for f, d in notes:
            seg = self.render(f, d)
            i0 = int(t * self.sr)
            out[i0:i0 + len(seg)] += seg[: max(0, len(out) - i0)]
            t += d + gap
        return out


def demo() -> None:
    """Render slot-stepped and audio-rate-swept versions of the same phrase."""
    sr = 44100
    phrase = [(110.0, 0.5), (146.83, 0.5), (164.81, 0.9)]

    stepped = SlotMorphSynth(sr=sr, osc_rate=4.0, osc_pattern="step",
                             filter_rate=4.0, filter_pattern="step")
    a = stepped.render_phrase(phrase)

    swept = SlotMorphSynth(sr=sr, osc_rate=0.5, osc_pattern="sweep",
                           filter_rate=0.25, filter_pattern="sweep")
    b = swept.render_phrase(phrase)

    # audio-rate slot sequencing: rate above 20 Hz turns slots into sidebands
    fast = SlotMorphSynth(sr=sr, osc_rate=120.0, osc_pattern="sweep",
                          filter_rate=40.0, filter_pattern="sweep")
    c = fast.render(110.0, 0.6)

    # parameter lock: cutoff pinned, so the filter trajectory must be flat
    locked = SlotMorphSynth(sr=sr, filter_rate=8.0, filter_pattern="sweep",
                            filter_locked=["cutoff"])
    traj = locked.flt_sys.advance(4096, sr)[:, 0]
    print(f"slot demo: step={len(a)} sweep={len(b)} audio-rate={len(c)} samples")
    print(f"  locked cutoff trajectory: min={traj.min():.1f} max={traj.max():.1f} "
          f"std={traj.std():.4f}")
    print(f"  rms step={np.sqrt((a**2).mean()):.4f} "
          f"sweep={np.sqrt((b**2).mean()):.4f} "
          f"audio-rate={np.sqrt((c**2).mean()):.4f}")

    spec_c = np.abs(np.fft.rfft(c * np.hanning(len(c))))
    f = np.fft.rfftfreq(len(c), 1 / sr)
    centroid = float((spec_c * f).sum() / max(1e-9, spec_c.sum()))
    print(f"  audio-rate slot sweep spectral centroid = {centroid:.0f} Hz "
          f"(sideband-rich, well above the 110 Hz fundamental)")

    assert np.isfinite(a).all() and np.isfinite(b).all() and np.isfinite(c).all()
    assert traj.std() < 1e-6, "locked parameter must not move"
    assert centroid > 400.0
    print("demo OK")


if __name__ == "__main__":
    demo()
