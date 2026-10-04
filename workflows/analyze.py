# -*- coding: utf-8 -*-
"""workflows/analyze.py — reverse analysis / decomposition entry point.

Symmetric counterpart to ``compose()``/``produce()``. Reads a MIDI file
headlessly and reports what the engine would need to reconstruct it:

    key estimate (Krumhansl-Schmuckler profile correlation)
    roman-numeral chord progression per bar (rules/harmony.py)
    Forte set-class names per chord (rules/set_theory.py)
    high-contrast grid render (visualization/grid.py)
    voice-leading violations (rules/voice_leading.py)
    per-voice density %

Purity: mido is used for READING only (never authoring); music21 is loaded
only behind the opt-in ``to_score=True`` flag; this module never plots.

    from workflows.analyze import analyze_midi
    report = analyze_midi("out.mid")
    print(report.summary())
    print(report.roman_progression)   # ["I", "V", "vi", "IV", ...]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from rules.harmony import MAJOR_DEGREES
from rules.set_theory import forte_name
from rules.voice_leading import VoiceLeadingRules
from visualization.grid import render_grid
from structures.matrix import UnitMatrix
from structures.unit import MusicUnit, MusicEvent

_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Krumhansl-Kessler (1982) probe-tone profiles, indexed by pitch class 0..11
# relative to the tonic (0 = tonic).
_KK_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_KK_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

# Natural-minor scale degrees with conventional case (aeolian spelling).
_MINOR_DEGREES = ["i", "ii", "III", "iv", "v", "VI", "VII"]
_MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]


@dataclass
class AnalysisReport:
    """Headless analysis result for a MIDI file."""

    path: str
    key: str
    mode: str
    bpm: float
    tpb: int
    total_notes: int
    duration_seconds: float
    sections: List[dict] = field(default_factory=list)
    roman_progression: List[str] = field(default_factory=list)
    forte_names: List[str] = field(default_factory=list)
    grid: str = ""
    violations: List[str] = field(default_factory=list)
    density: Dict[str, float] = field(default_factory=dict)
    score: object = None  # music21 stream, only when to_score=True

    def summary(self) -> str:
        lines = [
            f"Musicom analysis — {self.path}",
            f"Key: {self.key} {self.mode}  |  BPM: {self.bpm:.1f}  |  "
            f"notes: {self.total_notes}  |  duration: {self.duration_seconds:.1f}s",
            f"Roman progression: {' - '.join(self.roman_progression) or '(none)'}",
            f"Forte set-classes: {', '.join(self.forte_names) or '(none)'}",
        ]
        if self.density:
            dens = ", ".join(f"{k}: {v:.0f}%" for k, v in sorted(self.density.items()))
            lines.append(f"Density (per track): {dens}")
        if self.violations:
            lines.append(f"Voice-leading violations: {len(self.violations)}")
            lines.extend(f"  - {v}" for v in self.violations[:10])
        lines.append("")
        lines.append(self.grid)
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.summary()


# ---------------------------------------------------------------------------
# MIDI reading (mido, READ-only)
# ---------------------------------------------------------------------------

def _read_midi(path: str) -> dict:
    """Parse a MIDI file into absolute-tick note dicts + tempo + track names."""
    import mido

    mid = mido.MidiFile(str(path))
    tpb = mid.ticks_per_beat
    bpm = 120.0
    for msg in mid.tracks[0]:
        if msg.type == "set_tempo":
            bpm = float(mido.tempo2bpm(msg.tempo))
            break

    notes: List[dict] = []
    track_names: List[str] = []
    for ti, track in enumerate(mid.tracks):
        name = f"Voice{ti:02d}"
        program = channel = 0
        for msg in track:
            if msg.type == "track_name":
                name = msg.name
            if msg.type == "program_change":
                program, channel = msg.program, msg.channel
        track_names.append(name)
        abstick = 0
        active: Dict[int, tuple] = {}
        for msg in track:
            abstick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = (abstick, msg.velocity)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active:
                    start, vel = active.pop(msg.note)
                    notes.append({
                        "pitch": msg.note, "velocity": vel,
                        "start": start, "end": abstick,
                        "track": ti, "program": program, "channel": channel,
                    })
    notes.sort(key=lambda n: (n["start"], n["track"]))
    return {"notes": notes, "tpb": tpb, "bpm": bpm, "track_names": track_names}


# ---------------------------------------------------------------------------
# Key estimation
# ---------------------------------------------------------------------------

def _estimate_key(notes: List[dict]) -> tuple:
    """Krumhansl-Schmuckler key profile correlation -> (name, mode, tonic_pc)."""
    hist = np.zeros(12)
    for n in notes:
        hist[n["pitch"] % 12] += max(0, n["end"] - n["start"])
    if hist.sum() == 0:
        return "C", "major", 0
    best = None
    for tonic in range(12):
        for mode, profile in (("major", _KK_MAJOR), ("minor", _KK_MINOR)):
            rotated = np.array([profile[(i - tonic) % 12] for i in range(12)])
            corr = float(np.corrcoef(hist, rotated)[0, 1])
            if best is None or corr > best[0]:
                best = (corr, tonic, mode)
    _, tonic, mode = best
    return _NOTE_NAMES[tonic], mode, tonic


def _resolve_key(key: Optional[str]) -> Optional[tuple]:
    """Parse an explicit key string into (tonic_pc, mode), or None."""
    if not key:
        return None
    k = key.strip()
    if k.endswith("m") and k[:-1] in _NOTE_NAMES:
        return _NOTE_NAMES.index(k[:-1]), "minor"
    if k in _NOTE_NAMES:
        return _NOTE_NAMES.index(k), "major"
    return None


# ---------------------------------------------------------------------------
# Chord / roman detection
# ---------------------------------------------------------------------------

def _detect_chord(pc_weights: Dict[int, float]) -> tuple:
    """Best (root_pc, quality) explaining the weighted pitch-class content."""
    best = None
    for root in range(12):
        for qual, ivs in (("maj", (0, 4, 7)), ("min", (0, 3, 7))):
            score = sum(pc_weights.get((root + i) % 12, 0.0) for i in ivs)
            if best is None or score > best[0]:
                best = (score, root, qual)
    return best[1], best[2]


def _roman(root_pc: int, qual: str, tonic_pc: int, mode: str) -> str:
    """Roman numeral for a (root_pc, quality) chord in the given key/mode."""
    offset = (root_pc - tonic_pc) % 12
    scale = _MAJOR_SCALE if mode == "major" else _MINOR_SCALE
    degrees = MAJOR_DEGREES if mode == "major" else _MINOR_DEGREES
    # nearest scale degree (diatonic music hits an exact match)
    idx = min(range(7), key=lambda i: min(
        (offset - scale[i]) % 12, (scale[i] - offset) % 12))
    delta = (offset - scale[idx]) % 12
    if delta > 6:
        delta -= 12
    roman = degrees[idx]
    if delta == 0:
        return roman
    prefix = "#" * delta if delta > 0 else "b" * (-delta)
    return prefix + roman


# ---------------------------------------------------------------------------
# Grid + density
# ---------------------------------------------------------------------------

def _build_grid(notes: List[dict], data: dict, ticks_per_bar: int) -> str:
    """High-contrast grid via visualization/grid.py (one row per note track)."""
    note_tracks = sorted({n["track"] for n in notes})
    if not note_tracks:
        return ""
    max_end = max((n["end"] for n in notes), default=0)
    num_bars = max(1, int(np.ceil(max_end / ticks_per_bar)))
    rows = len(note_tracks)
    matrix = UnitMatrix(shape=(rows, num_bars))
    for r in range(rows):
        for c in range(num_bars):
            matrix.set_unit((r, c), MusicUnit())
    track_idx = {t: i for i, t in enumerate(note_tracks)}
    for n in notes:
        r = track_idx[n["track"]]
        b = int(n["start"] // ticks_per_bar)
        if b >= num_bars:
            continue
        rel_start = int(n["start"] - b * ticks_per_bar)
        rel_end = int(min(n["end"] - b * ticks_per_bar, ticks_per_bar))
        if rel_end <= rel_start:
            rel_end = rel_start + 1
        matrix.get_unit((r, b)).add_event(
            MusicEvent(n["pitch"], n["velocity"], rel_start, rel_end))
    names = [data["track_names"][t] if t < len(data["track_names"]) else f"Voice{t}"
             for t in note_tracks]
    return render_grid(matrix, voice_names=names)


def _density(notes: List[dict], data: dict) -> Dict[str, float]:
    """Per-track sounding-coverage %, keyed by track name."""
    max_end = max((n["end"] for n in notes), default=0)
    if max_end == 0:
        return {}
    out: Dict[str, float] = {}
    for t in sorted({n["track"] for n in notes}):
        ivs = sorted((n["start"], n["end"]) for n in notes if n["track"] == t)
        merged: List[list] = []
        for s, e in ivs:
            if merged and s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        sounding = sum(e - s for s, e in merged)
        name = data["track_names"][t] if t < len(data["track_names"]) else f"Voice{t}"
        out[name] = round(100.0 * sounding / max_end, 1)
    return out


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze_midi(path: str, key: Optional[str] = None,
                 to_score: bool = False) -> AnalysisReport:
    """Analyze a MIDI file headlessly. Returns an ``AnalysisReport``.

    Args:
        path: MIDI file to analyze.
        key: optional explicit key (e.g. "C", "Dm"); overrides the estimator.
        to_score: if True, also attach a music21 ``.score`` stream (opt-in;
            imports music21 lazily — the default path stays music21-free).
    """
    data = _read_midi(path)
    notes = data["notes"]
    tpb = data["tpb"]
    bpm = data["bpm"]
    ticks_per_bar = tpb * 4  # 4/4 default; time-sig meta not yet parsed

    # Percussion (GM channel 9) carries kick/snare/hat pitch classes that
    # pollute key/chord/forte analysis — exclude it from harmonic work but
    # keep it for the grid, density and note count.
    harmonic = [n for n in notes if n["channel"] != 9]

    est_key, est_mode, tonic = _estimate_key(harmonic)
    resolved = _resolve_key(key)
    if resolved is not None:
        tonic, est_mode = resolved
        est_key = key

    max_end = max((n["end"] for n in notes), default=0)
    num_bars = max(1, int(np.ceil(max_end / ticks_per_bar)) if max_end else 1)
    bar_pcs: List[Dict[int, float]] = [{} for _ in range(num_bars)]
    for n in harmonic:
        dur = max(0, n["end"] - n["start"])
        if dur <= 0:
            continue
        b = int(n["start"] // ticks_per_bar)
        if 0 <= b < num_bars:
            pc = n["pitch"] % 12
            bar_pcs[b][pc] = bar_pcs[b].get(pc, 0.0) + dur

    sections: List[dict] = []
    romans: List[str] = []
    for b in range(num_bars):
        weights = bar_pcs[b]
        if not weights:
            continue
        root, qual = _detect_chord(weights)
        roman = _roman(root, qual, tonic, est_mode)
        third = 3 if qual == "min" else 4
        triad = sorted({root % 12, (root + third) % 12, (root + 7) % 12})
        sections.append({
            "bar": b,
            "root": _NOTE_NAMES[root % 12],
            "quality": qual,
            "roman": roman,
            "forte": forte_name(triad),
            "pcs": sorted(weights.keys()),
        })
        romans.append(roman)

    # voice-leading violations across the detected chord sequence
    vl = VoiceLeadingRules("classical")
    violations: List[str] = []
    triads: List[List[int]] = []
    for s in sections:
        r = _NOTE_NAMES.index(s["root"])
        third = 3 if s["quality"] == "min" else 4
        triads.append(sorted([r, r + third, r + 7]))
    for i in range(1, len(triads)):
        violations += vl.check_parallel_motion(triads[i - 1], triads[i])

    report = AnalysisReport(
        path=str(path),
        key=est_key,
        mode=est_mode,
        bpm=bpm,
        tpb=tpb,
        total_notes=len(notes),
        duration_seconds=(max_end / tpb) * (60.0 / bpm) if tpb else 0.0,
        sections=sections,
        roman_progression=romans,
        forte_names=sorted({s["forte"] for s in sections}),
        grid=_build_grid(notes, data, ticks_per_bar),
        violations=violations,
        density=_density(notes, data),
    )
    if to_score:
        import music21  # noqa: F401  (opt-in heavy import)
        from music21 import converter
        report.score = converter.parse(str(path))
    return report
