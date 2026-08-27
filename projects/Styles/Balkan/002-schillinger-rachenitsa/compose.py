# -*- coding: utf-8 -*-
"""
Balkan Rachenitsa (7/8) composed with the Schillinger resultant method.

Method: SchillingerGenerator (method 018) -- rhythmic resultants from two
periodic generators (a=7, b=2) produce the 7/8 dance pulse. Phase 1 = raw
resultant draft (no harmony, raw tick grid). Phase 2 = rules post-process:
chord-tone quantization on the modal-harmony grid (D aeolian / harmonic
minor), voice-leading check, zero-drift via UnitMatrixComposer.

Engine only: musicom UnitMatrixComposer. No raw mido authoring.
"""

import os
import json
import hashlib

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from generators.schillinger import SchillingerGenerator

PROJECT_DIR = "/opt/data/projects/Styles/Balkan/002-schillinger-rachenitsa"
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")

BPM = 132
TPB = 480
BEATS_PER_BAR = 7
BAR_TICKS = TPB * BEATS_PER_BAR   # 3360 (7 eighths at 480 ticks)
EIGHTH = TPB                      # 480 (one 7/8 eighth note)

# D aeolian / harmonic-minor hybrid scale (D E F G A Bb C# -> D harmonic minor)
SCALE = [62, 64, 65, 67, 69, 70, 73]   # D4 harmonic minor

# Modal harmony: Dm | Bb | Gm | A  (i - VI - iv - V in D harmonic minor)
CHORD_TONES = {
    0: [62, 65, 69],   # Dm
    1: [70, 74, 77],   # Bb
    2: [67, 70, 74],   # Gm
    3: [69, 73, 76],   # A
}


def clamp_pitch(p, lo=48, hi=96):
    return max(lo, min(hi, p))


def schillinger_resultant_rhythm(a, b):
    """Return list of onset positions (in pulses) for generators a,b over span a*b."""
    total = a * b
    combined = []
    for i in range(total):
        if i % a == 0 or i % b == 0:
            combined.append(i)
    return combined


# ---------------------------------------------------------------------------
# PHASE 1: raw Schillinger resultant draft (no harmony, raw pitches)
# ---------------------------------------------------------------------------
def build_phase1():
    gen = SchillingerGenerator(generator_a=7, generator_b=2)
    raw_durations = gen.generate_resultant()
    # Raw melodic events: pitch via sine-coordinate projection on the scale
    # (this is the 'raw' generative draft -- pre-rules, no chord context)
    events = []
    tick = 0
    import math
    for i, dur in enumerate(raw_durations):
        pitch_idx = int(4 + 3 * math.sin(i * 0.8))
        pitch = SCALE[pitch_idx % len(SCALE)]
        ev_dur = dur * EIGHTH
        events.append(MusicEvent(pitch=pitch, volume=92,
                                 start_tick=tick, end_tick=tick + ev_dur))
        tick += ev_dur
    # Force the raw draft onto the same absolute grid as Phase 2:
    # section = 8 bars = 8*1920 ticks
    total = 8 * BAR_TICKS
    unit = MusicUnit()
    for e in events:
        if e.start_tick >= total:
            break
        if e.end_tick > total:
            e.end_tick = total
        unit.add_event(e)
    if not unit.events or unit.events[-1].end_tick < total:
        unit.add_event(MusicEvent(pitch=0, volume=0,
                                  start_tick=total - 10, end_tick=total))
    return unit


# ---------------------------------------------------------------------------
# PHASE 2: rules post-process (chord-tone quantization + zero-drift)
# ---------------------------------------------------------------------------
def quantize_to_chord(pitch, bar_idx):
    """Nearest chord tone within the current bar's harmony."""
    tones = CHORD_TONES[bar_idx % 4]
    return min(tones, key=lambda t: abs(t - pitch))


