"""Smoke tests for surveillance 2026-09-10 gear replicas.

Six replicable findings from the 2026-09-10 scan:

* Teaching Machines FuzzBillion  -> sound/effects/topology_distortion.py (SP-069)
* ZERO9 Fusion Filter            -> sound/effects/morph_filter.py        (SP-070)
* ZERO9 Severed Space / Eccentric Echo / Fractured Frequency /
  Crushing Compressor            -> sound/effects/severance.py           (SP-071)
* Crow Hill Brackish Pads        -> sound/synthesis/critter_pad.py       (SP-072)
* Muro Box N40 (twin comb)       -> sound/synthesis/music_box.py         (SP-073)
* Erica Synths Bullfrog Drums    -> sound/generators/drum_machine.py     (SP-074)
"""
import numpy as np

from sound.effects.topology_distortion import (
    FuzzBillion, ELEMENTS, ELEMENT_NAMES, circuit_count, random_code,
    code_from_switches)
from sound.effects.morph_filter import FusionFilter, CHARACTERS
from sound.effects.severance import (
    GatedReverb, DualEngineDelay, RhythmicGlitchChain, ParallelBandCompressor,
    spectral_declash)
from sound.synthesis.critter_pad import (
    PadPartialBank, Critters, pump_envelope, cassette, splosh)
from sound.synthesis.music_box import (
    TwinCombMusicBox, MusicBoxComb, TINE_RATIOS, midi_to_freq,
    DEFAULT_DETUNE_CENTS)
from sound.generators.drum_machine import (
    BullfrogDrums, Kit, SampleChannel, synthesize_drum_samples, X0X_STEPS)

SR = 22050


def _tone(f0=150.0, seconds=0.3, sr=SR):
    tt = np.arange(int(sr * seconds)) / sr
    return 0.5 * np.sin(2 * np.pi * f0 * tt)


# -------------------------------------------------------- topology distortion
def test_fuzzbillion_switch_matrix():
    assert circuit_count() == 10 ** 11
    assert len(ELEMENTS) == 10
    assert len(ELEMENT_NAMES) == 10
    code = random_code(seed=3)
    assert len(code) == 11 and all(0 <= c < 10 for c in code)
    assert code_from_switches(code) == code
    try:
        code_from_switches([0] * 10)
    except ValueError:
        pass
    else:
        raise AssertionError("short switch list must raise")


def test_fuzzbillion_knee_ordering_and_io():
    sr = SR
    fb = FuzzBillion(sample_rate=sr)
    tone = _tone(110.0, 0.25, sr)
    ge = fb.process(tone, code=(4,) + (0,) * 10)
    led = fb.process(tone, code=(7,) + (0,) * 10)
    assert not np.allclose(ge, led)
    c_ge = fb.profile(code=(4,) + (0,) * 10, seconds=0.2)["centroid"]
    c_si = fb.profile(code=(5,) + (0,) * 10, seconds=0.2)["centroid"]
    c_led = fb.profile(code=(7,) + (0,) * 10, seconds=0.2)["centroid"]
    assert c_ge > c_si > c_led
    inst = fb.process(tone, gain=3.0, io_mode="inst")
    line = fb.process(tone, gain=3.0, io_mode="line")
    assert not np.allclose(inst, line)
    assert np.all(np.isfinite(inst))


# ------------------------------------------------------------- morph filter
def test_fusion_filter_five_characters():
    ff = FusionFilter(sample_rate=SR)
    src = _tone(150.0, 0.3)
    outs = []
    for i, name in enumerate(CHARACTERS):
        out = ff.process(src, cutoff=1200.0, resonance=0.8, position=float(i))
        assert np.all(np.isfinite(out)), name
        outs.append(out)
    # each character must be a genuinely different response
    for i in range(len(outs) - 1):
        assert not np.allclose(outs[i], outs[i + 1])


def test_fusion_filter_morph_blends_and_stays_stable():
    ff = FusionFilter(sample_rate=SR)
    src = _tone(150.0, 0.3)
    a = ff.process(src, resonance=0.8, position=0.0)
    m = ff.process(src, resonance=0.8, position=0.5)
    b = ff.process(src, resonance=0.8, position=1.0)
    assert not np.allclose(a, m) and not np.allclose(b, m)
    w = ff.morph_positions(0.5)
    assert abs(sum(w.values()) - np.sqrt(2.0)) < 1e-6   # equal-power pair
    hot = ff.process(src, cutoff=800.0, resonance=0.99, position=2.5, drive=3.0)
    assert np.all(np.isfinite(hot))


# ----------------------------------------------------------------- ZERO9 kit
def test_gated_reverb_closes_tail():
    sr = SR
    n = int(sr * 0.8)
    tt = np.arange(n) / sr
    src = np.zeros(n)
    src[int(0.1 * sr):int(0.12 * sr)] = 1.0
    gr = GatedReverb(sample_rate=sr)
    out = gr.process(src, triggers=[0.11], gate_len=0.15)
    assert np.all(np.isfinite(out)) and len(out) == n
    # energy well after the gate close must be far below energy inside it
    inside = float(np.sum(out[int(0.11 * sr):int(0.24 * sr)] ** 2))
    after = float(np.sum(out[int(0.40 * sr):int(0.70 * sr)] ** 2))
    assert inside > after


def test_dual_engine_delay_routings_differ():
    dd = DualEngineDelay(sample_rate=SR)
    src = _tone(110.0, 0.4)
    ser = dd.process(src, routing="serial")
    par = dd.process(src, routing="parallel")
    assert not np.allclose(ser, par)
    assert np.all(np.isfinite(ser)) and np.all(np.isfinite(par))
    try:
        dd.process(src, routing="bogus")
    except ValueError:
        pass
    else:
        raise AssertionError("bad routing must raise")


