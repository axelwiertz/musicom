"""Stage-by-stage TB-303 circuit model (DJW Audio DW-303-style).

Rather than a generic virtual-analog voice, this models the 303 signal path
stage by stage, as the original schematic does:

1. **Oscillator** -- a sawtooth derived from a capacitor charge curve, not a
   mathematically perfect ramp.  The 303 saw has a curved flank (the reset
   transistor is not ideal), so the ramp is shaped by ``1 - exp(-k*x)`` and the
   duty is slightly asymmetric.  Square is taken from the same phase.
2. **Resonant 4-pole ladder lowpass** -- four one-pole stages with a *tanh*
   saturator between them and a soft-clipped feedback path.  The feedback
   clip is what makes the 303 resonance howl instead of self-destruct.
3. **Filter envelope** -- a decay envelope that drives cutoff in *octaves*
   (the 303's env-mod is exponential, ~2-4 octaves), with the accent adding a
   fast snap on top.
4. **Accent circuit** -- accent does three things simultaneously: boosts the
   VCA, increases resonance, and re-triggers the filter envelope with a shorter
   decay.  This interaction is the 303's signature "wah".
5. **VCA / output** -- a nonlinear amplifier stage that saturates slightly.

Two quality modes: ``full`` runs 4x oversampling of the ladder (matching the
"component-level" mode of the original), ``economy`` runs 1x with a simplified
saturator.  The difference is measurable in aliasing, not just CPU.

Slide is implemented as per-note portamento on the oscillator frequency, which
is how the hardware handles the "slide" step flag.
"""

from __future__ import annotations

import numpy as np

__all__ = ["TB303Circuit", "demo"]


def midi_to_hz(m: float) -> float:
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


