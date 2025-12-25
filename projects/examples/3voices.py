from pypianoroll import pitch_range

from structures import MidiInstrument, MusicPitchClass, PitchRange, Cardinality, PatternType, PatternMode
from structures import MusicPattern, MusicProject, MusicSection, MusicUnit, MusicVoice, MusicTime, UnitMatrix
from converters.pitch import name_to_midi
from converters.music21_pattern import pattern_to_m21scale
from converters.midi_converter import score_to_midifile
from converters.music21_score import project_to_score
from analysis import score_analyze

# New composition
project = MusicProject(name='Three Voices Composition',
    # Define musical pattern: C Major scale
    pattern=MusicPattern(name="C Major",
                 cardinality=Cardinality.HEPTA,
                 pattern_type=PatternType.SCALE,
                 mode=PatternMode.major,
                 tonic_pitch_class=MusicPitchClass.C),
    # Define time signature and length
    time=MusicTime(16,4,4),
    # Create three voices for melody and accompaniment
    voices=[
        MusicVoice(name='Voice 1', row_index=0,
                   pitch_range=PitchRange(), midi_instrument=MidiInstrument.FLUTE),
        MusicVoice(name='Voice 2', row_index=1,
                   pitch_range=PitchRange(), midi_instrument=MidiInstrument.VIOLIN),
        MusicVoice(name='Accompaniment', row_index=2,
               pitch_range=PitchRange(MusicPitchClass.C, 3, MusicPitchClass.G, 3),
               midi_instrument=MidiInstrument.BASS)
            ],
    # Define sections
    sections = [
        MusicSection ('Section A'),
        MusicSection ('Section B')
            ],
    matrix=UnitMatrix(3,2)  # 3 rows (voices), 2 columns (time)
    )

# Get scale pitches
m21scale = pattern_to_m21scale(project.pattern)
scale_pitches = m21scale.pitches[0:3]
pitches_list = scale_pitches + ["G4", "A4", "B4", "C5"]
print(pitches_list)

# Define units
project.matrix.set_unit(0, 0,
                MusicUnit('1a',
                  name_to_midi(['C5', 'D5', 'E5', 'F5']),
                  [1,1,1,1],
                  [1,1,1,1],
                  [100,100,100,100]))

project.matrix.set_unit(0, 1,
                MusicUnit('1b',
                  name_to_midi(['G5', 'A5', 'B4', 'C5']),
                  [1,1,1,1],
                  [1,1,1,1],
                  [100,100,100,100]))
project.matrix.set_unit(1, 0,
                MusicUnit('2a',
                  name_to_midi(['C4', 'E4', 'G4']),
                  [1,1,2],
                  [1,1,1],
                  [100,100,100]))
project.matrix.set_unit(1, 1,
                MusicUnit('2b',
                  name_to_midi(['F4', 'A4', 'C5']),
                  [1,1,2],
                  [1,1,1],
                  [100,100,100]))
project.matrix.set_unit(2, 0,
                MusicUnit('3',
                  name_to_midi(['C3', 'G3']),
                    [2,2],
                    [2,2],
                    [100,100]))

project.matrix.repeat_column(0,)

score = project_to_score(project.sections[0])
# Analyze score
score_analyze(score)
# Save score
score_to_midifile(score, "new.mid")