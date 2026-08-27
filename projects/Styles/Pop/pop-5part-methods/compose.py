# -*- coding: utf-8 -*-
"""
Pop 5-part composition — Phase 1 (framework + per-section method variation).

Framework (Method 001 Skeleton-First): key C major, 120 BPM, 4/4,
progression I-V-vi-IV (C-G-Am-F), 5 voices (Melody, Pad, Bass, Arp, Drums).

Each SECTION uses a DIFFERENT generative method but stays inside the same
framework (same key, same progression, same voice roles, same density target):
  Intro   -> Tendency Masking (023) sparse melody + sustained pad
  Verse   -> Markov (002) melody + Euclidean (011) drums + tendency bass
  Chorus  -> DPSM phase-shift (026) arp + inversion-heavy chords (lift)
  Bridge  -> Isorhythmic talea-color (032) melody + sustained pad
  Outro   -> Schillinger resultant (018) rhythm + progressive dropout

All cell events are CELL-LOCAL (0..SECTION_TICKS). Zero-drift enforced by
UnitMatrixComposer.validate().
"""

import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from sound.generators.event_core import (
    EuclideanCore, MarkovCore, StochasticCore, WeightedRandomCore,
)
from generators.schillinger import SchillingerGenerator
from generators.tintinnabuli import isorhythmize
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

BPM = 120
TPB = 480
BPB = 4
BAR = TPB * BPB          # 1920

# Section bar counts (form)
SECTION_BARS = {
    "Intro": 4,
    "Verse": 8,
    "Chorus": 8,
    "Bridge": 4,
    "Outro": 4,
}
SECTION_NAMES = ["Intro", "Verse", "Chorus", "Bridge", "Outro"]

# Chord tones (C major, I-V-vi-IV)
CHORD_TONES = {
    'C':  [60, 64, 67],
    'G':  [55, 59, 62],
    'Am': [57, 60, 64],
    'F':  [53, 57, 60],
}
# Per-section progression (all stay on I-V-vi-IV family)
PROGRESSIONS = {
    "Intro":  ['C', 'G', 'Am', 'F'],
    "Verse":  ['C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F'],
    "Chorus": ['C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F'],
    "Bridge": ['Am', 'F', 'C', 'G'],
    "Outro":  ['C', 'G', 'Am', 'F'],
}

C_MAJOR = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79]


def _chord_tones(chord, octave_shift=0):
    return [t + 12 * octave_shift for t in CHORD_TONES[chord]]


def quantize_to_chord(pitch, chord):
    tones = CHORD_TONES[chord] + [t + 12 for t in CHORD_TONES[chord]] + [t - 12 for t in CHORD_TONES[chord]]
    return min(tones, key=lambda t: abs(t - pitch))


# ---------------------------------------------------------------- melody

def _melody_markov(section, bars, seed):
    """Method 002: stepwise-biased Markov over C major."""
    random.seed(seed)
    scale = C_MAJOR
    trans = {}
    for i, n in enumerate(scale):
        trans[n] = {}
        if i < len(scale) - 1:
            trans[n][scale[i + 1]] = 0.35
        if i > 0:
            trans[n][scale[i - 1]] = 0.30
        trans[n][n] = 0.15
        if i < len(scale) - 2:
            trans[n][scale[i + 2]] = 0.10
        if i > 1:
            trans[n][scale[i - 2]] = 0.10
    mc = MarkovCore(trans)
    return mc.generate(bars * 4, seed=scale[0])


def _melody_tendency(section, bars, seed):
    """Method 023: tendency-masked walk toward center register."""
    random.seed(seed)
    st = StochasticCore(value_range=(60, 79), max_step=4,
                        tendency_target=69, tendency_strength=0.6)
    return st.generate(bars * 4, seed=67)


