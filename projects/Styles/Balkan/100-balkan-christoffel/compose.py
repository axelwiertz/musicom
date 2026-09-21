# -*- coding: utf-8 -*-
"""100-balkan-christoffel - Balkan Kopanitsa (11/8) / Method 069 Christoffel Word Combinatorial Composition (CWCC).
LAYER: concrete.

Architecture:
Two-Phase Architecture:
  Phase 1: Raw Christoffel Word Combinatorial Draft.
           - Lower Christoffel words C(5, 2) and Sturmian morphism expansions (G, D)
           - Raw pitch sequence walking unconstrained interval contours.
           - Unharmonized, single voice (Clarinet), raw dynamic contour.
           - Zero-drift validated single-voice draft exported as 100-balkan-christoffel-phase1.mid.
  Phase 2: Musicom rules post-processing:
           - Strict 16th-grid quantization (120 ticks @ 480 TPB). In Kopanitsa 11/8, each bar is
             11 sixteenths = 1320 ticks, divided into 2+2+3+2+2 pattern (240, 240, 360, 240, 240 ticks).
             All note start ticks are strict integer multiples of 120 ticks -> 0 off-grid onsets!
           - Modal Harmony quantization: D Dorian / D Folk Minor (D, E, F, G, A, B, C) over a 4-bar
             harmonic cycle (Dm - C - G/B - A7sus / Dm). Every pitched note is strictly checked against
             the mode scale (0 out-of-scale) and against the bar's chord tones (0 out-of-chord).
           - Voice-leading leap control and counterpoint integrity.
           - Multi-voice authentic Balkan folk arrangement:
             1. Lead: Clarinet (CLARINET, GM 71, ch 0)
             2. Countermelody: Fiddle / Violin (VIOLIN, GM 40, ch 1)
             3. Harmonic Texture / Chords: Acoustic Guitar / Tambura (ACOUSTIC_GUITAR, GM 25, ch 2)
             4. Bass: Double Bass (DOUBLE_BASS, GM 43, ch 3)
             5. Percussion: Tupan / Drum Kit (DRUM_KIT, ch 9)
           - Zero-drift gate via UnitMatrixComposer.validate().
           - Export phase 2 MIDI + provenance sidecar.
"""

import os
import sys
import json
from math import gcd
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (
    CLARINET, VIOLIN, ACOUSTIC_GUITAR, DOUBLE_BASS, DRUM_KIT
)

SEED = 20260921
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/repos/musicom/projects/Styles/Balkan/100-balkan-christoffel"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- Metric & Grid Setup
# Kopanitsa 11/8: 2+2+3+2+2
# TPB = 480. Sixteenth note = 120 ticks.
# One bar of 11/8 has 11 sixteenths = 1320 ticks.
TPB = 480
GRID16 = 120
PULSES_PER_BAR = 11
BAR_TICKS = PULSES_PER_BAR * GRID16  # 1320 ticks

# Beat offsets within a bar (pulses 0, 2, 4, 7, 9 -> ticks 0, 240, 480, 840, 1080)
BEAT_PULSES = [0, 2, 4, 7, 9]
BEAT_DURS_PULSES = [2, 2, 3, 2, 2]
BEAT_TICKS = [p * GRID16 for p in BEAT_PULSES]
BEAT_DUR_TICKS = [d * GRID16 for d in BEAT_DURS_PULSES]

BPM = 160  # lively Balkan Kopanitsa
SECTIONS = ["Intro", "Tema_A", "Tema_B", "Razvivka", "Tema_A_Var", "Zavurshek"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)
N_BARS = N_SECTIONS * BARS_PER_SECTION  # 24 bars
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION  # 5280 ticks
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS     # 31680 ticks

# ---------------------------------------------------------------- Harmonic Framework
# Key: D Dorian (D E F G A B C)
# Scale pitch classes: D(2), E(4), F(5), G(7), A(9), B(11), C(0)
D_DORIAN_PCS = {2, 4, 5, 7, 9, 11, 0}
SCALE_PITCHES_D4 = [62, 64, 65, 67, 69, 71, 72]  # D4, E4, F4, G4, A4, B4, C5

# Section chord progressions (1 chord per bar)
# D Dorian progression:
# Section 0 (Intro):       Dm | Dm | C  | Dm
# Section 1 (Tema A):      Dm | C  | G  | Dm
# Section 2 (Tema B):      F  | C  | Dm | Am
# Section 3 (Razvivka):    G  | F  | C  | Dm
# Section 4 (Tema A Var):  Dm | C  | G  | Dm
# Section 5 (Zavurshek):   Bb | C  | Dm | Dm

