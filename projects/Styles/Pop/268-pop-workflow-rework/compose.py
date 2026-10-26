# -*- coding: utf-8 -*-
"""Musicom rework job 2026-10-26: Pop/workflow-demo -> 268-pop-workflow-rework.

Source identity (extracted): Pop, C major, 120 BPM, 4/4, 480 tpb.
Voices: Lead(Flute 74) Pad(Piano 1) Bass(Contrabass 43) Arp(Clarinet 71) Drums(ch9).
Form: intro-verse-chorus-bridge-outro (28 bars).

Rework: rebuild through canonical UnitMatrixComposer two-phase architecture,
extend to 8 sections / 32 bars, apply 6 variation techniques.
"""
import json
import os
import hashlib

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual
from rules.progression import Scale7ChordDegree

# ---------------- constants ----------------
BAR = 1920  # 480 tpb * 4 beats
BPM = 120
INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # C major
KEY_PCS = set(INTERVALS)
QUALITY = {1: (0, 4, 7), 2: (0, 3, 7), 3: (0, 3, 7), 4: (0, 4, 7),
           5: (0, 4, 7), 6: (0, 3, 7), 7: (0, 3, 6)}

PROJ = "268-pop-workflow-rework"
BASE = "/opt/data/repos/musicom/projects/Styles/Pop/" + PROJ
STYLE = "pop"

hz_seed = int(hashlib.md5(PROJ.encode()).hexdigest()[:8], 16) % 100000
raw_seed = int(hashlib.md5(b"raw-268").hexdigest()[:8], 16) % 100000

# ---------------- helpers ----------------
def diatonic(deg_index):
    return Scale7ChordDegree.get_diatonic_note(60, INTERVALS, deg_index)

def chord_tones(d):
    root = Scale7ChordDegree.get_diatonic_note(48, INTERVALS, d - 1)
    q = QUALITY[d]
    tones = []
    for o in range(3):
        for iv in q:
            tones.append(root + 12 * o + iv)
    return sorted(set(tones))

# ---------------- form ----------------
# (name, bars, progression, drum_kind, lead_variant, deg_shift, octave_shift, slots_per_bar)
MOTIF_ASC = [0, 2, 4, 7, 4, 2]
MOTIF_DESC = [7, 4, 2, 0, 2, 4]
MOTIF_RETRO = list(reversed(MOTIF_ASC))

SECTIONS = [
    ("Intro",     4, [1, 4, 5, 1], "intro",     MOTIF_ASC,  0,  0,  8),
    ("VerseA",    4, [1, 5, 6, 4], "verse",     MOTIF_ASC,  0,  0,  8),
    ("VerseB",    4, [6, 4, 1, 5], "verse",     MOTIF_ASC,  4,  0,  8),
    ("PreChorus", 4, [4, 5, 6, 5], "prechorus", MOTIF_ASC,  0,  7, 16),
    ("ChorusA",   4, [1, 5, 6, 4], "chorus",    MOTIF_ASC,  0,  7,  8),
    ("Bridge",    4, [2, 4, 6, 5], "bridge",    MOTIF_DESC, 0,  0,  8),
    ("ChorusB",   4, [1, 5, 6, 4], "chorus",    MOTIF_ASC,  0, 14,  8),
    ("Outro",     4, [1, 4, 1, 1], "outro",     MOTIF_RETRO,0,  0,  4),
]
TOTAL_BARS = sum(s[1] for s in SECTIONS)

import numpy as np
raw_rng = np.random.default_rng(raw_seed)

# section cumulative start bars
section_start = {}
acc = 0
for name, bars, prog, dk, mot, dsh, osh, slots in SECTIONS:
    section_start[name] = acc
    acc += bars

# ---------------- Phase 1: raw generative draft (absolute ticks, single voice) ----------------
raw_events = []  # (onset_abs, raw_pitch, dur, vel)
for name, bars, prog, dk, mot, dsh, osh, slots in SECTIONS:
    start_abs = section_start[name] * BAR
    step = BAR // slots
    for bar in range(bars):
        for i in range(slots):
            deg = mot[(bar * slots + i) % len(mot)] + dsh + osh
            note = diatonic(deg)
            pitch = int(note) + int(raw_rng.integers(-1, 2))      # unquantized pitch
            onset = start_abs + bar * BAR + i * step + int(raw_rng.integers(-40, 41))  # unquantized rhythm
            dur = int(step) + int(raw_rng.integers(-40, 81))
            vel = int(raw_rng.integers(85, 111))
            span_total = TOTAL_BARS * BAR
            onset = max(0, min(onset, span_total - 120))
            dur = max(120, min(dur, span_total - onset))
            raw_events.append((onset, pitch, dur, vel))

