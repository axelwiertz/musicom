# -*- coding: utf-8 -*-
"""291-hiphop-ostinato-loop -- HipHop / Method 015 Ostinato Constraint Writing.

LAYER: concrete (Rules-Based).

Two-phase architecture:
  Phase 1: raw generative draft -- a single-voice 8th-note BASS ostinato with
           OFF-GRID fractional onset jitter and unquantized pitch drift around
           the chord roots. No harmony/pad/lead/drums. This IS the method's
           generative act (the ostinato cell).
  Phase 2: musicom rules post-process:
           1. GRID LOCK the ostinato to the 16th grid + dedup (078 rule).
           2. Chord-tone snap (root/fifth/octave) -> static lower-voice loop.
           3. Rhodes pad = whole-bar triad (harmony, chromatic-free).
           4. Lead = FOUR variation passes over the static ostinato (the
              "variations on top" that Method 015 prescribes): theme,
              diminution, register-shift + new contour, retrograde (sparse).
              Tiered snap: strong beats -> chord tone, weak -> scale tone,
              via sound.synthesis.scale_quantizer (tiered_quantize +
              classify_weight). Lead MAY carry NO ornament here (clean path).
           5. Boom-bap drum groove (kick/snare/hats) on the grid.
           6. Zero-drift landmark + validate() on BOTH phases.
           7. export_dual -> -perfect.mid + -humanized.mid.

Engine only. mido is used READ-ONLY in the separate verify step.
"""
import os
import json
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    FLUTE, SYNTH_BASS_1, RHODES, DRUM_KIT,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20261108
HZ_SEED = SEED * 7 + 1
rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------ project
PROJ = "/opt/data/projects/Styles/HipHop/291-hiphop-ostinato-loop"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- concept
BPM = 92
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120                     # 16th-note grid
GRID8 = 240                      # 8th-note grid
NAMES = ["A", "A", "B", "B"]     # form aabb
BARS_PER = 4
N_SECTIONS = 4
N_BARS = 16                      # 4 sections x 4 bars
SECTION_TICKS = BAR * BARS_PER   # 7680
TOTAL_TICKS = N_SECTIONS * SECTION_TICKS

# A natural minor: A B C D E F G
KEY = "A natural minor"
KEY_PCS = {0, 2, 4, 5, 7, 9, 11}
SCALE_ROOT = 57                  # A3

LEAD_LO, LEAD_HI = 60, 86        # flute range
BASS_LO, BASS_HI = 36, 60        # synth-bass register
PAD_LO, PAD_HI = 54, 72          # rhodes pad register

# ------------------------------------------------------------------- harmony
# A natural-minor diatonic triads. DEGREES[name] = (quality, root_midi).
#   m = (0,3,7), M = (0,4,7). All chord tones subset of A-minor scale
#   {A=9,B=11,C=0,D=2,E=4,F=5,G=7} -> no chromatic anywhere.
DEGREES = {
    "i":   ("m", 57),   # Am
    "VI":  ("M", 53),   # F
    "III": ("M", 48),   # C
    "VII": ("M", 55),   # G
    "iv":  ("m", 50),   # Dm
    "v":   ("m", 52),   # Em
}
INTERVALS = {"m": (0, 3, 7), "M": (0, 4, 7)}

SECTION_PROG = [
    ["i", "VI", "III", "VII"],   # 0 A
    ["i", "VI", "III", "VII"],   # 1 A
    ["iv", "v", "VI", "VII"],    # 2 B
    ["iv", "v", "VI", "VII"],    # 3 B
]
PROG = [deg for sec in SECTION_PROG for deg in sec]
assert len(PROG) == N_BARS, (len(PROG), N_BARS)


def chord_qual(root):
    for _name, (q, r) in DEGREES.items():
        if r == root:
            return q
    raise KeyError(root)


def chord_tones(root, lo=36, hi=88):
    tones = set()
    for oct_shift in (-12, 0, 12, 24):
        for i in INTERVALS[chord_qual(root)]:
            p = root + i + oct_shift
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def chord_pcs(root):
    return set((root + i) % 12 for i in INTERVALS[chord_qual(root)])


def PROG_ROOT(bar):
    return DEGREES[PROG[bar]][1]


