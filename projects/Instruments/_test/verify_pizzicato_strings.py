# -*- coding: utf-8 -*-
"""Verify Pizzicato Strings constants work with musicom engine — SOLO RENDER.

GM45 Pizzicato Strings — the string section playing pizzicato (plucked, not
bowed): a rhythmic/ostinato colour voice with a dry finger-pluck attack.
Rendered solo ONLY (no unison doubling — comb-filtering buzz).

Proves:
1. Registration through instrument_registry (by_name / by_program)
2. UnitMatrixComposer zero-drift (1 voice, 1 section) + MIDI export
3. FluidSynth solo render via discover_soundfont() (FluidR3_GM.sf2)
4. Spectral buzz gate (clean single voice)
5. Pipeline stem label (GM_PROGRAMS[45] = "Pizzicato Strings") + SF2 preset
   check (preset 45 = "Pizzicato Section" — cosmetic name diff, no routing)
6. Full RenderPipeline stem render -> trackXX_Pizzicato_Strings.wav
7. Empirical FluidR3 pitch sweep (audible 36-96, no gaps)
8. Karplus-Strong ring test (0.9960 pluck rings clearly vs 0.990 dull control)
"""
import os, sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# --- Registration proof through the registry (NOT direct module import) ---
from instrument_registry import by_name, by_program, PIZZICATO_STRINGS as REG
assert REG.midi_program == 45
assert by_name("pizzicato strings") is REG
assert by_program(45) is REG
print(f"REGISTRY: by_name('pizzicato strings') -> {by_name('pizzicato strings')}")
print(f"REGISTRY: by_program(45) -> {by_program(45)}")

