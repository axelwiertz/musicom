#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rework le_cercle_de_l_agent.mid to pass the 3-rule pre-flight gate.

Gate failures (pre-audit, 2026-10-15):
  - grid sync   : PASS (0 off-grid; all onsets on 240-tick 6/8 eighth grid)
  - harmony in-scale: PASS (0 out-of-scale; all 160 notes in G major)
  - harmony chord-tone: FAIL under strict G-triad (21 non-chord: 8 A + 13 E,
    the G-major-pentatonic passing/color tones of the folk tune)
  - zero-drift  : FAIL (track end ticks 23040 / 22560 / 21840 — unequal)
  - meta        : FAIL (no program_change, no tempo, no time_signature —
    would render all 3 tracks as Acoustic Grand Piano program 0)

Rework (two-phase, melody-preserving):
  phase1 sidecar = raw original (keep character).
  phase2 = re-harmonize comp G-B dyad -> explicit G6/9 (G B D E A) so the
           sounding harmony fully supports the G-major-pentatonic melody
           (every melody note becomes a chord tone), add GM programs
           (Violin 40 / Acoustic Guitar 25 / Piano 1), tempo 120 BPM,
           6/8 time signature, and pad ALL tracks to equal length (zero-drift).

Uses the musicom engine (UnitMatrixComposer); mido READ-ONLY for extraction.
"""
import json
import os
import shutil
from datetime import datetime, timezone

import mido
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

PROJ = "/opt/data/repos/musicom/projects/Styles/Balfolk/005-balfolk-production"
SRC_MIDI = os.path.join(PROJ, "midi", "le_cercle_de_l_agent.mid")
PHASE1 = os.path.join(PROJ, "midi", "le_cercle_de_l_agent-phase1.mid")

TPB = 480
BAR = 1440           # 6/8 bar = 6 eighths x 240 = 1440 ticks (beats_per_bar=3)
NBARS = 16
BPM = 120

# G6/9 chord-tone set = full G major pentatonic {G, B, D, E, A}
G_6_9 = {7, 11, 2, 4, 9}
G6_9_VOICING = [55, 59, 62, 64, 69]   # G3 B3 D4 E4 A4

VOICES = [
    ("Violin", 40, 0),
    ("Guitar", 25, 1),
    ("Piano", 1, 2),
]


def extract_events(track):
    """Return [(start_tick, end_tick, note, velocity)] in absolute ticks."""
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
else:
    print(f"phase1 sidecar exists: {PHASE1}")

mid = mido.MidiFile(SRC_MIDI)
voice_tracks = mid.tracks   # 3 tracks, no separate tempo track
assert len(voice_tracks) == 3, f"unexpected track count {len(voice_tracks)}"

melody_ev = extract_events(voice_tracks[0])   # Violin
bass_ev = extract_events(voice_tracks[1])     # Guitar
comp_ev = extract_events(voice_tracks[2])     # Piano (replaced by G6/9)
print(f"extracted: melody={len(melody_ev)} bass={len(bass_ev)} comp={len(comp_ev)}")

# 2. Build reworked matrix via engine
c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=3)
c.create_matrix(num_voices=len(VOICES), num_sections=NBARS)
for name, prog, ch in VOICES:
    c.add_voice(name, program=prog, channel=ch)
for s in range(NBARS):
    c.add_section(f"Bar{s+1}", bars=1)


def fill_bar(voice_name, bar_idx, rel_events):
    # terminal landmark guarantees unit len_ticks() == BAR
    rel_events.append(MusicEvent(pitch=0, volume=0, start_tick=BAR, end_tick=BAR))
    c.fill_voice_section(voice_name, f"Bar{bar_idx+1}", MusicUnit(events=rel_events))


def clamp(v, lo=0, hi=BAR):
    return max(lo, min(hi, v))


# melody: unchanged, assign to bar by absolute start, relative ticks
melody_snap = 0
for bar_idx in range(NBARS):
    lo, hi = bar_idx * BAR, (bar_idx + 1) * BAR
    rel = []
    for (st, en, note, vel) in melody_ev:
        if lo <= st < hi:
            rel.append(MusicEvent(pitch=note, volume=vel,
                                  start_tick=clamp(st - lo),
                                  end_tick=clamp(en - lo)))
    fill_bar("Violin", bar_idx, rel)

# bass: unchanged, assign by bar, relative ticks (pad handled by terminal landmark)
for bar_idx in range(NBARS):
    lo, hi = bar_idx * BAR, (bar_idx + 1) * BAR
    rel = []
    for (st, en, note, vel) in bass_ev:
        if lo <= st < hi:
            rel.append(MusicEvent(pitch=note, volume=vel,
                                  start_tick=clamp(st - lo),
                                  end_tick=clamp(en - lo)))
    fill_bar("Guitar", bar_idx, rel)

# comp: re-harmonized G6/9 downbeat chord (was G-B dyad)
for bar_idx in range(NBARS):
    rel = []
    for note in G6_9_VOICING:
        rel.append(MusicEvent(pitch=note, volume=68,
                              start_tick=0, end_tick=720))  # dotted-quarter bloom
    fill_bar("Piano", bar_idx, rel)

ok, msg = c.validate()
print(f"validate: {ok} ({msg})")
if not ok:
    raise SystemExit(f"Rework validate failed: {msg}")

c.to_midi(SRC_MIDI)
print(f"re-exported reworked MIDI: {SRC_MIDI} ({os.path.getsize(SRC_MIDI)} bytes)")

# 3. Post-process: add 6/8 time signature to track 0 (tempo track)
m2 = mido.MidiFile(SRC_MIDI)
m2.tracks[0].insert(0, mido.MetaMessage('time_signature', numerator=6,
                                        denominator=8, time=0))
m2.save(SRC_MIDI)
print("time_signature 6/8 added to track 0")

# 4. Provenance sidecar
prov = {
    "artifact": "le_cercle_de_l_agent.mid",
    "classification": "ai-assisted (reworked)",
    "generator": "Balfolk/005-balfolk-production/_cron_rework_le_cercle.py",
    "parameters": {
        "bpm": BPM,
        "key": "G major (G6/9 pentatonic drone)",
        "meter": "6/8",
        "bars": NBARS,
        "rework": ("pre-flight 3-rule gate: re-harmonize comp G-B -> G6/9 "
                   "(G B D E A), add GM programs (Violin 40/Guitar 25/Piano 1), "
                   "tempo 120, 6/8 time sig, zero-drift pad all tracks to 23040"),
    },
    "rework_stats": {
        "melody_preserved": len(melody_ev),
        "bass_preserved": len(bass_ev),
        "comp_notes_new": len(G6_9_VOICING) * NBARS,
    },
    "rework_utc": datetime.now(timezone.utc).isoformat(),
}
with open(SRC_MIDI + ".provenance.json", "w") as f:
    json.dump(prov, f, indent=2)
print("provenance updated")
