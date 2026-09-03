# -*- coding: utf-8 -*-
"""Probe: quick empty-unit validate gate + unit semantics sanity."""
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit

c = UnitMatrixComposer(bpm=100, ticks_per_beat=480, beats_per_bar=4)
c.create_matrix(num_voices=1, num_sections=1)
c.add_voice("X", program=65, channel=0)
c.add_section("A", bars=4)
u = create_empty_unit(7680)
c.set_unit(0, 0, u)
ok, msg = c.validate()
print("validate:", ok, msg)
print("track len:", c.get_track_length_ticks())
