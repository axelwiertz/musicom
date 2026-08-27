import os
import sys
import subprocess
import numpy as np
import soundfile as sf
from pathlib import Path
import importlib.util
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

# 1. Import Steel Guitar DSP
RESEARCH_SRC = Path("/opt/data/projects/Research/014-virtual-instruments-dsp/Src")
module_name = "dev_steel_guitar_2026-06-24"
spec = importlib.util.spec_from_file_location("dsp", str(RESEARCH_SRC / (module_name + ".py")))
dsp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dsp)

# 2. Config
OUT_DIR = Path("/opt/data/projects/Styles/Country/038-steel-guitar-demo")
AUDIO_PATH = OUT_DIR / "Audio" / "country_ensemble_16bar.wav"
MIDI_PATH = OUT_DIR / "MIDI" / "country_ensemble_16bar.mid"
OGG_PATH = OUT_DIR / "Audio" / "country_ensemble_16bar.ogg"
BPM = 90
SR = 44100
TICKS_PER_BEAT = 480

# 3. Chords (G, C, D)
CHORDS = {"G":[43,55,59,62], "C":[48,60,64,67], "D":[50,62,66,69]}
PROGRESSION = ["G"]*4 + ["C"]*2 + ["G"]*2 + ["D"]*2 + ["C"]*2 + ["G"]*4

# 4. Steel Pattern
STEEL_PATTERN = [
    ('G4',  0.0,  1.5,  'B4',  0.3),
    ('C5',  4.0,  0.5,  'D5',  0.1), ('D5', 4.5, 1.5, None, 0.0),
    ('E4',  8.0,  1.5,  'G4',  0.3), ('G4', 10.0, 2.0, 'E4', 1.0),
    ('D4',  12.0, 1.5,  'G4',  0.2), ('G4', 14.0, 2.0, None, 0.0),
    ('F#4', 16.0, 0.75, 'A4',  0.1), ('A4', 18.0, 1.5, 'F#4', 0.5),
    ('G4',  20.0, 1.5,  'E4',  0.3), ('E4', 22.0, 2.0, 'D4', 1.0),
    ('G4',  24.0, 1.0,  'B4',  0.2), ('G4', 30.0, 4.0, None, 0.0)
]

def build_midi_ensemble():
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    
    # Bass Track
    bass_track = MidiTrack()
    mid.tracks.append(bass_track)
    bass_track.append(MetaMessage('track_name', name='Acoustic Bass', time=0))
    bass_track.append(Message('program_change', program=32, time=0))
    current_tick = 0
    for bar_idx, chord_name in enumerate(PROGRESSION):
        notes = [CHORDS[chord_name][0], CHORDS[chord_name][0]+7]
        for i, note in enumerate([notes[0], notes[1], notes[0], notes[1]]):
            start_tick = (bar_idx * 4 + i) * TICKS_PER_BEAT
            bass_track.append(Message('note_on', note=note, velocity=90, time=start_tick - current_tick))
            bass_track.append(Message('note_off', note=note, velocity=0, time=TICKS_PER_BEAT // 2))
            current_tick = start_tick + TICKS_PER_BEAT // 2

    # Guitar Track
    guitar_track = MidiTrack()
    mid.tracks.append(guitar_track)
    guitar_track.append(MetaMessage('track_name', name='Rhythm Guitar', time=0))
    guitar_track.append(Message('program_change', program=25, time=0))
    current_tick = 0
    for bar_idx, chord_name in enumerate(PROGRESSION):
        notes = CHORDS[chord_name]
        for beat in range(4):
            # Up-down strum
            for off in [0, TICKS_PER_BEAT//2]:
                start_tick = bar_idx*4*TICKS_PER_BEAT + beat*TICKS_PER_BEAT + off
                for i, n in enumerate(notes):
                    delta = start_tick - current_tick
                    guitar_track.append(Message('note_on', note=n+12, velocity=60, time=max(0, delta)))
                    guitar_track.append(Message('note_off', note=n+12, velocity=0, time=10))
                    current_tick = start_tick + 10

    mid.save(MIDI_PATH)
    
    resolved = []
    for note, start, dur, slide, s_start in STEEL_PATTERN:
        f = dsp.NOTES[note]
        sf = dsp.NOTES[slide] if slide else None
        resolved.append((f, start, dur, sf, s_start))
    return resolved

print("Generating 16-bar Country Ensemble...")
resolved_lead = build_midi_ensemble()

total_beats = 16 * 4
audio_lead, _, _, _ = dsp.build_steel_guitar(resolved_lead, SR, BPM)

TEMP_WAV = "/tmp/bg.wav"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
subprocess.run(f"fluidsynth -ni -g 0.6 -F {TEMP_WAV} {SF2} {MIDI_PATH}", shell=True, check=True)
backup_audio, _ = sf.read(TEMP_WAV)

# Ensure backing is mono for mixdown
if len(backup_audio.shape) > 1:
    backup_audio = np.mean(backup_audio, axis=1)

min_len = min(len(audio_lead), len(backup_audio))
mixed = audio_lead[:min_len] * 1.5 + backup_audio[:min_len] * 0.5

mixed = mixed / np.max(np.abs(mixed)) * 0.9

sf.write(str(AUDIO_PATH), mixed, SR)
subprocess.run(f"ffmpeg -i {AUDIO_PATH} -codec:a libopus -b:a 64k {OGG_PATH} -y", shell=True, capture_output=True)
print(f"Project Complete: {AUDIO_PATH}")
