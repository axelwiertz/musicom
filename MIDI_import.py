'''
Music MIDI import
'''

# Modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *


# Location of files
MIDIpath = 'C:\\temp\Music\\MIDI\\'

strMIDIFileName =  'SuperTrouper.mid'
strMIDIFileName =  'AllThatSheWants.mid'
strMIDIFileName =  'bossa-nova.mid'
strMIDIFileName =  'AxelTheme.mid'
strMIDIFileName = 'BigYellowTaxi01.mid'
piece01 = read(MIDIpath + strMIDIFileName, split_channels=True)

# Read
print (pMIDI)

play(ST(0))
play(ST(1))
play(ST(1)[1:20])
play(ST(1)[1:10])
play(ST(1)[1:30])
play(ST(1)[1:26])

ST(1)[1:26]
ST(1)[1:26].notes

# Play
play(pMIDI, channel=1)
play(pMIDI, bpm=83, channel=1)
chan1 = 7
instr1 = 1
play (pMIDI[chan1])

print (pMIDI[chan1])
                                                                                                                       
[track] AUD_HO0930
BPM: 83.0
channel: 15 | track name: Channel 16 | instrument: Alto Sax | start time: 5.94140625 | content: chord(notes=[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, ...], interval=[23/384, 91/768, 49/768, 97/1536, 191/768, 49/768, 89/1536, 25/384, 185/1536, 33/256, ...], start_time=0)
play (pMIDI[chan1], instrument=instr1)
                                                                                                             
print (pMIDI[chan1].content)
                                                                                                             
play(pMIDI[7].content)
play(pMIDI[7].content, bpm=83, instrument=2)
pMIDI[7].content.notes
             
[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, G#3, B3, B3, C#4, E4, F#4, B3, B3, F#4, F#4, F#4, G#4, F#4, E4, E4]
play(pMIDI[7].content.notes)
 
c2 = C(c1.notes)

# Analyis
cht = mp.alg.detect(ST(1)[1:26])
'Cmaj13 omit F sort as [1, 2, 3, 5, 6, 4]'
cht = mp.alg.chord_analysis(ST(1))


mp.alg.detect(pMIDI[7].content)
'B13sus4 omit A sort as [1, 4, 2, 3, 5]'
c1[1:4]
chord(notes=[C#4, E4, E4], interval=[91/768, 49/768, 97/1536], start_time=0)
mp.alg.detect(pMIDI[7].content[1:3])
             
'C# with minor third'
mp.alg.detect(pMIDI[7].content[1:4])
             
'C# with minor third'
mp.alg.detect(pMIDI[7].content[1:10])
             
'C#madd4 omit G#'
pMIDI[7]
             
play(pMIDI[3].content, bpm=83, instrument=2)
play(pMIDI[4].content, bpm=83, instrument=2)
                                                                                                             
play(pMIDI[4].content, bpm=83, instrument=1)
                                                                                                             
play(pMIDI[5].content, bpm=83, instrument=1)
                                                                                                             
pMIDI[5].content
                                                                                                             
chord(notes=[E5, E5, F#5, F#5, F#5, C#5, C#5, C#5, F#5, F#5, ...], interval=[383/1536, 99/512, 1/8, 277/1536, 95/384, 385/1536, 289/1536, 67/512, 277/1536, 385/1536, ...], start_time=0)
pMIDI[7].content
             
chord(notes=[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, ...], interval=[23/384, 91/768, 49/768, 97/1536, 191/768, 49/768, 89/1536, 25/384, 185/1536, 33/256, ...], start_time=0)
c1
             
chord(notes=[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, ...], interval=[23/384, 91/768, 49/768, 97/1536, 191/768, 49/768, 89/1536, 25/384, 185/1536, 33/256, ...], start_time=0)
c1.interval
             
[0.05989583333333333, 0.11848958333333333, 0.06380208333333333, 0.06315104166666667, 0.24869791666666666, 0.06380208333333333, 0.057942708333333336, 0.06510416666666667, 0.12044270833333333, 0.12890625, 0.9381510416666666, 0.06380208333333333, 0.06380208333333333, 0.12239583333333333, 0.12630208333333334, 0.18359375, 0.06510416666666667, 0.08072916666666667, 0.23372395833333334, 0.07096354166666667, 0.23177083333333334, 0.20052083333333334, 0.12369791666666666, 0.130859375, 0.41796875]
>>> play (c1)
...              
>>> play(pMIDI[6].content, bpm=83, instrument=1)
...              
>>> pMIDI[6].content
...              
chord(notes=[G#2, G#2, G#2, C2, C#3, C2, A#2, F#2, E2, F#2, ...], interval=[385/384, 255/512, 47/384, 1/512, 31/256, 5/1536, 187/1536, 0, 1/16, 95/1536, ...], start_time=0)
>>> play(pMIDI)
...              
>>> print pMIDI[7].content
...              
SyntaxError: Missing parentheses in call to 'print'. Did you mean print(...)?
>>> print (pMIDI[7].content)
...              
chord(notes=[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, ...], interval=[23/384, 91/768, 49/768, 97/1536, 191/768, 49/768, 89/1536, 25/384, 185/1536, 33/256, ...], start_time=0)
>>> import matplotlib
Traceback (most recent call last):
  File "<pyshell#50>", line 1, in <module>
    import matplotlib
>>> import numpy
>>> import matplotlib
    import matplotlib
>>> import matplotlib.pyplot as plt
