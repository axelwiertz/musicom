# -*- coding: utf-8 -*-
"""304-trap-bibd-suite -- Trap / Method 132 Balanced Incomplete Block Design
Composition (BIBDC), concrete layer, strophic form.

METHOD IDENTITY (132 BIBDC):
  The ensemble schedule IS the composition. A balanced incomplete block design
  BIBD(v=4, k=3, lambda=2, b=4, r=3) over the four pitched voices:
    * v = 4 points  = {Lead, Pluck, Pad, Bass}
    * b = 4 blocks  = the four strophic verses
    * k = 3 voices active per verse (one rotating tacet)
    * r = 3 verses per voice  (every voice rests exactly one verse)
    * lambda = 2  (every voice-pair co-occurs in exactly 2 verses)
  Blocks (active sets):
    Verse1 {Lead, Pluck, Pad}   (Bass tacet  -- atmospheric, no 808)
    Verse2 {Lead, Pluck, Bass}  (Pad tacet    -- 808 enters)
    Verse3 {Lead, Pad, Bass}    (Pluck tacet  -- fullest)
    Verse4 {Pluck, Pad, Bass}   (Lead tacet   -- outro texture)
  Pair-novelty (new pairs per block) = 3, 2, 1, 0 -> provable monotone
  decreasing tension curve (the method's signature property).

TWO-PHASE ARCHITECTURE:
  Phase 1: raw single-voice melodic walk (Kalimba), unquantized chromatic pitch
           + off-grid rhythm, no harmony, no schedule.
  Phase 2: musicom rules post-process:
            1. grid-lock every pitched voice to the 16th grid (078 rule)
            2. tiered snap (ScaleQuantizer root=E + classify_weight):
               strong beat -> bar chord tone, weak -> E-minor scale tone
            3. BIBD ensemble schedule (per-verse active voice sets)
            4. full trap texture (bell lead, music-box pluck, warm pad,
               808 synth-bass, half-time drum kit)
            5. zero-drift landmark + validate() on BOTH phases
            6. export_dual -> -perfect.mid + -humanized.mid

Engine only. mido used READ-ONLY in a separate verify step.

E natural minor {4,6,7,9,11,0,2}; i-VI-III-VII loop (Em-C-G-D), 140 BPM 4/4.
"""
import os
import json
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual
from workflows.musicom_workflow import form_to_sections
from sound.synthesis.scale_quantizer import (
    ScaleQuantizer, classify_weight, STRONG_GRID,
)
from workflows.pitch_audit import audit_voice

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    KALIMBA, MUSIC_BOX, WARM_PAD, SYNTH_BASS_1, DRUM_KIT,
)

SEED = 20261114
HZ_SEED = SEED * 13 + 304
FORM_SEED = SEED * 10 + 7

# ------------------------------------------------------------------ project
PROJ = "/opt/data/projects/Styles/Trap/304-trap-bibd-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- concept
BPM = 140
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120
GRID8 = 240

FORM = "strophic"
NAMES = ["Verse1", "Verse2", "Verse3", "Verse4"]
BARS_PER = [8, 8, 8, 8]
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS_PER)           # 32
SEC_BAR_OFFSET = []
acc = 0
for b in BARS_PER:
    SEC_BAR_OFFSET.append(acc)
    acc += b

# E natural minor
KEY = "E natural minor"
KEY_PCS = {4, 6, 7, 9, 11, 0, 2}
SCALE_ROOT = 52                  # E3
STRONG = STRONG_GRID.get("4/4", (0, 960))

# ------------------------------------------------------------------- harmony
# i - VI - III - VII  (Em - C - G - D), classic trap minor loop, 2x per verse.
CHORDS = {
    "i":   {"pcs": {4, 7, 11},  "root": 40, "name": "Em"},
    "VI":  {"pcs": {0, 4, 7},   "root": 36, "name": "C"},
    "III": {"pcs": {7, 11, 2},  "root": 43, "name": "G"},
    "VII": {"pcs": {2, 6, 9},   "root": 38, "name": "D"},
}
_VERSE_PROG = ["i", "VI", "III", "VII", "i", "VI", "III", "VII"]
BAR_PROG = _VERSE_PROG * N_SECTIONS
assert len(BAR_PROG) == N_BARS
CHORD_PCS_BY_BAR = {bar: sorted(CHORDS[BAR_PROG[bar]]["pcs"])
                    for bar in range(N_BARS)}
ROOT_BY_BAR = {bar: CHORDS[BAR_PROG[bar]]["root"] for bar in range(N_BARS)}

