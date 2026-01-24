import numpy as np
from structures import MidiInstrument, MusicPitchClass, PatternType, PatternRotation
from structures import MusicPitchClassPattern, MusicProject, MusicSection, MusicUnit, MusicVoice, MusicTimeGrid, UnitMatrix
from converters.music21_pattern import pattern_to_m21scale
from converters.midi_converter import score_to_midifile
from converters.music21_score import project_to_score
from analysis import score_analyze

# New composition
project = MusicProject(name='Three Voices Composition',
    # Define musical pattern: C Major scale
    pitch_pattern=MusicPitchClassPattern(name="C Major",
                 definition=PatternType.HEPTATONIC,
                 rotation=PatternRotation.major,
                 initial=MusicPitchClass.C),
    # Define time signature and length: 16 ticks per cycle, 4 beats per cycle, quarter note gets the beat
    time_grid=MusicTimeGrid(ticks_per_cycle=16,beats_per_cycle=4,beat_note=4),
    # Create three voices for melody and accompaniment
    voices=[
        MusicVoice(name='Voice 1', row_index=0, midi_instrument=MidiInstrument.FLUTE),
        MusicVoice(name='Voice 2', row_index=1, midi_instrument=MidiInstrument.VIOLIN),
        MusicVoice(name='Accompaniment', row_index=2, midi_instrument=MidiInstrument.BASS)
            ],
    # Define sections
    sections = [
        MusicSection ('Section A'),
        MusicSection ('Section B')
            ],
    matrix=UnitMatrix(shape=(3,2))  # 3 rows (voices), 2 columns (time)
    )

# Pattern = scale
m21scale = pattern_to_m21scale(project.pitch_pattern)

# Define units for voice 1
pitches = project.pitch_pattern.get_pitches_in_octave(5)[0:3]
project.matrix.set_unit(pos=(0, 0),
                unit=MusicUnit(time_grid=project.time_grid,
                                pitches=pitches,))

pitches = project.pitch_pattern.get_pitches_in_octave(5)[4:7]
project.matrix.set_unit(pos=(0, 1),
                unit=MusicUnit(time_grid=project.time_grid,
                                pitches=pitches))

# Define chords for voice 2
c_major_triad = MusicPitchClassPattern (
    name="C Major Chord",
    definition=PatternType.MAJOR,
    initial=MusicPitchClass.C)
pitches = c_major_triad.get_pitches_in_octave(4)
project.matrix.set_unit(pos=(1, 0),unit=
                MusicUnit(time_grid=project.time_grid,
                          events=np.asarray([[pitches[0],1,4,100],
                                  [pitches[1],5,8,100],
                                  [pitches[2],9,16,100]])
                ))
f_major_triad = MusicPitchClassPattern (
    name="F Major Chord",
    definition=PatternType.MAJOR,
    initial=MusicPitchClass.F)
pitches = f_major_triad.get_pitches_in_octave(4)

project.matrix.set_unit(pos=(1, 1),unit=
                MusicUnit(time_grid=project.time_grid,
                          events=np.asarray([[pitches[0],1,4,100],
                                  [pitches[1],5,8,100],
                                  [pitches[2],9,16,100]])
                        ))
pattern_bass = MusicPitchClassPattern (
    name="Bass Pattern",
    definition=PatternType.PERFECT_FIFTH,
    initial=MusicPitchClass.C)
bass_pitches = pattern_bass.get_pitches_in_octave(3)
# Define bass units
project.matrix.set_unit(pos=(2, 0),unit=
                MusicUnit(time_grid=project.time_grid,
                 events=np.asarray([[bass_pitches[0],1,8,100],
                        [bass_pitches[1],9,16,100]])
                ))
project.matrix.repeat_column(0,)

score = project_to_score(project)
# Analyze score
score_analyze(score)
# Save score
score_to_midifile(score, "new.mid")