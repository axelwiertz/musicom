# -*- coding: utf-8 -*-
"""Tagged chromatic ornaments + step-resolution checker (Phase 3 P1).

VOICE_ROLE_WORKFLOW_PLAN.md (§3, §4): replace the binary in-scale/out-of-scale
wall with a tiered pitch discipline. A non-scale pitch is legal ONLY through
one of the four classical chromatic ornaments, each a rule, each countable,
each tagged. The four ornaments:

    passing        chromatic passing tone  — fills a whole-step gap,
                     half-step in travel direction (C -> C# -> D)
    neighbor       chromatic neighbor      — half-step above/below a chord
                     tone, returns (C Db C)
    approach       approach note           — chromatic lead-in to a strong
                     target (B -> C)
    leading_tone   secondary leading tone  — raises 7th toward next chord
                     root (F# -> G)

Tag schema (canonical note dict — same shape as ``harmony_writer`` notes, plus
two optional tag keys):

    {
        "pitch": int, "volume": int, "start_tick": int, "end_tick": int,
        "weight": "strong" | "weak",            # optional (default: onset grid)
        "ornament": None | "passing" | "neighbor" | "approach" | "leading_tone",
        "resolve_pitch": int,                   # for ornaments: the scale tone it resolves to
    }

This module is PURE — no engine deps, stdlib only. It does not decide *where*
to place ornaments (that is the P2 embellish stage); it defines the rules and
the resolution predicate so a fixture can build tagged ornaments and the audit
(``workflows.pitch_audit``) can verify them.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "ORNAMENT_KINDS",
    "is_chromatic",
    "is_step",
    "resolve_by_step",
    "chromatic_passing_tone",
    "chromatic_neighbor",
    "approach_note",
    "secondary_leading_tone",
]

ORNAMENT_KINDS = ("passing", "neighbor", "approach", "leading_tone")

# A chromatic ornament resolves to a scale tone by a semitone or whole tone.
_STEP_SEMITONES = (1, 2)


def is_chromatic(pitch: int, scale_pcs: Iterable[int]) -> bool:
    """True if ``pitch``'s pitch class is NOT in the scale."""
    return (pitch % 12) not in set(scale_pcs)


def is_step(a: int, b: int) -> bool:
    """True if two pitches are a semitone or whole tone apart (a step)."""
    return abs(a - b) in _STEP_SEMITONES


def resolve_by_step(ornament_pitch: int, resolve_pitch: int,
                    scale_pcs: Iterable[int]) -> bool:
    """An ornament resolves iff its target is a scale tone within one step.

    The invariant's condition (b): ``tagged chromatic_ornament AND resolves by
    step to a scale tone within 1 grid step``. This predicate checks the
    *pitch* half — the target must be in-scale AND a semitone/whole-tone away.
    The *time* half (within 1 grid step) is checked by the audit, which knows
    the grid.
    """
    if (resolve_pitch % 12) not in set(scale_pcs):
        return False
    return is_step(ornament_pitch, resolve_pitch)


def _note(pitch: int, start_tick: int, end_tick: int, volume: int,
          kind: str, resolve_pitch: int, weight: str = "weak") -> Dict:
    return {
        "pitch": pitch, "volume": volume,
        "start_tick": start_tick, "end_tick": end_tick,
        "weight": weight, "ornament": kind, "resolve_pitch": resolve_pitch,
    }


def chromatic_passing_tone(prev_pitch: int, next_pitch: int,
                           start_tick: int, end_tick: int,
                           volume: int = 90) -> Dict:
    """Chromatic passing tone between two scale notes a whole step apart.

    ``prev_pitch`` and ``next_pitch`` must be exactly 2 semitones apart (a
    whole-step gap). The passing tone is the half-step between them, moving in
    the travel direction (ascending C->D gives C#, descending D->C gives Db —
    the same MIDI pitch 61 either way). Resolves to ``next_pitch``.
    """
    if abs(next_pitch - prev_pitch) != 2:
        raise ValueError(
            f"chromatic passing tone needs a whole-step gap (2 semitones), "
            f"got {prev_pitch}->{next_pitch} = {next_pitch - prev_pitch}")
    mid = (prev_pitch + next_pitch) // 2
    return _note(mid, start_tick, end_tick, volume,
                 "passing", next_pitch)


def chromatic_neighbor(target_pitch: int, above: bool,
                       start_tick: int, end_tick: int,
                       volume: int = 90) -> Dict:
    """Chromatic neighbor: half-step above (or below) a chord tone, returns.

    ``above=True`` -> target+1 (e.g. C Db C); ``above=False`` -> target-1.
    Resolves back to ``target_pitch``.
    """
    pitch = target_pitch + 1 if above else target_pitch - 1
    return _note(pitch, start_tick, end_tick, volume,
                 "neighbor", target_pitch)


def approach_note(target_pitch: int, start_tick: int, end_tick: int,
                  volume: int = 90) -> Dict:
    """Chromatic approach note: half-step below a strong target (B -> C).

    Resolves up by semitone to ``target_pitch``.
    """
    return _note(target_pitch - 1, start_tick, end_tick, volume,
                 "approach", target_pitch)


def secondary_leading_tone(chord_root: int, start_tick: int, end_tick: int,
                           volume: int = 90) -> Dict:
    """Secondary leading tone: half-step below the next chord root (F# -> G).

    Raises the 7th toward ``chord_root``; resolves up by semitone.
    """
    return _note(chord_root - 1, start_tick, end_tick, volume,
                 "leading_tone", chord_root)


def demo() -> str:
    """Prove each ornament's pitch, tag, and step-resolution against C major."""
    scale = [0, 2, 4, 5, 7, 9, 11]
    cases = [
        chromatic_passing_tone(60, 62, 0, 240),       # C -> C# -> D
        chromatic_neighbor(60, True, 0, 240),          # C Db C
        chromatic_neighbor(60, False, 0, 240),         # C B C
        approach_note(60, 0, 240),                     # B -> C
        secondary_leading_tone(67, 0, 240),            # F# -> G
    ]
    for n in cases:
        ok = resolve_by_step(n["pitch"], n["resolve_pitch"], scale)
        assert ok, (n["pitch"], n["resolve_pitch"])
        print(f"{n['ornament']:12s} pitch={n['pitch']:3d} "
              f"-> {n['resolve_pitch']:3d}  resolves={ok}")
    # whole-step gap is enforced
    try:
        chromatic_passing_tone(60, 61, 0, 240)
    except ValueError as e:
        print(f"gap guard: {e}")
    else:
        raise AssertionError("expected ValueError for non-whole-step gap")
    return "ornament demo OK"


if __name__ == "__main__":
    print(demo())
