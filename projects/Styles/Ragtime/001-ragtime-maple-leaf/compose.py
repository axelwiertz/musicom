#!/usr/bin/env python3
"""001-ragtime-maple-leaf — Ragtime with boom-chick bass and ragged melody.

Musicom UnitMatrix engine. Left hand: root on 1&3, chord on 2&4.
Right hand: syncopated melody with ties. C major, chromatic passing.
Zero-drift validated.
"""
import os

from structures import MusicEvent, MusicUnit, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BEATS = 4
BAR = TPB * BEATS
QUARTER = TPB
EIGHTH = TPB // 2
SIXTEENTH = TPB // 4
BPM = 120
SECTIONS = 4
BARS_PER_SECTION = 4
SECTION = BAR * BARS_PER_SECTION

OUT = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(OUT, "MIDI")
AUDIO_DIR = os.path.join(OUT, "Audio")
ANALYSIS_DIR = os.path.join(OUT, "Analysis")


def clamp(events, sec):
    for e in events:
        if e.end_tick > sec:
            e.end_tick = sec
        if e.start_tick > sec:
            e.start_tick = sec - 10
    if not events or events[-1].end_tick < sec:
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=sec - 10, end_tick=sec))
    return events


def unit(events, sec):
    return MusicUnit(events=clamp(events, sec))


def build_lh():
    """Boom-chick: root (C2/G2) on 1&3, chord (C3-E3-G3) on 2&4."""
    ev = []
    chords = {
        "C": ([36, 43], [48, 52, 55]),
        "F": ([29, 41], [41, 45, 48]),
        "G": ([31, 43], [43, 47, 50]),
        "G7": ([31, 43], [43, 47, 50, 53]),
        "C7": ([36, 43], [48, 52, 55, 58]),
    }
    prog = ["C", "C", "F", "C", "C", "F", "C", "G", "C", "C", "G7", "C",
            "C", "F", "G", "C"]
    for bar, ch in enumerate(prog):
        roots, chord = chords[ch]
        t0 = bar * BAR
        # beat 1 & 3: root
        for b in (0, 2):
            r = roots[b // 2]
            ev.append(MusicEvent(pitch=r, volume=85, start_tick=t0 + b * QUARTER,
                                 end_tick=t0 + b * QUARTER + QUARTER))
        # beat 2 & 4: chord
        for b in (1, 3):
            for p in chord:
                ev.append(MusicEvent(pitch=p, volume=70,
                                     start_tick=t0 + b * QUARTER,
                                     end_tick=t0 + b * QUARTER + QUARTER))
    return unit(ev, SECTION)


def build_rh():
    """Ragged melody: syncopated, tied across beats, chromatic passing."""
    scale = [60, 62, 64, 65, 67, 69, 71, 72]
    # (bar, beat, pitch_idx, dur_beats) — syncopated
    motif = [
        (0, 0.0, 4, 0.5), (0, 1.5, 6, 0.5), (0, 2.0, 7, 0.5), (0, 3.5, 4, 0.5),
        (1, 0.0, 2, 0.5), (1, 1.5, 3, 0.5), (1, 2.0, 4, 0.5), (1, 3.5, 2, 0.5),
        (2, 0.0, 0, 1.0), (2, 2.0, 2, 0.5), (2, 3.5, 4, 0.5),
        (3, 0.0, 5, 0.5), (3, 1.5, 6, 0.5), (3, 2.0, 7, 0.5), (3, 3.5, 4, 0.5),
    ]
    ev = []
    for bar, beat, pi, dur in motif:
        t = int((bar * BAR) + (beat * QUARTER))
        ev.append(MusicEvent(pitch=scale[pi], volume=90, start_tick=t,
                             end_tick=t + int(dur * QUARTER)))
    # chromatic passing note on last beat of bar 3 (F# → G)
    t = 3 * BAR + 7 * EIGHTH
    ev.append(MusicEvent(pitch=66, volume=80, start_tick=t,
                         end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def build_banjo():
    """Optional 16th-note counter-rolls on chord tones."""
    chords = [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]]
    ev = []
    for bar, ch in enumerate(chords):
        t0 = bar * BAR
        for i in range(16):
            p = ch[i % 3]
            t = t0 + i * SIXTEENTH
            ev.append(MusicEvent(pitch=p, volume=55, start_tick=t,
                                 end_tick=t + SIXTEENTH))
    return unit(ev, SECTION)


def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS)
    composer.create_matrix(num_voices=3, num_sections=SECTIONS)
    composer.add_voice("PianoLH", program=MidiInstrument.PIANO, channel=0)
    composer.add_voice("PianoRH", program=MidiInstrument.PIANO, channel=1)
    composer.add_voice("Banjo", program=105, channel=2)  # GM banjo

    for s in range(SECTIONS):
        name = f"S{s+1}"
        composer.add_section(name, bars=BARS_PER_SECTION)
        composer.fill_voice_section("PianoLH", name, build_lh())
        composer.fill_voice_section("PianoRH", name, build_rh())
        composer.fill_voice_section("Banjo", name, build_banjo())

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"VALIDATION FAILED: {msg}")

    midi_path = os.path.join(MIDI_DIR, "ragtime-maple-leaf.mid")
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["PianoLH", "PianoRH", "Banjo"],
                             bpm=BPM)
    write_provenance(midi_path, AI_ASSISTED, "ragtime-maple-leaf",
                     parameters={"bpm": BPM, "form": "16-bar",
                                 "bass": "boom-chick", "key": "C major"})
    print(f"OK {midi_path} size={os.path.getsize(midi_path)} validate={msg}")


if __name__ == "__main__":
    main()
