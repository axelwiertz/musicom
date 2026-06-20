"""
Advanced example: Complete music composition workflow
Demonstrates integration of all libraries and modules.
"""

from musicom.structures import (
    Note, Chord, Scale, Sequence,
    MAJOR_SCALE, MINOR_SCALE, PENTATONIC_MAJOR,
    MAJOR_TRIAD, MINOR_TRIAD, DOMINANT_SEVENTH
)
from musicom.generators import (
    MelodyGenerator, ChordProgressionGenerator, 
    RhythmGenerator, PatternGenerator
)
from musicom.transformers import (
    TranspositionTransformer, TimeTransformer,
    DynamicsTransformer, HarmonicTransformer,
    RhythmicTransformer, PatternTransformer
)
from musicom.rules import (
    HarmonicRule, MelodicRule, ChordProgressionRule,
    ScaleRule, VoiceLeadingRule
)
from musicom.io import MIDIHandler

print("=" * 70)
print("ADVANCED COMPOSITION EXAMPLE: Creating a Multi-Section Piece")
print("=" * 70)

# ============================================================================
# SECTION 1: Setup - Define musical parameters
# ============================================================================
print("\n### SECTION 1: Setup ###")
print("-" * 70)

# Define scales for different sections
c_major = Scale(root=0, intervals=MAJOR_SCALE, name="C Major")
a_minor = Scale(root=9, intervals=MINOR_SCALE, name="A Minor")
c_pentatonic = Scale(root=0, intervals=PENTATONIC_MAJOR, name="C Pentatonic")

print(f"Main scale: {c_major.name}")
print(f"Secondary scale: {a_minor.name}")
print(f"Bridge scale: {c_pentatonic.name}")

# ============================================================================
# SECTION 2: Generate main melody (A section)
# ============================================================================
print("\n### SECTION 2: Generate Main Melody (A Section) ###")
print("-" * 70)

melody_gen = MelodyGenerator(c_major, seed=42)
main_melody = melody_gen.generate_stepwise(
    length=16, 
    start_pitch=67,  # G4
    duration=0.5,
    max_interval=2
)

print(f"Generated main melody: {len(main_melody)} notes")
contour = MelodicRule.analyze_contour(main_melody)
print(f"Melodic contour: {contour}")

# Check if all notes are in scale
in_scale_count = sum(1 for note in main_melody 
                     if ScaleRule.check_note_in_scale(note, c_major))
print(f"Notes in C major scale: {in_scale_count}/{len(main_melody)}")

# ============================================================================
# SECTION 3: Generate chord progression
# ============================================================================
print("\n### SECTION 3: Generate Chord Progression ###")
print("-" * 70)

chord_gen = ChordProgressionGenerator(key_root=0, is_major=True, seed=42)
chords = chord_gen.generate_progression(num_chords=8, duration=1.0)

print(f"Generated chord progression: {len(chords)} chords")
for i, chord in enumerate(chords[:4]):
    quality = HarmonicRule.identify_chord_quality(chord)
    pitches = [n.pitch for n in chord.notes]
    print(f"  Chord {i+1}: {quality:12s} - pitches {pitches}")

# Check voice leading between first two chords
if len(chords) >= 2:
    smoothness = VoiceLeadingRule.smooth_voice_leading(chords[0], chords[1])
    print(f"Voice leading smoothness (chords 1-2): {smoothness:.2f} semitones average")

# ============================================================================
# SECTION 4: Create contrasting B section
# ============================================================================
print("\n### SECTION 4: Create Contrasting B Section ###")
print("-" * 70)

# Generate melody in relative minor
b_melody_gen = MelodyGenerator(a_minor, seed=123)
b_section_melody = b_melody_gen.generate_stepwise(
    length=8,
    start_pitch=69,  # A4
    duration=0.5,
    max_interval=3
)

# Transpose it to create variation
b_section_melody_var = [note.transpose(-2) for note in b_section_melody]

print(f"B section melody: {len(b_section_melody)} notes")
print(f"B section transposed down 2 semitones")

# ============================================================================
# SECTION 5: Apply transformations
# ============================================================================
print("\n### SECTION 5: Apply Creative Transformations ###")
print("-" * 70)

# 1. Add harmonization to main melody
harmonized_melody = HarmonicTransformer.harmonize(
    main_melody[:8], 
    intervals=[4, 7]  # Major third and perfect fifth
)
print(f"Harmonized main melody: {len(harmonized_melody)} notes (from {len(main_melody[:8])})")

# 2. Create a retrograde version for development
retrograde_melody = PatternTransformer.retrograde(main_melody[:8])
print(f"Created retrograde version of melody")

# 3. Apply crescendo to a phrase
phrase = main_melody[:4]
with_crescendo = DynamicsTransformer.add_crescendo(phrase, start_vel=50, end_vel=90)
print(f"Applied crescendo: velocity range {with_crescendo[0].velocity} to {with_crescendo[-1].velocity}")

# 4. Quantize timing for rhythmic precision
quantized = TimeTransformer.quantize(main_melody, grid=0.25)
print(f"Quantized melody to 16th note grid")

# 5. Add humanization for natural feel
humanized = RhythmicTransformer.humanize(
    quantized,
    timing_variance=0.015,
    velocity_variance=5
)
print(f"Humanized melody with subtle timing and velocity variations")

