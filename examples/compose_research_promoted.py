#!/usr/bin/env python3
"""Composition demo for the three promoted-from-research modules.

Exercises:
  - generators/tintinnabuli.py  (Pärt M-voice + T-voice duet, isorhythmize)
  - generators/tonal_network.py (weighted graph-walk chord progression)
  - structures/metrical.py      (hierarchical metrical tree + quantization)

Layout (UnitMatrixComposer, zero-drift validated):
  Voice 0 "Tintinnabuli"  — Pärt duet (M-voice + T-voice interleaved)
  Voice 1 "Chords"        — tonal-network progression (root per graph role)
  Voice 2 "Isorhythm"     — cyclic talea looped over a color

All artifacts go to /opt/data/projects/Research/outputs/<project>/ per AGENTS.md.
"""
import os

from structures import MidiInstrument, MusicEvent, MusicUnit
from generators.tintinnabuli import TintinnabuliGenerator, isorhythmize
from generators.tonal_network import TonalNetworkGenerator
from structures.metrical import build_common_tree, quantize_onsets_to_ticks
from workflows.unitmatrix_composer import UnitMatrixComposer

TPB = 480
BAR = TPB * 4          # 4/4 bar
BPM = 90
SECTIONS = 4
BARS = 2
SECTION = BAR * BARS   # 3840 ticks per section

OUT = "/opt/data/projects/Research/outputs/compose-research-promoted"
MIDI_DIR = os.path.join(OUT, "MIDI")
AUDIO_DIR = os.path.join(OUT, "Audio")
ANALYSIS_DIR = os.path.join(OUT, "Analysis")

TONIC = 60  # C4


def pad(events):
    for e in events:
        if e.end_tick > SECTION:
            e.end_tick = SECTION
    if not events or events[-1].end_tick < SECTION:
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION - 10, end_tick=SECTION))
    return events


def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    # --- Voice 0: tintinnabuli (M-voice scale stepping + T-voice triad) ---
    tint = TintinnabuliGenerator(tonic=TONIC, mode='natural minor')
    # A small stepwise motive; Pärt sustains long notes over slow chords.
    motive = [62, 64, 60, 64, 67, 60, 62, 64, 60, 64, 67, 60, 67, 65, 64, 62]
    tint_events = []
    for s in range(SECTIONS):
        for i, m_pitch in enumerate(motive):
            t0 = (s * SECTION) + i * TPB
            # M-voice snapped onto the natural-minor scale (melody, high vel)
            # T-voice triad shadow placed above (position=1)
            m_p = tint.m_voice([m_pitch]).pitches[0]
            tint_events.append(MusicEvent(pitch=m_p, volume=88,
                                          start_tick=t0, end_tick=t0 + TPB))
            t_p = tint.t_voice([m_p], position=1).pitches[0]
            tint_events.append(MusicEvent(pitch=t_p, volume=60,
                                          start_tick=t0, end_tick=t0 + TPB))
    tint_sections = []
    for s in range(SECTIONS):
        seg = [e for e in tint_events
               if s * SECTION <= e.start_tick < (s + 1) * SECTION]
        shifted = []
        for e in seg:
            from structures import MusicEvent as ME
            shifted.append(ME(pitch=e.pitch, volume=e.volume,
                              start_tick=e.start_tick - s * SECTION,
                              end_tick=e.end_tick - s * SECTION))
        tint_sections.append(MusicUnit(events=pad(shifted)))

    # --- Voice 1: tonal-network chord progression (C major) --------------
    tnw = TonalNetworkGenerator(root=TONIC, tonic_quality='major', seed=3)
    chord_unit = tnw.progression(num_chords=SECTIONS * 2,  # 2 chords/section
                                 duration_beats=2.0, ticks_per_beat=TPB)
    # tag each chord's root for later visual seed
    roots = [tnw.node_pitches(r)[0] for r in tnw.progression_roles(SECTIONS * 2)]
    chord_sections = []
    for s in range(SECTIONS):
        start_tick = s * SECTION
        seg = [e for e in chord_unit.events
               if start_tick <= e.start_tick < start_tick + SECTION]
        shifted = []
        for e in seg:
            from structures import MusicEvent as ME
            shifted.append(ME(pitch=e.pitch % 12 + 48, volume=52,
                              start_tick=e.start_tick - start_tick,
                              end_tick=e.end_tick - start_tick))
        chord_sections.append(MusicUnit(events=pad(shifted)))

    # --- Voice 2: isorhythm (color cycled against a fixed talea) --------
    color = [0, 3, 7, 10, 5, 8, 2]          # pitch offsets (pattern)
    talea = [1.0, 0.5, 0.5, 1.5, 1.0, 0.5]  # durations in beats
    iso = isorhythmize(color, talea, ticks_per_beat=TPB, start_pitch=TONIC - 24)
    iso_sections = []
    iso_events = list(iso.events)
    for s in range(SECTIONS):
        seg = [e for e in iso_events
               if s * SECTION <= e.start_tick < (s + 1) * SECTION]
        shifted = []
        for e in seg:
            from structures import MusicEvent as ME
            shifted.append(ME(pitch=e.pitch, volume=70,
                              start_tick=e.start_tick - s * SECTION,
                              end_tick=e.end_tick - s * SECTION))
        iso_sections.append(MusicUnit(events=pad(shifted)))

    # --- assemble the composer -------------------------------------------
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    composer.create_matrix(num_voices=3, num_sections=SECTIONS)
    composer.add_voice("Tintinnabuli", program=MidiInstrument.FLUTE, channel=0)
    composer.add_voice("Chords", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Isorhythm", program=MidiInstrument.BASS, channel=2)

    for s in range(SECTIONS):
        name = f"S{s+1}"
        composer.add_section(name, bars=BARS)
        composer.fill_voice_section("Tintinnabuli", name, tint_sections[s])
        composer.fill_voice_section("Chords", name, chord_sections[s])
        composer.fill_voice_section("Isorhythm", name, iso_sections[s])

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"VALIDATION FAILED: {msg}")

    midi_path = os.path.join(MIDI_DIR, "research-promoted-demo.mid")
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40, "empty/corrupt output"

    print(f"OK {midi_path} size={os.path.getsize(midi_path)} validate={msg}")

    # --- Bonus: metrical quantization report ------------------------------
    tree = build_common_tree(bpm=BPM, beats=4, beats_per_bar=4, subdivisions=2)
    from structures.metrical import assign_metrical_level
    grid_times = quantize_onsets_to_ticks([0.0, 0.5, 1.0], BPM, TPB)
    levels = assign_metrical_level([0.0, 0.5, 1.0], tree)
    print("quantized ticks:", [(q.tick, q.duration_ticks) for q in grid_times])
    print("metrical levels:", [(lv.time, lv.label) for lv in levels])


if __name__ == "__main__":
    main()