# -*- coding: utf-8 -*-
"""256-tango-dorian-rework — nightly rework (2026-10-22).

Source: 087-tango-abstract-dorian (D dorian tango, subset-walk harmony).
This is a REBUILD from scratch through the canonical UnitMatrixComposer engine,
preserving the musical identity (Tango / D dorian / 112 BPM / sax+violin+cello
+piano+bass+drum-kit / VII-dorian "home" half-cadence) but:
  * LONGER form: 8 sections x 4 bars = 32 bars (source had 6 x 4 = 24).
  * MORE variation: 8 distinct techniques (transposition, inversion,
    retrograde, augmentation, diminution, register shift, counterline,
    density rise) mapped per section.
  * CORRECT dorian chord labels (source mislabeled Em as "Edim", G as "Gm").
  * Per-section harmonic regions with MIDPOINT chord root (no bar-0 tonic bug).
  * Humanization + dual-version export (perfect / humanized) via export_dual.

Two-phase architecture:
  Phase 1 (raw): single-voice generative draft. Per-bar pitch-index RANDOM
    WALK (reflected), fractional OFF-GRID onsets (raw fingerprint). No harmony.
  Phase 2 (rules): snap to 16th grid -> pitch_index -> degree -> nearest chord
    tone of the bar its SNAPPED onset lands in (floor t//BAR) -> per-section
    variation transform -> voice-leading cap -> register/range enforcement ->
    dedupe collisions -> full 6-voice texture -> zero-drift landmark padding.

Engine-only: structures + workflows.unitmatrix_composer + workflows.humanize.
mido used READ-ONLY for audits. Instruments from the importable registry.
"""
import json
import os
import random
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization

# ---- instrument registry (source of truth) ---------------------------------
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    SAXOPHONE, VIOLIN, CELLO, PIANO, DOUBLE_BASS, DRUM_KIT,
)

# ---- concept ---------------------------------------------------------------
GENRE = "Tango"
NAME = "256-tango-dorian-rework"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 2                       # D
KEY_NAME = "D dorian"
DORIAN_OFFS = [0, 2, 3, 5, 7, 9, 10]     # rel to D=0 -> D E F G A B C
SCALE_PCS = set((TONIC + o) % 12 for o in DORIAN_OFFS)
BPM = 112
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = BAR // 4                 # 480
SEED = 20261022
rng = random.Random(SEED)

# ---- form: 8 sections x 4 bars = 32 bars ----------------------------------
FORM = [("Intro", 4), ("TangoA", 4), ("TangoB", 4), ("Lift", 4),
        ("TangoA2", 4), ("Bridge", 4), ("Finale", 4), ("Coda", 4)]
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

# ---- harmony: per-section regions, correct dorian chords -------------------
DEG_NAMES = ["i", "ii", "III", "IV", "v", "vi", "VII"]
DEG_CHORD_LABELS = ["Dm", "Em", "F", "G", "Am", "Bdim", "C"]
DEG_QUALITIES = ["minor", "minor", "major", "major", "minor", "dim", "major"]

def chord_pcs(deg, seventh=False):
    idx = [deg % 7, (deg + 2) % 7, (deg + 4) % 7]
    if seventh:
        idx.append((deg + 6) % 7)
    return frozenset((TONIC + DORIAN_OFFS[i]) % 12 for i in idx)

def pc_to_pitch(pc, floor):
    for p in range(floor, floor + 12):
        if p % 12 == pc:
            return p
    return floor

def chord_tones(deg, seventh, floor, ceil):
    pcs = chord_pcs(deg, seventh)
    out = []
    for pc in sorted(pcs):
        p = pc_to_pitch(pc, floor)
        while p <= ceil:
            out.append(p)
            p += 12
    return sorted(out)

