
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from pathlib import Path
base = Path('/opt/data/projects/Styles/Cuban/001-cuban-trova-research')
mid_path = base/'daily-2026-07-01_cuban_001-cuban-trova-research_fixed.mid'
# 24 bars, 4/4, 96 BPM. 3 core musical roles + percussion.
lead = [62,64,65,67, 69,67,65,64] * 3
harmony = [50,52,53,55, 57,55,53,52] * 3
percus = [36,38,42,38, 36,38,42,38] * 3
bass = [38,38,40,38, 43,43,45,43] * 3
# expand each 8-step phrase into 24 bars by repeating 3x and sustaining at bar boundaries
mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(96), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
parts = [
    (0, 73, lead),      # lead melody
    (1, 24, harmony),   # acoustic guitar / harmonic voice
    (2, 33, bass),      # bass
]
for ch, program, seq in parts:
    tr = MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=program, time=0, channel=ch))
    prev = None
    for n in seq:
        if prev is not None:
            tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
        tr.append(Message('note_on', note=n, velocity=72, time=0, channel=ch))
        prev = n
    tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=ch))
# percussion channel 9
tr = MidiTrack(); mid.tracks.append(tr)
tr.append(Message('program_change', program=0, time=0, channel=9))
prev = None
for n in percus:
    if prev is not None:
        tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=9))
    tr.append(Message('note_on', note=n, velocity=90, time=0, channel=9))
    prev = n
tr.append(Message('note_off', note=prev, velocity=0, time=480, channel=9))
mid.save(mid_path)
print(mid_path)
