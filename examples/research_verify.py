"""
Verification script to test all framework components.
Run this after installation to ensure everything works.
"""

print("=" * 70)
print("MUSICOM FRAMEWORK VERIFICATION")
print("=" * 70)

# Test 1: Import all modules
print("\n[1/8] Testing imports...")
try:
    from musicom.structures import Note, Chord, Scale, Sequence, MAJOR_SCALE
    from musicom.generators import MelodyGenerator, ChordProgressionGenerator
    from musicom.transformers import TranspositionTransformer, TimeTransformer
    from musicom.rules import HarmonicRule, MelodicRule
    from musicom.io import MIDIHandler, PianoRollHandler
    print("✓ All modules imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    exit(1)

# Test 2: Create structures
print("\n[2/8] Testing structures...")
try:
    note = Note(pitch=60, duration=1.0)
    chord = Chord.from_intervals(60, [0, 4, 7])
    scale = Scale(root=0, intervals=MAJOR_SCALE)
    sequence = Sequence(events=[note], tempo=120.0)
    print(f"✓ Created note (pitch={note.pitch}), chord, scale, sequence")
except Exception as e:
    print(f"✗ Structure creation failed: {e}")
    exit(1)

# Test 3: Generate melody
print("\n[3/8] Testing melody generation...")
try:
    gen = MelodyGenerator(scale, seed=42)
    melody = gen.generate_stepwise(length=8)
    print(f"✓ Generated melody with {len(melody)} notes")
except Exception as e:
    print(f"✗ Melody generation failed: {e}")
    exit(1)

# Test 4: Generate chords
print("\n[4/8] Testing chord progression...")
try:
    chord_gen = ChordProgressionGenerator(key_root=0, is_major=True)
    chords = chord_gen.generate_progression(num_chords=4)
    print(f"✓ Generated chord progression with {len(chords)} chords")
except Exception as e:
    print(f"✗ Chord generation failed: {e}")
    exit(1)

# Test 5: Apply transformations
print("\n[5/8] Testing transformations...")
try:
    transposed = TranspositionTransformer.transpose_note(note, 5)
    stretched = TimeTransformer.time_stretch([note], 2.0)
    print(f"✓ Transposed note to pitch {transposed.pitch}")
    print(f"✓ Time stretched to duration {stretched[0].duration}")
except Exception as e:
    print(f"✗ Transformation failed: {e}")
    exit(1)

# Test 6: Validate with rules
print("\n[6/8] Testing music theory rules...")
try:
    quality = HarmonicRule.identify_chord_quality(chord)
    contour = MelodicRule.analyze_contour(melody)
    print(f"✓ Identified chord quality: {quality}")
    print(f"✓ Analyzed melodic contour: {contour}")
except Exception as e:
    print(f"✗ Rules validation failed: {e}")
    exit(1)

# Test 7: I/O handlers
print("\n[7/8] Testing I/O handlers...")
try:
    midi_handler = MIDIHandler()
    piano_handler = PianoRollHandler()
    print("✓ MIDI handler initialized (Music21)")
    print("✓ Piano roll handler initialized (PyPianoroll)")
except Exception as e:
    print(f"✗ I/O handler initialization failed: {e}")
    exit(1)

# Test 8: Integration
print("\n[8/8] Testing library integration...")
try:
    # Test Music21 integration
    import music21
    m21_stream = midi_handler.notes_to_music21(melody)
    print(f"✓ Converted to Music21 stream: {len(m21_stream.flat.notes)} notes")
    
    # Test PyPianoroll integration
    test_seq = Sequence(events=melody, tempo=120.0)
    multitrack = piano_handler.sequence_to_pianoroll(test_seq, resolution=24)
    print(f"✓ Converted to piano roll: shape {multitrack.tracks[0].pianoroll.shape}")
except Exception as e:
    print(f"✗ Integration test failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("ALL TESTS PASSED ✓")
print("=" * 70)
print("\nFramework is ready to use!")
print("Try running: python examples.py")
print("Or: python advanced_example.py")