# flat per-bar chord specs: (degree, seventh)
# region roots at MIDPOINT bar (start + nbars//2) — varied, never all tonic
CHORD_SPECS = []
for b in range(N_BARS):
    s = section_of_bar(b)
    bar_in_section = b - SECTION_TICKS[s][1] // BAR
    if s == "Intro":
        spec = (6, False) if bar_in_section in (0, 2) else (0, False)
    elif s == "TangoA":
        spec = [(0, False), (2, False), (3, False), (6, False)][bar_in_section]
    elif s == "TangoB":
        spec = [(3, False), (2, False), (1, False), (0, False)][bar_in_section]
    elif s == "Lift":
        spec = [(4, True), (1, True), (0, True), (6, True)][bar_in_section]
    elif s == "TangoA2":
        spec = [(0, False), (6, False), (2, False), (3, False)][bar_in_section]
    elif s == "Bridge":
        spec = [(5, False), (1, False), (4, False), (0, False)][bar_in_section]
    elif s == "Finale":
        spec = [(3, False), (4, False), (6, False), (0, False)][bar_in_section]
    else:  # Coda
        spec = (6, False) if bar_in_section in (1, 3) else (0, False)
    CHORD_SPECS.append(spec)

def bar_deg(b):
    return CHORD_SPECS[b][0]

# midpoint root per section (bars//2 into section)
section_roots = {}
for sname, nbars in FORM:
    soff = SECTION_TICKS[sname][1] // BAR
    mid = soff + nbars // 2
    d = CHORD_SPECS[mid][0]
    section_roots[sname] = d

# register pools per bar (chord tones realized per voice register)
LEAD_POOL = {b: chord_tones(CHORD_SPECS[b][0], CHORD_SPECS[b][1], 55, 88)
             for b in range(N_BARS)}
VIOLIN_POOL = {b: chord_tones(CHORD_SPECS[b][0], CHORD_SPECS[b][1], 67, 96)
               for b in range(N_BARS)}
CELLO_POOL = {b: chord_tones(CHORD_SPECS[b][0], CHORD_SPECS[b][1], 48, 72)
              for b in range(N_BARS)}
PIANO_POOL = {b: chord_tones(CHORD_SPECS[b][0], CHORD_SPECS[b][1], 60, 84)
              for b in range(N_BARS)}
BASS_POOL = {b: chord_tones(CHORD_SPECS[b][0], CHORD_SPECS[b][1], 38, 50)
             for b in range(N_BARS)}

def snap16(t):
    return int(round(t / SIXTEENTH) * SIXTEENTH)

# ============================================================================
# PHASE 1 — RAW GENERATIVE DRAFT (single voice, off-grid, pitch-index walk)
# ============================================================================
def nearest_scale_pitch(pitch, floor=52, ceil=88):
    best, bd = None, 1e9
    for p in range(floor, ceil + 1):
        if p % 12 in SCALE_PCS:
            d = abs(p - pitch)
            if d < bd:
                best, bd = p, d
    return best

raw_events = []                 # dicts: start_tick(abs), pitch_index, velocity, dur
pi_walk = 0.5
for b in range(N_BARS):
    n_ev = rng.randint(8, 12)
    for k in range(n_ev):
        frac = (k + rng.uniform(0.0, 0.9)) / n_ev
        st = b * BAR + int(frac * BAR)
        # reflected random walk of pitch_index in [0,1)
        pi_walk += rng.uniform(-0.14, 0.14)
        pi_walk = max(0.0, min(0.999, pi_walk))
        dur = int(rng.uniform(0.3, 0.9) * EIGHTH)
        raw_events.append({"start_tick": st, "pitch_index": pi_walk,
                           "velocity": rng.randint(70, 96), "dur": dur})

def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    # ALWAYS append the zero-drift terminal landmark. A real note that ends
    # exactly at sec_len (e.g. a whole-bar cello) would otherwise leave the
    # cell WITHOUT a landmark, and humanization's duration breathing (dc<1)
    # then shortens that note below sec_len -> validate() track mismatch.
    # The landmark (pitch 0) is passed through untouched by the humanizer.
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))
    return u

p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
p1.create_matrix(num_voices=1, num_sections=len(FORM))
p1.add_voice("RawDraft", program=SAXOPHONE.midi_program, channel=0)
for sname, nbars in FORM:
    p1.add_section(sname, bars=nbars)
