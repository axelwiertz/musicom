import sys
import os
import subprocess

def render_all_three():
    print("=== DUAL ENGINE ENGINE: COMPILATION & RENDERING FOR COSER TEST ===")
    
    soundfont_path = "/opt/data/.local/lib/python3.13/site-packages/pretty_midi/TimGM6mb.sf2"
    fluidsynth_bin = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
    
    compositions = [
        ("composition1_lsystem", "composition1_lsystem"),
        ("composition2_portamento", "composition2_portamento"),
        ("composition3_merged", "composition3_merged")
    ]
    
    for base_in, base_out in compositions:
        midi_path = f"/opt/data/projects/Research/outputs/{base_in}.mid"
        wav_path = f"/opt/data/projects/Research/outputs/{base_out}.wav"
        ogg_path = f"/opt/data/projects/Research/outputs/{base_out}.ogg"
        
        print(f"\nRendering {midi_path}...")
        
        # Phase A: FluidSynth GM rendering
        cmd_fluid = [
            fluidsynth_bin,
            "-ni",
            "-g", "1.3",
            "-F", wav_path,
            "-r", "44100",
            soundfont_path,
            midi_path
        ]
        subprocess.run(cmd_fluid, check=True)
        
        # Phase B: Opus encoding
        cmd_ffmpeg = [
            "ffmpeg",
            "-i", wav_path,
            "-codec:a", "libopus",
            "-application", "voip",
            "-b:a", "48k",
            ogg_path,
            "-y",
            "-loglevel", "error"
        ]
        subprocess.run(cmd_ffmpeg, check=True)
        print(f"Render successful => {ogg_path}")

if __name__ == "__main__":
    render_all_three()
