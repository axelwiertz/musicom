# -*- coding: utf-8 -*-
"""
Fractal Sequence Generator — melodic/hythmic material from recursive/chaotic systems.

Replicates the FRACTAL composition system from the Kaona B.A.C.H. module:
- Thue-Morse sequence → binary pitch contour (+1/0 semitone steps)
- Fibonacci sequence → rhythm/metric grouping patterns
- Sierpinski triangle ternary → note density/accents
- Logistic map (bifurcation / chaotic map) → chaotic pitch sequence

Each generator produces a list of (pitch, start_tick, duration_ticks, velocity)
events suitable for the musicom pipeline.

References:
    Kaona B.A.C.H. — Fractal system: "recursive sequences and chaotic systems,
    including Thue–Morse, Fibonacci, Sierpiński and the logistic map."
"""

import numpy as np
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ===========================================================================
# Fractal Sequence Generators
# ===========================================================================

@dataclass
class FractalEvent:
    """A single note event from a fractal generator."""
    pitch: int           # MIDI pitch (0-127)
    start_tick: int      # tick offset
    duration_ticks: int  # note duration in ticks
    velocity: int        # MIDI velocity (0-127)


# ---------------------------------------------------------------------------
# 1. Thue-Morse sequence
# ---------------------------------------------------------------------------

def thue_morse_bit(n: int) -> int:
    """Return the n-th Thue-Morse bit (0 or 1)."""
    return bin(n).count("1") & 1


def thue_morse_seq(length: int) -> np.ndarray:
    """Generate Thue-Morse sequence of given length as 0/1 array."""
    return np.array([thue_morse_bit(i) for i in range(length)], dtype=np.int8)


class ThueMorseMelody:
    """Binary pitch contour from Thue-Morse sequence.

    Maps 0/1 to +1 or -1 semitone steps from a root pitch, creating
    a non-repeating binary pattern that never has a period-3 run.

    Parameters
    ----------
    root_pitch : int
        Starting MIDI pitch.
    length : int
        Number of notes to generate.
    ticks_per_note : int
        Tick duration per event.
    ticks_per_beat : int
        Tick resolution (default 480).
    """

    def __init__(self, root_pitch: int = 60, length: int = 32,
                 ticks_per_note: int = 480, ticks_per_beat: int = 480):
        self.root_pitch = root_pitch
        self.length = length
        self.ticks_per_note = ticks_per_note
        self.ticks_per_beat = ticks_per_beat

    def generate(self) -> List[FractalEvent]:
        """Generate Thue-Morse pitch contour events."""
        bits = thue_morse_seq(self.length)
        events = []
        pitch = self.root_pitch
        for i in range(self.length):
            step = 1 if bits[i] else -1
            pitch += step
            pitch = max(0, min(127, pitch))
            events.append(FractalEvent(
                pitch=pitch,
                start_tick=i * self.ticks_per_note,
                duration_ticks=self.ticks_per_note,
                velocity=100,
            ))
        return events


# ---------------------------------------------------------------------------
# 2. Fibonacci rhyhm grouping
# ---------------------------------------------------------------------------

