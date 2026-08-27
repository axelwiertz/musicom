# -*- coding: utf-8 -*-
"""Composition entry point — musicom engine only.
Generates a 3-track electronic piece using Wave Function Collapse Grid Synthesis (Method 033)
and synthesizes the lead voice using Wave Terrain Synthesis (Method SP-022).
"""
import os
import wave
import sys
import numpy as np
import random

# Ensure clean imports from the installed musicom package
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# ---------------------------------------------------------------- CONFIG -----
PROJECT_ID = "045"
PROJECT_NAME = f"{PROJECT_ID}-wfc-terrain"
PROJECT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"

BPM = 100
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920 ticks
NUM_SECTIONS = 8                            # 8 bars total

# SoundFont configuration
SOUNDFONT_PATH = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH_BIN = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# ---------------------------------------------------------------- WFCGS -----
# Method 033: Wave Function Collapse Grid Synthesis

TILES = [
    # Lead tiles (0, 1)
    {"id": 0, "voice": "Lead", "pitch": [62, 65, 67, 69, 67, 65, 62, 60], "rhythm": [240]*8, "type": "melody"},
    {"id": 1, "voice": "Lead", "pitch": [69, 72, 74, 76, 74, 72, 69, 67], "rhythm": [240]*8, "type": "melody"},
    # Pad tiles (2, 3)
    {"id": 2, "voice": "Pad", "pitch": [[50, 57, 60, 64], [43, 55, 59, 62]], "rhythm": [960, 960], "type": "harmony"},
    {"id": 3, "voice": "Pad", "pitch": [[48, 55, 59, 62], [45, 52, 55, 59]], "rhythm": [960, 960], "type": "harmony"},
    # Bass tiles (4, 5)
    {"id": 4, "voice": "Bass", "pitch": [38, 0, 38, 41, 0, 41, 43, 45], "rhythm": [240]*8, "type": "bass"},
    {"id": 5, "voice": "Bass", "pitch": [36, 0, 36, 40, 0, 40, 43, 45], "rhythm": [240]*8, "type": "bass"},
]

# Horizontal rules: maps tile_id -> valid next tile_ids in same voice
HORIZONTAL_RULES = {
    0: [0, 1], # Motif A -> A or B
    1: [0, 1], # Motif B -> A or B
    2: [3],    # Chord A -> Chord B (forces alternation)
    3: [2],    # Chord B -> Chord A
    4: [4, 5], # Bass A -> Bass A or B
    5: [4, 5], # Bass B -> Bass A or B
}

# Vertical rules: maps tile_id -> valid below tile_ids in adjacent voices
# Row 0 (Lead) can stand above Pad (Row 1)
# Row 1 (Pad) can stand above Bass (Row 2)
VERTICAL_RULES = {
    0: [2, 3], # Lead 0 can be above Pad 2 or Pad 3
    1: [3],    # Lead 1 can only be above Pad 3 (high tension over Chord B)
    2: [4],    # Pad 2 must be above Bass 4 (D-based)
    3: [5],    # Pad 3 must be above Bass 5 (C-based)
}

