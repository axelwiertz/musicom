#!/usr/bin/env python3
"""Country loop 16-bar seamless. Regenerates MIDI + WAV."""
import os, sys, numpy as np
sys.path.insert(0, '/opt/data/repos/musicom')

# --- Fallback helpers (musicom deps broken) ---
class RhythmGenerator:
    def __init__(self, onsets=8, timesteps=16):
        self.onsets = onsets
        self.timesteps = timesteps
    def generate(self):
        grid = np.zeros(self.timesteps)
        for i in range(self.timesteps):
            grid[i] = 0.5 if i % 2 == 1 else 1.0
        return [type('obj', (object,), {'onset_intervals': grid.tolist()})()]

class MusicPitchClassSet:
    def __init__(self, name, definition, rotation, initial):
        self.name = name
        self.initial = initial
    def get_chord(self, degree, octave=5):
        notes = [7, 9, 11, 12, 14, 16, 18]  # G Ionian
        idx = (degree - 1) % 7
        base = notes[idx]
        return [base + 12 * o for o in range(3)]

# --- Music21 render ---
from music21 import stream, note, tempo, meter, midi, instrument, chord as m21chord

# Concept: G Major, 120 BPM, 16 bars, Country
s = stream.Score()
s.insert(0, tempo.MetronomeMark(number=120))
s.insert(0, meter.TimeSignature('4/4'))

# ----- Voice 1: Fiddle lead (melody) -----
fiddle = stream.Part()
fiddle.insert(0, instrument.Violin())

