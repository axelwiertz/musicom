
from music21 import stream, note, meter, tempo, instrument, midi

def build_v1_2_midi():
    s = stream.Score()
    s.insert(0, meter.TimeSignature('6/8'))
    s.insert(0, tempo.MetronomeMark(number=118))
    
    v1 = stream.Part(id='Violin'); v1.insert(0, instrument.Violin())
    v2 = stream.Part(id='Piano'); v2.insert(0, instrument.Piano())
    v3 = stream.Part(id='Bass'); v3.insert(0, instrument.AcousticGuitar())
    v4 = stream.Part(id='Perc'); v4.insert(0, instrument.Woodblock())
    
    # Track 1
    sections = [
        [69,0,0,71,0,0]*8,
        [62,64,65,67,69,71]*8,
        [62,67,72,64,69,65]*8,
        [74,72,71,73,71,69]*8,
        [74,72,69,67,65,62]*8,
        [69,0,0,71,0,0]*8
    ]
    for sec in sections:
        for p in sec:
            if p == 0: v1.append(note.Rest(quarterLength=0.5))
            else: v1.append(note.Note(p, quarterLength=0.5))
            
    # Track 2
    v2.append(note.Rest(quarterLength=24.0))
    for _ in range(8):
        for p in [74, 72, 71, 69, 67, 65]: v2.append(note.Note(p, quarterLength=0.5))
    for _ in range(8):
        v2.append(note.Note(62, quarterLength=1.5))
        v2.append(note.Note(69, quarterLength=1.5))
    for _ in range(8):
        for p in [62, 65, 67, 69, 72, 74]: v2.append(note.Note(p, quarterLength=0.5))
    v2.append(note.Rest(quarterLength=48.0))
    
    # Track 3 & 4
    for bar in range(48):
        root = 38 if bar < 16 or bar > 32 else 43
        v3.append(note.Note(root, quarterLength=1.5))
        v3.append(note.Note(root+7, quarterLength=1.5))
        v4.append(note.Note(76, quarterLength=0.5))
        v4.append(note.Rest(quarterLength=1.0))
        v4.append(note.Note(77, quarterLength=0.5))
        v4.append(note.Rest(quarterLength=1.0))

    s.append(v1); s.append(v2); s.append(v3); s.append(v4)
    s.write('midi', '/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI/grand_suite_v1_2.mid')

if __name__ == "__main__": build_v1_2_midi()
