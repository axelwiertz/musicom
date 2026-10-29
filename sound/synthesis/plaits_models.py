# -*- coding: utf-8 -*-
"""Plaits-style multi-model synthesis voice — Push and Groove MICRONIX style (SP-132).

Replicable logic from the Synthtopia article "Free Micronix Synthesizer Brings
24 Plaits-Based Synthesis Models To Your DAW" (2026-10-28): MICRONIX is a free
monophonic software synthesizer built on the open-source (MIT) DSP code of
Mutable Instruments Plaits — 24 synthesis models covering virtual analog, FM,
wavetable, granular, physical modeling and percussion, each exposing the three
Plaits macro controls (Harmonics, Timbre, Morph) with model-specific labels,
plus OUT/AUX blending, LFOs and a low-pass-gate (LPG) envelope mode modeled on
Plaits (Decay + Color).

What is replicated here (self-contained numpy, offline, clean-room — the real
Plaits C++ is MIT/public but we re-implement rather than copy):

- ``PlaitsVoice``: phase-accumulator voice with 10 representative models from
  the Plaits/MICRONIX model families::

      0  VA        — morphing saw→triangle→square, unison detune (Harmonics),
                     tanh waveshaping (Timbre)
      1  Wavefold  — VA saw through a sine wavefolder (Timbre = fold drive)
      2  FM        — 2-op FM: Morph = carrier:modulator ratio, Timbre = index,
                     Harmonics = modulator feedback
      5  Formant   — vowel-formant bank (A/E/I/O/U tables): Morph selects vowel,
                     Harmonics = formant spread, Timbre = brightness
      6  Harmonic  — additive partial bank: Harmonics = partial count,
                     Timbre = rolloff exponent, Morph = inharmonic stretch
      7  Wavetable — 4 built-in single-cycle tables, Morph crossfades table,
                     Timbre = scan offset, Harmonics = brightness blend
     13  Modal     — struck modal resonator: inharmonic damped partials
                     (Harmonics = ratios, Morph = decay/length)
     14  String    — Karplus-Strong delay-line string with one-pole loop
                     damping; Morph = pick position (brightness)
     20  Drum      — pitch-swept sine kick/tom: Timbre = sweep depth,
                     Harmonics = click, Morph = decay
     23  Noise     — noise percussion (snare/clap): Timbre = noise colour,
                     Harmonics = burst count, Morph = decay

- Macro mapping: every model interprets Harmonics/Timbre/Morph in 0..1 with
  model-specific meanings (as in the real plugin).
- ``LowpassGate``: Plaits-style LPG envelope — exponential decay shaped by a
  vactrol-like one-pole filter that closes over the decay; ``Color`` sets the
  starting cutoff (openness) of the gate.
- ADSR envelope, deterministic seed for noise models, mono output.

Not replicated: the plugin GUI, the full 24-model set (the granular model is
already covered by sound/synthesis/granular.py + scale_locked_granular.py;
speech/bowed/blown/bell families are adjacent to formant_voice.py/bowed.py/
keys_engine.py), and the OUT/AUX blend routing.

Usage:
    from sound.synthesis.plaits_models import PlaitsVoice

    v = PlaitsVoice(sample_rate=44100)
    out = v.render_note(pitch=48, dur=0.8, model=2,
                        harmonics=0.4, timbre=0.6, morph=0.5)
"""

import math
from typing import Optional

import numpy as np

__all__ = ["PlaitsVoice", "LowpassGate", "MODEL_NAMES"]

A440 = 440.0
MODEL_NAMES = {
    0: "va", 1: "wavefold", 2: "fm", 5: "formant", 6: "harmonic",
    7: "wavetable", 13: "modal", 14: "string", 20: "drum", 23: "noise",
}
_NAME_TO_ID = {v: k for k, v in MODEL_NAMES.items()}

# Formant tables (ratios above f0, relative amplitudes) for the 5 cardinal
# vowels — classic formant-frequency shapes (A/E/I/O/U) scaled to the pitch.
VOWEL_TABLES = {
    "A": ((1.00, 1.00), (1.45, 0.55), (3.60, 0.28)),
    "E": ((1.00, 1.00), (2.00, 0.45), (3.10, 0.30)),
    "I": ((1.00, 1.00), (2.70, 0.45), (3.80, 0.35)),
    "O": ((1.00, 1.00), (1.75, 0.55), (3.00, 0.22)),
    "U": ((1.00, 1.00), (2.40, 0.50), (2.90, 0.22)),
}
VOWEL_ORDER = ["A", "E", "I", "O", "U"]


