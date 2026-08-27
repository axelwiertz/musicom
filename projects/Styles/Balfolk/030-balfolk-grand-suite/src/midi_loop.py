
import sys
from music21 import stream, note, chord, meter, tempo, instrument, midi

def build_looping_suite():
    s = stream.Score()
    s.insert(0, meter.TimeSignature('6/8'))
    s.insert(0, tempo.MetronomeMark(number=118))
    
    # 1. Lead (Violin)
    v1 = stream.Part()
    v1.insert(0, instrument.Violin())
    
    # Sections (8 bars each)
    # Intro
    for _ in range(8):
        v1.append(note.Note(69, quarterLength=0.5)) # A4
        v1.append(note.Rest(quarterLength=1.0))
        v1.append(note.Note(71, quarterLength=0.5)) # B4
        v1.append(note.Rest(quarterLength=1.0))
        
    # Dance
    dance_notes = [62, 64, 65, 67, 69, 71] 
    for _ in range(8):
        for p in dance_notes: v1.append(note.Note(p, quarterLength=0.5))
            
    # Bridge
    for _ in range(8):
        for p in [62, 67, 72, 64, 69, 65]: v1.append(note.Note(p, quarterLength=0.5))
            
    # Outro (Circular/Softer)
    for i in range(8):
        if i < 4:
            v1.append(note.Note(62, quarterLength=1.5))
            v1.append(note.Note(69, quarterLength=1.5))
        else:
            # Mirroring Intro for seamless loop
            v1.append(note.Note(69, quarterLength=0.5))
            v1.append(note.Rest(quarterLength=1.0))
            v1.append(note.Note(62, quarterLength=0.5))
            v1.append(note.Rest(quarterLength=1.0))
        
    # 2. Counterpoint (Piano)
    v2 = stream.Part()
    v2.insert(0, instrument.Piano())
    v2.append(note.Rest(quarterLength=24.0)) # Rest for intro
    
    for _ in range(8): # Dance
        for p in [74, 72, 71, 69, 67, 65]: v2.append(note.Note(p, quarterLength=0.5))
    for _ in range(8): # Bridge
        v2.append(note.Note(62, quarterLength=1.5))
        v2.append(note.Note(69, quarterLength=1.5))
    v2.append(note.Rest(quarterLength=24.0)) # Fade out for outro
        
    # 3. Bass (Acoustic Guitar)
    v3 = stream.Part()
    v3.insert(0, instrument.AcousticGuitar())
    for i in range(32):
        root = 38 if i < 16 or i > 24 else 43
        v3.append(note.Note(root, quarterLength=1.5))
        v3.append(note.Note(root + 7, quarterLength=1.5))
        
    # 4. Percussion (Woodblock/Drum substitute)
    v4 = stream.Part()
    v4.insert(0, instrument.Woodblock())
    for _ in range(32):
        # 1: Low, 4: High
        v4.append(note.Note(76, quarterLength=0.5)) # Beat 1
        v4.append(note.Rest(quarterLength=1.0))
        v4.append(note.Note(77, quarterLength=0.5)) # Beat 4
        v4.append(note.Rest(quarterLength=1.0))
        
    s.append(v1)
    s.append(v2)
    s.append(v3)
    s.append(v4)
    
    mf = midi.translate.streamToMidiFile(s)
    mf.open('/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI/grand_suite_loop.mid', 'wb')
    mf.write()
    mf.close()

if __name__ == "__main__":
    build_looping_suite()
