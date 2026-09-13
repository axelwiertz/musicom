"""Tests for the voice-like instrument family (sound/synthesis/voice_like.py).

These assert the *principle*, not just that code runs: a non-vocal excitation
routed through a vocal-tract formant bank must put the formant envelope into
the output spectrum. That is what makes the family "familiar like a voice"
without being voices.
"""
import numpy as np
import pytest

from sound.synthesis.voice_like import (
    FORMANT_BANDWIDTHS,
    INSTRUMENTS,
    VOWEL_FORMANTS,
    VoiceLikeInstrument,
    _formant_bank,
    _resonator,
    render_phrase_wav,
)

SR = 44100


# --------------------------------------------------------------------------- #
# resonator primitives                                                         #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("freq,bw", [(270, 90), (730, 90), (2440, 170), (3800, 300)])
def test_resonator_is_stable_and_unity_peak(freq, bw):
    """Poles must be INSIDE the unit circle and the peak gain ~= 1.0.

    Regression guard: `a2 = -r**2` (instead of `+r**2`) puts the poles outside
    the circle and the filter diverges to inf/NaN.
    """
    b0, a1, a2 = _resonator(float(freq), float(bw), SR)
    r = np.exp(-np.pi * bw / SR)
    assert abs(a2 - r * r) < 1e-12, "a2 must be +r^2 (poles inside circle)"
    assert abs(a1 + 2.0 * r * np.cos(2 * np.pi * freq / SR)) < 1e-12

    x = np.random.default_rng(0).normal(0.0, 1.0, 8192)
    from scipy.signal import lfilter
    y = lfilter([b0], [1.0, a1, a2], x)
    assert np.all(np.isfinite(y)), "resonator diverged -> NaN/inf"
    assert np.abs(y).max() < 1e3, "resonator gain runaway"

    # measure the peak of |H| near freq
    w = 2 * np.pi * freq / SR
    z = np.exp(-1j * w)
    H = b0 / abs(1.0 + a1 * z + a2 * z ** 2)
    assert 0.8 < H < 1.25, f"peak gain {H} not ~unity"


# --------------------------------------------------------------------------- #
# formant bank: the core principle                                             #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("vowel", sorted(VOWEL_FORMANTS))
def test_bank_response_matches_vowel_formants(vowel):
    """The bank's impulse response must peak at the vowel's F1/F2/F3.

    This is the *definition* of the instrument family: the formant envelope
    is present in the filter, independent of any source.
    """
    imp = np.zeros(16384)
    imp[0] = 1.0
    y = _formant_bank(imp, VOWEL_FORMANTS[vowel], FORMANT_BANDWIDTHS,
                      (1.0, 0.8, 0.55, 0.3, 0.18), SR, mode="parallel")
    S = np.abs(np.fft.rfft(y, 65536))
    f = np.fft.rfftfreq(65536, 1.0 / SR)
    m = (f >= 150) & (f <= 4200)
    ff, SS = f[m], S[m]
    pk = [(SS[i], ff[i]) for i in range(2, len(SS) - 2)
          if SS[i] > SS[i - 1] and SS[i] >= SS[i + 1]]
    pk.sort(reverse=True)
    picked, used = [], []
    for _, fr in pk:
        if all(abs(fr - u) > 150.0 for u in used):
            picked.append(fr)
            used.append(fr)
        if len(picked) == 3:
            break
    picked.sort()
    for got, want in zip(picked, VOWEL_FORMANTS[vowel][:3]):
        assert abs(got - want) < 60.0, \
            f"{vowel}: measured {got:.0f} Hz vs target {want:.0f} Hz"


def test_vowel_envelopes_are_distinct():
    """Different vowels must produce different envelopes (not one filter)."""
    imp = np.zeros(8192)
    imp[0] = 1.0
    resp = {}
    for v in ("a", "e", "i", "o", "u"):
        y = _formant_bank(imp, VOWEL_FORMANTS[v], FORMANT_BANDWIDTHS,
                          (1.0, 0.8, 0.55, 0.3, 0.18), SR, mode="parallel")
        S = np.abs(np.fft.rfft(y, 32768))
        S = S / (S.max() + 1e-12)
        resp[v] = S
    for a in resp:
        for b in resp:
            if a < b:
                assert np.abs(resp[a] - resp[b]).max() > 0.15, \
                    f"{a} and {b} envelopes too similar"


