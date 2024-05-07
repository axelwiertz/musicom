'''
Part template
'''
import os
# Initialize
import time
import musicpy as mp
from musicpy import *
from musicpy.daw import *



# Chords
c1 = C('CM7', 3, 1/4, 1/8)^2
c2 = C('G7sus', 2, 1/4, 1/8)^2

# Melody
m1 = chord('B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, G#3, B3, B3, C#4, E4, F#4, B3, B3, F#4, F#4, F#4, G#4, F#4, E4, E4', 1/8, 1/8)
play (m1, wait=True)


print (m1.notes)
print (m1.interval)


# Instruments
# Play all MIDI instruments
''' 
for i in range(1, 127):
    play(c1, bpm=100, instrument=i)
    print i
    time.sleep(3)
'''



# Create piece
# p1 = P(tracks=[c1, c1],channels=[0, 1], instruments=[1,10])

# DAW
curpath = os.getcwd() + '\\Soundfont\\'
daw1 = daw(3, name='Song 1')
daw1.load(0, curpath + 'Emu 9ftgrand.sf2')
#daw1.load(1, curpath + 'R-piano.sf2')
p1 = P(tracks=[m1],channels=[0])
print (p1)
daw1.play(p1, wait=True)
