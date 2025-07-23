'''
MusicPy - Archive

Code using MusicPY, replaced by music21 code
'''

from musicpy import *

#from musicpy.daw import *
#from musicpy.database import *


# pceMIDI = mp.read (strPathIn + strFileName, get_off_drums=True, split_channels=True)
intTrack = 0
nFrom = 0
nTo = 4
#nTo = 47

intNumTracks = len(pceMIDI.tracks)
trkTrack1 = pceMIDI(intTrack)
lstNotes = trkTrack1.notes[nFrom:nTo]
intNumNotes = len (lstNotes)

print ('Track selected :')
print (trkTrack1)
print ('Track part from :' + str(nFrom) + ' to ' + str(nTo) + ' :')
print (trkTrack1[nFrom:nTo])
print ('Notes from track : '+ str(lstNotes))
print ('Number of notes : ' + str(intNumNotes))

print (pceMIDI[intTrack].content)
print (pceMIDI[intTrack].content.notes)

intInstr = 1
print ('Play selected track :')
#play(trkTrack1[nFrom:nTo], instrument=intInstr)
#, wait=True)

str1 = mp.alg.detect (pceMIDI(intTrack))
str2 = mp.alg.detect (trkTrack1[nFrom:nTo])
str3 = mp.alg.chord_analysis (pceMIDI(intTrack))
str4 = mp.alg.chord_analysis (trkTrack1[nFrom:nTo])
str5 = mp.alg.analyze_rhythm (trkTrack1[nFrom:nTo])


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

# Slice
chdTarget = trkTrack1[nFrom:nTo]

# Scales
sclSource = mp.scale('Bb', 'major')
# print (sclSource)
sclTarget = mp.scale('C', 'major')

# Modulate
chdTarget = pceMIDI[intTrack].content.modulation(sclSource, sclTarget)

print ('Target chord :')
print (chdTarget.notes)
pceTarget = mp.piece (tracks= [chdTarget])
print (pceTarget)
mp.write (pceTarget, name=strPathOut+ strMIDIFileNameOut)

intInstr = 1
intBPM = 100
print ('Play :')
#play(pceTarget, wait=True)
#play (pceMIDI, wait=True)
#play (pceMIDI[intTrack], instrument=intInstr, wait=True)
# play (pceMIDI[intTrack].content, bpm=intBPM, instrument=intInstr)
#play (chdTarget, wait=True)



# Melody creation syntax
c1 = C('CM7', 3, 1 / 4, 1 / 8) ^ 2
c2 = C('CM7')
c2 = C('CM7', 3)
c3 = C('CM7', 5)
c5 = C('CM7', 3, 1 / 4, 1 / 8)
c5 = C('CM7', 3, 1 / 4)
c6 = C('CM7', 3, 1 / 4) ^ 2

melody = (c1 | c2 | c3 * 2 )

chd4 = S('C4 major')%(15654321, 0.4)
chd01 = S('C major').get('1,2,3,4,5,6,7,1.1')

chd5 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
chd6 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])


# Chords
c1 = C('CM7', 3, 1/4, 1/8)^2
c2 = C('G7sus', 2, 1/4, 1/8)^2
chd01 = S('C4 major')%(15654321, 0.4)
print (chd01)
chd03 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

# Notes
chd02 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')


# Scales
s1 = S('C Major')
t1 = s1.get('-,1,-,2') % (1 / 2,)
t1 = s1.get('r,1,r,2')

#1
chd01 = chord ('F2, A2, F3')
chd02 = S('F major').get('1.-2;3.-2;1.-1')
#2
chd03 = chord('C2, C3, E3, G3')


# Melody

# Musical composition examples page 13

s1 = S('F major')

b1 = s1.get('-') + s1.get('1.-1; 3.-1; 1') + s1.get('5.-1; 5   ; 7.-1;2') + s1.get('1.-1; 5.-1; 1   ;3')
b2 = s1.get('6.-1; 4.-1; 1   ;4') + s1.get('1.-1; 3.-1; 1   ;5') + s1.get('6.-1; 3.-1; 1   ;6') + s1.get('5.-1; 5.-1; 2   ;7')
b3 = s1.get('1.-1; 5.-1; 3   ;1.+1')%(1,)


b21 = s1.get('-') + s1.get('1') + s1.get('7.-1; 2') + s1.get('5.-1; 3')
b22 = s1.get('6.-1; 4') + s1.get('3.-1; 5') + s1.get('4.-1; 6') + s1.get('2.-1; 7')
b23 = s1.get('1.-1; 1.+1')%(1,)

play (b1 + b2 + b3, wait=True)
play (b21 + b22 + b23, wait=True)


'''
:[] settings blok
r:n repeat the beat n times with the equally divided unit duration
R:n repeat the beat n times with the unit duration
b:n change the duration of the beat to the unit duration * n
'''

# drum
drm1 = drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
drm2 = drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')

drm3 =  drum ('K, K;H, S, H, K, K;H;PH, H;S, H')

print (drm3)



# Play DAW

intDAWChannel = 9
intPiano = 1

pceRhythm = piece ([chdRhythm], [intPiano], channels=[intDAWChannel])

intNumChannels = 10
strSongName = 'Percussion 001'
daw1 = daw(intNumChannels, name=strSongName)

# Play rhythm
print ('Play : ')
print (rtm1)
print (chdRhythm)
# play (chdRhythm, wait=True)
play (pceRhythm, wait=True)


print (daw1)
daw1.play(pceRhythm, wait=True)


rhythmic_info = rhythm.RhythmAnalyzer(rhythmic_stream)
rhythmic_info.getRhythm()

# Show the rhythmic information
print(rhythmic_info.getRhythm())


rtmSong = rtmBell
chd01 = chord('C4', 1/8, 1/8)*7
chd02 = chd01.apply_rhythm (rtmSong)
play(chd02, wait=True)

'''
lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (chd01.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)
'''
