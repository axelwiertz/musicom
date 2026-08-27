# -*- coding: utf-8 -*-
"""Composition entry point — musicom engine only.
Generates an 8-bar piece using Probabilistic Context-Free Grammar Recursion (Method 034)
and spatializes each voice using Binaural Woodworth-Schlosberg Spatialization (Method SP-021).
"""
import os
import wave
import sys
import numpy as np

# Ensure clean imports from the installed musicom package
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# ---------------------------------------------------------------- CONFIG -----
PROJECT_ID = "048"
PROJECT_NAME = f"{PROJECT_ID}-pcfg-binaural"
PROJECT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"

BPM = 100
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920 ticks
NUM_SECTIONS = 8                            # 8 bars total

# SoundFont configuration
SOUNDFONT_PATH = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH_BIN = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# Absolute Pitch Map representing C Dorian scale degrees
# Index 0 to 11
PITCH_MAP = [60, 62, 63, 65, 67, 69, 70, 72, 74, 75, 77, 79]  # C4, D4, Eb4, F4, G4, A4, Bb4, C5, D5, Eb5, F5, G5

# Chords corresponding to the 8 sections (each lasts 1 bar)
CHORDS = [
    [48, 51, 55, 58],  # Cm7 (Bar 1)
    [41, 45, 48, 51],  # F7 (Bar 2)
    [34, 38, 41, 46],  # Bb (Bar 3)
    [39, 43, 46, 50],  # EbMaj7 (Bar 4)
    [48, 51, 55, 58],  # Cm7 (Bar 5)
    [41, 45, 48, 51],  # F7 (Bar 6)
    [31, 34, 38, 41],  # Gm7 (Bar 7)
    [48, 52, 55, 60]   # C Major Picardy third (Bar 8)
]

BASS_ROOTS = [36, 41, 34, 39, 36, 41, 31, 36]  # C2, F2, Bb1, Eb2, C2, F2, G1, C2

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
    rng = np.random.default_rng(48)
    
    # We expand S, which will resolve to 8 bars of 16 sixteenths each = 128 notes
    terminals = expand_symbol('S', PCFG_RULES, rng)
    return terminals

# ------------------------------------------------------------- BINAURAL SPATIAL --
def first_order_lowpass(x, fc, fs):
    """Applies a simple first-order lowpass filter to x with cutoff fc."""
    n_samples = len(x)
    y = np.zeros(n_samples, dtype=np.float32)
    if np.isscalar(fc):
        fc_arr = np.full(n_samples, fc, dtype=np.float32)
    else:
        fc_arr = np.asarray(fc, dtype=np.float32)
    alpha = (2 * np.pi * fc_arr / fs) / (2 * np.pi * fc_arr / fs + 1.0)
    alpha = np.clip(alpha, 0.0, 1.0)
    y_prev = 0.0
    for i in range(n_samples):
        y[i] = alpha[i] * x[i] + (1.0 - alpha[i]) * y_prev
        y_prev = y[i]
    return y

def linear_fractional_delay(x, delay_samples):
    """Applies fractional delay to 1D signal x using linear interpolation."""
    n_samples = len(x)
    y = np.zeros(n_samples, dtype=np.float32)
    if np.isscalar(delay_samples):
        d_arr = np.full(n_samples, delay_samples, dtype=np.float32)
    else:
        d_arr = np.asarray(delay_samples, dtype=np.float32)
    for i in range(n_samples):
        d = d_arr[i]
        d_int = int(np.floor(d))
        d_frac = d - d_int
        idx1 = i - d_int
        idx2 = idx1 - 1
        val1 = x[idx1] if 0 <= idx1 < n_samples else 0.0
        val2 = x[idx2] if 0 <= idx2 < n_samples else 0.0
        y[i] = (1.0 - d_frac) * val1 + d_frac * val2
    return y

