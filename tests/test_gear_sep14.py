"""Smoke tests for surveillance 2026-09-14 gear replicas.

Eight replicable findings from the 2026-09-14 scan:

* Noise Engineering Legio "AT Legio" LFSR voice
      -> sound/synthesis/lfsr_voice.py        (SP-076)
* Korg Prologue "Elixir Vol 1" TZFM / STEPr
      -> sound/synthesis/tzfm.py               (SP-077)
* Rapid Flow omniGRID 16-track polymetric sequencer
      -> sound/generators/polymetric_grid.py   (SP-078)
* Born Second BS-203 MacroAcidizer
      -> sound/generators/acid_seq.py          (SP-079)
* Emergence Audio Envoy "Cadence Engine" rhythmic variator
      -> sound/generators/cadence_variator.py  (SP-080)
* Mylar Melodies / Befaco RANDOM8
      -> sound/modular/random8.py              (SP-081)
* Zlosynth Arplus
      -> sound/synthesis/string_scales.py      (SP-082)
* Sound Dust Drift Clouds (Wandering Engine + Portal)
      -> sound/modular/wandering.py            (SP-083)
"""
import numpy as np

from sound.synthesis.lfsr_voice import (
    LFSR, LFSRVoice, LFSR_MASKS, generate_bits, spectral_flatness,
    harmonic_error, pitch_from_spectrum, midi_to_freq as lfsr_midi_to_freq)
from sound.synthesis.tzfm import (
    TZFMVoice, SteppedOscillator, TZFMParams, build_bank_a, build_bank_b,
    BANKS, _lookup, WAVE_SIZE)
from sound.generators.polymetric_grid import (
    PolymetricGrid, Track, PerStepGraph, SHUFFLE_MODES, SCALES, RESOLUTIONS,
    eulerian_mask, MAX_STEPS, MIN_STEPS)
from sound.generators.acid_seq import (
    AcidVoice, AcidSequencer, MODES, STEP_DIVISIONS, SCALES as ACID_SCALES,
    AcidStep)
from sound.generators.cadence_variator import (
    CadenceEngine, CadenceLayer, FluxRandomizer, StepLanes, NUM_BLOCKS,
    MAX_BLOCK_STEPS, DIRECTIONS, FEELS)
from sound.modular.random8 import (
    Random8, RandomChannel, SCALES_15, STYLES, quantize_cv, MAX_STEPS as R8_STEPS)
from sound.synthesis.string_scales import (
    ArplusVoice, StringVoice, SCALE_GROUPS, SCALES_31, ARP_SHAPES, quantize,
    scale_pool, scale_degrees)
from sound.modular.wandering import (
    WanderingEngine, Portal, DriftCloudsVoice, ModRoute, DEFAULT_DESTINATIONS)

SR = 22050


# ------------------------------------------------------------------ LFSR voice
def test_lfsr_masks_are_maximal():
    for bits, mask in LFSR_MASKS.items():
        reg = LFSR(bits=bits, mask=mask)
        assert reg.is_maximal(), f"{bits}-bit mask {mask:#x} is not maximal"
        assert reg.measured_period() == (1 << bits) - 1


def test_lfsr_bitstream_repeats_at_one_period():
    reg = LFSR(bits=8)
    p = reg.period
    seq = generate_bits(bits=8, n_ticks=2 * p)
    assert np.array_equal(seq[:p], seq[p:])
    assert seq[:p].sum() == 128        # maximal sequences are near-balanced


def test_lfsr_tuning_law_and_pitch():
    v = LFSRVoice(sample_rate=SR, bits=8, os=8)
    clock, f0_actual, playable = v.tune(57.0)
    assert playable and abs(f0_actual - lfsr_midi_to_freq(57.0)) < 1e-9
    assert abs(clock - lfsr_midi_to_freq(57.0) * 255) < 1e-6
    audio = v.render_note(57.0, 0.5)
    line = pitch_from_spectrum(audio, SR)
    assert harmonic_error(line, lfsr_midi_to_freq(57.0)) < 0.01