# =====================================================================
# METHOD 132 -- Balanced Incomplete Block Design (BIBD v=4,k=3,lambda=2)
# =====================================================================
# active pitched-voice sets per verse (block). Drums are a constant layer
# OUTSIDE the design (trap groove backbone), not a BIBD point.
BIBD_ACTIVE = {
    0: {"Lead", "Pluck", "Pad"},   # Bass tacet
    1: {"Lead", "Pluck", "Bass"},  # Pad tacet
    2: {"Lead", "Pad", "Bass"},    # Pluck tacet
    3: {"Pluck", "Pad", "Bass"},   # Lead tacet
}
PITCHED = ["Lead", "Pluck", "Pad", "Bass"]


def pair_novelty_curve(active_by_section):
    """new voice-pairs introduced per section -> provable tension curve."""
    seen = set()
    curve = []
    for s in range(N_SECTIONS):
        voices = sorted(active_by_section[s])
        new = 0
        for i in range(len(voices)):
            for j in range(i + 1, len(voices)):
                p = (voices[i], voices[j])
                if p not in seen:
                    seen.add(p)
                    new += 1
        curve.append(new)
    return curve


PAIR_NOVELTY = pair_novelty_curve(BIBD_ACTIVE)
print("BIBD pair-novelty curve (per verse):", PAIR_NOVELTY,
      "sum:", sum(PAIR_NOVELTY), "(== C(4,2)=6)")

# ------------------------------------------------------------------- registers
LEAD_LO, LEAD_HI = 55, 84
PLUCK_LO, PLUCK_HI = 70, 89
PAD_LO, PAD_HI = 52, 72
BASS_LO, BASS_HI = 33, 52

sq = ScaleQuantizer(root=SCALE_ROOT, scale="minor")


def chord_tones(bar, lo, hi):
    tones = set()
    for base in (36, 48, 60, 72, 84, 96):
        for pc in CHORD_PCS_BY_BAR[bar]:
            p = base + pc
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def scale_tones(lo, hi):
    return [p for p in range(lo, hi + 1) if p % 12 in KEY_PCS]


def sec_of_bar(bar):
    s = 0
    while s < N_SECTIONS - 1 and bar >= SEC_BAR_OFFSET[s] + BARS_PER[s]:
        s += 1
    return s


# ------------------------------------------------------------------- Phase-1 walk
def raw_lead_walk(span, seed, lo, hi):
    """Raw single-voice melodic walk: mostly conjunct, off-grid onset jitter,
    unquantized chromatic pitch. This is the raw material the BIBD schedules."""
    rng = np.random.default_rng(seed)
    events = []
    pitch = int((lo + hi) / 2)
    onset = 0.0
    while onset < span - 240:
        st = int(round(onset + rng.normal(0, 18)))
        st = max(0, min(st, span - GRID16))
        if rng.random() < 0.22:
            step = int(rng.integers(-7, 8))
        else:
            step = int(rng.integers(-2, 3))
        pitch = int(np.clip(pitch + step, lo, hi))
        dur = int(round(200 + rng.normal(0, 45)))
        en = min(st + dur, span - 1)
        if en <= st:
            en = st + 1
        vel = int(np.clip(82 + rng.normal(0, 10), 50, 112))
        events.append(MusicEvent(pitch=pitch, volume=vel,
                                 start_tick=st, end_tick=en))
        onset += rng.choice([120, 240, 360, 480, 600, 720])
    return events


# ------------------------------------------------------------ PHASE 1: raw
phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=KALIMBA.midi_program, channel=0)

P1_OFFGRID = 0
P1_MEAN = {}
P1_RAW = {}           # keep raw events for phase-2 lead reuse
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER[s])
    span = BARS_PER[s] * BAR
    evs = raw_lead_walk(span, SEED + s, LEAD_LO, LEAD_HI)
    if not any(e.pitch == 0 and e.end_tick == span for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1,
                              end_tick=span))
    P1_OFFGRID += sum(1 for e in evs if e.pitch != 0 and e.start_tick % GRID16 != 0)
    pitches = [e.pitch for e in evs if e.pitch != 0]
    P1_MEAN[name] = round(float(np.mean(pitches)), 2) if pitches else 0.0
    P1_RAW[s] = evs
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
if not ok1:
    raise RuntimeError("phase1 validate FAIL: " + msg1)
P1_MIDI = os.path.join(MIDI_DIR, "304-trap-bibd-suite-phase1.mid")
phase1.to_midi(P1_MIDI)
assert os.path.getsize(P1_MIDI) > 40
print("PHASE1 validate:", msg1, "| off-grid onsets:", P1_OFFGRID)
print("PHASE1 per-section mean pitch:", P1_MEAN)


