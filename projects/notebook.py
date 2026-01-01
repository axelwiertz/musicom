"""
MusicPy - Notebook examples
"""

from structures import MusicProject, MusicSection, MusicTimeGrid
from structures import MusicPitchClass, MusicPitchPattern, Cardinality, PatternType, PatternMode
from converters.music21_stream import stream_to_unit
from converters.pypianoroll_converter import musicunit_to_track
from music21 import converter
from musicpy import musicpy, structures


def m21_tiny_notebook():
    stream = converter.parse('tinynotation: 4/4 c5 r r c5 r r c5 r')
    unit = stream_to_unit(stream, time=MusicTimeGrid(16, 4, 4, 120))
    roll = musicunit_to_track(unit)
    roll.plot()


def mp_percussion_notebook():
    """
    :[] settings blok
    r:n repeat the beat n times with the equally divided unit duration
    R:n repeat the beat n times with the unit duration
    b:n change the duration of the beat to the unit duration * n
    """

    # drum patterns
    drm1 = structures.drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
    drm2 = structures.drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
    drm3 = structures.drum('K, K;H, S, H, K, K;H;PH, H;S, H')

    percussion_chord = drm1 + drm2 + drm3

    piece = structures.piece(percussion_chord)
    musicpy.play(piece, wait=True)


def standard_notebook ():

    # subpatterns for common progressions
    # (TETRA,1,MAJOR7), (TETRA,2,MAJOR7), (TETRA,6,MAJOR7), (TETRA,2,MAJOR7)
    #    ['I7', 'II7', 'VI7', 'II7'],
    # TETRADIC PROGRESSIONS
    # (TETRA,1,MAJOR7), (TETRA,2,MAJOR7), (TETRA,6,MAJOR7), (TETRA,2,MAJOR7)
    #    ['i7', 'II7', 'isus', 'IVsus'],
    # 1, 2, 1, 4  i II bi bIV
    # (TETRA,1,MINOR), (TETRA,2,MAJOR), (TETRA,1,SUS2), (TETRA,4,SUS2)
        # 1, 5, 6, 5  i v VI V
    # 1, 6, 1, 6  I VI I VI
        # 1, 2, 1, 2  I II I II
    # 1, 5, 6, 5  i v VI V
        # 1,2,4,5  i II iv V
    # 1, 2, 1, 2  I II I II
    # 1,2,4,5  i II iv V

    proj = MusicProject(name='Fantasy A minor',
                        pattern=MusicPitchPattern("A minor", Cardinality.HEPTA, PatternType.SCALE,
                                                  PatternMode.minor, MusicPitchClass.A))

    proj = MusicProject(name='Fantasy C major',
                        pattern=MusicPitchPattern("C major", Cardinality.HEPTA, PatternType.SCALE,
                                                  PatternMode.major, MusicPitchClass.C),
                        sections=[MusicSection('A'), MusicSection('B')])

    # (TRIA,2,MAJOR), (TRIA,5,MAJOR), (TRIA,1,MAJOR)
    bossa_nova_progression2 = ['Imaj7', 'II7', 'iim7']

    flamenco_progression = (1, 7, 6, 5)

    loungejazz_progression1 = (7, 3, 6, 2, 5, 1)

    loungejazz_progression1 = (4, 2, 5, 1),
