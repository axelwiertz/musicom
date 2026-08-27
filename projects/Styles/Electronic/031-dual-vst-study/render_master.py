import pedalboard
from pedalboard.io import AudioFile
import mido
import numpy as np
import os

# Project Config
PROJECT_PATH = "/opt/data/projects/Styles/Electronic/031-dual-vst-study"
OUTPUT_WAV = f"{PROJECT_PATH}/audio/dual_vst_master.wav"
OUTPUT_OGG = f"{PROJECT_PATH}/audio/dual_vst_master.ogg"

# Plugin Paths
SYNTH_VST = "/usr/lib/vst3/Nekobi.vst3"
REVERB_VST = "/usr/lib/vst3/MaGigaverb.vst3"

SAMPLE_RATE = 44100
BPM = 125
BARS = 4
SIXTEENTH = 60 / (BPM * 4)
DURATION = SIXTEENTH * 16 * BARS

# G-Minor Arpeggio (G, Bb, D, F)
# Note, Step-Position
arp_pattern = [
    (43, 0), (46, 3), (50, 6), (53, 9), (55, 12), (50, 14),
    (43, 16), (46, 19), (50, 22), (53, 25), (55, 28), (50, 30),
    (43, 32), (46, 35), (50, 38), (53, 41), (55, 44), (58, 46),
    (43, 48), (46, 51), (50, 54), (55, 57), (53, 60), (43, 62)
]

print(f"--- Project 031: Dual-Core Render (Sequential) ---")

try:
    # 1. Load Plugins
    synth = pedalboard.load_plugin(SYNTH_VST)
    reverb = pedalboard.load_plugin(REVERB_VST)
    print(f"Loaded: {synth.name} & {reverb.name}")
    
    # 2. Build MIDI
    midi_events = []
    for note, step in arp_pattern:
        start_tick = int(step * SIXTEENTH * SAMPLE_RATE)
        end_tick = int((step + 0.8) * SIXTEENTH * SAMPLE_RATE)
        midi_events.append(mido.Message('note_on', note=note, velocity=95, time=start_tick))
        midi_events.append(mido.Message('note_off', note=note, velocity=0, time=end_tick))

    # 3. STEP A: Generate Raw Synth Audio (Dry)
    print("Step 1: Rendering Dry Synth Lead...")
    dry_audio = synth(midi_events, duration=DURATION, sample_rate=SAMPLE_RATE, num_channels=1)
    
    # Convert mono to stereo for the reverb stage
    dry_stereo = np.vstack((dry_audio, dry_audio))
    
    # 4. STEP B: Process through Reverb (Wet)
    print("Step 2: Applying Gigaverb...")
    # Wrap effect in a Pedalboard to handle the buffer
    master_board = pedalboard.Pedalboard([reverb])
    master_audio = master_board(dry_stereo, SAMPLE_RATE)
    
    # 5. Export
    with AudioFile(OUTPUT_WAV, 'w', SAMPLE_RATE, 2) as f:
        f.write(master_audio)
    
    # 6. Final MP3/OGG wrap
    os.system(f"ffmpeg -y -i {OUTPUT_WAV} -codec:a libvorbis -q:a 5 {OUTPUT_OGG}")
    print(f"Master Exported: {OUTPUT_OGG}")

except Exception as e:
    print(f"FAIL: {e}")
