"""
16-bar Pop Composition using the musicom engine.

Methods (canonical master-map):
- Method 002  Markov Transitions      → melody (stepwise-biased chain over C major)
- Method 011  Euclidean Groove        → drums (kick E(4,16), snare E(2,8)@backbeat, hat E(7,16))
- Method 023  Tendency Masking        → bass (constrained random walk toward root)
- Weighted Random Selection           → chord voicings (root / 1st inv / 2nd inv)

Structure: Verse1 (4 bars) → Chorus (4 bars) → Verse2 (4 bars) → Chorus (4 bars)
Key: C major. Progression: I-V-vi-IV (C-G-Am-F). BPM 120, 480 ticks/beat.

Usage (script):  python examples/compose_pop_16bar.py [output_dir]
Usage (import):  from examples.compose_pop_16bar import build_pop_composer
"""

import os
import sys
import random

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from sound.generators.event_core import (
    EuclideanCore, MarkovCore, StochasticCore, WeightedRandomCore,
)
from visualization.grid import write_grid_visualization

# ── Constants ──
BPM = 120
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR   # 1920
SECTION_BARS = 4
SECTION_TICKS = BAR_TICKS * SECTION_BARS     # 7680

# I-V-vi-IV in C major
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
PROGRESSION = ['C', 'G', 'Am', 'F']

SECTION_NAMES = ['Verse1', 'Chorus1', 'Verse2', 'Chorus2']


# ── Generative methods (Phase 1: raw drafts) ──

def gen_markov_melody(seed=42):
    """Method 002: Markov chain, stepwise bias + occasional 2nd-order leaps."""
    random.seed(seed)
    scale = SCALE['C']
    transitions = {}
    for i, note in enumerate(scale):
        transitions[note] = {}
        if i < len(scale) - 1:
            transitions[note][scale[i + 1]] = 0.35
        if i > 0:
            transitions[note][scale[i - 1]] = 0.30
        transitions[note][note] = 0.15
        if i < len(scale) - 2:
            transitions[note][scale[i + 2]] = 0.10
        if i > 1:
            transitions[note][scale[i - 2]] = 0.10
    markov = MarkovCore(transitions)
    return markov.generate(64, seed=scale[0])  # 16 bars × 4 quarter notes


def gen_euclidean_drums(seed=42):
    """Method 011: Euclidean rhythms for kick/snare/hat."""
    random.seed(seed)
    kick = EuclideanCore(pulses=4, steps=16)                    # four-on-the-floor
    snare = EuclideanCore(pulses=2, steps=8, rotation=4)        # backbeat 2 & 4
    hat = EuclideanCore(pulses=7, steps=16)                     # busy groove
    return kick.generate(256), snare.generate(128), hat.generate(256)


def gen_tendency_bass(seed=42):
    """Method 023: tendency-masked random walk toward the root register."""
    random.seed(seed)
    bass = StochasticCore(
        value_range=(36, 55),
        max_step=7,
        tendency_target=48,
        tendency_strength=0.5,
    )
    return bass.generate(32, seed=48)  # 16 bars × 2 half notes


def gen_weighted_voicings(seed=42):
    """Weighted-random chord voicing selection, no immediate repeats."""
    random.seed(seed)
    wr = WeightedRandomCore(
        {'root': 0.5, 'first_inv': 0.3, 'second_inv': 0.2},
        avoid_repeats=1,
    )
    return wr.generate(16)  # one per bar


def quantize_to_chord(pitch, chord_name):
    """Phase-2 quantization: nearest chord tone (incl. octave up)."""
    tones = CHORD_TONES[chord_name] + [t + 12 for t in CHORD_TONES[chord_name]]
    return min(tones, key=lambda t: abs(t - pitch))


# ── Build MusicUnits (cell-local ticks 0..SECTION_TICKS) ──

def build_melody_unit(melody_notes, section_idx):
    """Melody cell: 16 quarter notes. Cell events are LOCAL (aligner offsets them)."""
    unit = MusicUnit()
    note_ticks = BAR_TICKS // 4
    for bar in range(4):
        chord = PROGRESSION[bar]
        for beat in range(4):
            idx = section_idx * 16 + bar * 4 + beat
            pitch = quantize_to_chord(melody_notes[idx], chord)
            pitch = max(60, min(79, pitch))
            start = bar * BAR_TICKS + beat * note_ticks
            unit.add_event(MusicEvent(pitch, 85, start, start + note_ticks))
    return unit


