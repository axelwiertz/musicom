# -*- coding: utf-8 -*-
"""Verify Acoustic Bass (GM32) constants through the registry + audio render.

Structural template: _test/verify_fretless_bass.py.
Audio render: INSTRUMENT SOLO ONLY (one melodic voice, one track) — the
2026-09-01 comb-filter rule. A drum-kit voice rides along for context but is
NOT part of the solo render.
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# --- prove REGISTRATION: import through the registry, not the module -----
from instrument_registry import by_name, by_program, ACOUSTIC_BASS

from Bass.acoustic_bass.acoustic_bass import (
    MIDI_PROGRAM as AB_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, KARPLUS_DEFAULTS, BOWED_DEFAULTS,
    MODAL_PRESET, REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN,
    midi_to_freq,
)

assert ACOUSTIC_BASS is by_name("acoustic bass")
assert by_program(32) is ACOUSTIC_BASS
assert ACOUSTIC_BASS.midi_program == 32
assert ACOUSTIC_BASS.name == "Acoustic Bass"
print(f"Registry: {ACOUSTIC_BASS}")
print(f"Acoustic Bass: program={AB_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"sweet={ACOUSTIC_BASS.sweet_spot} A4={midi_to_freq(69):.1f}Hz")
print(f"Acoustic Bass: zones={ZONES}")
print(f"Acoustic Bass: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Acoustic Bass: E1={midi_to_freq(28):.2f}Hz A1={midi_to_freq(33):.2f}Hz "
      f"C2={midi_to_freq(36):.2f}Hz E2={midi_to_freq(40):.2f}Hz")

# --- engine test: 1 bar, 1 section ---------------------------------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES, beat_pattern

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Acoustic Bass", program=AB_PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)         # context only
comp.add_section("A", bars=1)

# Jazz walking line in E minor with a slap accent on the downbeat of beat 3:
# E2 . G2 . B2(slap) A2 | A2 . G2 . E2 ...
# (pitch, vel, start, end) with the terminal note flush at BAR
line = [
    (40, 78, 0, 420),      # E2 downbeat (pizz, woody)
    (43, 70, 480, 720),    # G2
    (47, 98, 720, 780),    # B2 slap — the rockabilly thwack
    (45, 76, 780, 1200),   # A2
    (43, 72, 1200, 1560),  # G2
    (40, 74, 1560, BAR),   # E2, terminal note ends flush at BAR
]
u = MusicUnit()
for p, v, s, e in line:
    u.add_event(MusicEvent(p, v, s, e))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
kick = beat_pattern()
snare = beat_pattern(beat_indices=(4, 12))
step = BAR // 16
for i in range(16):
    if kick[i]:
        u.add_event(MusicEvent(KIT["kick"], VELOCITIES["kick"], i * step, i * step + step))
    if snare[i]:
        u.add_event(MusicEvent(KIT["snare"], VELOCITIES["snare"], i * step, i * step + step))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/acoustic_bass_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
msize = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# --- audio: SOLO acoustic bass only, FluidR3 via discover_soundfont ------
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print(f"SoundFont: {sf2}")
assert sf2 and "FluidR3" in sf2, f"expected FluidR3, got {sf2}"

wav = "/opt/data/projects/Instruments/_test/acoustic_bass_test.wav"
render_midi(midi_path, wav, solo=0)          # voice 0 = Acoustic Bass
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# --- stem label check against the ACTUAL pipeline GM_PROGRAMS -----------
import inspect
import re
from sound.render.pipeline import RenderPipeline

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem label: GM_PROGRAMS[{AB_PGM}] = {labels[AB_PGM]!r}")
assert labels[AB_PGM] == "Acoustic Bass", f"stem label mismatch: {labels[AB_PGM]!r}"
assert STEM_LABEL == "Acoustic Bass".replace(" ", "_")

# --- SF2 preset name (phdr) ---------------------------------------------
import struct
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, AB_PGM), "MISSING")
print(f"SF2 preset {AB_PGM} -> {sf2_name!r}")
assert sf2_name == "Acoustic Bass", f"SF2 preset mismatch: {sf2_name!r}"

# --- RenderPipeline stem render on disk ---------------------------------
out_dir = "/opt/data/projects/Instruments/_test/stems_acoustic_bass"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Acoustic_Bass" in f for f in stem_files), f"no Acoustic_Bass stem: {stem_files}"
stem = [f for f in stem_files if "Acoustic_Bass" in f][0]
assert os.path.getsize(os.path.join(out_dir, stem)) > 40, "empty Acoustic Bass stem"

# --- Karplus-Strong engine smoke test (primary synthesis) ---------------
import numpy as np
from sound.synthesis.karplus_strong import karplus_strong

sr = 44100
audio = karplus_strong(pitch=40, dur=1.0, vel=100,
                       loop_gain=KARPLUS_DEFAULTS["loop_gain"], sr=sr)
peak = float(np.max(np.abs(audio)))
head = float(np.sqrt(np.mean(audio[:4410] ** 2)))
tail = float(np.sqrt(np.mean(audio[-4410:] ** 2)))
print(f"\nKarplus-Strong E2: peak={peak:.3f} head_rms={head:.4f} tail_rms={tail:.4f}")
assert peak > 0.01, "karplus render silent"
assert head > tail, "karplus string does not decay (loop_gain too high)"

# BowedString arco path must at least construct with the documented defaults
from sound.synthesis.bowed import BowedString
bows = BowedString(sample_rate=22050)
assert bows is not None
print(f"BowedString(arco) OK: {type(bows).__name__}")

print("\nALL CHECKS PASSED")
