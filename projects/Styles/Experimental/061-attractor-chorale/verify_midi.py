#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only MIDI structure verification for 061-attractor-chorale.

Uses mido ONLY for reading/analyzing the exported MIDI (allowed by
preflight: analysis context + musicom imports present).
"""
import os
import sys
import json

import mido
from structures import MusicUnit, MusicEvent, UnitMatrix
from workflows.unitmatrix_composer import UnitMatrixComposer
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree
from utilities.constants import SCALE_PATTERNS

MIDI_PATH = "/opt/data/projects/Styles/Experimental/061-attractor-chorale/MIDI/061-attractor-chorale.mid"

BAR_TICKS = 1920
TOTAL_EXPECTED = 8 * BAR_TICKS  # 15360

# Key: E dorian
KEY_ROOT = 52
SCALE = SCALE_PATTERNS['dorian']
CHORD_DEGREES = [1, 2, 4, 6, 1, 2, 4, 1]
ROMAN = ["i", "ii", "IV", "VI", "i", "ii", "IV", "i"]
VOICES = ["Soprano", "Alto", "Tenor", "Bass"]
RANGES = {"Soprano": (62, 84), "Alto": (53, 74), "Tenor": (48, 65), "Bass": (38, 55)}


def degree_to_midi(degree, base=KEY_ROOT):
    return Scale7ChordDegree.get_diatonic_note(base, SCALE, degree - 1)


def chord_tones(deg, register_center):
    """Triad tones (root/third/fifth) folded near a register center."""
    ct = [(deg - 1 + q) % 7 + 1 for q in (0, 2, 4)]
    tones = []
    for c in ct:
        p = degree_to_midi(c)
        while p > register_center + 6:
            p -= 12
        while p <= register_center - 6:
            p += 12
        tones.append(p)
    return tones


def main():
    print("=" * 68)
    print("VERIFICATION: 061-attractor-chorale (read-only mido analysis)")
    print("=" * 68)
    mid = mido.MidiFile("/opt/data/projects/Styles/Experimental/061-attractor-chorale/MIDI/061-attractor-chorale.mid")  # READING ONLY
    print(f"Ticks per beat : {mid.ticks_per_beat}")
    print(f"Tracks         : {len(mid.tracks)} (1 tempo + 4 voices)")
    print(f"File size      : {os.path.getsize(MIDI_PATH)} bytes")

    # ---- track end ticks (zero-drift check)
    ends = []
    for ti, track in enumerate(mid.tracks):
        acc = 0
        for msg in track:
            acc += msg.time
        ends.append(acc)
    print(f"Track end ticks: {ends}")
    voice_ends = ends[1:]
    drift_ok = len(set(voice_ends)) == 1 and voice_ends[0] == TOTAL_EXPECTED
    print(f"Zero-drift     : {'PASS' if drift_ok else 'FAIL'} "
          f"(all 4 voice tracks end at {TOTAL_EXPECTED} ticks = 8.0 bars)")
    if not drift_ok:
        sys.exit(1)

    # ---- per-bar chords from note events (pitch >= 1, velocity > 0)
    print()
    print("Per-bar chords (S/A/T/B) and harmonic membership:")
    bars = []
    violations = 0
    for bar in range(8):
        chord = []
        for vi in range(4):
            track = mid.tracks[vi + 1]
            acc = 0
            notes = []
            for msg in track:
                acc += msg.time
                if msg.type == 'note_on' and msg.velocity > 0 and msg.note > 0:
                    notes.append((acc, msg.note))
            bar_notes = [n for (t, n) in notes if bar * BAR_TICKS <= t < (bar + 1) * BAR_TICKS]
            # most frequent pitch in the bar = the bar's homophonic tone
            if bar_notes:
                chord.append(max(set(bar_notes), key=bar_notes.count))
            else:
                chord.append(None)
        bars.append(chord)
        deg = CHORD_DEGREES[bar]
        roman = ROMAN[bar]
        # membership check: each voice pitch must be a chord tone of the section
        centers = [(62 + 84) // 2, (53 + 74) // 2, (48 + 65) // 2, (38 + 55) // 2]
        tones = [chord_tones(deg, centers[vi]) for vi in range(4)]
        mem = []
        for vi in range(4):
            ok_m = chord[vi] in tones[vi]
            mem.append("Y" if ok_m else "N")
            if not ok_m:
                violations += 1
        print(f"  Bar {bar+1} {roman:>3}: {chord}  chord-tone: {' '.join(mem)}")
    print(f"Chord-tone membership violations: {violations}")

    # ---- voice leading: parallel fifths/octaves across bar transitions
    print()
    vlr = VoiceLeadingRules(style='classical')
    pv = 0
    for bar in range(1, 8):
        viols = vlr.check_parallel_motion(bars[bar - 1], bars[bar])
        pv += len(viols)
        if viols:
            print(f"  Bar {bar}->{bar+1}: {viols}")
    print(f"Parallel fifth/octave violations: {pv}")

    # ---- voice ranges
    rv = 0
    for bar in range(8):
        for vi, vname in enumerate(VOICES):
            r = vlr.validate_voice_ranges([bars[bar][vi]], {vname: RANGES[vname]})
            rv += len(r)
    print(f"Range violations: {rv}")

    # ---- voice crossing (S > A > T > B strict descending)
    cr = 0
    for bar in range(8):
        c = bars[bar]
        for i in range(3):
            if c[i] <= c[i + 1]:
                cr += 1
                print(f"  Crossing bar {bar+1} voices {i}: {c}")
    print(f"Voice crossings: {cr}")

    # ---- articulation / rhythm density summary
    print()
    for vi, vname in enumerate(VOICES):
        track = mid.tracks[vi + 1]
        acc = 0
        onsets = 0
        for msg in track:
            acc += msg.time
            if msg.type == 'note_on' and msg.velocity > 0 and msg.note > 0:
                onsets += 1
        print(f"  {vname:<10}: {onsets} sounding onsets")

    print()
    print("=" * 68)
    if drift_ok and violations == 0 and pv == 0 and rv == 0 and cr == 0:
        print("VERIFICATION: ALL PASS")
    else:
        print("VERIFICATION: ISSUES FOUND (see above)")
        sys.exit(1)


if __name__ == "__main__":
    main()
