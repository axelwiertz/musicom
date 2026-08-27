import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage

# DNA
style = 'Country'
meter = '4/4'
key = 'G mixolydian'
tempo = 96
beats_per_bar = 4
total_bars = 8

# Build MIDI
mid = mido.MidiFile(ticks_per_beat=480)

# Meta track
meta_track = MidiTrack()
meta_track.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8))
meta_track.append(MetaMessage('key_signature', key='G'))  # G mixolydian
meta_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))
meta_track.append(MetaMessage('track_name', name='META', time=0))
mid.tracks.append(meta_track)

# Main track
main_track = MidiTrack()
main_track.append(MetaMessage('track_name', name='Country Hope Loop v7', time=0))
mid.tracks.append(main_track)
track = main_track

# I-IV-V in G mixolydian: G C D
# Bar 1-4: I (G) boom-chick
# Bar 5-8: IV (C) boom-chick, bar-4 cadence lift to V (D) then back to I

# Drums: boom-chick pattern (kick on 1 and 3, snare on 2 and 4)
# We'll use GM drum map: kick=36, snare=38

# Chord voicings (close, narrow)
chords = {
    'G': [67, 71, 74],  # G3 B3 D4
    'C': [60, 64, 67],  # C3 E3 G3
    'D': [62, 66, 69],  # D3 F#3 A3
}

# Bass root
bass_map = {'G': 55, 'C': 48, 'D': 50}

# Write bars 1-8
for bar in range(total_bars):
    chord_letter = 'G' if bar < 4 else ('C' if bar < 6 else 'D')
    # Chord on beat 1
    for note in chords[chord_letter]:
        track.append(Message('note_on', note=note, velocity=80, time=0))
    for note in chords[chord_letter]:
        track.append(Message('note_off', note=note, velocity=0, time=480*4-1))
    # Bass root on beat 1
    track.append(Message('note_on', note=bass_map[chord_letter], velocity=90, time=0))
    track.append(Message('note_off', note=bass_map[chord_letter], velocity=0, time=480*4-1))
    # Drums boom-chick
    # Kick on 1 and 3, snare on 2 and 4
    for pos in [0, 480*2, 480*1, 480*3]:
        if pos < 480*4:
            if pos in [0, 480*2]:
                track.append(Message('note_on', note=36, velocity=100, time=0))
                track.append(Message('note_off', note=36, velocity=0, time=60))
            else:
                track.append(Message('note_on', note=38, velocity=90, time=0))
                track.append(Message('note_off', note=38, velocity=0, time=60))

mid.save('/opt/data/projects/Styles/Country/001-country-hope-loop/MIDI/country-hope-loop-v7.mid')
print('MIDI saved:', '/opt/data/projects/Styles/Country/001-country-hope-loop/MIDI/country-hope-loop-v7.mid')
