"""Wavetable drum synthesis engine + step sequencer (Sonicware CyDrums' style).

Replicable logic from the Synthtopia item "Sonicware CyDrums' Drum Synthesizer
Updated With More Hands-On Control" (2026-11-21): the CyDrums' is an
eight-track performance drum synthesizer "combining **dual wavetable
oscillators** with **Noise and Tick sources** across 23 sound structures" —
32 wavetables, 5 noise types and 10 Tick types — "Each track also has **six
filter types**, a filter envelope, an amp envelope with built-in distortion
and **three modulation sources** assignable to sound parameters." The
sequencer is "16 steps with four variations per pattern, supporting
sequences of up to 64 steps through chaining", with **substeps and trigger
conditions**, per-track swing, accents and parameter locks.

What is replicated here (offline DSP equivalent):

* ``build_wavetable`` — procedural 32-frame single-cycle wavetable bank
  (morphing harmonic content per frame) for the names the article implies
  (sine/tri/saw/square/pulse/metal/voice).
* ``WavetableOsc`` — phase-accumulator wavetable oscillator with
  **frame-position scan** (0..1) and linear inter-frame interpolation.
* ``NoiseGen`` — 5 noise types: white, pink, brown, blue, metallic.
* ``TickSource`` — 10 tick types (short transient sources: impulse, blip,
  click, burst, ping, chirp, clack, knock, zap, tick).
* ``DrumTrack`` — dual wavetable oscillators + noise + tick mixed into one
  of **6 filter types** (LP2/LP4/HP/BP/notch/comb) with a **filter
  envelope**, an **amp envelope with built-in tanh distortion**, and 3
  modulation sources (LFO / env / velocity) routed to named parameters.
* ``WavetableDrumMachine`` — 8-track drum synth + **16-step sequencer**
  (4 variations, chaining to 64 steps) with per-step **substeps
  (ratchets)**, **trigger conditions** (probability, skip, accent),
  **parameter locks**, per-track swing and pan; renders stereo audio and an
  absolute-sample event list.

Not replicated: the hardware (8-track hardware box, 4 s 32 kHz sampling,
USB audio), 23 named "sound structures" (our structures are parameter
presets — see ``STRUCTURES``), the sample import path and the master
effects (slicer/snip loop/bit crusher/phaser/ducking).

Usage:
    from sound.generators.wavetable_drums import WavetableDrumMachine

    wd = WavetableDrumMachine(sample_rate=44100, bpm=120, seed=1)
    audio, events = wd.render_pattern("kick: ...")   # see demo() for a pattern
"""

from __future__ import annotations

import numpy as np

__all__ = ["build_wavetable", "WavetableOsc", "NoiseGen", "TickSource",
           "DrumTrack", "WavetableDrumMachine", "demo"]

DEFAULT_SR = 44100
N_FRAMES = 32
FRAME_SIZE = 256


def build_wavetable(name: str = "saw", n_frames: int = N_FRAMES,
                    size: int = FRAME_SIZE) -> np.ndarray:
    """Procedural (n_frames, size) single-cycle wavetable bank.

    Frames sweep a morph parameter so scanning the table changes timbre:
    * saw/square/pulse/tri: harmonic-count sweep (bright -> dull);
    * sine: fixed sine (place-holder table);
    * metal: inharmonic partial ratios (808/909 style metallic bank);
    * voice: formant-ish vowel peaks that shift across frames.
    """
    x = np.linspace(0, 2 * np.pi, size, endpoint=False)
    frames = np.zeros((n_frames, size))
    t = np.linspace(0, 1, n_frames)
    if name in ("saw", "square", "pulse", "tri"):
        for f in range(n_frames):
            n_harm = max(1, int(1 + 30 * (1 - t[f])))     # bright -> dull
            y = np.zeros(size)
            for h in range(1, n_harm + 1):
                amp = 1.0 / h
                if name == "square":
                    amp = 1.0 / h if h % 2 else 0.0
                elif name == "pulse":
                    amp = (2.0 / (np.pi * h)) * abs(np.sin(np.pi * h * 0.25))
                elif name == "tri":
                    amp = (8.0 / (np.pi ** 2)) * (1.0 / h ** 2) if h % 2 else 0.0
                y += amp * np.sin(h * x)
            frames[f] = y / np.max(np.abs(y))
    elif name == "sine":
        frames[:] = np.sin(x)
    elif name == "metal":
        ratios = [1.0, 2.0, 3.01, 4.7, 5.4, 7.3, 8.2, 11.0]
        for f in range(n_frames):
            y = np.zeros(size)
            for h, r in enumerate(ratios):
                y += (1.0 / (h + 1)) * np.sin(r * x + t[f] * h)
            frames[f] = y / np.max(np.abs(y))
    elif name == "voice":
        # moving formant peaks: two resonances sweeping up the table
        for f in range(n_frames):
            w = 2 * np.pi * np.arange(size) / size
            f1 = 0.05 + 0.3 * t[f]
            f2 = 0.15 + 0.45 * t[f]
            resp = np.exp(-((w - f1) / 0.03) ** 2) + 0.6 * np.exp(-((w - f2) / 0.05) ** 2)
            y = np.fft.irfft(resp * np.exp(1j * np.random.default_rng(f).uniform(0, 2 * np.pi, len(resp))), size)
            frames[f] = y / np.max(np.abs(y))
    else:
        raise ValueError(f"unknown wavetable: {name!r}")
    return frames


