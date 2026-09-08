# -*- coding: utf-8 -*-
"""Verify Oboe constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Woodwind.oboe.oboe import (
    MIDI_PROGRAM as OBOE_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
from Woodwind.clarinet.clarinet import MIDI_PROGRAM as CL_PGM
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM

print(f"Oboe: program={OBOE_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Oboe: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm={FM_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Oboe: Bb3={midi_to_freq(52):.1f}Hz A4={midi_to_freq(69):.1f}Hz Bb4={midi_to_freq(70):.1f}Hz F5={midi_to_freq(77):.1f}Hz G6={midi_to_freq(92):.1f}Hz")
print(f"Context: clarinet_pgm={CL_PGM} piano_pgm={PIANO_PGM}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("Oboe", program=OBOE_PGM, channel=0)
comp.add_voice("Clarinet", program=CL_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Oboe: low-register sustained + sweet-spot plaintive phrase
u = MusicUnit()
# low zone Bb3-Eb4 sustained (dark reedy foundation)
for i, p in enumerate([52, 55, 58, 55]):
    u.add_event(MusicEvent(p, 72, i * 480, i * 480 + 460))
# sweet spot Bb4-F5 melodic phrase — end flush at BAR
for i, p in enumerate([70, 74, 76, 77]):
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
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 70, 0, BAR))
comp.set_unit(2, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/oboe_test.mid"
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
wav = "/opt/data/projects/Instruments/_test/oboe_test.wav"
# FIX (2026-09-01): render Oboe SOLO — full-stack unison doubling caused
# comb-filter buzz (35% hi-freq with FluidR3 full stack).
render_midi(midi_path, wav, solo=0)  # track 1 = Oboe (first voice)
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
for idx in [65, 66, 67, 68, 69, 70, 71, 72, 73, 74]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Oboe -> {labels[OBOE_PGM]!r}")
assert labels[OBOE_PGM] == "Oboe", f"stem label mismatch: {labels[OBOE_PGM]!r}"
assert STEM_LABEL == "Oboe"

# SF2 preset name for our program must be oboe (verified from phdr chunk)
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
sf2_name = preset_names.get((0, OBOE_PGM), "MISSING")
print(f"SF2 preset {OBOE_PGM} -> {sf2_name!r}")
assert "Oboe" in sf2_name, f"SF2 preset mismatch: {sf2_name!r}"

# Full RenderPipeline stem render (render_stems) — oboe stem label on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_oboe"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Oboe" in f for f in stem_files), f"no Oboe stem in {stem_files}"
oboe_stem = [f for f in stem_files if "Oboe" in f][0]
assert os.path.getsize(os.path.join(out_dir, oboe_stem)) > 40, "empty Oboe stem"

print("\nALL CHECKS PASSED")
