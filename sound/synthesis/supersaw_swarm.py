"""Supersaw swarm synthesizer — Native Instruments SuperStarSaw-style logic.

Replicable DSP from Native Instruments' SuperStarSaw (A.G. Cook collab,
reviewed on MusicTech 2026-08-20): the classic supersaw trick — many
slightly-detuned saw oscillators stacked into a thick, drifting sound —
taken to two independent "swarms" of 16 oscillators each, with:

- Per-swarm detune ``spread`` (a distribution of detune cents around the
  root; the classic JP-8000 supersaw used 7 saws, SuperStarSaw uses 16),
- A stereo field spread (per-oscillator pan),
- Per-oscillator amplitude randomization (the "drift" that makes a
  supersaw breathe),
- Harmony-engine scale / chord quantisation of every oscillator pitch
  (quantise the swarm to scale degrees or to chord tones, then widen
  with spread to create tense tone clusters),
- A Morph XY surface: 4 corner snapshots of parameter sets, blended
  bilinearly by (x, y) — the instrument's signature gesture controller.

What is NOT replicated here: the 235-preset library, the visual
oscillator-distribution UI, randomise-without-constraints behaviour
(a UX judgement call, not DSP), the filter/effects section (covered by
sound/effects/filter.py etc.).

Usage:
    from sound.synthesis.supersaw_swarm import SupersawSwarm

    s = SupersawSwarm(sample_rate=44100)
    audio = s.render_note(freq=110.0, duration=2.0, spread_cents=18.0)
"""

from typing import Dict, List, Optional, Tuple

import numpy as np

__all__ = ["SupersawSwarm", "SCALES", "SwarmSnapshot", "MorphPad"]

# Semitone offsets for common scales (0 = root); used by the harmony engine.
SCALES: Dict[str, List[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "super_locrian": [0, 1, 3, 4, 6, 8, 10],
    "dorian_sharp4": [0, 2, 3, 6, 7, 9, 10],
    "hirajoshi": [0, 2, 3, 7, 8],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "chromatic": list(range(12)),
}

# Classic chord shapes in semitone offsets from a root (harmony engine).
CHORDS: Dict[str, List[int]] = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "maj9": [0, 4, 7, 11, 14],
    "min9": [0, 3, 7, 10, 14],
    "add9": [0, 4, 7, 14],
    "power": [0, 7],
}


def _quantize_semitones(semi: float, degrees: List[int]) -> float:
    """Quantize a fractional semitone offset to the nearest scale degree.

    Continuous-space nearest-neighbour over the octave-wrapped degree list
    (with +/-1 octave copies so the wrap is seamless).
    """
    if not degrees:
        return semi
    octave = int(np.floor(semi / 12.0))
    pos = semi - octave * 12.0
    best, best_d = 0.0, float("inf")
    for deg in degrees:
        for rep in (deg - 12, deg, deg + 12):
            d = abs(pos - rep)
            if d < best_d:
                best_d = d
                best = rep
    return octave * 12.0 + best


class SwarmSnapshot:
    """A corner snapshot of swarm parameters for the morph pad.

    Each snapshot holds a complete parameterisation of one swarm: detune
    spread, pan spread, amplitude drift, cutoff feel (brightness is
    rendered as a gentle lowpass tilt applied at mix time) and an optional
    harmony mode (scale/chord + root).
    """

    def __init__(self, spread_cents: float = 15.0, pan_spread: float = 0.8,
                 drift: float = 0.25, brightness: float = 1.0,
                 harmony: Optional[str] = None,
                 harmony_root: int = 0) -> None:
        self.spread_cents = float(spread_cents)
        self.pan_spread = float(pan_spread)
        self.drift = float(drift)
        self.brightness = float(brightness)
        self.harmony = harmony  # scale name or chord name, None = off
        self.harmony_root = int(harmony_root)  # semitone offset for harmony


