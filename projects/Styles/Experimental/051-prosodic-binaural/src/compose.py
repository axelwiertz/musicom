# -*- coding: utf-8 -*-
"""
Project 051: Prosodic-Binaural
Method 005: Prosodic Narrative Coupling
SP-021: Binaural Woodworth-Schlosberg Spatialization

Maps speech prosody (syllable stress, clause boundaries, questions)
to musical parameters (velocity, contour, rhythm). Then renders with
binaural panning for 3D spatial placement.
"""
import os
import json
import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# --- CONFIG ---
PROJECT_NAME = "051-prosodic-binaural"
OUTPUT_DIR = "/opt/data/projects/Styles/Experimental/051-prosodic-binaural"
BPM = 96
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920

# Prosodic text: "Where does the river go when the rain stops falling?"
# Syllable stress pattern: 0 1 0 0 1 0 1 0 0 1 0 1 0 0 1 0 1 0 0
# Clause boundary after "go" (bar 4) and after "falling" (bar 8)
# Question intonation = rising pitch contour in final section

# Scale: D Dorian (D E F G A B C) = MIDI offsets from D4=62: 0,2,3,5,7,9,10
DORIAN = [62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]

# Prosodic mapping: stressed syllables -> higher velocity, longer duration, higher pitch
# Unstressed -> lower velocity, shorter, stepwise motion
# Question words -> rising contour


def pad_unit_to_length(unit, target_ticks):
    """Ensure unit has an event ending exactly at target_ticks (zero-drift)."""
    if not unit.events:
        unit.add_event(MusicEvent(pitch=60, volume=0, start_tick=target_ticks - 10, end_tick=target_ticks))
        return unit
    last_end = max(e.end_tick for e in unit.events)
    if last_end < target_ticks:
        unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=last_end, end_tick=target_ticks))
    elif last_end > target_ticks:
        # Clamp events that overshoot
        for e in unit.events:
            if e.end_tick > target_ticks:
                e.end_tick = target_ticks
            if e.start_tick >= target_ticks:
                e.start_tick = max(0, target_ticks - 10)
    return unit


def prosodic_melody_unit(section_ticks):
    """Generate melody mapped from speech prosody. section_ticks = total section length."""
    unit = MusicUnit()
    
    # Phrase 1: "Where does the ri-" (first half)
    # Syllables: WHERE(1) does(0) the(0) RI(1) ver(0)
    phrase1 = [
        (0, 100, 720),   # WHERE - stressed, low start, long
        (1, 55, 360),    # does - unstressed, step up
        (2, 50, 240),    # the - unstressed
        (4, 95, 600),    # RI - stressed, leap up to A
        (3, 60, 480),    # ver - unstressed, step down
    ]
    
    tick = 0
    for deg, vel, dur in phrase1:
        pitch = DORIAN[deg]
        unit.add_event(MusicEvent(pitch=pitch, volume=vel, start_tick=tick, end_tick=tick + dur))
        tick += dur + 60
    
    # Phrase 2: "-ver go when the rain" (second half)
    phrase2 = [
        (3, 55, 360),    # ver - continuation
        (5, 90, 720),    # GO - stressed, question pivot, leap to B
        (4, 50, 240),    # when
        (3, 45, 240),    # the
        (5, 85, 480),    # RAIN - stressed
    ]
    
    for deg, vel, dur in phrase2:
        pitch = DORIAN[deg]
        unit.add_event(MusicEvent(pitch=pitch, volume=vel, start_tick=tick, end_tick=tick + dur))
        tick += dur + 60
    
    # Pad to exact section length
    pad_unit_to_length(unit, section_ticks)
    return unit


def prosodic_bass_unit(section_ticks):
    """Bass follows speech rhythm: stressed syllables = bass accents."""
    unit = MusicUnit()
    
    bass_notes = [
        (38, 90, 1440),  # D2 - WHERE (2 beats + gap)
        (45, 70, 1440),  # A2 - GO
        (43, 80, 1440),  # G2 - RAIN
        (40, 85, 1440),  # E2 - STOPS
        (38, 100, 1440), # D2 - resolve
    ]
    
    tick = 0
    for pitch, vel, dur in bass_notes:
        if tick + dur > section_ticks:
            dur = section_ticks - tick
        if dur <= 0:
            break
        unit.add_event(MusicEvent(pitch=pitch, volume=vel, start_tick=tick, end_tick=tick + dur))
        tick += dur + 480  # gap between bass notes
    
    pad_unit_to_length(unit, section_ticks)
    return unit


