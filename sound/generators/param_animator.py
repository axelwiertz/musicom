"""Pentaphonic-style Parameter Animator — 16-step modulation pattern generator.

Inspired by Cherry Audio's Pentaphonic (Gleeman Pentaphonic recreation), which
includes a 16-step Parameter Animator that provides sequenced modulation for
synthesis parameters: filter cutoff, resonance, oscillator pitch modulation,
and oscillator gain. Each step in the sequence stores a target value; the
animator interpolates between steps at a rate determined by a master speed.

The Parameter Animator differs from a standard step sequencer in that it is
designed specifically for *continuous parameter modulation* — the output is a
floating-point control signal (like a  CV) that can be routed to any
synthesis parameter, rather than MIDI note events. This allows evolving,
patterned modulation of synthesis parameters over time.

Key DSP concepts:
- 16-step sequence per parameter lane (cutoff, resonance, pitch_mod, gain)
- Linear interpolation between step values (continuous CV output)
- Adjustable speed (tempo-synced or free)
- Per-lane depth control (modulation intensity)
- Loop modes: oneshot, forward, pingpong, random
- Each lane can be independently toggled and depth-scaled

Reference:
  - Cherry Audio Pentaphonic: https://cherryaudio.com/products/pentaphonic-synthesizer
  - https://www.synthtopia.com/content/2026/10/07/cherry-audio-revives-rare-gleeman-pentaphonic-as-a-modern-soft-synth/

Usage:
    from sound.generators.param_animator import ParameterAnimator, ParamLane

    anim = ParameterAnimator()
    anim.set_lane('cutoff', steps=[0.0, 0.5, 1.0, 0.8, 0.3, 0.0])
    t = np.linspace(0, 4.0, int(44100 * 4))
    cv = anim.render(t)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np


class LoopMode(Enum):
    """Playback mode for the step sequence."""
    FORWARD = "forward"       # 0→1→2→...→N-1→0→1→...
    PINGPONG = "pingpong"     # 0→1→...→N-1→N-2→...→0→1→...
    ONESHOT = "oneshot"       # 0→1→...→N-1 (hold last value)
    RANDOM = "random"         # Random step selection each reset


@dataclass
class ParamLane:
    """A single parameter lane in the animator.

    Parameters
    ----------
    name : str
        Parameter name (e.g. 'cutoff', 'resonance', 'pitch_mod', 'gain').
    steps : List[float]
        Sequence of values 0.0–1.0 for each step. Up to 16 steps.
    depth : float
        Modulation depth 0.0–1.0. 0 = output always at 0.5 (center).
        1 = full range. Depth is a scaling applied after interpolation.
    speed : float
        Steps per second (if not tempo-synced). Default 2.0 steps/sec.
    loop_mode : LoopMode
        Playback mode for the sequence.
    active : bool
        If False, lane outputs 0.5 (neutral center value).
    interpolate : bool
        If True (default), linearly interpolate between steps.
        If False, output is constant per-step (stepped CV).
    """

    name: str = "param"
    steps: List[float] = field(default_factory=lambda: [0.0, 1.0])
    depth: float = 1.0
    speed: float = 2.0
    loop_mode: LoopMode = LoopMode.FORWARD
    active: bool = True
    interpolate: bool = True

    def __post_init__(self):
        self._phase: float = 0.0  # in steps

    def reset(self, phase: float = 0.0):
        """Reset the lane phase.

        Parameters
        ----------
        phase : float
            Initial step position (fractional step index).
        """
        self._phase = phase

    def step(self, dt: float):
        """Advance the phase by `dt` seconds.

        Parameters
        ----------
        dt : float
            Time delta in seconds.
        """
        if not self.active or not self.steps:
            return
        n = len(self.steps)
        self._phase = (self._phase + self.speed * dt)

        if self.loop_mode == LoopMode.FORWARD:
            self._phase = self._phase % n
        elif self.loop_mode == LoopMode.PINGPONG:
            self._phase = self._phase % (2 * (n - 1))
            if self._phase > n - 1:
                self._phase = 2 * (n - 1) - self._phase
        elif self.loop_mode == LoopMode.ONESHOT:
            if self._phase >= n - 1:
                self._phase = float(n - 1)
        elif self.loop_mode == LoopMode.RANDOM:
            # resample random step on wrap
            if self._phase >= n:
                self._phase = float(np.random.randint(0, n))

    def read(self) -> float:
        """Read current lane output value (0.0–1.0).

        Returns
        -------
        float
            Interpolated step value, scaled by depth around center 0.5.
        """
        if not self.active or not self.steps:
            return 0.5
        n = len(self.steps)
        idx = int(self._phase)
        frac = self._phase - idx
        idx = idx % n

        if self.loop_mode == LoopMode.RANDOM:
            frac = 0.0  # stepped output for random mode

        if self.interpolate and n > 1:
            nxt = (idx + 1) % n
            a, b = self.steps[idx], self.steps[nxt]
            val = a + (b - a) * min(frac, 1.0)
        else:
            val = self.steps[idx]

        # Scale by depth around 0.5 center
        val = 0.5 + (val - 0.5) * self.depth
        return float(max(0.0, min(1.0, val)))


# ---------------------------------------------------------------------------
# Default lane presets
# ---------------------------------------------------------------------------
def cutoff_animator_lane() -> ParamLane:
    """Filter cutoff animator — opening/closing pattern."""
    return ParamLane(
        name="cutoff",
        steps=[0.0, 0.3, 0.7, 0.9, 1.0, 0.8, 0.4, 0.1],
        depth=0.8, speed=1.5, loop_mode=LoopMode.FORWARD
    )


def resonance_animator_lane() -> ParamLane:
    """Filter resonance animator — accent pulses."""
    return ParamLane(
        name="resonance",
        steps=[0.2, 0.2, 0.8, 0.3],
        depth=0.6, speed=3.0, loop_mode=LoopMode.FORWARD
    )


def pitch_mod_animator_lane() -> ParamLane:
    """Pitch modulation animator — vibrato pattern."""
    return ParamLane(
        name="pitch_mod",
        steps=[0.5, 0.6, 0.5, 0.4, 0.5],
        depth=0.15, speed=5.0, loop_mode=LoopMode.PINGPONG
    )


def gain_animator_lane() -> ParamLane:
    """Gain/volume animator — rhythmic pattern."""
    return ParamLane(
        name="gain",
        steps=[1.0, 0.8, 0.6, 0.3, 0.0, 0.3, 0.6, 0.8],
        depth=1.0, speed=2.0, loop_mode=LoopMode.FORWARD
    )


DEFAULT_ANIMATOR_PRESET = {
    "cutoff": cutoff_animator_lane(),
    "resonance": resonance_animator_lane(),
    "pitch_mod": pitch_mod_animator_lane(),
    "gain": gain_animator_lane(),
}


# ---------------------------------------------------------------------------
# Main animator
# ---------------------------------------------------------------------------
class ParameterAnimator:
    """Multi-lane 16-step parameter modulation animator.

    Parameters
    ----------
    sample_rate : int
        Sample rate in Hz (for sample-accurate stepping).
    lanes : Dict[str, ParamLane], optional
        Lane configurations. If None, uses DEFAULT_ANIMATOR_PRESET.
    """

    MAX_STEPS = 16

    def __init__(self, sample_rate: int = 44100,
                 lanes: Optional[Dict[str, ParamLane]] = None):
        self.sample_rate = sample_rate
        self.lanes: Dict[str, ParamLane] = {}
        lane_src = lanes or DEFAULT_ANIMATOR_PRESET
        for name, lane in lane_src.items():
            self.add_lane(name, lane)

    def add_lane(self, name: str, lane: ParamLane):
        """Add or replace a parameter lane.

        Parameters
        ----------
        name : str
            Lane name.
        lane : ParamLane
            Lane configuration.
        """
        if len(lane.steps) > self.MAX_STEPS:
            lane.steps = lane.steps[:self.MAX_STEPS]
        self.lanes[name] = lane

    def set_lane(self, name: str, steps: List[float],
                 depth: Optional[float] = None,
                 speed: Optional[float] = None,
                 loop_mode: Optional[LoopMode] = None):
        """Quick-set a lane's steps and optional overrides.

        Parameters
        ----------
        name : str
            Lane name. Creates lane if it doesn't exist.
        steps : List[float]
            Step values 0.0–1.0 (max {MAX_STEPS}).
        depth : float, optional
            Modulation depth.
        speed : float, optional
            Steps per second.
        loop_mode : LoopMode, optional
            Playback mode.
        """
        if len(steps) > self.MAX_STEPS:
            steps = steps[:self.MAX_STEPS]
        if name in self.lanes:
            lane = self.lanes[name]
            lane.steps = steps
            if depth is not None:
                lane.depth = depth
            if speed is not None:
                lane.speed = speed
            if loop_mode is not None:
                lane.loop_mode = loop_mode
        else:
            lane = ParamLane(name=name, steps=steps)
            if depth is not None:
                lane.depth = depth
            if speed is not None:
                lane.speed = speed
            if loop_mode is not None:
                lane.loop_mode = loop_mode
            self.lanes[name] = lane

    def reset(self):
        """Reset all lanes to initial phase."""
        for lane in self.lanes.values():
            lane.reset()

    def render(self, times: np.ndarray) -> Dict[str, np.ndarray]:
        """Render parameter CV signals for the given time array.

        Parameters
        ----------
        times : np.ndarray
            Time array in seconds (1-D).

        Returns
        -------
        Dict[str, np.ndarray]
            Dict mapping lane name → CV signal array (same length as times).
            Values in range 0.0–1.0.
        """
        if times.ndim != 1:
            raise ValueError("times must be a 1-D array")
        result: Dict[str, np.ndarray] = {}
        dt = times[1] - times[0] if len(times) > 1 else 1.0 / self.sample_rate

        for name, lane in self.lanes.items():
            out = np.zeros_like(times)
            lane.reset()
            for i in range(len(times)):
                out[i] = lane.read()
                lane.step(dt)
            result[name] = out

        return result

    def read_cv(self) -> Dict[str, float]:
        """Read the current CV value for all lanes (no advance).

        Returns
        -------
        Dict[str, float]
            Current lane values.
        """
        return {name: lane.read() for name, lane in self.lanes.items()}


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def demo():
    """Demonstrate the ParameterAnimator with default preset."""
    sr = 44100
    duration = 4.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    anim = ParameterAnimator(sample_rate=sr)
    cv = anim.render(t)

    print(f"ParameterAnimator demo ({sr} Hz, {duration:.1f}s)")
    for name, sig in cv.items():
        assert len(sig) == len(t), f"Lane '{name}' length mismatch"
        rms = float(np.sqrt(np.mean(sig ** 2)))
        min_v, max_v = float(np.min(sig)), float(np.max(sig))
        cycles = sum(1 for i in range(1, len(sig)) if sig[i] < 0.25 and sig[i-1] >= 0.25)
        print(f"  Lane '{name}': {len(sig)} samples, "
              f"range [{min_v:.3f}, {max_v:.3f}], RMS {rms:.3f}, "
              f"~{max(1, cycles)} zero-crossings at 0.25 threshold")
        assert len(sig) == len(t), "Length mismatch"
        assert min_v >= 0.0 and max_v <= 1.0, "CV out of range"

    print("  All lanes OK — CV signals in [0, 1] range, correct length")
    return cv


if __name__ == "__main__":
    demo()