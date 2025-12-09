from base.instrument import MidiInstrument
from musicpy import musicpy as mp, structures
# Compose unit
chord = structures.chord (notes='C4',
                              duration=1 / 8,
                              interval=1 / 8,
                               volume = 100) * 50
# Construct piece
piece = structures.piece(tracks=[structures.track(content=chord, instrument=MidiInstrument.PIANO, start_time=1)],
                              channels=[0],
                              start_times=[0])

# Melody creation syntax
# Chords
chord += structures.chord(notes='CM7',duration= 3,interval= 1/4,default_duration= 1/8) ^ 2
c2 = structures.chord('CM7')
c3 = structures.chord('CM7', 3)
chord = (c2 | c3 * 2 )
chord += structures.chord('CM7', 3,interval=1/4, default_duration=1/8)


chord = mp.S('C4 major')%(15654321, 0.4)
chord = structures.scale('C major').pick_chord_by_degree([1, 5])
chord = structures.scale('C major').get('1,2,3,4,5,6,7,1.1')

chord = structures.scale('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
chord = structures.scale('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

chord = structures.chord('CM7', 3, 1/4, 1/8)^2
chord = structures.chord('G7sus', 2, 1/4, 1/8)^2
chord = structures.scale('C4 major')%(15654321, 0.4)
chord = structures.scale('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

# Diatonic Scales
chord = structures.scale('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')

mpscale1 = structures.scale('C Major')
chord = mpscale1.get('-,1,-,2') % (1 / 2,)
chord = mpscale1.get('r,1,r,2')

#1
chord1 = structures.chord ('F2, A2, F3')
chord2 = structures.scale('F major').get('1.-2;3.-2;1.-1')
#2
chord3 = structures.chord('C2, C3, E3, G3')

# Melody
# Musical composition examples page 13
s1 = structures.scale('F major')
b1 = s1.get('-') + s1.get('1.-1; 3.-1; 1') + s1.get('5.-1; 5   ; 7.-1;2') + s1.get('1.-1; 5.-1; 1   ;3')
b2 = s1.get('6.-1; 4.-1; 1   ;4') + s1.get('1.-1; 3.-1; 1   ;5') + s1.get('6.-1; 3.-1; 1   ;6') + s1.get('5.-1; 5.-1; 2   ;7')
b3 = s1.get('1.-1; 5.-1; 3   ;1.+1')%(1,)
b21 = s1.get('-') + s1.get('1') + s1.get('7.-1; 2') + s1.get('5.-1; 3')
b22 = s1.get('6.-1; 4') + s1.get('3.-1; 5') + s1.get('4.-1; 6') + s1.get('2.-1; 7')
b23 = s1.get('1.-1; 1.+1')%(1,)

chord_b = b1 + b2 + b3
chord_bb = b21 + b22 + b23
