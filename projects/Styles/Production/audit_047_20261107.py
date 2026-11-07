# -*- coding: utf-8 -*-
"""Pre-flight rules audit + MIDI readback for 047-physarum-bowed.mid.

Three rules:
1. Grid sync    — every pitched-voice onset on the 8th/16th grid (120/240 ticks).
2. Harmony      — every pitched note in Bb-major scale AND a chord tone of its bar.
3. Zero-drift   — all note tracks equal length; validate() equivalence via track span.
"""
import json
import mido

SRC = ("/opt/data/repos/musicom/projects/Styles/Experimental/"
       "047-physarum-bowed/MIDI/047-physarum-bowed.mid")

BPM = 110
TPB = 480
BEATS = 4
BAR = TPB * BEATS          # 1920
NBARS = 8

# Bb major scale pcs
SCALE = {10, 0, 2, 3, 5, 7, 9}
# chord tones per bar (2-bar sections): Eb, Eb, F, F, Gm, Gm, Bb, Bb
CHORD_TONES = [
    {3, 7, 10},   # Eb major (Eb G Bb)
    {3, 7, 10},
    {5, 9, 0},    # F major (F A C)
    {5, 9, 0},
    {7, 10, 2},   # G minor (G Bb D)
    {7, 10, 2},
    {10, 2, 5},   # Bb major (Bb D F)
    {10, 2, 5},
]

GRID = 120  # 16th-note grid

mf = mido.MidiFile(SRC)
print("ticks_per_beat =", mf.ticks_per_beat, " length_s =", round(mf.length, 2))

tracks = []
for ti, tr in enumerate(mf.tracks):
    t = 0
    notes = []
    progs = []
    for m in tr:
        t += m.time
        if m.type == "program_change":
            progs.append(m.program)
        if m.type == "note_on" and m.velocity > 0:
            notes.append({"note": m.note, "vel": m.velocity, "on": t})
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            # close matching open note
            for n in reversed(notes):
                if n["note"] == m.note and "off" not in n:
                    n["off"] = t
                    break
    # assign off = on+something if missing
    for n in notes:
        if "off" not in n:
            n["off"] = n["on"] + 120
    end = max((n["off"] for n in notes), default=0)
    tracks.append({"index": ti, "progs": progs, "notes": notes, "span": end})
    print(f"track {ti}: progs={progs} notes={len(notes)} span={end} ticks")

# --- rule 3: zero-drift (note-bearing tracks equal span) ---
note_tracks = [t for t in tracks if t["notes"]]
spans = sorted({t["span"] for t in note_tracks})
print("\nnote-track spans:", spans, "-> zero-drift",
      "PASS" if len(spans) == 1 else "FAIL")

# --- rule 1: grid sync ---
off_grid = 0
total_onsets = 0
for t in note_tracks:
    for n in t["notes"]:
        total_onsets += 1
        if n["on"] % GRID != 0:
            off_grid += 1
print("grid: %d/%d onsets off-grid (grid=%d)" % (off_grid, total_onsets, GRID))

# --- rule 2: harmony (scale + chord tone) ---
out_scale = 0
out_chord = 0
pitched = 0
for t in note_tracks:
    for n in t["notes"]:
        pc = n["note"] % 12
        bar = min(n["on"] // BAR, NBARS - 1)
        pitched += 1
        if pc not in SCALE:
            out_scale += 1
        if pc not in CHORD_TONES[bar]:
            out_chord += 1

print("harmony: %d/%d out-of-scale, %d/%d out-of-chord" %
      (out_scale, pitched, out_chord, pitched))

result = {
    "src": SRC, "bpm": BPM, "tpb": TPB, "bar_ticks": BAR, "nbars": NBARS,
    "scale_pcs": sorted(SCALE),
    "note_tracks": len(note_tracks),
    "track_spans": sorted(spans),
    "zero_drift_pass": len(spans) == 1,
    "grid_pass": off_grid == 0,
    "scale_pass": out_scale == 0,
    "chord_pass": out_chord == 0,
    "off_grid": off_grid, "total_onsets": total_onsets,
    "out_scale": out_scale, "out_chord": out_chord, "pitched": pitched,
}
print("\nAUDIT:", json.dumps(result, indent=2))