# --- Constants (registry uniform view + raw module for field detail) ---
from Strings.pizzicato_strings.pizzicato_strings import (
    MIDI_PROGRAM as PGM, GM_NAME, STEM_LABEL, RANGE_MIN, RANGE_MAX,
    SOLO_RANGE, SWEET_SPOT, ZONES, ARTICULATIONS, SYNTHESIS,
    KARPLUS_DEFAULTS, MODAL_PRESET, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
assert REG.midi_program == PGM and REG.range_min == RANGE_MIN and REG.range_max == RANGE_MAX
print(f"Pizz Strings: program={PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} range={RANGE_MIN}-{RANGE_MAX} sweet={SWEET_SPOT}")
print(f"Pizz Strings: A3={midi_to_freq(57):.1f}Hz C4={midi_to_freq(60):.1f}Hz A4={midi_to_freq(69):.1f}Hz C6={midi_to_freq(84):.1f}Hz")
print(f"Pizz Strings: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS}")
print(f"Pizz Strings: reverb={REVERB_TAIL}s body_eq={EQ_BODY} presence_eq={EQ_PRESENCE} air_eq={EQ_AIR} pan={PAN}")
print(f"Pizz Strings: karplus={KARPLUS_DEFAULTS} modal={MODAL_PRESET} fm={FM_DEFAULTS}")

# --- Full engine test: UnitMatrixComposer — ONE VOICE (solo) ---
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Pizzicato_Strings", program=PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Pizzicato SOLO: A-minor ostinato figure in the sweet spot (A3..A4),
# eighth notes, short plucky durations; accented first downbeat.
# Notes: A3 C4 E4 A4 E4 C4 A3 C4  (57 60 64 69 64 60 57 60)
u = MusicUnit()
pluck = [57, 60, 64, 69, 64, 60, 57, 60]
for i, p in enumerate(pluck):
    vel = 94 if i == 0 else 76          # marcato downbeat, then ostinato
    end = BAR if i == len(pluck) - 1 else i * 240 + 60   # ~0.125 beat plucks
    u.add_event(MusicEvent(p, vel, i * 240, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
assert u.len_ticks() == BAR, f"unit not flush: {u.len_ticks()}"
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

outdir = "/opt/data/projects/Instruments/Strings/pizzicato_strings"
os.makedirs(outdir, exist_ok=True)
midi_path = os.path.join(outdir, "pizzicato_test.mid")
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# --- Render SOLO via discover_soundfont() ---
from _test.render_audio import render_midi, spectral_buzz_check

wav = os.path.join(outdir, "pizzicato_test.wav")
render_midi(midi_path, wav, solo=0)  # track 1 (index 0) = Pizzicato solo
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"

ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# --- Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed) ---
import inspect, re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  [{PGM}] = {labels[PGM]!r}")
assert labels[PGM] == "Pizzicato Strings", f"stem label mismatch: {labels[PGM]!r}"
assert STEM_LABEL == "Pizzicato_Strings"
print(f"  Pizzicato_Strings STEM_LABEL matches pipeline label [45] ✓")

# --- FluidR3 preset check ---
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
sf2_name = preset_names.get((0, PGM), "MISSING")
print(f"SF2 preset {PGM} -> {sf2_name!r}")
assert sf2_name == "Pizzicato Section", f"SF2 preset mismatch: {sf2_name!r}"

# --- Full RenderPipeline stem render — verify stem file on disk ---
out_stems = os.path.join(outdir, "stems_pizzicato")
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_stems)
stem_files = sorted(os.listdir(out_stems))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_stems, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Pizzicato_Strings" in f for f in stem_files), f"no Pizzicato_Strings stem in {stem_files}"
pz_stem = [f for f in stem_files if "Pizzicato_Strings" in f][0]
assert os.path.getsize(os.path.join(out_stems, pz_stem)) > 40, "empty Pizzicato stem"

# --- Empirical FluidR3 pitch sweep (audibility across claimed range) ---
print("\n--- FluidR3 preset 45 pitch sweep (RMS) ---")
import subprocess, tempfile, wave
import numpy as np
from mido import MidiFile, MidiTrack, Message
notes = [24, 30, 36, 40, 45, 48, 55, 60, 64, 69, 76, 84, 90, 96, 103, 108]
sweep = {}
with tempfile.TemporaryDirectory() as td:
    for mn in notes:
        mid = MidiFile(ticks_per_beat=480)
        tr = MidiTrack()
        tr.append(Message("program_change", program=PGM, channel=0, time=0))
        tr.append(Message("note_on", note=mn, velocity=100, channel=0, time=0))
        tr.append(Message("note_off", note=mn, velocity=0, channel=0, time=960))
        mid.tracks.append(tr)
        mp = os.path.join(td, f"n{mn}.mid"); wp = os.path.join(td, f"n{mn}.wav")
        mid.save(mp)
        r = subprocess.run(["/opt/data/micromamba/envs/musicom/bin/fluidsynth", "-ni", "-g", "1.2",
                            "-F", wp, sf2_path, mp], capture_output=True)
        assert r.returncode == 0, r.stderr.decode()[-300:]
        w = wave.open(wp, "rb"); sr = w.getframerate()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        w.close()
        rms = float(np.sqrt(np.mean(d[:int(0.6 * sr)] ** 2))) if len(d) else 0.0
        sweep[mn] = rms
        print(f"  note {mn:3d} -> RMS {rms:.4f} {'OK' if rms > 0.005 else 'SILENT?'}")
audible_in_range = all(sweep[mn] > 0.005 for mn in range(36, 97) if mn in sweep)
assert audible_in_range, "GAPS in documented range 36-96"
print(f"  Sweep: all documented-range notes (36-96) audible ✓")

# --- Karplus-Strong ring test (plucked waveguide = the recommended engine) ---
print("\n--- Karplus-Strong ring test (pizz pluck vs dull control) ---")
from sound.synthesis.karplus_strong import karplus_strong as karp_render
pk_a = np.asarray(karp_render(45, 1.0, vel=90, loop_gain=0.9960, sr=22050))  # pizz recco
pk_b = np.asarray(karp_render(45, 1.0, vel=90, loop_gain=0.9900, sr=22050))  # dull control
seg_a = pk_a[int(0.5 * 22050):int(1.0 * 22050)]
seg_b = pk_b[int(0.5 * 22050):int(1.0 * 22050)]
ring_a = float(np.sqrt(np.mean(seg_a ** 2))) if len(seg_a) else 0.0
ring_b = float(np.sqrt(np.mean(seg_b ** 2))) if len(seg_b) else 0.0
ratio = ring_a / max(ring_b, 1e-9)
print(f"  tail 0.5-1.0s RMS: pizz 0.9960={ring_a:.4f} dull 0.9900={ring_b:.4f} ratio={ratio:.2f}x")
assert ring_a > ring_b, "pizz loop_gain did NOT ring longer than dull control"
assert ratio > 1.5, f"ring advantage too small: {ratio:.2f}x"

print("\nALL CHECKS PASSED")