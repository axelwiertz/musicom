# -*- coding: utf-8 -*-
"""Read-only mido verification for 300-world-sheaf-cohomology.

Checks: zero-drift (all pitched tracks equal length), grid audit on exported
MIDI (perfect == 0 off-grid, humanized > 0 off-grid), file sizes.
"""
import os
import json

import mido

PROJ = "/opt/data/projects/Styles/World/300-world-sheaf-cohomology"
MIDI = os.path.join(PROJ, "MIDI")

res = {}


def analyze(path):
    mid = mido.MidiFile(path)
    ticks_per_beat = mid.ticks_per_beat
    track_lengths = []
    offgrid_16 = 0
    offgrid_8 = 0
    total_on = 0
    for tr in mid.tracks:
        t = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                total_on += 1
                if t % 120 != 0:
                    offgrid_16 += 1
                if t % 240 != 0:
                    offgrid_8 += 1
        track_lengths.append(t)
    return {
        "ticks_per_beat": ticks_per_beat,
        "n_tracks": len(mid.tracks),
        "track_lengths": track_lengths,
        "note_ons": total_on,
        "offgrid_16": offgrid_16,
        "offgrid_8": offgrid_8,
    }


for name in ["phase1", "perfect", "humanized"]:
    p = os.path.join(MIDI, f"300-world-sheaf-cohomology-{name}.mid")
    sz = os.path.getsize(p)
    a = analyze(p)
    res[name] = {"size": sz, **a}
    print(f"[{name}] size={sz} tracks={a['n_tracks']} "
          f"lengths={a['track_lengths']} note_ons={a['note_ons']} "
          f"off16={a['offgrid_16']} off8={a['offgrid_8']}")

voice_lengths = [l for l in res["perfect"]["track_lengths"][1:]]
zero_drift_ok = len(voice_lengths) > 0 and len(set(voice_lengths)) == 1
print("zero-drift (perfect voice tracks equal):", zero_drift_ok,
      "| lengths:", res["perfect"]["track_lengths"])
print("perfect off16:", res["perfect"]["offgrid_16"], "(expect 0)")
print("humanized off16:", res["humanized"]["offgrid_16"], "(expect > 0)")

assert res["perfect"]["offgrid_16"] == 0, "perfect must be 0 off-grid!"
assert res["humanized"]["offgrid_16"] > 0, "humanized must show jitter!"
assert zero_drift_ok, "zero-drift FAIL"

with open(os.path.join(PROJ, "Analysis", "readback.json"), "w") as f:
    json.dump(res, f, indent=2)
print("VERIFY OK")
