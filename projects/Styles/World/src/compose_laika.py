import sys
import os
import mido
import numpy as np
import wave
import ctypes

# Add musicom to path
sys.path.insert(0, '/root/musicom')
sys.path.insert(0, '/root/musicom_ai')

from structures.pitchclass import MusicPitchClassSet, PatternType
from structures.unit import MusicUnit, MusicEvent
from structures.timegrid import MusicTimeGrid, MusicRhythmPattern

# --- Technical Brief: Standard Laika ---
# Genre: Greek Popular (Laiko)
# Meter: 4/4 (Hasapiko) for simplicity/standard form
# Dromos: Hijaz (D F# G A Bb C D) or Niavent (D E F G# A Bb C# D)
# We use Hijaz on D.
# Instrumentation: Bouzouki (General MIDI: Banjo or Sitar or Steel Gtr), 
#                 Guitar (Nylon), Electric Bass, Percussion (GM Kit).

PROJECT_NAME = "cretan-laika-daily-2026-06-07"
OUTPUT_DIR = f"/opt/data/projects/{PROJECT_NAME}"
os.makedirs(f"{OUTPUT_DIR}/MIDI", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/Audio", exist_ok=True)

# 1. Scale: Hijaz (D)
# Intervals for Hijaz: 1, 3, 1, 2, 1, 2, 2
# From D: D(2), Eb(3), F#(6), G(7), A(9), Bb(10), C(0)
HIJAZ_D = [2, 3, 6, 7, 9, 10, 0]

# 2. Rhythms: Hasapiko (Square 4/4) or Zeibekiko (9/8)
# We use Hasapiko 4/4 grid for this study.
# Pattern: 1 . 2 . 3 . 4 .
# Rhythmic DNA: █░█░█░█░ (Strict 8th notes with syncopated bouzouki licks)

# 3. Composition logic
def compose_laika():
    events = []
    # Intro: 4 bars Bouzouki Taksim (Hijaz licks)
    # A: 8 bars Verse
    # B: 8 bars Chorus
    
    ticks_per_beat = 480
    
    # Simple Bouzouki melody (Hijaz D)
    melody_pitches = [62, 63, 66, 67, 69, 70, 74] # D4 Eb4 F#4 G4 A4 Bb4 D5
    # Motif: Hijaz descent/ascent
    motif = [62, 63, 66, 67, 66, 63, 62] 
    
    # 32 bars total
    for bar in range(32):
        start_tick = bar * 4 * ticks_per_beat
        # Bouzouki (Lead)
        for i in range(4):
            pitch = motif[i % len(motif)]
            if bar >= 4 and bar < 12: # Verse: octave lower/higher variation
                 pitch += 12 if bar % 2 == 0 else 0
            
            events.append(MusicEvent(
                pitch=pitch, 
                volume=100 + (bar % 4),
                start_tick=start_tick + i * ticks_per_beat,
                end_tick=start_tick + (i+0.5) * ticks_per_beat
            ))
            
        # Bass: D - A (I - V)
        events.append(MusicEvent(
            pitch=38 if bar % 4 < 3 else 41, # D2 or F2
            volume=80,
            start_tick=start_tick,
            end_tick=start_tick + 2 * ticks_per_beat
        ))
    
    return MusicUnit(events=events)

# 4. Export MIDI
from musicom.converters.music21_score import unit_to_stream
from music21 import midi, instrument

unit = compose_laika()
s = unit_to_stream(unit)

# Force instruments
# Bouzouki -> Banjo (GM 105)
# Bass -> Fingered Bass (GM 33)
p1 = s.parts[0]
p1.insert(0, instrument.Banjo())

mf = midi.translate.streamToMidiFile(s)
with open(f"{OUTPUT_DIR}/MIDI/composition.mid", 'wb') as f:
    f.write(mf.writestr())

print(f"MIDI exported to {OUTPUT_DIR}/MIDI/composition.mid")
