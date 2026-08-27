import subprocess
import music21
from music21 import instrument, note, chord, stream, tempo

# Create a stream for our Afrobeat groove
midi_stream = stream.Stream()
midi_stream.append(tempo.MetronomeMark(number=110))  # 110 BPM

# Define instruments
drums = instrument.Percussion()
bass = instrument.ElectricBass()
piano = instrument.ElectricPiano()
horns = instrument.Horn()  # Using horn for simplicity
guitar = instrument.ElectricGuitar()

# Create parts
drums_part = stream.Part()
drums_part.insert(0, drums)
bass_part = stream.Part()
bass_part.insert(0, bass)
piano_part = stream.Part()
piano_part.insert(0, piano)
horns_part = stream.Part()
horns_part.insert(0, horns)
guitar_part = stream.Part()
guitar_part.insert(0, guitar)

# Parameters
num_bars = 2
quarters_per_bar = 4
# We'll work in eighth notes for flexibility
eighths_per_bar = 8  # because 2 eighth notes per quarter note
total_eighths = num_bars * eighths_per_bar  # 16 eighth notes

# --- Drums ---
# Kick: on specific eighth notes (0, 2, 6, 8, 12) in the first bar? Let's define for two bars.
# We'll define a pattern for one bar and repeat.
# Kick pattern per bar (in eighth notes): [0, 2, 6]  -> beat1 down, beat1 and, beat2.5? 
# Let's use the pattern we discussed: kick on 1, 1.5, 2.5, 3, 4 (in quarter notes) -> convert to eighth notes:
#   Quarter note 1.0 -> eighth note 0 (down)
#   Quarter note 1.5 -> eighth note 1 (up)
#   Quarter note 2.5 -> eighth note 5 (up of beat2)
#   Quarter note 3.0 -> eighth note 4 (down of beat3)
#   Quarter note 4.0 -> eighth note 6 (down of beat4)
# So kick pattern per bar: [0, 1, 5, 4, 6] -> but note: 4 and 5 are swapped? Let's sort: [0,1,4,5,6]
# Actually, let's list the eighth notes for the kicks we want:
#   Beat 1 down: 0
#   Beat 1 and: 1
#   Beat 2.5 down? Wait, beat 2.5 is the up of beat2 -> eighth note 5? 
#   Beat 3 down: 4
#   Beat 4 down: 6
# So pattern: [0,1,5,4,6] -> but we want to play in time order: 0,1,4,5,6
# Let's use: [0,1,4,5,6] for one bar.
kick_pattern_per_bar = [0, 1, 4, 5, 6]
# For two bars, we repeat and offset by 8 for the second bar.
kick_pattern = []
for bar in range(num_bars):
    offset = bar * eighths_per_bar
    for idx in kick_pattern_per_bar:
        kick_pattern.append(offset + idx)

# Snare: on beats 2 and 4 -> in eighth notes: beat 2 down is 4, beat 4 down is 6? 
# Wait, beat 2 down is at quarter note 2.0 -> eighth note 4 (since 2*2 = 4)
# Beat 4 down is at quarter note 4.0 -> eighth note 8? 
# Actually, for one bar: 
#   Beat 2 down: 4
#   Beat 4 down: 12? No, because we are in one bar: 
#   Let's recalc for one bar (0-7 eighth notes):
#       Beat 1 down: 0
#       Beat 1 up: 1
#       Beat 2 down: 2
#       Beat 2 up: 3
#       Beat 3 down: 4
#       Beat 3 up: 5
#       Beat 4 down: 6
#       Beat 4 up: 7
#   So snare on beat 2 down (2) and beat 4 down (6) -> but wait, that's the downbeat of 2 and 4.
#   However, in Afrobeat, the snare is often on the backbeat (beats 2 and 4) which are the downbeats.
#   So snare pattern per bar: [2, 6]
snare_pattern_per_bar = [2, 6]
snare_pattern = []
for bar in range(num_bars):
    offset = bar * eighths_per_bar
    for idx in snare_pattern_per_bar:
        snare_pattern.append(offset + idx)

# Hi-hat: play every eighth note with velocity accent on the upbeats (the "and" of each beat)
# In eighth notes, the upbeats are the odd indices: 1,3,5,7,9,11,13,15
hi_hat_pattern = list(range(total_eighths))  # all eighth notes
hi_hat_velocities = []
for i in range(total_eighths):
    if i % 2 == 1:  # upbeat (the "and")
        hi_hat_velocities.append(100)
    else:  # downbeat
        hi_hat_velocities.append(60)

# Add drum notes
for idx in kick_pattern:
    n = note.Note(35)  # Acoustic Bass Drum
    n.quarterLength = 0.5  # eighth note
    n.velocity = 100
    drums_part.insert(idx * 0.5, n)  # because each eighth note is 0.5 quarter lengths

for idx in snare_pattern:
    n = note.Note(38)  # Acoustic Snare Drum
    n.quarterLength = 0.5
    n.velocity = 100
    drums_part.insert(idx * 0.5, n)

