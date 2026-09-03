# -*- coding: utf-8 -*-
"""Env probe — musicom nightly composition job."""
import sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
from instrument_registry import VIOLIN, PIANO, FLUTE, DRUM_KIT, CELLO, OBOE
print("registry OK:", VIOLIN, "|", PIANO.midi_program, "|", FLUTE.midi_program)
from workflows.musicom_workflow import produce, compose
print("produce OK")
import inspect
print("produce sig:", inspect.signature(produce))
from structures import MusicUnit, MusicEvent, UnitMatrix
print("structures OK")
from workflows.unitmatrix_composer import UnitMatrixComposer
print("composer OK")
from rules.subset_network import PatternNetwork, patterns_from_degrees
print("subset_network OK")
