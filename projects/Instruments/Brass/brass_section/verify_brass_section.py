# -*- coding: utf-8 -*-
"""Verify Brass Section constants work with musicom engine — SOLO render."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Brass.brass_section.brass_section import (
    MIDI_PROGRAM, GM_NAME, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, REVERB_TAIL, PAN, midi_to_freq,
)

print(f"Brass Section: program={MIDI_PROGRAM} gm={GM_NAME!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Brass Section: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Brass Section: C4={midi_to_freq(60):.1f}Hz G3={midi_to_freq(55):.1f}Hz C5={midi_to_freq(72):.1f}Hz")

# Full engine test: UnitMatrixComposer with instrument constants — SOLO only
from structures import MusicEvent, MusicUnit
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Brass Section", program=MIDI_PROGRAM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Brass Section: tutti fanfare in the idiomatically rich mid-range
# A fanfare on C4–G4–C5–E5 (60-67-72-76), the classic brass tutti zone
# No unison doubling — solo brass section only
u = MusicUnit()
fanfare_notes = [  # classic fanfare: C4-G4-C5-E5-G5
    (60, 85, 0, 480),      # C4 — ensemble bass
    (67, 82, 240, 720),    # G4 — mid tutti
    (72, 88, 480, 960),    # C5 — trumpet top
    (76, 80, 720, 1440),   # E5 — bright top
    (67, 90, 960, BAR),    # G4 — sustained final
]
for p, v, s, e in fanfare_notes:
    u.add_event(MusicEvent(p, v, s, e))
# zero-drift terminal landmark
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/Brass/brass_section/brass_section_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render to WAV via FluidSynth using discover_soundfont() — SOLO
from _test.render_audio import render_midi, spectral_buzz_check

wav = "/opt/data/projects/Instruments/Brass/brass_section/brass_section_test.wav"
render_midi(midi_path, wav, solo=0)  # instrument SOLO (buzz fix)
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
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [61, 56, 57, 58, 59, 60]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Brass Section -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Brass Section", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"

print("\nALL CHECKS PASSED")