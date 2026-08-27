#!/usr/bin/env python3
"""001-minimalism-phase-study — Steve Reich "Clapping Music"-style phase piece.

Minimalism process composition on the musicom UnitMatrix engine.
Two identical E(5,12) marimba cells on C pentatonic; voice B walks
+1 beat per section (phase process, Reich style). Pad + bass pedal
give 100% continuous layers.

Strict cell boundaries, zero-drift validated.
"""
import os

from structures import MusicEvent, MusicUnit, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# --- timing -----------------------------------------------------------
TPB = 480          # ticks per beat
BEATS = 4          # 4/4
BAR = TPB * BEATS  # 1920
QUARTER = TPB      # 480
EIGHTH = TPB // 2  # 240
SIXTEENTH = TPB // 4  # 120

BPM = 120

SECTIONS = 8
BARS_PER_SECTION = 3          # pattern cycle = 12 steps x QUARTER = 3 bars
SECTION = BAR * BARS_PER_SECTION  # 5760 ticks
STEP = QUARTER                # one hit per beat max
PHASE_WALK = QUARTER          # +1 beat per section for voice B

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(OUT_DIR, "MIDI")
AUDIO_DIR = os.path.join(OUT_DIR, "Audio")
ANALYSIS_DIR = os.path.join(OUT_DIR, "Analysis")


def euclidean(pulses, steps):
    """Bjorklund-style Euclidean rhythm -> list of bools."""
    out = []
    bucket = 0.0
    for _ in range(steps):
        bucket += pulses
        if bucket >= steps:
            bucket -= steps
            out.append(True)
        else:
            out.append(False)
    return out


def clamp_to_section(events, section_ticks):
    for e in events:
        if e.start_tick < 0:
            e.start_tick = 0
        if e.end_tick > section_ticks:
            e.end_tick = section_ticks
        if e.start_tick > section_ticks:
            e.start_tick = section_ticks - 10
    if not events or events[-1].end_tick < section_ticks:
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=section_ticks - 10,
                                 end_tick=section_ticks))
    return events


def marimba_cell(phase_ticks, pitches, volume=88):
    """E(5,12) cell on C pentatonic, phase-shifted by phase_ticks."""
    events = []
    pattern = euclidean(5, 12)
    for i, hit in enumerate(pattern):
        if not hit:
            continue
        t0 = phase_ticks + i * STEP
        t0 = t0 % SECTION  # wrap within section
        p = pitches[(i // 1) % len(pitches)]
        # pick pitch by hit index, not step index
        events.append(MusicEvent(pitch=p, volume=volume,
                                 start_tick=t0, end_tick=t0 + EIGHTH))
    return MusicUnit(events=clamp_to_section(events, SECTION))


def build_pad():
    """Sustained C major triad (C4-E4-G4), whole section."""
    events = []
    for p in (60, 64, 67):
        events.append(MusicEvent(pitch=p, volume=68,
                                 start_tick=0, end_tick=SECTION))
    return MusicUnit(events=clamp_to_section(events, SECTION))


def build_bass():
    """C2 pedal, whole notes per bar."""
    events = []
    for bar in range(BARS_PER_SECTION):
        t0 = bar * BAR
        events.append(MusicEvent(pitch=36, volume=78,
                                 start_tick=t0, end_tick=t0 + BAR))
    return MusicUnit(events=clamp_to_section(events, SECTION))


def build_perc():
    """E(5,16) kick, sparse anchor."""
    events = []
    pattern = euclidean(5, 16)
    for i, hit in enumerate(pattern):
        if hit:
            t0 = i * SIXTEENTH
            events.append(MusicEvent(pitch=36, volume=95,
                                     start_tick=t0, end_tick=t0 + SIXTEENTH))
    return MusicUnit(events=clamp_to_section(events, SECTION))


def main():
    os.makedirs(MIDI_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    pitches = [60, 62, 64, 67, 69]  # C pentatonic

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS)
    composer.create_matrix(num_voices=5, num_sections=SECTIONS)
    composer.add_voice("MarimbaA", program=12, channel=0)  # GM marimba
    composer.add_voice("MarimbaB", program=12, channel=1)
    composer.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=2)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=3)
    composer.add_voice("Perc", program=0, channel=9)

    for s in range(SECTIONS):
        section_name = f"S{s+1}"
        composer.add_section(section_name, bars=BARS_PER_SECTION)

        # Voice A: fixed cell. Voice B: phase walks +1 beat per section.
        composer.fill_voice_section("MarimbaA", section_name,
                                    marimba_cell(0, pitches))
        composer.fill_voice_section("MarimbaB", section_name,
                                    marimba_cell(s * PHASE_WALK, pitches))
        composer.fill_voice_section("Pad", section_name, build_pad())
        composer.fill_voice_section("Bass", section_name, build_bass())
        composer.fill_voice_section("Perc", section_name, build_perc())

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"VALIDATION FAILED: {msg}")

    midi_path = os.path.join(MIDI_DIR, "minimalism-phase.mid")
    composer.to_midi(midi_path)

    size = os.path.getsize(midi_path)
    assert size > 40, f"empty/corrupt MIDI: {size} bytes"

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path,
                             ticks_per_character=240,
                             voice_names=["MarimbaA", "MarimbaB",
                                          "Pad", "Bass", "Perc"],
                             bpm=BPM)

    write_provenance(midi_path, AI_ASSISTED, "minimalism-phase-study",
                     parameters={"bpm": BPM,
                                 "cell": "E(5,12) C-pentatonic",
                                 "phase_walk_per_section": PHASE_WALK,
                                 "sections": SECTIONS,
                                 "bars_per_section": BARS_PER_SECTION})

    print(f"OK midi={midi_path} size={size}")
    print(f"grid={grid_path}")
    print("validate:", msg)


if __name__ == "__main__":
    main()
