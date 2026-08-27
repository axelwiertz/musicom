import music21
from music21 import instrument, note, chord, stream, tempo, duration, harmony
import subprocess
import os

# Create a stream for the composition
score = stream.Stream()
score.append(tempo.MetronomeMark(number=120))  # Moderato

# Define instrument
piano_inst = instrument.Piano()
piano_part = stream.Part()
piano_part.insert(0, piano_inst)

# We'll create three iterations
# Each iteration is a phrase of 4 measures (in 4/4)
# We'll use legato by overlapping notes

# Helper to add a legato melody line given a list of (pitch, quarterLength) pairs
# and a start offset. We'll set the offset of each note such that it starts
# before the previous note ends (overlap by 25% of its duration, for example).
def add_legato_melody(part, note_list, start_offset=0.0):
    """
    note_list: list of tuples (pitch_midi, quarter_length)
    start_offset: where to start the first note (in quarter lengths)
    """
    current_offset = start_offset
    for i, (pitch, ql) in enumerate(note_list):
        n = note.Note(pitch)
        n.quarterLength = ql
        # For legato, we want the next note to start before this one ends.
        # We'll set the offset of the note to current_offset.
        # The next note's offset will be current_offset + ql * overlap_factor
        # We'll use an overlap factor of 0.75 (so next note starts at 75% of this note's duration)
        # Actually, we'll set the offset of the note to current_offset, and then
        # update current_offset for the next note.
        n.offset = current_offset
        part.insert(n.offset, n, endTuple=False)  # insert without specifying end time? 
        # Actually, we should set the offset and let the duration define the end.
        # The next note's offset will be set later.
        # For legato, we want the next note to start before this one ends.
        # So we will set the offset of the next note to be current_offset + ql * 0.75
        # But we don't know the next note yet. We'll handle it in the loop.
        # Instead, we'll adjust the offset of each note after we know the next?
        # Let's do a simpler approach: we'll set the offset of each note as we go,
        # and then after inserting all notes, we'll adjust the offsets to create overlap.
        # But music21's insert uses offset to determine position.
        # We'll instead create notes with a given offset and duration, and then
        # we can adjust the offset of each note after creation? 
        # Actually, we can set the offset attribute of the note before inserting.
        # We'll do that.
        # We'll set the offset to current_offset, then update current_offset for the next note.
        # To create legato, we want the next note to start before this one ends.
        # So we will set the offset increment to be less than the current note's quarterLength.
        # Let's use an overlap of 25%: i.e., the next note starts when 75% of the current note has elapsed.
        # So increment = ql * 0.75
        # But for the first note, we set offset = start_offset.
        # Then we add the note, then update current_offset += ql * 0.75
        # However, this means the note will actually end at offset + ql, which is later than the next note's start.
        # That's what we want for legato: overlap.
        # We'll do that.
        # But note: we must also set the note's offset attribute.
        n.offset = current_offset
        part.insert(n, endTuple=False)  # This inserts at the offset we set.
        # Update current_offset for the next note
        current_offset += ql * 0.75  # 75% of the duration -> 25% overlap
        # However, we also need to consider that the note's duration is ql, so the actual end is at offset + ql.
        # The next note will start at current_offset (which is offset + ql*0.75), so there is an overlap of ql - 0.75*ql = 0.25*ql.
        # That's a 25% overlap.
        # For the last note, we don't need to update current_offset further, but we'll do it anyway.

# Now define the material for each iteration.

# Iteration 1: Simple theme in C major
# We'll create a melody that is legato, using eighth notes and quarter notes.
# We'll also add an Alberti bass accompaniment.

# Let's define the melody for iteration 1 as a series of notes.
# We'll use quarter lengths for simplicity, but we can vary.
# We'll create a list of (pitch, ql) where pitch is MIDI note number.
# We'll use C4 = 60 as middle C.

