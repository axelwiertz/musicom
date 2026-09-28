"""Euclidean Fill Sequencer (Maschine 3.7-style).

Extends the basic Bjorklund Euclidean rhythm algorithm with two features
from Native Instruments Maschine 3.7 (September 2026 release):

1. **Fills** — extra lower-probability hits inserted into the empty
   ("rest") steps of the Euclidean pattern.  A fill density parameter
   controls how many of the empty slots get filled, and fill hits have
   lower velocity than the primary Euclidean pulses.

2. **Live rotation** — the Euclidean pattern can be rotated in real time
   (shifted left or right) while the loop plays, allowing the groove to
   be re-arranged without stopping.

The module is self-contained: pure Python/numpy, no external MIDI library
needed.

SP-095 (surveillance 2026-09-28).
"""

import numpy as np
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import random
import struct


# ---------------------------------------------------------------------------
# Bjorklund algorithm (standard)
# ---------------------------------------------------------------------------

def bjorklund(pulses: int, steps: int) -> List[int]:
    """Generate a Euclidean rhythm pattern using the Bjorklund algorithm.

    Distributes ``pulses`` ones as evenly as possible across ``steps``
    positions.  Returns a list of 0/1 ints of length ``steps``.

    This is the standard algorithm used by EuclideanCore in event_core.py
    (here kept as a standalone function for import without the EventCore
    class overhead).
    """
    if pulses <= 0:
        return [0] * steps
    if pulses >= steps:
        return [1] * steps

    pattern = []
    bucket = 0
    for _ in range(steps):
        bucket += pulses
        if bucket >= steps:
            bucket -= steps
            pattern.append(1)
        else:
            pattern.append(0)
    return pattern


# ---------------------------------------------------------------------------
# Euclidean Fill Sequencer
# ---------------------------------------------------------------------------

