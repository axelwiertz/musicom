"""Random Note Generator + Note Chance Sequencer (Maschine 3.7-style).

Two complementary tools inspired by Native Instruments Maschine 3.7
(September 2026 release):

1. RandomNoteGenerator — generates MIDI note sequences with configurable
   odds/pitch-range/scale-quantization, filling the grid from "nothing"
   rather than requiring a pre-existing pattern.

2. NoteChanceSequencer — wraps any existing note sequence and assigns
   per-note probability values; each loop iteration re-rolls every note
   independently, and any particular realisation can be "locked" to make
   it permanent.

Both avoid external ML dependencies — pure numpy + stdlib.

SP-094 (surveillance 2026-09-28).
"""

import numpy as np
from typing import List, Optional, Tuple, Dict, Callable
from dataclasses import dataclass, field
import random
import struct


# ---------------------------------------------------------------------------
# Chromatic scale helpers
# ---------------------------------------------------------------------------

CHROMATIC = np.array([60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71])

# Common scale intervals from root (semitones)
SCALE_INTERVALS = {
    "chromatic":       np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    "major":           np.array([0, 2, 4, 5, 7, 9, 11]),
    "minor":           np.array([0, 2, 3, 5, 7, 8, 10]),
    "pentatonic_major":np.array([0, 2, 4, 7, 9]),
    "pentatonic_minor":np.array([0, 3, 5, 7, 10]),
    "blues":           np.array([0, 3, 5, 6, 7, 10]),
    "phrygian":        np.array([0, 1, 3, 5, 7, 8, 10]),
    "lydian":          np.array([0, 2, 4, 6, 7, 9, 11]),
    "locrian":         np.array([0, 1, 3, 5, 6, 8, 10]),
    "whole_tone":      np.array([0, 2, 4, 6, 8, 10]),
    "diminished":      np.array([0, 2, 3, 5, 6, 8, 9, 11]),
    "augmented":       np.array([0, 3, 4, 7, 8, 11]),
}


def _scale_notes(root: int = 60, scale: str = "major") -> np.ndarray:
    """Return all MIDI notes in a given scale within MIDI range (0-127)."""
    intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["chromatic"])
    octaves = np.arange(-2, 10)  # covers MIDI range
    all_notes = []
    for oct in octaves:
        for iv in intervals:
            note = root + iv + oct * 12
            if 0 <= note < 128:
                all_notes.append(note)
    return np.array(sorted(set(all_notes)), dtype=int)


# ---------------------------------------------------------------------------
# 1. Random Note Generator
# ---------------------------------------------------------------------------

