
import random
from music21 import stream, note, meter, tempo, instrument, midi

def build_v1_6_midi():
    s = stream.Score()
    s.insert(0, meter.TimeSignature('6/8'))
    s.insert(0, tempo.MetronomeMark(number=122))
    
    # Track 1: Lead (Violin)
    v1 = stream.Part(id='Violin')
    v1.insert(0, instrument.Violin())
    
    # Melodic Sequences (matching v1.6 Audio)
    sections = [
        [69,0,0,71,0,0]*8, # 1: Intro
        [62,64,65,67,69,71]*7 + [62,64,65,67,71,74], # 2: Dance + Turnaround
        [62,67,72,64,69,65]*8, # 3: Bridge
        ([74,72,71,73,71,69]*4) + ([74,0,71,73,0,69]*4), # 4: Dance 2 + Hocket
        [74,72,71,69,67,65]*8, # 5: Descent
        [69,0,0,64,0,0]*8  # 6: Varied Outro
    ]
    
    for sec in sections:
        for p in sec:
            # Subtle micro-timing in MIDI (shifted offsets)
            n_obj = note.Rest(0.5) if p == 0 else note.Note(p, quarterLength=0.5)
            if not n_obj.isRest:
                # Metrical physics: Strong 1 and 4
                pos_in_bar = len(v1.elements) % 6
                n_obj.volume.velocity = 100 if pos_in_bar == 0 else (85 if pos_in_bar == 3 else 70)
                n_obj.volume.velocity += random.randint(-5, 5) # Human jitter
            v1.append(n_obj)

    # Track 2: Bass (Guitar)
    v3 = stream.Part(id='Bass')
    v3.insert(0, instrument.AcousticGuitar())
    for bar in range(48):
        root = 38 if bar < 16 or bar > 32 else 43
        n1 = note.Note(root, quarterLength=1.5)
        n1.volume.velocity = 95
        n2 = note.Note(root+5, quarterLength=1.5)
        n2.volume.velocity = 75
        v3.append(n1)
        v3.append(n2)

    # Track 3: Perc (Woodblock)
    v4 = stream.Part(id='Perc'); v4.insert(0, instrument.Woodblock())
    for _ in range(48):
        k = note.Note(76, quarterLength=0.5); k.volume.velocity = 110
        v4.append(k)
        v4.append(note.Rest(1.0))
        h = note.Note(77, quarterLength=0.5); h.volume.velocity = 85
        v4.append(h)
        v4.append(note.Rest(1.0))

    s.append(v1); s.append(v3); s.append(v4)
    s.write('midi', '/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI/grand_suite_v1_6_human.mid')

if __name__ == "__main__": build_v1_6_midi()
