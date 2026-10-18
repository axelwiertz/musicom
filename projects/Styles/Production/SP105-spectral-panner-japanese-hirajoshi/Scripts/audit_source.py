# -*- coding: utf-8 -*-
"""Pre-flight 3-rule audit of the source MIDI (read-only)."""
import sys
import mido

SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/opt/data/repos/musicom/projects/Styles/Japanese/001-japanese-hirajoshi/MIDI/japanese-hirajoshi.mid"

HIRA_PCS = {2, 3, 7, 8, 0}   # D hirajoshi: D Eb G Ab C
GRID = 120                    # 16th-note ticks (8th=240, 16th=120)

mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat
print("TPB:", tpb, " length(s):", round(mf.length, 3), " type:", mf.type)

tempo = None
for tr in mf.tracks:
    for m in tr:
        if m.type == "set_tempo":
            tempo = m.tempo
print("tempo us/beat:", tempo, " bpm:", round(mido.tempo2bpm(tempo), 2) if tempo else None)

pitched = []       # (track_idx, channel, program, events)
drum_tracks = []
track_lengths = []
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
            if m.channel == 9:
                notes.append(("drum", m.note, m.velocity, t))
            else:
                channel = m.channel
                notes.append(("note", m.note, m.velocity, t))
    track_lengths.append(t)
    if notes:
        ch = 9 if any(n[0] == "drum" for n in notes) else channel
        pitched.append((ti, ch, prog, notes))

print("\nTrack lengths (ticks):", track_lengths)
print("Zero-drift:", "PASS" if len(set(track_lengths)) == 1 else
      f"FAIL (distinct lengths: {sorted(set(track_lengths))})")

print("\n=== per-track (pitched voices) ===")
total_off_grid = 0
total_out_scale = 0
total_notes = 0
per_voice_pcs = {}
for ti, ch, prog, notes in pitched:
    is_drum = ch == 9
    off_grid = 0
    out_scale = 0
    pcs = set()
    onsets = []
    for kind, note, vel, t in notes:
        onsets.append(t)
        total_notes += 1
        pcs.add(note % 12)
        if t % GRID != 0:
            off_grid += 1
        if not is_drum and note % 12 not in HIRA_PCS:
            out_scale += 1
    if is_drum:
        print(f"track {ti}: DRUM (ch9, prog {prog})  notes={len(notes)} "
              f"onsets={sorted(set(onsets))}")
        continue
    total_off_grid += off_grid
    total_out_scale += out_scale
    per_voice_pcs[ti] = sorted(pcs)
    print(f"track {ti}: ch={ch} prog={prog} notes={len(notes)} "
          f"off_grid={off_grid} out_scale={out_scale} pcs={sorted(pcs)} "
          f"onsets={sorted(set(onsets))}")

print("\n=== TOTALS (pitched, excl drums) ===")
print("total notes:", total_notes)
print("off-grid onsets:", total_off_grid)
print("out-of-scale notes:", total_out_scale)

# identify the out-of-scale notes
print("\n=== out-of-scale notes detail ===")
for ti, ch, prog, notes in pitched:
    if ch == 9:
        continue
    for kind, note, vel, t in notes:
        if note % 12 not in HIRA_PCS:
            print(f"  track {ti} ch{ch} prog{prog}: note={note} "
                  f"(pc={note%12}) vel={vel} onset={t} (bar={t//1920}.{ (t%1920)//480 })")

print("\nGrid sync (16th=120):", "PASS" if total_off_grid == 0 else f"FAIL ({total_off_grid} off-grid)")
print("Harmony in-scale:", "PASS" if total_out_scale == 0 else f"FAIL ({total_out_scale} out-of-scale)")
