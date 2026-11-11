# -*- coding: utf-8 -*-
"""Render + master + encode the lounge piece to OGG (FluidSynth -> master())."""

import os
import subprocess

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from utilities.env import fluidsynth_bin

BASE = os.path.join("/opt/data/repos/musicom", "projects", "Styles", "Lounge",
                    "298-lounge-bossa-cocktail")
MIDI = os.path.join(BASE, "MIDI")
AUDIO = os.path.join(BASE, "Audio")
os.makedirs(AUDIO, exist_ok=True)

SF = discover_soundfont()
FLUID = fluidsynth_bin()
TARGET = target_for_style("lounge")

for tag in ("perfect", "humanized"):
    mid = os.path.join(MIDI, f"298-lounge-bossa-cocktail-{tag}.mid")
    wav = os.path.join(AUDIO, f"298-lounge-bossa-cocktail-{tag}.wav")
    ogg = os.path.join(AUDIO, f"298-lounge-bossa-cocktail-{tag}.ogg")

    subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav, SF, mid],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)

    subprocess.run(["ffmpeg", "-y", "-i", wav, "-codec:a", "libopus",
                    "-application", "voip", "-b:a", "48k", ogg],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"{tag}: LUFS={rep['integrated_lufs']:.2f} "
          f"TP={rep['true_peak_db']:.2f}dB "
          f"size={os.path.getsize(ogg)}B  {ogg}")
    os.remove(wav)

print("RENDER DONE")