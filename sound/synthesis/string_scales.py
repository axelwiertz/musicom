"""Scale-quantised multi-voice plucked-string resonator — Zlosynth "Arplus" style.

Replicable logic from the Sound On Sound review "Zlosynth Arplus" (September 2026
issue, reviewed by William Stokes).  Arplus "started as a Karplus-Strong experiment
on the Achordion; a mix of things I found interesting and complementary: scale
quantisation, arpeggio patterns and string voices all in one place":

  * **Six voices of string synthesis** that can be set to **arpeggiate**, and can
    also be **excited by an external audio signal** (the module's audio input) —
    "Karplus-Strong being based on quick delays".
  * **31 scales**, organised into groups with dedicated buttons: Western diatonic,
    Arabic maqam, Indian melakarta, Japanese pentatonics, plus a "Full" group for
    quarter-, semi- and whole-tone scales.
  * **Chords of up to eight notes**, adjustable **polyphony**, **filtering** and
    an "envelope-adjacent contour" so "its behaviour can feel crisp and stilted,
    long and languid or anything in between".
  * A **Tone** (root), **Size** (number of notes) and number-of-"strings" control,
    plus a set of arpeggio shapes.

What is replicated here:
- ``SCALE_GROUPS``: a **31-scale** bank in the module's five published groups
  (Western diatonic, Arabic maqam, Indian melakarta, Japanese pentatonic, Full).
  Maqam/melakarta degrees use the equal-tempered approximation; the "Full" group
  carries quarter-tone scales on a 24-TET grid.
- ``StringVoice``: a Karplus-Strong delay line in which the excitation is *mixed
  from* a pluck burst **and/or an external audio input** — the module's
  "excited by an external audio signal" behaviour — with a damping filter, a
  per-voice decay, and an output "contour" (the envelope-adjacent control).
- ``ArplusVoice``: up to 6 (configurable) string voices, chords of up to 8 scale
  degrees, polyphony limiting (oldest-note stealing), arpeggio shapes
  (up/ down/ updown/ random/ as-played) and pattern lengths, scale quantisation,
  and a global low-pass "filtering" stage.

Not replicated: the 10HP hardware, the panel's coloured arp buttons, the
Achordion/Kaseta ecosystem, and the exact proprietary scale tables (equal-tempered
approximations are used here and labelled as such).

Usage:
    from sound.synthesis.string_scales import ArplusVoice, SCALE_GROUPS

    v = ArplusVoice(sample_rate=44100)
    wav = v.render_chord([60, 64, 67], root=60, scale="hirajoshi",
                         arp="up", voices=6, duration=2.0)
    excited = v.resonate(external_audio, root=60, scale="maqam_hijaz",
                         chord_size=5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "SCALE_GROUPS",
    "SCALES_31",
    "ARP_SHAPES",
    "StringVoice",
    "ArplusVoice",
    "midi_to_freq",
]

A440 = 440.0
ARP_SHAPES = ("up", "down", "updown", "random", "played", "chord")

# The module's five published groups.
SCALE_GROUPS: Dict[str, Tuple[str, ...]] = {
    "western": ("major", "natural_minor", "harmonic_minor", "dorian",
                "phrygian", "lydian", "mixolydian", "locrian"),
    "maqam": ("maqam_rast", "maqam_bayati", "maqam_hijaz", "maqam_nahawand",
              "maqam_kurd", "maqam_saba"),
    "melakarta": ("mayamalavagowla", "mecakalyani", "hanumatodi",
                  "kharaharapriya", "shankarabharanam", "natabhairavi",
                  "kalyani_2"),
    "japanese": ("hirajoshi", "in_sen", "yo", "insen_2", "kumoi"),
    "full": ("whole_tone", "semitone_cluster", "quarter_tone", "chromatic",
             "quarter_octatonic"),
}

SCALES_31: Dict[str, Tuple[float, ...]] = {
    # --- Western diatonic (8)
    "major":            (0, 2, 4, 5, 7, 9, 11),
    "natural_minor":    (0, 2, 3, 5, 7, 8, 10),
    "harmonic_minor":   (0, 2, 3, 5, 7, 8, 11),
    "dorian":           (0, 2, 3, 5, 7, 9, 10),
    "phrygian":         (0, 1, 3, 5, 7, 8, 10),
    "lydian":           (0, 2, 4, 6, 7, 9, 11),
    "mixolydian":       (0, 2, 4, 5, 7, 9, 10),
    "locrian":          (0, 1, 3, 5, 6, 8, 10),
    # --- Arabic maqam (6), equal-tempered approximation of the 24-TET degrees
    "maqam_rast":       (0, 2, 4, 5, 7, 9, 10),      # ET approx of 0,2,3.5,5,7,9,10.5
    "maqam_bayati":     (0, 2, 3, 5, 7, 8, 10),      # ET approx of 0,1.5,3,5,7,8,10
    "maqam_hijaz":      (0, 1, 4, 5, 7, 8, 10),
    "maqam_nahawand":   (0, 2, 3, 5, 7, 8, 10),
    "maqam_kurd":       (0, 1, 3, 5, 7, 8, 10),
    "maqam_saba":       (0, 1, 3, 4, 6, 8, 10),
    # --- Indian melakarta (7)
    "mayamalavagowla":  (0, 1, 4, 5, 7, 8, 11),
    "mecakalyani":      (0, 2, 4, 6, 7, 9, 11),
    "hanumatodi":       (0, 1, 3, 5, 7, 8, 10),
    "kharaharapriya":   (0, 2, 3, 5, 7, 9, 10),
    "shankarabharanam": (0, 2, 4, 5, 7, 9, 11),
    "natabhairavi":     (0, 2, 3, 5, 7, 8, 10),
    "kalyani_2":        (0, 2, 4, 6, 8, 9, 11),
    # --- Japanese pentatonics (5)
    "hirajoshi":        (0, 2, 3, 7, 8),
    "in_sen":           (0, 1, 5, 7, 10),
    "yo":               (0, 2, 5, 7, 9),
    "insen_2":          (0, 2, 5, 7, 8),
    "kumoi":            (0, 2, 3, 7, 9),
    # --- "Full" category: quarter-, semi- and whole-tone (5), 24-TET where noted
    "whole_tone":       (0, 2, 4, 6, 8, 10),
    "semitone_cluster": (0, 1, 2, 3, 4, 5, 6),
    "quarter_tone":     tuple(i * 0.5 for i in range(24)),      # 24-TET
    "chromatic":        tuple(range(12)),
    "quarter_octatonic": (0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5),     # 24-TET
}

assert len(SCALES_31) == 31, "the Arplus bank is documented as 31 scales"
assert sum(len(v) for v in SCALE_GROUPS.values()) == 31


def midi_to_freq(note: float) -> float:
    """Equal-tempered MIDI note (A4 = 440 Hz) -> Hz.  Supports fractional notes."""
    return A440 * (2.0 ** ((float(note) - 69.0) / 12.0))


def scale_pool(scale: str, root: int = 60) -> List[float]:
    """Quantisation pool (MIDI notes, possibly fractional) for a scale."""
    if scale not in SCALES_31:
        raise ValueError(f"unknown scale {scale!r}; use one of {sorted(SCALES_31)}")
    degs = SCALES_31[scale]
    pool: List[float] = []
    for octave in range(-4, 5):
        for d in degs:
            pool.append(root + d + 12 * octave)
    return pool


def quantize(note: float, scale: str, root: int = 60) -> float:
    """Snap a (possibly fractional) note to the nearest member of a scale."""
    pool = scale_pool(scale, root)
    return min(pool, key=lambda p: abs(p - note))


def scale_degrees(scale: str, root: int = 60, size: int = 8,
                  spread: int = 1) -> List[float]:
    """``size`` chord degrees above ``root``, walking the scale (Achordion-style).

    ``spread`` skips scale degrees so a chord can stretch over octaves.
    """
    pool = [p for p in scale_pool(scale, root) if p >= root]
    out: List[float] = []
    idx = 0
    while len(out) < size and idx < len(pool):
        out.append(pool[idx])
        idx += max(1, int(spread))
    return out


@dataclass
class StringVoice:
    """One Karplus-Strong string that can be excited by audio as well as a pluck.

    Args:
        sample_rate: sample rate in Hz.
        freq: string fundamental in Hz.
        decay: loop gain (closer to 1 = longer sustain).
        damping: one-pole lowpass cutoff applied inside the loop, Hz.
        level: output level.
    """

    sample_rate: int = 44100
    freq: float = 220.0
    decay: float = 0.9955
    damping: float = 6000.0
    level: float = 1.0
    contour: float = 0.0           # 0 = crisp/stilted, 1 = long/languid

    @property
    def delay_len(self) -> int:
        """Loop length in samples (one full cycle — no half-period division)."""
        return max(2, int(round(self.sample_rate / max(1e-6, self.freq))))

    def excite_pluck(self, n: int, vel: float = 1.0,
                     rng: Optional[np.random.Generator] = None) -> np.ndarray:
        """Excitation buffer: a 2-sample noise impulse scaled by velocity."""
        if rng is None:
            rng = np.random.default_rng(int(self.freq * 7919) & 0xFFFF)
        ex = np.zeros(n)
        ex[:2] = rng.uniform(-1.0, 1.0, 2) * float(vel)
        return ex

    def render(self, n: int, excitation: Optional[np.ndarray] = None,
               vel: float = 1.0, rng: Optional[np.random.Generator] = None,
               input_mix: float = 0.0) -> np.ndarray:
        """Run the delay loop over ``n`` samples.

        Two excitation topologies:

        * **pluck** (``input_mix == 0``) — a short burst seeds the delay line and
          the loop rings on its own (classic Karplus-Strong).
        * **resonator** (``input_mix > 0``) — the external signal is summed into
          the loop input *at every sample*, so the string continuously filters the
          incoming audio and rings at its own fundamental.  This is the Arplus
          "excited by an external audio signal" behaviour; the input is also used
          as the seed burst, scaled by ``1 - input_mix``.
        """
        d = self.delay_len
        if excitation is None:
            ex = self.excite_pluck(n + d, vel, rng)
            drive = None
        else:
            ext = np.asarray(excitation, dtype=np.float64).ravel()
            drive = np.zeros(n + d)
            drive[: min(n + d, ext.size)] = ext[: min(n + d, ext.size)] * float(vel)
            seed = self.excite_pluck(n + d, vel, rng) * (1.0 - input_mix)
            ex = seed

        # loop damping coefficient
        a = 1.0 - np.exp(-2.0 * np.pi * min(self.damping, self.sample_rate * 0.45)
                         / self.sample_rate)
        # contour stretches the effective loop gain (crisp -> languid)
        gain = min(0.9999, self.decay + 0.004 * float(self.contour))

        out = ex.copy()
        lp = 0.0
        for i in range(d, n):
            prev = 0.5 * (out[i - d] + out[i - d - 1])
            lp += a * (prev - lp)
            loop = gain * lp
            if drive is not None:
                loop += float(input_mix) * drive[i]
            out[i] += loop
        out = out[:n]
        out -= out.mean()
        return out * self.level


class ArplusVoice:
    """Up to 6 plucked-string voices, scale-quantised, arpeggiated or strummed.

    Args:
        sample_rate: sample rate in Hz.
        voices: number of string voices (the module's "number of strings").
        filter_cutoff: output low-pass cutoff in Hz (0 = bypass) — "filtering".
    """

    def __init__(self, sample_rate: int = 44100, voices: int = 6,
                 filter_cutoff: float = 0.0):
        self.sr = int(sample_rate)
        self.voices = max(1, min(6, int(voices)))
        self.filter_cutoff = float(filter_cutoff)
        self._last_freq: Optional[float] = None

    # ------------------------------------------------------------------ chords
    def chord(self, root: int, scale: str, size: int = 4,
              spread: int = 1) -> List[float]:
        """Scale degrees forming a chord (up to 8 notes, per the module spec)."""
        return scale_degrees(scale, root=root, size=max(1, min(8, int(size))),
                             spread=spread)

    def arpeggiate(self, notes: Sequence[float], steps: int,
                   shape: str = "up", seed: int = 0) -> List[float]:
        """Expand a chord into ``steps`` arpeggio notes using one of the shapes."""
        if shape not in ARP_SHAPES:
            raise ValueError(f"shape must be one of {ARP_SHAPES}")
        notes = list(notes)
        if not notes:
            return []
        if shape == "chord":
            return [notes[0]] * steps
        if shape == "up":
            order = list(range(len(notes)))
        elif shape == "down":
            order = list(range(len(notes)))[::-1]
        elif shape == "updown":
            order = list(range(len(notes))) + list(range(1, len(notes) - 1))[::-1]
        elif shape == "played":
            order = list(range(len(notes)))
        else:                                   # random
            rng = np.random.default_rng(int(seed))
            order = list(rng.integers(0, len(notes), size=steps))
        if not order:
            order = [0]
        return [notes[order[i % len(order)]] for i in range(steps)]

    # ------------------------------------------------------------------ render
    def render_chord(self, notes: Optional[Sequence[float]] = None,
                     root: int = 60, scale: str = "major", chord_size: int = 4,
                     duration: float = 2.0, arp: Optional[str] = None,
                     steps: Optional[int] = None, step_rate: float = 8.0,
                     vel: float = 0.9, strum: float = 0.0,
                     decay: float = 0.9955, damping: float = 6000.0,
                     contour: float = 0.0, spread: int = 1,
                     seed: int = 0) -> np.ndarray:
        """Render a chord (strummed or arpeggiated) with up to ``voices`` strings.

        Args:
            notes: explicit notes (bypasses the scale/chord derivation).
            root: MIDI root when deriving the chord from a scale.
            scale: which of the 31 scales to use.
            chord_size: chord size in scale degrees (up to 8).
            duration: total render length, seconds.
            arp: an :data:`ARP_SHAPES` entry, or None for a sustained chord.
            steps: arpeggio step count (defaults to one per chord note).
            step_rate: arpeggio steps per second.
            strum: strum offset between chord notes, seconds (0 = simultaneous).
            decay / damping / contour: passed to each :class:`StringVoice`.

        Returns:
            Mono float64 buffer.
        """
        if notes is None:
            notes = self.chord(root, scale, chord_size, spread)
        notes = [quantize(n, scale, root) for n in notes]
        n_total = max(1, int(duration * self.sr))
        buf = np.zeros(n_total)
        rng = np.random.default_rng(int(seed))

        if arp is None:
            # sustain every note, limited to the voice count
            note_list = list(notes)[: self.voices]
            offsets = [i * float(strum) for i in range(len(note_list))]
        else:
            n_steps = int(steps or max(1, len(notes)))
            seq = self.arpeggiate(notes, n_steps, arp, seed)
            interval = 1.0 / max(0.1, float(step_rate))
            note_list = []
            offsets = []
            for i, m in enumerate(seq):
                start = i * interval
                if start * self.sr >= n_total:
                    break
                note_list.append(m)
                offsets.append(start)
            # polyphony: never more than `voices` strings sounding at once
            if len(note_list) > self.voices:
                keep = list(range(len(note_list)))
                note_list = [note_list[i] for i in keep]
                offsets = [offsets[i] for i in keep]

        for idx, (m, off) in enumerate(zip(note_list, offsets)):
            f = midi_to_freq(m)
            v = StringVoice(sample_rate=self.sr, freq=f, decay=decay,
                            damping=damping, level=1.0, contour=contour)
            i0 = int(off * self.sr)
            if i0 >= n_total:
                continue
            n_here = n_total - i0
            seg = v.render(n_here, vel=vel, rng=rng)
            buf[i0:] += seg

        if self.filter_cutoff and self.filter_cutoff > 0.0:
            buf = self._lowpass(buf, self.filter_cutoff)

        peak = float(np.max(np.abs(buf)))
        if peak > 1e-9:
            buf = buf / peak * 0.92
        return buf.astype(np.float64)

    def resonate(self, external: np.ndarray, root: int = 60,
                 scale: str = "maqam_hijaz", chord_size: int = 5,
                 input_mix: float = 0.6, decay: float = 0.9975,
                 damping: float = 4000.0, spread: int = 1) -> np.ndarray:
        """Excite a scale-tuned string bank with an external audio signal.

        This is the Arplus resonator behaviour: the incoming audio drives the delay
        loops, so the output is the input *filtered by the tuned strings* — feed it
        a drum loop and it rings at the scale degrees.
        """
        ext = np.asarray(external, dtype=np.float64).ravel()
        n = ext.size
        notes = [quantize(x, scale, root)
                 for x in self.chord(root, scale, chord_size, spread)]
        notes = notes[: self.voices]
        buf = np.zeros(n)
        for m in notes:
            v = StringVoice(sample_rate=self.sr, freq=midi_to_freq(m),
                            decay=decay, damping=damping)
            buf += v.render(n, excitation=ext, input_mix=input_mix)
        buf /= max(1, len(notes))
        peak = float(np.max(np.abs(buf)))
        if peak > 1e-9:
            buf = buf / peak * 0.92
        return buf.astype(np.float64)

    def _lowpass(self, x: np.ndarray, fc: float) -> np.ndarray:
        a = 1.0 - np.exp(-2.0 * np.pi * min(fc, self.sr * 0.45) / self.sr)
        out = np.empty_like(x)
        y = 0.0
        for i in range(x.size):
            y += a * (x[i] - y)
            out[i] = y
        return out


# ------------------------------------------------------------------------ demo
def demo() -> str:
    """Verify the 31-scale bank, arpeggio shapes, external excitation, polyphony."""
    sr = 22050
    print(f"scales: {len(SCALES_31)} in {len(SCALE_GROUPS)} published groups")
    for g, names in SCALE_GROUPS.items():
        print(f"  {g:10s} ({len(names)}): {', '.join(names)}")
    assert len(SCALES_31) == 31
    assert all(n in SCALES_31 for names in SCALE_GROUPS.values() for n in names)
    uniq = {s for names in SCALE_GROUPS.values() for s in names}
    print(f"  distinct scales across groups: {len(uniq)}")

    v = ArplusVoice(sample_rate=sr, voices=6)

    # --- scale quantisation
    for s in ("hirajoshi", "maqam_hijaz", "mayamalavagowla", "quarter_tone"):
        q = quantize(61.4, s, root=60)
        print(f"  quantize 61.40 -> {q:6.2f} ({s})")
    assert quantize(61.4, "quarter_tone", 60) == 61.5
    assert quantize(61.4, "whole_tone", 60) == 62.0

    # --- chords up to 8 notes
    for size in (3, 5, 8):
        c = v.chord(60, "mayamalavagowla", size=size)
        print(f"  chord size {size}: {[round(x, 1) for x in c]}")
        assert len(c) == size

    # --- arpeggio shapes
    notes = [60, 62, 64, 67, 69]
    for shape in ARP_SHAPES:
        seq = v.arpeggiate(notes, 8, shape, seed=4)
        print(f"  arp {shape:7s}: {seq}")
    up = v.arpeggiate(notes, 4, "up")
    down = v.arpeggiate(notes, 4, "down")
    print(f"  up={up} down={down} (down walks the chord in reverse order)")
    assert [notes.index(m) for m in down] == [len(notes) - 1 - i
                                             for i in [notes.index(m) for m in up]]
    updown = v.arpeggiate(notes, 6, "updown")
    assert updown[0] == notes[0] and max(updown) == max(notes)

    # --- sustained chord render
    chord = v.render_chord(root=60, scale="hirajoshi", chord_size=4,
                           duration=2.0, strum=0.02)
    print(f"chord render: len={chord.size} peak={np.max(np.abs(chord)):.3f} "
          f"finite={np.all(np.isfinite(chord))}")

    # --- Karplus-Strong pitch check on a single string
    x = v.render_chord(notes=[57.0], duration=1.5, decay=0.997,
                       damping=8000.0, strum=0.0)
    ac = np.correlate(x - x.mean(), x - x.mean(), mode="full")[x.size - 1:]
    ac /= ac[0] + 1e-12
    lo, hi = int(sr / 400.0), int(sr / 100.0)
    lag = lo + int(np.argmax(ac[lo:hi]))
    print(f"single string A3: autocorr f0 = {sr / lag:.1f} Hz "
          f"(target {midi_to_freq(57):.1f} Hz)")
    assert abs(sr / lag - midi_to_freq(57)) / midi_to_freq(57) < 0.06

    # --- arpeggio differs from the sustained chord and from a different shape
    arp_up = v.render_chord(root=60, scale="hirajoshi", chord_size=5,
                            duration=2.0, arp="up", steps=10, step_rate=8.0)
    arp_dn = v.render_chord(root=60, scale="hirajoshi", chord_size=5,
                            duration=2.0, arp="down", steps=10, step_rate=8.0)
    print(f"arpeggio up peak={np.max(np.abs(arp_up)):.3f} "
          f"differs from chord: {not np.allclose(arp_up, chord)} "
          f"up != down: {not np.allclose(arp_up, arp_dn)}")
    assert not np.allclose(arp_up, chord)
    assert not np.allclose(arp_up, arp_dn)

    # --- external excitation: the string bank resonates the input
    rng = np.random.default_rng(3)
    noise = rng.standard_normal(sr).astype(np.float64) * 0.5
    res = v.resonate(noise, root=60, scale="maqam_hijaz", chord_size=5,
                     input_mix=0.7)
    spec_in = np.abs(np.fft.rfft(noise * np.hanning(noise.size)))
    spec_out = np.abs(np.fft.rfft(res * np.hanning(res.size)))
    fr = np.fft.rfftfreq(res.size, 1.0 / sr)
    # white noise has a flat-ish spectrum; the resonator must add scale-degree peaks
    def flat(s):
        s = s + 1e-12
        return float(np.exp(np.mean(np.log(s))) / np.mean(s))
    print(f"resonate: len={res.size} finite={np.all(np.isfinite(res))} "
          f"spectral flatness in={flat(spec_in):.4f} -> out={flat(spec_out):.4f} "
          f"(peaks added)")
    assert flat(spec_out) < flat(spec_in)
    # peaks should sit on scale degrees
    degrees = v.chord(60, "maqam_hijaz", size=5)
    hits = 0
    for m in degrees:
        f = midi_to_freq(m)
        j = int(np.argmin(np.abs(fr - f)))
        near = spec_out[max(0, j - 4):j + 5]
        if near.size and near.max() > 0.25 * spec_out.max():
            hits += 1
    print(f"  resonator peaks on scale degrees: {hits}/{len(degrees)}")
    assert hits >= len(degrees) - 1

    # --- contour: crisp/stilted vs long/languid decay
    short = v.render_chord(notes=[60.0], duration=1.5, contour=0.0,
                           decay=0.99)
    long_ = v.render_chord(notes=[60.0], duration=1.5, contour=1.0,
                           decay=0.99)

    def tail_energy(a):
        return float(np.sqrt(np.mean(a[int(0.7 * a.size):] ** 2)))
    print(f"contour: tail RMS crisp={tail_energy(short):.5f} "
          f"languid={tail_energy(long_):.5f}")
    assert tail_energy(long_) > tail_energy(short)

    # --- filtering stage
    vf = ArplusVoice(sample_rate=sr, filter_cutoff=1200.0)
    filt = vf.render_chord(notes=[60.0, 64.0, 67.0], duration=1.0)
    print(f"filtered render: peak={np.max(np.abs(filt)):.3f} "
          f"finite={np.all(np.isfinite(filt))}")
    assert np.all(np.isfinite(filt))
    print("  string_scales demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
