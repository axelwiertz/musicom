'''
Music Instruments
'''
import os
# Initialize
import time
import musicpy as mp
from musicpy import *
from musicpy.daw import *

# Chords
chd01 = S('C major').get('1,2,3,4,5,6,7,1.1')

# Melody
chdMelody = [chd01, chd01, chd01]

# Tracks

# Piece
pce01 = P(tracks=[chdMelody[0], chdMelody[1], chdMelody[2]],channels=[0, 1, 2])
print (pce01)


# Instruments
# Play all MIDI instruments
'''
for i in range(1, 127):
    print ('MIDI instrument ' + str(i))
    play(chdMelody01, bpm=150, instrument=i, wait=True)
'''


strSFpath = os.getcwd() + '\\Soundfont\\'
# Instrument library
dctInstr = {}
dctInstr['Piano'] = ['Piano_NineFootGrand.sf2', 'Piano_RolandPiano.sf2']
dctInstr['Guitar'] = ['Guitar_SessionGuitar.sf2', 'Guitar_SeagullAcousticGuitar.SF2']
dctInstr['Brass'] = ['Brass_SoftHorn.sf2', 'Brass_SwingHorn1.sf2']


intNumChannels = 15
strSongName = 'Song 001'
daw1 = daw(intNumChannels, name=strSongName)

i = 0
intDAWChannel = 0
daw1.load(intDAWChannel, strSFpath + dctInstr['Piano'][i])

intDAWChannel = 1
daw1.load(intDAWChannel, strSFpath + dctInstr['Guitar'][i])

intDAWChannel = 2
daw1.load(intDAWChannel, strSFpath + dctInstr['Brass'][i])


print (daw1)
daw1.play(pce01, wait=True)
