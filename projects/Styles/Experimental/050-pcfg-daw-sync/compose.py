# -*- coding: utf-8 -*-
"""Composition entry point — musicom engine only.
Generates an 8-bar piece using Probabilistic Context-Free Grammar Recursion (Method 034)
and exports it for DAW synchronization (Method SP-005) including MIDI, MusicXML, and separate stems.
"""
import os
import wave
import sys
import numpy as np
import music21

# Ensure clean imports from the installed musicom package
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# ---------------------------------------------------------------- CONFIG -----
PROJECT_ID = "050"
PROJECT_NAME = f"{PROJECT_ID}-pcfg-daw-sync"
PROJECT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"

BPM = 100
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920 ticks
NUM_SECTIONS = 8                            # 8 bars total

# SoundFont configuration
SOUNDFONT_PATH = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH_BIN = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# Absolute Pitch Map representing D Dorian scale degrees
# Index 0 to 11
PITCH_MAP = [62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81]  # D4, E4, F4, G4, A4, B4, C5, D5, E5, F5, G5, A5

# Chords corresponding to the 8 sections (each lasts 1 bar)
CHORDS = [
    [50, 53, 57, 60],  # Dm7 (Bar 1)
    [43, 59, 62, 65],  # G7 (Bar 2)
    [48, 52, 55, 59],  # Cmaj7 (Bar 3)
    [45, 48, 52, 55],  # Am7 (Bar 4)
    [50, 53, 57, 60],  # Dm7 (Bar 5)
    [43, 59, 62, 65],  # G7 (Bar 6)
    [40, 55, 59, 62],  # Em7 (Bar 7)
    [50, 53, 57, 62]   # Dm Picardy-style resolution (Bar 8)
]

BASS_ROOTS = [50, 43, 48, 45, 50, 43, 40, 50]  # D3, G2, C3, A2, D3, G2, E2, D3

# ------------------------------------------------------------- PCFG GRAMMAR --
# Definitive grammar that ensures each bar expands to exactly 16 sixteenth notes
PCFG_RULES = {
    'S': [(['Bar_A', 'Bar_B', 'Bar_A', 'Bar_C', 'Bar_B', 'Bar_A', 'Bar_C', 'Bar_D'], 1.0)],
    'Bar_A': [(['Phrase_1', 'Phrase_1'], 0.7), (['Phrase_1', 'Phrase_2'], 0.3)],
    'Bar_B': [(['Phrase_2', 'Phrase_2'], 0.6), (['Phrase_2', 'Phrase_3'], 0.4)],
    'Bar_C': [(['Phrase_1', 'Phrase_3'], 0.8), (['Phrase_3', 'Phrase_3'], 0.2)],
    'Bar_D': [(['Phrase_3', 'Phrase_4'], 1.0)],
    
    'Phrase_1': [(['Motif_A', 'Motif_B'], 0.7), (['Motif_A', 'Motif_A'], 0.3)],
    'Phrase_2': [(['Motif_B', 'Motif_C'], 0.7), (['Motif_C', 'Motif_A'], 0.3)],
    'Phrase_3': [(['Motif_D', 'Motif_B'], 0.8), (['Motif_D', 'Motif_D'], 0.2)],
    'Phrase_4': [(['Motif_E', 'Motif_F'], 1.0)],
    
    'Motif_A': [(['n0', 'n2', 'n3', 'n4'], 0.5), (['n0', 'n3', 'n2', 'n3'], 0.5)],
    'Motif_B': [(['n4', 'n5', 'n6', 'n7'], 0.6), (['n4', 'n3', 'n4', 'r'], 0.4)],
    'Motif_C': [(['n7', 'n6', 'n5', 'n4'], 0.7), (['n7', 'n4', 'n5', 'r'], 0.3)],
    'Motif_D': [(['n3', 'n2', 'n1', 'n0'], 0.5), (['n2', 'n0', 'n2', 'r'], 0.5)],
    'Motif_E': [(['n0', 'n4', 'n7', 'n9'], 0.5), (['n0', 'n2', 'n4', 'n7'], 0.5)],
    'Motif_F': [(['n10', 'n7', 'n4', 'r'], 1.0)]
}

def expand_symbol(symbol, rules, rng):
    """Recursively expands a symbol according to the PCFG rules."""
    if symbol not in rules:
        return [symbol]
    productions = rules[symbol]
    patterns = [p[0] for p in productions]
    probs = [p[1] for p in productions]
    probs = np.array(probs, dtype=float)
    probs /= probs.sum()
    chosen_pattern = rng.choice(patterns, p=probs)
    expanded = []
    for sym in chosen_pattern:
        expanded.extend(expand_symbol(sym, rules, rng))
    return expanded

def generate_pcfg_melody():
    """Generates an 8-bar PCFG terminal history."""
    # Seed RNG for deterministic reproducibility
    rng = np.random.default_rng(50)
    
    # We expand S, which will resolve to 8 bars of 16 sixteenths each = 128 notes
    terminals = expand_symbol('S', PCFG_RULES, rng)
    return terminals