def bass_root(root):
    r = root
    while r > 48:
        r -= 12
    while r < 36:
        r += 12
    return r


def root_to_lead_center(root):
    c = root
    while c < 60:
        c += 12
    while c > 74:
        c -= 12
    return c


def global_bar(sec, local_tick):
    return int(sec) * BARS_PER + (int(local_tick) // BAR)


# ------------------------------------------------------------------- phase 1
def raw_ostinato(seed, center_root, duration_ticks):
    """Single-voice 8th-note ostinato: OFF-GRID jitter + unquantized pitch drift.

    Rhythm is a fixed 8-note (8th) ostinato cell repeated across the span;
    pitch drifts around the chord root (+/- fifth/octave) with small noise.
    """
    r = np.random.default_rng(seed)
    events = []
    tick = 0.0
    step = 240.0                       # 8th note
    offsets = [0, 12, 0, 7, 0, 12, 7, 12]   # root/octave/fifth contour
    idx = 0
    while tick < duration_ticks:
        jitter = r.normal(0.0, 0.16) * step          # off-grid onset jitter
        st = tick + jitter
        drift = int(r.normal(0.0, 1.4))               # unquantized pitch drift
        pitch = center_root + offsets[idx % len(offsets)] + drift
        pitch = int(np.clip(pitch, BASS_LO, BASS_HI))
        dur = step * (0.65 + 0.35 * r.random())
        en = int(round(st + dur))
        st = int(round(st))
        if en <= st:
            en = st + 1
        if en > duration_ticks:
            en = duration_ticks
        if 0 <= st < duration_ticks:
            vel = int(np.clip(72 + 18 * r.random(), 58, 96))
            events.append(MusicEvent(pitch=pitch, volume=vel,
                                     start_tick=st, end_tick=en))
        tick += step
        idx += 1
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("OstinatoRaw", program=SYNTH_BASS_1.midi_program, channel=0)

P1_RAW = {}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    # centre on the section's first chord root (section revolves around i or iv)
    center = root_to_lead_center(PROG_ROOT(s * BARS_PER))
    # keep it in bass register
    center = bass_root(center + 12) if center + 12 <= BASS_HI else bass_root(center)
    evs = raw_ostinato(SEED + s, center, SECTION_TICKS)
    P1_RAW[s] = list(evs)
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
if not ok1:
    raise RuntimeError("phase1 validate FAIL: " + msg1)
P1_MIDI = os.path.join(MIDI_DIR, "291-hiphop-ostinato-loop-phase1.mid")
phase1.to_midi(P1_MIDI)
print("PHASE1 validate:", msg1)
print("phase1 written", P1_MIDI)


# ------------------------------------------------------------------- phase 2
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead", FLUTE.midi_program, 0),           # 0 flute (variations on top)
    ("Bass", SYNTH_BASS_1.midi_program, 1),    # 1 808-style synth bass (ostinato)
    ("Pad", RHODES.midi_program, 2),           # 2 rhodes (dusty e-piano chords)
    ("Drums", 0, 9),                           # 3 boom-bap kit
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


def quantize_to_chord(pitch, tones):
    return min(tones, key=lambda c: (abs(c - pitch), c))


# tiered pitch discipline (engine)
from sound.synthesis.scale_quantizer import (  # noqa: E402
    ScaleQuantizer, classify_weight, STRONG_GRID,
)
sq = ScaleQuantizer(root=SCALE_ROOT, scale="minor")
STRONG = STRONG_GRID.get("4/4", (0, 960))

# ---- bass: grid-locked static ostinato (root/fifth/octave, chords) --------
BASS_OFFSETS = [0, 12, 0, 7, 0, 12, 7, 12]       # 8th-note contour (static)
for s in range(N_SECTIONS):
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        root = bass_root(PROG_ROOT(s * BARS_PER + bar))
        for k in range(8):
            st = t0 + k * GRID8
            pitch = root + BASS_OFFSETS[k]
            pitch = int(np.clip(pitch, BASS_LO, BASS_HI))
            vel = 82 if k % 2 == 0 else 70
            evs.append(MusicEvent(pitch=pitch, volume=vel,
                                  start_tick=st, end_tick=st + 200))
        # 16th pickup into the next bar
        if bar < BARS_PER - 1:
            evs.append(MusicEvent(pitch=root, volume=70,
                                  start_tick=t0 + BAR - GRID16,
                                  end_tick=t0 + BAR - 20))
    phase2.set_unit(1, s, MusicUnit(events=landmark(evs)))

# ---- pad: whole-bar sustained Rhodes triad (chromatic-free harmony) -------
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = PROG_ROOT(bar)
    iv = INTERVALS[chord_qual(root)]
    base = root + 12
    t0 = b * BAR
    e = []
    for k, i in enumerate(iv):
        p = base + i
        if PAD_LO <= p <= PAD_HI:
            e.append(MusicEvent(pitch=p, volume=52 + 4 * k,
                                start_tick=t0, end_tick=t0 + BAR - 90))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))


