#!/usr/bin/env python3
"""Interval-first composition demo — set theory + Hindemith + expansion.

Uses the new interval primitives from structures/intervals.py and the
interval generators from generators/. Renders to MIDI via the standard
UnitMatrixComposer (zero-drift validated).

Melody: L-System interval deltas on D minor (Bartók-style expansion).
Harmony: Hindemith-managed harmonic fluctuation (target rank <= 4).
Bass: Ratio-lattice-ish fifth walk.
"""
import os

from structures import MidiInstrument
from structures.intervals import interval_expansion, manage_fluctuation
from generators.interval_lsystem import IntervalLSystem
from generators.interval_chain import IntervalMarkovGenerator
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BAR = TPB * 4
BPM = 100
SECTIONS = 4
BARS = 4
SECTION = BAR * BARS  # 7680

OUT = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(OUT, "MIDI")
AUDIO_DIR = os.path.join(OUT, "Audio")
ANALYSIS_DIR = os.path.join(OUT, "Analysis")


def pad(events):
    for e in events:
        if e.end_tick > SECTION:
            e.end_tick = SECTION
    if not events or events[-1].end_tick < SECTION:
        from structures import MusicEvent
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION - 10, end_tick=SECTION))
    return events


def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    # --- melodic material: L-System intervals over D minor ------------
    ls = IntervalLSystem(axiom="A", rules={"A": "A+B", "B": "A-B"},
                         symbols={"+": 2, "-": 1})
    deltas = ls.generate_deltas(4)
    # extend 15 -> 16 by echoing the first delta (fractal self-similarity)
    deltas = deltas + [deltas[0]]
    # apply Bartók expansion: grow the interval sizes each section
    all_notes = []
    for s in range(SECTIONS):
        scale = [1, 2, 3, 4][s]
        expanded = [d * scale for d in deltas]
        all_notes.extend(expanded)

    # re-root at D4 (62) and keep within range
    melody_deltas = all_notes[:16 * SECTIONS]
    pitch = 62
    melody = []
    for d in melody_deltas:
        pitch += d
        melody.append(max(48, min(84, pitch)))

    # Hindemith harmonic fluctuation management: keep ranks <= 4
    melody = list(manage_fluctuation(melody, 4))

    # --- harmonic layer: interval Markov chain -------------------------
    mg = IntervalMarkovGenerator(train_intervals=[0, 2, -1, 3, -2, 4, -3, 2])
    chord_chain = mg.generate_sequence(length=SECTIONS * 4, seed=11)
    chords = mg.to_pitches(chord_chain, 62)  # D root

    # --- build composer -------------------------------------------------
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    composer.create_matrix(num_voices=3, num_sections=SECTIONS)
    composer.add_voice("Melody", program=MidiInstrument.FLUTE, channel=0)
    composer.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)

    for s in range(SECTIONS):
        name = f"S{s+1}"
        composer.add_section(name, bars=BARS)

        # melody: quarter-note events from L-System expansion
        from structures import MusicEvent, MusicUnit
        mel_events = []
        for i, p in enumerate(melody[s * 16:(s + 1) * 16]):
            t = i * TPB
            mel_events.append(MusicEvent(pitch=p, volume=92,
                                         start_tick=t, end_tick=t + TPB))
        composer.fill_voice_section("Melody", name,
                                    MusicUnit(events=pad(mel_events)))

        # pad: sustained chord per section (root + fifth from chain)
        root = chords[s] % 12 + 48
        pad_events = []
        for p in (root, root + 7, root + 12):
            pad_events.append(MusicEvent(pitch=p, volume=60,
                                         start_tick=0, end_tick=SECTION))
        composer.fill_voice_section("Pad", name,
                                    MusicUnit(events=pad(pad_events)))

        # bass: D pedal whole notes
        bass_events = []
        for b in range(BARS):
            t = b * BAR
            bass_events.append(MusicEvent(pitch=38, volume=80,
                                          start_tick=t, end_tick=t + BAR))
        composer.fill_voice_section("Bass", name,
                                    MusicUnit(events=pad(bass_events)))

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"VALIDATION FAILED: {msg}")

    midi_path = os.path.join(MIDI_DIR, "interval-methods-demo.mid")
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["Melody", "Pad", "Bass"], bpm=BPM)
    write_provenance(midi_path, AI_ASSISTED, "interval-methods-demo",
                     parameters={"bpm": BPM,
                                 "melody": "L-System intervals + Bartok expansion",
                                 "harmony": "interval Markov chain + Hindemith rank<=4",
                                 "bass": "D pedal"})
    print(f"OK {midi_path} size={os.path.getsize(midi_path)} validate={msg}")


if __name__ == "__main__":
    main()
