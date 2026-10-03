# -*- coding: utf-8 -*-
"""
Project 218: Baroque x Xenakis Sieve Theory (Method 025).

Autonomous nightly composition job (2026-10-02).
  Style:  Baroque (D minor, flowing allemande/courante/sarabande/gigue idiom)
  Method: 025 Xenakis Sieve Theory (modular congruence / residual sieve
          intersections over integer space)  -- Layer: concrete
  Key:    D natural minor (aeolian): D E F G Bb C  -> pcs {2,4,5,7,9,10,0}
  Tempo:  96 BPM, 4/4, 480 TPB -> BAR = 1920 ticks
  Form:   6 sections x 4 bars = 24 bars

Two-phase architecture:
  Phase 1 = raw generative draft: a single Violin voice whose pitch/timing is
            a Xenakis sieve WALK (unquantized ticks, chromatic sieve residues,
            no chord-tone quantization)  ->  <project>-phase1.mid
  Phase 2 = musicom rules: 16th-grid snap (120 ticks), per-bar chord-tone
            quantization to D minor, register clamp, full Baroque texture
            (5 voices)  ->  <project>.mid

Xenakis sieve formulas (periods over Z):
  Pitch sieve  S_p = { n : n mod 3 in {0,2} }  INTERSECT  { n : n mod 4 in {0,2,3} }
                     residues mod 12 = {0, 2, 3, 6, 8, 11}   (6-note sieve scale)
  Rhythm sieve S_r = { s : s mod 4 in {0,2,3} } INTERSECT { s : s mod 8 in {0,1,3,4,6} }
                     active 16th-steps = {0, 3, 4, 6, 8, 11, 12, 14}  (syncopated)

Zero-drift gate: UnitMatrixComposer.validate() MUST pass for both phases.
"""
import os
import numpy as np

from structures import MusicUnit, MusicEvent
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.unitmatrix_composer import UnitMatrixComposer

# Instrument registry (source of truth) -- full KB, not the 10-entry enum
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
import sys
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import VIOLIN, FLUTE, HARPSICHORD, CELLO

# ------------------------------------------------------------- CONFIG ----
GENRE = "Baroque"
PROJECT_NAME = "218-baroque-sieve"
PROJECT_DIR = f"/opt/data/repos/musicom/projects/Styles/{GENRE}/{PROJECT_NAME}"

BPM = 96
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR = TICKS_PER_BEAT * BEATS_PER_BAR      # 1920
GRID16 = 120                                # 16th note
GRID8 = 240                                 # 8th note

SEED = 20261002
rng = np.random.default_rng(SEED)

# D natural minor (aeolian): D E F G A Bb C -> pcs {2,4,5,7,9,10,0}
KEY_NAME = "D minor (natural/aeolian)"
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}

# chord degree -> pitch-class set (D natural-minor triads), each subset of KEY_PCS
DEG_PCS = {
    0: {2, 5, 9},     # i    Dm
    1: {4, 7, 10},    # ii°  Edim
    2: {5, 9, 0},     # III  F
    3: {7, 10, 2},    # iv   Gm
    4: {9, 0, 4},     # v    Am
    5: {10, 2, 5},    # VI   Bb
    6: {0, 4, 7},     # VII  C
}
DEG_NAME = {0: "i-Dm", 1: "iio-Edim", 2: "III-F", 3: "iv-Gm",
            4: "v-Am", 5: "VI-Bb", 6: "VII-C"}
# bass root MIDI (D2 = 38 as reference)
DEG_ROOT = {0: 38, 1: 40, 2: 41, 3: 43, 4: 45, 5: 46, 6: 48}

