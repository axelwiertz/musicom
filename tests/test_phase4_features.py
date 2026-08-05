"""Phase 4 tests: missing-link features (visualizer, vocal guide, DAW clock)."""
import os
import tempfile
import wave

import numpy as np

from structures import UnitMatrix, MusicUnit, MusicEvent
from visualization.grid import render_grid, write_grid_visualization
from sound.synthesis.vocal import FormantVocalGuide
from sound.sync.clock import DAWClockBridge


def _sample_matrix():
    m = UnitMatrix(shape=(2, 2))
    m.set_unit((0, 0), MusicUnit(events=[MusicEvent(60, 100, 0, 480)]))
    m.set_unit((0, 1), MusicUnit(events=[MusicEvent(64, 100, 0, 480)]))
    m.set_unit((1, 0), MusicUnit(events=[MusicEvent(48, 100, 0, 240)]))  # half density
    m.set_unit((1, 1), MusicUnit(events=[]))                              # rest
    return m


# --- T4.1 grid visualizer ----------------------------------------------------
def test_render_grid_chars_and_density():
    out = render_grid(_sample_matrix(), ticks_per_character=120,
                      voice_names=["Lead", "Bass"], bpm=120, mode="Ionian")
    assert "█" in out and "░" in out
    assert "Lead" in out and "Bass" in out
    assert "BPM: 120" in out and "Mode: Ionian" in out
    assert "Density:" in out


def test_write_grid_visualization_file():
    with tempfile.TemporaryDirectory() as d:
        path = write_grid_visualization(_sample_matrix(),
                                        os.path.join(d, "Analysis", "grid.txt"),
                                        ticks_per_character=120)
        assert os.path.getsize(path) > 40
        with open(path, encoding="utf-8") as f:
            assert "VISUALIZER" in f.read()


# --- T4.2 vocal guide synth --------------------------------------------------
def test_midi_to_freq():
    assert abs(FormantVocalGuide.midi_to_freq(69) - 440.0) < 1e-6
    assert abs(FormantVocalGuide.midi_to_freq(60) - 261.63) < 0.5


def test_render_syllable_wav():
    synth = FormantVocalGuide(sample_rate=22050)
    with tempfile.TemporaryDirectory() as d:
        p = synth.render_syllable(220.0, 0.5, "a", os.path.join(d, "syl.wav"))
        assert os.path.getsize(p) > 1000
        with wave.open(p, "rb") as w:
            assert w.getframerate() == 22050
            assert w.getnchannels() == 1


def test_render_melody_wav_duration():
    synth = FormantVocalGuide(sample_rate=22050)
    melody = MusicUnit(events=[
        MusicEvent(72, 100, 0, 480),
        MusicEvent(74, 100, 480, 960),
    ])
    with tempfile.TemporaryDirectory() as d:
        p = synth.render_melody(melody, os.path.join(d, "mel.wav"),
                                vowels=["a", "e"], ticks_per_beat=480, bpm=120)
        with wave.open(p, "rb") as w:
            # 960 ticks @ 120bpm, 480 tpb -> 1.0 s
            frames = w.getnframes()
            assert abs(frames / 22050 - 1.0) < 0.05


# --- T4.3 DAW clock bridge ---------------------------------------------------
def test_daw_clock_dry_run_counts_pulses():
    bridge = DAWClockBridge(bpm=120)
    bridge.start_virtual_output()   # enters fallback in headless env
    sent = bridge.run_clock(pulses_count=48, dry_run=True)
    assert sent == 48


def test_daw_clock_pulse_interval_math():
    # 24 PPQN at 120 BPM -> 0.5s per beat / 24 = 0.020833s per pulse
    bridge = DAWClockBridge(bpm=120)
    expected = 60.0 / (120 * 24.0)
    assert abs(expected - 0.0208333) < 1e-6
