# -*- coding: utf-8 -*-
"""265-baroque-counter-duet — axis-combo composition (2026-10-25).

Axis combo from COMPOSITION_DESIGN_SPACE.md (user pick: "2-lead counter"):

| axis | pick |
|---|---|
| layer path | concrete-only |
| paradigm | Stochastic — Markov 002 (degree walk, stepwise-biased) |
| lead count | **1 lead + 1 counter** (contrast + complementary density) |
| percussion | none (Baroque) |
| harmonization | harpsichord continuo (sustained triads) |
| voice count | 4 = Violin lead · Viola counter · Harpsichord · Cello |
| register | non-crossing: cello 36–55 → harp 48–72 → viola 55–72 → violin 67–96 |
| density | lead 8ths w/ rests, counter fills the free 8ths |
| form | A A2 B B2 binary (4×4 bars) |
| humanization | classical (7 ms σ) |

Method 002 Markov: first-order walk over 7 scale degrees with stepwise-biased
transition weights (leading-tone resolves to I/V). The COUNTER is the engine's
canonical `HarmonyWriter.counterline()` (Phase 3 P2, commit c5c73d7): contrast
(never sounds the lead's pitch class simultaneously) + complementary density
(onsets only on grid slots the lead leaves free). Viola register (55,72).

Two-phase: phase-1 raw Markov walk (chromatic pitch_index, off-grid), phase-2
rules (tiered pitch: strong→in-chord, weak→in-scale) + counter + continuo.

Engine-only: structures + unitmatrix_composer + humanize + scale_quantizer +
provenance. mido NOT used for authoring (read-only audits in verify.py).
"""
import json
import random
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization
from sound.synthesis.scale_quantizer import ScaleQuantizer, classify_weight
from sound.generators.harmony_writer import HarmonyWriter

# ---- instrument registry (source of truth) ---------------------------------
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import VIOLIN, VIOLA, HARPSICHORD, CELLO  # noqa: E402

# ---- concept ---------------------------------------------------------------
GENRE = "Baroque"
STYLE = "Classical"             # processing key: humanize 7ms, LUFS -18
NAME = "265-baroque-counter-duet"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 2                       # D
KEY_NAME = "D major (ionian)"
NAT = [0, 2, 4, 5, 7, 9, 11]    # major intervals
DEGREE_PC = [(TONIC + o) % 12 for o in NAT]     # D E F# G A B C#
SCALE_PCS = set(DEGREE_PC)
BPM = 96
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = BAR // 4                 # 480
SEED = 20261025
rng = random.Random(SEED)

# ---- form: binary A A2 B B2 (16 bars) --------------------------------------
FORM_NAME = "binary (A A2 B B2)"
FORM = [("A", 4), ("A2", 4), ("B", 4), ("B2", 4)]
N_BARS = sum(b for _, b in FORM)
SECTION_TICKS = {}
_tick = 0
for s, b in FORM:
    SECTION_TICKS[s] = (b * BAR, _tick)
    _tick += b * BAR
TOTAL_TICKS = _tick


def section_of_bar(b):
    acc = 0
    for sname, nbars in FORM:
        if acc <= b < acc + nbars:
            return sname
        acc += nbars
    return FORM[-1][0]


# ---- harmony: diatonic triads in D major -----------------------------------
DEG_NAMES = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
DEG_LABELS = ["D", "Em", "F#m", "G", "A", "Bm", "C#dim"]


def deg_pc(d):
    return (TONIC + NAT[d % 7]) % 12


def chord_pcs_deg(d):
    return frozenset(deg_pc((d + k) % 7) for k in (0, 2, 4))   # triad


# per-bar chord degree (16 bars, binary form)
CHORD_DEG = (
    [0, 4, 5, 3]            # A:  I  V  vi IV
    + [1, 4, 0, 4]          # A2: ii V  I  V
    + [5, 3, 1, 4]          # B:  vi IV ii V
    + [0, 3, 4, 0]          # B2: I  IV V  I
)
assert len(CHORD_DEG) == N_BARS, f"chord bars {len(CHORD_DEG)} != {N_BARS}"
CHORD_PCS = [chord_pcs_deg(d) for d in CHORD_DEG]


def pool(deg, floor, ceil):
    pcs = sorted(chord_pcs_deg(deg))
    out = []
    for pc in pcs:
        p = floor + ((pc - floor) % 12)
        while p <= ceil:
            out.append(p)
            p += 12
    return sorted(out)


LEAD_POOL = {b: pool(CHORD_DEG[b], 67, 96) for b in range(N_BARS)}
HARP_POOL = {b: pool(CHORD_DEG[b], 48, 72) for b in range(N_BARS)}
BASS_POOL = {b: pool(CHORD_DEG[b], 36, 55) for b in range(N_BARS)}

