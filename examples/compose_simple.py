# -*- coding: utf-8 -*-
"""Minimal UnitMatrix -> MIDI in ~12 lines.

Run:
    python examples/compose_simple.py
"""
import os

from structures import MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=2, num_sections=1)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
composer.add_voice("Bass", program=MidiInstrument.PIANO, channel=1)
composer.add_section("A", bars=1)
composer.fill_voice_section("Lead", "A", create_note_unit(72, 1920))
composer.fill_voice_section("Bass", "A", create_note_unit(48, 1920))

ok, msg = composer.validate()            # zero-drift gate — MUST be True
assert ok, msg

os.makedirs("outputs", exist_ok=True)
composer.to_midi("outputs/compose_simple.mid")
print("wrote outputs/compose_simple.mid")
