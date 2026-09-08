# -*- coding: utf-8 -*-
"""Verify Tuba constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Brass.tuba.tuba import (
    MIDI_PROGRAM as TUBA_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
from Brass.trombone.trombone import MIDI_PROGRAM as TROM_PGM
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM

print(f"Tuba: program={TUBA_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Tuba: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm={FM_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Tuba: D1={midi_to_freq(26):.1f}Hz C2={midi_to_freq(36):.1f}Hz G2={midi_to_freq(43):.1f}Hz Bb3={midi_to_freq(58):.1f}Hz C5={midi_to_freq(72):.1f}Hz")
print(f"Context: trombone_pgm={TROM_PGM} piano_pgm={PIANO_PGM}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("Tuba", program=TUBA_PGM, channel=0)
comp.add_voice("Trombone", program=TROM_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Tuba: low-register sustained + sweet-spot phrase, walking-bass feel
u = MusicUnit()
# low zone D1-G1 sustained (dark sub-bass foundation)
for i, p in enumerate([26, 31, 36, 31]):
    u.add_event(MusicEvent(p, 72, i * 480, i * 480 + 460))
# sweet spot G2-E3 bass phrase — end flush at BAR
for i, p in enumerate([43, 45, 48, 43]):
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

midi_path = "/opt/data/projects/Instruments/_test/tuba_test.mid"
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
wav = "/opt/data/projects/Instruments/_test/tuba_test.wav"
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
for idx in [56, 57, 58, 59, 60, 61]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Tuba -> {labels[TUBA_PGM]!r}")
assert labels[TUBA_PGM] == "Tuba", f"stem label mismatch: {labels[TUBA_PGM]!r}"
assert STEM_LABEL == "Tuba"

# SF2 preset name for our program must be "Tuba" (verified from phdr chunk)
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
sf2_name = preset_names.get((0, TUBA_PGM), "MISSING")
print(f"SF2 preset {TUBA_PGM} -> {sf2_name!r}")
assert sf2_name == "Tuba", f"SF2 preset mismatch: {sf2_name!r}"

print("\nALL CHECKS PASSED")
