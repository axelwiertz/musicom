# -*- coding: utf-8 -*-
"""Verify Tango Accordion (GM23, bandoneón) through the registry + audio.

Structural template: _test/verify_synth_brass_1.py.
Audio render: INSTRUMENT SOLO ONLY (one melodic voice, one track) — the
2026-09-01 comb-filter rule. A drum-kit voice rides along for context but is
NOT part of the solo render.
"""
import os
import sys

import numpy as np

sys.path.insert(0, "/opt/data/projects/Instruments")

# --- prove REGISTRATION: import through the registry, not the module -----
from instrument_registry import by_name, by_program, TANGO_ACCORDION, ACCORDION

from Keys.tango_accordion.tango_accordion import (
    MIDI_PROGRAM as TA_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, SWEET_SPOT, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, ADDITIVE_DEFAULTS, MODAL_PRESET,
    REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

assert TANGO_ACCORDION is by_name("tango accordion")
assert TANGO_ACCORDION is by_name("TANGO ACCORDION")
assert by_program(23) is TANGO_ACCORDION
assert TANGO_ACCORDION is not ACCORDION
assert TANGO_ACCORDION.midi_program == 23
assert TANGO_ACCORDION.family == "Keys"
assert TANGO_ACCORDION.name == "Tango Accordion"
assert TANGO_ACCORDION.stem_label == "Tango_Accordion"
print(f"Registry: {TANGO_ACCORDION}")
print(f"Tango Accordion: program={TA_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={TANGO_ACCORDION.range_min}-{TANGO_ACCORDION.range_max} "
      f"sweet={TANGO_ACCORDION.sweet_spot} A4={midi_to_freq(69):.1f}Hz")
print(f"Tango Accordion: zones={ZONES}")
print(f"Tango Accordion: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Tango Accordion: F2={midi_to_freq(41):.2f}Hz C4={midi_to_freq(60):.2f}Hz "
      f"C6={midi_to_freq(84):.2f}Hz C7={midi_to_freq(96):.2f}Hz")
print(f"Distinct from: ACCORDION program={ACCORDION.midi_program}")

# --- engine test: 1 bar, 1 section ---------------------------------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES, beat_pattern

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Tango Accordion", program=TA_PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)         # context only
comp.add_section("A", bars=1)

# Bandoneón phrase (A minor, cantabile register): marcato entrance on the
# downbeat, picado pickup, a fuelle swell into the bar end. Monophonic line —
# one instrument, one track, terminal landmark at BAR.
u = MusicUnit()
for p, v, s, e in [
    (76, 92, 0, 480),        # E5  marcato (acento) downbeat
    (77, 74, 480, 720),      # F5  cantabile
    (76, 74, 720, 960),      # E5
    (72, 82, 960, 1080),     # C5  picado
    (71, 74, 1080, 1320),    # B4  cantabile
    (69, 78, 1320, 1680),    # A4  fuelle swell
    (72, 70, 1680, BAR),     # C5  resolves into the bar end (terminal)
]:
    u.add_event(MusicEvent(p, v, s, e))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
kick = beat_pattern()
snare = beat_pattern(beat_indices=(4, 12))
step = BAR // 16
for i in range(16):
    if kick[i]:
        u.add_event(MusicEvent(KIT["kick"], VELOCITIES["kick"], i * step, i * step + step))
    if snare[i]:
        u.add_event(MusicEvent(KIT["snare"], VELOCITIES["snare"], i * step, i * step + step))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/tango_accordion_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
msize = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# --- audio: SOLO bandoneón only, FluidR3 via discover_soundfont ----------
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print(f"SoundFont: {sf2}")
assert sf2 and "FluidR3" in sf2, f"expected FluidR3, got {sf2}"

wav = "/opt/data/projects/Instruments/_test/tango_accordion_test.wav"
render_midi(midi_path, wav, solo=0)          # voice 0 = Tango Accordion
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# --- stem label check against the ACTUAL pipeline GM_PROGRAMS ------------
import inspect
import re
from sound.render.pipeline import RenderPipeline

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem label: GM_PROGRAMS[{TA_PGM}] = {labels[TA_PGM]!r}")
assert labels[TA_PGM] == "Tango Accordion", f"stem label mismatch: {labels[TA_PGM]!r}"
assert STEM_LABEL == "Tango Accordion".replace(" ", "_")

# --- SF2 preset name (phdr) ---------------------------------------------
import struct
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, TA_PGM), "MISSING")
print(f"SF2 preset {TA_PGM} -> {sf2_name!r}")

# --- RenderPipeline stem render on disk ---------------------------------
out_dir = "/opt/data/projects/Instruments/_test/stems_tango_accordion"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Tango_Accordion" in f for f in stem_files), f"no Tango_Accordion stem: {stem_files}"
stem = [f for f in stem_files if "Tango_Accordion" in f][0]
assert os.path.getsize(os.path.join(out_dir, stem)) > 40, "empty Tango Accordion stem"

