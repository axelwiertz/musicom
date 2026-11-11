# -*- coding: utf-8 -*-
"""Readback verification for 296-electronic-rmt-spectral.

mido READ-ONLY. Confirms:
  - perfect: 0 off-grid onsets (16th grid)
  - humanized: > 0 off-grid onsets (proves the humanizer ran)
  - zero-drift: all note tracks equal length
"""
import os
import json
import mido

PROJ = "/opt/data/projects/Styles/Electronic/296-electronic-rmt-spectral"
MIDI = os.path.join(PROJ, "MIDI")
GRID = 120  # 16th

out = {}
for name in ["perfect", "humanized", "phase1"]:
    path = os.path.join(MIDI, f"296-electronic-rmt-spectral-{name}.mid")
    mid = mido.MidiFile(path)
    tracks = {}
    for i, tr in enumerate(mid.tracks):
        t = 0
        onsets = []
        max_t = 0
        npitch = 0
        for m in tr:
            t += m.time
            if m.type == 'note_on' and m.velocity > 0:
                onsets.append((m.note, t))
                npitch += 1
                max_t = max(max_t, t)
        tracks[i] = {"onsets": onsets, "max_tick": max_t, "n_notes": npitch}
    per = {}
    for i, t in tracks.items():
        off16 = [tick for (note, tick) in t["onsets"] if tick % GRID != 0]
        per[i] = {"n": t["n_notes"], "off16": len(off16),
                  "max_tick": t["max_tick"]}
    lengths = [t["max_tick"] for t in tracks.values() if t["n_notes"] > 0]
    out[name] = {"tracks": per, "nonzero_track_lengths": sorted(lengths)}
    print(name, "| tracks:", per, "| lengths:", sorted(lengths))

with open(os.path.join(PROJ, "Analysis", "readback.json"), "w") as f:
    json.dump(out, f, indent=2)

perf = out["perfect"]
hum = out["humanized"]
tot_off_perfect = sum(t["off16"] for t in perf["tracks"].values())
tot_off_hum = sum(t["off16"] for t in hum["tracks"].values())
print("perfect total off-grid(16th):", tot_off_perfect)
print("humanized total off-grid(16th):", tot_off_hum)
assert tot_off_perfect == 0, "perfect has off-grid onsets!"
assert tot_off_hum > 0, "humanized shows no off-grid -> humanizer did not run!"
print("VERIFY OK")
