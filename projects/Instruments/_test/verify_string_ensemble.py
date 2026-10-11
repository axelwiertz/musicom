# -*- coding: utf-8 -*-
"""Verify String Ensemble 1 (GM48) constants work with musicom engine.

SOLO render (2026-09-01 lesson): the audio-render voice stack is the
instrument SOLO ONLY — one voice, one track. NO second melodic patch on
the same pitches (unison doubling = comb-filtering buzz).
"""
import os
import re
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# === 1. Import THROUGH the registry (proves registration) ===
from instrument_registry import by_name, by_program, STRING_ENSEMBLE

assert STRING_ENSEMBLE.midi_program == 48
assert by_name("string ensemble") is STRING_ENSEMBLE
assert by_name("string ensemble 1") is STRING_ENSEMBLE
assert by_program(48) is STRING_ENSEMBLE
print(f"Registry: by_name('string ensemble') -> {by_name('string ensemble')}")
print(f"Registry: by_program(48) -> {by_program(48)}")
print(f"Registry: STRING_ENSEMBLE.stem_label = {STRING_ENSEMBLE.stem_label!r}")
print(f"Registry: sweet_spot={STRING_ENSEMBLE.sweet_spot} "
      f"in_sweet_spot(72)={STRING_ENSEMBLE.in_sweet_spot(72)} "
      f"in_sweet_spot(20)={STRING_ENSEMBLE.in_sweet_spot(20)}")

from Strings.string_ensemble.string_ensemble import (
    MIDI_PROGRAM, GM_NAME, STEM_LABEL, SOLO_RANGE, SWEET_SPOT, ZONES,
    ARTICULATIONS, SYNTHESIS, SYNTHESIS_DEFAULTS, ADDITIVE_HARMONICS,
    REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
print(f"\n{GM_NAME}: program={MIDI_PROGRAM} range={STRING_ENSEMBLE.range_min}-"
      f"{STRING_ENSEMBLE.range_max} A4={midi_to_freq(69):.1f}Hz "
      f"C2={midi_to_freq(36):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"C6={midi_to_freq(84):.1f}Hz")
print(f"zones={ZONES} arts={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"synth_defaults={SYNTHESIS_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"additive_harmonics_keys={list(ADDITIVE_HARMONICS)}")

# === 2. Engine test: UnitMatrixComposer, 1 bar, 1 section, SOLO voice ===
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("StringEnsemble", program=MIDI_PROGRAM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# String Ensemble SOLO: sustained section chord in the sweet spot
# (C4-E4-G4-C5), one voice, one track — NO unison doubling, no second
# melodic patch. Ends flush at BAR (terminal landmark — zero-drift).
u = MusicUnit()
for p in [60, 64, 67, 72]:
    u.add_event(MusicEvent(p, 82, 0, BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/string_ensemble_test.mid"
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# === 3. Render to WAV via discover_soundfont() (FluidR3 preferred) ===
from _test.render_audio import render_midi_solo, spectral_buzz_check

wav = "/opt/data/projects/Instruments/_test/string_ensemble_test.wav"
render_midi_solo(midi_path, wav, instrument_track=0)  # voice 0 = the solo
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# === 4. Stem label check against ACTUAL pipeline GM_PROGRAMS ===
import inspect
from sound.render.pipeline import RenderPipeline

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  String Ensemble -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "String Ensemble 1", \
    f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "String_Ensemble_1", f"STEM_LABEL mismatch: {STEM_LABEL!r}"
print(f"  STEM_LABEL = {STEM_LABEL!r} (matches pipeline safe_name — no quirk)")

# === 5. SF2 preset name for program 48 (verified from phdr chunk) ===
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
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, MIDI_PROGRAM), "MISSING")
print(f"SF2 preset {MIDI_PROGRAM} -> {sf2_name!r}")
assert sf2_name == "Strings", f"SF2 preset mismatch: {sf2_name!r}"

# === 6. Additive engine smoke test (section pad sustains — no collapse) ===
from sound.synthesis.additive import SoundWave
sw = SoundWave(sample_rate=22050, duration=2.0, frequency=261.6)  # C4
_factors = ADDITIVE_HARMONICS["section_full"]
_factors = [f / sum(_factors) for f in _factors]  # engine requires sum == 1.0
sw.apply_overtones(_factors)
sw.get_adsr_weights(length=[0.10, 0.10, 0.70, 0.10],
                    decay=[0.01, 0.001, 0.0001, 0.05], sustain_level=0.8)
import numpy as np
audio = sw.fundamental.astype(float) * sw.weights[:len(sw.fundamental)]
peak = np.max(np.abs(audio)) if len(audio) else 0.0
# late-window ratio: pad should NOT collapse — late(1.0-1.5s) rms near sustain
late = audio[int(1.0 * 22050):int(1.5 * 22050)]
late_rms = np.sqrt(np.mean(late ** 2)) if len(late) else 0.0
ratio = late_rms / peak if peak > 0 else 1.0
print(f"\nAdditive string-ensemble pad: peak={peak:.3f} "
      f"late_rms/peak(1.0-1.5s)={ratio:.3f}")
assert peak > 0, "additive pad render silent"
assert ratio > 0.05, f"pad collapsed (late ratio {ratio:.3f}) — sustain failed"

# === 7. Empirical FluidR3 sweep already run (see _sweep_gm48.py) ===
print("\nEmpirical sweep (pre-run): preset 48 audible 24-96 (13/13), silent at 102+")

print("\nALL CHECKS PASSED")