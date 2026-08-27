#!/usr/bin/env python3
"""
Bluegrass Scruggs-Style Daily Pattern Composition - 2026-06-23
Focus: Metrical gravity (cut-time drive) and Scruggs forward roll patterns.
Framework: UnitMatrix rows = instruments, cols = form sections.
Sub-genre: Bluegrass / Scruggs-Style Bluegrass Breakdown
Features: Forward banjo roll, fiddle melody, mandolin chop (backbeat),
          guitar bass runs, upright bass two-beat.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
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
    # === BLUEGRASS SCRUGGS STYLE ===
    # Key: G Major (Mixolydian flavor with flat-7)
    # Time: 2/2 (cut time) | Tempo: 140 BPM
    # Characteristic: forward banjo roll (continuous 8th notes),
    #   mandolin chop on backbeats (2 & 4), bass two-beat (1 & 3),
    #   fiddle melody with open-string drone, guitar walking bass runs.
    #
    # Metrical gravity (2 bars, 8 eighth-notes per bar in cut time):
    # Strong beats: 1, 3 (the two half-note pulses per bar)
    # Backbeats: 2, 4 (mandolin chop accents)
    # Gravity: [1.0, 0.2, 0.8, 0.2, 0.7, 0.3, 0.6, 0.2]
    #
    # Form: 2-bar breakdown section (A)

    rows = ["Banjo", "Fiddle", "Mandolin", "Guitar", "Bass"]
    cols = ["A"]  # Single 2-bar section

    # === ROW 1: BANJO (Scruggs Forward Roll, ch=0, program=105) ===
    # GM program 105 = Banjo
    # Forward roll pattern: 5-3-1-5-3-1-5-3 (string pattern)
    # Continuous 8th notes with thumb accent (pitch), index (medium),
    # middle (light), thumb (accent) cycle
    banjo_events = []
    # G major pentatonic: G4=67, A4=69, B4=71, D5=74, E5=76
    # Forward roll across 2 bars = 16 eighth-notes
    # Pattern thumb(g) - index(b) - middle(d) - thumb(g) - index(b) - middle(d) - thumb(g) - index(c)
    # Bar 1: G D B G D B G C (over G chord)
    # Bar 2: G D B G D B G D (over D chord resolving to G)
    banjo_pattern = [
        # Bar 1 - G chord (I)
        (0.0, 67, 100),    # G4 - thumb accent
        (0.5, 74, 72),     # D5 - index medium
        (1.0, 71, 60),     # B4 - middle light
        (1.5, 67, 92),     # G4 - thumb accent
        (2.0, 74, 70),     # D5 - index medium
        (2.5, 71, 58),     # B4 - middle light
        (3.0, 67, 88),     # G4 - thumb accent
        (3.5, 72, 65),     # C5 - index (passing to IV)
        # Bar 2 - D7 chord (V) resolving to G (I)
        (4.0, 69, 95),     # A4 - thumb accent (V chord tone)
        (4.5, 76, 70),     # E5 - index medium
        (5.0, 74, 60),     # D5 - middle light
        (5.5, 69, 90),     # A4 - thumb accent
        (6.0, 76, 68),     # E5 - index medium
        (6.5, 74, 55),     # D5 - middle light
        (7.0, 67, 95),     # G4 - thumb accent (resolution)
        (7.5, 71, 75),     # B4 - index (leading tone)
    ]
    for beat, pitch, vel in banjo_pattern:
        add_note(banjo_events, 0, pitch, int(beat * TPB), int(0.35 * TPB), vel)

    # === ROW 2: FIDDLE (ch=1, program=40 - Violin) ===
    # Melody with characteristic bluegrass phrasing, open-string drone
    fiddle_events = []
    # G major pentatonic melody with Mixolydian flat-7 (F natural)
    # G4=67, A4=69, B4=71, C5=72, D5=74, E5=76, F5=77, G5=79
    fiddle_melody = [
        # Bar 1
        (0.0, 67, 100, 0.75),   # G4 - downbeat, full bow
        (0.75, 69, 70, 0.25),   # A4 - pick-up
        (1.0, 71, 80, 0.5),     # B4 - slur
        (1.5, 72, 75, 0.25),    # C5 - passing
        (2.0, 74, 85, 0.5),     # D5 - accent
        (2.5, 71, 68, 0.25),    # B4 - return
        (3.0, 67, 90, 0.5),     # G4 - hold
        (3.5, 69, 65, 0.25),    # A4 - pick-up
        # Bar 2
        (4.0, 76, 95, 0.75),    # E5 - high accent
        (4.75, 77, 75, 0.25),   # F5 - flat-7 Mixolydian color
        (5.0, 76, 80, 0.25),    # E5 - turn
        (5.25, 74, 72, 0.25),   # D5
        (5.5, 72, 70, 0.25),    # C5
        (5.75, 71, 80, 0.25),   # B4
        (6.0, 69, 85, 0.5),     # A4
        (6.5, 67, 78, 0.25),    # G4
        (7.0, 71, 90, 0.5),     # B4 - leading to root
        (7.5, 67, 95, 0.5),     # G4 - resolution
    ]
    for beat, pitch, vel, dur in fiddle_melody:
        add_note(fiddle_events, 1, pitch, int(beat * TPB), int(dur * TPB), vel)

    # === ROW 3: MANDOLIN (ch=2, program=104 - Mandolin) ===
    # Chop on backbeats 2 and 4 (offbeats in cut time)
    # Muted chord strums on beats 1.5, 3.5 (eighth-note positions)
    mandolin_events = []
    # G major chord voicing: G3=55, B3=59, D4=62, G4=67
    g_chord = [55, 59, 62, 67]
    d_chord = [50, 54, 57, 62]  # D4, F#4, A4, D5 (actually D3, F#3, A3, D4)
    # Actually let me use simpler voicings
    # G: G3=55, B3=59, D4=62
    # D7: D3=50, F#3=54, A3=57, C4=60
    g_voicing = [55, 59, 62, 67]
    d7_voicing = [50, 54, 57, 60]

    # Mandolin chops on backbeats (positions 1.5, 3.5, 5.5, 7.5)
    chop_patterns = [
        (1.5, g_voicing, 85),   # beat 2 backbeat - G
        (3.5, g_voicing, 82),   # beat 4 backbeat - G
        (5.5, d7_voicing, 85),  # beat 2 backbeat bar2 - D7
        (7.5, d7_voicing, 88),  # beat 4 backbeat bar2 - D7 (leading to G)
    ]
    for beat, voicing, vel in chop_patterns:
        for p in voicing:
            add_note(mandolin_events, 2, p, int(beat * TPB), int(0.08 * TPB), vel)

    # === ROW 4: GUITAR (ch=3, program=25 - Acoustic Guitar (nylon) / use 26 for steel) ===
    # Walking bass runs between chord changes + rhythm
    guitar_events = []
    # Walking bass run in G
    # G3=55, A3=57, B3=59, C4=60, D4=62, E4=64, F#4=66, F4=65, G4=67
    guitar_runs = [
        # Bar 1 - G chord walk-up
        (0.0, 55, 92, 0.75),    # G3 - bass note
        (0.75, 57, 68, 0.25),   # A3 - walk-up
        (1.0, 59, 72, 0.5),     # B3 - walk-up
        (1.5, 60, 70, 0.25),    # C4 - passing tone
        (2.0, 62, 85, 0.5),     # D4 - accent
        (2.5, 59, 65, 0.25),    # B3 - return
        (3.0, 55, 80, 0.5),     # G3
        (3.5, 57, 62, 0.25),    # A3 - approaching V
        # Bar 2 - D7 to G walk-down
        (4.0, 62, 90, 0.5),     # D4 - V chord root
        (4.5, 61, 68, 0.25),    # C#4 - chromatic approach
        (5.0, 62, 75, 0.25),    # D4
        (5.25, 60, 65, 0.25),   # C4
        (5.5, 59, 70, 0.25),    # B3
        (5.75, 57, 62, 0.25),   # A3
        (6.0, 55, 88, 0.75),    # G3 - return to tonic
        (6.75, 57, 65, 0.25),   # A3 - walk-up
        (7.0, 59, 75, 0.5),     # B3
        (7.5, 55, 70, 0.5),     # G3 - leading tone
    ]
    for beat, pitch, vel, dur in guitar_runs:
        add_note(guitar_events, 3, pitch, int(beat * TPB), int(dur * TPB), vel)

    # === ROW 5: BASS (ch=4, program=34 - Acoustic Bass / 43 for Double Bass) ===
    # Upright Bass two-beat: root on 1, fifth on 3 (half-note feel in cut time)
    bass_events = []
    # G2=43, D2=38, C2=36, A2=45
    bass_pattern = [
        # Bar 1 - G (I)
        (0.0, 43, 100, 1.5),    # G2 - root, heavy accent, held
        (2.0, 50, 88, 0.5),     # D3 - fifth, staccato
        (3.0, 43, 85, 0.5),     # G2 - root
        # Bar 2 - D7 (V) to G (I)
        (4.0, 38, 95, 0.5),     # D2 - V chord root
        (5.0, 50, 80, 0.5),     # D3 - fifth
        (6.0, 43, 92, 1.0),     # G2 - root (resolution)
        (7.0, 38, 75, 0.5),     # D2 - leading
    ]
    for beat, pitch, vel, dur in bass_pattern:
        add_note(bass_events, 4, pitch, int(beat * TPB), int(dur * TPB), vel)

    # === BUILD MIDI ===
    mid = MidiFile(ticks_per_beat=TPB)

    # Meta track
    meta = MidiTrack()
    meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(140), time=0))
    meta.append(MetaMessage('time_signature', numerator=2, denominator=2,
                            clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    mid.tracks.append(meta)

    # Track 0: Banjo (program 105)
    banjo_track = MidiTrack()
    banjo_track.append(Message('program_change', channel=0, program=105, time=0))
    mid.tracks.append(build_track(banjo_events))

    # Track 1: Fiddle (program 40)
    fiddle_track = MidiTrack()
    fiddle_track.append(Message('program_change', channel=1, program=40, time=0))
    mid.tracks.append(build_track(fiddle_events))

    # Track 2: Mandolin (program 104)
    mandolin_track = MidiTrack()
    mandolin_track.append(Message('program_change', channel=2, program=104, time=0))
    mid.tracks.append(build_track(mandolin_events))

    # Track 3: Guitar (program 25)
    guitar_track = MidiTrack()
    guitar_track.append(Message('program_change', channel=3, program=25, time=0))
    mid.tracks.append(build_track(guitar_events))

    # Track 4: Bass (program 34)
    bass_track = MidiTrack()
    bass_track.append(Message('program_change', channel=4, program=34, time=0))
    mid.tracks.append(build_track(bass_events))

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