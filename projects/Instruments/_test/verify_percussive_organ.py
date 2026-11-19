# -*- coding: utf-8 -*-
"""Verify Percussive Organ (GM17) constants through the importable registry.

Contract (nightly job, layer-aligned):
  * import via `from instrument_registry import by_name` — proves registration
  * SOLO render only: one voice, one track (no unison doubling -> no comb buzz)
  * zero-drift validate, MIDI export, FluidSynth WAV via discover_soundfont()
  * RenderPipeline stem label check on disk
"""
import os
import sys
import re
import struct
import inspect

sys.path.insert(0, "/opt/data/projects/Instruments")

from instrument_registry import by_name, by_program, registry_table

PO = by_name("percussive organ")
assert PO is not None, "percussive_organ not registered"
print("Registered:", PO)
print("by_program(17):", by_program(17))
print("by_program(16):", by_program(16), "(must be Drawbar Organ — distinct)")
assert by_program(17).name == "Percussive Organ"
assert by_program(16).name != "Percussive Organ"

print(f"program={PO.midi_program} gm={PO.gm_name!r} stem={PO.stem_label!r}")
print(f"range={PO.range_min}-{PO.range_max} solo={PO.solo_range} "
      f"sweet_spot={PO.sweet_spot}")
print(f"zones={PO.zones}")
print(f"articulations={list(PO.articulations)}")
print(f"synthesis={PO.synthesis!r} reverb={PO.reverb_tail}s pan={PO.pan}")
print(f"eq_body={PO.eq_body} eq_presence={PO.eq_presence} eq_air={PO.eq_air}")

from Keys.percussive_organ.percussive_organ import (
    midi_to_freq, ADDITIVE_HARMONICS, ADDITIVE_ENVELOPE, DRAWBAR_PRESETS,
    drawbar_harmonics, PERCUSSION_DEFAULTS, SF2_ENVELOPE,
    percussion_envelope, FM_DEFAULTS,
)
print(f"A4={midi_to_freq(69):.1f}Hz C2={midi_to_freq(36):.1f}Hz "
      f"C4={midi_to_freq(60):.1f}Hz C7={midi_to_freq(96):.1f}Hz")

# ---- 1. additive bank sanity ---------------------------------------------
for name, amps in ADDITIVE_HARMONICS.items():
    s = sum(amps)
    assert s > 0, name
    norm = [a / s for a in amps]
    assert abs(sum(norm) - 1.0) < 1e-9, f"{name} normalization failed"
print(f"additive banks OK ({len(ADDITIVE_HARMONICS)} registrations, normalized)")

reg = drawbar_harmonics(DRAWBAR_PRESETS["perc3"])
print("drawbar_harmonics(perc3):", reg)
assert abs(reg[1.0] - 1.0) < 1e-9 and 0.5 in reg

env = percussion_envelope(0.18, 44100)
print(f"percussion ping envelope: {len(env)} samples, head={env[0]:.3f}, "
      f"tail={env[-1]:.4f}")
assert env[0] == 1.0 and env[-1] < 0.01, "percussion envelope wrong"
assert PERCUSSION_DEFAULTS["harmonic"] == 3
assert 0.0 < PERCUSSION_DEFAULTS["level"] < 1.0

# ---- 2. UnitMatrixComposer, ONE voice, ONE section -----------------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Percussive Organ", program=PO.midi_program, channel=0)
comp.add_section("A", bars=1)

# Funk comp: C7 stab on beat 1, stab on 2&, sustained 3-4 voicing at the end.
u = MusicUnit()
voicing = [60, 64, 67, 70]          # C4 E4 G4 Bb4 — mid zone, sweet spot
for p in voicing:
    u.add_event(MusicEvent(p, 96, 0, 300))        # downbeat stab (1/8)
for p in voicing:
    u.add_event(MusicEvent(p, 92, 720, 900))      # "and" of 2 stab
for p in voicing:
    u.add_event(MusicEvent(p, 94, 1200, BAR))     # held chord into the bar line
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"zero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/percussive_organ_test.mid"
comp.to_midi(midi_path)
msize = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# ---- 3. SOLO WAV render via discover_soundfont() -------------------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/percussive_organ_test.wav"
render_midi(midi_path, wav, solo=0)   # voice 0 only = solo organ
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
bs_ok, rep = spectral_buzz_check(wav)
print(f"spectral check: {rep}")
assert bs_ok, f"buzz in solo render: {rep}"

# ---- 4. stem label on disk ----------------------------------------------
from sound.render.pipeline import RenderPipeline
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
print("soundfont:", sf2)
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"GM_PROGRAMS[17] = {labels[17]!r}  (16: {labels[16]!r})")
assert labels[17] == "Percussive Organ", f"pipeline label mismatch: {labels[17]!r}"
assert PO.stem_label == "Percussive_Organ"

data = open(sf2, "rb").read()
pos = data.find(b"phdr")
size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
preset = "MISSING"
for i in range(size // 38):
    off = pos + 8 + i * 38
    nm = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    if bank == 0 and num == 17:
        preset = nm
print(f"SF2 bank0 preset 17 = {preset!r}")
assert preset == "Percussive Organ"

out_dir = "/opt/data/projects/Instruments/_test/stems_percussive_organ"
pipeline = RenderPipeline(
    fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
    soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
files = sorted(os.listdir(out_dir))
print("stems:", files)
assert any("Percussive_Organ" in f for f in files), \
    f"no Percussive_Organ stem in {files}"
stem = [f for f in files if "Percussive_Organ" in f][0]
ssize = os.path.getsize(os.path.join(out_dir, stem))
print(f"stem {stem}: {ssize} bytes")
assert ssize > 40

# ---- 5. additive engine smoke test --------------------------------------
import numpy as np
from sound.synthesis.additive import SoundWave

sw = SoundWave(sample_rate=44100, duration=1.0, frequency=midi_to_freq(60))
amps = np.array(ADDITIVE_HARMONICS["perc3"], dtype=float)
amps = amps / amps.sum()
sw.apply_overtones(list(amps))
peak = float(np.max(np.abs(sw.wavedata)))
print(f"additive SoundWave perc3: peak={peak:.1f} "
      f"(sample_count={len(sw.wavedata)})")
assert peak > 0, "additive render silent"

print("\nALL CHECKS PASSED")
print("registry rows:", len(registry_table().splitlines()) - 2)