# scale quantizer (D major, root D3 = 50)
sq = ScaleQuantizer(root=50, scale="major")
STRONG = (0, 960)


def nearest_in_register(pc, lo, hi, near):
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc]
    return min(cands, key=lambda p: abs(p - near)) if cands else near


# ============================================================================
# MARKOV 002 — first-order degree walk (stepwise-biased)
# ============================================================================
def trans_weight(frm, to):
    d = abs(frm - to)
    if d == 0:
        w = 2.0
    elif d == 1:
        w = 5.0
    elif d == 2:
        w = 2.5
    else:
        w = 0.4
    if frm == 6 and to in (0, 4):     # leading tone resolves to I or V
        w += 6.0
    return w


MARKOV = [[trans_weight(i, j) for j in range(7)] for i in range(7)]


def lead_plays(b, e):
    """Downbeats always sound; inner 8ths leave gaps for the counter."""
    if e in (0, 4):
        return True
    return rng.random() < 0.55


# ============================================================================
# PHASE 1 — RAW MARKOV DRAFT (single voice, chromatic, off-grid)
# ============================================================================
raw_events = []
idx = rng.random()                    # pitch_index [0,1]
for b in range(N_BARS):
    for e in range(8):
        if rng.random() < 0.5:
            continue
        idx += rng.uniform(-0.12, 0.12)
        idx = max(0.0, min(1.0, idx))
        onset = b * BAR + e * EIGHTH + rng.randint(12, 55)   # off-grid
        pitch = 55 + int(idx * 31)                           # 55..86 chromatic
        raw_events.append({"start_tick": onset, "pitch": pitch,
                           "velocity": rng.randint(70, 100),
                           "dur": rng.randint(120, 240)})


def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))   # zero-drift landmark
    return u


p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
p1.create_matrix(num_voices=1, num_sections=len(FORM))
p1.add_voice("MarkovRaw", program=VIOLIN.midi_program, channel=0)
for sname, nbars in FORM:
    p1.add_section(sname, bars=nbars)
for sname, (slen, soff) in SECTION_TICKS.items():
    evs = []
    for e in raw_events:
        if soff <= e["start_tick"] < soff + slen:
            st = e["start_tick"] - soff
            end = min(st + e["dur"], slen - 1)
            evs.append(MusicEvent(pitch=e["pitch"], volume=e["velocity"],
                                  start_tick=st, end_tick=end))
    p1.fill_voice_section("MarkovRaw", sname, unit_from(evs, slen))
ok1, msg1 = p1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
p1.to_midi(str(midi1))
write_provenance(str(midi1), "ai-generated", f"musicom {NAME}",
                 sources=["methods_db:002 Markov (stochastic)", f"style:{STYLE}",
                          "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "form": FORM_NAME,
                             "notes": "raw Markov pitch_index walk -> chromatic "
                                      "off-grid line; pre-rules"})
print(f"phase1 raw events={len(raw_events)}")
print("phase1 midi:", midi1, midi1.stat().st_size, "bytes")

# ============================================================================
# PHASE 2 — RULES (tiered pitch + counter + continuo)
# ============================================================================

# --- lead (violin): Markov degree walk, tiered snap -------------------------
def lead_events():
    notes = []
    degree = 0
    pitch = 74                       # D5
    for b in range(N_BARS):
        for e in range(8):
            if not lead_plays(b, e):
                continue
            st = b * BAR + e * EIGHTH
            degree = rng.choices(range(7), weights=MARKOV[degree])[0]
            pc = DEGREE_PC[degree]
            pitch = min((p for p in range(67, 97) if p % 12 == pc),
                        key=lambda p: abs(p - pitch))
            w = classify_weight(st, STRONG, BAR)
            if w == "strong":
                p = sq.tiered_quantize(pitch, weight="strong",
                                       chord_tones=LEAD_POOL[b])
            else:
                p = pitch               # already a scale degree pc
            notes.append(MusicEvent(pitch=int(p), volume=92,
                                    start_tick=st, end_tick=st + EIGHTH))
    return notes


lead_q = lead_events()
lead_dicts = [{"pitch": e.pitch, "volume": e.volume,
               "start_tick": e.start_tick, "end_tick": e.end_tick}
              for e in lead_q]

# --- counter (viola): engine counterline — contrast + complementary density
hw = HarmonyWriter(key="D")
counter_events = []
for si, (sname, (slen, soff)) in enumerate(SECTION_TICKS.items()):
    local_lead = [{"pitch": d["pitch"], "volume": d["volume"],
                   "start_tick": d["start_tick"] - soff,
                   "end_tick": d["end_tick"] - soff}
                  for d in lead_dicts
                  if soff <= d["start_tick"] < soff + slen]
    ctr = hw.counterline(local_lead, grid=EIGHTH, register=(55, 72),
                         mode="independent", seed=SEED + si)
    for c in ctr:
        counter_events.append(MusicEvent(pitch=c["pitch"], volume=c["volume"],
                                         start_tick=c["start_tick"] + soff,
                                         end_tick=c["end_tick"] + soff))


