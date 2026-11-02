# -*- coding: utf-8 -*-
"""WMD Modbox MKII-style multi-mode CV generator — modular CV source.

Replicable logic from the WMD Modbox MKII announcement (Synthtopia
2026-11-01): a compact multifunction modulation module that combines a
Three-Phase LFO, a variable-shape Skew LFO, a digital sample-and-hold
circuit and an analog noise generator into one CV source.

What is replicated here (all pure CV/DSP, no hardware):

- ``ThreePhaseLFO``: three related outputs with three operating modes:
  *Phase Offset* (fixed phase relationships), *Phase Modulation* (cascading
  phase distortion — output 2's phase is modulated by output 1, output 3's by
  output 2) and *Frequency Spread* (output 2 runs up to 8x the base frequency
  while output 3 runs down to 1/8x).  A waveform control continuously morphs
  through saw -> sine -> triangle -> ramp.  Independent frequency ratios for
  outputs 2/3, 1V/octave tracking and audio-rate operation (it is just a
  phase accumulator, so the same code runs at any rate).
- ``SkewLFO``: morphs saw/triangle/ramp; a *slope* control adjusts the
  waveform transition and a separate *shape* function changes the curve from
  exponential through linear to logarithmic.  1V/octave tracking.
- ``SampleHold``: Sample & Hold, Track & Hold and *Turing Machine* modes.
  The Turing Machine stores a loop of 1..32 sampled voltages and a
  probability control decides whether new values enter the sequence or
  existing values repeat (change/repeat/reverse behaviour).
- ``ModboxCV``: combines the above with an analog white-noise generator and
  clock synchronization with ratios from 1:512 (slow division) to 4:1
  (multiplication), so all modulation can follow a broader rhythmic grid.

Not replicated: hardware, panel, settings auto-save, firmware updates.
"""

from __future__ import annotations

import numpy as np
from typing import List, Optional