def solve_wfc(num_voices, num_sections, tiles, horizontal_rules, vertical_rules):
    """Collapses the music grid under horizontal and vertical constraints."""
    voice_tiles = {
        0: [0, 1], # Lead
        1: [2, 3], # Pad
        2: [4, 5], # Bass
    }
    
    max_retries = 50
    for attempt in range(max_retries):
        # Initialize grid superposition
        grid = [[set(voice_tiles[v]) for _ in range(num_sections)] for v in range(num_voices)]
        
        def propagate(v, s):
            queue = [(v, s)]
            visited = set()
            while queue:
                curr_v, curr_s = queue.pop(0)
                if (curr_v, curr_s) in visited:
                    continue
                visited.add((curr_v, curr_s))
                
                curr_allowed = grid[curr_v][curr_s]
                if not curr_allowed:
                    return False # Contradiction!
                    
                # 1. Left neighbor
                if curr_s > 0:
                    prev_allowed = grid[curr_v][curr_s - 1]
                    new_prev = {t for t in prev_allowed if any(next_t in curr_allowed for next_t in horizontal_rules.get(t, []))}
                    if len(new_prev) < len(prev_allowed):
                        grid[curr_v][curr_s - 1] = new_prev
                        queue.append((curr_v, curr_s - 1))
                        
                # 2. Right neighbor
                if curr_s < num_sections - 1:
                    next_allowed = grid[curr_v][curr_s + 1]
                    valid_next = set()
                    for t in curr_allowed:
                        valid_next.update(horizontal_rules.get(t, []))
                    new_next = next_allowed.intersection(valid_next)
                    if len(new_next) < len(next_allowed):
                        grid[curr_v][curr_s + 1] = new_next
                        queue.append((curr_v, curr_s + 1))
                        
                # 3. Up neighbor
                if curr_v > 0:
                    above_allowed = grid[curr_v - 1][curr_s]
                    new_above = {t for t in above_allowed if any(below_t in curr_allowed for below_t in vertical_rules.get(t, []))}
                    if len(new_above) < len(above_allowed):
                        grid[curr_v - 1][curr_s] = new_above
                        queue.append((curr_v - 1, curr_s))
                        
                # 4. Down neighbor
                if curr_v < num_voices - 1:
                    below_allowed = grid[curr_v + 1][curr_s]
                    valid_below = set()
                    for t in curr_allowed:
                        valid_below.update(vertical_rules.get(t, []))
                    new_below = below_allowed.intersection(valid_below)
                    if len(new_below) < len(below_allowed):
                        grid[curr_v + 1][curr_s] = new_below
                        queue.append((curr_v + 1, curr_s))
            return True

        # Pre-seed first bar to establish tonal center
        grid[1][0] = {2} # Chord A
        grid[2][0] = {4} # Bass A
        if not propagate(1, 0) or not propagate(2, 0):
            continue
            
        success = True
        while True:
            # Find cell with minimum entropy > 1
            min_ent = 999
            target = None
            for v in range(num_voices):
                for s in range(num_sections):
                    sz = len(grid[v][s])
                    if sz > 1 and sz < min_ent:
                        min_ent = sz
                        target = (v, s)
                        
            if target is None:
                break # All collapsed!
                
            v, s = target
            chosen = random.choice(list(grid[v][s]))
            grid[v][s] = {chosen}
            if not propagate(v, s):
                success = False
                break
                
        if success:
            if any(any(len(grid[v][s]) == 0 for s in range(num_sections)) for v in range(num_voices)):
                continue
            return [[tiles[list(grid[v][s])[0]] for s in range(num_sections)] for v in range(num_voices)]
            
    raise RuntimeError("WFC failed to collapse after maximum retries.")

# ---------------------------------------------------------------- SP-022 WTS -----
# Method SP-022: Wave Terrain Synthesis

def terrain_sine_product(x, y):
    """Terrain function: vocal/multi-modal sine product."""
    return np.sin(np.pi * x) * np.cos(np.pi * y)