# Chord progression: G C G D | C G D G
chords = ['G', 'C', 'G', 'D', 'C', 'G', 'D', 'G']
# Melody pattern: arpeggiated triads with neighbor tones
melody_pitches = [
    # bar 1: G
    ('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('B4', 0.5),
    # bar 2: C
    ('C5', 0.5), ('E5', 0.5), ('G5', 0.5), ('E5', 0.5),
    # bar 3: G
    ('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('B4', 0.5),
    # bar 4: D
    ('A4', 0.5), ('D5', 0.5), ('F#5', 0.5), ('D5', 0.5),
    # bar 5: C
    ('C5', 0.5), ('E5', 0.5), ('G5', 0.5), ('E5', 0.5),
    # bar 6: G
    ('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('B4', 0.5),
    # bar 7: D
    ('A4', 0.5), ('D5', 0.5), ('F#5', 0.5), ('D5', 0.5),
    # bar 8: G (returns to start)
    ('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('B4', 0.5),
    # bar 9-16: repeat with variation
    ('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('B4', 0.5),
    ('C5', 0.5), ('E5', 0.5), ('G5', 0.5), ('E5', 0.5),
    ('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('B4', 0.5),
    ('A4', 0.5), ('D5', 0.5), ('F#5', 0.5), ('D5', 0.5),
    ('C5', 0.5), ('E5', 0.5), ('G5', 0.5), ('E5', 0.5),
    ('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('B4', 0.5),
    ('A4', 0.5), ('D5', 0.5), ('F#5', 0.5), ('D5', 0.5),
    ('G4', 1.0),  # hold last G for resolution
]

offset = 0.0
for pname, dur in melody_pitches:
    n = note.Note(pname)
    n.duration.quarterLength = dur
    n.volume.velocity = 100
    fiddle.insert(offset, n)
    offset += dur

# ----- Voice 2: Harmony (guitar chords) -----
guitar = stream.Part()
guitar.insert(0, instrument.AcousticGuitar())

chord_notes = {
    'G': ['G2', 'B2', 'D3', 'G3', 'B3'],
    'C': ['C3', 'E3', 'G3', 'C4', 'E4'],
    'D': ['D3', 'F#3', 'A3', 'D4', 'F#4'],
}

offset = 0.0
for chord_name in chords * 2:  # 8 chords × 2 = 16 bars
    c = m21chord.Chord(chord_notes[chord_name])
    c.duration.quarterLength = 2.0  # half note
    c.volume.velocity = 80
    guitar.insert(offset, c)
    offset += 2.0

# ----- Voice 3: Bass (walking) -----
bass = stream.Part()
bass.insert(0, instrument.AcousticBass())

bass_notes = [
    # Walking bass over I-IV-V-I
    ('G2', 0.5), ('B2', 0.5), ('D2', 0.5), ('G2', 0.5),
    ('C2', 0.5), ('E2', 0.5), ('G2', 0.5), ('C2', 0.5),
    ('G2', 0.5), ('B2', 0.5), ('D2', 0.5), ('G2', 0.5),
    ('D2', 0.5), ('F#2', 0.5), ('A2', 0.5), ('D2', 0.5),
    ('C2', 0.5), ('E2', 0.5), ('G2', 0.5), ('C2', 0.5),
    ('G2', 0.5), ('B2', 0.5), ('D2', 0.5), ('G2', 0.5),
    ('D2', 0.5), ('F#2', 0.5), ('A2', 0.5), ('D2', 0.5),
    ('G2', 0.5), ('B2', 0.5), ('D2', 0.5), ('G2', 1.0),  # last note longer
]
offset = 0.0
for pname, dur in bass_notes * 2:  # 8 bars × 2 = 16 bars
    n = note.Note(pname)
    n.duration.quarterLength = dur
    n.volume.velocity = 110
    bass.insert(offset, n)
    offset += dur

# ----- Voice 4: Drums (percussion) -----
drums = stream.Part()
drums.insert(0, instrument.Percussion())

# Kick 36, Snare 38, Hi-hat 42
drum_pattern = [
    # beat 1: kick, beat 2: snare, beat 3: kick, beat 4: snare
    (36, 0.0), (42, 0.0), (38, 2.0), (42, 2.0),
    (36, 4.0), (42, 4.0), (38, 6.0), (42, 6.0),
]

for bar in range(16):
    bar_offset = bar * 8.0  # 4 beats = 8 quarter notes
    for drum_note, beat_offset in drum_pattern:
        n = note.Note()
        n.pitch.midi = drum_note
        n.duration.quarterLength = 0.5
        n.volume.velocity = 100 if drum_note == 36 else 90
        drums.insert(bar_offset + beat_offset, n)

# Assemble score
s.insert(0, fiddle)
s.insert(0, guitar)
s.insert(0, bass)
s.insert(0, drums)

# Export
project_dir = "/opt/data/projects/Styles/Country/001-country-loop-seamless"
os.makedirs(f"{project_dir}/MIDI", exist_ok=True)
os.makedirs(f"{project_dir}/Audio", exist_ok=True)
os.makedirs(f"{project_dir}/Scores", exist_ok=True)

midi_path = f"{project_dir}/MIDI/loop.mid"
wav_path = f"{project_dir}/Audio/loop.wav"

s.write('midi', fp=midi_path)

# Render audio: sine wave from MIDI notes
from scipy.io import wavfile
sr = 44100
duration = 32.0  # 16 bars at 120 BPM = 32s
t = np.linspace(0, duration, int(sr * duration), endpoint=False)
audio = np.zeros_like(t)

for n in s.flatten().notesAndRests:
    if hasattr(n, 'pitch'):
        freq = n.pitch.frequency
        start = n.offset
        dur = n.duration.quarterLength * 0.5  # 120 BPM
        start_sample = int(start * sr * 0.5)
        end_sample = int((start + dur) * sr * 0.5)
        if end_sample > len(audio):
            end_sample = len(audio)
        if start_sample < end_sample and start_sample < len(audio):
            env = np.linspace(1, 0, end_sample - start_sample)
            audio[start_sample:end_sample] += 0.3 * np.sin(2 * np.pi * freq * t[start_sample:end_sample]) * env

mx = np.max(np.abs(audio))
if mx > 0:
    audio = audio / mx * 0.9
wavfile.write(wav_path, sr, audio.astype(np.float32))

# Dashboard
with open(f"{project_dir}/index.html", 'w') as f:
    f.write("""<!doctype html>
<html><head><title>001 Country Loop</title></head><body>
<h1>Country Loop 001</h1>
<p>G Major, 120 BPM, 16 bars, seamless</p>
<p>Voices: Fiddle, Guitar, Bass, Drums</p>
</body></html>""")

# MusicXML
s.write('musicxml', fp=f"{project_dir}/Scores/loop.xml")

print("✅ Generated: 001-country-loop-seamless")
print(f"   MIDI: {midi_path}")
print(f"   Audio: {wav_path}")
print(f"   Scores: {project_dir}/Scores/loop.xml")
print(f"   Dashboard: {project_dir}/index.html")