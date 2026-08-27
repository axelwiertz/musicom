from pathlib import Path
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

BASE = Path('/opt/data/projects/Styles/Cuban/005-cuban-son-clave-lift')
OUT = BASE / 'MIDI' / '005-cuban-son-clave-lift-v4.mid'

lead = [62, 64, 65, 67, 69, 67, 65, 62]
montuno = [50, 53, 55, 57, 55, 53, 52, 50]
bass = [38, 38, 41, 38, 43, 41, 38, 36]
clave = [36, 0, 38, 0, 36, 0, 38, 0]

mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(104), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))

parts = [
    (0, 73, lead),
    (1, 24, montuno),
    (2, 33, bass),
]

for ch, program, seq in parts:
    tr = MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=program, channel=ch, time=0))
    for n in seq:
        tr.append(Message('note_on', note=n, velocity=80, channel=ch, time=0))
        tr.append(Message('note_off', note=n, velocity=0, channel=ch, time=480))

tr = MidiTrack(); mid.tracks.append(tr)
tr.append(Message('program_change', program=0, channel=9, time=0))
for n in clave:
    if n == 0:
        tr.append(Message('note_off', note=36, velocity=0, channel=9, time=480))
    else:
        tr.append(Message('note_on', note=n, velocity=92, channel=9, time=0))
        tr.append(Message('note_off', note=n, velocity=0, channel=9, time=240))

mid.save(OUT)
print(OUT)