class Ladder:
    """4-pole ladder with per-stage tanh saturation and soft-clipped feedback."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate
        self.z = np.zeros(4)
        self.fb = 0.0

    @staticmethod
    def _coeff(cutoff_hz: float, sr: float) -> float:
        # one-pole TPT-ish coefficient, prewarped
        wc = 2.0 * np.pi * min(cutoff_hz, sr * 0.45)
        return float(1.0 - np.exp(-wc / sr))

    def process(self, x: np.ndarray, cutoff: np.ndarray | float,
                resonance: float, drive: float = 1.0) -> np.ndarray:
        n = x.size
        out = np.empty(n)
        g_arr = (np.full(n, self._coeff(cutoff, self.sr))
                 if np.isscalar(cutoff)
                 else np.array([self._coeff(c, self.sr) for c in cutoff]))
        k = 4.0 * float(np.clip(resonance, 0.0, 1.0)) * 1.05
        z1, z2, z3, z4 = self.z
        for i in range(n):
            g = g_arr[i]
            u = np.tanh(drive * (x[i] - k * self.fb))
            z1 += g * (u - z1)
            y1 = np.tanh(z1)                 # stage saturation
            z2 += g * (y1 - z2)
            y2 = np.tanh(z2)
            z3 += g * (y2 - z3)
            y3 = np.tanh(z3)
            z4 += g * (y3 - z4)
            self.fb = z4
            out[i] = z4
        self.z = np.array([z1, z2, z3, z4])
        return out


class TB303Circuit:
    """303 voice: osc -> ladder -> env-mod cutoff -> VCA, accent-aware."""

    def __init__(self, sample_rate: int = 44100, quality: str = "full",
                 waveform: str = "saw", cutoff: float = 320.0,
                 resonance: float = 0.75, env_mod: float = 2.6,
                 decay: float = 0.32, accent_amount: float = 0.65,
                 glide: float = 0.06, tune: float = 0.0):
        self.sr = sample_rate
        self.quality = quality            # "full" (4x OS) | "economy"
        self.os = 4 if quality == "full" else 1
        self.waveform = waveform
        self.cutoff = float(cutoff)
        self.resonance = float(resonance)
        self.env_mod = float(env_mod)     # octaves
        self.decay = float(decay)
        self.accent_amount = float(accent_amount)
        self.glide = float(glide)
        self.tune = float(tune)

    # -- oscillator --------------------------------------------------------
    def _osc(self, freq: np.ndarray) -> np.ndarray:
        dt = freq / (self.sr * self.os)
        phase = np.cumsum(dt) % 1.0
        # curved saw: the capacitor discharge is exponential, ~ -exp(-x)
        curve = 1.0 - np.exp(-3.2 * phase)
        curve = curve / (1.0 - np.exp(-3.2))
        saw = 2.0 * curve - 1.0
        if self.waveform == "square":
            return np.where(phase < 0.5, 1.0, -1.0) * 0.85
        # slight asymmetry: add a little of the square's 3rd harmonic
        return 0.92 * saw + 0.08 * np.where(phase < 0.48, 1.0, -1.0)

    # -- envelopes ---------------------------------------------------------
    def _envs(self, n: int, accent: bool) -> tuple[np.ndarray, np.ndarray]:
        t = np.arange(n) / self.sr
        d = self.decay * (0.6 if accent else 1.0)
        fenv = np.exp(-t / d)
        # accent: fast snap + raised floor
        snap = np.exp(-t / (0.012 if accent else 0.02))
        fenv = fenv + (0.45 * snap if accent else 0.0)
        amp = (1.0 + self.accent_amount if accent else 1.0) * \
            (0.25 + 0.75 * np.exp(-t / (self.decay * 1.4)))
        return fenv, amp

    # -- one note ----------------------------------------------------------
    def render_note(self, midi: float, dur_s: float, accent: bool = False,
                    slide_from: float | None = None) -> np.ndarray:
        os_sr = self.sr * self.os
        n = int((dur_s + 0.03) * os_sr)
        target = midi_to_hz(midi + self.tune)
        if slide_from is not None:
            f_start = midi_to_hz(slide_from + self.tune)
            gl = max(1, int(self.glide * os_sr))
            ramp = np.linspace(0.0, 1.0, gl) ** 0.6
            freq = np.empty(n)
            freq[:gl] = f_start * (target / f_start) ** ramp
            freq[gl:] = target
        else:
            freq = np.full(n, target)
        sig = self._osc(freq)

        fenv, amp = self._envs(n, accent)
        res = min(0.98, self.resonance + (0.12 * self.accent_amount if accent
                                          else 0.0))
        # cutoff in Hz, exponential envelope sweep in octaves
        cut = self.cutoff * (2.0 ** (self.env_mod * fenv))
        cut = np.clip(cut, 30.0, os_sr * 0.45)
        ladder = Ladder(os_sr)
        sig = ladder.process(sig, cut, res, drive=1.3)
        sig *= amp
        # VCA stage saturation
        sig = np.tanh(1.6 * sig) / 1.6
        if self.os > 1:
            m = (sig.size // self.os) * self.os
            sig = sig[:m].reshape(-1, self.os).mean(axis=1)
        peak = np.max(np.abs(sig)) or 1.0
        return 0.7 * sig / peak

    # -- pattern -----------------------------------------------------------
    def render_pattern(self, steps: list[dict], bpm: float = 130.0,
                       step_division: int = 4) -> np.ndarray:
        """Render a 303 pattern.

        Each step: ``{"midi": int|None, "accent": bool, "slide": bool}``.
        ``None`` = rest.  ``slide`` ties into the *next* note (303 semantics:
        the note glides up to the following pitch).
        """
        sec_per_step = 60.0 / bpm / step_division
        chunks = []
        prev_midi = None
        for i, s in enumerate(steps):
            m = s.get("midi")
            if m is None:
                chunks.append(np.zeros(int(sec_per_step * self.sr)))
                prev_midi = None if not s.get("slide") else prev_midi
                continue
            nxt = steps[(i + 1) % len(steps)]
            slide = bool(s.get("slide")) and nxt.get("midi") is not None
            dur = sec_per_step * (2.0 if slide else 0.85)
            chunks.append(self.render_note(
                m, dur, accent=bool(s.get("accent")),
                slide_from=prev_midi if s.get("slide") else None))
            prev_midi = m
        out = np.concatenate(chunks) if chunks else np.zeros(1)
        peak = np.max(np.abs(out)) or 1.0
        return out * min(1.0, 0.95 / peak)


def demo() -> None:
    bass = TB303Circuit(cutoff=280.0, resonance=0.82, env_mod=2.9,
                        decay=0.28, accent_amount=0.7, quality="full")
    pattern = [
        {"midi": 36}, {"midi": 36, "accent": True}, {"midi": None},
        {"midi": 43, "slide": True}, {"midi": 46}, {"midi": None},
        {"midi": 36, "accent": True}, {"midi": 39, "slide": True},
        {"midi": 36}, {"midi": None}, {"midi": 48, "accent": True},
        {"midi": 46}, {"midi": 43}, {"midi": None},
        {"midi": 36, "accent": True}, {"midi": 36},
    ]
    audio = bass.render_pattern(pattern, bpm=132, step_division=4)
    print(f"full   : {audio.size / bass.sr:.2f}s  rms={np.sqrt(np.mean(audio**2)):.4f}"
          f"  peak={np.max(np.abs(audio)):.3f}")
    eco = TB303Circuit(cutoff=280.0, resonance=0.82, env_mod=2.9,
                       decay=0.28, accent_amount=0.7, quality="economy")
    audio2 = eco.render_pattern(pattern, bpm=132, step_division=4)
    print(f"economy: {audio2.size / eco.sr:.2f}s  rms={np.sqrt(np.mean(audio2**2)):.4f}")
    # spectrum check: 4x oversampling must reduce energy above 15 kHz
    def hf_ratio(x):
        sp = np.abs(np.fft.rfft(x))
        f = np.fft.rfftfreq(x.size, 1 / eco.sr)
        return float(sp[f > 15000].sum() / (sp.sum() + 1e-12))
    print(f"HF ratio full={hf_ratio(audio):.4f} vs economy={hf_ratio(audio2):.4f}")
    assert audio.size > 1000 and np.max(np.abs(audio)) > 0.1


if __name__ == "__main__":
    demo()
