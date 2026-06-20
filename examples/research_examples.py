"""
Example usage of the Musicom framework.

This example demonstrates how to use the various modules to create,
transform, and export musical compositions.
"""

from musicom.structures import Note, Chord, Scale, Sequence, MAJOR_SCALE, MINOR_TRIAD
from musicom.generators import MelodyGenerator, ChordProgressionGenerator, RhythmGenerator
from musicom.transformers import TranspositionTransformer, TimeTransformer, HarmonicTransformer
from musicom.rules import HarmonicRule, MelodicRule, ChordProgressionRule
from musicom.io import MIDIHandler

# Example 1: Create a simple melody
print("Example 1: Creating a melody")
print("-" * 50)

# Define a C major scale
c_major = Scale(root=0, intervals=MAJOR_SCALE, name="C Major")

# Generate a melody
melody_gen = MelodyGenerator(c_major, seed=42)
melody = melody_gen.generate_stepwise(length=8, start_pitch=60, duration=0.5)

print(f"Generated {len(melody)} notes")
print(f"First note: pitch={melody[0].pitch}, duration={melody[0].duration}")

# Analyze the melody
contour = MelodicRule.analyze_contour(melody)
print(f"Melodic contour: {contour}")


# Example 2: Create a chord progression
print("\n\nExample 2: Creating a chord progression")
print("-" * 50)

# Generate a chord progression in C major
chord_gen = ChordProgressionGenerator(key_root=0, is_major=True, seed=42)
chords = chord_gen.generate_progression(num_chords=4, duration=1.0)

print(f"Generated {len(chords)} chords")
for i, chord in enumerate(chords):
    quality = HarmonicRule.identify_chord_quality(chord)
    print(f"Chord {i+1}: {quality}, pitches: {[n.pitch for n in chord.notes]}")


# Example 3: Apply transformations
print("\n\nExample 3: Applying transformations")
print("-" * 50)

# Transpose the melody
transposed = TranspositionTransformer.transpose_note(melody[0], semitones=5)
print(f"Original pitch: {melody[0].pitch}, Transposed pitch: {transposed.pitch}")

# Time stretch
stretched = TimeTransformer.time_stretch(melody, factor=2.0)
print(f"Original duration: {melody[0].duration}, Stretched duration: {stretched[0].duration}")

# Harmonize
harmonized = HarmonicTransformer.harmonize(melody[:4], intervals=[4, 7])  # Major third and perfect fifth
print(f"Original notes: {len(melody[:4])}, Harmonized notes: {len(harmonized)}")


# Example 4: Create a complete sequence and save as MIDI
print("\n\nExample 4: Creating and saving a composition")
print("-" * 50)

# Combine melody and chords into a sequence
all_events = []

# Add melody notes
for note in melody:
    all_events.append(note)

# Add chord notes (as separate notes)
for chord in chords:
    for note in chord.notes:
        all_events.append(note)

# Create sequence
sequence = Sequence(events=all_events, tempo=120.0, time_signature=(4, 4))
print(f"Sequence duration: {sequence.duration} beats")
print(f"Total events: {len(sequence.events)}")

# Save to MIDI (commented out to avoid file creation)
# try:
#     midi_handler = MIDIHandler()
#     midi_handler.save_midi(sequence, "output.mid")
#     print("Saved to output.mid")
# except Exception as e:
#     print(f"Note: To save MIDI files, ensure music21 is installed: {e}")


# Example 5: Validate music theory rules
print("\n\nExample 5: Validating music theory rules")
print("-" * 50)

# Check if notes are in scale
for i, note in enumerate(melody[:3]):
    in_scale = c_major.get_pitches(octave=4, num_octaves=3)
    is_valid = note.pitch in in_scale
    print(f"Note {i+1} (pitch {note.pitch}) in C major scale: {is_valid}")

# Suggest next chord
current_degree = 0  # Tonic
suggestions = ChordProgressionRule.suggest_next_chord(current_degree, scale_type="major")
print(f"\nAfter tonic (I), suggested next chords (scale degrees): {suggestions}")


# Example 6: Create an arpeggio pattern
print("\n\nExample 6: Creating an arpeggio")
print("-" * 50)

arpeggio = melody_gen.generate_arpeggio(
    chord_intervals=MINOR_TRIAD,
    root_pitch=60,
    repetitions=2,
    duration=0.25
)

print(f"Generated arpeggio with {len(arpeggio)} notes")
print(f"Pattern: {[n.pitch for n in arpeggio]}")


print("\n" + "=" * 50)
print("Examples completed successfully!")
print("=" * 50)
