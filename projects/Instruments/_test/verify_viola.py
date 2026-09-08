# -*- coding: utf-8 -*-
"""Verify Viola constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Strings.viola.viola import (
    MIDI_PROGRAM as VIOLA_PGM, GM_NAME, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, REVERB_TAIL, PAN, midi_to_freq,
)
from Strings.violin.violin import MIDI_PROGRAM as VIOLIN_PGM
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM

print(f"Viola: program={VIOLA_PGM} gm={GM_NAME!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Viola: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Viola: C3={midi_to_freq(48):.1f}Hz A4={midi_to_freq(69):.1f}Hz G6={midi_to_freq(91):.1f}Hz")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("Viola", program=VIOLA_PGM, channel=0)
comp.add_voice("Violin", program=VIOLIN_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Viola: low/mid register harmony + countermelody (role: harmony/countermelody)
u = MusicUnit()
# low-zone sustained harmony: C3-G3-C4-G3, half notes
for i, p in enumerate([48, 55, 60, 55]):
    u.add_event(MusicEvent(p, 82, i * 480, i * 480 + 460))
# mid-register countermelody (sweet spot) — end flush at BAR
for i, p in enumerate([64, 65, 67, 69]):
    u.add_event(MusicEvent(p, 74, i * 480, BAR if i == 3 else i * 480 + 400))
# zero-drift terminal landmark (belt + suspenders)
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
for p in [72, 74, 76, 77]:
    u.add_event(MusicEvent(p, 80, 0, BAR))
comp.set_unit(1, 0, u)

u = MusicUnit()
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 70, 0, BAR))
comp.set_unit(2, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/viola_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

import subprocess
from _test.render_audio import render_midi, spectral_buzz_check
sf2_legacy = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
wav = "/opt/data/projects/Instruments/_test/viola_test.wav"
render_midi(midi_path, wav, solo=0)  # instrument SOLO (buzz fix)
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# RenderPipeline stem label check (GM_PROGRAMS list, 0-indexed)
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem label (GM_PROGRAMS[{VIOLA_PGM}]): {labels[VIOLA_PGM]!r}")
assert labels[VIOLA_PGM] == "Viola", "stem label quirk!"

# Render stems for real: viola should label trackXX_Viola.wav
stems_out = "/opt/data/projects/Instruments/_test/stems_viola"
p = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2_legacy, gain=1.2)
stems = p.render_stems(midi_path, stems_out)
for name, path in stems.items():
    print(f"stem: {name} -> {path} ({os.path.getsize(path)} bytes)")
viola_stems = [n for n in stems if "Viola" in n]
assert viola_stems, f"no Viola stem found: {list(stems)}"
print(f"\nViola stem label OK: {viola_stems[0]}")

print("\nALL CHECKS PASSED")
