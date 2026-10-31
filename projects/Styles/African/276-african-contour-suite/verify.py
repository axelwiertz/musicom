# -*- coding: utf-8 -*-
"""276-african-contour-suite — read-only mido audit (zero-drift / grid / scale /
chord). Verify-don't-trust. mido used READING ONLY (analysis)."""
import os
import json

import mido  # READING ONLY (analysis)

PROJ = "/opt/data/projects/Styles/African/276-african-contour-suite"
BASE = "276-african-contour-suite"
MIDI = os.path.join(PROJ, "MIDI")

KEY_PCS = {0, 2, 4, 7, 9}
PALETTES = {"C": {0, 4, 7, 9}, "D": {2, 4, 7, 9}, "Am": {9, 0, 2, 4},
            "G": {7, 9, 0, 2}}
SECTION_PALETTES = [
    ["C", "G", "C", "C"], ["C", "Am", "C", "G"], ["Am", "G", "D", "G"],
    ["D", "G", "Am", "D"], ["Am", "D", "G", "Am"], ["G", "C", "D", "C"],
    ["C", "G", "Am", "C"], ["C", "G", "C", "C"],
]
BAR_PALETTE = [p for sec in SECTION_PALETTES for p in sec]
TOTAL_BARS = len(BAR_PALETTE)
BAR = 1920


def track_len(t):
    return sum(m.time for m in t)


def analyze(path, is_perfect):
    mid = mido.MidiFile(path)
    r = {"path": path, "size": os.path.getsize(path)}
    voice_lens = []
    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    pitched_onsets = 0
    drum_onsets = 0
    for i, t in enumerate(mid.tracks[1:], start=1):
        total = 0
        for m in t:
            total += m.time
            if m.type == "note_on" and m.velocity > 0:
                if m.channel == 9:
                    drum_onsets += 1
                    continue
                pitched_onsets += 1
                if not (total % 120 == 0 or total % 240 == 0):
                    offgrid += 1
                if m.note % 12 not in KEY_PCS:
                    scale_viol += 1
                bar = min(TOTAL_BARS - 1, total // BAR)
                if m.note % 12 not in PALETTES[BAR_PALETTE[bar]]:
                    chord_viol += 1
        voice_lens.append(total)
    r["n_tracks"] = len(mid.tracks)
    r["voice_track_lengths"] = voice_lens
    r["zero_drift"] = len(set(voice_lens)) == 1
    r["pitched_onsets"] = pitched_onsets
    r["drum_onsets"] = drum_onsets
    r["off_grid"] = offgrid
    r["scale_violations"] = scale_viol
    r["chord_violations"] = chord_viol
    return r


def main():
    out = {}
    for ver, is_perfect in (("phase1", False), ("perfect", True), ("humanized", False)):
        p = os.path.join(MIDI, f"{BASE}-{ver}.mid")
        assert os.path.getsize(p) > 40, f"empty: {p}"
        out[ver] = analyze(p, is_perfect)

    # assertions
    assert out["perfect"]["zero_drift"], "perfect zero-drift failed"
    assert out["humanized"]["zero_drift"], "humanized zero-drift failed"
    assert out["perfect"]["off_grid"] == 0, "perfect off-grid != 0"
    assert out["humanized"]["off_grid"] > 0, "humanized off-grid == 0 (jitter did not run)"
    assert out["perfect"]["scale_violations"] == 0, "perfect scale violations"
    assert out["perfect"]["chord_violations"] == 0, "perfect chord violations"

    with open(os.path.join(PROJ, "Analysis", "verify.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("VERIFY_OK")
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
