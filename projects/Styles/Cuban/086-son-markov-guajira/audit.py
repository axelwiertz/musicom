#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""086 audit: grid + scale + chord verification on exported MIDI files.

READ-ONLY mido analysis (authoring is engine-only; this is the mandatory
verification pass). Reports per-voice off-grid onsets (16th=120, 8th=240),
out-of-scale notes, and out-of-chord notes (chord = the phase-2 harmonic plan
for the bar where the note STARTS). All counts must be 0 for phase 2.
Phase 1 is the raw generative draft: off-grid onsets are EXPECTED (that is
the raw fingerprint), scale is loose (raw degree sampling) - reported for
contrast only.
"""
import json
import os
import sys

import mido  # READING ONLY (analysis)  # noqa: E402
from structures import MusicUnit, MusicEvent  # noqa: F401  (compliant import marker)

MIDI_DIR = "/opt/data/projects/Styles/Cuban/086-son-markov-guajira/MIDI"
P1 = os.path.join(MIDI_DIR, "086-son-markov-guajira-phase1.mid")
P2 = os.path.join(MIDI_DIR, "086-son-markov-guajira.mid")
OUT = "/opt/data/projects/Styles/Cuban/086-son-markov-guajira/Analysis/audit.json"

BAR = 1920
SECTION = BAR * 4

# A harmonic minor scale pcs (natural minor + raised 7th for the V7 chord)
KEY_PCS = {9, 11, 0, 2, 4, 5, 7, 8}
# Harmonic plan per bar (must match compose.py PROG exactly)
PROG = [0, 0, 0, 0, 0, 6, 5, 0, 1, 0, 4, 0, 3, 6, 4, 0,
        5, 3, 6, 0, 0, 6, 4, 0]
# bars voiced as E7 (V7, harmonic-minor leading tone)
V7_BARS = {10, 14, 23}
# absolute A-minor triad pcs per degree (0=A, 1=B, 2=C, 3=D, 4=E, 5=F, 6=G)
TRIAD = {0: {9, 0, 4}, 1: {11, 2, 5}, 2: {0, 4, 7}, 3: {2, 5, 9},
         4: {4, 7, 11}, 5: {5, 9, 0}, 6: {7, 11, 2}}
# degree-4 voiced as E7 (dominant, G# = pc8)
E7 = {4, 8, 11, 2}
DEG_NAME = {0: "Am", 1: "Bdim", 2: "C", 3: "Dm", 4: "E", 5: "F", 6: "G"}

GM_NAME = {24: "Tres (nylon gtr)", 1: "Piano", 25: "Ac.Guitar", 43: "Contrabass",
           56: "Trumpet", 12: "Marimba", 0: "Drums/ch9"}


def bar_chord_pcs(bar):
    if bar in V7_BARS:
        return E7
    return TRIAD[PROG[bar]]


def parse_tracks(path):
    mid = mido.MidiFile(path)
    voices = []
    for ti, track in enumerate(mid.tracks):
        if ti == 0:
            continue
        program, channel = 0, None
        for msg in track:
            if msg.type == "program_change":
                program, channel = msg.program, msg.channel
        # single pass: close a same-pitch note when a new onset for that
        # pitch arrives (percussion overlaps) or on note_off / vel-0 on.
        abstick = 0
        active = {}          # pitch -> [start, vel]
        notes = []
        def close(pitch, end_tick):
            if pitch in active:
                s, vel = active.pop(pitch)
                notes.append({"pitch": pitch, "vel": vel,
                              "start": s, "end": max(end_tick, s + 1)})
        for msg in track:
            abstick += msg.time
            if msg.type == "note_on":
                if msg.velocity > 0:
                    close(msg.note, abstick)
                    active[msg.note] = [abstick, msg.velocity]
                else:
                    close(msg.note, abstick)
            elif msg.type == "note_off":
                close(msg.note, abstick)
        # close anything left open at the last tick of the track
        for pitch in list(active):
            notes.append({"pitch": pitch, "vel": active[pitch][1],
                          "start": active[pitch][0],
                          "end": min(active[pitch][0] + 240, abstick + 1)})
        voices.append({"track": ti, "program": program, "channel": channel,
                       "notes": notes})
    return voices


def audit(path, label, expect_quantized=True):
    voices = parse_tracks(path)
    res = {"label": label, "voices": []}
    for v in voices:
        is_perc = (v["channel"] == 9)
        notes = [n for n in v["notes"] if n["pitch"] > 0]
        onsets = [n["start"] for n in notes]
        off16 = [o for o in onsets if o % 120 != 0]
        off8 = [o for o in onsets if o % 240 != 0]
        out_scale = []
        out_chord = []
        if not is_perc:          # scale/chord audit only for pitched voices
            for n in notes:
                pc = n["pitch"] % 12
                if pc not in KEY_PCS:
                    out_scale.append(n)
                bar = n["start"] // BAR
                if bar < 24 and pc not in bar_chord_pcs(bar):
                    out_chord.append(n)
        res["voices"].append({
            "track": v["track"],
            "program": v["program"],
            "gm": GM_NAME.get(v["program"], v["program"]),
            "channel": v["channel"],
            "percussion": is_perc,
            "note_count": len(notes),
            "off_grid_16th": len(off16),
            "off_grid_8th": len(off8),
            "out_of_scale": len(out_scale),
            "out_of_chord": len(out_chord),
            "first_onset": min(onsets) if onsets else None,
            "last_end": max((n["end"] for n in notes), default=None),
            "sample_out_scale": [n["pitch"] for n in out_scale[:5]],
            "sample_out_chord": [n["pitch"] for n in out_chord[:5]],
        })
    return res


def main():
    res = {"files": []}
    res["files"].append(audit(P2, "phase2 (rules)", expect_quantized=True))
    res["files"].append(audit(P1, "phase1 (raw)", expect_quantized=False))
    with open(OUT, "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
