# -*- coding: utf-8 -*-
"""Pre-flight 3-rule audit of source MIDI 059-genetic-chorale (read-only) + structure dump."""
import sys
import mido

SRC = "/opt/data/repos/musicom/projects/Styles/Experimental/059-genetic-chorale/MIDI/059-genetic-chorale.mid"

# G natural minor pitch classes: G A Bb C D Eb F
GMIN_PCS = {7, 9, 10, 0, 2, 3, 5}
GRID = 120
# chord tones per bar (i iv v i iv v iv i)
CHORD_DEGREES = [1, 4, 5, 1, 4, 5, 4, 1]
# triad pitch classes in G minor: i=Gm{7,10,2} iv=Cm{0,3,7} v=Dm{2,5,9}
def chord_pcs(deg):
    gmin = [7, 9, 10, 0, 2, 3, 5]  # G A Bb C D Eb F
    idx = deg - 1
    return {gmin[(idx + off) % 7] for off in (0, 2, 4)}

BAR_TICKS = 1920
N_BARS = 8

mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat
print("TPB:", tpb, " type:", mf.type, " length(s):", round(mf.length, 3))

tempo = None
for tr in mf.tracks:
    for m in tr:
        if m.type == "set_tempo":
            tempo = m.tempo
bpm = round(mido.tempo2bpm(tempo), 2) if tempo else None
print("tempo us/beat:", tempo, " bpm:", bpm)

track_lengths = []
pitched = []
for ti, tr in enumerate(mf.tracks):
    t = 0
    prog = None
    channel = None
    notes = []
    for m in tr:
        t += m.time
        if m.type == "program_change":
            prog = m.program
            channel = m.channel
        if m.type == "note_on" and m.velocity > 0:
            notes.append((m.note, m.velocity, t, m.channel))
    track_lengths.append(t)
    if notes:
        ch = notes[0][3]
        pitched.append((ti, ch, prog, notes))

print("track lengths (ticks):", track_lengths)
note_track_ends = sorted(set(track_lengths[1:]))
print("zero-drift (note tracks equal):", "PASS" if len(note_track_ends) == 1 else f"FAIL {note_track_ends}")

total_off_grid = total_out_scale = total_out_chord = total_notes = 0
print("\n=== per-track voices ===")
for ti, ch, prog, notes in pitched:
    is_drum = ch == 9
    off_grid = out_scale = out_chord = 0
    pcs = set()
    onsets = set()
    for note, vel, t, c in notes:
        onsets.add(t)
        total_notes += 1
        pcs.add(note % 12)
        if t % GRID != 0:
            off_grid += 1
        if not is_drum:
            if note % 12 not in GMIN_PCS:
                out_scale += 1
            bar = min(t // BAR_TICKS, N_BARS - 1)
            if note % 12 not in chord_pcs(CHORD_DEGREES[bar]):
                out_chord += 1
    tag = f"ch={ch} prog={prog}"
    total_off_grid += off_grid
    total_out_scale += out_scale
    total_out_chord += out_chord
    print(f"track {ti}: {tag} notes={len(notes)} off_grid={off_grid} "
          f"out_scale={out_scale} out_chord={out_chord} pcs={sorted(pcs)}")
    print(f"    onsets={sorted(set(t for n,v,t,c in notes))}")
    for n, v, t, c in notes:
        print(f"    note={n} vel={v} t={t} dur? (see note_off)")

print("\n=== TOTALS (pitched) ===")
print("total notes:", total_notes)
print("off-grid:", total_off_grid, " out-of-scale:", total_out_scale, " out-of-chord:", total_out_chord)
print("Grid sync (16th=120):", "PASS" if total_off_grid == 0 else f"FAIL ({total_off_grid})")
print("In-scale (Gmin):", "PASS" if total_out_scale == 0 else f"FAIL ({total_out_scale})")
print("Chord-tone per bar:", "PASS" if total_out_chord == 0 else f"FAIL ({total_out_chord})")

# per-bar chord dump (which notes sound in each bar)
print("\n=== per-bar sounding notes ===")
for bar in range(N_BARS):
    b0 = bar * BAR_TICKS
    b1 = b0 + BAR_TICKS
    sounding = set()
    for ti, ch, prog, notes in pitched:
        for n, v, t, c in notes:
            # need note_off to know duration; approximate: any note_on within bar
            if b0 <= t < b1:
                sounding.add(n)
    print(f"bar {bar+1} (deg {CHORD_DEGREES[bar]}): {sorted(sounding)}")
