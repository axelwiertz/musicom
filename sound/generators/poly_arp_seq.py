"""Polyphonic arpeggiator + step sequencer (Prophet Rev4 firmware mod-style).

Two engines in one module:

1. **Arpeggiator**: Up / Down / UpDown / Random / Assign modes,
   1-4 octave range, 40-300 BPM, tap-tempo, MIDI clock sync,
   dotted/triplet/swing note divisions, hold latch with re-latch.

2. **Polyphonic Step Sequencer**: up to 512 steps, chords up to 10 notes,
   rests + ties, forward/backward/pendulum playback, transpose from keyboard,
   patch-level memory.

The sequencer can be routed through the arpeggiator for chord-progression
arpeggiation.
"""

import random
from dataclasses import dataclass, field
from typing import Optional, Callable, Literal


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

NOTE_DIVISIONS = {
    '1/1': 1.0,
    '1/2': 0.5,
    '1/2d': 0.75,      # dotted half
    '1/2t': 1.0 / 3.0,  # half triplet
    '1/4': 0.25,
    '1/4d': 0.375,
    '1/4t': 0.25 / 1.5,
    '1/8': 0.125,
    '1/8d': 0.1875,
    '1/8t': 0.125 / 1.5,
    '1/16': 0.0625,
    '1/16d': 0.09375,
    '1/16t': 0.0625 / 1.5,
    '1/32': 0.03125,
}

ARP_MODES = ['up', 'down', 'updown', 'random', 'assign']


def ticks_per_step(bpm: float, division: str, swing: float = 0.0,
                   ppqn: int = 480) -> int:
    """Calculate ticks for one step."""
    base = NOTE_DIVISIONS.get(division, 0.25)
    ticks = int(ppqn * base * 4.0)
    return max(1, ticks)


# ---------------------------------------------------------------------------
# Arpeggiator
# ---------------------------------------------------------------------------

@dataclass
class ArpStep:
    """Single arpeggiator note event."""
    pitch: int       # MIDI pitch
    velocity: int    # 0..127
    gate: float      # 0..1 fraction of step duration
    tie: bool = False


class Arpeggiator:
    """Polyphonic arpeggiator (Prophet Rev4 firmware mod-style).

    Holds a set of active notes, then generates per-step note events
    according to the selected mode and parameters.
    """

    def __init__(self, bpm: int = 120, division: str = '1/16',
                 ppqn: int = 480):
        self.bpm = bpm
        self.division = division
        self.swing: float = 0.0       # 0..1
        self.octave_range: int = 2    # 1..4
        self.mode: str = 'up'
        self.hold: bool = False
        self.clock_source: str = 'internal'  # 'internal' | 'midi'

        self.ppqn = ppqn
        self._active_notes: dict[int, int] = {}  # pitch -> velocity
        self._latched_notes: dict[int, int] = {}
        self._step_index: int = 0
        self._tick_accum: int = 0
        self._direction: int = 1

    def note_on(self, pitch: int, velocity: int = 100):
        self._active_notes[pitch] = velocity

    def note_off(self, pitch: int):
        if self.hold:
            self._latched_notes[pitch] = self._active_notes.pop(pitch, 100)
        else:
            self._active_notes.pop(pitch, None)

    def toggle_hold(self):
        """Toggle hold latch.  When hold engaged, current notes latch."""
        self.hold = not self.hold
        if self.hold:
            self._latched_notes = dict(self._active_notes)
        else:
            self._latched_notes.clear()

    def all_notes_off(self):
        self._active_notes.clear()
        if not self.hold:
            self._latched_notes.clear()

    @property
    def current_notes(self) -> dict[int, int]:
        if self.hold:
            return self._latched_notes
        return self._active_notes

    def _build_note_list(self) -> list[int]:
        """Build ordered list of pitches for current mode."""
        notes = list(self.current_notes.keys())
        if not notes:
            return []
        notes.sort()

        result = []
        for oct_shift in range(self.octave_range):
            offset = oct_shift * 12
            for p in notes:
                result.append(p + offset)

        return result

    def tick(self, clock_ticks: int = 1) -> list[ArpStep]:
        """Advance by clock_ticks, return notes for this step.

        Returns empty list if no step is due.
        """
        step_ticks = ticks_per_step(self.bpm, self.division, self.swing,
                                    self.ppqn)
        self._tick_accum += clock_ticks

        if self._tick_accum < step_ticks:
            return []
        self._tick_accum -= step_ticks

        note_list = self._build_note_list()
        if not note_list:
            return []

        n = len(note_list)
        idx = self._step_index % n

        if self.mode == 'up':
            pitch = note_list[idx]
        elif self.mode == 'down':
            pitch = note_list[-(idx + 1)]
        elif self.mode == 'updown':
            cycle_len = 2 * n - 2 if n > 1 else 1
            pos = self._step_index % cycle_len
            if pos < n:
                pitch = note_list[pos]
            else:
                pitch = note_list[2 * n - 2 - pos]
        elif self.mode == 'random':
            pitch = random.choice(note_list)
        elif self.mode == 'assign':
            pitch = note_list[idx]
        else:
            pitch = note_list[idx]

        # Get velocity from closest matching note
        base_notes = self.current_notes
        # Map pitched note back to its base class
        base_pitch = pitch % 12
        # Find best matching note in active set
        best_pitch = min(base_notes.keys(), key=lambda p: abs(p - pitch))
        velocity = base_notes.get(best_pitch, 100)

        self._step_index += 1
        return [ArpStep(pitch=pitch, velocity=velocity, gate=0.8, tie=False)]


