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

# Chords (G, C, D)
CHORDS = {"G":[43,55,59,62], "C":[48,60,64,67], "D":[50,62,66,69]}
PROGRESSION = ["G"]*4 + ["C"]*2 + ["G"]*2 + ["D"]*2 + ["C"]*2 + ["G"]*4

# Steel Pattern
STEEL_PATTERN = [
    ('G4',  0.0,  1.5,  'B4',  0.3),
    ('C5',  4.0,  0.5,  'D5',  0.1), ('D5', 4.5, 1.5, None, 0.0),
    ('E4',  8.0,  1.5,  'G4',  0.3), ('G4', 10.0, 2.0, 'E4', 1.0),
    ('D4',  12.0, 1.5,  'G4',  0.2), ('G4', 14.0, 2.0, None, 0.0),
    ('F#4', 16.0, 0.75, 'A4',  0.1), ('A4', 18.0, 1.5, 'F#4', 0.5),
    ('G4',  20.0, 1.5,  'E4',  0.3), ('E4', 22.0, 2.0, 'D4', 1.0),
    ('G4',  24.0, 1.0,  'B4',  0.2), ('G4', 30.0, 4.0, None, 0.0)
]

def build_backing_midi():
    """Builds ONLY the backing tracks for FluidSynth sync."""
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    mid.tracks.append(MidiTrack()) # Container
    mid.tracks[0].append(MetaMessage('set_tempo', tempo=bpm2tempo(BPM)))

    # Bass
    bass = MidiTrack()
    mid.tracks.append(bass)
    bass.append(Message('program_change', program=32, time=0))
    for b_idx, chord in enumerate(PROGRESSION):
        root, fifth = CHORDS[chord][0], CHORDS[chord][0]+7
        for i, n in enumerate([root, fifth, root, fifth]):
            bass.append(Message('note_on', note=n, velocity=90, time=0))
            bass.append(Message('note_off', note=n, velocity=0, time=TICKS_PER_BEAT))
            
    # Rhythm Guitar
    gtr = MidiTrack()
    mid.tracks.append(gtr)
    gtr.append(Message('program_change', program=25, time=0))
    for b_idx, chord in enumerate(PROGRESSION):
        notes = [n+12 for n in CHORDS[chord]]
        for beat in range(4):
            for off in [0, TICKS_PER_BEAT//2]:
                for n in notes: gtr.append(Message('note_on', note=n, velocity=60, time=0))
                # 8th note spacing
                gtr.append(Message('note_off', note=notes[0], velocity=0, time=TICKS_PER_BEAT//2))
                for n in notes[1:]: gtr.append(Message('note_off', note=n, velocity=0, time=0))
    
    mid.save("/tmp/sync_backing.mid")

def render_sync():
    print("FIXING SYNC - Generating strictly aligned backing...")
    build_backing_midi()
    
    # 1. Backing (FluidSynth)
    SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    subprocess.run(f"fluidsynth -ni -g 0.6 -F /tmp/sync_bg.wav {SF2} /tmp/sync_backing.mid", shell=True, check=True)
    bg, _ = sf.read("/tmp/sync_bg.wav")
    if len(bg.shape) > 1: bg = np.mean(bg, axis=1)

    # 2. Lead (DSP)
    # Re-map lead pattern for DSP
    resolved = []
    for note, start, dur, slide, s_start in STEEL_PATTERN:
        resolved.append((dsp.NOTES[note], start, dur, dsp.NOTES[slide] if slide else None, s_start))
    
    # Calculate exact sample length (64 beats is 16 bars)
    total_beats = 64
    total_samples = int(SR * (total_beats * 60 / BPM))
    
    lead, _, _, _ = dsp.build_steel_guitar(resolved, SR, BPM)
    
    # PAD OR TRIM TO EXACT SAMPLE BOUNDARY
    final_lead = np.zeros(total_samples)
    final_bg = np.zeros(total_samples)
    
    use_l = min(len(lead), total_samples)
    use_b = min(len(bg), total_samples)
    
    final_lead[:use_l] = lead[:use_l]
    final_bg[:use_b] = bg[:use_b]
    
    # MIX
    master = final_lead * 1.6 + final_bg * 0.6
    master = master / np.max(np.abs(master)) * 0.95
    
    sf.write(str(AUDIO_PATH), master, SR)
    subprocess.run(f"ffmpeg -i {AUDIO_PATH} -codec:a libopus -b:a 64k {OGG_PATH} -y", shell=True, capture_output=True)
    print(f"SYNC FIXED. Final file: {AUDIO_PATH}")

if __name__ == "__main__":
    render_sync()
