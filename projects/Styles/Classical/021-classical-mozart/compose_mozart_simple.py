import music21
from music21 import instrument, note, chord, stream, tempo
import subprocess
import os

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

# We'll create three iterations (each 2 measures? Let's do 4 measures each for a total of 12 measures)
# Each iteration is 4 measures (4/4) = 16 quarter notes.

# We'll define the melody and accompaniment for each iteration as lists of (offset, pitch, duration)
# where offset is in quarter lengths from the start of the iteration.

# Iteration 1: Theme in C major
# Melody: a simple tune
# We'll use quarter and eighth notes.
# We'll create a list of notes for the right hand.
# We'll set the offset for each note.

# Let's define the melody for iteration 1 as a series of notes at specific offsets.
# We'll use the following melody (in quarter notes from start of iteration):
#   Measure 1: C4 (1), D4 (0.5), E4 (0.5), G4 (1)  -> offsets: 0,1,2,3
#   Measure 2: G4 (1), E4 (0.5), D4 (0.5), C4 (1)  -> offsets: 4,5,6,7
#   Measure 3: C5 (1), D5 (0.5), E5 (0.5), G5 (1)  -> offsets: 8,9,10,11
#   Measure 4: G5 (1), E5 (0.5), D5 (0.5), C5 (1)  -> offsets: 12,13,14,15
# But we want to make it legato, so we will start each note slightly before the previous one ends.
# We'll do that by setting the offset of each note to be the previous note's offset plus 0.75 * its duration.
# We'll compute the offsets iteratively.