def binaural_spatialization(x, fs, azimuth, distance=1.0, head_radius=0.0875, speed_of_sound=343.0):
    """Applies Binaural Woodworth-Schlosberg Spatialization (SP-021) to a mono signal."""
    n_samples = len(x)
    ref_distance = 1.0
    attn = ref_distance / max(distance, ref_distance)
    x_attn = x * attn
    if np.isscalar(azimuth):
        az_arr = np.full(n_samples, azimuth, dtype=np.float32)
    else:
        az_arr = np.asarray(azimuth, dtype=np.float32)
    az_arr = (az_arr + np.pi) % (2 * np.pi) - np.pi
    abs_az = np.abs(az_arr)
    tau = (head_radius / speed_of_sound) * (np.sin(abs_az) + abs_az)
    tau_samples = tau * fs
    delay_l = np.where(az_arr >= 0.0, tau_samples, 0.0)
    delay_r = np.where(az_arr < 0.0, tau_samples, 0.0)
    delayed_l = linear_fractional_delay(x_attn, delay_l)
    delayed_r = linear_fractional_delay(x_attn, delay_r)
    f_max = 20000.0
    f_min = 1000.0
    p = 2.0
    fc_l = np.where(az_arr >= 0.0, f_min + (f_max - f_min) * ((1.0 + np.cos(az_arr)) / 2.0)**p, f_max)
    fc_r = np.where(az_arr < 0.0, f_min + (f_max - f_min) * ((1.0 + np.cos(az_arr)) / 2.0)**p, f_max)
    out_l = first_order_lowpass(delayed_l, fc_l, fs)
    out_r = first_order_lowpass(delayed_r, fc_r, fs)
    return np.column_stack((out_l, out_r))

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
        "Lead": {"program": 40, "channel": 0},  # Violin
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
    
    # 2. Build and export separate track MIDI files for individual binaural spatial processing
    tracks_wav = {}
    for v_name in ["Lead", "Pad", "Bass"]:
        comp_single = build_music_matrix(terminals, single_voice_filter=v_name)
        ok, msg = comp_single.validate()
        if not ok:
            raise SystemExit(f"Single-track validation for {v_name} failed: {msg}")
        midi_single_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}_{v_name}_temp.mid"
        comp_single.to_midi(midi_single_path)
        
        # Render single-track MIDI to WAV via FluidSynth CLI
        wav_single_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_{v_name}_temp.wav"
        cmd_render = f"{FLUIDSYNTH_BIN} -ni -g 1.2 -F {wav_single_path} {SOUNDFONT_PATH} {midi_single_path} >/dev/null 2>&1"
        os.system(cmd_render)
        print(f"Track {v_name} rendered to WAV: {wav_single_path}")
        
        # Load and store signal
        sig, sr = read_wav(wav_single_path)
        # Convert to mono if stereo
        if sig.ndim == 2:
            sig = (sig[:, 0] + sig[:, 1]) / 2.0
        tracks_wav[v_name] = (sig, sr, midi_single_path, wav_single_path)
        
    print("\n--- STEP 3: Applying Binaural Woodworth-Schlosberg Spatialization (SP-021) ---")
    sr = 44100
    # Determine the maximum sample length across all tracks
    max_len = max(len(tracks_wav[v_name][0]) for v_name in tracks_wav)
    
    # Initialize stereo master bus
    master_stereo = np.zeros((max_len, 2), dtype=np.float32)
    
    for v_name, (sig, sig_sr, mid_path, wav_path) in tracks_wav.items():
        # Pad signal to max length
        sig_padded = np.zeros(max_len, dtype=np.float32)
        sig_padded[:len(sig)] = sig
        
        # Apply specific spatial layout
        if v_name == "Lead":
            # Dynamic sweep from far-left (-pi/2) to far-right (pi/2) and back
            t_vals = np.linspace(0, max_len / sr, max_len, dtype=np.float32)
            # Cycle slowly: sweeps left to right every 9.6 seconds (half of the 19.2s piece)
            azimuths = (np.pi / 2.0) * np.sin(2 * np.pi * 0.104 * t_vals)
            spatial_sig = binaural_spatialization(sig_padded, sr, azimuths)
            mix_gain = 0.65
        elif v_name == "Pad":
            # Fixed left position (-pi/4)
            spatial_sig = binaural_spatialization(sig_padded, sr, -np.pi / 4.0)
            mix_gain = 0.40
        else:  # Bass
            # Slightly right of center (pi/12)
            spatial_sig = binaural_spatialization(sig_padded, sr, np.pi / 12.0)
            mix_gain = 0.70
            
        master_stereo += spatial_sig * mix_gain
        print(f"Spatialized {v_name} onto 3D master bus (gain={mix_gain}).")
        
    print("\n--- STEP 4: Mastering and Peak Normalization ---")
    # Master peak normalization to -1dB (~0.89)
    peak = np.max(np.abs(master_stereo))
    if peak > 0:
        master_stereo = master_stereo * (0.89 / peak)
        
    wav_mixed_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_temp_mix.wav"
    write_wav(wav_mixed_path, master_stereo, num_channels=2, sample_rate=sr)
    
    print("\n--- STEP 5: Compressing to Opus OGG ---")
    ogg_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}.ogg"
    cmd_ffmpeg = f"ffmpeg -i {wav_mixed_path} -codec:a libopus -application voip -b:a 48k {ogg_path} -y -loglevel error"
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
            "methods": ["034", "SP-021"],
            "grid_voices": 3,
            "grid_sections": NUM_SECTIONS,
            "key": "C Dorian",
            "pcfg_seed": 48
        },
        notes="Composed via PCFG Recursion (Method 034) and spatialized via Binaural Spatialization (Method SP-021)."
    )
    
    # Cleanup temporary files
    temp_files = [wav_mixed_path]
    for v_name, (_, _, mid_path, wav_path) in tracks_wav.items():
        temp_files.append(mid_path)
        temp_files.append(wav_path)
        
    for tf in temp_files:
        if os.path.exists(tf):
            os.remove(tf)
            
    print("Cleanup complete. Temp files removed.")
    print("Project successfully created!")

if __name__ == "__main__":
    main()
