# -*- coding: utf-8 -*-
"""Verify Clavi constants work with musicom engine — SOLO render only.

No unison doubling (the 2026-09-01 bug fix). Drums or a low bass note
an octave+ below are fine, but never a second melodic patch on the same
pitches.
"""
import sys
import os

sys.path.insert(0, "/opt/data/projects/Instruments")

from Keys.clavi.clavi import (
    MIDI_PROGRAM as CLAVI_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, KARPLUS_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Clavi: program={CLAVI_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Clavi: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} ks={KARPLUS_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Clavi: F1={midi_to_freq(29):.1f}Hz C3={midi_to_freq(48):.1f}Hz C4={midi_to_freq(60):.1f}Hz C5={midi_to_freq(72):.1f}Hz F6={midi_to_freq(89):.1f}Hz")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Clavi", program=CLAVI_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Clavi: struck-string rhythm voice on channel 0 — funk chord chops in
# sweet spot (C3-C5), end flush at BAR (terminal landmark)
u = MusicUnit()
# Funky chop pattern: E4-G4-B4 (guitar register) on beat 1 + 3
for i, p in enumerate([64, 67, 71, 64, 67, 71, 64, 67, 71, 64, 67, 71]):
    start = i * 160  # 16th-note chops
    if i == 11:
        # last event ends at BAR
        u.add_event(MusicEvent(p, 85, start, BAR))
    else:
        u.add_event(MusicEvent(p, 85, start, start + 120))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_dir = "/opt/data/projects/Instruments/Keys/clavi"
os.makedirs(midi_dir, exist_ok=True)
midi_path = os.path.join(midi_dir, "clavi_test.mid")
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO via discover_soundfont()
from _test.render_audio import render_midi_solo, spectral_buzz_check
wav_path = os.path.join(midi_dir, "clavi_test.wav")
render_midi_solo(midi_path, wav_path, instrument_track=0)
wsize = os.path.getsize(wav_path)
print(f"WAV (solo): {wav_path} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav_path)
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
for idx in [6, 7, 8]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Clavi -> {labels[CLAVI_PGM]!r}")
# STEM_LABEL should match the pipeline's real label ("Clavi")
print(f"  STEM_LABEL = {STEM_LABEL!r}")
# Note: pipeline says "Clavi", FluidR3 preset says "Clavinet" — cosmetic
assert labels[CLAVI_PGM] == "Clavi", f"stem label mismatch: {labels[CLAVI_PGM]!r}"
assert STEM_LABEL == "Clavi"

# SF2 preset name for program 7 (verified from phdr chunk)
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
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
sf2_name = preset_names.get((0, CLAVI_PGM), "MISSING")
print(f"FluidR3 preset {CLAVI_PGM} -> {sf2_name!r}")
assert sf2_name == "Clavinet", f"SF2 preset mismatch: {sf2_name!r}"

# Full RenderPipeline stem render — Clavi stem label on disk
out_dir = os.path.join(midi_dir, "stems_clavi")
os.makedirs(out_dir, exist_ok=True)
from utilities.env import fluidsynth_bin
from sound.render.fluidsynth import discover_soundfont
pipeline = RenderPipeline(
    fluidsynth_bin=str(fluidsynth_bin()),
    soundfont_path=str(discover_soundfont()),
    gain=1.2,
)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Clavi" in f for f in stem_files), f"no Clavi stem in {stem_files}"
cl_stem = [f for f in stem_files if "Clavi" in f][0]
assert os.path.getsize(os.path.join(out_dir, cl_stem)) > 40, "empty Clavi stem"

# Karplus-Strong smoke test: struck waveguide = rubber-muted string
from sound.synthesis.karplus_strong import karplus_strong
audio = karplus_strong(pitch=60, dur=0.5, vel=85, loop_gain=0.996, width=0.3)
import numpy as np
peak = np.max(np.abs(audio))
tail_rms = np.sqrt(np.mean(audio[-2205:] ** 2))
tail_ratio = tail_rms / peak if peak > 0 else 1.0
print(f"\nKarplusStrong C4 (60): peak={peak:.3f} tail_rms/peak={tail_ratio:.3f}")
assert peak > 0, "KS clavi render silent"
# The clavinet is the SHORTEST ring in the plucked set — rubber mute kills
# energy fast. tail_ratio should be VERY low (much lower than harp/harpsichord).
print(f"  (clavinet rubber mute: tail ratio {tail_ratio:.4f} — expect < 0.05)")

# ModalSynth 'string' preset smoke test
from sound.synthesis.modal import ModalSynth
ms = ModalSynth(sample_rate=22050)
audio = ms.render_preset('string', duration=0.5, excitation='impulse')
peak2 = np.max(np.abs(audio))
tail2_rms = np.sqrt(np.mean(audio[-2205:] ** 2))
tail2_ratio = tail2_rms / peak2 if peak2 > 0 else 1.0
print(f"ModalSynth string: peak={peak2:.3f} tail_rms/peak={tail2_ratio:.3f}")
assert peak2 > 0, "modal clavi render silent"

print("\nALL CHECKS PASSED")
