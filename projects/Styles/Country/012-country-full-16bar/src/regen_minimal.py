
import mido
from mido import Message, MidiFile, MidiTrack

def generate():
    mid = MidiFile()
    progression = [67, 67, 72, 67, 67, 67, 74, 67, 72, 72, 67, 67, 74, 74, 67, 67]
    
    # 4 Tracks: Accordion, Guitar, Choir, Drums
    for i, prog in enumerate([21, 24, 52]):
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(Message('program_change', program=prog, time=0))
        for root in progression:
            # Simplified logic for regen demonstration
            track.append(Message('note_on', note=root, velocity=64, time=0))
            track.append(Message('note_off', note=root, time=1920))
            
    mid.save('../MIDI/16bar_country_regen.mid')
    print("Regenerated MIDI.")

if __name__ == '__main__':
    generate()
