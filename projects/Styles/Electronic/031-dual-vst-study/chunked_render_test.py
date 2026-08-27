import pedalboard
from pedalboard.io import AudioFile
import mido
import numpy as np
import os

PROJECT_PATH = "/opt/data/projects/Styles/Electronic/031-dual-vst-study"
OUTPUT_WAV = f"{PROJECT_PATH}/audio/chunked_vst_test.wav"
OUTPUT_OGG = f"{PROJECT_PATH}/audio/chunked_vst_test.ogg"

# Kars: String synthesis
KARS_VST = "/usr/lib/vst3/Kars.vst3"

SAMPLE_RATE = 44100
BLOCK_SIZE = 512 # Small blocks to ensure MIDI timing accuracy
DURATION = 4.0
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

print("--- CHUNKED RENDER: Manual MIDI Injection ---")

try:
    # Use load_plugin to get the raw plugin object
    synth = pedalboard.load_plugin(KARS_VST)
    print(f"Loaded: {synth.name}")
    
    # Define simple sequence (Notes at 0s, 1s, 2s, 3s)
    midi_plan = {
        0: 60,   # 0s: C3
        44100: 67, # 1s: G3
        88200: 72, # 2s: C4
        132300: 79 # 3s: G4
    }

    final_audio = np.zeros((1, TOTAL_SAMPLES), dtype=np.float32)
    
    # Render loop: process one block at a time
    for start_sample in range(0, TOTAL_SAMPLES, BLOCK_SIZE):
        end_sample = min(start_sample + BLOCK_SIZE, TOTAL_SAMPLES)
        actual_block_size = end_sample - start_sample
        
        # Check if any MIDI events fall in this specific block
        block_midi = []
        for sample_tick, note in midi_plan.items():
            if start_sample <= sample_tick < end_sample:
                # 'time' in this call is offset from start of buffer (0 to block_size)
                offset = sample_tick - start_sample
                block_midi.append(mido.Message('note_on', note=note, velocity=100, time=offset))
                # Auto note-off after 200ms (8820 samples)
                block_midi.append(mido.Message('note_off', note=note, velocity=0, time=min(offset + 8820, actual_block_size - 1)))

        # Process the block
        # We provide a zero-buffer as input and the MIDI to trigger the synth
        input_block = np.zeros((1, actual_block_size), dtype=np.float32)
        output_block = synth(input_block, SAMPLE_RATE, reset=False, midi=block_midi)
        
        final_audio[:, start_sample:end_sample] = output_block

    # Normalize
    peak = np.max(np.abs(final_audio))
    if peak > 0:
        final_audio = final_audio * (0.85 / peak)

    with AudioFile(OUTPUT_WAV, 'w', SAMPLE_RATE, 1) as f:
        f.write(final_audio)
    
    os.system(f"ffmpeg -y -i {OUTPUT_WAV} -codec:a libvorbis -q:a 5 {OUTPUT_OGG}")
    print(f"Chunked Master Exported: {OUTPUT_OGG}")

except Exception as e:
    print(f"FAIL: {e}")