def test_lfsr_long_register_is_noise_and_refused_when_tuning():
    v8 = LFSRVoice(sample_rate=SR, bits=8, os=8)
    v23 = LFSRVoice(sample_rate=SR, bits=23, os=8)
    a8 = v8.render_clock(6000.0, 0.3, bits=8)
    a23 = v23.render_clock(6000.0, 0.3, bits=23)
    assert spectral_flatness(a8) < spectral_flatness(a23)
    _, _, playable = v23.tune(69.0)
    assert not playable
    try:
        v23.render_note(69.0, 0.1, bits=23, strict=True)
    except ValueError:
        pass
    else:
        raise AssertionError("strict tuning of a 23-bit register must raise")


def test_lfsr_staircase_and_melody():
    v = LFSRVoice(sample_rate=SR, tone=0.0, staircase=1)
    flat = v.render_note(57.0, 0.2)
    v.staircase = 4
    stair = v.render_note(57.0, 0.2)
    assert len(np.unique(np.round(stair, 6))) > len(np.unique(np.round(flat, 6)))
    mel = v.render_melody([(52, 0.0, 0.2), (55, 0.2, 0.2)], bits=8)
    assert np.max(np.abs(mel)) > 0.05


# ------------------------------------------------------------------- TZFM/STEPr
def test_tzfm_banks_match_published_sizes():
    a, b = build_bank_a(), build_bank_b()
    assert len(a) == BANKS["A"] == 46
    assert len(b) == BANKS["B"] == 44
    assert all(w.shape == (WAVE_SIZE,) for w in a + b)
    assert all(np.max(np.abs(w)) <= 1.0 + 1e-9 for w in a + b)


def test_tzfm_through_zero_phase_reversal():
    v = TZFMVoice(sample_rate=SR)
    n = 512
    carrier = np.arange(n) * (220.0 / SR)
    mod = _lookup(v.bank_b[0], np.arange(n) * (220.0 / SR))
    phase = carrier + 2.0 * mod
    assert np.any(np.diff(phase) < 0), "no through-zero phase reversal"


def test_tzfm_ringmod_bitcrush_and_direction():
    v = TZFMVoice(sample_rate=SR)
    f = 220.0
    off = v.render(f, 0.3, TZFMParams(wave_a=1, wave_b=0, tzfm="off"))
    ab = v.render(f, 0.3, TZFMParams(wave_a=1, wave_b=0, tzfm="A->B", depth=0.9))
    ba = v.render(f, 0.3, TZFMParams(wave_a=1, wave_b=0, tzfm="B->A", depth=0.9))
    assert not np.allclose(ab, ba)
    assert not np.allclose(ab, off)
    ring = v.render(f, 0.3, TZFMParams(ringmod=1.0))
    assert not np.allclose(ring, off)
    clean = v.render(f, 0.3, TZFMParams())
    crush = v.render(f, 0.3, TZFMParams(bitcrush=1.0, crush_bits=4))
    assert len(np.unique(np.round(crush, 6))) < len(np.unique(np.round(clean, 6)))


def test_stepr_advances_a_bank_per_note():
    s = SteppedOscillator(sample_rate=SR, step_a=1, step_mode="AB")
    mel = [(55, 0.0, 0.2), (57, 0.2, 0.2), (59, 0.4, 0.2)]
    audio, used = s.render_melody(mel, TZFMParams(tzfm="A->B", depth=0.4))
    assert used == [0, 1, 2]
    assert audio.size > 0
    s2 = SteppedOscillator(sample_rate=SR, step_mode="A", step_a=3)
    _, used2 = s2.render_melody(mel)
    assert used2 == [0, 3, 6]
    s3 = SteppedOscillator(sample_rate=SR, step_mode="B", step_b=3)
    _, used3 = s3.render_melody(mel)
    assert used3 == [0, 0, 0]


# ------------------------------------------------------------- polymetric grid
def test_polymetric_grid_limits_and_periods():
    g = PolymetricGrid(bpm=120)
    t = g.add_track(1, steps=16, note=36)
    assert t.period_beats == 4.0
    try:
        g.add_track(2, steps=MAX_STEPS + 1)
    except ValueError:
        pass
    else:
        raise AssertionError("steps above the maximum must raise")
    try:
        g.add_track(2, steps=MIN_STEPS - 1)
    except ValueError:
        pass
    else:
        raise AssertionError("steps below the minimum must raise")
    try:
        g.add_track(17)
    except ValueError:
        pass
    else:
        raise AssertionError("more than 16 tracks must raise")


