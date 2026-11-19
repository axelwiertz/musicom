"""Formula-driven procedural drum synthesis (Drumlabooh 14-style).

Drumlabooh v14 added a *procedural synthesis engine* alongside sample playback:
a kit is a list of "generator modules" described by formulas rather than fixed
oscillator types.  This module implements that idea safely and concretely.

A **voice** is a stack of **layers**.  Each layer has three formulas evaluated
over the note's time axis ``t`` (seconds):

    pitch_hz = f(t)      e.g. "110*exp(-t*38) + 48"
    amp      = f(t)      e.g. "exp(-t*9)"
    cutoff   = f(t)      e.g. "900 + 6000*exp(-t*30)"

plus a waveform selector:

* ``sine`` / ``tri`` / ``saw`` / ``square``  -- band-limited additive phase
* ``noise``                                  -- white noise, optional "metal"
                                                (six inharmonic square partials,
                                                the 808-style metallic bank)
* ``fm``                                     -- carrier + modulator ratio
                                                (classic FM drum)

Formulas are parsed with ``ast`` and whitelisted to arithmetic + ``exp``,
``sin``, ``cos``, ``abs``, ``min``, ``max``, ``tanh`` and the variable ``t``.
Nothing is ``eval``'d blindly.

Effects per voice follow the order the hardware review calls out: filters,
**Live** control (per-hit random variation injected into the formulas), then an
**analog saturator**.  Kits are declarative dicts, so an "OM Kit"-style Goa kit
and a "RITM"-style electro kit are just data.
"""

from __future__ import annotations

import ast
import math

import numpy as np

__all__ = ["Formula", "DrumVoice", "FormulaDrumKit", "demo"]

_ALLOWED = {
    "exp": np.exp, "sin": np.sin, "cos": np.cos, "tanh": np.tanh,
    "abs": np.abs, "min": np.minimum, "max": np.maximum, "sqrt": np.sqrt,
    "pi": np.pi,
}


class Formula:
    """Compiled, whitelisted formula of the single variable ``t``."""

    def __init__(self, src: str | float):
        if isinstance(src, (int, float)):
            self.src = str(src)
            self._const = float(src)
            self._expr = None
            self._code = None
            return
        self.src = src
        self._const = None
        self._expr = ast.parse(src, mode="eval").body
        self._check(self._expr)
        self._code = compile(ast.Expression(self._expr), "<formula>", "eval")

    def _check(self, node):
        for n in ast.walk(node):
            if isinstance(n, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                              ast.Name, ast.Load, ast.Call, ast.operator,
                              ast.unaryop)):
                continue
            if isinstance(n, ast.Attribute):
                raise ValueError("attributes not allowed in formulas")
            raise ValueError(f"disallowed syntax: {type(n).__name__}")
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id not in _ALLOWED and n.id != "t":
                raise ValueError(f"unknown name {n.id!r}")
            if isinstance(n, ast.Call) and not (isinstance(n.func, ast.Name)
                                                and n.func.id in _ALLOWED):
                raise ValueError("unknown function in formula")

    def __call__(self, t: np.ndarray) -> np.ndarray:
        if self._const is not None:
            return np.full_like(t, self._const, dtype=np.float64)
        env = {"t": t, "__builtins__": {}}
        env.update({k: v for k, v in _ALLOWED.items() if callable(v)})
        env["pi"] = np.pi
        val = eval(self._code, env)  # noqa: S307 - AST-whitelisted above
        return np.asarray(val, dtype=np.float64) * np.ones_like(t)