# ============================================================================
# SECTION 6: Create rhythmic accompaniment
# ============================================================================
print("\n### SECTION 6: Create Rhythmic Accompaniment ###")
print("-" * 70)

rhythm_gen = RhythmGenerator(seed=42)

# Generate a bass line using arpeggios
bass_notes = []
for i, chord in enumerate(chords[:4]):
    root_pitch = chord.root.pitch - 12  # Octave below
    arpeggio = melody_gen.generate_arpeggio(
        chord_intervals=[0, 7, 12, 7],  # Root, fifth, octave, fifth
        root_pitch=root_pitch,
        repetitions=1,
        duration=0.25
    )
    # Offset timing
    for note in arpeggio:
        note.start_time += i * 1.0
    bass_notes.extend(arpeggio)

print(f"Generated bass line: {len(bass_notes)} notes (arpeggiated chords)")

# Generate Euclidean rhythm for percussion
euclidean_pattern = rhythm_gen.generate_euclidean(pulses=5, steps=8)
print(f"Euclidean rhythm pattern: {euclidean_pattern} (5 pulses in 8 steps)")

# ============================================================================
# SECTION 7: Build complete composition
# ============================================================================
print("\n### SECTION 7: Assemble Complete Composition ###")
print("-" * 70)

all_events = []

# Add main melody (offset to start at measure 1)
for note in humanized:
    all_events.append(note)

# Add harmonized section (offset by 8 beats)
for note in harmonized_melody:
    new_note = Note(
        pitch=note.pitch,
        duration=note.duration,
        velocity=note.velocity - 15,  # Softer harmony
        start_time=note.start_time + 8.0
    )
    all_events.append(new_note)

# Add bass line
for note in bass_notes:
    all_events.append(note)

# Add B section (offset by 16 beats)
for note in b_section_melody:
    new_note = Note(
        pitch=note.pitch,
        duration=note.duration,
        velocity=note.velocity,
        start_time=note.start_time + 16.0
    )
    all_events.append(new_note)

# Create the final sequence
composition = Sequence(
    events=all_events,
    tempo=120.0,
    time_signature=(4, 4)
)

print(f"Total composition duration: {composition.duration:.1f} beats")
print(f"Total events: {len(composition.events)}")
print(f"Tempo: {composition.tempo} BPM")
print(f"Time signature: {composition.time_signature[0]}/{composition.time_signature[1]}")

# ============================================================================
# SECTION 8: Analysis and validation
# ============================================================================
print("\n### SECTION 8: Composition Analysis ###")
print("-" * 70)

# Analyze the main melody
main_melody_notes = [e for e in composition.events if isinstance(e, Note)][:16]
large_leaps = MelodicRule.check_large_leap(main_melody_notes, max_leap=7)
print(f"Large melodic leaps found: {len(large_leaps)}")

# Get suggested next chord
current_chord_degree = 0  # Starting on tonic
suggestions = ChordProgressionRule.suggest_next_chord(current_chord_degree, "major")
print(f"After I chord, suggested progressions: {suggestions}")

# Validate harmonic consistency
scale_notes = c_major.get_pitches(octave=3, num_octaves=3)
out_of_scale = sum(1 for note in main_melody_notes 
                   if note.pitch not in scale_notes)
print(f"Notes outside C major scale: {out_of_scale}/{len(main_melody_notes)}")

# ============================================================================
# SECTION 9: Export (optional - commented out)
# ============================================================================
print("\n### SECTION 9: Export Options ###")
print("-" * 70)

print("To export this composition to MIDI:")
print("  1. Uncomment the code below")
print("  2. Ensure music21 is installed")
print("  3. Run this script")
print("")
print("Example code:")
print("  midi_handler = MIDIHandler()")
print("  midi_handler.save_midi(composition, 'my_composition.mid')")

# Uncomment to actually save:
# try:
#     midi_handler = MIDIHandler()
#     midi_handler.save_midi(composition, "advanced_composition.mid")
#     print("\n✓ Successfully saved to 'advanced_composition.mid'")
# except Exception as e:
#     print(f"\n✗ Error saving MIDI: {e}")

# ============================================================================
# SECTION 10: Summary
# ============================================================================
print("\n" + "=" * 70)
print("COMPOSITION COMPLETE!")
print("=" * 70)
print(f"""
Summary:
  - Created multi-section composition (A-B form)
  - Used C Major and A Minor scales
  - Generated melodic content with step-wise motion
  - Created harmonic progression following music theory
  - Applied transformations: harmonization, retrograde, dynamics
  - Added bass line with arpeggiated chords
  - Validated composition against music theory rules
  - Total duration: {composition.duration:.1f} beats ({composition.duration/4:.1f} measures)
  - Total notes/events: {len(composition.events)}
  
This demonstrates the integration of:
  ✓ Structures (Note, Chord, Scale, Sequence)
  ✓ Generators (MelodyGenerator, ChordProgressionGenerator, RhythmGenerator)
  ✓ Transformers (all types: transposition, time, dynamics, harmonic, rhythmic, pattern)
  ✓ Rules (validation and analysis)
  ✓ I/O (MIDI export capability)
""")
print("=" * 70)
