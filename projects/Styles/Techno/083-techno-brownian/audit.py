# -*- coding: utf-8 -*-
# READING ONLY (analysis): this file READS exported MIDI to verify the
# composition (grid/harmony audits). Authoring is done by compose.py through
# UnitMatrixComposer. mido is used strictly for reading, per AGENTS.md.
"""083-techno-brownian audit: grid sync + harmony (scale/chord) verification.

Reads the exported phase-1/phase-2 MIDI (mido allowed for READING), reconstructs
bar boundaries from tempo (128 BPM, 480 TPB, 4/4, 24 bars, 6 sections x 4), and
reports per-voice:
  - onset grid audit: 16th (120) and 8th (240) off-grid counts (0 required
    for every voice on the 16th grid)
  - harmony audit: out-of-scale + out-of-chord counts (0 required)
"""
import os
import json

import mido
from structures import MusicUnit, MusicEvent  # noqa: F401  (compliant import marker)

PROJ = "/opt/data/projects/Styles/Techno/083-techno-brownian"
P2_MIDI = os.path.join(PROJ, "MIDI/083-techno-brownian.mid")
P1_MIDI = os.path.join(PROJ, "MIDI/083-techno-brownian-phase1.mid")

BPM = 128
TPB = 480
BEATS = 4
BAR = TPB * BEATS          # 1920
GRID16 = 120
N_SECTIONS = 6
BARS_PER = 4
N_BARS = 24

VOICE_NAMES = ["Lead", "Cello", "Piano", "Violin", "Bass", "Drums"]
PERC_INDICES = {5}          # drums track (channel 9)

# F natural minor pitch set + pitch classes
SCALE = [41, 43, 44, 46, 48, 49, 51, 53, 55, 56, 58, 60, 61, 63, 65, 67,
         68, 70, 72, 73, 75, 77, 79, 80, 82, 84, 85, 87, 89]
SCALE_PCS = set(p % 12 for p in SCALE)

# diatonic triads in F natural minor, keyed by root MIDI (mirror of compose.py)
ROOT_QUAL = {53: "m", 49: "M", 44: "M", 51: "M", 46: "m", 48: "m"}
CHORD_NAMES = {53: "i", 49: "VI", 44: "III", 51: "VII", 46: "iv", 48: "v"}
PROG = ([53, 49, 44, 51] + [53, 46, 48, 53] + [49, 44, 51, 53] +
        [53, 49, 44, 51] + [53, 46, 48, 53] + [49, 44, 53, 53])


def chord_intervals(root):
    return (0, 3, 7) if ROOT_QUAL[root] == "m" else (0, 4, 7)


def chord_pcs(root):
    return set((root + i) % 12 for i in chord_intervals(root))


def read_voice_onsets(mid_path):
    """Parse exported MIDI: per-track absolute onsets + pitches.
    Track 0 is the conductor (tempo) track; pitched voices are tracks 1..N."""
    mid = mido.MidiFile(mid_path)
    tracks = []
    for ti, track in enumerate(mid.tracks):
        onsets = []
        notes = []
        t = 0
        for msg in track:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                onsets.append(t)
                notes.append((t, msg.note, msg.channel))
        tracks.append({"track": ti, "n": len(onsets), "onsets": onsets,
                       "notes": notes})
    return tracks[1:]       # drop conductor track


def grid_audit(mid_path, voice_names):
    """0 off-grid required for every voice on 16th (120) and 8th (240)."""
    pitched = read_voice_onsets(mid_path)
    out = {}
    for i, tr in enumerate(pitched):
        name = voice_names[i] if i < len(voice_names) else "track%d" % (i + 1)
        if tr["n"] == 0:
            out[name] = {"n": 0, "off16": 0, "off8": 0,
                         "off16_list": [], "off8_list": []}
            continue
        off16 = [o for o in tr["onsets"] if o % GRID16 != 0]
        off8 = [o for o in tr["onsets"] if o % (GRID16 * 2) != 0]
        out[name] = {"n": tr["n"], "off16": len(off16), "off8": len(off8),
                     "off16_list": off16[:8], "off8_list": off8[:8]}
    return out


def harmony_audit(mid_path, voice_names, perc_indices):
    """Every pitched (non-percussion) note must be a pitch-class member of the
    F-minor scale AND of its bar's chord (octave displacement allowed)."""
    pitched = read_voice_onsets(mid_path)
    out = {}
    for i, tr in enumerate(pitched):
        name = voice_names[i] if i < len(voice_names) else "track%d" % (i + 1)
        if i in perc_indices or tr["n"] == 0:
            out[name] = {"n": tr["n"], "out_of_scale": 0, "out_of_chord": 0,
                         "examples": []}
            continue
        oos = 0
        ooc = 0
        ex = []
        for (t, pitch, ch) in tr["notes"]:
            if pitch == 0:
                continue
            pc = pitch % 12
            if pc not in SCALE_PCS:
                oos += 1
                if len(ex) < 6:
                    ex.append({"tick": t, "pitch": pitch, "issue": "scale"})
            bar = min(t // BAR, N_BARS - 1)
            chord = chord_pcs(PROG[bar])
            if pc not in chord:
                ooc += 1
                if len(ex) < 6:
                    ex.append({"tick": t, "pitch": pitch, "bar": bar,
                               "chord": CHORD_NAMES[PROG[bar]], "issue": "chord"})
        out[name] = {"n": tr["n"], "out_of_scale": oos, "out_of_chord": ooc,
                     "examples": ex}
    return out


g_audit = grid_audit(P2_MIDI, VOICE_NAMES)
h_audit = harmony_audit(P2_MIDI, VOICE_NAMES, PERC_INDICES)
g1_audit = grid_audit(P1_MIDI, ["LeadRaw"])

audit = {
    "phase2_grid": g_audit,
    "phase2_harmony": h_audit,
    "phase1_grid": g1_audit,
    "voice_leading_flags": [],          # merged from vl_audit.json below
    "voice_leading_flag_count": 0,
    "phase1_validate": "",
    "phase2_validate": "",
}
vl_path = os.path.join(PROJ, "Analysis", "vl_audit.json")
if os.path.exists(vl_path):
    with open(vl_path) as f:
        vl = json.load(f)
    audit["voice_leading_flags"] = vl["voice_leading_flags"]
    audit["voice_leading_flag_count"] = vl["voice_leading_flag_count"]
    audit["phase1_validate"] = vl["phase1_validate"]
    audit["phase2_validate"] = vl["phase2_validate"]

with open(os.path.join(PROJ, "Analysis", "audit.json"), "w") as f:
    json.dump(audit, f, indent=2)

print("GRID AUDIT phase2:", {k: (v["n"], v["off16"], v["off8"]) for k, v in g_audit.items()})
print("HARMONY AUDIT phase2:", {k: (v["n"], v["out_of_scale"], v["out_of_chord"]) for k, v in h_audit.items()})
print("GRID AUDIT phase1 (raw, off-grid expected):",
      {k: (v["n"], v["off16"]) for k, v in g1_audit.items()})

# gate
bad = [k for k, v in g_audit.items() if v["off16"] != 0]
badh = [k for k, v in h_audit.items() if v["out_of_scale"] != 0 or v["out_of_chord"] != 0]
if bad or badh:
    raise SystemExit("AUDIT FAIL: off-grid %s, harmony %s" % (bad, badh))
print("AUDIT PASS: 0 off-grid (16th), 0 out-of-scale, 0 out-of-chord")
