# -*- coding: utf-8 -*-
"""Verify Alto Saxophone constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Woodwind.saxophone.saxophone import (
    MIDI_PROGRAM as SAX_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
from Woodwind.clarinet.clarinet import MIDI_PROGRAM as CL_PGM
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM

print(f"Sax: program={SAX_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Sax: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm={FM_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Sax: Db3={midi_to_freq(49):.1f}Hz C4={midi_to_freq(60):.1f}Hz C4={midi_to_freq(61):.1f}Hz C5={midi_to_freq(72):.1f}Hz G5={midi_to_freq(79):.1f}Hz E6={midi_to_freq(88):.1f}Hz")
print(f"Context: clarinet_pgm={CL_PGM} piano_pgm={PIANO_PGM}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("AltoSax", program=SAX_PGM, channel=0)
comp.add_voice("Clarinet", program=CL_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Sax: sweet-spot pop lead phrase C4-F5 — end flush at BAR (terminal landmark)
u = MusicUnit()
for i, p in enumerate([61, 65, 69, 72, 74, 72, 79]):
    u.add_event(MusicEvent(p, 82, i * 240, BAR if i == 6 else i * 240 + 200))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 68, 0, BAR))
comp.set_unit(1, 0, u)

u = MusicUnit()
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 66, 0, BAR))
comp.set_unit(2, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/saxophone_test.mid"
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
wav = "/opt/data/projects/Instruments/_test/saxophone_test.wav"
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
for idx in [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Sax -> {labels[SAX_PGM]!r}")
assert labels[SAX_PGM] == "Alto Sax", f"stem label mismatch: {labels[SAX_PGM]!r}"
assert STEM_LABEL == "Alto_Sax"

# SF2 preset name for our program must be the sax (verified from phdr chunk)
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
sf2_name = preset_names.get((0, SAX_PGM), "MISSING")
print(f"SF2 preset {SAX_PGM} -> {sf2_name!r}")
assert "AltoSax" in sf2_name, f"SF2 preset mismatch: {sf2_name!r}"

# Full RenderPipeline stem render (render_stems) — sax stem label on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_saxophone"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2_legacy, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Alto_Sax" in f for f in stem_files), f"no Alto_Sax stem in {stem_files}"
sax_stem = [f for f in stem_files if "Alto_Sax" in f][0]
assert os.path.getsize(os.path.join(out_dir, sax_stem)) > 40, "empty Sax stem"

print("\nALL CHECKS PASSED")
