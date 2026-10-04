# -*- coding: utf-8 -*-
"""Transform a composed matrix — transpose, retrograde, negative harmony.

Run:
    python examples/transform_simple.py
"""
import os

from structures import MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_chord_unit
from transformers.negative_harmony import NegativeHarmonyTransformer


def make_matrix() -> UnitMatrixComposer:
    composer = UnitMatrixComposer(bpm=100, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=1, num_sections=2)
    composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    composer.add_section("A", bars=1)
    composer.add_section("B", bars=1)
    composer.fill_voice_section("Lead", "A", create_chord_unit([60, 64, 67], 1920))  # C
    composer.fill_voice_section("Lead", "B", create_chord_unit([55, 59, 62], 1920))  # G
    ok, msg = composer.validate()
    assert ok, msg
    return composer


os.makedirs("outputs", exist_ok=True)

c = make_matrix()
c.to_midi("outputs/transform_original.mid")

c = make_matrix()
c.matrix.transpose_row(0, 7)             # transpose up a perfect fifth
c.to_midi("outputs/transform_transpose_up5.mid")

c = make_matrix()
c.matrix.retrograde_row(0)               # reverse the section order
c.to_midi("outputs/transform_retrograde.mid")

# Negative harmony mirrors the C-major triad across the tonic/dominant axis.
neg = NegativeHarmonyTransformer(key_center=60).transform(
    create_chord_unit([60, 64, 67], 1920))
print("negative-harmony pcs:", sorted({e.pitch % 12 for e in neg.events}))
