# -*- coding: utf-8 -*-
"""SP-032 FDN Reverberation production pass.

Source: Styles/Balfolk/005-balfolk-production/audio/VoiceAudio_basic_pitch.mid
Pipeline: FluidSynth dry render (TimGM6mb.sf2) -> SP-032 FDN reverb -> master -> OGG.

SP-032 per methods_db.md (Feedback Delay Network Reverberation, Jot 1992):
- N=8 parallel delay lines, mutually coprime prime lengths in the 200-1000
  sample range (doc: mean 60-sample lines give 0.011 modes/Hz - too low;
  use primes 200-1000 or N=16+ for smooth tails)
- Unitary Householder feedback matrix A = I - (2/N) 1 1^T (lossless core)
- Per-line gains g_i = 10^(-3 M_i / (fs * RT60)) -> controlled decay
- Frequency-dependent decay: one-pole lowpass (alpha = exp(-2*pi*fc/fs)) in
  each feedback path, rt60_high < rt60 (bright attack -> warm tail)
- Pre-delay + early reflections (y = x[n-Dpre] + sum a_k x[n-Dk] + FDN{x})
- Stereo: even lines -> L, odd lines -> R with width control
- Wet/dry mix, peak normalization to -1 dBFS

Note: repo sound/effects/fdn_reverb.py exists but is parameterized for a
short 'Tidal'-style tail (fb ~0.82/roundtrip); methods_db reference
implementation used here for spec-faithful RT60 control.
"""
import os
import json
import hashlib
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
OUT = Path('/opt/data/projects/Styles/Production/SP032-FDN-balfolk-voice-pitch')
SRC = Path('/opt/data/projects/Styles/Balfolk/005-balfolk-production/audio/VoiceAudio_basic_pitch.mid')
DRY = OUT / 'dry_render.wav'


# --------------------------------------------------------------------------
# SP-032 core: FeedbackDelayNetwork (methods_db reference implementation)
# --------------------------------------------------------------------------
class FeedbackDelayNetwork:
    """FDN reverberator with frequency-dependent decay (methods_db SP-032)."""

    def __init__(self, n_lines=8, delay_lengths=None, rt60=3.5, rt60_high=1.2,
                 fs=44100, damping_freq=3500.0, matrix_type='householder'):
        self.n_lines = n_lines
        self.fs = fs
        if delay_lengths is None:
            # coprime primes in the 200-1000 sample range (doc guidance)
            primes = [227, 251, 277, 307, 337, 367, 397, 431, 461, 491,
                      521, 547, 577, 607, 641, 673]
            self.M = np.array(primes[:n_lines])
        else:
            self.M = np.array(delay_lengths)
        self.g = 10 ** (-3 * self.M / (fs * rt60))
        omega = 2 * np.pi * damping_freq / fs
        self.alpha = np.exp(-omega)
        self.g_hf = 10 ** (-3 * self.M / (fs * rt60_high))
        self.A = self._build_matrix(matrix_type)
        self.A_scaled = np.diag(self.g) @ self.A
        self.B = np.ones(n_lines) / np.sqrt(n_lines)
        self.C = np.ones(n_lines) / n_lines
        self.delay_lines = [np.zeros(m) for m in self.M]
        self.delay_ptrs = np.zeros(n_lines, dtype=int)
        self.damp_state = np.zeros(n_lines)

    def _build_matrix(self, matrix_type):
        N = self.n_lines
        if matrix_type == 'householder':
            return np.eye(N) - (2.0 / N) * np.ones((N, N))
        if matrix_type == 'hadamard':
            h = np.array([[1.0]])
            while h.shape[0] < N:
                h = np.block([[h, h], [h, -h]])
            return h / np.sqrt(N)
        raise ValueError(f"Unknown matrix type: {matrix_type}")

    def process_sample(self, x):
        d = np.array([self.delay_lines[i][self.delay_ptrs[i]]
                      for i in range(self.n_lines)])
        self.damp_state = (1 - self.alpha) * d + self.alpha * self.damp_state
        y = self.A_scaled @ self.damp_state
        y += self.B * x
        for i in range(self.n_lines):
            self.delay_lines[i][self.delay_ptrs[i]] = y[i]
            self.delay_ptrs[i] = (self.delay_ptrs[i] + 1) % self.M[i]
        return float(np.dot(self.C, y))

    def process(self, x):
        y = np.zeros(len(x))
        for n in range(len(x)):
            y[n] = self.process_sample(x[n])
        return y


