import mido
from mido import Message, MidiFile, MidiTrack

def create_midi(path):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    BPM = 110
    TICKS_PER_BEAT = mid.ticks_per_beat
    
    # Bass Pattern
    bass_pattern = [46, 53, 46, 53]
    for _ in range(8):
        for note in bass_pattern:
            track.append(Message('note_on', note=note, velocity=80, time=0))
            track.append(Message('note_off', note=note, velocity=80, time=TICKS_PER_BEAT))
            
    mid.save(path)

create_midi('/opt/data/projects/018-landal-bollo-koos-hybrid/midi/hybrid_v1.mid')
print("MIDI saved.")
