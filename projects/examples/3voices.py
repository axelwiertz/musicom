from structures import MidiInstrument, MusicPitchClass, PitchRange, Cardinality, PatternType, PatternMode
from structures import MusicPattern, MusicProject, MusicSection, MusicUnit, MusicVoice, MusicTime, UnitMatrix
from converters.pitch import name_to_midi
from converters.music21_score import pattern_to_m21scale,score_to_midifile
from converters.music21_musicpy import section_to_score
from analysis import score_analyze

# New composition
project = MusicProject('Three Voices Composition',
    MusicPattern(name="C Major",
                 cardinality=Cardinality.HEPTA,
                 pattern_type=PatternType.SCALE,
                 mode=Mode.major_mode,
                 tonic_pitch_class=MusicPitchClass.C)
)
m21scale = pattern_to_m21scale(project.pattern)
scale_pitches = m21scale.pitches[0:3]
pitches_list = scale_pitches + ["G4", "A4", "B4", "C5"]
print(pitches_list)

# Create three voices for melody and accompaniment
project.voices = [
    MusicVoice('Voice 1', PitchRange(), MidiInstrument.FLUTE),
    MusicVoice('Voice 2', PitchRange(), MidiInstrument.VIOLIN),
    MusicVoice('Accompaniment', PitchRange(MusicPitchClass.C, 3, MusicPitchClass.G, 3), MidiInstrument.BASS)
]

# Define sections
project.sections = [
    MusicSection ('Section A', MusicTime(8,4,4), UnitMatrix(3,2)),
    MusicSection ('Section B', MusicTime(8,4,4), UnitMatrix(3,2))
]
# Define units
project.sections[0].matrix.set_unit(0, 0,
                MusicUnit('1a',
                  name_to_midi(['C5', 'D5', 'E5', 'F5']),
                  [1,1,1,1],
                  [1,1,1,1],
                  [100,100,100,100]))

project.sections[0].matrix.set_unit(0, 1,
                MusicUnit('1b',
                  name_to_midi(['G5', 'A5', 'B4', 'C5']),
                  [1,1,1,1],
                  [1,1,1,1],
                  [100,100,100,100]))
project.sections[0].matrix.set_unit(1, 0,
                MusicUnit('2a',
                  name_to_midi(['C4', 'E4', 'G4']),
                  [1,1,2],
                  [1,1,1],
                  [100,100,100]))
project.sections[0].matrix.set_unit(1, 1,
                MusicUnit('2b',
                  name_to_midi(['F4', 'A4', 'C5']),
                  [1,1,2],
                  [1,1,1],
                  [100,100,100]))
project.sections[0].matrix.set_unit(2, 0,
                MusicUnit('3',
                  name_to_midi(['C3', 'G3']),
                    [2,2],
                    [2,2],
                    [100,100]))

project.sections[0].matrix.repeat_column(0,)

score = section_to_score(project.sections[0])
# Analyze score
score_analyze(score)
# Save score
score_to_midifile(score, "new.mid")