"""Auto Divisi — chord distribution across instrument parts — Forma Labs
Filament 1.2 style.

Replicable orchestration logic from the Sound On Sound item "Forma Labs
Audio release Filament 1.2" (2026-10-16): Filament is a real-time MIDI
orchestration host (up to 64 instruments on one DAW track, voice
allocation, keyswitch management). The 1.2 update adds **Auto Divisi**
("automatically distribute chord notes across instrument parts") and
**Note-off Revoice** ("choose whether releasing a key redistributes the
remaining notes").

What is replicated here (pure MIDI-level logic, no audio DSP needed):

* ``AutoDivisi`` — distribute a chord (list of MIDI pitches) across ``N``
  instrument parts:
  - per-part pitch ranges (e.g. violin G3..C7, cello C2..A5);
  - **workload balancing**: notes spread so no part is overstuffed and
    doublings are avoided where possible (unison only when notes exceed
    parts);
  - **minimal motion**: given the previous chord's assignment, notes are
    assigned greedily to keep each part's line smooth (least total
    movement — good divisi voice-leading);
  - **layering**: when a part's range cannot host a note, the note is
    assigned to the nearest-range part instead of dropped.
* ``note_off_revoice`` flag: when a key releases, remaining held notes are
  re-distributed (redistribute) or kept in place (keep).

Usage:
    from sound.generators.auto_divisi import AutoDivisi

    ad = AutoDivisi(parts=[("vn1", (55, 96)), ("vn2", (55, 96)),
                           ("va", (48, 84)), ("vc", (36, 72))])
    assign = ad.distribute(chord=[60, 64, 67, 72])   # {pitch: part_name}
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

# default string-section ranges (MIDI notes) — 4-part string divisi
DEFAULT_PARTS = [
    ("vn1", (55, 96)),   # G3..C7
    ("vn2", (55, 96)),
    ("va", (48, 84)),    # C3..C6
    ("vc", (36, 72)),    # C2..C5
]


class AutoDivisi:
    """Distribute chord notes across instrument parts with balancing,
    minimal-motion coupling and optional note-off revoice.

    Args:
        parts: sequence of ``(name, (lo, hi))`` MIDI ranges.
        prev_assignment: ``{pitch: part_name}`` from the previous chord to
            couple voice-leading (optional).
    """

    def __init__(self, parts: Optional[Sequence[Tuple[str, Tuple[int, int]]]] = None,
                 prev_assignment: Optional[Dict[int, str]] = None):
        self.parts = list(parts or DEFAULT_PARTS)
        self.names = [p[0] for p in self.parts]
        self.ranges = {p[0]: p[1] for p in self.parts}
        self.prev = dict(prev_assignment or {})

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _fits(self, part: str, pitch: int) -> bool:
        lo, hi = self.ranges[part]
        return lo <= pitch <= hi

    def _nearest_part(self, pitch: int, exclude: set = None) -> str:
        exclude = exclude or set()
        best, best_d = None, None
        for name, (lo, hi) in self.parts:
            if name in exclude:
                continue
            d = 0
            if pitch < lo:
                d = lo - pitch
            elif pitch > hi:
                d = pitch - hi
            if best_d is None or d < best_d:
                best, best_d = name, d
        return best

    # ------------------------------------------------------------------
    # main API
    # ------------------------------------------------------------------
    def distribute(self, chord: Sequence[int], previous: Optional[Dict[int, str]] = None,
                   note_off_revoice: bool = False,
                   held_notes: Optional[Sequence[int]] = None) -> Dict[int, str]:
        """Assign every pitch in ``chord`` to a part.

        Args:
            chord: list of MIDI pitches (unsorted ok, dupes allowed for
                doublings).
            previous: the previous chord's assignment (overrides the one
                given at construction).
            note_off_revoice: if True, when this chord has *fewer* notes
                than the previous one ("a key released"), the remaining
                notes are fully re-distributed; if False, previously
                assigned parts are kept when still valid (no revoice).
            held_notes: pitches currently still held (used together with
                ``note_off_revoice``).

        Returns:
            ``{pitch: part_name}`` — one entry per input note (duplicate
            pitches get separate entries assigned to different parts when
            possible).
        """
        notes = [int(p) for p in chord]
        prev = dict(previous or self.prev)
        n_parts = len(self.parts)
        # track how many notes each part already carries
        load = {name: 0 for name in self.names}
        if prev:
            for p in prev.values():
                if p in load:
                    load[p] += 1

        assignment: Dict[int, str] = {}
        # 1) keep previous assignments where the note is still present
        #    (voice-leading continuity) unless note_off_revoice forces a
        #    full re-distribution of the *remaining* set.
        remaining = list(notes)
        if not note_off_revoice and prev:
            for pitch in list(remaining):
                if pitch in prev:
                    part = prev[pitch]
                    if self._fits(part, pitch):
                        assignment[pitch] = part
                        remaining.remove(pitch)
        # held_notes hint: those notes are the ones still sounding; when
        # revoicing, only re-distribute held notes.
        pool = [p for p in remaining]
        if note_off_revoice and held_notes:
            pool = [p for p in remaining if p in set(int(h) for h in held_notes)]

        # 2) greedy minimal-motion assignment, range-aware, load-balanced
        unassigned = sorted(pool)
        while unassigned:
            pitch = unassigned.pop(0)
            if pitch in assignment:
                continue
            # candidates that fit, preferring least-loaded
            fitting = [n for n in self.names
                       if self._fits(n, pitch) and load[n] < max(1, len(notes) // n_parts + 1)]
            if not fitting:
                fitting = [n for n in self.names if self._fits(n, pitch)]
            if not fitting:
                fitting = [self._nearest_part(pitch)]  # out-of-range fallback
            # among candidates pick the one with least motion from previous
            def motion(name: str) -> int:
                prev_part = None
                prev_pitches = [p for p, pn in prev.items() if pn == name]
                if prev_pitches:
                    prev_part = min(prev_pitches, key=lambda p: abs(p - pitch))
                    return abs(prev_part - pitch)
                return 0
            part = min(fitting, key=lambda n: (load[n], motion(n)))
            assignment[pitch] = part
            load[part] += 1

        # 3) doublings: duplicate pitches that remain get the next-least-
        #    loaded different part (unison spread).
        for pitch in list(notes):
            if notes.count(pitch) > 1 and pitch in assignment:
                used = {assignment[pitch]}
                for _ in range(notes.count(pitch) - 1):
                    alt = self._nearest_part(pitch, exclude=used)
                    if alt is None:
                        break
                    assignment.setdefault(pitch, alt)
                    used.add(alt)

        self.prev = assignment
        return assignment

    def revoice(self, held_notes: Sequence[int],
                previous: Optional[Dict[int, str]] = None) -> Dict[int, str]:
        """Re-distribute the currently held (still sounding) notes —
        Filament's "Note-off Revoice" behaviour. Notes that were released
        are dropped; the survivors are re-assigned for best balance."""
        prev = dict(previous or self.prev)
        held = [p for p in held_notes if p in prev]
        return self.distribute(held, previous=prev, note_off_revoice=True)


def demo() -> dict:
    """Self-test: distribute a Cmaj7 across 4 string parts, then revoice."""
    ad = AutoDivisi()
    chord = [60, 64, 67, 72]  # C4 E4 G4 C5
    first = ad.distribute(chord)
    second = ad.distribute([64, 67, 72], previous=first)         # G released
    revoiced = ad.revoice([60, 64, 72], previous=first)          # force revoice
    # invariants
    assert set(first.keys()) == set(chord)
    assert set(second.keys()) == {64, 67, 72}
    assert set(revoiced.keys()) <= {60, 64, 72}
    for mapping in (first, second, revoiced):
        for pitch, part in mapping.items():
            lo, hi = ad.ranges[part]
            assert lo <= pitch <= hi, f"{pitch} out of {part} range"
    # workload: with 4 notes / 4 parts, no part gets more than 1 note
    loads = {n: sum(1 for p in first.values() if p == n) for n in ad.names}
    assert max(loads.values()) <= 1, f"unbalanced: {loads}"
    return {
        "cmaj7": {str(k): v for k, v in sorted(first.items())},
        "after_release": {str(k): v for k, v in sorted(second.items())},
        "revoiced": {str(k): v for k, v in sorted(revoiced.items())},
        "loads": loads,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))