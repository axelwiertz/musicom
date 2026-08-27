
# Regeneration script for balfolk_jig
# Usage: python3 src/regen.py

import sys
sys.path.insert(0, '/root/musicom')

from structures.pitchclass import MusicPitchClassSet, PatternType
from generators import RhythmGenerator
from converters.music21_score import unit_to_stream
from music21 import midi

# 1. Define Patterns
scale = MusicPitchClassSet("Dorian", PatternType.HEPTATONIC, rotation=1, initial=2)
pitch_pattern = (2, 3, -2, 0, 5)
rhythm = RhythmGenerator(onsets=5, timesteps=8).generate()[0]

# 2. Generate Phrase
melody = combine(pitch_pattern, rhythm, scale, start_pitch=62)

# 3. Export MIDI
s = unit_to_stream(melody)
mf = midi.translate.streamToMidiFile(s)
with open('../MIDI/balfolk_jig.mid', 'wb') as f:
    f.write(mf.writestr())

print("Regenerated: MIDI/balfolk_jig.mid")
