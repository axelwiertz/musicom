"""
MusicPy - Notebook examples
"""

from musicpy import musicpy as mp, structures

from library import MCMIDI
from musicom import MusicalUnit, Composition



def create_mp_notebook ():
    unit = MusicalUnit()
    unit1, unit2 = MusicalUnit()
    comp = Composition()

    # Compose unit
    unit.chord = structures.chord (notes='C4',
                                  duration=1 / 8,
                                  interval=1 / 8,
                                   volume = 100) * 50
    # Construct piece
    comp.piece = structures.piece(tracks=[structures.track(content=unit.chord, instrument=MCMIDI.PIANO, start_time=1)],
                                  channels=[0],
                                  start_times=[0])

    # Melody creation syntax
    unit.chord += structures.chord('CM7', 3, 1/4, 1/8) ^ 2
    c2 = structures.chord('CM7')
    c3 = structures.chord('CM7', 3)
    unit.chord += structures.chord('CM7', 5)
    unit.chord += structures.chord('CM7', 3,interval=1/4, default_duration=1/8)
    unit.chord += structures.chord('CM7', 3, 1/4)
    unit.chord += structures.chord('CM7', 3, 1/4) ^ 2

    unit.chord = (c2 | c3 * 2 )

    unit.chord = mp.S('C4 major')%(15654321, 0.4)
    unit.chord = structures.scale('C major').pick_chord_by_degree([1, 5])
    unit.chord = structures.scale('C major').get('1,2,3,4,5,6,7,1.1')

    unit.chord = structures.scale('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
    unit.chord = structures.scale('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

    # Chords
    unit.chord = structures.chord('CM7', 3, 1/4, 1/8)^2
    unit.chord = structures.chord('G7sus', 2, 1/4, 1/8)^2
    unit.chord = structures.scale('C4 major')%(15654321, 0.4)
    unit.chord = structures.scale('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

    # Diatonic scale degrees
    unit.chord = structures.scale('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')

    # Scales
    mpscale1 = structures.scale('C Major')
    unit.chord = mpscale1.get('-,1,-,2') % (1 / 2,)
    unit.chord = mpscale1.get('r,1,r,2')

    #1
    unit1.chord = structures.chord ('F2, A2, F3')
    unit1.chord = structures.scale('F major').get('1.-2;3.-2;1.-1')
    #2
    unit2.chord = structures.chord('C2, C3, E3, G3')

    # Melody
    # Musical composition examples page 13
    s1 = structures.scale('F major')
    b1 = s1.get('-') + s1.get('1.-1; 3.-1; 1') + s1.get('5.-1; 5   ; 7.-1;2') + s1.get('1.-1; 5.-1; 1   ;3')
    b2 = s1.get('6.-1; 4.-1; 1   ;4') + s1.get('1.-1; 3.-1; 1   ;5') + s1.get('6.-1; 3.-1; 1   ;6') + s1.get('5.-1; 5.-1; 2   ;7')
    b3 = s1.get('1.-1; 5.-1; 3   ;1.+1')%(1,)
    b21 = s1.get('-') + s1.get('1') + s1.get('7.-1; 2') + s1.get('5.-1; 3')
    b22 = s1.get('6.-1; 4') + s1.get('3.-1; 5') + s1.get('4.-1; 6') + s1.get('2.-1; 7')
    b23 = s1.get('1.-1; 1.+1')%(1,)

    unit1.chord = b1 + b2 + b3
    unit2.chord = b21 + b22 + b23



def create_mp_notebook_percussion ():
    """
    :[] settings blok
    r:n repeat the beat n times with the equally divided unit duration
    R:n repeat the beat n times with the unit duration
    b:n change the duration of the beat to the unit duration * n
    """

    # drum
    drm1 = structures.drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
    drm2 = structures.drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
    drm3 =  structures.drum ('K, K;H, S, H, K, K;H;PH, H;S, H')

    percussion_unit = MusicalUnit ()
    percussion_unit.chord = drm1 + drm2 + drm3


    comp = Composition ()
    comp.piece = structures.piece(percussion_unit.chord, [MCMIDI.PIANO], channels=[MCMIDI.PERCUSSION_CHANNEL_INDEX])