def synth_wts_note(freq, dur, sr=44100, volume=100):
    """Synthesizes a single note waveform using Wave Terrain Synthesis with dynamic timbre sweep."""
    if freq <= 0 or dur <= 0:
        return np.zeros(int(sr * dur))
        
    n_samples = int(sr * dur)
    t = np.linspace(0, dur, n_samples, endpoint=False)
    
    # Orbit scale modulation (timbral sweep envelope)
    # Starts small, sweeps wide (attack), then narrows down (decay)
    attack_samples = int(0.2 * n_samples)
    decay_samples = n_samples - attack_samples
    
    r_attack = np.linspace(0.1, 0.9, attack_samples)
    r_decay = np.linspace(0.9, 0.2, decay_samples)
    r_mod = np.concatenate([r_attack, r_decay])
    
    # Scanning orbit: Lissajous orbit with ratio_y = 1.5
    phase_x = 2.0 * np.pi * freq * t
    phase_y = 2.0 * np.pi * freq * 1.5 * t
    
    x = r_mod * np.sin(phase_x)
    y = r_mod * np.sin(phase_y)
    
    # Keep trajectory within bounds
    x = np.clip(x, -1.0, 1.0)
    y = np.clip(y, -1.0, 1.0)
    
    # Terrain readout
    audio = terrain_sine_product(x, y)
    
    # Click-free volume ADSR envelope (5ms attack, 20ms release)
    att_env = int(min(0.005 * sr, n_samples * 0.1))
    rel_env = int(min(0.02 * sr, n_samples * 0.1))
    sus_env = n_samples - att_env - rel_env
    
    env_attack = np.linspace(0.0, 1.0, att_env)
    env_release = np.linspace(1.0, 0.0, rel_env)
    env_sustain = np.ones(sus_env)
    
    env = np.concatenate([env_attack, env_sustain, env_release])
    env = env[:n_samples]
    if len(env) < n_samples:
        env = np.pad(env, (0, n_samples - len(env)), 'constant', constant_values=0.0)
        
    # Scale by velocity volume
    return audio * env * (volume / 127.0) * 0.5


def synthesize_wts_lead(collapsed_grid, sr=44100, bpm=100, ticks_per_beat=480):
    """Synthesizes the complete Lead voice using Wave Terrain Synthesis."""
    seconds_per_tick = 60.0 / (bpm * ticks_per_beat)
    bar_ticks = ticks_per_beat * 4
    total_ticks = len(collapsed_grid[0]) * bar_ticks
    total_samples = int(sr * total_ticks * seconds_per_tick)
    
    lead_audio = np.zeros(total_samples)
    
    for col in range(len(collapsed_grid[0])):
        tile = collapsed_grid[0][col]
        pitch_list = tile["pitch"]
        rhythm_list = tile["rhythm"]
        
        col_start_tick = col * bar_ticks
        accum_ticks = 0
        
        for i, dur in enumerate(rhythm_list):
            pitch = pitch_list[i % len(pitch_list)]
            note_start_tick = col_start_tick + accum_ticks
            note_dur_ticks = dur
            
            if pitch is not None and pitch > 0:
                freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
                start_sec = note_start_tick * seconds_per_tick
                dur_sec = note_dur_ticks * seconds_per_tick
                
                # Synthesize note
                note_audio = synth_wts_note(freq, dur_sec, sr, volume=100)
                
                start_sample = int(start_sec * sr)
                n_samples_note = len(note_audio)
                
                if start_sample + n_samples_note > total_samples:
                    note_audio = note_audio[:total_samples - start_sample]
                    n_samples_note = len(note_audio)
                    
                lead_audio[start_sample : start_sample + n_samples_note] += note_audio
                
            accum_ticks += dur
            
    return lead_audio


# ---------------------------------------------------------------- HELPERS -----

def tile_to_unit(tile, volume=90) -> MusicUnit:
    """Converts WFC tile representation to a zero-drift MusicUnit."""
    events = []
    accumulated_ticks = 0
    pitch_list = tile["pitch"]
    rhythm_list = tile["rhythm"]
    
    for i, dur in enumerate(rhythm_list):
        pitch = pitch_list[i % len(pitch_list)]
        if pitch is not None:
            if isinstance(pitch, (list, tuple)):
                for p in pitch:
                    events.append(MusicEvent(
                        pitch=p if p > 0 else 0,
                        volume=volume if p > 0 else 0,
                        start_tick=accumulated_ticks,
                        end_tick=accumulated_ticks + dur
                    ))
            elif pitch > 0:
                events.append(MusicEvent(
                    pitch=pitch,
                    volume=volume,
                    start_tick=accumulated_ticks,
                    end_tick=accumulated_ticks + dur
                ))
            else:
                events.append(MusicEvent(
                    pitch=0,
                    volume=0,
                    start_tick=accumulated_ticks,
                    end_tick=accumulated_ticks + dur
                ))
        else:
            events.append(MusicEvent(
                pitch=0,
                volume=0,
                start_tick=accumulated_ticks,
                end_tick=accumulated_ticks + dur
            ))
        accumulated_ticks += dur
        
    if accumulated_ticks < BAR_TICKS:
        events.append(MusicEvent(
            pitch=0,
            volume=0,
            start_tick=accumulated_ticks,
            end_tick=BAR_TICKS
        ))
        
    return MusicUnit(events=events)


