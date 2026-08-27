
from music21 import stream, note, meter, tempo, instrument, midi

def build_v1_7_midi():
    s = stream.Score()
    s.insert(0, meter.TimeSignature('6/8'))
    s.insert(0, tempo.MetronomeMark(number=118))
    
    v1 = stream.Part(id='Violin'); v1.insert(0, instrument.Violin())
    v2 = stream.Part(id='Piano'); v2.insert(0, instrument.Piano())
    v3 = stream.Part(id='Bass'); v3.insert(0, instrument.AcousticGuitar())
    v4 = stream.Part(id='Perc'); v4.insert(0, instrument.Woodblock())
    
    m_patterns = {
        'A': [62, 65, 69, 67, 71, 69]*3,
        'B': [74, 71, 69, 72, 69, 65]*3,
        'C': [69, 67, 65, 62, 64, 62]*3,
        'D': [62, 69, 74, 0, 69, 65]*3
    }
    
    melody_seq = []
    for p in ['A', 'A']: melody_seq.extend(m_patterns[p]); melody_seq.extend([0]*6)
    for p in ['B', 'B']: melody_seq.extend(m_patterns[p]); melody_seq.extend([0]*6)
    for p in ['C', 'C']: melody_seq.extend(m_patterns[p]); melody_seq.extend([0]*6)
    for p in ['D', 'D']: melody_seq.extend(m_patterns[p]); melody_seq.extend([0]*6)
    
    for p in melody_seq:
        v1.append(note.Rest(0.5) if p == 0 else note.Note(p, 0.5))
    
    # Accomp fills the whole duration
    total_bars = len(melody_seq) // 6
    for b in range(total_bars):
        # Bass/Perc
        root = 38 if (b//7)%2 == 0 else 43
        v3.append(note.Note(root, 1.5))
        v3.append(note.Note(root+7, 1.5))
        v4.append(note.Note(76, 0.5)); v4.append(note.Rest(1.0))
        v4.append(note.Note(77, 0.5)); v4.append(note.Rest(1.0))
        # Piano chords
        v2.append(note.Note(62 if b%2==0 else 64, 1.5))
        v2.append(note.Note(65 if b%2==0 else 67, 1.5))

    s.append(v1); s.append(v2); s.append(v3); s.append(v4)
    s.write('midi', '/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI/grand_suite_v1_7.mid')

if __name__ == "__main__": build_v1_7_midi()
