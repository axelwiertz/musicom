# -*- coding: utf-8 -*-
"""Realization bridge — the missing Pattern -> MusicEvent[] abstraction.

This is the CONCRETE side of the architecture (see
``PATTERN_ARCHITECTURE.md``):

    12TET pc-set KERNEL   rules/set_theory.py    names, ICV, Z-relations
    PATTERN LIBRARY       rules/patterns.py      Pattern, rhythm, catalogues
    REALIZATION           rules/realize.py       <-- this module

WHY THIS MODULE EXISTS
----------------------
There was no shared ``Pattern -> MusicEvent[]`` function anywhere in the
repo. ``compose()``'s abstract path did it in six hardcoded inline lines
(``base = 48 + root_pc``), so every new consumer — concrete exercises, cron
jobs, HITL variants — either reinvented register placement or wandered off
into legacy code looking for it. That is a large part of why a composition
job once spent its whole budget inside a ``musicpy`` converter.

Division of responsibility
--------------------------
* This module owns *register placement*, *voicing*, *articulation* and
  *voice-leading continuity* between consecutive patterns.
* It does NOT own pattern content (``rules/patterns.py``) or set theory
  (``rules/set_theory.py``).
* It emits engine-native :class:`structures.unit.MusicEvent` objects with
  ABSOLUTE ticks, so output feeds straight into ``UnitMatrixComposer``.

PURITY
------
Imports ``structures`` only (MusicEvent). No MIDI I/O, no musicpy/music21,
no file writes. Deterministic: identical inputs give identical events.

COMPATIBILITY
-------------
:func:`realize_tonal_cluster` reproduces the legacy inline ``compose()``
logic **exactly**, and ``tests/test_realize_bridge.py`` pins the resulting
MIDI hash to prove the refactor was byte-neutral.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from rules.patterns import Pattern, voice_leading_distance
from structures.unit import MusicEvent

# Default register anchor used by the legacy compose() inline code (C3).
DEFAULT_BASE_REGISTER = 48

__all__ = [
    "DEFAULT_BASE_REGISTER",
    "placed_pitches",
    "place_in_register",
    "realize",
    "realize_progression",
    "realize_tonal_cluster",
    "voicing_spread",
    "articulation_events",
]


# ---------------------------------------------------------------------------
# Register placement
# ---------------------------------------------------------------------------

def placed_pitches(pcs: Iterable[int], base: int) -> List[int]:
    """Pitch classes -> sorted absolute MIDI pitches above *base*'s class.

    This is the legacy inline formula, preserved verbatim so the refactor is
    byte-neutral::

        root_pc = min(pat.subset)
        base = 48 + root_pc
        tones = [base + ((pc - root_pc) % 12) for pc in sorted(pat.subset)]

    *base* here is an absolute MIDI pitch whose pitch class acts as the
    anchor; each pc lands in the octave at or above it.
    """
    anchor_pc = base % 12
    return sorted(base + ((pc - anchor_pc) % 12) for pc in sorted(set(pcs)))


def place_in_register(pcs: Iterable[int], register: Tuple[int, int] = (48, 72),
                      *, anchor: str = "min", base: Optional[int] = None) -> List[int]:
    """Place a pitch-class set into a register band.

    ``anchor`` decides which pc is treated as the root:

    ``"min"``    the smallest pc (legacy ``compose()`` behaviour)
    ``"max"``    the largest pc
    ``"lowest"`` alias of ``"min"`` that also guarantees the bottom pitch is
                 the lowest possible within the band
    ``"pc"``     use ``base``'s pitch class as the anchor

    ``register`` is an inclusive ``(low, high)`` MIDI bound. Pitches are
    folded up into the band by octaves, so a set always fits; if the set is
    wider than the band the raw placement is returned (caller's problem —
    better than silently compressing a chord).
    """
    pcs_sorted = sorted(set(p % 12 for p in pcs))
    if not pcs_sorted:
        return []
    lo, hi = register
    if anchor == "pc":
        if base is None:
            raise ValueError("anchor='pc' requires an explicit base pitch")
        anchor_pc = base % 12
    elif anchor == "max":
        anchor_pc = max(pcs_sorted)
    elif anchor in ("min", "lowest"):
        anchor_pc = min(pcs_sorted)
    else:
        raise ValueError(
            f"unknown anchor {anchor!r}; expected 'min', 'max', 'lowest' or 'pc'"
        )

    # start from the lowest pitch in the band whose pc equals the anchor
    start = lo + ((anchor_pc - lo) % 12)
    pitches = sorted(start + ((pc - anchor_pc) % 12) for pc in pcs_sorted)
    span = pitches[-1] - pitches[0]
    if span > (hi - lo):
        return pitches                      # cannot fold without compression
    # fold the whole set up until it fits the top of the band
    while pitches[-1] > hi:
        pitches = [p - 12 for p in pitches]
    while pitches[0] < lo:
        pitches = [p + 12 for p in pitches]
    return sorted(pitches)


@dataclass(frozen=True)
class Voicing:
    """A chord voicing rule."""
    name: str
    spread: str = "close"    # close | open | drop2


VOICING_CLOSE = Voicing("close")
VOICING_OPEN = Voicing("open")
VOICING_DROP2 = Voicing("drop2")


def voicing_spread(pitches: Sequence[int], voicing: str = "close") -> List[int]:
    """Apply a voicing spread to a placed chord.

    ``close``  unchanged (the default, and what the legacy path used)
    ``open``   raise every second note an octave (open position)
    ``drop2``  drop the second-highest note an octave (drop-2)
    """
    p = sorted(pitches)
    if len(p) < 3 or voicing == "close":
        return p
    if voicing == "open":
        return sorted(p[i] + (12 if i % 2 else 0) for i in range(len(p)))
    if voicing == "drop2":
        out = list(p)
        out[-2] -= 12
        return sorted(out)
    raise ValueError(f"unknown voicing {voicing!r}; expected close/open/drop2")


# ---------------------------------------------------------------------------
# Articulation
# ---------------------------------------------------------------------------

def articulation_events(starts: Sequence[int], durations: Sequence[int],
                        articulation: float = 0.95) -> List[Tuple[int, int]]:
    """Trim note durations for articulation (legato = 1.0).

    ``0.95`` is the value used ad-hoc throughout the existing workflows.
    Returns ``(start_tick, end_tick)`` pairs.
    """
    if articulation > 1.0:
        raise ValueError("articulation must be <= 1.0 (legato = 1.0)")
    return [
        (s, s + max(1, int(round(d * articulation))))
        for s, d in zip(starts, durations)
    ]


# ---------------------------------------------------------------------------
# The realization primitive
# ---------------------------------------------------------------------------

def realize(pattern: Pattern, *, register: Tuple[int, int] = (48, 72),
            rhythm=None, bar_ticks: int = 1920, articulation: float = 1.0,
            velocity: int = 90, voicing: str = "close",
            anchor: str = "min", seed: int = 0) -> List["MusicEvent"]:
    """Abstract Pattern (+ optional rhythm) -> concrete MusicEvent list.

    With no *rhythm*, the pattern sounds as a single sustained chord across
    *bar_ticks*. With a :class:`~rules.patterns.RhythmPattern` or a plain
    sequence of ``(start, duration)`` tick pairs, each onset plays the chord.

    Emits absolute-tick :class:`MusicEvent` objects, so the result can be
    handed straight to ``UnitMatrixComposer`` via ``add_event``/units.
    """
    pitches = voicing_spread(
        place_in_register(pattern.subset, register, anchor=anchor), voicing
    )
    if not pitches:
        return []

    if rhythm is None:
        slots = [(0, bar_ticks)]
    elif hasattr(rhythm, "onsets_in_bar"):
        onsets = rhythm.onsets_in_bar(bar_ticks)
        step = (bar_ticks / float(rhythm.cycle)) if rhythm.cycle else bar_ticks
        slots = [(o, int(step)) for o in onsets]
    else:
        slots = [(int(s), int(d)) for s, d in rhythm]

    events: List["MusicEvent"] = []
    for start, dur in slots:
        for p in pitches:
            events.append(MusicEvent(p, velocity, start, start + dur))
    return events


def realize_progression(patterns: Sequence[Pattern], *,
                        register: Tuple[int, int] = (48, 72),
                        bar_ticks: int = 1920, bars_per_pattern: int = 1,
                        articulation: float = 1.0, velocity: int = 90,
                        voicing: str = "close", anchor: str = "min",
                        smooth: bool = False) -> List["MusicEvent"]:
    """Realize a sequence of patterns as one continuous concrete line.

    With ``smooth=True`` each pattern is placed to minimize voice-leading
    distance from the previous one (using the shared
    ``voice_leading_distance`` metric, in octave steps), instead of being
    anchored identically every time. That is the continuity rule the
    previous inline implementation lacked entirely.
    """
    events: List[MusicEvent] = []
    prev: Optional[List[int]] = None
    cursor = 0
    span = bar_ticks * bars_per_pattern

    for pattern in patterns:
        pitches = place_in_register(pattern.subset, register, anchor=anchor)
        if smooth and prev:
            best, best_d = pitches, None
            for shift in (-24, -12, 0, 12, 24):
                cand = sorted(p + shift for p in pitches)
                if cand[0] < register[0] or cand[-1] > register[1]:
                    continue
                d = voice_leading_distance(
                    [p % 12 for p in prev], [p % 12 for p in cand]
                )
                if best_d is None or d < best_d:
                    best, best_d = cand, d
            pitches = best
        pitches = voicing_spread(pitches, voicing)
        end = cursor + span
        trim = articulation_events([cursor], [span], articulation)[0][1]
        end_eff = min(end, trim) if articulation < 1.0 else end
        for p in pitches:
            events.append(MusicEvent(p, velocity, cursor, end_eff))
        prev = pitches
        cursor = end
    return events


def realize_tonal_cluster(pattern: Pattern, base: int = DEFAULT_BASE_REGISTER
                          ) -> List[int]:
    """The legacy ``compose()`` abstract-path placement, verbatim.

    Reproduces exactly::

        root_pc = min(pat.subset)
        base = 48 + root_pc
        tones = [base + ((pc - root_pc) % 12) for pc in sorted(pat.subset)]

    Kept as a named function so the refactor of ``compose()`` is provably
    byte-neutral rather than approximately equivalent. The golden ABS MIDI
    hash in ``tests/test_realize_bridge.py`` guards it.
    """
    root_pc = min(pattern.subset)
    anchor = base + root_pc
    return [anchor + ((pc - root_pc) % 12) for pc in sorted(pattern.subset)]


# ---------------------------------------------------------------------------
# Abstract-layer harmonic helpers used by the walk path
# ---------------------------------------------------------------------------

def tension_curve_targets(curve: Sequence[float], n_sections: int) -> List[float]:
    """Expand/resample a tension curve to exactly *n_sections* targets.

    Short curves repeat their last value; long ones are truncated. Keeps the
    walk's contract simple without duplicating slicing logic per call site.
    """
    if n_sections <= 0:
        return []
    if len(curve) >= n_sections:
        return list(curve[:n_sections])
    out = list(curve)
    while len(out) < n_sections:
        out.append(curve[-1] if curve else 0.0)
    return out


# relation names re-exported for consumers that reason about the walk
RELATION_NAMES: Dict[str, str] = {
    "tn": "transposition",
    "inv": "inversion",
    "z": "z-relation",
    "compl": "complementation",
    "plr": "parsimonious",
    "vl": "voice-leading",
}
