# -*- coding: utf-8 -*-
"""Render phase-2 + phase-1 MIDI to WAV + OGG via FluidSynth (SP-001)."""
import os

from workflows.musicom_workflow import produce

HERE = os.path.dirname(os.path.abspath(__file__))
MIDI = os.path.join(HERE, "MIDI")

for name in ["240-ragtime-glide.mid",
             "240-ragtime-glide-phase1.mid"]:
    p = os.path.join(MIDI, name)
    r = produce(p, method="SP-001")
    print(name, "->")
    print("  wav:", r.wav_path, os.path.getsize(r.wav_path), "bytes")
    print("  ogg:", r.ogg_path, os.path.getsize(r.ogg_path), "bytes")