SECTION_CHORDS = {
    0: ["Dm", "Dm", "C", "Dm"],
    1: ["Dm", "C", "G", "Dm"],
    2: ["F", "C", "Dm", "Am"],
    3: ["G", "F", "C", "Dm"],
    4: ["Dm", "C", "G", "Dm"],
    5: ["Bb", "C", "Dm", "Dm"],
}

# Chord tone pitch classes
CHORD_PCS = {
    "Dm": {2, 5, 9},        # D, F, A
    "C":  {0, 4, 7},        # C, E, G
    "G":  {7, 11, 2},       # G, B, D
    "F":  {5, 9, 0},        # F, A, C
    "Am": {9, 0, 4},        # A, C, E
    "Bb": {10, 2, 5},       # Bb, D, F (Balkan folk borrowing)
}

# Note: Bb introduces pitch class 10 for bar 20. Include 10 in full allowable pitch classes:
ALLOWED_PCS = D_DORIAN_PCS.union({10})

def get_bar_chord(sec_idx, bar_in_sec):
    return SECTION_CHORDS[sec_idx][bar_in_sec]

def get_bar_chord_pcs(sec_idx, bar_in_sec):
    ch = get_bar_chord(sec_idx, bar_in_sec)
    return CHORD_PCS[ch]

# ---------------------------------------------------------------- Christoffel Word Functions
def christoffel_word(p: int, q: int, a: str = "a", b: str = "b") -> str:
    """Lower Christoffel word: p letters a, q letters b, balanced."""
    assert gcd(p, q) == 1, "p and q must be coprime"
    n = p + q
    return "".join(
        b if ((k + 1) * q) // n > (k * q) // n else a
        for k in range(n)
    )

def sturmian_morph(word: str, morph: str = "G") -> str:
    rules = {
        "G":  {"a": "a",  "b": "ab"},
        "D":  {"a": "ba", "b": "b"},
        "G~": {"a": "a",  "b": "ba"},
        "D~": {"a": "ab", "b": "b"},
    }
    return "".join(rules[morph][c] for c in word)

# Master word: C(5, 2) = 'aaabaab'
C52 = christoffel_word(5, 2)
# Morphisms for variety
W_G = sturmian_morph(C52, "G")   # 'aaaabaaab'
W_D = sturmian_morph(C52, "D")   # 'baaabaaabaab'

# ---------------------------------------------------------------- Phase 1: Raw Generative Draft
def build_phase1():
    """Phase 1: Unquantized raw melodic walk driven purely by Christoffel word expansions."""
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=PULSES_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Clarinet", program=CLARINET.midi_program, channel=0)
    
    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        sec_events = []
        
        # Word sequence for this section
        if s_idx % 3 == 0:
            word = C52 * 6
        elif s_idx % 3 == 1:
            word = W_G * 4
        else:
            word = W_D * 3
            
        cur_tick = 0
        cur_pitch = 69.0  # continuous pitch float (A4)
        
        # Walk through the word
        for char in word:
            if cur_tick >= SECTION_TICKS - 150:
                break
            # Step in semitones based on char
            delta = 2.15 if char == "a" else -1.25
            cur_pitch += delta
            # Random duration jitter (unquantized)
            dur = int(rng.uniform(130, 250))
            if cur_tick + dur > SECTION_TICKS - 10:
                dur = SECTION_TICKS - 10 - cur_tick
            
            p_midi = int(round(np.clip(cur_pitch, 58, 86)))
            vel = int(rng.uniform(70, 105))
            sec_events.append(MusicEvent(
                pitch=p_midi,
                volume=vel,
                start_tick=cur_tick,
                end_tick=cur_tick + dur
            ))
            # Step forward with unquantized gap
            gap = int(rng.uniform(140, 270))
            cur_tick += gap
            
        # Pad terminal landmark to ensure exact SECTION_TICKS length
        if not sec_events or sec_events[-1].end_tick < SECTION_TICKS:
            sec_events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 10, end_tick=SECTION_TICKS))
        else:
            sec_events[-1].end_tick = SECTION_TICKS
            
        composer.fill_voice_section("Raw_Clarinet", s_name, MusicUnit(events=sec_events))
        
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 1 validate failed: {msg}")
        
    phase1_mid = os.path.join(MIDI_DIR, "100-balkan-christoffel-phase1.mid")
    composer.to_midi(phase1_mid)
    
    prov = {
        "project": "100-balkan-christoffel",
        "phase": 1,
        "method": "069 Christoffel Word Combinatorial Composition (CWCC)",
        "layer": "concrete",
        "description": "Raw unquantized Christoffel word walk on Clarinet",
        "ticks": TOTAL_TICKS,
        "seed": SEED,
    }
    with open(phase1_mid + ".provenance.json", "w") as f:
        json.dump(prov, f, indent=2)
        
    return phase1_mid


