# -*- coding: utf-8 -*-
"""OP-1 "Keys" engine — tine / reed / clav models + chord & scale mode.

Source: Synthtopia 2026-10-24, "Teenage Engineering OP-1 Mod Gives It new
Synth Engine, Chords, Effects & More" — Justin Joe's free alternate firmware
for the original OP-1 (built on firmware 246) adds:

  "A Keys synth engine (tine, reed and clav), Chord mode and scales,
   Piano-roll sequencer that records chords ..."

What is replicated here — the three key models, as real physical/instrument
models (the firmware flashing, UI and sequencer are not):

- ``tine``  — Rhodes-style modal tine: inharmonic partials
  (1, 2.0, 3.01, 4.2, 5.4, 6.27) with partial-dependent decay (upper partials
  die first), a short noise "bark" on attack, and a gentle pitch droop.
- ``reed``  — Wurlitzer-style free reed: band-limited pulse excitation driven
  through an asymmetric reed nonlinearity, then a resonant resonance peak at
  ~3.5× f0, giving the buzzy, hollow reed tone.
- ``clav``  — Clavinet-style struck string: Karplus-Strong delay line with a
  two-stage averaging loop filter (bright, stiff string) plus a pickup comb
  filter that notches harmonics at the plucking/ pickup distance.

Plus **chord mode**: a note can be expanded to a diatonic chord in a chosen
key/scale, matching "Chord mode and scales".

Not replicated: firmware 246 patch, the six new effects, the piano-roll
sequencer (use ``sound/generators/poly_arp_seq.py`` for step recording).

Usage:
    from sound.synthesis.keys_engine import KeysEngine
    ke = KeysEngine(sample_rate=44100)
    note = ke.play("tine", midi=60, dur=1.2, velocity=0.9)
    chord = ke.play_chord("reed", root=57, quality="min7", key="F", dur=1.5)
"""

from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np

__all__ = ["KeysEngine", "MODELS", "SCALES", "CHORDS", "chord_notes"]

MODELS = ("tine", "reed", "clav")

# major-scale semitone sets for Chord mode / scale quantising
SCALES: Dict[str, tuple] = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "pentatonic": (0, 2, 4, 7, 9),
}

CHORDS = {
    "maj": (0, 4, 7), "min": (0, 3, 7), "dim": (0, 3, 6),
    "aug": (0, 4, 8), "sus4": (0, 5, 7), "maj7": (0, 4, 7, 11),
    "min7": (0, 3, 7, 10), "dom7": (0, 4, 7, 10), "min9": (0, 3, 7, 10, 14),
    "add9": (0, 4, 7, 14),
}
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
A440 = 440.0


def _hz(midi: float) -> float:
    return A440 * 2.0 ** ((midi - 69.0) / 12.0)


def _key_pc(key: str) -> int:
    k = key.strip().upper().replace("♯", "#").replace("♭", "B")
    if k in NOTE_NAMES:
        return NOTE_NAMES.index(k)
    raise ValueError(f"unknown key {key!r}")


def chord_notes(root: int, quality: str = "maj", key: str = "C",
                scale: str = "major") -> List[int]:
    """Diatonic chord: root snapped to the key/scale, then the chord tones."""
    pcs = SCALES.get(scale.lower(), SCALES["major"])
    kpc = _key_pc(key)
    # snap the root down to the nearest scale tone
    rel = (root - kpc) % 12
    while rel not in pcs:
        root -= 1
        rel = (root - kpc) % 12
    ivs = CHORDS.get(quality.lower(), CHORDS["maj"])
    notes = [root + i for i in ivs]
    # keep chord tones inside the scale where the quality allows it
    return [n for n in notes if (n - kpc) % 12 in pcs or len(notes) <= 3]


