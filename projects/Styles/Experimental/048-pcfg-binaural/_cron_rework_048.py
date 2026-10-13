#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rework 048-pcfg-binaural to pass the 3-rule pre-flight gate.

Gate failures (pre-audit):
  - grid sync : PASS (0 off-grid)
  - harmony   : FAIL -> 1 scale violation (bar 8 pad E-natural) +
                        56 chord violations (lead PCFG line ignores chord tones)
  - zero-drift: PASS

Rework (two-phase):
  phase1 sidecar = raw original (keep character)
  phase2 = chord-tone quantize lead + reharmonize bar 8 pad to Cm (in C Dorian)

Uses the musicom engine (UnitMatrixComposer), mido READ-ONLY for extraction.
"""
import json
import os
import shutil
from datetime import datetime, timezone

import mido
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

PROJ = "/opt/data/repos/musicom/projects/Styles/Experimental/048-pcfg-binaural"
SRC_MIDI = os.path.join(PROJ, "MIDI", "048-pcfg-binaural.mid")
PHASE1 = os.path.join(PROJ, "MIDI", "048-pcfg-binaural-phase1.mid")

TPB = 480
BAR = 1920
NBARS = 8
BPM = 100

# Reworked chord pitch-class sets per bar (C Dorian harmony, picardy -> Cm).
CHORD_PCS = [
    {0, 3, 7, 10},   # bar1 Cm7
    {5, 9, 0, 3},    # bar2 F7
    {10, 2, 5},      # bar3 Bb
    {3, 7, 10, 2},   # bar4 EbMaj7
    {0, 3, 7, 10},   # bar5 Cm7
    {5, 9, 0, 3},    # bar6 F7
    {7, 10, 2, 5},   # bar7 Gm7
    {0, 3, 7},       # bar8 Cm (picardy E->Eb fixed)
]

VOICES = [
    ("Lead", 40, 0),
    ("Pad", 89, 1),
    ("Bass", 32, 2),
]


def snap_to_chord(note, bar):
    pcs = CHORD_PCS[bar]
    cands = [n for n in range(note - 12, note + 13)
             if 0 <= n <= 127 and n % 12 in pcs]
    return min(cands, key=lambda n: abs(n - note))


def extract_events(track):
    """Return [(start_tick, end_tick, note, velocity)] absolute ticks."""
    events = []
    tick = 0
    open_notes = {}
    for m in track:
        tick += m.time
        if m.type == "note_on" and m.velocity > 0:
            open_notes[m.note] = (tick, m.velocity)
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            if m.note in open_notes:
                st, vel = open_notes.pop(m.note)
                events.append((st, tick, m.note, vel))
    return events


# 1. Preserve raw as phase-1 sidecar
if not os.path.exists(PHASE1):
    shutil.copy2(SRC_MIDI, PHASE1)
    print(f"phase1 sidecar written: {PHASE1}")

mid = mido.MidiFile(SRC_MIDI)
# track 0 = tempo meta; tracks 1..3 = Lead, Pad, Bass (order matches VOICES)
voice_tracks = mid.tracks[1:]
assert len(voice_tracks) == len(VOICES), "unexpected track count"

# 2. Extract per-voice absolute events
voice_events = [extract_events(t) for t in voice_tracks]

# 3. Build reworked matrix via engine
c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
c.create_matrix(num_voices=len(VOICES), num_sections=NBARS)
for name, prog, ch in VOICES:
    c.add_voice(name, program=prog, channel=ch)
for s in range(NBARS):
    c.add_section(f"Bar{s+1}", bars=1)

stats = {"lead_snapped": 0, "pad_fixed": 0}
for vi, (name, prog, ch) in enumerate(VOICES):
    evs = voice_events[vi]
    for s in range(NBARS):
        lo, hi = s * BAR, (s + 1) * BAR
        rel_events = []
        for (st, en, note, vel) in evs:
            if not (lo <= st < hi):
                continue
            r_st = st - lo
            r_en = min(en - lo, BAR)
            if name == "Lead":
                new_note = snap_to_chord(note, s)
                if new_note != note:
                    stats["lead_snapped"] += 1
                note = new_note
            elif name == "Pad" and s == 7 and note == 52:
                note = 51  # E -> Eb, keeps pad in C Dorian
                stats["pad_fixed"] += 1
            rel_events.append(MusicEvent(pitch=note, volume=vel,
                                         start_tick=r_st, end_tick=r_en))
        # terminal landmark at BAR guarantees zero-drift
        rel_events.append(MusicEvent(pitch=0, volume=0, start_tick=BAR, end_tick=BAR))
        c.fill_voice_section(name, f"Bar{s+1}", MusicUnit(events=rel_events))

ok, msg = c.validate()
print(f"validate: {ok} ({msg})")
if not ok:
    raise SystemExit(f"Rework validate failed: {msg}")

c.to_midi(SRC_MIDI)
print(f"re-exported reworked MIDI: {SRC_MIDI} ({os.path.getsize(SRC_MIDI)} bytes)")
print("rework stats:", json.dumps(stats))

# 4. Provenance sidecar for reworked artifact
prov = {
    "artifact": "048-pcfg-binaural.mid",
    "classification": "ai-assisted (reworked)",
    "generator": "Experimental/048-pcfg-binaural/_cron_rework_048.py",
    "parameters": {
        "bpm": BPM,
        "key": "C Dorian",
        "methods": ["034", "SP-021"],
        "rework": "pre-flight 3-rule gate: chord-tone quantize lead, bar-8 pad E->Eb (Cm)",
    },
    "rework_stats": stats,
    "rework_utc": datetime.now(timezone.utc).isoformat(),
}
with open(SRC_MIDI + ".provenance.json", "w") as f:
    json.dump(prov, f, indent=2)
print("provenance updated")