class ThreePhaseLFO:
    """Three-output LFO with phase-offset / phase-mod / frequency-spread modes.

    Outputs are generated from one shared phase accumulator per mode:

    - ``phase_offset``: out2/out3 are copies of out1 shifted by fixed phase
      offsets (out2 ``phase2``, out3 ``phase3`` radians).
    - ``phase_mod``: cascading phase distortion — out2's phase is modulated
      by out1's value (``pm_depth``), out3's by out2's value.  Produces
      asymmetric, foldy shapes that are no longer simple sines.
    - ``freq_spread``: out2 runs at ``spread_ratio`` x the base frequency
      (up to 8x), out3 at ``1/spread_ratio`` x (down to 1/8x).
    """

    def __init__(
        self,
        freq_hz: float = 1.0,
        mode: str = "phase_offset",
        waveform: float = 0.0,       # 0 saw -> 0.5 sine -> 1 triangle -> 2 ramp
        phase2: float = 2.094,       # 120 deg default offset for out2
        phase3: float = 4.189,       # 240 deg default offset for out3
        pm_depth: float = 1.0,       # phase-mod depth (radians of extra phase)
        spread_ratio: float = 2.0,   # 1..8 frequency spread for out2
    ) -> None:
        assert mode in ("phase_offset", "phase_mod", "freq_spread")
        self.freq_hz = freq_hz
        self.mode = mode
        self.waveform = waveform
        self.phase2 = phase2
        self.phase3 = phase3
        self.pm_depth = pm_depth
        self.spread_ratio = spread_ratio

    @staticmethod
    def _morph(phase: np.ndarray, waveform: float) -> np.ndarray:
        """Continuous saw -> sine -> triangle -> ramp morph of a phase array.

        ``waveform`` is a position on a 0..2 line: 0 = saw, 0.5 = sine,
        1 = triangle, 2 = ramp.  Each section blends its two neighbours.
        """
        p = np.mod(phase, 2.0 * np.pi) / (2.0 * np.pi)  # 0..1
        if waveform <= 0.5:
            # saw (p) blended into sine
            t = waveform / 0.5
            saw = 2.0 * p - 1.0
            sine = np.sin(2.0 * np.pi * p)
            return (1.0 - t) * saw + t * sine
        if waveform <= 1.0:
            # sine blended into triangle
            t = (waveform - 0.5) / 0.5
            sine = np.sin(2.0 * np.pi * p)
            tri = 4.0 * np.abs(p - 0.5) - 1.0
            return (1.0 - t) * sine + t * tri
        # triangle blended into ramp (p goes 1 -> 0)
        t = (waveform - 1.0) / 1.0
        tri = 4.0 * np.abs(p - 0.5) - 1.0
        ramp = 1.0 - 2.0 * p
        return (1.0 - t) * tri + t * ramp

    def render(self, n_samples: int, sr: int = 48000,
               v_oct_cv: float = 0.0) -> np.ndarray:
        """Render ``n_samples`` of three CV outputs at sample rate ``sr``.

        ``v_oct_cv`` is an external 1V/octave CV that scales the base
        frequency (1 V doubles it), matching the module's 1V/octave tracking.
        """
        f = self.freq_hz * (2.0 ** v_oct_cv)
        t = np.arange(n_samples) / sr
        ph1 = 2.0 * np.pi * f * t
        if self.mode == "phase_offset":
            ph2 = ph1 + self.phase2
            ph3 = ph1 + self.phase3
        elif self.mode == "phase_mod":
            # cascading: out2 phase modulated by out1's waveform, out3 by out2's
            m1 = self._morph(ph1, self.waveform)
            ph2 = ph1 + self.pm_depth * m1
            m2 = self._morph(ph2, self.waveform)
            ph3 = ph2 + self.pm_depth * m2
        else:  # freq_spread
            ph2 = 2.0 * np.pi * f * self.spread_ratio * t
            ph3 = 2.0 * np.pi * f / self.spread_ratio * t
        out = np.stack([
            self._morph(ph1, self.waveform),
            self._morph(ph2, self.waveform),
            self._morph(ph3, self.waveform),
        ])
        return out


class SkewLFO:
    """Skew LFO — saw/triangle/ramp morph with slope + exponential->log shape.

    The *slope* control adjusts where in the cycle the transition happens
    (skewing the rise vs the fall); the *shape* function changes the curve
    from exponential through linear to logarithmic (``shape`` 0 = exp,
    0.5 = linear, 1 = log), applied on top of the base waveform.
    """

    def __init__(self, freq_hz: float = 1.0, slope: float = 0.5,
                 shape: float = 0.5, waveform: float = 0.0) -> None:
        self.freq_hz = freq_hz
        self.slope = slope            # 0..1 transition position
        self.shape = shape            # 0 exp .. 0.5 lin .. 1 log
        self.waveform = waveform      # 0 saw .. 1 triangle .. 2 ramp

    def _curve(self, x: np.ndarray) -> np.ndarray:
        """Apply the exponential/linear/logarithmic shape curve to 0..1."""
        if self.shape <= 0.5:
            t = self.shape / 0.5
            lin = x
            exp = (np.exp(x * 2.3) - 1.0) / (np.exp(2.3) - 1.0)
            return (1.0 - t) * exp + t * lin
        t = (self.shape - 0.5) / 0.5
        lin = x
        log = np.log1p(x * (np.e - 1.0)) / np.log(np.e)
        return (1.0 - t) * lin + t * log

    def render(self, n_samples: int, sr: int = 48000,
               v_oct_cv: float = 0.0) -> np.ndarray:
        f = self.freq_hz * (2.0 ** v_oct_cv)
        t = np.arange(n_samples) / sr
        p = np.mod(f * t, 1.0)
        # base waveform: blend saw (p) and triangle (4|p-0.5|-1) and ramp (1-2p)
        if self.waveform <= 1.0:
            w = (1.0 - self.waveform) * (2.0 * p - 1.0) + \
                self.waveform * (4.0 * np.abs(p - 0.5) - 1.0)
        else:
            w = (2.0 - self.waveform) * (4.0 * np.abs(p - 0.5) - 1.0) + \
                (self.waveform - 1.0) * (1.0 - 2.0 * p)
        # slope: skew the phase so the transition position is adjustable
        p_skew = np.mod(p + (0.5 - self.slope), 1.0)
        # recompute a skewed base for the transition-position control
        if self.waveform <= 1.0:
            w = (1.0 - self.waveform) * (2.0 * p_skew - 1.0) + \
                self.waveform * (4.0 * np.abs(p_skew - 0.5) - 1.0)
        else:
            w = (2.0 - self.waveform) * (4.0 * np.abs(p_skew - 0.5) - 1.0) + \
                (self.waveform - 1.0) * (1.0 - 2.0 * p_skew)
        # map 0..1 -> -1..1 then apply curve around the midpoint
        w01 = (w + 1.0) * 0.5
        return 2.0 * self._curve(w01) - 1.0


