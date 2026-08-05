# Copyright (c) 2026 Axel Wiertz / Musicom
#
# Licensed under the MIT License.

"""
examples/melodica_16bar_composition.py — A complete 16-bar programmatic composition.

Uses the MelodicaToMatrixConverter, writes standard MIDI tracks to disk, 
and synthesizes a realistic digital audio render (WAV) using Musicom's granular engine.
"""

import sys
import os

# Align search path to repository root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converters.melodica_adapter import MelodicaExchangeNote, MelodicaToMatrixConverter
from converters.midi_converter import export_midi
from sound.synthesis.granular import AperiodicGranulator
from structures import UnitMatrix, MusicUnit

def run_16bar_composition():
    print("[*] Initializing 16-Bar Melodica-to-Musicom Adapter...")
    
    # 16 bars at 4 beats/bar = 32 beats. Let's use 960 PPQ.
    # We will segment into 4 discrete 4-bar sections (8 bars each or 4 bars each: 4 bars * 4 beats = 16 beats per section)
    # Total timeline: 16 bars * 4 beats = 64 beats total.
    # Sections (4 bars each): Section 1 [0-16), Section 2 [16-32), Section 3 [32-48), Section 4 [48-64)
    converter = MelodicaToMatrixConverter(bpm=120.0, ticks_per_beat=960)

    # 1. Track A: Synth Lead (Arpeggiated progression, shifting across chord scales)
    # Progression: i (Cmin) -> bVI (AbMaj) -> bVII (BbMaj) -> v (Gmin)
    synth_lead = [
        # SECTION 1 (Bars 1-4, Cmin) [0.0 - 16.0 beats)
        MelodicaExchangeNote(pitch=60, start_beat=0.0, duration_beats=1.5),
        MelodicaExchangeNote(pitch=63, start_beat=1.5, duration_beats=1.5),
        MelodicaExchangeNote(pitch=67, start_beat=3.0, duration_beats=1.0),
        MelodicaExchangeNote(pitch=72, start_beat=4.0, duration_beats=4.0),
        MelodicaExchangeNote(pitch=60, start_beat=8.0, duration_beats=1.5),
        MelodicaExchangeNote(pitch=63, start_beat=9.5, duration_beats=1.5),
        MelodicaExchangeNote(pitch=67, start_beat=11.0, duration_beats=1.0),
        MelodicaExchangeNote(pitch=72, start_beat=12.0, duration_beats=4.0),

        # SECTION 2 (Bars 5-8, AbMaj) [16.0 - 32.0 beats)
        MelodicaExchangeNote(pitch=56, start_beat=16.0, duration_beats=1.5),
        MelodicaExchangeNote(pitch=60, start_beat=17.5, duration_beats=1.5),
        MelodicaExchangeNote(pitch=63, start_beat=19.0, duration_beats=1.0),
        MelodicaExchangeNote(pitch=68, start_beat=20.0, duration_beats=4.0),
        MelodicaExchangeNote(pitch=56, start_beat=24.0, duration_beats=1.5),
        MelodicaExchangeNote(pitch=60, start_beat=25.5, duration_beats=1.5),
        MelodicaExchangeNote(pitch=63, start_beat=27.0, duration_beats=1.0),
        MelodicaExchangeNote(pitch=68, start_beat=28.0, duration_beats=4.0),

        # SECTION 3 (Bars 9-12, BbMaj) [32.0 - 48.0 beats)
        MelodicaExchangeNote(pitch=58, start_beat=32.0, duration_beats=1.5),
        MelodicaExchangeNote(pitch=62, start_beat=33.5, duration_beats=1.5),
        MelodicaExchangeNote(pitch=65, start_beat=35.0, duration_beats=1.0),
        MelodicaExchangeNote(pitch=70, start_beat=36.0, duration_beats=4.0),
        MelodicaExchangeNote(pitch=58, start_beat=40.0, duration_beats=1.5),
        MelodicaExchangeNote(pitch=62, start_beat=41.5, duration_beats=1.5),
        MelodicaExchangeNote(pitch=65, start_beat=43.0, duration_beats=1.0),
        MelodicaExchangeNote(pitch=70, start_beat=44.0, duration_beats=4.0),

        # SECTION 4 (Bars 13-16, Gmin) [48.0 - 64.0 beats)
        MelodicaExchangeNote(pitch=55, start_beat=48.0, duration_beats=1.5),
        MelodicaExchangeNote(pitch=58, start_beat=49.5, duration_beats=1.5),
        MelodicaExchangeNote(pitch=62, start_beat=51.0, duration_beats=1.0),
        MelodicaExchangeNote(pitch=67, start_beat=52.0, duration_beats=4.0),
        MelodicaExchangeNote(pitch=55, start_beat=56.0, duration_beats=1.5),
        MelodicaExchangeNote(pitch=58, start_beat=57.5, duration_beats=1.5),
        MelodicaExchangeNote(pitch=62, start_beat=59.0, duration_beats=1.0),
        MelodicaExchangeNote(pitch=67, start_beat=60.0, duration_beats=4.0),
    ]

    # Track B: Deep Bass (Clean rooting notes matching chord anchors)
    deep_bass = [
        MelodicaExchangeNote(pitch=36, start_beat=0.0, duration_beats=16.0),
        MelodicaExchangeNote(pitch=32, start_beat=16.0, duration_beats=16.0),
        MelodicaExchangeNote(pitch=34, start_beat=32.0, duration_beats=16.0),
        MelodicaExchangeNote(pitch=31, start_beat=48.0, duration_beats=16.0),
    ]

    # Organize tracks into map
    melodica_tracks = {
        "Deep_Bass": deep_bass,
        "Synth_Lead": synth_lead
    }

    # Boundaries definitions in beats: 4 bars * 4 beats = 16 beats spacing
    boundaries = [0.0, 16.0, 32.0, 48.0, 64.0]

    print("[*] Rendering tracks to symmetric UnitMatrix...")
    matrix = converter.populate_matrix(melodica_tracks, boundaries)

    # Output paths
    midi_path = os.path.join("/opt/data", "melodica_16bar_output.mid")
    wav_path = os.path.join("/opt/data", "melodica_16bar_output.wav")

    # 2. Export aligned MIDI representation
    print(f"[*] Exporting aligned symbolic representation to MIDI: {midi_path}")
    export_midi(matrix, midi_path)

    # 3. Export Audio (Synthesizing with Granulator)
    print(f"[*] Compiling audio representation via Aperiodic Granular synthesis: {wav_path}")
    # Generate source carrier noise/signal and process
    temp_src = os.path.join("/opt/data", "temp_source.wav")
    
    # Create simple synth signal WAV
    import numpy as np
    import scipy.io.wavfile as wav_lib
    sample_rate = 44100
    t = np.linspace(0, 5.0, int(5.0 * sample_rate), endpoint=False)
    # Sine wave mixture (chord notes C-E-G)
    carrier = np.sin(2 * np.pi * 261.63 * t) + np.sin(2 * np.pi * 329.63 * t) + np.sin(2 * np.pi * 392.00 * t)
    carrier = carrier / np.max(np.abs(carrier)) * 0.5
    wav_lib.write(temp_src, sample_rate, (carrier * 32767).astype(np.int16))

    # Compile the granular cloud to physical audio output
    granulator = AperiodicGranulator(sample_rate=sample_rate)
    granulator.generate_cloud(
        source_path=temp_src,
        output_path=wav_path,
        duration_sec=32.0, # 32 seconds matching 16 bars at 120 BPM
        grain_size_ms=80.0,
        density_grains_per_sec=150,
        pitch_shift_semi=-2.0
    )

    # Cleanup temp src
    if os.path.exists(temp_src):
        os.remove(temp_src)

    print("\n" + "="*50)
    print(" RENDER SUCCESSFUL")
    print("="*50)
    print(f"MIDI Path: {midi_path}")
    print(f"WAV Path:  {wav_path}")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_16bar_composition()
