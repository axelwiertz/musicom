# -*- coding: utf-8 -*-
"""
222-flamenco-arc-register - Flamenco style / CONCRETE layer: Method 007
Narrative Arc Register Planning (Rules-Based, Macro/Form).

Autonomous nightly composition job (date: 2026-10-04, job 1fc3fd65d359).

Method 007 essence: a narrative story arc (calm -> rise -> climax -> fall ->
resolve) is mapped onto SPECIFIC REGISTRAL BOUNDARIES across the UnitMatrix
columns (bars). The melody is register-driven: at each time position the arc
dictates a register band, and the pitch material occupies that band.

Two-phase architecture:
  Phase 1 (raw draft): single Guitar voice. Pitches wander within the arc's
    register band at each bar (register-led, NOT chord-led), placed on
    FRACTIONAL off-grid ticks with micro-timing jitter. No scale/chord snap.
    -> <project>-phase1.mid
  Phase 2 (musicom rules): 16th-grid snap -> per-bar chord-tone quantize to the
    Andalusian cadence (Am-G-F-E) -> per-section register clamp -> full 5-voice
    flamenco texture (lead guitar, cante violin, compas clavi, bajo bass,
    palmas drum kit). -> <project>.mid

Key: E flamenco ("por arriba") composite = E F G G# A B C D
     pc {4,5,7,8,9,11,0,2}  (Phrygian-dominant + natural-3 blend)
Form: Entrada | Letra | Falseta | Cumbre | Bajada | Cierre (6 x 4 = 24 bars).
BPM 120, 4/4, 480 TPB (BAR = 1920, 16th = 120, 8th = 240, total = 46080).

Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading.
mido used READ-ONLY in the separate audit script.
"""
import os
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    ACOUSTIC_GUITAR, VIOLIN, CLAVI, DOUBLE_BASS,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20261004
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
GENRE = "Flamenco"
PROJECT_NAME = "222-flamenco-arc-register"
PROJ = f"/opt/data/repos/musicom/projects/Styles/{GENRE}/{PROJECT_NAME}"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- grid & timing
BPM = 120
TPB = 480
BEATS_PER_BAR = 4
GRID16 = 120
GRID8 = 240
BAR_TICKS = TPB * BEATS_PER_BAR          # 1920
BARS_PER_SECTION = 4
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION   # 7680
TOTAL_TICKS = SECTION_TICKS * 6                # 46080

# ---------------------------------------------------------------- harmony
# E flamenco composite scale: E(4) F(5) G(7) G#(8) A(9) B(11) C(0) D(2)
KEY_NAME = "E flamenco (por arriba) composite"
SCALE_PCS = {4, 5, 7, 8, 9, 11, 0, 2}

# Andalusian cadence chord degrees (0-indexed), each subset of SCALE_PCS
DEG_PCS = {
    0: {9, 0, 4},    # Am (iv)
    1: {7, 11, 2},   # G  (bIII)
    2: {5, 9, 0},    # F  (bII)
    3: {4, 8, 11},   # E  (I, major tonic)
}
DEG_NAME = {0: "Am", 1: "G", 2: "F", 3: "E"}
DEG_ROOT = {0: 45, 1: 43, 2: 41, 3: 40}   # A2 G2 F2 E2

# ---------------------------------------------------------------- form
# (name, 4 per-bar chord degrees, raw-grid step in ticks)
SECTIONS = [
    ("Entrada", [0, 1, 2, 3], 480),   # sparse, low register, tonic anchor
    ("Letra",   [0, 1, 2, 3], 240),   # lyrical mid register
    ("Falseta", [0, 2, 1, 3], 120),   # virtuosic mid-high run
    ("Cumbre",  [0, 1, 0, 3], 120),   # climax, highest register
    ("Bajada",  [2, 1, 0, 3], 240),   # descent
    ("Cierre",  [2, 1, 0, 3], 480),   # close, low register, resolve to E
]

