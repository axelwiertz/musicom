
from music21 import stream, note, meter, tempo, instrument, midi

def build_v1_1_midi():
    s = stream.Score()
    s.insert(0, meter.TimeSignature('6/8'))
    s.insert(0, tempo.MetronomeMark(number=118))
    
    v1 = stream.Part(); v1.insert(0, instrument.Violin())
    v2 = stream.Part(); v2.insert(0, instrument.Piano())
    v3 = stream.Part(); v3.insert(0, instrument.AcousticGuitar())
    v4 = stream.Part(); v4.insert(0, instrument.Woodblock()) # Percussion
    
    lead_notes = [
        [69,0,0,71,0,0]*8,
        [62,64,65,67,69,71]*8,
        [62,67,72,64,69,65]*8,
        [74,72,71,73,71,69]*8,
        [74,74,72,72,69,69,67,67,65,65,62,62,60,60,59,59,57,57,55,55,53,53,51,51]*2,
        [69,0,0,71,0,0]*8
    ]

    for section in lead_notes:
        for p in section:
            if p == 0: v1.append(note.Rest(quarterLength=0.5))
            else: v1.append(note.Note(p, quarterLength=0.5))
            
    # Bass / Percussion logic for MIDI
    for bar in range(48):
        root = 38 if bar < 24 or bar > 32 else 43
        v3.append(note.Note(root, quarterLength=1.5))
        v3.append(note.Note(root+7, quarterLength=1.5))
        # Percussion pulse
        v4.append(note.Note(76, quarterLength=0.5))
        v4.append(note.Rest(quarterLength=1.0))
        v4.append(note.Note(77, quarterLength=0.5))
        v4.append(note.Rest(quarterLength=1.0))

    s.append(v1); s.append(v2); s.append(v3); s.append(v4)
    s.write('midi', '/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI/grand_suite_v1_1.mid')

if __name__ == "__main__": build_v1_1_midi()
