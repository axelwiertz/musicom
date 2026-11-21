# -*- coding: utf-8 -*-
"""Read-only verification for 316-soul-voiceleading-suite (mido analysis ONLY)."""
import mido  # READING ONLY (analysis)
import os
import json

PROJ = "/opt/data/projects/Styles/Soul/316-soul-voiceleading-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")

BAR = 1920
KEY_PCS = {5, 7, 8, 10, 0, 1, 3}          # F natural minor
CHORDS = {
    53: [53, 56, 60], 55: [55, 58, 61], 56: [56, 60, 63], 58: [58, 61, 65],
    60: [60, 63, 67], 61: [61, 65, 68], 63: [63, 67, 70],
}
SEC_PROG = {
    0: [53, 61, 58, 53], 1: [53, 58, 56, 60], 2: [58, 60, 61, 63],
    3: [61, 56, 58, 60], 4: [53, 58, 55, 60], 5: [58, 60, 61, 63],
    6: [61, 56, 60, 53], 7: [58, 55, 61, 63], 8: [61, 56, 58, 60],
    9: [53, 63, 61, 53],
}
N_SECTIONS = 10
BARS_PER = 4
PROG = [SEC_PROG[s][b] for s in range(N_SECTIONS) for b in range(BARS_PER)]
assert len(PROG) == 40


def audit(path):
    mid = mido.MidiFile(path)
    tracks = mid.tracks
    lengths = [sum(m.time for m in t) for t in tracks]
    voice_lens = lengths[1:]
    zero_drift = len(set(voice_lens)) == 1
    pitched_onsets = 0
    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    n_voices = len(voice_lens)
    for i, tr in enumerate(tracks[1:], start=1):
        ch = None
        for m in tr:
            if m.type == "note_on":
                ch = m.channel
                break
        is_drum = (ch == 9)
        t = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                if is_drum:
                    continue
                pitched_onsets += 1
                if not (t % 120 == 0 or t % 240 == 0):
                    offgrid += 1
                pc = m.note % 12
                if pc not in KEY_PCS:
                    scale_viol += 1
                bar = t // BAR
                if bar >= len(PROG):
                    chord_viol += 1
                    continue
                chord_pcs = {c % 12 for c in CHORDS[PROG[bar]]}
                if pc not in chord_pcs:
                    chord_viol += 1
    return {
        "file": os.path.basename(path),
        "size": os.path.getsize(path),
        "n_tracks_total": len(tracks),
        "n_voice_tracks": n_voices,
        "track_lens": voice_lens,
        "zero_drift": zero_drift,
        "pitched_onsets": pitched_onsets,
        "offgrid": offgrid,
        "scale_viol": scale_viol,
        "chord_viol": chord_viol,
    }


for f in sorted(os.listdir(MIDI_DIR)):
    if f.endswith(".mid") and not f.endswith(".provenance.json"):
        r = audit(os.path.join(MIDI_DIR, f))
        print(json.dumps(r, default=str))