# section -> (name, 4 chord degrees per bar, transform, note)
SECTIONS = [
    ("Prelude",   [0, 5, 3, 0], "none",       "sieve exposed, sparse, tonic anchor"),
    ("Allemande", [0, 3, 6, 2], "transpose",  "flowing 16ths, motif up a major 3rd"),
    ("Courante",  [2, 6, 0, 3], "diminution", "sequence, rhythm compressed"),
    ("Sarabande", [3, 4, 0, 0], "octave_up",  "slow, regal, register lifted"),
    ("Gigue",     [0, 3, 5, 4], "invert",     "fast, imitative, contour inverted"),
    ("Finale",    [4, 0, 3, 0], "augment",    "broad cadence v-i-iv-i"),
]

# per-section lead step (grid resolution) for the raw sieve walk
SECTION_STEP = {
    "Prelude": 480, "Allemande": 120, "Courante": 120,
    "Sarabande": 240, "Gigue": 120, "Finale": 480,
}

# ------------------------------------------------------ Xenakis sieves ----
def is_in_pitch_sieve(n):
    return (n % 3 in (0, 2)) and (n % 4 in (0, 2, 3))

def is_in_rhythm_sieve(s):
    return (s % 4 in (0, 2, 3)) and (s % 8 in (0, 1, 3, 4, 6))

PITCH_RESIDUES = [n for n in range(12) if is_in_pitch_sieve(n)]
RHYTHM_STEPS = [s for s in range(16) if is_in_rhythm_sieve(s)]


# ------------------------------------------------------ helpers ----------
def chord_tones(deg_id, lo=40, hi=100):
    return [m for m in range(lo, hi + 1) if (m % 12) in DEG_PCS[deg_id]]


def nearest_in(pitches, target):
    return min(pitches, key=lambda p: abs(p - target))


def rhythm_gate(i, step):
    """Onset gate for the raw walk. Dense sections use the full sieve on the
    16th grid; sparser sections use a beat-level subset."""
    if step == 120:
        return (i % 16) in RHYTHM_STEPS
    if step == 240:
        return (i % 8) in (0, 2, 3, 4, 6)
    if step == 480:
        return (i % 4) in (0, 2)
    return True


