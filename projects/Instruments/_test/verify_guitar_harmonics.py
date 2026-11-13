# -*- coding: utf-8 -*-
"""Verify Guitar Harmonics (GM31) end-to-end — registry → composer → MIDI → WAV.

Structure follows _test/verify_marimba.py, with the 2026-09-01 fix applied:
the instrument is imported THROUGH the registry and the audio check renders
the instrument SOLO (one voice, one track) — never unison-doubled with a
second melodic patch.
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- 1. Registration proof: constants come from the registry ------------
from instrument_registry import by_name, by_program, GUITAR_HARMONICS as GH

print(f"registry: {GH!r}")
print(f"GH.midi_program={GH.midi_program} name={GH.gm_name!r} "
      f"stem={GH.stem_label!r} range={GH.range_min}-{GH.range_max} "
      f"sweet={GH.sweet_spot} synth={GH.synthesis}")
print(f"by_name('guitar harmonics') = {by_name('guitar harmonics')!r}")
print(f"by_program(31) = {by_program(31)!r}")

from Guitar.guitar_harmonics.guitar_harmonics import (
    MIDI_PROGRAM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES, ARTICULATIONS,
    SYNTHESIS, MODAL_PRESET, GUITAR_HARMONICS_MODES, KARPLUS_DEFAULTS,
    TRANSPOSE_SEMITONES, REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN,
    midi_to_freq,
)

assert MIDI_PROGRAM == GH.midi_program == 31
assert GH.zones == ZONES and GH.articulations == ARTICULATIONS
print(f"\nzones={ZONES}")
print(f"articulations={list(ARTICULATIONS)}")
print(f"transpose=+{TRANSPOSE_SEMITONES} semitones (SF2 patch sounds octave up)")
print(f"reverb={REVERB_TAIL}s eq_body={EQ_BODY} eq_presence={EQ_PRESENCE} "
      f"eq_air={EQ_AIR} pan={PAN}")
print(f"freq: written 48={midi_to_freq(48):.1f}Hz sounds "
      f"{midi_to_freq(48 + TRANSPOSE_SEMITONES):.1f}Hz")

# ---- 2. Zero-drift composer ---------------------------------------------
from structures import MusicEvent, MusicUnit
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("GuitarHarmonics", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Drums", program=0, channel=9)   # context only; NOT in solo WAV
comp.add_section("A", bars=1)

# Harmonic chime line, WRITTEN an octave below the desired sound
# (sounds 60,67,72,76,79,84,79,72 = C4..C6 chime arpeggio)
line = [48, 55, 60, 64, 67, 72, 67, 60]
u = MusicUnit()
for i, p in enumerate(line):
    start = i * 240
    end = BAR if i == len(line) - 1 else start + 220   # let the last one ring
    u.add_event(MusicEvent(p, 84, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
for p, v, s in [(36, 92, 0), (42, 60, 0), (42, 52, 240), (38, 84, 480),
                (42, 54, 720), (36, 90, 960), (42, 58, 960), (42, 50, 1200),
                (38, 82, 1440), (42, 56, 1680)]:
    u.add_event(MusicEvent(p, v, s, min(s + 120, BAR)))
u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))      # terminal landmark
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

MID = "/opt/data/projects/Instruments/_test/guitar_harmonics_test.mid"
comp.to_midi(MID)
msize = os.path.getsize(MID)
print(f"MIDI: {MID} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# ---- 3. Solo WAV render through discover_soundfont() --------------------
import wave
import numpy as np
from sound.render.fluidsynth import discover_soundfont
from _test.render_audio import render_midi, spectral_buzz_check

sf2 = discover_soundfont()
print(f"soundfont: {sf2}")
assert sf2 and "FluidR3" in os.path.basename(sf2), f"wrong soundfont: {sf2}"

WAV = "/opt/data/projects/Instruments/_test/guitar_harmonics_test.wav"
render_midi(MID, WAV, solo=0)          # SOLO guitar harmonics — track 1 only
wsize = os.path.getsize(WAV)
print(f"WAV (solo): {WAV} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"

ok, rep = spectral_buzz_check(WAV)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"


def load(path):
    w = wave.open(path, "rb")
    sr = w.getframerate()
    d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    w.close()
    return sr, d.astype(np.float32) / 32768


# ---- 4. Transposition proof IN the rendered artifact --------------------
sr, audio = load(WAV)
seg = audio[int(0.05 * sr):int(0.30 * sr)]        # first note = written 48
spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
fr = np.fft.rfftfreq(len(seg), 1 / sr)
peak = fr[np.argmax(spec)]
written = midi_to_freq(48)
expected = midi_to_freq(48 + TRANSPOSE_SEMITONES)
print(f"\nWritten 48 ({written:.1f} Hz) rendered peak {peak:.1f} Hz "
      f"(expected octave-up {expected:.1f} Hz, ratio {peak / written:.2f}x)")
assert abs(peak - expected) / expected < 0.06, "transposition not confirmed"

# odd-partial signature: energy at 1x/3x/5x of the SOUNDING pitch
bands = []
for k in (1, 2, 3, 5):
    idx = np.argmin(np.abs(fr - k * expected))
    bands.append(spec[max(0, idx - 3):idx + 4].max())
odd = bands[0] + bands[2] + bands[3]
print(f"partials re sounding pitch: 1x={bands[0]:.0f} 2x={bands[1]:.0f} "
      f"3x={bands[2]:.0f} 5x={bands[3]:.0f} -> odd share {100 * odd / sum(bands):.0f}%")
assert odd > bands[1] * 2, "odd-harmonic (node) spectrum not confirmed"

# ---- 5. ModalSynth custom bank ------------------------------------------
from sound.synthesis.modal import ModalSynth

ms = ModalSynth(sample_rate=44100)
modes = [(f / 440.0 * midi_to_freq(60), a, d) for f, a, d in GUITAR_HARMONICS_MODES]
audio_m = ms.render_custom(modes, duration=2.0, excitation="impulse")
peak_m = float(np.max(np.abs(audio_m)))
late = float(np.sqrt(np.mean(audio_m[int(1.0 * 44100):int(1.5 * 44100)] ** 2)))
print(f"\nModalSynth custom bank: peak={peak_m:.3f} "
      f"late(1.0-1.5s) rms/peak={late / peak_m:.3f}")
assert peak_m > 0, "modal render silent"
assert late / peak_m > 0.05, "harmonic ring too short — decay rates wrong"

ms2 = ModalSynth(sample_rate=44100)
mar = ms2.render_preset("marimba", duration=2.0, excitation="impulse")
mar_late = float(np.sqrt(np.mean(mar[int(1.0 * 44100):int(1.5 * 44100)] ** 2)))
mar_peak = float(np.max(np.abs(mar)))
print(f"  reference marimba preset late rms/peak={mar_late / mar_peak:.4f} "
      f"-> harmonics ring {(late / peak_m) / max(mar_late / mar_peak, 1e-9):.0f}x longer")

# ---- 6. Karplus-Strong fallback smoke -----------------------------------
from sound.synthesis.karplus_strong import karplus_strong

ks = karplus_strong(60, 3.0, vel=100,
                    loop_gain=KARPLUS_DEFAULTS["loop_gain"],
                    width=KARPLUS_DEFAULTS["width"], sr=44100)
ks_peak = float(np.max(np.abs(ks)))
ks_late = float(np.sqrt(np.mean(ks[int(1.0 * 44100):int(2.0 * 44100)] ** 2))) / ks_peak
dull = karplus_strong(60, 3.0, vel=100, loop_gain=0.990,
                      width=KARPLUS_DEFAULTS["width"], sr=44100)
dull_peak = float(np.max(np.abs(dull)))
dull_late = float(np.sqrt(np.mean(dull[int(1.0 * 44100):int(2.0 * 44100)] ** 2))) / dull_peak
print(f"Karplus loop_gain={KARPLUS_DEFAULTS['loop_gain']}: peak={ks_peak:.3f} "
      f"tail(1-2s)={ks_late:.5f} vs 0.990 dull control {dull_late:.5f} "
      f"-> {ks_late / dull_late:.1f}x")
assert ks_peak > 0 and ks_late / dull_late > 1.5, "KS ring not longer than dull control"

# ---- 7. Stem labels + SF2 preset ---------------------------------------
import inspect
import re
import struct
from sound.render.pipeline import RenderPipeline

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"Stem label: GM_PROGRAMS[31] = {labels[31]!r} -> file {labels[31].replace(' ', '_')!r}")
assert labels[31].replace(" ", "_") == "Guitar_harmonics", f"stem label mismatch: {labels[31]!r}"
assert STEM_LABEL == labels[31].replace(" ", "_")

data = open(sf2, "rb").read()
phdr = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr + 4:phdr + 8])[0]
presets = {}
for i in range(phdr_size // 38):
    off = phdr + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pn, bk = struct.unpack("<HH", data[off + 20:off + 24])
    presets[(bk, pn)] = name
sf2_name = presets.get((0, 31), "MISSING")
print(f"SF2 preset 31 -> {sf2_name!r}")
assert "Harmonic" in sf2_name, f"SF2 preset mismatch: {sf2_name!r}"

out_dir = "/opt/data/projects/Instruments/_test/stems_guitar_harmonics"
pipeline = RenderPipeline(fluidsynth_bin=os.environ["MUSICOM_FLUIDSYNTH"],
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(MID, out_dir)
stems = sorted(os.listdir(out_dir))
print(f"Stems ({len(stems)}):")
for f in stems:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
hit = [f for f in stems if "Guitar_harmonics" in f]
assert hit, f"no Guitar_harmonics stem in {stems}"
assert os.path.getsize(os.path.join(out_dir, hit[0])) > 40, "empty stem"

print("\nALL CHECKS PASSED")
