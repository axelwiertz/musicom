# -*- coding: utf-8 -*-
"""Verify Muted Guitar constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS, MUTED_GUITAR,
)

MG = by_name("muted_guitar")
print("Registry: by_name('muted_guitar') =", MG)
print("Registry: by_name('muted guitar')  =", by_name("muted guitar"))
print("Registry: by_name('Electric Guitar (muted)') =",
      by_name("Electric Guitar (muted)"))
print("Registry: by_program(28) =", by_program(28))
print("Registry: by_program(27) =", by_program(27), "(distinct: clean electric)")
assert MG.midi_program == 28
assert by_program(28).name == "Electric Guitar (muted)"
assert MUTED_GUITAR is MG
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
print("Registry table:\n" + table)
assert "| Guitar | Electric Guitar (muted) | 28 |" in table, \
    "muted guitar row missing from registry_table()"

# ---- Constants through the registry --------------------------------------
MIDI_PROGRAM = MG.midi_program
GM_NAME = MG.gm_name
STEM_LABEL = MG.stem_label
SOLO_RANGE = MG.solo_range
SWEET_SPOT = MG.sweet_spot
ZONES = MG.zones
ARTICULATIONS = MG.articulations
SYNTHESIS = MG.synthesis
MODAL_PRESET = MG.modal_preset
KARPLUS = MG.karplus_defaults
FM_DEFAULTS = MG.fm_defaults
REVERB_TAIL = MG.reverb_tail
EQ_BODY = MG.eq_body
EQ_PRESENCE = MG.eq_presence
EQ_AIR = MG.eq_air
PAN = MG.pan

print(f"\nMuted Guitar: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={MG.range_min}-{MG.range_max} sweet={SWEET_SPOT} solo={SOLO_RANGE}")
print(f"Muted Guitar: zones={ZONES}")
print(f"Muted Guitar: art={list(ARTICULATIONS)}")
print(f"Muted Guitar: synth={SYNTHESIS} modal={MODAL_PRESET!r} ks={KARPLUS}")
print(f"Muted Guitar: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from Guitar.muted_guitar.muted_guitar import midi_to_freq
print(f"Muted Guitar: E2={midi_to_freq(40):.1f}Hz A2={midi_to_freq(45):.1f}Hz "
      f"C3={midi_to_freq(48):.1f}Hz E4={midi_to_freq(64):.1f}Hz")
assert MG.in_range(40) and MG.in_range(76)
assert not MG.in_range(27) and not MG.in_range(85)
assert MG.in_sweet_spot(45)
assert not MG.in_sweet_spot(80), "high stabs are not the sweet spot"

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) -------------------
# Voice stack: Muted Guitar SOLO (ch0) + drum kit context (ch9). No second
# melodic patch on the same pitches (2026-09-01 comb-filter rule).
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES

BAR = 1920
STEP = 120  # 16th @ 480 tpb

comp = UnitMatrixComposer(bpm=104, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("MutedGuitar", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Drums", program=0, channel=9)
comp.add_section("A", bars=1)

# E5 power chord (E3/B3/E4 = 52/59/64) chopped in a 16th funk pattern.
# Durations come straight from ARTICULATIONS: chop 0.12 of a 16th, accents.
chord = [52, 59, 64]
chop_dur = int(STEP * ARTICULATIONS["funk_chop"][1])
accent_dur = int(STEP * ARTICULATIONS["accent"][1])
scratch_dur = int(STEP * ARTICULATIONS["scratch"][1])

u = MusicUnit()
for i in range(16):
    start = i * STEP
    if i % 4 == 0:            # downbeat accent chop
        for p in chord:
            u.add_event(MusicEvent(p, ARTICULATIONS["accent"][0],
                                   start, start + accent_dur))
    elif i % 2 == 1:          # upbeat chop
        for p in chord:
            u.add_event(MusicEvent(p, ARTICULATIONS["funk_chop"][0],
                                   start, start + chop_dur))
    else:                     # dead-string scratch (unpitched texture)
        u.add_event(MusicEvent(52, ARTICULATIONS["scratch"][0],
                               start, start + scratch_dur))

# Palm-muted octave hook in the second half (single notes, defined pitch)
for j, p in enumerate([64, 67, 64, 59]):
    start = 960 + j * 240
    u.add_event(MusicEvent(p, 76, start, start + int(240 * 0.3)))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Drum context
u = MusicUnit()
for start in (0, 960):
    u.add_event(MusicEvent(KIT["kick"], VELOCITIES["kick"], start, start + 120))
for start in (480, 1440):
    u.add_event(MusicEvent(KIT["snare"], VELOCITIES["snare"], start, start + 120))
for start in range(0, BAR, 240):
    u.add_event(MusicEvent(KIT["hat_closed"], VELOCITIES["hat_closed"],
                           start, start + 60))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/muted_guitar_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Audio: instrument SOLO only, FluidR3 via discover_soundfont() -------
from _test.render_audio import render_midi, spectral_buzz_check

wav = "/opt/data/projects/Instruments/_test/muted_guitar_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = muted guitar
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# ---- Stem label vs ACTUAL RenderPipeline GM_PROGRAMS --------------------
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in (27, 28, 29, 30):
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Muted Guitar -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Electric Guitar (muted)", \
    f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Electric_Guitar_muted"

# ---- FluidR3 preset name + audible full range --------------------------
import struct
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
print(f"\nSoundFont: {sf2}")
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pn, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, pn)] = name
sf2_name = preset_names.get((0, MIDI_PROGRAM), "MISSING")
print(f"SF2 preset {MIDI_PROGRAM} -> {sf2_name!r}")
assert sf2_name == "Palm Muted Guitar", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Karplus-Strong smoke test: palm mute = FAST decay ------------------
import numpy as np
from sound.synthesis.karplus_strong import karplus_strong
sr = 22050
audio = karplus_strong(45, 0.6, vel=100,
                       loop_gain=KARPLUS["loop_gain"],
                       width=KARPLUS["width"], sr=sr)
peak = float(np.max(np.abs(audio)))
tail = float(np.sqrt(np.mean(audio[-4410:] ** 2)))  # last 200 ms
ratio = tail / peak if peak else 1.0
print(f"Karplus-Strong muted: peak={peak:.3f} tail_rms/peak={ratio:.3f}")
assert peak > 0, "KS render silent"
assert ratio < 0.05, f"palm mute NOT damped enough (tail ratio {ratio:.3f})"

# ---- RenderPipeline stems: muted guitar + drums on disk ----------------
from sound.render.pipeline import RenderPipeline
out_dir = "/opt/data/projects/Instruments/_test/stems_muted_guitar"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Electric_Guitar_muted" in f for f in stem_files), \
    f"no muted-guitar stem in {stem_files}"
mg_stem = [f for f in stem_files if "Electric_Guitar_muted" in f][0]
assert os.path.getsize(os.path.join(out_dir, mg_stem)) > 40, "empty muted stem"

print("\nALL CHECKS PASSED")