# ------------------------------------------------- narrative arc (method 007)
# Registral boundaries per section = the "story arc" mapped to register.
REG_LO = 48
REG_HI = 88

SECTION_BANDS = {
    "Entrada": (48, 60),   # low, calm
    "Letra":   (60, 72),   # mid, lyrical
    "Falseta": (64, 79),   # mid-high, virtuosic
    "Cumbre":  (76, 88),   # high, climax peak
    "Bajada":  (64, 76),   # falling
    "Cierre":  (52, 64),   # low, resolved
}


def arc_level(bar_idx):
    """Global narrative arc 0..1 over 24 bars: rise to peak at bar ~14, fall."""
    if bar_idx <= 14:
        return (bar_idx / 14.0) ** 0.85
    return max(0.0, 1.0 - ((bar_idx - 14) / 9.0) ** 1.15)


def chord_tones(deg_id, lo=48, hi=88):
    return [m for m in range(lo, hi + 1) if (m % 12) in DEG_PCS[deg_id]]


def nearest_in(pitches, target):
    return min(pitches, key=lambda p: abs(p - target))


def onset_gate(i, step, name):
    if step == 480:
        return (i % 4) in (0, 2)
    if step == 240:
        return (i % 8) in (0, 2, 4, 6)
    if step == 120:
        return (i % 2) == 0
    return True


# ------------------------------------------------- phase-1 raw register walk
def raw_lead(section, sec_idx):
    """Phase 1: register-led walk. At each bar the narrative arc sets a
    register center; pitches wander within that band on off-grid ticks."""
    name, degrees, step = section
    lo, hi = SECTION_BANDS[name]
    out = []
    for bar_local in range(BARS_PER_SECTION):
        bar_global = sec_idx * BARS_PER_SECTION + bar_local
        center = REG_LO + arc_level(bar_global) * (REG_HI - REG_LO)
        n_slots = BAR_TICKS // step
        for i in range(n_slots):
            if not onset_gate(i, step, name):
                continue
            wander = int(rng.integers(-6, 7))
            raw_midi = int(np.clip(center + wander, lo, hi))
            vel = int(rng.integers(72, 100))
            jit = int(rng.integers(-18, 18))
            tick = bar_local * BAR_TICKS + i * step + jit
            out.append({"tick": max(0, tick), "midi": raw_midi,
                        "vel": vel, "dur": step})
    return out


# ------------------------------------------------- phase-2 transforms
def quantize(events, degrees, lo, hi):
    """Phase 2 rule: 16th-grid snap + per-bar chord-tone quantize + per-section
    register clamp + dedup collided (tick, pitch) keeping longest duration."""
    tones_per_bar = [chord_tones(d, lo, hi) for d in degrees]
    seen = {}
    for e in events:
        tick = int(round(e["tick"] / GRID16) * GRID16)
        bar = tick // BAR_TICKS
        if bar >= BARS_PER_SECTION:
            continue
        chor = nearest_in(tones_per_bar[bar], e["midi"])
        key = (tick, chor)
        seen[key] = max(seen.get(key, 0), e["dur"])
    out = [(t, p, 90, d) for (t, p), d in sorted(seen.items())]
    return out


def _unit_from_quantized(q, total):
    unit = MusicUnit()
    for (t, p, v, d) in q:
        unit.add_event(MusicEvent(pitch=p, volume=v,
                                  start_tick=t, end_tick=min(t + d, total)))
    return _pad(unit, total)


def _pad(unit, total):
    if not unit.events:
        unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=total))
    else:
        mx = max(e.end_tick for e in unit.events)
        if mx < total:
            unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=mx, end_tick=total))
    return unit


# ------------------------------------------------- voice builders (phase 2)
def build_lead_unit(section, sec_idx):
    name, degrees, step = section
    lo, hi = SECTION_BANDS[name]
    raw = raw_lead(section, sec_idx)
    q = quantize(raw, degrees, lo, hi)
    return _unit_from_quantized(q, SECTION_TICKS)


