# -*- coding: utf-8 -*-
"""Read-only mido verification audit for 229-soul-voiceleading-rework."""
import os
import json
import mido  # READING ONLY (analysis)

PROJ = "/opt/data/projects/Styles/Soul/229-soul-voiceleading-rework"
MIDI_DIR = os.path.join(PROJ, "MIDI")
P1 = os.path.join(MIDI_DIR, "229-soul-voiceleading-rework-phase1.mid")
P2 = os.path.join(MIDI_DIR, "229-soul-voiceleading-rework.mid")

KEY_PCS = {5, 7, 8, 10, 0, 1, 3}   # F natural minor
BAR = 1920
CHORDS = {53: [53, 56, 60], 55: [55, 58, 61], 56: [56, 60, 63],
          58: [58, 61, 65], 60: [60, 63, 67], 61: [61, 65, 68],
          63: [63, 67, 70]}
SEC_PROG = {0: [53, 61, 58, 53], 1: [53, 58, 56, 60], 2: [61, 56, 58, 60],
            3: [53, 58, 55, 60], 4: [61, 56, 60, 53], 5: [58, 55, 61, 63],
            6: [61, 56, 58, 60], 7: [53, 63, 61, 53]}
PROG = [SEC_PROG[s][b] for s in range(8) for b in range(4)]


def audit(path):
    mid = mido.MidiFile(path)
    tracks = mid.tracks
    lens = [sum(m.time for m in t) for t in tracks]
    voice_lens = lens[1:]
    zero_drift = len(set(voice_lens)) == 1
    off_grid = 0
    scale_viol = 0
    chord_viol = 0
    chord_viol_examples = []
    total_onsets = 0
    for ti, t in enumerate(tracks):
        if ti == 0:
            continue
        abso = 0
        for m in t:
            abso += m.time
            if m.type == "note_on" and m.velocity > 0:
                p = m.note
                ch = m.channel
                if ch == 9:
                    continue
                total_onsets += 1
                if not (abso % 120 == 0 or abso % 240 == 0):
                    off_grid += 1
                if p % 12 not in KEY_PCS:
                    scale_viol += 1
                bar = abso // BAR
                bar = bar if bar < len(PROG) else len(PROG) - 1
                ct = CHORDS[PROG[bar]]
                if p % 12 not in {c % 12 for c in ct}:
                    chord_viol += 1
                    if len(chord_viol_examples) < 10:
                        chord_viol_examples.append((ti, abso, p, PROG[bar], ct))
    return {
        "path": path,
        "size": os.path.getsize(path),
        "n_tracks": len(tracks),
        "voice_lens": voice_lens,
        "zero_drift": zero_drift,
        "n_pitched_onsets": total_onsets,
        "off_grid": off_grid,
        "scale_viol": scale_viol,
        "chord_viol": chord_viol,
        "chord_viol_examples": chord_viol_examples,
    }


res = {"phase1": audit(P1), "phase2": audit(P2)}
print(json.dumps(res, indent=2))
with open(os.path.join(PROJ, "Analysis", "verify.json"), "w") as f:
    json.dump(res, f, indent=2)
print("WROTE Analysis/verify.json")
