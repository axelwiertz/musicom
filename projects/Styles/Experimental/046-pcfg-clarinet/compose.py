# -*- coding: utf-8 -*-
"""Composition entry point — musicom engine only.
Generates a 3-track piece using PCFG Recursion (Method 034)
and synthesizes the lead voice using Digital Waveguide Clarinet physical modeling (Method SP-023).
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
PROJECT_ID = "046"
PROJECT_NAME = f"{PROJECT_ID}-pcfg-clarinet"
PROJECT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"

BPM = 100
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920 ticks
NUM_SECTIONS = 8                            # 8 bars total

# SoundFont configuration
SOUNDFONT_PATH = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH_BIN = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# --------------------------------------------------------------- SCALE ------
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # Bb Major

def degree_to_pitch(degree, voice):
    """Calculates absolute pitches using the canonical diatonic scaling formula."""
    if voice == "Lead":
        base = 70  # Bb4 (tenor/soprano range for clarinet)
    elif voice == "Pad":
        base = 58  # Bb3
    else:  # Bass
        base = 46  # Bb2
        
    octave_shift = degree // 7
    interval_idx = degree % 7
    pitch = base + octave_shift * 12 + SCALE_INTERVALS[interval_idx]
    return max(12, min(127, pitch))

# ------------------------------------------------------------- PCFG CORE -----
class PCFGComposer:
    def __init__(self, rules, seed=46):
        self.rules = rules
        self.rng = np.random.default_rng(seed)

    def expand(self, symbol):
        """Recursively expands a symbol according to the PCFG rules."""
        if symbol not in self.rules:
            return [symbol]  # Terminal symbol
            
        productions = self.rules[symbol]
        patterns = [p[0] for p in productions]
        probs = [p[1] for p in productions]
        
        # Normalize probabilities
        probs = np.array(probs, dtype=float)
        probs /= probs.sum()
        
        idx = self.rng.choice(len(patterns), p=probs)
        chosen_pattern = patterns[idx]
        
        expanded = []
        for sym in chosen_pattern:
            expanded.extend(self.expand(sym))
        return expanded

# ------------------------------------------------------------- GRAMMAR -------
RULES = {
    # Lead sections
    "LEAD_BAR_I": [
        (["HALF_L_I1", "HALF_L_I2"], 0.7),
        (["HALF_L_I1", "HALF_L_I1"], 0.3)
    ],
    "LEAD_BAR_V": [
        (["HALF_L_V1", "HALF_L_V2"], 0.8),
        (["HALF_L_V2", "HALF_L_V1"], 0.2)
    ],
    "LEAD_BAR_VI": [
        (["HALF_L_VI1", "HALF_L_VI2"], 0.7),
        (["HALF_L_VI1", "HALF_L_VI1"], 0.3)
    ],
    "LEAD_BAR_IV": [
        (["HALF_L_IV1", "HALF_L_IV2"], 0.8),
        (["HALF_L_IV2", "HALF_L_IV1"], 0.2)
    ],

    # Pad sections (chords)
    "PAD_BAR_I": [
        (["c0-2-4_w"], 0.9),
        (["c0-2-4_h", "c0-2-4_h"], 0.1)
    ],
    "PAD_BAR_V": [
        (["c4-6-8_w"], 0.9),
        (["c4-6-8_h", "c4-6-8_h"], 0.1)
    ],
    "PAD_BAR_VI": [
        (["c5-7-9_w"], 0.9),
        (["c5-7-9_h", "c5-7-9_h"], 0.1)
    ],
    "PAD_BAR_IV": [
        (["c3-5-7_w"], 0.9),
        (["c3-5-7_h", "c3-5-7_h"], 0.1)
    ],

    # Bass sections
    "BASS_BAR_I": [
        (["n0_h", "n4_h"], 0.6),
        (["n0_q", "n2_q", "n4_q", "n2_q"], 0.4)
    ],
    "BASS_BAR_V": [
        (["n4_h", "n1_h"], 0.6),
        (["n4_q", "n5_q", "n6_q", "n5_q"], 0.4)
    ],
    "BASS_BAR_VI": [
        (["n5_h", "n2_h"], 0.6),
        (["n5_q", "n6_q", "n7_q", "n6_q"], 0.4)
    ],
    "BASS_BAR_IV": [
        (["n3_h", "n0_h"], 0.6),
        (["n3_q", "n4_q", "n5_q", "n4_q"], 0.4)
    ],

    # Lead Half-note expansions
    "HALF_L_I1": [
        (["QUARTER_L_I1", "QUARTER_L_I2"], 0.8),
        (["n0_h"], 0.2)
    ],
    "HALF_L_I2": [
        (["QUARTER_L_I2", "QUARTER_L_I3"], 0.7),
        (["n7_h"], 0.3)
    ],
    "HALF_L_V1": [
        (["QUARTER_L_V1", "QUARTER_L_V2"], 0.8),
        (["n4_h"], 0.2)
    ],
    "HALF_L_V2": [
        (["QUARTER_L_V2", "QUARTER_L_V3"], 0.7),
        (["n11_h"], 0.3)
    ],
    "HALF_L_VI1": [
        (["QUARTER_L_VI1", "QUARTER_L_VI2"], 0.8),
        (["n5_h"], 0.2)
    ],
    "HALF_L_VI2": [
        (["QUARTER_L_VI2", "QUARTER_L_VI3"], 0.7),
        (["n12_h"], 0.3)
    ],
    "HALF_L_IV1": [
        (["QUARTER_L_IV1", "QUARTER_L_IV2"], 0.8),
        (["n3_h"], 0.2)
    ],
    "HALF_L_IV2": [
        (["QUARTER_L_IV2", "QUARTER_L_IV3"], 0.7),
        (["n10_h"], 0.3)
    ],

    # Lead Quarter-note expansions
    "QUARTER_L_I1": [
        (["n0_q"], 0.5),
        (["n2_e", "n4_e"], 0.5)
    ],
    "QUARTER_L_I2": [
        (["n2_q"], 0.5),
        (["n4_e", "n7_e"], 0.5)
    ],
    "QUARTER_L_I3": [
        (["n7_q"], 0.6),
        (["n9_e", "n7_e"], 0.4)
    ],

    "QUARTER_L_V1": [
        (["n4_q"], 0.5),
        (["n6_e", "n8_e"], 0.5)
    ],
    "QUARTER_L_V2": [
        (["n6_q"], 0.5),
        (["n8_e", "n11_e"], 0.5)
    ],
    "QUARTER_L_V3": [
        (["n11_q"], 0.6),
        (["n13_e", "n11_e"], 0.4)
    ],

    "QUARTER_L_VI1": [
        (["n5_q"], 0.5),
        (["n7_e", "n9_e"], 0.5)
    ],
    "QUARTER_L_VI2": [
        (["n7_q"], 0.5),
        (["n9_e", "n12_e"], 0.5)
    ],
    "QUARTER_L_VI3": [
        (["n12_q"], 0.6),
        (["n14_e", "n12_e"], 0.4)
    ],

    "QUARTER_L_IV1": [
        (["n3_q"], 0.5),
        (["n5_e", "n7_e"], 0.5)
    ],
    "QUARTER_L_IV2": [
        (["n5_q"], 0.5),
        (["n7_e", "n10_e"], 0.5)
    ],
    "QUARTER_L_IV3": [
        (["n10_q"], 0.6),
        (["n12_e", "n10_e"], 0.4)
    ],
}

# Progression over 8 bars: I - V - vi - IV - I - V - vi - IV
CHORD_SEQUENCE = ["I", "V", "VI", "IV", "I", "V", "VI", "IV"]

# ------------------------------------------------------------- SYNTH SP-023 ---
def digital_waveguide_clarinet(freq, sr, duration, mouth_pressure=0.85, reed_slope=-0.35, reed_offset=0.65, bell_gain=0.97, lpf_coef=0.4, breath_noise=0.015):
    """Physical modeling woodwind clarinet synthesizer (Method SP-023)."""
    n_samples = int(sr * duration)
    if n_samples <= 0:
        return np.array([])
        
    # Calculate delay line length (round-trip for closed-open pipe is fs / (2 * f0))
    delay_samples = int(round(sr / (2.0 * freq)))
    if delay_samples < 2:
        delay_samples = 2
        
    # Initialize waveguides
    delay_line = np.zeros(delay_samples)
    delay_ptr = 0
    
    # One-pole filter state
    lpf_state = 0.0
    
    # Construct standard ADSR pressure envelope
    p_env = np.zeros(n_samples)
    attack_len = int(min(0.01 * sr, n_samples * 0.1))  # Rapid attack
    decay_len = int(min(0.02 * sr, n_samples * 0.1))
    
    p_env[:attack_len] = np.linspace(0, mouth_pressure, attack_len)
    p_env[attack_len:-decay_len] = mouth_pressure
    p_env[-decay_len:] = np.linspace(mouth_pressure, 0, decay_len)
            
    # Add breath noise scaled by pressure
    noise = np.random.normal(0, breath_noise, n_samples)
    p_mouth_noise = p_env + p_env * noise
    
    output = np.zeros(n_samples)
    prev_reflected = 0.0
    
    # Simulation loop
    for n in range(n_samples):
        # 1. Read returning wave from waveguide end
        p_back = delay_line[delay_ptr]
        
        # 2. Apply one-pole LPF modeling high-frequency damping
        lpf_state = lpf_coef * p_back + (1.0 - lpf_coef) * lpf_state
        
        # 3. Apply negative reflection at open bell
        p_reflected = -bell_gain * lpf_state
        
        # 4. Calculate reed junction interaction
        pm = p_mouth_noise[n]
        delta_p = pm - p_reflected
        
        # Reed table reflection coefficient (non-linear polynomial approximation)
        r_reed = reed_slope * delta_p + reed_offset
        r_reed = max(-1.0, min(1.0, r_reed))
        
        # Outgoing pressure wave entering the bore
        p_forward = p_reflected + delta_p * r_reed
        
        # 5. Push wave into delay line
        delay_line[delay_ptr] = p_forward
        delay_ptr = (delay_ptr + 1) % delay_samples
        
        # 6. Radiated output is first difference of bell reflection
        output[n] = p_reflected - prev_reflected
        prev_reflected = p_reflected
        
    # Remove DC offset and normalize
    output = output - np.mean(output)
    max_val = np.max(np.abs(output))
    if max_val > 0:
        output = output / max_val
        
    return output

def synthesize_lead_pcfg(collapsed_lead, sr=44100, bpm=100, ticks_per_beat=480):
    """Synthesizes the Lead track using Digital Waveguide Clarinet modeling."""
    seconds_per_tick = 60.0 / (bpm * ticks_per_beat)
    bar_ticks = ticks_per_beat * 4
    total_ticks = len(collapsed_lead) * bar_ticks
    total_samples = int(sr * total_ticks * seconds_per_tick)
    
    lead_audio = np.zeros(total_samples)
    
    duration_map = {'w': 1920, 'h': 960, 'q': 480, 'e': 240, 's': 120}
    
    for col, terminals in enumerate(collapsed_lead):
        col_start_tick = col * bar_ticks
        accum_ticks = 0
        
        for term in terminals:
            parts = term.split('_')
            if len(parts) != 2:
                continue
            token, dur_char = parts[0], parts[1]
            dur = duration_map.get(dur_char, 480)
            
            note_start_tick = col_start_tick + accum_ticks
            note_dur_ticks = dur
            
            if token.startswith('n'):
                degree = int(token[1:])
                pitch = degree_to_pitch(degree, "Lead")
                freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
                
                start_sec = note_start_tick * seconds_per_tick
                dur_sec = note_dur_ticks * seconds_per_tick
                
                note_audio = digital_waveguide_clarinet(freq, sr, dur_sec)
                note_audio = note_audio * 0.40  # Clarinet volume balance
                
                start_sample = int(start_sec * sr)
                n_samples_note = len(note_audio)
                
                if start_sample + n_samples_note > total_samples:
                    note_audio = note_audio[:total_samples - start_sample]
                    n_samples_note = len(note_audio)
                    
                lead_audio[start_sample : start_sample + n_samples_note] += note_audio
                
            accum_ticks += dur
            
    return lead_audio

# ------------------------------------------------------------- UTILS ---------
def terminal_list_to_unit(terminals, voice, volume=90) -> MusicUnit:
    """Translates PCFG terminal strings to a zero-drift MusicUnit."""
    duration_map = {'w': 1920, 'h': 960, 'q': 480, 'e': 240, 's': 120}
    
    events = []
    accumulated_ticks = 0
    
    for term in terminals:
        parts = term.split('_')
        if len(parts) != 2:
            continue
        token, dur_char = parts[0], parts[1]
        dur = duration_map.get(dur_char, 480)
        
        if token.startswith('n'):
            degree = int(token[1:])
            pitch = degree_to_pitch(degree, voice)
            events.append(MusicEvent(
                pitch=pitch,
                volume=volume,
                start_tick=accumulated_ticks,
                end_tick=accumulated_ticks + dur
            ))
        elif token.startswith('c'):
            degrees_str = token[1:]
            degrees = [int(x) for x in degrees_str.split('-')]
            for deg in degrees:
                pitch = degree_to_pitch(deg, voice)
                events.append(MusicEvent(
                    pitch=pitch,
                    volume=volume,
                    start_tick=accumulated_ticks,
                    end_tick=accumulated_ticks + dur
                ))
        elif token.startswith('r'):
            events.append(MusicEvent(
                pitch=0,
                volume=0,
                start_tick=accumulated_ticks,
                end_tick=accumulated_ticks + dur
            ))
        accumulated_ticks += dur
        
    # Strict padding safety check for 1920 ticks
    if accumulated_ticks < 1920:
        events.append(MusicEvent(
            pitch=0,
            volume=0,
            start_tick=accumulated_ticks,
            end_tick=1920
        ))
    elif accumulated_ticks > 1920:
        cropped_events = []
        for e in events:
            if e.start_tick < 1920:
                e.end_tick = min(e.end_tick, 1920)
                cropped_events.append(e)
        events = cropped_events
        
    return MusicUnit(events=events)

def build_composition_matrix(grid, mode="full") -> UnitMatrixComposer:
    """Configures and returns the UnitMatrixComposer with zero-drift tracks."""
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    section_names = [f"Bar{i}" for i in range(1, NUM_SECTIONS + 1)]
    
    if mode == "full":
        c.create_matrix(num_voices=3, num_sections=NUM_SECTIONS)
        c.add_voice("Lead", program=72, channel=0)
        c.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=1)
        c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
        
        for name in section_names:
            c.add_section(name, bars=1)
            
        for s in range(NUM_SECTIONS):
            c.fill_voice_section("Lead", section_names[s], terminal_list_to_unit(grid["Lead"][s], "Lead", volume=95))
            c.fill_voice_section("Pad", section_names[s], terminal_list_to_unit(grid["Pad"][s], "Pad", volume=75))
            c.fill_voice_section("Bass", section_names[s], terminal_list_to_unit(grid["Bass"][s], "Bass", volume=90))
            
    elif mode == "accomp_only":
        c.create_matrix(num_voices=2, num_sections=NUM_SECTIONS)
        c.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=1)
        c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
        
        for name in section_names:
            c.add_section(name, bars=1)
            
        for s in range(NUM_SECTIONS):
            c.fill_voice_section("Pad", section_names[s], terminal_list_to_unit(grid["Pad"][s], "Pad", volume=75))
            c.fill_voice_section("Bass", section_names[s], terminal_list_to_unit(grid["Bass"][s], "Bass", volume=90))
            
    return c

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
    
    print("--- STEP 1: PCFG Recursive Expansion ---")
    pcfg = PCFGComposer(RULES, seed=46)
    
    grid = {"Lead": [], "Pad": [], "Bass": []}
    
    for chord in CHORD_SEQUENCE:
        grid["Lead"].append(pcfg.expand(f"LEAD_BAR_{chord}"))
        grid["Pad"].append(pcfg.expand(f"PAD_BAR_{chord}"))
        grid["Bass"].append(pcfg.expand(f"BASS_BAR_{chord}"))
        
    print("Grammar successfully expanded down to terminals!")
    for bar in range(NUM_SECTIONS):
        print(f"Bar {bar+1} ({CHORD_SEQUENCE[bar]}):")
        print(f"  Lead: {' '.join(grid['Lead'][bar])}")
        print(f"  Pad : {' '.join(grid['Pad'][bar])}")
        print(f"  Bass: {' '.join(grid['Bass'][bar])}")
        
    print("\n--- STEP 2: Creating and Validating MIDI Files ---")
    
    # 1. Full Multi-track MIDI
    comp_full = build_composition_matrix(grid, mode="full")
    ok, msg = comp_full.validate()
    if not ok:
        raise SystemExit(f"Full composition validation failed (track drift): {msg}")
    midi_full_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}.mid"
    comp_full.to_midi(midi_full_path)
    print(f"Full MIDI saved: {midi_full_path} ({os.path.getsize(midi_full_path)} bytes)")
    
    # 2. Accompaniment-only MIDI
    comp_accomp = build_composition_matrix(grid, mode="accomp_only")
    ok, msg = comp_accomp.validate()
    if not ok:
        raise SystemExit(f"Accompaniment validation failed: {msg}")
    midi_accomp_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}_accomp_temp.mid"
    comp_accomp.to_midi(midi_accomp_path)
    
    print("\n--- STEP 3: Rendering Accompaniment with FluidSynth ---")
    wav_accomp_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_accomp_temp.wav"
    cmd_render = f"{FLUIDSYNTH_BIN} -ni -g 1.3 -F {wav_accomp_path} {SOUNDFONT_PATH} {midi_accomp_path} >/dev/null 2>&1"
    os.system(cmd_render)
    print(f"Accompaniment rendered: {wav_accomp_path}")
    
    print("\n--- STEP 4: Synthesizing Lead via Clarinet Waveguide Synthesis ---")
    sr = 44100
    lead_sig = synthesize_lead_pcfg(grid["Lead"], sr=sr, bpm=BPM, ticks_per_beat=TICKS_PER_BEAT)
    print(f"Clarinet physical model output synthesized: {len(lead_sig)} samples")
    
    print("\n--- STEP 5: Mixing and Mastering ---")
    accomp_sig, _ = read_wav(wav_accomp_path)
    
    # Pad or slice to match length
    max_len = max(len(lead_sig), len(accomp_sig))
    lead_padded = np.zeros(max_len, dtype=np.float32)
    lead_padded[:len(lead_sig)] = lead_sig
    
    if accomp_sig.ndim == 2:
        accomp_padded = np.zeros((max_len, 2), dtype=np.float32)
        accomp_padded[:len(accomp_sig), :] = accomp_sig
        mixed = np.zeros((max_len, 2), dtype=np.float32)
        mixed[:, 0] = lead_padded * 0.60 + accomp_padded[:, 0] * 0.70
        mixed[:, 1] = lead_padded * 0.60 + accomp_padded[:, 1] * 0.70
        num_channels = 2
    else:
        accomp_padded = np.zeros(max_len, dtype=np.float32)
        accomp_padded[:len(accomp_sig)] = accomp_sig
        mixed = lead_padded * 0.60 + accomp_padded * 0.70
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
            "methods": ["034", "SP-023"],
            "grid_voices": 3,
            "grid_sections": NUM_SECTIONS,
            "physical_model": "digital_waveguide_clarinet",
            "key": "Bb Major",
            "pcfg_seed": 46
        },
        notes="Composed via PCFG Recursion (Method 034) and synthesized via physical modeling woodwind clarinet (Method SP-023)."
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