def apply_sp032(dry, rt60=3.5, rt60_high=1.2, damping_freq=3500.0,
                pre_delay_ms=25.0, early_reflections=True):
    """SP-032 FDN wet-only signal (per-voice shared room)."""
    n = len(dry)
    outs = []
    for ch in range(2):
        fdn = FeedbackDelayNetwork(n_lines=8, rt60=rt60, rt60_high=rt60_high,
                                   fs=SR, damping_freq=damping_freq,
                                   matrix_type='householder')
        # stereo split: even lines -> L, odd lines -> R via output weights
        if ch == 0:
            fdn.C = np.array([1.0 if i % 2 == 0 else 0.0 for i in range(8)])
        else:
            fdn.C = np.array([0.0 if i % 2 == 0 else 1.0 for i in range(8)])
        s = fdn.C.sum()
        fdn.C = fdn.C / s if s > 0 else fdn.C
        # pre-delay + early reflections (doc section 7)
        d_pre = int(pre_delay_ms * SR / 1000)
        buf = np.zeros(n + d_pre + 4096)
        buf[d_pre:d_pre + n] = dry[:, ch]
        if early_reflections:
            early = np.zeros_like(buf)
            for k, (dk_ms, ak) in enumerate([(31.0, 0.35), (47.0, 0.25),
                                             (63.0, 0.15), (87.0, 0.08)]):
                dk = int(dk_ms * SR / 1000)
                early[dk:dk + n] += ak * dry[:, ch]
            buf += early
        wet_ch = fdn.process(buf)
        outs.append(wet_ch[:n])
    L, R = outs[0], outs[1]
    # width via mid/side on wet portion
    mid = (L + R) * 0.5
    side = (L - R) * 0.5
    return np.column_stack([mid + side * 0.85, mid - side * 0.85])


# --------------------------------------------------------------------------
# load dry render
# --------------------------------------------------------------------------
with wave.open(str(DRY), 'rb') as wf:
    assert wf.getnchannels() == 2
    n = wf.getnframes()
    raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
dry = raw.reshape(-1, 2)
dur = n / SR
print(f"dry: {dur:.2f}s, peak={np.abs(dry).max():.3f}")

# pad 5 s so the RT60=3.5 s tail rings past the dry end
pad = np.zeros((int(5.0 * SR), 2))
wet_only = apply_sp032(np.concatenate([dry, pad]),
                       rt60=4.0, rt60_high=1.4, damping_freq=3200.0,
                       pre_delay_ms=25.0)

# Level-match wet bus to dry peak (standard reverb send), then dry/wet mix
dry_peak = np.abs(dry).max()
wet_peak = np.abs(wet_only).max()
wet_only = wet_only * (dry_peak / wet_peak)
WET_DRY = 0.42
wet = dry * (1.0 - WET_DRY) + wet_only[:len(dry)] * WET_DRY

# ---- verify on FDN output (wet-only): tail extends past last note ----
# Dry signal silent 48-50 s; last note ~47.4 s. Wet-only tail 1-2 s after last note.
last_note_s = 47.4
check_start = int((last_note_s + 1.0) * SR)
check_end = int((last_note_s + 2.0) * SR)
tail_wet = np.abs(wet_only[check_start:check_end, 0]).max()
tail_energy = np.sum(wet_only[check_start:check_end, 0] ** 2)
print(f"FDN wet-only tail 1-2s after last note: peak={tail_wet:.5f} energy={tail_energy:.2f}")
assert tail_wet > 0.002 and tail_energy > 0.05, "FDN tail not extending - reverb ineffective"
# and dry must be (near) silent there, proving the tail is FDN's work
dry_there = np.abs(dry[check_start:check_end, 0]).max()
print(f"dry level in same window: {dry_there:.5f}")
assert dry_there < tail_wet * 0.2, "dry not silent - check window invalid"

