import sys
import os
import subprocess

def run_fluidsynth_render():
    print("=== STEP 6: EXECUTING HIGH-FIDELITY AUDIO RENDERING ===")
    midi_path = "/opt/data/projects/Research/outputs/first_long_composition.mid"
    output_wav = "/opt/data/projects/Research/outputs/first_long_composition.wav"
    soundfont_path = "/opt/data/.local/lib/python3.13/site-packages/pretty_midi/TimGM6mb.sf2"
    fluidsynth_bin = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
    
    print(f"MIDI input: {midi_path}")
    print(f"SoundFont: {soundfont_path}")
    print(f"Output: {output_wav}")
    
    # Render command using system-level FluidSynth inside micromamba bin
    cmd = [
        fluidsynth_bin,
        "-ni",
        "-F", output_wav,
        "-r", "44100",
        soundfont_path,
        midi_path
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("=== RENDERING PIPELINE COMPLETE: SUCCESS ===")
        print(result.stdout)
    else:
        print("=== RENDERING PIPELINE FAILED ===")
        print("Error:", result.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_fluidsynth_render()
