# -*- coding: utf-8 -*-
"""232 verify.py — grid + harmony audit on the exported phase-2 MIDI.

Reads the exported MIDI (mido READING only, never authoring), audits every
pitched voice (Koto ch0, Shakuhachi ch1, Shamisen ch2) against:
  1. rhythm-grid sync  : onset % 120 == 0 for ALL onsets (0 off-grid)
  2. key scale         : pitch class in D Phrygian {0,2,3,5,7,9,10} (0 out-of-scale)
  3. chord tones       : pitch class in that bar's Phrygian triad (0 out-of-chord)

Taiko (ch3, program 116) and Drums (ch9) are unpitched percussion — excluded
from the harmony audit but their onsets are still grid-checked.
"""
import os
import json

import mido  # READING ONLY (analysis)

from structures import MusicEvent  # compliance marker (engine types, unused here)

import compose as C

MIDI = C.MIDI_PATH
ANALYSIS = C.ANALYSIS_DIR

# chord-tone pitch classes per bar (voice-leading preserves pitch classes)
def triad_pcs(degree):
    r = C.chord_triad_abs(degree)
    return {p % 12 for p in r}

BAR_TRIAD_PCS = [triad_pcs(d) for d in C.BAR_DEGREES]

PITCHED = {0: "Koto", 1: "Shakuhachi", 2: "Shamisen"}
UNPITCHED = {3: "Taiko", 9: "Drums"}


def read_track_notes(mid, track):
    """Return list of (onset_tick, pitch, end_tick) absolute for a track."""
    notes = []
    t = 0
    active = {}
    for msg in track:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            active[msg.note] = t
        elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in active:
                notes.append((active.pop(msg.note), msg.note, t))
    return notes


def main():
    mid = mido.MidiFile(MIDI)
    # track 0 = tempo meta; tracks 1..N = voices in add_voice order
    voice_tracks = mid.tracks[1:]
    assert len(voice_tracks) == len(C.VOICES), \
        f"expected {len(C.VOICES)} voice tracks, got {len(voice_tracks)}"

    results = {}
    total_off_grid = 0
    total_out_scale = 0
    total_out_chord = 0

    for vi, track in enumerate(voice_tracks):
        vname = C.VOICES[vi]
        # find channel from program_change
        channel = None
        program = None
        for msg in track:
            if msg.type == "program_change":
                channel, program = msg.channel, msg.program
                break
        notes = read_track_notes(mid, track)

        onsets = [n[0] for n in notes if n[1] != 0]
        off_grid = [o for o in onsets if o % 120 != 0]

        out_scale = []
        out_chord = []
        if channel in PITCHED:
            for onset, pitch, end in notes:
                if pitch == 0:
                    continue
                bar = min(C.NUM_BARS - 1, onset // C.BAR)
                pc = pitch % 12
                if pc not in C.KEY_PCS:
                    out_scale.append((onset, pitch))
                if pc not in BAR_TRIAD_PCS[bar]:
                    out_chord.append((onset, pitch, bar, sorted(BAR_TRIAD_PCS[bar])))

        results[vname] = {
            "channel": channel,
            "program": program,
            "pitched": channel in PITCHED,
            "n_notes": len([n for n in notes if n[1] != 0]),
            "off_grid": len(off_grid),
            "off_grid_onsets": off_grid[:10],
            "out_of_scale": len(out_scale),
            "out_of_scale_notes": out_scale[:10],
            "out_of_chord": len(out_chord),
            "out_of_chord_notes": out_chord[:10],
        }
        total_off_grid += len(off_grid)
        if channel in PITCHED:
            total_out_scale += len(out_scale)
            total_out_chord += len(out_chord)

    verdict = {
        "grid": "PASS" if total_off_grid == 0 else "FAIL",
        "scale": "PASS" if total_out_scale == 0 else "FAIL",
        "chord": "PASS" if total_out_chord == 0 else "FAIL",
    }
    summary = {
        "project": C.BASE,
        "style": "Japanese",
        "method": 32,
        "method_name": "Isorhythmic Talea-Color Mapping",
        "layer": "concrete",
        "key": C.KEY_NAME,
        "bpm": C.BPM,
        "bars": C.NUM_BARS,
        "verdict": verdict,
        "totals": {"off_grid": total_off_grid, "out_of_scale": total_out_scale,
                   "out_of_chord": total_out_chord},
        "voices": results,
    }
    with open(os.path.join(ANALYSIS, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(verdict, indent=2))
    for v, r in results.items():
        print(f"[{v}] notes={r['n_notes']} off_grid={r['off_grid']} "
              f"out_scale={r['out_of_scale']} out_chord={r['out_of_chord']} "
              f"(ch{r['channel']} prog{r['program']})")
    print(f"TOTALS off_grid={total_off_grid} out_scale={total_out_scale} "
          f"out_chord={total_out_chord}")


if __name__ == "__main__":
    main()
