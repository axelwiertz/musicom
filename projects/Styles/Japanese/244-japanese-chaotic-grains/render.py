# -*- coding: utf-8 -*-
"""Render phase-2 + phase-1 MIDI to WAV (FluidSynth) -> master (-14 LUFS) -> OGG."""
import os
import subprocess

from sound.render.fluidsynth import discover_soundfont
from utilities.env import fluidsynth_bin

HERE = "/opt/data/projects/Styles/Japanese/244-japanese-chaotic-grains"
MIDI = os.path.join(HERE, "MIDI")
AUDIO = os.path.join(HERE, "Audio")
os.makedirs(AUDIO, exist_ok=True)

SF = discover_soundfont()
assert SF, "no soundfont found"
GAIN = "0.6"

# dense 5-voice mix can clip at produce()'s 1.2; 0.6 lands peak ~0.9
for name in ["244-japanese-chaotic-grains.mid",
             "244-japanese-chaotic-grains-phase1.mid"]:
    stem = name[:-4]
    midi = os.path.join(MIDI, name)
    wav = os.path.join(AUDIO, stem + ".wav")
    subprocess.run([fluidsynth_bin(), "-ni", "-g", GAIN, "-F", wav, SF, midi],
                   check=True, capture_output=True, text=True)
    print(f"rendered {stem}.wav ({os.path.getsize(wav)} bytes)")

# ---- master both WAVs to -14 LUFS / -1 dBTP --------------------------------
from sound.effects.mastering import master
from sound.utils.io import read_wav, write_wav

for stem in ["244-japanese-chaotic-grains", "244-japanese-chaotic-grains-phase1"]:
    wav = os.path.join(AUDIO, stem + ".wav")
    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=-14.0, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)
    print(f"mastered {stem}: LUFS={rep['integrated_lufs']:.2f} "
          f"dBTP={rep['true_peak_db']:.2f}")

# ---- OGG encode (Opus) ------------------------------------------------------
for stem in ["244-japanese-chaotic-grains", "244-japanese-chaotic-grains-phase1"]:
    wav = os.path.join(AUDIO, stem + ".wav")
    ogg = os.path.join(AUDIO, stem + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-application", "voip",
                    "-b:a", "48k", ogg],
                   check=True, capture_output=True, text=True)
    print(f"{stem}.ogg ({os.path.getsize(ogg)} bytes)")

print("ALL RENDERS DONE")