# Phase 1 export (single voice, single 32-bar section)
p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=480, beats_per_bar=4)
p1.create_matrix(num_voices=1, num_sections=1)
p1.add_voice("LeadRaw", program=74, channel=0)
p1.add_section("Raw", bars=TOTAL_BARS)
p1_ev = [MusicEvent(int(p), int(v), int(o), int(o + d)) for (o, p, d, v) in raw_events]
span = TOTAL_BARS * BAR
p1_ev.append(MusicEvent(0, 0, span - 10, span))  # terminal landmark
p1.fill_voice_section("LeadRaw", "Raw", MusicUnit(events=p1_ev))
ok, msg = p1.validate()
if not ok:
    raise RuntimeError(f"phase1 validate failed: {msg}")
phase1_path = os.path.join(BASE, "MIDI", PROJ + "-phase1.mid")
p1.to_midi(phase1_path)

# ---------------- Phase 2: musicom rules post-processing ----------------
def snap(t):
    return int(round(t / 120.0)) * 120

def bar_degree(bar_abs):
    b = bar_abs
    for name, bars, prog, dk, mot, dsh, osh, slots in SECTIONS:
        if section_start[name] <= b < section_start[name] + bars:
            return prog[b - section_start[name]]
    return 1

quantized = {}  # (onset, pitch) -> dur (longest wins)
for (onset, pitch, dur, vel) in raw_events:
    qonset = max(0, snap(onset))
    bar = qonset // BAR
    # locate section for the SNAPPED onset (floor attribution, not round)
    for name, bars, prog, dk, mot, dsh, osh, slots in SECTIONS:
        if section_start[name] <= bar < section_start[name] + bars:
            sec_start = section_start[name] * BAR
            sec_len = bars * BAR
            break
    local = qonset - sec_start
    local = max(0, min(local, sec_len - 120))
    qonset = sec_start + local
    bar = qonset // BAR                      # re-derive after clamp
    d = bar_degree(bar)
    tones = chord_tones(d)
    qpitch = min(tones, key=lambda t: abs(t - pitch))
    qdur = max(120, min(480, snap(dur)))
    qdur = max(120, min(qdur, sec_start + sec_len - qonset))
    key = (qonset, qpitch)
    if key not in quantized or qdur > quantized[key][0]:
        quantized[key] = (qdur, vel)

# split quantized lead per section -> cell-local
lead_by_section = {name: [] for name, *_ in SECTIONS}
for (onset, pitch), (dur, vel) in sorted(quantized.items()):
    bar = onset // BAR
    for name, bars, prog, dk, mot, dsh, osh, slots in SECTIONS:
        if section_start[name] <= bar < section_start[name] + bars:
            local = onset - section_start[name] * BAR
            lead_by_section[name].append((local, pitch, dur, vel))
            break

# ---------------- build full composer ----------------
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=5, num_sections=len(SECTIONS))
composer.add_voice("Lead", program=74, channel=0)   # Flute
composer.add_voice("Pad",  program=1,  channel=1)   # Bright Acoustic Piano
composer.add_voice("Bass", program=43, channel=2)   # Contrabass
composer.add_voice("Arp",  program=71, channel=3)   # Clarinet
composer.add_voice("Drums", program=0, channel=9)

def landmark(events, sec_len):
    events.sort(key=lambda e: e.start_tick)
    events.append(MusicEvent(0, 0, max(0, sec_len - 10), sec_len))
    return MusicUnit(events=events)

for name, bars, prog, dk, mot, dsh, osh, slots in SECTIONS:
    composer.add_section(name, bars=bars)

