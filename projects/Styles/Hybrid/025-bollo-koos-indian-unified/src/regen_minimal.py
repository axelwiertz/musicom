import mido
from mido import Message, MidiFile, MidiTrack

def fix_025_harmony():
    mid = MidiFile(ticks_per_beat=480)
    
    # Track 1: Melody (Dutch + Indian ornaments)
    track_melody = MidiTrack()
    # Track 2: Chords (UnitMatrix style)
    track_harmony = MidiTrack()
    # Track 3: Percussion
    track_perc = MidiTrack()
    mid.tracks.extend([track_melody, track_harmony, track_perc])

    def add_note(track, pitch, duration, time=0, vel=70, channel=0):
        track.append(Message('note_on', note=pitch, velocity=vel, time=time, channel=channel))
        track.append(Message('note_off', note=pitch, velocity=0, time=duration, channel=channel))

    # BOLOO & KOOS Blend
    # D-E-F-D (Bollo) + C-G-E-C (Koos) + Bollywood Slides
    melody = [
        62, 64, 65, 62, # Bollo
        60, 67, 64, 60, # Koos
        62, 63, 62, 66, # Indian
        67, 66, 62, 62  # Blend
    ]
    
    for p in melody:
        add_note(track_melody, p, 480)

    # UnitMatrix Harmony (i - VII - VI - V)
    chords = [[62, 65, 69], [60, 64, 67], [58, 62, 65], [57, 61, 64]]
    for c in chords:
        for _ in range(4): # 1 bar each, quarter note pulse
            # Add chord notes at same time
            for i, p in enumerate(c):
                add_note(track_harmony, p, 480, time=0 if i > 0 else 0)
            # Advance time after notes
            track_harmony[-1].time = 480 # Offset the last note_off to advance

    # Clave (8-beat)
    clave = [1, 0, 1, 1, 0, 1, 0, 0] * 2
    for s in clave:
        if s:
            add_note(track_perc, 42, 240, vel=80)
        else:
            track_perc.append(Message('note_off', note=0, velocity=0, time=240))

    mid.save('../MIDI/bollo_koos_indian_v1.mid')

if __name__ == "__main__":
    fix_025_harmony()
