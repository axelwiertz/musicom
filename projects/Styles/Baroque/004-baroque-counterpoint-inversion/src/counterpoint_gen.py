import os
import sys

# Setup Musicom path
sys.path.append('/opt/data/repos/musicom')

from structures.unit import MusicUnit, MusicEvent
from converters.midi_converter import score_to_midifile
import musicpy as mp
from music21 import stream, note, midi

PROJECT_DIR = "/opt/data/projects/004-baroque-counterpoint-inversion"
MIDI_DIR = os.path.join(PROJECT_DIR, "midi")
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")

def unit_to_music21(unit: MusicUnit) -> stream.Part:
    part = stream.Part()
    for event in unit.events:
        n = note.Note(midi=event.pitch)
        n.volume.velocity = event.volume
        # music21 quarter lengths: 1 unit = 1 quarter
        n.quarterLength = event.duration
        part.insert(event.start_tick, n)
    return part

def main():
    # 1. Define C Minor Subject (inspired by Bach)
    # C4, D4, Eb4, B3, C4, G3, Ab3, G3
    subject_pitches = [60, 62, 63, 59, 60, 55, 56, 55]
    subject = MusicUnit(pitches=subject_pitches)
    
    # 2. Derive Inversion (Counterpoint)
    # Axis = C4 (60)
    counterpoint = subject.clone()
    counterpoint.invert(pivot=60)
    
    # 3. Derive Retrograde
    retro_subject = subject.clone()
    retro_subject.retrograde()
    
    # 4. Create Score
    s = stream.Score()
    s.insert(0, unit_to_music21(subject))
    s.insert(0, unit_to_music21(counterpoint))
    
    # Save MIDI
    os.makedirs(MIDI_DIR, exist_ok=True)
    midi_path = os.path.join(MIDI_DIR, "004_counterpoint_study.mid")
    
    # Explicit write using music21
    mf = midi.translate.streamToMidiFile(s)
    mf.open(midi_path, 'wb')
    mf.write()
    mf.close()
    
    print(f"MIDI saved to {midi_path}")

if __name__ == "__main__":
    main()