def build_cante_unit(section, sec_idx):
    """Cante (violin): sustained upper counterline, active at the lyric/climax/
    descent sections, doubling the arc peaks an octave above the lead."""
    name, degrees, step = section
    total = SECTION_TICKS
    unit = MusicUnit()
    if name not in ("Letra", "Cumbre", "Bajada"):
        return _pad(unit, total)
    lo, hi = SECTION_BANDS[name]
    hi += 12 if name == "Cumbre" else 0
    for bar in range(BARS_PER_SECTION):
        d = degrees[bar]
        tones = sorted(chord_tones(d, lo, hi), key=lambda x: abs(x - (hi - 4)))
        top = tones[:2]
        for pp in top:
            unit.add_event(MusicEvent(
                pitch=pp, volume=58,
                start_tick=bar * BAR_TICKS, end_tick=(bar + 1) * BAR_TICKS))
    return _pad(unit, total)


def build_compas_unit(section, sec_idx):
    """Compas (clavi): rasgueado strumming - 8th-note chord stabs (root/3rd/5th)
    with a strong flamenco 'golpe' accent on the downbeat."""
    name, degrees, step = section
    total = SECTION_TICKS
    unit = MusicUnit()
    for bar in range(BARS_PER_SECTION):
        d = degrees[bar]
        tones = sorted(chord_tones(d, 52, 76), key=lambda x: abs(x - 64))[:3]
        if len(tones) < 3:
            tones = chord_tones(d, 52, 76)[:3]
        pattern = [0, 1, 2, 1]
        for k in range(8):
            t = bar * BAR_TICKS + k * GRID8
            idx = pattern[k % 4]
            vol = 78 if k % 4 == 0 else 52
            unit.add_event(MusicEvent(
                pitch=tones[idx], volume=vol,
                start_tick=t, end_tick=t + GRID8))
    return _pad(unit, total)


def build_bajo_unit(section, sec_idx):
    """Bajo (double bass): quarter-note root/fifth/octave (all chord tones)
    locking the Andalusian cadence (Am-G-F-E)."""
    name, degrees, step = section
    total = SECTION_TICKS
    unit = MusicUnit()
    for bar in range(BARS_PER_SECTION):
        d = degrees[bar]
        root = DEG_ROOT[d]
        for beat, note in ((0, root), (1, root + 7), (2, root), (3, root + 12)):
            t = bar * BAR_TICKS + beat * TPB
            unit.add_event(MusicEvent(
                pitch=note, volume=70,
                start_tick=t, end_tick=t + TPB))
    return _pad(unit, total)


def build_palmas_unit(section, sec_idx):
    """Palmas (ch9): flamenco rumba compas - kick on 1 & 3, hand-clap palmas on
    2 & 4, closed hat on the 8th grid."""
    name, degrees, step = section
    total = SECTION_TICKS
    unit = MusicUnit()
    for bar in range(BARS_PER_SECTION):
        bs = bar * BAR_TICKS
        for pos in (0, 8):                     # kick beats 1 & 3
            unit.add_event(MusicEvent(pitch=KIT["kick"], volume=96,
                                      start_tick=bs + pos * GRID16,
                                      end_tick=bs + pos * GRID16 + 100))
        for pos in (4, 12):                    # palmas beats 2 & 4
            unit.add_event(MusicEvent(pitch=KIT["clap"], volume=82,
                                      start_tick=bs + pos * GRID16,
                                      end_tick=bs + pos * GRID16 + 60))
        for pos in range(0, 16, 2):            # closed hat 8ths
            unit.add_event(MusicEvent(pitch=KIT["hat_closed"], volume=40,
                                      start_tick=bs + pos * GRID16,
                                      end_tick=bs + pos * GRID16 + 40))
    return _pad(unit, total)