def _melody_isorhythm(section, bars, seed):
    """Method 032: isorhythmic talea-color melody."""
    random.seed(seed)
    color = [0, 4, 7, 5, 2, 4, 7, 9]     # semitone offsets (C major-ish)
    talea = [1.0, 0.5, 0.5, 1.0, 0.5, 0.5, 1.0, 0.5]
    unit = isorhythmize(color, talea, ticks_per_beat=TPB, start_pitch=60, volume=88)
    return unit


# ---------------------------------------------------------------- builders

def build_melody(section, section_idx):
    bars = SECTION_BARS[section]
    prog = PROGRESSIONS[section]
    unit = MusicUnit()
    note_ticks = BAR // 4  # quarter note

    if section == "Intro":
        # Tendency masking, sparse (half-note density) -> gentle entrance
        random.seed(100 + section_idx)
        st = StochasticCore(value_range=(64, 79), max_step=3,
                            tendency_target=72, tendency_strength=0.5)
        notes = st.generate(bars * 4, seed=67)
        for bar in range(bars):
            chord = prog[bar]
            for beat in range(4):
                if beat % 2 == 0:  # half-note density
                    idx = bar * 4 + beat
                    p = quantize_to_chord(notes[idx], chord)
                    p = max(64, min(79, p))
                    start = bar * BAR + beat * note_ticks
                    unit.add_event(MusicEvent(p, 80, start, start + note_ticks * 2))

    elif section == "Verse":
        notes = _melody_markov(section, bars, 200 + section_idx)
        for bar in range(bars):
            chord = prog[bar]
            for beat in range(4):
                idx = bar * 4 + beat
                p = quantize_to_chord(notes[idx], chord)
                p = max(60, min(79, p))
                start = bar * BAR + beat * note_ticks
                unit.add_event(MusicEvent(p, 85, start, start + note_ticks))

    elif section == "Chorus":
        notes = _melody_markov(section, bars, 300 + section_idx)
        for bar in range(bars):
            chord = prog[bar]
            for beat in range(4):
                idx = bar * 4 + beat
                p = quantize_to_chord(notes[idx], chord)
                p = max(67, min(84, p))   # lift: higher register
                start = bar * BAR + beat * note_ticks
                unit.add_event(MusicEvent(p, 92, start, start + note_ticks))

    elif section == "Bridge":
        # Isorhythmic talea-color, snapped to chord
        iso = _melody_isorhythm(section, bars, 400 + section_idx)
        tick = 0
        bar = 0
        for e in iso.events:
            if e.pitch == 0:
                continue
            chord = prog[min(bar, bars - 1)]
            p = quantize_to_chord(e.pitch, chord)
            p = max(60, min(79, p))
            start = e.start_tick
            end = min(e.end_tick, bars * BAR)
            if end > start:
                unit.add_event(MusicEvent(p, 82, start, end))
            bar = min(bars - 1, start // BAR)

    elif section == "Outro":
        # Schillinger resultant rhythm, dropout-friendly (sparse)
        sch = SchillingerGenerator(generator_a=3, generator_b=2)
        durations = sch.generate_resultant()
        tick = 0
        bar = 0
        i = 0
        while tick < bars * BAR and i < len(durations) * 4:
            chord = prog[min(bar, bars - 1)]
            dur = durations[i % len(durations)] * 120
            p = quantize_to_chord(67 + (i % 3) * 2, chord)
            p = max(60, min(79, p))
            end = min(tick + dur, bars * BAR)
            if end > tick:
                unit.add_event(MusicEvent(p, 78, tick, end))
            tick += dur
            bar = min(bars - 1, tick // BAR)
            i += 1

    # zero-drift terminal landmark
    if len(unit.data) == 0 or unit.len_ticks() < bars * BAR:
        last = unit.len_ticks() if len(unit.data) else 0
        unit.add_event(MusicEvent(0, 0, last, bars * BAR))
    return unit


def build_pad(section, section_idx):
    """Sustained whole-bar chords (continuous 100% layer)."""
    bars = SECTION_BARS[section]
    prog = PROGRESSIONS[section]
    unit = MusicUnit()
    for bar in range(bars):
        chord = prog[bar]
        tones = list(CHORD_TONES[chord])
        # voicing: chorus = inversion-heavy (lift)
        if section == "Chorus":
            tones = [tones[1], tones[2], tones[0] + 12]
        elif section == "Bridge":
            tones = [tones[2], tones[0] + 12, tones[1] + 12]
        start = bar * BAR
        for p in tones:
            unit.add_event(MusicEvent(p, 68, start, start + BAR))
    return unit


def build_bass(section, section_idx):
    """Bass: tendency-masked walk, half notes, root/fifth quantized."""
    bars = SECTION_BARS[section]
    prog = PROGRESSIONS[section]
    unit = MusicUnit()
    random.seed(500 + section_idx)
    st = StochasticCore(value_range=(36, 55), max_step=7,
                         tendency_target=48, tendency_strength=0.5)
    notes = st.generate(bars * 2, seed=48)
    note_ticks = BAR // 2
    for bar in range(bars):
        root = CHORD_TONES[prog[bar]][0]
        for beat in range(2):
            idx = bar * 2 + beat
            raw = notes[idx]
            best = min([root, root + 7, root - 12], key=lambda t: abs(t - raw))
            best = max(36, min(55, best))
            start = bar * BAR + beat * note_ticks
            unit.add_event(MusicEvent(best, 95, start, start + note_ticks))
    return unit


def build_arp(section, section_idx):
    """Method 026 DPSM: continuous 16th-note arpeggio cycling chord tones."""
    bars = SECTION_BARS[section]
    prog = PROGRESSIONS[section]
    unit = MusicUnit()
    step16 = BAR // 16
    if section in ("Intro", "Outro"):
        # sparse arp (eighth notes) for head/tail
        step = BAR // 8
        for bar in range(bars):
            chord = prog[bar]
            tones = CHORD_TONES[chord] + [t + 12 for t in CHORD_TONES[chord]]
            for i in range(8):
                start = bar * BAR + i * step
                p = tones[i % len(tones)]
                unit.add_event(MusicEvent(p, 70, start, start + step))
    else:
        for bar in range(bars):
            chord = prog[bar]
            tones = CHORD_TONES[chord] + [t + 12 for t in CHORD_TONES[chord]]
            for i in range(16):
                start = bar * BAR + i * step16
                p = tones[i % len(tones)]
                unit.add_event(MusicEvent(p, 72, start, start + step16))
    return unit


def build_drums(section, section_idx):
    """Euclidean-aligned drums, locked to the 16th-note grid.

    CRITICAL: The Bjorklund bucket algorithm in EuclideanCore shifts onsets
    off the beat. For pop, we need explicit beat-aligned patterns:
      kick  = beats 1,2,3,4  → ticks 0, 480, 960, 1440
      snare = beats 2,4      → ticks 480, 1440
      hat   = 8th notes      → ticks 0,240,480,...,1680

    Intro = hat-only build-in. Outro = progressive dropout.
    """
    bars = SECTION_BARS[section]
    unit = MusicUnit()
    step16 = BAR // 16   # 120 ticks
    step8 = BAR // 8     # 240 ticks

    # Explicit beat-aligned patterns per bar (16 steps = 16th notes)
    # kick:  beats 1,2,3,4 → indices 0,4,8,12
    # snare: beats 2,4     → indices 4,12
    # hat:   8th notes     → indices 0,2,4,6,8,10,12,14
    kick_bar  = [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0]
    snare_bar = [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0]
    hat_bar   = [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0]

    if section == "Intro":
        # bars 0-1 silent, bars 2-3 hat only
        for bar in range(bars):
            if bar >= 2:
                for i in range(16):
                    if hat_bar[i]:
                        start = bar * BAR + i * step16
                        unit.add_event(MusicEvent(MidiPercussion.CLOSED_HI_HAT, 60, start, start + step16))
    elif section == "Outro":
        # dropout: drums only bars 0-1
        for bar in range(min(2, bars)):
            for i in range(16):
                if kick_bar[i]:
                    start = bar * BAR + i * step16
                    unit.add_event(MusicEvent(MidiPercussion.BASS_DRUM, 95, start, start + step16))
            for i in range(16):
                if snare_bar[i]:
                    start = bar * BAR + i * step16
                    unit.add_event(MusicEvent(MidiPercussion.ACOUSTIC_SNARE, 85, start, start + step16))
            for i in range(16):
                if hat_bar[i]:
                    start = bar * BAR + i * step16
                    unit.add_event(MusicEvent(MidiPercussion.CLOSED_HI_HAT, 60, start, start + step16))
    else:
        for bar in range(bars):
            for i in range(16):
                if kick_bar[i]:
                    start = bar * BAR + i * step16
                    unit.add_event(MusicEvent(MidiPercussion.BASS_DRUM, 100, start, start + step16))
            for i in range(16):
                if snare_bar[i]:
                    start = bar * BAR + i * step16
                    unit.add_event(MusicEvent(MidiPercussion.ACOUSTIC_SNARE, 90, start, start + step16))
            for i in range(16):
                if hat_bar[i]:
                    start = bar * BAR + i * step16
                    unit.add_event(MusicEvent(MidiPercussion.CLOSED_HI_HAT, 65, start, start + step16))

    if len(unit.data) == 0 or unit.len_ticks() < bars * BAR:
        last = unit.len_ticks() if len(unit.data) else 0
        unit.add_event(MusicEvent(0, 0, last, bars * BAR))
    return unit


# ---------------------------------------------------------------- compose

def build_composer():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=5, num_sections=5)
    composer.add_voice("Melody", program=MidiInstrument.FLUTE, channel=0)
    composer.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    composer.add_voice("Arp", program=MidiInstrument.SYNTH_PAD, channel=3)
    composer.add_voice("Drums", program=0, channel=9)
    for name in SECTION_NAMES:
        composer.add_section(name, bars=SECTION_BARS[name])

    builders = [build_melody, build_pad, build_bass, build_arp, build_drums]
    for s, section in enumerate(SECTION_NAMES):
        for r, b in enumerate(builders):
            composer.set_unit(r, s, b(section, s))

    ok, msg = composer.validate()
    if not ok:
        raise ValueError(f"Zero-drift validation failed: {msg}")
    return composer


def compose_to(project_dir):
    os.makedirs(os.path.join(project_dir, 'MIDI'), exist_ok=True)
    os.makedirs(os.path.join(project_dir, 'Analysis'), exist_ok=True)

    composer = build_composer()
    midi_path = os.path.join(project_dir, 'MIDI', 'pop_5part_methods.mid')
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40, "Empty MIDI!"

    grid_path = os.path.join(project_dir, 'Analysis', 'grid_visualization.txt')
    write_grid_visualization(
        composer.matrix, grid_path,
        voice_names=["Melody", "Pad", "Bass", "Arp", "Drums"], bpm=BPM,
    )

    write_provenance(midi_path, AI_ASSISTED, "musicom skeleton-first + per-section methods",
                     sources=["C major I-V-vi-IV", "Markov 002", "Tendency 023",
                              "Euclidean 011", "DPSM 026", "Isorhythm 032", "Schillinger 018"],
                     parameters={"bpm": BPM, "form": "Intro-Verse-Chorus-Bridge-Outro"},
                     notes="Phase 1: framework + per-section method variation, same key/progression.")

    return midi_path, grid_path


if __name__ == '__main__':
    out = '/opt/data/projects/Styles/Pop/pop-5part-methods'
    midi, grid = compose_to(out)
    print(f"MIDI: {midi} ({os.path.getsize(midi)} bytes)")
    print(f"Grid: {grid}")
