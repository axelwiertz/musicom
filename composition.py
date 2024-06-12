'''
Music - Compose
'''
# modules
import os
import time
import musicpy as mp
from musicpy import *
from musicpy.daw import *

# function compose song framework
# put specific song parameters here
import song001
from song import *
# strSongName
# lstChdTrack # list of tracks: type mp.Chord
# lstIntChannel # list of channelnumbers
# lstIntStartTimes # list of starttimes

for i in range(0, len(lstChdTrack)):
    print ('Track    : ' + str(i))
    print ('Notes    : ' + str(lstChdTrack[i].notes))
    print ('Interval : ' + str(lstChdTrack[i].interval))


# Construct piece out of tracks
pce01 = P(tracks=lstChdTrack,channels=lstIntChannel, start_times=lstIntStartTimes)
# Play piece and wait until finish, writes temp.midi
print ('Play :')
print (pce01)
#play(pce01, wait=True)


# Instrumentation

# Instruments
# Play all MIDI instruments
'''
for i in range(1, 127):
    print ('MIDI instrument ' + str(i))
    play(chdMelody01, bpm=150, instrument=i, wait=True)
'''

# Soundfont library
strSFpath = os.getcwd() + '\\Soundfont\\'
dctInstr = {}
dctInstr['Piano'] = ['Piano_NineFootGrand.sf2', 'Piano_RolandPiano.sf2']
dctInstr['Guitar'] = ['Guitar_SessionGuitar.sf2', 'Guitar_SeagullAcousticGuitar.SF2']
dctInstr['Brass'] = ['Brass_SoftHorn.sf2', 'Brass_SwingHorn1.sf2']

# MP DAW
intNumChannels = 15
daw1 = daw(intNumChannels, name=strSongName)

i = 0
intDAWChannel = 0
daw1.load(intDAWChannel, strSFpath + dctInstr['Piano'][i])

intDAWChannel = 1
daw1.load(intDAWChannel, strSFpath + dctInstr['Guitar'][i])

intDAWChannel = 2
daw1.load(intDAWChannel, strSFpath + dctInstr['Brass'][i])

intDAWChannel = 9
daw1.load(intDAWChannel, strSFpath + dctInstr['Piano'][i]) #Percussion

intPiano = 1


print ('Play :')
print (daw1)
daw1.play(pce01, wait=True)

