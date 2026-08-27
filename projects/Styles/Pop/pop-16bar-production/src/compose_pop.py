"""
16-bar Pop Composition using musicom engine.
Methods: Markov (melody), Euclidean (drums), Tendency Masking (bass), Weighted Random (chords)
Structure: Verse1 (4 bars) → Chorus (4 bars) → Verse2 (4 bars) → Chorus (4 bars)
Key: C major. Progression: I-V-vi-IV (C-G-Am-F)
"""

import os
import numpy as np
import random

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from sound.generators.event_core import (
    EuclideanCore, MarkovCore, StochasticCore, WeightedRandomCore
)
from visualization.grid import write_grid_visualization

# ── Constants ──
BPM = 120
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920
SECTION_BARS = 4
SECTION_TICKS = BAR_TICKS * SECTION_BARS  # 7680

# ── Harmony ──
CHORD_TONES = {
    'C':  [60, 64, 67],
    'G':  [55, 59, 62],
    'Am': [57, 60, 64],
    'F':  [53, 57, 60],
}

SCALE = {
    'C':  [60, 62, 64, 65, 67, 69, 71, 72],
    'G':  [55, 57, 59, 60, 62, 64, 65, 67],
    'Am': [57, 59, 60, 62, 64, 65, 67, 69],
    'F':  [53, 55, 57, 59, 60, 62, 64, 65],
}

PROGRESSION = ['C', 'G', 'Am', 'F']  # I-V-vi-IV

# ── Generative Methods ──

def gen_markov_melody(seed=42):
    """Method 002: Markov chain for melody. Stepwise bias, occasional leaps."""
    random.seed(seed)
    scale = SCALE['C']  # Use C major for all, quantize to chord tones later
    
    transitions = {}
    for i, note in enumerate(scale):
        transitions[note] = {}
        if i < len(scale) - 1:
            transitions[note][scale[i+1]] = 0.35
        if i > 0:
            transitions[note][scale[i-1]] = 0.30
        transitions[note][note] = 0.15
        if i < len(scale) - 2:
            transitions[note][scale[i+2]] = 0.10
        if i > 1:
            transitions[note][scale[i-2]] = 0.10
    
    markov = MarkovCore(transitions)
    # 16 bars × 4 beats = 64 quarter notes
    return markov.generate(64, seed=scale[0])

def gen_euclidean_drums(seed=42):
    """Method 011: Euclidean rhythms for drums."""
    random.seed(seed)
    # Kick: E(4,16) = four-on-the-floor
    kick = EuclideanCore(pulses=4, steps=16)
    kick_pat = kick.generate(256)  # 16 bars × 16 steps
    
    # Snare: E(2,8) rotated for backbeat (beats 2,4)
    snare = EuclideanCore(pulses=2, steps=8, rotation=4)
    snare_pat = snare.generate(128)  # 16 bars × 8 steps
    
    # Hi-hat: E(7,16) = busy groove
    hat = EuclideanCore(pulses=7, steps=16)
    hat_pat = hat.generate(256)  # 16 bars × 16 steps
    
    return kick_pat, snare_pat, hat_pat

def gen_tendency_bass(seed=42):
    """Method 023: Tendency masking for bass line."""
    random.seed(seed)
    # Bass walks around root with tendency back
    bass = StochasticCore(
        value_range=(36, 55),  # Low register
        max_step=7,
        tendency_target=48,  # C3
        tendency_strength=0.5
    )
    # 16 bars × 2 beats = 32 half notes
    return bass.generate(32, seed=48)

def gen_weighted_chords(seed=42):
    """Weighted random for chord voicing selection per bar."""
    random.seed(seed)
    pool = {'root': 0.5, 'first_inv': 0.3, 'second_inv': 0.2}
    wr = WeightedRandomCore(pool, avoid_repeats=1)
    return wr.generate(16)  # 16 bars

def quantize_to_chord(pitch, chord_name):
    """Quantize melody note to nearest chord tone."""
    tones = CHORD_TONES[chord_name]
    # Also include octave-up versions
    all_tones = tones + [t + 12 for t in tones]
    best = min(all_tones, key=lambda t: abs(t - pitch))
    return best

# ── Build MusicUnits ──

def build_melody_unit(melody_notes, section_idx):
    """Build melody MusicUnit for one section (4 bars).

    NOTE: events inside a cell are LOCAL to the cell (0..SECTION_TICKS).
    The matrix aligner offsets them by cumulative section lengths.
    """
    unit = MusicUnit()
    note_ticks = BAR_TICKS // 4  # quarter note = 480 ticks
    
    for bar in range(4):
        chord = PROGRESSION[bar]
        for beat in range(4):
            idx = section_idx * 16 + bar * 4 + beat
            raw_pitch = melody_notes[idx]
            pitch = quantize_to_chord(raw_pitch, chord)
            # Keep in reasonable range
            pitch = max(60, min(79, pitch))
            
            start = bar * BAR_TICKS + beat * note_ticks
            unit.add_event(MusicEvent(
                pitch=pitch,
                volume=85,
                start_tick=start,
                end_tick=start + note_ticks
            ))
    
    return unit

def build_chord_unit(voicings, section_idx):
    """Build chord MusicUnit for one section (4 bars, one chord per bar)."""
    unit = MusicUnit()
    
    for bar in range(4):
        chord = PROGRESSION[bar]
        tones = CHORD_TONES[chord]
        voicing = voicings[section_idx * 4 + bar]
        
        if voicing == 'first_inv':
            tones = [tones[1], tones[2], tones[0] + 12]
        elif voicing == 'second_inv':
            tones = [tones[2], tones[0] + 12, tones[1] + 12]
        
        start = bar * BAR_TICKS
        for pitch in tones:
            unit.add_event(MusicEvent(
                pitch=pitch,
                volume=70,
                start_tick=start,
                end_tick=start + BAR_TICKS
            ))
    
    return unit