class KeysEngine:
    """Three key-instrument models with chord/scale expansion."""

    def __init__(self, sample_rate: int = 44100, seed: int = 0):
        self.sr = int(sample_rate)
        self.rng = np.random.default_rng(seed)

    # -- models ------------------------------------------------------------
    def _tine(self, f0: float, n: int, vel: float,
              params: Dict) -> np.ndarray:
        sr = self.sr
        t = np.arange(n) / sr
        ratios = (1.0, 2.0, 3.01, 4.2, 5.4, 6.27)
        decays = (3.2, 2.1, 1.4, 0.9, 0.55, 0.32)
        amps = (1.0, 0.55, 0.42, 0.28, 0.18, 0.12)
        bark = float(params.get("bark", 0.35))
        bell = float(params.get("bell", 0.6))
        droop = 1.0 + 0.004 * np.exp(-t / 0.05)   # small pitch droop
        out = np.zeros(n)
        for r, d, a in zip(ratios, decays, amps):
            g = a * (bell if r > 4 else 1.0)
            out += g * np.sin(2 * np.pi * f0 * r * t * droop) * \
                np.exp(-t / (d * 0.35))
        # hammer "bark": short filtered noise transient
        burst = self.rng.uniform(-1, 1, n) * np.exp(-t / 0.004)
        burst = np.convolve(burst, np.ones(6) / 6, "same")
        out += bark * burst * vel
        return out * np.minimum(1.0, 2.2 * vel)

    def _reed(self, f0: float, n: int, vel: float,
              params: Dict) -> np.ndarray:
        sr = self.sr
        t = np.arange(n) / sr
        nh = max(1, int(min(40, (sr * 0.45) / max(f0, 1.0))))
        pulse = np.zeros(n)
        for k in range(1, nh + 1):
            pulse += np.sin(2 * np.pi * f0 * k * t) / k
        pulse /= max(1e-9, np.max(np.abs(pulse)))
        # asymmetric reed curve -> strong odd harmonics + buzz
        drive = 1.5 + 4.0 * float(params.get("bite", 0.6))
        reed = np.tanh(drive * (pulse - 0.25 * pulse ** 2))
        # resonant peak ~3.5x f0 (the reed's body formant)
        res_f = min(f0 * 3.5, sr * 0.45)
        w0 = 2 * np.pi * res_f / sr
        r = 0.985
        b0 = (1 - r) * np.sqrt(1 - 2 * r * np.cos(2 * w0) + r * r)
        y = np.zeros(n)
        y1 = y2 = 0.0
        for i, v in enumerate(reed):
            yi = b0 * v + 2 * r * np.cos(w0) * y1 - r * r * y2
            y2, y1 = y1, yi
            y[i] = yi
        body = 0.6 * reed + 1.2 * y
        env = np.exp(-t / 1.1)
        attack = np.minimum(1.0, t / 0.004)
        return body * env * attack * np.minimum(1.0, 1.8 * vel)

    def _clav(self, f0: float, n: int, vel: float,
              params: Dict) -> np.ndarray:
        sr = self.sr
        stiffness = float(params.get("stiffness", 0.55))
        D = max(2, int(round(sr / max(f0, 1e-6))))
        buf = self.rng.uniform(-1, 1, D)
        # pick-up position comb on the excitation (pluck near the bridge)
        k = max(1, int(D * 0.18))
        buf = buf - 0.8 * np.roll(buf, k)
        out = np.zeros(n)
        gain = 0.990 + 0.008 * (1.0 - stiffness)
        prev = 0.0
        for i in range(n):
            cur = buf[i % D]
            out[i] = cur
            # two-stage averaging = brighter, stiffer string
            filt = 0.5 * (cur + prev)
            filt = 0.5 * (filt + buf[(i - 1) % D])
            buf[i % D] = gain * filt
            prev = cur
        # magnetic pickup comb (notch every ~D/0.18 samples)
        out = out - 0.5 * np.roll(out, max(1, int(D * 0.18)))
        env = np.exp(-np.arange(n) / (sr * 0.55))
        attack = np.minimum(1.0, np.arange(n) / (0.002 * sr))
        return out * env * attack * np.minimum(1.0, 2.0 * vel)

    def play(self, model: str, midi: int = 60, dur: float = 1.0,
             velocity: float = 0.9, params: Dict = None) -> np.ndarray:
        """Render one note of the tine/reed/clav model."""
        if model not in MODELS:
            raise ValueError(f"unknown model {model!r}; choose from {MODELS}")
        sr = self.sr
        f0 = _hz(midi)
        n = int(sr * (dur + 0.25))
        p = params or {}
        if model == "tine":
            y = self._tine(f0, n, velocity, p)
        elif model == "reed":
            y = self._reed(f0, n, velocity, p)
        else:
            y = self._clav(f0, n, velocity, p)
        tail = np.exp(-np.maximum(0, np.arange(n) / sr - dur) / 0.05)
        y *= tail
        peak = np.max(np.abs(y))
        return (y / peak * 0.9).astype(np.float32) if peak > 1e-9 else y

    def play_chord(self, model: str, root: int = 60, quality: str = "maj",
                   key: str = "C", scale: str = "major", dur: float = 1.5,
                   velocity: float = 0.8, spread: float = 0.0) -> np.ndarray:
        """Chord mode: expand a note to a diatonic chord (optionally strummed)."""
        notes = chord_notes(root, quality, key, scale)
        total = int(self.sr * (dur + 0.5))
        out = np.zeros(total)
        for j, m in enumerate(notes):
            v = self.play(model, m, dur, velocity * (1 - 0.04 * j))
            off = int(spread * j * self.sr)
            end = min(total, off + len(v))
            if end > off:
                out[off:end] += v[:end - off]
        peak = np.max(np.abs(out))
        return (out / peak * 0.9).astype(np.float32) if peak > 1e-9 else out

    def quantize_to_scale(self, midi: int, key: str = "C",
                          scale: str = "major") -> int:
        """Snap a MIDI note to the nearest tone of key/scale (Chord mode)."""
        pcs = SCALES.get(scale.lower(), SCALES["major"])
        kpc = _key_pc(key)
        best = min(range(-6, 7),
                   key=lambda d: (abs(d), d) and ((midi + d - kpc) % 12) in pcs)
        for d in sorted(range(-6, 7), key=abs):
            if (midi + d - kpc) % 12 in pcs:
                return midi + d
        return midi