# ------------------------------------------------- phase-1 export
def export_phase1(out_path):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    c.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    c.add_voice("Lead", program=ACOUSTIC_GUITAR.midi_program, channel=0)
    for (name, degrees, step) in SECTIONS:
        c.add_section(name, bars=BARS_PER_SECTION)
    for idx, section in enumerate(SECTIONS):
        name = section[0]
        raw = raw_lead(section, idx)
        total = SECTION_TICKS
        unit = MusicUnit()
        for e in raw:
            unit.add_event(MusicEvent(
                pitch=e["midi"], volume=e["vel"],
                start_tick=e["tick"], end_tick=min(e["tick"] + e["dur"], total)))
        c.fill_voice_section("Lead", name, _pad(unit, total))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    c.to_midi(out_path)
    return c


# ------------------------------------------------- main
def main():
    print("Scale:", sorted(SCALE_PCS), "-> E F G G# A B C D")
    print("Andalusian cadence: Am-G-F-E; roots", DEG_ROOT)

    p1_path = os.path.join(MIDI_DIR, f"{PROJECT_NAME}-phase1.mid")
    export_phase1(p1_path)
    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="007-Narrative-Arc-Register-Planning (raw register walk)",
        parameters={"phase": 1, "bpm": BPM, "key": KEY_NAME, "seed": SEED,
                    "voices": 1,
                    "arc": "register-led narrative arc (calm->rise->climax->fall->resolve)",
                    "register_bands": {k: list(v) for k, v in SECTION_BANDS.items()},
                    "note": "raw generative draft, unquantized ticks, register-wandered, pre-rules"},
    )

    c2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    c2.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    c2.add_voice("Lead",   program=ACOUSTIC_GUITAR.midi_program, channel=0)
    c2.add_voice("Cante",  program=VIOLIN.midi_program,          channel=1)
    c2.add_voice("Compas", program=CLAVI.midi_program,           channel=2)
    c2.add_voice("Bajo",   program=DOUBLE_BASS.midi_program,     channel=3)
    c2.add_voice("Palmas", program=0,                            channel=9)
    for (name, degrees, step) in SECTIONS:
        c2.add_section(name, bars=BARS_PER_SECTION)

    for idx, section in enumerate(SECTIONS):
        name = section[0]
        c2.fill_voice_section("Lead",   name, build_lead_unit(section, idx))
        c2.fill_voice_section("Cante",  name, build_cante_unit(section, idx))
        c2.fill_voice_section("Compas", name, build_compas_unit(section, idx))
        c2.fill_voice_section("Bajo",   name, build_bajo_unit(section, idx))
        c2.fill_voice_section("Palmas", name, build_palmas_unit(section, idx))

    ok, msg = c2.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")

    midi_path = os.path.join(MIDI_DIR, f"{PROJECT_NAME}.mid")
    c2.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40, "empty phase2"
    assert os.path.getsize(p1_path) > 40, "empty phase1"

    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator="007-Narrative-Arc-Register-Planning + musicom rules",
        parameters={"phase": 2, "bpm": BPM, "key": KEY_NAME, "seed": SEED,
                    "voices": 5, "form": "6 sections x 4 bars = 24 bars",
                    "quantization": "16th-grid (120 ticks)",
                    "chord_cycle": "Andalusian cadence Am-G-F-E",
                    "register_bands": {k: list(v) for k, v in SECTION_BANDS.items()}},
        notes="Flamenco 'por arriba'. Two-phase: register-led narrative arc walk "
              "-> chord-tone quantized + grid-snapped 5-voice flamenco texture "
              "(guitar/cante violin/compas clavi/bajo bass/palmas). All pitched "
              "voices are E-flamenco chord tones.",
    )

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=240, bpm=BPM)

    print("PHASE1", p1_path, os.path.getsize(p1_path))
    print("PHASE2", midi_path, os.path.getsize(midi_path))
    print("GRID", grid_path)


if __name__ == "__main__":
    main()
