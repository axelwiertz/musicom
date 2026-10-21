# -*- coding: utf-8 -*-
"""Pre-flight 3-rule audit of 012-country-country-uke v2 (2026-10-21)."""
import json
import mido

SRC = "/opt/data/repos/musicom/projects/Styles/Country/012-country-country-uke/MIDI/v2_country_unitmatrix.mid"

BAR = 1920  # 480 TPB * 4 beats
GRID = 120  # 16th ticks

GMAJ_PCS = {7, 9, 11, 0, 2, 4, 6}  # G A B C D E F#

CHORD_TONES = {
    "G": {7, 11, 2},
    "D": {2, 6, 9},
    "Em": {4, 7, 11},
    "C": {0, 4, 7},
}

# 48-bar progression (intro 4 + verse 8 + chorus 8 + verse 8 + chorus 8
# + bridge 4 + final chorus 4 + outro 4)
PROG = []
PROG += ["G", "D", "Em", "C"]                       # Intro (0-3)
PROG += ["G", "D", "Em", "C", "G", "D", "C", "D"]   # Verse 1 (4-11)
PROG += ["G", "D", "Em", "C", "G", "D", "C", "D"]   # Chorus 1 (12-19)
PROG += ["G", "D", "Em", "C", "G", "D", "C", "D"]   # Verse 2 (20-27)
PROG += ["G", "D", "Em", "C", "G", "D", "C", "D"]   # Chorus 2 (28-35)
PROG += ["Em", "C", "G", "D"]                       # Bridge (36-39)
PROG += ["G", "D", "C", "D"]                        # Final Chorus (40-43)
PROG += ["G", "C", "G", "G"]                        # Outro (44-47)
assert len(PROG) == 48, len(PROG)


def chord_pcs(bar):
    return CHORD_TONES[PROG[min(bar, 47)]]


mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat
print("TPB:", tpb, "length:", round(mf.length, 3), "tracks:", len(mf.tracks))

tempo = None
for tr in mf.tracks:
    for m in tr:
        if m.type == "set_tempo":
            tempo = m.tempo
print("bpm:", round(mido.tempo2bpm(tempo), 2) if tempo else None)

track_lengths = []
pitched = []
for ti, tr in enumerate(mf.tracks):
    t = 0
    prog = None
    notes = []
    for m in tr:
        t += m.time
        if m.type == "program_change":
            prog = m.program
        if m.type == "note_on" and m.velocity > 0:
            notes.append((m.note, m.velocity, t, m.channel))
    track_lengths.append(t)
    if notes:
        ch = notes[0][3]
        pitched.append((ti, ch, prog, notes))

# zero-drift: all note tracks (exclude track 0 tempo track) equal end tick
note_ends = [track_lengths[ti] for ti, *_ in pitched]
print("\nTrack end ticks (note tracks):", note_ends)
print("Zero-drift:", "PASS" if len(set(note_ends)) == 1 else
      f"FAIL (distinct: {sorted(set(note_ends))})")

print("\n=== per-track audit ===")
tot_off_grid = 0
tot_out_scale = 0
tot_out_chord = 0
tot_notes = 0
for ti, ch, prog, notes in pitched:
    is_drum = ch == 9
    off_grid = 0
    out_scale = 0
    out_chord = 0
    off_grid_examples = []
    out_chord_examples = []
    for note, vel, t, c in notes:
        tot_notes += 1
        if t % GRID != 0:
            off_grid += 1
            if len(off_grid_examples) < 6:
                off_grid_examples.append((note, t, t % GRID))
        if not is_drum:
            pc = note % 12
            if pc not in GMAJ_PCS:
                out_scale += 1
            bar = t // BAR
            if pc not in chord_pcs(bar):
                out_chord += 1
                if len(out_chord_examples) < 6:
                    out_chord_examples.append((note, pc, t, PROG[bar], bar))
    if is_drum:
        print(f"track {ti} ch9 DRUM: n={len(notes)} off_grid={off_grid}")
        tot_off_grid += off_grid
        continue
    tot_off_grid += off_grid
    tot_out_scale += out_scale
    tot_out_chord += out_chord
    print(f"track {ti} ch{ch} prog={prog}: n={len(notes)} "
          f"off_grid={off_grid} out_scale={out_scale} out_chord={out_chord}")
    if off_grid_examples:
        print(f"    off-grid eg: {off_grid_examples}")
    if out_chord_examples:
        print(f"    out-chord eg (note,pc,tick,chord,bar): {out_chord_examples}")

print("\n=== TOTALS (pitched) ===")
print("total notes:", tot_notes)
print("off-grid:", tot_off_grid)
print("out-of-scale:", tot_out_scale)
print("out-of-chord:", tot_out_chord)
print("\nGrid sync:", "PASS" if tot_off_grid == 0 else f"FAIL ({tot_off_grid})")
print("In-scale:", "PASS" if tot_out_scale == 0 else f"FAIL ({tot_out_scale})")
print("Chord-tone:", "PASS" if tot_out_chord == 0 else f"FAIL ({tot_out_chord})")

json.dump({
    "source": SRC, "bpm": round(mido.tempo2bpm(tempo), 2),
    "off_grid": tot_off_grid, "out_scale": tot_out_scale,
    "out_chord": tot_out_chord, "notes": tot_notes,
    "note_track_ends": note_ends,
}, open("/opt/data/projects/Styles/Production/_audit_20261021.json", "w"), indent=2)