# --- PhaseModSynth primary engine smoke (reed + octave-coupled pair) ----
from sound.synthesis.phase_mod import PhaseModSynth

pms = PhaseModSynth(sample_rate=22050)
base = pms.render_note(
    freq=midi_to_freq(69), duration=1.0,
    carrier_shape=FM_DEFAULTS["carrier_shape"],
    mod_shape=FM_DEFAULTS["mod_shape"],
    mod_freq_ratio=FM_DEFAULTS["mod_freq_ratio"],
    mod_depth=FM_DEFAULTS["mod_depth"],
    attack=FM_DEFAULTS["attack"],
    release=FM_DEFAULTS["release"],
    sustain_level=FM_DEFAULTS["sustain_level"],
)
octave = pms.render_note(
    freq=midi_to_freq(81), duration=1.0,
    carrier_shape=FM_DEFAULTS["carrier_shape"],
    mod_shape=FM_DEFAULTS["mod_shape"],
    mod_freq_ratio=FM_DEFAULTS["mod_freq_ratio"],
    mod_depth=FM_DEFAULTS["mod_depth"],
    attack=FM_DEFAULTS["attack"],
    release=FM_DEFAULTS["release"],
    sustain_level=FM_DEFAULTS["sustain_level"],
)
n = min(len(base), len(octave))
stack = base[:n] + FM_DEFAULTS["octave_double"] * octave[:n]
peak = float(np.max(np.abs(stack)))
sustain = float(np.sqrt(np.mean(stack[int(0.5 * 22050):int(0.6 * 22050)] ** 2)))
print(f"\nPhaseModSynth bandoneón A4 + octave reed: peak={peak:.3f} "
      f"sustain_rms={sustain:.4f} sustain/peak={sustain / peak:.3f}")
assert peak > 0.01, "PhaseModSynth bandoneón render silent"
assert sustain / peak > 0.15, f"reed sustain collapses (sustain/peak={sustain / peak:.3f})"

# --- Additive fallback smoke (octave-heavy harmonic stack) --------------
from sound.synthesis.additive import SoundWave

sw = SoundWave(sample_rate=22050, duration=1.0, frequency=midi_to_freq(69))
sw.create_sine_wave()
hw = np.array(ADDITIVE_DEFAULTS["harmonic_weights"], dtype=float)
hw = hw / hw.sum()   # apply_overtones asserts the partials sum to 1.0
sw.apply_overtones(hw.tolist())
add_peak = float(np.max(np.abs(sw.wavedata)))
print(f"Additive bandoneón stack: peak={add_peak:.1f} "
      f"(h2/h1 = {ADDITIVE_DEFAULTS['harmonic_weights'][1]:.2f} — the octave reed)")
assert add_peak > 0

# --- empirical FluidR3 pitch sweep (patch audibility) -------------------
import wave


def note_rms(midi_note, vel=90, dur=BAR):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("TA", program=TA_PGM, channel=0)
    c.add_section("A", bars=1)
    uu = MusicUnit()
    uu.add_event(MusicEvent(midi_note, vel, 0, dur))
    c.set_unit(0, 0, uu)
    okk, _ = c.validate()
    assert okk
    p = f"/opt/data/projects/Instruments/_test/_ta_sweep_{midi_note}.mid"
    c.to_midi(p)
    w = f"/opt/data/projects/Instruments/_test/_ta_sweep_{midi_note}.wav"
    render_midi(p, w, solo=0)
    with wave.open(w, "rb") as f:
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)
    return float(np.sqrt(np.mean(raw.astype(np.float64) ** 2)))


print("\nPitch sweep (RMS, velocity 90, 1-bar held notes):")
sweep = {}
for n_ in [24, 36, 41, 48, 60, 72, 84, 96, 108]:
    rms = note_rms(n_)
    sweep[n_] = rms
    print(f"  note {n_:3d}: RMS = {rms:8.1f} {'AUDIBLE' if rms > 100 else 'SILENT'}")
audible = [n_ for n_, r in sweep.items() if r > 100]
assert len(audible) == len(sweep), f"preset 23 gaps at {sorted(set(sweep) - set(audible))}"
print(f"  audible notes: {audible} (no gaps — SF2 never clips a composition)")

# --- timbre: spectral centroid of the patch at C4 and C6 ----------------
def centroid(midi_note):
    p = f"/opt/data/projects/Instruments/_test/_ta_sweep_{midi_note}.mid"
    if not os.path.exists(p):
        note_rms(midi_note)
    w = f"/opt/data/projects/Instruments/_test/_ta_sweep_{midi_note}.wav"
    with wave.open(w, "rb") as f:
        sr = f.getframerate()
        d = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    seg = d[int(0.15 * sr):int(0.55 * sr)]
    spec = np.abs(np.fft.rfft(seg))
    fr = np.fft.rfftfreq(len(seg), 1 / sr)
    return float((spec * fr).sum() / max(spec.sum(), 1e-9))


for n_ in (60, 84):
    print(f"Spectral centroid note {n_}: {centroid(n_):.0f} Hz")

print("\nALL CHECKS PASSED")
