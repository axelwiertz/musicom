# -*- coding: utf-8 -*-
"""Verify Tubular Bells constants work with musicom engine.

SOLO render only — no unison doubling (comb-filtering fix 2026-09-01).
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Percussion.tubular_bells.tubular_bells import (
    MIDI_PROGRAM as TB_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, MODAL_PRESET, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Tubular Bells: program={TB_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Tubular Bells: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Tubular Bells: C4={midi_to_freq(60):.1f}Hz G4={midi_to_freq(67):.1f}Hz C5={midi_to_freq(72):.1f}Hz F5={midi_to_freq(77):.1f}Hz")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Tubular Bells", program=TB_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Tubular Bells: melodic channel (0) — slow bell chime in the sweet spot,
# end flush at BAR (terminal landmark for zero-drift)
u = MusicUnit()
# Classic bell chime: C4, G4, C5 (tonic, fifth, octave above)
for i, p in enumerate([60, 67, 72, 67, 60]):
    start = i * 384  # spaced at ~384 ticks each (= 80% of a quarter note)
    end = BAR if i == 4 else start + 480  # last event fills to BAR
    u.add_event(MusicEvent(p, 82, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/tubular_bells_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# SOLO render via discover_soundfont()
import subprocess
from _test.render_audio import render_midi, spectral_buzz_check
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
wav = "/opt/data/projects/Instruments/_test/tubular_bells_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Tubular Bells (first voice)
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
for idx in [14]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Tubular Bells -> {labels[TB_PGM]!r}")
assert labels[TB_PGM] == "Tubular Bells", f"stem label mismatch: {labels[TB_PGM]!r}"
assert STEM_LABEL == "Tubular_Bells"

# Full RenderPipeline stem render — tubular bells stem label on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_tubular_bells"
if os.path.exists(out_dir):
    import shutil
    shutil.rmtree(out_dir)
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
tb_stem = [f for f in stem_files if "Tubular" in f or "tubular" in f]
if tb_stem:
    print(f"  Tubular Bells stem: {tb_stem[0]}")

# Also test through the registry
from instrument_registry import TUBULAR_BELLS, by_name, by_program
print(f"\nRegistry test:")
print(f"  TUBULAR_BELLS.midi_program = {TUBULAR_BELLS.midi_program} (should be 14)")
print(f"  by_name('tubular bells') = {by_name('tubular bells')}")
print(f"  by_program(14) = {by_program(14)}")
print(f"  TUBULAR_BELLS.in_sweet_spot(67) = {TUBULAR_BELLS.in_sweet_spot(67)}")
print(f"  TUBULAR_BELLS.in_sweet_spot(40) = {TUBULAR_BELLS.in_sweet_spot(40)} (should be False)")

print("\nALL CHECKS PASSED")