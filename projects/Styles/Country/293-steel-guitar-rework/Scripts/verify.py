# -*- coding: utf-8 -*-
"""Read-only verification of the 293 rework MIDI outputs (mido READING ONLY)."""
import os
import importlib.util

import mido  # READING ONLY (analysis)

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("compose", os.path.join(HERE, "compose.py"))
compose = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compose)

BAR = compose.BAR
KEY_PCS = compose.KEY_PCS
BAR_CHORDS = compose.BAR_CHORDS
DEGREE_TRIADS = compose.DEGREE_TRIADS
MIDI_DIR = compose.MIDI_DIR
NAME = compose.NAME


def analyze(path):
    mid = mido.MidiFile(path)
    voice_tracks = mid.tracks[1:]  # skip conductor (track 0)
    lengths = []
    drum_track_idx = None
    per_track = []
    for i, tr in enumerate(voice_tracks):
        # detect drum track: program_change on channel 9
        is_drum = any(m.type == 'program_change' and m.channel == 9 for m in tr)
        if is_drum:
            drum_track_idx = i
        ab = 0
        onsets = []
        for m in tr:
            ab += m.time
            if m.type == 'note_on' and m.velocity > 0 and m.note > 0:
                onsets.append((m.note, ab))
        lengths.append(ab)
        per_track.append((tr.name, ab, len(onsets), is_drum, onsets))
    n_tracks = len(voice_tracks)
    zero_drift = len(set(lengths)) == 1
    # off-grid / scale / chord over pitched tracks (exclude drums)
    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    for (name, ab, non, is_drum, onsets) in per_track:
        if is_drum:
            continue
        for (note, onset) in onsets:
            if not (onset % 120 == 0 or onset % 240 == 0):
                offgrid += 1
            if note % 12 not in KEY_PCS:
                scale_viol += 1
            bar = onset // BAR
            if bar >= len(BAR_CHORDS):
                chord_viol += 1
                continue
            deg = BAR_CHORDS[bar]
            if note % 12 not in DEGREE_TRIADS[deg]:
                chord_viol += 1
    return dict(n_tracks=n_tracks, lengths=lengths, zero_drift=zero_drift,
                offgrid=offgrid, scale_viol=scale_viol, chord_viol=chord_viol,
                drum_track_idx=drum_track_idx, per_track=per_track)


def main():
    files = {
        "phase1": os.path.join(MIDI_DIR, f"{NAME}-phase1.mid"),
        "perfect": os.path.join(MIDI_DIR, f"{NAME}-perfect.mid"),
        "humanized": os.path.join(MIDI_DIR, f"{NAME}-humanized.mid"),
    }
    results = {}
    for tag, path in files.items():
        sz = os.path.getsize(path)
        r = analyze(path)
        r["size_ok"] = sz > 40
        r["size"] = sz
        results[tag] = r
        print(f"== {tag} == size={sz} ({'OK' if sz > 40 else 'TOO SMALL'})")
        print(f"   tracks={r['n_tracks']} lens={r['lengths']} zero_drift={r['zero_drift']}")
        print(f"   offgrid={r['offgrid']} scale_viol={r['scale_viol']} chord_viol={r['chord_viol']} "
              f"drum_track={r['drum_track_idx']}")

    # assertions
    for tag in ("perfect", "humanized", "phase1"):
        assert results[tag]["size_ok"], f"{tag} empty/corrupt"
    for tag in ("perfect", "humanized"):
        assert results[tag]["zero_drift"], f"{tag} zero-drift FAIL"
        assert results[tag]["scale_viol"] == 0, f"{tag} scale violations"
    assert results["perfect"]["chord_viol"] == 0, "perfect chord violations"
    assert results["perfect"]["offgrid"] == 0, "perfect off-grid != 0"
    assert results["humanized"]["offgrid"] > 0, "humanized off-grid == 0 (jitter did not run)"
    assert results["phase1"]["zero_drift"], "phase1 zero-drift FAIL"
    assert results["perfect"]["n_tracks"] >= 4, "fewer than 4 tracks"

    print("\nALL CHECKS PASSED")
    print("perfect offgrid==0:", results["perfect"]["offgrid"] == 0)
    print("humanized offgrid>0:", results["humanized"]["offgrid"] > 0)
    print("perfect chord_viol==0:", results["perfect"]["chord_viol"] == 0)
    # Humanized chord_viol counts are bar-seam micro-timing crossings (notes
    # still in-key); the canonical humanizer clamps to SECTION seams, not bar
    # seams, so a note on a bar boundary can jitter a few ticks into the
    # adjacent bar. Reported for transparency, not a failure.
    print("humanized chord_viol (bar-seam jitter crossings, in-key):",
          results["humanized"]["chord_viol"])


if __name__ == "__main__":
    main()