for sname, (slen, soff) in SECTION_TICKS.items():
    evs = []
    for e in raw_events:
        if soff <= e["start_tick"] < soff + slen:
            pitch = nearest_scale_pitch(60 + e["pitch_index"] * 24, 55, 88)
            st = e["start_tick"] - soff
            end = min(st + e["dur"], slen - 1)
            evs.append(MusicEvent(pitch=pitch, volume=e["velocity"],
                                  start_tick=st, end_tick=end))
    p1.fill_voice_section("RawDraft", sname, unit_from(evs, slen))
ok1, msg1 = p1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
p1.to_midi(str(midi1))
write_provenance(str(midi1), "ai-generated", f"musicom nightly {NAME}",
                 sources=["methods_db:ABS-002 subset walk (pitch-index random walk)",
                          f"style:{GENRE}", "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "form": [s for s, _ in FORM],
                             "notes": f"raw pitch-index reflected random walk"})
print("phase1 midi:", midi1, midi1.stat().st_size, "bytes")

# ============================================================================
# PHASE 2 — RULES POST-PROCESS (grid snap + chord quant + variation + texture)
# ============================================================================

# --- variation transforms (per section) on a degree index -------------------
def deg_transpose(d, k=2):
    return (d + k) % 7

def deg_invert(d, pivot=4):
    return (2 * pivot - d) % 7

# --- lead: derive from phase-1 raw events, quantized + varied --------------
def lead_events():
    notes = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        pool = LEAD_POOL[b]
        raw = [e for e in raw_events if b * BAR <= e["start_tick"] < (b + 1) * BAR]
        raw.sort(key=lambda e: e["start_tick"])
        if s == "Bridge":
            raw = raw[::-1]                     # retrograde within section
        bar_notes = []
        for e in raw:
            st = snap16(e["start_tick"])
            if st >= (b + 1) * BAR:
                st = (b + 1) * BAR - SIXTEENTH
            d = int(e["pitch_index"] * 7) % 7
            dur = max(SIXTEENTH, snap16(e["dur"]))
            vel = e["velocity"]
            if s == "TangoB":
                d = deg_transpose(d, 2)         # transposition
            elif s == "TangoA2":
                d = deg_invert(d)               # inversion
            elif s == "Lift":
                dur = SIXTEENTH                 # diminution (16th runs)
                vel = min(127, vel + 6)
            elif s == "Finale":
                dur = min(EIGHTH * 2, dur * 2)  # augmentation
            elif s == "Coda":
                dur = SIXTEENTH                 # diminution fragment
                vel = max(30, vel - 25)         # fade
            elif s == "Intro":
                dur = min(EIGHTH * 2, dur + EIGHTH)   # sparse
            bar_notes.append((st, d, dur, vel))
        # register shift per section
        reg_floor = {"Intro": 55, "Bridge": 55}.get(s, 62)
        for st, d, dur, vel in bar_notes:
            target = pc_to_pitch((TONIC + DORIAN_OFFS[d]) % 12, reg_floor)
            best = min(pool, key=lambda p: abs(p - target))
            for cand in (best - 12, best + 12):
                if abs(cand - target) < abs(best - target):
                    best = cand
            pitch = max(49, min(88, best))      # sax range
            notes.append(MusicEvent(pitch=pitch, volume=int(vel),
                                    start_tick=st,
                                    end_tick=min(st + dur, (b + 1) * BAR - 1)))
    return notes