# ---- lead: four variation passes over the static ostinato ----------------
# (1) A(0): theme (half-note spacing, 8 onsets)
# (2) A(1): diminution (quarter-note spacing, 16 onsets) of the theme
# (3) B(2): register shift +12, new contour (16 onsets)
# (4) B(3): retrograde of theme, sparse (8 onsets)
THEME = [0, 2, -2, 3, -1, 2, -3, 1]


def lead_pass(s):
    register = 0
    if s == 0:
        steps = THEME
        density = 8
    elif s == 1:
        steps = THEME * 2              # diminution: 2x the onsets
        density = 16
    elif s == 2:
        steps = [0, 3, 2, -1, 4, -2, 1, -3, 0, 2, -4, 3, 1, -1, 2, -2]
        density = 16
        register = 12
    else:
        steps = list(reversed(THEME))  # retrograde
        density = 8

    center = root_to_lead_center(PROG_ROOT(s * BARS_PER + 1)) + register
    center = int(np.clip(center, LEAD_LO, LEAD_HI))
    spacing = SECTION_TICKS / float(density)
    evs = []
    cur = float(center)
    for i in range(density):
        st = int(round(i * spacing / GRID8) * GRID8)
        if st >= SECTION_TICKS:
            break
        cur += steps[i % len(steps)] * 2
        cur = float(np.clip(cur, LEAD_LO, LEAD_HI))
        bar = global_bar(s, st)
        if bar >= N_BARS:
            bar = N_BARS - 1
        tones = chord_tones(PROG_ROOT(bar), lo=LEAD_LO, hi=LEAD_HI)
        w = classify_weight(st, STRONG, BAR)
        pitch = sq.tiered_quantize(cur, weight=w, chord_tones=tones)
        en = min(SECTION_TICKS, st + int(spacing * 0.8))
        evs.append(MusicEvent(pitch=pitch, volume=74, start_tick=st, end_tick=en))
    return evs


LEAD_EVENTS = {}
for s in range(N_SECTIONS):
    LEAD_EVENTS[s] = lead_pass(s)
    phase2.set_unit(0, s, MusicUnit(events=landmark(LEAD_EVENTS[s])))

# ---- drums: boom-bap groove ----------------------------------------------
DRUM_PLAN = {
    0: dict(hat=50, kick=86, snare=78, kick16=False, hat16=False),
    1: dict(hat=56, kick=90, snare=82, kick16=True,  hat16=False),
    2: dict(hat=54, kick=88, snare=80, kick16=True,  hat16=True),
    3: dict(hat=44, kick=82, snare=74, kick16=False, hat16=False),
}
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        hat_step = GRID16 if plan["hat16"] else GRID8
        for k in range(0, BAR, hat_step):
            evs.append(MusicEvent(pitch=KIT["hat_closed"], volume=plan["hat"],
                                  start_tick=t0 + k, end_tick=t0 + k + 50))
        kick_slots = [0, 960]
        if plan["kick16"]:
            kick_slots += [720, 1440]
        for kb in kick_slots:
            evs.append(MusicEvent(pitch=KIT["kick"], volume=plan["kick"],
                                  start_tick=t0 + kb, end_tick=t0 + kb + 110))
        for sb in (480, 1440):
            evs.append(MusicEvent(pitch=KIT["snare"], volume=plan["snare"],
                                  start_tick=t0 + sb, end_tick=t0 + sb + 100))
    phase2.set_unit(3, s, MusicUnit(events=landmark(evs)))

