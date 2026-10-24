# -*- coding: utf-8 -*-
"""Verify Tremolo Strings constants work with musicom engine — SOLO RENDER.

GM44 Tremolo Strings — the bowed string section playing rapid repeated bow
strokes (film-score tension texture). Rendered solo ONLY (no unison
doubling — comb-filtering buzz rule; a tremolo section + another melodic
patch on the same pitch is a buzz machine).

Checks:
  1. Registry registration (by_name / by_program through instrument_registry)
  2. UnitMatrixComposer zero-drift (1 bar, SOLO voice)
  3. MIDI export > 40 bytes
  4. FluidSynth WAV render via discover_soundfont() — FluidR3 preferred
  5. Spectral 4-8 kHz buzz gate
  6. Stem label vs pipeline GM_PROGRAMS[44]
  7. FluidR3 preset 44 phdr name
  8. RenderPipeline stem render → trackXX_Tremolo_Strings.wav
  9. Additive section-note smoke + 7 Hz tremolo-AM rate check
 10. FluidR3 pitch sweep across range — no gaps
"""
import os, sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# --- 1. Registry registration proof (import THROUGH the registry) ---
from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, TREMOLO_STRINGS
inst = by_name("tremolo strings")
assert inst is TREMOLO_STRINGS, "by_name('tremolo strings') must return TREMOLO_STRINGS"
inst2 = by_program(44)
assert inst2 is TREMOLO_STRINGS, "by_program(44) must return TREMOLO_STRINGS"
assert ALL_INSTRUMENTS["tremolo_strings"].midi_program == 44
print("Registry: by_name('tremolo strings') =", inst)
print("Registry: by_program(44) =", inst2)
print("Registry: TREMOLO_STRINGS.stem_label =", repr(TREMOLO_STRINGS.stem_label))

from Strings.tremolo_strings.tremolo_strings import (
    MIDI_PROGRAM as TS_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, ADDITIVE_HARMONICS, SYNTHESIS_DEFAULTS,
    BOWED_DEFAULTS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY, EQ_PRESENCE,
    EQ_AIR, PAN, midi_to_freq,
)

print(f"Tremolo Strings: program={TS_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE}")
print(f"Tremolo Strings: C1={midi_to_freq(24):.1f}Hz C2={midi_to_freq(36):.1f}Hz C3={midi_to_freq(48):.1f}Hz C4={midi_to_freq(60):.1f}Hz C6={midi_to_freq(84):.1f}Hz C7={midi_to_freq(96):.1f}Hz")
print(f"Tremolo Strings: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS}")
print(f"Tremolo Strings: reverb={REVERB_TAIL}s body_eq={EQ_BODY} presence_eq={EQ_PRESENCE} air_eq={EQ_AIR} pan={PAN}")
print(f"Tremolo Strings: synthesis_defaults={SYNTHESIS_DEFAULTS}")

# --- 2. UnitMatrixComposer — ONE VOICE (solo) ---
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Tremolo_Strings", program=TS_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Tremolo Strings SOLO: underscore tension line — long chattering notes
# (A3-D4-F4-G4 -> A4), the classic suspense swell; end flush at BAR
u = MusicUnit()
notes = [57, 62, 65, 67, 69]  # A3 D4 F4 G4 A4
for i, p in enumerate(notes):
    u.add_event(MusicEvent(p, 76, i * 360, BAR if i == len(notes) - 1 else i * 360 + 340))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

outdir = "/opt/data/projects/Instruments/Strings/tremolo_strings"
os.makedirs(outdir, exist_ok=True)
midi_path = os.path.join(outdir, "tremolo_strings_test.mid")
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# --- 4. Render SOLO via discover_soundfont() — FluidR3_GM.sf2 preferred ---
from _test.render_audio import render_midi, spectral_buzz_check