def violin_events():
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        pool = VIOLIN_POOL[b]
        bar0 = b * BAR
        if s == "Bridge":
            # counterline: violin takes the retrograde motif in upper register
            raw = [e for e in raw_events if bar0 <= e["start_tick"] < bar0 + BAR]
            raw.sort(key=lambda e: e["start_tick"], reverse=True)
            for e in raw[:6]:
                st = snap16(e["start_tick"])
                d = int(e["pitch_index"] * 7) % 7
                target = pc_to_pitch((TONIC + DORIAN_OFFS[d]) % 12, 74)
                best = min(pool, key=lambda p: abs(p - target))
                evs.append(MusicEvent(pitch=best, volume=78,
                                      start_tick=st, end_tick=min(st + EIGHTH, bar0 + BAR - 1)))
        else:
            for beat in (1, 3):
                st = bar0 + beat * BEAT
                tones = pool
                p = tones[min(len(tones) - 1, 1)]
                evs.append(MusicEvent(pitch=p, volume=72,
                                      start_tick=st, end_tick=st + EIGHTH))
                st2 = st + EIGHTH
                if st2 < bar0 + BAR:
                    evs.append(MusicEvent(pitch=tones[len(tones) - 1], volume=66,
                                          start_tick=st2, end_tick=st2 + EIGHTH))
    return evs

