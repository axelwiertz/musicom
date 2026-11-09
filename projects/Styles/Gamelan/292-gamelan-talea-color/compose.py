# -*- coding: utf-8 -*-
"""292-gamelan-talea-color -- Gamelan / Method 032 Isorhythmic Talea-Color Mapping.

LAYER: concrete (Rules-Based, grid-locked, strict tonal gravity).

Two-phase architecture:
  Phase 1: raw generative draft -- a single-voice isorhythmic stream. A fixed
           COLOR (5-note C-pentatonic sequence) runs against a fixed TALEA
           (7-duration rhythm), coprime lengths (5 x 7) -> the pitch/rhythm
           alignment shifts every cycle (LCM 35) and only realigns after 35
           notes. Onsets carry OFF-GRID jitter + pitch carries unquantized
           semitone drift. No harmony/pad/kotekan/gong. This IS the method's
           generative act (talea x color decoupling).

  Phase 2: musicom rules post-process:
           1. GRID LOCK the balungan to the 16th grid (078 rule).
           2. Tiered snap (engine ScaleQuantizer + classify_weight): strong
              beats -> bar's slendro-trichord tone, weak -> pentatonic scale
              tone. Color stays fixed pentatonic => weak snap = identity.
           3. Kotekan (steel drums) = interlocking 16th figuration on chord
              tones (gamelan interlock).
           4. Saron (celesta) = sustained slendro trichord per bar (harmony,
              chromatic-free).
           5. Gong (double bass) = colotomic low gong root, 1 per bar.
           6. Zero-drift landmark + validate() on BOTH phases.
           7. export_dual -> -perfect.mid + -humanized.mid.

Engine only. mido is used READ-ONLY in the separate verify step.

C-major pentatonic (slendro): pitch classes {0,2,4,7,9} = C D E G A.
"""
import os
import json
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    MARIMBA, STEEL_DRUMS, CELESTA, DOUBLE_BASS,
)

SEED = 20261108
HZ_SEED = SEED * 13 + 292
rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------ project
PROJ = "/opt/data/projects/Styles/Gamelan/292-gamelan-talea-color"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- concept
BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120                     # 16th-note grid
GRID8 = 240                      # 8th-note grid
NAMES = ["S1", "S2", "S3", "S4", "S5", "S6"]   # through-composed form
BARS_PER = 4
N_SECTIONS = 6
N_BARS = 24                      # 6 sections x 4 bars
SECTION_TICKS = BAR * BARS_PER   # 7680
TOTAL_TICKS = N_SECTIONS * SECTION_TICKS

# C-major pentatonic (slendro): C D E G A
KEY = "C major pentatonic (slendro)"
KEY_PCS = {0, 2, 4, 7, 9}
SCALE_ROOT = 60                  # C4

# pentatonic degree index -> semitone offset from C
PENTA_OFFSET = [0, 2, 4, 7, 9]

# voice registers (from instrument sweet spots)
LEAD_LO, LEAD_HI = 60, 84        # marimba balungan
KOTEK_LO, KOTEK_HI = 65, 86      # steel drums interlock
SARON_LO, SARON_HI = 72, 96      # celesta pad
GONG_LO, GONG_HI = 40, 55        # double-bass gong

# ------------------------------------------------------------------- method
# COLOR: fixed 5-note pitch sequence (pentatonic degrees, arch contour).
COLOR_DEG = [0, 2, 4, 3, 1]      # C E A G D
COLOR = [72 + PENTA_OFFSET[d] for d in COLOR_DEG]   # [72, 76, 81, 79, 74]

# TALEA: fixed 7-duration rhythm (16th-note units), sums to 16 sixteenths = 1 bar.
TALEA16 = [2, 3, 2, 2, 3, 2, 2]  # 7 elements, coprime(7, 5)
assert sum(TALEA16) == 16, sum(TALEA16)

# ------------------------------------------------------------------- harmony
# colotomic gong cycle (24 bars, through-composed -- no exact section repeat).
GONG_DEG = [
    0, 3, 2, 0,      # S1
    4, 2, 1, 4,      # S2
    2, 0, 3, 2,      # S3
    1, 4, 0, 1,      # S4
    3, 1, 4, 3,      # S5
    0, 3, 4, 0,      # S6
]
assert len(GONG_DEG) == N_BARS, len(GONG_DEG)


