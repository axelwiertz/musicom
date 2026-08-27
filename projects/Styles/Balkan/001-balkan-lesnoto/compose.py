#!/usr/bin/env python3
"""001-balkan-lesnoto — Balkan 7/8 (2+2+3) dance with drone and ornamented melody.

Musicom UnitMatrix engine, beats_per_bar=7 → bar = 3360 ticks.
Tupan drum accents 1-4-7; gaida drone sustained; kaval melody
stepwise with ornaments on hijaz scale.
Zero-drift validated.
"""
import os

from structures import MusicEvent, MusicUnit, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BEATS = 7                     # 7/8
BAR = TPB * BEATS             # 3360
EIGHTH = TPB // 2             # 240
BPM = 120                     # dotted-quarter pulse
SECTIONS = 4
BARS_PER_SECTION = 4
SECTION = BAR * BARS_PER_SECTION  # 13440

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


def build_tupan():
    """7/8 accents on 1, 4, 7 (2+2+3)."""
    ev = []
    for i, hit in enumerate([1, 0, 0, 1, 0, 0, 1]):
        if hit:
            t = i * EIGHTH
            ev.append(MusicEvent(pitch=36, volume=100, start_tick=t,
                                 end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def build_tambura():
    """Drone: D2 + A2 sustained, 100% density."""
    ev = []
    for p in (38, 45):
        ev.append(MusicEvent(pitch=p, volume=70, start_tick=0,
                             end_tick=SECTION))
    return unit(ev, SECTION)


def build_gaida():
    """High drone D3 sustained + occasional fifth."""
    ev = [MusicEvent(pitch=50, volume=60, start_tick=0, end_tick=SECTION)]
    return unit(ev, SECTION)


def build_kaval():
    """Ornamented stepwise melody, D hijaz (D-Eb-F#-G-A-Bb-C)."""
    scale = [62, 63, 66, 67, 69, 70, 72]  # D hijaz
    # (step, pitch_idx, dur_8ths) — 4 bars of 7/8
    motif = [
        (0, 0, 1), (1, 2, 1), (2, 3, 1), (3, 4, 2),   # bar 1
        (7, 6, 1), (8, 5, 1), (9, 4, 1), (10, 2, 2),  # bar 2
        (14, 3, 1), (15, 2, 1), (16, 0, 1), (17, 1, 1), (18, 0, 2),  # bar 3
        (21, 2, 1), (22, 3, 1), (23, 4, 1), (24, 5, 1), (25, 6, 2),  # bar 4
    ]
    ev = []
    for step, pi, dur in motif:
        t = step * EIGHTH
        ev.append(MusicEvent(pitch=scale[pi], volume=90, start_tick=t,
                             end_tick=t + dur * EIGHTH))
    return unit(ev, SECTION)


def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS)
    composer.create_matrix(num_voices=4, num_sections=SECTIONS)
    composer.add_voice("Tupan", program=0, channel=9)
    composer.add_voice("Tambura", program=MidiInstrument.BASS, channel=2)
    composer.add_voice("Gaida", program=50, channel=3)  # synth strings
    composer.add_voice("Kaval", program=MidiInstrument.FLUTE, channel=0)

    for s in range(SECTIONS):
        name = f"S{s+1}"
        composer.add_section(name, bars=BARS_PER_SECTION)
        composer.fill_voice_section("Tupan", name, build_tupan())
        composer.fill_voice_section("Tambura", name, build_tambura())
        composer.fill_voice_section("Gaida", name, build_gaida())
        composer.fill_voice_section("Kaval", name, build_kaval())

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"VALIDATION FAILED: {msg}")

    midi_path = os.path.join(MIDI_DIR, "balkan-lesnoto.mid")
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["Tupan", "Tambura", "Gaida", "Kaval"],
                             bpm=BPM)
    write_provenance(midi_path, AI_ASSISTED, "balkan-lesnoto",
                     parameters={"bpm": BPM, "meter": "7/8 2+2+3",
                                 "scale": "D hijaz"})
    print(f"OK {midi_path} size={os.path.getsize(midi_path)} validate={msg}")


if __name__ == "__main__":
    main()
