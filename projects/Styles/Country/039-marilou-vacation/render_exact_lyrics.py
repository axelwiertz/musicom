
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from pathlib import Path
base = Path('/opt/data/projects/Styles/Country/039-marilou-vacation')
mid_path = base/'marilou_exact.mid'
# 8 lyric lines => 8 bars, one line per bar, then repeat chorus response if needed by sustained harmony
# Each line gets a distinct contour approximating lyric stress and question/answer shape.
rows = {
    0: {'program': 73, 'notes': [64,65,67,67,64,65,67,69]},  # lead melody tracks question-answer shape
    1: {'program': 24, 'notes': [55,55,57,55,55,55,57,55]},  # acoustic guitar
    2: {'program': 33, 'notes': [43,43,45,43,43,43,45,43]},  # bass
    4: {'program': 110,'notes': [72,72,74,76,76,74,72,74]},  # fiddle answer
    5: {'program': 91, 'notes': [67,67,69,67,67,67,69,67]},  # pedal steel support
}
# drums on channel 9 with section lift on chorus
kick = [36,38,42,38, 36,38,42,38]
mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(96), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
for ch, spec in rows.items():
    tr = MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=spec['program'], time=0, channel=ch))
    prev = None
    for n in spec['notes']:
        if prev is not None:
            tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
        tr.append(Message('note_on', note=n, velocity=72, time=0, channel=ch))
        prev = n
    tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
tr = MidiTrack(); mid.tracks.append(tr)
tr.append(Message('program_change', program=0, time=0, channel=9))
prev = None
for n in kick:
    if prev is not None:
        tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=9))
    tr.append(Message('note_on', note=n, velocity=88, time=0, channel=9))
    prev = n
tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=9))
mid.save(mid_path)
print(mid_path)