def triad_degrees(gong):
    """Slendro trichord: stack every-other pentatonic degree (quartal-ish)."""
    return sorted({gong % 5, (gong + 2) % 5, (gong + 4) % 5})


def chord_pcs(bar):
    return sorted({PENTA_OFFSET[d] for d in triad_degrees(GONG_DEG[bar])})


CHORD_PCS_BY_BAR = {bar: chord_pcs(bar) for bar in range(N_BARS)}


def chord_tones(bar, lo, hi):
    tones = set()
    for base in (48, 60, 72, 84, 96):
        for pc in CHORD_PCS_BY_BAR[bar]:
            p = base + pc
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def gong_root(bar):
    p = 36 + PENTA_OFFSET[GONG_DEG[bar]]   # C2 = 36
    while p < GONG_LO:
        p += 12
    return p


def global_bar(sec, local_tick):
    return int(sec) * BARS_PER + (int(local_tick) // BAR)


# ------------------------------------------------------------------- phase 1
def raw_talea_color(seed, span_ticks):
    """Single-voice isorhythmic stream: COLOR x TALEA, off-grid + raw pitch."""
    r = np.random.default_rng(seed)
    events = []
    onset = 0.0
    color_i = 0
    talea_i = 0
    while onset < span_ticks:
        dur16 = TALEA16[talea_i]
        jitter = r.normal(0.0, 0.14) * GRID16      # off-grid onset jitter
        st = int(round(onset + jitter))
        drift = int(r.normal(0.0, 1.6))            # unquantized pitch drift
        pitch = int(np.clip(COLOR[color_i] + drift, LEAD_LO, LEAD_HI))
        dur = dur16 * GRID16
        en = int(round(st + dur * (0.7 + 0.3 * r.random())))
        if en <= st:
            en = st + 1
        if en > span_ticks:
            en = span_ticks
        if 0 <= st < span_ticks:
            vel = int(np.clip(78 + 14 * r.random(), 60, 100))
            events.append(MusicEvent(pitch=pitch, volume=vel,
                                     start_tick=st, end_tick=en))
        onset += dur16 * GRID16
        color_i = (color_i + 1) % len(COLOR)
        talea_i = (talea_i + 1) % len(TALEA16)
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("BalunganRaw", program=MARIMBA.midi_program, channel=0)

P1_OFFGRID = 0
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_talea_color(SEED + s, SECTION_TICKS)
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    P1_OFFGRID += sum(1 for e in evs if e.pitch != 0 and e.start_tick % GRID16 != 0)
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
if not ok1:
    raise RuntimeError("phase1 validate FAIL: " + msg1)
P1_MIDI = os.path.join(MIDI_DIR, "292-gamelan-talea-color-phase1.mid")
phase1.to_midi(P1_MIDI)
print("PHASE1 validate:", msg1, "| off-grid onsets:", P1_OFFGRID)
print("phase1 written", P1_MIDI)


# ------------------------------------------------------------------- phase 2
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Balungan", MARIMBA.midi_program, 0),        # isorhythmic lead
    ("Kotekan", STEEL_DRUMS.midi_program, 1),     # interlocking 16ths
    ("Saron", CELESTA.midi_program, 2),           # sustained trichord pad
    ("Gong", DOUBLE_BASS.midi_program, 3),        # colotomic low gong
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)


def grid_lock_dedup(events, grid=GRID16):
    by_key = {}
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        if st < 0:
            st = 0
        en = max(st + 1, int(e.end_tick))
        if en > SECTION_TICKS:
            en = SECTION_TICKS
        key = (st, e.pitch)
        if key in by_key:
            if en > by_key[key].end_tick:
                by_key[key] = MusicEvent(pitch=e.pitch,
                                         volume=max(e.volume, by_key[key].volume),
                                         start_tick=st, end_tick=en)
        else:
            by_key[key] = MusicEvent(pitch=e.pitch, volume=e.volume,
                                     start_tick=st, end_tick=en)
    for key in sorted(by_key):
        out.append(by_key[key])
    return out


def landmark(events):
    out = []
    for e in events:
        if e.start_tick >= SECTION_TICKS:
            continue
        st = min(int(e.start_tick), SECTION_TICKS - 1)
        en = min(int(e.end_tick), SECTION_TICKS)
        if en <= st:
            en = st + 1
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=st, end_tick=en))
    out.sort(key=lambda e: (e.start_tick, 0 if e.pitch == 0 else 1))
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in out):
        out.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    return out


