# -*- coding: utf-8 -*-
"""302-techno-tendency-mask -- Techno / Method 023 Tendency Masking Stochastic
Bounds (TM-SB), concrete layer.

Stochastic, concrete layer. The generative core: a stochastic pitch walk whose
every step is BOUNDED by a dynamic tendency mask -- a per-section lower/upper
frequency envelope that opens (filter-style) across a section. The mask is the
musical idea: Intro narrows->opens, Break collapses to a narrow mid band
(breakdown), Drop throws the band wide open (peak energy), Outro closes it back
down. The raw walk lives INSIDE that band.

Two-phase architecture:
  Phase 1: raw generative draft. A single voice (saw lead) walks stochastically
           with its pitch clipped to the tendency mask [lo(t), hi(t)] at every
           step. Off-grid onset jitter + unquantized chromatic pitch. No harmony.
  Phase 2: musicom rules post-process:
            1. grid-lock the lead to the 8th grid (078 rule).
            2. tiered snap (ScaleQuantizer root=A + classify_weight):
               strong beat -> bar's chord tone, weak -> A-minor scale tone.
            3. texture: driving synth-bass (8th/16th pump), breakdown pad,
               offbeat rave stab (synth brass), 4-on-floor techno kit.
            4. zero-drift landmark + validate() on BOTH phases.
            5. export_dual -> -perfect.mid + -humanized.mid.

Engine only. mido used READ-ONLY in a separate verify step.

A natural minor: pitch classes {0,2,4,5,7,9,11} = A B C D E F G.
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
from workflows.musicom_workflow import pick_form, form_to_sections
from sound.synthesis.scale_quantizer import (
    ScaleQuantizer, classify_weight, STRONG_GRID,
)
from workflows.pitch_audit import audit_voice

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    SINGING_SAW, SYNTH_BASS_1, SYNTH_PAD, SYNTH_BRASS_1, DRUM_KIT,
)

SEED = 20261113
HZ_SEED = SEED * 13 + 302
FORM_SEED = SEED * 10 + 7

# ------------------------------------------------------------------ project
PROJ = "/opt/data/projects/Styles/Techno/302-techno-tendency-mask"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- concept
BPM = 128
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120
GRID8 = 240

_form = pick_form("techno", rng=np.random.default_rng(FORM_SEED))
while _form in ("loop", "loop4", "loop16"):
    _form = pick_form("techno", rng=np.random.default_rng(FORM_SEED + 1))
FORM = _form
NAMES, BARS_PER = form_to_sections(FORM)
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS_PER)

SEC_BAR_OFFSET = []
acc = 0
for b in BARS_PER:
    SEC_BAR_OFFSET.append(acc)
    acc += b

# A natural minor
KEY = "A natural minor"
KEY_PCS = {0, 2, 4, 5, 7, 9, 11}
TONIC = 57                      # A3
SCALE_ROOT = 57

# ------------------------------------------------------------------- harmony
# i - VI - VII  (Am - F - G): minimal techno lift. Pedal on Am, VI->VII only
# in the Drop's second half (the "filter open" harmonic moment).
CHORDS = {
    "i":   {"pcs": {9, 0, 4},   "root": 45, "name": "Am"},
    "VI":  {"pcs": {5, 9, 0},   "root": 41, "name": "F"},
    "VII": {"pcs": {7, 11, 2},  "root": 43, "name": "G"},
}
_SECTION_PROG = {
    "Intro": ["i", "i", "i", "i"],
    "Break": ["i"] * 8,
    "Drop":  ["i", "i", "VI", "VII", "i", "i", "VI", "VII"],
    "Outro": ["i", "i", "i", "i"],
}
BAR_PROG = []
for s, name in enumerate(NAMES):
    BAR_PROG += _SECTION_PROG.get(name, ["i"] * BARS_PER[s])
assert len(BAR_PROG) == N_BARS, (len(BAR_PROG), N_BARS)

CHORD_PCS_BY_BAR = {bar: sorted(CHORDS[BAR_PROG[bar]]["pcs"])
                    for bar in range(N_BARS)}
ROOT_BY_BAR = {bar: CHORDS[BAR_PROG[bar]]["root"] for bar in range(N_BARS)}

# =====================================================================
# METHOD 023 -- Tendency Masking Stochastic Bounds
# =====================================================================
# Each section carries a tendency mask = a (lo_start, lo_end, hi_start, hi_end)
# tuple. At progress p = t/span the allowed band is
#     lo(t) = lo0 + (lo1 - lo0) * p
#     hi(t) = hi0 + (hi1 - hi0) * p
# and the stochastic walk is clipped into [lo(t), hi(t)] at every step.
# "Opening" = band widens over the section; "closing" = band collapses.
# =====================================================================
MASK = {
    "Intro": (45, 43, 60, 74),   # opening (lo dips, hi rises)
    "Break": (48, 50, 58, 66),   # narrow mid band, subtle lift
    "Drop":  (57, 62, 84, 96),   # wide open, still rising (peak energy)
    "Outro": (62, 55, 96, 68),   # closing (lo rises, hi falls -> collapse)
}
MASK_WIDTH = {n: (int(MASK[n][3] - MASK[n][0]),
                  int(MASK[n][2] - MASK[n][1])) for n in MASK}
print("TENDENCY MASK per section (band width start->end):", MASK_WIDTH)

# ------------------------------------------------------------------- registers
LEAD_LO, LEAD_HI = 57, 96
BASS_LO, BASS_HI = 30, 55
PAD_LO, PAD_HI = 45, 69
STAB_LO, STAB_HI = 52, 76

sq = ScaleQuantizer(root=SCALE_ROOT, scale="minor")
STRONG = STRONG_GRID.get("4/4", (0, 960))


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
def raw_tendency_walk(span, mask, seed):
    """Single-voice raw draft: stochastic walk clipped into the tendency mask.

    - step = small random walk (mostly conjunct), rare bigger leap
    - pitch clipped to [lo(t), hi(t)] = the dynamic mask band at that moment
    - off-grid onset jitter + unquantized chromatic pitch (by design).
    """
    rng = np.random.default_rng(seed)
    lo0, lo1, hi0, hi1 = mask
    n_slots = max(1, int(span // GRID8))
    events = []
    pitch = int((lo0 + hi0) / 2)
    onset = 0.0
    for i in range(n_slots):
        p = i / max(1, n_slots - 1)
        lo = lo0 + (lo1 - lo0) * p
        hi = hi0 + (hi1 - hi0) * p
        if rng.random() < 0.18:
            step = int(rng.integers(-9, 10))
        else:
            step = int(rng.integers(-3, 4))
        pitch = int(np.clip(pitch + step, lo, hi))
        st = int(round(onset + rng.normal(0, 14)))
        st = max(0, min(st, span - 40))
        dur = int(round(180 + rng.normal(0, 35)))
        en = min(st + dur, span - 1)
        if en <= st:
            en = st + 1
        vel = int(np.clip(88 + rng.normal(0, 10), 50, 115))
        events.append(MusicEvent(pitch=pitch, volume=vel,
                                 start_tick=st, end_tick=en))
        onset += GRID8 + rng.normal(0, 16)
    return events


# ------------------------------------------------------------ PHASE 1: raw
phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("Tendency_Raw", program=SINGING_SAW.midi_program, channel=0)

P1_OFFGRID = 0
P1_MEAN = {}
P1_MAXLEAP = {}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER[s])
    span = BARS_PER[s] * BAR
    evs = raw_tendency_walk(span, MASK[name], SEED + s)
    if not any(e.pitch == 0 and e.end_tick == span for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1,
                              end_tick=span))
    P1_OFFGRID += sum(1 for e in evs if e.pitch != 0 and e.start_tick % GRID16 != 0)
    pitches = [e.pitch for e in evs if e.pitch != 0]
    P1_MEAN[name] = round(float(np.mean(pitches)), 2) if pitches else 0.0
    diffs = [abs(pitches[i] - pitches[i - 1]) for i in range(1, len(pitches))]
    P1_MAXLEAP[name] = max(diffs) if diffs else 0
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
if not ok1:
    raise RuntimeError("phase1 validate FAIL: " + msg1)
P1_MIDI = os.path.join(MIDI_DIR, "302-techno-tendency-mask-phase1.mid")
phase1.to_midi(P1_MIDI)
assert os.path.getsize(P1_MIDI) > 40
print("PHASE1 validate:", msg1, "| off-grid onsets:", P1_OFFGRID)
print("PHASE1 per-section mean pitch:", P1_MEAN)
print("PHASE1 per-section max leap:", P1_MAXLEAP)


# ------------------------------------------------------------ PHASE 2: rules
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead", SINGING_SAW.midi_program, 0),       # tendency-masked saw lead
    ("Bass", SYNTH_BASS_1.midi_program, 1),      # driving synth bass
    ("Pad", SYNTH_PAD.midi_program, 2),          # breakdown pad
    ("Stab", SYNTH_BRASS_1.midi_program, 3),     # offbeat rave stab
    ("Drums", 0, 9),                              # 4-on-floor techno kit
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for i, name in enumerate(NAMES):
    phase2.add_section(name, bars=BARS_PER[i])


def grid_lock_dedup(events, grid=GRID8):
    by_key = {}
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        st = max(0, st)
        en = max(st + 1, int(e.end_tick))
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


# ---- lead: tendency-masked walk, grid-locked + tiered snap -----------------
for s, name in enumerate(NAMES):
    span = BARS_PER[s] * BAR
    evs = raw_tendency_walk(span, MASK[name], SEED + s)
    evs = grid_lock_dedup(evs)
    out = []
    seen = {}
    for e in evs:
        if e.pitch == 0:
            continue
        if e.start_tick >= span:
            continue
        bar = SEC_BAR_OFFSET[s] + (e.start_tick // BAR)
        bar = min(bar, N_BARS - 1)
        pitch = snap(e, bar, LEAD_LO, LEAD_HI)
        key = (e.start_tick, pitch)
        if key in seen:
            if e.end_tick > seen[key].end_tick:
                seen[key] = MusicEvent(pitch=pitch,
                                       volume=max(e.volume, seen[key].volume),
                                       start_tick=e.start_tick, end_tick=e.end_tick)
        else:
            seen[key] = MusicEvent(pitch=pitch, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick)
    for key in sorted(seen):
        out.append(seen[key])
    phase2.set_unit(0, s, MusicUnit(events=landmark(out, span)))


# ---- bass: driving pump (8th in Drop, root/fifth elsewhere) ----------------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    name = NAMES[s]
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    root = ROOT_BY_BAR[bar]
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    if name == "Drop":
        # driving offbeat 8th pump: root on beat, octave on the "and"
        for e8 in range(8):
            t = t0 + e8 * GRID8
            p = root if e8 % 2 == 0 else root + 12
            vel = 104 if e8 % 2 == 0 else 92
            events.append(MusicEvent(pitch=p, volume=vel, start_tick=t,
                                     end_tick=t + int(GRID8 * 0.7)))
    elif name == "Break":
        # half-time root + fifth (breakdown space)
        events.append(MusicEvent(pitch=root, volume=90, start_tick=t0,
                                 end_tick=t0 + int(BAR * 0.85)))
        events.append(MusicEvent(pitch=root + 7, volume=74,
                                 start_tick=t0 + 960,
                                 end_tick=t0 + 960 + int(BAR * 0.8)))
    else:
        # Intro/Outro: root on beat 1, long
        events.append(MusicEvent(pitch=root, volume=88, start_tick=t0,
                                 end_tick=t0 + int(BAR * 0.9)))
    phase2.set_unit(1, s, MusicUnit(events=events))


# ---- pad: sustained triad (prominent in Break/Intro/Outro, silent in Drop) --
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    name = NAMES[s]
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    if name == "Drop":
        continue                      # let bass+lead+stab carry the Drop
    tones = chord_tones(bar, lo=PAD_LO, hi=PAD_HI)
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    vol = 52 if name == "Break" else 40
    for k, p in enumerate(tones):
        events.append(MusicEvent(pitch=p, volume=vol + 3 * k,
                                 start_tick=t0, end_tick=t0 + BAR - 60))
    phase2.set_unit(2, s, MusicUnit(events=events))


# ---- stab: offbeat rave chord stab (Drop only) -----------------------------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    name = NAMES[s]
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    if name != "Drop":
        continue
    tones = chord_tones(bar, lo=STAB_LO, hi=STAB_HI)
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    # offbeat of beats 2 and 4 (the classic backbeat "rave stab")
    for off in (720, 1680):
        for k, p in enumerate(tones):
            events.append(MusicEvent(pitch=p, volume=62 + 2 * k,
                                     start_tick=t0 + off,
                                     end_tick=t0 + off + int(GRID8 * 0.8)))
    phase2.set_unit(3, s, MusicUnit(events=events))


# ---- drums: 4-on-floor kick, offbeat hat, clap, 16th closed hat ------------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    name = NAMES[s]
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []

    # kick
    if name == "Drop":
        for beat in (0, 480, 960, 1440):          # 4-on-floor
            events.append(MusicEvent(pitch=36, volume=112,
                                     start_tick=t0 + beat,
                                     end_tick=t0 + beat + 90))
    elif name in ("Intro", "Outro"):
        for beat in (0, 960):                     # beats 1 & 3
            events.append(MusicEvent(pitch=36, volume=96,
                                     start_tick=t0 + beat,
                                     end_tick=t0 + beat + 90))
    else:                                          # Break: beat 1 only
        events.append(MusicEvent(pitch=36, volume=80, start_tick=t0,
                                 end_tick=t0 + 90))

    # clap on 2 & 4 (Drop strong, Break light)
    if name == "Drop":
        for beat in (480, 1440):
            events.append(MusicEvent(pitch=39, volume=90,
                                     start_tick=t0 + beat,
                                     end_tick=t0 + beat + 60))
    elif name == "Break":
        events.append(MusicEvent(pitch=39, volume=52, start_tick=t0 + 1440,
                                 end_tick=t0 + 1440 + 60))

    # open hat: offbeat 8ths (air), stronger in Drop
    for e8 in (1, 3, 5, 7):
        t = t0 + e8 * GRID8
        events.append(MusicEvent(pitch=46, volume=(74 if name == "Drop" else 52),
                                 start_tick=t, end_tick=t + 40))

    # closed hat: 16th roll in Drop, 8th pulse elsewhere
    if name == "Drop":
        for e16 in range(16):
            events.append(MusicEvent(pitch=42, volume=52,
                                     start_tick=t0 + e16 * GRID16,
                                     end_tick=t0 + e16 * GRID16 + 30))
    elif name in ("Intro", "Outro"):
        for e8 in range(8):
            events.append(MusicEvent(pitch=42, volume=40,
                                     start_tick=t0 + e8 * GRID8,
                                     end_tick=t0 + e8 * GRID8 + 30))
    phase2.set_unit(4, s, MusicUnit(events=events))


# finalize bass/pad/stab/drums cells with landmark
for s in range(N_SECTIONS):
    span = BARS_PER[s] * BAR
    for row in (1, 2, 3, 4):
        unit = phase2.matrix.get_unit((row, s))
        events = list(unit.events) if unit is not None else []
        phase2.set_unit(row, s, MusicUnit(events=landmark(events, span)))

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


PITCHED = [(0, "Lead"), (1, "Bass"), (2, "Pad"), (3, "Stab")]
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
perfect_mid = os.path.join(MIDI_DIR, "302-techno-tendency-mask-perfect.mid")
human_mid = os.path.join(MIDI_DIR, "302-techno-tendency-mask-humanized.mid")

hz_instruments = {
    "Lead": SINGING_SAW.humanize_dna,
    "Bass": SYNTH_BASS_1.humanize_dna,
    "Pad": SYNTH_PAD.humanize_dna,
    "Stab": SYNTH_BRASS_1.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
hz = export_dual(phase2, perfect_mid, human_mid,
                 style="techno", seed=HZ_SEED, bpm=BPM,
                 instruments=hz_instruments)
print("export_dual OK; hz summary:")
print(json.dumps(hz, indent=2, default=str))


# ------------------------------------------------------------------ provenance
write_provenance(P1_MIDI, AI_ASSISTED,
                 "Tendency Masking Stochastic Bounds (Method 023) -- raw draft",
                 parameters={"phase": "1", "layer": "raw", "style": "techno",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM,
                             "tendency_mask": MASK,
                             "section_mean_pitch": P1_MEAN,
                             "section_max_leap": P1_MAXLEAP},
                 notes="phase1 raw draft: single-voice stochastic walk clipped "
                       "into a dynamic tendency mask [lo(t),hi(t)] per section; "
                       "off-grid onset jitter + unquantized chromatic pitch; no harmony.")
write_provenance(perfect_mid, AI_ASSISTED,
                 "Tendency Masking 023 + musicom rules (phase 2, grid-locked)",
                 parameters={"phase": "2", "layer": "perfect", "style": "techno",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM,
                             "progression": BAR_PROG,
                             "tendency_mask": MASK},
                 notes="grid-locked concrete layer; off-grid onsets == 0; "
                       "tiered snap (strong->chord tone, weak->A-minor scale).")
write_provenance(human_mid, AI_ASSISTED,
                 "Tendency Masking 023 + rules + humanize (phase 2, humanized)",
                 parameters={"phase": "2", "layer": "humanized", "style": "techno",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "humanize_profiles": {
                                 k: (v.get("profile") if isinstance(v, dict) else v)
                                 for k, v in hz.items()}},
                 notes="style-derived seeded humanization (techno profile + "
                       "per-instrument DNA).")


# ------------------------------------------------------------------ grid viz + manifest
gv = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, gv, ticks_per_character=120,
                         voice_names=[v[0] for v in VOICES], bpm=BPM)
print("grid viz written", gv)

manifest = {
    "project": "302-techno-tendency-mask",
    "genre": "Techno",
    "method": "023 Tendency Masking Stochastic Bounds (TM-SB)",
    "paradigm": "Stochastic",
    "layer": "concrete",
    "form": FORM,
    "key": KEY,
    "key_pcs": sorted(KEY_PCS),
    "bpm": BPM,
    "bars": N_BARS,
    "sections": NAMES,
    "bars_per_section": BARS_PER,
    "tendency_mask": MASK,
    "mask_width_start_end": MASK_WIDTH,
    "progression": BAR_PROG,
    "section_mean_pitch_phase1": P1_MEAN,
    "section_max_leap_phase1": P1_MAXLEAP,
    "seed": SEED,
    "hz_seed": HZ_SEED,
    "form_seed": FORM_SEED,
    "phase1_midi": P1_MIDI,
    "perfect_midi": perfect_mid,
    "humanized_midi": human_mid,
    "phase1_offgrid": P1_OFFGRID,
    "grid_audit": grid_audit,
    "harmony_audit": harmony_audit,
    "hz_summary": hz,
}
with open(os.path.join(ANALYSIS_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, default=str)
print("DONE")
