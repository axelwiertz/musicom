# -*- coding: utf-8 -*-
"""249 verify — mido READ-ONLY readback of the three MIDIs.

Checks: zero-drift (equal track lengths), grid audit per voice (perfect must
be 0 off-grid, humanized must be >0), harmony audit (out-of-scale / out-of-
chord per pitched voice). Prints real numbers; writes Analysis/readback.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402
import mido  # noqa: E402

MIDI_DIR = os.path.join(C.PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(C.PROJECT_DIR, "Analysis")


def read_tracks(path):
    mid = mido.MidiFile(path)
    tracks = []
    for tr in mid.tracks:
        ch = None
        for m in tr:
            if m.type == "program_change":
                ch = m.channel
        t = 0
        onsets = []
        notes = []   # (note, start_tick, end_tick)
        active = {}
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0 and m.note > 0:
                onsets.append(t)
                active[m.note] = t
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                st = active.pop(m.note, None)
                if st is not None:
                    notes.append((m.note, st, t))
        if ch is not None and (onsets or notes):
            tracks.append({"channel": ch, "onsets": onsets, "notes": notes,
                           "length": t})
    return tracks


def audit(tracks, pitched_channels=(0, 1, 2)):
    res = []
    for tr in tracks:
        ch = tr["channel"]
        pitched = ch in pitched_channels
        off_grid = sum(1 for o in tr["onsets"] if (o % 120 != 0 and o % 240 != 0))
        out_scale = 0
        out_chord = 0
        n_pitched = 0
        if pitched:
            for note, st, et in tr["notes"]:
                n_pitched += 1
                pc = note % 12
                bar = min(C.TOTAL_BARS - 1, st // C.BAR)
                cpc = set(C.CHORD_TONES[bar])
                if pc not in C.KEY_PCS:
                    out_scale += 1
                if pc not in cpc:
                    out_chord += 1
        res.append({"channel": ch, "n_onsets": len(tr["onsets"]),
                    "n_pitched": n_pitched, "off_grid": off_grid,
                    "out_scale": out_scale, "out_chord": out_chord,
                    "track_length": tr["length"]})
    return res


def main():
    report = {}
    for label, path in [("phase1", C.PHASE1_PATH),
                        ("perfect", C.PERFECT_PATH),
                        ("humanized", C.HUMANIZED_PATH)]:
        size = os.path.getsize(path)
        tracks = read_tracks(path)
        lengths = [tr["length"] for tr in tracks]
        zero_drift = len(set(lengths)) <= 1
        aud = audit(tracks)
        report[label] = {"size": size, "n_tracks": len(tracks),
                         "track_lengths": lengths, "zero_drift": zero_drift,
                         "audit": aud}
        print(f"[{label}] size={size} tracks={len(tracks)} zero_drift={zero_drift}")
        for a in aud:
            print(f"    ch{a['channel']}: onsets={a['n_onsets']} "
                  f"pitched={a['n_pitched']} off_grid={a['off_grid']} "
                  f"out_scale={a['out_scale']} out_chord={a['out_chord']}")

    # global verdicts
    p_off = sum(a["off_grid"] for a in report["perfect"]["audit"])
    h_off = sum(a["off_grid"] for a in report["humanized"]["audit"])
    p_scale = sum(a["out_scale"] for a in report["perfect"]["audit"])
    p_chord = sum(a["out_chord"] for a in report["perfect"]["audit"])
    h_scale = sum(a["out_scale"] for a in report["humanized"]["audit"])
    h_chord = sum(a["out_chord"] for a in report["humanized"]["audit"])
    print(f"\nVERDICT: perfect off_grid={p_off} (want 0), "
          f"humanized off_grid={h_off} (want >0)")
    print(f"VERDICT: perfect out_scale={p_scale} out_chord={p_chord} (want 0)")
    print(f"VERDICT: humanized out_scale={h_scale} out_chord={h_chord} (want 0)")

    with open(os.path.join(ANALYSIS_DIR, "readback.json"), "w") as f:
        json.dump(report, f, indent=2)
    print("wrote Analysis/readback.json")


if __name__ == "__main__":
    main()