# Theme: C D E G | G E D C | (first 4 beats) then repeat an octave higher? 
# Let's make it: 
# Measure 1: C4 (quarter), D4 (eighth), E4 (eighth), G4 (quarter) -> beats 1, 2+, 3, 4
# Measure 2: G4 (quarter), E4 (eighth), D4 (eighth), C4 (quarter)
# Then repeat up an octave: 
# Measure 3: C5 (quarter), D5 (eighth), E5 (eighth), G5 (quarter)
# Measure 4: G5 (quarter), E5 (eighth), D5 (eighth), C5 (quarter)

# We'll convert to a list of (pitch, ql) in quarter lengths.
# We'll also want to add some pickup or something? Let's keep simple.

melody1 = [
    (60, 1.0),   # C4 quarter
    (62, 0.5),   # D4 eighth
    (64, 0.5),   # E4 eighth
    (67, 1.0),   # G4 quarter
    (67, 1.0),   # G4 quarter (second measure start)
    (64, 0.5),   # E4 eighth
    (62, 0.5),   # D4 eighth
    (60, 1.0),   # C4 quarter
    (72, 1.0),   # C5 quarter
    (74, 0.5),   # D5 eighth
    (76, 0.5),   # E5 eighth
    (79, 1.0),   # G5 quarter
    (79, 1.0),   # G5 quarter
    (76, 0.5),   # E5 eighth
    (74, 0.5),   # D5 eighth
    (72, 1.0)    # C5 quarter
]

# Now we'll add this melody to the piano part with legato.
# We'll start at offset 0.0.
add_legato_melody(piano_part, melody1, start_offset=0.0)

# Now we need to add accompaniment (Alberti bass) for the left hand.
# We'll create a second part for left hand? Or we can put both hands in the same part? 
# Better to have two parts: right hand (melody) and left hand (accompaniment).
# We'll create a second part for left hand.

left_hand_part = stream.Part()
left_hand_part.insert(0, instrument.Piano())  # same instrument but we can still have two parts

# Alberti bass pattern: for a C major chord, the pattern is: root, fifth, third, fifth (in eighth notes)
# We'll play this pattern per quarter note beat? Actually, Alberti bass is usually a broken chord pattern played as eighth notes.
# For each beat (quarter note), we play four eighth notes: root, fifth, third, fifth.
# We'll do that for each chord in the harmony.

# We'll define the harmony for each iteration.
# For iteration 1, we'll use a simple I - V - I - I? Actually, we can just arpeggiate C major triad throughout.
# But to make it more interesting, we can change chords: maybe I - vi - IV - V or something.
# Let's keep it simple: just C major arpeggio in Alberti bass pattern for the whole first iteration.

# We'll generate the Alberti bass pattern for each quarter note.
# We'll create a list of notes for the left hand part.

# We'll define the chord as C major: C3, E3, G3 (but we'll spread over octaves)
# Alberti bass pattern in eighth notes: [root, fifth, third, fifth] 
# Where root = C3 (48), fifth = G3 (55), third = E3 (52)
# We'll play this pattern repeatedly, each pattern lasting one beat (quarter note) but consisting of four eighth notes.
# So each eighth note is 0.5 quarter length.

# We'll create a list of (pitch, ql) for the left hand, where ql = 0.5 for each eighth note.
# We'll repeat the pattern for as many beats as we have in the melody.
# The melody1 above has a total duration? Let's compute: 
# We'll compute the total duration of melody1 by summing the quarter lengths, but note that because of legato overlap, the actual end time will be less.
# For simplicity, we'll assume the melody spans 4 measures (4 beats per measure * 4 measures = 16 quarter notes) if we ignore overlap.
# Actually, our melody1 has 16 notes? Let's count: 
#   The list has 16 entries? Let's see: 
#   [ (60,1.0), (62,0.5), (64,0.5), (67,1.0), (67,1.0), (64,0.5), (62,0.5), (60,1.0), (72,1.0), (74,0.5), (76,0.5), (79,1.0), (79,1.0), (76,0.5), (74,0.5), (72,1.0) ] -> 16 notes.
#   If we sum the quarter lengths: 1.0+0.5+0.5+1.0+1.0+0.5+0.5+1.0+1.0+0.5+0.5+1.0+1.0+0.5+0.5+1.0 = 16.0 quarter notes.
#   So 4 measures of 4/4 (16 quarter notes) exactly.