# ------------------------------------------------------------ PHASE 2: rules
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead", KALIMBA.midi_program, 0),      # bell/pluck lead
    ("Pluck", MUSIC_BOX.midi_program, 1),   # music-box counter
    ("Pad", WARM_PAD.midi_program, 2),      # sustained chords
    ("Bass", SYNTH_BASS_1.midi_program, 3), # 808 sub
    ("Drums", 0, 9),                         # half-time trap kit
]
N_V = len(VOICES)
ROW = {name: i for i, (name, _, _) in enumerate(VOICES)}
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for i, name in enumerate(NAMES):
    phase2.add_section(name, bars=BARS_PER[i])


def landmark(events, span):
    out = []
    for e in events:
        if e.start_tick >= span:
            continue
        st = min(int(e.start_tick), span - 1)
        en = min(int(e.end_tick), span)
        if en <= st:
            en = st + 1
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=st, end_tick=en))
    out.sort(key=lambda e: (e.start_tick, 0 if e.pitch == 0 else 1))
    if not any(e.pitch == 0 and e.end_tick == span for e in out):
        out.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1,
                              end_tick=span))
    return out


def tiered_snap(raw_pitch, local_start, global_bar, lo, hi):
    w = classify_weight(local_start, STRONG, BAR)
    if w == "strong":
        tones = chord_tones(global_bar, lo=lo, hi=hi)
        p = sq.tiered_quantize(raw_pitch, weight="strong", chord_tones=tones)
    else:
        p = sq.quantize(raw_pitch)
    if p < lo or p > hi:
        cands = scale_tones(lo, hi)
        if cands:
            p = min(cands, key=lambda x: abs(x - p))
    return p