def build_chord_unit(voicings, section_idx):
    """Chord cell: 1 voicing per bar, whole-note sustained (continuous layer)."""
    unit = MusicUnit()
    for bar in range(4):
        chord = PROGRESSION[bar]
        tones = list(CHORD_TONES[chord])
        voicing = voicings[section_idx * 4 + bar]
        if voicing == 'first_inv':
            tones = [tones[1], tones[2], tones[0] + 12]
        elif voicing == 'second_inv':
            tones = [tones[2], tones[0] + 12, tones[1] + 12]
        start = bar * BAR_TICKS
        for pitch in tones:
            unit.add_event(MusicEvent(pitch, 70, start, start + BAR_TICKS))
    return unit


def build_bass_unit(bass_notes, section_idx):
    """Bass cell: 2 half notes per bar, quantized to root or fifth."""
    unit = MusicUnit()
    note_ticks = BAR_TICKS // 2
    for bar in range(4):
        root = CHORD_TONES[PROGRESSION[bar]][0]
        for beat in range(2):
            idx = section_idx * 8 + bar * 2 + beat
            raw = bass_notes[idx]
            best = min([root, root + 7, root - 12], key=lambda t: abs(t - raw))
            best = max(36, min(55, best))
            start = bar * BAR_TICKS + beat * note_ticks
            unit.add_event(MusicEvent(best, 95, start, start + note_ticks))
    return unit


def build_drum_unit(kick_pat, snare_pat, hat_pat, section_idx):
    """Drum cell: Euclidean kick/snare/hat across 4 bars."""
    unit = MusicUnit()
    step16 = BAR_TICKS // 16
    step8 = BAR_TICKS // 8
    for bar in range(4):
        bar_offset = bar * BAR_TICKS
        for i in range(16):
            if kick_pat[section_idx * 64 + bar * 16 + i]:
                start = bar_offset + i * step16
                unit.add_event(MusicEvent(MidiPercussion.BASS_DRUM, 100, start, start + step16))
        for i in range(8):
            if snare_pat[section_idx * 32 + bar * 8 + i]:
                start = bar_offset + i * step8
                unit.add_event(MusicEvent(MidiPercussion.ACOUSTIC_SNARE, 90, start, start + step8))
        for i in range(16):
            if hat_pat[section_idx * 64 + bar * 16 + i]:
                start = bar_offset + i * step16
                unit.add_event(MusicEvent(MidiPercussion.CLOSED_HI_HAT, 65, start, start + step16))
    return unit


# ── Composition builder ──

def build_pop_composer(seed=42):
    """Build the 4-voice, 4-section (16-bar) pop UnitMatrixComposer."""
    melody = gen_markov_melody(seed)
    kick, snare, hat = gen_euclidean_drums(seed)
    bass = gen_tendency_bass(seed)
    voicings = gen_weighted_voicings(seed)

    composer = UnitMatrixComposer(
        bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR,
    )
    composer.create_matrix(num_voices=4, num_sections=4)
    composer.add_voice("Melody", program=MidiInstrument.FLUTE, channel=0)
    composer.add_voice("Chords", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    composer.add_voice("Drums", program=0, channel=9)
    for name in SECTION_NAMES:
        composer.add_section(name, bars=4)

    for s in range(4):
        composer.set_unit(0, s, build_melody_unit(melody, s))
        composer.set_unit(1, s, build_chord_unit(voicings, s))
        composer.set_unit(2, s, build_bass_unit(bass, s))
        composer.set_unit(3, s, build_drum_unit(kick, snare, hat, s))

    ok, msg = composer.validate()
    if not ok:
        raise ValueError(f"Zero-drift validation failed: {msg}")
    return composer


def compose_to(project_dir):
    """Compose and export MIDI + grid visualization into project_dir."""
    os.makedirs(os.path.join(project_dir, 'MIDI'), exist_ok=True)
    os.makedirs(os.path.join(project_dir, 'Analysis'), exist_ok=True)

    composer = build_pop_composer()
    midi_path = os.path.join(project_dir, 'MIDI', 'pop_16bar.mid')
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40, "Empty MIDI!"

    grid_path = os.path.join(project_dir, 'Analysis', 'grid_visualization.txt')
    write_grid_visualization(
        composer.matrix, grid_path,
        voice_names=["Melody", "Chords", "Bass", "Drums"], bpm=BPM,
    )
    return midi_path, grid_path


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/opt/data/projects/Styles/Pop/pop-16bar-production'
    midi, grid = compose_to(out)
    print(f"✓ MIDI: {midi} ({os.path.getsize(midi)} bytes)")
    print(f"✓ Grid: {grid}")