# So we'll create 16 beats worth of Alberti bass, each beat split into 4 eighth notes.

left_hand_notes = []
# Define the Alberti bass pattern for C major: [root, fifth, third, fifth] as eighth notes
pattern = [48, 55, 52, 55]  # C3, G3, E3, G3
# We'll repeat this pattern for 16 beats (since each pattern is one beat)
for beat in range(16):
    for i, pitch in enumerate(pattern):
        # Each eighth note starts at beat*0.5 + i*0.5? Actually, each eighth note is 0.5 quarter length.
        # So the offset for the i-th eighth note in beat b is: b*0.5 + i*0.5
        offset = beat * 0.5 + i * 0.5
        left_hand_notes.append((pitch, 0.5))

# Now we add these notes to the left hand part without legato (since accompaniment is usually not legato? 
# Actually, Alberti bass can be played legato as well, but we'll keep it detached for clarity.
# We'll just set the offset and duration without overlap.
for pitch, ql in left_hand_notes:
    n = note.Note(pitch)
    n.quarterLength = ql
    n.offset = current_offset  # Wait, we need to track offset separately.
    # We'll just set offset as we go.
    # Let's do a simple loop with a running offset.
    pass

# Let's instead create a simple loop to add notes with offset.
current_offset = 0.0
for pitch, ql in left_hand_notes:
    n = note.Note(pitch)
    n.quarterLength = ql
    n.offset = current_offset
    left_hand_part.insert(n.offset, n, endTuple=False)
    current_offset += ql  # no overlap, just add the duration

# Now we have the first iteration. We'll add a small gap between iterations? 
# We'll just continue the second iteration after the first.

# Now we need to define iteration 2 and 3.

# But before that, let's combine the parts into the score.
score.insert(0, piano_part)
score.insert(0, left_hand_part)

# However, we haven't written the MIDI yet. Let's continue to define iterations 2 and 3.

# We'll reset the current_offset for the next iteration? Actually, we want the iterations to follow sequentially.
# We'll keep a running offset variable that we pass to the add_legato_melody function.

# Let's refactor: we'll create a function that adds an iteration (melody and accompaniment) starting at a given offset,
# and returns the ending offset.