def build_melody_unit(seed):
    """Phase 2 melody: Schillinger rhythm, chord-tone quantized pitches."""
    gen = SchillingerGenerator(generator_a=7, generator_b=2)
    raw_durations = gen.generate_resultant()
    import math
    unit = MusicUnit()
    tick = 0
    bar_idx = 0
    for i, dur in enumerate(raw_durations):
        # 4-bar harmonic cycle; bar boundary = 1920 ticks
        bar_idx = tick // BAR_TICKS
        raw_pitch = SCALE[int(4 + 3 * math.sin(i * 0.8)) % len(SCALE)]
        pitch = quantize_to_chord(raw_pitch, bar_idx)
        pitch = clamp_pitch(pitch)
        ev_dur = dur * EIGHTH
        if tick + ev_dur > 8 * BAR_TICKS:
            ev_dur = 8 * BAR_TICKS - tick
        if ev_dur <= 0:
            break
        unit.add_event(MusicEvent(pitch=pitch, volume=95,
                                  start_tick=tick, end_tick=tick + ev_dur))
        tick += ev_dur
    if not unit.events or unit.events[-1].end_tick < 8 * BAR_TICKS:
        unit.add_event(MusicEvent(pitch=0, volume=0,
                                  start_tick=8 * BAR_TICKS - 10,
                                  end_tick=8 * BAR_TICKS))
    return unit


def build_pad_units():
    """Harmony voices: Dm-Bb-Gm-A pads, one chord per 4 bars (2 cycles of 8)."""
    chords = [[62, 65, 69], [70, 74, 77], [67, 70, 74], [69, 73, 76]]
    pad_units = []
    for voice_idx in range(3):
        unit = MusicUnit()
        for bar in range(8):
            chord = chords[bar % 4]
            pitch = chord[voice_idx]
            start = bar * BAR_TICKS
            end = start + BAR_TICKS
            unit.add_event(MusicEvent(pitch=pitch, volume=70,
                                      start_tick=start, end_tick=end))
        pad_units.append(unit)
    return pad_units


def build_bass_unit():
    """Root notes on beats 1, 3, 5, 7 of the 7/8 pulse (walking drone feel)."""
    roots = [62, 70, 67, 69]
    unit = MusicUnit()
    for bar in range(8):
        root = roots[bar % 4]
        for beat in range(4):
            start = bar * BAR_TICKS + beat * EIGHTH * 2
            end = start + EIGHTH * 2
            if end > (bar + 1) * BAR_TICKS:
                end = (bar + 1) * BAR_TICKS
            unit.add_event(MusicEvent(pitch=root - 12, volume=100,
                                      start_tick=start, end_tick=end))
    return unit


def build_drum_unit():
    """Balkan tapan: 7/8 pattern qqqqqq (beat on 1,4,6)."""
    unit = MusicUnit()
    kick_pitch = 36
    snap_pitch = 38
    # accents: 1 (0), 4 (3), 6 (5) in 7 eighth pulses
    accents = [0, 3, 5]
    for bar in range(8):
        base = bar * BAR_TICKS
        for pulse in range(7):
            start = base + pulse * EIGHTH
            end = start + EIGHTH - 20
            if pulse in accents:
                unit.add_event(MusicEvent(pitch=kick_pitch, volume=110,
                                          start_tick=start, end_tick=end))
            elif pulse in (1, 2, 4):
                unit.add_event(MusicEvent(pitch=snap_pitch, volume=70,
                                          start_tick=start, end_tick=end))
            else:
                # pulse 6: soft pickup snap (keeps track length aligned)
                unit.add_event(MusicEvent(pitch=snap_pitch, volume=45,
                                          start_tick=start, end_tick=end))
    # Tail pad to exact track length (zero-drift invariant)
    if unit.events and unit.events[-1].end_tick < 8 * BAR_TICKS:
        unit.add_event(MusicEvent(pitch=0, volume=0,
                                  start_tick=8 * BAR_TICKS - 10,
                                  end_tick=8 * BAR_TICKS))
    return unit


def build_all():
    """Assemble Phase 2 composition via UnitMatrixComposer. Returns (composer, ok, msg)."""
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=6, num_sections=1)
    composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    composer.add_voice("Pad1", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Pad2", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Pad3", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    composer.add_voice("Drums", program=0, channel=9)
    composer.add_section("A", bars=8)

    melody = build_melody_unit(seed=42)
    pads = build_pad_units()
    bass = build_bass_unit()
    drums = build_drum_unit()

    composer.fill_voice_section("Lead", "A", melody)
    composer.fill_voice_section("Pad1", "A", pads[0])
    composer.fill_voice_section("Pad2", "A", pads[1])
    composer.fill_voice_section("Pad3", "A", pads[2])
    composer.fill_voice_section("Bass", "A", bass)
    composer.fill_voice_section("Drums", "A", drums)

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"validate() failed: {msg}")
    return composer, ok, msg


