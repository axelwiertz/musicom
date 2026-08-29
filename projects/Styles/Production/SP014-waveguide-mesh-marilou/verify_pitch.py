#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Supplementary verification for SP-014 marilou: is the render tonal or noise?

SP-035 lesson says harmonic energy in first 8 harmonics of the LOWEST
fundamental >= 30% = tonal, single digits = noise. The whole-mix number here
is diluted by (a) broadband GM drums in the mix and (b) the mesh being a MODAL
resonator (steel-pan/marimba-like, deliberately inharmonic modal spectrum).

Checks:
1. mix harmonic energy (D2=73.42 Hz, first 8 harmonics) — same as before
2. bass STEM only: same metric (no drums, low register)
3. per-voice stems: dominant-peak note match + harmonic concentration around
   the voice's OWN expected fundamentals (energy in +/-2% band of f0..8f0)
4. autocorrelation pitch frames (SP-035 noise detector: 0 Hz frames = noise)
"""
import json
import sys
from pathlib import Path

import numpy as np

SR = 44100
OUT = Path('/opt/data/projects/Styles/Production/SP014-waveguide-mesh-marilou')


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def read_wav_mono(path):
    import wave
    with wave.open(str(path), 'r') as wf:
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr_w = wf.getframerate()
        frames = wf.readframes(wf.getnframes())
    data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    if nch == 2:
        data = data.reshape(-1, 2).mean(axis=1)
    return data, sr_w


def harm_energy(mono, fund, n_harm=8):
    n = len(mono)
    spec = np.abs(np.fft.rfft(mono * np.hanning(n)))
    f = np.fft.rfftfreq(n, 1.0 / SR)
    total = float(np.sum(spec ** 2))
    hsum = 0.0
    for h in range(1, n_harm + 1):
        f0 = fund * h
        idx = int(np.argmin(np.abs(f - f0)))
        hsum += float(spec[idx] ** 2)
    return hsum / total if total > 0 else 0.0


def autocorr_pitch_frames(mono, hop=0.5):
    """SP-035-style autocorrelation pitch detection per 0.5s frame."""
    win = int(0.5 * SR)
    frames_ok = 0
    frames_total = 0
    freqs = []
    for start in range(0, len(mono) - win + 1, win):
        seg = mono[start:start + win]
        frames_total += 1
        if np.max(np.abs(seg)) < 1e-4:
            continue
        ac = np.correlate(seg, seg, mode='full')[win - 1:]
        ac = ac / (ac[0] + 1e-12)
        # search lag range for f0 in 50..1000 Hz
        lo = int(SR / 1000.0)
        hi = int(SR / 50.0)
        if hi >= len(ac):
            hi = len(ac) - 1
        if hi <= lo:
            continue
        lag = lo + int(np.argmax(ac[lo:hi]))
        # require meaningful periodicity (normalized autocorr at lag > 0.3)
        if ac[lag] > 0.3:
            frames_ok += 1
            freqs.append(SR / lag)
        # else: 0 Hz frame (noise)
    return frames_ok, frames_total, freqs


def note_band_concentration(mono, notes):
    """Energy in +/-2% bands around each note's f0..8f0 / total energy."""
    n = len(mono)
    spec = np.abs(np.fft.rfft(mono * np.hanning(n))) ** 2
    f = np.fft.rfftfreq(n, 1.0 / SR)
    total = float(np.sum(spec))
    band = 0.0
    for nn in notes:
        f0 = midi_to_freq(nn)
        for h in range(1, 9):
            fc = f0 * h
            if fc > 20000:
                break
            m = (np.abs(f - fc) / fc) < 0.02
            band += float(np.sum(spec[m]))
    return band / total if total > 0 else 0.0


results = {}

# voice -> expected notes (from inspection)
VOICE_NOTES = {
    'FiddleLead.wav': [72, 74, 76, 77, 79, 81],
    'PedalSteel.wav': [64, 65, 67, 69, 71, 72],
    'LeadFlute.wav': [64, 66, 67, 69, 71, 72, 74],
    'AcGuitar.wav': [53, 55, 57],
    'BassBody.wav': [38, 40, 43, 45],
}

mix_path = OUT / 'Audio' / 'SP014-waveguide-mesh-marilou.wav'
mono_mix, _ = read_wav_mono(mix_path)
results['mix_harm_energy_D2_8h'] = round(harm_energy(mono_mix, 73.42), 4)
ok, tot, fr = autocorr_pitch_frames(mono_mix)
results['mix_autocorr_frames'] = f'{ok}/{tot}'
results['mix_autocorr_freqs'] = [round(x, 1) for x in fr[:10]]

# bass stem
bass, _ = read_wav_mono(OUT / 'Audio' / 'stems' / 'BassBody.wav')
results['bass_harm_energy_D2_8h'] = round(harm_energy(bass, 73.42), 4)
okb, totb, frb = autocorr_pitch_frames(bass)
results['bass_autocorr_frames'] = f'{okb}/{totb}'
results['bass_autocorr_freqs'] = [round(x, 1) for x in frb[:10]]

# per-voice concentration
for name, notes in VOICE_NOTES.items():
    mono, _ = read_wav_mono(OUT / 'Audio' / 'stems' / name)
    results[f'{name}_note_band_conc'] = round(note_band_concentration(mono, notes), 4)

print(json.dumps(results, indent=2))
(OUT / 'Analysis' / 'pitch_verification.json').write_text(
    json.dumps(results, indent=2), encoding='utf-8')
print('wrote Analysis/pitch_verification.json')
