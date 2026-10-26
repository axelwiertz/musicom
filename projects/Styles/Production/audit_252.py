# -*- coding: utf-8 -*-
"""Pre-flight 3-rule audit of source 252-balkan-spectral-extended-perfect.mid."""
import mido
from pathlib import Path

SRC = Path("/opt/data/repos/musicom/projects/Styles/Balkan/"
           "252-balkan-spectral-extended/MIDI/252-balkan-spectral-extended-perfect.mid")

mf = mido.MidiFile(str(SRC))
print("TPB =", mf.ticks_per_beat)
print("length (s) =", round(mf.length, 2))
print("n_tracks =", len(mf.tracks))

# tempo
for tr in mf.tracks:
    for m in tr:
        if m.type == "set_tempo":
            print("tempo = %.1f BPM" % (60_000_000 / m.tempo))

TPB = mf.ticks_per_beat
GRID = 120  # 16th
BAR = 1680  # 7/8 bar = 7 eighths * 240 = 1680 ticks (verify below)

# G Dorian pitch classes: G A Bb C D E F
SCALE_PCS = {7, 9, 10, 0, 2, 4, 5}

# degree -> chord-tone pitch classes (G Dorian diatonic triads)
# i=Gmin, ii=Amin, III=Bbmaj, IV=Cmaj, v=Dmin, VII=Fmaj
CHORD_PCS = {
    "i":   {7, 10, 2},
    "ii":  {9, 0, 4},
    "III": {10, 2, 5},
    "IV":  {0, 4, 7},
    "v":   {2, 5, 9},
    "VII": {5, 9, 0},
}
PROG_DEG = ["i","i","VII","VII","i","VII","IV","i",
            "IV","ii","VII","v","III","VII","IV","i",
            "v","IV","ii","VII","VII","IV","ii","v",
            "IV","VII","i","IV","i","VII","IV","i"]
N_BARS = 32
print("PROG len =", len(PROG_DEG))

grid_off = 0
off8 = 0
out_scale = 0
out_chord = 0
track_ends = []
total_notes = 0
per_track = []
# per-bar pitch-class sets (pitched voices only) to sanity check chord map
bar_pcs = [set() for _ in range(N_BARS)]

for ti, tr in enumerate(mf.tracks):
    chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
    is_drum = 9 in chans
    names = [m.name for m in tr if m.type == "track_name"]
    progs = [m.program for m in tr if m.type == "program_change"]
    t = 0
    n = 0
    max_end = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            n += 1
            total_notes += 1
            max_end = max(max_end, t)
            if is_drum:
                continue
            if (t % GRID) != 0:
                grid_off += 1
            if (t % 240) != 0:
                off8 += 1
            pc = m.note % 12
            if pc not in SCALE_PCS:
                out_scale += 1
            bar = min(t // BAR, N_BARS - 1)
            bar_pcs[bar].add(pc)
            deg = PROG_DEG[bar]
            if pc not in CHORD_PCS[deg]:
                out_chord += 1
    if n:
        track_ends.append(max_end)
    per_track.append((ti, names, progs, is_drum, n, max_end))

for row in per_track:
    print("track", row)
print("total_notes =", total_notes)
print("grid_off =", grid_off, " off8 =", off8, " out_scale =", out_scale,
      " out_chord =", out_chord)
print("track_ends =", sorted(set(track_ends)))
print("zero_drift =", len(set(track_ends)) == 1)

# dump a few bar pitch-class sets vs chord map to sanity check
for b in range(8):
    deg = PROG_DEG[b]
    print("bar %2d deg=%-3s chord_pcs=%s actual_pcs=%s"
          % (b, deg, sorted(CHORD_PCS[deg]), sorted(bar_pcs[b])))