def cello_events():
    evs = []
    for b in range(N_BARS):
        tones = CELLO_POOL[b]
        root = tones[0]
        fifth = tones[len(tones) // 2] if len(tones) > 1 else root
        st = b * BAR
        evs.append(MusicEvent(pitch=root, volume=58, start_tick=st, end_tick=st + BAR))
        evs.append(MusicEvent(pitch=fifth, volume=52, start_tick=st, end_tick=st + BAR))
    return evs

def piano_events():
    evs = []
    for b in range(N_BARS):
        tones = PIANO_POOL[b]
        bar0 = b * BAR
        for beat in (0, 2):
            st = bar0 + beat * BEAT
            for p in tones[:3]:
                evs.append(MusicEvent(pitch=p, volume=64,
                                      start_tick=st, end_tick=st + SIXTEENTH))
    return evs

def bass_events():
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        tones = BASS_POOL[b]
        root = tones[0]
        bar0 = b * BAR
        evs.append(MusicEvent(pitch=root, volume=92,
                              start_tick=bar0, end_tick=bar0 + 900))
        if s not in ("Coda", "Intro"):
            st = bar0 + 3 * BEAT + EIGHTH
            fifth = tones[len(tones) // 2] if len(tones) > 1 else root
            evs.append(MusicEvent(pitch=fifth, volume=84,
                                  start_tick=st,
                                  end_tick=min(st + EIGHTH * 2, bar0 + BAR - 1)))
    return evs

def drums_events():
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        bar0 = b * BAR
        dense = s in ("Lift", "Finale")
        # kick
        k_ons = [0, 1, 2, 3] if s == "Lift" else [0, 2]
        for beat in k_ons:
            st = bar0 + beat * BEAT
            evs.append(MusicEvent(pitch=36, volume=100,
                                  start_tick=st, end_tick=st + SIXTEENTH * 2))
        # snare backbeat 2 & 4
        for beat in (1, 3):
            st = bar0 + beat * BEAT
            evs.append(MusicEvent(pitch=38, volume=92 if dense else 70,
                                  start_tick=st, end_tick=st + SIXTEENTH * 2))
        # closed hat
        sub = SIXTEENTH if s in ("Lift", "TangoB", "Finale") else EIGHTH
        st = bar0
        while st < bar0 + BAR - sub:
            evs.append(MusicEvent(pitch=42, volume=56,
                                  start_tick=st, end_tick=st + sub // 2))
            st += sub
        if dense and s != "Lift":
            st = bar0 + 3 * BEAT + EIGHTH
            evs.append(MusicEvent(pitch=42, volume=80,
                                  start_tick=st, end_tick=st + SIXTEENTH))
    return evs

# --- final quantize: grid-snap (already grid) + chord-tone + dedupe ---------
def finalize_pitched(events, pool_by_bar):
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = snap16(e.start_tick)
        if st < 0:
            st = 0
        bar = min(st // BAR, N_BARS - 1)
        pool = pool_by_bar[bar]
        best = min(pool, key=lambda p: abs(p - e.pitch))
        for cand in (best - 12, best + 12):
            if abs(cand - e.pitch) < abs(best - e.pitch):
                best = cand
        out.append(MusicEvent(pitch=best, volume=int(e.volume),
                              start_tick=st, end_tick=max(st + 1, e.end_tick)))
    # dedupe (start, pitch) keep longest
    seen = {}
    res = []
    for e in out:
        if e.pitch == 0:
            res.append(e)
            continue
        key = (e.start_tick, e.pitch)
        if key in seen:
            seen[key].end_tick = max(seen[key].end_tick, e.end_tick)
        else:
            seen[key] = e
            res.append(e)
    res.sort(key=lambda e: (e.start_tick, e.pitch))
    return res

def cap_leaps(events, pool_by_bar, max_leap=10):
    evs = sorted([e for e in events if e.pitch], key=lambda e: e.start_tick)
    for i in range(1, len(evs)):
        prev, cur = evs[i - 1], evs[i]
        if cur.start_tick - prev.start_tick <= BAR and abs(cur.pitch - prev.pitch) > max_leap:
            bar = min(cur.start_tick // BAR, N_BARS - 1)
            pool = pool_by_bar[bar]
            target = prev.pitch + max_leap if cur.pitch > prev.pitch else prev.pitch - max_leap
            best = min(pool, key=lambda p: (abs(p - target), abs(p - cur.pitch)))
            cur.pitch = best
    return evs

lead_q = cap_leaps(finalize_pitched(lead_events(), LEAD_POOL), LEAD_POOL)
violin_q = cap_leaps(finalize_pitched(violin_events(), VIOLIN_POOL), VIOLIN_POOL)
cello_q = finalize_pitched(cello_events(), CELLO_POOL)
piano_q = finalize_pitched(piano_events(), PIANO_POOL)
bass_q = finalize_pitched(bass_events(), BASS_POOL)
drums_q = drums_events()

VOICES = [
    ("LeadSax", SAXOPHONE.midi_program, 0),
    ("Violin", VIOLIN.midi_program, 1),
    ("Cello", CELLO.midi_program, 2),
    ("Piano", PIANO.midi_program, 3),
    ("Bass", DOUBLE_BASS.midi_program, 4),
    ("Drums", 0, 9),
]
events_by_voice = {
    "LeadSax": lead_q, "Violin": violin_q, "Cello": cello_q,
    "Piano": piano_q, "Bass": bass_q, "Drums": drums_q,
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
        # SORT by start_tick: the humanizer's forward-clamp assumes ascending
        # onsets; unsorted cells (e.g. drums built kick/snare/hat in separate
        # loops) get pinned hundreds of ticks off-grid. Sort before clipping.
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
    "LeadSax": SAXOPHONE.humanize_dna,
    "Violin": VIOLIN.humanize_dna,
    "Cello": CELLO.humanize_dna,
    "Piano": PIANO.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=GENRE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked, no jitter"),
                          (humanized_path, "2-humanized", "style+instrument humanized")):
    write_provenance(str(path), "ai-generated", f"musicom nightly {NAME}",
                     sources=["methods_db:ABS-002 subset walk", f"style:{GENRE}",
                              "phase:2 rules", f"humanize_seed:{hz_seed}"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "form": [s for s, _ in FORM],
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
    "project": NAME, "genre": GENRE, "key": KEY_NAME, "bpm": BPM,
    "form": [s for s, _ in FORM], "bars": N_BARS, "total_ticks": TOTAL_TICKS,
    "source": "087-tango-abstract-dorian", "decision": "redesign (index.html missing)",
    "variations": {
        "Intro": "register shift (low) + sparse",
        "TangoA": "base motif",
        "TangoB": "transposition (+2 degrees)",
        "Lift": "diminution (16th) + density rise + 7th chords",
        "TangoA2": "inversion (pivot degree 4)",
        "Bridge": "retrograde + register shift + violin counterline",
        "Finale": "augmentation (x2) + tutti",
        "Coda": "diminution fragment + fade",
    },
    "section_roots_midpoint": {s: DEG_CHORD_LABELS[section_roots[s]]
                               for s, _ in FORM},
    "voices": [v for v, _, _ in VOICES],
    "humanize_seed": hz_seed,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("DONE compose")