def _centroid(x: np.ndarray, sr: int) -> float:
    s = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    return float((s * f).sum() / max(s.sum(), 1e-12))


def _decay_time(x: np.ndarray, sr: int) -> float:
    env = np.abs(x)
    k = max(1, int(0.01 * sr))
    env = np.convolve(env, np.ones(k) / k, "same")
    idx = np.where(env > 0.1 * env.max())[0]
    return float(idx[-1] / sr) if len(idx) else 0.0


def demo() -> str:
    sr = 22050
    ke = KeysEngine(sample_rate=sr, seed=5)
    rows = []
    for m in MODELS:
        y = ke.play(m, midi=60, dur=1.0, velocity=0.9)
        rows.append(f"{m:5s} len={len(y)/sr:.2f}s centroid={_centroid(y, sr):6.0f}Hz "
                    f"t10={_decay_time(y, sr):.2f}s")
    chord = ke.play_chord("tine", root=57, quality="min7", key="F", dur=1.5,
                          spread=0.012)
    print_notes = chord_notes(57, "min7", "F", "major")
    names = [f"{NOTE_NAMES[n % 12]}{n // 12 - 1}" for n in print_notes]
    f0 = _hz(print_notes[0])
    spec = np.abs(np.fft.rfft(chord * np.hanning(len(chord))))
    freqs = np.fft.rfftfreq(len(chord), 1.0 / sr)
    # verify the root fundamental is actually present in the chord spectrum
    bin0 = int(round(f0 / (freqs[1] - freqs[0])))
    band = spec[max(0, bin0 - 3):bin0 + 4].max()
    floor = np.median(spec) + 1e-12
    assert band > 20 * floor, f"root missing: {band:.1e} vs floor {floor:.1e}"
    assert all(ke.quantize_to_scale(n, "F", "major") == n
               for n in print_notes), "chord tones must be in key"
    return ("models=" + ",".join(MODELS) + "\n  " + "\n  ".join(rows) +
            f"\n  chord Fmin7 = {' '.join(names)} (root {f0:.1f}Hz, "
            f"root-band/median = {band / floor:.0f}x)")


if __name__ == "__main__":
    print(demo())
