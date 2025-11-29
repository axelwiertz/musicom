from typing import List
from music21 import stream
from musicpy import structures
from music21py import m21_to_mpy, mpy_to_m21
from structures import MusicVoice, MusicMatrix
from .m21 import unit_to_stream, stream_to_unit

# Section converters
def voices_to_parts (voices: List[MusicVoice]) -> List[stream.Part]:
    # Convert voices to score parts
    parts = []
    for v in voices:
        for u in v.units:
            parts.append(unit_to_stream(u))
    return parts

def score_to_matrix (score: stream.Score) -> MusicMatrix:
    # Convert score parts to matrix of units
    matrix = MusicMatrix()
    for i, p in enumerate(score.parts):
        matrix.set_unit(i,0, stream_to_unit(p))
        matrix.get_unit(i,0).name = p.partName
    return matrix

def matrix_to_score (matrix: MusicMatrix) -> stream.Score:
    # Convert matrix of units to music21 score
    score = stream.Score()
    for i in range(matrix.rows):
        part = stream.Part()
        for j in range(matrix.cols):
            part.append (unit_to_stream(matrix.get_unit(i,j)))
        score.append(part)
    return score

def score_to_piece (score : stream.Score) -> structures.piece:
    # convert music21 score to musicpy piece
    return m21_to_mpy(score)

def piece_to_score (piece : structures.piece) -> stream.Score:
    # convert musicpy piece to music21 score
    return mpy_to_m21(piece)

