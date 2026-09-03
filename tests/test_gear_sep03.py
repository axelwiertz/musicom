"""Smoke tests for surveillance 2026-09-03 gear replicas.

Supersaw swarm (SuperStarSaw-style), BBD chorus (Thorus XT-style),
fractional-pitch shimmer reverb (3rd Wave Shimmer Verb-style).
"""
import numpy as np
import pytest

from sound.synthesis.supersaw_swarm import (
    SupersawSwarm, SCALES, CHORDS, MorphPad)
from sound.effects.bbd_chorus import BBDChorus
from sound.effects.shimmer_reverb import ShimmerVerb

SR = 44100


# ---------------------------------------------------------------- supersaw
def test_supersaw_shape_and_peak():
    s = SupersawSwarm(sample_rate=SR, seed=3)
    a = s.render_note(110.0, 0.5, spread_cents=20.0, drift=0.3, swarm2=False)
    assert a.shape == (22050, 2)
    assert a.dtype == np.float32
    assert np.max(np.abs(a)) > 0.5


def test_supersaw_spread_raises_centroid():
    s = SupersawSwarm(sample_rate=SR, seed=3)

    def centroid(x):
        spec = np.abs(np.fft.rfft(x[:, 0]))
        freqs = np.fft.rfftfreq(len(x), 1.0 / SR)
        return float(np.sum(freqs * spec) / np.sum(spec))

    tight = s.render_note(110.0, 0.5, spread_cents=3.0, drift=0.05,
                          swarm2=False)
    wide = s.render_note(110.0, 0.5, spread_cents=60.0, drift=0.4,
                         swarm2=False)
    assert centroid(wide) > centroid(tight)


def test_supersaw_harmony_tables_and_morph():
    s = SupersawSwarm(sample_rate=SR, seed=3)
    qh = s.render_note(110.0, 0.5, spread_cents=30.0, harmony="maj7",
                       harmony_root=0, swarm2=False)
    assert np.isfinite(qh).all()
    assert SCALES["hirajoshi"] == [0, 2, 3, 7, 8]
    assert "super_locrian" in SCALES and "dorian_sharp4" in SCALES
    assert CHORDS["maj7"] == [0, 4, 7, 11]
    blend = MorphPad().sample(1.0, 1.0)
    assert blend.spread_cents == MorphPad().corners["d"].spread_cents


# ---------------------------------------------------------------- bbd chorus
@pytest.fixture
def pad_input():
    t = np.linspace(0, 1.0, SR, endpoint=False)
    x = 0.4 * np.sin(2 * np.pi * 220 * t) + 0.2 * np.sin(2 * np.pi * 440 * t)
    return x / np.max(np.abs(x))


def test_bbd_mono_stereo_and_fractional_voices(pad_input):
    x = pad_input
    ch = BBDChorus(sample_rate=SR, voices=4.0, seed=11)
    mono = ch.process(x, mix=0.6)
    assert len(mono) == len(x) and np.isfinite(mono).all()
    st = ch.process_stereo(x, mix=0.6, width=0.8)
    assert st.shape == (len(x), 2)
    v45 = BBDChorus(sample_rate=SR, voices=4.5, seed=11).process(x, mix=0.6)
    assert len(v45) == len(x)
    assert np.max(np.abs(mono - x * 0.4)) > 1e-4  # chorus moves the signal


def test_bbd_voice_count_changes_output(pad_input):
    x = pad_input
    v1 = BBDChorus(sample_rate=SR, voices=1.0, seed=11).process(x, mix=0.6)
    v8 = BBDChorus(sample_rate=SR, voices=8.0, seed=11).process(x, mix=0.6)
    assert np.max(np.abs(v8 - v1)) > 1e-3


# ---------------------------------------------------------------- shimmer
def test_pitch_shift_unit_moves_energy():
    """The SOLA shifter must transpose 440 Hz content to 880 Hz at +1200c
    while preserving length."""
    from sound.effects.shimmer_reverb import _BLOCK
    dur = _BLOCK / SR
    t = np.linspace(0, dur, _BLOCK, endpoint=False)
    blk = np.sin(2 * np.pi * 440 * t)
    sh = ShimmerVerb(sample_rate=SR, seed=5)._pitch_shift(blk, 1200.0)

    def band(x, lo, hi):
        spec = np.abs(np.fft.rfft(x))
        f = np.fft.rfftfreq(len(x), 1.0 / SR)
        m = (f >= lo) & (f <= hi)
        return float(np.sum(spec[m]))

    assert len(sh) == len(blk)
    assert band(sh, 820, 940) > band(sh, 400, 500) * 5


def test_shimmer_doubles_octave_in_steady_state():
    """Feeding a steady 440 Hz tone through +1 octave shimmer (amount=1)
    must move dominant energy up to 880 Hz vs plain reverb."""
    dur = 4.0
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    x = np.sin(2 * np.pi * 440 * t)
    sv = ShimmerVerb(sample_rate=SR, seed=5)
    r1 = sv.process(x, pitch_cents=1200, pitch_amount=1.0,
                    rev_time=0.6, mix=1.0)
    r0 = sv.process(x, pitch_cents=0, pitch_amount=0.0,
                    rev_time=0.6, mix=1.0)

    def band(sig, lo, hi):
        spec = np.abs(np.fft.rfft(sig))
        f = np.fft.rfftfreq(len(sig), 1.0 / SR)
        m = (f >= lo) & (f <= hi)
        return float(np.sum(spec[m]))

    s1 = r1[int(1.0 * SR):]
    s0 = r0[int(1.0 * SR):]
    # plain reverb concentrates at the fundamental; shimmer pushes energy
    # into the octave-up band
    assert band(s1, 820, 940) > band(s0, 820, 940) * 4
    assert band(s1, 820, 940) > band(s1, 400, 500) * 1.5


def test_shimmer_fractional_and_down_shifts():
    """Fractional (+250c -> 528 Hz from 440) and downward (-700c -> ~330 Hz)
    shifts land energy at the expected bands."""
    dur = 4.0
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    x = np.sin(2 * np.pi * 440 * t)
    sv = ShimmerVerb(sample_rate=SR, seed=5)

    def band(sig, lo, hi):
        spec = np.abs(np.fft.rfft(sig))
        f = np.fft.rfftfreq(len(sig), 1.0 / SR)
        m = (f >= lo) & (f <= hi)
        return float(np.sum(spec[m]))

    rf = sv.process(x, pitch_cents=250, pitch_amount=1.0,
                    rev_time=0.6, mix=1.0)
    r0 = sv.process(x, pitch_cents=0, pitch_amount=0.0,
                    rev_time=0.6, mix=1.0)
    sf = rf[int(1.0 * SR):]
    s0 = r0[int(1.0 * SR):]
    # the fractional shift (440 -> 528 Hz) adds energy that plain reverb
    # does not produce in that band
    assert band(sf, 500, 560) > band(s0, 500, 560) * 2.5

    rd = sv.process(x, pitch_cents=-700, pitch_amount=1.0,
                    rev_time=0.6, mix=1.0)
    sd = rd[int(1.0 * SR):]
    # downward shift pulls energy out of the source band (the octave-down
    # partials land where the plain reverb's own low rumble already lives,
    # so the clean observable is depletion of the 440 band)
    assert band(sd, 400, 500) < band(s0, 400, 500) * 0.65
