"""Multi-playhead sequencer: three independent read heads per track.

Inspired by AARM's ADEPT: a track stores one pool of musical material
``(line index, column index, pitch, velocity, length)`` and **three playheads**
(Orange / Yellow / Blue) read it simultaneously.  Each head has its own

* **length** -- how many pool steps it observes before wrapping (so heads
  drift against each other, producing polymetric phasing),
* **direction** -- forward, backward, pendulum, random walk,
* **clock division** -- 1/1 .. 1/8, including dotted and triplet ratios,
* **output** -- MIDI channel/voice tag,
* and a per-head **sequencer type** that transforms what it reads.

Sequencer types implemented (the pool is transformed, never destroyed, so a
track can be switched between types at runtime without losing data):

``NOTE_GRID`` identity, ``EUCLID`` mask from a Bjorklund pattern,
``ORBIT`` rotate by a phase accumulator, ``TRAPDOOR`` probabilistic drops,
``DEFLECTOR`` interval mirroring, ``PACHINKO`` seeded pitch random walk,
``LOGIC`` AND/XOR of two masks, ``PATHWAYS`` step in a fixed permutation.

Events are emitted in absolute ticks.
"""

from __future__ import annotations

import numpy as np

__all__ = ["Playhead", "SeqTrack", "MultiPlayheadSequencer", "euclid_mask", "demo"]


def euclid_mask(steps: int, pulses: int, rotate: int = 0) -> np.ndarray:
    """Bjorklund's Euclidean rhythm as a boolean mask."""
    if pulses <= 0:
        return np.zeros(steps, dtype=bool)
    if pulses >= steps:
        return np.ones(steps, dtype=bool)
    pattern = [1] * pulses + [0] * (steps - pulses)
    m = len(pattern)
    # bucket/remainder fill (equivalent to Bjorklund for our purposes)
    mask = np.zeros(steps, dtype=bool)
    for i in range(steps):
        mask[i] = ((i * pulses) % steps) < pulses
    if rotate:
        mask = np.roll(mask, rotate)
    return mask


DIRECTIONS = ("fwd", "bwd", "pendulum", "random")


