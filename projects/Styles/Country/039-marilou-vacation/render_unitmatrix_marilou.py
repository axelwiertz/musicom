
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from pathlib import Path
base = Path('/opt/data/projects/Styles/Country/039-marilou-vacation')
mid_path = base/'unitmatrix_marilou.mid'
# UnitMatrix rows mapped to GM instruments
rows = [
    {'channel': 0, 'program': 73, 'notes': [64,64,67,67,64,64,65,64, 67,67,69,71,71,69,67,67]}, # Lead melody / flute-like lead
    {'channel': 1, 'program': 25, 'notes': [55,55,57,55,55,55,57,55, 53,53,55,57,55,53,52,50]}, # Acoustic guitar steel
    {'channel': 2, 'program': 33, 'notes': [43,43,45,43,43,43,45,43, 40,40,43,45,43,40,38,36]}, # Electric bass
    {'channel': 3, 'program': 0, 'notes': [36,38,42,38,36,38,42,38, 36,38,42,38,36,38,42,38]}, # Drums channel 9 handled below
    {'channel': 4, 'program': 110, 'notes': [72,74,76,74,72,74,76,77, 76,77,79,81,79,77,76,74]}, # Fiddle-ish lead (bagpipe-like placeholder)
    {'channel': 5, 'program': 91, 'notes': [67,67,69,69,67,67,69,67, 65,65,67,69,67,65,64,62]}, # Pedal steel-ish pad
]
mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(96), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
for row in rows:
    ch = row['channel']
    tr = MidiTrack(); mid.tracks.append(tr)
    if ch == 3:
        tr.append(Message('program_change', program=0, time=0, channel=9))
        prev = None
        for n in row['notes']:
            if prev is not None:
                tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=9))
            tr.append(Message('note_on', note=n, velocity=90, time=0, channel=9))
            prev = n
        tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=9))
    else:
        tr.append(Message('program_change', program=row['program'], time=0, channel=ch))
        prev = None
        for n in row['notes']:
            if prev is not None:
                tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
            tr.append(Message('note_on', note=n, velocity=72, time=0, channel=ch))
            prev = n
        tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
mid.save(mid_path)
print(mid_path)