for i, idx in enumerate(hi_hat_pattern):
    n = note.Note(42)  # Closed Hi Hat
    n.quarterLength = 0.5
    n.velocity = hi_hat_velocities[i]
    drums_part.insert(idx * 0.5, n)

# --- Bass ---
# Bass pattern: we defined a pattern of eighth notes where we play notes.
# We'll use the pattern: [0,1,2,5,6,8,9,10,13,14] for two bars? 
# Let's define for one bar: [0,1,2,5,6] and then for the second bar: [8,9,10,13,14]
bass_pattern_per_bar = [0, 1, 2, 5, 6]
bass_pattern = []
for bar in range(num_bars):
    offset = bar * eighths_per_bar
    for idx in bass_pattern_per_bar:
        bass_pattern.append(offset + idx)
# We'll assign pitches: repeat a pattern of 5 notes for the two bars (we have 10 notes)
bass_pitches = [36, 40, 43, 46, 36, 36, 40, 43, 46, 36]  # C2, E2, G2, Bb2, C2 repeated
for i, idx in enumerate(bass_pattern):
    n = note.Note(bass_pitches[i])
    n.quarterLength = 0.5  # eighth note
    n.velocity = 100
    bass_part.insert(idx * 0.5, n)

# --- Piano ---
# Piano: chord stabs on the upbeats (odd eighth notes: 1,3,5,7,9,11,13,15)
# We'll define chords for each upbeat.
# We have 8 upbeats in two bars.
# We'll use two chords per bar: 
#   Bar 1: Cm and F
#   Bar 2: Bb and Eb
# So for upbeats in bar 1 (indices 1,3,5,7): 
#   1 -> Cm, 3 -> F, 5 -> Cm, 7 -> F
#   Bar 2 (indices 9,11,13,15):
#   9 -> Bb, 11 -> Eb, 13 -> Bb, 15 -> Eb
piano_chords = {
    'Cm': [36, 40, 43],  # C minor triad
    'F':  [41, 45, 48],  # F major triad
    'Bb': [46, 50, 53],  # Bb major triad
    'Eb': [51, 55, 58]   # Eb major triad
}
# Map upbeat index to chord
upbeat_to_chord = {
    1: 'Cm', 3: 'F', 5: 'Cm', 7: 'F',
    9: 'Bb', 11: 'Eb', 13: 'Bb', 15: 'Eb'
}
for eighth_idx, chord_name in upbeat_to_chord.items():
    # Convert eighth note index to quarter length offset: eighth_idx * 0.5
    offset_ql = eighth_idx * 0.5
    for pitch in piano_chords[chord_name]:
        n = note.Note(pitch)
        n.quarterLength = 0.5  # eighth note
        n.velocity = 70
        piano_part.insert(offset_ql, n)

# --- Horns ---
# Horn hits: we'll do on specific eighth notes: 
#   Downbeat of bar1: index0
#   Upbeat of beat2 in bar1: index3? 
#   Downbeat of bar2: index8
#   Upbeat of beat2 in bar2: index11
# Let's do: [0, 3, 8, 11] for a simple pattern.
horn_pattern = [0, 3, 8, 11]
horn_pitches = [60, 46, 65, 39]  # C4, Bb3, F4, Eb3
for i, eighth_idx in enumerate(horn_pattern):
    n = note.Note(horn_pitches[i])
    n.quarterLength = 0.5  # eighth note
    n.velocity = 85
    horns_part.insert(eighth_idx * 0.5, n)

# --- Guitar ---
# Guitar: play on the upbeats (same as piano) but with a muted, percussive feel.
# We'll play a single note (maybe the root of the chord) with short duration and low velocity.
# We'll use the same mapping as piano for the chord root.
# Let's define a root for each chord:
chord_roots = {
    'Cm': 36,
    'F':  41,
    'Bb': 46,
    'Eb': 51
}
# For each upbeat, we play the root of the chord.
for eighth_idx, chord_name in upbeat_to_chord.items():
    root = chord_roots[chord_name]
    offset_ql = eighth_idx * 0.5
    n = note.Note(root)
    n.quarterLength = 0.5  # eighth note
    n.velocity = 50  # very soft, muted
    guitar_part.insert(offset_ql, n)

# Add all parts to the stream
midi_stream.insert(0, drums_part)
midi_stream.insert(0, bass_part)
midi_stream.insert(0, piano_part)
midi_stream.insert(0, horns_part)
midi_stream.insert(0, guitar_part)

# Write MIDI file
midi_path = "MIDI/afrobeat_groove.mid"
midi_stream.write('midi', fp=midi_path)
print(f"MIDI written to {midi_path}")

# Try to render audio if fluidsynth is available
try:
    subprocess.run(['which', 'fluidsynth'], check=True, capture_output=True)
    soundfont = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    wav_path = "Audio/afrobeat_groove.wav"
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
        ogg_path = "Audio/afrobeat_groove.ogg"
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
