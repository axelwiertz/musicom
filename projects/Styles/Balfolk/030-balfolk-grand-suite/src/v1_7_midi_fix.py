
import os
from music21 import stream, note, meter, tempo, instrument, midi

def build_v1_7_fixed_midi():
    # ENSURE DIRECTORY EXISTS
    target_dir = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        
    s = stream.Score()
    s.insert(0, meter.TimeSignature('6/8'))
    s.insert(0, tempo.MetronomeMark(number=118))
    
    # Define Parts
    v1 = stream.Part(id='Violin'); v1.insert(0, instrument.Violin())
    v2 = stream.Part(id='Piano'); v2.insert(0, instrument.Piano())
    v3 = stream.Part(id='Bass'); v3.insert(0, instrument.AcousticGuitar())
    v4 = stream.Part(id='Perc'); v4.insert(0, instrument.Woodblock())
    
    # AABBCCDD Phrasing (3-bar parts + 1 bar rest)
    m_patterns = {
        'A': [62, 65, 69, 67, 71, 69]*3,
        'B': [74, 71, 69, 72, 69, 65]*3,
        'C': [69, 67, 65, 62, 64, 62]*3,
        'D': [62, 69, 74, 0, 69, 65]*3
    }
    
    melody_seq = []
    # Build sequence with 1 bar (6 pulses) rest between EVERY 3-bar block
    for char in ['A', 'A', 'B', 'B', 'C', 'C', 'D', 'D']:
        melody_seq.extend(m_patterns[char])
        melody_seq.extend([0]*6) # 1 bar Rest
        
    for p in melody_seq:
        if p == 0:
            v1.append(note.Rest(quarterLength=0.5))
        else:
            v1.append(note.Note(p, quarterLength=0.5))
            
    total_bars = len(melody_seq) // 6
    for b in range(total_bars):
        # Bass / Guitar
        root = 38 if (b // 4) % 2 == 0 else 43
        v3.append(note.Note(root, quarterLength=1.5))
        v3.append(note.Note(root+7, quarterLength=1.5))
        # Perc
        v4.append(note.Note(76, quarterLength=0.5))
        v4.append(note.Rest(quarterLength=1.0))
        v4.append(note.Note(77, quarterLength=0.5))
        v4.append(note.Rest(quarterLength=1.0))
        # Piano
        v2.append(note.Note(62 if b % 2 == 0 else 64, quarterLength=1.5))
        v2.append(note.Note(65 if b % 2 == 0 else 67, quarterLength=1.5))

    s.append(v1); s.append(v2); s.append(v3); s.append(v4)
    
    # SAVE AND VERIFY
    output_path = os.path.join(target_dir, "grand_suite_v1_7_ternary.mid")
    s.write('midi', output_path)
    
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"SUCCESS:{output_path}")
    else:
        print("FAILURE:MIDI_NOT_CREATED")

if __name__ == "__main__":
    build_v1_7_fixed_midi()
