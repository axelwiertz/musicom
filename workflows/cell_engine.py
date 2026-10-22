# -*- coding: utf-8 -*-
"""Role-first cell engine — the concrete-layer fill mechanism (Phase 3 P0).

VOICE_ROLE_WORKFLOW_PLAN.md (§2, §7-P0): replace the hardcoded per-voice fill
in ``musicom_workflow.compose()`` with a spec-driven loop. Every ``(voice,
section)`` cell flows through the same stages with cell-local parameters, and
the method resolves the voice's ROLE first, then the cell is filled under that
role.

P0 scope (this module):
  - ``CellContext`` — the read-only input bag every stage shares.
  - ``default_resolve_role`` — position-based role resolver (reproduces the
    legacy hardcoded fill's voice-index mapping exactly: 0=lead, 1=pad,
    2=bass, 3=arp, 4=rhythm).
  - ``ROLE_FILLERS`` — the five default fillers, byte-identical to the legacy
    hardcoded ``compose()`` fill (lead 8th arp / pad sustained / bass 1&3 /
    arp 16ths / drums grid). This is what makes the P0 rewire OUTPUT-NEUTRAL:
    the same events, just routed through the engine instead of inline.

P1/P2 (NOT in this module yet) will add: tiered snap + tagged chromatic
ornaments (``scale_quantizer.tiered_quantize`` + ``rules.ornament``), variation
transforms (``workflows.variation``), and the ``counter`` role. The method
contract (``resolve_role(context) -> str`` + ``generate(context, role)``) is
the target shape; ``default_resolve_role`` is the P0 stand-in.

Uses only the musicom engine (``structures.MusicUnit``/``MusicEvent``) — no raw
mido authoring, no ad-hoc numpy arrays (AGENTS.md hard rule).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

from structures import MusicEvent, MusicUnit

__all__ = [
    "CellContext",
    "CellComposer",
    "ROLE_FILLERS",
    "ROLE_BY_POSITION",
    "default_resolve_role",
    "fillers_table",
]


# ---------------------------------------------------------------------------
# CellContext — the single read-only input bag every stage shares
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CellContext:
    """Read-only per-(voice, section) context passed to every stage.

    Conceptual fields (plan §2) plus the mechanical fields the default P0
    fillers need to reproduce the legacy hardcoded fill exactly.
    """
    key: str                   # "C", "Eb", ...
    pattern: str               # scale/mode name: "major", "aeolian", ...
    chord_tones: tuple         # current chord's absolute tones (sorted)
    register: tuple            # (lo, hi) MIDI range for this voice
    density: float             # target events per bar (0.2 sparse .. 1.0 dense)
    # --- mechanical (P0 default fillers) ---
    root_midi: int = 48        # bass root for the section
    section_bars: int = 4      # bars in this section
    section_len: int = 0       # section length in ticks (= section_bars * BAR)
    bar_ticks: int = 1920      # ticks per bar (BAR)
    voice_idx: int = -1        # this voice's matrix row (for method role resolution)
    instrument_name: str = ""  # this voice's instrument name (for drum guard)
    # --- P1/P2 (reserved; default fillers ignore these) ---
    density_budget: float = 1.0
    strong_beat_grid: tuple = (0, 960)
    seed: int = 0
    other_roles: frozenset = field(default_factory=frozenset)
    counter_mode: str = "independent"


# ---------------------------------------------------------------------------
# Default role resolution — position-based, reproduces the legacy fill mapping
# ---------------------------------------------------------------------------

ROLE_BY_POSITION = ("lead", "pad", "bass", "arp", "rhythm")
_DRUM_NAMES = ("drum kit", "drums", "percussion")


def default_resolve_role(voice_idx: int, instrument_name: str,
                         ctx: Optional[CellContext] = None) -> Optional[str]:
    """Resolve a voice's role by its matrix position (the legacy default).

    voice 0=lead, 1=pad, 2=bass, 3=arp, 4=rhythm. The rhythm slot only fills
    when the instrument is a drum kit (matches ``compose()``'s old
    ``voices[4][1].lower() in ("drum kit", ...)`` guard). ``ctx`` is accepted
    for forward-compatibility with the method-driven resolver (P2) and ignored
    here.
    """
    if voice_idx < 0 or voice_idx >= len(ROLE_BY_POSITION):
        return None
    role = ROLE_BY_POSITION[voice_idx]
    if role == "rhythm" and (instrument_name or "").lower() not in _DRUM_NAMES:
        return None
    return role


# ---------------------------------------------------------------------------
# Default fillers — byte-identical to the legacy hardcoded compose() fill
# ---------------------------------------------------------------------------

def _fill_lead(ctx: CellContext) -> List[MusicEvent]:
    """Lead: 8th-note arpeggio of chord tones, octave up (legacy)."""
    evs = []
    for b in range(ctx.section_bars * 2):
        step = ctx.chord_tones[b % 3] + 12  # octave up for lead
        evs.append(MusicEvent(step, 90, b * 960, b * 960 + 480))
    return evs


def _fill_pad(ctx: CellContext) -> List[MusicEvent]:
    """Pad: sustained chord (whole-section), first three chord tones (legacy)."""
    return [MusicEvent(ctx.chord_tones[i], 60, 0, ctx.section_len) for i in range(3)]


def _fill_bass(ctx: CellContext) -> List[MusicEvent]:
    """Bass: root on beats 1 & 3 (legacy)."""
    return [MusicEvent(ctx.root_midi, 95, b * ctx.bar_ticks, b * ctx.bar_ticks + 900)
            for b in range(ctx.section_bars)]


def _fill_arp(ctx: CellContext) -> List[MusicEvent]:
    """Arp: 16th-note arpeggio of chord tones, octave up (legacy)."""
    evs = []
    for b in range(ctx.section_bars * 4):
        note = ctx.chord_tones[b % 3] + 12
        evs.append(MusicEvent(note, 70, b * 480, b * 480 + 240))
    return evs


def _fill_rhythm(ctx: CellContext) -> List[MusicEvent]:
    """Rhythm/drums: kick 1&3, snare 2&4, hats 8ths (legacy)."""
    evs = []
    for b in range(ctx.section_bars):
        bar_start = b * ctx.bar_ticks
        evs.append(MusicEvent(36, 100, bar_start, bar_start + 120))        # kick 1
        evs.append(MusicEvent(38, 90, bar_start + 960, bar_start + 1080))  # snare 3
        for h in range(8):
            evs.append(MusicEvent(42, 60, bar_start + h * 240,
                                  bar_start + h * 240 + 120))              # hats
    return evs


ROLE_FILLERS: Dict[str, Callable[[CellContext], List[MusicEvent]]] = {
    "lead": _fill_lead,
    "pad": _fill_pad,
    "bass": _fill_bass,
    "arp": _fill_arp,
    "rhythm": _fill_rhythm,
}


# ---------------------------------------------------------------------------
# CellComposer — fills a matrix cell under a resolved role
# ---------------------------------------------------------------------------

def _unit_from_events(events: Sequence[MusicEvent],
                      section_len: Optional[int] = None) -> MusicUnit:
    """Wrap events in a MusicUnit with a terminal silent landmark (zero-drift).

    Identical to ``musicom_workflow._unit_from_events`` — the terminal
    ``MusicEvent(0, 0, section_len, section_len)`` guarantees every voice's
    section unit ends at the exact cell length.
    """
    unit = MusicUnit()
    for ev in events:
        unit.add_event(ev)
    if section_len is None:
        section_len = max((ev.end_tick for ev in events), default=0)
    unit.add_event(MusicEvent(0, 0, section_len, section_len))
    return unit


class CellComposer:
    """Fill matrix cells through the role registry (thin orchestrator).

    Wraps a ``UnitMatrixComposer``; ``fill_cell`` looks up the role's filler,
    generates events under ``ctx``, wraps them zero-drift-safe, and fills the
    named cell.
    """

    def __init__(self, composer):
        self.composer = composer

    def fill_cell(self, voice_name: str, section_name: str,
                  ctx: CellContext, role: str) -> None:
        """Generate + fill one (voice, section) cell under ``role``."""
        if role not in ROLE_FILLERS:
            raise KeyError(f"unknown role {role!r}; available: {sorted(ROLE_FILLERS)}")
        events = ROLE_FILLERS[role](ctx)
        self.composer.fill_voice_section(
            voice_name, section_name, _unit_from_events(events, ctx.section_len))


def fillers_table() -> str:
    """Markdown table of role -> filler (for docs/)."""
    rows = ["| Role | Filler |", "|---|---|"]
    for role in ROLE_BY_POSITION:
        fn = ROLE_FILLERS[role]
        rows.append(f"| {role} | `{fn.__name__}` |")
    return "\n".join(rows)


if __name__ == "__main__":
    # Smoke test: one context, every role fills non-empty zero-drift units.
    ctx = CellContext(
        key="C", pattern="major", chord_tones=(48, 52, 55), register=(0, 127),
        density=1.0, root_midi=48, section_bars=4, section_len=4 * 1920,
        bar_ticks=1920,
    )
    print(fillers_table())
    print()
    for role in ROLE_BY_POSITION:
        evs = ROLE_FILLERS[role](ctx)
        unit = _unit_from_events(evs, ctx.section_len)
        print(f"{role}: {len(evs)} events, unit ends at {max(e.end_tick for e in unit.events)}")
    print("cell_engine smoke OK")
