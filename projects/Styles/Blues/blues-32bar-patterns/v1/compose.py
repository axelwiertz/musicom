#!/usr/bin/env python3
"""32-bar Blues composition with 5 core patterns:
1. 5th-6th-b7 Shuffle (Lead/Chords)
2. Walking Bass Line
3. Boogie-Woogie Bassline
4. Slow Blues Triplet Block Chords
5. Blue-Note Sliding / Grace Notes

Key: C Blues | 120 BPM | Shuffle feel | 4/4
"""

import os, sys
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# === CONSTANTS ===
TPB = 480
BPM = 120
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR  # 1920 ticks
SECTION_BARS = 4
SECTION = BAR * SECTION_BARS  # 7680 ticks
TOTAL_BARS = 32
TOTAL_SECTIONS = 8  # 8 x 4 bars = 32

# Swing: long=160, short=80 (2:1 ratio on eighth notes of 240 ticks)
EIGHTH = 240
LONG_EIGHTH = 160
SHORT_EIGHTH = 80
QUARTER = 480
HALF = 960
WHOLE = 1920

# C Blues scale: C Eb F F# G Bb
# MIDI: C4=60, Eb4=63, F4=65, F#4=66, G4=67, Bb4=70
# C7 chord: C E G Bb = 60 64 67 70
# F7 chord: F A C Eb = 65 69 72 75
# G7 chord: G B D F = 67 71 74 77

# Chord roots (MIDI, octave 2 for bass, octave 3 for chords)
CHORDS = {
    'C7': {'root': 48, 'third': 52, 'fifth': 55, 'flat7': 58,  # bass octave
           'root3': 60, 'third3': 64, 'fifth3': 67, 'flat7_3': 70,  # chord octave
           'bass_root': 36, 'bass_oct': 48},  # low bass
    'F7': {'root': 53, 'third': 57, 'fifth': 60, 'flat7': 63,
           'root3': 65, 'third3': 69, 'fifth3': 72, 'flat7_3': 75,
           'bass_root': 41, 'bass_oct': 53},
    'G7': {'root': 55, 'third': 59, 'fifth': 62, 'flat7': 65,
           'root3': 67, 'third3': 71, 'fifth3': 74, 'flat7_3': 77,
           'bass_root': 43, 'bass_oct': 55},
}

# 12-bar blues progression per section (4 bars each)
PROGRESSION = [
    # Section A1 (bars 1-4): C7 F7 C7 C7
    ['C7', 'F7', 'C7', 'C7'],
    # Section A2 (bars 5-8): F7 F7 C7 G7
    ['F7', 'F7', 'C7', 'G7'],
    # Section B1 (bars 9-12): F7 C7 G7 C7
    ['F7', 'C7', 'G7', 'C7'],
    # Section A3 (bars 13-16): C7 F7 C7 C7
    ['C7', 'F7', 'C7', 'C7'],
    # Section A4 (bars 17-20): F7 F7 C7 G7
    ['F7', 'F7', 'C7', 'G7'],
    # Section B2 (bars 21-24): F7 C7 G7 C7
    ['F7', 'C7', 'G7', 'C7'],
    # Section C1 (bars 25-28): C7 C7 F7 F7
    ['C7', 'C7', 'F7', 'F7'],
    # Section C2 (bars 29-32): G7 F7 C7 C7 (turnaround)
    ['G7', 'F7', 'C7', 'C7'],
]

SECTION_NAMES = ['A1', 'A2', 'B1', 'A3', 'A4', 'B2', 'C1', 'C2']


def make_pad_unit(chord_name, section_offset):
    """Create padding unit to fill section to exact length."""
    return MusicUnit(events=[
        MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10, end_tick=SECTION)
    ])


# === PATTERN BUILDERS ===

def pad_to_section(events):
    """Ensure unit ends at exactly SECTION boundary."""
    if not events or events[-1].end_tick < SECTION:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10, end_tick=SECTION))
    return events


