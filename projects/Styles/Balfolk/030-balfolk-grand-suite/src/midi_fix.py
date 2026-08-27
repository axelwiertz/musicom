
import sys
from music21 import stream, note, chord, meter, tempo, instrument, midi

def build_poly_suite():
    s = stream.Score()
    s.insert(0, meter.TimeSignature('6/8'))
    s.insert(0, tempo.MetronomeMark(number=118))
    
    # 1. Lead (Violin)
    v1 = stream.Part()
    v1.insert(0, instrument.Violin())
    
    # D Dorian scale: D4, E4, F4, G4, A4, B4, C5, D5 (62, 64, 65, 67, 69, 71, 72, 74)
    # Intro (8 bars of 6/8)
    for _ in range(8):
        v1.append(note.Note(69, quarterLength=0.5)) # A4
        v1.append(note.Rest(quarterLength=1.0))
        v1.append(note.Note(71, quarterLength=0.5)) # B4
        v1.append(note.Rest(quarterLength=1.0))
        
    # Dance (8 bars of 6/8) - Jig feel
    dance_notes = [62, 65, 69, 67, 67, 71] # D4, F4, A4, G4, G4, B4
    for _ in range(8):
        for p in dance_notes:
            v1.append(note.Note(p, quarterLength=0.5))
            
    # Bridge (8 bars)
    bridge_notes = [62, 67, 72, 64, 69, 65]
    for _ in range(8):
        for p in bridge_notes:
            v1.append(note.Note(p, quarterLength=0.5))
            
    # Climax (8 bars)
    for i in range(48):
        p = 62 + (i % 8)
        v1.append(note.Note(p, quarterLength=0.5))
        
    # 2. Counterpoint (Piano)
    v2 = stream.Part()
    v2.insert(0, instrument.Piano())
    # Rest for intro
    v2.append(note.Rest(quarterLength=24.0)) 
    
    # Descending Counter to Dance
    for i in range(8):
        scale_desc = [74, 72, 71, 69, 67, 65]
        for p in scale_desc:
            v2.append(note.Note(p, quarterLength=0.5))
            
    # Drones for Bridge
    for _ in range(8):
        v2.append(note.Note(62, quarterLength=1.5))
        v2.append(note.Note(69, quarterLength=1.5))
        
    # Chaos for Outro
    for i in range(48):
        p = 62 + ((i*2) % 12)
        v2.append(note.Note(p, quarterLength=0.5))
        
    # 3. Bass (Acoustic Guitar)
    v3 = stream.Part()
    v3.insert(0, instrument.AcousticGuitar())
    # Strong root/fifth pulse: D2 (38) and G2 (43)
    for i in range(32): # 32 bars
        root = 38 if (i // 4) % 2 == 0 else 43
        # Dotted quarter pulse
        v3.append(note.Note(root, quarterLength=1.5))
        v3.append(note.Note(root + 7, quarterLength=1.5))
        
    s.append(v1)
    s.append(v2)
    s.append(v3)
    
    mf = midi.translate.streamToMidiFile(s)
    mf.open('/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI/grand_suite_poly.mid', 'wb')
    mf.write()
    mf.close()

if __name__ == "__main__":
    build_poly_suite()