# ---- lead: quantized raw walk (transposed +12 in Verse3 for the peak) ------
LEAD_TRANS = {0: 0, 1: 0, 2: 12, 3: 0}   # Verse3 octave-up
for s, name in enumerate(NAMES):
    span = BARS_PER[s] * BAR
    if "Lead" not in BIBD_ACTIVE[s]:
        phase2.set_unit(ROW["Lead"], s, create_empty_unit(span))
        continue
    tr = LEAD_TRANS[s]
    out = []
    seen = {}
    for e in P1_RAW[s]:
        if e.pitch == 0:
            continue
        st = int(round(e.start_tick / GRID16) * GRID16)
        st = max(0, min(st, span - GRID16))
        global_bar = SEC_BAR_OFFSET[s] + min(st // BAR, BARS_PER[s] - 1)
        raw = e.pitch + tr
        p = tiered_snap(raw, st, global_bar, LEAD_LO + tr, LEAD_HI + tr)
        key = (st, p)
        if key in seen:
            if e.end_tick > seen[key].end_tick:
                seen[key] = MusicEvent(pitch=p, volume=max(e.volume, seen[key].volume),
                                       start_tick=st, end_tick=min(span, e.end_tick))
        else:
            seen[key] = MusicEvent(pitch=p, volume=e.volume, start_tick=st,
                                   end_tick=min(span, e.end_tick))
    for key in sorted(seen):
        out.append(seen[key])
    phase2.set_unit(ROW["Lead"], s, MusicUnit(events=landmark(out, span)))


# ---- pluck: syncopated 16th counterline (active V1,V2,V4) ------------------
def build_pluck(s):
    evs = []
    if "Pluck" not in BIBD_ACTIVE[s]:
        return evs
    prev = 79
    for b in range(BARS_PER[s]):
        bar = SEC_BAR_OFFSET[s] + b
        t0 = b * BAR
        tones = chord_tones(bar, PLUCK_LO, PLUCK_HI)
        for off in (360, 720, 1200, 1680):
            st = t0 + off
            p = min(tones, key=lambda t: abs(t - prev))
            evs.append(MusicEvent(pitch=p, volume=78, start_tick=st,
                                  end_tick=st + GRID16))
            prev = p
    return evs


# ---- pad: sustained triad (active V1,V3,V4) --------------------------------
def build_pad(s):
    evs = []
    if "Pad" not in BIBD_ACTIVE[s]:
        return evs
    for b in range(BARS_PER[s]):
        bar = SEC_BAR_OFFSET[s] + b
        t0 = b * BAR
        tones = chord_tones(bar, PAD_LO, PAD_HI)
        for k, p in enumerate(tones):
            evs.append(MusicEvent(pitch=p, volume=50 + 3 * k, start_tick=t0,
                                  end_tick=t0 + BAR - 60))
    return evs


# ---- bass: 808 sub (active V2,V3,V4) --------------------------------------
def build_bass(s):
    evs = []
    if "Bass" not in BIBD_ACTIVE[s]:
        return evs
    for b in range(BARS_PER[s]):
        bar = SEC_BAR_OFFSET[s] + b
        t0 = b * BAR
        root = ROOT_BY_BAR[bar]
        if root < BASS_LO:
            root = min(p for p in range(BASS_LO, BASS_HI + 1) if p % 12 == root % 12)
        oct_note = root + 12
        # sustained 808: root holds most of the bar, octave hit on the "and" of 2
        evs.append(MusicEvent(pitch=root, volume=96, start_tick=t0,
                              end_tick=t0 + int(BAR * 0.75)))
        evs.append(MusicEvent(pitch=oct_note, volume=82, start_tick=t0 + 720,
                              end_tick=t0 + 720 + GRID8))
    return evs


# ---- drums: half-time trap kit (constant, channel 9) -----------------------
KICK, SNARE, CLAP, HH_CL, HH_OP = 36, 38, 39, 42, 46


def build_drums(s):
    evs = []
    for b in range(BARS_PER[s]):
        t0 = b * BAR
        # kick on 1 + ghost kick before the snare (trap double-kick feel)
        evs.append(MusicEvent(pitch=KICK, volume=112, start_tick=t0,
                              end_tick=t0 + 90))
        evs.append(MusicEvent(pitch=KICK, volume=70, start_tick=t0 + 1560,
                              end_tick=t0 + 1560 + 60))
        # half-time snare on beat 3 + layered clap
        evs.append(MusicEvent(pitch=SNARE, volume=106, start_tick=t0 + 960,
                              end_tick=t0 + 960 + 80))
        evs.append(MusicEvent(pitch=CLAP, volume=92, start_tick=t0 + 960,
                              end_tick=t0 + 960 + 70))
        # rolling 16th closed hats, accent on off-8ths
        for e16 in range(16):
            st = t0 + e16 * GRID16
            v = 72 if e16 % 4 == 2 else 52
            evs.append(MusicEvent(pitch=HH_CL, volume=v, start_tick=st,
                                  end_tick=st + 50))
        # open hat on the "and" of 2 and 4
        for off in (720, 1680):
            evs.append(MusicEvent(pitch=HH_OP, volume=64, start_tick=t0 + off,
                                  end_tick=t0 + off + 60))
    if s == N_SECTIONS - 1:   # final crash on the last downbeat
        t0 = (BARS_PER[s] - 1) * BAR
        evs.append(MusicEvent(pitch=49, volume=90, start_tick=t0,
                              end_tick=t0 + 240))
    return evs


for s in range(N_SECTIONS):
    span = BARS_PER[s] * BAR
    phase2.set_unit(ROW["Pluck"], s, MusicUnit(events=landmark(build_pluck(s), span)))
    phase2.set_unit(ROW["Pad"], s, MusicUnit(events=landmark(build_pad(s), span)))
    phase2.set_unit(ROW["Bass"], s, MusicUnit(events=landmark(build_bass(s), span)))
    phase2.set_unit(ROW["Drums"], s, MusicUnit(events=landmark(build_drums(s), span)))

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
                          "start_tick": SEC_BAR_OFFSET[s] * BAR + e.start_tick,
                          "end_tick": SEC_BAR_OFFSET[s] * BAR + e.end_tick})
    return notes


grid_audit = {}
harmony_audit = {}
for name in PITCHED:
    row = ROW[name]
    notes = global_notes(row)
    onsets = [n["start_tick"] for n in notes]
    for grid_name, grid in (("16th", 120), ("8th", 240)):
        off = [o for o in onsets if o % grid != 0]
        grid_audit[f"{name}:{grid_name}"] = f"{len(off)}/{len(onsets)}"
    r = audit_voice(notes, sorted(KEY_PCS), chord_pcs_by_bar=CHORD_PCS_BY_BAR,
                    strong_grid=STRONG, bar_ticks=BAR, grid=GRID8)
    harmony_audit[name] = {
        "passes": r.passes, "audible": r.audible,
        "strong_ok": r.strong_ok, "weak_in_scale": r.weak_in_scale,
        "tagged": r.tagged_ornaments, "resolving": r.tagged_resolving,
        "non_resolving": r.tagged_non_resolving,
        "untagged_out_of_scale": r.untagged_out_of_scale,
        "strong_violations": r.strong_violations,
        "collisions": r.collisions,
    }
    print(f"AUDIT {name}: {r.summary()}")