def build_5th_6th_b7_shuffle(chord_name, section_offset):
    """Pattern 1: 5th-6th-b7 Shuffle (Lead voice)"""
    c = CHORDS[chord_name]
    events = []
    t = 0
    # Each bar: 4 beats = 8 eighth notes in shuffle
    for bar in range(4):
        bar_t = t
        # Beat 1: Root+5th (long)
        events.append(MusicEvent(pitch=c['root3'], volume=85, start_tick=bar_t, end_tick=bar_t + LONG_EIGHTH))
        events.append(MusicEvent(pitch=c['fifth3'], volume=80, start_tick=bar_t, end_tick=bar_t + LONG_EIGHTH))
        # Beat 1: 6th (short)
        sixth = c['root3'] + 9  # major 6th above root
        events.append(MusicEvent(pitch=c['root3'], volume=85, start_tick=bar_t + LONG_EIGHTH, end_tick=bar_t + LONG_EIGHTH + SHORT_EIGHTH))
        events.append(MusicEvent(pitch=sixth, volume=80, start_tick=bar_t + LONG_EIGHTH, end_tick=bar_t + LONG_EIGHTH + SHORT_EIGHTH))
        # Beat 2: Root+5th (long)
        events.append(MusicEvent(pitch=c['root3'], volume=80, start_tick=bar_t + QUARTER, end_tick=bar_t + QUARTER + LONG_EIGHTH))
        events.append(MusicEvent(pitch=c['fifth3'], volume=75, start_tick=bar_t + QUARTER, end_tick=bar_t + QUARTER + LONG_EIGHTH))
        # Beat 2: b7 (short)
        events.append(MusicEvent(pitch=c['root3'], volume=80, start_tick=bar_t + QUARTER + LONG_EIGHTH, end_tick=bar_t + QUARTER + LONG_EIGHTH + SHORT_EIGHTH))
        events.append(MusicEvent(pitch=c['flat7_3'], volume=78, start_tick=bar_t + QUARTER + LONG_EIGHTH, end_tick=bar_t + QUARTER + LONG_EIGHTH + SHORT_EIGHTH))
        # Beat 3: Root+5th (long)
        events.append(MusicEvent(pitch=c['root3'], volume=85, start_tick=bar_t + HALF, end_tick=bar_t + HALF + LONG_EIGHTH))
        events.append(MusicEvent(pitch=c['fifth3'], volume=80, start_tick=bar_t + HALF, end_tick=bar_t + HALF + LONG_EIGHTH))
        # Beat 3: 6th (short)
        events.append(MusicEvent(pitch=c['root3'], volume=85, start_tick=bar_t + HALF + LONG_EIGHTH, end_tick=bar_t + HALF + LONG_EIGHTH + SHORT_EIGHTH))
        events.append(MusicEvent(pitch=sixth, volume=80, start_tick=bar_t + HALF + LONG_EIGHTH, end_tick=bar_t + HALF + LONG_EIGHTH + SHORT_EIGHTH))
        # Beat 4: Root+b7 (long)
        events.append(MusicEvent(pitch=c['root3'], volume=82, start_tick=bar_t + HALF + QUARTER, end_tick=bar_t + HALF + QUARTER + LONG_EIGHTH))
        events.append(MusicEvent(pitch=c['flat7_3'], volume=80, start_tick=bar_t + HALF + QUARTER, end_tick=bar_t + HALF + QUARTER + LONG_EIGHTH))
        # Beat 4: 5th (short) - turnaround
        events.append(MusicEvent(pitch=c['root3'], volume=82, start_tick=bar_t + HALF + QUARTER + LONG_EIGHTH, end_tick=bar_t + HALF + QUARTER + LONG_EIGHTH + SHORT_EIGHTH))
        events.append(MusicEvent(pitch=c['fifth3'], volume=78, start_tick=bar_t + HALF + QUARTER + LONG_EIGHTH, end_tick=bar_t + HALF + QUARTER + LONG_EIGHTH + SHORT_EIGHTH))
        t += BAR
    pad_to_section(events)
    return MusicUnit(events=events)


