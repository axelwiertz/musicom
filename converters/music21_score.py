"""Converters between music21 and other structures."""
from structures import MusicProject, MusicTimeGrid, UnitMatrix, MusicSection, MusicVoice, MusicLinearTime
from converters.music21_stream import stream_to_unit, matrix_row_to_stream
from converters.music21_pattern import key_to_pattern
from music21 import stream, meter, tempo

# Score converters

def score_to_project(score: stream.Score) -> MusicProject:
    """Convert music21 Score to MusicProject."""
    # Get time signature and tempo from score
    if score.timeSignature is not None:
        # get score smallest note duration to determine ticks per cycle
        ival = score.timeSignature.ratioString.split('/')
        beats_per_cycle = int(ival[0])
        beat_note = int(ival[1])
        # Determine ticks per cycle based on smallest note duration in the score
        smallest_duration = min(n.quarterLength for n in score.recurse().notesAndRests)
        # Here we define ticks per cycle as the number of divisions of the beat note
        ticks_per_cycle = int((4 / beat_note) * beats_per_cycle * (1 / smallest_duration))
        # Here we assume the first metronome mark applies to the whole score
        time_grid = MusicTimeGrid(ticks_per_cycle=ticks_per_cycle,
                                    beats_per_cycle=beats_per_cycle,
                                    beat_note=beat_note)

        lineartime = MusicLinearTime(time_grid=time_grid,
            bpm=score.metronomeMarkBoundaries()[0][2].number)
    else:
        time_grid = MusicTimeGrid()
        lineartime = MusicLinearTime(time_grid=time_grid,)

    score_key = score.analyze('key')

    # Create project
    project = MusicProject(name=score.metadata.title or 'Untitled',
                           pitch_pattern=key_to_pattern(score_key),
                           sections=[MusicSection('From Score')],
                           matrix=UnitMatrix(shape=(len(score.parts), 1)),
                           voices=[],
                           time_grid=time_grid,
                           time=lineartime,)

    # Convert m21 parts to matrix rows (voices)
    for i, p in enumerate(score.parts):
        # Add voice
        project.voices.append (MusicVoice(
            name=p.partName or f'Voice {i+1}',
            midi_instrument=p.getInstrument().midiProgram,
            row_index=i,))
        # Convert part stream to matrix row
        project.matrix.set_unit(pos=(i,0), unit=stream_to_unit(p, time_grid))

    return project


def project_to_score(project: MusicProject) -> stream.Score:
    """Convert MusicProject to music21 Score."""
    score = stream.Score()
    # Set time signature
    if project.time_grid is not None:
        score.insert(0,
                     meter.TimeSignature(str(project.time_grid.beats_per_cycle) + '/'
                                        + str(project.time_grid.beat_note)))
    # Set tempo
    if project.time is not None:
        score.insert(0, tempo.MetronomeMark(number=project.time.bpm))

    # Convert matrix rows to m21 parts
    for i, v in enumerate(project.voices):
        # Create part for each voice
        part_ = stream.Part()
        stream_ = matrix_row_to_stream (project.matrix, i, project.time_grid)
        part_.append(stream_)
        part_.partName = v.name
        score.append(part_)

    return score

