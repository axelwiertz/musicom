# -*- coding: utf-8 -*-
"""Chorale DNA grid: 8 cells (columns) x 4 voices (rows) from the source MIDI.
Pitch classes shown per voice; W = whole-note (2.5 s) per cell.
Also writes a high-contrast ASCII grid for the README."""
import json
import sys

import mido

midi_path = sys.argv[1]
out_json = sys.argv[2]
out_txt = sys.argv[3]

mid = mido.MidiFile(midi_path)

def tick_to_sec(tick):
    abs_tempos = []
    at = 0
    for m in mid.tracks[0]:
        at += m.time
        if m.type == "set_tempo":
            abs_tempos.append((at, m.tempo))
    if not abs_tempos:
        abs_tempos = [(0, 500000)]
    sec = 0.0
    prev = 0
    tempo = abs_tempos[0][1]
    for at, tmp in abs_tempos:
        if tick <= at:
            break
        sec += (at - prev) * tempo / mid.ticks_per_beat / 1e6
        prev = at
        tempo = tmp
    sec += (tick - prev) * tempo / mid.ticks_per_beat / 1e6
    return sec

CELL = 2.5  # seconds per cell (whole note @ 96 BPM = 2.5 s)
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

cells = {}  # (track, cell) -> pitch
for ti, track in enumerate(mid.tracks):
    if ti == 0:
        continue
    abstick = 0
    for m in track:
        abstick += m.time
        if m.type == "note_on" and m.velocity > 0:
            cell = int(tick_to_sec(abstick) // CELL)
            cells[(ti, cell)] = m.note

voices = sorted({k[0] for k in cells})
rows = []
for ti in voices:
    row = []
    for c in range(8):
        p = cells.get((ti, c))
        row.append({"cell": c, "pitch": p,
                    "pc": NAMES[p % 12] if p is not None else None})
    rows.append(row)

# voice labels by program
programs = {}
for ti, track in enumerate(mid.tracks):
    if ti == 0:
        continue
    for m in track:
        if m.type == "program_change":
            programs[ti] = m.program

json.dump({"voices": {str(ti): {"program": programs.get(ti), "cells": rows[i]}
                      for i, ti in enumerate(voices)}}, open(out_json, "w"), indent=2)

# ASCII grid: cell columns, rows = voices, █ = onset, ░ = rest
lines = ["Chorale DNA — 8 cells x 4 voices (█ onset / ░ rest, 1 column = 2.5 s whole note)"]
header = "        " + "".join(f"  c{i}  " for i in range(8))
lines.append(header)
for i, ti in enumerate(voices):
    label = f"V{ti} (P{programs.get(ti)})"
    grid = "".join("  █  " if cells.get((ti, c)) else "  ░  " for c in range(8))
    lines.append(f"{label:<12} {grid}")
lines.append("")
lines.append("Pitch classes per cell:")
for i, ti in enumerate(voices):
    pcs = " ".join(f"{NAMES[cells[(ti,c)]%12]:>2}" if cells.get((ti, c)) else " ." for c in range(8))
    lines.append(f"V{ti} (P{programs.get(ti)}): {pcs}")
open(out_txt, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
