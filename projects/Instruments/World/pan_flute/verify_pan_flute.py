# -*- coding: utf-8 -*-
"""Verify Pan Flute constants work with musicom engine — SOLO RENDER.

GM78 Pan Flute — South American Andean panpipes (zampoña / siku / antara).
Line instrument: monophonic breath line. Rendered solo ONLY (no unison
doubling — comb-filtering buzz).
"""
import os, sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from World.pan_flute.pan_flute import (
    MIDI_PROGRAM as PF_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq, ADDITIVE_DEFAULTS,
    FM_DEFAULTS,
)

print(f"Pan Flute: program={PF_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE}")
print(f"Pan Flute: A4={midi_to_freq(69):.1f}Hz D4={midi_to_freq(62):.1f}Hz C6={midi_to_freq(84):.1f}Hz E7={midi_to_freq(100):.1f}Hz")
print(f"Pan Flute: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS}")
print(f"Pan Flute: reverb={REVERB_TAIL}s body_eq={EQ_BODY} presence_eq={EQ_PRESENCE} air_eq={EQ_AIR} pan={PAN}")
print(f"Pan Flute: fm_defaults={FM_DEFAULTS}")
print(f"Pan Flute: additive_defaults={ADDITIVE_DEFAULTS}")

# Full engine test: UnitMatrixComposer — ONE VOICE (solo)
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Pan_Flute", program=PF_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Pan Flute SOLO: Andean malta-zone melody (D4-C5-E5-D5-F5-E5-D4)
# Sweet-spot pentatonic line; end flush at BAR (terminal landmark)
u = MusicUnit()
notes = [62, 67, 71, 67, 72, 71, 62]  # D4 G4 B4 G4 C5 B4 D4 (pentatonic in malta)
for i, p in enumerate(notes):
    u.add_event(MusicEvent(p, 82, i * 240, BAR if i == len(notes) - 1 else i * 240 + 180))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

outdir = "/opt/data/projects/Instruments/World/pan_flute"
os.makedirs(outdir, exist_ok=True)
midi_path = os.path.join(outdir, "pan_flute_test.mid")
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO via discover_soundfont() — FluidR3_GM.sf2 preferred
from _test.render_audio import render_midi, spectral_buzz_check

wav = os.path.join(outdir, "pan_flute_test.wav")
render_midi(midi_path, wav, solo=0)  # track 1 (index 0) = Pan Flute solo
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"

ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed)
import inspect, re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  [{PF_PGM}] = {labels[PF_PGM]!r}")
assert labels[PF_PGM] == "Pan Flute", f"stem label mismatch: {labels[PF_PGM]!r}"
assert STEM_LABEL == "Pan_Flute"
print(f"  Pan_Flute STEM_LABEL matches pipeline label ✓")

# FluidR3 preset check
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
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, PF_PGM), "MISSING")
print(f"SF2 preset {PF_PGM} -> {sf2_name!r}")
assert sf2_name == "Pan Flute", f"SF2 preset mismatch: {sf2_name!r}"

# Full RenderPipeline stem render — verify stem file on disk
out_stems = "/opt/data/projects/Instruments/World/pan_flute/stems_pan_flute"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_stems)
stem_files = sorted(os.listdir(out_stems))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_stems, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Pan_Flute" in f for f in stem_files), f"no Pan_Flute stem in {stem_files}"
pan_stem = [f for f in stem_files if "Pan_Flute" in f][0]
assert os.path.getsize(os.path.join(out_stems, pan_stem)) > 40, "empty Pan Flute stem"

print("\nALL CHECKS PASSED")