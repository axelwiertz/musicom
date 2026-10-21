# -*- coding: utf-8 -*-
"""Verify Drawbar Organ (GM16) — registration + engine + audio, SOLO render.

Contract:
  * constants imported THROUGH the registry (`by_name`) => registration proof
  * UnitMatrixComposer, 1 bar / 1 section, ONE voice (no unison doubling)
  * zero-drift validate, MIDI export, FluidSynth WAV via discover_soundfont()
  * RenderPipeline stem label check against the real GM_PROGRAMS list
"""
import inspect
import os
import re
import sys

sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")

import numpy as np

from instrument_registry import ALL_INSTRUMENTS, by_name, by_program, registry_table
from Keys.drawbar_organ.drawbar_organ import (
    ADDITIVE_ENVELOPE, ADDITIVE_HARMONICS, DRAWBAR_FOOTAGES, DRAWBAR_PRESETS,
    drawbar_harmonics, midi_to_freq,
)

ORGAN = by_name("drawbar organ")
assert ORGAN is ALL_INSTRUMENTS["drawbar_organ"]

print(f"Drawbar Organ: program={ORGAN.midi_program} gm={ORGAN.gm_name!r} "
      f"stem={ORGAN.stem_label!r} range={ORGAN.range_min}-{ORGAN.range_max} "
      f"sweet={ORGAN.sweet_spot} solo={ORGAN.solo_range}")
print(f"Drawbar Organ: zones={ORGAN.zones}")
print(f"Drawbar Organ: art={list(ORGAN.articulations)} synth={ORGAN.synthesis}")
print(f"Drawbar Organ: reverb={ORGAN.reverb_tail}s eq={ORGAN.eq_body},{ORGAN.eq_presence},"
      f"{ORGAN.eq_air} pan={ORGAN.pan}")
print(f"Drawbar Organ: octaves 16'={midi_to_freq(60) * 0.5:.1f}Hz "
      f"8'={midi_to_freq(60):.1f}Hz 4'={midi_to_freq(60) * 2:.1f}Hz (C4 registration)")

assert ORGAN.family == "Keys"
assert ORGAN.midi_program == 16
assert by_program(16) is ORGAN
assert ORGAN.in_sweet_spot(67) and not ORGAN.in_sweet_spot(24)
assert ORGAN.in_range(24) and ORGAN.in_range(89) and not ORGAN.in_range(90)
assert drawbar_harmonics(DRAWBAR_PRESETS["jazz"]) == {0.5: 1.0, 1.5: 1.0, 1.0: 1.0}
assert len(DRAWBAR_FOOTAGES) == 9 and len(DRAWBAR_PRESETS["full"]) == 9

# Registry table row present
table = registry_table()
row = [ln for ln in table.splitlines() if "Drawbar Organ" in ln]
print("\nregistry_table row:", row)
assert row and "| Keys | Drawbar Organ | 16 |" in row[0], "missing registry_table row"

# ---- Engine test: UnitMatrixComposer, 1 voice, 1 bar ------------------------
from structures import MusicEvent, MusicUnit
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("DrawbarOrgan", program=ORGAN.midi_program, channel=0)
comp.add_section("A", bars=1)

# Gospel-style comp line in the sweet spot (G3..G5), key click + staccato
# stabs + one accented sustain; ends flush at BAR (terminal landmark).
prog = [(55, 90, 0, 240), (60, 86, 240, 480), (63, 86, 480, 720), (67, 92, 720, 1200),
        (63, 70, 1200, 1320), (60, 70, 1320, 1440), (55, 96, 1440, BAR)]
u = MusicUnit()
for pitch, vel, start, end in prog:
    u.add_event(MusicEvent(pitch, vel, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/drawbar_organ_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
msize = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# ---- Solo audio render (discover_soundfont, never hardcoded TimGM6mb) -------
from _test.render_audio import render_midi, spectral_buzz_check

wav = "/opt/data/projects/Instruments/_test/drawbar_organ_test.wav"
render_midi(midi_path, wav, solo=0)          # one voice, no doubling
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes, {wsize / 1024:.0f} KB)")
assert wsize > 40, "empty/corrupt WAV"
buzz_ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert buzz_ok, f"buzz in solo render: {rep}"

# ---- Stem label vs the ACTUAL pipeline GM_PROGRAMS list --------------------
from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline

sf2 = discover_soundfont()
print(f"\nSoundFont: {sf2}")
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"  GM_PROGRAMS[16] = {labels[16]!r}  STEM_LABEL = {ORGAN.stem_label!r}")
assert labels[16] == "Drawbar Organ"
assert ORGAN.stem_label == "Drawbar_Organ"
assert labels[16].replace(" ", "_") == ORGAN.stem_label