# ------------------------------------------------- phase-1 raw sieve -----
def raw_lead(section, sec_idx):
    """Phase 1: Xenakis sieve walk -> chromatic pitch + unquantized timing.
    Returns list of dicts {tick, midi, vel, dur}."""
    name, degrees, transform, _note = section
    step = SECTION_STEP[name]
    n = (4 * BAR) // step
    sieve_idx = sec_idx * 23 + 5          # per-section sieve phase
    out = []
    for i in range(n):
        if not rhythm_gate(i, step):
            continue
        # advance pitch sieve to next congruent match
        while not is_in_pitch_sieve(sieve_idx):
            sieve_idx += 1
        residue = sieve_idx % 12
        oct_wander = (sieve_idx // 12) % 2
        raw_midi = int(np.clip(62 + residue + 12 * oct_wander - 6, 55, 88))
        vel = int(rng.integers(72, 100))
        jit = int(rng.integers(-18, 18))   # micro-timing => off-grid (raw)
        out.append({"tick": max(0, i * step + jit),
                    "midi": raw_midi, "vel": vel, "dur": step})
        sieve_idx += 1
    return out


# ------------------------------------------------- phase-2 transforms -----
def apply_transform(events, transform):
    if transform == "none":
        return events
    if transform == "transpose":
        for e in events:
            e["midi"] += 4                       # up a major 3rd
        return events
    if transform == "diminution":
        base = min((e["tick"] for e in events), default=0)
        for e in events:
            e["tick"] = base + int((e["tick"] - base) * 0.5)
            e["dur"] = max(120, e["dur"] // 2)
        return events
    if transform == "octave_up":
        for e in events:
            e["midi"] += 12
        return events
    if transform == "invert":
        for e in events:
            e["midi"] = 124 - e["midi"]          # reflect contour around D4
        return events
    if transform == "augment":
        for e in events:
            e["midi"] -= 12                      # register down
            e["dur"] = max(e["dur"], 2 * 960)    # broadened duration
        return events
    return events


def quantize(events, degrees, lo=52, hi=88):
    """Phase 2 rule: chord-tone quantize per bar + 16th-grid snap + register
    clamp + dedup collided (tick,pitch) keeping longest duration.
    Candidates are chord tones ONLY within [lo,hi] (never clamp AFTER nearest,
    which would break chord membership)."""
    tones_per_bar = [chord_tones(d, lo, hi) for d in degrees]
    seen = {}
    for e in events:
        tick = int(round(e["tick"] / GRID16) * GRID16)   # snap to 16th grid
        bar = tick // BAR
        if bar >= 4:
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


# ------------------------------------------------- voice builders ---------
def build_lead_unit(section, sec_idx):
    name, degrees, transform, _ = section
    raw = raw_lead(section, sec_idx)
    raw = apply_transform(raw, transform)
    q = quantize(raw, degrees, lo=55, hi=88)
    return _unit_from_quantized(q, 4 * BAR)


def build_counter_unit(section, sec_idx):
    """Imitative second violin (canon at the octave, delayed one beat).
    Active in the contrapuntal sections (Allemande/Courante/Gigue)."""
    name, degrees, transform, _ = section
    total = 4 * BAR
    if name not in ("Allemande", "Courante", "Gigue"):
        return _pad(MusicUnit(), total)
    raw = raw_lead(section, sec_idx)
    raw = apply_transform(raw, transform)
    delayed = []
    for e in raw:
        tick = e["tick"] + TICKS_PER_BEAT
        if tick + 120 > total:
            continue
        delayed.append({"tick": tick, "midi": e["midi"] + 12,
                        "vel": max(40, e["vel"] - 10), "dur": e["dur"]})
    q = quantize(delayed, degrees, lo=60, hi=96)
    return _unit_from_quantized(q, total)


def build_recorder_unit(section, sec_idx):
    """Ornamental sustained upper line (recorder/Flute). Active in the slow +
    cadential sections, holding chord tones an octave above the continuo."""
    name, degrees, transform, _ = section
    total = 4 * BAR
    unit = MusicUnit()
    if name not in ("Prelude", "Sarabande", "Finale"):
        return _pad(unit, total)
    for bar in range(4):
        d = degrees[bar]
        tones = sorted(chord_tones(d, 67, 96), key=lambda x: abs(x - 79))
        top = tones[:2]
        for pp in top:
            unit.add_event(MusicEvent(
                pitch=pp, volume=62,
                start_tick=bar * BAR, end_tick=(bar + 1) * BAR))
    return _pad(unit, total)


def build_harpsichord_unit(section, sec_idx):
    """Basso-continuo realization: broken-chord 8th-note arpeggiation of each
    bar's triad (root/3rd/5th only -> always chord tones)."""
    name, degrees, transform, _ = section
    total = 4 * BAR
    unit = MusicUnit()
    for bar in range(4):
        d = degrees[bar]
        tones = sorted(chord_tones(d, 48, 72), key=lambda x: abs(x - 60))[:3]
        if len(tones) < 3:
            tones = chord_tones(d, 48, 72)[:3]
        pattern = [0, 1, 2, 1]                       # root-3rd-5th-3rd
        for k in range(8):                           # 8 eighth-notes
            t = bar * BAR + k * GRID8
            idx = pattern[k % 4]
            unit.add_event(MusicEvent(
                pitch=tones[idx], volume=58,
                start_tick=t, end_tick=t + GRID8))
    return _pad(unit, total)


def build_cello_unit(section, sec_idx):
    """Basso continuo bass line: quarter-note root/fifth/octave (all chord
    tones), locking beats 1-3 root, 2-4 fifth/octave."""
    name, degrees, transform, _ = section
    total = 4 * BAR
    unit = MusicUnit()
    for bar in range(4):
        d = degrees[bar]
        root = DEG_ROOT[d]
        for beat, note in ((0, root), (1, root + 7), (2, root), (3, root + 12)):
            t = bar * BAR + beat * TICKS_PER_BEAT
            unit.add_event(MusicEvent(
                pitch=note, volume=70,
                start_tick=t, end_tick=t + TICKS_PER_BEAT))
    return _pad(unit, total)


# ------------------------------------------------- phase-1 export ---------
def export_phase1(out_path):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    c.add_voice("Lead", program=VIOLIN.midi_program, channel=0)
    for (name, degrees, transform, note) in SECTIONS:
        c.add_section(name, bars=4)
    for idx, section in enumerate(SECTIONS):
        name = section[0]
        raw = raw_lead(section, idx)
        total = 4 * BAR
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


# ------------------------------------------------- main -------------------
def main():
    for sub in ("MIDI", "Audio", "Analysis"):
        os.makedirs(os.path.join(PROJECT_DIR, sub), exist_ok=True)

    print("Pitch sieve residues mod 12:", PITCH_RESIDUES)
    print("Rhythm sieve 16th-steps:", RHYTHM_STEPS)

    p1_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-phase1.mid")
    export_phase1(p1_path)
    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="025-Xenakis-Sieve-Theory (raw sieve walk)",
        parameters={"phase": 1, "bpm": BPM, "key": KEY_NAME, "seed": SEED,
                    "voices": 1,
                    "pitch_sieve": "n%3 in {0,2} & n%4 in {0,2,3}",
                    "rhythm_sieve": "s%4 in {0,2,3} & s%8 in {0,1,3,4,6}",
                    "note": "raw generative draft, unquantized ticks, chromatic, pre-rules"},
    )

    c2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c2.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    c2.add_voice("Lead",       program=VIOLIN.midi_program,     channel=0)
    c2.add_voice("Counter",    program=VIOLIN.midi_program,     channel=1)
    c2.add_voice("Recorder",   program=FLUTE.midi_program,      channel=2)
    c2.add_voice("Harpsichord", program=HARPSICHORD.midi_program, channel=3)
    c2.add_voice("Cello",      program=CELLO.midi_program,      channel=4)
    for (name, degrees, transform, note) in SECTIONS:
        c2.add_section(name, bars=4)

    for idx, section in enumerate(SECTIONS):
        name = section[0]
        c2.fill_voice_section("Lead",        name, build_lead_unit(section, idx))
        c2.fill_voice_section("Counter",     name, build_counter_unit(section, idx))
        c2.fill_voice_section("Recorder",    name, build_recorder_unit(section, idx))
        c2.fill_voice_section("Harpsichord", name, build_harpsichord_unit(section, idx))
        c2.fill_voice_section("Cello",       name, build_cello_unit(section, idx))

    ok, msg = c2.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")

    midi_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    c2.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40, "empty phase2"
    assert os.path.getsize(p1_path) > 40, "empty phase1"

    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator="025-Xenakis-Sieve-Theory + musicom rules",
        parameters={"phase": 2, "bpm": BPM, "key": KEY_NAME, "seed": SEED,
                    "voices": 5, "form": "6 sections x 4 bars = 24 bars",
                    "quantization": "16th-grid (120 ticks)",
                    "variations": "transpose(+M3), diminution, octave_up, invert, augment"},
        notes="Baroque D minor. Two-phase: raw Xenakis sieve walk -> chord-tone "
              "quantized + grid-snapped 5-voice texture (Violin/Violin2/Recorder/"
              "Harpsichord/Cello). All pitches are D-minor chord tones.",
    )

    grid_path = os.path.join(PROJECT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=240, bpm=BPM)

    print("PHASE1", p1_path, os.path.getsize(p1_path))
    print("PHASE2", midi_path, os.path.getsize(midi_path))
    print("GRID", grid_path)


if __name__ == "__main__":
    main()