# ------------------------------------------------------------- COMPOSER MATRIX --
def build_music_matrix(terminals, single_voice_filter=None) -> UnitMatrixComposer:
    """Configures UnitMatrixComposer with PCFG-derived melody and chordal harmony."""
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    section_names = [f"Bar{i}" for i in range(1, NUM_SECTIONS + 1)]
    
    # Decide which voices to add based on filter
    active_voices = ["Lead", "Pad", "Bass"]
    if single_voice_filter:
        active_voices = [single_voice_filter]
        
    c.create_matrix(num_voices=len(active_voices), num_sections=NUM_SECTIONS)
    
    # Mapping voices to programs and channels
    voice_configs = {
        "Lead": {"program": 73, "channel": 0},  # Flute
        "Pad": {"program": 89, "channel": 1},   # Synth Pad
        "Bass": {"program": 32, "channel": 2}   # Acoustic Bass
    }
    
    for v_name in active_voices:
        cfg = voice_configs[v_name]
        c.add_voice(v_name, program=cfg["program"], channel=cfg["channel"])
        
    for name in section_names:
        c.add_section(name, bars=1)
        
    for s in range(NUM_SECTIONS):
        sec_name = section_names[s]
        
        # 1. Lead voice: sixteenth step notes (total 16 steps per bar)
        if "Lead" in active_voices:
            lead_events = []
            accum_ticks = 0
            step_ticks = 120  # sixteenth note = 120 ticks
            
            # Get 16 steps corresponding to this bar
            bar_terminals = terminals[s * 16 : (s + 1) * 16]
            for term in bar_terminals:
                if term.startswith('n'):
                    offset = int(term[1:])
                    pitch = PITCH_MAP[offset % len(PITCH_MAP)] + (offset // len(PITCH_MAP)) * 12
                    volume = 90
                    lead_events.append(MusicEvent(
                        pitch=pitch,
                        volume=volume,
                        start_tick=accum_ticks,
                        end_tick=accum_ticks + 100  # slightly staccato/legato articulation
                    ))
                accum_ticks += step_ticks
                
            # Zero-drift validation / padding
            if accum_ticks < BAR_TICKS:
                lead_events.append(MusicEvent(pitch=0, volume=0, start_tick=accum_ticks, end_tick=BAR_TICKS))
            else:
                cropped = []
                for e in lead_events:
                    if e.start_tick < BAR_TICKS:
                        e.end_tick = min(e.end_tick, BAR_TICKS)
                        cropped.append(e)
                lead_events = cropped
                
            # Enforce exact bar length boundary to avoid cumulative drift
            if not lead_events or lead_events[-1].end_tick < BAR_TICKS:
                lead_events.append(MusicEvent(pitch=0, volume=0, start_tick=BAR_TICKS - 1, end_tick=BAR_TICKS))
                
            c.fill_voice_section("Lead", sec_name, MusicUnit(events=lead_events))
            
        # 2. Pad voice: chord pads lasting the whole bar
        if "Pad" in active_voices:
            pad_chord = CHORDS[s]
            pad_events = []
            for p in pad_chord:
                pad_events.append(MusicEvent(pitch=p, volume=65, start_tick=0, end_tick=BAR_TICKS))
            c.fill_voice_section("Pad", sec_name, MusicUnit(events=pad_events))
            
        # 3. Bass voice: root note holding the bar with rhythmic fifth-step pop at the end
        if "Bass" in active_voices:
            bass_pitch = BASS_ROOTS[s]
            bass_events = [
                MusicEvent(pitch=bass_pitch, volume=85, start_tick=0, end_tick=1440),
                MusicEvent(pitch=bass_pitch + 7, volume=75, start_tick=1440, end_tick=1920)
            ]
            c.fill_voice_section("Bass", sec_name, MusicUnit(events=bass_events))
            
    return c

# ------------------------------------------------------------- WAV I/O --------
def read_wav(path):
    with wave.open(path, 'rb') as wf:
        sr = wf.getframerate()
        n = wf.getnframes()
        data = wf.readframes(n)
        sig = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if wf.getnchannels() == 2:
            sig = sig.reshape(-1, 2)
        return sig, sr

def write_wav(filename, samples, num_channels, sample_rate=44100):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        audio = np.clip(samples, -1.0, 1.0)
        audio_int16 = (audio * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())

# ------------------------------------------------------------- MAIN ----------
def main():
    # Setup subdirectories
    os.makedirs(f"{PROJECT_DIR}/MIDI", exist_ok=True)
    os.makedirs(f"{PROJECT_DIR}/Audio", exist_ok=True)
    os.makedirs(f"{PROJECT_DIR}/Analysis", exist_ok=True)
    os.makedirs(f"{PROJECT_DIR}/Scores", exist_ok=True)
    
    print("--- STEP 1: PCFG Recursive Grammar Expansion ---")
    terminals = generate_pcfg_melody()
    print(f"Grammar successfully expanded to {len(terminals)} terminal steps.")
    
    print("\n--- STEP 2: Building Composition Matrices ---")
    # 1. Full Multi-track MIDI for DAW compliance
    comp_full = build_music_matrix(terminals)
    ok, msg = comp_full.validate()
    if not ok:
        raise SystemExit(f"Full composition validation failed: {msg}")
    midi_full_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}.mid"
    comp_full.to_midi(midi_full_path)
    print(f"Full MIDI saved: {midi_full_path} ({os.path.getsize(midi_full_path)} bytes)")
    
    # 2. Build and export separate track MIDI files for individual DAW stems (DAW/MTC Sync requirement)
    for v_name in ["Lead", "Pad", "Bass"]:
        comp_single = build_music_matrix(terminals, single_voice_filter=v_name)
        ok, msg = comp_single.validate()
        if not ok:
            raise SystemExit(f"Single-track validation for {v_name} failed: {msg}")
        midi_single_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}_{v_name}.mid"
        comp_single.to_midi(midi_single_path)
        print(f"  Exported DAW track: {midi_single_path} ({os.path.getsize(midi_single_path)} bytes)")
        
    print("\n--- STEP 3: Parsing MIDI to MusicXML via music21 (SP-005) ---")
    try:
        score = music21.converter.parse(midi_full_path)
        # Assign part names
        for i, part in enumerate(score.parts):
            if i == 0:
                part.partName = "Lead (Flute)"
            elif i == 1:
                part.partName = "Harmony (Pad)"
            elif i == 2:
                part.partName = "Bass"
        musicxml_path = f"{PROJECT_DIR}/Scores/{PROJECT_NAME}.musicxml"
        score.write('musicxml', fp=musicxml_path)
        print(f"MusicXML score exported successfully: {musicxml_path} ({os.path.getsize(musicxml_path)} bytes)")
    except Exception as e:
        print(f"Warning: MusicXML export failed: {e}")
        
    print("\n--- STEP 4: Rendering to Audio via FluidSynth CLI (SP-001) ---")
    wav_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_temp.wav"
    cmd_render = f"{FLUIDSYNTH_BIN} -ni -g 1.2 -F {wav_path} {SOUNDFONT_PATH} {midi_full_path} >/dev/null 2>&1"
    os.system(cmd_render)
    print(f"Rendered raw audio to {wav_path}")
    
    print("\n--- STEP 5: Peak Normalization ---")
    sig, sr = read_wav(wav_path)
    peak = np.max(np.abs(sig))
    if peak > 0:
        sig = sig * (0.89 / peak) # normalize to -1dB
    
    wav_norm_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_norm.wav"
    write_wav(wav_norm_path, sig, num_channels=2 if sig.ndim == 2 else 1, sample_rate=sr)
    
    print("\n--- STEP 6: Compressing to Opus OGG ---")
    ogg_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}.ogg"
    cmd_ffmpeg = f"ffmpeg -i {wav_norm_path} -codec:a libopus -application voip -b:a 48k {ogg_path} -y -loglevel error"
    os.system(cmd_ffmpeg)
    
    # Assert sizes
    midi_size = os.path.getsize(midi_full_path)
    ogg_size = os.path.getsize(ogg_path)
    print(f"Dual artifacts generated:")
    print(f"  - MIDI: {midi_full_path} ({midi_size} bytes)")
    print(f"  - OGG:  {ogg_path} ({ogg_size} bytes)")
    
    if midi_size <= 40 or ogg_size <= 40:
        raise SystemExit("Error: Generated files are empty or corrupt!")
        
    # Rhythm DNA visualization
    viz_path = f"{PROJECT_DIR}/Analysis/grid_visualization.txt"
    write_grid_visualization(comp_full.matrix, viz_path, ticks_per_character=240, bpm=BPM)
    print(f"Rhythm DNA written to {viz_path}")
    
    # Provenance JSON
    write_provenance(
        midi_full_path,
        classification=AI_ASSISTED,
        generator=f"Experimental/{PROJECT_NAME}/compose.py",
        parameters={
            "bpm": BPM,
            "methods": ["034", "SP-005"],
            "grid_voices": 3,
            "grid_sections": NUM_SECTIONS,
            "key": "D Dorian",
            "pcfg_seed": 50
        },
        notes="Composed via PCFG Recursion (Method 034) and synchronized for DAW integration (Method SP-005) with MusicXML + separated stems."
    )
    
    # Cleanup temporary files
    temp_files = [wav_path, wav_norm_path]
    for tf in temp_files:
        if os.path.exists(tf):
            os.remove(tf)
            
    print("Cleanup complete. Temp files removed.")
    print("Project successfully created!")

if __name__ == "__main__":
    main()