@dataclass
class RandomNoteGenerator:
    """Generates MIDI note sequences from configurable odds.

    Maschine 3.7 "Random Note Generator" concept: set the odds
    (density), pitch range, and optional scale, and get a sequence
    of MIDI notes back without needing a pre-existing pattern.

    Parameters
    ----------
    density : float, default=0.3
        Probability (0..1) that any given step slot is filled with a note.
    pitch_range : Tuple[int, int], default=(48, 84)
        Low/high MIDI note range for generated pitches.
    scale : str, default="chromatic"
        Scale name from SCALE_INTERVALS (e.g. "major", "minor", "blues").
        Pitches are quantized to this scale.
    root : int, default=60 (C4)
        Root note of the scale.
    velocity_range : Tuple[int, int], default=(64, 127)
        Min/max velocity for generated notes.
    max_octave_jump : int, default=2
        Maximum octave jump between consecutive notes (limits extremes
        when using sequential mode).
    seed : Optional[int], default=None
        Random seed for reproducibility.
    """
    density: float = 0.3
    pitch_range: Tuple[int, int] = (48, 84)
    scale: str = "chromatic"
    root: int = 60
    velocity_range: Tuple[int, int] = (64, 127)
    max_octave_jump: int = 2
    seed: Optional[int] = None

    def __post_init__(self):
        self._rng = random.Random(self.seed)
        self._np_rng = np.random.RandomState(self.seed)

    def generate(self, num_steps: int, time_per_step: int = 480,
                 sequential: bool = True) -> List[Dict]:
        """Generate a sequence of note events.

        Parameters
        ----------
        num_steps : int
            Number of step slots to generate.
        time_per_step : int, default=480 (one quarter note at 480 tpb)
            Tick duration of each step.
        sequential : bool, default=True
            If True, picks notes that move smoothly from the previous one.
            If False, picks from the full scale pool each step.

        Returns
        -------
        List[Dict]
            Each dict has keys: pitch, start, duration, velocity.
            ``start`` and ``duration`` are in ticks.
        """
        valid_notes = _scale_notes(self.root, self.scale)
        # Filter to pitch range
        valid_notes = valid_notes[(valid_notes >= self.pitch_range[0])
                                  & (valid_notes <= self.pitch_range[1])]
        if len(valid_notes) == 0:
            valid_notes = np.arange(self.pitch_range[0], self.pitch_range[1] + 1)

        events: List[Dict] = []
        prev_pitch: Optional[int] = None

        for i in range(num_steps):
            start = i * time_per_step
            dur = max(time_per_step // 2, 120)  # at least an eighth note-ish

            if self._rng.random() < self.density:
                # Pick a pitch
                if sequential and prev_pitch is not None:
                    # Bias toward nearby notes
                    candidates = valid_notes[
                        np.abs(valid_notes - prev_pitch)
                        <= self.max_octave_jump * 12
                    ]
                    if len(candidates) == 0:
                        candidates = valid_notes
                    pitch = int(self._rng.choice(candidates.tolist()))
                else:
                    pitch = int(self._rng.choice(valid_notes.tolist()))

                vel = self._rng.randint(
                    self.velocity_range[0], self.velocity_range[1] + 1
                )

                events.append({
                    "pitch": pitch,
                    "start": start,
                    "duration": dur,
                    "velocity": vel,
                })
                prev_pitch = pitch
            else:
                # Rest — no pitch generated
                pass

        return events

    def generate_midi(self, num_steps: int, time_per_step: int = 480,
                      sequential: bool = True) -> bytes:
        """Generate a Standard MIDI File (SMF) from the random notes.

        Returns
        -------
        bytes
            Tiny single-track Type-0 MIDI file.
        """
        from structures import MidiInstrument  # avoid top-level import cost

        events = self.generate(num_steps, time_per_step, sequential)
        return _events_to_midi(events, ticks_per_quarter=time_per_step)


# ---------------------------------------------------------------------------
# 2. Note Chance Sequencer
# ---------------------------------------------------------------------------

@dataclass
class NoteChanceSequencer:
    """Per-note chance re-roll engine (Maschine 3.7 Note Event Chance).

    Takes an existing note sequence and assigns a *chance* value (0..1)
    to each note.  On each call to ``reroll()`` every note is independently
    evaluated: if its chance roll succeeds the note is *active* for that
    loop iteration; otherwise it is silent.  Notes can be *locked* to
    force them active regardless of future rolls.

    This creates a "breathing" pattern that varies subtly each iteration
    while preserving the underlying musical structure.

    Parameters
    ----------
    events : List[Dict]
        Base note events (same format as RandomNoteGenerator output).
    default_chance : float, default=0.8
        Default per-note probability (0..1).
    lockable : bool, default=True
        If True, per-note locking is enabled.
    """
    events: List[Dict] = field(default_factory=list)
    default_chance: float = 0.8
    lockable: bool = True

    def __post_init__(self):
        self._chances: List[float] = []
        self._locked: List[bool] = []
        self._active: List[bool] = []
        self._rng = random.Random()
        self._init_chances()

    def _init_chances(self):
        """Assign chance and lock state for each event."""
        self._chances = [self.default_chance] * len(self.events)
        self._locked = [False] * len(self.events)
        self._active = [True] * len(self.events)

    def set_chance(self, index: int, chance: float):
        """Set chance value for a specific note.

        Parameters
        ----------
        index : int
            Event index.
        chance : float
            New probability (0..1).  Clipped to valid range.
        """
        if 0 <= index < len(self.events):
            self._chances[index] = max(0.0, min(1.0, chance))

    def set_chance_all(self, chance: float):
        """Set all note chances to the same value."""
        for i in range(len(self.events)):
            self._chances[i] = max(0.0, min(1.0, chance))

    def lock_note(self, index: int):
        """Lock a note so it is always active."""
        if self.lockable and 0 <= index < len(self.events):
            self._locked[index] = True
            self._active[index] = True  # immediately active

    def unlock_note(self, index: int):
        """Unlock a note so it returns to chance-based activity."""
        if self.lockable and 0 <= index < len(self.events):
            self._locked[index] = False

    def lock_all(self):
        """Lock every note (freeze the pattern)."""
        for i in range(len(self.events)):
            self.lock_note(i)

    def unlock_all(self):
        """Unlock every note."""
        for i in range(len(self.events)):
            self.unlock_note(i)

    def reroll(self) -> List[Dict]:
        """Re-roll every unlocked note's chance and return active events.

        Returns
        -------
        List[Dict]
            Subset of the original events that passed the chance roll for
            this iteration (plus all locked notes).
        """
        active: List[Dict] = []
        for i, ev in enumerate(self.events):
            if self._locked[i]:
                active.append(ev)
            else:
                # Re-roll
                self._active[i] = self._rng.random() < self._chances[i]
                if self._active[i]:
                    active.append(ev)
        return active

    def active_mask(self) -> List[bool]:
        """Return which notes are active for the current loop."""
        return [self._active[i] if i < len(self._active) else False
                for i in range(len(self.events))]

    def to_midi(self, rerolls: int = 4,
                ticks_per_quarter: int = 480) -> List[bytes]:
        """Generate multiple MIDI files, one per reroll iteration.

        Parameters
        ----------
        rerolls : int
            Number of re-roll iterations (each produces one MIDI file).
        ticks_per_quarter : int
            MIDI clock ticks per quarter note.

        Returns
        -------
        List[bytes]
            One SMF (bytes) per reroll, showing the pattern breathing.
        """
        files: List[bytes] = []
        for _ in range(rerolls):
            active = self.reroll()
            files.append(_events_to_midi(active, ticks_per_quarter))
        return files


# ---------------------------------------------------------------------------
# MIDI export helper
# ---------------------------------------------------------------------------

def _events_to_midi(events: List[Dict],
                    ticks_per_quarter: int = 480) -> bytes:
    """Convert event dicts to a Type-0 SMF byte string.

    Parameters
    ----------
    events : List[Dict]
        Must have keys: pitch, start, duration, velocity.
    ticks_per_quarter : int
        PPQ for the MIDI file.

    Returns
    -------
    bytes
        Complete SMF file.
    """
    if not events:
        # Write a silent one-beat MIDI to keep the pipeline happy
        events = [{"pitch": 60, "start": 0, "duration": ticks_per_quarter,
                   "velocity": 0}]

    # Sort by start tick
    sorted_ev = sorted(events, key=lambda e: e["start"])

    # Build track events
    track_data = bytearray()
    tick = 0
    track_end = 0

    # Tempo meta (120 BPM = 500000 microseconds per quarter)
    track_data.extend(_vlq(0))          # delta = 0
    track_data.extend(b'\xff\x51\x03')
    track_data.extend(struct.pack('>I', 500000)[1:])  # 120 BPM

    for ev in sorted_ev:
        delta = ev["start"] - tick
        track_data.extend(_vlq(delta))
        # Note On (channel 0)
        track_data.extend(bytes([0x90, ev["pitch"],
                          max(1, min(127, ev["velocity"]))]))
        track_end = max(track_end, ev["start"] + ev["duration"])
        tick = ev["start"]

    # Note Off for each note
    tick = 0
    for ev in sorted_ev:
        off_tick = ev["start"] + ev["duration"]
        delta = off_tick - tick
        if delta > 0:
            track_data.extend(_vlq(delta))
        track_data.extend(bytes([0x80, ev["pitch"], 0]))
        tick = off_tick

    # End of track
    track_data.extend(_vlq(max(1, track_end - tick)))
    track_data.extend(b'\xff\x2f\x00')

    # Assemble header
    track_len = len(track_data)
    header = b'MThd' + struct.pack('>I', 6) + struct.pack('>HHH', 0, 1,
                                                           ticks_per_quarter)
    track_chunk = b'MTrk' + struct.pack('>I', track_len) + track_data

    return header + track_chunk


def _vlq(value: int) -> bytes:
    """Encode a variable-length quantity (MIDI delta-time)."""
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
    """Smoke-test both generators and show MIDI output."""
    print("=== RandomNoteGenerator Demo ===\n")

    # 1. Random Note Generator — generate an 8-bar idea
    rng = RandomNoteGenerator(
        density=0.4,
        pitch_range=(48, 84),
        scale="minor",
        root=48,  # C3
        seed=42,
    )
    events = rng.generate(num_steps=32, time_per_step=480, sequential=True)
    print(f"Random notes generated: {len(events)} events")
    for ev in events[:8]:  # show first 8
        print(f"  pitch={ev['pitch']:3d}  start={ev['start']:5d}  "
              f"dur={ev['duration']:4d}  vel={ev['velocity']}")
    if len(events) > 8:
        print(f"  ... and {len(events)-8} more")

    midi_bytes = rng.generate_midi(num_steps=32)
    print(f"\nMIDI file: {len(midi_bytes)} bytes (non-empty: {len(midi_bytes) > 40})")
    midi_path = "/tmp/random_note_gen_demo.mid"
    with open(midi_path, "wb") as f:
        f.write(midi_bytes)
    print(f"Wrote: {midi_path}")

    # 2. Note Chance Sequencer
    print("\n=== NoteChanceSequencer Demo ===\n")
    ncs = NoteChanceSequencer(
        events=events,
        default_chance=0.7,
    )
    # Lock the first note
    if events:
        ncs.lock_note(0)

    for iteration in range(4):
        active = ncs.reroll()
        print(f"Iteration {iteration+1}: {len(active)}/{len(events)} notes active")
        for ev in active[:3]:
            print(f"  pitch={ev['pitch']:3d}  "

                   f"start={ev['start']:5d}")
        if len(active) > 3:
            print(f"  ... and {len(active)-3} more")

    # 3. Multi-reroll MIDI export
    midi_files = ncs.to_midi(rerolls=3)
    print(f"\nMulti-reroll MIDI: {len(midi_files)} files generated")
    for i, mf in enumerate(midi_files):
        path = f"/tmp/note_chance_{i}.mid"
        with open(path, "wb") as f:
            f.write(mf)
        print(f"  {path}: {len(mf)} bytes")

    print("\n--- Demo complete ---")


if __name__ == "__main__":
    demo()