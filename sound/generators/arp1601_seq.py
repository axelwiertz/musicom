# -*- coding: utf-8 -*-
"""ARP 1601-style analogue step sequencer — 16 steps (or 2 x 8), three gate
buses, per-step Skip / Reset switches, clock pulse-width CV, quantiser.

Replicable logic from the Behringer 1601 Sequencer announcement (Synthtopia,
2026-11-04): an unofficial copy of the 1970s ARP 1601 in Eurorack format —
16 steps splittable into two independent 8-step patterns, three gate buses,
free 10-octave CV range, Skip and Reset buttons with CV inputs, per-step
switches selectable as Skip *or* Reset, clock pulse-width control plus CV for
gate length (staccato → legato), a clocked Gate-1 output for accents, CV
transpose, a "position 1" CV output for triggering events on loop restart,
separate quantiser inputs, and MIDI/USB.

The hardware (panel, 42 controls, MIDI/USB I/O) is not replicated; the
*sequencing behaviour* is, including the details that make an analogue
sequencer feel different from a DAW piano roll:

- **Skip** steps advance the clock but emit nothing (and their CV is not
  latched); **Reset** steps jump the play head back to step 1 of the current
  pattern and emit nothing — the switch is a position, not an action.
- **Gate buses**: each step is assigned to bus 1/2/3.  Bus 1 is the "clocked
  Gate 1" accent output, bus 2/3 can drive separate envelopes.
- **Pulse width** sets gate length as a fraction of the step clock, and a
  per-step CV offset moves it, so a sequence can slide from staccato to
  legato without changing tempo.
- **Quantiser**: the CV output is snapped to a scale (separate quantise
  input per the hardware), after transposition — matching the original
  order of operations.
- **Position 1 CV**: a pulse emitted when the sequence wraps to step 1,
  usable as a reset trigger for downstream modules.

Pure event logic (no audio), absolute ticks at 480 PPQN so it drops straight
into ``structures.MusicEvent`` pipelines.

Usage::

    from sound.generators.arp1601_seq import ARP1601Sequencer
    seq = ARP1601Sequencer(bpm=120, split=True, scale=(0, 2, 3, 5, 7, 8, 10))
    seq.set_cv(0, 0); seq.set_cv(1, 3); seq.set_mode(5, "skip")
    events = seq.generate(cycles=2)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

TICKS_PER_BEAT = 480
STEPS = 16


@dataclass
class SeqStep:
    """One physical step of the 1601."""

    cv: float = 0.0                 # semitones above the base CV
    gate: bool = True
    bus: int = 1                    # 1..3 (Gate 1 = clocked accent bus)
    mode: str = "play"              # "play" | "skip" | "reset"
    pulse_width: float = 0.5        # 0..1 of the step, plus pw_cv
    pw_cv: float = 0.0              # CV offset on gate length, -0.4..0.4


@dataclass
class StepEvent:
    """Rendered sequencer event (absolute ticks)."""

    tick: int
    step: int
    cv: float                       # final, quantised, transposed semitones
    gate: bool
    bus: int
    length_ticks: int
    velocity: int                   # 100 on bus 1 accents, 80 otherwise
    position1: bool = False


class ARP1601Sequencer:
    """16-step / dual-8-step sequencer with Skip, Reset and gate buses."""

    def __init__(self, bpm: float = 120.0, steps: int = STEPS,
                 split: bool = False, rate: float = 1.0,
                 quantize: bool = True,
                 scale: Sequence[int] | None = None,
                 ticks_per_beat: int = TICKS_PER_BEAT):
        self.bpm = float(bpm)
        self.steps = int(steps)
        self.split = bool(split)
        self.rate = float(rate)         # clock division: 1 = one step per 16th
        self.quantize = bool(quantize)
        self.scale = tuple(scale) if scale else tuple(range(12))
        self.tpb = int(ticks_per_beat)
        self.data: List[SeqStep] = [SeqStep() for _ in range(self.steps)]

        # MIDI clock at 24 PPQN; default step = 16th note (6 clocks)
        self.clocks_per_step = 6

    # ------------------------------------------------------------------ #
    # editing
    # ------------------------------------------------------------------ #
    def set_cv(self, i: int, semitones: float) -> None:
        self.data[i % self.steps].cv = float(semitones)

    def set_gate(self, i: int, on: bool = True) -> None:
        self.data[i % self.steps].gate = bool(on)

    def set_bus(self, i: int, bus: int) -> None:
        if bus not in (1, 2, 3):
            raise ValueError("bus must be 1, 2 or 3")
        self.data[i % self.steps].bus = int(bus)

    def set_mode(self, i: int, mode: str) -> None:
        if mode not in ("play", "skip", "reset"):
            raise ValueError("mode must be play, skip or reset")
        self.data[i % self.steps].mode = mode

    def set_pulse_width(self, i: int, width: float, cv_offset: float = 0.0) -> None:
        st = self.data[i % self.steps]
        st.pulse_width = float(min(1.0, max(0.02, width)))
        st.pw_cv = float(max(-0.4, min(0.4, cv_offset)))

    def set_pattern(self, values: Sequence[float], offset: int = 0,
                    gates: Sequence[bool] | None = None) -> None:
        """Bulk-load CVs (and optional gates) into a pattern block."""
        for k, v in enumerate(values):
            self.set_cv(offset + k, v)
            if gates is not None:
                self.set_gate(offset + k, gates[k])

    # ------------------------------------------------------------------ #
    # clocking
    # ------------------------------------------------------------------ #
    def step_ticks(self) -> int:
        """Ticks per step: a 16th at the given tempo and clock rate."""
        quarter = self.tpb * 60.0 / self.bpm
        return max(1, int(round(quarter / 4.0 / self.rate)))

    def _quantise(self, cv: float) -> float:
        if not self.quantize:
            return cv
        return float(min(self.scale, key=lambda s: abs(s - cv)))

    def generate(self, cycles: int = 1, transpose: float = 0.0,
                 pattern: str = "AB", seed: int | None = None) -> List[StepEvent]:
        """Render ``cycles`` passes of the sequence.

        pattern : "AB" (both halves), "A" (steps 1-8) or "B" (steps 9-16).
        """
        st_ticks = self.step_ticks()
        blocks = {"A": (0, 8), "B": (8, 16)}
        order: List[tuple[int, int]] = []
        if self.split and pattern.upper() in ("AB", "BA"):
            for _ in range(cycles):
                order.append(blocks["A"])
                order.append(blocks["B"])
        elif self.split and pattern.upper() in blocks:
            order = [blocks[pattern.upper()]] * cycles
        else:
            order = [(0, self.steps)] * cycles

        events: List[StepEvent] = []
        pos = 0
        for (lo, hi) in order:
            idx = lo
            block_len = hi - lo
            first = True
            for k in range(hi - lo):
                st = self.data[idx]
                tick = pos * st_ticks
                if st.mode == "reset":
                    idx = lo                       # jump back, emit nothing
                    pos += 1
                    continue
                if st.mode == "skip" or not st.gate:
                    idx = lo + (idx - lo + 1) % block_len
                    pos += 1
                    continue
                cv = self._quantise(st.cv + float(transpose))
                pw = min(1.0, max(0.02, st.pulse_width + st.pw_cv))
                length = max(1, int(round(pw * st_ticks)))
                events.append(StepEvent(
                    tick=tick, step=idx, cv=cv, gate=True, bus=st.bus,
                    length_ticks=length,
                    velocity=100 if st.bus == 1 else 80,
                    position1=(first and idx == lo),
                ))
                first = False
                idx = lo + (idx - lo + 1) % block_len
                pos += 1
        return events

    def position1_pulses(self, events: Sequence[StepEvent]) -> List[int]:
        """Ticks where a position-1 (loop restart) trigger fires."""
        return [e.tick for e in events if e.position1]

    # ------------------------------------------------------------------ #
    def to_music_events(self, events: Sequence[StepEvent], channel: int = 0,
                        base_note: int = 48):
        """Convert to ``structures.MusicEvent`` objects (absolute ticks)."""
        from structures import MusicEvent
        return [MusicEvent(pitch=int(round(base_note + e.cv)),
                           volume=e.velocity,
                           start_tick=e.tick,
                           end_tick=e.tick + e.length_ticks) for e in events]


def demo() -> None:
    """Two 8-step patterns, a skip step, a reset step, three gate buses."""
    seq = ARP1601Sequencer(bpm=120, split=True,
                           scale=(0, 2, 3, 5, 7, 8, 10))   # natural minor
    # pattern A: rising minor arpeggio with a skipped step
    seq.set_pattern([0, 3, 7, 12, 15, 12, 7, 3], offset=0)
    seq.set_mode(4, "skip")
    # pattern B: answer phrase that resets early
    seq.set_pattern([12, 10, 8, 7, 5, 3, 0, 0], offset=8)
    seq.set_mode(14, "reset")
    for i in range(0, 16, 3):
        seq.set_bus(i, 1 if i % 2 == 0 else 2)
    seq.set_pulse_width(1, 0.22, cv_offset=-0.08)   # short, staccato
    seq.set_pulse_width(6, 0.9)                     # long, legato

    ev = seq.generate(cycles=2, transpose=0.0, pattern="AB")
    print(f"ARP-1601 demo: {len(ev)} gate events over 2 x (A+B)")
    print(f"  step ticks={seq.step_ticks()} at {seq.bpm:.0f} bpm "
          f"(16th @ 480 PPQN)")
    for e in ev[:6]:
        print(f"  tick {e.tick:5d} step {e.step + 1:2d} cv {e.cv:+5.1f} "
              f"bus {e.bus} len {e.length_ticks}")
    assert len(ev) == 2 * (8 - 1 + 8 - 1), len(ev)   # skip + reset drop 2
    assert all(e.gate for e in ev)
    assert ev[0].tick == 0 and ev[0].position1
    # reset truncates pattern B to 6 notes (steps 9..14), no event at step 15
    assert not any(e.step == 14 for e in ev), "reset step must not sound"
    buses = {e.bus for e in ev}
    assert buses == {1, 2}, buses
    # quantiser: every emitted CV is on the minor scale
    assert all(e.cv % 12 in (0, 2, 3, 5, 7, 8, 10) for e in ev)
    print(f"  position-1 triggers at ticks {seq.position1_pulses(ev)}")
    print(f"  buses used: {sorted(buses)}, CVs all on natural minor")
    print("demo OK")


if __name__ == "__main__":
    demo()
