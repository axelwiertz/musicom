# -*- coding: utf-8 -*-
"""Verify Fiddle constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)
FIDDLE = by_name("fiddle")
print("Registry: by_name('fiddle') =", FIDDLE)
print("Registry: by_program(110) =", by_program(110))
assert FIDDLE.midi_program == 110
assert by_program(110).name == "Fiddle"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
print("Registry table:\n" + table)
assert "| World | Fiddle | 110 |" in table, "fiddle row missing from registry_table()"

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = FIDDLE.midi_program
GM_NAME = FIDDLE.gm_name
STEM_LABEL = FIDDLE.stem_label
SOLO_RANGE = FIDDLE.solo_range
SWEET_SPOT = FIDDLE.sweet_spot
ZONES = FIDDLE.zones
ARTICULATIONS = FIDDLE.articulations
SYNTHESIS = FIDDLE.synthesis
BOWED_DEFAULTS = FIDDLE.bowed_defaults
MODAL_PRESET = FIDDLE.modal_preset
REVERB_TAIL = FIDDLE.reverb_tail
EQ_BODY = FIDDLE.eq_body
EQ_PRESENCE = FIDDLE.eq_presence
EQ_AIR = FIDDLE.eq_air
PAN = FIDDLE.pan

print(f"\nFiddle: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={FIDDLE.range_min}-{FIDDLE.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Fiddle: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"bowed={BOWED_DEFAULTS} modal={MODAL_PRESET!r}")
print(f"Fiddle: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from World.fiddle.fiddle import midi_to_freq
print(f"Fiddle: G3={midi_to_freq(55):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"A4={midi_to_freq(69):.1f}Hz C6={midi_to_freq(84):.1f}Hz "
      f"C7={midi_to_freq(96):.1f}Hz")
assert FIDDLE.in_range(55) and FIDDLE.in_range(96) and not FIDDLE.in_range(54)
assert FIDDLE.in_sweet_spot(69)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Fiddle solo melody (ch0). Context: ONE low bass note an octave+
# below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Fiddle", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Fiddle: folk dance line in the sweet spot (G3..E6), drivey 8th feel;
# every note voice-shaped, last event ends FLUSH at BAR (terminal landmark).
u = MusicUnit()
mel = [69, 72, 74, 76, 74, 72, 69, 67]  # A4 C5 D5 E5 D5 C5 A4 G4 — reel idiom
n = len(mel)
dur = BAR // n  # 240 ticks each, contiguous 8ths
for i, p in enumerate(mel):
    start = i * dur
    end = BAR if i == n - 1 else (i + 1) * dur
    u.add_event(MusicEvent(p, 84, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass D2 (38) — well below the fiddle's G3 (55), no overlap
u = MusicUnit()
u.add_event(MusicEvent(38, 58, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/fiddle_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/fiddle_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Fiddle (first voice) ONLY
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# ---- Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed) -----
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [40, 41, 42, 104, 109, 110, 111]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Fiddle -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Fiddle", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Fiddle"

# ---- SF2 preset name check (phdr chunk, resolved SoundFont) ---------------
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
print(f"\nSF2: {sf2}")
import struct
with open(sf2, "rb") as f:
    data = f.read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, MIDI_PROGRAM), "MISSING")
print(f"SF2 preset {MIDI_PROGRAM} -> {sf2_name!r}")
assert sf2_name == "Fiddle", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — fiddle stem label on disk ----------
out_dir = "/opt/data/projects/Instruments/_test/stems_fiddle"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Fiddle" in f for f in stem_files), f"no Fiddle stem in {stem_files}"
fi_stem = [f for f in stem_files if "Fiddle" in f][0]
assert os.path.getsize(os.path.join(out_dir, fi_stem)) > 40, "empty Fiddle stem"

# ---- BowedString smoke test: sustained bowed tone --------------------------
from sound.synthesis.bowed import BowedString
import numpy as np
sr = 22050
bs = BowedString(sample_rate=sr)
audio = bs.render_note(69, 0.8, bow_velocity=0.2, bow_force=1.5)
peak = np.max(np.abs(audio))
# A sustained bowed tone should NOT collapse to silence: late-window RMS
# (0.5-0.7s) must still be a real fraction of the peak.
late_rms = np.sqrt(np.mean(audio[int(0.5 * sr):int(0.7 * sr)] ** 2))
ratio = late_rms / peak if peak > 0 else 1.0
print(f"\nBowedString fiddle: peak={peak:.3f} late(0.5-0.7s)_rms/peak={ratio:.3f}")
assert peak > 0, "bowed fiddle render silent"
assert ratio > 0.30, "bowed tone collapses — expected sustained bow, got pluck decay"

print("\nALL CHECKS PASSED")