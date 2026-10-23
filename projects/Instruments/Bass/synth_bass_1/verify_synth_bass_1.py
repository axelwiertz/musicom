# -*- coding: utf-8 -*-
"""Verify Synth Bass 1 constants work with musicom engine — SOLO RENDER.

GM38 Synth Bass 1 — the classic analog synth bass (VCO → ladder filter →
ADSR). Monophonic line instrument. Rendered solo ONLY (no unison doubling
— comb-filtering buzz rule).

Checks:
  1. Registry registration (by_name / by_program through instrument_registry)
  2. UnitMatrixComposer zero-drift (1 bar, SOLO voice)
  3. MIDI export > 40 bytes
  4. FluidSynth WAV render via discover_soundfont() — FluidR3 preferred
  5. Spectral 4-8 kHz buzz gate
  6. Stem label vs pipeline GM_PROGRAMS[38]
  7. FluidR3 preset 38 phdr name
  8. RenderPipeline stem render → trackXX_Synth_Bass_1.wav
  9. MonoSynth (subtractive engine) smoke test
 10. FluidR3 pitch sweep across range — no gaps
"""
import os, sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# --- 1. Registry registration proof (import THROUGH the registry) ---
from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, SYNTH_BASS_1
inst = by_name("synth bass 1")
assert inst is SYNTH_BASS_1, "by_name('synth bass 1') must return SYNTH_BASS_1"
inst2 = by_program(38)
assert inst2 is SYNTH_BASS_1, "by_program(38) must return SYNTH_BASS_1"
assert ALL_INSTRUMENTS["synth_bass_1"].midi_program == 38
print("Registry: by_name('synth bass 1') =", inst)
print("Registry: by_program(38) =", inst2)
print("Registry: SYNTH_BASS_1.stem_label =", repr(SYNTH_BASS_1.stem_label))

from Bass.synth_bass_1.synth_bass_1 import (
    MIDI_PROGRAM as SB_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, SYNTHESIS_DEFAULTS, FM_DEFAULTS,
    KARPLUS_DEFAULTS, REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN,
    midi_to_freq,
)

print(f"Synth Bass 1: program={SB_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE}")
print(f"Synth Bass 1: A0={midi_to_freq(21):.1f}Hz C1={midi_to_freq(24):.1f}Hz C2={midi_to_freq(36):.1f}Hz A2={midi_to_freq(45):.1f}Hz C4={midi_to_freq(60):.1f}Hz C5={midi_to_freq(84):.1f}Hz")
print(f"Synth Bass 1: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS}")
print(f"Synth Bass 1: reverb={REVERB_TAIL}s body_eq={EQ_BODY} presence_eq={EQ_PRESENCE} air_eq={EQ_AIR} pan={PAN}")
print(f"Synth Bass 1: synthesis_defaults={SYNTHESIS_DEFAULTS}")
print(f"Synth Bass 1: fm_defaults={FM_DEFAULTS} karplus_defaults={KARPLUS_DEFAULTS}")

# --- 2. UnitMatrixComposer — ONE VOICE (solo) ---
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Synth_Bass_1", program=SB_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Synth Bass SOLO: disco octave-displacement riff in the groove pocket
# (A2-A3-A2-A3-E2-E3-A2), staccato gate feel; end flush at BAR
u = MusicUnit()
notes = [45, 57, 45, 57, 40, 52, 45]  # A2 A3 A2 A3 E2 E3 A2
for i, p in enumerate(notes):
    u.add_event(MusicEvent(p, 84, i * 240, BAR if i == len(notes) - 1 else i * 240 + 150))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

outdir = "/opt/data/projects/Instruments/Bass/synth_bass_1"
os.makedirs(outdir, exist_ok=True)
midi_path = os.path.join(outdir, "synth_bass_1_test.mid")
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# --- 4. Render SOLO via discover_soundfont() — FluidR3_GM.sf2 preferred ---
from _test.render_audio import render_midi, spectral_buzz_check

wav = os.path.join(outdir, "synth_bass_1_test.wav")
render_midi(midi_path, wav, solo=0)  # track 1 (index 0) = Synth Bass solo
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
print(f"  [{SB_PGM}] = {labels[SB_PGM]!r}")
assert labels[SB_PGM] == "Synth Bass 1", f"stem label mismatch: {labels[SB_PGM]!r}"
assert STEM_LABEL == "Synth_Bass_1"
print(f"  Synth_Bass_1 STEM_LABEL matches pipeline sanitized label ✓")

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
sf2_name = preset_names.get((0, SB_PGM), "MISSING")
print(f"SF2 preset {SB_PGM} -> {sf2_name!r}")
assert sf2_name == "Synth Bass 1", f"SF2 preset mismatch: {sf2_name!r}"

# --- 8. Full RenderPipeline stem render — verify stem file on disk ---
out_stems = os.path.join(outdir, "stems_synth_bass_1")
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_stems)
stem_files = sorted(os.listdir(out_stems))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_stems, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Synth_Bass_1" in f for f in stem_files), f"no Synth_Bass_1 stem in {stem_files}"
sb_stem = [f for f in stem_files if "Synth_Bass_1" in f][0]
assert os.path.getsize(os.path.join(out_stems, sb_stem)) > 40, "empty Synth Bass 1 stem"

# --- 9. MonoSynth smoke test (subtractive engine) ---
from sound.synthesis.mono_synth import MonoSynth
import numpy as np
ms = MonoSynth(sample_rate=22050)
ms.set_oscillator(waveform=SYNTHESIS_DEFAULTS["waveform"], sub_level=SYNTHESIS_DEFAULTS["sub_level"])
ms.set_filter(cutoff=SYNTHESIS_DEFAULTS["filter_cutoff"], resonance=SYNTHESIS_DEFAULTS["filter_resonance"],
              env_amount=SYNTHESIS_DEFAULTS["filter_env_amount"], keytrack=SYNTHESIS_DEFAULTS["filter_keytrack"])
ms.set_envelope(a=SYNTHESIS_DEFAULTS["env_a"], d=SYNTHESIS_DEFAULTS["env_d"],
                s=SYNTHESIS_DEFAULTS["env_s"], r=SYNTHESIS_DEFAULTS["env_r"])
audio = ms.render_note(midi_note=38, duration=1.0)  # D2 — groove pocket
peak = np.max(np.abs(audio))
sustain_rms = np.sqrt(np.mean(audio[int(0.5 * 22050):int(0.7 * 22050)] ** 2))
print(f"\nMonoSynth D2: peak={peak:.3f} sustain_rms/peak={sustain_rms / max(peak, 1e-9):.3f}")
assert peak > 0, "MonoSynth synth bass silent"
assert sustain_rms / max(peak, 1e-9) > 0.1, "MonoSynth bass has no sustain (gate collapse?)"

# --- 10. FluidR3 pitch sweep across range — no gaps ---
import subprocess, tempfile, wave
sweep_notes = [24, 36, 48, 60, 72, 84]  # C1 C2 C3 C4 C5 C6? (84 = C5)
print(f"\nFluidR3 pitch sweep (RMS, notes {sweep_notes[0]}-{sweep_notes[-1]}):")
import mido
for note in sweep_notes:
    mf = mido.MidiFile()
    t = mido.MidiTrack()
    t.append(mido.Message("program_change", program=SB_PGM, channel=0, time=0))
    t.append(mido.Message("note_on", note=note, velocity=90, channel=0, time=0))
    t.append(mido.Message("note_off", note=note, velocity=0, channel=0, time=480))
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
