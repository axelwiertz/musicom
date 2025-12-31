"""Example script to load a MIDI file, convert it to a music21 score, and analyze it."""
from converters.midi_converter import midifile_to_score
from converters.visual import score_to_visual
from converters.music21_score import score_to_project
from analysis import score_analyze

score = midifile_to_score('O_Holy_Night_choir_SATB__Adolphe_Adam.mid')
project = score_to_project(score)
score_analyze (score)
score_to_visual(score)