class SampleHold:
    """Digital S&H / T&H / Turing Machine CV sampler.

    - ``sample_hold``: capture the input voltage at each trigger edge and
      hold until the next one.
    - ``track_hold``: follow the input while the gate is high, hold the last
      value when the gate goes low.
    - ``turing_machine``: maintain a loop of ``loop_len`` (1..32) sampled
      voltages; each clock tick, with probability ``prob_new`` a NEW value
      enters the loop (and the oldest falls out), otherwise the loop repeats
      its existing values.  ``reverse`` makes the loop read backwards, which
      produces reversing patterns.
    """

    def __init__(self, mode: str = "sample_hold", loop_len: int = 16,
                 prob_new: float = 0.5, reverse: bool = False) -> None:
        assert mode in ("sample_hold", "track_hold", "turing_machine")
        self.mode = mode
        self.loop_len = max(1, min(32, int(loop_len)))
        self.prob_new = prob_new
        self.reverse = reverse
        self.loop: List[float] = [0.0] * self.loop_len
        self.loop_pos = 0

    def process(self, input_cv: np.ndarray, trigger: np.ndarray,
                gate: Optional[np.ndarray] = None) -> np.ndarray:
        """Process one block of CV.

        Args:
            input_cv: input voltage signal (or noise for random patterns).
            trigger: 1.0 at trigger events (clock), else 0.
            gate:    1.0 while gate high (only used in track_hold).
        """
        n = len(input_cv)
        out = np.zeros(n)
        held = 0.0
        prev_trig = 0.0
        rng = np.random.default_rng(0)
        for i in range(n):
            if self.mode == "sample_hold":
                if trigger[i] > 0.5 and prev_trig <= 0.5:
                    held = input_cv[i]
            elif self.mode == "track_hold":
                g = gate[i] if gate is not None else 0.0
                if g > 0.5:
                    held = input_cv[i]
            else:  # turing_machine
                if trigger[i] > 0.5 and prev_trig <= 0.5:
                    # circular buffer: the current position is the output.
                    # With probability prob_new a NEW value overwrites it,
                    # otherwise the existing stored value repeats.  Advancing
                    # the position each clock makes stored values re-circulate
                    # (repeating patterns); reverse walks the loop backwards
                    # (reversing patterns).
                    if rng.random() < self.prob_new:
                        self.loop[self.loop_pos] = input_cv[i]
                    held = self.loop[self.loop_pos]
                    if self.reverse:
                        self.loop_pos = (self.loop_pos - 1) % self.loop_len
                    else:
                        self.loop_pos = (self.loop_pos + 1) % self.loop_len
            prev_trig = trigger[i]
            out[i] = held
        return out


