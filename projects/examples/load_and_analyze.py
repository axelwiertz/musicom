"""Example script to load a MIDI file, convert it to a music21 score, and analyze it."""
from converters.music21_score import midifile_to_score, score_to_visual
from converters.music21_musicpy import score_to_section
from analysis import score_analyze

score = midifile_to_score('O_Holy_Night_choir_SATB__Adolphe_Adam.mid')
section = score_to_section(score)
score_analyze (score)
score_to_visual(score)
