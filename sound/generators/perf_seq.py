# -*- coding: utf-8 -*-
"""On-the-fly performance step sequencer — Stylophone "On-The-Fly" style.

Replicable logic from the Synthtopia item "Stylophone On-The-Fly Performance
Sequencer Features 24 Memories, Loop Recording" (2026-11-06).

The hardware is built around *real-time manipulation* rather than stop-and-edit
programming: an eight-step programming cell expands to 16/32/64-step
sequences, eight pattern chains switch under the fingers, 24 sequence memories
hold per-step pitch and duty cycle, direction can be flipped while running, and
six step effects (Skip, Rest, Tie, Slide, Ratchet, Random) plus a manual
performance button supply variation.  Groove is handled by tempo, swing,
lead/lag timing, note length and gate length.  A separate Loop Record captures
up to 128 steps into 24 loop memories.

What is replicated here (pure sequencing logic, stdlib + numpy):

* ``Pattern`` — 8-step programming cell expanded to 16/32/64 steps, per-step
  pitch and duty cycle, per-step effect slot.
* ``MemoryBank`` — 24 sequence memories (save/recall patterns) plus 24 loop
  memories for captured performances.
* ``Sequencer`` — chain of 8 patterns with live chain switching, forward /
  reverse / bounce direction changeable at any tick, scale quantise and
  transpose via knob/CV/MIDI value, swing, lead/lag in ms, note length and
  gate length.
* ``LoopRecorder`` — captures up to 128 steps of incoming note events,
  quantises them to the step grid with per-step duty, stores into a loop
  memory.
* ``StepEffect`` enumeration: SKIP, REST, TIE, SLIDE, RATCHET, RANDOM.

Not replicated: CV/gate hardware I/O, unit linking, the analogue output stage.

Usage:
    from sound.generators.perf_seq import Pattern, Sequencer

    p = Pattern(length=16, root=48, scale="minor")
    p.set_step(0, pitch=0, duty=0.5)
    seq = Sequencer(patterns=[p], bpm=124)
    events = seq.render(bars=1)
    seq.write_midi(events, "on_the_fly.mid")
"""

from __future__ import annotations

import os
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

TPB = 480                      # ticks per beat (musicom standard)
CHROMATIC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
SCALES: Dict[str, List[int]] = {
    "chromatic": CHROMATIC,
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "pentatonic": [0, 2, 4, 7, 9],
    "blues": [0, 3, 5, 6, 7, 10],
}
EFFECTS = ("", "skip", "rest", "tie", "slide", "ratchet", "random")


@dataclass
class NoteEvent:
    """A rendered sequencer event in absolute ticks."""
    pitch: int
    start: int
    dur: int
    vel: int = 100
    slide: bool = False
    step: int = 0