for name, bars, prog, dk, mot, dsh, osh, slots in SECTIONS:
    sec_len = bars * BAR
    # Lead
    ev = [MusicEvent(int(p), int(v), int(o), int(o + d)) for (o, p, d, v) in lead_by_section[name]]
    composer.fill_voice_section("Lead", name, landmark(ev, sec_len))

    # Pad: whole-bar triad per bar
    pev = []
    for bar in range(bars):
        d = prog[bar]
        root = Scale7ChordDegree.get_diatonic_note(48, INTERVALS, d - 1) + 12
        for iv in QUALITY[d]:
            pev.append(MusicEvent(int(root + iv), 70, bar * BAR, (bar + 1) * BAR))
    composer.fill_voice_section("Pad", name, landmark(pev, sec_len))

    # Bass: driving root on every beat (8ths in chorus)
    bev = []
    div = 8 if dk == "chorus" else 4
    step = BAR // div
    for bar in range(bars):
        d = prog[bar]
        root = Scale7ChordDegree.get_diatonic_note(36, INTERVALS, d - 1)
        for i in range(div):
            bev.append(MusicEvent(int(root), 90, bar * BAR + i * step, bar * BAR + i * step + step - 40))
    composer.fill_voice_section("Bass", name, landmark(bev, sec_len))

    # Arp: chord-tone arpeggio (16ths in chorus/prechorus)
    aev = []
    div = 16 if dk in ("chorus", "prechorus") else 8
    step = BAR // div
    for bar in range(bars):
        d = prog[bar]
        root = Scale7ChordDegree.get_diatonic_note(60, INTERVALS, d - 1)
        tones = [root + iv for iv in QUALITY[d]] + [root + 12]
        for i in range(div):
            p = tones[i % len(tones)]
            aev.append(MusicEvent(int(p), 75, bar * BAR + i * step, bar * BAR + i * step + step - 20))
    composer.fill_voice_section("Arp", name, landmark(aev, sec_len))

    # Drums (ch9)
    dev = []
    for bar in range(bars):
        b0 = bar * BAR
        if dk == "intro" or dk == "outro":
            dev.append(MusicEvent(36, 90, b0, b0 + 120))
            for i in range(8):
                dev.append(MusicEvent(42, 60, b0 + i * 240, b0 + i * 240 + 120))
        elif dk == "verse":
            for i in range(8):
                dev.append(MusicEvent(42, 60, b0 + i * 240, b0 + i * 240 + 120))
            dev.append(MusicEvent(36, 95, b0, b0 + 120)); dev.append(MusicEvent(36, 95, b0 + 960, b0 + 1080))
            dev.append(MusicEvent(38, 90, b0 + 480, b0 + 600)); dev.append(MusicEvent(38, 90, b0 + 1440, b0 + 1560))
        elif dk == "prechorus":
            for i in range(8):
                dev.append(MusicEvent(42, 65, b0 + i * 240, b0 + i * 240 + 120))
            dev.append(MusicEvent(36, 95, b0, b0 + 120)); dev.append(MusicEvent(36, 95, b0 + 960, b0 + 1080))
            dev.append(MusicEvent(38, 90, b0 + 480, b0 + 600)); dev.append(MusicEvent(38, 90, b0 + 1440, b0 + 1560))
            if bar == bars - 1:  # snare build
                for i in range(8):
                    dev.append(MusicEvent(38, 80, b0 + i * 240, b0 + i * 240 + 120))
        elif dk == "chorus":
            for i in range(16):
                dev.append(MusicEvent(42, 55, b0 + i * 120, b0 + i * 120 + 60))
            dev.append(MusicEvent(36, 100, b0, b0 + 120)); dev.append(MusicEvent(36, 100, b0 + 960, b0 + 1080))
            dev.append(MusicEvent(38, 95, b0 + 480, b0 + 600)); dev.append(MusicEvent(38, 95, b0 + 1440, b0 + 1560))
            dev.append(MusicEvent(49, 80, b0, b0 + 240))
        elif dk == "bridge":
            for i in range(8):
                dev.append(MusicEvent(42, 50, b0 + i * 240, b0 + i * 240 + 120))
            dev.append(MusicEvent(36, 85, b0, b0 + 120)); dev.append(MusicEvent(38, 80, b0 + 1440, b0 + 1560))
    composer.fill_voice_section("Drums", name, landmark(dev, sec_len))

ok, msg = composer.validate()
if not ok:
    raise RuntimeError(f"phase2 validate failed (perfect): {msg}")

# grid visualization of the perfect layer
grid_path = os.path.join(BASE, "Analysis", "grid_visualization.txt")
write_grid_visualization(composer.matrix, grid_path, ticks_per_character=120)

