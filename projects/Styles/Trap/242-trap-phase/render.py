# -*- coding: utf-8 -*-
"""Render phase-2 + phase-1 MIDI to WAV + OGG via FluidSynth (SP-001 style).

Gain 0.6 (produce()'s 1.2 clipped the dense 7-voice trap mix at peak 1.0),
then direct Opus OGG. SoundFont auto-resolved via discover_soundfont().
(peaknorm unavailable in this ffmpeg build — gain 0.6 already lands peak
~0.91 with zero clipped samples, so no normalization step is needed.)
"""
import os
import subprocess

from sound.render.fluidsynth import discover_soundfont
from utilities.env import fluidsynth_bin

HERE = os.path.dirname(os.path.abspath(__file__))
MIDI = os.path.join(HERE, "MIDI")
AUDIO = os.path.join(HERE, "Audio")
os.makedirs(AUDIO, exist_ok=True)

SF = discover_soundfont()
assert SF, "no soundfont found"
GAIN = "0.6"

for name in ["242-trap-phase.mid", "242-trap-phase-phase1.mid"]:
    stem = name[:-4]
    midi = os.path.join(MIDI, name)
    wav = os.path.join(AUDIO, stem + ".wav")
    ogg = os.path.join(AUDIO, stem + ".ogg")

    subprocess.run([fluidsynth_bin(), "-ni", "-g", GAIN, "-F", wav, SF, midi],
                   check=True, capture_output=True, text=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-application", "voip",
                    "-b:a", "48k", ogg],
                   check=True, capture_output=True, text=True)
    print(name, "->")
    print("  wav:", wav, os.path.getsize(wav), "bytes")
    print("  ogg:", ogg, os.path.getsize(ogg), "bytes")