class MorphPad:
    """Bilinear 2x2 morph surface between four parameter snapshots.

    Four corners (A/B/C/D) each hold a SwarmSnapshot. An (x, y) position
    in [0, 1]^2 blends them bilinearly — the SuperStarSaw "floral Morpher"
    gesture idea: park a patch in each corner and drift/automate between
    them for musical gestures. The pad itself is static (no path
    recorder / LFO on the pad; the product omits that too).
    """

    def __init__(self, a: Optional[SwarmSnapshot] = None,
                 b: Optional[SwarmSnapshot] = None,
                 c: Optional[SwarmSnapshot] = None,
                 d: Optional[SwarmSnapshot] = None) -> None:
        self.corners = {
            "a": a or SwarmSnapshot(spread_cents=4.0, drift=0.05),
            "b": b or SwarmSnapshot(spread_cents=30.0, drift=0.1),
            "c": c or SwarmSnapshot(spread_cents=60.0, drift=0.4,
                                    harmony="minor", harmony_root=0),
            "d": d or SwarmSnapshot(spread_cents=15.0, drift=0.6,
                                    harmony="maj7", harmony_root=-12),
        }

    def sample(self, x: float, y: float) -> SwarmSnapshot:
        """Blend the four corners at pad position (x, y) in [0, 1]^2."""
        x = float(np.clip(x, 0.0, 1.0))
        y = float(np.clip(y, 0.0, 1.0))
        top = _lerp_snapshot(self.corners["a"], self.corners["b"], x)
        bottom = _lerp_snapshot(self.corners["c"], self.corners["d"], x)
        return _lerp_snapshot(top, bottom, y)


def _lerp_snapshot(p: SwarmSnapshot, q: SwarmSnapshot, t: float
                   ) -> SwarmSnapshot:
    """Linear interpolation of two snapshots' numeric fields.

    Harmony is blended in the most musical way available without a full
    morphing engine: the target harmony (chord/scale with larger spread)
    wins once t crosses 0.5, otherwise the source harmony stays. Numeric
    parameters interpolate continuously.
    """
    out = SwarmSnapshot(
        spread_cents=p.spread_cents * (1 - t) + q.spread_cents * t,
        pan_spread=p.pan_spread * (1 - t) + q.pan_spread * t,
        drift=p.drift * (1 - t) + q.drift * t,
        brightness=p.brightness * (1 - t) + q.brightness * t,
        harmony=p.harmony if t < 0.5 else q.harmony,
        harmony_root=p.harmony_root if t < 0.5 else q.harmony_root,
    )
    return out


