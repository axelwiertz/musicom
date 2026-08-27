#!/usr/bin/env python3
"""001-techno-four-floor — Detroit-style techno loop.

Musicom UnitMatrix engine. Four-on-floor kick E(4,16), offbeat hats,
clap on 2&4, syncopated bass 8ths, Aeolian pad. Hypnotic repetition.
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
BPM = 132
SECTIONS = 4
BARS_PER_SECTION = 4
SECTION = BAR * BARS_PER_SECTION

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


def build_kick():
    """Four-on-the-floor E(4,16)."""
    ev = []
    for i in range(4):
        t = i * QUARTER
        ev.append(MusicEvent(pitch=36, volume=105, start_tick=t,
                             end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def build_hat():
    """Offbeat 8ths + 16th ghost notes."""
    ev = []
    for i in range(8):
        t = i * EIGHTH + EIGHTH // 2  # offbeat
        ev.append(MusicEvent(pitch=70, volume=70, start_tick=t,
                             end_tick=t + EIGHTH))
    # ghost 16ths between
    for i in range(16):
        t = i * SIXTEENTH
        if t % QUARTER != EIGHTH // 2:
            ev.append(MusicEvent(pitch=70, volume=35, start_tick=t,
                                 end_tick=t + SIXTEENTH))
    return unit(ev, SECTION)


def build_clap():
    """On 2 and 4."""
    ev = []
    for b in (1, 3):
        t = b * QUARTER
        ev.append(MusicEvent(pitch=39, volume=95, start_tick=t,
                             end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def build_bass():
    """Syncopated 8th ostinato on A (Aeolian root)."""
    ev = []
    pattern = [1, 0, 1, 0, 1, 1, 0, 1]  # syncopated
    for i, hit in enumerate(pattern):
        if hit:
            t = i * EIGHTH
            ev.append(MusicEvent(pitch=33, volume=92, start_tick=t,
                                 end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def build_pad():
    """A Aeolian sustained chord, whole section."""
    ev = []
    for p in (57, 60, 64):  # A-C-E
        ev.append(MusicEvent(pitch=p, volume=65, start_tick=0,
                             end_tick=SECTION))
    return unit(ev, SECTION)


def build_lead():
    """Hypnotic 16th cell on A minor pentatonic."""
    scale = [69, 72, 74, 76, 79]
    cell = [0, 1, 2, 1, 3, 1, 2, 1]  # pentatonic motif
    ev = []
    for i, pi in enumerate(cell):
        t = i * EIGHTH
        ev.append(MusicEvent(pitch=scale[pi], volume=80, start_tick=t,
                             end_tick=t + EIGHTH))
    return unit(ev, SECTION)


def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS)
    composer.create_matrix(num_voices=6, num_sections=SECTIONS)
    composer.add_voice("Kick", program=0, channel=9)
    composer.add_voice("Hat", program=0, channel=9)
    composer.add_voice("Clap", program=0, channel=9)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    composer.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=3)
    composer.add_voice("Lead", program=80, channel=0)  # square lead

    for s in range(SECTIONS):
        name = f"S{s+1}"
        composer.add_section(name, bars=BARS_PER_SECTION)
        composer.fill_voice_section("Kick", name, build_kick())
        composer.fill_voice_section("Hat", name, build_hat())
        composer.fill_voice_section("Clap", name, build_clap())
        composer.fill_voice_section("Bass", name, build_bass())
        composer.fill_voice_section("Pad", name, build_pad())
        composer.fill_voice_section("Lead", name, build_lead())

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"VALIDATION FAILED: {msg}")

    midi_path = os.path.join(MIDI_DIR, "techno-four-floor.mid")
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["Kick", "Hat", "Clap", "Bass",
                                          "Pad", "Lead"],
                             bpm=BPM)
    write_provenance(midi_path, AI_ASSISTED, "techno-four-floor",
                     parameters={"bpm": BPM, "kick": "E(4,16)",
                                 "bass": "syncopated 8ths", "key": "A Aeolian"})
    print(f"OK {midi_path} size={os.path.getsize(midi_path)} validate={msg}")


if __name__ == "__main__":
    main()
