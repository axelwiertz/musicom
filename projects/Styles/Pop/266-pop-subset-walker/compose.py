# -*- coding: utf-8 -*-
"""266-pop-subset-walker — abstract+concrete ABS-002 Subset Walker, pop style.

Axis combo from COMPOSITION_DESIGN_SPACE.md (user pick: "abstract+concrete
ABS-002 walker, pop"):

| axis | pick |
|---|---|
| layer path | **abstract + concrete** (ABS-002 skeleton -> concrete fill) |
| paradigm | ABS (tonal) — 12TET subset network walk |
| lead count | 1 (flute) |
| percussion | full kit (pop backbeat) |
| harmonization | piano pad (sustained) + clarinet 16th arp |
| voice count | 5 = Flute · Piano · Double Bass · Clarinet · Drums |
| form | intro-verse-chorus-bridge-chorus2-outro (24 bar) |
| humanization | pop (4 ms sigma) |

ABS-002 Subset Walker (L4, rules/subset_network.py): the ABSTRACT layer walks
a PatternNetwork of C-major diatonic anchors (triads + 7th chords + V7) under
a tension curve (intro low -> chorus peak -> bridge settle -> resolve), then a
forced V7->I cadence. The walked subset per bar IS the harmony. The CONCRETE
layer realizes it: lead samples the walked-subset pitch classes, pad/bass/arp
fill chord tones, drums lock the backbeat.

Two-phase: phase-1 raw draft (single flute, subset-pc pitches, off-grid 8th
jitter), phase-2 rules (grid-lock + scale-snap + chord quantize + full texture).
Engine-only: structures + unitmatrix_composer + rules.subset_network +
workflows.humanize. mido READ-ONLY in verify.py.
"""
import json
import random
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.humanize import export_dual
from rules.subset_network import standard_patterns, PatternNetwork
from rules.patterns import tension as set_tension, interval_vector

# ---- instrument registry (source of truth) ---------------------------------
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import FLUTE, PIANO, DOUBLE_BASS, CLARINET, DRUM_KIT  # noqa: E402

# ---- concept ---------------------------------------------------------------
GENRE = "Pop"
STYLE = "Pop"
NAME = "266-pop-subset-walker"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 0                       # C
KEY_NAME = "C major (ionian)"
NAT = [0, 2, 4, 5, 7, 9, 11]
SCALE_PCS = set(NAT)
BPM = 120
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = BAR // 4                 # 480
SEED = 20261026

# ============================================================================
# ABSTRACT LAYER — ABS-002 subset walk (C-major diatonic anchors)
# ============================================================================
lib = {p.id: p for p in standard_patterns()}
# all diatonic to C major (no chromatic notes — the V7 is the diatonic G7)
POOL_IDS = ["maj0", "min2", "min4", "maj5", "maj7", "min9",     # triads
            "maj70", "min72", "min74", "maj75", "min79",        # diatonic 7ths
            "dom77"]                                            # V7 (G7)
POOL = [lib[i] for i in POOL_IDS]
NET = PatternNetwork(POOL)

# tension curve across 24 bars: intro low -> verse rise -> chorus peak ->
# bridge settle -> chorus2 peak -> outro resolve (22 walked + 2 cadence bars)
TENSION_CURVE = ([2.5] * 4 + [4.0] * 4 + [6.5] * 4 + [4.5] * 4 + [6.5] * 4
                 + [2.5] * 4)
_walk_rng = random.Random(SEED)
WALK = NET.walk("maj0", 22, rng=_walk_rng, tension_curve=TENSION_CURVE,
                home="maj0") + ["dom77", "maj0"]      # forced V7 -> I cadence
assert len(WALK) == 24

PAT_LABEL = {
    "maj0": "I", "min2": "ii", "min4": "iii", "maj5": "IV",
    "maj7": "V", "min9": "vi",
    "maj70": "Imaj7", "min72": "ii7", "min74": "iii7",
    "maj75": "IVmaj7", "min79": "vi7", "dom77": "V7",
}
CHORD_LABELS = [PAT_LABEL[pid] for pid in WALK]

# concrete chord realization: root MIDI + quality -> chord-tone intervals
CHORD_DEF = {
    "maj0": (48, "M"), "min2": (38, "m"), "min4": (40, "m"),
    "maj5": (41, "M"), "maj7": (43, "M"), "min9": (45, "m"),
    "maj70": (48, "M7"), "min72": (38, "m7"), "min74": (40, "m7"),
    "maj75": (41, "M7"), "min79": (45, "m7"), "dom77": (43, "7"),
}
IV = {"m": (0, 3, 7), "M": (0, 4, 7), "d": (0, 3, 6), "7": (0, 4, 7, 10),
      "m7": (0, 3, 7, 10), "M7": (0, 4, 7, 11)}

SCALE_PITCHES = sorted({p for p in range(36, 100) if p % 12 in SCALE_PCS})


def chord_tones(pid, lo, hi):
    root, kind = CHORD_DEF[pid]
    tones = set()
    for oct_shift in range(-2, 6):
        for i in IV[kind]:
            p = root + i + oct_shift * 12
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def quantize_to_chord(pitch, tones):
    return min(tones, key=lambda c: (abs(c - pitch), c))


