Python 3.12.1 (tags/v3.12.1:2305ca5, Dec  7 2023, 22:03:25) [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
from musicpy import *
curpath = 'C:\\temp\Music\\'

pMIDI = read(curpath + 'AUD_HO0930.mid')
pMIDI
[piece] AUD_HO0930
BPM: 83.0
track 0 | channel: 1 | track name: Channel 2 | instrument: Electric Bass (finger) | start time: 0 | content: chord(notes=[E2, A1, B1, A1, B1, E1, A1, B1, B1, E2, ...], interval=[145/256, 1/16, 3/16, 91/1536, 185/1536, 73/128, 89/1536, 71/384, 25/128, 851/1536, ...], start_time=0)
track 1 | channel: 2 | track name: Channel 3 | instrument: Bright Acoustic Piano | start time: 2.0052083333333335 | content: chord(notes=[E5, E5, E5, D#5, F#5, D#5, E5, C#5, C#5, C#5, ...], interval=[373/1536, 299/1536, 287/1536, 191/1536, 185/1536, 23/384, 107/1536, 187/768, 25/128, 193/1536, ...], start_time=0)
track 2 | channel: 3 | track name: Channel 4 | instrument: Celesta | start time: 3.8723958333333335 | content: chord(notes=[B3, B3, B3, B3, B3, B3, B3, B3, B3, B3, ...], interval=[33/512, 49/768, 33/256, 1/8, 95/768, 33/512, 191/1536, 1/16, 95/768, 49/768, ...], start_time=0)
track 3 | channel: 5 | track name: Channel 6 | instrument: Acoustic Guitar (steel) | start time: 0.0013020833333333333 | content: chord(notes=[E3, B3, G#3, E4, E4, B3, G#3, E3, E3, B3, ...], interval=[1/512, 1/1536, 1/1536, 91/512, 1/512, 1/1536, 1/384, 33/512, 1/1536, 1/1536, ...], start_time=0)
track 4 | channel: 6 | track name: Channel 7 | instrument: Acoustic Guitar (steel) | start time: 0 | content: chord(notes=[E3, G#3, E4, B3, E3, G#3, E4, B3, F#4, D#4, ...], interval=[5/1536, 1/512, 1/1536, 373/1536, 1/512, 1/512, 0, 29/96, 1/384, 1/768, ...], start_time=0)
track 5 | channel: 7 | track name: Channel 8 | instrument: Acoustic Guitar (nylon) | start time: 0 | content: chord(notes=[E5, E5, F#5, F#5, F#5, C#5, C#5, C#5, F#5, F#5, ...], interval=[383/1536, 99/512, 1/8, 277/1536, 95/384, 385/1536, 289/1536, 67/512, 277/1536, 385/1536, ...], start_time=0)
track 6 | channel: 9 | track name: Channel 10 | instrument: Acoustic Grand Piano | start time: 4.376953125 | content: chord(notes=[G#2, G#2, G#2, C2, C#3, C2, A#2, F#2, E2, F#2, ...], interval=[385/384, 255/512, 47/384, 1/512, 31/256, 5/1536, 187/1536, 0, 1/16, 95/1536, ...], start_time=0)
track 7 | channel: 15 | track name: Channel 16 | instrument: Alto Sax | start time: 5.94140625 | content: chord(notes=[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, ...], interval=[23/384, 91/768, 49/768, 97/1536, 191/768, 49/768, 89/1536, 25/384, 185/1536, 33/256, ...], start_time=0)
play(pMIDI, channel=1)
                                                                                                                       
play(pMIDI, bpm=83, channel=1)
                                                                                                                       
play(pMIDI, bpm=83, channel=5)
                                                                                                                       
play (pMIDI[1])
                                                                                                                       
play (pMIDI[2])
                                                                                                                       
play (pMIDI[3])
                                                                                                                       
play (pMIDI[7])
                                                                                                                       
pMIDI[7]
                                                                                                                       
[track] AUD_HO0930
BPM: 83.0
channel: 15 | track name: Channel 16 | instrument: Alto Sax | start time: 5.94140625 | content: chord(notes=[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, ...], interval=[23/384, 91/768, 49/768, 97/1536, 191/768, 49/768, 89/1536, 25/384, 185/1536, 33/256, ...], start_time=0)
play (pMIDI[7], instrument=1)
                                                                                                             
pMIDI[7].notes
                                                                                                             
Traceback (most recent call last):
  File "<pyshell#13>", line 1, in <module>
    pMIDI[7].notes
AttributeError: 'track' object has no attribute 'notes'
pMIDI[7].content
                                                                                                             
chord(notes=[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, ...], interval=[23/384, 91/768, 49/768, 97/1536, 191/768, 49/768, 89/1536, 25/384, 185/1536, 33/256, ...], start_time=0)
play(pMIDI[7].content)
             
play(pMIDI[7].content, bpm=83, instrument=2)
             
pMIDI[7].content.notes
             
[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, G#3, B3, B3, C#4, E4, F#4, B3, B3, F#4, F#4, F#4, G#4, F#4, E4, E4]
play(pMIDI[7].content.notes)
 
Traceback (most recent call last):
  File "<pyshell#18>", line 1, in <module>
    play(pMIDI[7].content.notes)
  File "C:\Users\92591\AppData\Local\Programs\Python\Python312\Lib\site-packages\musicpy\musicpy.py", line 276, in play
    file = write(current_chord=current_chord,
  File "C:\Users\92591\AppData\Local\Programs\Python\Python312\Lib\site-packages\musicpy\musicpy.py", line 767, in write
    current_chord = concat(current_chord, '|')
  File "C:\Users\92591\AppData\Local\Programs\Python\Python312\Lib\site-packages\musicpy\musicpy.py", line 228, in concat
    temp |= t
TypeError: unsupported operand type(s) for |=: 'note' and 'note'
len(pMIDI[7].content.notes)
                 
25
c1 = pMIDI[7].content
                 
c1
                 
chord(notes=[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, ...], interval=[23/384, 91/768, 49/768, 97/1536, 191/768, 49/768, 89/1536, 25/384, 185/1536, 33/256, ...], start_time=0)
c2 = C(c1.notes)
             
Traceback (most recent call last):
  File "<pyshell#22>", line 1, in <module>
    c2 = C(c1.notes)
  File "C:\Users\92591\AppData\Local\Programs\Python\Python312\Lib\site-packages\musicpy\musicpy.py", line 1144, in trans
    obj = obj.replace(' ', '')
AttributeError: 'list' object has no attribute 'replace'
detect(pMIDI[7].content)
             
Traceback (most recent call last):
  File "<pyshell#23>", line 1, in <module>
    detect(pMIDI[7].content)
NameError: name 'detect' is not defined
import musicpy as mp
mp.alg.detect(pMIDI[7].content)
'B13sus4 omit A sort as [1, 4, 2, 3, 5]'
c1(1;3)
SyntaxError: invalid syntax
c1(1,3)
Traceback (most recent call last):
  File "<pyshell#27>", line 1, in <module>
    c1(1,3)
TypeError: chord.__call__() takes 2 positional arguments but 3 were given
c1[1,4]
Traceback (most recent call last):
  File "<pyshell#28>", line 1, in <module>
    c1[1,4]
  File "C:\Users\92591\AppData\Local\Programs\Python\Python312\Lib\site-packages\musicpy\structures.py", line 1590, in __getitem__
    return self.notes[ind]
TypeError: list indices must be integers or slices, not tuple
c1[1:4]
chord(notes=[C#4, E4, E4], interval=[91/768, 49/768, 97/1536], start_time=0)
mp.alg.detect(pMIDI[7].content[1:3])
             
'C# with minor third'
mp.alg.detect(pMIDI[7].content[1:4])
             
'C# with minor third'
mp.alg.detect(pMIDI[7].content[1:10])
             
'C#madd4 omit G#'
pMIDI[7].interval
             
Traceback (most recent call last):
  File "<pyshell#33>", line 1, in <module>
    pMIDI[7].interval
AttributeError: 'track' object has no attribute 'interval'
pMIDI[7].intervals
             
Traceback (most recent call last):
  File "<pyshell#34>", line 1, in <module>
    pMIDI[7].intervals
AttributeError: 'track' object has no attribute 'intervals'
pMIDI[7]
             
[track] AUD_HO0930
BPM: 83.0
channel: 15 | track name: Channel 16 | instrument: Alto Sax | start time: 5.94140625 | content: chord(notes=[B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, ...], interval=[23/384, 91/768, 49/768, 97/1536, 191/768, 49/768, 89/1536, 25/384, 185/1536, 33/256, ...], start_time=0)
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
ModuleNotFoundError: No module named 'matplotlib'
>>> import numpy
>>> import matplotlib
Traceback (most recent call last):
  File "<pyshell#52>", line 1, in <module>
    import matplotlib
ModuleNotFoundError: No module named 'matplotlib'
>>> import matplotlib
Traceback (most recent call last):
  File "<pyshell#53>", line 1, in <module>
    import matplotlib
ModuleNotFoundError: No module named 'matplotlib'
>>> import matplotlib.pyplot as plt
Traceback (most recent call last):
  File "<pyshell#54>", line 1, in <module>
    import matplotlib.pyplot as plt
ModuleNotFoundError: No module named 'matplotlib'
