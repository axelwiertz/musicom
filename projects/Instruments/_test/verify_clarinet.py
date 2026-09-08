# -*- coding: utf-8 -*-
"""Verify Clarinet constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Woodwind.clarinet.clarinet import (
    MIDI_PROGRAM as CL_PGM, GM_NAME, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, REVERB_TAIL, PAN, midi_to_freq,
)
from Woodwind.flute.flute import MIDI_PROGRAM as FLUTE_PGM
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM

print(f"Clarinet: program={CL_PGM} gm={GM_NAME!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Clarinet: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Clarinet: E3={midi_to_freq(52):.1f}Hz C4={midi_to_freq(60):.1f}Hz B5={midi_to_freq(83):.1f}Hz C7={midi_to_freq(96):.1f}Hz")
print(f"Context: flute_pgm={FLUTE_PGM} piano_pgm={PIANO_PGM}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("Clarinet", program=CL_PGM, channel=0)
comp.add_voice("Flute", program=FLUTE_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Clarinet: chalumeau low-register phrase + clarion sweet-spot phrase
u = MusicUnit()
# low chalumeau: E3-B3-E3-B3 roots, half notes (dark woody zone)
for i, p in enumerate([52, 59, 52, 59]):
    u.add_event(MusicEvent(p, 82, i * 480, i * 480 + 460))
# clarion sweet-spot melodic phrase — end flush at BAR
for i, p in enumerate([71, 74, 76, 79]):
    u.add_event(MusicEvent(p, 78, i * 480, BAR if i == 3 else i * 480 + 400))
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

midi_path = "/opt/data/projects/Instruments/_test/clarinet_test.mid"
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
wav = "/opt/data/projects/Instruments/_test/clarinet_test.wav"
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
for idx in [40, 56, 57, 71, 73, 74]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Clarinet -> {labels[CL_PGM]!r}")
assert labels[CL_PGM] == "Clarinet", f"stem label mismatch: {labels[CL_PGM]!r}"

# Sanity: SF2 preset name for our program must be a clarinet
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
sf2_name = preset_names.get((0, CL_PGM), "MISSING")
print(f"SF2 preset {CL_PGM} -> {sf2_name!r}")
assert "Clarinet" in sf2_name, f"SF2 preset mismatch: {sf2_name!r}"

print("\nALL CHECKS PASSED")
