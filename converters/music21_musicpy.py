"""Converters between music21 and MusicPy ."""
from music21 import stream
from musicpy import structures
from music21py import m21_to_mpy, mpy_to_m21


# Section converters
def score_to_piece (score : stream.Score) -> structures.piece:
    # convert music21 score to musicpy piece
    return m21_to_mpy(score)

def piece_to_score (piece : structures.piece) -> stream.Score:
    # convert musicpy piece to music21 score
    return mpy_to_m21(piece)

# Unit converters
def stream_to_chord(stream_in: stream.Stream) -> structures.chord:
    # convert music21 stream to musicpy chord
    return m21_to_mpy(stream_in)

