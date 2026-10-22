# -*- coding: utf-8 -*-
"""Deterministic variation operators over a MusicUnit's event list (Phase 3 P2).

VOICE_ROLE_WORKFLOW_PLAN.md (§2 stage 4 "vary", §7-P2): structural variation
transforms applied to a cell's material — inversion, retrograde, transposition,
density scaling, and rhythmic displacement. Each is a pure function over a
``list[MusicEvent]``: it never mutates the input, and it preserves the
zero-drift terminal silent landmark (pitch 0) so the result still passes
``composer.validate()``.

These are the building blocks for the ``counter`` role's ``transform`` mode
(``harmony_writer.counterline``) and for per-section variation. Purely
mechanical — no engine deps beyond ``structures.MusicEvent``.
"""

from __future__ import annotations

from typing import List, Sequence

from structures import MusicEvent

__all__ = [
    "invert", "retrograde", "transpose", "density_scale", "displace",
    "audible", "landmarks",
]


def audible(events: Sequence[MusicEvent]) -> List[MusicEvent]:
    """Return only the audible events (pitch > 0)."""
    return [e for e in events if e.pitch > 0]


def landmarks(events: Sequence[MusicEvent]) -> List[MusicEvent]:
    """Return only the silent landmarks (pitch == 0)."""
    return [e for e in events if e.pitch == 0]


def invert(events: Sequence[MusicEvent], axis: int) -> List[MusicEvent]:
    """Chromatic inversion around a pitch axis: ``pitch' = 2*axis - pitch``.

    Landmarks are preserved verbatim. E.g. invert C-E-G (60,64,67) around 60
    -> 60, 56, 53.
    """
    out: List[MusicEvent] = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
        else:
            out.append(MusicEvent(2 * axis - e.pitch, e.volume,
                                  e.start_tick, e.end_tick))
    return out


def transpose(events: Sequence[MusicEvent], semitones: int) -> List[MusicEvent]:
    """Shift every audible pitch by ``semitones`` (register shift, not key)."""
    out: List[MusicEvent] = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
        else:
            out.append(MusicEvent(e.pitch + semitones, e.volume,
                                  e.start_tick, e.end_tick))
    return out


def retrograde(events: Sequence[MusicEvent],
               section_len: int | None = None) -> List[MusicEvent]:
    """Reverse the audible events in time (mirror around ``section_len``).

    Each audible event's new start = ``L - old_end``, new end = ``L - old_start``
    where ``L`` is the cell length. The terminal landmark stays at ``L`` so the
    unit still ends on the exact cell boundary.
    """
    if section_len is None:
        section_len = max((e.end_tick for e in events), default=0)
    rev: List[MusicEvent] = []
    for e in events:
        if e.pitch == 0:
            continue
        rev.append(MusicEvent(e.pitch, e.volume,
                              section_len - e.end_tick, section_len - e.start_tick))
    # time-sorted so downstream onset order matches the reversed playback
    rev.sort(key=lambda e: e.start_tick)
    # re-add the terminal landmark at the cell boundary
    rev.append(MusicEvent(0, 0, section_len, section_len))
    return rev


def density_scale(events: Sequence[MusicEvent], factor: float) -> List[MusicEvent]:
    """Thin the audible events to a fraction ``factor`` (0 < factor <= 1).

    Keeps an evenly-spaced subset of size ``ceil(n * factor)`` (first and last
    always kept). Landmarks preserved. factor > 1 is NOT supported — thickening
    needs new material, which is the generative method's job, not a transform.
    """
    if not (0 < factor <= 1):
        raise ValueError(f"density_scale factor must be in (0, 1], got {factor}")
    aud = audible(events)
    lms = landmarks(events)
    n = len(aud)
    if n == 0:
        return list(events)
    keep = max(1, int(round(n * factor)))
    if keep >= n:
        return list(events)
    # evenly-spaced indices over [0, n-1], endpoints included
    idx = {int(round(i * (n - 1) / (keep - 1))) for i in range(keep)}
    out = [aud[i] for i in sorted(idx)]
    return out + lms


def displace(events: Sequence[MusicEvent], offset_ticks: int) -> List[MusicEvent]:
    """Shift every audible onset by ``offset_ticks`` (rhythmic displacement).

    Durations are preserved; notes are clamped so no tail crosses the cell
    boundary (the terminal landmark's tick). Landmarks preserved.
    """
    L = max((e.end_tick for e in events), default=0)
    out: List[MusicEvent] = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        s = e.start_tick + offset_ticks
        e_ = e.end_tick + offset_ticks
        if s < 0:
            s = 0
        if e_ > L:
            e_ = L
        if e_ <= s:
            e_ = min(L, s + 1)
        out.append(MusicEvent(e.pitch, e.volume, s, e_))
    return out


def demo() -> str:
    """Prove each transform is deterministic and landmark-preserving."""
    events = [
        MusicEvent(60, 90, 0, 480),      # C
        MusicEvent(64, 90, 480, 960),    # E
        MusicEvent(67, 90, 960, 1440),   # G
        MusicEvent(0, 0, 1920, 1920),    # terminal landmark
    ]
    inv = invert(events, 60)
    assert [e.pitch for e in inv] == [60, 56, 53, 0], [e.pitch for e in inv]
    tr = transpose(events, 12)
    assert [e.pitch for e in tr] == [72, 76, 79, 0]
    rev = retrograde(events, 1920)
    # G ends at 1440 -> new start 480; C starts 0 ends 480 -> new end 1920
    assert [e.pitch for e in rev] == [67, 64, 60, 0]
    assert rev[-1].end_tick == 1920
    thin = density_scale(events, 0.5)
    assert [e.pitch for e in thin if e.pitch > 0] == [60, 67]
    disp = displace(events, 240)
    assert [e.start_tick for e in disp if e.pitch > 0] == [240, 720, 1200]
    # purity: input untouched
    assert [e.pitch for e in events] == [60, 64, 67, 0]
    print("invert:", [e.pitch for e in inv])
    print("transpose+12:", [e.pitch for e in tr])
    print("retrograde:", [e.pitch for e in rev])
    print("density_scale 0.5:", [e.pitch for e in thin if e.pitch > 0])
    print("displace+240:", [e.start_tick for e in disp if e.pitch > 0])
    return "variation demo OK"


if __name__ == "__main__":
    print(demo())
