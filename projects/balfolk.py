"""Balfolk Music Generation Project"""
import random
from structures import MusicProject, MusicSection, MusicPattern, MusicVoice, MusicTime, MusicPitchClass, PitchRange, Cardinality, PatternType, PatternMode
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
                                 PatternMode.minor_mode,
                                 MusicPitchClass.A),
                    sections=[MusicSection('Balfolk Section',
                                  MusicTime(12, 6, 8, 120))], # typical Balfolk rhythm
                    voices=[MusicVoice("melody",
                                       PitchRange('C4', 'C6')),
                            MusicVoice("bass",
                                       PitchRange('C2', 'C4'))]
                    )

# Bourrée-inspired melody
triad_patterns = [1,2,3,4]

melody_notes = [
    ['C4', 'E4', 'G4'],
    ['D4', 'F4', 'A4'],
    ['E4', 'G4', 'B4'],
    ['F4', 'A4', 'C5']
]
melody_intervals = [1, 1, 1]
melody_onsets = [1, 1, 1]
melody_durations = [1, 1, 1]

#TODO: Implement melody generator based on triad patterns
gen = SequentialPatternGenerator(triad_patterns, 4, 2, 1, 80)
units = gen.generate()

#TODO: Implement more complex rhythmic patterns and variations
# Create melody with rhythmic variation
for i in range(16):  # 4 measures
    # Choose a random melodic fragment
    fragment = random.choice(melody_notes)

    # Arpeggiate chords
    for note_name in fragment:
        n = note.Note(note_name)
        n.duration.type = 'eighth'
        proj.voices[MELODY].append(n)

# Create accompaniment (drone/rhythmic support)
bass_notes = ['C3', 'G3']
for i in range(32):  # matching melody length
    bass_note = note.Note(random.choice(bass_notes))
    bass_note.duration.type = 'eighth'
    proj.voices[BASS].append(bass_note)

score = section_to_score(proj.sections[0])

# Analyze score
score_analyze(score)
# Save score
score_to_midifile(score, "balfolk.mid")
