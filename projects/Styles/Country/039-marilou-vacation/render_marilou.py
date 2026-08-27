
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from pathlib import Path
base = Path('/opt/data/projects/Styles/Country/039-marilou-vacation')
mid_path = base/'marilou_country.mid'
# 16 bars = 8 verse, 8 chorus
tracks = {
    0: [64,64,67,67,64,64,65,64, 67,67,69,71,71,69,67,67], # lead vocal
    1: [55,55,57,55,55,55,57,55, 53,53,55,57,55,53,52,50], # acoustic guitar
    2: [43,43,45,43,43,43,45,43, 40,40,43,45,43,40,38,36], # bass
    3: [36,36,36,36,36,36,36,36, 36,36,36,36,36,36,36,36], # drums (kick/snare simplified)
    4: [72,74,76,74,72,74,76,77, 76,77,79,81,79,77,76,74], # fiddle
    5: [67,67,69,69,67,67,69,67, 65,65,67,69,67,65,64,62], # pedal steel
}
mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(96), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
for ch, seq in tracks.items():
    tr = MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=0, time=0, channel=ch))
    prev = None
    for n in seq:
        if prev is not None:
            tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
        tr.append(Message('note_on', note=n, velocity=72 if ch!=3 else 90, time=0, channel=ch))
        prev = n
    tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
mid.save(mid_path)
print(mid_path)