def midi_to_freq(m: int) -> float:
    return A440 * (2.0 ** ((m - 69) / 12.0))


class LowpassGate:
    """Plaits-style low-pass gate: vactrol-like exponential decay through a
    closing one-pole lowpass.  ``decay`` sets the envelope time constant and
    ``color`` sets the starting cutoff (how 'open' the vactrol is at the hit).
    """

    def __init__(self, sample_rate: int = 44100) -> None:
        self.sr = int(sample_rate)

    def apply(self, x: np.ndarray, decay: float = 0.4,
              color: float = 0.5) -> np.ndarray:
        n = len(x)
        out = np.zeros(n)
        lp = 0.0
        # cutoff sweeps from an open start down to a closed floor over decay
        start_cut = 200.0 + 9000.0 * float(np.clip(color, 0.0, 1.0))
        floor_cut = 120.0
        tau = max(0.02, float(decay))  # seconds
        for i in range(n):
            t = i / self.sr
            env = math.exp(-t / tau)
            cut = floor_cut + (start_cut - floor_cut) * env
            a = 1.0 - math.exp(-2.0 * math.pi * cut / self.sr)
            lp += a * (x[i] * env - lp)
            out[i] = lp
        return out


class PlaitsVoice:
    """Phase-accumulator multi-model voice (Plaits/MICRONIX-style).

    Parameters
    ----------
    sample_rate : int
        Output sample rate in Hz.
    seed : int, optional
        Seed for noise models and unison detune (deterministic runs).
    """

    def __init__(self, sample_rate: int = 44100, seed: Optional[int] = None) -> None:
        self.sr = int(sample_rate)
        self._rng = np.random.default_rng(seed)
        # wavetable model: 4 single-cycle tables, 256 samples each
        self._tables = self._build_tables()

    # ---------------------------------------------------------------- tables
    @staticmethod
    def _build_tables():
        n = 256
        t = np.arange(n) / n
        sine = np.sin(2.0 * np.pi * t)
        saw = 2.0 * t - 1.0
        tri = 1.0 - 4.0 * np.abs(t - 0.5)
        sq = np.where(t < 0.5, 1.0, -1.0)
        # 'harmonic' table: sum of 8 partials with 1/k rolloff (formant-ish)
        harm = np.zeros(n)
        for k in range(1, 9):
            harm += (1.0 / k) * np.sin(2.0 * np.pi * k * t)
        harm /= np.max(np.abs(harm))
        return np.stack([sine, saw, tri, harm])

    # ---------------------------------------------------------------- helpers
    def _adsr(self, n: int, attack: float, decay: float, sustain: float,
              release: float) -> np.ndarray:
        env = np.ones(n)
        a_n = max(1, int(attack * self.sr))
        d_n = max(1, int(decay * self.sr))
        r_n = max(1, int(release * self.sr))
        if a_n < n:
            env[:a_n] = np.linspace(0.0, 1.0, a_n)
        a_end = min(a_n, n)
        if d_n > 0:
            d_len = min(d_n, n - a_end)
            if d_len > 0:
                env[a_end:a_end + d_len] = np.linspace(1.0, sustain, d_len)
            env[a_end + d_len:] = sustain
        else:
            env[a_end:] = sustain
        if r_n > 0:
            r_start = max(a_end + d_n, n - r_n)
            if r_start < n:
                env[r_start:] *= np.linspace(1.0, 0.0, n - r_start)
        return env

    # ---------------------------------------------------------------- models
    def _m_va(self, n, f0, harmonics, timbre, morph):
        out = np.zeros(n)
        ph0 = 0.0
        ph1 = 0.0
        detune = float(harmonics) * 14.0  # cents
        f1 = f0 * (2.0 ** (detune / 1200.0))
        drive = 1.0 + 4.0 * float(timbre)
        for i in range(n):
            s0 = 2.0 * ph0 - 1.0
            s1 = 2.0 * ph1 - 1.0
            # morph 0..1: saw -> triangle -> square (piecewise blend)
            if morph < 0.5:
                tri = 1.0 - 4.0 * abs(ph0 - 0.5)
                s = s0 * (1.0 - 2.0 * morph) + tri * (2.0 * morph)
            else:
                m2 = (morph - 0.5) * 2.0
                tri = 1.0 - 4.0 * abs(ph0 - 0.5)
                sq = 1.0 if ph0 < 0.5 else -1.0
                s = tri * (1.0 - m2) + sq * m2
            s2 = 2.0 * ph1 - 1.0
            y = 0.5 * (s + s2)
            out[i] = math.tanh(drive * y) / math.tanh(drive)
            ph0 = (ph0 + f0 / self.sr) % 1.0
            ph1 = (ph1 + f1 / self.sr) % 1.0
        return out

    def _m_wavefold(self, n, f0, harmonics, timbre, morph):
        out = np.zeros(n)
        ph = 0.0
        drive = 1.0 + 6.0 * float(timbre)
        for i in range(n):
            x = 2.0 * ph - 1.0
            folded = (2.0 / math.pi) * math.asin(
                math.sin(math.pi * x * drive))
            y = folded * (1.0 - 0.5 * float(morph)) + x * 0.5 * float(morph)
            out[i] = math.tanh(2.0 * y) / math.tanh(2.0)
            ph = (ph + f0 / self.sr) % 1.0
        return out

    def _m_fm(self, n, f0, harmonics, timbre, morph):
        out = np.zeros(n)
        ratio = 0.25 + 3.75 * float(morph)     # 0.25 .. 4.0
        idx = float(timbre) * (1.0 + 9.0 * float(harmonics))
        fb = 2.0 * float(harmonics)
        cph = 0.0
        mph = 0.0
        prev = 0.0
        for i in range(n):
            m = math.sin(2.0 * math.pi * mph + fb * prev * math.pi)
            y = math.sin(2.0 * math.pi * cph + idx * m * math.pi)
            out[i] = y
            prev = y
            cph = (cph + f0 / self.sr) % 1.0
            mph = (mph + (f0 * ratio) / self.sr) % 1.0
        return out

    def _m_formant(self, n, f0, harmonics, timbre, morph):
        out = np.zeros(n)
        spread = 1.0 + 0.35 * float(harmonics)
        bright = 1.0 - 0.5 * float(timbre)     # rolloff exponent
        pos = float(morph) * (len(VOWEL_ORDER) - 1)
        i0 = int(math.floor(pos))
        i1 = min(i0 + 1, len(VOWEL_ORDER) - 1)
        frac = pos - i0
        tab0 = VOWEL_TABLES[VOWEL_ORDER[i0]]
        tab1 = VOWEL_TABLES[VOWEL_ORDER[i1]]
        phases = [0.0, 0.0, 0.0]
        for i in range(n):
            acc = 0.0
            for k in range(3):
                r0, a0 = tab0[k]
                r1, a1 = tab1[k]
                r = (r0 * (1.0 - frac) + r1 * frac) * spread
                a = (a0 * (1.0 - frac) + a1 * frac) * (1.0 / (k + 1.0)) ** bright
                phases[k] = (phases[k] + (f0 * r) / self.sr) % 1.0
                acc += a * math.sin(2.0 * math.pi * phases[k])
            out[i] = acc / 1.6
        return out

    def _m_harmonic(self, n, f0, harmonics, timbre, morph):
        k_max = 1 + int(round(float(harmonics) * 15.0))    # 1..16 partials
        rolloff = 0.5 + 2.0 * float(timbre)                # 0.5..2.5
        inharm = 0.04 * float(morph)                       # stretch
        phases = np.zeros(k_max)
        out = np.zeros(n)
        for i in range(n):
            acc = 0.0
            for k in range(1, k_max + 1):
                fk = f0 * k * (1.0 + inharm * (k - 1))
                phases[k - 1] = (phases[k - 1] + fk / self.sr) % 1.0
                amp = 1.0 / (k ** rolloff)
                acc += amp * math.sin(2.0 * math.pi * phases[k - 1])
            out[i] = acc
        return out

    def _m_wavetable(self, n, f0, harmonics, timbre, morph):
        out = np.zeros(n)
        pos = float(morph) * 3.0                 # 0..3 across the 4 tables
        t0 = int(math.floor(pos))
        t1 = min(t0 + 1, 3)
        frac = pos - t0
        scan = float(timbre) * 0.5               # intra-cycle scan offset
        bright = float(harmonics)                # blend with derivative
        ph = 0.0
        prev_y = 0.0
        for i in range(n):
            p = (ph + scan) % 1.0
            x = p * 256.0
            xi = int(math.floor(x)) % 256
            xf = x - math.floor(x)
            nxt = (xi + 1) % 256
            y0 = (self._tables[t0, xi] * (1.0 - xf) + self._tables[t0, nxt] * xf)
            y1 = (self._tables[t1, xi] * (1.0 - xf) + self._tables[t1, nxt] * xf)
            y = y0 * (1.0 - frac) + y1 * frac
            d = y - prev_y                        # derivative -> brightness
            out[i] = y * (1.0 - bright) + d * bright * 2.0
            prev_y = y
            ph = (ph + f0 / self.sr) % 1.0
        return out

    def _m_modal(self, n, f0, harmonics, timbre, morph):
        # struck modal resonator: damped inharmonic partials, vectorized
        t = np.arange(n) / self.sr
        ratios = (1.0, 2.01, 2.99, 4.03 + 1.5 * float(harmonics))
        tau = 0.12 + 1.4 * float(morph)          # decay length
        bright = 0.5 + 0.5 * float(timbre)
        out = np.zeros(n)
        for k, r in enumerate(ratios):
            a = (0.5 ** k) * (1.0 + 0.6 * bright)
            out += a * np.exp(-t / (tau * (1.0 + 0.25 * k))) * \
                np.sin(2.0 * np.pi * f0 * r * t)
        return out / 1.8

    def _m_string(self, n, f0, harmonics, timbre, morph):
        # Karplus-Strong delay-line string, BBD-free; pick position = morph
        d = max(2, int(round(self.sr / f0)))
        buf = self._rng.uniform(-1.0, 1.0, d).astype(np.float64)
        damp = 0.30 + 0.68 * float(timbre)       # loop lowpass amount
        gain = 0.985 + 0.014 * float(harmonics)  # decay
        pick = int(round(d * float(morph))) % d
        out = np.zeros(n)
        rp = 0
        lp = 0.0
        for i in range(n):
            x0 = buf[rp]
            x1 = buf[(rp + pick) % d]
            s = 0.5 * (x0 + x1)                  # two-tap averaging
            lp += damp * (s - lp)                # one-pole loop damping
            buf[rp] = lp * gain
            out[i] = s
            rp = (rp + 1) % d
        return out

    def _m_drum(self, n, f0, harmonics, timbre, morph):
        out = np.zeros(n)
        sweep = 1.0 + 2.5 * float(timbre)
        tau = 0.04 + 0.35 * float(morph)
        click = float(harmonics)
        ph = 0.0
        for i in range(n):
            t = i / self.sr
            f_inst = f0 * (1.0 + (sweep - 1.0) * math.exp(-t / 0.03))
            ph = (ph + f_inst / self.sr) % 1.0
            env = math.exp(-t / tau)
            y = math.sin(2.0 * math.pi * ph) * env
            if click > 0.02 and i < int(0.004 * self.sr):
                y += click * 0.3 * self._rng.uniform(-1.0, 1.0) * \
                    (1.0 - i / (0.004 * self.sr))
            out[i] = y
        return out

    def _m_noise(self, n, f0, harmonics, timbre, morph):
        out = np.zeros(n)
        tau = 0.025 + 0.22 * float(morph)
        cut = 400.0 + 9000.0 * float(timbre)     # noise colour
        bursts = 1 if float(harmonics) < 0.5 else 3  # snare vs clap
        a = 1.0 - math.exp(-2.0 * math.pi * cut / self.sr)
        lp = 0.0
        for i in range(n):
            t = i / self.sr
            if bursts > 1:
                # clap: re-triggered bursts within the first third of decay
                bt = t * (3.0 / tau)
                burst_env = math.exp(-(bt % 1.0) * 6.0)
                env = math.exp(-t / tau) * burst_env
            else:
                env = math.exp(-t / tau)
            x = self._rng.uniform(-1.0, 1.0)
            lp += a * (x - lp)
            out[i] = lp * env
        return out

    # ---------------------------------------------------------------- render
    def render_note(self, pitch: int, dur: float, model=0,
                    harmonics: float = 0.5, timbre: float = 0.5,
                    morph: float = 0.5, vel: int = 100,
                    envelope: str = "adsr", lpg_decay: float = 0.4,
                    lpg_color: float = 0.5, attack: float = 0.005,
                    decay: float = 0.2, sustain: float = 0.6,
                    release: float = 0.15) -> np.ndarray:
        """Render one note with the given Plaits model and macro settings.

        Returns a mono float array of length ``int(dur * sample_rate)``.
        ``model`` may be an int (0/1/2/5/6/7/13/14/20/23) or a name string
        (``'va'``, ``'wavefold'``, ``'fm'``, ``'formant'``, ``'harmonic'``,
        ``'wavetable'``, ``'modal'``, ``'string'``, ``'drum'``, ``'noise'``).
        """
        if isinstance(model, str):
            model = _NAME_TO_ID[model]
        n = max(1, int(round(dur * self.sr)))
        f0 = midi_to_freq(pitch)
        h = float(np.clip(harmonics, 0.0, 1.0))
        t = float(np.clip(timbre, 0.0, 1.0))
        m = float(np.clip(morph, 0.0, 1.0))
        raw = {
            0: self._m_va, 1: self._m_wavefold, 2: self._m_fm,
            5: self._m_formant, 6: self._m_harmonic, 7: self._m_wavetable,
            13: self._m_modal, 14: self._m_string, 20: self._m_drum,
            23: self._m_noise,
        }[model](n, f0, h, t, m)
        amp = (vel / 127.0) ** 1.5
        raw = raw * amp
        if envelope == "lpg":
            out = LowpassGate(self.sr).apply(raw, decay=lpg_decay, color=lpg_color)
        else:
            out = raw * self._adsr(n, attack, decay, sustain, release)
        peak = np.max(np.abs(out)) if n else 0.0
        if peak > 1.0:
            out = out / peak * 0.98
        return out