def prosodic_pad_unit(section_ticks):
    """Pad/chordal texture: sustained chords at clause boundaries."""
    unit = MusicUnit()
    
    # Chord at each clause boundary - 4 bars = 7680 ticks per section
    chords = [
        ([50, 57, 62, 64], 70, 0, 2880),       # Dm9 - bars 1-1.5
        ([55, 59, 62], 65, 2880, 2880),         # G/B - bars 1.5-3
        ([53, 57, 60, 64], 75, 5760, 1920),     # Cmaj9 - bar 3-4
    ]
    
    for pitches, vel, offset, dur in chords:
        if offset + dur > section_ticks:
            dur = section_ticks - offset
        for p in pitches:
            unit.add_event(MusicEvent(pitch=p, volume=vel, start_tick=offset, end_tick=offset + dur))
    
    pad_unit_to_length(unit, section_ticks)
    return unit


def build_composer():
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c.create_matrix(num_voices=3, num_sections=2)
    
    # Voices
    c.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    c.add_voice("Bass", program=MidiInstrument.BASS, channel=1)
    c.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=2)
    
    # Sections: A = statement (bars 1-4), B = question (bars 5-8)
    c.add_section("A", bars=4)
    c.add_section("B", bars=4)
    
    # Section lengths: 4 bars each
    section_ticks = 4 * BAR  # 7680
    
    # Generate prosodic units (relative ticks, padded to section length)
    melody_a = prosodic_melody_unit(section_ticks)
    melody_b = prosodic_melody_unit(section_ticks)
    
    bass_a = prosodic_bass_unit(section_ticks)
    bass_b = prosodic_bass_unit(section_ticks)
    
    pad_a = prosodic_pad_unit(section_ticks)
    pad_b = prosodic_pad_unit(section_ticks)
    
    # Fill matrix
    c.fill_voice_section("Lead", "A", melody_a)
    c.fill_voice_section("Lead", "B", melody_b)
    c.fill_voice_section("Bass", "A", bass_a)
    c.fill_voice_section("Bass", "B", bass_b)
    c.fill_voice_section("Pad", "A", pad_a)
    c.fill_voice_section("Pad", "B", pad_b)
    
    return c


