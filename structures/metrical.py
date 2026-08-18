"""Hierarchical metrical structures (promoted from ``research/rhythm.py``).

Models time as a *tree* of metrical levels (measure → beat → subdivision),
rather than a flat tick stream. This is the standard notation of meter and is
stable regardless of tempo — each level carries its own period in seconds and
an optional phase offset.

Also provides a general onset-quantization routine that snaps an onset time
onto a specified metrical grid.

Usage:
    from structures.metrical import MetricalNode, build_common_tree, \
        QuantizedEvent, quantize_onsets_to_ticks

    measure = build_common_tree(bpm=120, beats=4, beats_per_bar=4)
    events = quantize_onsets_to_ticks([0.0, 0.5, 0.75], 120, 480)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Sequence


@dataclass
class MetricalNode:
    """A single level of a metrical hierarchy.

    Attributes:
        level_name: semantic label, e.g. 'measure', 'beat', 'subdivision'.
        period: duration of one unit at this level, in seconds.
        phase_offset: offset of this level relative to global t=0, in seconds.
        children: nested sub-levels (e.g. a beat's subdivisions).
    """

    level_name: str
    period: float
    phase_offset: float = 0.0
    children: List["MetricalNode"] = field(default_factory=list)

    def total_seconds(self, reps: float = 1.0) -> float:
        """Total duration of ``reps`` units at this level (excluding children)."""
        return self.period * reps

    def tick_phase(self, tick: int, ticks_per_beat: int = 1) -> float:
        """Return the phase (0..1) of ``tick`` within one period at this level."""
        if self.period <= 0:
            return 0.0
        ticks_in_period = self.period * ticks_per_beat  # ticks per unit (1 beat = tpb)
        return (tick % max(1, ticks_in_period)) / max(1, ticks_in_period)


@dataclass
class HierarchicalEvent:
    """An event tagged with the metrical level it belongs to."""

    time: float
    node: MetricalNode
    label: Optional[str] = None


@dataclass
class QuantizedEvent:
    """A time expressed in absolute ticks at a given resolution."""

    tick: int
    ticks_per_beat: int
    duration_ticks: int


def seconds_to_ticks(time_s: float, bpm: float, ticks_per_beat: int) -> int:
    """Convert a time in seconds to absolute ticks at ``bpm``."""
    beats = time_s * (bpm / 60.0)
    return int(round(beats * ticks_per_beat))


def quantize_onsets_to_ticks(
    times: Sequence[float],
    bpm: float,
    ticks_per_beat: int,
    duration_s: float = 0.1,
) -> List[QuantizedEvent]:
    """Snap a list of onset times (seconds) to a tick grid.

    Args:
        times: onset times in seconds.
        bpm: tempo.
        ticks_per_beat: resolution.
        duration_s: default note duration in seconds (converted to ticks).

    Returns:
        A list of ``QuantizedEvent`` sorted by onset tick.
    """
    events = [
        QuantizedEvent(
            tick=seconds_to_ticks(t, bpm, ticks_per_beat),
            ticks_per_beat=ticks_per_beat,
            duration_ticks=max(1, seconds_to_ticks(duration_s, bpm, ticks_per_beat)),
        )
        for t in times
    ]
    return sorted(events, key=lambda e: e.tick)


def build_common_tree(bpm: float, beats: int = 4, beats_per_bar: int = 4,
                      subdivisions: int = 2) -> MetricalNode:
    """Build a measure→beat→subdivision tree for a given tempo.

    Args:
        bpm: beats per minute.
        beats: number of levels to build (measure + beat + subdivisions).
        beats_per_bar: beats in the top-level measure.
        subdivisions: number of subdivision slots per beat (2 = eighth notes).

    Returns:
        Root ``MetricalNode`` (the measure).
    """
    beat_s = 60.0 / bpm
    measure = MetricalNode(level_name="measure", period=beat_s * beats_per_bar,
                           phase_offset=0.0)
    beat = MetricalNode(level_name="beat", period=beat_s, phase_offset=0.0)
    sub = MetricalNode(level_name="subdivision", period=beat_s / subdivisions,
                       phase_offset=0.0)
    beat.children.append(sub)
    for _ in range(beats_per_bar):
        measure.children.append(beat)
    return measure


def assign_metrical_level(times: Sequence[float],
                          tree: MetricalNode,
                          tolerance: float = 1e-6) -> List[HierarchicalEvent]:
    """Classify onsets (seconds) into the metrical hierarchy by period match.

    For each onset, find the *shallowest* metrical level (measure > beat >
    subdivision) whose boundary the onset lands exactly on. This aligns an
    onset with its strongest metrical position: a downbeat lands on the
    measure boundary (shallowest), a beat boundary on the beat, and an
    off-beat eighth only on the subdivision. Falls back to the root if nothing
    matches (unquantized time).

    Args:
        times: onset times in seconds.
        tree: root ``MetricalNode`` of the hierarchy.
        tolerance: floating tolerance for division checks.

    Returns:
        A list of ``HierarchicalEvent``.
    """
    def collect_matching_levels(t: float, node: MetricalNode, depth: int,
                                out: List[tuple]):
        """Collect (depth, node) for every level the onset lands on."""
        if node.period <= 0 or abs(t / node.period - round(t / node.period)) <= tolerance:
            out.append((depth, node))
        for child in node.children:
            collect_matching_levels(t, child, depth + 1, out)

    def shallowest_match(t: float) -> MetricalNode:
        matches: List[tuple] = []
        collect_matching_levels(t, tree, 0, matches)
        if not matches:
            return tree
        matches.sort(key=lambda d: d[0])  # shallowest = smallest depth
        return matches[0][1]

    out: List[HierarchicalEvent] = []
    for t in times:
        matched = shallowest_match(t)
        out.append(HierarchicalEvent(time=t, node=matched, label=matched.level_name))
    return out