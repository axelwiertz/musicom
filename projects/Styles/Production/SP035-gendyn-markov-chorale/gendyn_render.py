#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SP-035 GENDYN Stochastic Breakpoint Synthesis — production pass
Source: 058-markov-chorale (Markov chain chorale, C major, 90 BPM, I-IV-V-I)
Method: Xenakis GENDYN — stochastic time-amplitude breakpoints per period,
        linearly interpolated, fresh random draw every period.

Follows methods_db.md SP-035 spec:
  - per-voice (f0, N, sigma_a, sigma_t) parameter sets
  - dynamic stochastic variation (random walk on sigma_a)
  - DC removal per period
  - ADSR + short crossfades to avoid clicks
  - lowpass to tame aliasing, normalize to 0.89 peak
"""
import os
import json
import wave
import subprocess
import hashlib

import numpy as np
import mido
from mido import MidiFile

# ---------------------------------------------------------------- config
SR = 48000
BPM = 90
OUT_DIR = "/opt/data/projects/Styles/Production/SP035-gendyn-markov-chorale"
SRC_MIDI = "/opt/data/projects/Styles/Experimental/058-markov-chorale/MIDI/058-markov-chorale.mid"
NAME = "058-markov-chorale-gendyn"
PEAK = 0.89

os.makedirs(os.path.join(OUT_DIR, "Audio"), exist_ok=True)

# per-voice GENDYN parameter sets (methods_db SP-035 section 7)
# keyed by MIDI program number
VOICE_PARAMS = {
    74: dict(role="Lead (Flute)",    n_bp=12, sigma_a=0.25, sigma_t=0.08,
             amp_dist="gaussian", time_dist="uniform",  gain=1.0),
    33: dict(role="Bass",            n_bp=6,  sigma_a=0.10, sigma_t=0.06,
             amp_dist="gaussian", time_dist="uniform",  gain=1.4),
    49: dict(role="Harmony (Strings)", n_bp=15, sigma_a=0.30, sigma_t=0.10,
             amp_dist="gaussian", time_dist="uniform",  gain=0.9),
}
DEFAULT_PARAMS = dict(role="Unknown", n_bp=12, sigma_a=0.25, sigma_t=0.08,
                      amp_dist="gaussian", time_dist="uniform", gain=1.0)


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def gendyn_period(f0, n_bp, sigma_a, sigma_t, amp_dist, time_dist, rng):
    """One period of GENDYN breakpoints -> waveform (DC removed)."""
    period_samples = int(SR / f0)
    period_samples = max(period_samples, 8)
    mean_dt = period_samples / n_bp

    # time intervals
    if time_dist == "uniform":
        dt = rng.uniform(mean_dt * (1 - sigma_t), mean_dt * (1 + sigma_t), n_bp)
    elif time_dist == "gaussian":
        dt = rng.normal(mean_dt, sigma_t * mean_dt, n_bp)
        dt = np.clip(dt, 1, None)
    else:  # exponential
        dt = rng.exponential(mean_dt, n_bp)

    dt = dt / dt.sum() * period_samples
    t = np.cumsum(dt)
    t = np.insert(t, 0, 0)[:n_bp]

    # amplitudes
    if amp_dist == "uniform":
        a = rng.uniform(-sigma_a, sigma_a, n_bp)
    elif amp_dist == "beta":
        a = 2 * rng.beta(2, 2, n_bp) - 1
    else:  # gaussian
        a = np.clip(rng.normal(0, sigma_a, n_bp), -1, 1)

    # ensure strictly increasing integer times
    t_int = np.clip(np.round(t).astype(int), 0, period_samples - 1)
    t_int = np.unique(t_int)
    if len(t_int) < 2:
        t_int = np.array([0, period_samples - 1])
    a = a[:len(t_int)]

    x = np.arange(period_samples)
    y = np.interp(x, t_int, a)
    y = y - np.mean(y)  # DC removal per period
    return y


def synth_note(midi_pitch, velocity, dur_sec, params, rng, f0_override=None):
    """Synthesize one note with GENDYN + ADSR + dynamic sigma_a walk."""
    f0 = midi_to_freq(midi_pitch) if f0_override is None else f0_override
    n_bp = params["n_bp"]
    sigma_a0 = params["sigma_a"]
    sigma_t = params["sigma_t"]
    amp_dist = params["amp_dist"]
    time_dist = params["time_dist"]

    n_samples = int(dur_sec * SR)
    if n_samples <= 0:
        return np.zeros(0, dtype=np.float32)
    n_periods = max(int(dur_sec * f0), 1)
    period_samples = max(int(SR / f0), 8)

    # dynamic stochastic variation: random walk on sigma_a (Skorokhod-reflected)
    walk = rng.normal(0, 0.01, n_periods)
    sig_a = np.clip(np.cumsum(walk) + sigma_a0, 0.05, 0.9)

    out = np.zeros(n_samples, dtype=np.float64)
    for p in range(n_periods):
        period = gendyn_period(f0, n_bp, sig_a[p], sigma_t, amp_dist, time_dist, rng)
        start = p * period_samples
        end = min(start + period_samples, n_samples)
        if start >= n_samples:
            break
        out[start:end] = period[:end - start]

    # ADSR + crossfades (short attack, longer release; no clicks)
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
tempo_us = 500000  # default 120 BPM
for track in mid.tracks:
    for msg in track:
        if msg.type == "tempo":
            tempo_us = msg.tempo
            break
    else:
        continue
    break
sec_per_tick = tempo_us / 1e6 / tpb

# collect note events: (abs_start_sec, abs_end_sec, pitch, velocity, program)
notes = []
for track in mid.tracks:
    program = 0
    abs_ticks = 0
    for msg in track:
        abs_ticks += msg.time
        if msg.type == "program_change":
            program = msg.program
        elif msg.type == "note_on" and msg.velocity > 0:
            dur = 0
            # find matching note_off / note_on vel 0 in same track
            notes.append(dict(
                start=abs_ticks * sec_per_tick,
                pitch=msg.note, vel=msg.velocity, program=program,
                track=track.name,
            ))
# compute durations by pairing note_on with subsequent note_off per (track, channel, pitch)
events = []
all_open_notes = []  # collect unclosed notes across all tracks
for track in mid.tracks:
    program = 0
    abs_ticks = 0
    open_notes = {}  # (channel, pitch) -> start_tick
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
    # any unclosed notes in this track: give them 1 beat
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
rng = np.random.default_rng()

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
print(f"total duration: {total_dur:.2f}s, buffer: {n_total} samples")

# ---------------------------------------------------------------- post
# gentle lowpass to tame aliasing (spec pitfall 1)
try:
    from scipy.signal import butter, sosfilt
    sos = butter(4, 16000, fs=SR, output="sos")
    mix = sosfilt(sos, mix)
    print("lowpass: butter 4-pole 16 kHz applied")
except Exception as exc:
    print(f"lowpass skipped ({exc})")

# normalize to PEAK
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * PEAK

# silence verification (skill: measure silence ratio + per-second RMS)
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

# ---------------------------------------------------------------- write wav
wav_path = os.path.join(OUT_DIR, "Audio", f"{NAME}.wav")
data16 = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open(wav_path, "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(data16.tobytes())
print(f"WAV: {wav_path} ({os.path.getsize(wav_path)} bytes)")

# ---------------------------------------------------------------- ogg
ogg_path = os.path.join(OUT_DIR, "Audio", f"{NAME}.ogg")
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
    "-codec:a", "libopus", "-b:a", "128k", ogg_path,
], check=True)
print(f"OGG: {ogg_path} ({os.path.getsize(ogg_path)} bytes)")

# ---------------------------------------------------------------- copy midi
midi_copy = os.path.join(OUT_DIR, f"058-markov-chorale.mid")
with open(SRC_MIDI, "rb") as f:
    data = f.read()
with open(midi_copy, "wb") as f:
    f.write(data)
sha = hashlib.sha256(data).hexdigest()

# ---------------------------------------------------------------- provenance
prov = {
    "job": "SP-035 production pass (autonomous cron)",
    "source_midi": SRC_MIDI,
    "source_midi_sha256": sha,
    "production_method": "SP-035",
    "production_method_name": "GENDYN Stochastic Breakpoint Synthesis",
    "parameters": {
        "sample_rate": SR,
        "bpm": BPM,
        "per_voice": {str(k): v for k, v in VOICE_PARAMS.items()},
        "dynamic_walk": {"sigma_a_step": 0.01, "bounds": [0.05, 0.9]},
        "adsr": {"attack_s": 0.010, "release_s": 0.080},
        "lowpass_hz": 16000,
        "peak": PEAK,
    },
    "outputs": {
        "full_mix_wav": wav_path,
        "full_mix_ogg": ogg_path,
        "midi_copy": midi_copy,
    },
    "verification": {
        "notes_parsed": len(events),
        "notes_synthesized": n_synth,
        "duration_sec": round(total_dur, 2),
        "silence_ratio": round(silent, 4),
        "rms_per_second": rms_map,
        "peak": round(peak, 4),
    },
    "description": "Xenakis GENDYN stochastic breakpoint synthesis: random time-amplitude breakpoints per period, linear interpolation, fresh random draw each period, dynamic sigma_a random walk, per-voice parameter sets.",
}
with open(os.path.join(OUT_DIR, "provenance.json"), "w") as f:
    json.dump(prov, f, indent=2)
print("provenance.json written")
print("DONE")
