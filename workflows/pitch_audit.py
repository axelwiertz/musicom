# -*- coding: utf-8 -*-
"""Revised scale/chord audit with the tagged-ornament exemption (Phase 3 P1).

VOICE_ROLE_WORKFLOW_PLAN.md (§4): the old audit demanded
``pitch % 12 in KEY_PCS`` for every pitched note -> 0 violations. That cannot
survive chromatic passing tones. The new invariant is:

    every pitched note is EITHER
      (a) in-scale AND in-chord,  OR
      (b) tagged chromatic_ornament AND resolves by step to a scale tone
          within 1 grid step

Still hard: 0 un-tagged out-of-scale, and a tagged ornament that does NOT
resolve is still flagged. This module is the additive audit — the existing
audit functions stay, and the golden-hash gates are untouched.

Input: a per-voice note stream (list of dicts, ``StructuralNote``, or
``MusicEvent``-shaped objects — anything with ``pitch``/``start_tick``/
``end_tick`` attributes or keys). Each note MAY carry ``weight`` ("strong"/
"weak") and ``ornament``/``resolve_pitch`` tags (see ``rules.ornament``).

Pure module, stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from rules.ornament import resolve_by_step
from sound.synthesis.scale_quantizer import classify_weight

__all__ = ["AuditResult", "audit_voice"]


def _f(note: Any, key: str, default=None):
    """Read a field from a dict, dataclass, or MusicEvent-shaped object."""
    if isinstance(note, dict):
        return note.get(key, default)
    return getattr(note, key, default)


def _i(note: Any, key: str, default: int = 0) -> int:
    """Read an int field (pitch/start_tick/end_tick) safely."""
    v = _f(note, key, default)
    return int(v) if v is not None else default


def _audible(note: Any) -> bool:
    return _i(note, "pitch", 0) > 0


@dataclass
class AuditResult:
    """Counts from one voice's pitch-discipline audit."""
    total: int = 0
    audible: int = 0
    strong_ok: int = 0
    weak_in_scale: int = 0
    tagged_ornaments: int = 0
    tagged_resolving: int = 0
    tagged_non_resolving: int = 0
    untagged_out_of_scale: int = 0
    strong_violations: int = 0
    collisions: int = 0
    violations: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def passes(self) -> bool:
        """True iff the pitch discipline holds: no un-tagged out-of-scale, no
        non-resolving ornament, no strong note off scale/chord."""
        return (self.untagged_out_of_scale == 0
                and self.tagged_non_resolving == 0
                and self.strong_violations == 0)

    def summary(self) -> str:
        status = "PASS" if self.passes else "FAIL"
        return (f"[{status}] total={self.audible} "
                f"strong_ok={self.strong_ok} weak_in_scale={self.weak_in_scale} "
                f"tagged={self.tagged_ornaments} "
                f"resolving={self.tagged_resolving} "
                f"non_resolving={self.tagged_non_resolving} "
                f"untagged_out={self.untagged_out_of_scale} "
                f"strong_viol={self.strong_violations} collisions={self.collisions}")


