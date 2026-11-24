# -*- coding: utf-8 -*-
"""Verify Pad 3 (polysynth) (GM90) constants work with the musicom engine.

Checks, in order:
1. constants imported THROUGH THE REGISTRY (proves registration)
2. UnitMatrixComposer 1 bar / 1 section: Polysynth Pad SOLO on ch0
   (sustained chord pad) + drum-kit context on ch9 — NO second melodic patch
   doubling the same pitches (2026-09-01 comb-filter rule)
3. zero-drift validate()
4. MIDI export + size gate
5. FluidSynth SOLO render via discover_soundfont() + size + buzz gate
6. RenderPipeline stem label on disk
7. PolySynth engine smoke test (sustained analog pad, no natural decay)
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

from instrument_registry import by_name, POLYSYNTH_PAD

SYN = POLYSYNTH_PAD
print(f"Registered: {SYN!r}")
print(f"  program={SYN.midi_program} gm={SYN.gm_name!r} stem={SYN.stem_label!r}")
print(f"  range={SYN.range_min}-{SYN.range_max} solo={SYN.solo_range} "
      f"sweet={SYN.sweet_spot}")
print(f"  synth={SYN.synthesis!r} poly={SYN.polysynth_defaults}")
print(f"  reverb={SYN.reverb_tail}s eq_body={SYN.eq_body} "
      f"eq_presence={SYN.eq_presence} eq_air={SYN.eq_air} pan={SYN.pan}")
assert SYN.midi_program == 90
assert by_name("polysynth pad") is SYN
assert by_name("Pad 3 (polysynth)") is SYN
assert SYN.in_sweet_spot(72) and not SYN.in_sweet_spot(24)

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=104, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Pad 3 (polysynth)", program=SYN.midi_program, channel=0)
comp.add_voice("Drums", program=0, channel=9)
comp.add_section("A", bars=1)

BAR = 1920

# Voice 0: sustained pad chord Cmaj7 (C4 E4 G4 B4) held the whole bar,
# terminal landmark flush at BAR. No decay — that is the polysynth-pad point.
u = MusicUnit()
for p in (60, 64, 67, 71):
    u.add_event(MusicEvent(p, 72, 0, BAR))
comp.set_unit(0, 0, u)

# Voice 1: drum context (ch9), must end flush at BAR for zero-drift
u = MusicUnit()
for start, pitch, vel in ((0, 36, 96), (480, 42, 70), (960, 38, 92),
                          (1440, 42, 70)):
    u.add_event(MusicEvent(pitch, vel, start, start + 120))
u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/polysynth_pad_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# SOLO render (track 0 = Pad 3 polysynth) via discover_soundfont()
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/polysynth_pad_test.wav"
render_midi(midi_path, wav, solo=0)
from sound.render.fluidsynth import discover_soundfont
print(f"SoundFont: {discover_soundfont()}")
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed)
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem label: GM_PROGRAMS[{SYN.midi_program}] = "
      f"{labels[SYN.midi_program]!r}")
assert labels[SYN.midi_program] == "Pad 3 (polysynth)", \
    f"stem label mismatch: {labels[SYN.midi_program]!r}"
assert SYN.stem_label == "Pad_3_polysynth"

# Full RenderPipeline stem render — label on disk
sf2 = discover_soundfont()
fluidsynth = os.environ.get(
    "MUSICOM_FLUIDSYNTH", "/opt/data/micromamba/envs/musicom/bin/fluidsynth")
out_dir = "/opt/data/projects/Instruments/_test/stems_polysynth_pad"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Pad_3_polysynth" in f for f in stem_files), stem_files
stem = [f for f in stem_files if "Pad_3_polysynth" in f][0]
assert os.path.getsize(os.path.join(out_dir, stem)) > 40

# PolySynth engine smoke test: sustained analog pad tone (slow attack,
# sustain 0.85, NO natural decay — the pad holds flat while gated). Measure
# RMS inside the sustain plateau at two windows (0.5-0.7 s vs 1.3-1.5 s):
# a flat pad keeps the ratio ~1.0; a decaying voice would drop toward 0.
import numpy as np
from sound.synthesis.polysynth import Oscillator, EnvelopeGenerator

sr = 22050
osc = Oscillator(sample_rate=sr)
osc.waveform = "saw"
n = int(1.5 * sr)
sig = osc.generate(220.0, n)
env = EnvelopeGenerator(sample_rate=sr)
env.set(attack=0.35, decay=0.2, sustain=0.85, release=0.6)
e = env.generate(1.5, gate_off=1.5)
audio = sig * e
peak = float(np.max(np.abs(audio)))
def rms(a, t0, t1):
    return float(np.sqrt(np.mean(a[int(t0 * sr):int(t1 * sr)] ** 2)))
early_rms = rms(audio, 0.5, 0.7)
late_rms = rms(audio, 1.3, 1.5)
flat_ratio = late_rms / early_rms if early_rms > 0 else 0.0
print(f"\nPolySynth: peak={peak:.3f} early(0.5-0.7s)={early_rms:.3f} "
      f"late(1.3-1.5s)={late_rms:.3f} late/early={flat_ratio:.3f}")
assert peak > 0, "poly render silent"
assert flat_ratio > 0.7, "polysynth pad must SUSTAIN (flat), not decay"

print("\nALL CHECKS PASSED")
