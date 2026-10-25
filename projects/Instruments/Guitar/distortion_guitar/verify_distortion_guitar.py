# -*- coding: utf-8 -*-
"""Verify Distortion Guitar constants work with musicom engine — SOLO RENDER.

GM30 Distortion Guitar — the high-gain rock/metal guitar voice (heavier
sibling of Overdriven Guitar GM29). Rendered solo ONLY (no unison doubling
— comb-filtering buzz rule; stacking a second melodic patch on the same
pitches is a buzz machine).

Checks:
  1. Registry registration (by_name / by_program through instrument_registry)
  2. UnitMatrixComposer zero-drift (1 bar, SOLO voice)
  3. MIDI export > 40 bytes
  4. FluidSynth WAV render via discover_soundfont() — FluidR3 preferred
  5. Spectral 4-8 kHz buzz gate
  6. Stem label vs pipeline GM_PROGRAMS[30]
  7. FluidR3 preset 30 phdr name
  8. RenderPipeline stem render → trackXX_Distortion_Guitar.wav
  9. Karplus-Strong smoke: 0.9992 ring vs 0.990 dull control
 10. FluidR3 pitch sweep across range — no gaps
"""
import os, sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# --- 1. Registry registration proof (import THROUGH the registry) ---
from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, DISTORTION_GUITAR
inst = by_name("distortion guitar")
assert inst is DISTORTION_GUITAR, "by_name('distortion guitar') must return DISTORTION_GUITAR"
inst2 = by_program(30)
assert inst2 is DISTORTION_GUITAR, "by_program(30) must return DISTORTION_GUITAR"
assert ALL_INSTRUMENTS["distortion_guitar"].midi_program == 30
print("Registry: by_name('distortion guitar') =", inst)
print("Registry: by_program(30) =", inst2)
print("Registry: DISTORTION_GUITAR.stem_label =", repr(DISTORTION_GUITAR.stem_label))

from Guitar.distortion_guitar.distortion_guitar import (
    MIDI_PROGRAM as DG_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, KARPLUS_DEFAULTS, FM_DEFAULTS,
    ADDITIVE_DEFAULTS, REVERB_TAIL, EQ_BODY, EQ_PRESENCE,
    EQ_AIR, PAN, midi_to_freq,
)

print(f"Distortion Guitar: program={DG_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE}")
print(f"Distortion Guitar: E1={midi_to_freq(28):.1f}Hz E2={midi_to_freq(40):.1f}Hz E3={midi_to_freq(52):.1f}Hz C5={midi_to_freq(72):.1f}Hz E6={midi_to_freq(76):.1f}Hz C6={midi_to_freq(84):.1f}Hz")
print(f"Distortion Guitar: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS}")
print(f"Distortion Guitar: karplus={KARPLUS_DEFAULTS}")
print(f"Distortion Guitar: fm={FM_DEFAULTS} additive={ADDITIVE_DEFAULTS}")
print(f"Distortion Guitar: reverb={REVERB_TAIL}s body_eq={EQ_BODY} presence_eq={EQ_PRESENCE} air_eq={EQ_AIR} pan={PAN}")

# --- 2. UnitMatrixComposer — ONE VOICE (solo) ---
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Distortion_Guitar", program=DG_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Distortion Guitar SOLO: metal lead line (E3-G3-A3-C4 -> E4), the classic
# power-chord-anchored riff register; end flush at BAR (terminal landmark)
u = MusicUnit()
notes = [52, 55, 57, 60, 64]  # E3 G3 A3 C4 E4
for i, p in enumerate(notes):
    u.add_event(MusicEvent(p, 88, i * 360, BAR if i == len(notes) - 1 else i * 360 + 340))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

outdir = "/opt/data/projects/Instruments/Guitar/distortion_guitar"
os.makedirs(outdir, exist_ok=True)
midi_path = os.path.join(outdir, "distortion_guitar_test.mid")
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# --- 4. Render SOLO via discover_soundfont() — FluidR3_GM.sf2 preferred ---
from _test.render_audio import render_midi, spectral_buzz_check

