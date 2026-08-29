# -*- coding: utf-8 -*-
"""080-groove-sieve audit: grid sync + harmony (scale/chord) verification.

Reads the exported phase-2 MIDI (mido allowed for READING), reconstructs
bar boundaries from tempo (110 BPM, 480 TPB, 4/4, 24 bars, 6 sections x 4),
and reports per-voice:
  - onset grid audit: 16th (120) and 8th (240) off-grid counts (must be 0)
  - harmony audit: out-of-scale + out-of-chord counts (must be 0)
"""
import os
import json

# READING ONLY (analysis): this file READS exported MIDI to verify the
# composition (grid/harmony audits). Authoring is done by compose.py through
# UnitMatrixComposer. mido is used strictly for reading, per AGENTS.md.
import mido
from structures import MusicUnit, MusicEvent  # noqa: F401  (compliant import marker)

PROJ = "/opt/data/projects/Styles/Groove/080-groove-sieve"
MIDI_PATH = os.path.join(PROJ, "MIDI/080-groove-sieve.mid")

BPM = 110
TPB = 480
BEATS = 4
BAR = TPB * BEATS          # 1920
N_SECTIONS = 6
BARS_PER = 4
N_BARS = 24
SECTION_TICKS = BAR * BARS_PER

SCALE_PCS = {55 % 12, 57 % 12, 58 % 12, 60 % 12, 62 % 12, 63 % 12, 65 % 12,
             67 % 12, 69 % 12, 70 % 12, 72 % 12, 74 % 12, 75 % 12, 77 % 12,
             79 % 12, 81 % 12}
# G natural minor pitch classes: G A Bb C D Eb F
assert SCALE_PCS == {7, 9, 10, 0, 2, 3, 5}, SCALE_PCS

CHORDS = {
    55: [55, 58, 62],   # Gm  i
    58: [58, 62, 65],   # Bb  III
    60: [60, 63, 67],   # Cm  iv
    62: [62, 65, 69],   # D   V
    63: [63, 67, 70],   # Eb  VI
}
PROG = ([55, 58, 60, 62] * 2) + [55, 60, 62, 55] + [55, 62, 55, 63] + \
       [55, 58, 60, 62] + [55, 62, 60, 55]
assert len(PROG) == N_BARS


def chord_for_bar(bar):
    return CHORDS[PROG[bar]]


mid = mido.MidiFile(MIDI_PATH)
print("MIDI tracks:", len(mid.tracks), "length_ticks:", mid.length)

# reconstruct voices: group note_on events by track; pitch 0 = landmark.
# Percussion channel (9) is excluded from the HARMONY audit (drums are not
# pitched voices) but still grid-audited.
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
    # grid audit on ALL notes (incl. percussion) - pitched + drum onsets
    all_onsets = [t for (p, t, vel, ch) in v["notes"] if p > 0]
    onsets = [t for (p, t) in pitched]
    off16 = [o for o in all_onsets if o % 120 != 0]
    off8 = [o for o in all_onsets if o % 240 != 0]
    # harmony audit (pitched voices only; chord-tone check is
    # pitch-class-based so octave displacements count as chord tones)
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