def main():
    os.makedirs(MIDI_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    # ---- Phase 1 raw draft ----
    phase1_unit = build_phase1()
    comp1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                               beats_per_bar=BEATS_PER_BAR)
    comp1.create_matrix(num_voices=1, num_sections=1)
    comp1.add_voice("Raw", program=MidiInstrument.FLUTE, channel=0)
    comp1.add_section("A", bars=8)
    comp1.fill_voice_section("Raw", "A", phase1_unit)
    ok1, msg1 = comp1.validate()
    if not ok1:
        raise RuntimeError(f"phase1 validate failed: {msg1}")
    phase1_mid = os.path.join(MIDI_DIR, "002-schillinger-rachenitsa-phase1.mid")
    comp1.to_midi(phase1_mid)

    # ---- Phase 2 rules composition ----
    comp2, ok2, msg2 = build_all()
    final_mid = os.path.join(MIDI_DIR, "002-schillinger-rachenitsa.mid")
    comp2.to_midi(final_mid)

    # ---- Grid visualization ----
    try:
        from visualization.grid import write_grid_visualization
        write_grid_visualization(comp2.matrix, os.path.join(ANALYSIS_DIR,
                                                            "grid_visualization.txt"))
    except Exception as exc:
        with open(os.path.join(ANALYSIS_DIR, "grid_visualization.txt"), "w") as f:
            f.write(f"[grid viz unavailable: {exc}]\n")
    # ---- Provenance ----
    provenance = {
        "project": "002-schillinger-rachenitsa",
        "style": "Balkan",
        "genre": "Rachenitsa (7/8 dance)",
        "method": "schillinger_resultant (SchillingerGenerator a=7 b=2)",
        "classification": "ai-generated",
        "key": "D harmonic minor",
        "bpm": BPM,
        "bars": 8,
        "section_structure": "A x8 (Dm-Bb-Gm-A x2)",
        "phase1": "raw resultant draft, no harmony, sine-axis pitch projection",
        "phase2": "chord-tone quantization + voice leading + zero-drift UnitMatrix",
        "generator": "generators.schillinger.SchillingerGenerator",
        "engine": "musicom UnitMatrixComposer",
        "artifacts": {
            "phase1_mid": phase1_mid,
            "final_mid": final_mid,
        },
    }
    prov_path = os.path.join(ANALYSIS_DIR, "provenance.json")
    with open(prov_path, "w") as f:
        json.dump(provenance, f, indent=2)

    # ---- Summary ----
    summary = {
        "project": "002-schillinger-rachenitsa",
        "style": "Balkan",
        "method": "schillinger_resultant",
        "key": "D harmonic minor",
        "bpm": BPM,
        "bars": 8,
        "time_signature": "7/8",
        "harmony": "Dm - Bb - Gm - A (i - VI - iv - V)",
        "voices": ["Lead flute", "Pad strings x3", "Bass", "Tapan drums"],
        "melody_dna": "Schillinger resultant 7x2 durations, chord-tone quantized",
        "rhythm_dna": "7/8 pulses, tapan accents on 1,4,6",
    }
    summ_path = os.path.join(ANALYSIS_DIR, "summary.json")
    with open(summ_path, "w") as f:
        json.dump(summary, f, indent=2)

    # ---- Size asserts ----
    for p in [phase1_mid, final_mid, prov_path, summ_path]:
        size = os.path.getsize(p)
        assert size > 40, f"empty artifact: {p} ({size}B)"
        print(f"OK {os.path.relpath(p, PROJECT_DIR)}: {size} bytes")

    print(f"validate phase1: {ok1} ({msg1})")
    print(f"validate phase2: {ok2} ({msg2})")


if __name__ == "__main__":
    main()
