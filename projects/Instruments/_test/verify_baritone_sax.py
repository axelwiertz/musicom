# -*- coding: utf-8 -*-
"""Verify Baritone Saxophone constants with musicom engine.

Tests:
1. Constants import through registry
2. UnitMatrixComposer with solo baritone sax (NO unison doubling)
3. Zero-drift validation
4. MIDI export
5. FluidSynth render via discover_soundfont()
6. Stem label check against pipeline GM_PROGRAMS
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from instrument_registry import (
    BARITONE_SAX, by_name, by_program, ALL_INSTRUMENTS
)
from Woodwind.baritone_sax.baritone_sax import (
    MIDI_PROGRAM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Baritone Sax: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Baritone Sax: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Baritone Sax: A1={midi_to_freq(33):.1f}Hz C2={midi_to_freq(36):.1f}Hz C3={midi_to_freq(48):.1f}Hz C4={midi_to_freq(60):.1f}Hz")

# Full engine test: UnitMatrixComposer with baritone sax SOLO
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("BaritoneSax", program=MIDI_PROGRAM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Baritone Sax: SOLO melodic line in sweet spot C3-F4
# Deep bari voice — use C3 (48), D3(50), F3(53), G3(55), A3(57), C4(60), F4(65)
# Ends flush at BAR (terminal landmark) — zero drift
u = MusicUnit()
notes = [48, 50, 53, 55, 57, 60, 65, 60, 57, 55, 53, 50, 48]
for i, p in enumerate(notes):
    start = i * 140
    end = i * 140 + 130
    u.add_event(MusicEvent(p, 80, start, end))
# Fill to BAR with terminal landmark
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/baritone_sax_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render solo via FluidSynth with discover_soundfont()
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/baritone_sax_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 (voice 0) = Baritone Sax
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
print(f"  [67] = {labels[67]!r}")
assert labels[MIDI_PROGRAM] == "Baritone Sax", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Baritone_Sax", f"STEM_LABEL mismatch: {STEM_LABEL!r}"
print(f"  Baritone Sax -> {labels[MIDI_PROGRAM]!r} ✓")

# Full RenderPipeline stem render
out_dir = "/opt/data/projects/Instruments/_test/stems_baritone_sax"
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Baritone_Sax" in f for f in stem_files), f"no Baritone_Sax stem in {stem_files}"
bari_stem = [f for f in stem_files if "Baritone_Sax" in f][0]
assert os.path.getsize(os.path.join(out_dir, bari_stem)) > 40, "empty Baritone Sax stem"

print(f"\nALL CHECKS PASSED")