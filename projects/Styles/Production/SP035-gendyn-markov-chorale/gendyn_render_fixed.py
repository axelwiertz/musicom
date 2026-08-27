#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SP-035 GENDYN Stochastic Breakpoint Synthesis — FIXED version (v2).

FIX (2026-08-24): the cron render redrew every breakpoint from scratch each
period with no phase continuity → broadband NOISE (autocorrelation pitch = 0 Hz
everywhere, harmonic content 4%). True Xenakis dynamic-stochastic GENDYN:

  1. Breakpoint TIME positions drawn ONCE per note (fixed grid in period)
  2. Breakpoint AMPLITUDES evolve via small Skorokhod-reflected random walk
     per period (dynamic stochastic evolution, not full redraw)
  3. First + last breakpoints forced to 0 → period-boundary phase continuity
     (no clicks, clear pitch)
  4. DC removal per period
  5. Per-voice params: n_bp small (6-12), walk sigma = sigma_a * 0.4
  6. ADSR + lowpass + normalize 0.89 peak (same as v1)

Source: 058-markov-chorale (Markov chorale, C major, 90 BPM, I-IV-V-I).
"""
import os
import json
import wave
import subprocess
import hashlib

import numpy as np
import mido
from mido import MidiFile

SR = 48000
BPM = 90
OUT_DIR = "/opt/data/projects/Styles/Production/SP035-gendyn-markov-chorale"
SRC_MIDI = "/opt/data/projects/Styles/Experimental/058-markov-chorale/MIDI/058-markov-chorale.mid"
NAME = "058-markov-chorale-gendyn-v2"
PEAK = 0.89

os.makedirs(os.path.join(OUT_DIR, "Audio"), exist_ok=True)

VOICE_PARAMS = {
    74: dict(role="Lead (Flute)",    n_bp=8,  sigma_a=0.20, gain=1.0),
    33: dict(role="Bass",            n_bp=6,  sigma_a=0.12, gain=1.4),
    49: dict(role="Harmony (Strings)", n_bp=10, sigma_a=0.25, gain=0.9),
}
DEFAULT_PARAMS = dict(role="Unknown", n_bp=8, sigma_a=0.20, gain=1.0)


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def gendyn_period(f0, t_bps, amps_prev, sigma_walk, rng):
    """One period: interpolate current amplitudes (random walk from previous).

    Args:
        f0: fundamental Hz
        t_bps: normalized breakpoint times in [0,1], sorted, 0 and 1 included
        amps_prev: previous period's amplitudes (same length)
        sigma_walk: per-period amplitude random-walk scale
    Returns:
        (waveform samples, new amplitudes)
    """
    period_samples = max(int(SR / f0), 8)
    n_bp = len(t_bps)

    # dynamic stochastic evolution: small random walk, Skorokhod-reflected
    amps = np.clip(amps_prev + rng.normal(0, sigma_walk, n_bp), -0.85, 0.85)
    # phase continuity: period boundaries anchored at zero
    amps[0] = 0.0
    amps[-1] = 0.0

    t_abs = t_bps * (period_samples - 1)
    x = np.arange(period_samples)
    y = np.interp(x, t_abs, amps)
    y = y - np.mean(y)  # DC removal per period
    return y, amps


def synth_note(midi_pitch, velocity, dur_sec, params, rng):
    f0 = midi_to_freq(midi_pitch)
    n_bp = params["n_bp"]
    sigma_a = params["sigma_a"]
    sigma_walk = sigma_a * 0.4

    n_samples = int(dur_sec * SR)
    if n_samples <= 0:
        return np.zeros(0, dtype=np.float32)
    n_periods = max(int(dur_sec * f0), 1)
    period_samples = max(int(SR / f0), 8)

    # FIX: breakpoint times drawn ONCE per note (stable grid), 0 and 1 anchored
    t_bps = np.sort(rng.uniform(0, 1, n_bp))
    t_bps[0] = 0.0
    t_bps[-1] = 1.0
    # initial amplitudes: moderate random shape
    amps = np.clip(rng.normal(0, sigma_a * 0.5, n_bp), -0.85, 0.85)
    amps[0] = 0.0
    amps[-1] = 0.0

    out = np.zeros(n_samples, dtype=np.float64)
    for p in range(n_periods):
        period, amps = gendyn_period(f0, t_bps, amps, sigma_walk, rng)
        start = p * period_samples
        end = min(start + period_samples, n_samples)
        if start >= n_samples:
            break
        out[start:end] = period[:end - start]

    # ADSR + crossfades
    vel = velocity / 127.0
    attack = min(int(0.010 * SR), n_samples // 2)
    release = min(int(0.080 * SR), n_samples // 2)
    env = np.ones(n_samples)
    if attack > 0:
        env[:attack] = np.linspace(0, 1, attack)
    if release > 0:
        env[-release:] = np.linspace(1, 0, release)
    out = out * env * vel * params["gain"]
    return out.astype(np.float32)


# ---------------------------------------------------------------- read midi
mid = MidiFile(SRC_MIDI)
tpb = mid.ticks_per_beat
tempo_us = 500000
for track in mid.tracks:
    for msg in track:
        if msg.type == "tempo":
            tempo_us = msg.tempo
            break
    else:
        continue
    break
sec_per_tick = tempo_us / 1e6 / tpb

events = []
for track in mid.tracks:
    program = 0
    abs_ticks = 0
    open_notes = {}
    for msg in track:
        abs_ticks += msg.time
        if msg.type == "program_change":
            program = msg.program
        elif msg.type == "note_on" and msg.velocity > 0:
            open_notes[(msg.channel, msg.note)] = (abs_ticks, msg.velocity, program)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            key = (msg.channel, msg.note)
            if key in open_notes:
                st, vel, p = open_notes.pop(key)
                events.append(dict(
                    start=st * sec_per_tick,
                    end=abs_ticks * sec_per_tick,
                    pitch=msg.note, vel=vel, program=p,
                ))
    for key, (st, vel, p) in open_notes.items():
        events.append(dict(
            start=st * sec_per_tick,
            end=(st + tpb) * sec_per_tick,
            pitch=key[1], vel=vel, program=p,
        ))

assert events, "no note events parsed"
total_dur = max(e["end"] for e in events) + 1.0
n_total = int(total_dur * SR)
mix = np.zeros(n_total, dtype=np.float64)
rng = np.random.default_rng(42)  # FIX: seeded for reproducibility

n_synth = 0
for e in events:
    params = VOICE_PARAMS.get(e["program"], DEFAULT_PARAMS)
    dur = e["end"] - e["start"]
    note = synth_note(e["pitch"], e["vel"], dur, params, rng)
    if len(note) == 0:
        continue
    start_s = int(e["start"] * SR)
    end_s = min(start_s + len(note), n_total)
    if start_s >= n_total:
        continue
    mix[start_s:end_s] += note[:end_s - start_s]
    n_synth += 1

print(f"parsed events: {len(events)}, synthesized notes: {n_synth}")
print(f"total duration: {total_dur:.2f}s")

# ---------------------------------------------------------------- post
try:
    from scipy.signal import butter, sosfilt
    sos = butter(4, 16000, fs=SR, output="sos")
    mix = sosfilt(sos, mix)
    print("lowpass: butter 4-pole 16 kHz applied")
except Exception as exc:
    print(f"lowpass skipped ({exc})")

peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * PEAK

# ---------------------------------------------------------------- verify
mono = mix
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
secs = int(total_dur)
rms_map = []
for s in range(secs):
    seg = mono[s * SR:(s + 1) * SR]
    rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    rms_map.append(round(rms, 5))
print(f"silence ratio: {silent*100:.1f}%")
print(f"per-second RMS: {rms_map}")

# pitch check: autocorrelation on 0.3s frames
def est_pitch(seg, sr):
    seg = seg - seg.mean()
    n = len(seg)
    ac = np.correlate(seg, seg, 'full')[n - 1:]
    ac /= (ac[0] + 1e-12)
    min_lag = int(0.002 * sr); max_lag = int(0.02 * sr)
    lag_range = ac[min_lag:max_lag]
    if len(lag_range) == 0:
        return 0
    peak_idx = np.argmax(lag_range) + min_lag
    if ac[peak_idx] < 0.5:
        return 0
    return sr / peak_idx

pitches = []
for t0 in np.arange(0.3, max(total_dur - 0.5, 0.5), 0.5):
    seg = mono[int(t0 * SR):int((t0 + 0.3) * SR)]
    p = est_pitch(seg, SR)
    if p > 0:
        pitches.append(p)
print(f"pitch frames detected: {len(pitches)}")
if pitches:
    print(f"  pitch range: {min(pitches):.0f}-{max(pitches):.0f} Hz, "
          f"median {np.median(pitches):.0f} Hz")

# ---------------------------------------------------------------- write wav
wav_path = os.path.join(OUT_DIR, "Audio", f"{NAME}.wav")
data16 = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open(wav_path, "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(data16.tobytes())
print(f"WAV: {wav_path} ({os.path.getsize(wav_path)} bytes)")

ogg_path = os.path.join(OUT_DIR, "Audio", f"{NAME}.ogg")
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
    "-codec:a", "libopus", "-b:a", "128k", ogg_path,
], check=True)
print(f"OGG: {ogg_path} ({os.path.getsize(ogg_path)} bytes)")

# ---------------------------------------------------------------- provenance
with open(SRC_MIDI, "rb") as f:
    data = f.read()
sha = hashlib.sha256(data).hexdigest()

prov = {
    "job": "SP-035 production pass FIXED (v2)",
    "source_midi": SRC_MIDI,
    "source_midi_sha256": sha,
    "production_method": "SP-035",
    "production_method_name": "GENDYN Stochastic Breakpoint Synthesis (dynamic-stochastic, fixed)",
    "fix": "v1 redrew breakpoints each period → noise (pitch detect 0 Hz, harmonic 4%). "
           "v2: fixed breakpoint times per note, amplitude random-walk per period "
           "(Skorokhod-reflected), zero-anchored boundaries (phase continuity).",
    "parameters": {
        "sample_rate": SR,
        "bpm": BPM,
        "seed": 42,
        "per_voice": {str(k): {kk: vv for kk, vv in v.items() if kk != "role"} for k, v in VOICE_PARAMS.items()},
        "sigma_walk_factor": 0.4,
        "amplitude_bounds": [-0.85, 0.85],
        "adsr": {"attack_s": 0.010, "release_s": 0.080},
        "lowpass_hz": 16000,
        "peak": PEAK,
    },
    "outputs": {
        "full_mix_wav": wav_path,
        "full_mix_ogg": ogg_path,
    },
    "verification": {
        "notes_parsed": len(events),
        "notes_synthesized": n_synth,
        "duration_sec": round(total_dur, 2),
        "silence_ratio": round(silent, 4),
        "rms_per_second": rms_map,
        "pitch_frames_detected": len(pitches),
    },
}
prov_path = os.path.join(OUT_DIR, "provenance_v2.json")
with open(prov_path, "w") as f:
    json.dump(prov, f, indent=2)
print(f"provenance: {prov_path}")
print("DONE")
