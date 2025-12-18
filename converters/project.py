"""Converters between music21 Score and MusicPy MusicSection and piece."""
from structures import MusicSection, MusicTime, MusicMatrix, MusicPattern
from music21 import stream
from musicpy import structures
from music21py import m21_to_mpy, mpy_to_m21
from .time import meter_to_time
from .music21_converter import stream_to_unit, matrix_row_to_stream, key_to_pattern

# Section converters
def score_to_pattern(score: stream.Score) -> MusicPattern:
    key = score.analyze('key')
    return key_to_pattern(key)

def score_to_time(score: stream.Score, timesteps: int) -> MusicTime:
    if score.timeSignature is not None:
        time = meter_to_time(score.timeSignature, timesteps,
                             score.metronomeMarkBoundaries()[0][2].number)
    else:
        time = MusicTime(4,4,4)
    return time


def score_to_section(score: stream.Score) -> MusicSection:
    # Convert score parts to matrix of units
    matrix = MusicMatrix(len(score.parts), 1)

    section = MusicSection(score.metadata.title or 'Untitled', None, matrix)

    for i, p in enumerate(score.parts):
        matrix.set_unit(i,0, stream_to_unit(p))
        matrix.get_unit(i,0).name = p.partName

    return section


def section_to_score(section : MusicSection) -> stream.Score:
    # Convert section to m21 score
    score = stream.Score()
    # Convert section matrix to m21 parts
    for i in range(section.matrix.rows):
        part_ = stream.Part()
        stream_ = matrix_row_to_stream (section.matrix, i)
        part_.append(stream_)
        part_.partName = f"Voice {i+1}"
        score.append(part_)

    return score

# Piece converters

def score_to_piece (score : stream.Score) -> structures.piece:
    # convert music21 score to musicpy piece
    return m21_to_mpy(score)

def piece_to_score (piece : structures.piece) -> stream.Score:
    # convert musicpy piece to music21 score
    return mpy_to_m21(piece)
