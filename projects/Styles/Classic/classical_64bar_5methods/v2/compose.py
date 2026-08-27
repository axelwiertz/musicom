#!/usr/bin/env python3
"""64-bar Classical composition — 5 sections, 5 methods. Richer voicings, proper Classical style."""
import os, random
random.seed(42)

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

OUT = "/opt/data/projects/Styles/Classic/classical_64bar_5methods/v2"
os.makedirs(OUT, exist_ok=True)

# === CONSTANTS ===
TPB = 480
BPM = 108  # Classical tempo
BEATS = 4
BAR = TPB * BEATS
HALF = BAR // 2
QUARTER = BAR // 4
EIGHTH = QUARTER // 2
SIXTEENTH = EIGHTH // 2

# === HELPERS ===
def pad_to_section(events, section_ticks):
    for e in events:
        if e.end_tick > section_ticks:
            e.end_tick = section_ticks
    if not events or events[-1].end_tick < section_ticks:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=section_ticks-10, end_tick=section_ticks))
    return events

def mk(pitch, vol, start, end):
    return MusicEvent(pitch=pitch, volume=vol, start_tick=start, end_tick=end)

# Classical chord voicings (4-part harmony, proper voice leading)
# Format: {chord: [soprano, alto, tenor, bass]} in MIDI pitches
CHORDS_G_MAJOR = {
    'G':    [55, 52, 47, 31],  # G3 D3 G2 G1 (root position)
    'G6':   [57, 52, 47, 31],  # B3 D3 G2 G1 (first inversion)
    'D':    [57, 54, 50, 38],  # B3 F#3 D2 D1
    'D7':   [57, 53, 50, 38],  # B3 C3 G2 D1
    'Em':   [55, 52, 47, 35],  # G3 E3 B2 B1
    'C':    [57, 55, 52, 40],  # B3 G3 E2 C2
    'Am':   [57, 52, 48, 33],  # B3 E3 C2 A1
}

CHORDS_D_MAJOR = {
    'D':    [57, 54, 50, 38],  # B3 F#3 D2 D1
    'A':    [57, 54, 49, 37],  # B3 F#3 C#2 A1
    'A7':   [57, 53, 49, 37],  # B3 C3 C#2 A1
    'Bm':   [57, 54, 50, 36],  # B3 F#3 D2 B1
    'G':    [55, 52, 47, 31],  # G3 D3 G2 G1
    'F#m':  [57, 54, 49, 34],  # B3 F#3 C#2 F#1
}

CHORDS_C_MAJOR = {
    'C':    [55, 52, 48, 36],  # G3 E3 C2 C1
    'G':    [55, 52, 47, 31],  # G3 D3 G2 G1
    'F':    [53, 52, 48, 36],  # F3 E3 C2 C1
    'Am':   [52, 48, 45, 33],  # E3 C2 A1 A1
}

