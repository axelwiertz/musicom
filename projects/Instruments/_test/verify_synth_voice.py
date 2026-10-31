# -*- coding: utf-8 -*-
"""Verify Synth Voice (GM54) constants through the registry + audio render.

Structural template: _test/verify_synth_brass_1.py.
Audio render: INSTRUMENT SOLO ONLY (one melodic voice, one track) — the
2026-09-01 comb-filter rule. A drum-kit voice rides along for context but is
NOT part of the solo render.
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# --- prove REGISTRATION: import through the registry, not the module -----
from instrument_registry import by_name, by_program, SYNTH_VOICE

from Synth.synth_voice.synth_voice import (
    MIDI_PROGRAM as SV_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, ADDITIVE_DEFAULTS,
    POLYSYNTH_DEFAULTS, REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN,
    midi_to_freq,
)

assert SYNTH_VOICE is by_name("synth voice")
assert by_program(54) is SYNTH_VOICE
assert SYNTH_VOICE.midi_program == 54
assert SYNTH_VOICE.name == "Synth Voice"
print(f"Registry: {SYNTH_VOICE}")
print(f"Synth Voice: program={SV_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"sweet={SYNTH_VOICE.sweet_spot} A4={midi_to_freq(69):.1f}Hz")
print(f"Synth Voice: zones={ZONES}")
print(f"Synth Voice: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"reverb={REVERB_TAIL}s pan={PAN}")
print(f"Synth Voice: C2={midi_to_freq(36):.2f}Hz C4={midi_to_freq(60):.2f}Hz "
      f"C6={midi_to_freq(84):.2f}Hz")

# --- engine test: 1 bar, 1 section ---------------------------------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES, beat_pattern

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Synth Voice", program=SV_PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)         # context only
comp.add_section("A", bars=1)

# Synth-voice phrase: G-major "ah" lead (downbeat accent) -> voice swell into
# the bar end (terminal landmark at BAR). One melodic patch ONLY.
u = MusicUnit()
for p, v, s, e in [
    (67, 85, 0, 720),      # G4  marcato entrance ("ah!")
    (64, 74, 720, 1440),   # E4  legato join
    (62, 72, 1440, 1740),  # D4  swell tail
    (60, 66, 1740, BAR),   # C4  sustain to bar end (sustain)
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

midi_path = "/opt/data/projects/Instruments/_test/synth_voice_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
msize = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# --- audio: SOLO synth voice only, FluidR3 via discover_soundfont --------
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print(f"SoundFont: {sf2}")
assert sf2 and "FluidR3" in sf2, f"expected FluidR3, got {sf2}"

wav = "/opt/data/projects/Instruments/_test/synth_voice_test.wav"
render_midi(midi_path, wav, solo=0)          # voice 0 = Synth Voice
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
print(f"\nStem label: GM_PROGRAMS[{SV_PGM}] = {labels[SV_PGM]!r}")
assert labels[SV_PGM] == "Synth Voice", f"stem label mismatch: {labels[SV_PGM]!r}"
assert STEM_LABEL == "Synth Voice".replace(" ", "_")

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
sf2_name = preset_names.get((0, SV_PGM), "MISSING")
print(f"SF2 preset {SV_PGM} -> {sf2_name!r}")
assert sf2_name == "Synth Voice", f"SF2 preset mismatch: {sf2_name!r}"

# --- RenderPipeline stem render on disk ---------------------------------
out_dir = "/opt/data/projects/Instruments/_test/stems_synth_voice"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Synth_Voice" in f for f in stem_files), f"no Synth_Voice stem: {stem_files}"
stem = [f for f in stem_files if "Synth_Voice" in f][0]
assert os.path.getsize(os.path.join(out_dir, stem)) > 40, "empty Synth Voice stem"

# --- PhaseModSynth engine smoke test (primary synthesis) ----------------
import numpy as np
from sound.synthesis.phase_mod import PhaseModSynth

pms = PhaseModSynth(sample_rate=22050)
pm = pms.render_note(freq=midi_to_freq(67), duration=1.0,
                     carrier_shape=FM_DEFAULTS["carrier_shape"],
                     mod_shape=FM_DEFAULTS["mod_shape"],
                     mod_freq_ratio=FM_DEFAULTS["mod_freq_ratio"],
                     mod_depth=FM_DEFAULTS["mod_depth"])
pm_peak = float(np.max(np.abs(pm)))
sustain = float(np.sqrt(np.mean(pm[11025:13230] ** 2)))  # t = 0.5-0.6 s
print(f"\nPhaseModSynth voice G4: peak={pm_peak:.3f} sustain_rms={sustain:.4f} "
      f"sustain/peak={sustain/pm_peak:.3f}")
assert pm_peak > 0.01, "PhaseModSynth voice render silent"
assert sustain / pm_peak > 0.15, f"voice sustain collapses (sustain/peak={sustain/pm_peak:.3f})"

# --- Additive secondary engine smoke (formant stack) ---------------------
from sound.synthesis.additive import SoundWave  # noqa: E402
sw = SoundWave(sample_rate=22050, duration=1.0, frequency=midi_to_freq(67))
harm = np.array(ADDITIVE_DEFAULTS["harmonic_weights"], dtype=float)
harm = harm / harm.sum()  # apply_overtones requires factors summing to 1.0
sw.apply_overtones(harm.tolist())
sw.get_adsr_weights([0.3, 0.1, 0.5, 0.1], [0.25, 0.1, 0.0002, 0.1],
                    sustain_level=0.85)
add = np.abs(sw.weights)
add_peak = float(np.max(add)) if add.size else 0.0
print(f"Additive formant voice G4: envelope peak={add_peak:.3f}")
assert add_peak > 0.01, "Additive voice render silent"

# --- Polysynth tertiary engine smoke -------------------------------------
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
ps_peak = float(np.max(np.abs(audio)))
print(f"Polysynth oscillator-voice G4: peak={ps_peak:.3f}")
assert ps_peak > 0.01, "Polysynth voice render silent"

# --- empirical FluidR3 pitch sweep (patch audibility) -------------------
import wave


def note_rms(midi_note, vel=90, dur=BAR):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("SV", program=54, channel=0)
    c.add_section("A", bars=1)
    uu = MusicUnit()
    uu.add_event(MusicEvent(midi_note, vel, 0, dur))
    c.set_unit(0, 0, uu)
    okk, _ = c.validate()
    assert okk
    p = f"/opt/data/projects/Instruments/_test/_sv_sweep_{midi_note}.mid"
    c.to_midi(p)
    w = f"/opt/data/projects/Instruments/_test/_sv_sweep_{midi_note}.wav"
    render_midi(p, w, solo=0)
    with wave.open(w, "rb") as f:
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)
    return float(np.sqrt(np.mean(raw.astype(np.float64) ** 2)))


print("\nPitch sweep (RMS, velocity 90, 1-bar held notes):")
sweep = {}
for n in [24, 36, 48, 60, 72, 84, 96, 108]:
    rms = note_rms(n)
    sweep[n] = rms
    print(f"  note {n:3d}: RMS = {rms:8.1f} {'AUDIBLE' if rms > 100 else 'SILENT'}")
audible = [n for n, r in sweep.items() if r > 100]
assert len(audible) == len(sweep), f"preset 54 gaps at {sorted(set(sweep)-set(audible))}"
print(f"  audible notes: {audible} (no gaps — SF2 never clips a composition)")

# --- spectral centroid (brightness of the voice) -------------------------
import numpy.fft as fft


def centroid(path):
    w = wave.open(path, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    seg = data[: int(1.0 * sr)]
    spec = np.abs(fft.rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    return float(np.sum(freqs * spec) / np.sum(spec))


print(f"\nSpectral centroid: C4 = {centroid('/opt/data/projects/Instruments/_test/_sv_sweep_60.wav'):.0f} Hz, "
      f"C6 = {centroid('/opt/data/projects/Instruments/_test/_sv_sweep_84.wav'):.0f} Hz")

print("\nALL CHECKS PASSED")
