# -*- coding: utf-8 -*-
"""Pre-flight 3-rule audit of the source MIDI (read-only).

Source: Styles/Latin/bossa-nova-daily-2026-06-15/composition.mid
Key: A minor (A natural minor = A B C D E F G), harmony = Am7 (A C E G).
"""
import sys
import mido

SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/opt/data/repos/musicom/projects/Styles/Latin/bossa-nova-daily-2026-06-15/composition.mid"

# A natural minor pitch classes
AMIN_PCS = {9, 11, 0, 2, 4, 5, 7}   # A B C D E F G
# Am7 chord tones (A C E G)
AM7_PCS = {9, 0, 4, 7}
GRID = 120   # 16th-note ticks (8th=240, 16th=120 at TPB 480)

mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat
print("TPB:", tpb, " length(s):", round(mf.length, 3), " type:", mf.type)

tempo = None
for tr in mf.tracks:
    for m in tr:
        if m.type == "set_tempo":
            tempo = m.tempo
print("tempo us/beat:", tempo, " bpm:", round(mido.tempo2bpm(tempo), 2) if tempo else None)

pitched = []       # (track_idx, channel, program, notes)
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
            notes.append((m.note, m.velocity, t, m.channel))
    track_lengths.append(t)
    if notes:
        ch = notes[0][3]
        pitched.append((ti, ch, prog, notes))

print("\nTrack lengths (ticks):", track_lengths)
note_track_lengths = [tl for (ti, ch, prog, notes), tl in
                      zip(pitched, [track_lengths[ti] for ti, *_ in pitched])]
print("Zero-drift (note tracks equal len):", "PASS" if len(set(track_lengths[1:])) == 1 else
      f"CHECK (distinct lengths: {sorted(set(track_lengths[1:]))})")

print("\n=== per-track (voices) ===")
total_off_grid = 0
total_out_scale = 0
total_out_chord = 0
total_notes = 0
for ti, ch, prog, notes in pitched:
    is_drum = ch == 9
    off_grid = 0
    out_scale = 0
    out_chord = 0
    pcs = set()
    onsets = set()
    for note, vel, t, c in notes:
        onsets.add(t)
        total_notes += 1
        pcs.add(note % 12)
        if t % GRID != 0:
            off_grid += 1
        if not is_drum:
            if note % 12 not in AMIN_PCS:
                out_scale += 1
            if note % 12 not in AM7_PCS:
                out_chord += 1
    tag = "DRUM (ch9)" if is_drum else f"ch={ch} prog={prog}"
    if is_drum:
        print(f"track {ti}: {tag} notes={len(notes)} onsets={sorted(onsets)}")
        continue
    total_off_grid += off_grid
    total_out_scale += out_scale
    total_out_chord += out_chord
    print(f"track {ti}: {tag} notes={len(notes)} "
          f"off_grid={off_grid} out_scale={out_scale} out_chord={out_chord} "
          f"pcs={sorted(pcs)}")

print("\n=== TOTALS (pitched, excl drums) ===")
print("total notes:", total_notes)
print("off-grid onsets:", total_off_grid)
print("out-of-scale notes:", total_out_scale)
print("out-of-chord notes:", total_out_chord)

print("\nGrid sync (16th=120):", "PASS" if total_off_grid == 0 else f"FAIL ({total_off_grid} off-grid)")
print("Harmony in-scale:", "PASS" if total_out_scale == 0 else f"FAIL ({total_out_scale} out-of-scale)")
print("Harmony chord-tone (Am7):", "PASS" if total_out_chord == 0 else f"FAIL ({total_out_chord} out-of-chord)")
