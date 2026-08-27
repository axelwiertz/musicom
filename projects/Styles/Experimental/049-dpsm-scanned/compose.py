# -*- coding: utf-8 -*-
"""Composition entry point — musicom engine only.
Generates an 8-bar piece using Deconstructive Phase-Shift Minimalism (Method 026)
and renders the main voices using the Scanned Synthesis Engine (Method SP-018).
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
PROJECT_ID = "049"
PROJECT_NAME = f"{PROJECT_ID}-dpsm-scanned"
PROJECT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"

BPM = 110
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920 ticks
NUM_SECTIONS = 8                            # 8 bars total

# SoundFont configuration (for Bass rendering via FluidSynth)
SOUNDFONT_PATH = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH_BIN = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# Scale: C Dorian (C4 to Bb5)
PITCH_MAP = [60, 62, 63, 65, 67, 69, 70, 72, 74, 75, 77, 79]

# Core 16-step sixteenth-note pattern for DPSM (unison state)
# Index references into PITCH_MAP
CORE_PITCHES = [0, 2, 3, 5, 7, 5, 3, 2, 7, 9, 10, 7, 5, 3, 2, 0]
CORE_TRIGGERS = [1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1]

# Bass root notes for the 8 sections (1 bar per section)
BASS_ROOTS = [36, 39, 41, 43, 36, 39, 34, 36]  # C2, Eb2, F2, G2, C2, Eb2, Bb1, C2

# --------------------------------------------------------- SCANNED SYNTHESIS -
def generate_scanned_synthesis(duration, sr, f_fund, num_masses=64, k_s=1.5, k_c=0.1, d_s=0.05, f_control=100.0, amplitude=0.5):
    """Generates a dynamic physical-modeling waveform using Scanned Synthesis."""
    num_samples = int(sr * duration)
    output = np.zeros(num_samples, dtype=np.float32)
    
    # Initialize physical model states (displacements and velocities)
    x = np.zeros(num_masses, dtype=np.float32)
    mid = num_masses // 2
    for i in range(num_masses):
        if i < mid:
            x[i] = i / mid
        else:
            x[i] = (num_masses - i) / (num_masses - mid)
            
    v = np.zeros(num_masses, dtype=np.float32)
    dt_control = 1.0 / f_control
    samples_per_control = int(sr / f_control)
    if samples_per_control < 1:
        samples_per_control = 1
        
    phase = 0.0
    phase_step = f_fund / sr
    
    sample_idx = 0
    while sample_idx < num_samples:
        # Update physical model (slow-rate step)
        x_left = np.roll(x, 1)
        x_right = np.roll(x, -1)
        
        a = k_s * (x_left - 2.0 * x + x_right) - k_c * x - d_s * v
        v += a * dt_control
        x += v * dt_control
        
        # Audio rendering for this control frame
        for _ in range(samples_per_control):
            if sample_idx >= num_samples:
                break
                
            scan_idx = phase * num_masses
            idx_low = int(np.floor(scan_idx))
            idx_high = (idx_low + 1) % num_masses
            alpha = scan_idx - idx_low
            
            val = (1.0 - alpha) * x[idx_low] + alpha * x[idx_high]
            output[sample_idx] = val * amplitude
            
            phase = (phase + phase_step) % 1.0
            sample_idx += 1
            
    return output

def apply_envelope(signal, sr, attack_time=0.010, release_time=0.030):
    """Applies a smooth envelope with short attack and release to avoid clicks."""
    n = len(signal)
    env = np.ones(n, dtype=np.float32)
    
    attack_samples = min(int(attack_time * sr), n)
    release_samples = min(int(release_time * sr), n)
    
    if attack_samples > 0:
        env[:attack_samples] = np.linspace(0.0, 1.0, attack_samples)
    if release_samples > 0:
        env[-release_samples:] = np.linspace(1.0, 0.0, release_samples)
        
    return signal * env

def render_events_scanned(events, duration_sec, sr=44100):
    """Renders a list of MusicEvent objects into a continuous float32 audio signal using Scanned Synthesis."""
    total_samples = int(duration_sec * sr)
    track_audio = np.zeros(total_samples, dtype=np.float32)
    
    ticks_to_sec = duration_sec / (NUM_SECTIONS * BAR_TICKS)
    
    for event in events:
        if event.pitch > 0 and event.volume > 0:
            f_fund = 440.0 * (2.0 ** ((event.pitch - 69) / 12.0))
            start_time = event.start_tick * ticks_to_sec
            end_time = event.end_tick * ticks_to_sec
            
            note_dur = end_time - start_time
            if note_dur <= 0:
                continue
                
            # Generate the note
            note_sig = generate_scanned_synthesis(
                duration=note_dur,
                sr=sr,
                f_fund=f_fund,
                num_masses=64,
                k_s=1.5,
                k_c=0.1,
                d_s=0.05,
                f_control=120.0,
                amplitude=0.3
            )
            note_sig = apply_envelope(note_sig, sr)
            
            # Sum into track
            start_idx = int(start_time * sr)
            end_idx = start_idx + len(note_sig)
            if end_idx > total_samples:
                note_sig = note_sig[:total_samples - start_idx]
                end_idx = total_samples
                
            track_audio[start_idx:end_idx] += note_sig * (event.volume / 127.0)
            
    return track_audio

# ------------------------------------------------------------- COMPOSER MATRIX --
def build_music_matrix(single_voice_filter=None) -> UnitMatrixComposer:
    """Configures UnitMatrixComposer with DPSM-derived phasing.
    
    Voice 1: Piano1 (Static Phase)
    Voice 2: Piano2 (Shifting Phase)
    Voice 3: Bass (Solid Chord Roots)
    """
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    section_names = [f"Bar{i}" for i in range(1, NUM_SECTIONS + 1)]
    
    # Filter voices
    all_voices = ["Piano1", "Piano2", "Bass"]
    active_voices = [single_voice_filter] if single_voice_filter else all_voices
    
    c.create_matrix(num_voices=len(active_voices), num_sections=NUM_SECTIONS)
    
    voice_configs = {
        "Piano1": {"program": 0, "channel": 0},
        "Piano2": {"program": 0, "channel": 1},
        "Bass": {"program": 32, "channel": 2}
    }
    
    for v_name in active_voices:
        cfg = voice_configs[v_name]
        c.add_voice(v_name, program=cfg["program"], channel=cfg["channel"])
        
    for name in section_names:
        c.add_section(name, bars=1)
        
    step_ticks = 120  # sixteenth note = 120 ticks
    
    for s in range(NUM_SECTIONS):
        sec_name = section_names[s]
        
        # Voice 1: Piano1 (Static loop)
        if "Piano1" in active_voices:
            events_1 = []
            for step in range(16):
                if CORE_TRIGGERS[step] == 1:
                    pitch_idx = CORE_PITCHES[step]
                    pitch = PITCH_MAP[pitch_idx % len(PITCH_MAP)] + (pitch_idx // len(PITCH_MAP)) * 12
                    events_1.append(MusicEvent(
                        pitch=pitch,
                        volume=90,
                        start_tick=step * step_ticks,
                        end_tick=step * step_ticks + 100
                    ))
            # Zero-drift padding
            if not events_1 or events_1[-1].end_tick < BAR_TICKS:
                events_1.append(MusicEvent(pitch=0, volume=0, start_tick=BAR_TICKS - 1, end_tick=BAR_TICKS))
            c.fill_voice_section("Piano1", sec_name, MusicUnit(events=events_1))
            
        # Voice 2: Piano2 (Shifting loop)
        # Shift increases by 1 step (120 ticks) for each section
        if "Piano2" in active_voices:
            events_2 = []
            phase_shift = s  # 0 to 7 steps shift
            for step in range(16):
                shifted_step = (step + phase_shift) % 16
                if CORE_TRIGGERS[shifted_step] == 1:
                    pitch_idx = CORE_PITCHES[shifted_step]
                    pitch = PITCH_MAP[pitch_idx % len(PITCH_MAP)] + (pitch_idx // len(PITCH_MAP)) * 12
                    events_2.append(MusicEvent(
                        pitch=pitch,
                        volume=90,
                        start_tick=step * step_ticks,
                        end_tick=step * step_ticks + 100
                    ))
            # Zero-drift padding
            if not events_2 or events_2[-1].end_tick < BAR_TICKS:
                events_2.append(MusicEvent(pitch=0, volume=0, start_tick=BAR_TICKS - 1, end_tick=BAR_TICKS))
            c.fill_voice_section("Piano2", sec_name, MusicUnit(events=events_2))
            
        # Voice 3: Bass (Solid roots, holding)
        if "Bass" in active_voices:
            bass_pitch = BASS_ROOTS[s]
            events_bass = [
                MusicEvent(pitch=bass_pitch, volume=95, start_tick=0, end_tick=1440),
                MusicEvent(pitch=bass_pitch + 7, volume=80, start_tick=1440, end_tick=1920)  # Fifth pop
            ]
            c.fill_voice_section("Bass", sec_name, MusicUnit(events=events_bass))
            
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
    print("--- START COMPOSITION PIPELINE ---")
    
    # 1. Full Multi-track MIDI
    comp_full = build_music_matrix()
    ok, msg = comp_full.validate()
    if not ok:
        raise SystemExit(f"Full composition validation failed: {msg}")
        
    midi_full_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}.mid"
    comp_full.to_midi(midi_full_path)
    midi_size = os.path.getsize(midi_full_path)
    print(f"Full MIDI saved: {midi_full_path} ({midi_size} bytes)")
    
    if midi_size <= 40:
        raise SystemExit("Error: MIDI empty or corrupt!")
        
    # Total duration in seconds: 8 bars, each bar is 4 beats, each beat is 60/110 seconds
    beat_duration = 60.0 / BPM
    bar_duration = 4.0 * beat_duration
    total_duration = NUM_SECTIONS * bar_duration
    
    sr = 44100
    total_samples = int(total_duration * sr)
    
    print("\n--- STEP 1: Rendering Lead & Shifting Pianos via Scanned Synthesis (SP-018) ---")
    
    # Retrieve absolute events directly from the full composer matrix!
    # Row 0: Piano1, Row 1: Piano2, Row 2: Bass
    p1_events = comp_full.matrix.get_row_events(0)
    p2_events = comp_full.matrix.get_row_events(1)
    
    print(f"Synthesizing Piano 1 (Static) - {len(p1_events)} events...")
    audio_p1 = render_events_scanned(p1_events, total_duration, sr)
    
    print(f"Synthesizing Piano 2 (Shifting) - {len(p2_events)} events...")
    audio_p2 = render_events_scanned(p2_events, total_duration, sr)
    
    print("\n--- STEP 2: Rendering Bass via FluidSynth CLI ---")
    comp_bass = build_music_matrix(single_voice_filter="Bass")
    ok, msg = comp_bass.validate()
    if not ok:
        raise SystemExit(f"Bass track validation failed: {msg}")
        
    temp_bass_midi = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}_bass_temp.mid"
    temp_bass_wav = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_bass_temp.wav"
    comp_bass.to_midi(temp_bass_midi)
    
    cmd_render = f"{FLUIDSYNTH_BIN} -ni -g 1.4 -F {temp_bass_wav} {SOUNDFONT_PATH} {temp_bass_midi} >/dev/null 2>&1"
    os.system(cmd_render)
    
    # Read the Bass WAV
    audio_bass, bass_sr = read_wav(temp_bass_wav)
    if audio_bass.ndim == 2:
        audio_bass = (audio_bass[:, 0] + audio_bass[:, 1]) / 2.0
        
    # Match length of Bass to Scanned Synthesis arrays
    audio_bass_padded = np.zeros(total_samples, dtype=np.float32)
    min_len = min(len(audio_bass), total_samples)
    audio_bass_padded[:min_len] = audio_bass[:min_len]
    
    print("\n--- STEP 3: Mixing and Spatial Placement ---")
    # Panning: Piano 1 left, Piano 2 right, Bass center
    # Create stereo signal
    master_stereo = np.zeros((total_samples, 2), dtype=np.float32)
    
    # Piano 1 (Static) - 75% Left, 25% Right
    master_stereo[:, 0] += audio_p1 * 0.75
    master_stereo[:, 1] += audio_p1 * 0.25
    
    # Piano 2 (Shifting) - 25% Left, 75% Right
    master_stereo[:, 0] += audio_p2 * 0.25
    master_stereo[:, 1] += audio_p2 * 0.75
    
    # Bass - 50% Left, 50% Right
    master_stereo[:, 0] += audio_bass_padded * 0.50
    master_stereo[:, 1] += audio_bass_padded * 0.50
    
    # Master peak normalization to -1dB
    peak = np.max(np.abs(master_stereo))
    if peak > 0:
        master_stereo = master_stereo * (0.89 / peak)
        
    mixed_wav_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_temp_mix.wav"
    write_wav(mixed_wav_path, master_stereo, num_channels=2, sample_rate=sr)
    
    print("\n--- STEP 4: Compressing to Opus OGG ---")
    ogg_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}.ogg"
    cmd_ffmpeg = f"ffmpeg -i {mixed_wav_path} -codec:a libopus -application voip -b:a 48k {ogg_path} -y -loglevel error"
    os.system(cmd_ffmpeg)
    
    ogg_size = os.path.getsize(ogg_path)
    print(f"Dual artifacts generated:")
    print(f"  - MIDI: {midi_full_path} ({midi_size} bytes)")
    print(f"  - OGG:  {ogg_path} ({ogg_size} bytes)")
    
    if ogg_size <= 40:
        raise SystemExit("Error: OGG rendering failed or empty!")
        
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
            "methods": ["026", "SP-018"],
            "grid_voices": 3,
            "grid_sections": NUM_SECTIONS,
            "key": "C Dorian",
            "num_masses": 64,
            "scanned_tension": 1.5
        },
        notes="Composed via Deconstructive Phase-Shift Minimalism (Method 026) and rendered via Scanned Synthesis Engine (Method SP-018)."
    )
    
    # Cleanup temporary files
    for path in [temp_bass_midi, temp_bass_wav, mixed_wav_path]:
        if os.path.exists(path):
            os.remove(path)
            
    print("Temporary files cleaned up.")
    print("SUCCESS: 049-dpsm-scanned pipeline finished successfully!")

if __name__ == "__main__":
    main()
