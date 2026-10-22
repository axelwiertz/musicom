# -*- coding: utf-8 -*-
"""Shared realization spine (Phase 4 P0) — raw notes -> validated MusicUnit.

METHOD_CONTRACT_PLAN.md (§2.3): the method-agnostic post-processing every
composition method feeds into, so the cron stops re-writing snap/harmonize/audit
per night. Stages (each already shipped as a standalone module in Phase 3):

    snap       classify_weight + tiered snap (strong = scale+chord, weak = scale)
    harmonize  strong-beat chord-tone snap (folded into the tiered snap)
    vary       (no-op here; workflows.variation plugs in at P2)
    embellish  (no-op here; rules.ornament plugs in at P2)
    validate   zero-drift terminal landmark + (start,pitch) dedup

``realize()`` accepts BOTH raw ``RawNote`` (gets snapped) and already-realized
``MusicEvent`` (passed through — the ``DefaultMethod`` legacy fill). That
union is what keeps ``compose()`` byte-identical when the spine is adopted.

Pure module — engine deps only, deterministic.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Union

from structures import MusicEvent, MusicUnit
from utilities.constants import SCALE_PATTERNS

from workflows.cell_engine import CellContext
from workflows.method_contract import MethodOutput, RawNote

__all__ = ["realize"]


def _nearest_scale_pitch(raw: float, scale_pcs: set) -> int:
    """Nearest MIDI pitch whose pitch class is in the scale, around ``raw``."""
    center = int(round(raw))
    return min((p for p in range(center - 6, center + 7) if (p % 12) in scale_pcs),
               key=lambda p: abs(p - raw))


def _snap(raw_pitch: float, weight: str, scale_pcs: set,
          chord_tones: Optional[List[int]]) -> int:
    """Strong = scale THEN chord (in-scale AND in-chord); weak = scale only.

    Mirrors ``ScaleQuantizer.tiered_quantize`` semantics, but against an
    arbitrary pitch-class set (so the full ``SCALE_PATTERNS`` catalogue works,
    not just ScaleQuantizer's built-in six scales).
    """
    pitch = _nearest_scale_pitch(raw_pitch, scale_pcs)
    if weight == "strong" and chord_tones:
        pitch = min(chord_tones, key=lambda c: abs(c - pitch))
    return pitch


def realize(method_output: Sequence[MethodOutput], ctx: CellContext,
            role: str = "lead", grid: int = 240,
            scale_pcs: Optional[Sequence[int]] = None) -> MusicUnit:
    """Realize raw (or pre-realized) method output into a zero-drift MusicUnit.

    Raw ``RawNote`` -> mapped into ``ctx.register``, weight-classified from the
    onset grid, snapped to scale (and chord on strong beats), grid-locked to
    ``grid`` ticks, deduped by (start, pitch). ``MusicEvent`` -> passed through
    unchanged (already realized). A terminal silent landmark guarantees the
    unit ends exactly at ``ctx.section_len``.

    ``role`` is threaded through for the P2 vary/embellish stages; it does not
    change the P0 snap/harmonize behaviour.
    """
    if scale_pcs is None:
        scale_pcs = SCALE_PATTERNS.get(ctx.pattern)
    if scale_pcs is None:
        raise ValueError(
            f"unknown pattern {ctx.pattern!r}; use one of {sorted(SCALE_PATTERNS)}")
    pcs = set(scale_pcs)
    strong_grid = tuple(ctx.strong_beat_grid)
    chord_tones = list(ctx.chord_tones) if ctx.chord_tones else None
    lo, hi = ctx.register
    section_len = ctx.section_len

    events: List[MusicEvent] = []
    seen: Dict[tuple, int] = {}

    for note in method_output:
        if isinstance(note, MusicEvent):
            # already realized -> pass through (DefaultMethod legacy fill)
            if note.pitch > 0:
                events.append(note)
            continue

        # RawNote -> snap + harmonize + grid-lock
        raw_pitch = lo + note.pitch_index * (hi - lo)
        weight = _classify(note.onset, strong_grid, ctx.bar_ticks)
        pitch = _snap(raw_pitch, weight, pcs, chord_tones)

        onset = int(round(note.onset / grid) * grid)
        if section_len:
            onset = max(0, min(onset, section_len - 1))
            end = min(onset + grid, section_len)
        else:
            end = onset + grid

        key = (onset, pitch)
        if key in seen:  # post-quantize collision (machine-gun repeat)
            continue
        seen[key] = 1
        events.append(MusicEvent(pitch, note.velocity, onset, end))

    return _unit(events, section_len)


def _classify(onset: float, strong_grid: tuple, bar_ticks: int) -> str:
    from sound.synthesis.scale_quantizer import classify_weight
    return classify_weight(int(round(onset)), strong_grid, bar_ticks)


def _unit(events: List[MusicEvent], section_len: Optional[int]) -> MusicUnit:
    """Wrap events with a terminal silent landmark (zero-drift invariant)."""
    unit = MusicUnit()
    for e in events:
        unit.add_event(e)
    if section_len is None:
        section_len = max((e.end_tick for e in events), default=0)
    unit.add_event(MusicEvent(0, 0, section_len, section_len))
    return unit


def demo() -> str:
    """Prove raw notes realize to a validated, in-key, grid-locked unit."""
    from workflows.pitch_audit import audit_voice
    ctx = CellContext(
        key="C", pattern="major", chord_tones=(60, 64, 67),
        register=(60, 84), density=1.0, root_midi=48,
        section_bars=1, section_len=1920, bar_ticks=1920,
        voice_idx=0, instrument_name="Flute",
    )
    raw = [
        RawNote(pitch_index=0.55, onset=123.4, velocity=90),  # off-grid chromatic-ish
        RawNote(pitch_index=0.3, onset=500.0, velocity=90),
        RawNote(pitch_index=0.9, onset=960.0, velocity=90),   # strong beat -> chord
    ]
    unit = realize(raw, ctx, "lead", grid=240)
    notes = [e for e in unit.events if e.pitch > 0]
    r = audit_voice(unit.events, [0, 2, 4, 5, 7, 9, 11], strong_grid=(0, 960))
    print("realized pitches:", [e.pitch for e in notes])
    print("onsets:", [e.start_tick for e in notes], "(all % 240 == 0:",
          all(e.start_tick % 240 == 0 for e in notes), ")")
    print("audit:", r.summary())
    assert r.passes, r.summary()
    assert all(e.start_tick % 240 == 0 for e in notes)
    return "realize_spine demo OK"


if __name__ == "__main__":
    print(demo())
