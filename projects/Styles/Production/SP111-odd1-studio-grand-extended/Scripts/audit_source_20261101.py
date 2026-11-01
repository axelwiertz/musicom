# -*- coding: utf-8 -*-
import mido

SRC = "/opt/data/repos/musicom/projects/Styles/Classical/studio_grand_extended/v1/studio_grand_extended.mid"
TPB = 480
BAR = 1920
GRID = 120
N_BARS = 32
SCALE_PCS = {0, 2, 4, 5, 7, 9, 11}  # C major
TRIADS = {
    "C":  {0, 4, 7},
    "G":  {7, 11, 2},
    "F":  {5, 9, 0},
    "Am": {9, 0, 4},
}
# per-section progression, 4 bars each
PROG_SECTIONS = [
    ['C', 'C', 'G', 'G'],    # Intro
    ['C', 'C', 'G', 'G'],    # V1a
    ['C', 'C', 'F', 'C'],    # V1b
    ['F', 'C', 'G', 'Am'],   # ChA
    ['F', 'C', 'G', 'C'],    # ChB
    ['C', 'Am', 'G', 'G'],   # V2a
    ['C', 'Am', 'F', 'C'],   # V2b
    ['F', 'C', 'G', 'C'],    # Outro
]
PROG = [c for sec in PROG_SECTIONS for c in sec]
assert len(PROG) == N_BARS, len(PROG)

mf = mido.MidiFile(SRC)
print("tpb:", mf.ticks_per_beat, "n_tracks:", len(mf.tracks), "length_sec:", round(mf.length, 2))
grid_off = off8 = out_scale = out_chord = 0
track_ends = []
total_notes = 0
per_track = {}
for ti, tr in enumerate(mf.tracks):
    chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
    is_drum = 9 in chans
    t = 0
    n_notes = 0
    g_off = o_scale = o_chord = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            n_notes += 1
            total_notes += 1
            if is_drum:
                continue
            if (t % GRID) != 0:
                grid_off += 1
                g_off += 1
            if (t % 240) != 0:
                off8 += 1
            pc = m.note % 12
            if pc not in SCALE_PCS:
                out_scale += 1
                o_scale += 1
            bar = min(t // BAR, N_BARS - 1)
            if pc not in TRIADS[PROG[bar]]:
                out_chord += 1
                o_chord += 1
    if n_notes:
        track_ends.append(t)
        per_track[ti] = dict(is_drum=is_drum, n=n_notes, goff=g_off, oscale=o_scale, ochord=o_chord, end=t, chans=sorted(chans))

print("=== PER-TRACK ===")
for ti, d in per_track.items():
    print(f"track {ti}: drum={d['is_drum']} n={d['n']} goff={d['goff']} oscale={d['oscale']} ochord={d['ochord']} end={d['end']} chans={d['chans']}")

print("=== TOTALS ===")
print("grid_off(16th):", grid_off, "off8:", off8, "out_scale:", out_scale, "out_chord:", out_chord)
print("track_ends:", sorted(set(track_ends)), "zero_drift:", len(set(track_ends)) == 1)
print("total_notes:", total_notes)