def build_walking_bass(chord_name, section_offset):
    """Pattern 2: Walking Bass Line (1-3-5-6-b7 ascending/descending)
    Continuous eighth-note walk with passing tones.
    """
    c = CHORDS[chord_name]
    events = []
    t = 0
    for bar in range(4):
        bar_t = t
        # Walking pattern: 8 eighth notes per bar (swing feel)
        # Ascending: root-3-5-6-b7-6-5-3
        walk_up = [c['bass_root'], c['root'], c['third'], c['root'] + 9, c['flat7'],
                   c['root'] + 9, c['third'], c['root']]
        # Descending variation on bar 2,4
        walk_down = [c['flat7'], c['third'], c['root'], c['bass_root'],
                     c['root'] - 2, c['bass_root'], c['third'], c['root']]
        
        walk = walk_up if bar % 2 == 0 else walk_down
        
        for i, pitch in enumerate(walk):
            if i % 2 == 0:
                start = bar_t + i * LONG_EIGHTH + (i // 2) * (SHORT_EIGHTH - LONG_EIGHTH + EIGHTH)
                # Simpler: use straight swing positions
                pass
            # Swing positions for 8 eighth notes:
            # 0: 0, 1: LONG, 2: QUARTER, 3: QUARTER+LONG, 4: HALF, 5: HALF+LONG, 6: 3*QUARTER, 7: 3*QUARTER+LONG
            swing_pos = [0, LONG_EIGHTH, QUARTER, QUARTER + LONG_EIGHTH,
                        HALF, HALF + LONG_EIGHTH, HALF + QUARTER, HALF + QUARTER + LONG_EIGHTH]
            start = bar_t + swing_pos[i]
            dur = LONG_EIGHTH if i % 2 == 0 else SHORT_EIGHTH
            vol = 95 if i % 2 == 0 else 80
            events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=start, end_tick=start + dur))
        t += BAR
    pad_to_section(events)
    return MusicUnit(events=events)


def build_boogie_bass(chord_name, section_offset):
    """Pattern 3: Boogie-Woogie Bassline
    Alternating low bass + octave/5th bounce.
    """
    c = CHORDS[chord_name]
    events = []
    t = 0
    for bar in range(4):
        bar_t = t
        # Boogie pattern per bar (8 eighth notes, swing):
        # Low-root, octave, 5th, octave, low-root, 6th, 5th, b7
        boogie = [
            (c['bass_root'], 100),           # low root
            (c['bass_oct'], 85),              # octave up
            (c['bass_root'] + 7, 90),         # 5th
            (c['bass_oct'], 85),              # octave
            (c['bass_root'], 100),            # low root
            (c['bass_root'] + 9, 88),         # 6th
            (c['bass_root'] + 7, 90),         # 5th
            (c['flat7'] - 12, 85),            # b7 (low octave)
        ]
        swing_pos = [0, LONG_EIGHTH, QUARTER, QUARTER + LONG_EIGHTH,
                    HALF, HALF + LONG_EIGHTH, HALF + QUARTER, HALF + QUARTER + LONG_EIGHTH]
        for i, (pitch, vol) in enumerate(boogie):
            start = bar_t + swing_pos[i]
            dur = LONG_EIGHTH if i % 2 == 0 else SHORT_EIGHTH
            events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=start, end_tick=start + dur))
        t += BAR
    pad_to_section(events)
    return MusicUnit(events=events)


def build_block_chords(chord_name, section_offset):
    """Pattern 4: Block Chords (Triplet pulse / sustained dominant 7ths)
    Piano plays full dom7 chords with triplet subdivision feel.
    """
    c = CHORDS[chord_name]
    events = []
    t = 0
    triplet = QUARTER // 3  # 160 ticks
    for bar in range(4):
        bar_t = t
        # Each beat: 3 triplet subdivisions, chord struck on beat 1, pulsing
        for beat in range(4):
            beat_t = bar_t + beat * QUARTER
            # Strike block chord on beat 1 of each beat (accented)
            vol = 88 if beat == 0 else 75
            # Root + 3rd + 5th + b7
            for p in [c['root3'], c['third3'], c['fifth3'], c['flat7_3']]:
                events.append(MusicEvent(pitch=p, volume=vol, start_tick=beat_t,
                                        end_tick=beat_t + triplet * 2))
            # Second triplet: slight rest/pulse
            for p in [c['root3'], c['third3'], c['fifth3'], c['flat7_3']]:
                events.append(MusicEvent(pitch=p, volume=vol - 15, start_tick=beat_t + triplet * 2,
                                        end_tick=beat_t + triplet * 3))
        t += BAR
    pad_to_section(events)
    return MusicUnit(events=events)


