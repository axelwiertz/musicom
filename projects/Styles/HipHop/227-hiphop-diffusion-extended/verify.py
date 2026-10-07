# -*- coding: utf-8 -*-
# READING ONLY (analysis) — mido used for reading/verification, never authoring.
import mido, os, json

P = "/opt/data/repos/musicom/projects/Styles/HipHop/227-hiphop-diffusion-extended"
MIDI_DIR = os.path.join(P, "MIDI")

BAR_TICKS = 1920
GRID16 = 120
GRID8 = 240
A_MINOR_PCS = {9, 11, 0, 2, 4, 5, 7}

SECTION_CHORDS = {
    0: ["Am", "Am", "Am", "Am"],
    1: ["Am", "F",  "C",  "G"],
    2: ["Am", "F",  "C",  "G"],
    3: ["Dm", "Am", "Em", "Am"],
    4: ["Am", "F",  "C",  "G"],
    5: ["F",  "C",  "G",  "Am"],
    6: ["Am", "F",  "C",  "G"],
    7: ["C",  "G",  "Am", "F"],
    8: ["Am", "F",  "C",  "G"],
    9: ["Am", "Am", "Am", "Am"],
}
CHORD_PCS = {
    "Am": {9, 0, 4}, "F": {5, 9, 0}, "C": {0, 4, 7},
    "G": {7, 11, 2}, "Dm": {2, 5, 9}, "Em": {4, 7, 11},
}

def chord_for_tick(t):
    bar = t // BAR_TICKS
    sec = bar // 4
    bin_sec = bar % 4
    return SECTION_CHORDS[sec][bin_sec], sec, bar

def audit_midi(path, label):
    mid = mido.MidiFile(path)
    print(f"\n=== {label}: {os.path.basename(path)} ({os.path.getsize(path)} B) ===")
    assert os.path.getsize(path) > 40, "empty/corrupt"

    lengths = []
    chans = {}
    for i, t in enumerate(mid.tracks):
        tot = sum(m.time for m in t)
        lengths.append(tot)
        for m in t:
            if m.type in ("program_change", "note_on", "note_off"):
                chans.setdefault(i, m.channel)
    voice_lengths = lengths[1:]
    zd = len(set(voice_lengths)) == 1
    print(f"tracks={len(mid.tracks)} (incl conductor), voice track lengths={set(voice_lengths)}, zero_drift={zd}")
    assert zd, "ZERO-DRIFT FAIL"

    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    total_pitched = 0
    pitched_tracks = 0
    for i, t in enumerate(mid.tracks):
        if i == 0:
            continue
        ch = chans.get(i)
        if ch == 9:
            continue
        pitched_tracks += 1
        abs_tick = 0
        for m in t:
            abs_tick += m.time
            if m.type == "note_on" and m.velocity > 0:
                total_pitched += 1
                on = abs_tick
                pc = m.note % 12
                if on % GRID16 != 0 and on % GRID8 != 0:
                    offgrid += 1
                if pc not in A_MINOR_PCS:
                    scale_viol += 1
                chord, sec, bar = chord_for_tick(on)
                if pc not in CHORD_PCS[chord]:
                    chord_viol += 1

    print(f"pitched_tracks={pitched_tracks}, pitched_onsets={total_pitched}")
    print(f"OFF_GRID={offgrid}  SCALE_VIOL={scale_viol}  CHORD_VIOL={chord_viol}")
    return dict(tracks=len(mid.tracks), zero_drift=zd, offgrid=offgrid,
                scale_viol=scale_viol, chord_viol=chord_viol,
                pitched=total_pitched, track_len=voice_lengths[0] if voice_lengths else None)

res = {}
res["phase1"] = audit_midi(os.path.join(MIDI_DIR, "227-hiphop-diffusion-extended-phase1.mid"), "PHASE 1")
res["phase2"] = audit_midi(os.path.join(MIDI_DIR, "227-hiphop-diffusion-extended.mid"), "PHASE 2")

print("\n=== SUMMARY ===")
print(json.dumps(res, indent=1))

# asserts
p2 = res["phase2"]
assert p2["zero_drift"], "phase2 zero drift failed"
assert p2["offgrid"] == 0, "phase2 off-grid != 0"
assert p2["scale_viol"] == 0, "phase2 scale violations != 0"
assert p2["chord_viol"] == 0, "phase2 chord violations != 0"
assert p2["pitched"] > 300, "phase2 suspiciously few pitched onsets"
print("\nALL PHASE-2 CHECKS PASSED")