def audit_voice(notes: Sequence[Any], scale_pcs: Sequence[int],
                chord_pcs_by_bar: Optional[Dict[int, Sequence[int]]] = None,
                strong_grid: Sequence[int] = (0, 960),
                bar_ticks: int = 1920, grid: int = 240,
                dedup: bool = True) -> AuditResult:
    """Audit one voice's note stream against the P1 pitch invariant.

    Args:
        notes: the voice's events (dicts / StructuralNote / MusicEvent).
        scale_pcs: the key's pitch classes (e.g. C major -> [0,2,4,5,7,9,11]).
        chord_pcs_by_bar: optional {bar_index: chord pitch classes}; a STRONG
            note must be in-chord when this is provided. Omit to skip the
            in-chord half of the strong check (in-scale only).
        strong_grid: strong-beat tick offsets within a bar (default 4/4 1&3).
        bar_ticks: ticks per bar (BAR, default 1920).
        grid: one grid step in ticks — a resolving ornament's target must
            appear within this many ticks after the ornament (default 240 =
            8th note).
        dedup: also count (start_tick, pitch) collisions (default True).

    Returns an ``AuditResult``; ``result.passes`` is the hard gate.
    """
    scale = set(scale_pcs)
    r = AuditResult()
    audible = [n for n in notes if _audible(n)]
    r.audible = len(audible)

    # index of resolve target by pitch, sorted by start_tick, for the
    # "within 1 grid step" timing check
    by_pitch: Dict[int, List[Any]] = {}
    for n in audible:
        by_pitch.setdefault(_i(n, "pitch"), []).append(n)

    seen: Dict[tuple, int] = {}
    for n in audible:
        pitch = _i(n, "pitch")
        start = _i(n, "start_tick", 0)
        end = _i(n, "end_tick", 0)
        weight = _f(n, "weight", None)
        if weight not in ("strong", "weak"):
            weight = classify_weight(start, tuple(strong_grid), bar_ticks)
        ornament = _f(n, "ornament", None)
        resolve_pitch = _f(n, "resolve_pitch", None)

        r.total += 1
        in_scale = (pitch % 12) in scale
        bar = start // bar_ticks
        chord_pcs = None
        if chord_pcs_by_bar is not None:
            chord_pcs = chord_pcs_by_bar.get(bar)
        in_chord = True if chord_pcs is None else (pitch % 12) in set(chord_pcs)

        if weight == "strong":
            if in_scale and in_chord:
                r.strong_ok += 1
            else:
                r.strong_violations += 1
                r.violations.append({
                    "kind": "strong", "pitch": pitch, "start_tick": start,
                    "in_scale": in_scale, "in_chord": in_chord, "bar": bar})
        else:  # weak
            if in_scale:
                r.weak_in_scale += 1
            elif ornament is not None:
                r.tagged_ornaments += 1
                if _ornament_resolves(pitch, resolve_pitch, scale, by_pitch,
                                      start, grid):
                    r.tagged_resolving += 1
                else:
                    r.tagged_non_resolving += 1
                    r.violations.append({
                        "kind": "non_resolving", "pitch": pitch,
                        "start_tick": start, "ornament": ornament,
                        "resolve_pitch": resolve_pitch})
            else:
                r.untagged_out_of_scale += 1
                r.violations.append({
                    "kind": "untagged", "pitch": pitch, "start_tick": start,
                    "bar": bar})

        if dedup:
            key = (start, pitch)
            if key in seen:
                r.collisions += 1
            else:
                seen[key] = 1

    return r


def _ornament_resolves(pitch: int, resolve_pitch: Optional[int],
                       scale: set, by_pitch: Dict[int, List[Any]],
                       start: int, grid: int) -> bool:
    """A tagged ornament resolves iff its target is a scale tone within one
    step (pitch) AND appears within ``grid`` ticks (time)."""
    if resolve_pitch is None:
        return False
    rp = int(resolve_pitch)
    if (rp % 12) not in scale:
        return False
    if not resolve_by_step(pitch, rp, scale):
        return False
    # time half: the target must actually occur within `grid` ticks AFTER the
    # ornament's onset (the resolution note is the following scale tone).
    candidates = by_pitch.get(rp, [])
    for c in candidates:
        cs = _i(c, "start_tick", 0)
        if 0 < cs - start <= grid:
            return True
    return False


def demo() -> str:
    """Prove the gate: tagged passing tone passes, non-resolving fails."""
    from rules.ornament import chromatic_passing_tone, approach_note
    scale = [0, 2, 4, 5, 7, 9, 11]  # C major
    # bar of 8ths: C(0) strong, C#(240) passing weak, D(480) strong, rest
    notes = [
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
        chromatic_passing_tone(60, 62, 240, 480),   # C# -> resolves to D
        {"pitch": 62, "volume": 90, "start_tick": 480, "end_tick": 720, "weight": "strong"},
        {"pitch": 64, "volume": 90, "start_tick": 720, "end_tick": 960, "weight": "weak"},
    ]
    res = audit_voice(notes, scale, strong_grid=(0, 960))
    print("tagged passing tone:", res.summary())
    assert res.passes and res.tagged_resolving == 1 and res.tagged_ornaments == 1

    # a non-resolving ornament: chromatic approach to D(62) -> C#(61), but the
    # target 62 never appears -> tagged but non-resolving -> FAIL
    bad = [
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
        approach_note(62, 240, 480),  # C# -> D(62) but 62 never follows
        {"pitch": 64, "volume": 90, "start_tick": 480, "end_tick": 720, "weight": "strong"},
    ]
    bad_res = audit_voice(bad, scale, strong_grid=(0, 960))
    print("non-resolving ornament:", bad_res.summary())
    assert not bad_res.passes and bad_res.tagged_non_resolving == 1

    # an un-tagged out-of-scale note -> FAIL
    untagged = [
        {"pitch": 60, "volume": 90, "start_tick": 0, "end_tick": 240, "weight": "strong"},
        {"pitch": 61, "volume": 90, "start_tick": 240, "end_tick": 480, "weight": "weak"},  # C# un-tagged
        {"pitch": 62, "volume": 90, "start_tick": 480, "end_tick": 720, "weight": "strong"},
    ]
    ures = audit_voice(untagged, scale, strong_grid=(0, 960))
    print("untagged chromatic:", ures.summary())
    assert not ures.passes and ures.untagged_out_of_scale == 1

    return "pitch_audit demo OK"


if __name__ == "__main__":
    print(demo())
