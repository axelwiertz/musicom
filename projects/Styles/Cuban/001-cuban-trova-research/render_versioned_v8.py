
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from pathlib import Path
base = Path('/opt/data/projects/Styles/Cuban/001-cuban-trova-research')
mid_path = base/'daily-2026-07-01_cuban_001-cuban-trova-research-v8.mid'
# 24 bars, explicit versioned file, 3 parts + percussion, sustained through full form
lead = [62,64,65,67,69,67,65,64] * 3
harmony = [50,52,53,55,57,55,53,52] * 3
bass = [38,38,40,38,43,43,45,43] * 3
perc = [36,38,42,38,36,38,42,38] * 3
mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(96), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
for ch, program, seq in [(0,73,lead),(1,24,harmony),(2,33,bass)]:
    tr = MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=program, time=0, channel=ch))
    for n in seq:
        tr.append(Message('note_on', note=n, velocity=72, time=0, channel=ch))
        tr.append(Message('note_off', note=n, velocity=0, time=480, channel=ch))
tr = MidiTrack(); mid.tracks.append(tr)
tr.append(Message('program_change', program=0, time=0, channel=9))
for n in perc:
    tr.append(Message('note_on', note=n, velocity=88, time=0, channel=9))
    tr.append(Message('note_off', note=n, velocity=0, time=480, channel=9))
mid.save(mid_path)
print(mid_path)