def test_eulerian_mask_is_even_and_rotates():
    pat = eulerian_mask(5, 12)
    assert sum(pat) == 5
    on = [i for i, v in enumerate(pat) if v]
    gaps = [on[i + 1] - on[i] for i in range(len(on) - 1)]
    assert max(gaps) - min(gaps) <= 1
    assert eulerian_mask(5, 12, rotation=2) != pat


def test_polymetric_grid_ensemble_and_shuffle():
    g = PolymetricGrid(bpm=120)
    g.add_track(1, steps=16, note=36).set_pattern([127, 0, 0, 0] * 4)
    g.add_track(2, steps=12, note=42).set_pattern([0, 90, 0, 70] * 3)
    g.add_track(3, steps=7, note=40).set_pattern([110, 0, 95, 0, 0, 100, 0])
    assert len({t.period_beats for t in g.tracks.values()}) == 3
    assert g.ensemble_period_beats > 0
    assert len(SHUFFLE_MODES) == 8
    a = [e[0] for e in g.render(loops=1, seed=1)]
    g.set_shuffle("mpc60", 1.0)
    b = [e[0] for e in g.render(loops=1, seed=1)]
    assert a and len(a) == len(b)
    assert not np.allclose(a, b)
    try:
        g.set_shuffle("nope")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown shuffle must raise")


def test_polymetric_grid_scale_quantise_and_midi():
    g = PolymetricGrid(bpm=120, root=0, scale="minor")
    trk = g.add_track(1, steps=8, note=64)
    assert all((p - 0) % 12 in SCALES["minor"] for p in
               [g.quantize(n) % 12 for n in range(60, 72)])
    ev = g.to_midi_events(loops=1, seed=3, ticks_per_beat=480)
    assert all(e["end_tick"] > e["start_tick"] for e in ev)


def test_per_step_graphs_randomise_within_bounds():
    gr = PerStepGraph("velocity", 100.0, 1.0, 127.0)
    gr.set(0, 127.0)
    assert gr.get(0) == 127.0 and gr.get(5) == 100.0
    gr.randomize(1.0, np.random.default_rng(1), 16)
    assert 1.0 <= min(gr.values.values()) and max(gr.values.values()) <= 127.0


# ----------------------------------------------------------------- acid seq
def test_acid_modes_and_scale_lock():
    assert set(MODES) == {"303", "202", "BB"}
    seq = AcidSequencer(scale="minor", density=0.6, seed=5)
    steps = seq.randomize(16)
    pool = set(seq._pitch_pool())
    assert all(s.offset in pool for s in steps)
    assert steps[0].step == 0 and steps[0].offset == 0
    assert abs(len(steps) - round(0.6 * 16)) <= 1


def test_acid_time_divisions_and_determinism():
    for div, spb in STEP_DIVISIONS.items():
        s = AcidSequencer(division=div)
        assert abs(s.steps_per_beat - spb) < 1e-9
    a = AcidSequencer(seed=11).randomize(16)
    b = AcidSequencer(seed=11).randomize(16)
    c = AcidSequencer(seed=12).randomize(16)
    assert [(s.step, s.offset) for s in a] == [(s.step, s.offset) for s in b]
    assert [(s.step, s.offset) for s in a] != [(s.step, s.offset) for s in c]


