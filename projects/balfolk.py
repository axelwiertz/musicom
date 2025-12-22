"""Balfolk Music Generation Project"""
import random
from structures import MusicProject, MusicSection, MusicVoice, MusicTime, MusicPitchClass, PitchRange
from structures import MusicPattern, Cardinality, PatternType, PatternMode, UnitMatrix
from converters.music21_score import section_to_score
from converters.midi_converter import score_to_midifile
from generators import SequentialPatternGenerator
from analysis import score_analyze

MELODY = 0
BASS = 1
# Scale: A minor (C major)
proj = MusicProject(name='Balfolk Project',
                    pattern=MusicPattern('A minor',
                                 Cardinality.HEPTA,
                                 PatternType.SCALE,
                                 PatternMode.minor,
                                 MusicPitchClass.A),
                    sections=[MusicSection('Balfolk Section',
                                  )],
                    voices=[MusicVoice("melody",
                                       PitchRange('C4', 'C6')),
                            MusicVoice("bass",
                                       PitchRange('C2', 'C4'))],
                    time=MusicTime(12, 6, 8, 120), # typical Balfolk rhythm
                    matrix=UnitMatrix(),
                    )

# Bourrée-inspired melody
triad_patterns = [1,2,3,4]

tria_patterns = MusicPattern('Triads',
                             Cardinality.TRIA,
                             PatternType.MAJOR,
                             PatternMode.major,
                             MusicPitchClass.C,
                             4)

#TODO: Implement melody generator based on triad patterns
gen = SequentialPatternGenerator([proj.pattern], 4, 2, 1)
melody_units = gen.generate()

melody_notes = [
    ['C4', 'E4', 'G4'],
    ['D4', 'F4', 'A4'],
    ['E4', 'G4', 'B4'],
    ['F4', 'A4', 'C5']
]

melody_intervals = [1, 1, 1]
melody_durations = [1, 1, 1]


#TODO: Implement more complex rhythmic patterns and variations
# Create melody with rhythmic variation
for i in range(16):  # 4 measures
    # Choose a random melodic fragment
    unit = random.choice(melody_units)
    proj.matrix.data[MELODY, i] = unit

# Create accompaniment (drone/rhythmic support)
bass_notes = ['C3', 'G3']
bass_intervals = [1, 1]
bass_units = []
for i in range(32):  # matching melody length
    unit = random.choice(bass_units)
    proj.matrix.data[BASS, i] = unit


score = section_to_score(proj.sections[0])

# Analyze score
score_analyze(score)
# Save score
score_to_midifile(score, "balfolk.mid")