# tiered pitch discipline (engine)
from sound.synthesis.scale_quantizer import (  # noqa: E402
    ScaleQuantizer, classify_weight, STRONG_GRID,
)
sq = ScaleQuantizer(root=SCALE_ROOT, scale="pentatonic")
STRONG = STRONG_GRID.get("4/4", (0, 960))

# ---- balungan: grid-locked isorhythmic lead, tiered snap ------------------
def balungan_events(s):
    raw = raw_talea_color(SEED + s, SECTION_TICKS)
    raw = grid_lock_dedup(raw)
    evs = []
    for e in raw:
        if e.pitch == 0:
            continue
        bar = global_bar(s, e.start_tick)
        tones = chord_tones(bar, lo=LEAD_LO, hi=LEAD_HI)
        w = classify_weight(e.start_tick, STRONG, BAR)
        pitch = sq.tiered_quantize(e.pitch, weight=w, chord_tones=tones)
        evs.append(MusicEvent(pitch=pitch, volume=e.volume,
                              start_tick=e.start_tick, end_tick=e.end_tick))
    return landmark(evs)

for s in range(N_SECTIONS):
    phase2.set_unit(0, s, MusicUnit(events=balungan_events(s)))

# ---- kotekan: interlocking 16th figuration on chord tones -----------------
for s in range(N_SECTIONS):
    evs = []
    for bar in range(BARS_PER):
        gb = global_bar(s, bar * BAR)
        t0 = bar * BAR
        tones = chord_tones(gb, lo=KOTEK_LO, hi=KOTEK_HI)
        n = len(tones)
        for k in range(16):          # 16 sixteenths per bar
            tone = tones[(k + gb) % n]
            st = t0 + k * GRID16
            vel = 70 if k % 2 == 0 else 58
            evs.append(MusicEvent(pitch=tone, volume=vel,
                                  start_tick=st, end_tick=st + 90))
    phase2.set_unit(1, s, MusicUnit(events=landmark(evs)))

# ---- saron: sustained slendro trichord per bar ----------------------------
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    t0 = b * BAR
    tones = chord_tones(bar, lo=SARON_LO, hi=SARON_HI)
    e = []
    for k, p in enumerate(tones):
        e.append(MusicEvent(pitch=p, volume=50 + 3 * k,
                            start_tick=t0, end_tick=t0 + BAR - 80))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# ---- gong: colotomic low gong root, 1 per bar -----------------------------
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    t0 = b * BAR
    root = gong_root(bar)
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.append(MusicEvent(pitch=root, volume=88,
                             start_tick=t0, end_tick=t0 + int(BAR * 0.75)))
    phase2.set_unit(3, s, MusicUnit(events=events))

# finalize saron + gong cells with landmark
for s in range(N_SECTIONS):
    for row in (2, 3):
        unit = phase2.matrix.get_unit((row, s))
        events = list(unit.events) if unit is not None else []
        phase2.set_unit(row, s, MusicUnit(events=landmark(events)))

ok2, msg2 = phase2.validate()
if not ok2:
    raise RuntimeError("phase2 validate FAIL: " + msg2)
print("PHASE2 validate:", msg2)


# ------------------------------------------------------------------ audits
def global_notes(row):
    notes = []
    for s in range(N_SECTIONS):
        unit = phase2.matrix.get_unit((row, s))
        if unit is None:
            continue
        for e in unit.events:
            if e.pitch == 0:
                continue
            notes.append({"pitch": e.pitch,
                          "start_tick": s * SECTION_TICKS + e.start_tick})
    return notes


from workflows.pitch_audit import audit_voice  # noqa: E402

PITCHED = [(0, "Balungan"), (1, "Kotekan"), (2, "Saron"), (3, "Gong")]
grid_audit = {}
harmony_audit = {}
for row, vname in PITCHED:
    notes = global_notes(row)
    onsets = [n["start_tick"] for n in notes]
    for grid_name, grid in (("16th", 120), ("8th", 240)):
        off = [o for o in onsets if o % grid != 0]
        grid_audit[f"{vname}:{grid_name}"] = f"{len(off)}/{len(onsets)}"
    r = audit_voice(notes, sorted(KEY_PCS), chord_pcs_by_bar=CHORD_PCS_BY_BAR,
                    strong_grid=STRONG, bar_ticks=BAR, grid=GRID8)
    harmony_audit[vname] = {
        "passes": r.passes, "audible": r.audible,
        "strong_ok": r.strong_ok, "weak_in_scale": r.weak_in_scale,
        "tagged": r.tagged_ornaments, "resolving": r.tagged_resolving,
        "non_resolving": r.tagged_non_resolving,
        "untagged_out_of_scale": r.untagged_out_of_scale,
        "strong_violations": r.strong_violations,
        "collisions": r.collisions,
    }
    print(f"AUDIT {vname}: {r.summary()}")

