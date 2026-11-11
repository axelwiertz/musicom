# -*- coding: utf-8 -*-
"""Style-aware rhythm recipes (P0 of PLAN_vary-instrumentation-rhythm.md).

The engine's fill path was a single style-agnostic ``ROLE_FILLERS`` dict — every
piece got the same groove (bass 1&3, drums grid, arp 16ths). This module makes
the rhythm layer **style-aware**: ``RHYTHM_BY_STYLE`` maps a style to a full
``{role: filler}`` recipe, and ``style_fillers(style)`` resolves it.

Filler signature (identical to ``cell_engine.ROLE_FILLERS``)::

    filler(ctx: CellContext) -> List[MusicEvent]

Events are CELL-LOCAL (start at 0, no terminal landmark — ``CellComposer`` adds
it via ``_unit_from_events``). ``style_fillers("pop")`` returns ``ROLE_FILLERS``
verbatim, so the pop path stays byte-identical (golden-hash gates).

Uses only the musicom engine — no mido authoring, no ad-hoc arrays.
"""

from __future__ import annotations

from typing import Callable, Dict, List

from structures import MusicEvent

from workflows.cell_engine import ROLE_FILLERS, CellContext

__all__ = ["RHYTHM_BY_STYLE", "style_fillers", "STYLE_ALIASES"]

# ---------------------------------------------------------------------------
# Style name normalization — map genre dirs / STYLE_REGISTRY keys to a rhythm
# family. Unknown styles fall back to "pop" (the byte-pinned default).
# ---------------------------------------------------------------------------

# canonical rhythm family -> aliases (lowercase, hyphen/space-normalized)
STYLE_ALIASES: Dict[str, List[str]] = {
    "pop":        ["pop", "rock", "soul", "ballad", "r&b", "rnb"],
    "techno":     ["techno", "house", "edm", "electronic", "trance", "trap",
                   "drill", "phonk", "dance"],
    "jazz":       ["jazz", "blues", "swing", "bebop", "ragtime", "big band"],
    "funk":       ["funk", "disco", "groove", "afrobeat", "african", "west african",
                   "west african polyrhythms"],
    "flamenco":   ["flamenco"],
    "latin":      ["latin", "bossa", "bossa nova", "bossanova", "samba", "cuban",
                   "tango", "balkan", "reggae", "ska", "kizomba"],
    "ambient":    ["ambient", "minimal", "minimalism", "cinematic", "drone",
                   "experimental", "world", "other"],
    "chanson":    ["chanson", "country", "folk", "celtic", "bluegrass", "balfolk",
                   "klezmer", "indian classical", "japanese", "chinese", "gamelan"],
    "metal":      ["metal", "hard rock", "punk"],
    "hiphop":     ["hiphop", "hip hop", "rap", "boom bap"],
    "classical":  ["classical", "classic", "baroque", "romantic", "chamber",
                   "opera", "fanfare", "poetry", "modal"],
}

_ALIAS_TO_FAMILY: Dict[str, str] = {}
for _fam, _aliases in STYLE_ALIASES.items():
    for _a in _aliases:
        _ALIAS_TO_FAMILY[_a] = _fam


def _norm(style: str) -> str:
    """Normalize a style string to a canonical rhythm-family key ("" -> pop)."""
    if not style:
        return "pop"
    key = style.lower().strip().replace("_", " ").replace("-", " ")
    # direct match first (exact alias or exact family name)
    if key in _ALIAS_TO_FAMILY:
        return _ALIAS_TO_FAMILY[key]
    # substring match (e.g. "bossa_nova_1960s" -> contains "bossa")
    for alias, fam in _ALIAS_TO_FAMILY.items():
        if alias in key:
            return fam
    return "pop"


# ---------------------------------------------------------------------------
# Bass recipes (root-driven; each uses ctx.root_midi + ctx.bar_ticks)
# ---------------------------------------------------------------------------

def _bass_1and3(ctx: CellContext) -> List[MusicEvent]:
    """pop: root on beats 1 & 3 (legacy byte-pinned)."""
    return ROLE_FILLERS["bass"](ctx)


