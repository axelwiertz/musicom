# -*- coding: utf-8 -*-
"""Deeper audit: off-grid onset detail + per-voice/chord-tone analysis."""
import mido
from collections import Counter, defaultdict

SRC = "/opt/data/repos/musicom/projects/Styles/Pop/moonlight-shadow/MIDI/moonlight-shadow-variant2.mid"
mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat  # 480
BAR = tpb * 4  # 1920
GRID_16 = tpb // 4

# collect notes per track with absolute ticks
notes_by_track = {}
for i, tr in enumerate(mf.tracks):
    t = 0
    evs = []
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            evs.append((m.note, t, m.channel))
    notes_by_track[i] = evs

# off-grid onsets: which residuals (onset % 120) appear?
resid = Counter()
offgrid_notes = []
for i, evs in notes_by_track.items():
    for note, t, ch in evs:
        if ch == 9:
            continue
        r = t % GRID_16
        resid[r] += 1
        if r != 0:
            offgrid_notes.append((i, note, t, r, t // BAR))
print("onset %%120 residual histogram (pitched):", dict(sorted(resid.items())))
print("num off-grid notes:", len(offgrid_notes))
# show a sample
for row in offgrid_notes[:25]:
    print("  track", row[0], "note", row[1], "tick", row[2], "resid", row[3], "bar", row[4])

# per-voice off-grid counts
per_voice = defaultdict(int)
for i, note, t, r, bar in offgrid_notes:
    per_voice[i] += 1
print("per-track off-grid counts:", dict(per_voice))

# total pitched per track
print("per-track pitched totals:", {i: len([e for e in evs if e[2] != 9]) for i, evs in notes_by_track.items()})

# are off-grid notes humanized (tiny jitter) or grossly off?
# small residuals vs big
small = sum(1 for r in resid if r in (1, 2, 3, 117, 118, 119) or r in (239, 240, 241) or r in (358,359,360,361,362) or r in (478,479,480,481,482))
print("resid close to grid boundaries:", small)

# chord-tone analysis: need chord progression. Print bar-majority pitch classes.
E_MAJOR = {4, 6, 8, 9, 11, 1, 3}
# gather pitched (non-perc) notes by bar
bar_pcs = defaultdict(Counter)
for i, evs in notes_by_track.items():
    for note, t, ch in evs:
        if ch == 9:
            continue
        bar_pcs[t // BAR][note % 12] += 1
print("\nper-bar pitch-class histogram (top 4):")
for bar in sorted(bar_pcs):
    top = bar_pcs[bar].most_common(4)
    print("  bar", bar, ":", top)
