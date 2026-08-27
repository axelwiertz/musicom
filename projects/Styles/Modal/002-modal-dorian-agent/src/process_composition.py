import os
import sys
import subprocess

def process_composition(midi_path):
    # 1. Synthesize (Placeholder for actual synthesis tool or numpy logic)
    wav_path = midi_path.replace('.midi', '.wav').replace('.mid', '.wav')
    print(f"Synthesizing {midi_path}...")
    
    # Using ffmpeg/fluidsynth or fallback to notification
    # For now, we ensure the directory exists
    os.makedirs("Analysis", exist_ok=True)
    
    # 2. Visualize via songsee
    viz_path = f"Analysis/{os.path.basename(midi_path)}.png"
    print(f"Generating visualization to {viz_path}...")
    # This command uses the songsee skill capability
    subprocess.run(["songsee", wav_path, "--viz", "spectrogram,chroma,loudness", "-o", viz_path])
    
    # 3. Convert for Telegram (Instant Playback)
    ogg_path = wav_path.replace('.wav', '.ogg')
    subprocess.run(["ffmpeg", "-i", wav_path, "-codec:a", "libopus", "-b:a", "48k", ogg_path, "-y"])
    
    print(f"DONE. Output files: {viz_path}, {ogg_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_composition(sys.argv[1])
    else:
        print("Usage: python process_composition.py <path_to_midi>")