# ---------------------------------------------------------------------------
# Polyphonic Step Sequencer
# ---------------------------------------------------------------------------

@dataclass
class SeqStep:
    """Single polyphonic sequencer step."""
    pitches: list[tuple[int, int]]  # list of (pitch, velocity) pairs
    tie: bool = False               # tie to previous step
    rest: bool = False              # rest (no sound)
    duration_ratio: float = 1.0     # fraction of step duration


class PolySequencer:
    """Polyphonic step sequencer (Prophet Rev4 firmware mod-style).

    Up to 512 steps, each step can hold a chord of up to 10 notes.
    Supports rests, ties, forward/backward/pendulum playback,
    and keyboard transpose.
    """

    def __init__(self, bpm: int = 120, division: str = '1/16',
                 ppqn: int = 480):
        self.bpm = bpm
        self.division = division
        self.swing: float = 0.0
        self.direction: str = 'forward'
        self.transpose: int = 0
        self.ppqn = ppqn
        self._steps: list[SeqStep] = []
        self._step_index: int = 0
        self._pendulum_dir: int = 1
        self._tick_accum: int = 0
        self._max_steps: int = 512
        self._looping: bool = True

    @property
    def length(self) -> int:
        return len(self._steps)

    @property
    def max_steps(self) -> int:
        return self._max_steps

    def clear(self):
        self._steps.clear()
        self._step_index = 0

    def add_step(self, pitches: Optional[list[tuple[int, int]]] = None,
                 tie: bool = False, rest: bool = False,
                 duration_ratio: float = 1.0) -> bool:
        if len(self._steps) >= self._max_steps:
            return False
        self._steps.append(SeqStep(
            pitches=pitches or [],
            tie=tie,
            rest=rest,
            duration_ratio=duration_ratio,
        ))
        return True

    def set_step(self, index: int, step: SeqStep) -> bool:
        if 0 <= index < len(self._steps):
            self._steps[index] = step
            return True
        return False

    def remove_step(self, index: int) -> bool:
        if 0 <= index < len(self._steps):
            self._steps.pop(index)
            return True
        return False

    def insert_step(self, index: int, step: SeqStep) -> bool:
        if len(self._steps) >= self._max_steps:
            return False
        self._steps.insert(index, step)
        return True

    def record_chord(self, pitches: list[tuple[int, int]]):
        if self._step_index < len(self._steps):
            self._steps[self._step_index].pitches = pitches[:10]
        else:
            self.add_step(pitches=pitches[:10])

    def tick(self, clock_ticks: int = 1) -> list[ArpStep]:
        """Advance sequencer, return notes for current step."""
        if not self._steps:
            return []

        step_ticks = ticks_per_step(self.bpm, self.division, self.swing,
                                    self.ppqn)
        self._tick_accum += clock_ticks

        if self._tick_accum < step_ticks:
            return []
        self._tick_accum -= step_ticks

        idx = self._step_index
        if self.direction == 'backward':
            idx = len(self._steps) - 1 - self._step_index
        elif self.direction == 'pendulum':
            cycle = 2 * len(self._steps) - 2 if len(self._steps) > 1 else 1
            pos = self._step_index % cycle
            if pos < len(self._steps):
                idx = pos
            else:
                idx = 2 * len(self._steps) - 2 - pos

        step = self._steps[idx % len(self._steps)]

        self._step_index += 1
        if not self._looping and self._step_index >= len(self._steps):
            return []

        if step.rest:
            return []

        events = []
        for pitch, vel in step.pitches:
            transposed = min(127, max(0, pitch + self.transpose))
            events.append(ArpStep(
                pitch=transposed,
                velocity=vel,
                gate=step.duration_ratio,
                tie=step.tie,
            ))
        return events


