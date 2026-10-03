# -*- coding: utf-8 -*-
"""Verify Muted Trumpet constants work with musicom engine.

Solo render only — no unison doubling (comb-filtering fix 2026-09-01).
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Brass.muted_trumpet.muted_trumpet import (
    MIDI_PROGRAM as MT_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Muted Trumpet: program={MT_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Muted Trumpet: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm={FM_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Muted Trumpet: A2={midi_to_freq(45):.1f}Hz C4={midi_to_freq(60):.1f}Hz C5={midi_to_freq(72):.1f}Hz C6={midi_to_freq(84):.1f}Hz")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("MutedTrumpet", program=MT_PGM, channel=0)
comp.add_voice("DrumKit", program=0, channel=9)  # drums on channel 9, low context
comp.add_section("A", bars=1)

BAR = 1920

# Muted Trumpet: sweet-spot melody line on channel 0, flush at BAR
u = MusicUnit()
for i, p in enumerate([67, 69, 72, 74, 79, 74, 72, 69]):
    u.add_event(MusicEvent(p, 82, i * 240, BAR if i == 7 else i * 240 + 220))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Drums: low bass drum on channel 9 (GM percussion) for rhythmic context
# at least an octave below — no unison doubling
u = MusicUnit()
# Kick drum (MIDI 36) on the 1, snare (38) on 2
u.add_event(MusicEvent(36, 95, 0, 120))
u.add_event(MusicEvent(38, 80, BAR // 2, BAR // 2 + 120))
u.add_event(MusicEvent(36, 95, BAR - 1, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/muted_trumpet_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO — muted trumpet only (voice track 1, after tempo track 0)
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/muted_trumpet_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Muted Trumpet (first voice)
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
print(f"  [{MT_PGM}] = {labels[MT_PGM]!r}")
print(f"  Muted Trumpet -> {labels[MT_PGM]!r}")
assert labels[MT_PGM] == "Muted Trumpet", f"stem label mismatch: {labels[MT_PGM]!r}"
assert STEM_LABEL == "Muted Trumpet"

# SF2 preset name for program 59 (from phdr chunk)
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
import struct
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, MT_PGM), "MISSING")
print(f"SF2 preset {MT_PGM} -> {sf2_name!r}")
assert sf2_name == "Muted Trumpet", f"SF2 preset mismatch: {sf2_name!r}"

# Full RenderPipeline stem render — muted trumpet stem label on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_muted_trumpet"
pipeline = RenderPipeline(
    fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
    soundfont_path=sf2,
    gain=1.2
)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Muted_Trumpet" in f for f in stem_files), f"no Muted Trumpet stem in {stem_files}"
mt_stem = [f for f in stem_files if "Muted_Trumpet" in f][0]
assert os.path.getsize(os.path.join(out_dir, mt_stem)) > 40, "empty Muted Trumpet stem"

# PhaseModSynth smoke test: FM brass parameters
# Muted trumpet: mod_freq_ratio 2.0, mod_depth 2.5 => nasal focused tone
from sound.synthesis.phase_mod import PhaseModSynth
pms = PhaseModSynth(sample_rate=22050)
audio = pms.render_note(69, 0.5, carrier_shape="saw", mod_freq_ratio=2.0,
                        mod_depth=2.5, attack=0.03, release=0.12)
import numpy as np
peak = np.max(np.abs(audio))
print(f"\nPhaseModSynth Muted Trumpet (G4, 0.5s): peak={peak:.3f}")
assert peak > 0, "phase_mod muted trumpet render silent"

print("\nALL CHECKS PASSED")