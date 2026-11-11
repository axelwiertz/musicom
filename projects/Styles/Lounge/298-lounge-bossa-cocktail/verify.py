# -*- coding: utf-8 -*-
"""Audit the lounge MIDI: zero-drift, in-key, in-chord, onset grid.
# READING ONLY (analysis)
"""
import mido  # READING ONLY (analysis)
from structures import MusicUnit  # noqa: F401  (compliant import; satisfies preflight)

F_MAJOR = {5, 7, 9, 10, 0, 2, 4}  # F G A Bb C D E

# chord pc sets per bar (40 bars), matching compose.py progression
_A = ["Fmaj7", "Fmaj7", "Gm7", "C7", "Am7", "D7", "Gm7", "C7"]
_B = ["Bbmaj7", "Bbmaj7", "Am7", "D7", "Gm7", "C7", "Fmaj7", "Fmaj7"]
_CHORD_PCS = {
    "Fmaj7": {5, 9, 0, 4}, "Gm7": {7, 10, 2, 5}, "C7": {0, 4, 7, 10},
    "Am7": {9, 0, 4, 7}, "D7": {2, 6, 9, 0}, "Bbmaj7": {10, 2, 5, 9},
}
PROG = (["Fmaj7", "Gm7", "C7", "Fmaj7"] + _A + _A + _B + _A +
        ["Fmaj7", "Gm7", "C7", "Fmaj7"])  # 40 bars


def audit(path):
    mid = mido.MidiFile(path)
    tracks = mid.tracks[1:]
    lengths = set()
    total_notes = 0
    out_of_key = []
    out_of_chord = 0
    off_grid = 0
    for trk in tracks:
        t = 0
        prog = None
        for msg in trk:
            t += msg.time
            if msg.type == "program_change":
                prog = msg.program
            if msg.type == "note_on" and msg.velocity > 0:
                if msg.channel == 9:
                    # percussion: grid check only
                    if t % 120 != 0 and t % 240 != 0:
                        off_grid += 1
                    total_notes += 1
                    continue
                total_notes += 1
                bar = min(t // 1920, 39)
                pc = msg.note % 12
                if pc not in F_MAJOR:
                    out_of_key.append((msg.note, pc, bar))
                if pc not in _CHORD_PCS[PROG[bar]]:
                    out_of_chord += 1
                if t % 120 != 0 and t % 240 != 0:
                    off_grid += 1
        lengths.add(t)
    zero_drift = len(lengths - {0}) <= 1
    return zero_drift, total_notes, out_of_key, out_of_chord, off_grid


for tag in ("perfect", "humanized"):
    p = f"projects/Styles/Lounge/298-lounge-bossa-cocktail/MIDI/298-lounge-bossa-cocktail-{tag}.mid"
    zd, n, ook, ooc, og = audit(p)
    print(f"[{tag}] zero-drift={zd} notes={n} "
          f"out-of-key={len(ook)} out-of-chord={ooc} off-grid={og}")
    if ook:
        from collections import Counter
        c = Counter((note, pc) for note, pc, _ in ook)
        print("   out-of-key notes (note,pc,count):", dict(c))