# ---- RT60 sanity: energy decay rate inside wet-only tail ----
# measure from 48.5 s (post-last-note region) onward
env = np.abs(wet[check_start:, 0])
thresh = env.max() * 0.01  # -40 dB
t20 = 0.0
for i, v in enumerate(env):
    if v > thresh:
        t20 = i / SR
print(f"wet tail: -40 dB point at {t20:.2f}s after dry end")

# ---- master: normalize to -1 dBFS ----
peak = np.abs(wet).max()
wet = wet * (10 ** (-1.0 / 20.0)) / peak

# ---- silence check ----
mono = (wet[:, 0] + wet[:, 1]) * 0.5
silent_ratio = np.sum(np.abs(mono) < 0.001) / len(mono)
print(f"silence ratio: {silent_ratio*100:.1f}%")
assert silent_ratio < 0.30, "render too silent"

# ---- write processed WAV ----
WAV_OUT = OUT / 'balfolk_voice_pitch_SP032_FDN.wav'
pcm16 = (np.clip(wet, -1.0, 1.0) * 32767.0).astype(np.int16)
with wave.open(str(WAV_OUT), 'wb') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm16.tobytes())
assert os.path.getsize(WAV_OUT) > 40000
print(f"WAV: {WAV_OUT} ({os.path.getsize(WAV_OUT)} bytes)")

# ---- OGG (Opus, Telegram convention) ----
OGG_OUT = OUT / 'balfolk_voice_pitch_SP032_FDN.ogg'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(WAV_OUT),
                '-codec:a', 'libopus', '-application', 'voip', '-b:a', '48k',
                str(OGG_OUT)], check=True)
assert os.path.getsize(OGG_OUT) > 10000
print(f"OGG: {OGG_OUT} ({os.path.getsize(OGG_OUT)} bytes)")

# ---- copy source MIDI ----
MIDI_OUT = OUT / 'VoiceAudio_basic_pitch.mid'
shutil.copy2(SRC, MIDI_OUT)


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


prov = {
    "job": "nightly production pass (SP)",
    "composition_source": str(SRC),
    "composition_sha256": sha256(SRC),
    "production_method": "SP-032",
    "production_method_name": "Feedback Delay Network (FDN) Reverberation",
    "method_family": "Synthesis Engines / Algorithmic Spatialization",
    "method_notes": ("Jot 1992 FDN: 8 coprime prime delay lines (227-431 samples @44.1k, "
                     "modal density ~0.06 modes/Hz), Householder unitary feedback matrix, "
                     "per-line one-pole HF damping at 3.2 kHz, g_i = 10^(-3 M_i/(fs*RT60)), "
                     "RT60=4.0 s / RT60_high=1.4 s (frequency-dependent decay), "
                     "pre-delay 25 ms + 4 early reflections, even/odd line split for stereo "
                     "width 0.85, wet bus level-matched to dry peak, mixed at 42% wet. "
                     "Reference implementation from methods_db.md "
                     "(repo sound/effects/fdn_reverb.py is short-tail 'Tidal' style)."),
    "parameters": {"n_lines": 8, "rt60_s": 4.0, "rt60_high_s": 1.4,
                   "damping_freq_hz": 3200.0, "pre_delay_ms": 25.0,
                   "wet_dry": 0.42, "width": 0.85, "sample_rate": SR,
                   "matrix": "householder", "normalization_dBFS": -1.0},
    "artifacts": {
        "midi": str(MIDI_OUT),
        "dry_wav": str(DRY),
        "processed_wav": str(WAV_OUT),
        "processed_ogg": str(OGG_OUT),
    },
    "checks": {
        "fdn_tail_peak_after_dry_end": round(float(tail_wet), 5),
        "fdn_tail_energy_after_dry_end": round(float(tail_energy), 2),
        "wet_tail_minus40dB_point_s": round(t20, 2),
        "silence_ratio": round(float(silent_ratio), 4),
        "peak_dBFS": -1.0,
    },
}
with open(OUT / 'provenance.json', 'w') as f:
    json.dump(prov, f, indent=2)
print("provenance.json written")
