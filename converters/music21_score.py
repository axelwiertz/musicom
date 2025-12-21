"""Converters between music21 and other structures."""
from structures import MusicMatrix, MusicSection
from converters.music21_stream import stream_to_unit, matrix_row_to_stream
from converters.time import meter_to_time, time_to_meter, time_to_tempo
from music21 import stream

# Score converters

def score_to_section(score: stream.Score) -> MusicSection:
    # Convert score parts to matrix of units
    matrix = MusicMatrix(len(score.parts), 1)
    time = meter_to_time(score.timeSignature, 4, score.metronomeMarkBoundaries()[0][2].number)
    matrix.time = time
    section = MusicSection(score.metadata.title or 'Untitled', None, matrix)

    for i, p in enumerate(score.parts):
        matrix.set_unit(i,0, stream_to_unit(p, time))
        matrix.get_unit(i,0).name = p.partName

    return section


def section_to_score(section : MusicSection) -> stream.Score:
    # Convert section to m21 score
    score = stream.Score()
    score.insert(0, time_to_meter(section.time))
    score.insert(0, time_to_tempo(section.time))

    # Convert section matrix to m21 parts
    for i in range(section.matrix.rows):
        part_ = stream.Part()
        stream_ = matrix_row_to_stream (section.matrix, i, section.time)
        part_.append(stream_)
        part_.partName = f"Voice {i+1}"
        score.append(part_)

    return score