def build_blue_note_lead(chord_name, section_offset):
    """Pattern 5: Blue-Note Sliding / Grace Notes
    Slide from b3 to 3, then to 5, b7. Expressive lead line.
    """
    c = CHORDS[chord_name]
    events = []
    t = 0
    # Blues scale notes relative to chord root (octave 4):
    # root, b3, 3, 4(#11/b5), 5, b7
    root = c['root3']  # e.g. C4=60
    b3 = root + 3      # Eb
    maj3 = root + 4    # E
    four = root + 5    # F
    b5 = root + 6      # F#
    fifth = root + 7   # G
    b7 = root + 10     # Bb
    
    for bar in range(4):
        bar_t = t
        # Phrase 1 (beat 1-2): Slide b3 -> 3 -> 5
        # Grace note b3 (short)
        events.append(MusicEvent(pitch=b3, volume=70, start_tick=bar_t, end_tick=bar_t + 80))
        # Slide to maj3 (medium)
        events.append(MusicEvent(pitch=maj3, volume=90, start_tick=bar_t + 80, end_tick=bar_t + 80 + 240))
        # Resolve to 5th (long)
        events.append(MusicEvent(pitch=fifth, volume=95, start_tick=bar_t + 320, end_tick=bar_t + 320 + 480))
        
        # Phrase 2 (beat 3-4): b7 -> b5 -> 4 -> root turnaround
        events.append(MusicEvent(pitch=b7, volume=88, start_tick=bar_t + HALF, end_tick=bar_t + HALF + 240))
        events.append(MusicEvent(pitch=b5, volume=75, start_tick=bar_t + HALF + 240, end_tick=bar_t + HALF + 400))
        events.append(MusicEvent(pitch=four, volume=80, start_tick=bar_t + HALF + 400, end_tick=bar_t + HALF + 640))
        events.append(MusicEvent(pitch=root, volume=85, start_tick=bar_t + HALF + 640, end_tick=bar_t + BAR))
        
        # Vary on odd bars: add b3 slide ornament
        if bar % 2 == 1:
            # Quick b3 grace at beat 3
            events.append(MusicEvent(pitch=b3, volume=65, start_tick=bar_t + HALF - 40, end_tick=bar_t + HALF))
        
        t += BAR
    pad_to_section(events)
    return MusicUnit(events=events)


def build_shuffle_rhythm(chord_name, section_offset):
    """Chord voice: shuffle rhythm comping with dom7 chords.
    Pattern 1 variant for chordal accompaniment.
    """
    c = CHORDS[chord_name]
    events = []
    t = 0
    for bar in range(4):
        bar_t = t
        # Shuffle comping: hits on beats 1, 2-and, 3, 4-and
        # Beat 1: full chord
        for p in [c['root3'], c['third3'], c['fifth3'], c['flat7_3']]:
            events.append(MusicEvent(pitch=p, volume=78, start_tick=bar_t, end_tick=bar_t + LONG_EIGHTH))
        # Beat 2-and: stab
        for p in [c['third3'], c['fifth3'], c['flat7_3']]:
            events.append(MusicEvent(pitch=p, volume=70, start_tick=bar_t + QUARTER + LONG_EIGHTH,
                                    end_tick=bar_t + QUARTER + LONG_EIGHTH + SHORT_EIGHTH))
        # Beat 3: full chord
        for p in [c['root3'], c['third3'], c['fifth3'], c['flat7_3']]:
            events.append(MusicEvent(pitch=p, volume=78, start_tick=bar_t + HALF,
                                    end_tick=bar_t + HALF + LONG_EIGHTH))
        # Beat 4-and: stab
        for p in [c['third3'], c['fifth3'], c['flat7_3']]:
            events.append(MusicEvent(pitch=p, volume=70, start_tick=bar_t + HALF + QUARTER + LONG_EIGHTH,
                                    end_tick=bar_t + HALF + QUARTER + LONG_EIGHTH + SHORT_EIGHTH))
        t += BAR
    pad_to_section(events)
    return MusicUnit(events=events)