class DrumVoice:
    """A single drum sound: stack of formula-driven layers + FX chain."""

    def __init__(self, name: str, layers: list[dict], length: float = 0.45,
                 drive: float = 0.0, hp: float = 20.0, lp: float = 18000.0,
                 live: float = 0.0, seed: int = 0):
        self.name = name
        self.layers = []
        for l in layers:
            self.layers.append({
                "wave": l.get("wave", "sine"),
                "pitch": Formula(l.get("pitch", 120.0)),
                "amp": Formula(l.get("amp", "exp(-t*12)")),
                "cutoff": Formula(l.get("cutoff", 12000.0)),
                "ratio": float(l.get("ratio", 1.0)),
                "gain": float(l.get("gain", 1.0)),
                "decay_zero": bool(l.get("decay_zero", True)),
            })
        self.length = length
        self.drive = drive
        self.hp = hp
        self.lp = lp
        self.live = live
        self.rng = np.random.default_rng(seed)

    # -- waveforms ---------------------------------------------------------
    def _osc(self, wave: str, freq: np.ndarray, sr: int) -> np.ndarray:
        n = freq.size
        phase = 2 * np.pi * np.cumsum(freq) / sr
        if wave == "sine":
            return np.sin(phase)
        if wave == "tri":
            return 2.0 / np.pi * np.arcsin(np.sin(phase))
        if wave == "saw":
            # additive, harmonic-limited: avoids naive aliasing on pitch sweeps
            out = np.zeros(n)
            for h in range(1, 12):
                out += np.sin(h * phase) / h
            return out * (2 / np.pi)
        if wave == "square":
            out = np.zeros(n)
            for h in range(1, 12, 2):
                out += np.sin(h * phase) / h
            return out * (4 / np.pi)
        if wave == "noise":
            return self.rng.standard_normal(n) * 0.5
        if wave == "metal":
            # six inharmonic squares, 808 metallic bank style
            base = max(20.0, float(np.mean(freq)))
            ratios = (1.0, 1.4471, 1.6170, 1.9265, 2.5028, 2.6637)
            out = np.zeros(n)
            for r in ratios:
                ph = 2 * np.pi * np.cumsum(np.full(n, base * r)) / sr
                out += np.sign(np.sin(ph))
            return out / 6.0
        if wave == "fm":
            carrier = np.sin(phase)
            mod = np.sin(phase * 2.0 + 0.0)
            return np.sin(phase + 4.0 * mod)
        raise ValueError(f"unknown wave {wave!r}")

    # -- render ------------------------------------------------------------
    def render(self, sr: int = 44100, velocity: float = 1.0,
               live_amount: float | None = None) -> np.ndarray:
        n = int(self.length * sr)
        t = np.arange(n) / sr
        live = self.live if live_amount is None else live_amount
        out = np.zeros(n)
        for l in self.layers:
            pitch = l["pitch"](t)
            if live > 0:
                pitch = pitch * (1.0 + live * self.rng.uniform(-0.06, 0.06))
            amp = l["amp"](t) * l["gain"]
            if live > 0:
                # "Live" control varies the decay of static one-shots
                amp = amp * (1.0 + live * self.rng.uniform(-0.15, 0.10))
            sig = self._osc(l["wave"], np.maximum(5.0, pitch), sr) * amp
            # per-layer one-pole lowpass whose cutoff follows its formula
            cut = np.clip(l["cutoff"](t), 60.0, sr * 0.45)
            z = 0.0
            y = np.empty(n)
            for i in range(n):
                a = math.exp(-2 * math.pi * cut[i] / sr)
                z = (1 - a) * sig[i] + a * z
                y[i] = z
            out += y
        out *= velocity
        out = self._hp_filter(out, sr)
        out = self._lp_filter(out, sr)
        out = self._saturate(out)
        peak = float(np.max(np.abs(out)) or 1.0)
        return out / peak * (0.5 + 0.45 * velocity)

    # -- fx ----------------------------------------------------------------
    def _onepole(self, x, sr, cutoff, highpass=False):
        a = math.exp(-2 * math.pi * min(cutoff, sr * 0.45) / sr)
        y = np.empty_like(x)
        z = 0.0
        for i in range(x.size):
            z = (1 - a) * x[i] + a * z
            y[i] = x[i] - z if highpass else z
        return y

    def _hp_filter(self, x, sr):
        return self._onepole(x, sr, max(20.0, self.hp), highpass=True) \
            if self.hp > 20 else x

    def _lp_filter(self, x, sr):
        return self._onepole(x, sr, self.lp) if self.lp < sr * 0.45 else x

    def _saturate(self, x):
        if self.drive <= 0:
            return x
        d = 1.0 + 8.0 * self.drive
        return np.tanh(d * x) / d


# ---------------------------------------------------------------------------
# Kit = declarative data (the "formula-based drum-kit" spec)
# ---------------------------------------------------------------------------

