# -*- coding: utf-8 -*-
"""Rework 247-metal-fourier-spectrum.mid: de-humanize (snap onsets to 16th grid).

Pre-flight gate rule 1 (grid sync) FAILS on the source because the composition
job shipped a HUMANIZED MIDI (always-on micro-timing; 1826/1984 pitched onsets
off-grid). Harmony (0 out-of-scale / 0 out-of-chord) and zero-drift already
pass. Humanization shifted each onset <= 20 ticks from its grid position, so
round(onset/120)*120 recovers the exact pre-humanization grid.

Rework = snap every note_on onset to the nearest 16th grid (120 ticks),
preserve each note's duration, clamp to the 61440-tick span, keep the pitch-0
terminal landmark at 61440. Then re-audit (must read 0/0/0 + zero-drift).
"""
from collections import defaultdict
import json
from pathlib import Path

import mido

SRC = Path("/opt/data/repos/musicom/projects/Styles/Metal/"
           "247-metal-fourier-spectrum/MIDI/247-metal-fourier-spectrum.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP157-whole-tone-filterbank-247-metal-fourier-spectrum")
MIDIDIR = OUT / "MIDI"
MIDIDIR.mkdir(parents=True, exist_ok=True)

TPB = 480
BAR = 1920
GRID = 120
TOTAL = 61440

mf = mido.MidiFile(str(SRC))
assert mf.ticks_per_beat == TPB


def rebuild_track(tr):
    """Return a rebuilt track with onsets snapped to the grid."""
    # 1. absolute times + event kind
    ev = []
    t = 0
    for m in tr:
        t += m.time
        ev.append((m, t))
    # 2. note_on indices per note (FIFO), and shift per note_on
    open_stack = defaultdict(list)
    note_on_shift = {}     # index of note_on event -> delta
    note_off_shift = {}    # index of note_off event -> delta (matches its note_on)
    for i, (m, t) in enumerate(ev):
        if m.type == "note_on" and m.velocity > 0:
            open_stack[m.note].append(i)
            snapped = int(round(t / GRID)) * GRID
            snapped = min(max(snapped, 0), TOTAL - GRID)
            note_on_shift[i] = snapped - t
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            st = open_stack.get(m.note)
            if st:
                j = st.pop(0)
                note_off_shift[i] = note_on_shift[j]
            else:
                note_off_shift[i] = 0  # landmark / stray -> untouched
    # 3. new absolute times
    new_abs = []
    for i, (m, t) in enumerate(ev):
        if i in note_on_shift:
            nt = t + note_on_shift[i]
        elif i in note_off_shift:
            nt = t + note_off_shift[i]
        else:
            nt = t
        nt = min(max(nt, 0), TOTAL)
        new_abs.append((m, nt))
    # 4. stable sort by (abs time, note_off-before-note_on at equal tick)
    def key(x):
        m, nt = x
        kind = 0
        if m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            kind = 0  # note-off first
        elif m.type == "note_on":
            kind = 1
        return (nt, kind)
    new_abs.sort(key=key)
    # 5. rebuild with delta times
    out = mido.MidiTrack()
    last = 0
    for m, nt in new_abs:
        nm = m.copy(time=max(0, nt - last))
        out.append(nm)
        last = nt
    return out


tracks = []
tracks.append(mf.tracks[0])  # tempo/meta track
for tr in mf.tracks[1:]:
    tracks.append(rebuild_track(tr))

out_mf = mido.MidiFile(ticks_per_beat=TPB)
out_mf.tracks = tracks

reworked = MIDIDIR / "247-metal-fourier-spectrum.mid"
out_mf.save(str(reworked))
print("wrote", reworked, reworked.stat().st_size, "bytes")

# ---- re-audit the reworked file ----
SEC_BARS = {"Head1": range(0, 8), "Solo1": range(8, 16),
            "Solo2": range(16, 24), "Head2": range(24, 32)}
POOLS = {"Head1": {0, 2, 4, 6, 7, 9, 11}, "Solo1": {0, 3, 4, 6, 7, 9, 11},
         "Solo2": {1, 2, 4, 5, 7, 8, 10, 11}, "Head2": {0, 2, 4, 6, 7, 9, 11}}
CHORD_TONES = [
    {4, 7, 11}, {4, 7, 11}, {0, 4, 7}, {7, 11, 2},
    {2, 6, 9}, {0, 4, 7}, {2, 6, 9}, {4, 7, 11},
    {4, 7, 11}, {9, 0, 4}, {11, 3, 6}, {4, 7, 11},
    {0, 4, 7}, {6, 9, 0}, {11, 3, 6}, {4, 7, 11},
    {4, 7, 11}, {4, 7, 10, 1}, {5, 8, 11, 2}, {4, 7, 11},
    {4, 7, 10, 1}, {11, 2, 5}, {5, 8, 11, 2}, {4, 7, 11},
    {4, 7, 11}, {4, 7, 11}, {0, 4, 7}, {7, 11, 2},
    {2, 6, 9}, {0, 4, 7}, {2, 6, 9}, {4, 7, 11},
]


def sec_of_bar(bar):
    for name, rng in SEC_BARS.items():
        if bar in rng:
            return name


def audit(path):
    m = mido.MidiFile(str(path))
    grid_off = out_scale = out_chord = total = 0
    ends = []
    for tr in m.tracks:
        chans = {x.channel for x in tr if x.type in ("note_on", "note_off")}
        is_drum = 9 in chans
        t = 0
        n = 0
        last_end = 0
        for x in tr:
            t += x.time
            if x.type == "note_on" and x.velocity > 0:
                n += 1
                total += 1
                if is_drum:
                    last_end = max(last_end, t)
                    continue
                if (t % GRID) != 0:
                    grid_off += 1
                pc = x.note % 12
                bar = min(t // BAR, 31)
                if pc not in POOLS[sec_of_bar(bar)]:
                    out_scale += 1
                if pc not in CHORD_TONES[bar]:
                    out_chord += 1
                last_end = max(last_end, t)
            elif x.type == "note_off" or (x.type == "note_on" and x.velocity == 0):
                last_end = max(last_end, t)
        if n:
            ends.append(last_end)
    return {"grid_off": grid_off, "out_scale": out_scale,
            "out_chord": out_chord, "total_notes": total,
            "zero_drift": len(set(ends)) == 1, "track_ends": sorted(set(ends))}


res = audit(reworked)
print(json.dumps(res, indent=2))
assert res["grid_off"] == 0, "grid still off after rework"
assert res["out_scale"] == 0, "out-of-scale after rework"
assert res["out_chord"] == 0, "out-of-chord after rework"
assert res["zero_drift"], "zero-drift broken after rework"
print("REWORK OK: 0 off-grid / 0 out-of-scale / 0 out-of-chord / zero-drift")