# We'll define the melody as a list of (pitch, duration) in quarter lengths.
melody1_pitch_dur = [
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

# Now we compute the offsets for legato: each note starts at the previous offset + 0.75 * previous duration.
# We'll set the first note's offset to 0.
melody1_offsets = []
current_offset = 0.0
for pitch, dur in melody1_pitch_dur:
    melody1_offsets.append((current_offset, pitch, dur))
    current_offset += dur * 0.75  # 25% overlap

# Now we add these notes to the right hand part.
for offset, pitch, dur in melody1_offsets:
    n = note.Note(pitch)
    n.quarterLength = dur
    n.offset = offset
    rh_part.insert(n.offset, n, endTuple=False)

# Now the accompaniment for iteration 1: Alberti bass on C major for each quarter note beat.
# We'll split each beat into four eighth notes (each 0.25 quarter length).
# We'll create a pattern for each beat: [root, fifth, third, fifth] in the bass clef.
# We'll use C2, G2, E3, G2 (but we can adjust octaves).
# We'll create a list of notes for the left hand part.

# We have 16 beats (4 measures * 4 beats per measure).
# For each beat, we play the Alberti bass pattern.
# We'll set the offset for each eighth note.

# We'll create a list for the left hand notes.
lh_notes1 = []
# Alberti bass pattern for C major: root (C2), fifth (G2), third (E3), fifth (G2)
# We'll use: C2=36, G2=43, E3=52, G2=43
pattern1 = [36, 43, 52, 43]
# For each beat (0 to 15)
for beat in range(16):
    beat_offset = beat * 1.0  # each beat starts at quarter note beat
    for i, pitch in enumerate(pattern1):
        # Each eighth note in the pattern starts at beat_offset + i * 0.25
        note_offset = beat_offset + i * 0.25
        lh_notes1.append((note_offset, pitch, 0.25))

# Now add these notes to the left hand part.
for offset, pitch, dur in lh_notes1:
    n = note.Note(pitch)
    n.quarterLength = dur
    n.offset = offset
    lh_part.insert(n.offset, n, endTuple=False)

# Now we need to add the second and third iterations.
# We'll do similarly but with different melodies and accompaniments.

# Iteration 2: Development in G major
# We'll shift the melody up a perfect fourth? Actually, we'll go to G major.
# We'll use a similar rhythm but in G major.

melody2_pitch_dur = [
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

# Compute legato offsets for melody2
melody2_offsets = []
current_offset = 0.0  # we will start this iteration after the first one ends.
# But we need to know where the first iteration ends.
# We'll approximate the end of the first iteration as the last note's offset + its duration.
# We'll compute that from melody1_offsets.
if melody1_offsets:
    last_offset, last_pitch, last_dur = melody1_offsets[-1]
    iteration1_end = last_offset + last_dur
else:
    iteration1_end = 0.0
# We'll add a small gap? Let's just start the second iteration at the end of the first.
current_offset = iteration1_end

for pitch, dur in melody2_pitch_dur:
    melody2_offsets.append((current_offset, pitch, dur))
    current_offset += dur * 0.75

# Add melody2 notes to the right hand part.
for offset, pitch, dur in melody2_offsets:
    n = note.Note(pitch)
    n.quarterLength = dur
    n.offset = offset
    rh_part.insert(n.offset, n, endTuple=False)

# Accompaniment for iteration 2: Alberti bass on G major.
# G major: G2, D3, B3
# Pattern: root, fifth, third, fifth -> G2, D3, B3, D3
# We'll use: G2=43, D3=50, B3=59
pattern2 = [43, 50, 59, 50]
# We'll create notes for the left hand part, continuing from where the first iteration left off.
# We need to know the offset for the left hand part. We'll continue from the end of the first iteration's accompaniment.
# We'll assume the first iteration's accompaniment ended at iteration1_end (same as melody).
# We'll start the second iteration's accompaniment at iteration1_end.
# We'll create 16 beats of accompaniment for the second iteration.
lh_notes2 = []
for beat in range(16):
    beat_offset = iteration1_end + beat * 1.0
    for i, pitch in enumerate(pattern2):
        note_offset = beat_offset + i * 0.25
        lh_notes2.append((note_offset, pitch, 0.25))

for offset, pitch, dur in lh_notes2:
    n = note.Note(pitch)
    n.quarterLength = dur
    n.offset = offset
    lh_part.insert(n.offset, n, endTuple=False)

# Iteration 3: Recapitulation in C major with variation.
# We'll use a melody that is similar to the first but with some embellishments and a cadence.

melody3_pitch_dur = [
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

# Compute legato offsets for melody3, starting after the second iteration.
# We need the end of the second iteration.
if melody2_offsets:
    last_offset2, last_pitch2, last_dur2 = melody2_offsets[-1]
    iteration2_end = last_offset2 + last_dur2
else:
    iteration2_end = iteration1_end  # fallback
current_offset = iteration2_end

for pitch, dur in melody3_pitch_dur:
    melody3_offsets.append((current_offset, pitch, dur))
    current_offset += dur * 0.75

# Add melody3 notes to the right hand part.
for offset, pitch, dur in melody3_offsets:
    n = note.Note(pitch)
    n.quarterLength = dur
    n.offset = offset
    rh_part.insert(n.offset, n, endTuple=False)

# Accompaniment for iteration 3: Alberti bass on C major, but with a cadential progression: I - V - I in the last two measures.
# We'll do:
#   First 12 beats (first three measures): C major Alberti bass
#   Beat 12 and 13: G7 Alberti bass (we'll use G major triad for simplicity)
#   Beat 14 and 15: C major Alberti bass
# We'll create 16 beats.

pattern3_C = [36, 43, 52, 43]  # C major
pattern3_G = [43, 50, 59, 50]  # G major

lh_notes3 = []
for beat in range(16):
    beat_offset = iteration2_end + beat * 1.0
    if beat < 12:
        pattern = pattern3_C
    elif beat < 14:
        pattern = pattern3_G
    else:
        pattern = pattern3_C
    for i, pitch in enumerate(pattern):
        note_offset = beat_offset + i * 0.25
        lh_notes3.append((note_offset, pitch, 0.25))

for offset, pitch, dur in lh_notes3:
    n = note.Note(pitch)
    n.quarterLength = dur
    n.offset = offset
    lh_part.insert(n.offset, n, endTuple=False)

# Now add both parts to the score
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
