# -*- coding: utf-8 -*-
"""Verify French Horn constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Brass.french_horn.french_horn import (
    MIDI_PROGRAM as FH_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, PAN, midi_to_freq,
)
from Brass.trombone.trombone import MIDI_PROGRAM as TROM_PGM
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM

print(f"FrenchHorn: program={FH_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"FrenchHorn: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm={FM_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"FrenchHorn: F2={midi_to_freq(41):.1f}Hz F3={midi_to_freq(53):.1f}Hz C5={midi_to_freq(72):.1f}Hz C6={midi_to_freq(84):.1f}Hz")
print(f"Context: trombone_pgm={TROM_PGM} piano_pgm={PIANO_PGM}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("FrenchHorn", program=FH_PGM, channel=0)
comp.add_voice("Trombone", program=TROM_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Horn: low-register sustained + sweet-spot phrase
u = MusicUnit()
# low zone F2-C4 sustained (dark mellow)
for i, p in enumerate([41, 48, 53, 48]):
    u.add_event(MusicEvent(p, 74, i * 480, i * 480 + 460))
# sweet spot F3-F5 melodic phrase — end flush at BAR
for i, p in enumerate([60, 64, 67, 72]):
    u.add_event(MusicEvent(p, 78, i * 480, BAR if i == 3 else i * 480 + 400))
# zero-drift terminal landmark (belt + suspenders)
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
for p in [48, 52, 55]:
    u.add_event(MusicEvent(p, 70, 0, BAR))
comp.set_unit(1, 0, u)

u = MusicUnit()
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 70, 0, BAR))
comp.set_unit(2, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/french_horn_test.mid"
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
wav = "/opt/data/projects/Instruments/_test/french_horn_test.wav"
render_midi(midi_path, wav, solo=0)  # instrument SOLO (buzz fix)
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed)
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [56, 57, 58, 60, 61]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  FrenchHorn -> {labels[FH_PGM]!r}")
assert labels[FH_PGM] == "French Horn", f"stem label mismatch: {labels[FH_PGM]!r}"
assert STEM_LABEL == "French Horn"

# Sanity: SF2 preset name for our program must be a horn (plural in TimGM6mb)
import struct
data = open(sf2_legacy, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, FH_PGM), "MISSING")
print(f"SF2 preset {FH_PGM} -> {sf2_name!r}")
assert "French Horn" in sf2_name, f"SF2 preset mismatch: {sf2_name!r}"

print("\nALL CHECKS PASSED")
