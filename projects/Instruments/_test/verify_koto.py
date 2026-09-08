# -*- coding: utf-8 -*-
"""Verify Koto constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)
KOTO = by_name("koto")
print("Registry: by_name('koto') =", KOTO)
print("Registry: by_program(107) =", by_program(107))
assert KOTO.midi_program == 107
assert by_program(107).name == "Koto"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
print("Registry table:\n" + registry_table())

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = KOTO.midi_program
GM_NAME = KOTO.gm_name
STEM_LABEL = KOTO.stem_label
SOLO_RANGE = KOTO.solo_range
SWEET_SPOT = KOTO.sweet_spot
ZONES = KOTO.zones
ARTICULATIONS = KOTO.articulations
SYNTHESIS = KOTO.synthesis
KARPLUS_DEFAULTS = KOTO.karplus_defaults
MODAL_PRESET = KOTO.modal_preset
FM_DEFAULTS = KOTO.fm_defaults
REVERB_TAIL = KOTO.reverb_tail
EQ_BODY = KOTO.eq_body
EQ_PRESENCE = KOTO.eq_presence
EQ_AIR = KOTO.eq_air
PAN = KOTO.pan

print(f"\nKoto: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={KOTO.range_min}-{KOTO.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Koto: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"karplus={KARPLUS_DEFAULTS} modal={MODAL_PRESET!r} fm={FM_DEFAULTS}")
print(f"Koto: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from World.koto.koto import midi_to_freq
print(f"Koto: D#3={midi_to_freq(51):.1f}Hz A3={midi_to_freq(57):.1f}Hz "
      f"A4={midi_to_freq(69):.1f}Hz C6={midi_to_freq(84):.1f}Hz "
      f"F#6={midi_to_freq(90):.1f}Hz")
assert KOTO.in_range(51) and KOTO.in_range(90) and not KOTO.in_range(50)
assert KOTO.in_sweet_spot(69)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Koto solo melody (ch0). Context: ONE low bass note an octave
# below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Koto", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Koto: monophonic plucked line in hirajoshi flavor, sweet spot; last event
# ends FLUSH at BAR (terminal landmark -> zero-drift).
# E4 G4 A4 C5 A4 G4 E4 — all within sweet spot (64..79), hirajoshi-ish.
u = MusicUnit()
mel = [64, 67, 69, 72, 69, 67, 64]
for i, p in enumerate(mel):
    start = i * 240
    end = BAR if i == len(mel) - 1 else start + 200
    u.add_event(MusicEvent(p, 82, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass A2 (45) — a full octave+ below the lowest koto note (64)
u = MusicUnit()
u.add_event(MusicEvent(45, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/koto_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/koto_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Koto (first voice) ONLY
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
for idx in [104, 105, 106, 107, 108]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Koto -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Koto", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Koto"

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
assert sf2_name == "Koto", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — koto stem label on disk -----------
out_dir = "/opt/data/projects/Instruments/_test/stems_koto"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Koto" in f for f in stem_files), f"no Koto stem in {stem_files}"
koto_stem = [f for f in stem_files if "Koto" in f][0]
assert os.path.getsize(os.path.join(out_dir, koto_stem)) > 40, "empty Koto stem"

# ---- Karplus-Strong smoke test: koto ring between guitar and sitar --------
from sound.synthesis.karplus_strong import karplus_strong
import numpy as np
sr = 44100
audio = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=KARPLUS_DEFAULTS["loop_gain"])
audio_dull = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=0.990)  # dull control
peak = np.max(np.abs(audio))
tail_rms = np.sqrt(np.mean(audio[int(1.0 * sr):int(2.0 * sr)] ** 2))  # 1-2 s, pre-fade
tail_ratio = tail_rms / peak if peak > 0 else 1.0
peak_dull = np.max(np.abs(audio_dull))
tail_dull = np.sqrt(np.mean(audio_dull[int(1.0 * sr):int(2.0 * sr)] ** 2)) / peak_dull if peak_dull > 0 else 1.0
print(f"\nKarplus-Strong koto: peak={peak:.3f} tail_rms/peak(1-2s)={tail_ratio:.3f} "
      f"(low-gain control={tail_dull:.3f})")
assert peak > 0, "karplus koto render silent"
assert tail_ratio > 0.003, "koto decay too fast — loop_gain too low for koto ring"
# Koto loop_gain (0.9970) sits deliberately below sitar's (0.9975) — expect a
# clear but modest ring advantage over the dull 0.990 control (~2x, not 3x).
assert tail_ratio > 1.5 * tail_dull, "koto loop_gain shows no ring advantage over dull control"

print("\nALL CHECKS PASSED")
