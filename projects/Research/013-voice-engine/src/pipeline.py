import sys
import os
import pedalboard
from pedalboard import Pedalboard, Reverb, Compressor, HighPassFilter, Gain, Limiter
from pedalboard.io import AudioFile
import subprocess

def master_audio(input_vox, input_instr, output_final):
    """
    1. Mixes Vocal and Instrumental using FFmpeg.
    2. Runs Pedalboard mastering chain on the mix.
    """
    mix_temp = "/tmp/mix_temp.wav"
    
    # MIXING (FFmpeg)
    # amix=inputs=2:duration=first:dropout_transition=2
    cmd = [
        "ffmpeg", "-y",
        "-i", input_vox,
        "-i", input_instr,
        "-filter_complex", "amix=inputs=2:duration=longest",
        mix_temp
    ]
    subprocess.run(cmd, check=True)
    
    # MASTERING (Pedalboard)
    with AudioFile(mix_temp) as f:
        audio = f.read(f.frames)
        sample_rate = f.sample_rate

    # Mastering Chain
    board = Pedalboard([
        HighPassFilter(cutoff_frequency_hz=100),
        Compressor(threshold_db=-18, ratio=3),
        Reverb(room_size=0.15, dry_level=0.9, wet_level=0.1),
        Gain(gain_db=1.5),
        Limiter(threshold_db=-0.1)
    ])

    mastered = board(audio, sample_rate)

    with AudioFile(output_final, 'w', sample_rate, mastered.shape[0]) as f:
        f.write(mastered)
    
    # Final conversion to OGG for Telegram
    ogg_final = output_final.replace(".wav", ".ogg")
    cmd_ogg = [
        "ffmpeg", "-y", "-i", output_final,
        "-c:a", "libopus", "-b:a", "64k",
        ogg_final
    ]
    subprocess.run(cmd_ogg, check=True)
    
    return ogg_final

if __name__ == "__main__":
    print("Vocal Mixing & Mastering Pipeline Core Loaded.")
