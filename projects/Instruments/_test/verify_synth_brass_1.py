# -*- coding: utf-8 -*-
"""Verify Synth Brass 1 (GM62) constants through the registry + audio render.

Structural template: _test/verify_fretless_bass.py.
Audio render: INSTRUMENT SOLO ONLY (one melodic voice, one track) — the
2026-09-01 comb-filter rule. A drum-kit voice rides along for context but is
NOT part of the solo render.
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# --- prove REGISTRATION: import through the registry, not the module -----
from instrument_registry import by_name, by_program, SYNTH_BRASS_1

from Synth.synth_brass_1.synth_brass_1 import (
    MIDI_PROGRAM as SB_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, POLYSYNTH_DEFAULTS, FM_DEFAULTS,
    REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

assert SYNTH_BRASS_1 is by_name("synth brass 1")
assert by_program(62) is SYNTH_BRASS_1
assert SYNTH_BRASS_1.midi_program == 62
assert SYNTH_BRASS_1.name == "Synth Brass 1"
print(f"Registry: {SYNTH_BRASS_1}")
print(f"Synth Brass 1: program={SB_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"sweet={SYNTH_BRASS_1.sweet_spot} A4={midi_to_freq(69):.1f}Hz")
print(f"Synth Brass 1: zones={ZONES}")
print(f"Synth Brass 1: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"reverb={REVERB_TAIL}s pan={PAN}")
print(f"Synth Brass 1: C2={midi_to_freq(36):.2f}Hz C4={midi_to_freq(60):.2f}Hz "
      f"C6={midi_to_freq(84):.2f}Hz")

# --- engine test: 1 bar, 1 section ---------------------------------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES, beat_pattern

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Synth Brass 1", program=SB_PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)         # context only
comp.add_section("A", bars=1)

# Synth brass stab line: G-major stab chord (downbeat) -> D/G/B stab (off) ->
# sustained C-major swell into the bar end (terminal landmark at BAR).
u = MusicUnit()
for p, v, s, e in [
    (55, 96, 0, 480),      # G3  downbeat stab (sfz)
    (60, 96, 0, 480),      # C4
    (64, 96, 0, 480),      # E4
    (62, 88, 720, 1080),   # D4  off-beat stab (marcato)
    (67, 88, 720, 1080),   # G4
    (71, 88, 720, 1080),   # B4
    (60, 78, 1440, BAR),   # C4  sustained swell to bar end (sustain)
    (64, 78, 1440, BAR),   # E4
    (67, 78, 1440, BAR),   # G4
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

midi_path = "/opt/data/projects/Instruments/_test/synth_brass_1_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
msize = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# --- audio: SOLO synth brass only, FluidR3 via discover_soundfont --------
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print(f"SoundFont: {sf2}")
assert sf2 and "FluidR3" in sf2, f"expected FluidR3, got {sf2}"

wav = "/opt/data/projects/Instruments/_test/synth_brass_1_test.wav"
render_midi(midi_path, wav, solo=0)          # voice 0 = Synth Brass 1
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
print(f"\nStem label: GM_PROGRAMS[{SB_PGM}] = {labels[SB_PGM]!r}")
assert labels[SB_PGM] == "Synth Brass 1", f"stem label mismatch: {labels[SB_PGM]!r}"
assert STEM_LABEL == "Synth Brass 1".replace(" ", "_")

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
sf2_name = preset_names.get((0, SB_PGM), "MISSING")
print(f"SF2 preset {SB_PGM} -> {sf2_name!r}")
assert sf2_name == "Synth Brass 1", f"SF2 preset mismatch: {sf2_name!r}"

# --- RenderPipeline stem render on disk ---------------------------------
out_dir = "/opt/data/projects/Instruments/_test/stems_synth_brass_1"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Synth_Brass_1" in f for f in stem_files), f"no Synth_Brass_1 stem: {stem_files}"
stem = [f for f in stem_files if "Synth_Brass_1" in f][0]
assert os.path.getsize(os.path.join(out_dir, stem)) > 40, "empty Synth Brass 1 stem"

# --- Polysynth engine smoke test (primary synthesis) --------------------
import numpy as np
from sound.synthesis.polysynth import PolyVoice

pv = PolyVoice(sample_rate=22050)
pv.osc1.waveform = POLYSYNTH_DEFAULTS["osc1_waveform"]
pv.osc2.waveform = POLYSYNTH_DEFAULTS["osc2_waveform"]
pv.osc2.detune_cents = POLYSYNTH_DEFAULTS["osc2_detune_cents"]
pv.osc3.waveform = POLYSYNTH_DEFAULTS["osc3_waveform"]
pv.osc3.level = POLYSYNTH_DEFAULTS["osc3_level"]
pv.filter.cutoff = POLYSYNTH_DEFAULTS["filter_cutoff"]
pv.filter.resonance = POLYSYNTH_DEFAULTS["filter_resonance"]
pv.env1.set(attack=POLYSYNTH_DEFAULTS["env_attack"],
            decay=POLYSYNTH_DEFAULTS["env_decay"],
            sustain=POLYSYNTH_DEFAULTS["env_sustain"],
            release=POLYSYNTH_DEFAULTS["env_release"])
audio = pv.render_note(freq=midi_to_freq(67), duration=1.0)
peak = float(np.max(np.abs(audio)))
sustain = float(np.sqrt(np.mean(audio[11025:13230] ** 2)))  # t = 0.5-0.6 s
print(f"\nPolysynth brass G4: peak={peak:.3f} sustain_rms={sustain:.4f} "
      f"sustain/peak={sustain/peak:.3f}")
assert peak > 0.01, "polysynth brass render silent"
assert sustain / peak > 0.15, f"brass sustain collapses (sustain/peak={sustain/peak:.3f})"

# --- PhaseModSynth secondary engine smoke -------------------------------
from sound.synthesis.phase_mod import PhaseModSynth
pms = PhaseModSynth(sample_rate=22050)
pm = pms.render_note(freq=midi_to_freq(67), duration=1.0,
                     carrier_shape=FM_DEFAULTS["carrier_shape"],
                     mod_shape=FM_DEFAULTS["mod_shape"],
                     mod_freq_ratio=FM_DEFAULTS["mod_freq_ratio"],
                     mod_depth=FM_DEFAULTS["mod_depth"])
pm_peak = float(np.max(np.abs(pm)))
print(f"PhaseModSynth brass G4: peak={pm_peak:.3f}")
assert pm_peak > 0.01, "PhaseModSynth brass render silent"

# --- empirical FluidR3 pitch sweep (patch audibility) -------------------
import wave


def note_rms(midi_note, vel=90, dur=BAR):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("SB", program=62, channel=0)
    c.add_section("A", bars=1)
    uu = MusicUnit()
    uu.add_event(MusicEvent(midi_note, vel, 0, dur))
    c.set_unit(0, 0, uu)
    okk, _ = c.validate()
    assert okk
    p = f"/opt/data/projects/Instruments/_test/_sb_sweep_{midi_note}.mid"
    c.to_midi(p)
    w = f"/opt/data/projects/Instruments/_test/_sb_sweep_{midi_note}.wav"
    render_midi(p, w, solo=0)
    with wave.open(w, "rb") as f:
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)
    return float(np.sqrt(np.mean(raw.astype(np.float64) ** 2)))


print("\nPitch sweep (RMS, velocity 90, 1-bar held notes):")
sweep = {}
for n in [36, 48, 60, 72, 84, 96, 108]:
    rms = note_rms(n)
    sweep[n] = rms
    print(f"  note {n:3d}: RMS = {rms:8.1f} {'AUDIBLE' if rms > 100 else 'SILENT'}")
audible = [n for n, r in sweep.items() if r > 100]
assert len(audible) == len(sweep), f"preset 62 gaps at {sorted(set(sweep)-set(audible))}"
print(f"  audible notes: {audible} (no gaps — SF2 never clips a composition)")

print("\nALL CHECKS PASSED")