def build_composition(collapsed_grid, mode="full") -> UnitMatrixComposer:
    """Builds UnitMatrixComposer representation of the piece."""
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    
    section_names = [f"Bar{i}" for i in range(1, NUM_SECTIONS + 1)]
    
    if mode == "full":
        c.create_matrix(num_voices=3, num_sections=NUM_SECTIONS)
        c.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
        c.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=1)
        c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
        
        for name in section_names:
            c.add_section(name, bars=1)
            
        for s in range(NUM_SECTIONS):
            c.fill_voice_section("Lead", section_names[s], tile_to_unit(collapsed_grid[0][s], volume=90))
            c.fill_voice_section("Pad", section_names[s], tile_to_unit(collapsed_grid[1][s], volume=80))
            c.fill_voice_section("Bass", section_names[s], tile_to_unit(collapsed_grid[2][s], volume=95))
            
    elif mode == "accomp_only":
        c.create_matrix(num_voices=2, num_sections=NUM_SECTIONS)
        c.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=1)
        c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
        
        for name in section_names:
            c.add_section(name, bars=1)
            
        for s in range(NUM_SECTIONS):
            c.fill_voice_section("Pad", section_names[s], tile_to_unit(collapsed_grid[1][s], volume=80))
            c.fill_voice_section("Bass", section_names[s], tile_to_unit(collapsed_grid[2][s], volume=95))
            
    return c


def read_wav(path):
    """Helper to read WAV file into np.ndarray."""
    with wave.open(path, 'rb') as wf:
        sr = wf.getframerate()
        n = wf.getnframes()
        data = wf.readframes(n)
        sig = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if wf.getnchannels() == 2:
            sig = sig.reshape(-1, 2)
        return sig, sr


