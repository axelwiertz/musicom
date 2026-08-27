#!/usr/bin/env python3
"""001-trap-half-time — Trap with 808 sub-bass and half-time drums.

Musicom UnitMatrix engine. Kick E(2,16) on 1 + and-of-3, snare on 3,
hi-hat 16ths with rolls, 808 sub sustained roots, dark Phrygian pad.
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
BPM = 140
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
    """Half-time: kick on 1 (t=0) and 'and' of 3 (t=10/16 bar)."""
    ev = []
    for i, hit in enumerate(euclidean(2, 16, rotation=0)):
        if hit:
            t = i * SIXTEENTH
            ev.append(MusicEvent(pitch=36, volume=105, start_tick=t,
                                 end_tick=t + SIXTEENTH))
    # add snare on beat 3 (t=8/16)
    ev.append(MusicEvent(pitch=38, volume=100, start_tick=8 * SIXTEENTH,
                         end_tick=8 * SIXTEENTH + SIXTEENTH))
    return unit(ev, SECTION)


def build_hat():
    """16th hi-hats with a roll on beat 4 (32nd burst)."""
    ev = []
    for i in range(16):
        t = i * SIXTEENTH
        vel = 60 if i % 2 == 0 else 75  # accent offbeats
        ev.append(MusicEvent(pitch=70, volume=vel, start_tick=t,
                             end_tick=t + SIXTEENTH))
    # roll: 4 extra 32nds before beat 4 (t=14/16)
    for j in range(4):
        t = 14 * SIXTEENTH + j * (SIXTEENTH // 2)
        ev.append(MusicEvent(pitch=70, volume=90, start_tick=t,
                             end_tick=t + SIXTEENTH // 2))
    return unit(ev, SECTION)


def build_808():
    """Sustained root notes, half-bar durations — the trap sub."""
    ev = []
    roots = [28, 28, 35, 31]  # C1, C1, G1, Eb1 (Phrygian-ish)
    for i, r in enumerate(roots):
        t = i * (BAR // 2)
        ev.append(MusicEvent(pitch=r, volume=95, start_tick=t,
                             end_tick=t + BAR // 2))
    return unit(ev, SECTION)


def build_pad():
    """Dark Phrygian sustained chords: Cm(add b9) → Eb → G → Cm."""
    chords = [
        [48, 51, 55, 59],   # C phrygian: C-Eb-G-Db
        [51, 55, 58, 63],   # Eb
        [43, 47, 50, 55],   # G
        [48, 51, 55, 59],   # Cm
    ]
    ev = []
    for ci, ch in enumerate(chords):
        t = ci * BAR
        for p in ch:
            ev.append(MusicEvent(pitch=p, volume=65, start_tick=t,
                                 end_tick=t + BAR))
    return unit(ev, SECTION)


def build_lead():
    """Sparse dark motif, minor pentatonic + b2 color."""
    scale = [72, 75, 77, 79, 82, 84]
    motif = [
        (0, 0, 1.0), (1.5, 2, 0.5), (2.0, 3, 0.5), (3.5, 1, 1.5),
    ]
    ev = []
    for beat, pi, dur in motif:
        t = int(beat * QUARTER)
        ev.append(MusicEvent(pitch=scale[pi], volume=88, start_tick=t,
                             end_tick=t + int(dur * QUARTER)))
    return unit(ev, SECTION)


def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS)
    composer.create_matrix(num_voices=5, num_sections=SECTIONS)
    composer.add_voice("KickSnare", program=0, channel=9)
    composer.add_voice("Hat", program=0, channel=9)
    composer.add_voice("808", program=MidiInstrument.BASS, channel=2)
    composer.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=3)
    composer.add_voice("Lead", program=80, channel=0)  # square lead

    for s in range(SECTIONS):
        name = f"S{s+1}"
        composer.add_section(name, bars=BARS_PER_SECTION)
        composer.fill_voice_section("KickSnare", name, build_kick())
        composer.fill_voice_section("Hat", name, build_hat())
        composer.fill_voice_section("808", name, build_808())
        composer.fill_voice_section("Pad", name, build_pad())
        composer.fill_voice_section("Lead", name, build_lead())

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"VALIDATION FAILED: {msg}")

    midi_path = os.path.join(MIDI_DIR, "trap-half-time.mid")
    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["KickSnare", "Hat", "808", "Pad",
                                          "Lead"],
                             bpm=BPM)
    write_provenance(midi_path, AI_ASSISTED, "trap-half-time",
                     parameters={"bpm": BPM, "kick": "E(2,16) half-time",
                                 "808": "C1 roots", "scale": "C phrygian"})
    print(f"OK {midi_path} size={os.path.getsize(midi_path)} validate={msg}")


if __name__ == "__main__":
    main()
