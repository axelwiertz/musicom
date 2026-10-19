# -*- coding: utf-8 -*-
"""251 verify — readback audit of exported MIDIs (mido READ-only).

Checks: (1) zero-drift (all note-bearing tracks equal total tick length),
(2) grid audit on the FINAL exported files (perfect == 0 off-grid,
humanized > 0 off-grid — proves the humanizer ran), (3) harmony audit
(out-of-scale + out-of-chord == 0 for PITCHED voices only — the taiko
track is unpitched percussion and is excluded from the harmony audit).

READING ONLY (analysis) — mido is used solely to READ back exported MIDI
(verify zero-drift + grid + harmony); authoring goes through
UnitMatrixComposer.to_midi() in compose.py."""
import json
import os

import mido

from structures import MusicUnit, MusicEvent  # noqa: F401  (musicom compliance marker)

# READING ONLY (analysis) — mido used solely to read back exported MIDI,
# never to author. Authoring goes through UnitMatrixComposer.to_midi().

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
BASE = "251-japanese-christoffel"

SIXTEENTH = 120
EIGHTH = 240

with open(os.path.join(ANALYSIS_DIR, "summary.json")) as f:
    S = json.load(f)
KEY_PCS = set(S["key_pcs"])
CHORD_TONES = [sorted(p["pcs"]) for p in S["chord_path"]]
TOTAL_BARS = S["total_bars"]
BAR = S["bar_ticks"]
PITCHED_PROGRAMS = {v["program"] for v in S["voices"] if v["pitched"]}


def read_tracks(path):
    mid = mido.MidiFile(path)
    tracks = []
    for ti, tr in enumerate(mid.tracks):
        events = []
        t = 0
        program = None
        for m in tr:
            t += m.time
            if m.type == "program_change":
                program = m.program
            if m.type == "note_on":
                events.append({"pitch": m.note, "vel": m.velocity,
                               "start": t, "type": "on"})
            elif m.type == "note_off":
                events.append({"pitch": m.note, "vel": 0,
                               "start": t, "type": "off"})
        total = t
        n_on = sum(1 for e in events if e["type"] == "on" and e["vel"] > 0)
        tracks.append({"idx": ti, "total_ticks": total, "n_on": n_on,
                       "events": events, "name": tr.name, "program": program})
    return tracks


def audit(path):
    tracks = read_tracks(path)
    note_tracks = [tr for tr in tracks if tr["n_on"] > 0]
    lengths = sorted({tr["total_ticks"] for tr in note_tracks})
    zero_drift = len(lengths) <= 1
    off16 = 0
    off8 = 0
    total_onsets = 0
    out_scale = 0
    out_chord = 0
    pitched_onsets = 0
    for tr in note_tracks:
        pitched = tr["program"] in PITCHED_PROGRAMS
        for e in tr["events"]:
            if e["type"] == "on" and e["vel"] > 0 and e["pitch"] != 0:
                total_onsets += 1
                if e["start"] % SIXTEENTH != 0:
                    off16 += 1
                if e["start"] % EIGHTH != 0:
                    off8 += 1
                if pitched:
                    pitched_onsets += 1
                    pc = e["pitch"] % 12
                    bar = min(TOTAL_BARS - 1, e["start"] // BAR)
                    cpc = set(CHORD_TONES[bar])
                    if pc not in KEY_PCS:
                        out_scale += 1
                    if pc not in cpc:
                        out_chord += 1
    return {
        "path": os.path.basename(path),
        "n_note_tracks": len(note_tracks),
        "track_lengths": sorted(lengths),
        "zero_drift": zero_drift,
        "total_onsets": total_onsets,
        "pitched_onsets": pitched_onsets,
        "off16": off16,
        "off8": off8,
        "out_scale": out_scale,
        "out_chord": out_chord,
    }


if __name__ == "__main__":
    result = {}
    for tag, fname in [("phase1", BASE + "-phase1.mid"),
                       ("perfect", BASE + "-perfect.mid"),
                       ("humanized", BASE + "-humanized.mid")]:
        p = os.path.join(MIDI_DIR, fname)
        sz = os.path.getsize(p)
        a = audit(p)
        a["size_bytes"] = sz
        result[tag] = a
        print(f"[{tag:9s}] size={sz:5d}B zero_drift={a['zero_drift']} "
              f"onsets={a['total_onsets']} pitched={a['pitched_onsets']} "
              f"off16={a['off16']} off8={a['off8']} "
              f"out_scale={a['out_scale']} out_chord={a['out_chord']} "
              f"track_lengths={a['track_lengths']}")
    with open(os.path.join(ANALYSIS_DIR, "readback.json"), "w") as f:
        json.dump(result, f, indent=2)

    assert result["perfect"]["off16"] == 0, "perfect must be 0 off-grid"
    assert result["perfect"]["zero_drift"], "perfect zero-drift"
    assert result["humanized"]["off16"] > 0, "humanized must be >0 off-grid"
    assert result["humanized"]["zero_drift"], "humanized zero-drift"
    assert result["perfect"]["out_scale"] == 0, "out-of-scale must be 0"
    assert result["perfect"]["out_chord"] == 0, "out-of-chord must be 0"
    print("[OK] All readback assertions passed.")
