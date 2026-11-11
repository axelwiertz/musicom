# -*- coding: utf-8 -*-
"""Readback verification for 297-flamenco-falseta-suite.

mido READ-ONLY. Confirms:
  - zero-drift: all note tracks equal length
  - perfect: 0 off-grid onsets (16th grid); humanized: > 0 (jitter ran)
  - scale violations (A major) == 0 for perfect (skip ch9)
  - chord violations (per-bar t//BAR) == 0 for perfect (skip ch9)
"""
import os
import json
import mido

PROJ = "/opt/data/projects/Styles/Flamenco/297-flamenco-falseta-suite"
MIDI = os.path.join(PROJ, "MIDI")
GRID = 120            # 16th
BAR = 1920
KEY_PCS = {9, 11, 1, 2, 4, 6, 8}    # A major

DEGREE_TRIADS = {
    "I":   {9, 1, 4}, "ii": {11, 2, 6}, "iii": {1, 4, 8}, "IV": {2, 6, 9},
    "V":   {4, 8, 11}, "vi": {6, 9, 1}, "vii": {8, 11, 2},
}
SECTIONS = [
    ("Intro", 4, ["I", "I", "I", "V"]),
    ("Falseta I", 4, ["I", "vi", "IV", "V"]),
    ("Letra I", 4, ["V", "V", "V", "I"]),
    ("Falseta II", 4, ["vi", "vi", "IV", "V"]),
    ("Letra II", 4, ["IV", "IV", "ii", "V"]),
    ("Falseta III", 6, ["I", "V", "vi", "IV", "V", "I"]),
    ("Cierre", 6, ["IV", "V", "I", "I", "V", "I"]),
]
BAR_CHORDS = [c for (_n, _b, ch) in SECTIONS for c in ch]
TOTAL_BARS = len(BAR_CHORDS)

out = {}
for name in ["perfect", "humanized", "phase1"]:
    path = os.path.join(MIDI, f"297-flamenco-falseta-suite-{name}.mid")
    assert os.path.getsize(path) > 40, f"{name} empty"
    mid = mido.MidiFile(path)
    tracks = []
    for i, tr in enumerate(mid.tracks):
        t = 0
        max_t = 0
        notes = []           # (note, tick, vel, channel)
        chans = set()
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                notes.append((m.note, t, m.velocity, m.channel))
                max_t = max(max_t, t)
                chans.add(m.channel)
            elif m.type == "note_off":
                max_t = max(max_t, t)
        tracks.append({"idx": i, "notes": notes, "max_tick": max_t,
                       "chans": chans})
    # zero-drift: voice tracks (skip conductor track 0)
    vt = tracks[1:]
    lens = [t["max_tick"] for t in vt]
    zero_drift = len(set(lens)) == 1
    # off-grid (pitched only, skip ch9)
    offgrid = 0
    total_pitched = 0
    scale_viol = 0
    chord_viol = 0
    for t in vt:
        is_drum = (9 in t["chans"])
        for (note, tick, vel, ch) in t["notes"]:
            if is_drum:
                continue
            total_pitched += 1
            if not (tick % 120 == 0 or tick % 240 == 0):
                offgrid += 1
            if note % 12 not in KEY_PCS:
                scale_viol += 1
            bar = tick // BAR
            if bar >= TOTAL_BARS:
                bar = TOTAL_BARS - 1
            if note % 12 not in DEGREE_TRIADS[BAR_CHORDS[bar]]:
                chord_viol += 1
    out[name] = {
        "n_voice_tracks": len(vt), "track_lengths": lens,
        "zero_drift": zero_drift, "off_grid": offgrid,
        "pitched_notes": total_pitched, "scale_violations": scale_viol,
        "chord_violations": chord_viol,
    }
    print(f"{name}: tracks={len(vt)} len={set(lens)} zero_drift={zero_drift} "
          f"off_grid={offgrid} pitched={total_pitched} "
          f"scale_viol={scale_viol} chord_viol={chord_viol}")

with open(os.path.join(PROJ, "Analysis", "readback.json"), "w") as f:
    json.dump(out, f, indent=2)

perf = out["perfect"]
hum = out["humanized"]
assert perf["zero_drift"], "perfect zero-drift FAIL"
assert perf["off_grid"] == 0, f"perfect off-grid {perf['off_grid']}"
assert hum["off_grid"] > 0, "humanized off-grid == 0 -> humanizer did not run"
assert perf["scale_violations"] == 0, f"perfect scale violations {perf['scale_violations']}"
assert perf["chord_violations"] == 0, f"perfect chord violations {perf['chord_violations']}"
print("VERIFY OK")
