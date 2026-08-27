# -*- coding: utf-8 -*-
"""Composition entry point — musicom engine only.
Generates an 8-bar piece using Physarum Polycephalum Transport Network Optimization (Method 035)
and synthesizes the lead voice using Digital Waveguide Bowed String physical modeling (Method SP-024).
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
PROJECT_ID = "047"
PROJECT_NAME = f"{PROJECT_ID}-physarum-bowed"
PROJECT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"

BPM = 110
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920 ticks
NUM_SECTIONS = 8                            # 8 bars total

# SoundFont configuration
SOUNDFONT_PATH = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH_BIN = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# Absolute Pitch Map representing Bb Major scale degrees
# Node 0 to 11
PITCH_MAP = [55, 58, 60, 62, 63, 65, 67, 70, 72, 74, 77, 79]  # G3, Bb3, C4, D4, Eb4, F4, G4, Bb4, C5, D5, F5, G5

# Chords corresponding to the 4 sections (each lasts 2 bars)
# Bar 1-2: Eb Major (Eb3, G3, Bb3, Eb4)
# Bar 3-4: F Major (F3, A3, C4, F4)
# Bar 5-6: G Minor (G3, Bb3, D4, G4)
# Bar 7-8: Bb Major (Bb2, D3, F3, Bb3)
CHORDS = [
    [51, 55, 58, 63],  # Eb Major
    [51, 55, 58, 63],
    [53, 57, 60, 65],  # F Major
    [53, 57, 60, 65],
    [55, 58, 62, 67],  # G Minor
    [55, 58, 62, 67],
    [46, 50, 53, 58],  # Bb Major
    [46, 50, 53, 58]
]

BASS_ROOTS = [39, 39, 41, 41, 43, 43, 34, 34]  # Eb2, Eb2, F2, F2, G2, G2, Bb1, Bb1

# ------------------------------------------------------------- PHYSARUM SIM --
def simulate_physarum(num_nodes=12, steps=128):
    """Simulates slime mold foraging and network optimization."""
    # Seed RNG for deterministic reproducibility
    rng = np.random.default_rng(47)
    
    positions = np.zeros((num_nodes, 2))
    for i in range(num_nodes):
        positions[i] = [i / (num_nodes - 1), 0.5 + 0.3 * np.sin(i * 1.5)]
        
    L = np.zeros((num_nodes, num_nodes))
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:
                dist = np.linalg.norm(positions[i] - positions[j])
                L[i, j] = max(dist, 0.15)
            else:
                L[i, i] = 1.0
                
    D = np.ones((num_nodes, num_nodes)) * 0.5
    np.fill_diagonal(D, 0.0)
    
    melody_history = []
    
    for t in range(steps):
        bar_idx = t // 16
        # Section chord nodes
        if bar_idx in [0, 1]:    # Eb Major: source = Node 4 (Eb4), sinks = Nodes 6 (G4), 7 (Bb4)
            source = 4
            sinks = [6, 7]
        elif bar_idx in [2, 3]:  # F Major: source = Node 5 (F4), sinks = Nodes 7 (Bb4), 8 (C5)
            source = 5
            sinks = [7, 8]
        elif bar_idx in [4, 5]:  # G Minor: source = Node 0 (G3), sinks = Nodes 3 (D4), 6 (G4)
            source = 0
            sinks = [3, 6]
        else:                  # Bb Major: source = Node 1 (Bb3), sinks = Nodes 3 (D4), 5 (F4)
            source = 1
            sinks = [3, 5]
            
        S = np.zeros(num_nodes)
        S[source] = 1.0
        for sink in sinks:
            S[sink] = -1.0 / len(sinks)
            
        C = D / L
        M = np.zeros((num_nodes, num_nodes))
        for i in range(num_nodes):
            M[i, i] = np.sum(C[i, :])
            for j in range(num_nodes):
                if i != j:
                    M[i, j] = -C[i, j]
                    
        # Ground node 0 to resolve singularity
        M[0, :] = 0.0
        M[0, 0] = 1.0
        S[0] = 0.0
        
        try:
            p = np.linalg.solve(M, S)
        except np.linalg.LinAlgError:
            p = np.zeros(num_nodes)
            
        Q = np.zeros((num_nodes, num_nodes))
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j:
                    Q[i, j] = (D[i, j] / L[i, j]) * (p[i] - p[j])
                    
        decay = 0.08
        D = D + np.abs(Q) - decay * D
        D = np.clip(D, 0.01, 6.0)
        np.fill_diagonal(D, 0.0)
        
        # Find active center of flow
        node_flows = np.sum(np.abs(Q), axis=1)
        center_node = np.argmax(node_flows)
        
        # Peristaltic wall contraction wave
        omega_0 = 0.75
        theta_ij = center_node * 1.6
        psi = node_flows[center_node] * (1.0 + 0.28 * np.sin(omega_0 * t + theta_ij))
        
        melody_history.append((center_node, psi))
        
    return melody_history

# ------------------------------------------------------------- BOWED STRING SYNTH --
def digital_waveguide_bowed_string(freq, sr, duration, bow_velocity=0.18, bow_force=1.4, bow_position=0.14, string_impedance=1.0, friction_decay=4.5, nut_reflection=0.99, bridge_reflection=0.94, lpf_coef=0.55, noise_level=0.012):
    """Synthesizes a bowed string using friction-induced waveguide physical modeling (SP-024)."""
    n_samples = int(sr * duration)
    if n_samples <= 0:
        return np.array([], dtype=np.float32)
        
    delay_total = int(round(sr / (2.0 * freq)))
    delay_neck = int(round(delay_total * bow_position))
    delay_bridge = delay_total - delay_neck
    
    if delay_neck < 2: delay_neck = 2
    if delay_bridge < 2: delay_bridge = 2
    
    neck_left = np.zeros(delay_neck)
    neck_right = np.zeros(delay_neck)
    bridge_left = np.zeros(delay_bridge)
    bridge_right = np.zeros(delay_bridge)
    
    lpf_state = 0.0
    
    # Envelope bow velocity to prevent pop clicks
    v_env = np.full(n_samples, bow_velocity)
    ramp = int(min(0.015 * sr, n_samples * 0.12))
    if ramp > 0:
        v_env[:ramp] = np.linspace(0.0, bow_velocity, ramp)
        v_env[-ramp:] = np.linspace(bow_velocity, 0.0, ramp)
        
    f_env = np.full(n_samples, bow_force)
    
    output = np.zeros(n_samples)
    bow_noise = np.random.normal(0, noise_level, n_samples)
    v_bow_noisy = v_env + v_env * bow_noise
    
    for n in range(n_samples):
        v_neck_in = neck_right[-1]
        v_bridge_in = bridge_left[0]
        v_incoming = v_neck_in + v_bridge_in
        
        v_b = v_bow_noisy[n]
        f_b = f_env[n]
        
        K = f_b / (2.0 * string_impedance)
        v_input = v_incoming - v_b
        v_rel = v_input
        
        # 4 steps of Newton-Raphson
        for _ in range(4):
            exp_term = np.exp(-friction_decay * v_rel**2)
            h_val = v_rel - K * v_rel * exp_term - v_input
            h_prime = 1.0 - K * exp_term * (1.0 - 2.0 * friction_decay * v_rel**2)
            v_rel = v_rel - h_val / h_prime
            
        v_string = v_rel + v_b
        delta_v = 0.5 * (v_string - v_incoming)
        
        v_neck_out = v_bridge_in + delta_v
        v_bridge_out = v_neck_in + delta_v
        
        neck_right_next = -nut_reflection * neck_left[0]
        bridge_end = bridge_right[-1]
        lpf_state = lpf_coef * bridge_end + (1.0 - lpf_coef) * lpf_state
        bridge_left_next = -bridge_reflection * lpf_state
        
        neck_left = np.roll(neck_left, 1)
        neck_left[0] = v_neck_out
        
        neck_right = np.roll(neck_right, 1)
        neck_right[0] = neck_right_next
        
        bridge_left = np.roll(bridge_left, 1)
        bridge_left[0] = bridge_left_next
        
        bridge_right = np.roll(bridge_right, 1)
        bridge_right[0] = v_bridge_out
        
        output[n] = lpf_state
        
    # Remove DC offset and normalize output
    output = output - np.mean(output)
    max_val = np.max(np.abs(output))
    if max_val > 0:
        output = output / max_val
        
    # Attack-Decay-Sustain-Release envelope (25ms A, 20ms D, 0.82 S, 60ms R)
    attack_samples = int(0.025 * sr)
    decay_samples = int(0.020 * sr)
    release_samples = int(0.060 * sr)
    
    env = np.ones(n_samples, dtype=np.float32)
    if n_samples > attack_samples + decay_samples + release_samples:
        env[:attack_samples] = np.linspace(0.0, 1.0, attack_samples)
        env[attack_samples : attack_samples + decay_samples] = np.linspace(1.0, 0.82, decay_samples)
        env[-release_samples:] = np.linspace(0.82, 0.0, release_samples)
        env[attack_samples + decay_samples : -release_samples] = 0.82
    else:
        env[:int(n_samples*0.1)] = np.linspace(0.0, 1.0, int(n_samples*0.1))
        env[-int(n_samples*0.2):] = np.linspace(1.0, 0.0, int(n_samples*0.2))
        
    return output * env

# ------------------------------------------------------------- SYNTH LEAD -----
def synthesize_lead_physarum(lead_units, sr=44100, bpm=110, ticks_per_beat=480):
    """Synthesizes Lead track notes sequentially using Bowed String wave synthesis."""
    seconds_per_tick = 60.0 / (bpm * ticks_per_beat)
    total_ticks = len(lead_units) * BAR_TICKS
    total_samples = int(sr * total_ticks * seconds_per_tick)
    
    lead_audio = np.zeros(total_samples, dtype=np.float32)
    
    for bar_idx, unit in enumerate(lead_units):
        col_start_tick = bar_idx * BAR_TICKS
        for event in unit.events:
            if event.pitch == 0 or event.volume == 0:
                continue
            
            # Absolute timing calculation
            start_tick = col_start_tick + event.start_tick
            end_tick = col_start_tick + event.end_tick
            
            start_sec = start_tick * seconds_per_tick
            dur_sec = (end_tick - start_tick) * seconds_per_tick
            
            freq = 440.0 * (2.0 ** ((event.pitch - 69) / 12.0))
            
            # Map volume to physical parameters
            force = 1.0 + (event.volume / 127.0) * 0.8
            vel = 0.12 + (event.volume / 127.0) * 0.15
            
            note_audio = digital_waveguide_bowed_string(freq, sr, dur_sec, bow_velocity=vel, bow_force=force)
            note_audio = note_audio * 0.35  # Bowed string mix balance
            
            start_sample = int(start_sec * sr)
            n_samples_note = len(note_audio)
            
            if start_sample + n_samples_note > total_samples:
                note_audio = note_audio[:total_samples - start_sample]
                n_samples_note = len(note_audio)
                
            lead_audio[start_sample : start_sample + n_samples_note] += note_audio
            
    return lead_audio

# ------------------------------------------------------------- COMPOSER MATRIX --
def build_music_matrix(lead_history, mode="full") -> UnitMatrixComposer:
    """Configures UnitMatrixComposer with Physarum-derived melody and chordal harmony."""
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    section_names = [f"Bar{i}" for i in range(1, NUM_SECTIONS + 1)]
    
    if mode == "full":
        c.create_matrix(num_voices=3, num_sections=NUM_SECTIONS)
        c.add_voice("Lead", program=40, channel=0)  # Violin
        c.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=1)
        c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    else:
        c.create_matrix(num_voices=2, num_sections=NUM_SECTIONS)
        c.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=1)
        c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
        
    for name in section_names:
        c.add_section(name, bars=1)
        
    lead_units_list = []
    # Translate Physarum history into MusicUnit blocks
    for s in range(NUM_SECTIONS):
        sec_name = section_names[s]
        
        # 1. Lead voice: sixteenth step notes
        lead_events = []
        accum_ticks = 0
        step_ticks = 120  # sixteenth note = 120 ticks
        
        # Get 16 steps corresponding to this bar
        bar_history = lead_history[s * 16 : (s + 1) * 16]
        
        for step_idx, (node, psi) in enumerate(bar_history):
            # Dynamic gating based on slime mold lifecycle:
            # Bar 1-2 (Exploratory): Trigger notes frequently. Low threshold.
            # Bar 3-4 (Optimization): High threshold. Clearer, strong peaks.
            # Bar 5-6 (MST): Steady, highly periodic triggers.
            # Bar 7-8 (Decay): Very high threshold, fading to silence.
            if s in [0, 1]:
                threshold = 0.35
            elif s in [2, 3]:
                threshold = 0.60
            elif s in [4, 5]:
                threshold = 0.50
            else:
                threshold = 0.85
                
            if psi > threshold:
                pitch = PITCH_MAP[node]
                # Scale velocity/volume proportional to contractive wave amplitude
                volume = int(np.clip(60 + psi * 25, 40, 115))
                # Note duration: eighth note (240 ticks) or sixteenth (120 ticks)
                dur = 240 if psi > 0.75 else 120
                
                # Truncate to avoid overlapping past sixteenth grid bounds if needed
                # For simplicity, let's keep it clean
                lead_events.append(MusicEvent(
                    pitch=pitch,
                    volume=volume,
                    start_tick=accum_ticks,
                    end_tick=accum_ticks + dur
                ))
            else:
                # Rest
                pass
                
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
            
        lead_unit = MusicUnit(events=lead_events)
        lead_units_list.append(lead_unit)
        
        # 2. Pad voice: chord pads lasting the whole bar
        pad_chord = CHORDS[s]
        pad_events = []
        for p in pad_chord:
            pad_events.append(MusicEvent(pitch=p, volume=70, start_tick=0, end_tick=BAR_TICKS))
        pad_unit = MusicUnit(events=pad_events)
        
        # 3. Bass voice: root note holding the bar
        bass_pitch = BASS_ROOTS[s]
        # Play dotted half + quarter note for movement
        bass_events = [
            MusicEvent(pitch=bass_pitch, volume=85, start_tick=0, end_tick=1440),
            MusicEvent(pitch=bass_pitch + 7, volume=75, start_tick=1440, end_tick=1920) # fifth step up
        ]
        bass_unit = MusicUnit(events=bass_events)
        
        # Fill cells
        if mode == "full":
            c.fill_voice_section("Lead", sec_name, lead_unit)
            c.fill_voice_section("Pad", sec_name, pad_unit)
            c.fill_voice_section("Bass", sec_name, bass_unit)
        else:
            c.fill_voice_section("Pad", sec_name, pad_unit)
            c.fill_voice_section("Bass", sec_name, bass_unit)
            
    if mode == "full":
        return c, lead_units_list
        
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
    
    print("--- STEP 1: Physarum Network Simulation ---")
    lead_history = simulate_physarum(num_nodes=12, steps=128)
    print(f"Slime mold simulation finished. Generated {len(lead_history)} steps of developmental data.")
    
    print("\n--- STEP 2: Building Composition Matrices ---")
    # 1. Full Multi-track MIDI
    comp_full, lead_units = build_music_matrix(lead_history, mode="full")
    ok, msg = comp_full.validate()
    if not ok:
        raise SystemExit(f"Full composition validation failed: {msg}")
    midi_full_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}.mid"
    comp_full.to_midi(midi_full_path)
    print(f"Full MIDI saved: {midi_full_path} ({os.path.getsize(midi_full_path)} bytes)")
    
    # 2. Accompaniment-only MIDI
    comp_accomp = build_music_matrix(lead_history, mode="accomp_only")
    ok, msg = comp_accomp.validate()
    if not ok:
        raise SystemExit(f"Accompaniment validation failed: {msg}")
    midi_accomp_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}_accomp_temp.mid"
    comp_accomp.to_midi(midi_accomp_path)
    
    print("\n--- STEP 3: Rendering Accompaniment with FluidSynth ---")
    wav_accomp_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_accomp_temp.wav"
    # Execute FluidSynth CLI render
    cmd_render = f"{FLUIDSYNTH_BIN} -ni -g 1.1 -F {wav_accomp_path} {SOUNDFONT_PATH} {midi_accomp_path} >/dev/null 2>&1"
    os.system(cmd_render)
    print(f"Accompaniment rendered: {wav_accomp_path}")
    
    print("\n--- STEP 4: Synthesizing Lead via Bowed String Waveguide Synthesis ---")
    sr = 44100
    # We already have lead_units from building the full matrix
    lead_sig = synthesize_lead_physarum(lead_units, sr=sr, bpm=BPM, ticks_per_beat=TICKS_PER_BEAT)
    print(f"Bowed string physical model output synthesized: {len(lead_sig)} samples")
    
    print("\n--- STEP 5: Mixing and Mastering ---")
    accomp_sig, _ = read_wav(wav_accomp_path)
    
    # Pad to match maximum duration
    max_len = max(len(lead_sig), len(accomp_sig))
    lead_padded = np.zeros(max_len, dtype=np.float32)
    lead_padded[:len(lead_sig)] = lead_sig
    
    if accomp_sig.ndim == 2:
        accomp_padded = np.zeros((max_len, 2), dtype=np.float32)
        accomp_padded[:len(accomp_sig), :] = accomp_sig
        mixed = np.zeros((max_len, 2), dtype=np.float32)
        mixed[:, 0] = lead_padded * 0.55 + accomp_padded[:, 0] * 0.75
        mixed[:, 1] = lead_padded * 0.55 + accomp_padded[:, 1] * 0.75
        num_channels = 2
    else:
        accomp_padded = np.zeros(max_len, dtype=np.float32)
        accomp_padded[:len(accomp_sig)] = accomp_sig
        mixed = lead_padded * 0.55 + accomp_padded * 0.75
        num_channels = 1
        
    # Master peak normalization to -1dB
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
    
    # Provenance JSON
    write_provenance(
        midi_full_path,
        classification=AI_ASSISTED,
        generator=f"Experimental/{PROJECT_NAME}/compose.py",
        parameters={
            "bpm": BPM,
            "methods": ["035", "SP-024"],
            "grid_voices": 3,
            "grid_sections": NUM_SECTIONS,
            "physical_model": "digital_waveguide_bowed_string",
            "key": "Bb Major / G Minor",
            "physarum_seed": 47
        },
        notes="Composed via Physarum Polycephalum Transport Network Optimization (Method 035) and synthesized via bowed string waveguide modeling (Method SP-024)."
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
