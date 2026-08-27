# -*- coding: utf-8 -*-
"""Composition entry point — musicom engine only.
Generates an isorhythmic composition and spatializes the lead voice via SP-021.
"""
import os
import wave
import sys
import numpy as np

# Ensure clean imports from the installed musicom package
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# ---------------------------------------------------------------- CONFIG -----
PROJECT_ID = "044"
PROJECT_NAME = f"{PROJECT_ID}-isorhythmic-spatial"
PROJECT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"

BPM = 100
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR
BARS_PER_SECTION = 4
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION  # 1920 * 4 = 7680 ticks

# SoundFont configuration
SOUNDFONT_PATH = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH_BIN = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# ---------------------------------------------------------------- ITCM ENGINE -----
# Method 032: Isorhythmic Talea-Color Mapping (ITCM)

def generate_isorhythm_events(talea_durations, color_pitches, total_ticks):
    """
    Generates a list of (pitch, duration) tuples using Isorhythmic Talea-Color Mapping.
    If pitch is a list/tuple, it returns a chord event.
    """
    events = []
    accumulated_ticks = 0
    
    talea_len = len(talea_durations)
    color_len = len(color_pitches)
    
    talea_idx = 0
    color_idx = 0
    
    while accumulated_ticks < total_ticks:
        dur = talea_durations[talea_idx % talea_len]
        pitch = color_pitches[color_idx % color_len]
        
        # Check if duration exceeds the remaining ticks
        if accumulated_ticks + dur > total_ticks:
            dur = total_ticks - accumulated_ticks
            
        if dur > 0:
            events.append((pitch, dur))
            accumulated_ticks += dur
            
        talea_idx += 1
        # Only advance color index if pitch is not empty/rest (0 or None)
        if pitch is not None:
            if isinstance(pitch, (list, tuple)):
                if len(pitch) > 0 and pitch[0] > 0:
                    color_idx += 1
            elif pitch > 0:
                color_idx += 1
            else:
                color_idx += 1  # Standard rest behavior, advance color
        else:
            color_idx += 1
            
    return events


def build_music_unit(events, total_ticks=SECTION_TICKS, volume=90) -> MusicUnit:
    """Converts (pitch, duration) tuples from ITCM into a zero-drift MusicUnit."""
    unit_events = []
    accumulated_ticks = 0
    
    for pitch, dur in events:
        if pitch is not None:
            if isinstance(pitch, (list, tuple)):
                # Chord
                for p in pitch:
                    unit_events.append(MusicEvent(
                        pitch=p if p > 0 else 0,
                        volume=volume if p > 0 else 0,
                        start_tick=accumulated_ticks,
                        end_tick=accumulated_ticks + dur
                    ))
            elif pitch > 0:
                # Single note
                unit_events.append(MusicEvent(
                    pitch=pitch,
                    volume=volume,
                    start_tick=accumulated_ticks,
                    end_tick=accumulated_ticks + dur
                ))
            else:
                # Rest note (pitch == 0 or negative)
                unit_events.append(MusicEvent(
                    pitch=0,
                    volume=0,
                    start_tick=accumulated_ticks,
                    end_tick=accumulated_ticks + dur
                ))
        else:
            # Silent event
            unit_events.append(MusicEvent(
                pitch=0,
                volume=0,
                start_tick=accumulated_ticks,
                end_tick=accumulated_ticks + dur
            ))
        accumulated_ticks += dur
        
    # Enforce exact total section ticks boundary alignment via silent pad tail
    if accumulated_ticks < total_ticks:
        unit_events.append(MusicEvent(
            pitch=0,
            volume=0,
            start_tick=accumulated_ticks,
            end_tick=total_ticks
        ))
        
    return MusicUnit(events=unit_events)


# ---------------------------------------------------------------- SP-021 DSP -----
# Method SP-021: Binaural Woodworth-Schlosberg Spatialization

def first_order_lowpass(x, fc, fs):
    """Applies first-order lowpass filter to x with cutoff fc (array or scalar)."""
    n_samples = len(x)
    y = np.zeros(n_samples)
    
    if np.isscalar(fc):
        fc_arr = np.full(n_samples, fc)
    else:
        fc_arr = np.asarray(fc)
        
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
    y = np.zeros(n_samples)
    
    if np.isscalar(delay_samples):
        d_arr = np.full(n_samples, delay_samples)
    else:
        d_arr = np.asarray(delay_samples)
        
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
    """Applies Binaural Woodworth-Schlosberg Spatialization to a monophonic input signal."""
    n_samples = len(x)
    
    ref_distance = 1.0
    attn = ref_distance / max(distance, ref_distance)
    x_attn = x * attn
    
    if np.isscalar(azimuth):
        az_arr = np.full(n_samples, azimuth)
    else:
        az_arr = np.asarray(azimuth)
        
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