def build_drums(section_offset):
    """Shuffle drum pattern: ride cymbal shuffle + snare on 2&4 + kick on 1&3."""
    events = []
    t = 0
    swing_pos = [0, LONG_EIGHTH, QUARTER, QUARTER + LONG_EIGHTH,
                HALF, HALF + LONG_EIGHTH, HALF + QUARTER, HALF + QUARTER + LONG_EIGHTH]
    
    for bar in range(4):
        bar_t = t
        for i in range(8):
            start = bar_t + swing_pos[i]
            dur = LONG_EIGHTH if i % 2 == 0 else SHORT_EIGHTH
            
            # Ride cymbal (51) on every eighth (shuffle pattern)
            ride_vol = 72 if i % 2 == 0 else 55
            events.append(MusicEvent(pitch=51, volume=ride_vol, start_tick=start, end_tick=start + dur))
            
            # Hi-hat (42) on beats 2 and 4 (positions 2,3 and 6,7)
            if i in [2, 3, 6, 7]:
                events.append(MusicEvent(pitch=42, volume=45, start_tick=start, end_tick=start + dur))
        
        # Snare (38) on beats 2 and 4
        events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_t + QUARTER, end_tick=bar_t + QUARTER + 240))
        events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_t + HALF + QUARTER, end_tick=bar_t + HALF + QUARTER + 240))
        
        # Kick (36) on beats 1 and 3
        events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t, end_tick=bar_t + 240))
        events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t + HALF, end_tick=bar_t + HALF + 240))
        
        t += BAR
    
    # Pad to section boundary
    events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10, end_tick=SECTION))
    return MusicUnit(events=events)


# === COMPOSITION ===
print("Building 32-bar Blues composition...")
print(f"Key: C Blues | BPM: {BPM} | Shuffle 2:1 | {TOTAL_BARS} bars")

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
composer.create_matrix(num_voices=4, num_sections=TOTAL_SECTIONS)

# Voices
composer.add_voice("Lead", program=MidiInstrument.TRUMPET, channel=0)
composer.add_voice("Chords", program=MidiInstrument.PIANO, channel=1)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
composer.add_voice("Drums", program=0, channel=9)

# Sections
for i, name in enumerate(SECTION_NAMES):
    composer.add_section(name, bars=SECTION_BARS)

# Fill voices per section
# Strategy: alternate bass patterns, vary lead patterns
for sec_idx in range(TOTAL_SECTIONS):
    name = SECTION_NAMES[sec_idx]
    chords = PROGRESSION[sec_idx]
    offset = sec_idx * SECTION
    
    # Drums: same shuffle throughout
    drum_unit = build_drums(offset)
    composer.fill_voice_section("Drums", name, drum_unit)
    
    # Lead: Pattern 5 (blue notes) for B sections, Pattern 1 (shuffle) for A/C
    if name.startswith('B'):
        lead_unit = build_blue_note_lead(chords[0], offset)
    elif name.startswith('C'):
        lead_unit = build_blue_note_lead(chords[0], offset)
    else:
        lead_unit = build_5th_6th_b7_shuffle(chords[0], offset)
    composer.fill_voice_section("Lead", name, lead_unit)
    
    # Chords: Pattern 4 (block chords) for C sections, shuffle comping for A/B
    if name.startswith('C'):
        chord_unit = build_block_chords(chords[0], offset)
    else:
        chord_unit = build_shuffle_rhythm(chords[0], offset)
    composer.fill_voice_section("Chords", name, chord_unit)
    
    # Bass: Pattern 2 (walking) for B sections, Pattern 3 (boogie) for A sections
    if name.startswith('B'):
        bass_unit = build_walking_bass(chords[0], offset)
    else:
        bass_unit = build_boogie_bass(chords[0], offset)
    composer.fill_voice_section("Bass", name, bass_unit)

# Validate
ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
if not ok:
    print("ERROR: Validation failed. Aborting.")
    sys.exit(1)

# Export MIDI
out_dir = "/opt/data/projects/Styles/Blues/blues-32bar-patterns/v1"
midi_path = os.path.join(out_dir, "blues_32bar.mid")
composer.to_midi(midi_path)

size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "MIDI file empty/corrupt"

# Grid visualization
grid_path = os.path.join(out_dir, "grid_visualization.txt")
write_grid_visualization(composer.matrix, grid_path, ticks_per_character=480,
                         voice_names=["Lead", "Chords", "Bass", "Drums"], bpm=BPM)
print(f"Grid: {grid_path}")

# Provenance
write_provenance(midi_path, AI_ASSISTED, "compose-loop/blues-32bar-patterns",
                 parameters={"bpm": BPM, "key": "C Blues", "bars": 32,
                            "patterns": ["5th-6th-b7 shuffle", "walking bass",
                                        "boogie bass", "block chords", "blue note slides"]})

print("Done ✓")