def build_bass_unit(bass_notes, section_idx):
    """Build bass MusicUnit for one section (4 bars, 2 notes per bar)."""
    unit = MusicUnit()
    note_ticks = BAR_TICKS // 2  # half note = 960 ticks
    
    for bar in range(4):
        chord = PROGRESSION[bar]
        root = CHORD_TONES[chord][0]
        
        for beat in range(2):
            idx = section_idx * 8 + bar * 2 + beat
            raw_pitch = bass_notes[idx]
            # Quantize to root or fifth of chord
            fifth = root + 7
            best = min([root, fifth, root - 12], key=lambda t: abs(t - raw_pitch))
            best = max(36, min(55, best))
            
            start = bar * BAR_TICKS + beat * note_ticks
            unit.add_event(MusicEvent(
                pitch=best,
                volume=95,
                start_tick=start,
                end_tick=start + note_ticks
            ))
    
    return unit

def build_drum_unit(kick_pat, snare_pat, hat_pat, section_idx):
    """Build drum MusicUnit for one section (4 bars)."""
    unit = MusicUnit()
    step16 = BAR_TICKS // 16  # 120 ticks per 16th
    step8 = BAR_TICKS // 8    # 240 ticks per 8th
    
    for bar in range(4):
        bar_offset = bar * BAR_TICKS
        
        # Kick: 16th note grid
        for i in range(16):
            idx = section_idx * 64 + bar * 16 + i
            if kick_pat[idx]:
                start = bar_offset + i * step16
                unit.add_event(MusicEvent(
                    pitch=MidiPercussion.BASS_DRUM,
                    volume=100,
                    start_tick=start,
                    end_tick=start + step16
                ))
        
        # Snare: 8th note grid
        for i in range(8):
            idx = section_idx * 32 + bar * 8 + i
            if snare_pat[idx]:
                start = bar_offset + i * step8
                unit.add_event(MusicEvent(
                    pitch=MidiPercussion.ACOUSTIC_SNARE,
                    volume=90,
                    start_tick=start,
                    end_tick=start + step8
                ))
        
        # Hi-hat: 16th note grid
        for i in range(16):
            idx = section_idx * 64 + bar * 16 + i
            if hat_pat[idx]:
                start = bar_offset + i * step16
                unit.add_event(MusicEvent(
                    pitch=MidiPercussion.CLOSED_HI_HAT,
                    volume=65,
                    start_tick=start,
                    end_tick=start + step16
                ))
    
    return unit

# ── Main ──

def compose():
    """Compose 16-bar pop song."""
    print("=== 16-Bar Pop Composition ===")
    print(f"BPM: {BPM} | Key: C major | Progression: I-V-vi-IV")
    print(f"Methods: Markov(002) + Euclidean(011) + Tendency(023) + WeightedRandom")
    
    # Generate materials
    melody = gen_markov_melody(seed=42)
    kick, snare, hat = gen_euclidean_drums(seed=42)
    bass = gen_tendency_bass(seed=42)
    voicings = gen_weighted_chords(seed=42)
    
    # Build composer
    composer = UnitMatrixComposer(
        bpm=BPM,
        ticks_per_beat=TICKS_PER_BEAT,
        beats_per_bar=BEATS_PER_BAR
    )
    composer.create_matrix(num_voices=4, num_sections=4)
    
    composer.add_voice("Melody", program=MidiInstrument.FLUTE, channel=0)
    composer.add_voice("Chords", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    composer.add_voice("Drums", program=0, channel=9)
    
    composer.add_section("Verse1", bars=4)
    composer.add_section("Chorus1", bars=4)
    composer.add_section("Verse2", bars=4)
    composer.add_section("Chorus2", bars=4)
    
    # Fill matrix
    for s in range(4):
        names = ['Verse1', 'Chorus1', 'Verse2', 'Chorus2']
        melody_unit = build_melody_unit(melody, s)
        chord_unit = build_chord_unit(voicings, s)
        bass_unit = build_bass_unit(bass, s)
        drum_unit = build_drum_unit(kick, snare, hat, s)
        
        col = s
        composer.set_unit(0, col, melody_unit)
        composer.set_unit(1, col, chord_unit)
        composer.set_unit(2, col, bass_unit)
        composer.set_unit(3, col, drum_unit)
        
        print(f"  {names[s]}: melody={len(melody_unit.data)} events, "
              f"chords={len(chord_unit.data)}, bass={len(bass_unit.data)}, "
              f"drums={len(drum_unit.data)}")
    
    # Validate
    ok, msg = composer.validate()
    print(f"\nValidation: {msg}")
    assert ok, f"Validation failed: {msg}"
    
    # Export
    base = '/opt/data/projects/Styles/Pop/pop-16bar-production'
    midi_path = os.path.join(base, 'MIDI', 'pop_16bar.mid')
    composer.to_midi(midi_path)
    
    size = os.path.getsize(midi_path)
    print(f"✓ MIDI: {midi_path} ({size} bytes)")
    assert size > 40, "Empty MIDI!"
    
    # Grid visualization
    grid_path = os.path.join(base, 'Analysis', 'grid_visualization.txt')
    write_grid_visualization(composer.matrix, grid_path, voice_names=[
        "Melody", "Chords", "Bass", "Drums"
    ], bpm=BPM)
    print(f"✓ Grid: {grid_path}")
    
    return midi_path

if __name__ == '__main__':
    compose()
