# -*- coding: utf-8 -*-
"""Rework 052-perlin-chebyshev.mid: chord-tone quantize the lead voice.

Pre-flight audit found 34 out-of-chord lead notes (all in track 1 / flute):
  - G  (pc 7)  repeated over Dm7 (21 x)
  - Bb (pc 10) repeated over Dm7 (5 x)
  - E  (pc 4)  repeated over Dm7 (8 x)

Everything else is clean: 0 off-grid, 0 out-of-scale (all 72 onsets in D
natural minor), zero-drift (3 note tracks x 23040 ticks).  Harmony is a static
Dm7 (D F A C = pc {2,5,9,0}) across all 12 bars (pad = Dm7 sustains, bass =
D/F/A roots).  Fix = snap each non-chord lead note to the nearest chord tone of
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
       "052-perlin-chebyshev/MIDI/052-perlin-chebyshev.mid")

OUT_DIR = ("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP154-wax-theory-vinyl-052-perlin-chebyshev")
MID = os.path.join(OUT_DIR, "MIDI")
os.makedirs(MID, exist_ok=True)

BPM = 100
TPB = 480
BAR = 1920          # 4/4 bar
NBARS = 12          # 3 sections x 4 bars
NSEC = 3
BARS_PER_SEC = 4
SECTION = BARS_PER_SEC * BAR   # 7680

# voices, in composer order (row 0,1,2) with their GM programs
VOICES = [
    ("Lead", 74, 0),   # flute
    ("Pad", 88, 1),    # new age pad
    ("Bass", 33, 2),   # electric bass finger
]

# D natural minor scale pcs
SCALE = {2, 4, 5, 7, 9, 10, 0}
# chord tones per section (static Dm7 = D F A C across all 12 bars)
CHORD_TONES = [{2, 5, 9, 0}] * NBARS


def read_tracks():
    mf = mido.MidiFile(SRC)
    out = []
    for tr in mf.tracks:
        t = 0
        notes = []
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                notes.append({"note": m.note, "vel": m.velocity,
                              "on": t, "off": None})
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
composer.create_matrix(num_voices=3, num_sections=NSEC)
for name, prog, ch in VOICES:
    composer.add_voice(name, program=prog, channel=ch)
for s in range(NSEC):
    composer.add_section(f"Sec{s+1}", bars=BARS_PER_SEC)

quantized = []   # per voice: per section event lists
for vi, notes in enumerate(tracks):
    q = []
    for s in range(NSEC):
        lo = s * SECTION
        hi = lo + SECTION
        events = []
        for n in notes:
            if lo <= n["on"] < hi:
                pitch = n["note"]
                bar_idx = n["on"] // BAR
                bar_chord = CHORD_TONES[bar_idx]
                pc = pitch % 12
                if vi == 0 and pc not in bar_chord:
                    before_ooc += 1
                    pitch = snap_to_chord(pitch, bar_chord)
                rel_on = n["on"] - lo
                rel_off = min(n["off"] - lo, SECTION)
                events.append(MusicEvent(
                    pitch=pitch, volume=n["vel"],
                    start_tick=rel_on, end_tick=rel_off))
        # terminal landmark to guarantee unit length == SECTION
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION - 1, end_tick=SECTION))
        q.append(MusicUnit(events=events))
    quantized.append(q)

# fill cells
for vi, (name, prog, ch) in enumerate(VOICES):
    for s in range(NSEC):
        composer.fill_voice_section(name, f"Sec{s+1}", quantized[vi][s])

ok, msg = composer.validate()
print("validate:", ok, msg)
assert ok, msg

out_midi = os.path.join(MID, "052-perlin-chebyshev.mid")
composer.to_midi(out_midi)
print("reworked MIDI:", out_midi, os.path.getsize(out_midi), "bytes")

# phase1 sidecar = original raw
phase1 = os.path.join(MID, "052-perlin-chebyshev-phase1.mid")
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
assert len(spans) == 1, "zero-drift violated after rework"
print("REWORK CLEAN")
