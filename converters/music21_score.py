"""Converters between music21 and other structures."""
from structures import MusicProject, MusicTimeGrid, UnitMatrix, MusicSection, MusicVoice
from converters.music21_stream import stream_to_unit, matrix_row_to_stream
from converters.music21_pattern import key_to_pattern
from converters.time import meter_to_time, time_to_meter, time_to_tempo
from music21 import stream

# Score converters

def score_to_project(score: stream.Score) -> MusicProject:
    """Convert music21 Score to MusicProject."""
    # Get time signature and tempo from score
    if score.timeSignature is not None:
        time = meter_to_time(score.timeSignature, 4, score.metronomeMarkBoundaries()[0][2].number)
    else:
        time = MusicTimeGrid.default_time()

    score_key = score.analyze('key')

    # Create project
    project = MusicProject(name=score.metadata.title or 'Untitled',
                           pattern=key_to_pattern(score_key),
                           sections=[MusicSection('From Score')],
                           matrix=UnitMatrix(shape=(len(score.parts), 1)),
                           voices=[],
                           time=time)

    # Convert m21 parts to matrix rows (voices)
    for i, p in enumerate(score.parts):
        # Add voice
        project.voices.append (MusicVoice(
            name=p.partName or f'Voice {i+1}',
            midi_instrument=p.getInstrument().midiProgram,
            row_index=i,))
        # Convert part stream to matrix row
        project.matrix.set_unit(i,0, stream_to_unit(p, time))

    return project


def project_to_score(project: MusicProject) -> stream.Score:
    """Convert MusicProject to music21 Score."""
    score = stream.Score()
    score.insert(0, time_to_meter(project.time))
    score.insert(0, time_to_tempo(project.time))

    # Convert matrix rows to m21 parts
    for i, v in enumerate(project.voices):
        # Create part for each voice
        part_ = stream.Part()
        stream_ = matrix_row_to_stream (project.matrix, i, project.time)
        part_.append(stream_)
        part_.partName = v.name
        score.append(part_)

    return score