wav = os.path.join(outdir, "distortion_guitar_test.wav")
render_midi(midi_path, wav, solo=0)  # track 1 (index 0) = Distortion Guitar solo
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"

ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# --- 6. Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed) ---
import inspect, re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  [{DG_PGM}] = {labels[DG_PGM]!r}")
assert labels[DG_PGM] == "Distortion Guitar", f"stem label mismatch: {labels[DG_PGM]!r}"
assert STEM_LABEL == "Distortion_Guitar"
print(f"  Distortion_Guitar STEM_LABEL matches pipeline sanitized label ✓")

# --- 7. FluidR3 preset check ---
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
sf2_name = preset_names.get((0, DG_PGM), "MISSING")
print(f"SF2 preset {DG_PGM} -> {sf2_name!r}")
assert sf2_name == "Distortion Guitar", f"SF2 preset mismatch: {sf2_name!r}"

# --- 8. Full RenderPipeline stem render — verify stem file on disk ---
out_stems = os.path.join(outdir, "stems_distortion_guitar")
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_stems)
stem_files = sorted(os.listdir(out_stems))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_stems, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Distortion_Guitar" in f for f in stem_files), f"no Distortion_Guitar stem in {stem_files}"
dg_stem = [f for f in stem_files if "Distortion_Guitar" in f][0]
assert os.path.getsize(os.path.join(out_stems, dg_stem)) > 40, "empty Distortion Guitar stem"

# --- 9. Karplus-Strong smoke: high loop_gain ring vs dull control ---
# Distortion guitar = plucked waveguide + hard-clip compression. The
# signature is the LONG ring at high loop_gain (0.9992) — the compression
# sustain. Compare against the 0.990 dull control.
import numpy as np
from sound.synthesis.karplus_strong import karplus_strong

def late_ratio(loop_gain, pitch=64, dur=2.5):
    sig = karplus_strong(pitch, dur, vel=110, loop_gain=loop_gain, sr=22050)
    peak = max(np.max(np.abs(sig)), 1e-9)
    late = np.sqrt(np.mean(sig[int(1.0 * 22050):int(2.0 * 22050)] ** 2))
    return late / peak

r_hi = late_ratio(KARPLUS_DEFAULTS["loop_gain"])
r_dull = late_ratio(0.990)
print(f"\nKarplus-Strong ring (E4): loop_gain={KARPLUS_DEFAULTS['loop_gain']} -> late(1-2s) rms/peak={r_hi:.4f}")
print(f"Karplus-Strong ring (E4): loop_gain=0.990 (dull control) -> late(1-2s) rms/peak={r_dull:.4f}")
print(f"Ring advantage: {r_hi / max(r_dull, 1e-9):.1f}x")
assert r_hi > 2.0 * r_dull, "distortion ring NOT above dull control — loop_gain not effective"

# --- 10. FluidR3 pitch sweep across range — no gaps ---
import subprocess, tempfile, wave, mido
sweep_notes = [28, 40, 52, 64, 76, 84]
print(f"\nFluidR3 pitch sweep (RMS, notes {sweep_notes[0]}-{sweep_notes[-1]}):")
for note in sweep_notes:
    mf = mido.MidiFile()
    t = mido.MidiTrack()
    t.append(mido.Message("program_change", program=DG_PGM, channel=0, time=0))
    t.append(mido.Message("note_on", note=note, velocity=95, channel=0, time=0))
    t.append(mido.Message("note_off", note=note, velocity=0, channel=0, time=960))
    mf.tracks.append(t)
    fd, tmp = tempfile.mkstemp(suffix=".mid")
    os.close(fd)
    mf.save(tmp)
    tmp_wav = tempfile.mktemp(suffix=".wav")
    r = subprocess.run(["/opt/data/micromamba/envs/musicom/bin/fluidsynth", "-ni", "-g", "1.2",
                        "-F", tmp_wav, sf2_path, tmp], capture_output=True)
    w = wave.open(tmp_wav, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    d = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    rms = float(np.sqrt(np.mean(d ** 2)))
    os.unlink(tmp)
    os.unlink(tmp_wav)
    print(f"  note {note:3d} ({midi_to_freq(note):7.1f} Hz) rms={rms:.4f} {'OK' if rms > 0.002 else 'SILENT!'}")
    assert rms > 0.002, f"note {note} silent in FluidR3 sweep"

print("\nALL CHECKS PASSED")
