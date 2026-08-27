
import sys, subprocess, json
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from pathlib import Path
base = Path('/opt/data/projects/Styles/Experimental/032-prime-fractal-full')
mid_path = base/'voice-leading-graph-search-example.mid'
wav_path = base/'voice-leading-graph-search-example.wav'
voices = [
    [64,64,65,64,62,64],
    [60,60,69,69,71,72],
    [67,64,69,69,67,67],
    [48,45,53,50,55,48],
]
mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(88), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
for i, seq in enumerate(voices):
    tr = MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=0, time=0, channel=i))
    prev = None
    for n in seq:
        if prev is not None:
            tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=i))
        tr.append(Message('note_on', note=n, velocity=72, time=0, channel=i))
        prev = n
    tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=i))
mid.save(mid_path)
print(json.dumps({'mid': str(mid_path)}))
