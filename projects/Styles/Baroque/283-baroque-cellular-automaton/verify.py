# -*- coding: utf-8 -*-
"""Read-only verification of the 283 outputs. mido = READING ONLY (analysis)."""
import os
import json

import mido  # READING ONLY (analysis) -- never used for authoring

from structures import MusicEvent
from workflows.pitch_audit import audit_voice
from sound.synthesis.scale_quantizer import STRONG_GRID

PROJ = "/opt/data/projects/Styles/Baroque/283-baroque-cellular-automaton"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

BAR_TICKS = 1920
BARS_PER_SECTION = 8
GRID16 = 120
GRID8 = 240
KEY_PCS = {0, 1, 2, 4, 5, 7, 9, 10}
STRONG_GRID_44 = STRONG_GRID.get("4/4", (0, 960))

CHORD_PLAN = {
    "A1": ["Dm", "C", "Bb", "A", "Dm", "Gm", "A", "Dm"],
    "B":  ["F", "C", "Dm", "A", "Bb", "Gm", "A", "Dm"],
    "A2": ["Dm", "C", "Bb", "A", "Dm", "Gm", "A", "Dm"],
}
CHORD_PCS = {
    "Dm": {2, 5, 9}, "C": {0, 4, 7}, "Bb": {10, 2, 5},
    "A": {9, 1, 4}, "Gm": {7, 10, 2}, "F": {5, 9, 0},
}
SECTIONS = ["A1", "B", "A2"]


def chord_pcs_by_bar():
    out = {}
    for s_idx, sec in enumerate(SECTIONS):
        for b in range(BARS_PER_SECTION):
            bar = s_idx * BARS_PER_SECTION + b
            out[bar] = CHORD_PCS[CHORD_PLAN[sec][b]]
    return out


def parse_notes(path):
    """Read MIDI (analysis only) -> list of MusicEvent per track."""
    mid = mido.MidiFile(path)
    tracks = []
    for tr in mid.tracks:
        t = 0
        notes = []
        pending = {}
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                pending[m.note] = (t, m.velocity)
            elif (m.type == "note_off") or (m.type == "note_on" and m.velocity == 0):
                if m.note in pending:
                    st, vel = pending.pop(m.note)
                    if t > st:
                        notes.append(MusicEvent(pitch=m.note, volume=vel,
                                                start_tick=st, end_tick=t))
        tracks.append({"notes": notes, "length": t})
    return tracks


def analyze(path, harmony=True):
    assert os.path.getsize(path) > 40, f"too small: {path}"
    tracks = parse_notes(path)
    voice_tracks = tracks[1:]
    lens = [tr["length"] for tr in voice_tracks]
    zero_drift = len(set(lens)) == 1

    cpb = chord_pcs_by_bar()
    per_voice = []
    tot_off8 = 0
    tot_off16 = 0
    for i, tr in enumerate(voice_tracks):
        notes = tr["notes"]
        onsets = [n.start_tick for n in notes if n.pitch > 0]
        off8 = [o for o in onsets if o % GRID8 != 0]
        off16 = [o for o in onsets if o % GRID16 != 0]
        tot_off8 += len(off8)
        tot_off16 += len(off16)
        entry = {"track": i, "n_notes": len(onsets),
                 "off_8th": len(off8), "off_16th": len(off16)}
        if harmony:
            r = audit_voice(notes, sorted(KEY_PCS), chord_pcs_by_bar=cpb,
                            strong_grid=STRONG_GRID_44, bar_ticks=BAR_TICKS,
                            grid=GRID8)
            entry["audit"] = {
                "passes": bool(r.passes),
                "audible": r.audible,
                "strong_ok": r.strong_ok,
                "weak_in_scale": r.weak_in_scale,
                "tagged_ornaments": r.tagged_ornaments,
                "tagged_resolving": r.tagged_resolving,
                "tagged_non_resolving": r.tagged_non_resolving,
                "untagged_out_of_scale": r.untagged_out_of_scale,
                "strong_violations": r.strong_violations,
                "collisions": r.collisions,
            }
        per_voice.append(entry)

    return {
        "path": path,
        "bytes": os.path.getsize(path),
        "ntracks": len(tracks),
        "voice_tracks": len(voice_tracks),
        "track_lengths": lens,
        "zero_drift": zero_drift,
        "total_off_8th": tot_off8,
        "total_off_16th": tot_off16,
        "voices": per_voice,
    }


if __name__ == "__main__":
    files = {
        "phase1": os.path.join(MIDI_DIR, "283-baroque-cellular-automaton-phase1.mid"),
        "perfect": os.path.join(MIDI_DIR, "283-baroque-cellular-automaton-perfect.mid"),
        "humanized": os.path.join(MIDI_DIR, "283-baroque-cellular-automaton-humanized.mid"),
    }
    report = {}
    for name, path in files.items():
        r = analyze(path, harmony=(name != "phase1"))
        report[name] = r
        print(f"--- {name} ---")
        print(json.dumps(r, indent=2))

    out = os.path.join(ANALYSIS_DIR, "verify.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("wrote", out)