def add_iteration(score, melody_pattern, chord_pattern_func, start_offset):
    """
    melody_pattern: list of (pitch, ql) for the right hand melody
    chord_pattern_func: a function that given a beat index (0-based) and start offset of the beat, 
                        returns a list of (pitch, ql) for the left hand accompaniment for that beat (e.g., Alberti bass)
    start_offset: where to start this iteration (in quarter lengths)
    Returns the ending offset after this iteration.
    """
    # We'll create a part for right hand and left hand for this iteration.
    rh_part = stream.Part()
    rh_part.insert(0, instrument.Piano())
    lh_part = stream.Part()
    lh_part.insert(0, instrument.Piano())
    
    # Add melody with legato
    # We need to know the total duration of the melody pattern to compute the overlap correctly?
    # Our add_legato_melody function assumes we want to chain notes with overlap.
    # We'll use it as is, but we need to pass the start_offset.
    add_legato_melody(rh_part, melody_pattern, start_offset=start_offset)
    
    # Now we need to compute the ending offset of the melody to know where the accompaniment should go.
    # Since we used overlap, the actual end time of the melody is not simply start_offset + sum(ql).
    # We'll approximate by using the offset of the last note plus its quarter length.
    # We'll compute the last note's offset and length from the rh_part.
    # But for simplicity, we'll assume the melody duration is the sum of the quarter lengths (ignoring overlap) 
    # because the overlap is only for legato and the notes still sound for their full duration.
    # Actually, in legato, the note does sound for its full duration, but the next note starts before it ends.
    # So the offset of the last note plus its quarter length is still the correct end time.
    # We'll compute that.
    if len(rh_part.notes) > 0:
        last_note = rh_part.notes[-1]
        melody_end = last_note.offset + last_note.quarterLength
    else:
        melody_end = start_offset  # fallback
    
    # Now we generate accompaniment from start_offset to melody_end.
    # We'll split the time into beats (quarter notes).
    # We'll assume a tempo of 120 BPM, so each quarter note is 0.5 seconds, but we work in quarter lengths.
    # We'll generate accompaniment for each quarter note beat from start_offset to melody_end.
    # We'll round to the nearest eighth note? We'll just generate for each quarter note.
    # Number of beats = (melody_end - start_offset)  (since each beat is 1 quarter length)
    num_beats = int(round(melody_end - start_offset))
    # We'll generate accompaniment for each beat.
    current_acc_offset = start_offset
    for beat_idx in range(num_beats):
        # Get the accompaniment pattern for this beat (relative to the beat start)
        acc_notes = chord_pattern_func(beat_idx)  # returns list of (pitch, ql) for the beat, where ql is in quarter lengths, and the pattern should sum to 1.0 (one beat)
        # Now we add each note in the pattern at the current offset.
        for pitch, ql in acc_notes:
            n = note.Note(pitch)
            n.quarterLength = ql
            n.offset = current_acc_offset
            lh_part.insert(n.offset, n, endTuple=False)
            current_acc_offset += ql
    # After processing all beats, we should have current_acc_offset == melody_end (approximately)
    
    # Add the parts to the score
    score.insert(0, rh_part)
    score.insert(0, lh_part)
    
    return melody_end

# Now we define the melody patterns for each iteration and the accompaniment functions.

# Iteration 1: as before
melody1 = [
    (60, 1.0),   # C4 quarter
    (62, 0.5),   # D4 eighth
    (64, 0.5),   # E4 eighth
    (67, 1.0),   # G4 quarter
    (67, 1.0),   # G4 quarter
    (64, 0.5),   # E4 eighth
    (62, 0.5),   # D4 eighth
    (60, 1.0),   # C4 quarter
    (72, 1.0),   # C5 quarter
    (74, 0.5),   # D5 eighth
    (76, 0.5),   # E5 eighth
    (79, 1.0),   # G5 quarter
    (79, 1.0),   # G5 quarter
    (76, 0.5),   # E5 eighth
    (74, 0.5),   # D5 eighth
    (72, 1.0)    # C5 quarter
]

# Accompaniment for iteration 1: Alberti bass on C major chord for each beat.
def acc1(beat_idx):
    # Alberti bass pattern: root, fifth, third, fifth (as eighth notes)
    # We'll use C3, G3, E3, G3
    return [(48, 0.25), (55, 0.25), (52, 0.25), (55, 0.25)]  # each eighth note is 0.25 quarter length? Wait, we need each eighth note to be 0.25? 
    # Actually, we want four eighth notes to make one beat (quarter note). So each eighth note is 0.25 quarter length.
    # Yes, because 4 * 0.25 = 1.0.
    # So we return list of (pitch, 0.25)
    # But our earlier left_hand_notes used ql=0.5 for eighth notes, which was wrong.
    # Let's correct: we want each eighth note to be 0.25 quarter length.
    # However, in our earlier left_hand_notes we used 0.5, which would make each eighth note a quarter note, leading to eighth notes being half a beat? 
    # Let's fix: we want the pattern to be four eighth notes per beat, so each eighth note = 0.25 quarter length.
    # We'll change the acc function to return (pitch, 0.25).
    # But note: the beat duration is 1.0 quarter length, so four notes of 0.25 each sum to 1.0.
    return [(48, 0.25), (55, 0.25), (52, 0.25), (55, 0.25)]