# ---------------------------------------------------------------- AUDIO I/O -----

def read_wav(path) -> tuple[np.ndarray, int]:
    """Reads a WAV file and returns float32 samples and sampling rate."""
    with wave.open(path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        fs = wf.getframerate()
        n_frames = wf.getnframes()
        
        data = wf.readframes(n_frames)
        if sampwidth == 2:
            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        elif sampwidth == 1:
            samples = (np.frombuffer(data, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        else:
            raise ValueError("Unsupported sample width")
            
        if n_channels == 2:
            samples = samples.reshape(-1, 2)
            
        return samples, fs


def write_wav(path, samples, fs):
    """Writes float32 stereo/mono samples to a 16-bit PCM WAV file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as wf:
        n_channels = 2 if samples.ndim == 2 else 1
        wf.setnchannels(n_channels)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        
        clipped = np.clip(samples, -1.0, 1.0)
        ints = (clipped * 32767.0).astype(np.int16)
        wf.writeframes(ints.tobytes())


# ---------------------------------------------------------------- COMPOSITION MATRIX -----

def build_composition(mode="full") -> UnitMatrixComposer:
    """Builds the UnitMatrixComposer for the chosen track combination.
    mode can be "full", "lead_only", or "accomp_only".
    """
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    
    # 4 Voices (Rows)
    c.create_matrix(num_voices=4, num_sections=4)
    c.add_voice("Lead", program=MidiInstrument.VIOLIN, channel=0)
    c.add_voice("Bass", program=MidiInstrument.BASS, channel=1)
    c.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=2)
    c.add_voice("Drums", program=0, channel=9)
    
    # 4 Sections (Columns)
    c.add_section("Intro", bars=BARS_PER_SECTION)
    c.add_section("A_Talea", bars=BARS_PER_SECTION)
    c.add_section("B_Shift", bars=BARS_PER_SECTION)
    c.add_section("Outro", bars=BARS_PER_SECTION)
    
    # --- DNA definition (Coprime loops) ---
    
    # Lead: Talea (9 elements) x Color (7 elements). Coprime!
    lead_talea = [480, 240, 240, 480, 480, 960, 480, 240, 480]
    lead_color_a = [62, 65, 64, 67, 69, 72, 74] # D Dorian
    # Section B: Retrograde Talea & Inverted Color around G4 (67)
    lead_talea_b = lead_talea[::-1]
    lead_color_b = [72, 69, 70, 67, 65, 62, 60]
    
    # Bass: Talea (5 elements) x Color (4 elements). Coprime!
    bass_talea = [960, 480, 480, 960, 960]
    bass_color_a = [38, 41, 45, 43] # Octave 3 D, F, A, G
    bass_color_b = [45, 43, 41, 38]
    
    # Pad: Talea (3 elements) x Color (5 chords). Coprime!
    pad_talea = [1920, 1920, 1920]
    pad_color = [
        [50, 53, 57],  # Dm
        [53, 57, 60],  # F
        [55, 59, 62],  # G
        [57, 60, 64],  # Am
        [48, 52, 55]   # C
    ]
    
    # Drums: Talea (6 elements) x Color (5 elements). Coprime!
    drums_talea = [240, 240, 480, 240, 240, 480]
    drums_color = [
        MidiPercussion.BASS_DRUM,
        MidiPercussion.CLOSED_HI_HAT,
        MidiPercussion.CLOSED_HI_HAT,
        MidiPercussion.ACOUSTIC_SNARE,
        MidiPercussion.CLOSED_HI_HAT
    ]
    
    # --- Fill Cells based on Mode and Section ---
    sections = ["Intro", "A_Talea", "B_Shift", "Outro"]
    
    for s in sections:
        # 1. Lead voice
        if mode in ("full", "lead_only"):
            events = []
            if s == "Intro":
                # Sparsely intro
                events = generate_isorhythm_events([960], [0, 62, 0, 65], SECTION_TICKS)
            elif s == "A_Talea":
                events = generate_isorhythm_events(lead_talea, lead_color_a, SECTION_TICKS)
            elif s == "B_Shift":
                events = generate_isorhythm_events(lead_talea_b, lead_color_b, SECTION_TICKS)
            elif s == "Outro":
                # Sparsely fade out
                events = generate_isorhythm_events([960], [62, 0, 0, 0], SECTION_TICKS)
            c.fill_voice_section("Lead", s, build_music_unit(events, total_ticks=SECTION_TICKS, volume=90))
        else:
            # Silent
            c.fill_voice_section("Lead", s, create_empty_unit(SECTION_TICKS))
            
        # 2. Bass voice
        if mode in ("full", "accomp_only"):
            events = []
            if s in ("Intro", "A_Talea"):
                events = generate_isorhythm_events(bass_talea, bass_color_a, SECTION_TICKS)
            elif s == "B_Shift":
                events = generate_isorhythm_events(bass_talea, bass_color_b, SECTION_TICKS)
            elif s == "Outro":
                events = generate_isorhythm_events([960], [38, 0, 38, 0], SECTION_TICKS)
            c.fill_voice_section("Bass", s, build_music_unit(events, total_ticks=SECTION_TICKS, volume=100))
        else:
            c.fill_voice_section("Bass", s, create_empty_unit(SECTION_TICKS))
            
        # 3. Pad voice
        if mode in ("full", "accomp_only"):
            events = []
            if s in ("Intro", "A_Talea", "B_Shift"):
                events = generate_isorhythm_events(pad_talea, pad_color, SECTION_TICKS)
            elif s == "Outro":
                events = generate_isorhythm_events([1920], [[50, 53, 57], 0, [50, 53, 57], 0], SECTION_TICKS)
            c.fill_voice_section("Pad", s, build_music_unit(events, total_ticks=SECTION_TICKS, volume=75))
        else:
            c.fill_voice_section("Pad", s, create_empty_unit(SECTION_TICKS))
            
        # 4. Drums voice
        if mode in ("full", "accomp_only"):
            events = []
            if s == "Intro":
                # No drums in Intro
                c.fill_voice_section("Drums", s, create_empty_unit(SECTION_TICKS))
            elif s in ("A_Talea", "B_Shift"):
                events = generate_isorhythm_events(drums_talea, drums_color, SECTION_TICKS)
                c.fill_voice_section("Drums", s, build_music_unit(events, total_ticks=SECTION_TICKS, volume=80))
            elif s == "Outro":
                # Sparse outro hi-hats
                events = generate_isorhythm_events([480], [MidiPercussion.CLOSED_HI_HAT, 0], SECTION_TICKS)
                c.fill_voice_section("Drums", s, build_music_unit(events, total_ticks=SECTION_TICKS, volume=70))
        else:
            c.fill_voice_section("Drums", s, create_empty_unit(SECTION_TICKS))
            
    return c


# ---------------------------------------------------------------- MAIN -----

def main():
    # Make sure output directories exist
    os.makedirs(f"{PROJECT_DIR}/MIDI", exist_ok=True)
    os.makedirs(f"{PROJECT_DIR}/Audio", exist_ok=True)
    os.makedirs(f"{PROJECT_DIR}/Analysis", exist_ok=True)
    
    print("--- STEP 1: Building and Validating MIDI Files ---")
    
    # 1. Build Full Composition MIDI
    comp_full = build_composition(mode="full")
    ok, msg = comp_full.validate()
    if not ok:
        raise SystemExit(f"Full composition validation failed (track drift): {msg}")
    midi_full_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}.mid"
    comp_full.to_midi(midi_full_path)
    print(f"Full MIDI saved: {midi_full_path} ({os.path.getsize(midi_full_path)} bytes)")
    
    # 2. Build Lead-only MIDI (for spatialization)
    comp_lead = build_composition(mode="lead_only")
    ok, msg = comp_lead.validate()
    if not ok:
        raise SystemExit(f"Lead composition validation failed: {msg}")
    midi_lead_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}_lead_temp.mid"
    comp_lead.to_midi(midi_lead_path)
    
    # 3. Build Accompaniment-only MIDI
    comp_accomp = build_composition(mode="accomp_only")
    ok, msg = comp_accomp.validate()
    if not ok:
        raise SystemExit(f"Accompaniment composition validation failed: {msg}")
    midi_accomp_path = f"{PROJECT_DIR}/MIDI/{PROJECT_NAME}_accomp_temp.mid"
    comp_accomp.to_midi(midi_accomp_path)
    
    print("--- STEP 2: Rendering MIDI tracks via FluidSynth ---")
    
    wav_lead_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_lead_temp.wav"
    wav_accomp_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_accomp_temp.wav"
    
    # Render Lead track
    os.system(f"{FLUIDSYNTH_BIN} -ni -g 1.5 -F {wav_lead_path} {SOUNDFONT_PATH} {midi_lead_path} >/dev/null 2>&1")
    # Render Accompaniment track
    os.system(f"{FLUIDSYNTH_BIN} -ni -g 1.2 -F {wav_accomp_path} {SOUNDFONT_PATH} {midi_accomp_path} >/dev/null 2>&1")
    
    print("--- STEP 3: Applying SP-021 Binaural Spatialization ---")
    
    # Load wavs
    lead_sig, fs = read_wav(wav_lead_path)
    accomp_sig, _ = read_wav(wav_accomp_path)
    
    # Convert lead signal to mono for spatialization (if it's stereo)
    if lead_sig.ndim == 2:
        lead_sig_mono = 0.5 * (lead_sig[:, 0] + lead_sig[:, 1])
    else:
        lead_sig_mono = lead_sig
        
    n_samples = len(lead_sig_mono)
    t = np.arange(n_samples) / float(fs)
    
    # Define a dynamic orbiting azimuth angle (one complete 360-degree rotation every 8 seconds)
    # azimuth = 2 * pi * f * t
    orbit_freq = 0.125  # 1 / 8 seconds
    azimuth_angle = 2 * np.pi * orbit_freq * t
    
    # Apply binaural spatialization
    spatialized_lead = binaural_spatialization(lead_sig_mono, fs, azimuth_angle, distance=1.2)
    
    # Standardize length of lead and accompaniment
    max_len = max(len(spatialized_lead), len(accomp_sig))
    
    if len(spatialized_lead) < max_len:
        spatialized_lead = np.pad(spatialized_lead, ((0, max_len - len(spatialized_lead)), (0, 0)))
    if len(accomp_sig) < max_len:
        if accomp_sig.ndim == 2:
            accomp_sig = np.pad(accomp_sig, ((0, max_len - len(accomp_sig)), (0, 0)))
        else:
            accomp_sig = np.pad(accomp_sig, (0, max_len - len(accomp_sig)))
            accomp_sig = np.column_stack((accomp_sig, accomp_sig))
            
    # Mix spatialized lead with centered accompaniment
    mixed_sig = spatialized_lead + accomp_sig
    
    # Peak normalization to -1dB (amplitude 0.89)
    peak = np.max(np.abs(mixed_sig))
    if peak > 0:
        mixed_sig = mixed_sig * (0.89 / peak)
        
    wav_mixed_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}_mixed_temp.wav"
    write_wav(wav_mixed_path, mixed_sig, fs)
    print(f"Mixed WAV written: {wav_mixed_path}")
    
    print("--- STEP 4: Compressing mixed WAV to OGG ---")
    ogg_path = f"{PROJECT_DIR}/Audio/{PROJECT_NAME}.ogg"
    
    # FFmpeg compression to OGG (Opus)
    ffmpeg_cmd = f"ffmpeg -i {wav_mixed_path} -codec:a libopus -application voip -b:a 48k {ogg_path} -y -loglevel error"
    os.system(ffmpeg_cmd)
    
    print("--- STEP 5: Creating visual assets and sidecar files ---")
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
            "methods": ["032", "SP-021"],
            "lead_talea_len": 9,
            "lead_color_len": 7,
            "bass_talea_len": 5,
            "bass_color_len": 4,
            "drums_talea_len": 6,
            "drums_color_len": 5,
        },
        notes="Composed via Isorhythmic Talea-Color Mapping (ITCM) and spatialized via Binaural Woodworth-Schlosberg Spatialization."
    )
    
    # --- CLEANUP ---
    # Delete temporary MIDI and WAV files
    temp_files = [midi_lead_path, midi_accomp_path, wav_lead_path, wav_accomp_path, wav_mixed_path]
    for tf in temp_files:
        if os.path.exists(tf):
            os.remove(tf)
            
    print("Cleanup complete. Temp files removed.")
    print(f"Final output .mid size: {os.path.getsize(midi_full_path)} bytes")
    print(f"Final output .ogg size: {os.path.getsize(ogg_path)} bytes")
    print("Project successfully created!")

if __name__ == "__main__":
    main()
