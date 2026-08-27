import os
import sys
import subprocess
import numpy as np
import soundfile as sf
from pathlib import Path

# Add project root to sys.path to allow imports with dashes in names
# Using import_module for files with dashes in filename
import importlib.util

RESEARCH_SRC = Path("/opt/data/projects/Research/014-virtual-instruments-dsp/Src")
module_name = "dev_steel_guitar_2026-06-24"
spec = importlib.util.spec_from_file_location("dsp", str(RESEARCH_SRC / (module_name + ".py")))
dsp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dsp)


# Config
OUT_DIR = Path("/opt/data/projects/Styles/Country/038-steel-guitar-demo")
AUDIO_PATH = OUT_DIR / "Audio" / "steel_guitar_demo.wav"
MIDI_PATH = OUT_DIR / "MIDI" / "steel_guitar_demo.mid"
OGG_PATH = OUT_DIR / "Audio" / "steel_guitar_demo.ogg"

# Custom Country Pattern: "The Crying Slide"
COUNTRY_PATTERN = [
    # (note, start_beat, dur_beats, slide_target, slide_start_beat)
    ('A4',  0.0,  1.0,  'B4',  0.3),   # A4 slide up to B4
    ('B4',  1.0,  0.5,   None,  0.0),   
    ('A4',  1.5,  0.5,   None,  0.0),
    ('G4',  2.0,  2.0,  'E4',  0.5),   # G4 long soulful slide to E4
    
    ('D4',  4.0,  1.5,  'G4',  0.2),   # Country bounce slide
    ('G4',  5.5,  0.5,   None,  0.0),
    ('F#4', 6.0,  2.0,  'G4',  0.8),   # F# to G resolution
    
    ('A4',  8.0,  0.75, 'B4',  0.2),
    ('D5',  8.75, 0.25,  None,  0.0),
    ('B4',  9.0,  1.0,  'A4',  0.4),
    ('G4',  10.0, 3.0,  'D4',  1.0),   # Final long fade slide
]

# Resolve pattern
pattern_resolved = []
for item in COUNTRY_PATTERN:
    note, start, dur, slide_target, slide_off = item
    freq = dsp.NOTES[note]
    slide_freq = dsp.NOTES[slide_target] if slide_target else None
    pattern_resolved.append((freq, start, dur, slide_freq, slide_off))

print("=== Generating Steel Guitar Sound ===")

# Render audio using DSP model
audio, freq_env, times, freqs = dsp.build_steel_guitar(pattern_resolved, dsp.SR, 90) # Slower tempo 90
sf.write(str(AUDIO_PATH), audio, dsp.SR)
print(f"Saved audio: {AUDIO_PATH}")

# Convert to OGG
subprocess.run(["ffmpeg", "-i", str(AUDIO_PATH), "-codec:a", "libopus", "-b:a", "64k", str(OGG_PATH), "-y"], 
               capture_output=True, check=True)
print(f"Saved ogg: {OGG_PATH}")

# Save MIDI
dsp.write_midi_file(str(MIDI_PATH), pattern_resolved, 90, dsp.NOTES)
print(f"Saved MIDI: {MIDI_PATH}")

# Write small analysis
with open(OUT_DIR / "Analysis" / "theory.md", "w") as f:
    f.write("# Steel Guitar Demo Analysis\n\n")
    f.write("- **Instrument**: Synthesised Steel Guitar (Karplus-Strong + Magnetic Pickup)\n")
    f.write("- **Style**: Emotive Country Glissando\n")
    f.write("- **DSP Attributes**: \n")
    f.write("  - Harmonic Resonance: 680Hz Bandpass peak (Magnetic Pickup twang)\n")
    f.write("  - Portamento: Manual frequency trajectory (Steel slide emulation)\n")
    f.write("  - Note Realism: Noise-burst onset (8ms duration)\n")

print("=== Done ===")
