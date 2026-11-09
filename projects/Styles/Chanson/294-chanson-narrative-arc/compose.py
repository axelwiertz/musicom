# -*- coding: utf-8 -*-
"""294-chanson-narrative-arc -- Chanson / Method 007 Narrative Arc Register Planning.

LAYER: concrete (Rules-Based, grid-locked, moderate registral gravity).

Two-phase architecture:
  Phase 1: raw generative draft -- a single-voice melodic stream that maps a
           STORY ARC to REGISTER. Each of the 4 strophic verses carries its
           own register center (V1 exposition LOW -> V2 rising -> V3 climax
           HIGH -> V4 denouement FALLING), and within each verse the contour
           rises to a local climax (~62% through) then falls. Onsets carry
           OFF-GRID jitter + pitch carries unquantized drift. No harmony /
           counterline / bass / pad. This IS the method's generative act
           (narrative arc -> register boundaries).

  Phase 2: musicom rules post-process:
           1. GRID LOCK the lead to the 16th/8th grid (078 rule).
           2. Tiered snap (engine ScaleQuantizer + classify_weight): strong
              beats -> bar's chord tone, weak -> F-major scale tone.
           3. Counterline (clarinet) = off-beat scale-step interlock.
           4. Accordion pad = sustained triad per bar (harmony, chromatic-free).
           5. Double bass = root (beat 1) + fifth (beat 3) per bar.
           6. Zero-drift landmark + validate() on BOTH phases.
           7. export_dual -> -perfect.mid + -humanized.mid.

Engine only. mido is used READ-ONLY in the separate verify step.

F major: pitch classes {5,7,9,10,0,2,4} = F G A Bb C D E.
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
    VIOLIN, CLARINET, ACCORDION, DOUBLE_BASS,
)

SEED = 20261109
HZ_SEED = SEED * 13 + 294
rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------ project
PROJ = "/opt/data/projects/Styles/Chanson/294-chanson-narrative-arc"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- concept
BPM = 72
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120                     # 16th-note grid
GRID8 = 240                      # 8th-note grid
NAMES = ["Verse1", "Verse2", "Verse3", "Verse4"]   # strophic form
BARS_PER = 8
N_SECTIONS = 4
N_BARS = 32                      # 4 verses x 8 bars
SECTION_TICKS = BAR * BARS_PER   # 15360
TOTAL_TICKS = N_SECTIONS * SECTION_TICKS

# F major
KEY = "F major"
KEY_PCS = {5, 7, 9, 10, 0, 2, 4}
SCALE_ROOT = 53                  # F3
PCS = [5, 7, 9, 10, 0, 2, 4]     # scale degree 0..6 -> pitch class

# ------------------------------------------------------------------- method
# Narrative arc register plan (Method 007): the story arc maps to REGISTER.
# Verse-level register centers rise to a climax in V3, then fall in V4.
REGISTER_CENTER = [67, 72, 77, 69]   # per verse
REGISTER_WIDTH = [7, 7, 7, 7]        # half-range per verse

# voice registers (from instrument sweet spots)
LEAD_LO, LEAD_HI = 60, 84        # violin lead
COUNTER_LO, COUNTER_HI = 62, 84  # clarinet counterline
PAD_LO, PAD_HI = 55, 79          # accordion pad
BASS_LO, BASS_HI = 34, 50        # double bass roots


def degree_pcs(d0):
    """Triad pitch classes for a 0-indexed scale degree."""
    return sorted({PCS[d0 % 7], PCS[(d0 + 2) % 7], PCS[(d0 + 4) % 7]})


def chord_pcs(deg1):
    """Triad pitch classes for a 1-indexed degree (1=I .. 7=vii)."""
    return degree_pcs((deg1 - 1) % 7)


# strophic verse progression (degrees 1..7): I vi ii V I vi IV V (half cadence),
# final verse resolves to I. 32 bars total.
VERSE_PROG = [1, 6, 2, 5, 1, 6, 4, 5]
VERSE_PROG_END = [1, 6, 2, 5, 1, 6, 4, 1]
PROG_DEG = []
for v in range(N_SECTIONS):
    PROG_DEG += (VERSE_PROG_END if v == N_SECTIONS - 1 else VERSE_PROG)
assert len(PROG_DEG) == N_BARS

CHORD_PCS_BY_BAR = {bar: chord_pcs(PROG_DEG[bar]) for bar in range(N_BARS)}

ROOT_MIDI = {1: 41, 6: 38, 2: 43, 5: 36, 4: 46}   # F2 D2 G2 C2 Bb2


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


def global_bar(sec, local_tick):
    return int(sec) * BARS_PER + (int(local_tick) // BAR)


# ------------------------------------------------------------------- phase 1
def raw_narrative_arc(seed, span_ticks, center, width):
    """Single-voice narrative-arc stream: register rises to a local climax
    (~62% through the verse) then falls; off-grid onset jitter + unquantized
    pitch drift. NO scale/chord enforcement -- raw generative draft."""
    r = np.random.default_rng(seed)
    events = []
    onset = 0.0
    step = GRID8                    # 8th-note base spacing
    n = int(span_ticks // step)
    for i in range(n):
        frac = i / max(1.0, n - 1)
        # intra-verse narrative arc: rise to climax at 0.62, then fall
        if frac <= 0.62:
            arc = frac / 0.62
        else:
            arc = 1.0 - (frac - 0.62) / 0.38
        pitch_float = center - width + 2.0 * width * arc + r.normal(0, 1.3)
        st = int(round(onset + r.normal(0, 0.16) * GRID16))
        pitch = int(round(np.clip(pitch_float, center - width, center + width)))
        dur = int(round(step * (0.65 + 0.45 * r.random())))
        en = st + dur
        if en <= st:
            en = st + 1
        if en > span_ticks:
            en = span_ticks
        if 0 <= st < span_ticks:
            vel = int(np.clip(72 + 16 * r.random(), 55, 100))
            events.append(MusicEvent(pitch=pitch, volume=vel,
                                     start_tick=st, end_tick=en))
        onset += step + r.normal(0, 20)
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("NarrativeRaw", program=VIOLIN.midi_program, channel=0)

P1_OFFGRID = 0
P1_MEAN = {}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_narrative_arc(SEED + s, SECTION_TICKS,
                            REGISTER_CENTER[s], REGISTER_WIDTH[s])
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    P1_OFFGRID += sum(1 for e in evs if e.pitch != 0 and e.start_tick % GRID16 != 0)
    pitches = [e.pitch for e in evs if e.pitch != 0]
    P1_MEAN[name] = round(float(np.mean(pitches)), 2) if pitches else 0.0
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
if not ok1:
    raise RuntimeError("phase1 validate FAIL: " + msg1)
P1_MIDI = os.path.join(MIDI_DIR, "294-chanson-narrative-arc-phase1.mid")
phase1.to_midi(P1_MIDI)
print("PHASE1 validate:", msg1, "| off-grid onsets:", P1_OFFGRID)
print("PHASE1 per-verse mean pitch:", P1_MEAN)
print("phase1 written", P1_MIDI)


# ------------------------------------------------------------------- phase 2
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead", VIOLIN.midi_program, 0),        # narrative-arc melody
    ("Counter", CLARINET.midi_program, 1),   # off-beat counterline
    ("Accordion", ACCORDION.midi_program, 2),  # sustained triad pad
    ("Bass", DOUBLE_BASS.midi_program, 3),   # root + fifth
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
sq = ScaleQuantizer(root=SCALE_ROOT, scale="major")
STRONG = STRONG_GRID.get("4/4", (0, 960))


def snap(e, bar, lo, hi):
    w = classify_weight(e.start_tick, STRONG, BAR)
    if w == "strong":
        tones = chord_tones(bar, lo=lo, hi=hi)
        return sq.tiered_quantize(e.pitch, weight="strong", chord_tones=tones)
    p = sq.quantize(e.pitch)
    if p < lo or p > hi:
        cands = scale_tones(lo, hi)
        if cands:
            p = min(cands, key=lambda x: abs(x - p))
    return p


# ---- lead: grid-locked narrative-arc melody, tiered snap ------------------
for s in range(N_SECTIONS):
    raw = raw_narrative_arc(SEED + s, SECTION_TICKS,
                            REGISTER_CENTER[s], REGISTER_WIDTH[s])
    raw = grid_lock_dedup(raw)
    evs = []
    for e in raw:
        if e.pitch == 0:
            continue
        bar = global_bar(s, e.start_tick)
        pitch = snap(e, bar, LEAD_LO, LEAD_HI)
        evs.append(MusicEvent(pitch=pitch, volume=e.volume,
                              start_tick=e.start_tick, end_tick=e.end_tick))
    phase2.set_unit(0, s, MusicUnit(events=landmark(evs)))

# ---- counter: off-beat clarinet counterline (weak -> scale only) ----------
for s in range(N_SECTIONS):
    r = np.random.default_rng(SEED + 1000 + s)
    evs = []
    cur = 65
    for bar in range(BARS_PER):
        gb = global_bar(s, bar * BAR)
        for k, off in enumerate((240, 720, 1200, 1680)):
            st = bar * BAR + off
            step = int(r.choice([-2, -1, -1, 1, 1, 2]))
            cand = cur + step
            if cand % 12 in KEY_PCS and COUNTER_LO <= cand <= COUNTER_HI:
                cur = cand
            else:
                cands = scale_tones(COUNTER_LO, COUNTER_HI)
                cur = min(cands, key=lambda x: abs(x - cand))
            evs.append(MusicEvent(pitch=cur, volume=58 + 8 * int(k % 2),
                                  start_tick=st, end_tick=st + 200))
    phase2.set_unit(1, s, MusicUnit(events=landmark(evs)))

# ---- accordion: sustained triad per bar -----------------------------------
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    t0 = b * BAR
    tones = chord_tones(bar, lo=PAD_LO, hi=PAD_HI)
    e = [MusicEvent(pitch=p, volume=50 + 3 * k,
                    start_tick=t0, end_tick=t0 + BAR - 80)
         for k, p in enumerate(tones)]
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# ---- bass: root (beat 1) + fifth (beat 3) per bar -------------------------
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    t0 = b * BAR
    deg = PROG_DEG[bar]
    root = ROOT_MIDI[deg]
    fifth = root + 7
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.append(MusicEvent(pitch=root, volume=88, start_tick=t0,
                             end_tick=t0 + int(BAR * 0.45)))
    events.append(MusicEvent(pitch=fifth, volume=80, start_tick=t0 + 960,
                             end_tick=t0 + 960 + int(BAR * 0.45)))
    phase2.set_unit(3, s, MusicUnit(events=events))

# finalize accordion + bass cells with landmark
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

PITCHED = [(0, "Lead"), (1, "Counter"), (2, "Accordion"), (3, "Bass")]
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
assert all(int(x.split("/")[0]) == 0 for k, x in grid_audit.items()
           if k.endswith(":16th")), "grid audit FAIL (16th must be 0 off-grid)"


# ------------------------------------------------------------------ export
perfect_mid = os.path.join(MIDI_DIR, "294-chanson-narrative-arc-perfect.mid")
human_mid = os.path.join(MIDI_DIR, "294-chanson-narrative-arc-humanized.mid")

hz_instruments = {
    "Lead": VIOLIN.humanize_dna,
    "Counter": CLARINET.humanize_dna,
    "Accordion": ACCORDION.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
}
hz = export_dual(phase2, perfect_mid, human_mid,
                 style="chanson", seed=HZ_SEED, bpm=BPM,
                 instruments=hz_instruments)
print("export_dual OK; hz summary:")
print(json.dumps(hz, indent=2, default=str))


# ------------------------------------------------------------------ provenance
write_provenance(P1_MIDI, AI_ASSISTED,
                 "Narrative Arc Register Planning (Method 007)",
                 parameters={"phase": "1", "layer": "raw", "style": "chanson",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": "strophic",
                             "register_center": REGISTER_CENTER,
                             "register_width": REGISTER_WIDTH,
                             "verse_mean_pitch": P1_MEAN},
                 notes="phase1 raw draft: single-voice narrative-arc stream; "
                       "register rises V1->V3 (climax) then falls V4; "
                       "off-grid onset jitter + unquantized pitch drift; "
                       "no harmony/counter/bass/pad.")
write_provenance(perfect_mid, AI_ASSISTED,
                 "Narrative Arc Register Planning 007 + musicom rules (phase 2, grid-locked)",
                 parameters={"phase": "2", "layer": "perfect", "style": "chanson",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": "strophic",
                             "progression": PROG_DEG,
                             "register_center": REGISTER_CENTER},
                 notes="grid-locked concrete layer; off-grid onsets == 0; "
                       "tiered snap (strong->chord tone, weak->F-major scale).")
write_provenance(human_mid, AI_ASSISTED,
                 "Narrative Arc Register Planning 007 + rules + humanize (phase 2, humanized)",
                 parameters={"phase": "2", "layer": "humanized", "style": "chanson",
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
    "project": "294-chanson-narrative-arc",
    "genre": "Chanson",
    "method": "007 Narrative Arc Register Planning",
    "layer": "concrete",
    "form": "strophic",
    "key": KEY,
    "key_pcs": sorted(KEY_PCS),
    "bpm": BPM,
    "bars": N_BARS,
    "sections": NAMES,
    "progression": PROG_DEG,
    "progression_pcs": CHORD_PCS_BY_BAR,
    "register_center": REGISTER_CENTER,
    "register_width": REGISTER_WIDTH,
    "verse_mean_pitch_phase1": P1_MEAN,
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
