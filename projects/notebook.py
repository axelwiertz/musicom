"""
MusicPy - Notebook examples
"""

from structures.instrument import MidiInstrument
from base.twelvetone import PitchClass
from structures import MusicUnit
from structures.pattern import MusicPattern
from rules.diatonic import Diatonic
from music21 import converter, instrument
from musicpy import structures



def m21_tiny_notebook():
    unit = MusicUnit()
    unit.stream = converter.parse('tinynotation: 4/4 c5 r r c5 r r c5 r')
    unit.instrument = instrument.Piano()



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

    percussion_unit = MusicUnit()
    percussion_unit.chord = drm1 + drm2 + drm3

    comp = MusicComposition()
    comp.piece = structures.piece(percussion_unit.chord,
                                  [MidiInstrument.PIANO],

    comp = MusicComposition ()
    return comp


    scale7 = MusicPattern(Cardinality.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode)

def standard_notebook ():

    scale7 = MusicPattern (Cardinality.HEPTA, Diatonic.SCALE, PitchClass.C , Diatonic.major_mode)
        # (TETRA,1,MAJOR7), (TETRA,2,MAJOR7), (TETRA,6,MAJOR7), (TETRA,2,MAJOR7)
        ['I7', 'II7', 'VI7', 'II7'],
    # TETRADIC PROGRESSIONS
    # (TETRA,1,MAJOR7), (TETRA,2,MAJOR7), (TETRA,6,MAJOR7), (TETRA,2,MAJOR7)
        ['i7', 'II7', 'isus', 'IVsus'],
    # 1, 2, 1, 4  i II bi bIV
    # (TETRA,1,MINOR), (TETRA,2,MAJOR), (TETRA,1,SUS2), (TETRA,4,SUS2)
        # 1, 5, 6, 5  i v VI V
    # 1, 6, 1, 6  I VI I VI
        # 1, 2, 1, 2  I II I II
    # 1, 5, 6, 5  i v VI V
        # 1,2,4,5  i II iv V
    # 1, 2, 1, 2  I II I II
    ]
    # 1,2,4,5  i II iv V
    scale7 = MusicPattern(Cardinality.HEPTA, Diatonic.SCALE, TwelveTET.A, Diatonic.minor_mode)
        ]


    scale7 = MusicPattern(Cardinality.HEPTA, Diatonic.SCALE, TwelveTET.A, Diatonic.minor_mode)
    comp = MusicComposition('Fantasy C major')

    scale7 = MusicPattern(Cardinality.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode)
    sectionA = MusicSection('A')
    sectionB = MusicSection('B')
    scale7 = MusicPattern(Cardinality.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode)
                            sections=[sectionA, sectionA, sectionB, sectionA])
    
    # (TRIA,2,MAJOR), (TRIA,5,MAJOR), (TRIA,1,MAJOR)
                       sections = [sectionA, sectionA, sectionB, sectionA])
    bossa_nova_progression2 = ['Imaj7', 'II7', 'iim7']

    flamenco_progression = (1, 7, 6, 5)

    loungejazz_progression1 = (7, 3, 6, 2, 5, 1)

    return comp
    loungejazz_progression1 = (4, 2, 5, 1),
