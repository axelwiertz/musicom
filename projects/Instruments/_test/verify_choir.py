# -*- coding: utf-8 -*-
"""Verify Choir (GM52, Choir Aahs) — constants + registry + engine end-to-end.

Pattern: verify_marimba.py / verify_synth_pad.py, but the audio-render voice
stack is the instrument SOLO ONLY (one voice, one track — no unison doubling;
the 2026-09-01 comb-filter lesson).
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# 1) Registration proof — import THROUGH the registry (the KB gate)
from instrument_registry import (  # noqa: E402
    CHOIR, ALL_INSTRUMENTS, by_name, by_program, registry_table,
)

assert "choir" in ALL_INSTRUMENTS, "choir NOT registered"
from Vocal.choir.choir import (  # noqa: E402
    midi_to_freq, ADDITIVE_HARMONICS, SYNTHESIS_DEFAULTS,
    SINGING_VOICE_DEFAULTS, FM_DEFAULTS,
    RANGE_MIN, RANGE_MAX, SOLO_RANGE, SWEET_SPOT,
)

print(f"Registered: choir -> {ALL_INSTRUMENTS['choir']!r}")
print("Registry table (Vocal rows):")
for line in registry_table().splitlines():
    if line.startswith("| Vocal |"):
        print(f"  {line}")

print("\nConstants:")
print(f"  CHOIR.midi_program = {CHOIR.midi_program} (GM {CHOIR.gm_name!r})")
print(f"  range              = {RANGE_MIN}–{RANGE_MAX}")
print(f"  solo_range         = {SOLO_RANGE}, sweet_spot = {SWEET_SPOT}")
print(f"  by_name('choir')   = {by_name('choir')!r}")
print(f"  by_name('choir aahs') = {by_name('choir aahs')!r}")
print(f"  by_program(52)     = {by_program(52)!r}")
print(f"  by_program(53)     = {by_program(53)!r}  (human_voice — distinct)")
print(f"  stem_label         = {CHOIR.stem_label!r}")
print(f"  zones              = {CHOIR.zones}")
print(f"  articulations      = {list(CHOIR.articulations)}")
print(f"  synthesis          = {CHOIR.synthesis}")
print(f"  reverb_tail        = {CHOIR.reverb_tail}s, pan = {CHOIR.pan}")
print(f"  A4 = {midi_to_freq(69):.1f} Hz, C4 = {midi_to_freq(60):.1f} Hz")
assert by_program(52) is CHOIR
assert by_program(53) is not CHOIR, "GM53 must stay human_voice"
assert CHOIR.in_sweet_spot(64) is True
assert CHOIR.in_sweet_spot(24) is False

# 2) Engine test: UnitMatrixComposer — ONE voice (the choir), 1 bar
from structures import MusicEvent, MusicUnit  # noqa: E402
from workflows.unitmatrix_composer import UnitMatrixComposer  # noqa: E402

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Choir", program=CHOIR.midi_program, channel=0)
comp.add_section("A", bars=1)

BAR = 1920
# Choral voicing: bass G2 + C3-G3-C4-E4 stacked "ah" chord, whole bar, flush
# at BAR (terminal landmark -> zero drift).
u = MusicUnit()
for p in [43, 48, 55, 60, 64]:
    u.add_event(MusicEvent(p, 74, 0, BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/choir_test.mid"
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# 3) SOLO render (instrument alone — no second melodic patch)
from _test.render_audio import render_midi, spectral_buzz_check  # noqa: E402

wav = "/opt/data/projects/Instruments/_test/choir_test.wav"
render_midi(midi_path, wav, solo=0)
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# 4) Empirical FluidR3 pitch sweep (RMS per note, patch audibility)
import wave  # noqa: E402
import numpy as np  # noqa: E402
from sound.render.fluidsynth import discover_soundfont  # noqa: E402

sf2 = discover_soundfont()
print(f"\nSoundFont: {sf2}")


def note_rms(midi_note, vel=74, dur=BAR):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("Choir", program=52, channel=0)
    c.add_section("A", bars=1)
    uu = MusicUnit()
    uu.add_event(MusicEvent(midi_note, vel, 0, dur))
    c.set_unit(0, 0, uu)
    okk, _ = c.validate()
    assert okk
    p = f"/opt/data/projects/Instruments/_test/_choir_sweep_{midi_note}.mid"
    c.to_midi(p)
    w = f"/opt/data/projects/Instruments/_test/_choir_sweep_{midi_note}.wav"
    render_midi(p, w, solo=0)
    with wave.open(w, "rb") as f:
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)
    return float(np.sqrt(np.mean(raw.astype(np.float64) ** 2)))


print("Pitch sweep (RMS, velocity 74, 1-bar held notes):")
sweep = {}
for n in [24, 36, 40, 48, 60, 72, 84, 88, 96]:
    rms = note_rms(n)
    sweep[n] = rms
    print(f"  note {n:3d}: RMS = {rms:8.1f} {'AUDIBLE' if rms > 100 else 'SILENT'}")
audible = [n for n, r in sweep.items() if r > 100]
assert len(audible) == len(sweep), f"preset 52 gaps at {sorted(set(sweep)-set(audible))}"
print(f"  audible notes: {audible} (no gaps — SF2 never clips a composition)")

# 5) SF2 preset name + stem label from the REAL pipeline list
import struct  # noqa: E402
import inspect  # noqa: E402
import re  # noqa: E402

data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
print(f"\nSF2 preset 52 -> {preset_names.get((0, 52), 'MISSING')!r} "
      f"(53 -> {preset_names.get((0, 53), 'MISSING')!r})")

from sound.render.pipeline import RenderPipeline  # noqa: E402

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"  GM_PROGRAMS[52] = {labels[52]!r}")
assert labels[52] == "Choir Aahs", f"stem label mismatch: {labels[52]!r}"
from Vocal.choir.choir import STEM_LABEL  # noqa: E402
assert STEM_LABEL == "Choir_Aahs"

# 6) Stem render through the real pipeline
out_dir = "/opt/data/projects/Instruments/_test/stems_choir"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
    assert os.path.getsize(fp) > 40, f"empty stem {f}"
assert any("Choir_Aahs" in f for f in stem_files), f"no Choir_Aahs stem in {stem_files}"

# 7) Additive smoke: choir envelope must HOLD sustain (2026-10-11 tail fix).
#    QUIRK (documented for synth_pad): apply_overtones leaves self.frequency at
#    the TOP partial, so decay_S is PER-GRID-STEP — use decay_S ~1e-4.
from sound.synthesis.additive import SoundWave  # noqa: E402

sw = SoundWave(sample_rate=22050, duration=2.0, frequency=midi_to_freq(60))
harm = np.array(ADDITIVE_HARMONICS["choir_ah"], dtype=float)
harm = harm / harm.sum()
sw.apply_overtones(harm.tolist())
sw.get_adsr_weights([0.18, 0.07, 0.65, 0.10], [0.2, 0.3, 0.0001, 0.1],
                    sustain_level=0.88)
w = sw.weights
n = w.shape[0]
late_w = float(np.max(w[int(0.7 * n):int(0.9 * n)]))
print(f"\nAdditive choir envelope: weights_len={n} late-sustain max={late_w:.3f} "
      f"(target ≥ 0.45 — the 2026-10-11 collapse-bug gate)")
assert late_w >= 0.45, f"additive choir envelope collapsed: late max {late_w:.3f}"

# 8) SingingVoice secondary engine smoke: one section voice sustains + vibrato
from sound.synthesis.singing_voice import SingingVoice  # noqa: E402

sv = SingingVoice(sample_rate=22050, voice_type=SINGING_VOICE_DEFAULTS["voice_type"])
note = sv.render_note(midi=64, dur=1.5, vowel="a", amp=0.8,
                      vibrato_hz=SINGING_VOICE_DEFAULTS["vibrato_hz"],
                      vibrato_semitones=SINGING_VOICE_DEFAULTS["vibrato_depth"],
                      aspiration=SINGING_VOICE_DEFAULTS["breathiness"],
                      shimmer=SINGING_VOICE_DEFAULTS["shimmer"], seed=7)
peak = float(np.max(np.abs(note)))
sustain = float(np.sqrt(np.mean(note[11025:13230] ** 2)))  # t = 0.5–0.6 s
print(f"SingingVoice section voice (alto, E4): peak={peak:.3f} "
      f"sustain_rms={sustain:.4f} sustain/peak={sustain/peak:.3f}")
assert peak > 0, "SingingVoice choir voice silent"
assert sustain / peak > 0.15, f"section voice collapses (sustain/peak={sustain/peak:.3f})"

# Section stack: 4 detuned voices -> chorus thickness (RMS grows, no nulls)
from Vocal.choir.choir import SYNTHESIS_DEFAULTS as SD  # noqa: E402

d = SD["detune"]
stack = np.zeros(33075)
for k in range(SD["stack"]):
    cents = (k - (SD["stack"] - 1) / 2) * d * 100 * 2
    v = SingingVoice(sample_rate=22050, voice_type="alto")
    f_ratio = 2.0 ** (cents / 1200.0)
    midi_shift = 12 * np.log2(f_ratio)
    stack += v.render_note(midi=64 + midi_shift, dur=1.5, vowel="a", amp=0.8,
                           vibrato_hz=5.2, vibrato_semitones=0.28,
                           aspiration=0.22, shimmer=0.05, seed=k)
stack_rms = float(np.sqrt(np.mean((stack / SD["stack"]) ** 2)))
print(f"Section stack ({SD['stack']} voices, ±{d*100:.2f}% detune): "
      f"rms={stack_rms:.4f}, max={float(np.max(np.abs(stack))):.3f}")
assert stack_rms > 0.01, "section stack sums to near-silence (phase cancellation)"

print("\nALL CHECKS PASSED")