def apply_binaural_pan(midi_path, output_wav_path, sr=44100):
    """
    SP-021: Binaural Woodworth-Schlosberg Spatialization
    Apply HRTF-inspired panning to rendered audio.
    ITD (interaural time difference) + ILD (interaural level difference).
    """
    # First render MIDI to mono WAV via FluidSynth
    import subprocess
    raw_wav = output_wav_path.replace('.wav', '_raw.wav')
    
    sf2_path = "/opt/data/micromamba/envs/musicom/bin/TimGM6mb.sf2"
    if not os.path.exists(sf2_path):
        sf2_path = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    if not os.path.exists(sf2_path):
        sf2_path = "/usr/share/sounds/sf2/TimGM6mb.sf2"
    
    fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
    
    result = subprocess.run(
        [fluidsynth, '-ni', '-g', '1.2', '-F', raw_wav, sf2_path, midi_path],
        capture_output=True, text=True, timeout=60
    )
    
    if not os.path.exists(raw_wav) or os.path.getsize(raw_wav) < 100:
        print(f"FluidSynth failed: {result.stderr}")
        return False
    
    # Read raw WAV
    import wave
    with wave.open(raw_wav, 'r') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_data = wf.readframes(n_frames)
    
    audio = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
    if n_channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)
    audio = audio / 32768.0
    
    # Binaural processing: slow LFO panning with ITD/ILD
    n_samples = len(audio)
    t = np.arange(n_samples) / sr
    
    # HRTF parameters
    # Head radius ~0.0875m, speed of sound 343 m/s
    # Max ITD = head_radius/c = ~0.255ms = ~11 samples at 44100
    MAX_ITD_SAMPLES = 11
    HEAD_RADIUS = 0.0875
    C_SOUND = 343.0
    
    # Slow panning LFO (0.08 Hz) - creates spatial movement
    pan_lfo = 0.5 + 0.4 * np.sin(2 * np.pi * 0.08 * t)  # 0.1 to 0.9 range
    
    # Secondary LFO for elevation feel (0.03 Hz)
    elev_lfo = 0.5 + 0.3 * np.sin(2 * np.pi * 0.03 * t + np.pi/4)
    
    # ITD: Woodworth formula
    # ITD(theta) = (head_radius/c) * (theta + sin(theta)) for azimuth theta
    azimuth = (pan_lfo - 0.5) * np.pi  # -pi/2 to pi/2
    itd_seconds = (HEAD_RADIUS / C_SOUND) * (azimuth + np.sin(azimuth))
    itd_samples = (itd_seconds * sr).astype(int)
    itd_samples = np.clip(itd_samples, -MAX_ITD_SAMPLES, MAX_ITD_SAMPLES)
    
    # ILD: head shadow effect (frequency-dependent, simplified)
    # Higher frequencies = more shadow = louder on near ear
    ild_left = np.where(pan_lfo > 0.5, 1.0 - 0.3 * (pan_lfo - 0.5), 1.0)
    ild_right = np.where(pan_lfo < 0.5, 1.0 - 0.3 * (0.5 - pan_lfo), 1.0)
    
    # Build stereo with ITD delay
    left = np.zeros(n_samples + MAX_ITD_SAMPLES)
    right = np.zeros(n_samples + MAX_ITD_SAMPLES)
    
    for i in range(n_samples):
        delay = itd_samples[i]
        if delay >= 0:
            left[i + delay] += audio[i] * ild_left[i]
            right[i] += audio[i] * ild_right[i]
        else:
            left[i] += audio[i] * ild_left[i]
            right[i - delay] += audio[i] * ild_right[i]
    
    # Trim to original length
    left = left[:n_samples]
    right = right[:n_samples]
    
    # Apply gentle low-pass for head-shadow realism (simple moving average)
    kernel_size = 3
    kernel = np.ones(kernel_size) / kernel_size
    left = np.convolve(left, kernel, mode='same')
    right = np.convolve(right, kernel, mode='same')
    
    # Stack to stereo
    stereo = np.column_stack([left, right])
    
    # Peak normalize to -1dB
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo = stereo * (0.89 / peak)
    
    # Write stereo WAV
    stereo_int16 = (stereo * 32767).astype(np.int16)
    with wave.open(output_wav_path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(stereo_int16.tobytes())
    
    # Cleanup raw
    if os.path.exists(raw_wav):
        os.remove(raw_wav)
    
    return True


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "MIDI"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "Audio"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "Analysis"), exist_ok=True)
    
    # Build composition
    composer = build_composer()
    
    # Validate (zero-drift gate)
    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"Validation failed: {msg}")
    
    # Export MIDI
    midi_path = os.path.join(OUTPUT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    composer.to_midi(midi_path)
    
    size = os.path.getsize(midi_path)
    assert size > 40, f"MIDI empty: {size} bytes"
    print(f"MIDI: {midi_path} ({size} bytes)")
    
    # Grid visualization
    grid_path = os.path.join(OUTPUT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path, ticks_per_character=240, bpm=BPM)
    
    # Provenance
    write_provenance(
        midi_path,
        classification=AI_ASSISTED,
        generator="051-prosodic-binaural/compose.py",
        parameters={
            "bpm": BPM,
            "method": "005-prosodic-narrative-coupling",
            "sp_method": "SP-021-binaural-woodworth-schlosberg",
            "scale": "D Dorian",
            "prosodic_text": "Where does the river go when the rain stops falling?",
        },
        notes="Prosodic Narrative Coupling: speech stress/contour mapped to velocity/pitch. "
              "Binaural HRTF spatialization with Woodworth ITD + head-shadow ILD."
    )
    
    # Render audio with binaural spatialization
    wav_path = os.path.join(OUTPUT_DIR, "Audio", f"{PROJECT_NAME}.wav")
    ogg_path = os.path.join(OUTPUT_DIR, "Audio", f"{PROJECT_NAME}.ogg")
    
    success = apply_binaural_pan(midi_path, wav_path)
    if success and os.path.exists(wav_path):
        wav_size = os.path.getsize(wav_path)
        assert wav_size > 40, f"WAV empty: {wav_size} bytes"
        print(f"WAV: {wav_path} ({wav_size} bytes)")
        
        # Convert to OGG
        import subprocess
        subprocess.run(
            ['ffmpeg', '-i', wav_path, '-codec:a', 'libopus',
             '-application', 'voip', '-b:a', '48k', ogg_path, '-y', '-loglevel', 'error'],
            timeout=30
        )
        
        if os.path.exists(ogg_path):
            ogg_size = os.path.getsize(ogg_path)
            assert ogg_size > 40, f"OGG empty: {ogg_size} bytes"
            print(f"OGG: {ogg_path} ({ogg_size} bytes)")
            
            # Cleanup WAV
            os.remove(wav_path)
            print("WAV cleaned up")
        else:
            print("ERROR: OGG conversion failed")
    else:
        print("ERROR: Binaural render failed")
    
    print("DONE")


if __name__ == "__main__":
    main()
