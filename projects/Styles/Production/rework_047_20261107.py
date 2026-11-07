# -*- coding: utf-8 -*-
"""Rework 047-physarum-bowed.mid: chord-tone quantize the lead voice.

Pre-flight audit found 38 out-of-chord lead notes (all in track 1 / violin):
  - Eb4 (pc 3) repeated over the F-major section (bars 2-3)
  - G4  (pc 7) repeated over F-major (bar 3)
  - G3  (pc 7) over Bb-major (bars 6-7)

Everything else is clean: 0 off-grid, 0 out-of-scale, zero-drift (3 tracks x
15360 ticks).  Fix = snap each non-chord lead note to the nearest chord tone of
its bar (minimal |semitone| move, tie -> lower note).  Preserves grid, scale,
velocity, durations, and zero-drift.  Raw draft kept as a phase1 sidecar.

Uses the musicom engine (UnitMatrixComposer) for the re-export, no raw mido
writing.
"""
import os
import shutil
import json

import mido

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

SRC = ("/opt/data/repos/musicom/projects/Styles/Experimental/"
       "047-physarum-bowed/MIDI/047-physarum-bowed.mid")

OUT_DIR = ("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP146-feedback-loop-fx-047-physarum-bowed")
MID = os.path.join(OUT_DIR, "MIDI")
os.makedirs(MID, exist_ok=True)

BPM = 110
TPB = 480
BAR = 1920
NBARS = 8

# voices, in composer order (row 0,1,2) with their GM programs
VOICES = [
    ("Lead", 40, 0),
    ("Pad", 88, 1),
    ("Bass", 33, 2),
]

# Bb major scale pcs
SCALE = {10, 0, 2, 3, 5, 7, 9}
# chord tones per bar (Eb,Eb,F,F,Gm,Gm,Bb,Bb)
CHORD_TONES = [
    {3, 7, 10}, {3, 7, 10},
    {5, 9, 0}, {5, 9, 0},
    {7, 10, 2}, {7, 10, 2},
    {10, 2, 5}, {10, 2, 5},
]


def read_tracks():
    mf = mido.MidiFile(SRC)
    out = []
    for ti, tr in enumerate(mf.tracks):
        t = 0
        notes = []
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                notes.append({"note": m.note, "vel": m.velocity, "on": t, "off": None})
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                for n in reversed(notes):
                    if n["note"] == m.note and n["off"] is None:
                        n["off"] = t
                        break
        for n in notes:
            if n["off"] is None:
                n["off"] = n["on"] + 120
        if notes:
            out.append(notes)
    return out


def snap_to_chord(pitch, chord_tones):
    pc = pitch % 12
    if pc in chord_tones:
        return pitch
    best = None
    best_d = 999
    for ct in chord_tones:
        delta = ((ct - pc + 6) % 12) - 6   # signed -6..+6
        cand = pitch + delta
        d = abs(delta)
        if d < best_d or (d == best_d and cand < best):
            best_d = d
            best = cand
    return best


tracks = read_tracks()
assert len(tracks) == 3, "expected 3 note tracks, got %d" % len(tracks)

# before/after counters
before_ooc = 0
after_ooc = 0

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=3, num_sections=NBARS)
for name, prog, ch in VOICES:
    composer.add_voice(name, program=prog, channel=ch)
for s in range(NBARS):
    composer.add_section(f"Bar{s+1}", bars=1)

quantized = []   # list per voice of per-section event lists
for vi, notes in enumerate(tracks):
    q = []
    for s in range(NBARS):
        lo = s * BAR
        hi = lo + BAR
        events = []
        for n in notes:
            if lo <= n["on"] < hi:
                pitch = n["note"]
                bar_chord = CHORD_TONES[s]
                pc = pitch % 12
                if vi == 0 and pc not in bar_chord:
                    before_ooc += 1
                    pitch = snap_to_chord(pitch, bar_chord)
                rel_on = n["on"] - lo
                rel_off = min(n["off"] - lo, BAR)
                events.append(MusicEvent(
                    pitch=pitch, volume=n["vel"],
                    start_tick=rel_on, end_tick=rel_off))
        # terminal landmark to guarantee unit length == BAR (skipped in MIDI out)
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=BAR - 1, end_tick=BAR))
        q.append(MusicUnit(events=events))
    quantized.append(q)

# fill cells
for vi, (name, prog, ch) in enumerate(VOICES):
    for s in range(NBARS):
        composer.fill_voice_section(name, f"Bar{s+1}", quantized[vi][s])

ok, msg = composer.validate()
print("validate:", ok, msg)
assert ok, msg

out_midi = os.path.join(MID, "047-physarum-bowed.mid")
composer.to_midi(out_midi)
print("reworked MIDI:", out_midi, os.path.getsize(out_midi), "bytes")

# phase1 sidecar = original raw
phase1 = os.path.join(MID, "047-physarum-bowed-phase1.mid")
shutil.copyfile(SRC, phase1)
print("phase1 sidecar:", phase1, os.path.getsize(phase1), "bytes")

# re-audit the output
mf = mido.MidiFile(out_midi)
off_grid = 0
out_scale = 0
out_chord = 0
total = 0
spans = set()
for tr in mf.tracks:
    t = 0
    notes = []
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            notes.append({"note": m.note, "on": t, "off": None})
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            for n in reversed(notes):
                if n["note"] == m.note and n["off"] is None:
                    n["off"] = t
                    break
    if not notes:
        continue
    spans.add(max(n["off"] for n in notes))
    for n in notes:
        total += 1
        if n["on"] % 120 != 0:
            off_grid += 1
        pc = n["note"] % 12
        bar = min(n["on"] // BAR, NBARS - 1)
        if pc not in SCALE:
            out_scale += 1
        if pc not in CHORD_TONES[bar]:
            out_chord += 1

audit = {
    "off_grid": off_grid, "out_scale": out_scale, "out_chord": out_chord,
    "total_onsets": total, "track_spans": sorted(spans),
    "zero_drift": len(spans) == 1,
}
print("re-audit:", json.dumps(audit))
print("before out-of-chord:", before_ooc, "-> after:", out_chord)

with open(os.path.join(MID, "rework_audit.json"), "w") as f:
    json.dump({"before_out_of_chord": before_ooc, "after": audit}, f, indent=2)

assert out_chord == 0, "chord-tone rework did not reach 0"
assert off_grid == 0 and out_scale == 0
print("REWORK CLEAN")
