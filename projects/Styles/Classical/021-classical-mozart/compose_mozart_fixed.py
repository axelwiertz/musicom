import music21
from music21 import instrument, note, chord, stream, tempo

# Create a stream for the composition
score = stream.Stream()
score.append(tempo.MetronomeMark(number=120))  # Moderato

# Define instrument
piano_inst = instrument.Piano()
# We'll have two parts: right hand (melody) and left hand (accompaniment)
rh_part = stream.Part()
rh_part.insert(0, piano_inst)
lh_part = stream.Part()
lh_part.insert(0, piano_inst)

# Helper to add a legato melody given a list of (pitch, duration) and a start offset.
# Returns the ending offset after the melody.
def add_legato_melody(part, pitch_dur_list, start_offset=0.0):
    current_offset = start_offset
    for pitch, dur in pitch_dur_list:
        n = note.Note(pitch)
        n.quarterLength = dur
        n.offset = current_offset
        part.insert(n.offset, n)  # insert at offset
        current_offset += dur * 0.75  # 25% overlap for next note
    # Return the estimated end offset (start of next note would be current_offset, but the last note ends at start_offset + sum(dur))
    # We'll compute the actual end by summing durations from start_offset
    total_dur = sum(dur for _, dur in pitch_dur_list)
    return start_offset + total_dur

# Helper to add Alberti bass accompaniment for a given number of beats, starting at a given offset.
# pattern_func: a function that takes beat index (0-based) and returns a list of (pitch, duration) for that beat (should sum to 1.0 beat)
def add_accompaniment(part, num_beats, start_offset, pattern_func):
    current_offset = start_offset
    for beat in range(num_beats):
        pattern = pattern_func(beat)  # list of (pitch, dur) for this beat
        for pitch, dur in pattern:
            n = note.Note(pitch)
            n.quarterLength = dur
            n.offset = current_offset
            part.insert(n.offset, n)
            current_offset += dur
    # After all beats, current_offset should be start_offset + num_beats
    return start_offset + num_beats

# --- Iteration 1: C major ---
melody1 = [
    (60, 1.0),   # C4
    (62, 0.5),   # D4
    (64, 0.5),   # E4
    (67, 1.0),   # G4
    (67, 1.0),   # G4
    (64, 0.5),   # E4
    (62, 0.5),   # D4
    (60, 1.0),   # C4
    (72, 1.0),   # C5
    (74, 0.5),   # D5
    (76, 0.5),   # E5
    (79, 1.0),   # G5
    (79, 1.0),   # G5
    (76, 0.5),   # E5
    (74, 0.5),   # D5
    (72, 1.0)    # C5
]
end1 = add_legato_melody(rh_part, melody1, start_offset=0.0)

# Accompaniment for iteration 1: Alberti bass on C major, 16 beats (4 measures)
def acc1_pattern(beat_idx):
    # Alberti bass: root, fifth, third, fifth (as eighth notes)
    # Each eighth note is 0.25 beat
    return [(36, 0.25), (43, 0.25), (52, 0.25), (43, 0.25)]  # C2, G2, E3, G2
end1_acc = add_accompaniment(lh_part, 16, start_offset=0.0, pattern_func=acc1_pattern)
# We'll assume the accompaniment ends at the same time as the melody (or we can take the max later)

# --- Iteration 2: G major ---
melody2 = [
    (67, 1.0),   # G4
    (69, 0.5),   # A4
    (71, 0.5),   # B4
    (72, 1.0),   # C5
    (72, 1.0),   # C5
    (71, 0.5),   # B4
    (69, 0.5),   # A4
    (67, 1.0),   # G4
    (79, 1.0),   # G5
    (81, 0.5),   # A5
    (83, 0.5),   # B5
    (84, 1.0),   # C6
    (84, 1.0),   # C6
    (83, 0.5),   # B5
    (81, 0.5),   # A5
    (79, 1.0)    # G5
]
start2 = end1  # start where first iteration ends (approx)
end2 = add_legato_melody(rh_part, melody2, start_offset=start2)

# Accompaniment for iteration 2: Alberti bass on G major, 16 beats
def acc2_pattern(beat_idx):
    # G major: G2, D3, B3
    return [(43, 0.25), (50, 0.25), (59, 0.25), (50, 0.25)]  # G2, D3, B3, D3
end2_acc = add_accompaniment(lh_part, 16, start_offset=start2, pattern_func=acc2_pattern)

# --- Iteration 3: C major with cadence ---
melody3 = [
    (60, 1.0),   # C4
    (62, 0.5),   # D4
    (64, 0.5),   # E4
    (65, 0.5),   # F4
    (67, 1.0),   # G4
    (67, 1.0),   # G4
    (65, 0.5),   # F4
    (64, 0.5),   # E4
    (62, 0.5),   # D4
    (60, 1.0),   # C4
    (72, 1.0),   # C5
    (74, 0.5),   # D5
    (76, 0.5),   # E5
    (77, 0.5),   # F5
    (79, 1.0),   # G5
    (79, 1.0),   # G5
    (77, 0.5),   # F5
    (76, 0.5),   # E5
    (74, 0.5),   # D5
    (72, 1.0)    # C5
]
start3 = end2  # start where second iteration ends
end3 = add_legato_melody(rh_part, melody3, start_offset=start3)

# Accompaniment for iteration 3: Alberti bass with cadential progression I - V - I
# We'll do: first 12 beats C major, next 2 beats G7 (using G major triad), last 2 beats C major
def acc3_pattern(beat_idx):
    if beat_idx < 12:
        # C major
        return [(36, 0.25), (43, 0.25), (52, 0.25), (43, 0.25)]
    elif beat_idx < 14:
        # G7 (using G major triad)
        return [(43, 0.25), (50, 0.25), (59, 0.25), (50, 0.25)]
    else:
        # C major again
        return [(36, 0.25), (43, 0.25), (52, 0.25), (43, 0.25)]
end3_acc = add_accompaniment(lh_part, 16, start_offset=start3, pattern_func=acc3_pattern)

# Add both parts to the score
score.insert(0, rh_part)
score.insert(0, lh_part)

# Write MIDI file
midi_path = "MIDI/mozart_classical.mid"
score.write('midi', fp=midi_path)
print(f"MIDI written to {midi_path}")

# Now render audio using fluidsynth if available
try:
    subprocess.run(['which', 'fluidsynth'], check=True, capture_output=True)
    soundfont = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    wav_path = "Audio/mozart_classical.wav"
    cmd = [
        'fluidsynth',
        '-ni',
        soundfont,
        midi_path,
        '-F',
        wav_path,
        '-r',
        '44100'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print(f"WAV rendered: {wav_path}")
        # Convert to OGG
        ogg_path = "Audio/mozart_classical.ogg"
        cmd = [
            'ffmpeg',
            '-y',
            '-i',
            wav_path,
            '-c:a',
            'libopus',
            '-application',
            'voip',
            '-b:a',
            '48k',
            ogg_path
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        print(f"OGG rendered: {ogg_path}")
    else:
        print(f"Fluidsynth error: {result.stderr}")
except (subprocess.CalledProcessError, FileNotFoundError):
    print("Fluidsynth not available or error, skipping audio rendering")

print("Done.")
