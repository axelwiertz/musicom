# -*- coding: utf-8 -*-
# READING ONLY (analysis): this file READS exported MIDI to verify the
# composition (grid/harmony audits). Authoring is done by compose.py through
# UnitMatrixComposer. mido is used strictly for reading, per AGENTS.md.
"""081-funk-schillinger audit: grid sync + harmony (scale/chord) verification.

Reads the exported phase-2 MIDI (mido allowed for READING), reconstructs
bar boundaries from tempo (100 BPM, 480 TPB, 4/4, 24 bars, 6 sections x 4),
and reports per-voice:
  - onset grid audit: 16th (120) and 8th (240) off-grid counts (must be 0)
  - harmony audit: out-of-scale + out-of-chord counts (must be 0)
"""
import os
import json

import mido
from structures import MusicUnit, MusicEvent  # noqa: F401  (compliant import marker)

PROJ = "/opt/data/projects/Styles/Funk/081-funk-schillinger"
MIDI_PATH = os.path.join(PROJ, "MIDI/081-funk-schillinger.mid")

BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS          # 1920
N_SECTIONS = 6
BARS_PER = 4
N_BARS = 24
SECTION_TICKS = BAR * BARS_PER

# Bb major pitch classes: Bb C D Eb F G A
SCALE_PCS = {10, 0, 2, 3, 5, 7, 9}
assert SCALE_PCS == {58 % 12, 60 % 12, 62 % 12, 63 % 12, 65 % 12, 67 % 12, 69 % 12}

CHORDS = {
    58: [58, 62, 65],   # Bb  I
    60: [60, 63, 67],   # Cm  ii
    62: [62, 65, 69],   # Dm  iii
    63: [63, 67, 70],   # Eb  IV
    65: [65, 69, 72],   # F   V
}
PROG = ([58, 60, 62, 65] * 2) + [58, 63, 65, 58] + [58, 65, 58, 60] + \
       [58, 60, 62, 65] + [58, 63, 60, 58]
assert len(PROG) == N_BARS


def chord_for_bar(bar):
    return CHORDS[PROG[bar]]


mid = mido.MidiFile(MIDI_PATH)
print("MIDI tracks:", len(mid.tracks), "length_ticks:", mid.length)

voices = []
for ti, track in enumerate(mid.tracks):
    name = None
    notes = []
    abs_t = 0
    for msg in track:
        abs_t += msg.time
        if msg.type == "program_change":
            name = f"prog{msg.program}"
        if msg.type == "note_on" and msg.velocity > 0:
            notes.append((msg.note, abs_t, msg.velocity, msg.channel))
    if not notes:
        continue
    voices.append({"track": ti, "name": name, "notes": notes})

print("voices with notes:", len(voices))
results = {}
for v in voices:
    name = v["name"] or f"track{v['track']}"
    is_perc = any(ch == 9 for (_p, _t, _vel, ch) in v["notes"])
    pitched = [(p, t) for (p, t, vel, ch) in v["notes"] if p > 0 and ch != 9]
    all_onsets = [t for (p, t, vel, ch) in v["notes"] if p > 0]
    onsets = [t for (p, t) in pitched]
    off16 = [o for o in all_onsets if o % 120 != 0]
    off8 = [o for o in all_onsets if o % 240 != 0]
    out_scale = []
    out_chord = []
    for p, t in pitched:
        if (p % 12) not in SCALE_PCS:
            out_scale.append((p, t))
        bar = min(t // BAR, N_BARS - 1)
        tones = chord_for_bar(bar)
        chord_pcs = {c % 12 for c in tones}
        if (p % 12) not in chord_pcs:
            out_chord.append((p, t, bar))
    results[name] = {
        "n_onsets": len(onsets),
        "n_total_onsets": len(all_onsets),
        "off16": len(off16), "off8": len(off8),
        "is_percussion": is_perc,
        "out_of_scale": len(out_scale), "out_of_chord": len(out_chord),
        "out_of_chord_examples": out_chord[:5],
    }
    print(f"  {name:12s} total_onsets={len(all_onsets):3d} "
          f"off16={len(off16):3d} off8={len(off8):3d} "
          f"out_scale={len(out_scale):3d} out_chord={len(out_chord):3d}"
          f"{' [perc]' if is_perc else ''}")

with open(os.path.join(PROJ, "Analysis/audit.json"), "w") as f:
    json.dump(results, f, indent=2)
print("audit written to Analysis/audit.json")