# ============================================================
# SECTION A: MARKOV TRANSITIONS (16 bars) — G MAJOR
# ============================================================
def build_section_a():
    """Markov melody over G-D-Em-C progression. Classical voice leading."""
    section_ticks = BAR * 16
    progression = ['G', 'D', 'Em', 'C'] * 4  # I-V-vi-IV
    
    # Markov on scale degrees (G major: G A B C D E F#)
    markov = {
        0: [(2, 0.30), (4, 0.25), (5, 0.20), (1, 0.15), (0, 0.10)],  # G
        1: [(2, 0.30), (3, 0.25), (4, 0.20), (0, 0.15), (1, 0.10)],  # A
        2: [(3, 0.30), (4, 0.25), (5, 0.20), (2, 0.15), (0, 0.10)],  # B
        3: [(4, 0.30), (5, 0.25), (2, 0.20), (3, 0.15), (0, 0.10)],  # C
        4: [(5, 0.30), (6, 0.25), (0, 0.20), (4, 0.15), (2, 0.10)],  # D
        5: [(6, 0.30), (0, 0.25), (3, 0.20), (5, 0.15), (4, 0.10)],  # E
        6: [(0, 0.30), (4, 0.25), (5, 0.20), (6, 0.15), (2, 0.10)],  # F#
    }
    
    def pick_next(degree):
        r = random.random()
        cum = 0
        for d, p in markov[degree]:
            cum += p
            if r < cum:
                return d
        return markov[degree][-1][0]
    
    G_MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]  # G A B C D E F#
    
    # Piano: Markov melody + Alberti bass accompaniment
    piano_events = []
    degree = 0
    for bar in range(16):
        chord = progression[bar]
        # Melody (right hand): Markov chain
        degree = 0  # Start from tonic each chord
        for beat in range(4):
            p = 60 + G_MAJOR_SCALE[degree % 7] + (degree // 7) * 12
            if p < 67:
                p += 12
            if p > 79:
                p -= 12
            piano_events.append(mk(p, 85, bar*BAR + beat*QUARTER, bar*BAR + beat*QUARTER + QUARTER - 10))
            degree = pick_next(degree)
        
        # Alberti bass (left hand): broken chord pattern
        chord_voicing = CHORDS_G_MAJOR[chord]
        bass_notes = [chord_voicing[2], chord_voicing[1], chord_voicing[0], chord_voicing[1]]
        for eighth in range(8):
            n = bass_notes[eighth % 4]
            piano_events.append(mk(n, 65, bar*BAR + eighth*EIGHTH, bar*BAR + eighth*EIGHTH + EIGHTH - 10))
    
    # Strings: 4-part harmony, sustained
    string_events = []
    for bar in range(16):
        chord = progression[bar]
        voicing = CHORDS_G_MAJOR[chord]
        for i, n in enumerate(voicing):
            string_events.append(mk(n, 70, bar*BAR, bar*BAR + BAR - 10))
    
    # Bass: root-fifth pattern
    bass_events = []
    bass_root = {'G': 31, 'D': 38, 'Em': 35, 'C': 36}
    bass_fifth = {'G': 43, 'D': 50, 'Em': 47, 'C': 43}
    for bar in range(16):
        chord = progression[bar]
        bass_events.append(mk(bass_root[chord], 90, bar*BAR, bar*BAR + HALF - 10))
        bass_events.append(mk(bass_fifth[chord], 80, bar*BAR + HALF, bar*BAR + BAR - 10))
    
    # Percussion: Classical light (timpani on tonic/dominant)
    perc_events = []
    for bar in range(16):
        # Timpani on beat 1
        perc_events.append(mk(47, 75, bar*BAR, bar*BAR + QUARTER - 10))
        # Light snare on beat 3 every other bar
        if bar % 2 == 0:
            perc_events.append(mk(38, 60, bar*BAR + HALF, bar*BAR + HALF + QUARTER - 10))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# SECTION B: ISORHYTHMIC TALEA-COLOR (16 bars) — D MAJOR
# ============================================================
def build_section_b():
    """Isorhythmic in D major. Talea(7) x Color(5)."""
    section_ticks = BAR * 16
    progression = ['D', 'A', 'Bm', 'G'] * 4  # I-V-vi-IV in D
    
    talea = [1, 0, 1, 1, 0, 1, 0]
    color = [62, 66, 69, 71, 74]  # D4 F#4 A4 B4 D5
    
    piano_events = []
    color_idx = 0
    total_quarters = 16 * 4
    for i in range(total_quarters):
        if talea[i % 7] == 1:
            p = color[color_idx % 5]
            start = i * QUARTER
            piano_events.append(mk(p, 85, start, start + QUARTER - 10))
            color_idx += 1
    
    # Strings: rich 4-part
    string_events = []
    for bar in range(16):
        chord = progression[bar]
        voicing = CHORDS_D_MAJOR[chord]
        for n in voicing:
            string_events.append(mk(n, 70, bar*BAR, bar*BAR + BAR - 10))
    
    # Bass
    bass_events = []
    bass_root = {'D': 38, 'A': 33, 'Bm': 35, 'G': 31}
    bass_fifth = {'D': 50, 'A': 45, 'Bm': 47, 'G': 43}
    for bar in range(16):
        chord = progression[bar]
        bass_events.append(mk(bass_root[chord], 90, bar*BAR, bar*BAR + HALF - 10))
        bass_events.append(mk(bass_fifth[chord], 80, bar*BAR + HALF, bar*BAR + BAR - 10))
    
    # Percussion
    perc_events = []
    for bar in range(16):
        perc_events.append(mk(36, 85, bar*BAR, bar*BAR + QUARTER - 10))
        perc_events.append(mk(38, 70, bar*BAR + HALF, bar*BAR + HALF + QUARTER - 10))
        for e in range(8):
            perc_events.append(mk(42, 45, bar*BAR + e*EIGHTH, bar*BAR + e*EIGHTH + EIGHTH - 10))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# SECTION C: DPSM PHASE-SHIFT (16 bars) — G MAJOR
# ============================================================
def build_section_c():
    """3-phase arpeggios in G major. Flowing texture."""
    section_ticks = BAR * 16
    progression = ['G', 'Em', 'C', 'D'] * 4
    
    # Chord tones for arpeggios (expanded range)
    arp_tones = {
        'G':  [43, 47, 50, 55, 59, 62, 67, 71],
        'Em': [40, 43, 47, 52, 55, 59, 64, 67],
        'C':  [36, 40, 43, 48, 52, 55, 60, 64],
        'D':  [38, 42, 45, 50, 54, 57, 62, 66],
    }
    
    offsets = [0, 160, 320]
    
    piano_events = []
    for bar in range(16):
        chord = progression[bar]
        tones = arp_tones[chord]
        for layer_offset in offsets:
            t = layer_offset
            note_idx = 0
            while t < BAR:
                p = tones[note_idx % len(tones)]
                piano_events.append(mk(p, 60, bar*BAR + t, bar*BAR + t + SIXTEENTH - 5))
                t += SIXTEENTH
                note_idx += 1
    
    # Strings: sustained pads
    string_events = []
    for bar in range(16):
        chord = progression[bar]
        voicing = CHORDS_G_MAJOR[chord]
        for n in voicing:
            string_events.append(mk(n, 65, bar*BAR, bar*BAR + BAR - 10))
    
    # Bass: walking eighth notes
    bass_events = []
    bass_walk = {
        'G':  [31, 38, 43, 47, 50, 47, 43, 38],
        'Em': [28, 35, 40, 43, 47, 43, 40, 35],
        'C':  [24, 31, 36, 40, 43, 40, 36, 31],
        'D':  [26, 33, 38, 42, 45, 42, 38, 33],
    }
    for bar in range(16):
        chord = progression[bar]
        walk = bass_walk[chord]
        for e in range(8):
            bass_events.append(mk(walk[e], 85, bar*BAR + e*EIGHTH, bar*BAR + e*EIGHTH + EIGHTH - 10))
    
    # Percussion: Euclidean
    perc_events = []
    for bar in range(16):
        for pos in [0, 4, 8, 12]:
            perc_events.append(mk(36, 90, bar*BAR + pos*SIXTEENTH, bar*BAR + pos*SIXTEENTH + SIXTEENTH - 5))
        for pos in [0, 3, 5]:
            tick = pos * EIGHTH
            perc_events.append(mk(38, 75, bar*BAR + tick, bar*BAR + tick + EIGHTH - 5))
        for pos in [0, 2, 4, 6, 8, 11, 14]:
            perc_events.append(mk(42, 50, bar*BAR + pos*SIXTEENTH, bar*BAR + pos*SIXTEENTH + SIXTEENTH - 5))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# SECTION D: XENAKIS SIEVE (8 bars) — D MAJOR (dominant preparation)
# ============================================================
def build_section_d():
    """Sieve on D pedal. Building tension for return to G."""
    section_ticks = BAR * 8
    
    # Xenakis sieve: {x: x%3==0} U {x: x%5==2} in [62,81]
    sieve = set()
    for x in range(62, 82):
        if x % 3 == 0 or x % 5 == 2:
            sieve.add(x)
    sieve = sorted(sieve)
    
    piano_events = []
    sieve_idx = 0
    for bar in range(8):
        for eighth in range(8):
            p = sieve[sieve_idx % len(sieve)]
            vol = 95 if eighth == 0 else 70
            piano_events.append(mk(p, vol, bar*BAR + eighth*EIGHTH, bar*BAR + eighth*EIGHTH + EIGHTH - 10))
            sieve_idx += 1
    
    # Strings: tremolo
    string_events = []
    for bar in range(8):
        chord_tones = [50, 54, 57]  # D3 F#3 A3
        for sixteenth in range(16):
            n = chord_tones[sixteenth % 3]
            vol = 60 + (15 if sixteenth % 2 == 0 else 0)
            string_events.append(mk(n, vol, bar*BAR + sixteenth*SIXTEENTH, bar*BAR + sixteenth*SIXTEENTH + SIXTEENTH - 5))
    
    # Bass: D pedal
    bass_events = []
    for bar in range(8):
        bass_events.append(mk(38, 90, bar*BAR, bar*BAR + BAR - 10))
    
    # Percussion: accelerating
    perc_events = []
    for bar in range(8):
        base_vol = 50 + bar * 8
        if bar < 2:
            for q in range(4):
                perc_events.append(mk(38, base_vol, bar*BAR + q*QUARTER, bar*BAR + q*QUARTER + QUARTER - 10))
        elif bar < 4:
            for e in range(8):
                perc_events.append(mk(38, base_vol, bar*BAR + e*EIGHTH, bar*BAR + e*EIGHTH + EIGHTH - 10))
        else:
            for s in range(16):
                perc_events.append(mk(38, min(127, base_vol + s), bar*BAR + s*SIXTEENTH, bar*BAR + s*SIXTEENTH + SIXTEENTH - 5))
            perc_events.append(mk(36, 100, bar*BAR, bar*BAR + QUARTER - 10))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# SECTION E: SKELETON-FIRST DNA (8 bars, Coda) — G MAJOR
# ============================================================
def build_section_e():
    """DNA transforms, final resolution to G."""
    section_ticks = BAR * 8
    
    # DNA: G major triad [0, 4, 7] intervals
    pitch_dna = [0, 4, 7]
    rhythm_dna = [QUARTER, EIGHTH, EIGHTH]
    
    G_MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
    
    def dna_melody(start_tick, pitch_offsets, durations, root=67, scale=G_MAJOR_SCALE, vol=80):
        events = []
        t = start_tick
        for i in range(len(pitch_offsets)):
            p = root + scale[pitch_offsets[i] % 7] + (pitch_offsets[i] // 7) * 12
            d = durations[i % len(durations)]
            events.append(mk(p, vol, t, t + d - 10))
            t += d
        return events
    
    piano_events = []
    
    # Bars 0-1: Original
    for bar in range(2):
        for rep in range(2):
            evts = dna_melody(bar*BAR + rep*BAR//2, pitch_dna, rhythm_dna)
            piano_events.extend(evts)
    
    # Bars 2-3: Augmented
    for bar in range(2, 4):
        aug_durations = [d*2 for d in rhythm_dna]
        evts = dna_melody((bar-2)*BAR + (bar%2)*BAR//2, pitch_dna, aug_durations, root=79)
        piano_events.extend(evts)
    
    # Bars 4-5: Retrograde
    retro_pitches = list(reversed(pitch_dna))
    for bar in range(4, 6):
        for rep in range(2):
            evts = dna_melody(bar*BAR + rep*BAR//2, retro_pitches, rhythm_dna)
            piano_events.extend(evts)
    
    # Bar 6: Inverted
    inverted = [14 - d for d in pitch_dna]
    half_rhythm = [d//2 for d in rhythm_dna]
    for rep in range(4):
        evts = dna_melody(6*BAR + rep*BAR//4, inverted, half_rhythm, vol=75)
        piano_events.extend(evts)
    
    # Bar 7: Final G major chord
    for n in [55, 59, 62, 67]:  # G3 B3 D4 G4
        piano_events.append(mk(n, 85, 7*BAR, 7*BAR + BAR - 10))
    
    # Strings
    string_events = []
    for bar in range(8):
        if bar < 7:
            for d in pitch_dna:
                p = 43 + G_MAJOR_SCALE[d % 7]
                string_events.append(mk(p, 65, bar*BAR, bar*BAR + BAR - 10))
        else:
            for n in [43, 47, 50, 55]:
                string_events.append(mk(n, 70, bar*BAR, bar*BAR + BAR - 10))
    
    # Bass
    bass_events = []
    bass_line = [31, 31, 30, 30, 28, 28, 26, 31]  # G G F# F# E E D G
    for bar in range(8):
        bass_events.append(mk(bass_line[bar], 85, bar*BAR, bar*BAR + BAR - 10))
    
    # Percussion
    perc_events = []
    for bar in range(8):
        if bar == 7:
            perc_events.append(mk(49, 100, 7*BAR, 7*BAR + BAR - 10))
            perc_events.append(mk(36, 100, 7*BAR, 7*BAR + QUARTER - 10))
        elif bar < 6:
            perc_events.append(mk(36, 70, bar*BAR, bar*BAR + QUARTER - 10))
    
    piano_unit = MusicUnit(events=pad_to_section(piano_events, section_ticks))
    string_unit = MusicUnit(events=pad_to_section(string_events, section_ticks))
    bass_unit = MusicUnit(events=pad_to_section(bass_events, section_ticks))
    perc_unit = MusicUnit(events=pad_to_section(perc_events, section_ticks))
    return piano_unit, string_unit, bass_unit, perc_unit

# ============================================================
# ASSEMBLE
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

composer.add_voice("Strings", program=MidiInstrument.STRING_ENSEMBLE, channel=0)
composer.add_voice("Piano", program=MidiInstrument.PIANO, channel=1)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
composer.add_voice("Percussion", program=0, channel=9)

composer.add_section("A", bars=16)
composer.add_section("B", bars=16)
composer.add_section("C", bars=16)
composer.add_section("D", bars=8)
composer.add_section("E", bars=8)

print("Filling matrix...")
composer.fill_voice_section("Piano", "A", piano_a)
composer.fill_voice_section("Strings", "A", strings_a)
composer.fill_voice_section("Bass", "A", bass_a)
composer.fill_voice_section("Percussion", "A", perc_a)

composer.fill_voice_section("Piano", "B", piano_b)
composer.fill_voice_section("Strings", "B", strings_b)
composer.fill_voice_section("Bass", "B", bass_b)
composer.fill_voice_section("Percussion", "B", perc_b)

composer.fill_voice_section("Piano", "C", piano_c)
composer.fill_voice_section("Strings", "C", strings_c)
composer.fill_voice_section("Bass", "C", bass_c)
composer.fill_voice_section("Percussion", "C", perc_c)

composer.fill_voice_section("Piano", "D", piano_d)
composer.fill_voice_section("Strings", "D", strings_d)
composer.fill_voice_section("Bass", "D", bass_d)
composer.fill_voice_section("Percussion", "D", perc_d)

composer.fill_voice_section("Piano", "E", piano_e)
composer.fill_voice_section("Strings", "E", strings_e)
composer.fill_voice_section("Bass", "E", bass_e)
composer.fill_voice_section("Percussion", "E", perc_e)

print("Validating...")
ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
assert ok, f"Validation failed: {msg}"

midi_path = f"{OUT}/classical_64bar.mid"
composer.to_midi(midi_path)
print(f"MIDI: {midi_path}")

import os
assert os.path.getsize(midi_path) > 40
print(f"Size: {os.path.getsize(midi_path)} bytes")

grid_path = f"{OUT}/grid_visualization.txt"
write_grid_visualization(composer.matrix, grid_path,
                         ticks_per_character=240,
                         voice_names=["Strings", "Piano", "Bass", "Percussion"],
                         bpm=BPM)

write_provenance(midi_path, AI_ASSISTED, "compose-loop/classical_64bar_5methods",
                 parameters={"bpm": BPM, "keys": "G-D-G-D-G", "bars": 64,
                            "methods": ["Markov", "Isorhythmic", "DPSM", "Xenakis", "DNA"]})

print("\n✓ COMPOSED")