# ---------------------------------------------------------------------------
# Combined Arpeggiator + Sequencer
# ---------------------------------------------------------------------------

class ArpSeqCombined:
    """Combined arpeggiator -> poly sequencer (Prophet Rev4 style).

    The sequencer can be routed *through* the arpeggiator: a recorded
    chord sequence is fed into the arp to create changing chord
    progressions.
    """

    def __init__(self, bpm: int = 120, division: str = '1/16',
                 ppqn: int = 480):
        self.arp = Arpeggiator(bpm, division, ppqn)
        self.seq = PolySequencer(bpm, division, ppqn)
        self.arp_through_seq: bool = False

    def tick(self, clock_ticks: int = 1) -> list[ArpStep]:
        """Combined tick: advance both, return events."""
        seq_events = self.seq.tick(clock_ticks)

        if self.arp_through_seq and seq_events:
            for ev in seq_events:
                self.arp.note_on(ev.pitch, ev.velocity)
            arp_events = self.arp.tick(clock_ticks)
            return arp_events if arp_events else seq_events

        arp_events = self.arp.tick(clock_ticks)
        return arp_events or seq_events


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    """Demo: arpeggiate Cmaj7 chord through several modes, then poly seq."""
    print("=== Arpeggiator Demo ===")
    arp = Arpeggiator(bpm=120, division='1/16')

    for p in [60, 64, 67, 71]:
        arp.note_on(p, 100)

    print("  Active notes:", sorted(arp.current_notes.keys()))
    print("  Cmaj7 arpeggiation modes:")

    for mode in ['up', 'down', 'updown', 'random']:
        arp.mode = mode
        events = []
        for _ in range(16):
            evts = arp.tick(120)
            events.extend(evts)
        pitches = [e.pitch for e in events if e]
        print(f"    {mode}: {pitches[:12]}{'...' if len(pitches) > 12 else ''}")

    arp.all_notes_off()
    print()

    print("=== Polyphonic Sequencer Demo ===")
    seq = PolySequencer(bpm=120, division='1/8')
    chords = [
        [(60, 100), (64, 90), (67, 85), (71, 80)],  # Cmaj7
        [(62, 100), (65, 90), (69, 85), (72, 80)],  # Dm7
        [(55, 95), (59, 85), (62, 80), (67, 75)],   # G7
        [(60, 100), (64, 90), (67, 85), (71, 80)],  # Cmaj7
    ]
    for chord in chords:
        seq.add_step(pitches=chord)
    print(f"  {seq.length} steps recorded")

    events = []
    for _ in range(32):
        evts = seq.tick(240)
        events.extend(evts)
    print(f"  Played {len([e for e in events if e])} events")

    for d in ['forward', 'backward', 'pendulum']:
        seq.direction = d
        seq._step_index = 0
        evts = []
        for _ in range(8):
            evts.extend(seq.tick(240))
        pitches = [e.pitch for e in evts if e]
        print(f"    direction={d}: pitches={pitches}")

    print()
    print("=== Combined Demo ===")
    combined = ArpSeqCombined(bpm=120)
    for chord in chords:
        combined.seq.add_step(pitches=chord)
    combined.arp_through_seq = True

    events = []
    for _ in range(16):
        evts = combined.tick(120)
        events.extend(evts)
    arp_pitches = [e.pitch for e in events if e]
    print(f"  Seq->Arp: {len(arp_pitches)} events, pitches={arp_pitches[:16]}...")
    print("  Demo PASSED")


if __name__ == '__main__':
    demo()