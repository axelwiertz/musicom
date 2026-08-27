from pathlib import Path
import sys
sys.path.insert(0, '/opt/data/repos/musicom')

from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

BASE = Path('/opt/data/projects/Styles/Country/041-country-railroad-morning')
MIDI = BASE / 'MIDI' / '041-country-railroad-morning-v1.mid'

mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack(); mid.tracks.append(meta)
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(106), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))

tracks = []
for name, ch, program in [('Lead', 0, 26), ('Harmony', 1, 24), ('Bass', 2, 33), ('Drums', 9, 0), ('Guitar', 3, 25)]:
    t = MidiTrack(); mid.tracks.append(t)
    t.append(MetaMessage('track_name', name=name, time=0))
    if ch != 9:
        t.append(Message('program_change', channel=ch, program=program, time=0))
    tracks.append(t)

bar = 1920
q = 480

def add_note(track, ch, note, start, dur, vel=84):
    track.append(Message('note_on', channel=ch, note=note, velocity=vel, time=start))
    track.append(Message('note_off', channel=ch, note=note, velocity=0, time=dur))

# Lead v1 winner DNA: 6 variations compressed into one 8-bar loop. Bars 1-2 motif, 3-4 answer, 5-6 lift, 7-8 cadence.
lead_notes = [67,69,71,69,67,69,74,71, 69,67,64,67,69,71,69,67]
bass_roots = [43,43,45,45,48,48,43,43]
chords = [55,60,62,55,55,60,62,55]

time = 0
for bar_i in range(8):
    # drums: kick 1/3, snare 2/4, hat 8ths
    t = tracks[3]
    for beat in range(4):
        t.append(Message('note_on', channel=9, note=42, velocity=44, time=(0 if beat else time)))
        t.append(Message('note_off', channel=9, note=42, velocity=0, time=240))
        if beat in (0,2):
            t.append(Message('note_on', channel=9, note=36, velocity=88, time=0))
            t.append(Message('note_off', channel=9, note=36, velocity=0, time=0))
        else:
            t.append(Message('note_on', channel=9, note=38, velocity=92, time=0))
            t.append(Message('note_off', channel=9, note=38, velocity=0, time=0))
        t.append(Message('note_on', channel=9, note=42, velocity=44, time=0))
        t.append(Message('note_off', channel=9, note=42, velocity=0, time=240))
    time = 0
    # harmony pad block
    add_note(tracks[1], 1, chords[bar_i], 0 if bar_i else bar, bar, 62)
    # bass root-5 pickup feel
    add_note(tracks[2], 2, bass_roots[bar_i], 0 if bar_i else bar, bar, 76)
    # guitar chop
    add_note(tracks[4], 3, 59, 0 if bar_i else bar, 240, 58)
    add_note(tracks[4], 3, 62, 240, 240, 58)
    add_note(tracks[4], 3, 59, 240, 240, 58)
    add_note(tracks[4], 3, 62, 240, 240, 58)
    # lead cells
    base = bar_i * 2
    add_note(tracks[0], 0, lead_notes[base], 0 if bar_i else bar, 240, 92)
    add_note(tracks[0], 0, lead_notes[base+1], 240, 240, 92)
    # advance by one bar in ticks for following track events
    for tr in tracks:
        for msg in tr:
            if hasattr(msg, 'time'):
                pass

mid.save(MIDI)
print(MIDI)
