# -*- coding: utf-8 -*-
"""Verify Bassoon constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Woodwind.bassoon.bassoon import (
    MIDI_PROGRAM as BASSOON_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
from Woodwind.clarinet.clarinet import MIDI_PROGRAM as CLAR_PGM
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM

print(f"Bassoon: program={BASSOON_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Bassoon: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm={FM_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Bassoon: Bb1={midi_to_freq(34):.1f}Hz C3={midi_to_freq(48):.1f}Hz G2={midi_to_freq(43):.1f}Hz C4={midi_to_freq(60):.1f}Hz C5={midi_to_freq(72):.1f}Hz E6={midi_to_freq(88):.1f}Hz")
print(f"Context: clarinet_pgm={CLAR_PGM} piano_pgm={PIANO_PGM}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("Bassoon", program=BASSOON_PGM, channel=0)
comp.add_voice("Clarinet", program=CLAR_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Bassoon: low-register sustained + sweet-spot phrase — woodwind bass feel
u = MusicUnit()
# low zone Bb1-F2 sustained (dark woodwind foundation)
for i, p in enumerate([34, 38, 41, 38]):
    u.add_event(MusicEvent(p, 72, i * 480, i * 480 + 460))
# sweet spot C3-C4 phrase — end flush at BAR
for i, p in enumerate([48, 50, 53, 48]):
    u.add_event(MusicEvent(p, 78, i * 480, BAR if i == 3 else i * 480 + 400))
# zero-drift terminal landmark (belt + suspenders)
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 70, 0, BAR))
comp.set_unit(1, 0, u)

u = MusicUnit()
for p in [55, 59, 62]:
    u.add_event(MusicEvent(p, 70, 0, BAR))
comp.set_unit(2, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/bassoon_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

import subprocess
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
wav = "/opt/data/projects/Instruments/_test/bassoon_test.wav"
# FIX (2026-09-01): render Bassoon SOLO — full-stack unison doubling
# (bassoon+clarinet+piano on same chord) caused comb-filter buzz (38% hi-freq).
render_midi(midi_path, wav, solo=0)  # track 1 = Bassoon (first voice)
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
for idx in [65, 66, 68, 69, 70, 71, 72]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Bassoon -> {labels[BASSOON_PGM]!r}")
assert labels[BASSOON_PGM] == "Bassoon", f"stem label mismatch: {labels[BASSOON_PGM]!r}"
assert STEM_LABEL == "Bassoon"

# SF2 preset name for our program must be "Bassoon" (verified from phdr chunk)
import struct
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, BASSOON_PGM), "MISSING")
print(f"SF2 preset {BASSOON_PGM} -> {sf2_name!r}")
assert sf2_name == "Bassoon", f"SF2 preset mismatch: {sf2_name!r}"

# Render stems via RenderPipeline and confirm trackXX_Bassoon.wav
stems_dir = "/opt/data/projects/Instruments/_test/stems_bassoon"
p = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
stems = p.render_stems(midi_path, stems_dir)
for name, path in stems.items():
    print(f"stem {name} -> {os.path.basename(path)} ({os.path.getsize(path)} bytes)")
assert any("Bassoon" in name for name in stems), f"no Bassoon stem: {list(stems)}"

print("\nALL CHECKS PASSED")
