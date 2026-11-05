# -*- coding: utf-8 -*-
"""Formant-preserving pitch correction + diatonic harmony stacker —
Klevgrand "Altitude Harmony" style (Sound On Sound news, 2026-10-28).

Replicable logic: the product is a simplified Altitude (pitch-correction /
harmony generator) that retunes a lead vocal and instantly adds up to three
harmony parts above or below it, *without moving the formants*, with a single
Style control that goes from transparent correction to hard-tuned
vocoder-style snap, and four one-knob characters (Clones / Droid / Vibrato /
Tremolo).  What is proprietary is the GUI and the commercial tuning
heuristics; the DSP family is classic.

What this module implements (numpy only, no ML):

- ``estimate_f0``: YIN-style cumulative-mean-normalised-difference pitch
  tracker (first minimum under a threshold, parabolic interpolation),
  frame-wise with voicing confidence from the CMND floor and RMS gate.
- ``PSOLAShifter``: time-domain pitch-synchronous overlap-add.  Grains of
  two local periods are taken around pitch marks and re-laid at a spacing of
  ``period / ratio``, so the fundamental moves while the *spectral envelope*
  (formants) stays where it was — the reason PSOLA is the classic vocal
  shifter.  Duration is preserved: the read position advances at 1x while
  the grain spacing is scaled, so grains are reused/omitted rather than
  resampling the signal (resampling would drag formants with the pitch).
  ``formant_ratio`` deliberately resamples each grain instead, which *does*
  move the envelope (that is the "Droid" character).
- ``PitchCorrector``: per-frame ratio = target/f0, target chosen by scale
  quantisation with a hysteresis band, then one-pole smoothed with a
  ``retune_ms`` time constant.  ``style`` 0 = slow transparent glide,
  style 1 = instant snap to the scale (the hard-tune / vocoder edge comes
  from the zero retune time, exactly as on the hardware).
- ``HarmonyStacker``: up to 3 additional parts placed by *scale degrees*
  (diatonic, so the interval is major or minor as the key requires) above or
  below the lead, each part gain/pan/level, mixed with the lead.
- Characters: ``clones`` (two detuned doubled voices, hard-panned),
  ``droid`` (formant shift down a fixed interval), ``vibrato`` and
  ``tremolo`` (sinusoidal ratio / gain modulation).

Not replicated: the plug-in's tracking/latency modes, the preset "Styles"
content, ARA/AAX integration.

Usage::

    from sound.effects.formant_harmonizer import PitchCorrector, HarmonyStacker
    tuned = PitchCorrector(44100).process(voice, key="C", scale="major")
    parts = HarmonyStacker(44100).process(voice, key="C", scale="major",
                                          intervals=(2, 4, -3))
"""

from __future__ import annotations

import numpy as np

A4 = 440.0
NOTE_TO_PC = {"C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4,
              "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8, "A": 9,
              "A#": 10, "BB": 10, "B": 11}

SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "chromatic": list(range(12)),
}


def hz_to_midi(f: float) -> float:
    return 69.0 + 12.0 * np.log2(max(f, 1e-6) / A4)


def midi_to_hz(m: float) -> float:
    return A4 * 2.0 ** ((m - 69.0) / 12.0)


