# -*- coding: utf-8 -*-
"""MIDI note-editor transforms: Strum and Stretch Selection — Cubase 16
Key Editor style.

Replicable logic from the Cubase 16 announcement (Synthtopia / MusicTech,
2026-11-04).  Two of the new Key Editor functions are pure *event
arithmetic*, which is exactly what a tick-based engine can replicate:

- **Strum** — spread the notes of a chord in time so a programmed block
  chord takes on a strummed performance character.  Options modelled here:
  direction (up / down / alternate / random), total spread in ticks,
  curve (linear / ease-in / ease-out / exponential), velocity ramp across
  the strum (down-strums naturally accent the first string), per-note
  random jitter, and chord grouping by start tick so only simultaneous notes
  are affected.
- **Stretch Selection** — expand or compress a MIDI passage to a new
  duration, including the accelerando / ritardando shapes: the note onsets
  are remapped through a time-warp curve and the note lengths follow the
  local warp derivative, so a passage stretched with an "accel" curve speeds
  up toward its end instead of merely scaling.

Events are plain tuples ``(pitch, velocity, start_tick, end_tick)`` — the
same shape as ``structures.MusicEvent`` — plus a ``Note`` dataclass for
convenience.  Nothing here touches audio.

Usage::

    from sound.generators.strum_stretch import strum, stretch_selection
    strummed = strum(notes, spread_ticks=48, direction="down")
    sped_up = stretch_selection(notes, target_ticks=1920 * 2,
                                curve="accel", gamma=1.8)
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

NoteTuple = Tuple[int, int, int, int]


@dataclass
class Note:
    pitch: int
    velocity: int
    start: int
    end: int

    def as_tuple(self) -> NoteTuple:
        return (self.pitch, self.velocity, self.start, self.end)


def _as_notes(notes: Iterable) -> List[Note]:
    out: List[Note] = []
    for n in notes:
        if isinstance(n, Note):
            out.append(n)
        elif hasattr(n, "pitch") and hasattr(n, "start_tick"):
            out.append(Note(int(n.pitch), int(getattr(n, "volume", 100)),
                            int(n.start_tick), int(n.end_tick)))
        else:
            p, v, s, e = n
            out.append(Note(int(p), int(v), int(s), int(e)))
    return out


def _curve(x: float, kind: str, gamma: float) -> float:
    x = min(1.0, max(0.0, x))
    if kind == "linear":
        return x
    if kind == "ease_in":
        return x ** gamma
    if kind == "ease_out":
        return 1.0 - (1.0 - x) ** gamma
    if kind == "exponential":
        g = max(0.05, gamma)
        return (pow(g, x) - 1.0) / (g - 1.0)
    if kind == "s_curve":
        return 0.5 - 0.5 * __import__("math").cos(3.141592653589793 * x)
    return x


def _group_chords(notes: Sequence[Note], tol: int = 0) -> List[List[int]]:
    """Group indices of notes whose onsets are within ``tol`` ticks."""
    order = sorted(range(len(notes)), key=lambda i: (notes[i].start, notes[i].pitch))
    groups: List[List[int]] = []
    for i in order:
        if groups and abs(notes[i].start - notes[groups[-1][0]].start) <= tol:
            groups[-1].append(i)
        else:
            groups.append([i])
    return groups


def strum(notes: Iterable, spread_ticks: int = 40, direction: str = "down",
          curve: str = "linear", gamma: float = 1.6,
          velocity_ramp: float = 0.15, jitter_ticks: int = 0,
          chord_tolerance: int = 2, seed: int | None = None,
          alternate_offset: int = 0) -> List[NoteTuple]:
    """Spread simultaneous notes in time.

    direction : "down" (low → high), "up", "alternate" or "random".
    curve : shape of the intra-strum spacing ("linear", "ease_in",
        "ease_out", "exponential", "s_curve").
    velocity_ramp : fractional velocity change from first to last note
        (0.15 = +15 % on the last note, -0.2 = quieter on the last).
    jitter_ticks : uniform random timing jitter per note (± n ticks).
    """
    ns = _as_notes(notes)
    rng = random.Random(seed)
    out = [Note(n.pitch, n.velocity, n.start, n.end) for n in ns]
    for g_idx, group in enumerate(_group_chords(ns, tol=chord_tolerance)):
        if len(group) < 2:
            continue
        ordered = sorted(group, key=lambda i: (ns[i].pitch, ns[i].start))
        if direction == "down":
            order = ordered
        elif direction == "up":
            order = list(reversed(ordered))
        elif direction == "alternate":
            order = ordered if (g_idx + alternate_offset) % 2 == 0 else list(reversed(ordered))
        elif direction == "random":
            order = ordered[:]
            rng.shuffle(order)
        else:
            raise ValueError("direction must be down/up/alternate/random")
        n = len(order)
        base = ns[group[0]].start
        for k, i in enumerate(order):
            u = k / (n - 1) if n > 1 else 0.0
            offset = int(round(_curve(u, curve, gamma) * spread_ticks))
            jit = rng.randint(-jitter_ticks, jitter_ticks) if jitter_ticks else 0
            out[i].start = base + offset + jit
            # keep note length constant; only the onset moves
            length = ns[i].end - ns[i].start
            out[i].end = out[i].start + length
            if velocity_ramp:
                v = ns[i].velocity * (1.0 + velocity_ramp * u)
                out[i].velocity = int(max(1, min(127, round(v))))
    return [n.as_tuple() for n in out]


def stretch_selection(notes: Iterable, factor: float | None = None,
                      target_ticks: int | None = None,
                      curve: str = "linear", gamma: float = 1.8,
                      anchor_start: int | None = None,
                      min_length: int = 1) -> List[NoteTuple]:
    """Time-warp a passage to a new length.

    ``factor`` multiplies the passage length; ``target_ticks`` sets the new
    length in ticks (wins over ``factor``).  ``curve``:
    "linear" (uniform), "accel" (intervals shrink toward the end),
    "rit" (intervals grow toward the end), "s_curve" (slow-fast-slow).
    Note lengths follow the local warp derivative.

    The passage is the span from the earliest onset to the latest note end
    (or ``anchor_start`` if given).
    """
    ns = _as_notes(notes)
    if not ns:
        return []
    t0 = anchor_start if anchor_start is not None else min(n.start for n in ns)
    t1 = max(n.end for n in ns)
    span = max(1, t1 - t0)
    new_span = int(round(target_ticks)) if target_ticks is not None \
        else int(round(span * (1.0 if factor is None else float(factor))))
    new_span = max(1, new_span)

    def warp(u: float) -> float:
        if curve == "accel":
            return 1.0 - (1.0 - u) ** gamma      # fast at the end
        if curve == "rit":
            return u ** gamma                    # slow at the end
        return _curve(u, curve, gamma)

    eps = 1e-4
    out: List[NoteTuple] = []
    for n in ns:
        u0 = min(1.0, max(0.0, (n.start - t0) / span))
        u1 = min(1.0, max(0.0, (n.end - t0) / span))
        s = t0 + warp(u0) * new_span
        e = t0 + warp(u1) * new_span
        if e - s < min_length:
            e = s + min_length
        out.append((n.pitch, n.velocity, int(round(s)), int(round(e))))
    out.sort(key=lambda x: (x[2], x[0]))
    return out


def groove_shift(notes: Iterable, amount_ticks: int,
                 every: int = 2, offset: int = 0) -> List[NoteTuple]:
    """Delay every Nth onset — quick 'push/pull' feel helper used with strum."""
    ns = _as_notes(notes)
    order = sorted(range(len(ns)), key=lambda i: ns[i].start)
    out = [n.as_tuple() for n in ns]
    for rank, i in enumerate(order):
        if (rank + offset) % every == 0:
            p, v, s, e = out[i]
            out[i] = (p, v, s + amount_ticks, e + amount_ticks)
    return out


def demo() -> None:
    """Strum a four-note chord, then warp a two-bar phrase with an accel."""
    # --- strum -----------------------------------------------------------
    chord = [(60, 96, 0, 480), (64, 96, 0, 480),
             (67, 96, 0, 480), (72, 96, 0, 480)]
    s_down = strum(chord, spread_ticks=40, direction="down", curve="ease_out",
                   velocity_ramp=0.18, seed=4)
    s_up = strum(chord, spread_ticks=40, direction="up", seed=4)
    print("strum demo (down, 40 ticks, ease_out):")
    for p, v, st, en in s_down:
        print(f"  pitch {p} vel {v} start {st:3d} len {en - st}")
    assert [n[2] for n in s_down] == [0, 19, 33, 40], [n[2] for n in s_down]
    assert s_down[0][1] < s_down[-1][1], "velocity ramp must rise"
    up_map = {p: st for p, v, st, e in s_up}
    assert up_map[72] == 0 and up_map[60] == 40, up_map

    # --- stretch ---------------------------------------------------------
    phrase = [(60, 100, 0, 240), (62, 100, 240, 480), (64, 100, 480, 720),
              (65, 100, 720, 960), (67, 100, 960, 1200), (69, 100, 1200, 1440)]
    accel = stretch_selection(phrase, target_ticks=2880, curve="accel", gamma=2.0)
    rit = stretch_selection(phrase, target_ticks=2880, curve="rit", gamma=2.0)
    lin = stretch_selection(phrase, factor=2.0)

    def gaps(seq):
        starts = [n[2] for n in seq]
        return [b - a for a, b in zip(starts[:-1], starts[1:])]

    print(f"\nstretch demo: 1440-tick phrase -> 2880 ticks")
    print(f"  linear gaps: {gaps(lin)}")
    print(f"  accel gaps : {gaps(accel)}  (shrink toward the end)")
    print(f"  rit gaps   : {gaps(rit)}  (grow toward the end)")
    assert gaps(accel)[0] > gaps(accel)[-1], gaps(accel)
    assert gaps(rit)[0] < gaps(rit)[-1], gaps(rit)
    assert all(g > 0 for g in gaps(accel) + gaps(rit) + gaps(lin))
    assert max(n[3] for n in accel) <= 2880 + 1
    assert all(n[3] > n[2] for n in accel)
    print("demo OK")


if __name__ == "__main__":
    demo()
