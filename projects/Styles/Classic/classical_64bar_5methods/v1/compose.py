#!/usr/bin/env python3
"""64-bar Classic composition — 5 sections, 5 algorithmic methods."""
import os, random
random.seed(42)

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

OUT = "/opt/data/projects/Styles/Classic/classical_64bar_5methods/v1"
os.makedirs(OUT, exist_ok=True)

# === CONSTANTS ===
TPB = 480
BPM = 112
BEATS = 4
BAR = TPB * BEATS        # 1920
HALF = BAR // 2          # 960
QUARTER = BAR // 4       # 480
EIGHTH = QUARTER // 2    # 240
SIXTEENTH = EIGHTH // 2  # 120

# === HELPERS ===
def pad_to_section(events, section_ticks):
    for e in events:
        if e.end_tick > section_ticks:
            e.end_tick = section_ticks
    if not events or events[-1].end_tick < section_ticks:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=section_ticks-10, end_tick=section_ticks))
    return events

def diatonic(key_root, scale_intervals, degree_index):
    """Absolute MIDI pitch from scale degree."""
    return key_root + (degree_index // 7) * 12 + scale_intervals[degree_index % 7]

def mk(pitch, vol, start, end):
    return MusicEvent(pitch=pitch, volume=vol, start_tick=start, end_tick=end)

# === SCALES ===
C_MAJOR = [0, 2, 4, 5, 7, 9, 11]
F_MAJOR = [0, 2, 4, 5, 7, 9, 11]  # same intervals, different root
G_MAJOR = [0, 2, 4, 5, 7, 9, 11]

# Chord definitions: (root_degree, third_degree, fifth_degree) in scale
CHORDS_C = {
    'C':  (0, 2, 4),   # C E G
    'Am': (5, 0, 2),   # A C E  (degree 5=A, +7=next octave C, +7=E)
    'F':  (3, 5, 0),   # F A C
    'G':  (4, 6, 1),   # G B D
}

def chord_pitches(root_midi, intervals, chord_name, octave_offset=0):
    """Get chord pitches as MIDI numbers given root and scale."""
    degrees = CHORDS_C[chord_name]
    pitches = []
    for d in degrees:
        p = root_midi + intervals[d % 7] + (d // 7) * 12 + octave_offset
        pitches.append(p)
    return pitches

# ============================================================
# SECTION A: MARKOV TRANSITIONS (16 bars)
# ============================================================
def build_section_a():
    """Markov chain melody over C-Am-F-G progression."""
    section_ticks = BAR * 16  # 30720
    progression = ['C', 'Am', 'F', 'G'] * 4  # 16 bars, 4 bars each chord
    
    # Markov transition table (scale degrees 0-6: C D E F G A B)
    markov = {
        0: [(2, 0.30), (4, 0.25), (5, 0.20), (1, 0.15), (0, 0.10)],
        1: [(2, 0.30), (3, 0.25), (4, 0.20), (0, 0.15), (1, 0.10)],
        2: [(3, 0.30), (4, 0.25), (5, 0.20), (2, 0.15), (0, 0.10)],
        3: [(4, 0.30), (5, 0.25), (2, 0.20), (3, 0.15), (0, 0.10)],
        4: [(5, 0.30), (6, 0.25), (0, 0.20), (4, 0.15), (2, 0.10)],
        5: [(6, 0.30), (0, 0.25), (3, 0.20), (5, 0.15), (4, 0.10)],
        6: [(0, 0.30), (4, 0.25), (5, 0.20), (6, 0.15), (2, 0.10)],
    }
    
    def pick_next(degree):
        r = random.random()
        cum = 0
        for d, p in markov[degree]:
            cum += p
            if r < cum:
                return d
        return markov[degree][-1][0]
    
    # Piano: Markov melody
    piano_events = []
    degree = 0
    for bar in range(16):
        chord = progression[bar]
        chord_deg = CHORDS_C[chord]
        # Start from chord root degree each bar
        degree = chord_deg[0]
        for beat in range(4):
            p = diatonic(60, C_MAJOR, degree)
            # Ensure in octave 4-5
            if p < 60:
                p += 12
            if p > 76:
                p -= 12
            piano_events.append(mk(p, 80, bar*BAR + beat*QUARTER, bar*BAR + beat*QUARTER + QUARTER - 10))
            degree = pick_next(degree)
    
    # Strings: sustained whole-note chords
    string_events = []
    for bar in range(16):
        chord = progression[bar]
        # Build chord in octave 3
        if chord == 'C':
            notes = [48, 52, 55]  # C3 E3 G3
        elif chord == 'Am':
            notes = [45, 48, 52]  # A2 C3 E3
        elif chord == 'F':
            notes = [41, 45, 48]  # F2 A2 C3
        elif chord == 'G':
            notes = [43, 47, 50]  # G2 B2 D3
        for n in notes:
            string_events.append(mk(n, 70, bar*BAR, bar*BAR + BAR - 10))
    
    # Bass: root on 1, fifth on 3
    bass_events = []
    bass_notes = {'C': (36, 43), 'Am': (33, 40), 'F': (29, 36), 'G': (31, 38)}
    for bar in range(16):
        chord = progression[bar]
        root, fifth = bass_notes[chord]
        bass_events.append(mk(root, 90, bar*BAR, bar*BAR + HALF - 10))
        bass_events.append(mk(fifth, 80, bar*BAR + HALF, bar*BAR + BAR - 10))
    
    # Percussion: light
    perc_events = []
    for bar in range(16):
        # Hi-hat every eighth
        for eighth in range(8):
            perc_events.append(mk(42, 50, bar*BAR + eighth*EIGHTH, bar*BAR + eighth*EIGHTH + EIGHTH - 10))
        # Snare on beat 3 every other bar
        if bar % 2 == 0:
            perc_events.append(mk(38, 70, bar*BAR + HALF, bar*BAR + HALF + QUARTER - 10))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# SECTION B: ISORHYTHMIC TALEA-COLOR (16 bars)
# ============================================================
def build_section_b():
    """Talea(7) x Color(5) coprime isorhythm in F major."""
    section_ticks = BAR * 16
    progression = ['F', 'Am', 'F', 'G'] * 4  # F major context
    
    # Talea: rhythm cycle length 7
    talea = [1, 0, 1, 1, 0, 1, 0]
    # Color: pitch cycle length 5 (F major pitches)
    color = [65, 69, 72, 74, 77]  # F4 A4 C5 D5 F5
    
    # Piano: isorhythmic
    piano_events = []
    color_idx = 0
    total_quarters = 16 * 4  # 64 quarter positions
    for i in range(total_quarters):
        if talea[i % 7] == 1:
            p = color[color_idx % 5]
            start = i * QUARTER
            piano_events.append(mk(p, 85, start, start + QUARTER - 10))
            color_idx += 1
    
    # Strings: sustained chords
    string_events = []
    chord_map = {
        'F': [41, 45, 48],   # F2 A2 C3
        'Am': [45, 48, 52],  # A2 C3 E3
        'G': [43, 47, 50],   # G2 B2 D3
    }
    for bar in range(16):
        chord = progression[bar]
        for n in chord_map[chord]:
            string_events.append(mk(n, 70, bar*BAR, bar*BAR + BAR - 10))
    
    # Bass: root-fifth alternating half notes
    bass_events = []
    bass_map = {'F': (29, 36), 'Am': (33, 40), 'G': (31, 38)}
    for bar in range(16):
        chord = progression[bar]
        root, fifth = bass_map[chord]
        bass_events.append(mk(root, 90, bar*BAR, bar*BAR + HALF - 10))
        bass_events.append(mk(fifth, 80, bar*BAR + HALF, bar*BAR + BAR - 10))
    
    # Percussion: full
    perc_events = []
    for bar in range(16):
        # Kick on 1, 3
        perc_events.append(mk(36, 90, bar*BAR, bar*BAR + QUARTER - 10))
        perc_events.append(mk(36, 80, bar*BAR + HALF, bar*BAR + HALF + QUARTER - 10))
        # Snare on 2, 4
        perc_events.append(mk(38, 75, bar*BAR + QUARTER, bar*BAR + QUARTER + QUARTER - 10))
        perc_events.append(mk(38, 75, bar*BAR + HALF + QUARTER, bar*BAR + HALF + BAR - 10))
        # Hi-hat eighths
        for e in range(8):
            perc_events.append(mk(42, 45, bar*BAR + e*EIGHTH, bar*BAR + e*EIGHTH + EIGHTH - 10))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# SECTION C: DPSM PHASE-SHIFT (16 bars)
# ============================================================
def build_section_c():
    """3 phase-shifted arpeggio layers in G major."""
    section_ticks = BAR * 16
    progression = ['G', 'Em', 'C', 'D'] * 4
    
    # Chord tones for arpeggios
    arp_tones = {
        'G':  [43, 47, 50, 55, 59, 62],   # G2 B2 D3 G3 B3 D4
        'Em': [40, 43, 47, 52, 55, 59],   # E2 G2 B2 E3 G3 B3
        'C':  [36, 40, 43, 48, 52, 55],   # C2 E2 G2 C3 E3 G3
        'D':  [38, 42, 45, 50, 54, 57],   # D2 F#2 A2 D3 F#3 A3
    }
    
    # DPSM: 3 layers offset by 160 ticks
    offsets = [0, 160, 320]
    
    piano_events = []
    for bar in range(16):
        chord = progression[bar]
        tones = arp_tones[chord]
        for layer_offset in offsets:
            # Sixteenth-note arpeggio cycling through tones
            t = layer_offset
            note_idx = 0
            while t < BAR:
                p = tones[note_idx % len(tones)]
                if p < 48:
                    p += 12
                piano_events.append(mk(p, 60, bar*BAR + t, bar*BAR + t + SIXTEENTH - 5))
                t += SIXTEENTH
                note_idx += 1
    
    # Strings: sustained pads
    string_events = []
    string_chords = {
        'G':  [43, 47, 50],
        'Em': [40, 43, 47],
        'C':  [36, 40, 43],
        'D':  [38, 42, 45],
    }
    for bar in range(16):
        chord = progression[bar]
        for n in string_chords[chord]:
            string_events.append(mk(n, 65, bar*BAR, bar*BAR + BAR - 10))
    
    # Bass: walking eighth notes
    bass_events = []
    bass_tones = {
        'G':  [31, 38, 43, 47],
        'Em': [28, 35, 40, 43],
        'C':  [24, 31, 36, 40],
        'D':  [26, 33, 38, 42],
    }
    for bar in range(16):
        chord = progression[bar]
        tones = bass_tones[chord]
        for e in range(8):
            p = tones[e % len(tones)]
            bass_events.append(mk(p, 85, bar*BAR + e*EIGHTH, bar*BAR + e*EIGHTH + EIGHTH - 10))
    
    # Percussion: Euclidean groove
    perc_events = []
    for bar in range(16):
        # Kick: E(4,16) = positions 0,4,8,12
        for pos in [0, 4, 8, 12]:
            perc_events.append(mk(36, 95, bar*BAR + pos*SIXTEENTH, bar*BAR + pos*SIXTEENTH + SIXTEENTH - 5))
        # Snare: E(3,8) = positions 0,3,5 of 8 → mapped to sixteenths
        for pos in [0, 3, 5]:
            tick = pos * (EIGHTH)
            perc_events.append(mk(38, 80, bar*BAR + tick, bar*BAR + tick + EIGHTH - 5))
        # Hi-hat: E(7,16) = 7 hits in 16
        for pos in [0, 2, 4, 6, 8, 11, 14]:
            perc_events.append(mk(42, 50, bar*BAR + pos*SIXTEENTH, bar*BAR + pos*SIXTEENTH + SIXTEENTH - 5))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# SECTION D: XENAKIS SIEVE (8 bars)
# ============================================================
def build_section_d():
    """Modular congruence pitch set, C pedal, building tension."""
    section_ticks = BAR * 8
    
    # Xenakis sieve: {x: x%3==0} U {x: x%5==2} in [60,79]
    sieve = set()
    for x in range(60, 80):
        if x % 3 == 0 or x % 5 == 2:
            sieve.add(x)
    sieve = sorted(sieve)  # [60,62,63,66,67,69,72,75,77,78]
    
    # Piano: eighth notes from sieve pool, accent beat 1
    piano_events = []
    sieve_idx = 0
    for bar in range(8):
        for eighth in range(8):
            p = sieve[sieve_idx % len(sieve)]
            vol = 95 if eighth == 0 else 70
            piano_events.append(mk(p, vol, bar*BAR + eighth*EIGHTH, bar*BAR + eighth*EIGHTH + EIGHTH - 10))
            sieve_idx += 1
    
    # Strings: tremolo sixteenth notes on C chord tones
    string_events = []
    chord_tones = [48, 52, 55]  # C3 E3 G3
    for bar in range(8):
        for sixteenth in range(16):
            n = chord_tones[sixteenth % 3]
            vol = 60 + (15 if sixteenth % 2 == 0 else 0)  # oscillation
            string_events.append(mk(n, vol, bar*BAR + sixteenth*SIXTEENTH, bar*BAR + sixteenth*SIXTEENTH + SIXTEENTH - 5))
    
    # Bass: C2 pedal whole notes
    bass_events = []
    for bar in range(8):
        bass_events.append(mk(36, 90, bar*BAR, bar*BAR + BAR - 10))
    
    # Percussion: accelerating snare rolls + crescendo
    perc_events = []
    for bar in range(8):
        # Phase 1 (bars 0-1): quarter note snare
        # Phase 2 (bars 2-3): eighth note snare
        # Phase 3 (bars 4-5): sixteenth note snare
        # Phase 4 (bars 6-7): sixteenth + crescendo
        base_vol = 50 + bar * 8  # crescendo
        
        if bar < 2:
            # Quarter notes
            for q in range(4):
                perc_events.append(mk(38, base_vol, bar*BAR + q*QUARTER, bar*BAR + q*QUARTER + QUARTER - 10))
        elif bar < 4:
            # Eighth notes
            for e in range(8):
                perc_events.append(mk(38, base_vol, bar*BAR + e*EIGHTH, bar*BAR + e*EIGHTH + EIGHTH - 10))
        else:
            # Sixteenth notes
            for s in range(16):
                perc_events.append(mk(38, min(127, base_vol + s), bar*BAR + s*SIXTEENTH, bar*BAR + s*SIXTEENTH + SIXTEENTH - 5))
            # Kick on beat 1
            perc_events.append(mk(36, 100, bar*BAR, bar*BAR + QUARTER - 10))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# SECTION E: SKELETON-FIRST DNA (8 bars, Coda)
# ============================================================
def build_section_e():
    """DNA pitch [0,4,7] + rhythm [Q,E,E] transformations."""
    section_ticks = BAR * 8
    
    # DNA seeds
    pitch_dna = [0, 4, 7]   # C E G intervals from root
    rhythm_dna = [QUARTER, EIGHTH, EIGHTH]  # Q E E = 1 bar
    
    def dna_melody(start_tick, pitch_offsets, durations, root=60, scale=C_MAJOR, vol=80):
        events = []
        t = start_tick
        for i in range(len(pitch_offsets)):
            p = root + scale[pitch_offsets[i] % 7] + (pitch_offsets[i] // 7) * 12
            d = durations[i % len(durations)]
            events.append(mk(p, vol, t, t + d - 10))
            t += d
        return events
    
    piano_events = []
    
    # Bars 0-1: Original DNA, repeat to fill 2 bars
    for bar in range(2):
        for rep in range(2):  # 2 repetitions of DNA per bar
            evts = dna_melody(bar*BAR + rep*BAR//2, pitch_dna, rhythm_dna)
            piano_events.extend(evts)
    
    # Bars 2-3: Augmented (x2 duration), transposed +12
    for bar in range(2, 4):
        aug_durations = [d*2 for d in rhythm_dna]  # HALF, QUARTER, QUARTER
        evts = dna_melody((bar-2)*BAR + (bar%2)*BAR//2, [d for d in pitch_dna], aug_durations, root=72)
        piano_events.extend(evts)
    
    # Bars 4-5: Retrograde
    retro_pitches = list(reversed(pitch_dna))
    for bar in range(4, 6):
        for rep in range(2):
            evts = dna_melody(bar*BAR + rep*BAR//2, retro_pitches, rhythm_dna)
            piano_events.extend(evts)
    
    # Bar 6: Inverted (mirror around C4=60), halved rhythm
    inverted = [14 - d for d in pitch_dna]  # mirror: 14-0=14, 14-4=10, 14-7=7
    half_rhythm = [d//2 for d in rhythm_dna]  # EIGHTH, SIXTEENTH, SIXTEENTH
    for rep in range(4):  # 4 reps to fill bar
        evts = dna_melody(6*BAR + rep*BAR//4, inverted, half_rhythm, vol=75)
        piano_events.extend(evts)
    
    # Bar 7: Final sustained C major chord
    for n in [60, 64, 67, 72]:  # C4 E4 G4 C5
        piano_events.append(mk(n, 80, 7*BAR, 7*BAR + BAR - 10))
    
    # Strings: DNA-based sustained chords, progressive dropout
    string_events = []
    for bar in range(8):
        if bar < 7:
            # Build from DNA intervals
            for d in pitch_dna:
                p = 48 + C_MAJOR[d % 7]  # octave 3
                string_events.append(mk(p, 65, bar*BAR, bar*BAR + BAR - 10))
        else:
            # Final bar: full C major chord
            for n in [48, 52, 55, 60]:
                string_events.append(mk(n, 70, bar*BAR, bar*BAR + BAR - 10))
    
    # Bass: root C, descending to final C
    bass_events = []
    bass_line = [36, 36, 35, 35, 33, 33, 31, 36]  # C2 C2 B1 B1 A1 A1 G1 C2
    for bar in range(8):
        p = bass_line[bar]
        bass_events.append(mk(p, 85, bar*BAR, bar*BAR + BAR - 10))
    
    # Percussion: sparse, crash on final bar only
    perc_events = []
    for bar in range(8):
        if bar == 7:
            # Crash cymbal + kick
            perc_events.append(mk(49, 100, 7*BAR, 7*BAR + BAR - 10))  # crash
            perc_events.append(mk(36, 100, 7*BAR, 7*BAR + QUARTER - 10))  # kick
        elif bar < 6:
            # Minimal: just kick on beat 1
            perc_events.append(mk(36, 70, bar*BAR, bar*BAR + QUARTER - 10))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# ASSEMBLE COMPOSITION
# ============================================================
print("Building sections...")

piano_a, strings_a, bass_a, perc_a = build_section_a()
piano_b, strings_b, bass_b, perc_b = build_section_b()
piano_c, strings_c, bass_c, perc_c = build_section_c()
piano_d, strings_d, bass_d, perc_d = build_section_d()
piano_e, strings_e, bass_e, perc_e = build_section_e()

print("Creating composer...")
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
composer.create_matrix(num_voices=4, num_sections=5)

# Add voices
composer.add_voice("Strings", program=MidiInstrument.STRING_ENSEMBLE, channel=0)
composer.add_voice("Piano", program=MidiInstrument.PIANO, channel=1)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
composer.add_voice("Percussion", program=0, channel=9)

# Add sections
composer.add_section("A", bars=16)
composer.add_section("B", bars=16)
composer.add_section("C", bars=16)
composer.add_section("D", bars=8)
composer.add_section("E", bars=8)

# Fill voice-sections
print("Filling matrix...")
# Section A: Markov
composer.fill_voice_section("Piano", "A", piano_a)
composer.fill_voice_section("Strings", "A", strings_a)
composer.fill_voice_section("Bass", "A", bass_a)
composer.fill_voice_section("Percussion", "A", perc_a)

# Section B: Isorhythmic
composer.fill_voice_section("Piano", "B", piano_b)
composer.fill_voice_section("Strings", "B", strings_b)
composer.fill_voice_section("Bass", "B", bass_b)
composer.fill_voice_section("Percussion", "B", perc_b)

# Section C: DPSM
composer.fill_voice_section("Piano", "C", piano_c)
composer.fill_voice_section("Strings", "C", strings_c)
composer.fill_voice_section("Bass", "C", bass_c)
composer.fill_voice_section("Percussion", "C", perc_c)

# Section D: Xenakis
composer.fill_voice_section("Piano", "D", piano_d)
composer.fill_voice_section("Strings", "D", strings_d)
composer.fill_voice_section("Bass", "D", bass_d)
composer.fill_voice_section("Percussion", "D", perc_d)

# Section E: DNA
composer.fill_voice_section("Piano", "E", piano_e)
composer.fill_voice_section("Strings", "E", strings_e)
composer.fill_voice_section("Bass", "E", bass_e)
composer.fill_voice_section("Percussion", "E", perc_e)

# Validate
print("Validating...")
ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
assert ok, f"Validation failed: {msg}"

# Export MIDI
midi_path = f"{OUT}/classical_64bar.mid"
composer.to_midi(midi_path)
print(f"MIDI exported: {midi_path}")

import os
assert os.path.getsize(midi_path) > 40, "MIDI empty/corrupt"
print(f"MIDI size: {os.path.getsize(midi_path)} bytes")

# Grid visualization
grid_path = f"{OUT}/grid_visualization.txt"
write_grid_visualization(composer.matrix, grid_path,
                         ticks_per_character=240,
                         voice_names=["Strings", "Piano", "Bass", "Percussion"],
                         bpm=BPM)
print(f"Grid visualization: {grid_path}")

# Provenance
write_provenance(midi_path, AI_ASSISTED, "compose-loop/classical_64bar_5methods",
                 parameters={"bpm": BPM, "key": "C major", "bars": 64,
                            "methods": ["Markov", "Isorhythmic", "DPSM", "Xenakis", "DNA"]})
print("Provenance written.")
print("\n✓ COMPOSITION COMPLETE")
