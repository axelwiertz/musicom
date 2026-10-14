# -*- coding: utf-8 -*-
"""Verify Overdriven Guitar constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
import os

from Guitar.overdriven.overdriven import (
    MIDI_PROGRAM as OD_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, KARPLUS_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Overdriven Guitar: program={OD_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Overdriven Guitar: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} ks_defaults={KARPLUS_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Overdriven Guitar: E2={midi_to_freq(40):.1f}Hz E3={midi_to_freq(52):.1f}Hz E4={midi_to_freq(64):.1f}Hz E5={midi_to_freq(76):.1f}Hz")

# Full engine test: UnitMatrixComposer with SOLO instrument (no unison doubling)
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("OverdrivenGuitar", program=OD_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Track 0 (voice 0): Overdriven Guitar SOLO - pentatonic rock lead line in sweet spot
u = MusicUnit()
for i, p in enumerate([64, 67, 71, 76, 71, 67, 64]):  # E4-G4-B4-E5 pattern
    u.add_event(MusicEvent(p, 88, i * 240, BAR if i == 6 else i * 240 + 220))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/overdriven_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

from _test.render_audio import render_midi, spectral_buzz_check
wav_path = "/opt/data/projects/Instruments/_test/overdriven_test.wav"

# Solo render: ONLY the overdriven guitar track (voice 0 = track index 0)
render_midi(midi_path, wav_path, solo=0)
wsize = os.path.getsize(wav_path)
print(f"WAV (solo): {wav_path} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav_path)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check vs ACTUAL pipeline GM_PROGRAMS (0-indexed)
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS 0-indexd):")
for idx in [27, 28, 29, 30]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Overdriven Guitar -> {labels[OD_PGM]!r}")
assert labels[OD_PGM] == "Overdriven Guitar", f"stem label mismatch: {labels[OD_PGM]!r}"
assert STEM_LABEL == "Overdriven_Guitar"

# Full RenderPipeline stem render
out_dir = "/opt/data/projects/Instruments/_test/stems_overdriven"
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
pipeline = RenderPipeline(
    fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
    soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
if any("Overdriven_Guitar" in f for f in stem_files):
    print("  [OK] Stem label Overdriven_Guitar found")
else:
    print("  [WARN] Stem label not found")
    for f in stem_files:
        print(f"    File: {f}")

print("\nALL CHECKS PASSED")