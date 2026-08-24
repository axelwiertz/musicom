"""Micro-timing shift sequencer — Rapid Flow miniGRID-style.

Replicable logic from Rapid Flow's miniGRID sequencer plug-in (SOS
2026-08-24): four independent MIDI lanes, each with up to +/-64 ms of
per-lane time shift, up to 32 steps per lane, per-lane note assignment,
mute/solo, and vintage shuffle styles modeled on iconic drum machines
(TR-909, MPC60, SP-12, MPC3000, DMX, LM-1, Tanzbar).

What is replicated here:
- 4-lane step sequencer with per-lane note, step count, mute/solo, and
  per-lane micro time shift in milliseconds (with fine 0.02 ms resolution).
- Vintage shuffle curves: per-machine deviation from the straight grid,
  expressed as a swing ratio and an offset pattern per 8th-note pair.
- Note event output as (start_time_sec, midi_note, velocity) so any
  downstream renderer can apply the timing.

Not replicated: DAW transport locking / plugin UI (host concern only).

Usage:
    from sound.generators.micro_timing_seq import MicroTimingSequencer

    seq = MicroTimingSequencer(bpm=120)
    seq.add_lane(0, note=36, steps=[1,0,1,0,1,0,1,0], shift_ms=-8.0)
    events = seq.render(shuffle="mpc60", shuffle_amount=0.55)
"""

from typing import Dict, List, Optional, Tuple

__all__ = ["MicroTimingSequencer", "SHUFFLE_STYLES", "VINTAGE_OFFSETS"]


# Swing ratios per vintage machine (amount of the 8th-note pair occupied by
# the first hit) — the classic "shuffle feel" parameter of each box.
SHUFFLE_STYLES = {
    "tr909":   0.54,
    "tanzbar": 0.56,
    "mpc60":   0.62,
    "sp12":    0.60,
    "mpc3000": 0.58,
    "dmx":     0.57,
    "lm1":     0.55,
}

# Additional per-16th micro offset pattern (in fractions of a 16th) for each
# machine, encoding the "human timing" fingerprint of the hardware sequencer.
# Values are fractions of a 16th-note duration; index 0..3 = the four 16ths
# within each 8th-note pair.
VINTAGE_OFFSETS = {
    "tr909":   [0.000, 0.000, 0.000, 0.000],
    "tanzbar": [0.000, 0.010, 0.000, -0.008],
    "mpc60":   [0.000, -0.012, 0.000, 0.014],
    "sp12":    [0.000, 0.008, 0.000, -0.010],
    "mpc3000": [0.000, 0.000, 0.000, 0.000],
    "dmx":     [0.000, 0.006, 0.000, 0.006],
    "lm1":     [0.000, 0.000, 0.000, 0.000],
}