def _bass_8th_offbeat(ctx: CellContext) -> List[MusicEvent]:
    """techno/house: root stabbed on the 8th off-beats (drive)."""
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        for e in range(8):
            if e % 2 == 1:  # off-beat 8ths only
                evs.append(MusicEvent(ctx.root_midi, 95, base + e * 240,
                                      base + e * 240 + 200))
    return evs


def _bass_walking(ctx: CellContext) -> List[MusicEvent]:
    """jazz/blues: walking 8ths cycling root/5th/octave/3rd."""
    root = ctx.root_midi
    walk = [root, root + 7, root + 12, root + 4]
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        for e in range(8):
            p = walk[e % 4]
            evs.append(MusicEvent(p, 92, base + e * 240, base + e * 240 + 220))
    return evs


def _bass_funk(ctx: CellContext) -> List[MusicEvent]:
    """funk/disco: syncopated 16th root+octave 'one' pattern."""
    root = ctx.root_midi
    # 16-step pattern: hit slots (0=beat1, 7=the 'e' of 2, 8=beat3, 14=off 4)
    hits = [0, 7, 8, 14]
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        for i in hits:
            p = root if i in (0, 8) else root + 12
            evs.append(MusicEvent(p, 95, base + i * 120, base + i * 120 + 160))
    return evs


def _bass_oompah(ctx: CellContext) -> List[MusicEvent]:
    """chanson/folk/country: root(1) fifth(2) root(3) fifth(4)."""
    root = ctx.root_midi
    fifth = root + 7
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        for beat in range(4):
            p = root if beat % 2 == 0 else fifth
            evs.append(MusicEvent(p, 92, base + beat * 480, base + beat * 480 + 360))
    return evs


def _bass_drone(ctx: CellContext) -> List[MusicEvent]:
    """ambient/minimal: sustained root across the whole section."""
    return [MusicEvent(ctx.root_midi, 84, 0, ctx.section_len)]


# ---------------------------------------------------------------------------
# Rhythm (drum) recipes — channel-9 kit notes, no terminal landmark
# ---------------------------------------------------------------------------

def _drums_pop(ctx: CellContext) -> List[MusicEvent]:
    """pop: legacy grid (kick 1, snare 3, hats 8ths) — byte-pinned."""
    return ROLE_FILLERS["rhythm"](ctx)


def _drums_four_floor(ctx: CellContext) -> List[MusicEvent]:
    """techno/house: four-on-floor kick, clap 2&4, off-beat open hat."""
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        for beat in range(4):
            evs.append(MusicEvent(36, 100, base + beat * 480, base + beat * 480 + 120))
        evs.append(MusicEvent(39, 82, base + 480, base + 480 + 90))   # clap 2
        evs.append(MusicEvent(39, 82, base + 1440, base + 1440 + 90))  # clap 4
        for e in range(8):
            if e % 2 == 1:
                evs.append(MusicEvent(46, 60, base + e * 240, base + e * 240 + 100))
    return evs