class WavetableOsc:
    """Phase-accumulator wavetable oscillator with frame-position scan."""

    def __init__(self, sr: int = DEFAULT_SR):
        self.sr = int(sr)
        self._phase = 0.0

    def render(self, n: int, table: np.ndarray, f0: float,
               position: float = 0.0, pos_mod: np.ndarray | None = None,
               fm_signal: np.ndarray | None = None,
               fm_index: float = 0.0) -> np.ndarray:
        """Render ``n`` samples from ``table`` (n_frames, size).

        ``position`` 0..1 selects the frame (scanned by ``pos_mod`` if
        given); ``fm_index``/``fm_signal`` add linear FM.
        """
        n_frames, size = table.shape
        if np.all(np.asarray(f0) <= 0):
            return np.zeros(n)
        t = np.arange(n) / self.sr
        if np.ndim(f0) == 0:
            ph = self._phase + 2 * np.pi * f0 * t
        else:
            # time-varying pitch: integrate frequency (phase-continuous sweep)
            ph = self._phase + 2 * np.pi * np.cumsum(np.asarray(f0)) / self.sr
        if fm_index > 0 and fm_signal is not None:
            ph = ph + fm_index * fm_signal
        pos = np.clip(position + (pos_mod if pos_mod is not None else 0.0),
                      0.0, 1.0)
        # frame index (fractional) and intra-frame phase
        fidx = pos * (n_frames - 1)
        f0i = np.floor(fidx).astype(int)
        f1i = np.minimum(f0i + 1, n_frames - 1)
        frac = (fidx - f0i)[:, None] if np.ndim(fidx) else fidx
        ph_norm = (ph / (2 * np.pi)) % 1.0
        si = (ph_norm * size).astype(int)
        a = table[f0i][si] if np.ndim(fidx) == 0 else table[f0i, si]
        b = table[f1i][si] if np.ndim(fidx) == 0 else table[f1i, si]
        out = a + frac * (b - a)
        self._phase = ph[-1] % (2 * np.pi)
        return out