def demo() -> dict:
    """Render one note on every model and report per-model RMS/peak."""
    v = PlaitsVoice(sample_rate=22050, seed=7)
    results = {}
    for mid, name in MODEL_NAMES.items():
        x = v.render_note(pitch=52, dur=0.6, model=mid, vel=110,
                          envelope="lpg", lpg_decay=0.35, lpg_color=0.6)
        rms = float(np.sqrt(np.mean(x ** 2)))
        peak = float(np.max(np.abs(x)))
        results[name] = (len(x), rms, peak)
    return results


if __name__ == "__main__":
    import os
    import tempfile
    import wave

    v = PlaitsVoice(sample_rate=22050, seed=7)
    seq = [
        (36, 0.30, "drum", 0.5, 0.7, 0.3),
        (43, 0.30, "drum", 0.5, 0.3, 0.5),
        (48, 0.35, "fm", 0.4, 0.6, 0.5),
        (55, 0.35, "fm", 0.4, 0.6, 0.5),
        (52, 0.40, "string", 0.5, 0.5, 0.5),
        (56, 0.40, "harmonic", 0.6, 0.4, 0.3),
        (60, 0.40, "harmonic", 0.6, 0.4, 0.3),
        (48, 0.50, "wavetable", 0.5, 0.4, 0.7),
        (52, 0.50, "formant", 0.5, 0.5, 0.8),
        (57, 0.50, "modal", 0.5, 0.5, 0.4),
        (48, 0.45, "noise", 0.7, 0.6, 0.4),
        (50, 0.45, "wavefold", 0.5, 0.5, 0.5),
    ]
    sr = v.sr
    total = int(sum(d * sr for _, d, *_ in seq))
    mix = np.zeros(total)
    pos = 0
    for pitch, d, model, h, t, m in seq:
        note = v.render_note(pitch, d, model=model, harmonics=h,
                             timbre=t, morph=m, vel=112)
        end = pos + len(note)
        mix[pos:end] += note
        pos = end
    peak = float(np.max(np.abs(mix)))
    if peak > 1.0:
        mix = mix / peak * 0.95
    print("sequence samples:", len(mix), "peak:", round(peak, 3))

    res = demo()
    for name, (ln, rms, pk) in res.items():
        print(f"  model {name:<10} len={ln} rms={rms:.4f} peak={pk:.4f}")
    assert all(ln > 0 and pk > 0.001 for ln, rms, pk in res.values()), \
        "some model rendered silence"

    path = os.path.join(tempfile.gettempdir(), "plaits_models_demo.wav")
    pcm = (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    print("wrote", path, os.path.getsize(path), "bytes")
    assert os.path.getsize(path) > 1000, "demo wav too small"
    print("OK — SP-132 plaits_models module works")
