# -*- coding: utf-8 -*-
"""Verify Double Bass constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Strings.double_bass.double_bass import (
    MIDI_PROGRAM as DB_PGM, GM_NAME, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, REVERB_TAIL, PAN, midi_to_freq,
)
from Strings.cello.cello import MIDI_PROGRAM as CELLO_PGM
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM

print(f"DoubleBass: program={DB_PGM} gm={GM_NAME!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"DoubleBass: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"DoubleBass: E1={midi_to_freq(28):.1f}Hz A1={midi_to_freq(33):.1f}Hz G2={midi_to_freq(43):.1f}Hz D5={midi_to_freq(74):.1f}Hz")
print(f"Context: cello_pgm={CELLO_PGM} piano_pgm={PIANO_PGM}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("DoubleBass", program=DB_PGM, channel=0)
comp.add_voice("Cello", program=CELLO_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Double bass: low-zone sub-bass roots + pizzicato rhythm (role: bass/rhythm)
u = MusicUnit()
# bowed sub-bass roots: E1-A1-D2-G2, half notes (dark low zone)
for i, p in enumerate([28, 33, 38, 43]):
    u.add_event(MusicEvent(p, 86, i * 480, i * 480 + 460))
# pizzicato walking rhythm (mid zone, sweet spot) — end flush at BAR
for i, p in enumerate([40, 42, 43, 45]):
    u.add_event(MusicEvent(p, 70, i * 480, BAR if i == 3 else i * 480 + 140))
# zero-drift terminal landmark (belt + suspenders)
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 70, 0, BAR))
comp.set_unit(1, 0, u)

u = MusicUnit()
for p in [72, 74, 76, 77]:
    u.add_event(MusicEvent(p, 80, 0, BAR))
comp.set_unit(2, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/double_bass_test.mid"
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
wav = "/opt/data/projects/Instruments/_test/double_bass_test.wav"
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
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [40, 41, 42, 43, 44]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  DoubleBass -> {labels[DB_PGM]!r}")
assert labels[DB_PGM] == "Contrabass", f"stem label mismatch: {labels[DB_PGM]!r}"

# Sanity: SF2 preset name for our program must be a contrabass, not something else
import struct
data = open(sf2_legacy, "rb").read()
pos = data.find(b"pdta")
pdta_off = pos - 8
pdta_size = struct.unpack("<I", data[pdta_off + 4:pdta_off + 8])[0]
phdr_pos = data.find(b"phdr", pdta_off, pdta_off + pdta_size)
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, DB_PGM), "MISSING")
print(f"SF2 preset {DB_PGM} -> {sf2_name!r}")
assert "Contrabass" in sf2_name, f"SF2 preset mismatch: {sf2_name!r}"

# Render stems for real: double bass should label trackXX_Contrabass.wav
stems_out = "/opt/data/projects/Instruments/_test/stems_double_bass"
p = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2_legacy, gain=1.2)
stems = p.render_stems(midi_path, stems_out)
for name, path in stems.items():
    print(f"stem: {name} -> {path} ({os.path.getsize(path)} bytes)")
bass_stems = [n for n in stems if "Contrabass" in n]
assert bass_stems, f"no Contrabass stem found: {list(stems)}"
print(f"\nDouble bass stem label OK: {bass_stems[0]}")

print("\nALL CHECKS PASSED")
