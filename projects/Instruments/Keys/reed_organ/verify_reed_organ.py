# -*- coding: utf-8 -*-
"""Verify Reed Organ constants work with musicom engine.

SOLO render only — no unison doubling (no comb-filtering buzz).
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# Import through the registry (proves registration)
from instrument_registry import REED_ORGAN, by_name, by_program
from Keys.reed_organ.reed_organ import (
    MIDI_PROGRAM as REO_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, MODAL_PRESET, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Reed Organ: program={REO_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Reed Organ: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm_defaults={FM_DEFAULTS}")
print(f"Reed Organ: modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Reed Organ: A2={midi_to_freq(45):.1f}Hz C4={midi_to_freq(60):.1f}Hz C6={midi_to_freq(84):.1f}Hz C7={midi_to_freq(96):.1f}Hz")
print(f"Registry: by_name('reed organ') = {by_name('reed organ')}")
print(f"Registry: by_program(20) = {by_program(20)}")
print(f"Registry: REED_ORGAN.stem_label = {repr(REED_ORGAN.stem_label)}")
assert REED_ORGAN.midi_program == 20
assert REED_ORGAN.gm_name == "Reed Organ"
assert REED_ORGAN.in_sweet_spot(72) == True
assert REED_ORGAN.in_sweet_spot(30) == False

# Full engine test: UnitMatrixComposer with instrument constants — SOLO
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)  # SOLO
comp.add_voice("ReedOrgan", program=REO_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Reed Organ: sustained chords — the instrument is polyphonic, so write a
# C major chord across the bar, then a brief melodic phrase.
u = MusicUnit()
# Sustained C4-E4-G4 chord (full bar)
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 72, 0, BAR))
# Add a short melodic rip: C5 - D5 - E5 - G5
for i, p in enumerate([72, 74, 76, 79]):
    u.add_event(MusicEvent(p, 80, i * 240, i * 240 + 200))
# Terminal landmark to ensure zero-drift
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/Keys/reed_organ/reed_organ_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render to WAV via FluidSynth using discover_soundfont() (prefers FluidR3)
from _test.render_audio import render_midi, spectral_buzz_check

wav = "/opt/data/projects/Instruments/Keys/reed_organ/reed_organ_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Reed Organ (first voice)
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check against pipeline GM_PROGRAMS (0-indexed)
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  [20] = {labels[20]!r}")
print(f"  Reed Organ -> {labels[REO_PGM]!r}")
assert labels[REO_PGM] == "Reed Organ", f"stem label mismatch: {labels[REO_PGM]!r}"
assert STEM_LABEL == "Reed Organ"

# SF2 preset name verification
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
print(f"\nSoundFont: {sf2}")
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
sf2_name = preset_names.get((0, REO_PGM), "MISSING")
print(f"SF2 preset {REO_PGM} -> {sf2_name!r}")
assert sf2_name == "Reed Organ", f"SF2 preset mismatch: {sf2_name!r}"

# PhaseModSynth smoke test: free reed = saw carrier, moderate modulation
from sound.synthesis.phase_mod import PhaseModSynth
pms = PhaseModSynth(sample_rate=22050)
for midi_note in [60, 72, 84]:
    freq = midi_to_freq(midi_note)
    audio = pms.render_note(freq=freq, duration=0.5, **FM_DEFAULTS)
    import numpy as np
    peak = np.max(np.abs(audio))
    assert peak > 0, f"PhaseModSynth silent at note {midi_note}"
    print(f"  PhaseModSynth note {midi_note} ({freq:.0f} Hz): peak={peak:.4f}")

# Full RenderPipeline stem render — Reed Organ stem label on disk
out_dir = "/opt/data/projects/Instruments/Keys/reed_organ/stems"
pipeline = RenderPipeline(
    fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
    soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Reed_Organ" in f for f in stem_files), f"no Reed Organ stem in {stem_files}"
ro_stem = [f for f in stem_files if "Reed_Organ" in f][0]
assert os.path.getsize(os.path.join(out_dir, ro_stem)) > 40, "empty Reed Organ stem"

print("\nALL CHECKS PASSED")