# SF2 internal preset name (phdr) — cosmetic comparison only
import struct
data = open(sf2, "rb").read()
pos = data.find(b"phdr")
size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
sf2_name = "MISSING"
for i in range(size // 38):
    off = pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pnum, bank = struct.unpack("<HH", data[off + 20:off + 24])
    if pnum == 16 and bank == 0:
        sf2_name = name
        break
print(f"  SF2 preset 16 -> {sf2_name!r} (cosmetic only)")
assert sf2_name != "MISSING"

# RenderPipeline stems on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_drawbar_organ"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems ({len(stem_files)}): {stem_files}")
assert any("Drawbar_Organ" in f for f in stem_files), stem_files
for f in stem_files:
    assert os.path.getsize(os.path.join(out_dir, f)) > 40

# ---- Additive engine: integer drawbar bank (SoundWave, engine API) --------
from sound.synthesis.additive import SoundWave

fac = np.array(ADDITIVE_HARMONICS["jazz"], dtype=float)
fac = list(fac / fac.sum())
sw = SoundWave(sample_rate=22050, duration=0.5, frequency=midi_to_freq(60))
sw.apply_overtones(fac)
sw.get_adsr_weights(
    length=[0.02, 0.0, 0.94, 0.04],   # proportions, must sum to 1.0
    decay=[0.0, 0.0, 0.0, 0.5], sustain_level=ADDITIVE_ENVELOPE["sustain"])
audio = sw.fundamental
peak = float(np.max(np.abs(audio)))
early = float(np.sqrt(np.mean(audio[2000:4000] ** 2)))
late = float(np.sqrt(np.mean(audio[-2000:] ** 2)))
print(f"\nAdditive (jazz bank) C4: peak={peak:.0f} early/late RMS ratio={late / early:.3f}")
assert peak > 0, "additive organ render silent"
assert 0.85 < late / early < 1.05, "tonewheel tone must NOT decay while held"

# ---- True drawbar ratios incl. the 1.5x quint (custom additive sum) --------
reg = drawbar_harmonics(DRAWBAR_PRESETS["jazz"])   # 16' + 5 1/3' + 8'
sr = 22050
t = np.arange(int(sr * 0.5)) / sr
f0 = midi_to_freq(60)
mix = sum(g * np.sin(2 * np.pi * f0 * ratio * t) for ratio, g in reg.items())
mix /= max(np.max(np.abs(mix)), 1e-9)
spec = np.abs(np.fft.rfft(mix))
fr = np.fft.rfftfreq(len(mix), 1 / sr)
def peak_near(f):
    sel = (fr > f * 0.97) & (fr < f * 1.03)
    return float(spec[sel].max()) if sel.any() else 0.0
h8, h16, hq = peak_near(f0), peak_near(f0 * 0.5), peak_near(f0 * 1.5)
print(f"Drawbar 888000000 partials: 8'={h8:.0f} 16'={h16:.0f} 5 1/3'(quint)={hq:.0f}")
assert hq > 0.5 * h8, "quint drawbar (1.5x) missing from the registration"
assert h16 > 0.5 * h8, "sub-octave drawbar (0.5x) missing from the registration"

# ---- Leslie motor model (MOTOR_DEFAULTS) as AM -----------------------------
# A steady tonewheel note is NOT decaying, so an envelope-follower test of the
# kind used for the vibraphone motor cannot work here. AM on a steady carrier
# shows up as sidebands at f0 +/- rate — check those instead.
MOTOR = ORGAN.motor_defaults
t2 = np.arange(int(sr * 2.0)) / sr
mix2 = sum(g * np.sin(2 * np.pi * f0 * ratio * t2) for ratio, g in reg.items())
env = 1.0 - MOTOR["depth"] * 0.5 * (1.0 - np.cos(2 * np.pi * MOTOR["rate_hz"] * t2))
mod = mix2 * env
mspec = np.abs(np.fft.rfft(mod))
mfreq = np.fft.rfftfreq(len(mod), 1 / sr)
def band_peak(f, w=0.6):
    sel = (mfreq >= f - w) & (mfreq <= f + w)
    return float(mspec[sel].max()) if sel.any() else 0.0
carrier = band_peak(f0)
upper = band_peak(f0 + MOTOR["rate_hz"])
lower = band_peak(f0 - MOTOR["rate_hz"])
print(f"Motor: rate={MOTOR['rate_hz']}Hz depth={MOTOR['depth']} "
      f"sidebands/f0 = {upper / carrier:.3f} up, {lower / carrier:.3f} down")
assert upper > 0.05 * carrier and lower > 0.05 * carrier, \
    "Leslie AM produced no measurable sidebands at the motor rate"
assert MOTOR["rate_range_hz"][0] < MOTOR["rate_hz"] < MOTOR["rate_range_hz"][1]

print("\nALL CHECKS PASSED")
