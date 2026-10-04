# -*- coding: utf-8 -*-
"""Produce audio from a MIDI file — two methods, one call each.

SP-011 (Karplus-Strong) is pure Python — the default no-dependency path (no
SoundFont required). SP-001 (FluidSynth) needs a SoundFont on disk and is
opt-in.

Run:
    python examples/produce_simple.py
"""
from workflows.musicom_workflow import compose, produce

r = compose(style="pop", key="C", bpm=120, out_dir="outputs")
midi = r.midi_path

# CREATE — Karplus-Strong string synthesis (pure Python)
p = produce(midi, method="SP-011")
print("SP-011 wav:", p.wav_path)
print("SP-011 ogg:", p.ogg_path)

# RENDER — FluidSynth SoundFont (opt-in; needs a .sf2 on disk)
try:
    p = produce(midi, method="SP-001")
    print("SP-001 wav:", p.wav_path)
except FileNotFoundError as e:
    print("SP-001 skipped (no SoundFont):", e)