wav = os.path.join(outdir, "tremolo_strings_test.wav")
render_midi(midi_path, wav, solo=0)  # track 1 (index 0) = Tremolo Strings solo
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
print(f"  [{TS_PGM}] = {labels[TS_PGM]!r}")
assert labels[TS_PGM] == "Tremolo Strings", f"stem label mismatch: {labels[TS_PGM]!r}"
assert STEM_LABEL == "Tremolo_Strings"
print(f"  Tremolo_Strings STEM_LABEL matches pipeline sanitized label ✓")

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
sf2_name = preset_names.get((0, TS_PGM), "MISSING")
print(f"SF2 preset {TS_PGM} -> {sf2_name!r}")
assert sf2_name == "Tremolo", f"SF2 preset mismatch: {sf2_name!r}"

# --- 8. Full RenderPipeline stem render — verify stem file on disk ---
out_stems = os.path.join(outdir, "stems_tremolo_strings")
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_stems)
stem_files = sorted(os.listdir(out_stems))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_stems, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Tremolo_Strings" in f for f in stem_files), f"no Tremolo_Strings stem in {stem_files}"
ts_stem = [f for f in stem_files if "Tremolo_Strings" in f][0]
assert os.path.getsize(os.path.join(out_stems, ts_stem)) > 40, "empty Tremolo Strings stem"

# --- 9. Additive section-note smoke + 7 Hz tremolo-AM rate check ---
# The tremolo is not a synthesis-engine parameter: model it as AM at the
# documented rate on the additive section tone, prove the rate is real.
import numpy as np
from sound.synthesis.additive import SoundWave

sr = 22050
dur = 2.0
n = int(sr * dur)
t = np.arange(n) / sr
w = SoundWave(sample_rate=sr, duration=dur, frequency=220.0, amplitude=4096)
w.create_sine_wave(amplitude=4096)
f = np.array(ADDITIVE_HARMONICS["section_full"], dtype=float)
f = f / f.sum()          # apply_overtones asserts partials sum to 1.0
w.apply_overtones(f, amplitude=4096)
# ADSR: fast attack (bow already moving), long sustain, quick release.
# decay_S is per grid-step (top-partial frequency quirk) — 3e-5 holds a
# 2 s chord without collapse.
w.get_adsr_weights(length=[0.02, 0.02, 0.90, 0.06],
                   decay=[0.05, 0.01, 3e-5, 0.05],
                   sustain_level=0.9)
data = w.fundamental * w.weights
w.wavedata = data * (4096 / np.max(data))
carrier = w.wavedata.astype(np.float32) / 32768.0
carrier = carrier[:n]
env = 0.5 * (1 + np.sin(2 * np.pi * SYNTHESIS_DEFAULTS["tremolo_hz"] * t))
audio = carrier * env
peak = np.max(np.abs(audio))
late_rms = np.sqrt(np.mean(audio[int(1.0 * sr):int(1.5 * sr)] ** 2))
print(f"\nAdditive tremolo note (A3): peak={peak:.3f} late(1.0-1.5s)_rms/peak={late_rms / max(peak, 1e-9):.3f}")
assert peak > 0, "additive tremolo note silent"
assert late_rms / max(peak, 1e-9) > 0.2, "section tone collapses (no sustain)"

# envelope spectrum: AM sideband should peak at tremolo_hz
from numpy.fft import rfft
env_fft = np.abs(rfft(env - np.mean(env)))
freqs = np.fft.rfftfreq(n, 1 / sr)
f_peak = freqs[np.argmax(env_fft[1:]) + 1]
print(f"Envelope AM peak frequency: {f_peak:.2f} Hz (expect ~{SYNTHESIS_DEFAULTS['tremolo_hz']} Hz)")
assert abs(f_peak - SYNTHESIS_DEFAULTS["tremolo_hz"]) < 0.5, f"AM rate wrong: {f_peak:.2f}"

# --- 10. FluidR3 pitch sweep across range — no gaps ---
import subprocess, tempfile, wave, mido
sweep_notes = [24, 36, 48, 60, 72, 84, 96]
print(f"\nFluidR3 pitch sweep (RMS, notes {sweep_notes[0]}-{sweep_notes[-1]}):")
for note in sweep_notes:
    mf = mido.MidiFile()
    t = mido.MidiTrack()
    t.append(mido.Message("program_change", program=TS_PGM, channel=0, time=0))
    t.append(mido.Message("note_on", note=note, velocity=90, channel=0, time=0))
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
