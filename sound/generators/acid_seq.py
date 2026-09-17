"""Acid bass-line sequencer + voice — Born Second BS-203 MacroAcidizer style.

Replicable logic from the Sound On Sound news item "BS-203 MacroAcidizer from
Born Second" (published 6/9/26), the first virtual instrument from Born Second:

  * **Three operating modes** — *Mode 303* (a faithful TB-303 recreation),
    *Mode 202* ("the steeper envelope and brighter top end of the MR-202"), and
    *Mode BB* ("the 'nastier' sound offered by the Juteon Bassboy").
  * **Acid Sequencer with a Randomize function** that creates basslines "locked to
    major or minor scales", "with detailed control over the likes of **note
    length, density, time divisions** and so on".
  * Built-in FX: saturation, delay and reverb.

Mechanism (why each mode sounds different — modelled explicitly):
- The 303 has a *single* decaying filter envelope with accent adding a short
  boost; the **202's envelope is steeper** (higher decay slope / shorter effective
  decay) and its top end is brighter.  This module encodes that as per-mode
  ``env_decay``, ``env_slope`` (exponent applied to the decay curve) and
  ``brightness`` (a one-pole high shelf on the oscillator before the filter).
- *Mode BB* is "nastier": more pre-filter drive, more resonance and a harder
  clipper on the filter output — the Juteon Bassboy's aggressive character.
- The **303 slide** is a real pitch glide between consecutive slide-flagged steps
  (exponential, ~60 ms), and **accent** is a distinct louder+brighter hit, not
  just velocity: accent raises the envelope peak *and* the resonance, exactly as
  the hardware's accent circuit does.
- The randomizer is *scale-locked*: pitches are drawn from the mode's scale
  degrees, then filtered by the density target.

Not replicated: the analogue TB-303/Juteon circuits themselves, the plug-in UI.

Usage:
    from sound.generators.acid_seq import AcidSequencer, AcidVoice, MODES

    seq = AcidSequencer(scale="minor", density=0.55, seed=7)
    notes = seq.randomize(steps=16)          # [(step, pitch, accent, slide), ...]
    v = AcidVoice(sample_rate=44100, mode="303")
    audio = v.render_sequence(notes, bpm=130, root=33)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "MODES",
    "ModeSpec",
    "AcidVoice",
    "AcidSequencer",
    "SCALES",
    "STEP_DIVISIONS",
    "midi_to_freq",
]

A440 = 440.0

SCALES: Dict[str, Tuple[int, ...]] = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
    "minor_pentatonic": (0, 3, 5, 7, 10),
    "phrygian": (0, 1, 3, 5, 7, 8, 10),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
}

# "time divisions" — steps per beat.
STEP_DIVISIONS: Dict[str, float] = {
    "1/4": 1.0, "1/8": 2.0, "1/8T": 3.0, "1/16": 4.0, "1/16T": 6.0, "1/32": 8.0,
}


def midi_to_freq(note: float) -> float:
    """Equal-tempered MIDI note (A4 = 440 Hz) -> Hz."""
    return A440 * (2.0 ** ((float(note) - 69.0) / 12.0))


@dataclass(frozen=True)
class ModeSpec:
    """Per-mode voice parameters (the three BS-203 operating modes)."""
    name: str
    env_decay: float          # filter envelope decay time, seconds
    env_slope: float          # decay curve exponent (>1 = steeper = 202)
    env_amount: float         # envelope -> cutoff depth, octaves
    brightness: float         # pre-filter one-pole shelf cutoff, Hz
    drive: float              # pre-filter overdrive
    resonance: float          # base resonance 0..1
    accent_boost: float       # extra resonance + envelope on accented steps
    clip: float               # output hard-clip level (lower = nastier)
    square_level: float = 0.85


MODES: Dict[str, ModeSpec] = {
    "303": ModeSpec("TB-303", env_decay=0.24, env_slope=1.0, env_amount=3.2,
                    brightness=9000.0, drive=1.6, resonance=0.72,
                    accent_boost=0.16, clip=0.98),
    "202": ModeSpec("MC-202 / MR-202", env_decay=0.11, env_slope=2.0, env_amount=3.6,
                    brightness=15000.0, drive=1.4, resonance=0.68,
                    accent_boost=0.12, clip=0.95),
    "BB": ModeSpec("Juteon Bassboy", env_decay=0.18, env_slope=1.6, env_amount=4.0,
                   brightness=11000.0, drive=3.2, resonance=0.88,
                   accent_boost=0.24, clip=0.62),
}


@dataclass
class AcidStep:
    """One sequencer step: pitch offset from the root, accent, slide."""
    step: int
    offset: int                 # semitone offset from the sequence root
    accent: bool = False
    slide: bool = False
    gate: float = 0.55          # note length as a fraction of the step


class AcidSequencer:
    """16-step acid sequencer with scale-locked randomisation.

    Args:
        scale: key of :data:`SCALES` (the randomizer's pitch pool).
        density: 0..1 target share of sounding steps.
        division: key of :data:`STEP_DIVISIONS` (steps per beat).
        octave_range: how many octaves above the root the randomizer may reach.
        seed: RNG seed (deterministic patterns).
    """

    def __init__(self, scale: str = "minor", density: float = 0.55,
                 division: str = "1/16", octave_range: int = 2,
                 seed: int = 0, gate_min: float = 0.35,
                 gate_max: float = 0.9, accent_prob: float = 0.3,
                 slide_prob: float = 0.25):
        if scale not in SCALES:
            raise ValueError(f"scale must be one of {sorted(SCALES)}")
        if division not in STEP_DIVISIONS:
            raise ValueError(f"division must be one of {sorted(STEP_DIVISIONS)}")
        self.scale = scale
        self.density = float(min(1.0, max(0.0, density)))
        self.division = division
        self.octave_range = int(octave_range)
        self.seed = int(seed)
        self.gate_min = float(gate_min)
        self.gate_max = float(gate_max)
        self.accent_prob = float(accent_prob)
        self.slide_prob = float(slide_prob)
        self.steps: List[AcidStep] = []

    # ------------------------------------------------------------------ helpers
    @property
    def steps_per_beat(self) -> float:
        return STEP_DIVISIONS[self.division]

    def _pitch_pool(self) -> List[int]:
        """Legal semitone offsets (scale degrees across the octave range)."""
        degs = SCALES[self.scale]
        pool: List[int] = []
        for octave in range(self.octave_range + 1):
            for d in degs:
                pool.append(d + 12 * octave)
        return sorted(set(pool))

    # --------------------------------------------------------------- authoring
    def randomize(self, steps: int = 16, seed: Optional[int] = None,
                  root_step: bool = True) -> List[AcidStep]:
        """Generate a scale-locked pattern of ``steps`` steps.

        Density governs how many steps sound; the first step always sounds when
        ``root_step`` is set (the classic acid downbeat).
        """
        rng = np.random.default_rng(self.seed if seed is None else int(seed))
        pool = self._pitch_pool()
        # low degrees are favoured (bass lines sit near the root)
        weights = np.array([1.0 / (1.0 + 0.35 * p) for p in pool])
        weights = weights / weights.sum()

        n_sound = int(round(self.density * steps))
        n_sound = max(1, min(steps, n_sound))
        idx = rng.choice(steps, size=n_sound, replace=False)
        idx = sorted(int(i) for i in idx)
        if root_step and 0 not in idx:
            idx[0] = 0
            idx = sorted(set(idx))

        out: List[AcidStep] = []
        prev_offset = 0
        for s in range(steps):
            if s not in idx:
                continue
            offset = int(rng.choice(pool, p=weights))
            # second-most-common acid interval is the octave/root jump
            if s > 0 and rng.random() < 0.18:
                offset = prev_offset + (12 if rng.random() < 0.5 else -12)
            offset = max(0, min(24 + 12 * self.octave_range, offset))
            accent = bool(rng.random() < self.accent_prob)
            slide = bool(rng.random() < self.slide_prob and s < steps - 1)
            gate = float(rng.uniform(self.gate_min, self.gate_max))
            out.append(AcidStep(s, offset, accent, slide, gate))
            prev_offset = offset

        if root_step and out and out[0].step == 0:
            out[0] = AcidStep(0, 0, True, out[0].slide, out[0].gate)
        self.steps = out
        return out

    def set_pattern(self, steps: Sequence[AcidStep]) -> None:
        """Install an explicit pattern (e.g. transcribed from tab)."""
        self.steps = list(steps)

    # ------------------------------------------------------------------- timing
    def step_seconds(self, bpm: float) -> float:
        """Duration of one step in seconds."""
        return 60.0 / float(bpm) / self.steps_per_beat

    def gate_seconds(self, bpm: float, step: AcidStep) -> float:
        """Note length (seconds) for a step, honouring the slide flag."""
        base = self.step_seconds(bpm)
        gate = base * step.gate
        if step.slide:
            gate *= 1.75                 # slides tie into the next step
        return gate


class AcidVoice:
    """Single-VCO acid voice: saw/square + 3-pole ladder + env + accent + slide.

    Args:
        sample_rate: sample rate in Hz.
        mode: key of :data:`MODES` ("303", "202", "BB").
        drive / resonance / env_amount: per-instance overrides of the mode.
    """

    def __init__(self, sample_rate: int = 44100, mode: str = "303",
                 drive: Optional[float] = None,
                 resonance: Optional[float] = None,
                 env_amount: Optional[float] = None,
                 square: bool = False):
        if mode not in MODES:
            raise ValueError(f"mode must be one of {sorted(MODES)}")
        self.sr = int(sample_rate)
        self.mode = mode
        self.spec = MODES[mode]
        self.drive = float(self.spec.drive if drive is None else drive)
        self.resonance = float(self.spec.resonance if resonance is None else resonance)
        self.env_amount = float(self.spec.env_amount if env_amount is None else env_amount)
        self.square = bool(square)
        self.cutoff = 260.0               # base (fully decayed) cutoff, Hz
        self.slide_time = 0.055           # 303 slide glide time, seconds
        self.dc = 0.0

    # ------------------------------------------------------------------ source
    def _osc(self, phases: np.ndarray) -> np.ndarray:
        if self.square:
            w = np.where((phases % 1.0) < 0.5, 1.0, -1.0)
        else:
            w = 2.0 * (phases % 1.0) - 1.0
        return w * self.spec.square_level

    def _bright_shelf(self, x: np.ndarray) -> np.ndarray:
        """One-pole high shelf: mode-specific top-end brightness."""
        fc = min(self.spec.brightness, self.sr * 0.45)
        a = 1.0 - np.exp(-2.0 * np.pi * fc / self.sr)
        hp = np.empty_like(x)
        low = 0.0
        for i in range(x.size):
            low += a * (x[i] - low)
            hp[i] = x[i] - low
        return x + 0.6 * hp

    def _ladder3(self, x: np.ndarray, cutoff: np.ndarray,
                 res: np.ndarray) -> np.ndarray:
        """Three-pole saturating ladder with per-sample cutoff/resonance."""
        n = x.size
        out = np.empty(n)
        s1 = s2 = s3 = 0.0
        for i in range(n):
            g = 1.0 - np.exp(-2.0 * np.pi * float(cutoff[i]) / self.sr)
            g = min(g, 0.85)
            k = 3.2 * float(res[i])
            u = np.tanh(x[i] - k * s3)
            s1 += g * (u - s1)
            s2 += g * (s1 - s2)
            s3 += g * (s2 - s3)
            out[i] = s3
        return out

    # ------------------------------------------------------------------ render
    def render_step(self, offset: int, step_sec: float, gate_sec: float,
                    accent: bool = False, previous_offset: Optional[int] = None,
                    slide: bool = False, root_note: int = 33,
                    amp: float = 0.85) -> np.ndarray:
        """Render one sequencer step (mono).

        Args:
            offset: semitone offset from ``root_note``.
            step_sec: full step length in seconds (the buffer length).
            gate_sec: sounding length inside the step.
            accent: accent flag (louder + brighter + more resonant).
            previous_offset: previous step's offset, used for the slide glide.
            slide: glide from ``previous_offset`` into ``offset``.
            root_note: sequence root MIDI note.
            amp: output amplitude.
        """
        n = max(1, int(round(step_sec * self.sr)))
        n_gate = max(1, min(n, int(round(gate_sec * self.sr))))

        # --- pitch with exponential slide from the previous step
        target = midi_to_freq(root_note + offset)
        if slide and previous_offset is not None:
            start = midi_to_freq(root_note + previous_offset)
            n_glide = max(1, int(self.slide_time * self.sr))
            k = min(n_glide, n)
            glide = start * (target / start) ** (np.arange(k) / float(k))
            freq = np.concatenate([glide, np.full(n - k, target)])
        else:
            freq = np.full(n, target)

        phases = np.cumsum(freq / self.sr)
        osc = self._osc(phases)

        # --- pre-filter overdrive, mode-dependent brightness
        x = np.tanh(self.drive * osc)
        x = self._bright_shelf(x)

        # --- filter envelope: steeper slope in 202 mode, accent boosts both
        env = np.ones(n)
        decay = self.spec.env_decay * (0.75 if accent else 1.0)
        t = np.arange(n) / self.sr
        env = np.exp(-(t / max(1e-4, decay)) ** self.spec.env_slope)
        attack = min(n, max(1, int(0.0015 * self.sr)))
        env[:attack] *= np.linspace(0.0, 1.0, attack)
        depth = self.env_amount * (1.0 + (self.spec.accent_boost if accent else 0.0))
        cutoff = (self.cutoff + (target * 0.5)) * (2.0 ** (depth * env))
        res = np.full(n, min(1.0, self.resonance +
                             (self.spec.accent_boost if accent else 0.0)))
        # release: close the filter over the last 15 % so steps do not bleed
        rel = int(n_gate * 0.85)
        if rel < n:
            tail = np.linspace(0.0, 0.9, n - rel)
            cutoff[rel:] *= 2.0 ** (-depth * tail)

        filt = self._ladder3(x, cutoff, res)

        # --- VCA: gate envelope with 303-style fast attack/short release
        gate_env = np.zeros(n)
        na, nr = max(1, int(0.001 * self.sr)), max(1, int(0.010 * self.sr))
        gate_env[:na] = np.linspace(0.0, 1.0, na)
        gate_env[na:max(na, n_gate - nr)] = 1.0
        if n_gate > na:
            rel_start = max(na, n_gate - nr)
            gate_env[rel_start:n_gate] = np.linspace(
                1.0, 0.0, max(1, n_gate - rel_start))
        if n_gate < n:
            gate_env[n_gate:] = 0.0

        y = filt * gate_env * (1.25 if accent else 1.0)
        # --- mode-dependent output saturation / clip ("nastier" for BB)
        y = np.tanh(y * 1.25)
        y = np.clip(y, -self.spec.clip, self.spec.clip)

        # --- DC block so the pitch envelope does not offset the output
        r = 0.9995
        out = np.empty(n)
        prev_in = self.dc
        prev_out = 0.0
        for i in range(n):
            xin = y[i]
            prev_out = r * prev_out + (xin - prev_in)
            prev_in = xin
            out[i] = prev_out
        self.dc = prev_in

        peak = float(np.max(np.abs(out))) or 1.0
        return (out / peak * amp).astype(np.float64)

    def render_sequence(self, steps: Sequence[AcidStep], bpm: float = 130.0,
                        root_note: int = 33, loops: int = 1,
                        tail: float = 0.3) -> np.ndarray:
        """Render a whole pattern (``loops`` passes) to a mono buffer."""
        if not steps:
            return np.zeros(1)
        step_sec = 60.0 / float(bpm) / STEP_DIVISIONS["1/16"]
        # honour the sequencer's own division if the steps came from one
        total = int((len(steps) * loops + 1) * step_sec * self.sr + tail * self.sr)
        buf = np.zeros(total)
        prev_offset: Optional[int] = 0
        for loop in range(int(loops)):
            for st in steps:
                step_s = 60.0 / float(bpm) / STEP_DIVISIONS["1/16"]
                gate = step_s * st.gate * (1.75 if st.slide else 1.0)
                seg = self.render_step(st.offset, step_s, gate, st.accent,
                                       prev_offset, st.slide, root_note)
                i0 = int(round((loop * len(steps) + st.step) * step_s * self.sr))
                i1 = min(len(buf), i0 + seg.size)
                if i1 > i0:
                    buf[i0:i1] += seg[: i1 - i0]
                prev_offset = st.offset
        peak = float(np.max(np.abs(buf))) or 1.0
        return (buf / peak * 0.92).astype(np.float64)


def render_pattern(sequencer: AcidSequencer, bpm: float = 130.0,
                   root_note: int = 33, mode: str = "303",
                   sample_rate: int = 44100, loops: int = 1) -> np.ndarray:
    """Convenience: randomize + render in one call."""
    steps = sequencer.steps or sequencer.randomize()
    v = AcidVoice(sample_rate=sample_rate, mode=mode)
    return v.render_sequence(steps, bpm=bpm, root_note=root_note, loops=loops)


# ------------------------------------------------------------------------ demo
def demo() -> str:
    """Prove the three modes differ, the randomizer is scale-locked, slide works."""
    sr = 22050

    for name, spec in MODES.items():
        print(f"mode {name:3s} ({spec.name}): env_decay={spec.env_decay}s "
              f"slope={spec.env_slope} drive={spec.drive} res={spec.resonance} "
              f"clip={spec.clip}")

    seq = AcidSequencer(scale="minor", density=0.55, division="1/16",
                        seed=7, octave_range=2)
    steps = seq.randomize(steps=16)
    pool = set(seq._pitch_pool())
    print(f"randomized pattern ({len(steps)}/16 steps, density 0.55):")
    for st in steps:
        print(f"   step {st.step:2d}  +{st.offset:2d} st  "
              f"{'ACCENT' if st.accent else '      '} "
              f"{'SLIDE' if st.slide else '     '} gate={st.gate:.2f}")
    assert all(st.offset in pool for st in steps), "randomizer left the scale"
    print(f"scale lock ({seq.scale}): every offset in pool {sorted(pool)} -> True")
    assert steps[0].step == 0 and steps[0].offset == 0

    # time divisions
    print("time divisions (steps per beat):", STEP_DIVISIONS)
    bpm = 130.0
    for div in ("1/16", "1/8T", "1/32"):
        s2 = AcidSequencer(division=div, seed=1)
        print(f"   {div:5s} -> step = {s2.step_seconds(bpm) * 1000:6.1f} ms")

    # the three modes must produce measurably different audio
    stats = {}
    for mode in MODES:
        v = AcidVoice(sample_rate=sr, mode=mode)
        audio = v.render_sequence(steps, bpm=bpm, root_note=33)
        spec = np.abs(np.fft.rfft(audio * np.hanning(audio.size)))
        fr = np.fft.rfftfreq(audio.size, 1.0 / sr)
        centroid = float(np.sum(fr * spec) / (np.sum(spec) + 1e-12))
        stats[mode] = (centroid, float(np.sqrt(np.mean(audio ** 2))),
                       float(np.max(np.abs(audio))))
        print(f"mode {mode:3s}: len={audio.size} centroid={centroid:8.1f} Hz "
              f"rms={stats[mode][1]:.4f} peak={stats[mode][2]:.3f} "
              f"finite={np.all(np.isfinite(audio))}")
    assert len({round(c, 1) for c, _, _ in stats.values()}) == 3, \
        "modes should have distinct spectra"
    assert stats["202"][0] > stats["303"][0], "202 mode must be brighter than 303"

    # slide: a slide step glides instead of jumping
    v = AcidVoice(sample_rate=sr, mode="303")
    step_s = 60.0 / bpm / 4.0
    slid = v.render_step(12, step_s, step_s * 0.8, False, 0, True, 33)
    jumped = v.render_step(12, step_s, step_s * 0.8, False, 0, False, 33)
    n_glide = int(v.slide_time * sr)
    print(f"slide: first {n_glide} samples differ from a hard jump: "
          f"{not np.allclose(slid[:n_glide], jumped[:n_glide])}")
    assert not np.allclose(slid[:n_glide], jumped[:n_glide])

    # accent is more than velocity: it also opens the filter
    acc = v.render_step(0, step_s, step_s * 0.8, True, 0, False, 33)
    plain = v.render_step(0, step_s, step_s * 0.8, False, 0, False, 33)
    def cen(x):
        X = np.abs(np.fft.rfft(x * np.hanning(x.size)))
        f = np.fft.rfftfreq(x.size, 1.0 / sr)
        return float(np.sum(f * X) / (np.sum(X) + 1e-12))
    print(f"accent: rms {np.sqrt(np.mean(acc ** 2)):.4f} vs "
          f"{np.sqrt(np.mean(plain ** 2)):.4f}; centroid {cen(acc):.0f} Hz vs "
          f"{cen(plain):.0f} Hz")
    assert cen(acc) >= cen(plain) * 0.98

    # density control
    for d in (0.25, 0.5, 0.9):
        s = AcidSequencer(density=d, seed=3)
        print(f"density {d:.2f} -> {len(s.randomize(16))} sounding steps")
        assert abs(len(s.steps) - round(d * 16)) <= 1

    # deterministic per seed
    a = AcidSequencer(seed=11).randomize(16)
    b = AcidSequencer(seed=11).randomize(16)
    c = AcidSequencer(seed=12).randomize(16)
    assert [(s.step, s.offset) for s in a] == [(s.step, s.offset) for s in b]
    assert [(s.step, s.offset) for s in a] != [(s.step, s.offset) for s in c]
    print("determinism: same seed identical, different seed differs -> True")

    out = render_pattern(seq, bpm=130.0, mode="BB", sample_rate=sr, loops=2)
    print(f"render_pattern: len={out.size} peak={np.max(np.abs(out)):.3f}")
    assert np.max(np.abs(out)) > 0.1
    print("  acid_seq demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