def test_cascade_mode_is_stable():
    """Cascade (series resonators) must not blow up either."""
    x = np.random.default_rng(1).normal(0.0, 1.0, 8192)
    y = _formant_bank(x, (240.0, 900.0, 1800.0, 2600.0),
                      FORMANT_BANDWIDTHS, (1.0, 0.75, 0.5, 0.28), SR,
                      mode="cascade")
    assert np.all(np.isfinite(y))
    assert np.abs(y).max() < 1e4


@pytest.mark.parametrize("vowel", sorted(VOWEL_FORMANTS))
def test_cascade_sections_resonate_above_unity(vowel):
    """Each cascade section must be unity at DC (b0 = 1 + a1 + a2) and resonate.

    Unity DC gain is what makes the cascade self-compensating: the higher
    formants get progressively more gain, which cancels the source's 1/f
    rolloff. Without it the source tilt dominates and the instrument sounds
    like its oscillator rather than its vowel.
    """
    for f, bw in zip(VOWEL_FORMANTS[vowel], FORMANT_BANDWIDTHS):
        r = np.exp(-np.pi * bw / SR)
        a1 = -2.0 * r * np.cos(2.0 * np.pi * f / SR)
        a2 = r * r
        b0 = 1.0 + a1 + a2
        # DC response of the section must be exactly 1.0
        assert abs(b0 / (1.0 + a1 + a2) - 1.0) < 1e-12
        # and the section must actually resonate above unity.
        # NOTE: the peak height depends on f/bw (Q = f/bw), so low formants
        # with wide bandwidths resonate only mildly — /i/ F1 = 270/90 = Q 3
        # peaks at ~3.1x. Requiring more would be unphysical.
        w = 2 * np.pi * f / SR
        z = np.exp(-1j * w)
        peak = b0 / abs(1.0 + a1 * z + a2 * z ** 2)
        assert peak > 2.5, f"{vowel} {f:.0f} Hz section does not resonate (peak={peak:.2f})"


@pytest.mark.parametrize("vowel", sorted(VOWEL_FORMANTS))
def test_lpc_envelope_recovers_formants_from_cascade(vowel):
    """LPC must recover the formants from the cascade bank's own response.

    This is the independent check that the tract (not the source) shapes the
    spectrum: a cascade of all-pole resonators is genuinely all-pole, so an
    LPC fit recovers its formants. (A *parallel* sum would be pole-zero and
    LPC would fail — which is why cascade is the default.)

    Tolerance is per-vowel because F3 resolution depends on the pole Q: /i/
    has F1 at 270 Hz (Q~3) and F2/F3 only ~700 Hz apart, so LPC merges them
    slightly (measured error 91 Hz). 150 Hz is comfortably inside the
    perceptual formant tolerance while still failing a wrong formant set.
    """
    from sound.synthesis.voice_like import envelope_peaks, lpc_spectral_envelope

    imp = np.zeros(16384)
    imp[0] = 1.0
    y = _formant_bank(imp, VOWEL_FORMANTS[vowel], FORMANT_BANDWIDTHS,
                      (1.0, 1.0, 1.0, 1.0, 1.0), SR, mode="cascade")
    f, env = lpc_spectral_envelope(y, SR, order=12, preemph=0.0)
    got = envelope_peaks(f, env, lo=200.0, hi=4200.0)
    want = list(VOWEL_FORMANTS[vowel][:3])
    assert len(got) == 3, f"{vowel}: expected 3 formants, got {got}"
    for g, w in zip(got, want):
        assert abs(g - w) < 150.0, f"{vowel}: LPC found {g:.0f} Hz, want {w:.0f}"