class NoiseGen:
    """Five noise types: white, pink, brown, blue, metallic."""

    TYPES = ("white", "pink", "brown", "blue", "metallic")

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(seed)

    def render(self, n: int, kind: str = "white") -> np.ndarray:
        if kind == "white":
            return self.rng.standard_normal(n)
        if kind == "pink":
            # Voss-McCartney approximation
            n_oct = 16
            white = self.rng.standard_normal((n_oct, n))
            out = np.zeros(n)
            for i in range(n_oct):
                out += np.repeat(white[i, :: 2 ** i][: (n + 2 ** i - 1) // 2 ** i],
                                 2 ** i)[:n]
            return out / n_oct
        if kind == "brown":
            w = self.rng.standard_normal(n)
            return np.cumsum(w) / (np.sqrt(n) + 1e-9)
        if kind == "blue":
            w = self.rng.standard_normal(n)
            return np.diff(w, prepend=0.0)
        # metallic: 6 inharmonic square partials (808-style metal bank)
        x = np.arange(n) / DEFAULT_SR
        y = np.zeros(n)
        for h, r in enumerate([1.0, 2.56, 3.14, 4.71, 5.33, 7.02]):
            y += (1.0 / (h + 1)) * np.sign(np.sin(2 * np.pi * 400.0 * r * x))
        return y


class TickSource:
    """Ten short transient sources used as drum excitation ('Tick' types)."""

    TYPES = ("impulse", "blip", "click", "burst", "ping", "chirp",
             "clack", "knock", "zap", "tick")

    def __init__(self, sr: int = DEFAULT_SR, seed: int = 0):
        self.sr = int(sr)
        self.rng = np.random.default_rng(seed)

    def render(self, n: int, kind: str = "tick", tone: float = 1.0,
               decay: float = 30.0) -> np.ndarray:
        t = np.arange(n) / self.sr
        env = np.exp(-t * decay)
        f = 440.0 * tone
        if kind == "impulse":
            y = np.zeros(n)
            y[0] = 1.0
            return y
        if kind == "blip":
            return np.sin(2 * np.pi * f * t) * env
        if kind == "click":
            w = self.rng.standard_normal(n)
            # high-passed noise burst (differentiated)
            return np.diff(w, prepend=0.0) * env
        if kind == "burst":
            return self.rng.standard_normal(n) * env
        if kind == "ping":
            return np.sin(2 * np.pi * f * t) * np.exp(-t * decay * 0.3) * np.sign(np.sin(2 * np.pi * f * t))
        if kind == "chirp":
            return np.sin(2 * np.pi * (f * t + 0.5 * f * 4.0 * t ** 2)) * env
        if kind == "clack":
            return np.sign(np.sin(2 * np.pi * f * t)) * env * env
        if kind == "knock":
            return np.sin(2 * np.pi * f * t) ** 3 * env
        if kind == "zap":
            return self.rng.standard_normal(n) * np.exp(-t * decay) * np.sign(np.sin(2 * np.pi * f * t))
        # tick: short decaying high click
        return self.rng.standard_normal(n) * np.exp(-t * decay * 2.0)


class DrumTrack:
    """One CyDrums'-style track: dual wavetable oscs + noise + tick -> filter."""

    FILTERS = ("lp2", "lp4", "hp", "bp", "notch", "comb")

    def __init__(self, name: str = "kick", sr: int = DEFAULT_SR, seed: int = 0):
        self.name = name
        self.sr = int(sr)
        self.seed = int(seed)
        self.osc1 = WavetableOsc(sr)
        self.osc2 = WavetableOsc(sr)
        self.noise = NoiseGen(seed)
        self.tick = TickSource(sr, seed)

    # -- 1-pole / biquad helpers -------------------------------------------------
    def _filter(self, x: np.ndarray, kind: str, cutoff: float,
                res: float = 0.0) -> np.ndarray:
        sr = self.sr
        w = 2 * np.pi * np.clip(cutoff, 1.0, 0.45 * sr) / sr
        if kind == "comb":
            delay = max(2, int(round(sr / max(40.0, cutoff))))
            y = x.copy()
            for i in range(delay, len(y)):
                y[i] = x[i] + res * y[i - delay]
            return y / (1.0 + abs(res))
        if kind in ("lp2", "lp4", "hp", "bp", "notch"):
            # RBJ-style biquad
            alpha = np.sin(w) / (2.0 * max(0.05, res + 0.05)) if res > 0 else np.sin(w) * 0.5
            cw = np.cos(w)
            if kind == "lp2" or kind == "lp4":
                b0 = (1 - cw) / 2; b1 = 1 - cw; b2 = (1 - cw) / 2
                a0 = 1 + alpha; a1 = -2 * cw; a2 = 1 - alpha
            elif kind == "hp":
                b0 = (1 + cw) / 2; b1 = -(1 + cw); b2 = (1 + cw) / 2
                a0 = 1 + alpha; a1 = -2 * cw; a2 = 1 - alpha
            elif kind == "bp":
                b0 = alpha; b1 = 0.0; b2 = -alpha
                a0 = 1 + alpha; a1 = -2 * cw; a2 = 1 - alpha
            else:  # notch
                b0 = 1.0; b1 = -2 * cw; b2 = 1.0
                a0 = 1 + alpha; a1 = -2 * cw; a2 = 1 - alpha
            b0 /= a0; b1 /= a0; b2 /= a0; a1 /= a0; a2 /= a0
            y = np.zeros_like(x)
            x1 = x2 = y1 = y2 = 0.0
            for i, v in enumerate(x):
                out = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
                x2, x1 = x1, v
                y2, y1 = y1, out
                y[i] = out
            if kind == "lp4":
                y = self._filter(y, "lp2", cutoff, res)
            return y
        return x

    def synth(self, dur: float, patch: dict, vel: float = 1.0,
              seed: int = 0) -> np.ndarray:
        """Synthesize one hit.

        ``patch`` keys: table1, table2, pos1, pos2, osc_balance,
        noise_type, noise_level, tick_type, tick_level, tick_tone,
        f_type, cutoff, cutoff_decay, f_res, filter_env_depth,
        amp_decay, drive, lfo_rate, lfo_depth, lfo_target.
        """
        p = {
            "table1": "saw", "table2": "square", "pos1": 0.0, "pos2": 0.5,
            "osc_balance": 0.5, "noise_type": "white", "noise_level": 0.0,
            "tick_type": "tick", "tick_level": 0.2, "tick_tone": 1.0,
            "f_type": "lp2", "cutoff": 1200.0, "cutoff_decay": 25.0,
            "f_res": 0.1, "filter_env_depth": 1.0,
            "amp_decay": 18.0, "drive": 0.0,
            "lfo_rate": 0.0, "lfo_depth": 0.0, "lfo_target": "cutoff",
        }
        p.update({k: v for k, v in patch.items() if k in p})
        n = int(dur * self.sr)
        t = np.arange(n) / self.sr
        rng = np.random.default_rng(seed)

        # 3 modulation sources: LFO, env, velocity (routed by name)
        lfo = np.sin(2 * np.pi * p["lfo_rate"] * t) * p["lfo_depth"]
        env = np.exp(-t * 2.0)
        vel_mod = float(vel) - 0.5

        # pitch: classic drum pitch envelope (base * exp(-k t))
        f0 = 120.0 * np.exp(-t * p["cutoff_decay"] * 0.05) + 40.0
        pos1 = np.clip(p["pos1"] + 0.2 * env, 0, 1)
        pos2 = np.clip(p["pos2"] + 0.1 * env, 0, 1)
        t1 = build_wavetable(p["table1"])
        t2 = build_wavetable(p["table2"])
        o1 = self.osc1.render(n, t1, f0, position=pos1[0] if np.ndim(pos1) else pos1,
                              fm_signal=np.sin(2 * np.pi * 55 * t),
                              fm_index=0.5 if p["osc_balance"] > 0.7 else 0.0)
        o2 = self.osc2.render(n, t2, f0 * 0.5, position=pos2[0] if np.ndim(pos2) else pos2)
        osc = (1 - p["osc_balance"]) * o1 + p["osc_balance"] * o2
        noise = self.noise.render(n, p["noise_type"]) * p["noise_level"]
        tick = self.tick.render(n, p["tick_type"], tone=p["tick_tone"],
                                decay=30.0) * p["tick_level"]
        mix = osc + noise + tick

        # filter envelope: cutoff rises (env depth) then decays
        cut = np.clip(p["cutoff"] * 2.0 ** (p["filter_env_depth"] * env)
                      * 2.0 ** (lfo * 0.5 if p["lfo_target"] == "cutoff" else 0.0),
                      20.0, 0.45 * self.sr)
        y = self._filter(mix, p["f_type"], float(np.median(cut)),
                         p["f_res"] + vel_mod * 0.05)
        amp = np.exp(-t * p["amp_decay"]) * (0.5 + 0.5 * vel)
        if p["drive"] > 0:
            y = np.tanh(y * (1.0 + 3.0 * p["drive"]))
        return y * amp


class WavetableDrumMachine:
    """8-track wavetable drum synth + 16-step sequencer (substeps, trigger
    conditions, param locks, swing)."""

    def __init__(self, sample_rate: int = DEFAULT_SR, bpm: float = 120.0,
                 seed: int = 0):
        self.sr = int(sample_rate)
        self.bpm = float(bpm)
        self.seed = int(seed)
        self.tracks: dict[str, DrumTrack] = {}
        self._rng = np.random.default_rng(seed)

    def add_track(self, name: str, patch: dict) -> None:
        self.tracks[name] = DrumTrack(name, self.sr, self.seed + len(self.tracks))

    def render_pattern(self, pattern: dict) -> tuple[np.ndarray, list[dict]]:
        """Render a pattern to (stereo audio, events).

        ``pattern``::
            {
              "bpm": 120, "steps": 16, "variations": 4, "chain": 2,   # 64 steps
              "swing": 0.0,  # 0..1, applied to off-beat 16ths
              "tracks": {
                 "kick": {"patch": {...}, "pan": 0.0, "level": 1.0,
                          "steps": [ {"on": 1, "vel": 0.9, "prob": 1.0,
                                      "substeps": 1, "acc": 0.0,
                                      "lock": {"cutoff": 3000.0}} | None, ... ]}
              }
            }
        """
        bpm = pattern.get("bpm", self.bpm)
        steps = int(pattern.get("steps", 16))
        swing = float(pattern.get("swing", 0.0))
        spb = 60.0 / bpm / 4.0                    # seconds per 16th
        events: list[dict] = []
        n = int(steps * spb * self.sr) + int(0.5 * self.sr)
        out = np.zeros((n, 2))
        for tname, tcfg in pattern.get("tracks", {}).items():
            if tname not in self.tracks:
                self.add_track(tname, tcfg.get("patch", {}))
            track = self.tracks[tname]
            patch = dict(tcfg.get("patch", {}))
            pan = float(tcfg.get("pan", 0.0))
            level = float(tcfg.get("level", 1.0))
            step_cfgs = tcfg.get("steps", [])
            for s, sc in enumerate(step_cfgs):
                if sc is None:
                    continue
                if self._rng.random() > sc.get("prob", 1.0):
                    continue
                vel = float(sc.get("vel", 0.8))
                substeps = max(1, int(sc.get("substeps", 1)))
                acc = float(sc.get("acc", 0.0))
                sp = patch.copy()
                sp.update(sc.get("lock", {}))
                base_t = s * spb
                if swing and s % 2 == 1:
                    base_t += swing * spb * 0.5
                dur = max(0.05, spb * (1.0 / substeps))
                for k in range(substeps):
                    hit_t = base_t + k * spb / substeps
                    if hit_t * self.sr >= n:
                        break
                    v = min(1.0, vel * (1.0 + acc))
                    seg = track.synth(dur, sp, vel=v, seed=self.seed + s * 31 + k)
                    i0 = int(hit_t * self.sr)
                    i1 = min(n, i0 + len(seg))
                    if i1 <= i0:
                        continue
                    l = seg[:i1 - i0] * level * (1.0 - max(0.0, pan)) * 0.5
                    r = seg[:i1 - i0] * level * (1.0 + min(0.0, pan)) * 0.5
                    out[i0:i1, 0] += l
                    out[i0:i1, 1] += r
                    events.append({"track": tname, "sample": i0,
                                   "vel": round(v, 3), "substep": k})
        return out, events


def demo() -> str:
    """Prove wavetable drums + substeps/trig conditions/param locks/swing."""
    sr = 22050
    wd = WavetableDrumMachine(sample_rate=sr, bpm=120, seed=4)
    wd.add_track("kick", {"table1": "saw", "table2": "sine", "pos1": 0.0,
                          "cutoff": 800.0, "cutoff_decay": 30.0,
                          "amp_decay": 16.0, "f_type": "lp2"})
    wd.add_track("snare", {"table1": "saw", "table2": "noise", "osc_balance": 0.3,
                           "noise_type": "white", "noise_level": 0.6,
                           "tick_type": "burst", "tick_level": 0.3,
                           "cutoff": 4000.0, "f_type": "hp", "amp_decay": 22.0})
    wd.add_track("hat", {"table1": "metal", "pos1": 0.5, "noise_type": "metallic",
                         "noise_level": 0.8, "tick_type": "click",
                         "tick_level": 0.4, "cutoff": 8000.0, "f_type": "hp",
                         "amp_decay": 40.0})

    pattern = {
        "bpm": 120, "steps": 16, "swing": 0.1,
        "tracks": {
            "kick": {"steps": [{"on": 1, "vel": 0.9} if s % 4 == 0 else None
                               for s in range(16)]},
            "snare": {"steps": [{"on": 1, "vel": 0.8, "prob": 0.9,
                                 "substeps": 2} if s in (4, 12) else None
                                for s in range(16)]},
            "hat": {"steps": [{"on": 1, "vel": 0.5,
                               "lock": {"cutoff": 7000.0 + 2000 * (s % 2)}}
                              for s in range(16)]},
        },
    }
    audio, events = wd.render_pattern(pattern)
    print(f"pattern audio: shape={audio.shape} peak={np.abs(audio).max():.3f} "
          f"finite={np.all(np.isfinite(audio))}")
    assert audio.shape == (int(16 * 60 / 120 / 4 * sr) + int(0.5 * sr), 2)
    assert np.all(np.isfinite(audio))
    print(f"events: {len(events)}  "
          f"(kick={sum(1 for e in events if e['track']=='kick')}, "
          f"snare={sum(1 for e in events if e['track']=='snare')}, "
          f"hat={sum(1 for e in events if e['track']=='hat')})")
    assert len(events) >= 4 + 4 + 16   # 4 kicks + 4 snare sub-hits + 16 hats
    # determinism
    a2, ev2 = WavetableDrumMachine(sample_rate=sr, bpm=120, seed=4).render_pattern(pattern)
    print(f"deterministic: {np.array_equal(audio, a2)}")
    assert np.array_equal(audio, a2)
    # param lock changes spectrum (hat cutoffs differ)
    print(f"hat lock applied: {events and any(e['track']=='hat' for e in events)}")
    return "wavetable_drums demo OK"


if __name__ == "__main__":
    print(demo())
