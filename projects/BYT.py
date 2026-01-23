""" Big Yellow Taxi Music Project """
from structures import MusicPitchClass, PatternType, PatternRotation, UnitMatrix, MusicLinearTime
from structures import MusicProject, MusicPitchClassPattern, MusicTimeGrid, MusicUnit
from converters.pitch import name_to_midi
from converters.musicpy_converter import unit_to_sound

# Create project
proj = MusicProject(name='Big yellow taxi',
                    pitch_pattern=MusicPitchClassPattern(name='B flat major',
                               definition=PatternType.HEPTATONIC,
                               rotation=PatternRotation.major,
                               initial=MusicPitchClass.B_FLAT),
                    time_grid=MusicTimeGrid(ticks_per_cycle=8,beats_per_cycle=4,beat_note=4),
                    matrix=UnitMatrix(shape=(1,1)),
                    )

# Create unit
unit = MusicUnit(pitches=name_to_midi (name=['B3', 'C#4', 'E4', 'E4', 'F#4', 'C#4', 'E4', 'E4', 'F#4', 'E4', 'G#3', 'B3', 'B3', 'C#4',
    'E4', 'F#4', 'B3', 'B3', 'F#4', 'F#4', 'F#4', 'G#4', 'F#4', 'E4', 'E4'])
    )

# Set unit in project matrix
proj.matrix.set_unit(0,0,unit)


# Convert unit to sound
unit_to_sound(unit=unit, time=MusicLinearTime(bpm=100) )

