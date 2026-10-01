# -*- coding: utf-8 -*-
"""Verify Tenor Saxophone constants work with musicom engine (SOLO)."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Woodwind.tenor_sax.tenor_sax import (
    MIDI_PROGRAM as TS_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Tenor Sax: program={TS_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Tenor Sax: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm_depth={FM_DEFAULTS['mod_depth']} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Tenor Sax: A2={midi_to_freq(45):.1f}Hz C4={midi_to_freq(60):.1f}Hz C5={midi_to_freq(72):.1f}Hz C6={midi_to_freq(84):.1f}Hz")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("TenorSax", program=TS_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Tenor Sax: sweet-spot lead line — single melodic voice, NO unison doubling
# Play a short bluesy line in the tenor's sweet spot (F3-F5)
u = MusicUnit()
notes = [65, 67, 69, 72, 74, 72, 69]  # F3-G3-A3-C4-D4-C4-A3
for i, p in enumerate(notes):
    start = i * 240
    dur = 220 if i < 6 else 0  # last note extends to BAR
    u.add_event(MusicEvent(p, 82, start, start + dur))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

# Export MIDI
import os
outdir = "/opt/data/projects/Instruments/Woodwind/tenor_sax"
midi_path = os.path.join(outdir, "tenor_sax_test.mid")
os.makedirs(outdir, exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO via discover_soundfont() — NO secondary patch doubling
from _test.render_audio import render_midi_solo, spectral_buzz_check

wav = os.path.join(outdir, "tenor_sax_test.wav")
render_midi_solo(midi_path, wav, instrument_track=0)  # track 0 = first voice (Tenor Sax solo, after tempo track)
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
print(f"\nStem label check (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  index [66] = {labels[66]!r}")
print(f"  Expected label: {GM_NAME!r} -> stem file trackXX_{STEM_LABEL!r}.wav")
assert labels[TS_PGM] == "Tenor Sax", f"stem label mismatch: {labels[TS_PGM]!r}"
assert STEM_LABEL == "Tenor_Sax"

# RenderPipeline stem render — verify stem label on disk
out_stems = os.path.join(outdir, "stems_tenor_sax")
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
pipeline = RenderPipeline(soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_stems)
stem_files = sorted(os.listdir(out_stems))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_stems, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Tenor_Sax" in f for f in stem_files), f"no Tenor_Sax stem in {stem_files}"
ts_stem = [f for f in stem_files if "Tenor_Sax" in f][0]
assert os.path.getsize(os.path.join(out_stems, ts_stem)) > 40, "empty Tenor Sax stem"

# PhaseModSynth smoke test — conical single-reed spectrum
from sound.synthesis.phase_mod import PhaseModSynth
pm = PhaseModSynth(sample_rate=22050)
params = dict(FM_DEFAULTS)
audio = pm.render_note(freq=midi_to_freq(72), duration=0.5, **params)
import numpy as np
peak = np.max(np.abs(audio))
# Late tail (last 100 ms) — sustained note should NOT decay to zero
tail_rms = np.sqrt(np.mean(audio[-2205:] ** 2))
tail_ratio = tail_rms / peak if peak > 0 else 1.0
print(f"\nPhaseModSynth C5={midi_to_freq(72):.1f}Hz: peak={peak:.3f} tail_rms/peak={tail_ratio:.3f}")
assert peak > 0, "phase mod render silent"
# Saw-based reed should sustain (breath-driven), so tail should be non-trivial
assert tail_ratio > 0.05, f"tenor sax tail too quiet ({tail_ratio:.3f}) — expected sustained character"

print("\nALL CHECKS PASSED")