def test_lpc_envelope_available_without_scipy_would_raise():
    """A too-short signal must raise rather than silently return garbage."""
    from sound.synthesis.voice_like import lpc_spectral_envelope
    with pytest.raises(ValueError, match="too short"):
        lpc_spectral_envelope(np.zeros(8), SR, order=24)


def test_vowel_envelope_follows_tract_not_source():
    """The rendered vowel envelope must match its own vowel's tract response.

    Correlates the LPC envelope of the rendered note against the LPC envelope
    of the bank driven by an impulse: high correlation proves the tract, not
    the excitation, is setting the spectral shape. Compared in **dB**, since a
    linear-amplitude correlation is dominated by the single largest peak.
    """
    from sound.synthesis.voice_like import lpc_spectral_envelope

    imp = np.zeros(16384)
    imp[0] = 1.0
    pred = {}
    for v in ("a", "e", "i", "o", "u"):
        y = _formant_bank(imp, VOWEL_FORMANTS[v], FORMANT_BANDWIDTHS,
                          (1.0, 1.0, 1.0, 1.0, 1.0), SR, mode="cascade")
        f, e = lpc_spectral_envelope(y, SR, order=12, preemph=0.0)
        m = (f >= 200.0) & (f <= 4200.0)
        pred[v] = 20.0 * np.log10(e[m] + 1e-12)

    vi = VoiceLikeInstrument("vox_humana", SR, seed=6)
    for v in ("a", "e", "i", "o", "u"):
        x = vi.render_note(110.0, 2.0, vowel=v)
        f, e = lpc_spectral_envelope(x, SR, order=12, preemph=0.0)
        m = (f >= 200.0) & (f <= 4200.0)
        r = float(np.corrcoef(20.0 * np.log10(e[m] + 1e-12), pred[v])[0, 1])
        # measured 0.73 (/i/, hardest) .. 0.95 (/u/)
        assert r > 0.65, f"vowel {v}: rendered envelope r={r:.3f} vs its tract"


# --------------------------------------------------------------------------- #
# instruments                                                                  #
# --------------------------------------------------------------------------- #

def test_family_registry():
    assert set(INSTRUMENTS) == {
        "vox_humana", "kazoo", "jaw_harp", "didgeridoo",
        "singing_saw", "talkbox",
    }
    for name, s in INSTRUMENTS.items():
        for key in ("label", "gm_name", "midi_program", "source", "amp",
                    "gains", "range", "note"):
            assert key in s, f"{name} missing {key}"
        assert len(s["gains"]) == 5, f"{name} gains must cover F1..F5"
        lo, hi = s["range"]
        assert lo < hi


