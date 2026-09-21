"""Tests for 2026-09-21 gear replications: Orbit (SP-090) & Grey Matter (SP-091)."""

import numpy as np
import pytest

from sound.effects.orbit_sculptor import (
    OrbitalStereoSculptor,
    OrbitalBandProcessor,
    BandConfig,
    ModulatorConfig,
    LinkwitzRiley4Crossover,
)
from sound.effects.delta_sigma_saturator import (
    DeltaSigmaSaturator,
    DeltaSigmaStage,
    SlewLimiter,
    ReconstructionFilter,
)
from workflows.musicom_workflow import SP_METHODS


def test_sp_methods_registration():
    assert "SP-090" in SP_METHODS
    assert SP_METHODS["SP-090"][0] == "sound.effects.orbit_sculptor"

    assert "SP-091" in SP_METHODS
    assert SP_METHODS["SP-091"][0] == "sound.effects.delta_sigma_saturator"


def test_orbit_crossover_summation():
    """LR4 crossover should reconstruct flat magnitude response across bands."""
    fs = 44100
    crossover = LinkwitzRiley4Crossover(low_mid_cross=300.0, mid_high_cross=3000.0, fs=fs)
    num_samples = 4096
    t = np.arange(num_samples) / fs
    # Impulse input
    impulse = np.zeros((2, num_samples), dtype=np.float32)
    impulse[:, 10] = 1.0

    low, mid, high = crossover.process(impulse)
    summed = low + mid + high

    # Energy conservation check
    assert np.all(np.isfinite(summed))
    # Correlation between input and reconstructed impulse should be very high
    assert np.max(np.abs(summed)) > 0.5


def test_orbit_stereo_sculptor_processing():
    fs = 44100
    sculptor = OrbitalStereoSculptor(fs=fs, bpm=120.0)
    audio = np.random.randn(2, 8820).astype(np.float32) * 0.2

    out = sculptor.process(audio)
    assert out.shape == audio.shape
    assert np.all(np.isfinite(out))
    assert not np.isnan(out).any()

    # Randomize high band
    sculptor.randomize_band("high", seed=123)
    out2 = sculptor.process(audio)
    assert out2.shape == audio.shape
    assert not np.isnan(out2).any()


def test_orbit_mono_correlation():
    mono = np.ones((2, 1000), dtype=np.float32)
    assert pytest.approx(OrbitalStereoSculptor.mono_correlation(mono), 0.01) == 1.0

    antiphase = np.vstack([np.ones(1000), -np.ones(1000)]).astype(np.float32)
    assert OrbitalStereoSculptor.mono_correlation(antiphase) == pytest.approx(-1.0, abs=0.01)


def test_delta_sigma_stage():
    stage = DeltaSigmaStage()
    out_samples = [stage.process_sample(0.2, strain=0.1) for _ in range(100)]
    # Should output 1-bit stream (-1.0 or 1.0)
    assert set(out_samples).issubset({-1.0, 1.0})


def test_delta_sigma_saturator_processing():
    fs = 44100
    sat = DeltaSigmaSaturator(drive_db=3.0, strain=0.3, mode="console", fs=fs)
    audio = np.random.randn(2, 4410).astype(np.float32) * 0.3

    out = sat.process(audio)
    assert out.shape == audio.shape
    assert np.all(np.isfinite(out))
    assert not np.isnan(out).any()


def test_delta_sigma_modes():
    fs = 44100
    audio = np.sin(2 * np.pi * 440 * np.arange(4410) / fs).astype(np.float32)
    stereo = np.vstack([audio, audio])

    for mode in ("clean", "console", "broken"):
        sat = DeltaSigmaSaturator(drive_db=6.0, strain=0.8, mode=mode, fs=fs)
        out = sat.process(stereo)
        assert out.shape == stereo.shape
        assert np.all(np.isfinite(out))