@dataclass
class EuclideanFillSequencer:
    """Euclidean rhythm generator with fills and live rotation.

    Parameters
    ----------
    pulses : int, default=5
        Number of primary hits in the Euclidean pattern.
    steps : int, default=16
        Total number of steps in the pattern.
    rotation : int, default=0
        Initial rotation offset (steps to shift left).
    fill_density : float, default=0.3
        Probability (0..1) that each empty (rest) step receives a fill hit.
    fill_velocity_factor : float, default=0.6
        Velocity scaling for fill hits relative to primary hits (0..1).
    primary_velocity_range : Tuple[int, int], default=(100, 127)
        Min/max velocity for primary Euclidean hits.
    swing : float, default=0.0
        Swing amount (0..1).  Even-indexed steps are shifted later by
        ``swing * (step_duration/2)``; odd-indexed steps are shorter by
        the same amount.
    seed : Optional[int], default=None
        Random seed for fill generation reproducibility.
    """
    pulses: int = 5
    steps: int = 16
    rotation: int = 0
    fill_density: float = 0.3
    fill_velocity_factor: float = 0.6
    primary_velocity_range: Tuple[int, int] = (100, 127)
    swing: float = 0.0
    seed: Optional[int] = None

    def __post_init__(self):
        self._rng = random.Random(self.seed)
        self._base_pattern: List[int] = []  # cached raw pattern
        self._cached_for: Tuple[Optional[int], Optional[int]] = (None, None)

    def _get_base(self) -> List[int]:
        """Get or compute the Euclidean base pattern with current rotation."""
        if self._base_pattern and self._cached_for == (self.pulses, self.steps):
            pattern = self._base_pattern[:]
        else:
            pattern = bjorklund(self.pulses, self.steps)
            self._base_pattern = pattern[:]
            self._cached_for = (self.pulses, self.steps)

        # Apply rotation
        if self.rotation != 0:
            rot = self.rotation % self.steps
            pattern = pattern[rot:] + pattern[:rot]

        return pattern

    def regenerate(self) -> List[int]:
        """Recompute the base pattern (after changing pulses/steps/rotation).

        Returns the current binary pattern (0=rest, 1=primary hit).
        """
        self._base_pattern = bjorklund(self.pulses, self.steps)
        self._cached_for = (self.pulses, self.steps)
        return self._get_base()

    def rotate(self, offset: int):
        """Set rotation offset (live rotation)."""
        self.rotation = offset % self.steps

    def rotate_by(self, delta: int):
        """Add ``delta`` to current rotation (positive = shift left)."""
        self.rotation = (self.rotation + delta) % self.steps

    def set_pulses(self, n: int):
        """Change the number of primary hits (live update)."""
        self.pulses = max(0, min(self.steps, n))

    def set_fill_density(self, density: float):
        """Set fill density (0..1)."""
        self.fill_density = max(0.0, min(1.0, density))

    def generate(self, num_bars: int = 1,
                 time_per_step: int = 120) -> List[Dict]:
        """Generate a sequence of hit events with fills.

        Parameters
        ----------
        num_bars : int, default=1
            Number of times to repeat the Euclidean pattern.
        time_per_step : int, default=120 (32nd note at 480 tpb, 4/4)
            Tick duration of each step slot.

        Returns
        -------
        List[Dict]
            Each dict: pitch (60 for rim/kick placeholder), start, duration,
            velocity, is_fill.
        """
        base = self._get_base()
        total_steps = self.steps
        events: List[Dict] = []

        for bar in range(num_bars):
            for step_idx in range(total_steps):
                abs_step = bar * total_steps + step_idx
                step_is_hit = base[step_idx]

                # Apply swing offset
                start_tick = abs_step * time_per_step
                if self.swing > 0 and step_idx % 2 == 1:
                    # Even-indexed last longer, odd-indexed shorter
                    swing_offset = int(self.swing * time_per_step * 0.5)
                    start_tick += swing_offset

                dur = max(time_per_step // 2, time_per_step - 1)  # mostly staccato-ish

                if step_is_hit:
                    # Primary Euclidean hit
                    vel = self._rng.randint(
                        self.primary_velocity_range[0],
                        self.primary_velocity_range[1] + 1
                    )
                    events.append({
                        "pitch": 60,
                        "start": start_tick,
                        "duration": dur,
                        "velocity": vel,
                        "is_fill": False,
                    })
                elif self.fill_density > 0 and self._rng.random() < self.fill_density:
                    # Fill hit on an empty step
                    fill_vel = max(1, int(
                        self.primary_velocity_range[0]
                        * self.fill_velocity_factor
                    ))
                    events.append({
                        "pitch": 60,
                        "start": start_tick,
                        "duration": dur,
                        "velocity": fill_vel,
                        "is_fill": True,
                    })

        return events

    def generate_hit_mask(self, num_bars: int = 1) -> List[float]:
        """Return a simple numeric hit mask (pulse = velocity, fill = vel*factor).

        Useful for quick inspection without event dicts.
        """
        events = self.generate(num_bars)
        total = num_bars * self.steps
        mask = [0.0] * total
        tick_per = 120  # assume default
        for ev in events:
            idx = ev["start"] // tick_per
            if 0 <= idx < total:
                mask[idx] = max(mask[idx], ev["velocity"] / 127.0)
        return mask

    def generate_midi(self, num_bars: int = 1,
                      ticks_per_quarter: int = 480,
                      pitch: int = 60) -> bytes:
        """Export the generated pattern as a single-track SMF.

        Parameters
        ----------
        num_bars : int
            Number of pattern repetitions.
        ticks_per_quarter : int, default=480
            PPQ.
        pitch : int, default=60
            MIDI pitch for the hits (kick/rim/clave).

        Returns
        -------
        bytes
            Standard MIDI File.
        """
        events = self.generate(num_bars,
                               time_per_step=ticks_per_quarter // 4)  # 16th
        return _euclid_events_to_midi(events, pitch, ticks_per_quarter)


# ---------------------------------------------------------------------------
# MIDI export
# ---------------------------------------------------------------------------

def _euclid_events_to_midi(events: List[Dict], pitch: int,
                            ticks_per_quarter: int) -> bytes:
    """Convert Euclidean hit events to Type-0 SMF bytes."""
    if not events:
        events = [{"pitch": pitch, "start": 0, "duration": ticks_per_quarter // 4,
                   "velocity": 0, "is_fill": False}]

    sorted_ev = sorted(events, key=lambda e: e["start"])

    track_data = bytearray()
    tick = 0
    track_end = 0

    # Tempo meta (120 BPM)
    track_data.extend(_evlq(0))
    track_data.extend(b'\xff\x51\x03')
    track_data.extend(struct.pack('>I', 500000)[1:])

    for ev in sorted_ev:
        delta = ev["start"] - tick
        if delta >= 0:
            track_data.extend(_evlq(delta))
        else:
            track_data.extend(_evlq(0))
        track_data.extend(bytes([0x90, pitch, max(1, min(127, ev["velocity"]))]))
        track_end = max(track_end, ev["start"] + ev["duration"])
        tick = ev["start"]

    tick = 0
    for ev in sorted_ev:
        off_tick = ev["start"] + ev["duration"]
        delta = off_tick - tick
        if delta > 0:
            track_data.extend(_evlq(delta))
        track_data.extend(bytes([0x80, pitch, 0]))
        tick = off_tick

    track_data.extend(_evlq(max(1, track_end - tick)))
    track_data.extend(b'\xff\x2f\x00')

    header = b'MThd' + struct.pack('>I', 6) + struct.pack('>HHH', 0, 1,
                                                           ticks_per_quarter)
    track_chunk = b'MTrk' + struct.pack('>I', len(track_data)) + track_data
    return header + track_chunk


def _evlq(value: int) -> bytes:
    """VLQ for MIDI delta."""
    if value < 0:
        value = 0
    buf = bytearray()
    while True:
        v = value & 0x7f
        value >>= 7
        if value:
            v |= 0x80
        buf.append(v)
        if value == 0:
            break
    return bytes(buf)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    """Smoke-test Euclidean Fill Sequencer."""
    print("=== EuclideanFillSequencer Demo ===\n")

    efs = EuclideanFillSequencer(
        pulses=5,
        steps=16,
        fill_density=0.4,
        seed=123,
    )

    # Show base pattern
    base = efs._get_base()
    print(f"Euclidean(5,16) base: {''.join(str(b) for b in base)}")
    print(f"  rotation={efs.rotation}, fill_density={efs.fill_density}")

    # Generate 1 bar of events
    events = efs.generate(num_bars=2)
    primary = [e for e in events if not e["is_fill"]]
    fills = [e for e in events if e["is_fill"]]
    print(f"\n2 bars: {len(primary)} primary hits + {len(fills)} fills = {len(events)} total")

    # Generate hit mask for visualisation
    mask = efs.generate_hit_mask(num_bars=2)
    # Show mask as ASCII
    vis = ''.join('X' if m > 0.7 else 'x' if m > 0.2 else '.' for m in mask)
    print(f"\nHit mask (X=primary, x=fill, .=rest):")
    print(f"  {vis[:16]} |{vis[16:32]}")

    # Test live rotation
    efs.rotate(4)
    base_r4 = efs._get_base()
    print(f"\nRotation=4: {''.join(str(b) for b in base_r4)}")

    efs.rotate(0)
    efs.set_pulses(7)
    base_7 = efs._get_base()
    print(f"Pulses=7:   {''.join(str(b) for b in base_7)}")

    # MIDI export
    midi_bytes = efs.generate_midi(num_bars=2)
    print(f"\nMIDI file: {len(midi_bytes)} bytes (non-empty: {len(midi_bytes) > 40})")
    midi_path = "/tmp/euclidean_fill_seq_demo.mid"
    with open(midi_path, "wb") as f:
        f.write(midi_bytes)
    print(f"Wrote: {midi_path}")

    # Test with different fill density
    efs.set_fill_density(0.8)
    events_dense = efs.generate(num_bars=1)
    fills_dense = [e for e in events_dense if e["is_fill"]]
    print(f"\nfill_density=0.8: 1 bar = {len(fills_dense)} fills")


if __name__ == "__main__":
    demo()