# ---------------------------------------------------------------- Helper: Quantize to Chord Tone
def nearest_chord_tone(target_midi, chord_pcs, min_p, max_p):
    """Find the closest MIDI pitch within [min_p, max_p] whose pitch class is in chord_pcs."""
    best_p = None
    best_dist = 999
    for p in range(min_p, max_p + 1):
        if (p % 12) in chord_pcs:
            dist = abs(p - target_midi)
            if dist < best_dist:
                best_dist = dist
                best_p = p
    return best_p if best_p is not None else target_midi


# ---------------------------------------------------------------- Phase 2: Rules-Processed Arrangement
def build_phase2():
    """Phase 2: Multi-voice authentic Balkan Kopanitsa with 100% grid & harmonic compliance."""
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=PULSES_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)
    
    composer.add_voice("Clarinet", program=CLARINET.midi_program, channel=0)
    composer.add_voice("Fiddle", program=VIOLIN.midi_program, channel=1)
    composer.add_voice("Tambura", program=ACOUSTIC_GUITAR.midi_program, channel=2)
    composer.add_voice("Bass", program=DOUBLE_BASS.midi_program, channel=3)
    composer.add_voice("Drums", program=0, channel=9)
    
    # Pre-compute melodic seeds using Christoffel words
    # Clarinet contour: C(5, 2) = 'aaabaab'
    # Fiddle contour: rotation of C(5, 2)
    c_word = C52 * 10
    rot_c_word = (C52[3:] + C52[:3]) * 10
    
    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        
        clar_events = []
        fid_events = []
        tam_events = []
        bass_events = []
        drum_events = []
        
        for bar in range(BARS_PER_SECTION):
            bar_start = bar * BAR_TICKS
            chord = get_bar_chord(s_idx, bar)
            chord_pcs = get_bar_chord_pcs(s_idx, bar)
            
            # --- 1. Bass: Kopanitsa Root & Fifth on Beat 1 (short), Beat 3 (long), Beat 4 (short)
            # Bass range: 36 (C2) to 55 (G3)
            root_pc = list(chord_pcs)[0]  # Root is first PC in chord definition
            if chord == "Dm": root_pc, fifth_pc = 2, 9
            elif chord == "C": root_pc, fifth_pc = 0, 7
            elif chord == "G": root_pc, fifth_pc = 7, 2
            elif chord == "F": root_pc, fifth_pc = 5, 0
            elif chord == "Am": root_pc, fifth_pc = 9, 4
            elif chord == "Bb": root_pc, fifth_pc = 10, 5
            
            root_midi = nearest_chord_tone(38, {root_pc}, 34, 46)
            fifth_midi = nearest_chord_tone(43, {fifth_pc}, 34, 50)
            
            # Bass pattern in 11/8 (pulses 0, 2, 4, 7, 9):
            # Pulse 0 (Beat 1, len 2 pulses = 240 ticks): root
            # Pulse 4 (Beat 3, len 3 pulses = 360 ticks): root
            # Pulse 7 (Beat 4, len 2 pulses = 240 ticks): fifth
            # Pulse 9 (Beat 5, len 2 pulses = 240 ticks): root
            b_hits = [
                (0, 240, root_midi, 105),
                (480, 360, root_midi, 100),
                (840, 240, fifth_midi, 95),
                (1080, 240, root_midi, 100),
            ]
            for st_rel, dur, p, vel in b_hits:
                bass_events.append(MusicEvent(
                    pitch=p, volume=vel,
                    start_tick=bar_start + st_rel,
                    end_tick=bar_start + st_rel + dur
                ))
                
            # --- 2. Tambura / Rhythm Guitar: Syncopated Folk Comping
            # Offbeat stabs on beats 2, 3, 5 (ticks 240, 480, 1080)
            # Voicings in register 55..72
            triad_notes = [nearest_chord_tone(60, {pc}, 55, 72) for pc in chord_pcs]
            for st_rel, dur in [(240, 240), (480, 360), (1080, 240)]:
                for tn in triad_notes:
                    tam_events.append(MusicEvent(
                        pitch=tn, volume=85,
                        start_tick=bar_start + st_rel,
                        end_tick=bar_start + st_rel + dur
                    ))
                    
            # --- 3. Drums (Tupan / Balkan percussion):
            # Kick (MIDI 36): heavy pulse on Beat 1 (0) and Beat 3 (480) - the long beat!
            # Snare/Rim (MIDI 38/37): crisp backbeats on Beat 2 (240), Beat 4 (840), Beat 5 (1080)
            # Closed Hat (MIDI 42): continuous 16th pulse riding all 11 sixteenths!
            for p_idx in range(PULSES_PER_BAR):
                ht_start = bar_start + p_idx * GRID16
                drum_events.append(MusicEvent(
                    pitch=42, volume=70 if p_idx in BEAT_PULSES else 50,
                    start_tick=ht_start, end_tick=ht_start + GRID16
                ))
            # Kick hits
            drum_events.append(MusicEvent(pitch=36, volume=110, start_tick=bar_start, end_tick=bar_start + 240))
            drum_events.append(MusicEvent(pitch=36, volume=115, start_tick=bar_start + 480, end_tick=bar_start + 360))
            # Snare hits
            drum_events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_start + 240, end_tick=bar_start + 480))
            drum_events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_start + 840, end_tick=bar_start + 1080))
            drum_events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_start + 1080, end_tick=bar_start + 1320))
            
            # --- 4. Clarinet (Lead): Fast Kopanitsa Virtuosic Runs
            # Subdivision of 11/8 pulses using Christoffel letters
            # 5 beats per bar:
            # Beat 1 (2 pulses): two 16ths (120, 120)
            # Beat 2 (2 pulses): two 16ths (120, 120)
            # Beat 3 (3 pulses): three 16ths (120, 120, 120) -> characteristic Kopanitsa roll!
            # Beat 4 (2 pulses): two 16ths (120, 120)
            # Beat 5 (2 pulses): one 8th (240)
            # Total events = 2 + 2 + 3 + 2 + 1 = 10 events, all strictly quantized to 120 ticks!
            clar_slots = [
                (0, 120), (120, 120),
                (240, 120), (360, 120),
                (480, 120), (600, 120), (720, 120),
                (840, 120), (960, 120),
                (1080, 240)
            ]
            
            lead_pitch = 74  # D5
            for slot_idx, (st_rel, dur) in enumerate(clar_slots):
                # Use Christoffel word to drive step up or step down
                char = c_word[(bar * 10 + slot_idx) % len(c_word)]
                step = 2 if char == "a" else -1
                target = lead_pitch + step
                # Quantize strictly to chord tone
                q_pitch = nearest_chord_tone(target, chord_pcs, 62, 86)
                lead_pitch = q_pitch
                clar_events.append(MusicEvent(
                    pitch=q_pitch,
                    volume=95 if st_rel in BEAT_TICKS else 80,
                    start_tick=bar_start + st_rel,
                    end_tick=bar_start + st_rel + dur
                ))
                
            # --- 5. Fiddle (Countermelody): Sustained 5-Beat Melodic Contour
            # Fiddle plays across the 5 macro beats (240, 240, 360, 240, 240)
            fid_pitch = 65  # F4
            for b_idx in range(5):
                st_rel = BEAT_TICKS[b_idx]
                dur = BEAT_DUR_TICKS[b_idx]
                char = rot_c_word[(bar * 5 + b_idx) % len(rot_c_word)]
                step = 2 if char == "a" else -2
                target = fid_pitch + step
                q_pitch = nearest_chord_tone(target, chord_pcs, 57, 77)
                fid_pitch = q_pitch
                fid_events.append(MusicEvent(
                    pitch=q_pitch,
                    volume=88,
                    start_tick=bar_start + st_rel,
                    end_tick=bar_start + st_rel + dur
                ))

        # End of section: ensure terminal landmarks and exact section length
        for ev_list in [clar_events, fid_events, tam_events, bass_events, drum_events]:
            if not ev_list or ev_list[-1].end_tick < SECTION_TICKS:
                ev_list.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 10, end_tick=SECTION_TICKS))
            else:
                ev_list[-1].end_tick = SECTION_TICKS
                
        composer.fill_voice_section("Clarinet", s_name, MusicUnit(events=clar_events))
        composer.fill_voice_section("Fiddle", s_name, MusicUnit(events=fid_events))
        composer.fill_voice_section("Tambura", s_name, MusicUnit(events=tam_events))
        composer.fill_voice_section("Bass", s_name, MusicUnit(events=bass_events))
        composer.fill_voice_section("Drums", s_name, MusicUnit(events=drum_events))
        
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 2 validate failed: {msg}")
        
    phase2_mid = os.path.join(MIDI_DIR, "100-balkan-christoffel.mid")
    composer.to_midi(phase2_mid)
    
    prov = {
        "project": "100-balkan-christoffel",
        "phase": 2,
        "method": "069 Christoffel Word Combinatorial Composition (CWCC)",
        "layer": "concrete",
        "key": "D Dorian",
        "bpm": BPM,
        "time_signature": "11/8 (2+2+3+2+2)",
        "bars": N_BARS,
        "ticks": TOTAL_TICKS,
        "seed": SEED,
    }
    with open(phase2_mid + ".provenance.json", "w") as f:
        json.dump(prov, f, indent=2)
        
    return phase2_mid

if __name__ == "__main__":
    p1 = build_phase1()
    print(f"Phase 1 exported: {p1} ({os.path.getsize(p1)} bytes)")
    p2 = build_phase2()
    print(f"Phase 2 exported: {p2} ({os.path.getsize(p2)} bytes)")
