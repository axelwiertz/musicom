# Copyright (c) 2026 Axel Wiertz / Musicom
#
# Licensed under the MIT License.

"""
examples/melodica_composition.py — Programmatic composition using the Melodica adapter.

Compiles a multi-section arrangement using simulated Melodica parametric tracks,
segments them through the MelodicaToMatrixConverter, and outputs a aligned UnitMatrix.
"""

import sys
import os

# Align search path to repository root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converters.melodica_adapter import MelodicaExchangeNote, MelodicaToMatrixConverter
from structures import UnitMatrix, MusicUnit

def run_composition():
    print("[*] Initializing Melodica-to-Musicom Adapter...")
    # Set standard MIDI properties (120 BPM, standard 960 PPQ)
    converter = MelodicaToMatrixConverter(bpm=120.0, ticks_per_beat=960)

    # 1. Simulate Melodica-Generated Parametric Streams
    # Track A: Flute Melody (Arpeggiated theme, flowing across sections)
    flute_melody = [
        # Intro Section [0.0 - 4.0 beats)
        MelodicaExchangeNote(pitch=72, start_beat=0.0, duration_beats=1.0, velocity=95),
        MelodicaExchangeNote(pitch=76, start_beat=1.0, duration_beats=1.0, velocity=100),
        MelodicaExchangeNote(pitch=79, start_beat=2.0, duration_beats=1.0, velocity=105),
        MelodicaExchangeNote(pitch=84, start_beat=3.0, duration_beats=1.0, velocity=110),
        # Verse Section [4.0 - 8.0 beats)
        MelodicaExchangeNote(pitch=83, start_beat=4.0, duration_beats=2.0, velocity=100),
        MelodicaExchangeNote(pitch=81, start_beat=6.0, duration_beats=2.0, velocity=95),
    ]

    # Track B: Acoustic Bass (Steady grounding notes)
    acoustic_bass = [
        # Spans continuous 4-beat long notes matching chord roots
        MelodicaExchangeNote(pitch=48, start_beat=0.0, duration_beats=4.0, velocity=90),
        MelodicaExchangeNote(pitch=43, start_beat=4.0, duration_beats=4.0, velocity=85),
    ]

    # Pack simulated streams into a track map
    melodica_tracks = {
        "Flute": flute_melody,
        "Acoustic_Bass": acoustic_bass
    }

    # Define Section Boundaries stochastically (Intro [0.0, 4.0), Verse [4.0, 8.0))
    boundaries = [0.0, 4.0, 8.0]

    print("[*] Segmenting continuous notes and populating structural UnitMatrix...")
    # Compile the matrix cleanly
    matrix = converter.populate_matrix(melodica_tracks, boundaries)

    # 2. Inspect resulting matrix dimensions and verify cell contents
    print("\n" + "="*50)
    print(" MUSICOM MATRIX ASSEMBLY COMPLETED SUCCESSFULLY")
    print("="*50)
    print(f"Matrix Dimension (Rows x Columns): {matrix.data.shape}")
    print(f"Row 0 (Acoustic Bass) | Section 0 Event Count: {len(matrix.get_unit((0,0)).events)}")
    print(f"Row 0 (Acoustic Bass) | Section 1 Event Count: {len(matrix.get_unit((0,1)).events)}")
    print(f"Row 1 (Flute)         | Section 0 Event Count: {len(matrix.get_unit((1,0)).events)}")
    print(f"Row 1 (Flute)         | Section 1 Event Count: {len(matrix.get_unit((1,1)).events)}")
    print("="*50 + "\n")

    # Verify timing alignment
    lengths = matrix.get_all_row_lengths()
    print(f"[*] Track Ticks: {lengths}")
    print(f"[*] Timing Alignment Validated: {matrix.validate_timing()}")

if __name__ == "__main__":
    run_composition()