def write_wav(filename, samples, num_channels, sample_rate=44100):
    """Helper to write np.ndarray to WAV file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        audio = np.clip(samples, -1.0, 1.0)
        audio_int16 = (audio * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())


# ---------------------------------------------------------------- MAIN -----

def main():
    # Create directories
    os.makedirs(f"{PROJECT_DIR}/MIDI", exist_ok=True)
    os.makedirs(f"{PROJECT_DIR}/Audio", exist_ok=True)
    os.makedirs(f"{PROJECT_DIR}/Analysis", exist_ok=True)
    
    print("--- STEP 1: Wave Function Collapse Grid Collapse ---")
    grid = solve_wfc(3, NUM_SECTIONS, TILES, HORIZONTAL_RULES, VERTICAL_RULES)
    print("Grid collapsed successfully!")
    for v in range(3):
        row_str = " | ".join([f"Tile {grid[v][s]['id']}" for s in range(NUM_SECTIONS)])
        print(f"Voice {v}: {row_str}")
        
    print("\n--- STEP 2: Generating and Validating MIDI Files ---")
    
    # 1. Full Multi-track MIDI
    comp_full = build_composition(grid, mode="full")
    ok, msg = comp_full.validate()
    if not ok:
        raise SystemExit(f"Full composition validation failed (track drift): {msg}")
    midi_full_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}.mid"
    comp_full.to_midi(midi_full_path)
    print(f"Full MIDI saved: {midi_full_path} ({os.path.getsize(midi_full_path)} bytes)")
    
    # 2. Accompaniment-only MIDI (for rendering)
    comp_accomp = build_composition(grid, mode="accomp_only")
    ok, msg = comp_accomp.validate()
    if not ok:
        raise SystemExit(f"Accompaniment validation failed: {msg}")
    midi_accomp_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}_accomp_temp.mid"
    comp_accomp.to_midi(midi_accomp_path)
    
    print("\n--- STEP 3: Rendering Accompaniment with FluidSynth ---")
    wav_accomp_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_accomp_temp.wav"
    cmd_render = f"{FLUIDSYNTH_BIN} -ni -g 1.4 -F {wav_accomp_path} {SOUNDFONT_PATH} {midi_accomp_path} >/dev/null 2>&1"
    os.system(cmd_render)
    print(f"Accompaniment rendered: {wav_accomp_path}")
    
    print("\n--- STEP 4: Synthesizing Lead via Wave Terrain Synthesis ---")
    sr = 44100
    lead_sig = synthesize_wts_lead(grid, sr=sr, bpm=BPM, ticks_per_beat=TICKS_PER_BEAT)
    print(f"WTS Lead Synthesized: {len(lead_sig)} samples")
    
    print("\n--- STEP 5: Mixing and Mastering ---")
    accomp_sig, _ = read_wav(wav_accomp_path)
    
    # Pad or slice to match lengths
    max_len = max(len(lead_sig), len(accomp_sig))
    lead_padded = np.zeros(max_len, dtype=np.float32)
    lead_padded[:len(lead_sig)] = lead_sig
    
    if accomp_sig.ndim == 2:
        # Stereo accomp
        accomp_padded = np.zeros((max_len, 2), dtype=np.float32)
        accomp_padded[:len(accomp_sig), :] = accomp_sig
        
        mixed = np.zeros((max_len, 2), dtype=np.float32)
        mixed[:, 0] = lead_padded * 0.55 + accomp_padded[:, 0] * 0.75
        mixed[:, 1] = lead_padded * 0.55 + accomp_padded[:, 1] * 0.75
        num_channels = 2
    else:
        # Mono accomp
        accomp_padded = np.zeros(max_len, dtype=np.float32)
        accomp_padded[:len(accomp_sig)] = accomp_sig
        
        mixed = lead_padded * 0.55 + accomp_padded * 0.75
        num_channels = 1
        
    # Peak Normalization to ~-1dB
    peak = np.max(np.abs(mixed))
    if peak > 0:
        mixed = mixed * (0.89 / peak)
        
    wav_mixed_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_temp_mix.wav"
    write_wav(wav_mixed_path, mixed, num_channels, sample_rate=sr)
    
    print("\n--- STEP 6: Compressing to Opus OGG ---")
    ogg_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}.ogg"
    cmd_ffmpeg = f"ffmpeg -i {wav_mixed_path} -codec:a libopus -application voip -b:a 48k {ogg_path} -y -loglevel error"
    os.system(cmd_ffmpeg)
    print(f"OGG saved: {ogg_path} ({os.path.getsize(ogg_path)} bytes)")
    
    # Rhythm DNA visualization
    viz_path = f"{PROJECT_DIR}/Analysis/grid_visualization.txt"
    write_grid_visualization(comp_full.matrix, viz_path, ticks_per_character=240, bpm=BPM)
    print(f"Rhythm DNA written to {viz_path}")
    
    # Provenance
    write_provenance(
        midi_full_path,
        classification=AI_ASSISTED,
        generator=f"Experimental/{PROJECT_NAME}/compose.py",
        parameters={
            "bpm": BPM,
            "methods": ["033", "SP-022"],
            "grid_voices": 3,
            "grid_sections": NUM_SECTIONS,
            "terrain": "sine_product",
            "orbit": "lissajous",
            "wts_lead_ratio": 1.5,
        },
        notes="Composed via Wave Function Collapse Grid Synthesis (Method 033) and synthesized via Wave Terrain Synthesis (Method SP-022)."
    )
    
    # Cleanup temporary files
    temp_files = [midi_accomp_path, wav_accomp_path, wav_mixed_path]
    for tf in temp_files:
        if os.path.exists(tf):
            os.remove(tf)
            
    print("Cleanup complete. Temp files removed.")
    print("Project successfully created!")

if __name__ == "__main__":
    main()
