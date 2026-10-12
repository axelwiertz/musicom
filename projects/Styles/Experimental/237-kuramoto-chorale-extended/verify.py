# -*- coding: utf-8 -*-
"""Read-only mido verification of 237-kuramoto-chorale-extended MIDI.

Reports exact counts required by the rework quality gate.
mido used ONLY for reading/analysis (never authoring).
"""
import os
import mido

from rules.progression import Scale7ChordDegree

BASE = "/opt/data/projects/Styles/Experimental/237-kuramoto-chorale-extended"
PHASE2 = os.path.join(BASE, "MIDI", "237-kuramoto-chorale-extended.mid")
PHASE1 = os.path.join(BASE, "MIDI", "237-kuramoto-chorale-extended-phase1.mid")

KEY_ROOT_PC = 5
SCALE_INTERVALS = [0, 2, 3, 5, 7, 9, 10]
KEY_PCS = sorted(set((KEY_ROOT_PC + iv) % 12 for iv in SCALE_INTERVALS))
KEY_ROOT_MIDI = 53

# Per-bar chord degrees (must match compose.py exactly).
SECTION_DEGREES = [
    [0, 0], [0, 3], [3, 6], [6, 3, 0], [0, 2], [4, 6], [3, 6, 0], [0, 0],
]
BAR_DEGREES = []
for d in SECTION_DEGREES:
    BAR_DEGREES.extend(d)
BAR = 1920


def chord_pcs(degree):
    r = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree)
    t = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 2)
    f = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 4)
    return {r % 12, t % 12, f % 12}


def verify(path, check_chord=True):
    print(f"=== {os.path.basename(path)} ===")
    print(f"size = {os.path.getsize(path)} bytes (assert > 40: "
          f"{os.path.getsize(path) > 40})")
    mid = mido.MidiFile(path)
    lengths = [sum(m.time for m in tr) for tr in mid.tracks]
    voice_lens = lengths[1:]
    zd = len(set(voice_lens)) == 1
    print(f"voice tracks = {len(voice_lens)}, zero-drift = {zd}, len = {set(voice_lens)}")

    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    n_pitched = 0
    for tr in mid.tracks[1:]:
        t = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                if m.channel == 9:
                    continue
                n_pitched += 1
                if not (t % 120 == 0 or t % 240 == 0):
                    offgrid += 1
                if (m.note % 12) not in KEY_PCS:
                    scale_viol += 1
                if check_chord:
                    bar = t // BAR
                    if bar < len(BAR_DEGREES):
                        if (m.note % 12) not in chord_pcs(BAR_DEGREES[bar]):
                            chord_viol += 1
    print(f"pitched onsets (excl ch9) = {n_pitched}")
    print(f"off-grid count = {offgrid}  (MUST be 0)")
    print(f"scale violations = {scale_viol}  (MUST be 0)")
    if check_chord:
        print(f"chord violations = {chord_viol}  (MUST be 0)")
    return zd, offgrid, scale_viol, chord_viol, n_pitched, len(voice_lens)


print("KEY pcs:", KEY_PCS)
r2 = verify(PHASE2, check_chord=True)
print()
r1 = verify(PHASE1, check_chord=False)