# Iteration 2: develop the theme, maybe modulate to G major.
# We'll vary the melody: maybe use a similar rhythm but different notes, or invert the melody.
# We'll create a melody that is a variation: 
#   Start on G, go up to D, etc.
# We'll also change the accompaniment to G major.

melody2 = [
    (67, 1.0),   # G4 quarter
    (69, 0.5),   # A4 eighth
    (71, 0.5),   # B4 eighth
    (72, 1.0),   # C5 quarter
    (72, 1.0),   # C5 quarter
    (71, 0.5),   # B4 eighth
    (69, 0.5),   # A4 eighth
    (67, 1.0),   # G4 quarter
    (79, 1.0),   # G5 quarter
    (81, 0.5),   # A5 eighth
    (83, 0.5),   # B5 eighth
    (84, 1.0),   # C5 quarter? Wait, C5 is 72, actually C5 is 72, D5 is 74, E5 is 76, G5 is 79, A5 is 81, B5 is 83.
    # Let's do: G5, A5, B5, C6? 
    # We'll do: G5, A5, B5, C6 (84) for the last four notes? 
    # Let's redesign melody2 to be a development: 
    #   We'll use the same rhythm but start on G4 and go up to C5 then back to G4, then up an octave.
    #   We'll do: 
    #   G4 A B C5 | C5 B A G4 | 
    #   G5 A5 B5 C6 | C6 B5 A5 G5 |
    # Let's define that.
]
# Let's rewrite melody2 clearly:
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

# Accompaniment for iteration 2: Alberti bass on G major chord.
def acc2(beat_idx):
    # G major: G3, D3, B3
    # Pattern: root, fifth, third, fifth
    return [(55, 0.25), (62, 0.25), (59, 0.25), (62, 0.25)]  # G3=55, D3=62, B3=59

# Iteration 3: return to C major with embellishments, maybe a turning figure or a trill.
# We'll create a melody that ends with a cadence.

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

# Accompaniment for iteration 3: Alberti bass on C major, but maybe with a cadential progression: I - V - I
# We'll make the accompaniment change chords: 
#   First half: C major
#   Second half: G7 then C major? 
# We'll do: 
#   Beats 0-7: C major Alberti bass
#   Beats 8-15: G7 Alberti bass for first two beats, then C major for last two beats? 
#   Actually, we want a cadence: V7 to I in the last two beats.
#   Let's do: 
#   Beats 0-11: C major Alberti bass
#   Beat 12: G7 Alberti bass (but we need to split the beat into four eighth notes)
#   Beat 13: G7 Alberti bass
#   Beat 14: C major Alberti bass
#   Beat 15: C major Alberti bass
#   But we want the V7 to last for two beats? 
#   Let's do: 
#   Beats 0-11: C major
#   Beat 12: G7
#   Beat 13: G7
#   Beat 14: C major
#   Beat 15: C major
#   That's two beats of V7 then two beats of I.
#   We'll implement acc3 to return the pattern based on beat_idx.

def acc3(beat_idx):
    if beat_idx < 12:
        # C major
        return [(48, 0.25), (55, 0.25), (52, 0.25), (55, 0.25)]
    elif beat_idx < 14:
        # G7: G3, B3, D3, F3 (root, third, fifth, seventh) but Alberti bass pattern? We'll use root, fifth, third, fifth as before.
        # For G7 chord, we can still use the triad (G, B, D) ignoring the seventh for simplicity.
        return [(55, 0.25), (62, 0.25), (59, 0.25), (62, 0.25)]  # G3, D3, B3, D3
    else:
        # C major again
        return [(48, 0.25), (55, 0.25), (52, 0.25), (55, 0.25)]

# Now we add the three iterations sequentially.
current_offset = 0.0
current_offset = add_iteration(score, melody1, acc1, current_offset)
current_offset = add_iteration(score, melody2, acc2, current_offset)
current_offset = add_iteration(score, melody3, acc3, current_offset)

# Now we have the score with all parts.

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