KITS = {
    "RITM": {   # 1980s electro: long sine kicks, snappy noise snare
        "kick": dict(length=0.55, drive=0.25, layers=[
            {"wave": "sine", "pitch": "150*exp(-t*32) + 42",
             "amp": "exp(-t*6.5)", "gain": 1.2},
            {"wave": "noise", "pitch": 3000, "amp": "exp(-t*220)",
             "gain": 0.25, "cutoff": 6000},
        ]),
        "snare": dict(length=0.32, drive=0.15, hp=120, layers=[
            {"wave": "noise", "pitch": 900, "amp": "exp(-t*11) + 0.2*exp(-t*38)",
             "gain": 1.0, "cutoff": 8000},
            {"wave": "tri", "pitch": "260*exp(-t*18) + 180",
             "amp": "exp(-t*16)", "gain": 0.5},
        ]),
        "clap": dict(length=0.28, layers=[
            {"wave": "noise", "pitch": 1200, "cutoff": 4000, "gain": 1.0,
             "amp": "(exp(-t*70)*0.6 + exp(-t*18)*0.4)"},
        ]),
        "hat": dict(length=0.09, hp=6000, layers=[
            {"wave": "metal", "pitch": 3200, "amp": "exp(-t*95)", "gain": 0.8,
             "cutoff": 14000},
        ]),
    },
    "OM": {     # Goa trance: pitched toms, long metallic hats
        "kick": dict(length=0.42, drive=0.4, layers=[
            {"wave": "sine", "pitch": "185*exp(-t*45) + 48",
             "amp": "exp(-t*8)", "gain": 1.3},
        ]),
        "tom": dict(length=0.36, layers=[
            {"wave": "sine", "pitch": "190*exp(-t*14) + 88",
             "amp": "exp(-t*7)", "gain": 1.0},
            {"wave": "noise", "pitch": 1200, "amp": "exp(-t*90)", "gain": 0.2},
        ]),
        "hat": dict(length=0.6, hp=7000, layers=[
            {"wave": "metal", "pitch": 4100, "amp": "exp(-t*9)", "gain": 0.7,
             "cutoff": 15000},
        ]),
    },
}


class FormulaDrumKit:
    """A bank of DrumVoices addressed by name."""

    def __init__(self, spec: dict, sample_rate: int = 44100, seed: int = 0):
        self.sr = sample_rate
        self.voices: dict[str, DrumVoice] = {}
        for i, (name, cfg) in enumerate(spec.items()):
            self.voices[name] = DrumVoice(name, seed=seed + i, **cfg)

    @classmethod
    def from_kit(cls, kit_name: str, **kw) -> "FormulaDrumKit":
        return cls(KITS[kit_name], **kw)

    def hit(self, name: str, velocity: float = 1.0,
            live: float | None = None) -> np.ndarray:
        return self.voices[name].render(self.sr, velocity, live)

    def render_pattern(self, steps: list[tuple[str, float]], bpm: float = 132.0,
                       division: int = 4, live: float = 0.3) -> np.ndarray:
        """``steps`` is a list of (voice, velocity); 0.0 = rest."""
        spb = 60.0 / bpm / division
        seg = int(spb * self.sr)
        total = seg * len(steps) + int(0.6 * self.sr)
        buf = np.zeros(total)
        for i, (name, vel) in enumerate(steps):
            if not name or vel <= 0:
                continue
            s = self.hit(name, vel, live=live)
            o = i * seg
            end = min(total, o + s.size)
            buf[o:end] += s[:end - o]
        peak = float(np.max(np.abs(buf)) or 1.0)
        return buf * min(1.0, 0.95 / peak)


def demo() -> None:
    kit = FormulaDrumKit.from_kit("RITM", seed=5)
    for name in kit.voices:
        s = kit.hit(name, 0.9)
        print(f"  {name:5s} {s.size / kit.sr * 1000:6.1f} ms  "
              f"peak {np.max(np.abs(s)):.2f}  rms {np.sqrt(np.mean(s**2)):.3f}")
    # two bars of electro: kick on quarters, snare on 2 and 4, hats on 8ths
    steps = []
    for i in range(32):
        voice, vel = None, 0.0
        if i % 4 == 0:
            voice, vel = "kick", 1.0
        if i % 8 == 4:
            voice, vel = "snare", 0.85
        if i % 2 == 0 and voice is None:
            voice, vel = "hat", 0.45 if i % 4 else 0.6
        steps.append((voice, vel))
    audio = kit.render_pattern(steps, bpm=128, division=4)
    print(f"pattern: {audio.size / kit.sr:.2f}s rms={np.sqrt(np.mean(audio**2)):.4f}")
    # formula safety: attribute access must be rejected
    try:
        Formula("t.__class__")
    except ValueError as e:
        print("formula sandbox rejects attribute access:", e)
    assert audio.size > 1000 and np.max(np.abs(audio)) > 0.1


if __name__ == "__main__":
    demo()