class Playhead:
    """One read head over a track's step pool."""

    def __init__(self, length: int | None = None, direction: str = "fwd",
                 division: float = 4.0, output: str = "ch0",
                 seq_type: str = "NOTE_GRID", euclid: tuple[int, int] | None = None,
                 drop_prob: float = 0.0, seed: int = 0, transpose: int = 0,
                 min_pitch: int = 24, max_pitch: int = 96):
        self.length = length
        self.direction = direction if direction in DIRECTIONS else "fwd"
        self.division = float(division)   # steps per beat
        self.output = output
        self.seq_type = seq_type
        self.euclid = euclid
        self.drop_prob = float(drop_prob)
        self.rng = np.random.default_rng(seed)
        self.transpose = int(transpose)
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self._pos = 0
        self._dir = 1
        self._phase = 0

    def reset(self):
        self._pos = 0
        self._dir = 1
        self._phase = 0

    # ------------------------------------------------------------------
    def _next_index(self, n: int) -> int:
        length = self.length or n
        length = max(1, min(length, n))
        if self.direction == "fwd":
            idx = self._pos % length
            self._pos += 1
        elif self.direction == "bwd":
            idx = (length - 1) - (self._pos % length)
            self._pos += 1
        elif self.direction == "pendulum":
            idx = self._pos
            self._pos += self._dir
            if self._pos >= length - 1 or self._pos <= 0:
                self._dir *= -1
        else:  # random walk
            idx = int(np.clip(self._pos + self.rng.choice([-1, 0, 1]), 0, length - 1))
            self._pos = idx
        return int(idx)

    def _transform(self, pool: list[dict], idx: int, n: int) -> dict | None:
        """Apply the head's sequencer type; return a note or None (skip)."""
        t = self.seq_type.upper()
        note = dict(pool[idx])
        if t == "NOTE_GRID":
            return note
        if t == "EUCLID":
            pulses, rot = self.euclid or (n // 2, 0)
            mask = euclid_mask(n, pulses, rot)
            return note if mask[idx] else None
        if t == "ORBIT":
            shift = self._phase // n if n else 0
            self._phase += 1
            return dict(pool[(idx + shift) % n])
        if t == "TRAPDOOR":
            if self.drop_prob and self.rng.random() < self.drop_prob:
                return None
            return note
        if t == "DEFLECTOR":
            # mirror intervals around the pool's centre pitch
            centre = int(np.median([p["midi"] for p in pool]))
            note["midi"] = int(np.clip(2 * centre - note["midi"],
                                       self.min_pitch, self.max_pitch))
            return note
        if t == "PACHINKO":
            step = int(self.rng.choice([-7, -5, -4, -3, -2, 2, 3, 4, 5, 7]))
            note["midi"] = int(np.clip(note["midi"] + step,
                                       self.min_pitch, self.max_pitch))
            return note
        if t == "LOGIC":
            a = euclid_mask(n, max(1, n // 2))
            b = euclid_mask(n, max(1, n // 3), rotate=1)
            return note if (a[idx] ^ b[idx]) else None
        if t == "PATHWAYS":
            order = np.argsort([(i * 5) % max(1, n) for i in range(n)])
            return dict(pool[int(order[idx % n])])
        return note


class SeqTrack:
    """A pool of steps read by 1..3 playheads."""

    def __init__(self, name: str, steps: int = 16, trig_tracks: int = 0,
                 pool: list[dict] | None = None):
        self.name = name
        self.steps = steps
        self.trig_tracks = trig_tracks   # >0: pool entries are track triggers
        self.pool = pool or [{"midi": 60, "vel": 100, "len": 1.0}
                             for _ in range(steps)]
        self.heads: list[Playhead] = []

    def add_head(self, **kw) -> Playhead:
        h = Playhead(**kw)
        self.heads.append(h)
        return h

    def set_step(self, i: int, midi: int | None = None, vel: int = 100,
                 length: float = 1.0, **extra):
        if midi is None:
            midi = self.pool[i % len(self.pool)]["midi"]
        d = {"midi": int(midi), "vel": int(vel), "len": float(length)}
        d.update(extra)
        self.pool[i % len(self.pool)] = d


class MultiPlayheadSequencer:
    def __init__(self, bpm: float = 120.0, ticks_per_beat: int = 480,
                 beats_per_bar: int = 4):
        self.bpm = bpm
        self.tpb = ticks_per_beat
        self.bpb = beats_per_bar
        self.tracks: dict[str, SeqTrack] = {}

    def add_track(self, name: str, steps: int = 16, **kw) -> SeqTrack:
        tr = SeqTrack(name, steps, **kw)
        self.tracks[name] = tr
        return tr

    def generate(self, bars: int = 4) -> list[tuple]:
        """Emit ``(output, start_tick, dur_tick, midi, vel, track)`` events.

        Each head advances on its own clock division, so a 16-step head at
        1/16 against a 12-step head at 1/16 triplet drifts through 4 bars
        before realigning -- the "interconnected system" behaviour.
        """
        events: list[tuple] = []
        end_tick = bars * self.bpb * self.tpb
        for tr in self.tracks.values():
            n = len(tr.pool)
            for head in tr.heads:
                head.reset()
                step_ticks = self.tpb / head.division
                t = 0.0
                guard = 0
                while t < end_tick and guard < 100000:
                    guard += 1
                    idx = head._next_index(n)
                    note = head._transform(tr.pool, idx, n)
                    if note is not None:
                        start = int(round(t))
                        dur = max(1, int(round(step_ticks * note.get("len", 1.0))))
                        midi = int(np.clip(note["midi"] + head.transpose, 0, 127))
                        events.append((head.output, start, dur, midi,
                                       int(note.get("vel", 100)), tr.name))
                    t += step_ticks
        events.sort(key=lambda e: (e[1], e[0]))
        return events

    # ------------------------------------------------------------------
    def to_midi_bytes(self, events: list[tuple], path: str | None = None):
        """Write a type-1 SMF (uses the repo's MIDI helper when available)."""
        try:
            from sound.utils.midi import write_events  # type: ignore
            return write_events(events, self.tpb, path)
        except Exception:
            import struct
            data = bytearray()
            chans = sorted({e[0] for e in events})
            data += b"MThd" + struct.pack(">IHHH", 6, 1, len(chans) + 1, self.tpb)
            # tempo track
            tempo = int(60_000_000 / self.bpm)
            data += b"MTrk" + struct.pack(">I", 11) + b"\x00\xff\x51\x03" + \
                tempo.to_bytes(3, "big") + b"\x00\xff\x2f\x00"
            for ci, ch in enumerate(chans):
                evs = [e for e in events if e[0] == ch]
                body = bytearray()
                last = 0
                for _, st, du, midi, vel, _tr in evs:
                    body += _vlq(st - last) + bytes([0x90 | ci, midi & 127, vel & 127])
                    body += _vlq(du) + bytes([0x80 | ci, midi & 127, 0])
                    last = st + du
                body += b"\x00\xff\x2f\x00"
                data += b"MTrk" + struct.pack(">I", len(body)) + body
            if path:
                with open(path, "wb") as f:
                    f.write(bytes(data))
            return bytes(data)


def _vlq(v: int) -> bytes:
    v = max(0, int(v))
    out = [v & 0x7F]
    v >>= 7
    while v:
        out.insert(0, (v & 0x7F) | 0x80)
        v >>= 7
    return bytes(out)


def demo() -> None:
    seq = MultiPlayheadSequencer(bpm=118)
    tr = seq.add_track("pool", steps=16)
    scale = [36, 39, 43, 46, 48, 51, 55]
    for i in range(16):
        tr.set_step(i, midi=scale[i % len(scale)], vel=100 if i % 4 == 0 else 74,
                    length=0.9 if i % 4 else 1.6)
    tr.add_head(length=16, direction="fwd", division=4, output="bass")
    tr.add_head(length=12, direction="bwd", division=3, output="arpA",
                seq_type="EUCLID", euclid=(7, 0))
    tr.add_head(length=7, direction="pendulum", division=6, output="arpB",
                seq_type="PACHINKO", seed=3, transpose=12)

    ev = seq.generate(bars=4)
    per_out: dict[str, int] = {}
    for e in ev:
        per_out[e[0]] = per_out.get(e[0], 0) + 1
    print(f"{len(ev)} events over 4 bars: {per_out}")
    # phase check: the 16/12/7 pool lengths only realign at lcm = 336 steps
    print("LCM of head lengths:", np.lcm.reduce([16, 12, 7]))
    mid = seq.to_midi_bytes(ev)
    print(f"SMF bytes: {len(mid)}")
    assert len(mid) > 60 and len(ev) > 20


if __name__ == "__main__":
    demo()
