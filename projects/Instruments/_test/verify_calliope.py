# -*- coding: utf-8 -*-
"""Verify Calliope (GM82, Lead 3) constants through the registry + audio render.

Structural template: _test/verify_synth_bass_2.py.
Audio render: INSTRUMENT SOLO ONLY (one melodic voice, one track) — the
2026-09-01 comb-filter rule. A drum-kit voice rides along for context but is
NOT part of the solo render.
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# --- prove REGISTRATION: import through the registry, not the module -----
from instrument_registry import by_name, by_program, CALIOPE

from Synth.calliope.calliope import (
    MIDI_PROGRAM as CAL_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, SYNTHESIS_DEFAULTS, FM_DEFAULTS,
    ADDITIVE_DEFAULTS, AIRPIPE_DEFAULTS, REVERB_TAIL, EQ_BODY, EQ_PRESENCE,
    EQ_AIR, PAN, midi_to_freq,
)

assert CALIOPE is by_name("calliope")
assert CALIOPE is by_name("LEAD 3 (CALLIOPE)")
assert by_program(82) is CALIOPE
assert CALIOPE.midi_program == 82
assert CALIOPE.name == "Lead 3 (calliope)"
print(f"Registry: {CALIOPE}")
print(f"Calliope: program={CAL_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"sweet={CALIOPE.sweet_spot} A4={midi_to_freq(69):.1f}Hz")
print(f"Calliope: zones={ZONES}")
print(f"Calliope: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"reverb={REVERB_TAIL}s pan={PAN}")
print(f"Calliope: C5={midi_to_freq(72):.2f}Hz G5={midi_to_freq(79):.2f}Hz "
      f"C6={midi_to_freq(84):.2f}Hz")

# --- engine test: 1 bar, 1 section ---------------------------------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES, beat_pattern

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Calliope", program=CAL_PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)         # context only
comp.add_section("A", bars=1)

# Carnival tune in C (mid register, chiff blips + a trill + accents),
# terminal note flush at BAR:
# C5 G5 C6 G5(acc) | G5 E5 C5 G4 ...
line = [
    (72, 78, 0, 360),      # C5 downbeat pipe
    (76, 74, 360, 720),    # E5
    (79, 76, 720, 1080),   # G5
    (84, 88, 1080, 1200),  # C6 accent — the calliope yell
    (79, 74, 1200, 1440),  # G5
    (76, 76, 1440, 1680),  # E5
    (72, 80, 1680, 1800),  # C5 chiff blip
    (67, 72, 1800, BAR),   # G4, terminal note ends flush at BAR
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

midi_path = "/opt/data/projects/Instruments/_test/calliope_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
msize = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# --- audio: SOLO calliope only, FluidR3 via discover_soundfont -----------
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print(f"SoundFont: {sf2}")
assert sf2 and "FluidR3" in sf2, f"expected FluidR3, got {sf2}"

wav = "/opt/data/projects/Instruments/_test/calliope_test.wav"
render_midi(midi_path, wav, solo=0)          # voice 0 = Calliope
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
print(f"\nStem label: GM_PROGRAMS[{CAL_PGM}] = {labels[CAL_PGM]!r}")
assert labels[CAL_PGM] == "Lead 3 (calliope)", f"stem label mismatch: {labels[CAL_PGM]!r}"
assert STEM_LABEL == "Lead_3_calliope"

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
sf2_name = preset_names.get((0, CAL_PGM), "MISSING")
print(f"SF2 preset {CAL_PGM} -> {sf2_name!r}")
assert sf2_name == "Calliope Lead", f"SF2 preset mismatch: {sf2_name!r}"

# --- RenderPipeline stem render on disk ---------------------------------
out_dir = "/opt/data/projects/Instruments/_test/stems_calliope"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Lead_3_calliope" in f for f in stem_files), f"no Lead_3_calliope stem: {stem_files}"
stem = [f for f in stem_files if "Lead_3_calliope" in f][0]
assert os.path.getsize(os.path.join(out_dir, stem)) > 40, "empty calliope stem"

# --- PhaseModSynth engine smoke test (primary synthesis) ----------------
import numpy as np
from sound.synthesis.phase_mod import PhaseModSynth

sr = 22050
pm = PhaseModSynth(sample_rate=sr)
audio = pm.render_note(freq=midi_to_freq(72), duration=1.0, **FM_DEFAULTS)  # C5
peak = float(np.max(np.abs(audio)))
head = float(np.sqrt(np.mean(audio[: int(0.2 * sr)] ** 2)))
mid = float(np.sqrt(np.mean(audio[int(0.25 * sr):int(0.75 * sr)] ** 2)))
tail = float(np.sqrt(np.mean(audio[-int(0.2 * sr):] ** 2)))
print(f"\nPhaseModSynth C5 (depth {FM_DEFAULTS['mod_depth']}): "
      f"peak={peak:.3f} head_rms={head:.4f} mid_rms={mid:.4f} tail_rms={tail:.4f}")
assert peak > 0.01, "phase_mod render silent"
assert mid > 0.001, "pipe note collapses (sustain does not hold)"

# --- AirPipe physical-model smoke test (tertiary synthesis) -------------
from sound.synthesis.air_pipe import AirPipe

pipe = AirPipe(midi_note=72, pressure=AIRPIPE_DEFAULTS["pressure"],
               stopped=AIRPIPE_DEFAULTS["stopped"],
               length_scale=AIRPIPE_DEFAULTS["length_scale"],
               sample_rate=sr, seed=3)
pa = pipe.render(1.0)
pp = float(np.max(np.abs(pa)))
prms = float(np.sqrt(np.mean(pa ** 2)))
print(f"AirPipe C5 (pressure {AIRPIPE_DEFAULTS['pressure']}): "
      f"peak={pp:.3f} rms={prms:.4f}")
assert pp > 0.01, "air_pipe render silent"

# --- Additive alternative smoke test -------------------------------------
from sound.synthesis.additive import SoundWave

add = SoundWave(sample_rate=sr, duration=1.0, frequency=midi_to_freq(72))
w = ADDITIVE_DEFAULTS["harmonic_weights"]
wsum = sum(w)
add.apply_overtones([x / wsum for x in w])      # API requires sum == 1.0
add.get_adsr_weights(length=[0.02, 0.1, 0.78, 0.1],
                     decay=[0.075, 0.02, 0.005, 0.1],
                     sustain_level=0.8)
data = add.fundamental * add.weights
ap = float(np.max(np.abs(data)))
print(f"Additive C5: peak={ap:.3f}")
assert ap > 0.01, "additive render silent"

print("\nALL CHECKS PASSED")