# ---------------------------------------------------------------------------
# pattern
# ---------------------------------------------------------------------------
class Pattern:
    """Eight-step programming cell expanded to 16/32/64 steps.

    Args:
        length: 16, 32 or 64 steps.
        root: root MIDI note.
        scale: key name from ``SCALES``.
        steps: optional explicit 8-step cell [(pitch_offset, duty, effect)].
    """

    def __init__(self, length: int = 16, root: int = 48, scale: str = "minor",
                 steps: Optional[Sequence[Tuple[int, float, str]]] = None):
        if length not in (16, 32, 64):
            length = 16
        self.length = int(length)
        self.root = int(root)
        self.scale = scale if scale in SCALES else "minor"
        cell = list(steps or [(i, 0.5, "") for i in range(8)])
        # expand the 8-step cell cyclically across the full sequence
        self.base: List[Tuple[int, float, str]] = []
        for i in range(self.length):
            po, duty, fx = cell[i % len(cell)]
            self.base.append((int(po), float(np.clip(duty, 0.01, 1.0)),
                              fx if fx in EFFECTS else ""))
        # working copy that effects can mutate
        self.steps: List[Dict] = [
            {"pitch": po, "duty": duty, "effect": fx, "ratchet": 3, "prob": 0.3}
            for po, duty, fx in self.base
        ]

    # -- editing ------------------------------------------------------------
    def set_step(self, index: int, pitch: Optional[int] = None,
                 duty: Optional[float] = None, effect: Optional[str] = None,
                 ratchet: int = 3, prob: float = 0.3) -> "Pattern":
        s = self.steps[index % self.length]
        if pitch is not None:
            s["pitch"] = int(pitch)
        if duty is not None:
            s["duty"] = float(np.clip(duty, 0.01, 1.0))
        if effect is not None:
            s["effect"] = effect if effect in EFFECTS else ""
        s["ratchet"] = int(max(2, min(6, ratchet)))
        s["prob"] = float(np.clip(prob, 0.0, 1.0))
        return self

    def reset(self) -> "Pattern":
        self.steps = [dict(pitch=po, duty=duty, effect=fx, ratchet=3, prob=0.3)
                      for po, duty, fx in self.base]
        return self

    def snapshot(self) -> Dict:
        return {"length": self.length, "root": self.root, "scale": self.scale,
                "steps": [dict(s) for s in self.steps]}

    @classmethod
    def from_snapshot(cls, snap: Dict) -> "Pattern":
        p = cls(length=snap["length"], root=snap["root"], scale=snap["scale"])
        p.steps = [dict(s) for s in snap["steps"]]
        return p

    # -- pitch --------------------------------------------------------------
    def quantise(self, midi: float, transpose: int = 0) -> int:
        """Snap a MIDI value to the pattern's scale, then transpose."""
        m = int(round(midi)) + int(transpose)
        sc = SCALES[self.scale]
        # nearest scale degree
        best, best_d = m, 99
        for octv in (-1, 0, 1):
            for d in sc:
                cand = self.root + 12 * octv + d + (int(transpose) // 12) * 12
                cand = 12 * round((m - cand) / 12) + cand
                dist = abs(cand - m)
                if dist < best_d:
                    best, best_d = cand, dist
        return int(np.clip(best, 0, 127))


# ---------------------------------------------------------------------------
# memories
# ---------------------------------------------------------------------------
class MemoryBank:
    """24 sequence memories + 24 loop-record memories."""

    def __init__(self) -> None:
        self.sequence: List[Optional[Dict]] = [None] * 24
        self.loops: List[Optional[Dict]] = [None] * 24

    def store(self, slot: int, pattern: Pattern) -> None:
        self.sequence[int(slot) % 24] = pattern.snapshot()

    def recall(self, slot: int) -> Optional[Pattern]:
        snap = self.sequence[int(slot) % 24]
        return Pattern.from_snapshot(snap) if snap else None

    def store_loop(self, slot: int, loop: Dict) -> None:
        self.loops[int(slot) % 24] = loop

    def recall_loop(self, slot: int) -> Optional[Dict]:
        return self.loops[int(slot) % 24]


# ---------------------------------------------------------------------------
# sequencer
# ---------------------------------------------------------------------------
class Sequencer:
    """Chain-of-patterns performance sequencer.

    Args:
        patterns: up to 8 patterns in the chain.
        bpm: tempo.
        steps_per_beat: 4 = 16th notes.
        swing: 0..1, delays odd steps.
        lead_lag_ms: positive = lay back, negative = push.
        note_length: 0..2 multiplier on step duration.
        gate_length: 0..1 multiplier on the pattern duty cycle.
        direction: "forward" | "reverse" | "bounce".
        seed: deterministic Random effect.
    """

    def __init__(self, patterns: Optional[Sequence[Pattern]] = None,
                 bpm: float = 120.0, steps_per_beat: int = 4,
                 swing: float = 0.0, lead_lag_ms: float = 0.0,
                 note_length: float = 1.0, gate_length: float = 1.0,
                 direction: str = "forward", seed: int = 0):
        self.patterns: List[Pattern] = list(patterns or [Pattern()])[:8]
        self.bpm = float(bpm)
        self.steps_per_beat = int(steps_per_beat)
        self.swing = float(np.clip(swing, 0.0, 0.75))
        self.lead_lag_ms = float(lead_lag_ms)
        self.note_length = float(np.clip(note_length, 0.05, 2.0))
        self.gate_length = float(np.clip(gate_length, 0.01, 1.0))
        self.direction = direction if direction in ("forward", "reverse", "bounce") else "forward"
        self.rng = np.random.default_rng(seed)
        self._bounce_dir = 1
        self.transpose = 0
        self.chain = list(range(len(self.patterns)))

    # -- live controls ------------------------------------------------------
    def set_direction(self, direction: str) -> None:
        if direction in ("forward", "reverse", "bounce"):
            self.direction = direction

    def set_chain(self, chain: Sequence[int]) -> None:
        self.chain = [int(i) % max(1, len(self.patterns)) for i in chain][:8]

    def set_transpose(self, semitones: int) -> None:
        self.transpose = int(semitones)

    # -- rendering ----------------------------------------------------------
    def _step_offset(self, step_pos: int, step_index: int) -> float:
        """Timing offset in ticks for swing + lead/lag."""
        ticks_per_step = TPB / self.steps_per_beat
        swing_off = (self.swing * ticks_per_step * 0.5) if (step_pos % 2 == 1) else 0.0
        lag = self.lead_lag_ms * TPB * self.bpm / 60000.0
        return swing_off + lag

    def render(self, bars: int = 1, start_tick: int = 0,
               directions_at: Optional[Dict[int, str]] = None) -> List[NoteEvent]:
        """Render ``bars`` of 4/4, honouring live direction changes.

        Args:
            bars: number of 4/4 bars.
            start_tick: absolute start tick.
            directions_at: {tick_offset: direction} applied during playback.
        """
        ticks_per_step = int(round(TPB / self.steps_per_beat))
        total_steps = bars * 4 * self.steps_per_beat
        events: List[NoteEvent] = []
        if not self.patterns:
            return events
        dirs = dict(directions_at or {})

        pos = 0
        bounced = 1
        last_pitch: Optional[int] = None
        for n in range(total_steps):
            # live direction switch
            for tick, d in list(dirs.items()):
                if n * ticks_per_step >= tick:
                    self.set_direction(d)
                    dirs.pop(tick)

            pat = self.patterns[self.chain[(n // max(1, self.patterns[0].length)) % len(self.chain)]]
            idx = pos % pat.length
            s = pat.steps[idx]

            # advance position for next step
            if self.direction == "forward":
                pos += 1
            elif self.direction == "reverse":
                pos -= 1
            else:
                pos += bounced
                if pos >= pat.length - 1 or pos <= 0:
                    bounced *= -1
            pos %= pat.length

            fx = s["effect"]
            t0 = start_tick + n * ticks_per_step + int(round(self._step_offset(n, idx)))
            step_dur = ticks_per_step
            gate = max(1, int(step_dur * s["duty"] * self.gate_length))
            dur = max(1, int(step_dur * self.note_length))

            if fx == "skip":
                continue
            if fx == "rest":
                last_pitch = None
                continue
            if fx == "tie" and events:
                events[-1].dur += step_dur
                continue

            pitch_off = s["pitch"]
            if fx == "random":
                if self.rng.random() < s["prob"]:
                    pitch_off = int(self.rng.integers(-7, 13))
                    pitch_off = int(np.clip(pitch_off, -12, 24))
            midi = pat.quantise(pat.root + pitch_off, self.transpose)

            if fx == "ratchet":
                reps = int(s["ratchet"])
                sub = max(1, gate // reps)
                for r in range(reps):
                    events.append(NoteEvent(midi, t0 + r * sub, max(1, sub - 1),
                                            100 if r == 0 else 84, False, idx))
            elif fx == "slide" and last_pitch is not None:
                # legato overlap: start at previous end so a glide is possible
                prev_end = events[-1].start + events[-1].dur if events else t0
                events.append(NoteEvent(midi, max(t0, prev_end - 8), dur,
                                        100, True, idx))
            else:
                events.append(NoteEvent(midi, t0, gate, 100,
                                        fx == "slide", idx))
            last_pitch = midi
        return events


# ---------------------------------------------------------------------------
# loop recorder
# ---------------------------------------------------------------------------
class LoopRecorder:
    """Capture up to 128 steps of played notes into a 24-slot loop memory."""

    MAX_STEPS = 128

    def __init__(self, steps_per_beat: int = 4, max_steps: int = MAX_STEPS,
                 sr: int = 44100):
        self.steps_per_beat = int(steps_per_beat)
        self.max_steps = min(int(max_steps), self.MAX_STEPS)
        self.sr = sr
        self.tick_per_step = TPB / self.steps_per_beat

    def capture(self, events: Sequence[NoteEvent], bank: MemoryBank,
                slot: int, origin_tick: int = 0) -> Dict:
        """Quantise ``events`` onto the step grid and store in loop memory."""
        grid: List[Dict] = []
        for e in sorted(events, key=lambda x: x.start):
            step = int(round((e.start - origin_tick) / self.tick_per_step))
            if step < 0 or step >= self.max_steps:
                continue
            duty = float(np.clip(e.dur / self.tick_per_step, 0.05, 1.0))
            grid.append({"step": step, "pitch": int(e.pitch),
                         "duty": round(duty, 3), "vel": int(e.vel)})
        loop = {"length": max(1, min(self.max_steps, len(grid))),
                "events": grid, "captured": len(grid)}
        bank.store_loop(slot, loop)
        return loop

    def replay(self, loop: Dict, start_tick: int = 0) -> List[NoteEvent]:
        tp = self.tick_per_step
        out = []
        for g in loop["events"]:
            out.append(NoteEvent(g["pitch"], start_tick + int(g["step"] * tp),
                                 max(1, int(g["duty"] * tp)), g.get("vel", 100)))
        return out


# ---------------------------------------------------------------------------
# MIDI writer (delta-correct, type 0)
# ---------------------------------------------------------------------------
def write_midi(events: Sequence[NoteEvent], path: str, bpm: float = 120.0,
               tpb: int = TPB, channel: int = 0) -> str:
    """Write events to a type-0 MIDI file with correct delta times."""
    def vlq(value: int) -> bytes:
        value = max(0, int(value))
        out = bytearray([value & 0x7F])
        value >>= 7
        while value:
            out.insert(0, (value & 0x7F) | 0x80)
            value >>= 7
        return bytes(out)

    abs_evts: List[Tuple[int, int, bytes]] = []
    tempo_us = int(60_000_000 / bpm)
    track = bytearray()
    track += b"\x00\xff\x51\x03" + tempo_us.to_bytes(3, "big")
    name = b"On-The-Fly Seq"
    track += b"\x00\xff\x03" + bytes([len(name)]) + name

    for e in events:
        p = int(np.clip(e.pitch, 0, 127))
        v = int(np.clip(e.vel, 1, 127))
        abs_evts.append((e.start, 1, bytes([0x90 | channel, p, v])))
        abs_evts.append((e.start + max(1, e.dur), 0,
                         bytes([0x80 | channel, p, 0])))
    abs_evts.sort(key=lambda x: (x[0], x[1]))

    last = 0
    for tick, _, msg in abs_evts:
        track += vlq(tick - last) + msg
        last = tick
    track += b"\x00\xff\x2f\x00"

    with open(path, "wb") as f:
        f.write(b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpb))
        f.write(b"MTrk" + struct.pack(">I", len(track)) + bytes(track))
    return path


# ---------------------------------------------------------------------------
# demo
# ---------------------------------------------------------------------------
def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Build a 64-step pattern, apply effects, render + record a loop."""
    os.makedirs(out_dir, exist_ok=True)

    p = Pattern(length=64, root=45, scale="minor")
    for i, off in enumerate([0, 0, 3, 0, 7, 5, 3, 10]):
        p.set_step(i, pitch=off)
    p.set_step(2, effect="rest")
    p.set_step(5, effect="ratchet", ratchet=3)
    p.set_step(6, effect="slide")
    p.set_step(9, effect="tie")
    p.set_step(11, effect="random", prob=0.5)
    p.set_step(13, effect="skip")

    bank = MemoryBank()
    bank.store(0, p)

    seq = Sequencer(patterns=[p], bpm=124, swing=0.25, lead_lag_ms=-6.0,
                    gate_length=0.8, direction="forward", seed=5)
    ev = seq.render(bars=8, directions_at={2 * TPB: "bounce", 6 * TPB: "reverse"})
    path = os.path.join(out_dir, "on_the_fly_64step.mid")
    write_midi(ev, path, bpm=124)

    print("=== Stylophone On-The-Fly performance sequencer ===")
    print(f"pattern: {p.length} steps, root {p.root}, scale {p.scale}")
    print(f"rendered {len(ev)} events; pitches {sorted({e.pitch for e in ev})}")
    print(f"slides: {sum(e.slide for e in ev)}, ratchet hits: "
          f"{sum(1 for e in ev if e.step == 5)}")
    print(f"midi: {path} ({os.path.getsize(path)} B)")

    # live direction changes actually reorder the pitch stream
    fwd = Sequencer(patterns=[p], bpm=124).render(bars=1)
    rev = Sequencer(patterns=[p], bpm=124, direction="reverse").render(bars=1)
    print(f"forward first 6 pitches : {[e.pitch for e in fwd[:6]]}")
    print(f"reverse first 6 pitches : {[e.pitch for e in rev[:6]]}")

    # memory recall + loop record
    recalled = bank.recall(0)
    loop = LoopRecorder().capture(ev[:40], bank, slot=3, origin_tick=0)
    replay = LoopRecorder().replay(bank.recall_loop(3))
    print(f"memory 0 recalled: {recalled.length} steps; "
          f"loop memory 3: {loop['captured']} events, "
          f"replay {len(replay)} notes")

    assert os.path.getsize(path) > 400 and len(ev) > 40
    print("demo OK")
    return {"path": path, "events": len(ev), "loop": loop["captured"]}


if __name__ == "__main__":
    demo()
