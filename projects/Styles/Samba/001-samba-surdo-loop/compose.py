#!/usr/bin/env python3
"""001-samba-surdo-loop — Brazilian samba, 2/4 feel, layered percussion.

Musicom UnitMatrix engine. Surdo E(2,8), tamborim 16th subdivisions,
shaker continuous 16ths, 8th-note bass, syncopated major-key melody.
Zero-drift validated.
"""
import os

from structures import MusicEvent, MusicUnit, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BEATS = 4
BAR = TPB * BEATS          # 1920
QUARTER = TPB
EIGHTH = TPB // 2
SIXTEENTH = TPB // 4
BPM = 100
SECTIONS = 4
BARS_PER_SECTION = 4
SECTION = BAR * BARS_PER_SECTION   # 7680

OUT = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(OUT, "MIDI")
AUDIO_DIR = os.path.join(OUT, "Audio")
ANALYSIS_DIR = os.path.join(OUT, "Analysis")


def euclidean(pulses, steps, rotation=0):
    out = [False] * steps
    bucket = 0.0
    idx = 0
    for _ in range(steps):
        bucket += pulses
        if bucket >= steps:
            bucket -= steps
            out[idx] = True
        idx += 1
    return out[rotation:] + out[:rotation]


def clamp(events, section_ticks):
    for e in events:
        if e.end_tick > section_ticks:
            e.end_tick = section_ticks
        if e.start_tick > section_ticks:
            e.start_tick = section_ticks - 10
    if not events or events[-1].end_tick < section_ticks:
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=section_ticks - 10,
                                 end_tick=section_ticks))
    return events


def unit(events, sec):
    return MusicUnit(events=clamp(events, sec))


def build_surdo():
    """E(2,8) on beats 1 and 2 (2/4 feel) — kick."""
    ev = []
    for i, hit in enumerate(euclidean(2, 8)):
        if hit:
            t = i * EIGHTH
            ev.append(MusicEvent(pitch=36, volume=100, start_tick=t,
                                 end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def build_tamborim():
    """16th subdivisions, swung — high frame drum."""
    ev = []
    for i, hit in enumerate(euclidean(5, 16)):
        if hit:
            t = i * SIXTEENTH
            ev.append(MusicEvent(pitch=76, volume=80, start_tick=t,
                                 end_tick=t + SIXTEENTH))
    return unit(ev, SECTION)


def build_shaker():
    """Continuous 16ths — the groove clock."""
    ev = []
    for i in range(16):
        t = i * SIXTEENTH
        ev.append(MusicEvent(pitch=70, volume=55, start_tick=t,
                             end_tick=t + SIXTEENTH))
    return unit(ev, SECTION)


def build_bass():
    """8th-note root ostinato, C major (I-V)."""
    ev = []
    roots = [36, 43, 36, 43]  # C, G
    for i in range(16):
        r = roots[(i // 2) % 4]
        t = i * EIGHTH
        ev.append(MusicEvent(pitch=r, volume=88, start_tick=t,
                             end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def build_melody():
    """Syncopated C-major melody over 4 bars."""
    # C major pentatonic + F# chromatic passing
    scale = [72, 74, 76, 77, 79, 81, 84]
    # (beat, pitch_idx, dur_beats) — syncopated
    motif = [
        (0.0, 0, 0.5), (0.5, 2, 0.5), (1.5, 4, 1.0), (2.5, 2, 0.5),
        (3.0, 5, 0.5), (3.5, 4, 0.5), (4.0, 0, 0.5), (4.5, 2, 0.5),
        (5.5, 3, 1.0), (6.5, 2, 0.5), (7.0, 1, 0.5), (7.5, 0, 0.5),
    ]
    ev = []
    for beat, pi, dur in motif:
        t = int(beat * QUARTER)
        ev.append(MusicEvent(pitch=scale[pi], volume=92,
                             start_tick=t, end_tick=t + int(dur * QUARTER)))
    # repeat motif 4x across section
    base = ev[:]
    ev = []
    for b in range(4):
        for e in base:
            ev.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                 start_tick=e.start_tick + b * BAR,
                                 end_tick=e.end_tick + b * BAR))
    return unit(ev, SECTION)


def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS)
    composer.create_matrix(num_voices=5, num_sections=SECTIONS)
    composer.add_voice("Surdo", program=0, channel=9)
    composer.add_voice("Tamborim", program=0, channel=9)
    composer.add_voice("Shaker", program=0, channel=9)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    composer.add_voice("Melody", program=MidiInstrument.FLUTE, channel=0)

    for s in range(SECTIONS):
        name = f"S{s+1}"
        composer.add_section(name, bars=BARS_PER_SECTION)
        composer.fill_voice_section("Surdo", name, build_surdo())
        composer.fill_voice_section("Tamborim", name, build_tamborim())
        composer.fill_voice_section("Shaker", name, build_shaker())
        composer.fill_voice_section("Bass", name, build_bass())
        composer.fill_voice_section("Melody", name, build_melody())

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"VALIDATION FAILED: {msg}")

    midi_path = os.path.join(MIDI_DIR, "samba-surdo-loop.mid")
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["Surdo", "Tamborim", "Shaker",
                                          "Bass", "Melody"],
                             bpm=BPM)
    write_provenance(midi_path, AI_ASSISTED, "samba-surdo-loop",
                     parameters={"bpm": BPM, "surdo": "E(2,8)",
                                 "tamborim": "E(5,16)", "key": "C major"})
    print(f"OK {midi_path} size={os.path.getsize(midi_path)} validate={msg}")


if __name__ == "__main__":
    main()