# finalize pad cells with landmark
for s in range(N_SECTIONS):
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    phase2.set_unit(2, s, MusicUnit(events=landmark(events)))

ok2, msg2 = phase2.validate()
if not ok2:
    raise RuntimeError("phase2 validate FAIL: " + msg2)
print("PHASE2 validate:", msg2)


# ---- grid + harmony audit (perfect, pre-humanize) ------------------------
def global_notes(row):
    notes = []
    for s in range(N_SECTIONS):
        unit = phase2.matrix.get_unit((row, s))
        if unit is None:
            continue
        for e in unit.events:
            if e.pitch == 0:
                continue
            notes.append({"pitch": e.pitch, "start_tick": s * SECTION_TICKS + e.start_tick})
    return notes


from workflows.pitch_audit import audit_voice  # noqa: E402

CHORD_PCS_BY_BAR = {bar: chord_pcs(PROG_ROOT(bar)) for bar in range(N_BARS)}
PITCHED = [(0, "Lead"), (1, "Bass"), (2, "Pad")]
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


# ------------------------------------------------------------------ export
perfect_mid = os.path.join(MIDI_DIR, "291-hiphop-ostinato-loop-perfect.mid")
human_mid = os.path.join(MIDI_DIR, "291-hiphop-ostinato-loop-humanized.mid")

hz_instruments = {
    "Lead": FLUTE.humanize_dna,
    "Bass": SYNTH_BASS_1.humanize_dna,
    "Pad": RHODES.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
hz = export_dual(phase2, perfect_mid, human_mid,
                 style="hiphop", seed=HZ_SEED, bpm=BPM, instruments=hz_instruments)
print("export_dual OK; hz summary:")
print(json.dumps(hz, indent=2, default=str))


# ------------------------------------------------------------------ provenance
write_provenance(P1_MIDI, AI_ASSISTED,
                 "Ostinato Constraint Writing (Method 015)",
                 parameters={"phase": "1", "layer": "raw", "style": "hiphop",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "sections": N_SECTIONS, "bars": N_BARS},
                 notes="phase1 raw draft: single-voice 8th-note bass ostinato, "
                       "OFF-GRID fractional onset jitter + unquantized pitch "
                       "drift; no harmony/pad/lead/drums.")
write_provenance(perfect_mid, AI_ASSISTED,
                 "Ostinato 015 + musicom rules (phase 2, grid-locked)",
                 parameters={"phase": "2", "layer": "perfect", "style": "hiphop",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": "aabb",
                             "variation": ["theme", "diminution",
                                           "register-shift", "retrograde",
                                           "new-contour"]},
                 notes="grid-locked concrete layer; off-grid onsets == 0; "
                       "static bass ostinato + 4 lead variation passes on top.")
write_provenance(human_mid, AI_ASSISTED,
                 "Ostinato 015 + musicom rules + humanize (phase 2, humanized)",
                 parameters={"phase": "2", "layer": "humanized", "style": "hiphop",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "humanize_profiles": {
                                 k: (v.get("profile") if isinstance(v, dict) else v)
                                 for k, v in hz.items()}},
                 notes="style-derived seeded humanization (hiphop profile + "
                       "per-instrument DNA).")


# ------------------------------------------------------------------ grid viz + manifest
gv = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, gv, ticks_per_character=120)
print("grid viz written", gv)

manifest = {
    "project": "291-hiphop-ostinato-loop",
    "genre": "HipHop",
    "method": "015 Ostinato Constraint Writing",
    "layer": "concrete",
    "form": "aabb",
    "key": KEY,
    "key_pcs": sorted(KEY_PCS),
    "bpm": BPM,
    "bars": N_BARS,
    "sections": NAMES,
    "progression": PROG,
    "seed": SEED,
    "hz_seed": HZ_SEED,
    "phase1_midi": P1_MIDI,
    "perfect_midi": perfect_mid,
    "humanized_midi": human_mid,
    "grid_audit": grid_audit,
    "harmony_audit": harmony_audit,
    "hz_summary": hz,
}
with open(os.path.join(ANALYSIS_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, default=str)
print("DONE")