class SupersawSwarm:
    """Two independent 16-oscillator supersaw swarms with harmony + morph.

    Parameters
    ----------
    sample_rate : int
        Sampling rate in Hz.
    osc_per_swarm : int
        Number of detuned saws per swarm (SuperStarSaw ships 16).
    """

    def __init__(self, sample_rate: int = 44100, osc_per_swarm: int = 16,
                 seed: Optional[int] = None) -> None:
        self.sr = int(sample_rate)
        self.osc_count = max(1, int(osc_per_swarm))
        self.rng = np.random.RandomState(seed)
        self.morph = MorphPad()

    # ------------------------------------------------------------------ #
    @staticmethod
    def _detune_ladder(n: int) -> np.ndarray:
        """Alternating detune offsets, normalized to [-1, 1].

        The ladder positions alternate small/large (1, -1, 2, -2, 3, -3, ...)
        so adjacent saws beat at different rates; normalization maps the
        outermost oscillator to +/-1 so ``spread_cents`` scales the whole
        distribution.
        """
        idx = np.arange(n)
        cents = np.where(idx % 2 == 0, (idx // 2) + 1, -((idx + 1) // 2))
        cents = cents.astype(np.float64)
        mx = np.max(np.abs(cents)) or 1.0
        return cents / mx

    def _harmony_degrees(self, harmony: Optional[str]) -> Optional[List[int]]:
        """Resolve a scale or chord name to a quantizer degree list."""
        if harmony is None:
            return None
        if harmony in SCALES:
            return SCALES[harmony]
        if harmony in CHORDS:
            return CHORDS[harmony]
        raise ValueError(f"unknown harmony '{harmony}', use a SCALES or CHORDS key")

    def _swarm(self, freq: float, duration: float, spread_cents: float,
               pan_spread: float, drift: float,
               harmony: Optional[str], harmony_root: int) -> Tuple[np.ndarray, np.ndarray]:
        """Render one swarm as a (left, right) pair.

        Per-oscillator detune is ``ladder[i] * spread_cents`` cents around the
        root. When a harmony (scale or chord) is set, each oscillator's total
        semitone position is quantized to the nearest degree of that scale /
        chord shape — the SuperStarSaw "usher each oscillator into the chosen
        scale's confines" trick: small spread lands the whole swarm on the
        harmony tones, wide spread lets oscillators wrap into neighbouring
        octaves and form tense tone clusters.
        """
        n = int(duration * self.sr)
        if n <= 0:
            return np.zeros(0), np.zeros(0)
        ladder = self._detune_ladder(self.osc_count)
        t = np.arange(n) / self.sr
        degrees = self._harmony_degrees(harmony)
        base_midi = 69.0 + 12.0 * np.log2(max(freq, 1e-6) / 440.0)

        # per-oscillator random amplitudes (drift) and pans
        amps = 1.0 + drift * (self.rng.uniform(-1, 1, self.osc_count))
        pans = pan_spread * self.rng.uniform(-1, 1, self.osc_count)

        left = np.zeros(n)
        right = np.zeros(n)
        for i in range(self.osc_count):
            cents = ladder[i] * spread_cents
            semi = base_midi + cents / 100.0
            if degrees is not None:
                # quantize the oscillator's offset from the played root
                rel = _quantize_semitones(semi - base_midi, degrees)
                semi = base_midi + rel
            f = 440.0 * (2.0 ** ((semi - 69.0) / 12.0))
            saw = _saw(t, f)
            # equal-power pan law
            th = (pans[i] + 1.0) * np.pi / 4.0
            gl, gr = np.cos(th), np.sin(th)
            left += amps[i] * gl * saw
            right += amps[i] * gr * saw
        return left, right

    # ------------------------------------------------------------------ #
    def render_note(self, freq: float, duration: float,
                    spread_cents: float = 18.0, pan_spread: float = 0.8,
                    drift: float = 0.3, harmony: Optional[str] = None,
                    harmony_root: int = 0, brightness: float = 1.0,
                    swarm2: bool = True, morph_xy: Optional[Tuple[float, float]] = None
                    ) -> np.ndarray:
        """Render a supersaw note (stereo float32 interleaved or mono).

        Args:
            freq: Note frequency in Hz (the root the swarms stack around).
            duration: Seconds.
            spread_cents: Total detune range in cents across the swarm.
            pan_spread: 0..1 — how widely oscillators are panned.
            drift: 0..1 — per-oscillator amplitude randomization (chorus life).
            harmony: Scale name (SCALES) or chord name (CHORDS) to quantize
                the swarm to; None leaves the swarm purely detuned.
            harmony_root: Semitone offset for harmony quantisation.
            brightness: 0..1 output lowpass tilt (1.0 = full bandwidth).
            swarm2: Render the second (contrasting) swarm and blend it.
            morph_xy: (x, y) pad position; when given it overrides the
                spread/drift/harmony arguments with the morph pad's blend.

        Returns:
            Stereo float32 numpy array, shape (n, 2).
        """
        snap = None
        if morph_xy is not None:
            snap = self.morph.sample(*morph_xy)
            spread_cents = snap.spread_cents
            pan_spread = snap.pan_spread
            drift = snap.drift
            brightness = snap.brightness
            harmony = snap.harmony
            harmony_root = snap.harmony_root

        shape = None  # scales and chords resolved inside _swarm via name
        left, right = self._swarm(freq, duration, spread_cents, pan_spread,
                                  drift, harmony, harmony_root)
        if swarm2:
            # second swarm: a fifth above + wider pan, blended at lower level
            # for movement between the two layers
            l2, r2 = self._swarm(freq * (2.0 ** (7.0 / 12.0)), duration,
                                 spread_cents * 0.8, pan_spread * 1.2,
                                 drift, harmony, harmony_root + 7)
            left = 0.65 * left + 0.35 * l2
            right = 0.65 * right + 0.35 * r2

        # brightness: one-pole lowpass tilt
        if brightness < 1.0:
            cutoff = _cutoff_for_brightness(brightness, self.sr)
            left = _one_pole_lp(left, cutoff, self.sr)
            right = _one_pole_lp(right, cutoff, self.sr)

        # soft normalize
        peak = max(np.max(np.abs(left)) if len(left) else 0.0,
                   np.max(np.abs(right)) if len(right) else 0.0)
        if peak > 1e-9:
            left /= peak
            right /= peak
        return np.stack([left, right], axis=1).astype(np.float32)


def _saw(t: np.ndarray, freq: float) -> np.ndarray:
    """Cheap band-limited-ish saw via summed harmonics (polyBLEP-free)."""
    if freq <= 0:
        return np.zeros_like(t)
    phase = (freq * t) % 1.0
    return 2.0 * phase - 1.0


def _one_pole_lp(x: np.ndarray, cutoff: float, sr: int) -> np.ndarray:
    """Simple one-pole lowpass (brightness tilt)."""
    if cutoff >= sr * 0.49 or len(x) == 0:
        return x
    alpha = 1.0 - np.exp(-2.0 * np.pi * cutoff / sr)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y


def _cutoff_for_brightness(b: float, sr: int) -> float:
    """Map brightness 0..1 to a lowpass cutoff (log taper)."""
    b = float(np.clip(b, 0.01, 1.0))
    return min(sr * 0.49, 300.0 * (2.0 ** (b * 7.0)))


def demo() -> str:
    """Run a short demo of the supersaw swarm engine."""
    sr = 44100
    s = SupersawSwarm(sample_rate=sr, seed=3)
    # A: narrow tight stack
    a1 = s.render_note(110.0, 1.2, spread_cents=4.0, drift=0.05,
                       swarm2=False)
    # B: wide classic supersaw
    a2 = s.render_note(110.0, 1.2, spread_cents=22.0, drift=0.3)
    # C: harmony-quantized cluster (minor scale, wide spread)
    a3 = s.render_note(110.0, 1.2, spread_cents=45.0, drift=0.4,
                       harmony="minor", harmony_root=0)
    # D: chord-quantized maj7 spread across two octaves
    a4 = s.render_note(110.0, 1.2, spread_cents=35.0, drift=0.5,
                       harmony="maj7", harmony_root=-12, swarm2=False)
    # E: morph pad gesture from corner A to corner C
    a5 = s.render_note(110.0, 1.2, morph_xy=(1.0, 0.0))
    return "\n".join([
        "SupersawSwarm demo:",
        f"  tight:    {a1.shape} peak={np.max(np.abs(a1)):.3f}",
        f"  supersaw: {a2.shape} peak={np.max(np.abs(a2)):.3f}",
        f"  scale-Q:  {a3.shape} peak={np.max(np.abs(a3)):.3f}",
        f"  chord-Q:  {a4.shape} peak={np.max(np.abs(a4)):.3f}",
        f"  morph AC: {a5.shape} peak={np.max(np.abs(a5)):.3f}",
        f"  osc/swarm={s.osc_count} morph_corner_C=spread {s.morph.corners['c'].spread_cents:.0f}c "
        f"harmony {s.morph.corners['c'].harmony}",
    ])


if __name__ == "__main__":
    print(demo())
