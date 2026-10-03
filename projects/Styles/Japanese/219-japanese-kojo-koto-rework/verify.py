# -*- coding: utf-8 -*-
# READING ONLY (analysis)
"""Read-only verification of 219-japanese-kojo-koto-rework MIDI."""
import os
import json
import mido

PROJ = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

P2 = os.path.join(MIDI_DIR, "219-japanese-kojo-koto-rework.mid")
P1 = os.path.join(MIDI_DIR, "219-japanese-kojo-koto-rework-phase1.mid")

GRID16 = 120
GRID8 = 240
BAR = 1920

SCALE_PCS = {9, 10, 2, 4, 7}
PALETTES = {
    "A":  {9, 10, 2, 4}, "Bb": {10, 2, 4, 7}, "D": {2, 4, 7, 9},
    "E":  {4, 7, 9, 10}, "G":  {7, 9, 10, 2},
}
PROGRESSIONS = [
    ["A", "A", "D", "A"], ["A", "G", "Bb", "A"], ["Bb", "D", "E", "Bb"],
    ["D", "G", "A", "D"], ["E", "A", "G", "E"], ["G", "A", "Bb", "E"],
    ["A", "Bb", "D", "A"], ["A", "E", "D", "A"],
]

def palette_at(tick):
    bar = tick // BAR
    sec = bar // 4
    bin_sec = bar % 4
    return PALETTES[PROGRESSIONS[sec][bin_sec]]

def parse(path):
    mid = mido.MidiFile(path)
    out = []
    for i, trk in enumerate(mid.tracks):
        t = 0
        notes = []
        ch = None
        for msg in trk:
            t += msg.time
            if msg.type in ("note_on", "note_off") and getattr(msg, "channel", None) is not None:
                ch = msg.channel
        at = 0
        open_notes = {}
        for msg in trk:
            at += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                open_notes.setdefault(msg.note, at)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                st = open_notes.pop(msg.note, None)
                if st is not None:
                    notes.append({"pitch": msg.note, "start": st, "end": at, "ch": ch})
        out.append({"idx": i, "len": t, "ch": ch, "notes": notes})
    return out

def verify():
    r = {"phase2": {}, "phase1": {}}
    for key, path, is_phase2 in (("phase2", P2, True), ("phase1", P1, False)):
        tracks = parse(path)
        lengths = [tr["len"] for tr in tracks]
        voice_lengths = lengths[1:]
        zero_drift = len(set(voice_lengths)) == 1
        n_voices = len(tracks) - 1
        off_grid = out_scale = out_chord = total = 0
        per_track = []
        for tr in tracks[1:]:
            ch = tr["ch"]
            is_drum = (ch == 9)
            t_off = t_scale = t_chord = t_n = 0
            for n in tr["notes"]:
                if n["pitch"] == 0:
                    continue
                t_n += 1
                total += 1
                if n["start"] % GRID16 != 0:
                    t_off += 1
                    off_grid += 1
                if not is_drum and is_phase2:
                    pc = n["pitch"] % 12
                    if pc not in SCALE_PCS:
                        t_scale += 1
                        out_scale += 1
                    if pc not in palette_at(n["start"]):
                        t_chord += 1
                        out_chord += 1
            per_track.append({"idx": tr["idx"], "ch": ch, "len": tr["len"],
                              "notes": t_n, "off_grid": t_off,
                              "out_scale": t_scale, "out_chord": t_chord})
        r[key] = {
            "file": os.path.basename(path),
            "size": os.path.getsize(path),
            "n_voices": n_voices,
            "voice_lengths": sorted(set(voice_lengths)),
            "zero_drift": zero_drift,
            "total_notes": total,
            "off_grid": off_grid,
            "out_scale": out_scale,
            "out_chord": out_chord,
            "tracks": per_track,
        }
    with open(os.path.join(ANALYSIS_DIR, "rework_verify.json"), "w") as f:
        json.dump(r, f, indent=2)
    return r

if __name__ == "__main__":
    r = verify()
    for k in ("phase1", "phase2"):
        d = r[k]
        print(f"=== {k} ({d['file']}, {d['size']} B) ===")
        print(f"  size>40: {d['size'] > 40}")
        print(f"  voice tracks: {d['n_voices']}  lengths={d['voice_lengths']}  zero-drift={d['zero_drift']}")
        print(f"  total notes: {d['total_notes']}  off_grid: {d['off_grid']}")
        if k == "phase2":
            print(f"  out_scale: {d['out_scale']}  out_chord: {d['out_chord']}")
        for t in d["tracks"]:
            print(f"    track{t['idx']} ch{t['ch']} len={t['len']} notes={t['notes']} "
                  f"offgrid={t['off_grid']} oos={t['out_scale']} ooc={t['out_chord']}")
    print("\nSaved rework_verify.json")
