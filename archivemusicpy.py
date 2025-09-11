'''
MusicPy - Music21

Code using MusicPY and music21
'''

from music21py import *
from musicpy import database, musicpy, daw, control, algorithms

from harmony import *
from library import *


piece_midi = musicpy.read (DEFAULT_PATH + DEFAULT_MIDI_FILE_IN, get_off_drums=True, split_channels=True)
track_number = 0
nFrom = 0
nTo = 4
#nTo = 47

intNumTracks = len(piece_midi.tracks)
trkTrack1 = piece_midi(track_number)
lstNotes = trkTrack1.notes[nFrom:nTo]
intNumNotes = len (lstNotes)

print ('Track selected :')
print (trkTrack1)
print ('Track part from :' + str(nFrom) + ' to ' + str(nTo) + ' :')
print (trkTrack1[nFrom:nTo])
print ('Notes from track : '+ str(lstNotes))
print ('Number of notes : ' + str(intNumNotes))

print (piece_midi[track_number].content)
print (piece_midi[track_number].content.notes)

intInstr = 1
print ('Play selected track :')
#play(trkTrack1[nFrom:nTo], instrument=intInstr)
#, wait=True)

part_analyzed = piece_midi(track_number)
part_analyzed = trkTrack1[nFrom:nTo]
str1 = algorithms.detect (part_analyzed)
str2 = algorithms.chord_analysis (piece_midi(track_number))
str3 = algorithms.analyze_rhythm (trkTrack1[nFrom:nTo])


scl01 = musicpy.S(str(dctStyleScale['Standard'][0]))
scl01 = musicpy.S('C major')

chd01 = scl01.chord_progression(lstChordPattern[0])
for i in range(1, len(lstChordPattern)-1):
#    print (lstChordPattern[i])
    chd02 = scl01.chord_progression(lstChordPattern[i], durations=1 / 2, intervals=0, volumes=None, chords_interval=None)
    chd01 = chd01 + musicpy.rest(1/2) + chd02

chords_in_scale = scl01%(1234567, 0.5)
mpstream_chords = chords_in_scale[0]
for i in range(1, 7):
#    print (lstChordPattern[i])
    mpstream_chords = mpstream_chords + musicpy.rest(1/2) + chords_in_scale[i]


# Output
lstChdTrack = [mpstream_chords] # list of tracks
lstIntChannel = [1] # list of channelnumbers
lstIntStartTimes = [0] # list of starttimes

strSongName = 'Patterns'
rtmSong = []

# strSongName
# lstChdTrack # list of tracks: type musicpy.Chord
# lstIntChannel # list of channelnumbers
# lstIntStartTimes # list of starttimes
mpstream = chord('C4', 1/8, 1/8)*100
mpstream_rhythm = []
lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (mpstream.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (mpstream_rhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)


for i in range(0, len(lstChdTrack)):
    print ('Track    : ' + str(i))
    print ('Notes    : ' + str(lstChdTrack[i].notes))
    print ('Interval : ' + str(lstChdTrack[i].interval))


# Construct piece out of tracks
pce01 = musicpy.piece(tracks=lstChdTrack,channels=lstIntChannel, start_times=lstIntStartTimes)
# Play piece and wait until finish, writes temusicpy.midi
print ('Play :')
print (pce01)
musicpy.play(pce01, wait=True)


# Instrumentation

# Instruments
# Play all MIDI instruments
'''
for i in range(1, 127):
    print ('MIDI instrument ' + str(i))
    play(chdMelody01, bpm=150, instrument=i, wait=True)
'''

# Soundfont library
strSFpath = '\\Soundfont\\'
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
mpstream_out = trkTrack1[nFrom:nTo]

# Scales
sclSource = musicpy.scale('Bb', 'major')
# print (sclSource)
sclTarget = musicpy.scale('C', 'major')

# Modulate
mpstream_out = piece_midi[track_number].content.modulation(sclSource, sclTarget)

print ('Target musicpy stream :')
print (mpstream_out.notes)
pceTarget = musicpy.piece (tracks= [mpstream_out])
print (pceTarget)
musicpy.write (pceTarget, name=DEFAULT_PATH+DEFAULT_MIDI_FILE_OUT)

intInstr = 1
intBPM = 100
print ('Play :')
#play(pceTarget, wait=True)
#play (piece_midi, wait=True)
#play (piece_midi[track_number], instrument=intInstr, wait=True)
# play (piece_midi[track_number].content, bpm=intBPM, instrument=intInstr)
#play (mpstream_out, wait=True)



# Melody creation syntax
c1 = musicpy.chord('CM7', 3, 1 / 4, 1 / 8) ^ 2
c2 = musicpy.chord('CM7')
c2 = musicpy.chord('CM7', 3)
c3 = musicpy.chord('CM7', 5)
c5 = musicpy.chord('CM7', 3, 1 / 4, 1 / 8)
c5 = musicpy.chord('CM7', 3, 1 / 4)
c6 = musicpy.chord('CM7', 3, 1 / 4) ^ 2

melody = (c1 | c2 | c3 * 2 )

chd4 = musicpy.S('C4 major')%(15654321, 0.4)
mpstream = S('C major').get('1,2,3,4,5,6,7,1.1')

chd5 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
chd6 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])


# Chords
c1 = C('CM7', 3, 1/4, 1/8)^2
c2 = C('G7sus', 2, 1/4, 1/8)^2
mpstream = S('C4 major')%(15654321, 0.4)
print (mpstream)
chd03 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

# Notes
chd02 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')


# Scales
s1 = S('C Major')
t1 = s1.get('-,1,-,2') % (1 / 2,)
t1 = s1.get('r,1,r,2')

#1
mpstream = chord ('F2, A2, F3')
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

mpstream_percussion = []

# Percussion channel 10
intDAWChannel = 9
intPiano = 1
pceRhythm = piece (mpstream_percussion, [intPiano], channels=[intDAWChannel])

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
mpstream = chord('C4', 1/8, 1/8)*7
chd02 = mpstream.apply_rhythm (rtmSong)
play(chd02, wait=True)


lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (mpstream.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)
