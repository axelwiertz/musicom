import numpy as np
from structures import MidiInstrument, MusicPitchClass, PatternType, PatternRotation
from structures import MusicPitchClassPattern, MusicProject, MusicSection, MusicUnit, MusicVoice, MusicTimeGrid, UnitMatrix
from converters.music21_pattern import pattern_to_m21scale
from converters.midi_converter import score_to_midifile
from converters.music21_score import project_to_score
from analysis import score_analyze

# New composition
project = MusicProject(
    name='Three Voices Composition',
    # Define musical pattern: C Major scale
    pitch_pattern=MusicPitchClassPattern(
        name="C Major",
        definition=PatternType.HEPTATONIC,
        rotation=PatternRotation.major,
        initial=MusicPitchClass.C
    ),
    # Define time signature and length: 16 ticks per cycle, 4 beats per cycle, quarter note gets the beat
    time_grid=MusicTimeGrid(ticks_per_cycle=16, beats_per_cycle=4, beat_note=4),
    # Create three voices for melody and accompaniment
    voices=[
        MusicVoice(name='Voice 1', row_index=0, midi_instrument=MidiInstrument.FLUTE),
        MusicVoice(name='Voice 2', row_index=1, midi_instrument=MidiInstrument.VIOLIN),
        MusicVoice(name='Accompaniment', row_index=2, midi_instrument=MidiInstrument.BASS)
    ],
    # Define sections
    sections=[
        MusicSection('Section A'),
        MusicSection('Section B')
    ],
    matrix=UnitMatrix(shape=(3, 2))  # 3 rows (voices), 2 columns (sections)
)

# Pattern = scale
m21scale = pattern_to_m21scale(project.pitch_pattern)

# Define units for voice 1 (Flute melody)
# Section A: First three notes of C Major scale in octave 5
pitches = project.pitch_pattern.get_pitches_in_octave(5)[0:3]
project.matrix.set_unit(
    pos=(0, 0),
    unit=MusicUnit(time_grid=project.time_grid, pitches=pitches)
)

# Section B: Notes 5-7 of C Major scale in octave 5
pitches = project.pitch_pattern.get_pitches_in_octave(5)[4:7]
project.matrix.set_unit(
    pos=(0, 1),
    unit=MusicUnit(time_grid=project.time_grid, pitches=pitches)
)

# Define chords for voice 2 (Violin harmony)
# Section A: C Major triad
c_major_triad = MusicPitchClassPattern(
    name="C Major Chord",
    definition=PatternType.MAJOR,
    initial=MusicPitchClass.C
)
pitches = c_major_triad.get_pitches_in_octave(4)
project.matrix.set_unit(
    pos=(1, 0),
    unit=MusicUnit(
        time_grid=project.time_grid,
        events=np.asarray([
            [pitches[0], 1, 4, 100],   # C note: start tick 1, end tick 4, velocity 100
            [pitches[1], 5, 8, 100],   # E note: start tick 5, end tick 8, velocity 100
            [pitches[2], 9, 16, 100]   # G note: start tick 9, end tick 16, velocity 100
        ])
    )
)

# Section B: F Major triad
f_major_triad = MusicPitchClassPattern(
    name="F Major Chord",
    definition=PatternType.MAJOR,
    initial=MusicPitchClass.F
)
pitches = f_major_triad.get_pitches_in_octave(4)
project.matrix.set_unit(
    pos=(1, 1),
    unit=MusicUnit(
        time_grid=project.time_grid,
        events=np.asarray([
            [pitches[0], 1, 4, 100],   # F note: start tick 1, end tick 4, velocity 100
            [pitches[1], 5, 8, 100],   # A note: start tick 5, end tick 8, velocity 100
            [pitches[2], 9, 16, 100]   # C note: start tick 9, end tick 16, velocity 100
        ])
    )
)

# Define bass units (Accompaniment)
# Section A: C and G (perfect fifth from C)
pattern_bass_c = MusicPitchClassPattern(
    name="Bass Pattern C",
    definition=PatternType.PERFECT_FIFTH,
    initial=MusicPitchClass.C
)
bass_pitches = pattern_bass_c.get_pitches_in_octave(3)
project.matrix.set_unit(
    pos=(2, 0),
    unit=MusicUnit(
        time_grid=project.time_grid,
        events=np.asarray([
            [bass_pitches[0], 1, 8, 100],   # C note: start tick 1, end tick 8, velocity 100
            [bass_pitches[1], 9, 16, 100]   # G note: start tick 9, end tick 16, velocity 100
        ])
    )
)

# Section B: F and C (perfect fifth from F)
pattern_bass_f = MusicPitchClassPattern(
    name="Bass Pattern F",
    definition=PatternType.PERFECT_FIFTH,
    initial=MusicPitchClass.F
)
bass_pitches = pattern_bass_f.get_pitches_in_octave(3)
project.matrix.set_unit(
    pos=(2, 1),
    unit=MusicUnit(
        time_grid=project.time_grid,
        events=np.asarray([
            [bass_pitches[0], 1, 8, 100],   # F note: start tick 1, end tick 8, velocity 100
            [bass_pitches[1], 9, 16, 100]   # C note: start tick 9, end tick 16, velocity 100
        ])
    )
)

# Convert project to music21 score
score = project_to_score(project)

# Analyze score
print("Analyzing score...")
score_analyze(score)

# Save score to MIDI file
print("Saving MIDI file...")
score_to_midifile(score, "three_voices.mid")
print("MIDI file saved as 'three_voices.mid'")