def test_glitch_chain_and_parallel_band_compressor():
    src = _tone(140.0, 0.4)
    gc = RhythmicGlitchChain(sample_rate=SR)
    out = gc.process(src, bpm=120.0)
    assert not np.allclose(out, src)
    pc = ParallelBandCompressor(sample_rate=SR)
    comp = pc.process(src)
    assert np.all(np.isfinite(comp)) and len(comp) == len(src)
    dc = spectral_declash(src, SR)
    assert len(dc) == len(src)


# ------------------------------------------------------------- critter pad
def test_pad_partial_bank_rebalance_changes_output():
    bank = PadPartialBank(sample_rate=SR)
    a = bank.render_note(110.0, duration=1.5, seed=3)
    bank.balance["critters"] = 0.0
    b = bank.render_note(110.0, duration=1.5, seed=3)
    assert not np.allclose(a, b)
    assert np.all(np.isfinite(a)) and np.max(np.abs(a)) > 0.2


def test_critters_is_stochastic_and_microtonal():
    cr = Critters(sample_rate=SR, density=3.0)
    a = cr.render(220.0, 1.0, seed=1, sr=SR)
    b = cr.render(220.0, 1.0, seed=2, sr=SR)
    assert not np.allclose(a, b)
    assert cr.microtonal_set in ("quarter-tone", "eighth-tone", "just-ish",
                                 "chromatic-drift")
    assert len(cr.trigger_times(1.0, seed=1)) >= 1


def test_cassette_splosh_pump_finite():
    src = _tone(200.0, 0.3)
    worn = cassette(src, SR, amount=0.6)
    wet = splosh(src, SR, mix=0.3)
    env = pump_envelope(len(src), SR, which=1)
    assert np.all(np.isfinite(worn)) and np.all(np.isfinite(wet))
    assert len(env) == len(src) and env.max() > 0.5


# ---------------------------------------------------------------- music box
def test_music_box_inharmonic_partials():
    assert TINE_RATIOS[0] == 1.0 and TINE_RATIOS[1] > 6.0
    comb = MusicBoxComb(sample_rate=SR)
    out = comb.pluck(midi_to_freq(72), 1.0, seed=1)
    assert np.max(np.abs(out)) > 0.05
    spec = np.abs(np.fft.rfft(out * np.hanning(len(out))))
    fr = np.fft.rfftfreq(len(out), 1.0 / SR)
    f0 = midi_to_freq(72)
    band = (fr > f0 * 5.0) & (fr < f0 * 8.0)
    assert np.sum(spec[band]) > 0.0


def test_twin_comb_detune_beats():
    mb = TwinCombMusicBox(sample_rate=SR)
    assert mb.detune_cents == DEFAULT_DETUNE_CENTS
    note = mb.render_note(72, duration=1.5, seed=1)
    assert note.shape[1] == 2 and np.all(np.isfinite(note))

    def beat_depth(x):
        env = np.abs(x[:, 0] + x[:, 1])
        tail = env[int(0.3 * SR):]
        if len(tail) < 100:
            return 0.0
        d = tail - np.convolve(tail, np.ones(200) / 200, mode="same")
        return float(np.std(d) / (np.mean(tail) + 1e-9))

    mb.detune_cents = 0.0
    unison = mb.render_note(72, duration=1.5, seed=1)
    mb.detune_cents = DEFAULT_DETUNE_CENTS
    twin = mb.render_note(72, duration=1.5, seed=1)
    assert beat_depth(twin) > beat_depth(unison)

    mel = mb.render_melody([(72, 0.0, 0.5), (76, 0.5, 0.5)], seed=5)
    assert mel.shape[1] == 2 and np.all(np.isfinite(mel))


# ------------------------------------------------------------ drum machine
def test_bullfrog_channels_and_grid_render():
    bf = BullfrogDrums(sample_rate=SR)
    assert sorted(bf.channels) == [1, 2, 3, 4, 5, 6, 7]     # + CV lane = ch 8
    bf.load_kit(Kit.demo_kit(SR))
    grid = {1: {0: 1.0, 4: 0.8}, 3: {2: 0.7, 6: 0.7}}
    audio = bf.render(grid, bpm=120.0, steps=16, bars=1, swing=0.4,
                      flams={(1, 4): 2})
    assert audio.shape[1] == 2
    assert np.all(np.isfinite(audio)) and np.max(np.abs(audio)) > 0.1
    assert len(synthesize_drum_samples(SR)) == 7
    assert X0X_STEPS == 64


def test_bullfrog_repro_params_and_cv_lane():
    sr = SR
    ch = SampleChannel(np.random.default_rng(0).standard_normal(sr // 4),
                       sample_rate=sr)
    base = ch.render(hold=0.1)
    ch.start, ch.end = 0.05, 0.6
    trimmed = ch.render(hold=0.1)
    ch.loop = 0.25
    looped = ch.render(hold=0.25)
    assert len(trimmed) < len(base)
    assert len(looped) > len(trimmed)
    ch.muted = True
    assert len(ch.render()) == 1

    bf = BullfrogDrums(sample_rate=sr)
    bf.load_kit(Kit.demo_kit(sr))
    bf.cv.set(0, 0.2)
    bf.cv.set(8, 0.9)
    seq = bf.to_cv_sequence(16)
    assert [s for s, _ in seq] == [0, 8]
    pitches = bf.cv.to_pitch_sequence(16, base_freq=55.0)
    assert pitches[0][1] > 55.0
    assert len(bf.pattern_to_midi_events({1: {0: 1.0, 4: 0.5}}, steps=16)) == 2