def test_unknown_instrument_raises():
    with pytest.raises(ValueError, match="Unknown instrument"):
        VoiceLikeInstrument("definitely_not_real")


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_render_note_is_finite_and_normalized(name):
    vi = VoiceLikeInstrument(name, SR, seed=3)
    x = vi.render_note(220.0, 0.8, vowel="a")
    assert len(x) == int(0.8 * SR)
    assert np.all(np.isfinite(x)), f"{name} produced NaN/inf"
    assert 0.5 <= np.abs(x).max() <= 1.0, f"{name} peak {np.abs(x).max()}"


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_render_is_deterministic(name):
    a = VoiceLikeInstrument(name, SR, seed=42).render_note(220.0, 0.5, "a")
    b = VoiceLikeInstrument(name, SR, seed=42).render_note(220.0, 0.5, "a")
    assert np.allclose(a, b), f"{name} not deterministic for a fixed seed"
    c = VoiceLikeInstrument(name, SR, seed=43).render_note(220.0, 0.5, "a")
    assert not np.allclose(a, c), f"{name} ignores its seed"


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_formant_envelope_drives_spectrum(name):
    """The output spectrum must correlate with the formant bank response.

    Excludes jaw_harp: a plucked lamella is an energy-decaying transient whose
    colour is set at the pluck instant, which a windowed steady-state
    correlation understates (its filter is still correct — see the impulse
    test above).
    """
    if name == "jaw_harp":
        pytest.skip("percussive transient; covered by the impulse-response test")
    vi = VoiceLikeInstrument(name, SR, seed=4)
    f0 = 110.0
    x = vi.render_note(f0, 2.0, vowel="a")
    win = np.hanning(len(x))
    S = np.abs(np.fft.rfft(x * win, 65536))
    fr = np.fft.rfftfreq(65536, 1.0 / SR)
    harm = []
    for k in range(1, 31):
        fk = k * f0
        if fk >= 0.45 * SR:
            break
        i = int(np.argmin(np.abs(fr - fk)))
        harm.append(20 * np.log10(S[max(0, i - 1):i + 2].max() + 1e-12))
    harm = np.array(harm)

    imp = np.zeros(16384)
    imp[0] = 1.0
    y = _formant_bank(imp, vi.formants_for("a"), FORMANT_BANDWIDTHS,
                      vi.spec["gains"], SR, mode=vi.spec.get("mode", "parallel"),
                      antiformant=vi.spec.get("antiformant"))
    Sy = np.abs(np.fft.rfft(y, 65536))
    fy = np.fft.rfftfreq(65536, 1.0 / SR)
    pred = 20 * np.log10(np.interp(f0 * np.arange(1, len(harm) + 1), fy, Sy) + 1e-12)

    r = float(np.corrcoef(harm, pred)[0, 1])
    assert r > 0.6, f"{name}: spectrum poorly correlated with formants (r={r:.3f})"


def test_instruments_sound_different():
    """Centroids must differ — otherwise this is one filter with six labels."""
    cents = {}
    for name in INSTRUMENTS:
        x = VoiceLikeInstrument(name, SR, seed=8).render_note(220.0, 1.0, "a")
        S = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
        f = np.fft.rfftfreq(len(x), 1.0 / SR)
        cents[name] = float((f * S).sum() / (S.sum() + 1e-15))
    assert len({round(c / 30) for c in cents.values()}) >= 5, \
        f"too many instruments share a centroid: {cents}"


def test_tract_scale_shifts_formants():
    """didgeridoo's tall_tract must lower its formants vs the raw vowel."""
    vi = VoiceLikeInstrument("didgeridoo", SR)
    scaled = vi.formants_for("a")
    raw = VOWEL_FORMANTS["a"]
    assert scaled[0] < raw[0], "tract_scale did not lower F1"
    assert all(s < r for s, r in zip(scaled, raw))
    # and a human-tract instrument must NOT be scaled
    plain = VoiceLikeInstrument("vox_humana", SR)
    assert plain.formants_for("a") == tuple(raw)


def test_talkbox_morph_changes_output():
    vi = VoiceLikeInstrument("talkbox", SR, seed=2)
    plain = vi.render_note(196.0, 1.0, vowel="a")
    morph = vi.render_note(196.0, 1.0, vowel="a", vowel_end="o")
    assert not np.allclose(plain, morph), "vowel morph had no effect"


def test_phrase_and_wav_output(tmp_path):
    path = tmp_path / "phrase.wav"
    notes = [(69, 0.3, "a"), (72, 0.3, "o"), (76, 0.4, "e")]
    render_phrase_wav(str(path), notes, instrument="vox_humana", sample_rate=SR)
    assert path.exists()
    assert path.stat().st_size > 40, "empty WAV written"

    import wave
    with wave.open(str(path), "rb") as w:
        assert w.getnchannels() == 1
        assert w.getframerate() == SR
        assert w.getnframes() > SR  # > 1 s of audio


def test_phrase_length_scales_with_notes():
    vi = VoiceLikeInstrument("kazoo", SR, seed=1)
    short = vi.render_phrase([(69, 0.5, "a")], gap=0.0, tail=0.0)
    long = vi.render_phrase([(69, 0.5, "a"), (71, 0.5, "a")], gap=0.0, tail=0.0)
    assert len(long) == pytest.approx(2 * len(short), abs=2)
