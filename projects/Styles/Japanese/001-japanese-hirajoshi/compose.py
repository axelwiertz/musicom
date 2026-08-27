#!/usr/bin/env python3
"""001-japanese-hirajoshi — Japanese hōgaku study in D hirajoshi.

Musicom UnitMatrix engine. Koto sparse plucks, shakuhachi sustained
ornamented melody, shamisen 8th ostinato, taiko on strong beats.
Ma (silence) structural. Zero-drift validated.
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
BPM = 70
SECTIONS = 4
BARS_PER_SECTION = 4
SECTION = BAR * BARS_PER_SECTION

OUT = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(OUT, "MIDI")
AUDIO_DIR = os.path.join(OUT, "Audio")
ANALYSIS_DIR = os.path.join(OUT, "Analysis")

# D hirajoshi: D-Eb-G-Ab-C (2-1-4-1-4)
HIRA = [62, 63, 67, 68, 72]


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


def build_koto():
    """Sparse plucks on strong beats, hirajoshi scale."""
    # (beat, pitch_idx, dur_beats)
    motif = [
        (0.0, 0, 1.5), (2.5, 3, 0.5), (3.5, 4, 1.0),
        (4.0, 2, 1.0), (6.5, 1, 0.5),
    ]
    ev = []
    for beat, pi, dur in motif:
        t = int(beat * QUARTER)
        ev.append(MusicEvent(pitch=HIRA[pi], volume=85, start_tick=t,
                             end_tick=t + int(dur * QUARTER)))
    return unit(ev, SECTION)


def build_shakuhachi():
    """Sustained ornamented melody, wide leaps, breath attacks."""
    motif = [
        (0.0, 4, 2.0), (2.0, 2, 1.0), (3.0, 4, 1.0),
        (4.0, 3, 2.0), (6.0, 1, 0.5), (6.5, 0, 1.5),
        (8.0, 2, 1.0), (9.0, 3, 1.0), (10.0, 4, 2.0),
        (12.0, 0, 2.0), (14.0, 4, 2.0),
    ]
    ev = []
    for beat, pi, dur in motif:
        t = int(beat * QUARTER)
        ev.append(MusicEvent(pitch=HIRA[pi] + 12, volume=80, start_tick=t,
                             end_tick=t + int(dur * QUARTER)))
    # mordent ornament on first note
    t = 0
    ev.append(MusicEvent(pitch=HIRA[4] + 12 + 1, volume=70,
                         start_tick=t + EIGHTH // 2,
                         end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def build_shamisen():
    """8th-note ostinato on D + G (root + 4th), sparse but steady."""
    ev = []
    for i in range(32):
        p = 62 if i % 2 == 0 else 67
        t = i * EIGHTH
        ev.append(MusicEvent(pitch=p, volume=60, start_tick=t,
                             end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def build_taiko():
    """Low taiko hits on beat 1 of each bar only."""
    ev = []
    for bar in range(4):
        t = bar * BAR
        ev.append(MusicEvent(pitch=36, volume=100, start_tick=t,
                             end_tick=t + QUARTER))
    return unit(ev, SECTION)


def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS)
    composer.create_matrix(num_voices=4, num_sections=SECTIONS)
    composer.add_voice("Koto", program=108, channel=0)  # GM koto
    composer.add_voice("Shakuhachi", program=75, channel=1)  # pan flute
    composer.add_voice("Shamisen", program=106, channel=2)  # shamisen
    composer.add_voice("Taiko", program=0, channel=9)

    for s in range(SECTIONS):
        name = f"S{s+1}"
        composer.add_section(name, bars=BARS_PER_SECTION)
        composer.fill_voice_section("Koto", name, build_koto())
        composer.fill_voice_section("Shakuhachi", name, build_shakuhachi())
        composer.fill_voice_section("Shamisen", name, build_shamisen())
        composer.fill_voice_section("Taiko", name, build_taiko())

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"VALIDATION FAILED: {msg}")

    midi_path = os.path.join(MIDI_DIR, "japanese-hirajoshi.mid")
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["Koto", "Shakuhachi", "Shamisen",
                                          "Taiko"],
                             bpm=BPM)
    write_provenance(midi_path, AI_ASSISTED, "japanese-hirajoshi",
                     parameters={"bpm": BPM, "scale": "D hirajoshi 2-1-4-1-4",
                                 "instruments": "koto-shakuhachi-shamisen-taiko"})
    print(f"OK {midi_path} size={os.path.getsize(midi_path)} validate={msg}")


if __name__ == "__main__":
    main()