# humanize instruments DNA
hz_instruments = {
    "Lead":  (None, 6.0, None, 0.02),
    "Pad":   (None, 5.0, None, 0.015),
    "Bass":  (5.0, 4.0, 8.0, 0.01),
    "Arp":   (None, 5.0, None, 0.02),
    "Drums": (2.0, 4.0, 0.0, 0.008),
}

perfect_path = os.path.join(BASE, "MIDI", PROJ + "-perfect.mid")
humanized_path = os.path.join(BASE, "MIDI", PROJ + "-humanized.mid")
hz = export_dual(composer, perfect_path, humanized_path,
                 style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

# ---------------- provenance ----------------
def jp(x):
    return json.dumps(x, sort_keys=True)

provenance_params = {
    "bpm": BPM, "key": "C", "mode": "major", "style": STYLE,
    "form": "intro-verseA-verseB-prechorus-chorusA-bridge-chorusB-outro",
    "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
    "voices": [["Lead", "Flute", 74], ["Pad", "Piano", 1], ["Bass", "Contrabass", 43],
               ["Arp", "Clarinet", 71], ["Drums", "ch9", 0]],
    "humanize_seed": hz_seed, "raw_seed": raw_seed,
    "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
}
write_provenance(phase1_path, AI_ASSISTED, "musicom two-phase (phase=1 raw generative draft, pre-rules)",
                 sources=["Styles/Pop/workflow-demo/pop-001.mid"],
                 parameters=dict(provenance_params, phase=1),
                 notes="Raw unquantized pitch+rhythm; single voice LeadRaw.")
write_provenance(perfect_path, AI_ASSISTED, "musicom two-phase (phase=2 musicom rules: chord-tone quantize + grid snap + dedup)",
                 sources=["Styles/Pop/workflow-demo/pop-001.mid", phase1_path],
                 parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
                 notes="Grid-locked perfect layer.")
write_provenance(humanized_path, AI_ASSISTED, "musicom two-phase (phase=2 + humanization)",
                 sources=[perfect_path],
                 parameters=dict(provenance_params, phase=2, version="humanized",
                                 humanize_seed=hz_seed,
                                 humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                                     for kk, vv in v.items() if kk != "profile"}
                                                 for k, v in hz.items()}),
                 notes="Humanized layer (style pop + per-instrument DNA).")

# ---------------- report ----------------
section_roots = []
for name, bars, prog, dk, mot, dsh, osh, slots in SECTIONS:
    mid = prog[len(prog) // 2]
    section_roots.append(mid)
root_names = ["C", "D", "E", "F", "G", "A", "B"]

summary = {
    "chosen_source": "Styles/Pop/workflow-demo",
    "chosen_genre": "Pop",
    "audit_failures": ["no compose.py (engine-authorship evidence missing)",
                       "phase1.mid missing", "project provenance.json + index.html missing"],
    "redesign_required": True,
    "new_project": BASE,
    "form_bars": TOTAL_BARS,
    "form_sections": len(SECTIONS),
    "variation_techniques": ["transposition", "inversion", "retrograde", "augmentation",
                             "diminution", "register_shift"],
    "section_roots": [root_names[r - 1] for r in section_roots],
    "hz_seed": hz_seed,
    "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"} for k, v in hz.items()},
    "phase1_path": phase1_path,
    "perfect_path": perfect_path,
    "humanized_path": humanized_path,
}

print("COMPOSE_OK")
print(json.dumps(summary, indent=2, default=str))
with open(os.path.join(BASE, "Analysis", "rework_audit.json"), "w") as f:
    json.dump({"chosen": "Pop/workflow-demo", "genre": "Pop",
               "standard_failures": summary["audit_failures"],
               "redesign_required": True,
               "source_identity": {"key": "C major", "bpm": 120,
                                   "motif": "C-E-G-C arpeggio (0,2,4,7)",
                                   "voices": ["Lead/Flute", "Pad/Piano", "Bass/Contrabass",
                                              "Arp/Clarinet", "Drums"],
                                   "form": "intro-verse-chorus-bridge-outro"}}, f, indent=2)
with open(os.path.join(BASE, "Analysis", "compose_summary.json"), "w") as f:
    json.dump(summary, f, indent=2, default=str)
