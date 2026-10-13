#!/usr/bin/env python3
"""Verify Clean Electric Guitar (GM27) — UnitMatrixComposer + FluidSynth solo render.

Pattern: verify_marimba.py structural template but SOLO (no unison doubling).
One voice, one track — the clean electric guitar alone — NO second melodic
patch doubling the same pitches (comb-filtering bug, fixed 2026-09-01).
A low bass root note at an octave+ below is OK for context.

Uses discover_soundfont() — NEVER hardcode TimGM6mb.
"""

import os, sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# === Registry import — proves registration ===
from instrument_registry import CLEAN_ELECTRIC, by_name, by_program

print("=== Clean Electric Guitar (GM27) — Registry verification ===")
print(f"  by_name('clean electric') -> {by_name('clean electric')}")
print(f"  by_program(27) -> {by_program(27)}")
print(f"  CLEAN_ELECTRIC.midi_program = {CLEAN_ELECTRIC.midi_program} (should be 27)")
print(f"  CLEAN_ELECTRIC.stem_label = {CLEAN_ELECTRIC.stem_label!r}")
print(f"  CLEAN_ELECTRIC.in_sweet_spot(52) = {CLEAN_ELECTRIC.in_sweet_spot(52)}")
print(f"  CLEAN_ELECTRIC.in_sweet_spot(30) = {CLEAN_ELECTRIC.in_sweet_spot(30)}")

# === UnitMatrixComposer — solo clean electric ===
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# One voice — CLEAN ELECTRIC SOLO ONLY. No second melodic patch on same pitches.
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("CleanElectric", program=27, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Clean electric rhythm comp: C major chord in sweet spot — arpeggiated strum
# pattern over 1 bar: C3-E3-G3-C4 (arpeggio, not block chord — idiomatic
# fingerpicking/strum texture). End flush at BAR (terminal landmark).
u = MusicUnit()
chord_notes = [48, 52, 55, 60]  # C2-E2-G2-C3 — low register, idiomatic open-position
for i, p in enumerate(chord_notes):
    start = i * 420
    end = start + 380 if i < len(chord_notes) - 1 else BAR
    u.add_event(MusicEvent(p, 78, start, end))
# Zero-drift pad: ensure total length == BAR
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\n=== Zero-drift check ===")
print(f"  validate() = {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

# Export MIDI
midi_dir = "/opt/data/projects/Instruments/_test"
os.makedirs(midi_dir, exist_ok=True)
midi_path = os.path.join(midi_dir, "clean_electric_test.mid")
comp.to_midi(midi_path)
midi_size = os.path.getsize(midi_path)
print(f"\n=== MIDI export ===")
print(f"  {midi_path} ({midi_size} bytes)")
assert midi_size > 40, f"empty/corrupt MIDI: {midi_size} bytes"

# === FluidSynth render (SOLO) via discover_soundfont() ===
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
fluidsynth = os.environ.get("MUSICOM_FLUIDSYNTH", "/opt/data/micromamba/envs/musicom/bin/fluidsynth")
print(f"\n=== FluidSynth render ===")
print(f"  SoundFont: {sf2}")
print(f"  Fluidsynth: {fluidsynth}")

wav_path = os.path.join(midi_dir, "clean_electric_test.wav")
render_cmd = f"{fluidsynth} -ni -g 1.2 -F {wav_path} {sf2} {midi_path}"
print(f"  Command: {render_cmd}")
ret = os.system(render_cmd)
assert ret == 0, f"FluidSynth failed with exit code {ret}"
wav_size = os.path.getsize(wav_path)
print(f"  WAV: {wav_path} ({wav_size} bytes)")
assert wav_size > 40, f"empty/corrupt WAV: {wav_size} bytes"
print(f"  WAV size > 40 bytes: ✅")

# === Spectral buzz check (no comb-filtering) ===
try:
    from _test.render_audio import spectral_buzz_check
    ok_buzz, buzz_report = spectral_buzz_check(wav_path)
    print(f"\n=== Spectral check ===")
    print(f"  {buzz_report}")
    assert ok_buzz, f"buzz in solo render: {buzz_report}"
except ImportError:
    print("\n=== Spectral check: skipped (render_audio not available) ===")

# === Stem label check against pipeline GM_PROGRAMS ===
import inspect, re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
pipeline_label = labels[27]
print(f"\n=== Stem label check ===")
print(f"  Pipeline GM_PROGRAMS[27] = {pipeline_label!r}")
print(f"  STEM_LABEL = {CLEAN_ELECTRIC.stem_label!r}")
assert pipeline_label == "Electric Guitar (clean)", f"pipeline label mismatch: {pipeline_label!r}"
# The stem label sanitizer removes parens: "Electric Guitar (clean)" -> "Electric_Guitar_clean"
expected_stem = pipeline_label.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
print(f"  Expected stem file: trackXX_{expected_stem}.wav")
assert CLEAN_ELECTRIC.stem_label == expected_stem, f"STEM_LABEL mismatch: {CLEAN_ELECTRIC.stem_label!r} != {expected_stem!r}"
print(f"  Stem label: ✅")

# === Full RenderPipeline stem render ===
out_dir = "/opt/data/projects/Instruments/_test/stems_clean_electric"
pipeline = RenderPipeline(
    fluidsynth_bin=fluidsynth,
    soundfont_path=sf2,
    gain=1.2
)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\n=== Stem render ({len(stem_files)} files) ===")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")

# Check that Clean Electric stem exists
assert any("Electric_Guitar_clean" in f for f in stem_files), \
    f"no clean electric stem in {stem_files}"
clean_stem = [f for f in stem_files if "Electric_Guitar_clean" in f][0]
clean_size = os.path.getsize(os.path.join(out_dir, clean_stem))
print(f"  Clean Electric stem: {clean_stem} ({clean_size} bytes)")
assert clean_size > 40, f"empty Clean Electric stem"

print(f"\n{'='*60}")
print(f"ALL CHECKS PASSED ✅")
print(f"{'='*60}")