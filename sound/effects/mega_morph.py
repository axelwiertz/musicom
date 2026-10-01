# -*- coding: utf-8 -*-
"""
MegaMorph — multi-segment envelope generator for parameter modulation.

Replicates the Sync Audio MegaMorph concept:
- Multi-segment envelope generator that can be 'attached' to any parameter
- Segment types: linear ramp, exponential, logarithmic, step, bezier-smooth
- Loop / repeat / sustain / bounce modes
- Tempo-synced segment durations
- Multiple independent envelope lanes for different parameters
- Useful for shaping synth/fx parameters into rhythmic patterns.

Inspired by Sync Audio MegaMorph (Instrument / FX / Warp variants).
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Tuple
import math


# ---------------------------------------------------------------------------
# Segment types
# ---------------------------------------------------------------------------

class SegmentShape(Enum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    STEP = "step"                    # immediate jump to target
    SMOOTHSTEP = "smoothstep"        # cubic S-curve (smooth in/out)
    BEZIER = "bezier"                # quadratic bezier midpoint pull


# ---------------------------------------------------------------------------
# Envelope segment
# ---------------------------------------------------------------------------

@dataclass
class EnvSegment:
    """One segment of a multi-segment envelope.

    Parameters
    ----------
    target : float
        End value for this segment (0..1 typically).
    duration_beats : float
        Segment length in beats (used with tempo-sync).
    duration_sec : float
        Segment length in seconds (fallback if tempo=0).
    shape : SegmentShape
        Curve shape for interpolation.
    curvature : float
        For exponential/logarithmic: >1 exponential, <1 anti-exponential.
        For bezier: bezier midpoint (0..1, 0.5=linear).
    """

    target: float = 1.0
    duration_beats: float = 1.0
    duration_sec: float = 1.0
    shape: SegmentShape = SegmentShape.LINEAR
    curvature: float = 2.0


# ---------------------------------------------------------------------------
# Envelope modes
# ---------------------------------------------------------------------------

class EnvMode(Enum):
    ONESHOT = "oneshot"           # play once then hold last value
    LOOP = "loop"                 # loop segments
    BOUNCE = "bounce"             # forward then backward
    SUSTAIN = "sustain"           # play once then hold at sustain_idx


# ---------------------------------------------------------------------------
# Multi-segment envelope
# ---------------------------------------------------------------------------

class MultiSegmentEnv:
    """Multi-segment envelope generator.

    Produces a control signal (0..1) that steps through a list of segments.
    Each segment interpolates from previous value to target value.

    Parameters
    ----------
    segments : List[EnvSegment]
        The segment list.
    mode : EnvMode
        Playback mode.
    sustain_idx : int
        Segment index to hold at in SUSTAIN mode.
    initial_value : float
        Starting value before first segment.
    bpm : float
        Tempo for beat-synced durations (0 = use seconds).
    """

    def __init__(self, segments: Optional[List[EnvSegment]] = None,
                 mode: EnvMode = EnvMode.LOOP,
                 sustain_idx: int = -1,
                 initial_value: float = 0.0,
                 bpm: float = 120.0):
        self.segments = segments or [EnvSegment()]
        self.mode = mode
        self.sustain_idx = sustain_idx if sustain_idx >= 0 else len(self.segments) - 1
        self.initial_value = initial_value
        self.bpm = bpm
        self._current_value = initial_value
        self._current_idx = 0
        self._segment_progress = 0.0  # 0..1 within current segment
        self._direction = 1  # 1 = forward, -1 = bounce backward

    def reset(self):
        """Reset envelope to initial state."""
        self._current_value = self.initial_value
        self._current_idx = 0
        self._segment_progress = 0.0
        self._direction = 1

    @property
    def current_value(self) -> float:
        return self._current_value

    @property
    def current_segment(self) -> EnvSegment:
        return self.segments[self._current_idx]

    def _interpolate(self, start_val: float, seg: EnvSegment, progress: float) -> float:
        """Apply shape interpolation."""
        p = max(0.0, min(1.0, progress))

        if seg.shape == SegmentShape.LINEAR:
            return start_val + (seg.target - start_val) * p
        elif seg.shape == SegmentShape.EXPONENTIAL:
            # exponential curve: accelerate toward target
            curve = max(0.1, seg.curvature)
            eased = (math.exp(curve * p) - 1) / (math.exp(curve) - 1)
            return start_val + (seg.target - start_val) * eased
        elif seg.shape == SegmentShape.LOGARITHMIC:
            # logarithmic: decelerate toward target
            curve = max(0.1, seg.curvature)
            eased = math.log(1 + curve * p) / math.log(1 + curve)
            return start_val + (seg.target - start_val) * eased
        elif seg.shape == SegmentShape.STEP:
            return seg.target if p >= 1.0 else start_val
        elif seg.shape == SegmentShape.SMOOTHSTEP:
            # cubic smoothstep: 3p² - 2p³
            eased = p * p * (3.0 - 2.0 * p)
            return start_val + (seg.target - start_val) * eased
        elif seg.shape == SegmentShape.BEZIER:
            # quadratic bezier: midpoint curvature
            mid = max(0.0, min(1.0, seg.curvature))
            # control point pulls toward (0.5, mid)
            bx = p
            by = 2 * (1 - p) * p * mid + p * p
            return start_val + (seg.target - start_val) * by
        else:
            return start_val + (seg.target - start_val) * p

    def _segment_duration_sec(self, seg: EnvSegment) -> float:
        """Get segment duration in seconds."""
        if self.bpm > 0 and seg.duration_beats > 0:
            beat_sec = 60.0 / self.bpm
            return seg.duration_beats * beat_sec
        return seg.duration_sec

    def advance(self, delta_sec: float) -> float:
        """Advance envelope by delta_sec seconds, return current value.

        This is the main call — call each sample or each buffer frame.
        """
        seg = self.segments[self._current_idx]
        dur = self._segment_duration_sec(seg)
        if dur <= 0:
            dur = 0.001  # prevent division by zero

        # Accumulate progress
        self._segment_progress += delta_sec / dur

        while self._segment_progress >= 1.0:
            # Move to next segment
            self._segment_progress -= 1.0

            if self.mode == EnvMode.ONESHOT:
                if self._current_idx >= len(self.segments) - 1:
                    self._current_idx = self.sustain_idx
                    self._segment_progress = 0.0
                    self._current_value = self.segments[self.sustain_idx].target
                    return self._current_value
                else:
                    self._current_idx += 1
            elif self.mode == EnvMode.LOOP:
                self._current_idx = (self._current_idx + 1) % len(self.segments)
            elif self.mode == EnvMode.BOUNCE:
                if self._direction == 1:
                    if self._current_idx >= len(self.segments) - 1:
                        self._direction = -1
                        self._current_idx = max(0, self._current_idx - 1)
                    else:
                        self._current_idx += 1
                else:
                    if self._current_idx <= 0:
                        self._direction = 1
                        self._current_idx = min(len(self.segments) - 1, self._current_idx + 1)
                    else:
                        self._current_idx -= 1
            elif self.sustain_idx < len(self.segments):
                if self._current_idx >= len(self.segments) - 1:
                    self._current_idx = self.sustain_idx
                    self._segment_progress = 0.0
                    self._current_value = self.segments[self.sustain_idx].target
                    return self._current_value
                else:
                    self._current_idx += 1

        # Interpolate within current segment
        seg = self.segments[self._current_idx]
        # Determine start value: previous segment's target
        prev_idx = self._current_idx - 1 if self._current_idx > 0 else len(self.segments) - 1
        if self.mode == EnvMode.BOUNCE and self._direction == -1:
            # In bounce, we reverse through segments — get the 'other side'
            next_idx = (self._current_idx + 1) % len(self.segments)
            start_val = self.segments[next_idx].target if next_idx < len(self.segments) else self.initial_value
        else:
            start_val = self.segments[prev_idx].target if prev_idx >= 0 else self.initial_value

        self._current_value = self._interpolate(start_val, seg, self._segment_progress)
        return self._current_value


# ---------------------------------------------------------------------------
# MegaMorph — multi-lane envelope modulation host
# ---------------------------------------------------------------------------

class MegaMorph:
    """Multi-lane envelope modulation system, the core of MegaMorph.

    Each 'lane' is an independent MultiSegmentEnv that can modulate any
    named parameter.  The render() method returns a dict of parameter_name → value.

    Parameters
    ----------
    lanes : dict of str → MultiSegmentEnv
        Lane name → envelope generator.
    bpm : float
        Global tempo.
    """

    def __init__(self, lanes: Optional[dict] = None, bpm: float = 120.0):
        self.lanes: dict[str, MultiSegmentEnv] = lanes or {}
        self.bpm = bpm

    def add_lane(self, name: str, env: MultiSegmentEnv):
        """Add a modulation lane."""
        self.lanes[name] = env

    def remove_lane(self, name: str):
        self.lanes.pop(name, None)

    def reset(self):
        """Reset all lanes."""
        for env in self.lanes.values():
            env.reset()

    def render(self, duration_sec: float, step_sec: float = 0.01
               ) -> dict[str, np.ndarray]:
        """Render all lanes for a given duration.

        Parameters
        ----------
        duration_sec : float
            Total duration in seconds.
        step_sec : float
            Time step per sample (1/sr for audio rate, larger for control rate).

        Returns
        -------
        lanes_out : dict[str, ndarray]
            Lane name → array of values at each time step.
        """
        n_steps = max(1, int(duration_sec / step_sec))
        out: dict[str, np.ndarray] = {}
        for name, env in self.lanes.items():
            env.reset()
            values = np.zeros(n_steps)
            for i in range(n_steps):
                values[i] = env.advance(step_sec)
            out[name] = values
        return out

    def render_audio_mod(self, duration_sec: float, sr: int = 44100
                         ) -> dict[str, np.ndarray]:
        """Render at audio rate for sample-level modulation."""
        step = 1.0 / sr
        return self.render(duration_sec, step)


# ---------------------------------------------------------------------------
# Preset factory methods
# ---------------------------------------------------------------------------

def envelope_preset(name: str = "trance_gate", bpm: float = 128.0) -> MegaMorph:
    """Create a MegaMorph from a named preset.

    Presets: 'trance_gate', 'sidechain_pump', 'rhythmic_stutter',
             'evolve_fade', 'bounce_filter', 'lfo_env'.
    """
    presets: dict[str, list[tuple[str, EnvMode, list[EnvSegment], float]]] = {
        "trance_gate": [
            ("volume", EnvMode.LOOP,
             [EnvSegment(1.0, 0.25, 0, shape=SegmentShape.LINEAR),
              EnvSegment(0.0, 0.75, 0, shape=SegmentShape.EXPONENTIAL, curvature=4.0)],
             0.0),
        ],
        "sidechain_pump": [
            ("volume", EnvMode.LOOP,
             [EnvSegment(0.0, 0.05, 0, shape=SegmentShape.STEP),
              EnvSegment(1.0, 0.25, 0, shape=SegmentShape.SMOOTHSTEP),
              EnvSegment(1.0, 0.70, 0, shape=SegmentShape.LINEAR)],
             0.0),
        ],
        "rhythmic_stutter": [
            ("volume", EnvMode.LOOP,
             [EnvSegment(1.0, 0.125, 0, shape=SegmentShape.STEP),
              EnvSegment(0.0, 0.125, 0, shape=SegmentShape.STEP),
              EnvSegment(1.0, 0.125, 0, shape=SegmentShape.STEP),
              EnvSegment(0.0, 0.125, 0, shape=SegmentShape.STEP),
              EnvSegment(1.0, 0.125, 0, shape=SegmentShape.STEP),
              EnvSegment(0.0, 0.125, 0, shape=SegmentShape.STEP),
              EnvSegment(1.0, 0.125, 0, shape=SegmentShape.STEP),
              EnvSegment(0.0, 0.125, 0, shape=SegmentShape.STEP)],
             0.0),
        ],
        "evolve_fade": [
            ("mix", EnvMode.ONESHOT,
             [EnvSegment(0.0, 0.0, 0.0, shape=SegmentShape.STEP),
              EnvSegment(1.0, 0.0, 4.0, shape=SegmentShape.SMOOTHSTEP)],
             0.0),
        ],
        "bounce_filter": [
            ("cutoff", EnvMode.BOUNCE,
             [EnvSegment(0.3, 0.5, 0, shape=SegmentShape.LINEAR),
              EnvSegment(0.9, 0.5, 0, shape=SegmentShape.SMOOTHSTEP)],
             0.3),
        ],
        "lfo_env": [
            ("depth", EnvMode.LOOP,
             [EnvSegment(1.0, 1.0, 0, shape=SegmentShape.BEZIER, curvature=0.8),
              EnvSegment(0.0, 1.0, 0, shape=SegmentShape.BEZIER, curvature=0.2)],
             0.0),
        ],
    }

    if name not in presets:
        raise ValueError(f"Unknown preset {name!r}. Available: {list(presets.keys())}")

    mm = MegaMorph(bpm=bpm)
    for lane_name, mode, segments, init_val in presets[name]:
        for s in segments:
            s.target = max(0.0, min(1.0, s.target))
        env = MultiSegmentEnv(segments, mode=mode, initial_value=init_val, bpm=bpm)
        mm.add_lane(lane_name, env)
    return mm


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    """Demonstrate MegaMorph with several presets + custom env."""
    import sys, os

    bpm = 128
    duration = 4.0
    sr = 100  # control rate

    print("=== MegaMorph Demo ===")
    print(f"BPM={bpm}, duration={duration}s")

    for pname in ["sidechain_pump", "trance_gate", "bounce_filter", "rhythmic_stutter", "lfo_env"]:
        mm = envelope_preset(pname, bpm)
        out = mm.render(duration, step_sec=1.0 / sr)
        print(f"\nPreset: {pname}")
        for lane, vals in out.items():
            print(f"  {lane}: {len(vals)} values, "
                  f"min={vals.min():.3f}, max={vals.max():.3f}, "
                  f"mean={vals.mean():.3f}")

    # Custom: 3-lane multi-segment envelope
    print("\n--- Custom 3-lane ---")
    mm = MegaMorph(bpm=bpm)
    mm.add_lane("pitch", MultiSegmentEnv([
        EnvSegment(0.5, 0.5, 0, shape=SegmentShape.SMOOTHSTEP),
        EnvSegment(0.8, 0.5, 0, shape=SegmentShape.SMOOTHSTEP),
        EnvSegment(0.2, 0.5, 0, shape=SegmentShape.EXPONENTIAL, curvature=3.0),
        EnvSegment(0.6, 0.5, 0, shape=SegmentShape.LINEAR),
    ], mode=EnvMode.LOOP, initial_value=0.5, bpm=bpm))

    mm.add_lane("filter", MultiSegmentEnv([
        EnvSegment(0.9, 1.0, 0, shape=SegmentShape.SMOOTHSTEP),
        EnvSegment(0.1, 1.0, 0, shape=SegmentShape.EXPONENTIAL, curvature=5.0),
    ], mode=EnvMode.BOUNCE, initial_value=0.5, bpm=bpm))

    mm.add_lane("volume", MultiSegmentEnv([
        EnvSegment(1.0, 0.125, 0, shape=SegmentShape.STEP),
        EnvSegment(0.0, 0.125, 0, shape=SegmentShape.STEP),
    ], mode=EnvMode.LOOP, initial_value=1.0, bpm=bpm))

    out = mm.render(duration, step_sec=1.0 / sr)
    for lane, vals in out.items():
        print(f"  {lane}: {len(vals)} values, min={vals.min():.3f}, "
              f"max={vals.max():.3f}, mean={vals.mean():.3f}")

    # Save CSV for visualization
    csv_path = "/tmp/megamorph_demo.csv"
    import csv
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["step", *out.keys()])
        n = len(next(iter(out.values())))
        for i in range(n):
            w.writerow([i, *(out[k][i] if i < len(out[k]) else 0.0 for k in out)])
    print(f"\nWrote {csv_path} ({n} rows)")

    print("\nMegaMorph demo OK.")
    return csv_path


if __name__ == "__main__":
    demo()