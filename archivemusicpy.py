'''
MusicPy - Archive
'''

from musicpy import *

scl01 = S(str(dctStyleScale['Standard'][0]))
scl01 = mp.S('C major')

chd01 = scl01.chord_progression(lstChordSeqs[0])
for i in range(1, len(lstChordSeqs)-1):
#    print (lstChordPattern[i])
    chd02 = scl01.chord_progression(lstChordSeqs[i], durations=1 / 2, intervals=0, volumes=None, chords_interval=None)
    chd01 = chd01 + mp.rest(1/2) + chd02

lstChdScale = scl01%(1234567, 0.5)
chd01 = lstChdScale[0]
for i in range(1, 7):
#    print (lstChordPattern[i])
    chd01 = chd01 + mp.rest(1/2) + lstChdScale[i]


# Output
lstChdTrack = [chd01] # list of tracks
lstIntChannel = [1] # list of channelnumbers
lstIntStartTimes = [0] # list of starttimes

strSongName = 'Patterns'

# strSongName
# lstChdTrack # list of tracks: type mp.Chord
# lstIntChannel # list of channelnumbers
# lstIntStartTimes # list of starttimes
chd01 = chord('C4', 1/8, 1/8)*100
lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (chd01.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)


for i in range(0, len(lstChdTrack)):
    print ('Track    : ' + str(i))
    print ('Notes    : ' + str(lstChdTrack[i].notes))
    print ('Interval : ' + str(lstChdTrack[i].interval))


# Construct piece out of tracks
pce01 = P(tracks=lstChdTrack,channels=lstIntChannel, start_times=lstIntStartTimes)
# Play piece and wait until finish, writes temp.midi
print ('Play :')
print (pce01)
play(pce01, wait=True)


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
#daw1.play(pce01, wait=True)

