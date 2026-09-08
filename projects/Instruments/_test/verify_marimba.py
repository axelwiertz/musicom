# -*- coding: utf-8 -*-
"""Verify Marimba constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Percussion.marimba.marimba import (
    MIDI_PROGRAM as MAR_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, MODAL_PRESET, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
from Woodwind.clarinet.clarinet import MIDI_PROGRAM as CL_PGM
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM

print(f"Marimba: program={MAR_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Marimba: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Marimba: A2={midi_to_freq(45):.1f}Hz C4={midi_to_freq(60):.1f}Hz C6={midi_to_freq(84):.1f}Hz C7={midi_to_freq(96):.1f}Hz")
print(f"Context: clarinet_pgm={CL_PGM} piano_pgm={PIANO_PGM}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("Marimba", program=MAR_PGM, channel=0)
comp.add_voice("Clarinet", program=CL_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Marimba: melodic percussion on channel 0 (NOT ch9) — sweet-spot lead line,
# end flush at BAR (terminal landmark)
u = MusicUnit()
for i, p in enumerate([72, 76, 79, 84, 79, 76, 72]):
    u.add_event(MusicEvent(p, 85, i * 240, BAR if i == 6 else i * 240 + 200))
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

midi_path = "/opt/data/projects/Instruments/_test/marimba_test.mid"
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
wav = "/opt/data/projects/Instruments/_test/marimba_test.wav"
# FIX (2026-09-01): render Marimba SOLO via discover_soundfont() (FluidR3
# preferred). The old full-stack render (Marimba+Clarinet+Piano unison on
# C-E-G) caused comb-filter buzz — spectral centroid 3160->6637 Hz.
render_midi(midi_path, wav, solo=0)  # track 1 = Marimba (first voice)
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
for idx in [11, 12, 13, 14]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Marimba -> {labels[MAR_PGM]!r}")
assert labels[MAR_PGM] == "Marimba", f"stem label mismatch: {labels[MAR_PGM]!r}"
assert STEM_LABEL == "Marimba"

# SF2 preset name for program 12 (verified from phdr chunk)
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
sf2_name = preset_names.get((0, MAR_PGM), "MISSING")
print(f"SF2 preset {MAR_PGM} -> {sf2_name!r}")
assert sf2_name == "Marimba", f"SF2 preset mismatch: {sf2_name!r}"

# Full RenderPipeline stem render — marimba stem label on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_marimba"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2_legacy, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Marimba" in f for f in stem_files), f"no Marimba stem in {stem_files}"
mar_stem = [f for f in stem_files if "Marimba" in f][0]
assert os.path.getsize(os.path.join(out_dir, mar_stem)) > 40, "empty Marimba stem"

# ModalSynth 'marimba' preset smoke test: struck bar = fast exponential decay
from sound.synthesis.modal import ModalSynth
ms = ModalSynth(sample_rate=22050)
audio = ms.render_preset('marimba', duration=0.5, excitation='impulse')
import numpy as np
peak = np.max(np.abs(audio))
# Compare late tail (last 100 ms, ~t=0.4s) vs peak — exp(-8*0.4)=0.04, so the
# tail should be far below the transient peak if decay is exponential/fast
tail_rms = np.sqrt(np.mean(audio[-2205:] ** 2))
tail_ratio = tail_rms / peak if peak > 0 else 1.0
print(f"\nModalSynth marimba: peak={peak:.3f} tail_rms/peak={tail_ratio:.3f}")
assert peak > 0, "modal marimba render silent"
assert tail_ratio < 0.2, "marimba decay NOT fast (no sustain plateau expected)"

print("\nALL CHECKS PASSED")
