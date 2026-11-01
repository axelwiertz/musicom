# -*- coding: utf-8 -*-
"""verify.py - READ-ONLY mido audit of the 278-funk-contour-groove-suite MIDIs.

Reports zero-drift, off-grid counts, scale violations, chord violations.
mido used ONLY for reading/analysis (not authoring).
"""
import json
import os
import mido  # READING ONLY (analysis)

PROJ = "/opt/data/projects/Styles/Funk/278-funk-contour-groove-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")

KEY_PCS = {4, 7, 9, 11, 2}   # E minor pentatonic

PALETTES = {
    "Em": {4, 7, 11, 2},
    "G": {7, 9, 11, 2},
    "A": {9, 4, 11, 2},
    "D": {2, 7, 9, 4},
}
SECTION_PALETTES = [
    ["Em", "Em", "G", "Em"],
    ["Em", "A", "Em", "G"],
    ["A", "G", "D", "G"],
    ["D", "G", "A", "D"],
    ["G", "Em", "D", "Em"],
    ["D", "A", "G", "D"],
    ["A", "D", "G", "D"],
    ["Em", "G", "Em", "Em"],
]
BARS_PER_SECTION = 4
BAR = 1920


def palette_for_tick(t):
    gbar = t // BAR
    sec = gbar // BARS_PER_SECTION
    binsec = gbar % BARS_PER_SECTION
    return PALETTES[SECTION_PALETTES[sec][binsec]]


def audit(path, tag):
    mid = mido.MidiFile(path)
    lengths = []
    tracks_info = []
    total_off_grid = 0
    total_scale_viol = 0
    total_chord_viol = 0
    pitched_onsets = 0
    for i, t in enumerate(mid.tracks):
        ticks = sum(m.time for m in t)
        lengths.append(ticks)
        if i == 0:
            continue  # conductor
        abs_t = 0
        chans = set()
        off_grid = scale_viol = chord_viol = 0
        n_on = 0
        for m in t:
            abs_t += m.time
            if m.type == "note_on" and m.velocity > 0:
                ch = getattr(m, "channel", None)
                chans.add(ch)
                n_on += 1
                if ch == 9:
                    continue  # drums
                pitched_onsets += 1
                if abs_t % 120 != 0:
                    off_grid += 1
                pc = m.note % 12
                if pc not in KEY_PCS:
                    scale_viol += 1
                if pc not in palette_for_tick(abs_t):
                    chord_viol += 1
        total_off_grid += off_grid
        total_scale_viol += scale_viol
        total_chord_viol += chord_viol
        tracks_info.append({"track": i, "channels": sorted(chans),
                            "n_onset": n_on, "off_grid": off_grid,
                            "scale_viol": scale_viol,
                            "chord_viol": chord_viol})
    voice_lengths = lengths[1:]
    res = {
        "path": path, "tag": tag,
        "n_voice_tracks": len(voice_lengths),
        "track_lengths_ticks": voice_lengths,
        "zero_drift": len(set(voice_lengths)) == 1,
        "pitched_onsets": pitched_onsets,
        "off_grid": total_off_grid,
        "scale_violations": total_scale_viol,
        "chord_violations": total_chord_viol,
        "tracks": tracks_info,
    }
    return res


if __name__ == "__main__":
    out = {}
    for tag, fn in [("phase1", "278-funk-contour-groove-suite-phase1.mid"),
                    ("perfect", "278-funk-contour-groove-suite-perfect.mid"),
                    ("humanized", "278-funk-contour-groove-suite-humanized.mid")]:
        p = os.path.join(MIDI_DIR, fn)
        assert os.path.getsize(p) > 40, f"empty/corrupt {fn}"
        r = audit(p, tag)
        out[tag] = r
        print(f"\n=== {tag} ===")
        print(f"  voice tracks: {r['n_voice_tracks']}, lengths={r['track_lengths_ticks']}")
        print(f"  zero_drift={r['zero_drift']}")
        print(f"  pitched_onsets={r['pitched_onsets']} off_grid={r['off_grid']} "
              f"scale_viol={r['scale_violations']} chord_viol={r['chord_violations']}")
    with open(os.path.join(PROJ, "Analysis", "verify.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nverify.json written")