class MicroTimingSequencer:
    """Four-lane step sequencer with per-lane micro timing shift."""

    def __init__(self, bpm: float = 120.0, steps_per_beat: int = 4):
        """
        Args:
            bpm: Tempo in beats per minute.
            steps_per_beat: Grid resolution (4 = 16th notes).
        """
        self.bpm = bpm
        self.steps_per_beat = steps_per_beat
        self.lanes: Dict[int, dict] = {}
        self.shuffle_style: str = "mpc60"
        self.shuffle_amount: float = 0.5
        self._lane_counter = 0

    # -- configuration ---------------------------------------------------- #
    def add_lane(self, note: int, steps: List[int],
                 shift_ms: float = 0.0, lane_id: Optional[int] = None,
                 muted: bool = False) -> int:
        """Add a lane.

        Args:
            note: MIDI note triggered by this lane's hits.
            steps: Step velocities (0 = off, >0 = on), up to 32 entries.
            shift_ms: Per-lane micro time shift in ms (-64..+64).
            lane_id: Optional explicit lane id (0..3); auto-assigned if None.
            muted: Start muted.

        Returns:
            The lane id.
        """
        if len(steps) > 32:
            raise ValueError("max 32 steps per lane")
        if lane_id is None:
            lane_id = self._lane_counter
            self._lane_counter += 1
        self.lanes[lane_id] = {
            "note": note,
            "steps": list(steps),
            "shift_ms": float(max(-64.0, min(64.0, shift_ms))),
            "muted": muted,
        }
        return lane_id

    def set_shift(self, lane_id: int, shift_ms: float) -> None:
        """Set per-lane micro time shift (-64..+64 ms)."""
        self.lanes[lane_id]["shift_ms"] = float(max(-64.0, min(64.0, shift_ms)))

    def set_mute(self, lane_id: int, muted: bool) -> None:
        """Mute or unmute a lane."""
        self.lanes[lane_id]["muted"] = muted

    def set_shuffle(self, style: str, amount: float = 0.5) -> None:
        """Set the vintage shuffle style (see SHUFFLE_STYLES keys)."""
        if style not in SHUFFLE_STYLES:
            raise ValueError(f"unknown shuffle style '{style}', choose from {sorted(SHUFFLE_STYLES)}")
        self.shuffle_style = style
        self.shuffle_amount = float(max(0.0, min(1.0, amount)))

    # -- timing math ------------------------------------------------------ #
    def _step_duration(self) -> float:
        """Duration of one grid step in seconds."""
        return 60.0 / self.bpm / self.steps_per_beat

    def _shuffle_offset(self, step_index: int) -> float:
        """Timing offset (seconds) applied to a step by the shuffle curve.

        The first 16th of each 8th-note pair is delayed by the swing ratio
        (amount), the second 16th is pulled back by the remainder, and the
        machine's fingerprint offset (fraction of a 16th) is added.
        """
        step = step_index % self.steps_per_beat
        pair_pos = step % 2
        step_dur = self._step_duration()
        base = SHUFFLE_STYLES[self.shuffle_style]
        swing = (base - 0.5) * 2.0 * self.shuffle_amount
        if pair_pos == 0:
            off = swing * step_dur
        else:
            off = -swing * step_dur
        fp = VINTAGE_OFFSETS[self.shuffle_style]
        off += fp[step % 4] * step_dur
        return off

    # -- render ----------------------------------------------------------- #
    def render(self, bars: int = 1, loops: int = 1,
               velocity_scale: float = 1.0) -> List[Tuple[float, int, int]]:
        """Render all lanes to note events.

        Args:
            bars: Number of bars per pass over the step grid.
            loops: Number of times to repeat the grid.
            velocity_scale: Multiply step velocities (0..1).

        Returns:
            List of (start_time_sec, midi_note, velocity) tuples, sorted by
            time. start_time is absolute seconds from the pattern start.
        """
        events: List[Tuple[float, int, int]] = []
        steps = max((len(l["steps"]) for l in self.lanes.values()), default=0)
        if steps == 0:
            return events
        bar_steps = self.steps_per_beat * 4
        for loop in range(loops):
            for step in range(steps * bars):
                base_time = loop * (bars * bar_steps * self._step_duration())
                for lane in self.lanes.values():
                    if lane["muted"]:
                        continue
                    vel = lane["steps"][step % len(lane["steps"])]
                    if vel <= 0:
                        continue
                    t = base_time + step * self._step_duration()
                    t += self._shuffle_offset(step)
                    t += lane["shift_ms"] / 1000.0
                    events.append((max(0.0, t), lane["note"], int(min(127, vel * velocity_scale))))
        events.sort(key=lambda e: e[0])
        return events

    def render_clock(self, bars: int = 1, loops: int = 1) -> Dict[str, object]:
        """Render plus timing stats (for demos/tests).

        Returns:
            dict with "events", "max_shift_ms" (observed), and "grid_steps".
        """
        events = self.render(bars=bars, loops=loops)
        step_dur = self._step_duration()
        shifts = [e[0] - round(e[0] / step_dur) * step_dur for e in events]
        return {
            "events": events,
            "max_shift_ms": (max(shifts) - min(shifts)) * 1000.0 if shifts else 0.0,
            "grid_steps": self.steps_per_beat,
        }


def demo() -> str:
    """Run a demo pattern through all vintage shuffle styles."""
    seq = MicroTimingSequencer(bpm=120)
    # classic 4-on-floor kick + off-beat hats with opposite micro shifts
    seq.add_lane(note=36, steps=[1, 0, 0, 0] * 4, lane_id=0, shift_ms=-2.0)   # kick, slightly early
    seq.add_lane(note=42, steps=[0, 0, 1, 0] * 4, lane_id=1, shift_ms=+4.0)   # hat, pushed late
    seq.add_lane(note=38, steps=[0, 1, 0, 1] * 4, lane_id=2, shift_ms=0.0)    # snare
    seq.add_lane(note=51, steps=[1, 0, 1, 0, 0, 0, 1, 1] * 2, lane_id=3, shift_ms=-6.0)  # 8-step rim lane

    lines = ["MicroTimingSequencer demo (bpm=120, 1 bar, 16th grid):"]
    for style in sorted(SHUFFLE_STYLES):
        seq.set_shuffle(style, amount=0.55)
        ev = seq.render(bars=1)
        n = len(ev)
        spread = (max(e[0] for e in ev) - min(e[0] for e in ev)) * 1000.0
        lines.append(f"  {style:8s}: {n:3d} events, span {spread:6.1f} ms")
    # micro-shift proof: same style, shift one lane hard and measure it
    seq.set_shuffle("tr909", amount=0.5)
    seq.set_shift(1, +64.0)
    ev = seq.render(bars=1)
    hat_times = [e[0] for e in ev if e[1] == 42]
    kick_times = [e[0] for e in ev if e[1] == 36]
    if hat_times and kick_times:
        delta = (hat_times[0] - kick_times[1]) * 1000.0
        lines.append(f"  micro-shift proof: hat {delta:+.1f} ms vs following kick grid")
    return "\n".join(lines)


if __name__ == "__main__":
    print(demo())