def test_acid_modes_sound_different_and_slide():
    sr = SR
    steps = AcidSequencer(seed=7).randomize(8)
    cents = {}
    for mode in MODES:
        v = AcidVoice(sample_rate=sr, mode=mode)
        a = v.render_sequence(steps, bpm=130.0, root_note=33)
        assert np.all(np.isfinite(a))
        spec = np.abs(np.fft.rfft(a * np.hanning(a.size)))
        fr = np.fft.rfftfreq(a.size, 1.0 / sr)
        cents[mode] = float(np.sum(fr * spec) / (np.sum(spec) + 1e-12))
    assert len({round(c, 1) for c in cents.values()}) == 3
    assert cents["202"] > cents["303"]

    v = AcidVoice(sample_rate=sr, mode="303")
    step_s = 60.0 / 130.0 / 4.0
    slid = v.render_step(12, step_s, step_s * 0.8, False, 0, True, 33)
    jumped = v.render_step(12, step_s, step_s * 0.8, False, 0, False, 33)
    n_glide = int(v.slide_time * sr)
    assert not np.allclose(slid[:n_glide], jumped[:n_glide])


def test_acid_accent_is_more_than_velocity():
    v = AcidVoice(sample_rate=SR, mode="303")
    step_s = 60.0 / 130.0 / 4.0
    acc = v.render_step(0, step_s, step_s * 0.8, True, 0, False, 33)
    plain = v.render_step(0, step_s, step_s * 0.8, False, 0, False, 33)

    def cen(x):
        X = np.abs(np.fft.rfft(x * np.hanning(x.size)))
        f = np.fft.rfftfreq(x.size, 1.0 / SR)
        return float(np.sum(f * X) / (np.sum(X) + 1e-12))
    assert cen(acc) >= cen(plain) * 0.98


# ------------------------------------------------------------ cadence variator
def test_cadence_blocks_and_totals():
    eng = CadenceEngine(bpm=120)
    lo = eng.add_layer("low", block_steps=[8, 8, 4, 6])
    hi = eng.add_layer("high", block_steps=[7, 5, 8, 8])
    assert len(lo.blocks) == NUM_BLOCKS == 4
    assert all(b.steps <= MAX_BLOCK_STEPS for b in lo.blocks + hi.blocks)
    assert lo.total_steps == 26 and hi.total_steps == 28
    try:
        CadenceLayer("x", block_steps=[9])
    except ValueError:
        pass
    else:
        raise AssertionError("a wrong block count must raise")


def test_cadence_step_lanes_and_rest():
    eng = CadenceEngine(bpm=120)
    lo = eng.add_layer("low", block_steps=[8, 8, 4, 6])
    lo.blocks[0].set_step(0, velocity=127, pitch=0, length=0.9, pan=-0.6,
                          hp=120, lp=2000)
    lanes = lo.lanes_at(0)
    assert lanes["pan"] == -0.6 and lanes["hp"] == 120.0
    lo.blocks[0].lanes.velocity[7] = 0.0
    ev = eng.render_events(loops=1, seed=1, apply_flux=False)
    assert not [e for e in ev if e["layer"] == "low" and e["step"] == 7]


def test_cadence_directions_and_feels():
    layer = CadenceLayer("x", block_steps=[8, 8, 8, 8], direction="reverse")
    assert layer.step_index(0) == layer.total_steps - 1
    layer.direction = "pingpong"
    seq = [layer.step_index(p) for p in range(2 * layer.total_steps)]
    assert seq[0] == 0 and max(seq) == layer.total_steps - 1
    for feel in FEELS:
        layer.feel = feel
        assert isinstance(layer.feel_offset(0), float)
    try:
        CadenceLayer("y", direction="sideways")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown direction must raise")


