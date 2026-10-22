# -*- coding: utf-8 -*-
"""Verify Jazz Guitar constants work with musicom engine — SOLO RENDER.

GM26 Electric Guitar (jazz) — archtop hollow-body jazz guitar. Rendered solo
ONLY (no unison doubling — comb-filtering buzz, the 2026-09-01 lesson).

Imports through the REGISTRY (by_name) to prove registration, then builds a
1-bar UnitMatrixComposer with ONE voice and validates zero-drift.
"""
import os, sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ----
from instrument_registry import by_name, by_program, JAZZ_GUITAR

jg = by_name("jazz guitar")
print(f"Registry: by_name('jazz guitar') = {jg}")
print(f"Registry: by_program(26)        = {by_program(26)}")
print(f"Registry: JAZZ_GUITAR constant  = {JAZZ_GUITAR}")
assert jg.midi_program == 26, "registry program mismatch"
assert by_program(26).name == "Electric Guitar (jazz)"
assert JAZZ_GUITAR is jg

from Guitar.jazz_guitar.jazz_guitar import (
    MIDI_PROGRAM as JG_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, KARPLUS_DEFAULTS, MODAL_PRESET, FM_DEFAULTS,
    REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"\nJazz Guitar: program={JG_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE}")
print(f"Jazz Guitar: A4={midi_to_freq(69):.1f}Hz E2={midi_to_freq(40):.1f}Hz C3={midi_to_freq(48):.1f}Hz C5={midi_to_freq(72):.1f}Hz E6={midi_to_freq(76):.1f}Hz")
print(f"Jazz Guitar: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS}")
print(f"Jazz Guitar: reverb={REVERB_TAIL}s body_eq={EQ_BODY} presence_eq={EQ_PRESENCE} air_eq={EQ_AIR} pan={PAN}")
print(f"Jazz Guitar: karplus_defaults={KARPLUS_DEFAULTS}")

# ---- Full engine test: UnitMatrixComposer — ONE VOICE (solo) ----
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Jazz_Guitar", program=JG_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Jazz Guitar SOLO: Wes-style octave-melody line in the sweet spot
# (C3-C5); thumb-attack octaves on beats 1, 3; comping chord stroke on 2&4.
# End flush at BAR (terminal landmark).
u = MusicUnit()
events = [
    # octave melody (root + octave = the Wes texture), in sweet spot
    (60, 84),  # C3+C5
    (64, 83),  # E3+E5
    (67, 82),  # G3+G5
    (64, 83),  # E3+E5
    (62, 84),  # D3+D5
    (67, 82),  # G3+G5
    (60, 84),  # C3+C5
]
for i, (p, vel) in enumerate(events):
    start = i * 240
    end = BAR if i == len(events) - 1 else i * 240 + 200
    u.add_event(MusicEvent(p, vel, start, end))
    u.add_event(MusicEvent(p + 12, vel - 6, start, end))  # octave double
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

outdir = "/opt/data/projects/Instruments/Guitar/jazz_guitar"
os.makedirs(outdir, exist_ok=True)
midi_path = os.path.join(outdir, "jazz_guitar_test.mid")
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() — FluidR3_GM.sf2 preferred ----
from _test.render_audio import render_midi, spectral_buzz_check

wav = os.path.join(outdir, "jazz_guitar_test.wav")
render_midi(midi_path, wav, solo=0)  # track 1 (index 0) = Jazz Guitar solo
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"

ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# ---- Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed) ----
import inspect, re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  [{JG_PGM}] = {labels[JG_PGM]!r}")
assert labels[JG_PGM] == "Electric Guitar (jazz)", f"stem label mismatch: {labels[JG_PGM]!r}"
assert STEM_LABEL == "Electric_Guitar_jazz"
print(f"  STEM_LABEL matches pipeline label ('Electric_Guitar_jazz') ✓")
print(f"  Note: FluidR3 preset 26 = 'Jazz Guitar' (common name) vs pipeline")
print(f"  'Electric Guitar (jazz)' (GM2 spelling) — cosmetic, no routing impact")

# ---- FluidR3 preset check ----
from sound.render.fluidsynth import discover_soundfont
sf2_path = discover_soundfont()
print(f"\nSoundFont: {sf2_path}")
import struct
data = open(sf2_path, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, JG_PGM), "MISSING")
print(f"SF2 preset {JG_PGM} -> {sf2_name!r}")
assert sf2_name == "Jazz Guitar", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — verify stem file on disk ----
out_stems = os.path.join(outdir, "stems_jazz_guitar")
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_stems)
stem_files = sorted(os.listdir(out_stems))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_stems, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Electric_Guitar_jazz" in f for f in stem_files), \
    f"no Electric_Guitar_jazz stem in {stem_files}"
jg_stem = [f for f in stem_files if "Electric_Guitar_jazz" in f][0]
assert os.path.getsize(os.path.join(out_stems, jg_stem)) > 40, "empty Jazz Guitar stem"

# ---- Karplus-Strong ring character test (the jazz guitar identity) ----
# loop_gain 0.9975 (flatwound ring) must out-ring the 0.990 dull control
# in the 1.0-2.0 s window (pre-fade; KS fades only the last 10%).
import numpy as np
from sound.synthesis.karplus_strong import karplus_strong

for lg in (0.9975, 0.990):
    audio = karplus_strong(pitch=60, dur=3.0, vel=90, loop_gain=lg)
    peak = np.max(np.abs(audio))
    win = audio[int(1.0 * 44100):int(2.0 * 44100)]
    tail_rms = np.sqrt(np.mean(win ** 2))
    ratio = tail_rms / peak if peak > 0 else 0.0
    print(f"KS ring: loop_gain={lg} -> late(1-2s) rms/peak={ratio:.4f}")
    assert peak > 0, "KS render silent"
ring_hi = None
ring_lo = None
for lg in (0.9975, 0.990):
    audio = karplus_strong(pitch=60, dur=3.0, vel=90, loop_gain=lg)
    win = audio[int(1.0 * 44100):int(2.0 * 44100)]
    ratio = np.sqrt(np.mean(win ** 2)) / max(np.max(np.abs(audio)), 1e-9)
    if lg == 0.9975:
        ring_hi = ratio
    else:
        ring_lo = ratio
assert ring_hi > ring_lo, f"jazz ring {ring_hi} NOT above dull control {ring_lo}"
print(f"Jazz guitar ring advantage: {ring_hi:.4f} vs dull control {ring_lo:.4f} "
      f"({ring_hi / max(ring_lo, 1e-9):.1f}x) ✓")

print("\nALL CHECKS PASSED")