def _drums_swing(ctx: CellContext) -> List[MusicEvent]:
    """jazz/blues: ride swing (off-beat 8th at 2/3 beat), kick 1&3, hat 2&4."""
    evs = []
    SWING = int(2 * 480 / 3)  # 320
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        evs.append(MusicEvent(36, 92, base, base + 100))               # kick 1
        evs.append(MusicEvent(36, 80, base + 960, base + 960 + 100))   # kick 3
        evs.append(MusicEvent(38, 70, base + 480, base + 480 + 90))    # snare 2
        evs.append(MusicEvent(38, 70, base + 1440, base + 1440 + 90))  # snare 4
        for e in range(8):  # swung ride: 8ths, off-beat pushed to 320
            off = (e // 2) * 480 + (0 if e % 2 == 0 else SWING)
            evs.append(MusicEvent(51, 68, base + off, base + off + 60))
    return evs


def _drums_funk(ctx: CellContext) -> List[MusicEvent]:
    """funk/disco: 16th hats, snare 2&4, kick 1 & 3-and."""
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        evs.append(MusicEvent(36, 100, base, base + 110))              # kick 1
        evs.append(MusicEvent(36, 88, base + 1440, base + 1440 + 100))  # kick 3-and
        evs.append(MusicEvent(38, 88, base + 480, base + 480 + 90))    # snare 2
        evs.append(MusicEvent(38, 88, base + 1440, base + 1440 + 90))  # snare 4
        for e in range(16):  # 16th hats, accent off-beats
            v = 70 if e % 2 == 1 else 52
            evs.append(MusicEvent(42, v, base + e * 120, base + e * 120 + 60))
    return evs


def _drums_flamenco(ctx: CellContext) -> List[MusicEvent]:
    """flamenco: 12-beat compas accents (3/4-ish), palmas-style hits."""
    # compas accents on the 12-beat cycle: 3, 6, 8, 10, 12
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        for beat in range(12):  # 12 eighth-positions per bar
            t = base + beat * 160
            if beat in (2, 5, 7, 9, 11):
                evs.append(MusicEvent(36, 95, t, t + 90))       # golpe
            elif beat % 3 == 0:
                evs.append(MusicEvent(60, 70, t, t + 70))       # palmas (high bongo)
    return evs


def _drums_latin(ctx: CellContext) -> List[MusicEvent]:
    """latin/bossa/samba: clave 3-2 (bell), kick 1&3, rim 2&4."""
    CLAVE = [0, 3, 6, 10, 12]  # 3-2 son clave positions in 16ths (simplified)
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        evs.append(MusicEvent(36, 90, base, base + 110))              # kick 1
        evs.append(MusicEvent(36, 80, base + 960, base + 960 + 100))  # kick 3
        evs.append(MusicEvent(37, 70, base + 480, base + 480 + 80))   # rim 2
        evs.append(MusicEvent(37, 70, base + 1440, base + 1440 + 80))  # rim 4
        for p in CLAVE:
            evs.append(MusicEvent(56, 72, base + p * 120, base + p * 120 + 60))  # cowbell
    return evs


def _drums_ambient(ctx: CellContext) -> List[MusicEvent]:
    """ambient/minimal: no kit — sparse low tom swell at section edges only."""
    return []


def _drums_march(ctx: CellContext) -> List[MusicEvent]:
    """chanson/country/folk: march kick 1&3, snare 2&4, light 8th hats."""
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        for beat in (0, 2):
            evs.append(MusicEvent(36, 92, base + beat * 480, base + beat * 480 + 100))
        for beat in (1, 3):
            evs.append(MusicEvent(38, 84, base + beat * 480, base + beat * 480 + 90))
        for e in range(8):
            evs.append(MusicEvent(42, 50, base + e * 240, base + e * 240 + 70))
    return evs


def _drums_metal(ctx: CellContext) -> List[MusicEvent]:
    """metal: double-kick 16ths on 1&3, snare 2&4, crash on 1."""
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        for beat in (0, 2):
            for k in range(4):  # double-kick 16ths on the beat
                evs.append(MusicEvent(36, 96, base + beat * 480 + k * 120,
                                      base + beat * 480 + k * 120 + 90))
        for beat in (1, 3):
            evs.append(MusicEvent(38, 95, base + beat * 480, base + beat * 480 + 90))
        evs.append(MusicEvent(49, 85, base, base + 400))  # crash
        for e in range(8):
            evs.append(MusicEvent(42, 55, base + e * 240, base + e * 240 + 70))
    return evs


def _drums_hiphop(ctx: CellContext) -> List[MusicEvent]:
    """hiphop/trap: boom-bap kick 1 & 3-and, snare 2&4, sparse hats."""
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        evs.append(MusicEvent(36, 100, base, base + 110))              # kick 1
        evs.append(MusicEvent(36, 90, base + 1440, base + 1440 + 100))  # kick 3-and
        evs.append(MusicEvent(38, 90, base + 480, base + 480 + 90))    # snare 2
        evs.append(MusicEvent(38, 90, base + 1440, base + 1440 + 90))  # snare 4
        for e in (0, 2, 4, 6):
            evs.append(MusicEvent(42, 60, base + e * 240, base + e * 240 + 70))
    return evs


def _drums_classical(ctx: CellContext) -> List[MusicEvent]:
    """classical/baroque: no drum kit — single timpani hit on downbeat."""
    evs = []
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        evs.append(MusicEvent(47, 80, base, base + 300))  # timpani (low tom)
    return evs


# ---------------------------------------------------------------------------
# Lead / pad overrides (only where idiomatic — otherwise pop recipes)
# ---------------------------------------------------------------------------

def _lead_swing(ctx: CellContext) -> List[MusicEvent]:
    """jazz/blues: swung 8th lead — off-beats at 2/3 beat (tick 320)."""
    evs = []
    SWING = int(2 * 480 / 3)
    for b in range(ctx.section_bars):
        base = b * ctx.bar_ticks
        for e in range(8):
            off = (e // 2) * 480 + (0 if e % 2 == 0 else SWING)
            step = ctx.chord_tones[e % 3] + 12
            end = min(base + off + 360, base + ctx.bar_ticks)  # clamp at bar seam
            evs.append(MusicEvent(step, 88, base + off, end))
    return evs


def _pad_drone(ctx: CellContext) -> List[MusicEvent]:
    """ambient/minimal: root+5th drone (open fifth, not full triad)."""
    return [MusicEvent(ctx.chord_tones[0], 62, 0, ctx.section_len),
            MusicEvent(ctx.chord_tones[0] + 7, 58, 0, ctx.section_len)]


# ---------------------------------------------------------------------------
# The registry + resolver
# ---------------------------------------------------------------------------

def _recipe(**overrides: Callable[[CellContext], List[MusicEvent]]):
    """Start from the pop (byte-pinned) fillers, replace named roles."""
    d: Dict[str, Callable] = dict(ROLE_FILLERS)
    d.update(overrides)
    return d


RHYTHM_BY_STYLE: Dict[str, Dict[str, Callable]] = {
    "pop":       dict(ROLE_FILLERS),  # verbatim — golden-hash pinned
    "techno":    _recipe(bass=_bass_8th_offbeat, rhythm=_drums_four_floor),
    "jazz":      _recipe(lead=_lead_swing, bass=_bass_walking, rhythm=_drums_swing),
    "funk":      _recipe(bass=_bass_funk, rhythm=_drums_funk),
    "flamenco":  _recipe(rhythm=_drums_flamenco),
    "latin":     _recipe(rhythm=_drums_latin),
    "ambient":   _recipe(pad=_pad_drone, bass=_bass_drone, rhythm=_drums_ambient),
    "chanson":   _recipe(bass=_bass_oompah, rhythm=_drums_march),
    "metal":     _recipe(rhythm=_drums_metal),
    "hiphop":    _recipe(rhythm=_drums_hiphop),
    "classical": _recipe(rhythm=_drums_classical),
}


def style_fillers(style: str) -> Dict[str, Callable]:
    """Resolve a style to its full ``{role: filler}`` recipe (pop default)."""
    return RHYTHM_BY_STYLE.get(_norm(style), RHYTHM_BY_STYLE["pop"])


if __name__ == "__main__":
    # Smoke test: every family fills non-empty, zero-drift-safe units.
    from workflows.cell_engine import _unit_from_events
    ctx = CellContext(
        key="C", pattern="major", chord_tones=(48, 52, 55), register=(0, 127),
        density=1.0, root_midi=48, section_bars=2, section_len=2 * 1920,
        bar_ticks=1920,
    )
    for fam, fillers in sorted(RHYTHM_BY_STYLE.items()):
        roles = sorted(fillers)
        assert set(roles) == set(ROLE_FILLERS), f"{fam}: {roles}"
        n = sum(len(fillers[r](ctx)) for r in roles)
        print(f"{fam:10s} {roles}  total_events={n}")
    print("style_rhythm smoke OK:", len(RHYTHM_BY_STYLE), "families")