def test_flux_randomizer_depth_and_targeting():
    eng = CadenceEngine(bpm=120)
    lo = eng.add_layer("low", block_steps=[8, 8, 8, 8])
    base = eng.render_events(loops=1, seed=3, apply_flux=False)
    base_v = [float(e["velocity"]) for e in base if e["layer"] == "low"]

    eng.flux = FluxRandomizer(depth=0.0, blocks=[0, 2], seed=9)
    same = [e for e in eng.render_events(loops=1, seed=3, apply_flux=True)
            if e["layer"] == "low"]
    assert all(a["velocity"] == b["velocity"] for a, b in zip(base, same))

    # Depth-proportional jitter, measured on the lane arrays themselves (event
    # counts can shift when flux pushes a velocity past the rest threshold).
    def jitter(depth, blocks):
        layer = CadenceLayer("m", block_steps=[8, 8, 8, 8])
        before = layer.blocks[0].lanes.velocity.copy()
        FluxRandomizer(depth=depth, blocks=blocks,
                       seed=11).apply(layer, np.random.default_rng(11))
        return float(np.mean(np.abs(layer.blocks[0].lanes.velocity - before)))

    assert jitter(0.5, [0, 2]) > jitter(0.1, [0, 2]) > 0.0
    assert jitter(1.0, [0, 2]) > jitter(0.5, [0, 2])
    # targeting blocks 2,3 leaves block 0 untouched
    assert jitter(0.5, [2, 3]) == 0.0

    # per-block targeting: block 1 is untouched when flux names block 0 only
    eng.flux = FluxRandomizer(depth=0.8, blocks=[0], seed=4)
    before = lo.blocks[1].lanes.velocity.copy()
    eng.render_events(loops=1, seed=4, apply_flux=True)
    assert np.allclose(before, lo.blocks[1].lanes.velocity)

    # ranges stay legal
    eng.flux = FluxRandomizer(depth=1.0, blocks=None, seed=8)
    eng.flux.apply(lo, np.random.default_rng(8))
    for b in lo.blocks:
        assert b.lanes.velocity.min() >= 1.0
        assert b.lanes.velocity.max() <= 127.0
        assert b.lanes.pan.min() >= -1.0 and b.lanes.pan.max() <= 1.0
        assert np.all(b.lanes.lp >= b.lanes.hp * 1.2)


def test_cadence_independent_lfos():
    eng = CadenceEngine(bpm=120, master_lfo_rate=1.3)
    a = eng.add_layer("a", block_steps=[8] * 4, rate=2)
    b = eng.add_layer("b", block_steps=[7, 5, 8, 8], rate=3)
    a.lfo_rate, a.lfo_depth = 0.4, 0.3
    b.lfo_rate, b.lfo_depth = 2.7, 0.3
    assert a.lfo_value(0.1) != b.lfo_value(0.1)
    ev = eng.render_events(loops=2, seed=12, apply_flux=False)
    assert len({e["layer"] for e in ev}) == 2


# ---------------------------------------------------------------- RANDOM8
def test_random8_bank_sizes():
    assert len(SCALES_15) == 15
    assert len(STYLES) == 6
    assert R8_STEPS == 32
    r8 = Random8()
    assert len(r8.channels) == 8


def test_random8_quantise_after_attenuation():
    r8 = Random8(seed=11)
    r8.set_preset(0, attenuate=0.35, scale="hirajoshi")
    r8.set_preset(1, attenuate=0.35, scale=None)
    out = r8.process(64)
    assert len(np.unique(np.round(out[0], 6))) < len(np.unique(np.round(out[1], 6)))
    again = np.array([quantize_cv(v, "hirajoshi") for v in out[0]])
    assert np.allclose(out[0], again, atol=1e-12)


def test_random8_offset_and_attenuate():
    r8 = Random8(seed=5)
    r8.set_preset(0, offset=0.0, attenuate=1.0)
    r8.set_preset(1, offset=0.6, attenuate=1.0)
    o = r8.process(120)
    assert o[1].min() > o[0].min()
    r8.set_preset(2, attenuate=0.25)
    o2 = r8.process(120)
    assert o2[2].max() < o2[0].max()


def test_random8_dividr_and_probability():
    for div, expect in ((1, 15), (4, 3), (8, 1)):
        r8 = Random8(seed=7)
        r8.set_preset(0, dividr=div, scale=None, style="uniform")
        vals = r8.process(16)[0]
        changes = int(np.sum(np.diff(vals) != 0))
        assert changes <= expect + 1
    r8 = Random8(seed=8)
    r8.set_preset(0, probability=0.25, scale=None, style="uniform")
    vals = r8.process(80)[0]
    assert int(np.sum(np.diff(vals) != 0)) < 40
    try:
        r8.set_preset(0, dividr=9)
    except ValueError:
        pass
    else:
        raise AssertionError("dividr above 8 must raise")


