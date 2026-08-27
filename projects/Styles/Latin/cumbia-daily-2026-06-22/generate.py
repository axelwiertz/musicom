#!/usr/bin/env python3
"""
Cumbia Daily Pattern Composition - 2026-06-22
Focus: Metrical gravity (2/4 cumbia pulse) and characteristic syncopation.
Framework: UnitMatrix rows = instruments, cols = form sections.
Sub-genre: Latin / Cumbia (Colombian)
Features: llamador pulse (strict off-beats), alegre syncopation, maraca steady 16th, accordion melody
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
    # === CUMBIA (Colombian) ===
    # Key: D Dorian (D E F G A B C D)
    # Time: 2/4 | Tempo: 100 BPM (moderate cumbia)
    # Characteristic: steady llamador pulse (strict off-beats), alegre syncopation,
    #   maraca 16th shuffle, accordion melody
    #
    # Cumbia rhythm structure (2/4):
    #   Beat 1: downbeat (bombo + bass)
    #   Beat &: llamador strike (off-beat ONLY — the "caller" calls on the upbeats)
    #   Beat 1.5 (& of 1): alegre syncopated hit
    #   Beat 2: bombo off-beat
    #   Beat 2.5 (& of 2): alegre hit
    #
    # Metrical gravity (16 sixteenth-notes per 2/4 bar, 2 bars = 32):
    # Strong accents: beat 1 (0), beat 1.5 (4), beat 2 (8), beat 2.5 (12)
    # Llamador pulse on OFF-beats ONLY (& of 1, & of 2 — strictly the upbeats)
    # Bombo on downbeats + off-beats
    # Maraca: continuous 16th-note with heavy-light-light shuffle accent

    rows = ["Bombo", "Llamador", "Alegre", "Maraca", "Accordion"]
    cols = ["A"]  # Single 2-bar section

    # === ROW 1: BOMBO (Bass Drum, ch=0, program=35 - Acoustic Bass) ===
    # Deep bass drum marking downbeats and off-beats
    # Cumbia bombo pattern: 1 + 2 + (eighth note pulse with emphasis on 1 and & of 2)
    bombo_events = []
    # Bombo hits: beats 0, 1, 2, 3 in 2 bars of 2/4
    # Traditional: beat 1 strong, beat 1.5 light, beat 2 medium, beat 2.5 light
    bombo_hits = [
        (0.0, 100),   # Bar 1 downbeat - strong
        (1.0, 72),    # Bar 1 off-beat - medium
        (2.0, 95),    # Bar 2 downbeat - strong
        (3.0, 70),    # Bar 2 off-beat - medium
    ]
    pitch = 36  # Kick drum surrogate on piano channel
    for beat, vel in bombo_hits:
        add_note(bombo_events, 0, pitch, int(beat * TPB), int(0.4 * TPB), vel)

    # Also add a bass line (acoustic bass, program 34) on same track - simpler approach
    # Actually let me separate: channel 0 = bass line (acoustic bass), channel 9 = percussion
    # Let me redo - use ch=0 for bombo bass line, ch=1 for llamador, etc.

    # I need to restructure. Let me use proper channels:
    # ch=0: Bass (Bombo surrogate + bass line) - Acoustic Bass (program=34)
    # ch=1: Llamador (perc on drum ch)
    # ch=2: Alegre (perc on drum ch)
    # ch=3: Accordion (Accordion program=22)
    # ch=9: Percussion (Maraca, Llamador, Alegre)

    # Let me clear the bombo_events and start fresh with proper channel assignment

    bombo_events.clear()
    # Bass line using acoustic bass (program 34)
    # D Dorian root movement: D (38), A (45), D (38), C (36), D (38)
    bass_notes = [
        (0.0, 38, 100, 0.9),   # D2 - downbeat
        (0.5, 38, 65, 0.4),    # D2 - offbeat light
        (1.0, 38, 85, 0.6),    # D2 - beat 2
        (1.5, 38, 60, 0.3),    # D2 - offbeat light
        (2.0, 40, 100, 0.9),   # E2 - bar 2 downbeat
        (2.5, 40, 65, 0.4),    # E2 - offbeat light
        (3.0, 38, 85, 0.6),    # D2 - beat 2
        (3.5, 38, 60, 0.3),    # D2 - offbeat light
    ]
    for beat, pitch, vel, dur in bass_notes:
        add_note(bombo_events, 0, pitch, int(beat * TPB), int(dur * TPB), vel)

    # === ROW 2: LLAMADOR (ch=9, GM Percussion) ===
    # Llamador = low-pitched drum, strict off-beat pattern only
    # In authentic Colombian cumbia, the llamador (the "caller") plays ONLY on the
    # off-beats / upbeats (the "&"). Silent on downbeats — leaves space for bombo.
    # Using Low Tom (45) as surrogate
    llamador_events = []
    # OFF-beats ONLY: 0.5, 1.5, 2.5, 3.5 — no downbeats!
    llamador_hits = [0.5, 1.5, 2.5, 3.5]
    for b in llamador_hits:
        add_note(llamador_events, DRUM_CH, 45, int(b * TPB), int(0.08 * TPB), 82)

    # === ROW 3: ALEGRE (ch=9, GM Percussion) ===
    # Alegre = higher-pitched drum, syncopated off-beat accents
    # Using Conga (High, 63) as surrogate
    alegre_events = []
    # Alegre hits: off-beats with characteristic cumbia accentuation
    alegre_hits = [
        (0.25, 85),   # upbeat before 1
        (0.75, 90),   # upbeat before 2 - stronger
        (1.25, 80),   # upbeat before 1 (bar2)
        (1.75, 90),   # upbeat before 2 - stronger
        (2.25, 85),
        (2.75, 90),
        (3.25, 80),
        (3.75, 92),   # final accent leading to next section
    ]
    for beat, vel in alegre_hits:
        add_note(alegre_events, DRUM_CH, 63, int(beat * TPB), int(0.06 * TPB), vel)

    # === ROW 4: MARACA (ch=9) ===
    # Continuous 16th-note shuffle / shaker pattern
    maraca_events = []
    # Cumbia maraca: steady 16th notes with slight accent pattern
    for half_beat in range(16):  # 16 sixteenths in 2 bars of 2/4
        beat = half_beat * 0.25
        if half_beat % 4 == 0:  # on the eighth note
            vel = 55
        elif half_beat % 4 == 2:  # off-eighth
            vel = 62  # slightly stronger accent (cumbia maraca swing)
        else:
            vel = 40
        add_note(maraca_events, DRUM_CH, 70, int(beat * TPB), int(0.04 * TPB), vel)

    # === ROW 5: ACCORDION (ch=4, program=22) ===
    # D Dorian melody with characteristic cumbia phrasing
    # Scale: D4=62, E4=64, F4=65, G4=67, A4=69, B4=71, C5=72, D5=74
    accordion_events = []
    # Melodic pattern - D Dorian motif with cumbia phrasing
    melody = [
        (0.0, 62, 95, 0.5),     # D4 - downbeat
        (0.5, 64, 75, 0.25),    # E4 - pickup
        (0.75, 65, 80, 0.25),   # F4
        (1.0, 67, 85, 0.5),     # G4 - beat 2
        (1.5, 69, 72, 0.25),    # A4
        (1.75, 67, 78, 0.25),   # G4 - turn
        (2.0, 65, 90, 0.5),     # F4 - bar 2 downbeat
        (2.5, 64, 75, 0.25),    # E4
        (2.75, 62, 70, 0.25),   # D4
        (3.0, 69, 88, 0.75),    # A4 - held (beat 2)
        (3.75, 62, 90, 0.25),   # D4 - resolution
    ]
    for beat, pitch, vel, dur in melody:
        add_note(accordion_events, 4, pitch, int(beat * TPB), int(dur * TPB), vel)

    # Build MIDI
    mid = MidiFile(ticks_per_beat=TPB)

    # Meta track
    meta = MidiTrack()
    meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(100), time=0))
    meta.append(MetaMessage('time_signature', numerator=2, denominator=2, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    mid.tracks.append(meta)

    # Track 0: Bass/Bombo (Acoustic Bass, program 34)
    bass_track = MidiTrack()
    bass_track.append(Message('program_change', channel=0, program=34, time=0))
    mid.tracks.append(build_track(bombo_events))

    # Track 1: Llamador (perc on ch9)
    mid.tracks.append(build_track(llamador_events))

    # Track 2: Alegre (perc on ch9)
    mid.tracks.append(build_track(alegre_events))

    # Track 3: Maraca (perc on ch9)
    mid.tracks.append(build_track(maraca_events))

    # Track 4: Accordion (program 22)
    acc_track = MidiTrack()
    acc_track.append(Message('program_change', channel=4, program=22, time=0))
    # Merge accordion events into this track
    prev = 0
    sorted_acc = sorted(accordion_events, key=lambda x: (x[0], 0 if x[1].type == 'note_off' else 1))
    for tick, msg in sorted_acc:
        msg.time = int(tick - prev)
        msg.channel = 4
        acc_track.append(msg)
        prev = tick
    acc_track.append(MetaMessage('end_of_track', time=0))
    mid.tracks.append(acc_track)

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