class ModboxCV:
    """Combined Modbox-style CV module: LFOs + S&H/Turing + noise + clock.

    Wires the pieces together the way the hardware does: the white-noise
    output is normalled into the S&H input (so random voltage patterns need
    no external source), and the Skew LFO's pulse output is normalled into
    the S&H trigger (so the LFO clocks the sampler).  Clock ratios from
    1:512 to 4:1 drive the LFO frequencies from a master clock.
    """

    CLOCK_RATIOS = [1 / 512, 1 / 256, 1 / 128, 1 / 64, 1 / 32, 1 / 16,
                    1 / 8, 1 / 4, 1 / 2, 1.0, 2.0, 4.0]

    def __init__(self, clock_hz: float = 1.0, clock_ratio: float = 1.0,
                 three_phase: Optional[ThreePhaseLFO] = None,
                 skew: Optional[SkewLFO] = None,
                 sh_mode: str = "turing_machine",
                 sh_loop_len: int = 16, sh_prob_new: float = 0.5) -> None:
        self.clock_hz = clock_hz
        self.clock_ratio = clock_ratio
        self.three_phase = three_phase or ThreePhaseLFO()
        self.skew = skew or SkewLFO()
        self.sh = SampleHold(mode=sh_mode, loop_len=sh_loop_len,
                             prob_new=sh_prob_new)

    def _master_freq(self) -> float:
        return self.clock_hz * self.clock_ratio

    def render(self, n_samples: int, sr: int = 48000, seed: int = 0) -> dict:
        """Render one block; returns dict of named CV outputs (each -1..1).

        Outputs: ``three_phase`` (3, n), ``skew``, ``sh`` (sampled CV),
        ``noise`` (white noise, normalled into the S&H input).
        """
        rng = np.random.default_rng(seed)
        t = np.arange(n_samples) / sr
        base = self._master_freq()
        self.three_phase.freq_hz = base
        self.skew.freq_hz = base
        three = self.three_phase.render(n_samples, sr)
        skew = self.skew.render(n_samples, sr)
        noise = rng.uniform(-1.0, 1.0, n_samples)
        # pulse of the skew LFO (rising edge) clocks the S&H
        pulse = (np.diff(np.concatenate([[0.0], (skew > 0.0).astype(float)]))
                 > 0.5).astype(float)
        sh = self.sh.process(noise, pulse)
        return {"three_phase": three, "skew": skew, "sh": sh, "noise": noise}


def demo() -> None:
    """Render one block in each three-phase mode and print output stats."""
    import numpy as np
    for mode in ("phase_offset", "phase_mod", "freq_spread"):
        m = ModboxCV(clock_hz=2.0, clock_ratio=2.0,
                     three_phase=ThreePhaseLFO(mode=mode, waveform=0.5,
                                               spread_ratio=4.0),
                     sh_mode="turing_machine", sh_loop_len=16,
                     sh_prob_new=0.5)
        # 4 seconds so the skew LFO crosses zero many times and clocks the S&H
        out = m.render(4 * 48000, sr=48000, seed=42)
        tp = out["three_phase"]
        print(f"[{mode}] three_phase shape={tp.shape} "
              f"rms={np.sqrt((tp ** 2).mean(axis=1)).round(4)} "
              f"sh range={out['sh'].min():+.3f}..{out['sh'].max():+.3f} "
              f"skew rms={np.sqrt((out['skew'] ** 2).mean()):.4f}")
    # Turing machine behaviour: count distinct held values over 200 ticks
    sh = SampleHold(mode="turing_machine", loop_len=8, prob_new=0.3)
    trig = np.zeros(9600)
    trig[::48] = 1.0
    held = sh.process(np.random.default_rng(1).uniform(-1, 1, 9600), trig)
    distinct = len(np.unique(np.round(held, 6)))
    print(f"turing_machine(loop=8, prob_new=0.3): {distinct} distinct held values "
          f"over {len(held)//48} ticks (expect repeating loop -> fewer than ticks)")
    assert tp.shape == (3, 4 * 48000)
    assert np.isfinite(held).all()
    print("demo OK")


if __name__ == "__main__":
    demo()