def test_random8_cascading_trigs_and_loops():
    trig_map = {0: [1] * 8, 3: [1, 0, 1, 0, 1, 0, 1, 0]}
    r8 = Random8(seed=9)
    for c in r8.channels:
        c.scale, c.style = None, "uniform"
    out = r8.process(8, trigs=trig_map, cascading=True)
    assert int(np.sum(np.diff(out[4]) != 0)) > 0

    ch = r8.channel(0)
    assert [ch.cycle_loop_mode() for _ in range(3)] == ["evolve", "loop", "random"]
    ch.loop_mode, ch.steps = "loop", 8
    ch._buffer = list(np.linspace(0.0, 1.0, 8))
    ch._cursor = 0
    looped = r8.process(16)[0]
    assert np.allclose(looped[:8], looped[8:])


def test_random8_styles_and_slide():
    stats = {}
    for style in STYLES:
        r8 = Random8(seed=3)
        r8.set_preset(0, style=style)
        vals = r8.process(300)[0]
        stats[style] = (float(vals.std()), float(np.mean(np.abs(np.diff(vals)))),
                        float(np.mean((vals > 0.95) | (vals < 0.05))))
    assert stats["uniform"][0] > stats["bell"][0]
    assert stats["drift"][1] < stats["uniform"][1]
    assert stats["burst"][2] > stats["bell"][2]

    r8 = Random8(seed=17)
    c = r8.channel(0)
    c.style, c.scale, c.slide = "uniform", None, 1.0
    vals = r8.process(8)[0]
    stream = c.apply_slide(np.repeat(vals, 64), SR, max_time=0.05)
    hard = np.abs(np.diff(np.repeat(vals, 64)))
    assert np.abs(np.diff(stream)).max() < hard.max() / 10.0
    c.slide = 0.0
    assert np.allclose(c.apply_slide(np.repeat(vals, 64), SR), np.repeat(vals, 64))


# ------------------------------------------------------------ string scales
def test_string_scales_bank_and_groups():
    assert len(SCALES_31) == 31
    assert sum(len(v) for v in SCALE_GROUPS.values()) == 31
    assert all(n in SCALES_31 for names in SCALE_GROUPS.values() for n in names)


def test_string_quantise_and_chords():
    assert quantize(61.4, "quarter_tone", 60) == 61.5
    assert quantize(61.4, "whole_tone", 60) == 62.0
    v = ArplusVoice(sample_rate=SR)
    for size in (3, 5, 8):
        assert len(v.chord(60, "mayamalavagowla", size=size)) == size
    assert all(m in scale_pool("hirajoshi", 60) for m in v.chord(60, "hirajoshi", 4))


def test_string_arp_shapes():
    v = ArplusVoice(sample_rate=SR)
    notes = [60, 62, 64, 67, 69]
    for shape in ARP_SHAPES:
        seq = v.arpeggiate(notes, 6, shape, seed=1)
        assert len(seq) == 6
    up = [notes.index(m) for m in v.arpeggiate(notes, 4, "up")]
    down = [notes.index(m) for m in v.arpeggiate(notes, 4, "down")]
    assert down == [len(notes) - 1 - i for i in up]
    assert all(m == notes[0] for m in v.arpeggiate(notes, 3, "chord"))


def test_string_karplus_pitch_and_arpeggio():
    v = ArplusVoice(sample_rate=SR)
    x = v.render_chord(notes=[57.0], duration=1.2, decay=0.997, damping=8000.0)
    ac = np.correlate(x - x.mean(), x - x.mean(), mode="full")[x.size - 1:]
    ac /= ac[0] + 1e-12
    lo, hi = int(SR / 400.0), int(SR / 100.0)
    lag = lo + int(np.argmax(ac[lo:hi]))
    assert abs(SR / lag - 220.0) / 220.0 < 0.06
    arp = v.render_chord(root=60, scale="hirajoshi", chord_size=5, duration=1.5,
                         arp="up", steps=8, step_rate=8.0)
    chord = v.render_chord(root=60, scale="hirajoshi", chord_size=5, duration=1.5)
    assert not np.allclose(arp, chord)


