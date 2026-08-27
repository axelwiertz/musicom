#!/usr/bin/env python3
"""
Classic Tango Daily Pattern Composition - 2026-06-21
Focus: Metrical gravity (marcato accents) and 3-3-2 syncopation.
Framework: UnitMatrix rows = instruments, cols = form sections.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo
import subprocess

TPB = 480
BAR = TPB * 4
DRUM_CH = 9

@dataclass
class UnitCell:
    pitch_pattern: List[int] = field(default_factory=list)
    rhythm_pattern: List[float] = field(default_factory=list)
    percussion: Dict[int, List[float]] = field(default_factory=dict)

@dataclass
class UnitMatrix:
    rows: List[str]
    cols: List[str]
    cells: Dict[str, Dict[str, UnitCell]]


def add_note(events, channel, note, start_tick, dur_tick, vel):
    events.append((start_tick, Message('note_on', channel=channel, note=note, velocity=vel, time=0)))
    events.append((start_tick + dur_tick, Message('note_off', channel=channel, note=note, velocity=0, time=0)))


def build_track(events):
    track = MidiTrack()
    prev = 0
    for tick, msg in sorted(events, key=lambda x: (x[0], 0 if x[1].type == 'note_off' else 1)):
        msg.time = int(tick - prev)
        track.append(msg)
        prev = tick
    track.append(MetaMessage('end_of_track', time=0))
    return track


def run():
    # === TANGO CLASSIC ===
    # Key: A Harmonic Minor (relative C major)
    # Time: 4/4 | Tempo: 128 BPM
    # Characteristic: marcato accents, 3-3-2 syncopation, dramatic leaps
    
    rows = ["Bass", "Piano", "Bandoneon", "Percussion"]
    cols = ["A"]  # Single 2-bar section for daily pattern

    # === METRICAL GRAVITY (8 eighth-notes in 2 bars) ===
    # Strong beats: 1, 4, 6, 8 (tango marcato feel)
    # 3-3-2 syncopation: accent groups of 3+3+2 eighth notes
    # Gravity profile: [1.0, 0.3, 0.5, 0.9, 0.4, 0.9, 0.3, 0.8]
    
    # === ROW 1: BASS (Double Bass, ch=0, program=43) ===
    # Marcato root-fifth pattern on strong beats
    bass_events = []
    bass_notes = [40, 45, 40, 47, 40, 45, 40, 47]  # E, A, E, B / E, A, E, B
    bass_beats = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]  # Quarter-note pulse
    bass_velocities = [100, 70, 80, 95, 85, 92, 75, 88]
    for i, b in enumerate(bass_beats):
        add_note(bass_events, 0, bass_notes[i], int(b * TPB), int(0.9 * TPB), bass_velocities[i])
    
    # === ROW 2: PIANO (ch=1, program=1) ===
    # Chordal punctuation on 3-3-2 pattern: beats 0, 3, 6 (eighth-note positions)
    # Am7 chord tones: A C E G
    piano_events = []
    # 3-3-2 accent pattern across 2 bars (16 eighth-notes)
    # Accented positions (6th-note grid): 0, 3, 6, 8, 11, 14
    # Group 1: [0,1,2] accent at 0
    # Group 2: [3,4,5] accent at 3
    # Group 3: [6,7] accent at 6
    # Repeat for bar 2: positions 8, 11, 14
    piano_chord = [45, 48, 52, 57]  # Am voicing (A, C, E, A)
    piano_hits = [0.0, 1.5, 3.0, 4.0, 5.5, 7.0]  # 3-3-2 syncopation in beats
    for b in piano_hits:
        for p in piano_chord:
            vel = 85 if b in [0.0, 3.0, 4.0, 7.0] else 65
            add_note(piano_events, 1, p, int(b * TPB), int(0.125 * TPB), vel)
    
    # === ROW 3: BANDONEON (ch=2, program=23) ===
    # Dramatic melodic line with chromatic passing tones (A harmonic minor)
    # Scale: A B C D E F G# A
    # Melody: arpeggiated with chromatic approach notes
    bandoneon_events = []
    # Melody pitches in A harmonic minor (midi: A4=69, etc)
    melody = [
        (0.0, 69, 100),     # A4 - downbeat
        (0.75, 72, 80),     # C5 - weak
        (1.5, 68, 85),      # G#4 - chromatic leading tone
        (2.0, 64, 75),      # E4
        (2.75, 67, 90),     # G4
        (3.5, 68, 95),      # G#4 -> A
        (4.0, 69, 100),     # A4 - bar 2 downbeat
        (4.75, 72, 80),     # C5 - dramatic leap (fixed)
        (5.5, 72, 85),      # C5
        (6.0, 65, 75),      # F4
        (6.75, 68, 90),     # G#4
        (7.5, 69, 95),      # A4 - resolution
    ]
    for beat, pitch, vel in melody:
        dur = 0.5 if beat % 1.0 == 0 else 0.25
        add_note(bandoneon_events, 2, pitch, int(beat * TPB), int(dur * TPB), vel)
    
    # === ROW 4: PERCUSSION (ch=9) ===
    # Marcato accent pattern: side stick on 3-3-2 rhythm
    perc_events = []
    
    # Side stick (37) - marcato pattern on 3-3-2 accents
    side_stick_hits = [0.0, 1.5, 3.0, 4.0, 5.5, 7.0]
    for b in side_stick_hits:
        add_note(perc_events, DRUM_CH, 37, int(b * TPB), int(0.08 * TPB), 95)
    
    # Kick (36) - downbeats (1, 3, 5, 7)
    kick_hits = [0.0, 2.0, 4.0, 6.0]
    for b in kick_hits:
        add_note(perc_events, DRUM_CH, 36, int(b * TPB), int(0.25 * TPB), 90)
    
    # Closed hi-hat (42) - steady eighth-note pulse
    hat_hits = [x * 0.5 for x in range(16)]
    for b in hat_hits:
        vel = 80 if b % 1.0 == 0 else 55
        add_note(perc_events, DRUM_CH, 42, int(b * TPB), int(0.05 * TPB), vel)
    
    # Build MIDI
    mid = MidiFile(ticks_per_beat=TPB)
    
    # Meta track
    meta = MidiTrack()
    meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(128), time=0))
    meta.append(MetaMessage('time_signature', numerator=4, denominator=2, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    mid.tracks.append(meta)
    
    # Bass track
    mid.tracks.append(build_track(bass_events))
    # Piano track
    mid.tracks.append(build_track(piano_events))
    # Bandoneon track
    mid.tracks.append(build_track(bandoneon_events))
    # Percussion track
    mid.tracks.append(build_track(perc_events))
    
    midi_path = Path("composition.mid")
    mid.save(midi_path)
    print(f"Saved: {midi_path}")
    
    # Render audio
    wav_path = Path("composition.wav")
    sf = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    result = subprocess.run(
        ['fluidsynth', '-ni', sf, str(midi_path), '-F', str(wav_path), '-r', '44100'],
        capture_output=True, text=True
    )
    print(result.stdout[-200:] if result.stdout else "fluidsynth done")
    print(result.stderr[-200:] if result.stderr else "")
    
    if wav_path.exists():
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(wav_path), '-codec:a', 'libvorbis', '-q:a', '5', 'composition.ogg'],
            capture_output=True
        )
        print(f"Rendered: composition.ogg")
        wav_path.unlink()  # Clean up WAV
    else:
        print("WARNING: No WAV file generated")


if __name__ == "__main__":
    run()