class FibonacciRhythm:
    """Rhythmic grouping pattern from Fibonacci numbers.

    Fibonacci numbers (1, 2, 3, 5, 8, 13, 21, ...) determine note durations.
    Each Fibonacci number forms a group; the sequence cycles through
    selected Fibonacci numbers to create an irregular metric feel.

    Parameters
    ----------
    fib_indices : list of int
        Indices into the Fibonacci sequence to use as beat-group lengths.
        e.g. [2, 3, 5] = groups of 3, 5, 8 beats.
    base_ticks : int
        Ticks per beat (default = ticks_per_beat).
    root_pitch : int
        Base MIDI pitch.
    repeats : int
        How many times to cycle through the pattern.
    """

    FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    def __init__(self, fib_indices: List[int] = None,
                 base_ticks: int = 480,
                 root_pitch: int = 48,
                 repeats: int = 4):
        self.fib_indices = fib_indices or [2, 3, 5]  # 2, 3, 5
        self.base_ticks = base_ticks
        self.root_pitch = root_pitch
        self.repeats = repeats

    def generate(self) -> List[FractalEvent]:
        """Generate rhythmic events grouped by Fibonacci durations."""
        events = []
        tick = 0
        for cycle in range(self.repeats):
            for fi in self.fib_indices:
                group_len = self.FIB[fi]
                group_duration = group_len * self.base_ticks  # ticks
                # One note per group at start of group (accented)
                vel = 110 if group_len > 2 else 90  # longer groups louder
                events.append(FractalEvent(
                    pitch=self.root_pitch + 12,
                    start_tick=tick,
                    duration_ticks=max(120, group_duration // 2),
                    velocity=vel,
                ))
                # Subdivisions: note per beat within group (lower vel)
                for beat in range(1, group_len):
                    bt = tick + beat * self.base_ticks
                    events.append(FractalEvent(
                        pitch=self.root_pitch,
                        start_tick=bt,
                        duration_ticks=max(60, self.base_ticks // 2),
                        velocity=70,
                    ))
                tick += group_duration
        return events


# ---------------------------------------------------------------------------
# 3. Sierpinski density
# ---------------------------------------------------------------------------

class SierpinskiAccent:
    """Note density and accent pattern from Sierpinski triangle.

    Uses Pascal's triangle parity (Rule 90 cellular automaton) to determine
    which beats in a bar are accented (odd == 1 == accented).

    Parameters
    ----------
    rows : int
        Number of Sierpinski rows to generate (bars).
    beats_per_bar : int
        Number of beats/positions per row (default 16 = 16th notes in 4/4).
    pitches : tuple of (int, int, int)
        (accent_pitch, normal_pitch, soft_pitch) in MIDI.
    """

    def __init__(self, rows: int = 8, beats_per_bar: int = 16,
                 pitches: Tuple[int, int, int] = (72, 60, 48)):
        self.rows = rows
        self.beats_per_bar = beats_per_bar
        self.accent_pitch, self.normal_pitch, self.soft_pitch = pitches

    def generate(self) -> List[FractalEvent]:
        """Generate accent events by Sierpinski density pattern."""
        # Rule 90: row[n+1][j] = row[n][j-1] ^ row[n][j+1]
        n = self.beats_per_bar
        grid = np.zeros((self.rows, n), dtype=np.int8)
        # Seed: single 1 at center of row 0
        grid[0, n // 2] = 1

        for r in range(1, self.rows):
            for c in range(n):
                left = grid[r - 1, (c - 1) % n]
                right = grid[r - 1, (c + 1) % n]
                grid[r, c] = left ^ right

        # Map to events
        events = []
        ticks_per_pos = 480 // (n // 4)  # assume n = 16 positions in 4/4
        for r in range(self.rows):
            for c in range(n):
                start = r * 1920 + c * ticks_per_pos  # 1920 ticks/bar
                if grid[r, c] == 1:
                    pitch = self.accent_pitch
                    vel = 110
                else:
                    # Even cell: position determines density
                    # Cells surrounded by 1s get normal, isolated 0s get soft
                    neighbors = 0
                    for dc in [-1, 1]:
                        nc = (c + dc) % n
                        if r > 0 and grid[r - 1, nc] == 1:
                            neighbors += 1
                    if neighbors >= 2:
                        pitch = self.normal_pitch
                        vel = 85
                    else:
                        pitch = self.soft_pitch
                        vel = 55
                events.append(FractalEvent(
                    pitch=pitch,
                    start_tick=start,
                    duration_ticks=max(60, ticks_per_pos // 2),
                    velocity=vel,
                ))
        return events


# ---------------------------------------------------------------------------
# 4. Logistic map chaos
# ---------------------------------------------------------------------------

class LogisticMapMelody:
    """Chaotic pitch and rhythm sequence from the logistic map.

    Logistic map: x_{n+1} = r * x_n * (1 - x_n)
    Produces chaotic behavior at r ≈ 3.57..4.0.

    Parameters
    ----------
    r : float
        Growth parameter (3.6–4.0 for chaos).
    x0 : float
        Initial value (0..1).
    length : int
        Number of events.
    pitch_range : tuple of (int, int)
        Min and max MIDI pitch.
    ticks_per_beat : int
        Resolution.
    """

    def __init__(self, r: float = 3.9, x0: float = 0.5,
                 length: int = 64,
                 pitch_range: Tuple[int, int] = (36, 96),
                 ticks_per_beat: int = 480):
        self.r = r
        self.x0 = x0
        self.length = length
        self.pitch_min, self.pitch_max = pitch_range
        self.ticks_per_beat = ticks_per_beat

    def generate(self) -> List[FractalEvent]:
        """Generate chaotic pitch events from logistic map orbit."""
        events = []
        x = self.x0
        # Burn-in
        for _ in range(50):
            x = self.r * x * (1.0 - x)

        for i in range(self.length):
            x = self.r * x * (1.0 - x)
            # Pitch
            p_range = self.pitch_max - self.pitch_min
            pitch = self.pitch_min + int(x * p_range)
            pitch = max(0, min(127, pitch))

            # Duration from previous x (chaotic rhythm)
            prev_x = x
            x = self.r * x * (1.0 - x)
            dur_factor = 0.25 + 1.5 * abs(prev_x)  # 0.25..1.75
            dur_ticks = max(120, int(dur_factor * self.ticks_per_beat))

            # Velocity from x
            vel = max(40, min(127, int(40 + 87 * prev_x)))

            events.append(FractalEvent(
                pitch=pitch,
                start_tick=i * dur_ticks,
                duration_ticks=dur_ticks,
                velocity=vel,
            ))
        return events


# ---------------------------------------------------------------------------
# Combined fractal sequence generator
# ---------------------------------------------------------------------------

class FractalSequenceGenerator:
    """Combined generator that can produce from any fractal subsystem.

    Wraps the four generators: thue_morse, fibonacci, sierpinski, logistic.
    """

    GENERATORS = ("thue_morse", "fibonacci", "sierpinski", "logistic")

    def __init__(self, generator_type: str = "logistic", **kwargs):
        if generator_type not in self.GENERATORS:
            raise ValueError(f"generator_type must be one of {self.GENERATORS}")

        if generator_type == "thue_morse":
            self._gen = ThueMorseMelody(**{k: v for k, v in kwargs.items()
                                           if k in ("root_pitch", "length",
                                                     "ticks_per_note",
                                                     "ticks_per_beat")})
        elif generator_type == "fibonacci":
            self._gen = FibonacciRhythm(**{k: v for k, v in kwargs.items()
                                           if k in ("fib_indices", "base_ticks",
                                                     "root_pitch", "repeats")})
        elif generator_type == "sierpinski":
            self._gen = SierpinskiAccent(**{k: v for k, v in kwargs.items()
                                            if k in ("rows", "beats_per_bar",
                                                      "pitches")})
        elif generator_type == "logistic":
            self._gen = LogisticMapMelody(**{k: v for k, v in kwargs.items()
                                             if k in ("r", "x0", "length",
                                                       "pitch_range",
                                                       "ticks_per_beat")})

    def generate(self) -> List[FractalEvent]:
        return self._gen.generate()


# ---------------------------------------------------------------------------
# MIDI export helper
# ---------------------------------------------------------------------------

def events_to_midi(events: List[FractalEvent],
                   output_path: str,
                   ticks_per_beat: int = 480,
                   tempo_bpm: int = 120,
                   track_name: str = "Fractal Sequence"):
    """Write FractalEvent list to a MIDI file using stdlib only.

    Format: single-track Type 0 MIDI file.
    """
    import struct

    # Build track events
    track_data = bytearray()
    # Tempo meta
    tempo_us = int(60_000_000 / tempo_bpm)
    track_data.extend([
        0x00, 0xFF, 0x51, 0x03,
        (tempo_us >> 16) & 0xFF, (tempo_us >> 8) & 0xFF, tempo_us & 0xFF,
    ])
    # Track name
    name_bytes = track_name.encode('ascii', errors='replace')
    track_data.extend([0x00, 0xFF, 0x03, len(name_bytes)])
    track_data.extend(name_bytes)

    # Sort events by start_tick
    sorted_events = sorted(events, key=lambda e: e.start_tick)

    for ev in sorted_events:
        # Delta time (variable length)
        delta = ev.start_tick
        # Variable-length encoding
        vl = []
        val = delta
        while True:
            vl.insert(0, val & 0x7F)
            if val < 128:
                break
            val >>= 7
        for i in range(len(vl)):
            if i < len(vl) - 1:
                track_data.append(vl[i] | 0x80)
            else:
                track_data.append(vl[i])

        # Note on
        vel = max(0, min(127, int(ev.velocity)))
        pit = max(0, min(127, int(ev.pitch)))
        track_data.extend([0x90, pit, vel])

        # Note off after duration
        dur = max(1, ev.duration_ticks)
        # Variable-length for duration
        vl_dur = []
        val = dur
        while True:
            vl_dur.insert(0, val & 0x7F)
            if val < 128:
                break
            val >>= 7
        for i in range(len(vl_dur)):
            if i < len(vl_dur) - 1:
                track_data.append(vl_dur[i] | 0x80)
            else:
                track_data.append(vl_dur[i])
        note_off_vel = 0
        track_data.extend([0x80, pit, note_off_vel])

    # End of track
    track_data.extend([0x00, 0xFF, 0x2F, 0x00])

    # MIDI file header
    header_size = 14
    data_size = len(track_data)
    tpb = ticks_per_beat

    with open(output_path, 'wb') as f:
        f.write(b'MThd')
        f.write(struct.pack('>I', header_size - 8))
        f.write(struct.pack('>HHH', 0, 1, tpb))  # Type 0, 1 track, tpb
        f.write(b'MTrk')
        f.write(struct.pack('>I', data_size))
        f.write(track_data)

    return output_path


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    """Run all four fractal generators and produce MIDI + summary."""
    import os, sys

    print("=== Fractal Sequence Generator Demo ===")
    out_dir = "/tmp"
    results = []

    # 1. Thue-Morse pitch contour
    print("\n1. Thue-Morse Melody (64 notes)")
    tm = ThueMorseMelody(root_pitch=60, length=64, ticks_per_note=240)
    ev_tm = tm.generate()
    path_tm = os.path.join(out_dir, "fractal_thue_morse.mid")
    events_to_midi(ev_tm, path_tm, track_name="Thue-Morse")
    results.append(("thue_morse", len(ev_tm), path_tm))
    print(f"   {len(ev_tm)} events → {path_tm}")

    # 2. Fibonacci rhythm groups
    print("\n2. Fibonacci Rhythm (groups 2,3,5 beats × 4 cycles)")
    fb = FibonacciRhythm(fib_indices=[2, 3, 5], base_ticks=480,
                         root_pitch=36, repeats=4)
    ev_fb = fb.generate()
    path_fb = os.path.join(out_dir, "fractal_fibonacci.mid")
    events_to_midi(ev_fb, path_fb, track_name="Fibonacci Rhythm")
    results.append(("fibonacci", len(ev_fb), path_fb))
    print(f"   {len(ev_fb)} events → {path_fb}")

    # 3. Sierpinski accent pattern
    print("\n3. Sierpinski Density (8 rows × 16 positions)")
    sa = SierpinskiAccent(rows=8, beats_per_bar=16,
                          pitches=(72, 60, 48))
    ev_sa = sa.generate()
    path_sa = os.path.join(out_dir, "fractal_sierpinski.mid")
    events_to_midi(ev_sa, path_sa, track_name="Sierpinski Accent")
    results.append(("sierpinski", len(ev_sa), path_sa))
    print(f"   {len(ev_sa)} events → {path_sa}")

    # 4. Logistic map chaos
    print("\n4. Logistic Map Melody (r=3.9, 64 events)")
    lm = LogisticMapMelody(r=3.9, length=64, pitch_range=(36, 96))
    ev_lm = lm.generate()
    path_lm = os.path.join(out_dir, "fractal_logistic.mid")
    events_to_midi(ev_lm, path_lm, track_name="Logistic Map")
    results.append(("logistic", len(ev_lm), path_lm))
    print(f"   {len(ev_lm)} events → {path_lm}")

    # Summary
    print("\n=== Summary ===")
    for name, count, path in results:
        size = os.path.getsize(path)
        print(f"  {name:15s}: {count:3d} events, {size:6d} bytes → {path}")

    print("\nFractal Sequence Generator demo complete.")
    return results


if __name__ == "__main__":
    demo()