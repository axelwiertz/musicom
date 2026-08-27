
from music21 import stream, note, meter, tempo, instrument, midi

def build_extended_midi():
    s = stream.Score()
    s.insert(0, meter.TimeSignature('6/8'))
    s.insert(0, tempo.MetronomeMark(number=118))
    v = stream.Part()
    v.insert(0, instrument.Violin())
    
    sections = [
        [69,0,0,71,0,0]*8, # 1: Intro
        [62,64,65,67,69,71]*8, # 2: Dance
        [62,67,72,64,69,65]*8, # 3: Bridge 1
        [74,72,71,73,71,69]*8, # 4: Dance 2
        [74,74,72,72,69,69,67,67,65,65,62,62,60,60,59,59,57,57,55,55,53,53,51,51]*2, # 5: Descent
        [69,0,0,71,0,0]*8 # 6: Outro
    ]
    
    for seq in sections:
        for p in seq:
            if p == 0: v.append(note.Rest(quarterLength=0.5))
            else: v.append(note.Note(p, quarterLength=0.5))
    
    s.append(v)
    s.write('midi', '/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI/grand_suite_extended.mid')

if __name__ == "__main__": build_extended_midi()
