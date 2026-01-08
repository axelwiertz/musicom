"""Balfolk Music Generation Project"""
import random
from structures import MusicProject, MusicSection, MusicVoice, MusicTimeGrid, MusicPitchClass, PitchRange
from structures import MusicPitchClassPattern, Cardinality, PatternType, PatternRotation, UnitMatrix
from converters.music21_score import project_to_score
from converters.midi_converter import score_to_midifile
from generators import SequentialPatternGenerator
from analysis import score_analyze

MELODY = 0
BASS = 1
# Scale: A minor (C major)
proj = MusicProject(name='Balfolk',
                    pattern=MusicPitchClassPattern('A minor',
                                 Cardinality.HEPTA,
                                 PatternType.SCALE,
                                 PatternRotation.minor,
                                 MusicPitchClass.A),
                    sections=[MusicSection('Balfolk Section',
                                  )],
                    voices=[MusicVoice("melody",
                                       PitchRange('C4', 'C6')),
                            MusicVoice("bass",
                                       PitchRange('C2', 'C4'))],
                    time=MusicTimeGrid(ticks_per_cycle=12, beats_per_cycle=6, beat_note=8), # typical Balfolk rhythm
                    matrix=UnitMatrix(),
                    )

# Bourrée-inspired melody
triad_patterns = [1,2,3,4]

tria_pattern = MusicPitchClassPattern(name='Triads',
                             cardinality=Cardinality.TRIA,
                             pattern_type=PatternType.MAJOR,
                             rotation=PatternRotation.major,
                             tonic_pitch_class=MusicPitchClass.C,
                             tonic_octave=4)

gen = SequentialPatternGenerator(patterns=[tria_pattern],
                             timesteps_in=2,
                             volume_in=100)
melody_units = gen.generate()

melody_notes = [
    ['C4', 'E4', 'G4'], # C major triad
    ['D4', 'F4', 'A4'], #
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


score = project_to_score(proj)

# Analyze score
score_analyze(score)
# Save score
score_to_midifile(score, "balfolk.mid")
