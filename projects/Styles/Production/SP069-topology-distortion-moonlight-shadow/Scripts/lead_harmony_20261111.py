# -*- coding: utf-8 -*-
"""Lead-vs-accompaniment harmony check for moonlight-shadow (post-rework clean)."""
import mido
from collections import Counter, defaultdict

SRC = "/opt/data/repos/musicom/projects/Styles/Production/SP069-topology-distortion-moonlight-shadow/MIDI/moonlight-shadow-clean.mid"
mf = mido.MidiFile(SRC)
BAR = 1920

def read_notes(ti):
    tr = mf.tracks[ti]
    t = 0
    open_notes = []
    rows = []
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            open_notes.append({"note": m.note, "on": t})
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            for i in range(len(open_notes) - 1, -1, -1):
                if open_notes[i]["note"] == m.note:
                    n = open_notes.pop(i)
                    rows.append((n["note"], n["on"]))
                    break
    return rows

# clean.mid: tempo track (0), then 6 voice tracks (1-6)
note_tracks = []
for i, tr in enumerate(mf.tracks):
    if any(m.type == "note_on" and m.velocity > 0 for m in tr):
        note_tracks.append(i)

print("note track indices:", note_tracks)
# order: Melody(74), Strings(49), Pad(88), Bass(33), Guitar(25), Drums(9)
lead = read_notes(note_tracks[0])
accomp = []
for ti in note_tracks[1:5]:  # strings, pad, bass, guitar (skip drums)
    accomp += read_notes(ti)

# accompaniment pcs per bar
accomp_pcs = defaultdict(set)
for note, on in accomp:
    accomp_pcs[on // BAR].add(note % 12)

# lead out-of-accomp-pc per bar
print("\n=== LEAD notes not in accompaniment pcs (per bar) ===")
lead_ooc = 0
for note, on in lead:
    bar = on // BAR
    if note % 12 not in accomp_pcs[bar]:
        lead_ooc += 1
        if lead_ooc <= 60:
            print(f"  bar {bar:2d} note={note} pc={note%12} acc_pcs={sorted(accomp_pcs[bar])}")
print("total lead notes not in accompaniment pcs:", lead_ooc, "/", len(lead))

# also show accomp pcs per bar (the "chord" per bar)
print("\n=== accompaniment pcs per bar (derived chord) ===")
for bar in range(32):
    print(f"  bar {bar:2d}: {sorted(accomp_pcs[bar])}")
