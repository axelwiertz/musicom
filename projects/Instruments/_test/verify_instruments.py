# -*- coding: utf-8 -*-
"""Verify instrument constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Strings.violin.violin import (
    MIDI_PROGRAM as VIOLIN_PGM, SWEET_SPOT as VIO_SWEET, midi_to_freq,
)
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM
from Brass.trumpet.trumpet import MIDI_PROGRAM as TRUMPET_PGM, FM_DEFAULTS
from Woodwind.flute.flute import MIDI_PROGRAM as FLUTE_PGM, STEM_LABEL
from Guitar.acoustic.acoustic_guitar import MIDI_PROGRAM as GUITAR_PGM
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES, beat_pattern

print(f"Violin: program={VIOLIN_PGM} sweet={VIO_SWEET} A4={midi_to_freq(69):.1f}Hz")
print(f"Piano:  program={PIANO_PGM}")
print(f"Trumpet: program={TRUMPET_PGM} FM={FM_DEFAULTS['carrier_shape']} depth={FM_DEFAULTS['mod_depth']}")
print(f"Flute:  program={FLUTE_PGM} stem_label={STEM_LABEL}")
print(f"Guitar: program={GUITAR_PGM}")
print(f"DrumKit: kick={KIT['kick']} snare={KIT['snare']} kick_vel={VELOCITIES['kick']}")
print(f"beat_pattern(beats 1-2-3-4): {beat_pattern()}")
print(f"beat_pattern(backbeat 2&4):  {beat_pattern(beat_indices=(4,12))}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("Violin", program=VIOLIN_PGM, channel=0)
comp.add_voice("Piano", program=PIANO_PGM, channel=1)
comp.add_voice("Drums", program=0, channel=9)
comp.add_section("A", bars=1)

BAR = 1920
u = MusicUnit()
for i, p in enumerate([72, 74, 76, 77]):
    u.add_event(MusicEvent(p, 80, i * 480, i * 480 + 480))
comp.set_unit(0, 0, u)

u = MusicUnit()
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 70, 0, BAR))
comp.set_unit(1, 0, u)

u = MusicUnit()
kick = beat_pattern()
snare = beat_pattern(beat_indices=(4, 12))
step = BAR // 16
for i in range(16):
    if kick[i]:
        u.add_event(MusicEvent(KIT['kick'], VELOCITIES['kick'], i * step, i * step + step))
    if snare[i]:
        u.add_event(MusicEvent(KIT['snare'], VELOCITIES['snare'], i * step, i * step + step))
# zero-drift terminal landmark
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(2, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
midi_path = "/opt/data/projects/Instruments/_test/instruments_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
print(f"MIDI: {midi_path} ({os.path.getsize(midi_path)} bytes)")

import subprocess
from _test.render_audio import render_midi, spectral_buzz_check
sf2 = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"  # noqa — legacy check only
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
wav = "/opt/data/projects/Instruments/_test/instruments_test.wav"
# FIX (2026-09-01): render instrument SOLO with preferred SoundFont —
# full-stack unison doubling caused comb-filter buzz in all test WAVs.
render_midi(midi_path, wav, solo=0)  # track 1 = Violin (first voice)
print(f"WAV (solo): {wav} ({os.path.getsize(wav)} bytes)")
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"