# --------------------------------------------------------------------------- #
# pitch tracking
# --------------------------------------------------------------------------- #
def estimate_f0(x: np.ndarray, sr: int = 44100, fmin: float = 70.0,
                fmax: float = 900.0, frame: int = 1024, hop: int = 256,
                threshold: float = 0.15) -> dict:
    """YIN-style f0 track.

    Returns dict with ``times``, ``f0`` (Hz, 0.0 where unvoiced), ``conf``
    (1 - CMND minimum) and ``rms``, one entry per analysed frame.
    """
    x = np.asarray(x, dtype=float)
    if x.ndim > 1:
        x = x.mean(axis=0)
    tau_min = max(2, int(sr / fmax))
    tau_max = min(frame // 2, int(sr / fmin))
    n_frames = max(1, 1 + (len(x) - frame) // hop)
    times = np.zeros(n_frames)
    f0 = np.zeros(n_frames)
    conf = np.zeros(n_frames)
    rms = np.zeros(n_frames)
    for k in range(n_frames):
        s = k * hop
        seg = x[s:s + frame]
        if len(seg) < frame:
            seg = np.pad(seg, (0, frame - len(seg)))
        seg = seg - seg.mean()
        rms[k] = float(np.sqrt(np.mean(seg ** 2)))
        times[k] = (s + frame / 2) / sr
        if rms[k] < 1e-4:
            continue
        d = np.zeros(tau_max + 1)
        for tau in range(1, tau_max + 1):
            diff = seg[:frame - tau] - seg[tau:]
            d[tau] = float(np.dot(diff, diff))
        cmnd = np.ones_like(d)
        cum = np.cumsum(d[1:])
        cmnd[1:] = d[1:] * np.arange(1, tau_max + 1) / np.maximum(cum, 1e-12)
        lo, hi = tau_min, tau_max
        idx = None
        for tau in range(lo, hi):
            if cmnd[tau] < threshold and cmnd[tau] <= cmnd[tau + 1]:
                idx = tau
                break
        if idx is None:
            idx = lo + int(np.argmin(cmnd[lo:hi]))
        # parabolic refinement around the chosen lag
        if 1 <= idx < tau_max:
            a, b, c = cmnd[idx - 1], cmnd[idx], cmnd[idx + 1]
            denom = (a - 2 * b + c)
            shift = 0.5 * (a - c) / denom if abs(denom) > 1e-12 else 0.0
            shift = float(np.clip(shift, -1.0, 1.0))
        else:
            shift = 0.0
        lag = idx + shift
        f0[k] = sr / lag if lag > 0 else 0.0
        conf[k] = float(np.clip(1.0 - cmnd[idx], 0.0, 1.0))
        if cmnd[idx] > 0.6:          # clearly unvoiced
            f0[k] = 0.0
    return {"times": times, "f0": f0, "conf": conf, "rms": rms}


def _fill_unvoiced(f0: np.ndarray) -> np.ndarray:
    """Hold the last voiced value through unvoiced gaps (for shifting)."""
    out = f0.copy()
    last = 0.0
    for i in range(len(out)):
        if out[i] > 0:
            last = out[i]
        elif last > 0:
            out[i] = last
    first = next((v for v in out if v > 0), 100.0)
    out[out <= 0] = first
    return out


# --------------------------------------------------------------------------- #
# PSOLA
# --------------------------------------------------------------------------- #
class PSOLAShifter:
    """Pitch-synchronous overlap-add shifter (duration preserving).

    Parameters
    ----------
    sample_rate : int
    frame, hop : int
        Pitch-analysis framing.
    """

    def __init__(self, sample_rate: int = 44100, frame: int = 1024,
                 hop: int = 256):
        self.sr = int(sample_rate)
        self.frame = int(frame)
        self.hop = int(hop)

    def _ratio_curve(self, n: int, times: np.ndarray,
                     ratio: np.ndarray) -> np.ndarray:
        t = np.arange(n) / self.sr
        return np.interp(t, times, ratio)

    def _period_curve(self, n: int, times: np.ndarray, f0: np.ndarray) -> np.ndarray:
        t = np.arange(n) / self.sr
        f = np.interp(t, times, f0)
        return self.sr / np.maximum(f, 20.0)

    def process(self, x: np.ndarray, ratio: np.ndarray | None = None,
                f0_track: dict | None = None, formant_ratio: float = 1.0) -> np.ndarray:
        """Shift ``x`` by a per-frame ratio curve (output pitch = f0 * ratio)."""
        x = np.asarray(x, dtype=float)
        n = len(x)
        if f0_track is None:
            f0_track = estimate_f0(x, self.sr)
        times = f0_track["times"]
        f0 = _fill_unvoiced(f0_track["f0"])
        if ratio is None:
            ratio = np.ones(len(times))
        ratio = np.asarray(ratio, dtype=float)
        if len(ratio) == 1:
            ratio = np.full(len(times), float(ratio[0]))
        r_curve = np.clip(self._ratio_curve(n, times, ratio), 0.25, 4.0)
        p_curve = self._period_curve(n, times, f0)
        f_curve = np.interp(np.arange(n) / self.sr, times, f0)

        # analysis pitch marks at the local period
        marks = [0.0]
        while marks[-1] < n + 2 * self.frame:
            p = p_curve[min(int(marks[-1]), n - 1)]
            marks.append(marks[-1] + max(2.0, p))
        marks = np.asarray(marks)
        mark_p = np.array([p_curve[min(int(m), n - 1)] for m in marks])

        out = np.zeros(n + 4 * self.frame)
        wsum = np.zeros_like(out)
        pos = 0.0
        while pos < n:
            i = int(np.searchsorted(marks, pos))
            i = int(np.clip(i, 0, len(marks) - 1))
            # nearest mark
            if i > 0 and abs(marks[i - 1] - pos) < abs(marks[i] - pos):
                i -= 1
            p = float(mark_p[i])
            half = max(2, int(round(p)))
            c = int(round(marks[i]))
            a0, a1 = max(0, c - half), min(n, c + half)
            if a1 - a0 < 4:
                pos += max(1.0, p / float(r_curve[min(int(pos), n - 1)]))
                continue
            grain = x[a0:a1].copy()
            if formant_ratio != 1.0:
                L = max(4, int(round(len(grain) / formant_ratio)))
                grain = np.interp(np.linspace(0, len(grain) - 1, L),
                                  np.arange(len(grain)), grain)
            grain *= np.hanning(len(grain) + 2)[1:-1]
            s = int(round(pos))
            if s + len(grain) > len(out):
                grain = grain[:len(out) - s]
            out[s:s + len(grain)] += grain
            wsum[s:s + len(grain)] += np.hanning(len(grain) + 2)[1:-1]
            pos += max(1.0, p / float(r_curve[min(int(pos), n - 1)]))
        nz = wsum > 0.35
        out[nz] /= wsum[nz]
        # normalise the level change caused by grain reuse
        e_in = float(np.sqrt(np.mean(x ** 2))) + 1e-9
        e_out = float(np.sqrt(np.mean(out[:n] ** 2))) + 1e-9
        return out[:n] * (e_in / e_out)


# --------------------------------------------------------------------------- #
# correction
# --------------------------------------------------------------------------- #
def _scale_snap(midi: float, key: str, scale: str) -> float:
    pcs = SCALES.get(scale, SCALES["major"])
    root = NOTE_TO_PC.get(key.upper().replace("♯", "#").replace("♭", "B"), 0)
    best, best_d = midi, 1e9
    for octv in (-1, 0, 1):
        for pc in pcs:
            cand = 12 * (np.floor((midi - root) / 12) + octv) + root + pc
            d = abs(cand - midi)
            if d < best_d:
                best, best_d = cand, d
    return best


class PitchCorrector:
    """Altitude-style retune with formants held in place."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)
        self.shifter = PSOLAShifter(sample_rate)

    def process(self, x: np.ndarray, key: str = "C", scale: str = "major",
                style: float = 0.5, retune_ms: float | None = None,
                strength: float = 1.0, formant_ratio: float = 1.0) -> np.ndarray:
        """Retune ``x``.

        style : 0..1
            0 = slow, transparent glide; 1 = instant snap (hard tune).
        retune_ms : float | None
            Overrides the style-derived glide time (style maps 120 ms → 0 ms).
        strength : 0..1
            How far toward the target note the pitch is pulled.
        """
        x = np.asarray(x, dtype=float)
        if x.ndim > 1:
            return np.stack([self.process(ch, key, scale, style, retune_ms,
                                          strength, formant_ratio) for ch in x])
        tr = estimate_f0(x, self.sr)
        voiced = tr["f0"] > 0
        if not voiced.any():
            return x.copy()
        if retune_ms is None:
            retune_ms = 120.0 * (1.0 - float(np.clip(style, 0, 1)))
        # one-pole coefficient for the frame period
        frame_s = (tr["times"][1] - tr["times"][0]) if len(tr["times"]) > 1 else 0.01
        a = float(np.exp(-frame_s / max(retune_ms / 1000.0, 1e-5)))

        midi = np.array([hz_to_midi(f) if f > 0 else 0.0 for f in tr["f0"]])
        # median filter over voiced neighbours to stop note-level jitter
        med = midi.copy()
        for i in range(len(midi)):
            w = [midi[j] for j in range(max(0, i - 2), min(len(midi), i + 3)) if midi[j] > 0]
            if w:
                med[i] = float(np.median(w))
        target = np.array([_scale_snap(m, key, scale) if m > 0 else 0.0 for m in med])
        smooth = target.copy()
        cur = target[0] if target[0] > 0 else 69.0
        for i in range(len(target)):
            if target[i] <= 0:
                smooth[i] = cur
                continue
            cur = a * cur + (1 - a) * target[i]
            smooth[i] = cur
        ratio = np.ones(len(tr["f0"]))
        for i in range(len(ratio)):
            if tr["f0"][i] > 0 and smooth[i] > 0:
                r = 2.0 ** ((smooth[i] - midi[i]) / 12.0)
                ratio[i] = 1.0 + (r - 1.0) * float(np.clip(strength, 0, 1))
        return self.shifter.process(x, ratio, tr, formant_ratio=formant_ratio)


# --------------------------------------------------------------------------- #
# harmony
# --------------------------------------------------------------------------- #
class HarmonyStacker:
    """Up to three diatonic harmony parts above/below a lead vocal."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)
        self.shifter = PSOLAShifter(sample_rate)

    def _degree_target(self, midi: float, key: str, scale: str,
                       degree: int) -> float:
        pcs = SCALES.get(scale, SCALES["major"])
        root = NOTE_TO_PC.get(key.upper().replace("♯", "#").replace("♭", "B"), 0)
        # index of the nearest scale degree, then move by `degree` steps
        best_i, best_d = 0, 1e9
        for o in (-1, 0, 1):
            for i, pc in enumerate(pcs):
                cand = 12 * (np.floor((midi - root) / 12) + o) + root + pc
                d = abs(cand - midi)
                if d < best_d:
                    best_i, best_d = i + 7 * o, d
        n = len(pcs)
        j = best_i + degree
        octv = j // n
        return 12 * (np.floor((midi - root) / 12) + octv) + root + pcs[j % n]

    def process(self, x: np.ndarray, key: str = "C", scale: str = "major",
                intervals: tuple = (2, 4, -3), direction: str = "above",
                pans: tuple | None = None, gains: tuple | None = None,
                style: float = 0.2) -> dict:
        """Return ``{"lead", "parts", "mix", "ratio_curves"}``.

        intervals are *scale degrees* (+2 = a third up, +4 = a fifth up,
        -3 = a fourth below), so the intervals stay diatonic in the key.
        """
        x = np.asarray(x, dtype=float)
        tr = estimate_f0(x, self.sr)
        midi = np.array([hz_to_midi(f) if f > 0 else 0.0 for f in tr["f0"]])
        lead = PitchCorrector(self.sr).process(x, key, scale, style) if style > 0 else x
        parts = []
        curves = []
        for deg in intervals:
            tgt = np.array([self._degree_target(m, key, scale, deg) if m > 0 else 0.0
                            for m in midi])
            ratio = np.ones(len(midi))
            for i in range(len(midi)):
                if midi[i] > 0 and tgt[i] > 0:
                    ratio[i] = 2.0 ** ((tgt[i] - midi[i]) / 12.0)
            ratio = _smooth_ratio(ratio, tr["times"])
            curves.append(ratio)
            parts.append(self.shifter.process(x, ratio, tr))
        pans = pans or tuple(np.linspace(-0.6, 0.6, len(parts)))
        gains = gains or tuple(0.85 / max(1, np.sqrt(len(parts))) for _ in parts)
        mix = np.zeros_like(lead)
        mix += lead
        lw = np.zeros_like(lead)
        rw = np.zeros_like(lead)
        for p, pan, g in zip(parts, pans, gains):
            ang = (float(pan) + 1.0) * np.pi / 4.0
            lw += g * np.cos(ang) * p
            rw += g * np.sin(ang) * p
        mix = np.stack([lead + lw, lead + rw])
        peak = np.abs(mix).max()
        if peak > 0.99:
            mix *= 0.99 / peak
        return {"lead": lead, "parts": parts, "mix": mix,
                "ratio_curves": curves}


def _smooth_ratio(ratio: np.ndarray, times: np.ndarray, ms: float = 25.0) -> np.ndarray:
    if len(times) < 2:
        return ratio
    frame_s = times[1] - times[0]
    a = float(np.exp(-frame_s / max(ms / 1000.0, 1e-5)))
    out = ratio.copy()
    cur = ratio[0] if ratio[0] > 0 else 1.0
    for i in range(len(out)):
        cur = a * cur + (1 - a) * out[i]
        out[i] = cur
    return out


# --------------------------------------------------------------------------- #
# one-knob characters
# --------------------------------------------------------------------------- #
def clone_double(x: np.ndarray, sr: int = 44100, detune_cents: float = 8.0,
                 spread: float = 0.8) -> np.ndarray:
    """'Clones': two detuned doubles, hard-panned (PSOLA, formants kept)."""
    sh = PSOLAShifter(sr)
    up = sh.process(x, np.array([2.0 ** (detune_cents / 1200.0)]))
    dn = sh.process(x, np.array([2.0 ** (-detune_cents / 1200.0)]))
    l = (1 - spread / 2) * x + (spread / 2) * up
    r = (1 - spread / 2) * x + (spread / 2) * dn
    return np.stack([l, r])


def droid(x: np.ndarray, sr: int = 44100, formant_semitones: float = -5.0) -> np.ndarray:
    """'Droid': formant shift with the pitch left alone."""
    return PSOLAShifter(sr).process(
        x, np.ones(1), formant_ratio=2.0 ** (formant_semitones / 12.0))


def vibrato(x: np.ndarray, sr: int = 44100, rate: float = 5.5,
            depth_cents: float = 25.0) -> np.ndarray:
    n = len(x)
    t = np.arange(n) / sr
    curve = 2.0 ** ((depth_cents * np.sin(2 * np.pi * rate * t)) / 1200.0)
    # ratio is per-sample here; feed it as a 1-frame-per-sample track
    tr = estimate_f0(x, sr)
    r_at_frames = np.interp(tr["times"], t, curve)
    return PSOLAShifter(sr).process(x, r_at_frames, tr)


def tremolo(x: np.ndarray, sr: int = 44100, rate: float = 5.0,
            depth: float = 0.5) -> np.ndarray:
    n = len(x)
    t = np.arange(n) / sr
    return x * (1.0 - depth * 0.5 * (1.0 + np.sin(2 * np.pi * rate * t)))


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Correct a flat-ish synthetic vowel and stack a diatonic third+fifth."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    sr = 22050
    t = np.arange(int(sr * 1.2)) / sr
    # glottal-ish pulse train at 213 Hz (between B3 246.9 and A3 220)
    f0_in = 213.0
    ph = 2 * np.pi * f0_in * t
    src = sum((1.0 / h) * np.sin(h * ph) for h in range(1, 25))
    def formant(sig):
        out = np.zeros_like(sig)
        for fc, bw, g in ((700, 130, 1.0), (1220, 160, 0.6)):
            r = np.exp(-np.pi * bw / sr)
            th = 2 * np.pi * fc / sr
            a1, a2 = 2 * r * np.cos(th), -r * r
            y = np.zeros_like(sig)
            for i in range(2, len(sig)):
                y[i] = g * sig[i] + a1 * y[i - 1] + a2 * y[i - 2]
            out += y
        return out / (np.abs(out).max() + 1e-9) * 0.5
    voice = formant(src.astype(float))

    pc = PitchCorrector(sr)
    tuned = pc.process(voice, key="A", scale="major", style=1.0)
    hs = HarmonyStacker(sr)
    res = hs.process(voice, key="A", scale="major", intervals=(2, 4, -3), style=0.0)

    def f0_of(sig):
        tr = estimate_f0(sig, sr)
        v = tr["f0"][tr["f0"] > 0]
        return float(np.median(v)) if len(v) else 0.0

    f_in = f0_of(voice)
    f_tuned = f0_of(tuned)
    print(f"harmonizer demo: lead f0={f_in:.1f} Hz -> corrected {f_tuned:.1f} Hz "
          f"(A major snaps 213 Hz to G#3 207.7, not A3 220)")
    print(f"  parts f0: " + ", ".join(f"{f0_of(p):.1f}" for p in res["parts"])
          + " Hz (expect B3 246.9 / D4 293.7 / D3 146.8 from G#3)")
    print(f"  mix: {res['mix'].shape}, peak={np.abs(res['mix']).max():.3f}")
    assert abs(f_tuned - 207.65) < 2.0, f_tuned
    assert res["mix"].shape[0] == 2 and res["mix"].shape[1] == len(voice)
    assert np.isfinite(res["mix"]).all()
    for name, sig in (("voice", voice), ("tuned", tuned), ("mix", res["mix"])):
        np.save(os.path.join(out_dir, f"harmonizer_{name}.npy"),
                np.asarray(sig, dtype=np.float32))
    print(f"  wrote {out_dir}/harmonizer_*.npy")
    print("demo OK")
    return {"f_in": f_in, "f_tuned": f_tuned}


if __name__ == "__main__":
    demo()
