# -*- coding: utf-8 -*-
# READING ONLY (analysis) — mido is used only to read back the exported MIDI
# for the grid/harmony audit. No MIDI authoring happens here.
"""Verify grid + harmony + zero-drift on the exported phase-2 MIDI (read-only mido)."""
import json
import os

import mido

from structures import MusicEvent
from rules.progression import Scale7ChordDegree

KEY_ROOT_MIDI = 62
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}
BAR = 1920
BAR_DEGREES = [
    0, 0, 5, 5,
    0, 5, 6, 5, 3, 0, 5, 6,
    3, 4, 5, 6, 3, 4, 0, 6,
    0, 5, 3, 4, 5, 6, 0, 0,
    0, 0, 5, 0,
]

PROG_NAME = {8: "Lead(Celesta)", 19: "Pad(Organ)", 42: "Bass(Cello)",
             46: "Sparkle(Harp)"}
CH9_NAME = "Drums"


def triad_pcs(degree):
    def dn(d):
        return Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, d)
    return {dn(degree) % 12, dn(degree + 2) % 12, dn(degree + 4) % 12}


def analyze(path):
    mf = mido.MidiFile(path)
    tpb = mf.ticks_per_beat
    results = []
    track_lengths = []
    for idx, tr in enumerate(mf.tracks):
        channel = None
        program = None
        for m in tr:
            if m.type == "program_change":
                program = m.program
                channel = m.channel
            elif m.type == "note_on" and m.velocity > 0 and channel is None:
                channel = m.channel
        t = 0
        notes = []
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0 and m.note > 0:
                notes.append(MusicEvent(pitch=m.note, volume=m.velocity,
                                        start_tick=t, end_tick=t + 1))
        if not notes:
            continue
        track_lengths.append(t)
        is_drums = (channel == 9)
        name = CH9_NAME if is_drums else PROG_NAME.get(program, f"track{idx}(prog{program})")

        off_grid_16 = [e for e in notes if e.start_tick % 120 != 0]
        off_grid_8 = [e for e in notes if e.start_tick % 240 != 0]

        out_scale = 0
        out_chord = 0
        if not is_drums:
            for e in notes:
                pc = e.pitch % 12
                bar = e.start_tick // BAR
                bar = min(bar, len(BAR_DEGREES) - 1)
                if pc not in KEY_PCS:
                    out_scale += 1
                if pc not in triad_pcs(BAR_DEGREES[bar]):
                    out_chord += 1

        results.append({
            "voice": name, "channel": channel, "program": program,
            "notes": len(notes), "off_grid_16th": len(off_grid_16),
            "off_grid_8th": len(off_grid_8), "out_of_scale": out_scale,
            "out_of_chord": out_chord,
        })
    return results, track_lengths, tpb


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    midi = os.path.join(base, "MIDI", "234-ambient-pareto-build.mid")
    results, lengths, tpb = analyze(midi)

    total_notes = sum(r["notes"] for r in results)
    total_off16 = sum(r["off_grid_16th"] for r in results)
    total_off8 = sum(r["off_grid_8th"] for r in results)
    total_oscale = sum(r["out_of_scale"] for r in results)
    total_ochord = sum(r["out_of_chord"] for r in results)

    print("=== GRID + HARMONY AUDIT (phase-2 MIDI readback) ===")
    print(f"tpb={tpb}  tracks={len(results)}  total_notes={total_notes}")
    for r in results:
        print(f"  {r['voice']:16s} ch{r['channel']:>2} prog{r['program']:>3} "
              f"notes={r['notes']:>4} off16={r['off_grid_16th']} off8={r['off_grid_8th']} "
              f"out_scale={r['out_of_scale']} out_chord={r['out_of_chord']}")
    print(f"TOTAL: off16={total_off16} off8={total_off8} "
          f"out_scale={total_oscale} out_chord={total_ochord}")
    print(f"zero-drift (track lengths): {lengths} -> equal={len(set(lengths)) == 1}")

    out = {
        "tpb": tpb, "per_voice": results,
        "totals": {"notes": total_notes, "off_grid_16th": total_off16,
                   "off_grid_8th": total_off8, "out_of_scale": total_oscale,
                   "out_of_chord": total_ochord},
        "track_lengths": lengths, "zero_drift_equal": len(set(lengths)) == 1,
    }
    with open(os.path.join(base, "Analysis", "verification.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("wrote Analysis/verification.json")