def nearest_pc_pitch(pc, lo, hi, anchor=None):
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc]
    if not cands:
        return None
    if anchor is None:
        return min(cands, key=lambda p: (abs(p - (lo + hi) // 2), p))
    return min(cands, key=lambda p: (abs(p - anchor), p))


NAMES = ["Intro", "Verse", "Chorus", "Bridge", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER        # 24

# ============================================================================
# PHASE 1 — RAW DRAFT (single flute, subset-pc pitch, off-grid 8th jitter)
# ============================================================================
P_ONSET = {0: 0.50, 1: 0.68, 2: 0.85, 3: 0.55, 4: 0.85, 5: 0.45}
CENTERS = {0: 76.0, 1: 78.0, 2: 82.0, 3: 74.0, 4: 82.0, 5: 72.0}
rng1 = random.Random(SEED + 1)

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("FluteRaw", program=FLUTE.midi_program, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)

raw_pc_of_bar = []
for s, name in enumerate(NAMES):
    evs = []
    prev_end = 0
    for slot in range(BARS_PER * BAR // EIGHTH):      # 8th slots
        bar = s * BARS_PER + (slot * EIGHTH) // BAR
        pid = WALK[bar]
        pcs = sorted(lib[pid].pcs)
        if rng1.random() < P_ONSET[s]:
            pc = int(rng1.choice(pcs))
            st = slot * EIGHTH + int(rng1.randint(-40, 41))   # off-grid
            st = max(0, min(st, BARS_PER * BAR - 1))
            anchor = CENTERS[s] + rng1.uniform(-4, 4)
            p = nearest_pc_pitch(pc, 69, 91, anchor=int(anchor))
            if p is None:
                continue
            if st < prev_end - 10:
                st = prev_end + 10
            dur = int(EIGHTH * (0.85 + 0.4 * rng1.random()))
            en = min(st + dur, BARS_PER * BAR)
            if en > st:
                evs.append(MusicEvent(pitch=p, volume=int(72 + 24 * rng1.random()),
                                      start_tick=st, end_tick=en))
                prev_end = en
    # zero-drift landmark
    evs.append(MusicEvent(0, 0, BARS_PER * BAR - 1, BARS_PER * BAR))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
phase1.to_midi(str(midi1))
write_provenance(str(midi1), "ai-generated", f"musicom {NAME}",
                 sources=["methods_db:ABS-002 Subset Walker", f"style:{STYLE}",
                          "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "walk": WALK,
                             "tension_curve": TENSION_CURVE,
                             "notes": "subset-walk pc -> off-grid raw flute line"})
print(f"phase1 raw events ok; midi {midi1.stat().st_size} bytes")

# ============================================================================
# PHASE 2 — RULES (grid-lock + scale-snap + chord quantize + pop texture)
# ============================================================================

def quantize_to_grid(events, grid=SIXTEENTH):
    q = []
    for e in events:
        if e.pitch == 0:
            q.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        q.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                            start_tick=st, end_tick=max(st + 1, e.end_tick)))
    return q


phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
VOICES = [
    ("Flute", FLUTE.midi_program, 0),          # lead
    ("Piano", PIANO.midi_program, 1),          # pad
    ("Bass", DOUBLE_BASS.midi_program, 2),     # bass
    ("Clarinet", CLARINET.midi_program, 3),    # arp
    ("Drums", 0, 9),                            # percussion
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for vname, prog, ch in VOICES:
    phase2.add_voice(vname, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead (flute): grid-lock -> scale snap -> chord quantize per bar --------
for s in range(N_SECTIONS):
    raw_unit = phase1.matrix.get_unit((0, s))
    raw_events = quantize_to_grid(list(raw_unit.events))
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        sc = min(SCALE_PITCHES, key=lambda c: (abs(c - e.pitch), c))
        bar = s * BARS_PER + (e.start_tick // BAR)
        bar = min(bar, N_BARS - 1)
        tones = chord_tones(WALK[bar], lo=69, hi=91)
        qp = quantize_to_chord(sc, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick))
    phase2.set_unit(0, s, MusicUnit(events=q_events))

# --- piano (pad): sustained root-position triad per bar ---------------------
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    pid = WALK[bar]
    tones = chord_tones(pid, lo=48, hi=64)[:3]      # root-position triad
    t0 = b * BAR
    evs = [MusicEvent(pitch=p, volume=52 + 4 * k, start_tick=t0,
                      end_tick=t0 + BAR - 60)
           for k, p in enumerate(tones)]
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(evs)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- bass (double bass): root pulse, 8th in chorus, octave pop ---------------
BASS_8TH = {2, 4}
BASS_OCT = {2, 4}
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root, _kind = CHORD_DEF[WALK[bar]]
    root_pc = root % 12
    bass = nearest_pc_pitch(root_pc, 33, 50, anchor=38) or 38
    octv = bass + 12 if bass + 12 <= 55 else bass
    t0 = b * BAR
    evs = []
    step = EIGHTH if s in BASS_8TH else BEAT
    for k in range(0, BAR, step):
        on_beat = (k // step) % 2 == 0
        pitch = bass if on_beat else (octv if s in BASS_OCT else bass)
        evs.append(MusicEvent(pitch=pitch, volume=88 if on_beat else 66,
                              start_tick=t0 + k, end_tick=t0 + k + step - 40))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(evs)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- clarinet (arp): 16th chord-tone arpeggio --------------------------------
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    pid = WALK[bar]
    tones = chord_tones(pid, lo=60, hi=84)
    t0 = b * BAR
    evs = []
    n = len(tones)
    for k in range(0, BAR, SIXTEENTH):
        idx = (k // SIXTEENTH) % n
        evs.append(MusicEvent(pitch=tones[idx], volume=50,
                              start_tick=t0 + k, end_tick=t0 + k + 80))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(evs)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- drums (pop backbeat): kick 1&3, snare 2&4, hats; 16th hats in chorus ----
DRUM_PLAN = {
    0: dict(kick=70, snare=None, hat=40, hat16=False, clap=False),
    1: dict(kick=90, snare=80, hat=48, hat16=False, clap=False),
    2: dict(kick=100, snare=92, hat=54, hat16=True, clap=True),
    3: dict(kick=72, snare=70, hat=40, hat16=False, clap=False),
    4: dict(kick=100, snare=92, hat=54, hat16=True, clap=True),
    5: dict(kick=64, snare=None, hat=34, hat16=False, clap=False),
}
KICK, SNARE, CLHAT, CLAP = 36, 38, 42, 39
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        hat_step = SIXTEENTH if plan["hat16"] else EIGHTH
        for k in range(0, BAR, hat_step):
            evs.append(MusicEvent(pitch=CLHAT, volume=plan["hat"],
                                  start_tick=t0 + k, end_tick=t0 + k + 60))
        for kb in (0, 960):                      # kick 1 & 3
            evs.append(MusicEvent(pitch=KICK, volume=plan["kick"],
                                  start_tick=t0 + kb, end_tick=t0 + kb + 120))
        if plan["snare"] is not None:
            for sb in (480, 1440):               # snare 2 & 4
                evs.append(MusicEvent(pitch=SNARE, volume=plan["snare"],
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["clap"]:
            for sb in (480, 1440):
                evs.append(MusicEvent(pitch=CLAP, volume=72,
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# ---- normalize every cell to exact section boundary (zero-drift invariant) --
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    out = []
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
        if e.start_tick >= total_ticks:
            e.start_tick = total_ticks - 1
        if e.end_tick > e.start_tick:
            out.append(e)
    has_landmark = any(e.pitch == 0 and e.end_tick == total_ticks for e in out)
    if not has_landmark:
        out.append(MusicEvent(0, 0, total_ticks - 1, total_ticks))
    return MusicUnit(events=sorted(out, key=lambda e: (e.start_tick, e.pitch)))

for r in range(N_V):
    for c in range(N_SECTIONS):
        u = phase2.matrix.get_unit((r, c))
        phase2.set_unit(r, c, normalize_cell(u, BARS_PER * BAR))

ok2, msg2 = phase2.validate()
assert ok2, f"phase2 validate failed: {msg2}"

# ---- dual-version export (perfect then humanized) --------------------------
hz_seed = SEED + 1
hz_instruments = {
    "Flute": FLUTE.humanize_dna,
    "Piano": PIANO.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
    "Clarinet": CLARINET.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(phase2, str(perfect_path), str(humanized_path),
                 style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked"),
                          (humanized_path, "2-humanized", "pop humanized")):
    write_provenance(str(path), "ai-generated", f"musicom {NAME}",
                     sources=["methods_db:ABS-002 Subset Walker", f"style:{STYLE}",
                              "phase:2 rules"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "walk": WALK,
                                 "tension_curve": TENSION_CURVE,
                                 "humanize": hz, "note": note})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

# ---- summary (abstract skeleton + realization) ------------------------------
walk_detail = []
for bar, pid in enumerate(WALK):
    walk_detail.append({
        "bar": bar, "pattern": pid, "label": PAT_LABEL[pid],
        "pcs": sorted(lib[pid].pcs),
        "tension": round(set_tension(lib[pid].pcs), 2),
        "icv": interval_vector(lib[pid].pcs),
    })
summary = {
    "project": NAME, "genre": GENRE, "style_key": STYLE,
    "method": "ABS-002 Subset Walker (abstract) -> concrete pop fill",
    "layer": "abstract+concrete", "paradigm": "ABS (tonal)",
    "key": KEY_NAME, "bpm": BPM,
    "form": [n for n in NAMES], "bars": N_BARS,
    "tension_curve": TENSION_CURVE,
    "walk": WALK, "chord_labels": CHORD_LABELS,
    "walk_detail": walk_detail,
    "voices": [v for v, _, _ in VOICES],
    "humanize_seed": hz_seed,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("walk:", " ".join(CHORD_LABELS))
print("DONE compose")