# --- harpsichord (harmony): sustained continuo triads ----------------------
def harp_events():
    evs = []
    for b in range(N_BARS):
        tones = HARP_POOL[b][-4:]      # close voicing, upper register
        bar0 = b * BAR
        for p in tones:
            evs.append(MusicEvent(pitch=p, volume=58, start_tick=bar0,
                                  end_tick=bar0 + BAR - 1))
    return evs


# --- cello (bass): continuo root on 1, fifth on 3 --------------------------
def bass_events():
    evs = []
    for b in range(N_BARS):
        root_pc = deg_pc(CHORD_DEG[b])          # actual chord root pc
        root = nearest_in_register(root_pc, 36, 55, root_pc + 36)
        fifth = nearest_in_register((root_pc + 7) % 12, 36, 55, root + 7)
        bar0 = b * BAR
        evs.append(MusicEvent(pitch=root, volume=92, start_tick=bar0,
                              end_tick=bar0 + EIGHTH * 3))
        evs.append(MusicEvent(pitch=fifth, volume=84, start_tick=bar0 + 960,
                              end_tick=bar0 + 960 + EIGHTH * 3))
    return evs


harp_q = harp_events()
bass_q = bass_events()

VOICES = [
    ("Violin", VIOLIN.midi_program, 0),
    ("Viola", VIOLA.midi_program, 1),
    ("Harpsichord", HARPSICHORD.midi_program, 2),
    ("Cello", CELLO.midi_program, 3),
]
events_by_voice = {
    "Violin": lead_q, "Viola": counter_events,
    "Harpsichord": harp_q, "Cello": bass_q,
}

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICES), num_sections=len(FORM))
for vname, prog, ch in VOICES:
    composer.add_voice(vname, program=prog, channel=ch)
for sname, nbars in FORM:
    composer.add_section(sname, bars=nbars)

for vname, prog, ch in VOICES:
    evs = events_by_voice[vname]
    for sname, (slen, soff) in SECTION_TICKS.items():
        seg = sorted([e for e in evs if soff <= e.start_tick < soff + slen],
                     key=lambda e: (e.start_tick, e.pitch))
        for e in seg:
            e.start_tick -= soff
            e.end_tick -= soff
            if e.end_tick > slen:
                e.end_tick = slen
            if e.end_tick <= e.start_tick:
                e.end_tick = e.start_tick + 1
        composer.fill_voice_section(vname, sname, unit_from(seg, slen))

# ---- dual-version export (perfect then humanized) --------------------------
hz_seed = SEED + 1
hz_instruments = {
    "Violin": VIOLIN.humanize_dna,
    "Viola": VIOLA.humanize_dna,
    "Harpsichord": HARPSICHORD.humanize_dna,
    "Cello": CELLO.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked, no jitter"),
                          (humanized_path, "2-humanized", "classical humanized")):
    write_provenance(str(path), "ai-generated", f"musicom {NAME}",
                     sources=["methods_db:002 Markov", "counter: HarmonyWriter.counterline",
                              f"style:{STYLE}", "phase:2 rules"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "form": FORM_NAME,
                                 "humanize": hz, "note": note})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

# ---- grid visualization + summary ------------------------------------------
try:
    write_grid_visualization(composer.matrix,
                             str(ROOT / "Analysis" / "grid_visualization.txt"))
except Exception as exc:
    print("grid viz skipped:", exc)

summary = {
    "project": NAME, "genre": GENRE, "style_key": STYLE,
    "method": "002 Markov (stochastic degree walk)",
    "layer": "concrete", "paradigm": "Stochastic",
    "axis_combo": "concrete-only x Stochastic(Markov 002) x 1+counter x no-perc "
                  "x harpsichord-continuo x 4-voice x non-crossing x A-A2-B-B2",
    "key": KEY_NAME, "bpm": BPM, "form": FORM_NAME,
    "form_sections": [s for s, _ in FORM], "bars": N_BARS,
    "total_ticks": TOTAL_TICKS, "tonic": TONIC,
    "scale_pcs": DEGREE_PC, "chord_degrees": CHORD_DEG,
    "chord_labels": [DEG_LABELS[d] for d in CHORD_DEG],
    "voices": [v for v, _, _ in VOICES],
    "counter": {"register": [55, 72], "mode": "independent",
                "constraints": ["contrast (no lead pc doubling)",
                                "complementary density (free 8th slots)"]},
    "markov_weights": MARKOV,
    "raw_event_count": len(raw_events),
    "lead_note_count": len(lead_q),
    "counter_note_count": len(counter_events),
    "humanize_seed": hz_seed,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("DONE compose")
