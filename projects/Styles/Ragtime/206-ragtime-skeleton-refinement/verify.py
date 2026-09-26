# -*- coding: utf-8 -*-
"""206-ragtime-skeleton-refinement - READ-ONLY verification (mido allowed for READING).

# READING ONLY (analysis)

Audits the exported phase-2 MIDI (never authoring — composition is engine-only):
  - grid audit: every pitched voice onset must be on 16th (120) / 8th (240) grid
  - harmony audit: every pitched note PC in key scale AND in its bar's chord tones
  - zero-drift: all tracks equal length
Also reports phase-1 raw off-grid character (expected: many off-grid).
"""
import json
import os
from structures import MusicUnit, MusicEvent  # compliant musicom import marker
import mido

PROJ = "/opt/data/repos/musicom/projects/Styles/Ragtime/206-ragtime-skeleton-refinement"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

TPB = 480
BAR_TICKS = 1920
GRID16 = 120
GRID8 = 240

# same harmony constants as compose.py (kept in sync)
SCALE_SET = {0, 2, 4, 5, 7, 9, 11}
CHORDS = {
    "C": {0, 4, 7}, "Cmaj7": {0, 4, 7, 11}, "Dm": {2, 5, 9},
    "Dm7": {2, 5, 9, 0}, "Em7": {4, 7, 11, 2}, "F": {5, 9, 0},
    "Fmaj7": {5, 9, 0, 4}, "G7": {7, 11, 2, 5}, "Am": {9, 0, 4},
    "Am7": {9, 0, 4, 7},
}
SECTIONS = ["Intro", "A", "B", "A2", "Trio", "Coda"]
BARS = [4, 8, 8, 8, 8, 4]
SECTION_CHORDS = {
    "Intro": ["G7", "G7", "G7", "G7"],
    "A":     ["C", "Cmaj7", "Am", "Dm7", "G7", "C", "F", "G7"],
    "B":     ["F", "Fmaj7", "Dm", "G7", "Em7", "Am", "Dm7", "G7"],
    "A2":    ["C", "Cmaj7", "Am", "Dm7", "G7", "C", "G7", "C"],
    "Trio":  ["F", "F", "Dm", "G7", "C", "Am", "F", "G7"],
    "Coda":  ["C", "G7", "C", "C"],
}
BAR_CHORD_PCS = []
for s in SECTIONS:
    for n in SECTION_CHORDS[s]:
        BAR_CHORD_PCS.append(CHORDS[n])


def audit(mid_path, voices):
    mid = mido.MidiFile(mid_path)
    assert len(mid.tracks) >= 1 + len(voices), "track count mismatch"
    result = {"voices": {}, "track_lengths": []}
    # track 0 = tempo meta
    for vi, (track, vname) in enumerate(zip(mid.tracks[1:], voices)):
        onsets = []
        notes = []      # (pitch, onset_tick)
        t = 0
        for msg in track:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                if msg.note > 0:
                    onsets.append(t)
                    notes.append((msg.note, t))
        result["track_lengths"].append(t)
        # grid audit
        off16 = [o for o in onsets if o % GRID16 != 0]
        off8 = [o for o in onsets if o % GRID8 != 0]
        # harmony audit
        out_scale = []
        out_chord = []
        for pitch, on in notes:
            bar = on // BAR_TICKS
            pc = pitch % 12
            if pc not in SCALE_SET:
                out_scale.append((pitch, on))
            chord_pcs = BAR_CHORD_PCS[bar] if bar < len(BAR_CHORD_PCS) else set()
            if pc not in chord_pcs:
                out_chord.append((pitch, on))
        result["voices"][vname] = {
            "n_onsets": len(onsets),
            "n_notes": len(notes),
            "off_grid_16th": len(off16),
            "off_grid_8th": len(off8),
            "out_of_scale": len(out_scale),
            "out_of_chord": len(out_chord),
        }
    # zero-drift: all tracks equal length
    lengths = set(result["track_lengths"])
    result["zero_drift"] = (len(lengths) == 1)
    result["track_lengths"] = list(lengths)
    return result


def main():
    p2 = os.path.join(MIDI_DIR, "206-ragtime-skeleton-refinement.mid")
    p1 = os.path.join(MIDI_DIR, "206-ragtime-skeleton-refinement-phase1.mid")

    print("=== PHASE 2 (rules) audit ===")
    r2 = audit(p2, ["Melody", "Bass", "Comp"])
    print(json.dumps(r2, indent=2))

    print("\n=== PHASE 1 (raw) grid character ===")
    r1 = audit(p1, ["Raw_Melody"])
    v = r1["voices"]["Raw_Melody"]
    print(f"onsets={v['n_onsets']} off_grid_16th={v['off_grid_16th']} "
          f"(raw draft -> off-grid expected)")

    # verdicts
    verdict_grid = all(r2["voices"][v]["off_grid_16th"] == 0 for v in r2["voices"])
    verdict_harm = all(r2["voices"][v]["out_of_scale"] == 0 and
                       r2["voices"][v]["out_of_chord"] == 0 for v in r2["voices"])
    summary = {
        "project": "206-ragtime-skeleton-refinement",
        "grid_audit": {v: r2["voices"][v]["off_grid_16th"] for v in r2["voices"]},
        "grid_verdict": "PASS" if verdict_grid else "FAIL",
        "harmony_audit": {
            v: {"out_of_scale": r2["voices"][v]["out_of_scale"],
                "out_of_chord": r2["voices"][v]["out_of_chord"]}
            for v in r2["voices"]},
        "harmony_verdict": "PASS" if verdict_harm else "FAIL",
        "zero_drift": r2["zero_drift"],
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nGRID VERDICT: {'PASS (0 off-grid)' if verdict_grid else 'FAIL'}")
    print(f"HARMONY VERDICT: {'PASS (0 out-of-key/chord)' if verdict_harm else 'FAIL'}")
    print(f"ZERO-DRIFT: {'PASS' if r2['zero_drift'] else 'FAIL'}")


if __name__ == "__main__":
    main()
