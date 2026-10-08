# -*- coding: utf-8 -*-
"""Verify Electric Bass (finger) constants work with musicom engine.

Solo render (NO unison doubling): one voice, one track = clean spectral check.
Bass is a line instrument — monophonic groove, no dense chords.

Follows the verify_marimba.py pattern but simplified to SOLO-only render
as required by the 2026-09-01 fix (no clarinet/piano unison doubling).
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Bass.electric_bass.electric_bass import (
    MIDI_PROGRAM as BASS_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, KARPLUS_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
# Import through registry to prove registration
from instrument_registry import ELECTRIC_BASS, ALL_INSTRUMENTS, by_name, by_program

print(f"Electric Bass: program={BASS_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Electric Bass: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Electric Bass: E1={midi_to_freq(28):.1f}Hz A1={midi_to_freq(33):.1f}Hz D2={midi_to_freq(38):.1f}Hz G2={midi_to_freq(43):.1f}Hz")
print(f"Electric Bass: E2={midi_to_freq(40):.1f}Hz A3={midi_to_freq(57):.1f}Hz C4={midi_to_freq(60):.1f}Hz")
print(f"Karplus defaults: {KARPLUS_DEFAULTS}")

# Prove registry registration
print(f"\nRegistry: ELECTRIC_BASS.program={ELECTRIC_BASS.midi_program} ELECTRIC_BASS.name={ELECTRIC_BASS.name!r}")
print(f"Registry: by_name('electric bass') -> {by_name('electric bass').name}")
print(f"Registry: by_program(33) -> {by_program(33).name}")
assert ELECTRIC_BASS.midi_program == 33, f"expected 33, got {ELECTRIC_BASS.midi_program}"
assert by_name("electric bass").midi_program == 33
assert by_program(33).midi_program == 33

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)  # SOLO — one voice only
comp.add_voice("ElectricBass", program=BASS_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Electric Bass: SOLO groove line on channel 0 (melodic channel)
# Simple root-fifth walking pattern in the groove pocket (E2-D3):
# E2-A2-D3-A2-E2-A2-E2 (root-fifth groove), end flush at BAR with terminal
u = MusicUnit()
notes = [40, 45, 50, 45, 40, 45, 40]  # E2-A2-D3-A2-E2-A2-E2
for i, p in enumerate(notes):
    start = i * 240
    end = BAR if i == len(notes) - 1 else i * 240 + 200
    u.add_event(MusicEvent(p, 78, start, end))
# Zero-drift: terminal landmark padded to BAR (all instruments rule)
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/electric_bass_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO via discover_soundfont() (FluidR3 preferred)
from _test.render_audio import render_midi_solo, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/electric_bass_test.wav"
render_midi_solo(midi_path, wav, instrument_track=0)
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
print(f"  Electric Bass (GM{BASS_PGM}) -> {labels[BASS_PGM]!r}")
assert labels[BASS_PGM] == "Electric Bass (finger)", f"stem label mismatch: {labels[BASS_PGM]!r}"
assert STEM_LABEL == "Electric_Bass_finger", f"STEM_LABEL mismatch: {STEM_LABEL!r}"

# SF2 preset name check via FluidR3
from sound.render.fluidsynth import discover_soundfont
sf2_path = discover_soundfont()
print(f"\nSoundFont: {sf2_path}")
import struct
data = open(sf2_path, "rb").read()
phdr_pos = data.find(b"phdr")
if phdr_pos >= 0:
    phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
    preset_names = {}
    for i in range(phdr_size // 38):
        off = phdr_pos + 8 + i * 38
        name = data[off:off+20].split(b"\x00")[0].decode("latin1")
        preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
        preset_names[(bank, preset_num)] = name
    sf2_name = preset_names.get((0, BASS_PGM), "MISSING")
    print(f"SF2 preset {BASS_PGM} -> {sf2_name!r}")

# RenderPipeline stem render for complete verification
fluidsynth_bin = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
out_dir = "/opt/data/projects/Instruments/_test/stems_electric_bass"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth_bin, soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Electric_Bass_finger" in f for f in stem_files), \
    f"no Electric_Bass_finger stem in {stem_files}"
bass_stem = [f for f in stem_files if "Electric_Bass_finger" in f][0]
assert os.path.getsize(os.path.join(out_dir, bass_stem)) > 40, "empty Electric Bass stem"

# Karplus-Strong smoke test: plucked waveguide electric bass note
from sound.synthesis.karplus_strong import karplus_strong
audio = karplus_strong(
    pitch=40,  # E2 = 82.41 Hz
    dur=0.5,
    loop_gain=0.9970,
    width=0.6,
)
import numpy as np
peak = np.max(np.abs(audio))
assert peak > 0, "karplus electric bass render silent"
print(f"\nKarplusStrong E2: peak={peak:.3f} audio_len={len(audio)}")

print("\nALL CHECKS PASSED")