def test_string_external_excitation_filters_the_input():
    v = ArplusVoice(sample_rate=SR)
    noise = np.random.default_rng(3).standard_normal(SR) * 0.5
    res = v.resonate(noise, root=60, scale="maqam_hijaz", chord_size=5,
                     input_mix=0.7)

    def flat(s):
        s = s + 1e-12
        return float(np.exp(np.mean(np.log(s))) / np.mean(s))
    assert flat(np.abs(np.fft.rfft(res * np.hanning(res.size)))) < \
        flat(np.abs(np.fft.rfft(noise * np.hanning(noise.size))))
    assert np.all(np.isfinite(res))


# ---------------------------------------------------------------- wandering
def test_wandering_is_not_an_lfo():
    sr = SR
    cv = WanderingEngine(sample_rate=sr, seed=3).process(int(sr * 6))

    def reversal_cv(sig):
        x = np.convolve(sig, np.ones(sr // 10) / (sr // 10), mode="same")
        d = np.sign(np.diff(x))
        d = d[d != 0]
        idx = np.where(np.diff(d) != 0)[0]
        iv = np.diff(idx) / float(sr)
        return float(iv.std() / iv.mean()) if iv.size >= 2 else 0.0

    t = np.arange(cv.size) / sr
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t)
    assert reversal_cv(cv) > 8.0 * reversal_cv(lfo)


def test_wandering_slew_and_stall_controls():
    sr = SR

    def mean_speed(slew, stall, seed=11):
        e = WanderingEngine(sample_rate=sr, seed=seed, rate=0.9, wobble=0.8,
                            stall_probability=stall)
        v = e.process(int(sr * 3), slew=slew)
        return float(np.mean(np.abs(np.diff(v))))

    assert mean_speed(1.0, 0.3) < mean_speed(0.0, 0.3) / 5.0
    # a high stall probability freezes more of the signal; average over seeds
    free = float(np.mean([mean_speed(0.0, 0.0, s) for s in (11, 12, 13, 14)]))
    stalled = float(np.mean([mean_speed(0.0, 1.0, s) for s in (11, 12, 13, 14)]))
    assert stalled < free, f"stalls must damp motion ({stalled} vs {free})"


def test_portal_routing_maths():
    p = Portal(seed=5)
    p.add_route("drift", "filter_cutoff", 0.4)
    p.add_route("portal", "filter_cutoff", 0.5)
    p.add_route("drift", "pan", 0.3)
    mods = p.apply({"drift": 1.0, "portal": 1.0})
    assert abs(mods["filter_cutoff"] - 0.9) < 1e-9
    assert abs(mods["pan"] - 0.3) < 1e-9
    p.routes[0].enabled = False
    assert abs(p.apply({"drift": 1.0, "portal": 1.0})["filter_cutoff"] - 0.5) < 1e-9
    try:
        p.reroute(1, destination="not_a_destination")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown destination must raise")
    assert p.reroute(1, destination="volume").destination == "volume"


def test_portal_surprise_never_empties():
    p = Portal(seed=7)
    for i, d in enumerate(DEFAULT_DESTINATIONS[:5]):
        p.add_route(f"src{i}", d, 0.3 + 0.1 * i)
    n = len(p.routes)
    p.surprise(amount=1.0, n=n)
    assert len(p.routes) == n
    assert all(r.destination in DEFAULT_DESTINATIONS for r in p.routes)
    assert p.surprise(amount=0.0) == 0


def test_drift_clouds_voice_two_layers():
    sr = SR
    tt = np.arange(int(sr * 2)) / sr
    cloud = 0.6 * np.sin(2 * np.pi * 220 * tt) * np.exp(-tt)
    shadow = 0.4 * np.sin(2 * np.pi * 110 * tt) * np.exp(-tt)
    v = DriftCloudsVoice(sample_rate=sr, mod_wheel=0.5, seed=4)
    out = v.render(cloud, shadow, n_blocks=32)
    assert out.shape == (cloud.size, 2)
    assert np.all(np.isfinite(out))
    assert abs(sum(v.balance) - 1.0) < 1e-9
    v2 = DriftCloudsVoice(sample_rate=sr, mod_wheel=0.9, seed=4)
    assert v2.balance[0] > v.balance[0]
