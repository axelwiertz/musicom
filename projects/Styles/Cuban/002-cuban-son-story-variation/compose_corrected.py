
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from pathlib import Path
base = Path('/opt/data/projects/Styles/Cuban/002-cuban-son-story-variation')
mid_path = base/'MIDI'/'002-cuban-son-story-variation-v2.mid'
# 24 bars total, 4/4, 96 BPM, explicit Cuban-style roles.
lead = [62,64,65,67,69,67,65,64] * 3
harm = [50,52,53,55,57,55,53,52] * 3
bass = [38,38,40,38,43,43,45,43] * 3
perc = [36,38,42,38,36,38,42,38] * 3
reply = [67,67,69,67,65,65,67,65] * 3
mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(96), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
tracks = [
    (0, 73, lead),   # melodic lead
    (1, 24, harm),   # guitar
    (2, 33, bass),   # bass
    (4, 110, reply), # reply voice / coro-like lead
]
for ch, program, seq in tracks:
    tr = MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=program, time=0, channel=ch))
    for n in seq:
        tr.append(Message('note_on', note=n, velocity=72, time=0, channel=ch))
        tr.append(Message('note_off', note=n, velocity=0, time=480, channel=ch))
tr = MidiTrack(); mid.tracks.append(tr)
tr.append(Message('program_change', program=0, time=0, channel=9))
for n in perc:
    tr.append(Message('note_on', note=n, velocity=90, time=0, channel=9))
    tr.append(Message('note_off', note=n, velocity=0, time=480, channel=9))
mid.save(mid_path)
print(mid_path)
