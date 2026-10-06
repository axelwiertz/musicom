# -*- coding: utf-8 -*-
"""Verify Rhodes (Electric Piano 1) constants work with musicom engine.

SOLO render: ONE voice, ONE track — no unison doubling. Comb-filtering
buzz fix (2026-09-01): stacking a second melodic patch (clarinet/piano) on
the SAME pitches creates audible beating. This script renders the Rhodes
SOLO for the audio check.
"""
import os
import sys
import struct
import re
import inspect
import subprocess

sys.path.insert(0, "/opt/data/projects/Instruments")

from instrument_registry import RHODES

def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)

print(f"Rhodes: program={RHODES.midi_program} gm={RHODES.gm_name!r} stem={RHODES.stem_label!r} sweet={RHODES.solo_range}")
print(f"Rhodes: zones={RHODES.zones} art={list(RHODES.articulations.keys()) if RHODES.articulations else None} synth={RHODES.synthesis} reverb={RHODES.reverb_tail}s pan={RHODES.pan}")
print(f"Rhodes: E1={midi_to_freq(36):.1f}Hz C4={midi_to_freq(60):.1f}Hz C5={midi_to_freq(72):.1f}Hz C6={midi_to_freq(84):.1f}Hz")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Rhodes", program=RHODES.midi_program, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Rhodes: sweet-spot chordal comping on channel 0 — no unison doubling.
# End flush at BAR (terminal landmark).
u = MusicUnit()
# A lush Cmaj7 chord wash (C4-E4-G4-B4) held full bar
for p in [60, 64, 67, 71]:
    u.add_event(MusicEvent(p, 72, 0, BAR))
# Melodic top note at 4th beat as bell-like accent
u.add_event(MusicEvent(76, 85, BAR - 480, BAR))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/Keys/rhodes/rhodes_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

from _test.render_audio import render_midi, spectral_buzz_check
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
wav = "/opt/data/projects/Instruments/Keys/rhodes/rhodes_test.wav"
# SOLO render: Rhodes alone (track 1 = first voice) via discover_soundfont()
render_midi(midi_path, wav, solo=0)  # track 1 = Rhodes (first and only voice)
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed)
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  [4] = {labels[4]!r}")
print(f"  Rhodes -> {labels[RHODES.midi_program]!r}")
assert labels[RHODES.midi_program] == "Electric Piano 1", \
    f"stem label mismatch: {labels[RHODES.midi_program]!r}"
assert RHODES.stem_label == "Electric_Piano_1"

# SF2 preset name for program 4 (verified from phdr chunk)
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
assert sf2, "no SoundFont found"
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
assert phdr_pos >= 0, "no phdr chunk in SF2"
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, RHODES.midi_program), "MISSING")
print(f"SF2 preset {RHODES.midi_program} -> {sf2_name!r}")
# FluidR3_GM.sf2 stores preset 4 as "Rhodes EP" (internal SF2 name),
# while GM_PROGRAMS[4] = "Electric Piano 1" (pipeline stem label).
# This cosmetic difference has no routing impact.
print(f"  (note: FluidR3 names it 'Rhodes EP' internally — cosmetic only)")

# RenderPipeline stem render — Rhodes stem label on disk
out_dir = "/opt/data/projects/Instruments/Keys/rhodes/stems"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Electric_Piano_1" in f for f in stem_files), \
    f"no Rhodes stem in {stem_files}"
rh_stem = [f for f in stem_files if "Electric_Piano_1" in f][0]
assert os.path.getsize(os.path.join(out_dir, rh_stem)) > 40, "empty Rhodes stem"

# ModalSynth 'string' preset smoke test: moderate decay
from sound.synthesis.modal import ModalSynth
ms = ModalSynth(sample_rate=22050)
audio = ms.render_preset('string', duration=0.5, excitation='impulse')
import numpy as np
peak = np.max(np.abs(audio))
tail_rms = np.sqrt(np.mean(audio[-2205:] ** 2))
tail_ratio = tail_rms / peak if peak > 0 else 1.0
print(f"\nModalSynth 'string': peak={peak:.3f} tail_rms/peak={tail_ratio:.3f}")
assert peak > 0, "modal string render silent"

print("\nALL CHECKS PASSED")