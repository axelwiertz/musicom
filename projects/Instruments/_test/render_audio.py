# -*- coding: utf-8 -*-
"""Shared audio-render helper for instrument verify scripts.

Fixes the two bugs found in all test WAVs (2026-09-01):
1. Hardcoded TimGM6mb.sf2 (thin, buzzy patches) -> discover_soundfont()
   (prefers FluidR3_GM.sf2, the proper 141MB set).
2. 3-voice unison doubling (instrument + clarinet + piano on the SAME
   pitches = comb-filtering/beating = audible buzz).

Usage:
    from _test.render_audio import render_midi_solo
    wav = render_midi_solo(midi_path, out_wav)   # instrument solo
"""
import os
import subprocess
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")


def render_midi(midi_path, out_wav, gain="1.2", solo=None):
    """Render a MIDI to WAV with the preferred SoundFont.

    Args:
        midi_path: MIDI file to render
        out_wav: output WAV path
        gain: FluidSynth gain (default 1.2)
        solo: optional track index (0-based, excluding tempo track 0) to
              render ALONE. If None, renders the full MIDI.

    Returns the WAV path (raises on failure).
    """
    from sound.render.fluidsynth import discover_soundfont
    sf2 = discover_soundfont()
    if not sf2:
        raise FileNotFoundError(
            "no SoundFont — install FluidR3_GM.sf2 or TimGM6mb.sf2 "
            "(discover_soundfont())")
    fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
    midi_path = str(midi_path)
    out_wav = str(out_wav)

    # solo render: build a temp MIDI with only the tempo track + chosen track
    if solo is not None:
        import mido
        import tempfile
        m = mido.MidiFile(midi_path)
        keep = [m.tracks[0]]  # tempo track always
        # solo is 0-based voice index: voice 0 = m.tracks[1]
        keep.append(m.tracks[solo + 1])
        sub = mido.MidiFile()
        sub.ticks_per_beat = m.ticks_per_beat
        sub.tracks = keep
        fd, tmp_midi = tempfile.mkstemp(suffix=".mid")
        os.close(fd)
        sub.save(tmp_midi)
        midi_path = tmp_midi

    r = subprocess.run([fluidsynth, "-ni", "-g", gain, "-F", out_wav,
                        sf2, midi_path], capture_output=True)
    if solo is not None:
        os.unlink(midi_path)
    if r.returncode != 0:
        raise RuntimeError(f"fluidsynth failed: {r.stderr.decode()[-500:]}")
    if not os.path.exists(out_wav) or os.path.getsize(out_wav) < 1000:
        raise RuntimeError(f"render failed/empty: {out_wav}")
    return out_wav


def render_midi_solo(midi_path, out_wav, instrument_track=1, gain="1.2"):
    """Render ONLY the instrument track (track index 1 = first voice).

    This is the fix for the buzz: no clarinet/piano doubling on the same
    pitches. Use this for the audible instrument check.
    """
    return render_midi(midi_path, out_wav, gain=gain, solo=instrument_track)


def spectral_buzz_check(wav_path, lo_hz=4000, hi_hz=8000, max_frac=0.20):
    """Check a rendered WAV for audible high-frequency buzz.

    Compares the 4-8 kHz band (the audible 'buzz' region — comb-filtered
    unison, aliasing, reed squawk) against total energy. Ultrasonic noise
    above ~16 kHz is ignored (FluidSynth dither/floor, inaudible).

    Returns (ok, report_str).
    """
    import numpy as np
    import wave
    from numpy.fft import rfft
    w = wave.open(wav_path, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    seg = data[: int(0.5 * sr)]
    spec = np.abs(rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    buzz = spec[(freqs >= lo_hz) & (freqs < hi_hz)].sum()
    tot = spec[(freqs >= 50) & (freqs < 16000)].sum()  # audible band only
    frac = buzz / max(tot, 1e-9)
    report = (f"4-8kHz buzz energy = {frac * 100:.1f}% "
              f"({'OK' if frac <= max_frac else 'BUZZ — too bright'})")
    return frac <= max_frac, report