for k, v in grid_audit.items():
    print("GRID", k, v)
assert all(r["passes"] for r in harmony_audit.values()), "harmony audit FAIL"
# only the finest required grid (16th) must be 0 off-grid
assert all(int(x.split("/")[0]) == 0 for k, x in grid_audit.items()
           if k.endswith(":16th")), "grid audit FAIL (16th must be 0 off-grid)"


# ------------------------------------------------------------------ export
perfect_mid = os.path.join(MIDI_DIR, "292-gamelan-talea-color-perfect.mid")
human_mid = os.path.join(MIDI_DIR, "292-gamelan-talea-color-humanized.mid")

hz_instruments = {
    "Balungan": MARIMBA.humanize_dna,
    "Kotekan": STEEL_DRUMS.humanize_dna,
    "Saron": CELESTA.humanize_dna,
    "Gong": DOUBLE_BASS.humanize_dna,
}
hz = export_dual(phase2, perfect_mid, human_mid,
                 style="gamelan", seed=HZ_SEED, bpm=BPM,
                 instruments=hz_instruments)
print("export_dual OK; hz summary:")
print(json.dumps(hz, indent=2, default=str))


# ------------------------------------------------------------------ provenance
write_provenance(P1_MIDI, AI_ASSISTED,
                 "Isorhythmic Talea-Color Mapping (Method 032)",
                 parameters={"phase": "1", "layer": "raw", "style": "gamelan",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "talea": TALEA16, "color": COLOR,
                             "sections": N_SECTIONS, "bars": N_BARS},
                 notes="phase1 raw draft: single-voice isorhythmic stream, "
                       "COLOR (5) x TALEA (7) coprime -> shifting alignment; "
                       "off-grid onset jitter + unquantized pitch drift; "
                       "no harmony/kotekan/saron/gong.")
write_provenance(perfect_mid, AI_ASSISTED,
                 "Isorhythmic Talea-Color 032 + musicom rules (phase 2, grid-locked)",
                 parameters={"phase": "2", "layer": "perfect", "style": "gamelan",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": "through-composed",
                             "talea": TALEA16, "color": COLOR},
                 notes="grid-locked concrete layer; off-grid onsets == 0; "
                       "tiered snap (strong->slendro trichord, weak->pentatonic).")
write_provenance(human_mid, AI_ASSISTED,
                 "Isorhythmic Talea-Color 032 + rules + humanize (phase 2, humanized)",
                 parameters={"phase": "2", "layer": "humanized", "style": "gamelan",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "humanize_profiles": {
                                 k: (v.get("profile") if isinstance(v, dict) else v)
                                 for k, v in hz.items()}},
                 notes="style-derived seeded humanization (default profile + "
                       "per-instrument DNA).")


# ------------------------------------------------------------------ grid viz + manifest
gv = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, gv, ticks_per_character=120)
print("grid viz written", gv)

manifest = {
    "project": "292-gamelan-talea-color",
    "genre": "Gamelan",
    "method": "032 Isorhythmic Talea-Color Mapping",
    "layer": "concrete",
    "form": "through-composed",
    "key": KEY,
    "key_pcs": sorted(KEY_PCS),
    "bpm": BPM,
    "bars": N_BARS,
    "sections": NAMES,
    "talea": TALEA16,
    "color": COLOR,
    "gong_degrees": GONG_DEG,
    "progression_pcs": CHORD_PCS_BY_BAR,
    "seed": SEED,
    "hz_seed": HZ_SEED,
    "phase1_midi": P1_MIDI,
    "perfect_midi": perfect_mid,
    "humanized_midi": human_mid,
    "grid_audit": grid_audit,
    "harmony_audit": harmony_audit,
    "hz_summary": hz,
    "phase1_offgrid": P1_OFFGRID,
}
with open(os.path.join(ANALYSIS_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, default=str)
print("DONE")