for k, v in grid_audit.items():
    print("GRID", k, v)
assert all(r["passes"] for r in harmony_audit.values()), "harmony audit FAIL"
assert all(int(x.split("/")[0]) == 0 for k, x in grid_audit.items()
           if k.endswith(":16th")), "grid audit FAIL (16th must be 0 off-grid)"


# ------------------------------------------------------------------ export
perfect_mid = os.path.join(MIDI_DIR, "304-trap-bibd-suite-perfect.mid")
human_mid = os.path.join(MIDI_DIR, "304-trap-bibd-suite-humanized.mid")

hz_instruments = {
    "Lead": KALIMBA.humanize_dna,
    "Pluck": MUSIC_BOX.humanize_dna,
    "Pad": WARM_PAD.humanize_dna,
    "Bass": SYNTH_BASS_1.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
hz = export_dual(phase2, perfect_mid, human_mid,
                 style="trap", seed=HZ_SEED, bpm=BPM,
                 instruments=hz_instruments)
print("export_dual OK; hz summary:")
print(json.dumps(hz, indent=2, default=str))


# ------------------------------------------------------------------ provenance
prog_per_section = {
    NAMES[s]: [CHORDS[BAR_PROG[SEC_BAR_OFFSET[s] + b]]["name"]
               for b in range(BARS_PER[s])]
    for s in range(N_SECTIONS)
}
write_provenance(P1_MIDI, AI_ASSISTED,
                 "BIBDC (Method 132) -- raw melodic walk (phase 1)",
                 parameters={"phase": "1", "layer": "raw", "style": "trap",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM, "section_mean_pitch": P1_MEAN},
                 notes="phase1 raw draft: single-voice stochastic walk (Kalimba), "
                       "unquantized chromatic pitch + off-grid rhythm; no harmony, "
                       "no BIBD schedule yet.")
write_provenance(perfect_mid, AI_ASSISTED,
                 "BIBDC (Method 132) + musicom rules (phase 2, grid-locked)",
                 parameters={"phase": "2", "layer": "perfect", "style": "trap",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM, "progression": BAR_PROG,
                             "bibd_active": {str(k): sorted(v) for k, v in BIBD_ACTIVE.items()},
                             "pair_novelty": PAIR_NOVELTY},
                 notes="grid-locked concrete layer; off-grid onsets == 0; tiered "
                       "snap (strong->chord tone, weak->E-minor scale); BIBD "
                       "ensemble schedule v=4,k=3,lambda=2,b=4,r=3.")
write_provenance(human_mid, AI_ASSISTED,
                 "BIBDC (Method 132) + rules + humanize (phase 2, humanized)",
                 parameters={"phase": "2", "layer": "humanized", "style": "trap",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "humanize_profiles": {
                                 k: (v.get("profile") if isinstance(v, dict) else v)
                                 for k, v in hz.items()}},
                 notes="style-derived seeded humanization (trap profile + "
                       "per-instrument DNA).")


# ------------------------------------------------------------------ grid viz + manifest
gv = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, gv, ticks_per_character=120,
                         voice_names=[v[0] for v in VOICES], bpm=BPM,
                         mode="E minor / Trap BIBDC strophic")
print("grid viz written", gv)

manifest = {
    "project": "304-trap-bibd-suite",
    "genre": "Trap",
    "method": "132 Balanced Incomplete Block Design Composition (BIBDC)",
    "paradigm": "Rules-Based",
    "layer": "concrete",
    "form": FORM,
    "key": KEY,
    "key_pcs": sorted(KEY_PCS),
    "bpm": BPM,
    "bars": N_BARS,
    "sections": NAMES,
    "bars_per_section": BARS_PER,
    "progression": BAR_PROG,
    "progression_per_section": prog_per_section,
    "bibd": {"v": 4, "k": 3, "lambda": 2, "b": 4, "r": 3,
             "active_by_section": {str(k): sorted(v) for k, v in BIBD_ACTIVE.items()},
             "pair_novelty": PAIR_NOVELTY},
    "seed": SEED,
    "hz_seed": HZ_SEED,
    "form_seed": FORM_SEED,
    "phase1_midi": P1_MIDI,
    "perfect_midi": perfect_mid,
    "humanized_midi": human_mid,
    "phase1_offgrid": P1_OFFGRID,
    "phase1_mean_pitch": P1_MEAN,
    "grid_audit": grid_audit,
    "harmony_audit": harmony_audit,
    "hz_summary": hz,
}
with open(os.path.join(ANALYSIS_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, default=str)
print("DONE compose.")
