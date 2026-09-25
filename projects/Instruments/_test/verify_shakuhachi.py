# -*- coding: utf-8 -*-
"""Verify Shakuhachi constants work with musicom engine — SOLO only."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

import os

# Import through the registry to prove registration works
from instrument_registry import (
    SHAKUCHACHI, by_name, by_program, ALL_INSTRUMENTS
)

PGM = SHAKUCHACHI.midi_program
print(f"Shakuhachi: program={PGM} gm={SHAKUCHACHI.gm_name!r} "
      f"stem={SHAKUCHACHI.stem_label!r} sweet={SHAKUCHACHI.solo_range} "
      f"A4={SHAKUCHACHI.module_path}")
print(f"  zones={SHAKUCHACHI.zones} art={list(SHAKUCHACHI.articulations)} "
      f"synth={SHAKUCHACHI.synthesis} reverb={SHAKUCHACHI.reverb_tail}s "
      f"pan={SHAKUCHACHI.pan}")
print(f"  range={SHAKUCHACHI.range_min}-{SHAKUCHACHI.range_max}")

# Quick freq check
from World.shakuhachi.shakuhachi import midi_to_freq
print(f"  D4={midi_to_freq(62):.1f}Hz A4={midi_to_freq(69):.1f}Hz "
      f"D6={midi_to_freq(86):.1f}Hz E7={midi_to_freq(100):.1f}Hz")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=100, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Shakuhachi", program=PGM, channel=0)
# Add a low koto drone (octave+ below — will not cause comb-filtering)
comp.add_voice("Koto", program=107, channel=1)
comp.add_section("A", bars=2)

BAR = 1920

# Shakuhachi: monophonic pentatonic line on channel 0 (NOT ch9)
# D4-F4-A4-C5-D5 line in otsu register, terminal landmark at 2*BAR
u = MusicUnit()
notes = [62, 65, 69, 72, 74, 72, 69, 65]  # D-F-A-C-D-C-A-F
for i, p in enumerate(notes):
    start = i * 480  # 8th-notes at 100bpm
    end = BAR if i == len(notes) - 1 else start + 440
    u.add_event(MusicEvent(p, 82, start, end))
if u.len_ticks() < 2 * BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), 2 * BAR))
comp.set_unit(0, 0, u)

# Koto drone: low D3, one octave and a fifth below the lowest shakuhachi note
u2 = MusicUnit()
u2.add_event(MusicEvent(50, 50, 0, 2 * BAR))  # D3 drone
comp.set_unit(1, 0, u2)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/shakuhachi_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO (track 1 = first voice = shakuhachi only)
from _test.render_audio import render_midi_solo, spectral_buzz_check

wav = "/opt/data/projects/Instruments/_test/shakuhachi_test.wav"
render_midi_solo(midi_path, wav, instrument_track=1)
wsize = os.path.getsize(wav)
print(f"WAV (solo shakuhachi): {wav} ({wsize} bytes)")
assert wsize > 1000, f"empty/corrupt WAV: {wsize} bytes"

ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check against pipeline GM_PROGRAMS
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [75, 76, 77, 78, 79]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Shakuhachi -> {labels[PGM]!r}")
assert labels[PGM] == "Shakuhachi", f"stem label mismatch: {labels[PGM]!r}"
assert SHAKUCHACHI.stem_label == "Shakuhachi"

# FluidR3 preset name check
from sound.render.fluidsynth import discover_soundfont
sf2_path = discover_soundfont()
print(f"\nSoundFont: {sf2_path}")

import struct
data = open(sf2_path, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, PGM), "MISSING")
print(f"SF2 preset {PGM} -> {sf2_name!r}")
assert sf2_name == "Shakuhachi", f"SF2 preset mismatch: {sf2_name!r}"

# PhaseModSynth smoke test
# Shakuhachi: sine carrier + sine mod, ratio 1.0, depth 2.0, attack 0.06
from sound.synthesis.phase_mod import PhaseModSynth
import numpy as np
pms = PhaseModSynth(sample_rate=22050)
audio = pms.render_note(freq=587.33, duration=0.5)  # D5=587.33Hz
peak = np.max(np.abs(audio))
print(f"\nPhaseModSynth shakuhachi (D5=587.33Hz): peak={peak:.3f}")
assert peak > 0, "FM shakuhachi render silent"

# Full RenderPipeline stem render
out_dir = "/opt/data/projects/Instruments/_test/stems_shakuhachi"
pipeline = RenderPipeline(
    fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
    soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Shakuhachi" in f for f in stem_files), \
    f"no Shakuhachi stem in {stem_files}"
sha_stem = [f for f in stem_files if "Shakuhachi" in f][0]
assert os.path.getsize(os.path.join(out_dir, sha_stem)) > 40, \
    "empty Shakuhachi stem"

print("\nALL CHECKS PASSED")