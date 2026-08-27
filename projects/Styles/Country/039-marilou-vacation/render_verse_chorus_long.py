
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from pathlib import Path
base = Path('/opt/data/projects/Styles/Country/039-marilou-vacation')
mid_path = base/'marilou_verse_chorus.mid'
# 8 bars total: 4 verse + 4 chorus, each bar 4 beats, one lyric line per bar
# Lead contour follows question-answer, with sustained notes on longer syllables
lead = [
    64,66,67,69,  # line 1 question rising
    69,67,66,64,  # line 2 answer falling
    64,66,69,71,  # line 3 question rising higher
    71,69,67,66,  # line 4 answer falling
    69,69,71,72,  # chorus hook starts open
    72,71,69,67,  # answer line gently falls
    71,72,74,72,  # question line lifts again
    72,71,69,67,  # final answer resolves
]
acg = [55,55,57,55, 55,55,57,55, 53,53,55,53, 55,55,57,55,
       57,57,55,57, 55,55,53,55, 57,57,55,57, 55,55,57,55]
bass = [43,43,45,43, 43,43,45,43, 40,40,43,40, 43,43,45,43,
        40,40,43,40, 38,38,40,38, 43,43,45,43, 43,43,40,38]
fiddle = [72,72,74,74, 72,72,74,76, 74,74,76,77, 76,74,72,74,
          76,77,79,77, 76,74,72,74, 77,79,81,79, 77,76,74,72]
steel = [67,67,69,67, 67,67,69,67, 65,65,67,65, 67,67,69,67,
         69,69,71,69, 67,67,69,67, 69,71,72,71, 69,67,65,64]
# drums as repeated groove notes, one per beat
kick_snare = [36,42,38,42] * 8

mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(96), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
tracks = [
    (0, 73, lead),
    (1, 24, acg),
    (2, 33, bass),
    (4, 110, fiddle),
    (5, 91, steel),
]
for ch, program, seq in tracks:
    tr = MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=program, time=0, channel=ch))
    prev = None
    for n in seq:
        if prev is not None:
            tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
        tr.append(Message('note_on', note=n, velocity=72, time=0, channel=ch))
        prev = n
    tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
tr = MidiTrack(); mid.tracks.append(tr)
tr.append(Message('program_change', program=0, time=0, channel=9))
prev = None
for n in kick_snare:
    if prev is not None:
        tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=9))
    tr.append(Message('note_on', note=n, velocity=88, time=0, channel=9))
    prev = n
tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=9))
mid.save(mid_path)
print(mid_path)
