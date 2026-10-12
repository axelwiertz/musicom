# -*- coding: utf-8 -*-
"""Verify Synth Pad (GM88) constants + registration + engine end-to-end.

Pattern: verify_marimba.py, but the audio-render voice stack is the
instrument SOLO ONLY (one voice, one track — no unison doubling; the
2026-09-01 comb-filter lesson).
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# 1) Registration proof — import THROUGH the registry (the KB gate)
from instrument_registry import (  # noqa: E402
    SYNTH_PAD, ALL_INSTRUMENTS, by_name, by_program, registry_table,
)

assert "synth_pad" in ALL_INSTRUMENTS, "synth_pad NOT registered"
from structures import MidiInstrument  # noqa: E402
from Synth.synth_pad.synth_pad import midi_to_freq  # noqa: E402

print(f"Registered: synth_pad -> {ALL_INSTRUMENTS['synth_pad']!r}")
print(f"Registry table (Synth row):")
for line in registry_table().splitlines():
    if line.startswith("| Synth |"):
        print(f"  {line}")

print(f"\nConstants:")
print(f"  SYNTH_PAD.midi_program = {SYNTH_PAD.midi_program} (GM {SYNTH_PAD.gm_name!r})")
print(f"  MidiInstrument.SYNTH_PAD = {MidiInstrument.SYNTH_PAD} "
      f"(enum matches registry: {MidiInstrument.SYNTH_PAD == SYNTH_PAD.midi_program})")
print(f"  by_name('synth pad')      = {by_name('synth pad')!r}")
print(f"  by_name('pad 1 (new age)')= {by_name('pad 1 (new age)')!r}")
print(f"  by_program(88)            = {by_program(88)!r}")
print(f"  stem_label                = {SYNTH_PAD.stem_label!r}")
print(f"  sweet_spot                = {SYNTH_PAD.sweet_spot}, "
      f"solo_range = {SYNTH_PAD.solo_range}")
print(f"  zones                     = {SYNTH_PAD.zones}")
print(f"  articulations             = {list(SYNTH_PAD.articulations)}")
print(f"  synthesis                 = {SYNTH_PAD.synthesis}")
print(f"  reverb_tail               = {SYNTH_PAD.reverb_tail}s, pan = {SYNTH_PAD.pan}")
print(f"  A4 = {midi_to_freq(69):.1f} Hz")

# 2) Engine test: UnitMatrixComposer — ONE voice (the pad), 1 bar
from structures import MusicEvent, MusicUnit  # noqa: E402
from workflows.unitmatrix_composer import UnitMatrixComposer  # noqa: E402

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Synth Pad", program=SYNTH_PAD.midi_program, channel=0)
comp.add_section("A", bars=1)

BAR = 1920
# Pad chord C4-E4-G4-C5, whole bar, flush at BAR (terminal landmark)
u = MusicUnit()
for p in [60, 64, 67, 72]:
    u.add_event(MusicEvent(p, 72, 0, BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/synth_pad_test.mid"
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# 3) SOLO render (instrument alone — no second melodic patch)
from _test.render_audio import render_midi, spectral_buzz_check  # noqa: E402

wav = "/opt/data/projects/Instruments/_test/synth_pad_test.wav"
render_midi(midi_path, wav, solo=0)
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# 4) Empirical FluidR3 pitch sweep (RMS per note, patch audibility)
import subprocess  # noqa: E402
import wave  # noqa: E402
import numpy as np  # noqa: E402
from sound.render.fluidsynth import discover_soundfont  # noqa: E402

sf2 = discover_soundfont()
print(f"\nSoundFont: {sf2}")

def note_rms(midi_note, vel=72, dur_ticks=BAR):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("Pad", program=88, channel=0)
    c.add_section("A", bars=1)
    uu = MusicUnit()
    uu.add_event(MusicEvent(midi_note, vel, 0, dur_ticks))
    c.set_unit(0, 0, uu)
    okk, _ = c.validate()
    assert okk
    p = f"/opt/data/projects/Instruments/_test/_sweep_n{midi_note}.mid"
    c.to_midi(p)
    w = f"/opt/data/projects/Instruments/_test/_sweep_n{midi_note}.wav"
    render_midi(p, w, solo=0)
    with wave.open(w, "rb") as f:
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)
    return float(np.sqrt(np.mean(raw.astype(np.float64) ** 2)))

print("Pitch sweep (RMS, velocity 72, 1-bar sustained notes):")
sweep = {}
for n in [36, 48, 60, 72, 84, 96, 108]:
    rms = note_rms(n)
    sweep[n] = rms
    print(f"  note {n:3d}: RMS = {rms:8.1f} {'AUDIBLE' if rms > 100 else 'SILENT'}")
audible = [n for n, r in sweep.items() if r > 100]
assert audible, "preset 88 silent everywhere — patch missing?"
print(f"  audible notes: {audible}")

# 5) SF2 preset name from phdr
import struct  # noqa: E402

data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
for pgm in (88, 89):
    print(f"SF2 preset {pgm} -> {preset_names.get((0, pgm), 'MISSING')!r}")

# 6) Stem label via actual RenderPipeline
from sound.render.pipeline import RenderPipeline  # noqa: E402

out_dir = "/opt/data/projects/Instruments/_test/stems_synth_pad"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
    assert os.path.getsize(fp) > 40, f"empty stem {f}"
pad_stem = [f for f in stem_files if "Pad_1_new_age" in f]
assert pad_stem, f"no Pad_1_new_age stem in {stem_files}"
assert "Pad_1_new_age" in stem_files[0], f"expected Pad_1_new_age stem, got {stem_files}"

# 7) PhaseModSynth smoke: analog-pad alt — slow attack (onset < sustain)
from sound.synthesis.phase_mod import PhaseModSynth  # noqa: E402
from Synth.synth_pad.synth_pad import FM_DEFAULTS, ADDITIVE_HARMONICS, midi_to_freq  # noqa: E402

pms = PhaseModSynth(sample_rate=22050)
audio = pms.render_note(freq=midi_to_freq(60), duration=1.5, **FM_DEFAULTS)
peak = float(np.max(np.abs(audio)))
onset = float(np.sqrt(np.mean(audio[:1102] ** 2)))   # first 50 ms (attack 0.6 s)
late = float(np.sqrt(np.mean(audio[22050:24255] ** 2)))  # t=1.0–1.1 s (sustain)
ratio = onset / late if late > 0 else 1.0
print(f"\nPhaseModSynth pad (FM_DEFAULTS): peak={peak:.4f} onset_rms={onset:.4f} "
      f"late_rms={late:.4f} onset/late={ratio:.3f}")
assert peak > 0, "PhaseModSynth pad silent"
assert ratio < 0.6, f"pad attack NOT slow (onset/late={ratio:.3f})"

# 8) Additive smoke: pad envelope must HOLD sustain (2026-10-11 tail fix).
#    QUIRK: apply_overtones leaves self.frequency at the TOP partial
#    (~7x fundamental), so the ADSR grid step is ~1/(duration*top_partial) s
#    and decay_S is PER-GRID-STEP — a pad recipe must use decay_S ~1e-4 to
#    hold a 2 s chord (documented in instrument.md).
from sound.synthesis.additive import SoundWave  # noqa: E402

sw = SoundWave(sample_rate=22050, duration=2.0, frequency=midi_to_freq(60))
harm = np.array(ADDITIVE_HARMONICS["pad_warm"], dtype=float)
harm = harm / harm.sum()  # apply_overtones requires factors summing to 1.0
sw.apply_overtones(harm.tolist())
sw.get_adsr_weights([0.3, 0.05, 0.6, 0.05], [0.2, 0.3, 0.0001, 0.1],
                    sustain_level=0.9)
w = sw.weights
n = w.shape[0]
late_w = float(np.max(w[int(0.7 * n):int(0.9 * n)]))  # deep in the sustain leg
print(f"Additive pad envelope: weights_len={n} late-sustain max={late_w:.3f} "
      f"(target ≥ 0.45 — the 2026-10-11 collapse-bug gate)")
assert late_w >= 0.45, f"additive pad envelope collapsed: late max {late_w:.3f}"

print("\nALL CHECKS PASSED")