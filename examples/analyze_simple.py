# -*- coding: utf-8 -*-
"""Reverse analysis — MIDI -> key / chords / grid.

Run:
    python examples/analyze_simple.py
"""
from workflows.musicom_workflow import compose
from workflows.analyze import analyze_midi

r = compose(style="pop", key="C", bpm=120, out_dir="outputs")
rep = analyze_midi(r.midi_path)

print(rep.summary())
