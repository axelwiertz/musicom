#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SP-017 Modified FM (Feedback FM & Phase Modulation) — Production pass on
001-balkan-lesnoto (Balkan, 7/8 2+2+3, D hijaz, 120 BPM, 16 bars, 4 sections).

Source: /opt/data/projects/Styles/Balkan/001-balkan-lesnoto/MIDI/balkan-lesnoto.mid
  Voices: Tupan (ch9 prog0, note 36 accents 1-4-7), Tambura (prog33, D2+A2 drone),
          Gaida (prog50, D3 drone), Kaval (prog74, D hijaz ornamented melody).

Method (methods_db SP-017):
  y[n] = Ac * cos( 2*pi*fc*n*Ts + I[n]*y_m[n] )          carrier phase modulation
  y_m[n] = cos( 2*pi*fm*n*Ts + beta*y_m[n-1] )            modulator with SELF-FEEDBACK
  I[n] = dynamic modulation index (slow LFO wobble per note)

Per-voice FM roles (remapped by GM program for this composition):
  Kaval  (74): fm = 1x fc (breathy flute), I = 2.0, beta = 0.15
  Gaida  (50): fm = 2x fc (reedy drone shimmer), I = 1.5, beta = 0.25
  Tambura(33): fm = 1x fc (brassy saw-like),  I = 4.0, beta = 0.60, decay env
  Tupan  (0):  chaotic feedback (beta > 1.6 -> deterministic noise burst):
               note 36 fc=85Hz beta=2.2 (low "dum" frame-drum thump)

Pitfalls addressed (SP-035 lesson + skills):
  - carrier + modulator phase accumulated continuously per note (no zipper)
  - feedback recurrence computed sample-by-sample (honest self-feedback)
  - per-note ADSR (no clicks), additive buffer (no overlap crossfade needed)
  - DC removal per voice
  - 20 Hz HP + 16 kHz LP post (scipy sosfilt)
  - normalize 0.89 peak; silence ratio + per-second RMS; FFT pitch verification +
    note-vs-detected match + harmonic-energy check (reports in provenance)

Outputs -> /opt/data/projects/Styles/Production/SP017-feedback-fm-balkan-lesnoto/
  Audio/SP017-feedback-fm-balkan-lesnoto.wav|.ogg + stems/
  MIDI/ (copy of source)
  provenance.json + Analysis/render_stats.json + Analysis/grid_visualization.txt
"""
import os
import json
import wave
import shutil
import subprocess
import hashlib
import math
from collections import defaultdict

import numpy as np
import mido
from mido import MidiFile

SR = 44100
OUT_DIR = "/opt/data/projects/Styles/Production/SP017-feedback-fm-balkan-lesnoto"
SRC_MIDI = "/opt/data/projects/Styles/Balkan/001-balkan-lesnoto/MIDI/balkan-lesnoto.mid"
NAME = "SP017-feedback-fm-balkan-lesnoto"
PEAK = 0.89
SEED = 20260831

os.makedirs(os.path.join(OUT_DIR, "Audio", "stems"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "MIDI"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "Analysis"), exist_ok=True)


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


# ------------------------------------------------------------------ FM engine
def feedback_fm_note(fc, fm, index, beta, dur_sec, rng,
                     attack_s=0.015, release_s=0.080, index_lfo_hz=0.4,
                     index_lfo_depth=0.30):
    """One note: carrier phase-modulated by self-feedback modulator.

    y_m[n] = cos(phi_m[n] + beta*y_m[n-1])
    y[n]   = cos(phi_c[n] + I[n]*y_m[n])
    I[n]   = index * (1 + depth*sin(2*pi*lfo_hz*t))   dynamic modulation index
    """
    n = int(dur_sec * SR)
    if n <= 0:
        return np.zeros(0, dtype=np.float32)
    phi_c = 2.0 * math.pi * fc / SR
    phi_m = 2.0 * math.pi * fm / SR
    # precompute index LFO
    lfo = 1.0 + index_lfo_depth * np.sin(2 * np.pi * index_lfo_hz *
                                         np.arange(n) / SR)
    y = np.empty(n, dtype=np.float32)
    ph_m = rng.uniform(0, 2 * math.pi)
    ph_c = rng.uniform(0, 2 * math.pi)
    y_m_prev = 0.0
    for i in range(n):
        y_m = math.cos(ph_m + beta * y_m_prev)
        y[i] = math.cos(ph_c + index * lfo[i] * y_m)
        y_m_prev = y_m
        ph_m += phi_m
        ph_c += phi_c
    # ADSR
    attack = min(int(attack_s * SR), n // 2)
    release = min(int(release_s * SR), n // 2)
    env = np.ones(n)
    if attack > 0:
        env[:attack] = np.linspace(0, 1, attack)
    if release > 0:
        env[-release:] = np.linspace(1, 0, release)
    return (y * env).astype(np.float32)


VOICE_PARAMS = {
    74: dict(role="Kaval (Flute, D hijaz melody)", fm_mult=1.0, index=2.0, beta=0.15,
             gain=0.50, attack_s=0.015, release_s=0.090),
    50: dict(role="Gaida (Drone, Synth Strings)", fm_mult=2.0, index=1.5, beta=0.25,
             gain=0.32, attack_s=0.060, release_s=0.150),
    33: dict(role="Tambura (Bass drone, Electric Bass)", fm_mult=1.0, index=4.0, beta=0.60,
             gain=0.55, attack_s=0.010, release_s=0.090),
}
DEFAULT_PARAMS = dict(role="Unknown", fm_mult=2.0, index=2.0, beta=0.2,
                      gain=0.3, attack_s=0.02, release_s=0.10)

# percussion: pitch -> (fc, beta, gain, dur_scale)
PERC = {
    36: dict(fc=85.0,  beta=2.2, gain=1.00, release_s=0.120),  # tupan low "dum"
}
PERC_DEFAULT = dict(fc=800.0, beta=2.4, gain=0.6, release_s=0.06)


def render_perc_note(pitch, dur_sec, rng):
    """Chaotic feedback FM percussion: beta>1.6 -> deterministic noise burst."""
    p = PERC.get(pitch, PERC_DEFAULT)
    n = int(dur_sec * SR)
    if n <= 0:
        return np.zeros(0, dtype=np.float32)
    fm = p["fc"]
    fc = p["fc"] * rng.uniform(0.9, 1.1)
    phi_m = 2 * math.pi * fm / SR
    phi_c = 2 * math.pi * fc / SR
    y = np.empty(n, dtype=np.float32)
    ph_m = rng.uniform(0, 2 * math.pi)
    ph_c = rng.uniform(0, 2 * math.pi)
    y_m_prev = 0.0
    for i in range(n):
        y_m = math.cos(ph_m + p["beta"] * y_m_prev)
        y[i] = math.cos(ph_c + p["beta"] * y_m)  # same beta drives chaos
        y_m_prev = y_m
        ph_m += phi_m
        ph_c += phi_c
    attack = min(int(0.002 * SR), n // 2)
    release = min(int(p["release_s"] * SR), n // 2)
    env = np.ones(n)
    if attack > 0:
        env[:attack] = np.linspace(0, 1, attack)
    if release > 0:
        env[-release:] = np.linspace(1, 0, release)
    return (y * env * p["gain"]).astype(np.float32)


def render_voice(events, params, rng):
    total = max(e["end"] for e in events) + 0.5
    n_total = int(total * SR)
    buf = np.zeros(n_total, dtype=np.float64)
    for e in events:
        dur = e["end"] - e["start"]
        if dur <= 0:
            continue
        fc = midi_to_freq(e["pitch"])
        fm = fc * params["fm_mult"]
        y = feedback_fm_note(fc, fm, params["index"], params["beta"], dur, rng,
                             attack_s=params["attack_s"],
                             release_s=params["release_s"])
        if len(y) == 0:
            continue
        y = y * (e["vel"] / 127.0) * params["gain"]
        start_s = int(e["start"] * SR)
        end_s = min(start_s + len(y), n_total)
        if start_s >= n_total:
            continue
        buf[start_s:end_s] += y[:end_s - start_s]
    buf = buf - np.mean(buf)  # DC removal per voice
    return buf


# ------------------------------------------------------------------ read midi
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
                events.append(dict(start=st * sec_per_tick,
                                   end=abs_ticks * sec_per_tick,
                                   pitch=msg.note, vel=vel, program=p))
    for key, (st, vel, p) in open_notes.items():
        events.append(dict(start=st * sec_per_tick,
                           end=(st + tpb) * sec_per_tick,
                           pitch=key[1], vel=vel, program=p))

assert events, "no note events parsed"
total_dur = max(e["end"] for e in events) + 0.5
n_total = int(total_dur * SR)
print(f"parsed {len(events)} events, duration {total_dur:.2f}s, tempo {tempo_us}")

# ------------------------------------------------------------------ render
by_prog = defaultdict(list)
for e in events:
    by_prog[e["program"]].append(e)

rng = np.random.default_rng(SEED)
voice_buffers = {}
mix = np.zeros(n_total, dtype=np.float64)
n_synth = 0
for prog, evs in sorted(by_prog.items()):
    if prog == 0:
        # percussion channel (ch9 program 0)
        params = dict(role="Percussion (Tupan)")
        buf = np.zeros(int(total_dur * SR), dtype=np.float64)
        for e in evs:
            y = render_perc_note(e["pitch"], e["end"] - e["start"], rng)
            if len(y) == 0:
                continue
            y = y * (e["vel"] / 127.0)
            start_s = int(e["start"] * SR)
            end_s = min(start_s + len(y), len(buf))
            if start_s >= len(buf):
                continue
            buf[start_s:end_s] += y[:end_s - start_s]
            n_synth += 1
        buf = buf - np.mean(buf)
        voice_buffers[prog] = buf
        mix[:len(buf)] += buf
        print(f"voice prog {prog} (Percussion): {len(evs)} notes rendered")
    else:
        params = VOICE_PARAMS.get(prog, DEFAULT_PARAMS)
        buf = render_voice(evs, params, rng)
        voice_buffers[prog] = buf
        mix[:len(buf)] += buf
        n_synth += len(evs)
        print(f"voice prog {prog} ({params['role']}): {len(evs)} notes rendered")

# ------------------------------------------------------------------ post
try:
    from scipy.signal import butter, sosfilt
    sos_hp = butter(2, 20, fs=SR, output="sos", btype="highpass")
    sos_lp = butter(4, 16000, fs=SR, output="sos", btype="lowpass")
    mix = sosfilt(sos_hp, sosfilt(sos_lp, mix))
    print("post: 20 Hz HP + 16 kHz LP applied")
except Exception as exc:
    print(f"post filters skipped ({exc})")

peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * PEAK

# ------------------------------------------------------------------ verify
mono = mix
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
secs = int(total_dur)
rms_map = []
for s in range(secs):
    seg = mono[s * SR:(s + 1) * SR]
    rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    rms_map.append(round(rms, 5))
print(f"silence ratio: {silent * 100:.1f}%")
print(f"per-second RMS: {rms_map}")


def fft_pitch(seg, sr):
    seg = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    mask = (freqs >= 50) & (freqs <= 1000)
    if not np.any(mask):
        return 0.0, 0.0
    idx = np.argmax(spec[mask])
    return freqs[mask][idx], spec[mask][idx]


# expected notes active per 0.5s window (from MIDI events)
win = 0.5
n_win = int(win * SR)
detected = []       # (t0, peak_hz)
expected_by_win = []  # list of freq sets per window
t0s = np.arange(0.25, max(total_dur - 0.5, 0.5), 0.5)
for t0 in t0s:
    seg = mono[int(t0 * SR):int((t0 + 0.5) * SR)]
    p, _ = fft_pitch(seg, SR)
    if p > 0:
        detected.append((t0, p))
    # expected active pitched notes (exclude percussion prog 0)
    exp = []
    for e in events:
        if e["program"] == 0:
            continue
        if e["start"] <= t0 + win and e["end"] >= t0:
            exp.append(midi_to_freq(e["pitch"]))
    expected_by_win.append((t0, exp))

match_count = 0
matched_windows = 0
for (t0, exp), (t0d, p) in zip(expected_by_win, detected):
    if not exp:
        continue
    matched_windows += 1
    # detected peak near any expected note freq or one of its first 4 harmonics
    hit = False
    for f in exp:
        for k in (1, 2, 3, 4):
            if abs(p - k * f) / (k * f) < 0.02:
                hit = True
                break
        if hit:
            break
    if hit:
        match_count += 1

# harmonic energy: for the lowest fundamental present, energy in first 8 harmonics
def harmonic_energy(seg, f0, sr):
    n = len(seg)
    spec = np.abs(np.fft.rfft(seg * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    total = np.sum(spec ** 2) + 1e-12
    harm = 0.0
    for k in range(1, 9):
        harm += (spec[np.argmin(np.abs(freqs - k * f0))] ** 2)
    return harm / total

# find lowest active fundamental across whole piece
lowest_f0 = min(midi_to_freq(e["pitch"]) for e in events if e["program"] != 0)
harm_en = harmonic_energy(mono[int(0.5 * SR):int(2.5 * SR)], lowest_f0, SR)
harm_en_all = []
for t0 in np.arange(0.5, min(total_dur - 1.0, 8.0), 1.0):
    harm_en_all.append(round(harmonic_energy(mono[int(t0 * SR):int((t0 + 1.0) * SR)], lowest_f0, SR), 4))

print(f"pitch frames detected: {len(detected)} / {len(t0s)}")
if detected:
    ps = [p for _, p in detected]
    print(f"  pitch range: {min(ps):.0f}-{max(ps):.0f} Hz, median {np.median(ps):.0f} Hz")
print(f"note-match windows: {match_count}/{matched_windows}")
print(f"harmonic energy (lowest f0 {lowest_f0:.1f} Hz, first 8 harm): {harm_en:.3f}")

# ------------------------------------------------------------------ write wavs
def write_wav(path, data, sr=SR):
    data16 = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data16.tobytes())

wav_path = os.path.join(OUT_DIR, "Audio", f"{NAME}.wav")
write_wav(wav_path, mix)
print(f"WAV: {wav_path} ({os.path.getsize(wav_path)} bytes)")

stem_paths = {}
for prog, buf in voice_buffers.items():
    if prog == 0:
        role = "Percussion"
    else:
        role = VOICE_PARAMS.get(prog, DEFAULT_PARAMS)["role"]
    sp = os.path.join(OUT_DIR, "Audio", "stems", f"stem_{role.split('(')[0].strip().lower().replace(' ', '_')}.wav")
    pk = np.max(np.abs(buf))
    if pk > 0:
        buf = buf / pk * PEAK
    write_wav(sp, buf)
    stem_paths[role] = sp
    print(f"stem: {sp} ({os.path.getsize(sp)} bytes)")

ogg_path = os.path.join(OUT_DIR, "Audio", f"{NAME}.ogg")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                "-codec:a", "libopus", "-b:a", "128k", ogg_path], check=True)
print(f"OGG: {ogg_path} ({os.path.getsize(ogg_path)} bytes)")

# copy source midi
midi_out = os.path.join(OUT_DIR, "MIDI", f"{NAME}.mid")
shutil.copy2(SRC_MIDI, midi_out)

# ------------------------------------------------------------------ provenance
with open(SRC_MIDI, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()

prov = {
    "job": "SP-017 production pass (cron)",
    "source_midi": SRC_MIDI,
    "source_midi_sha256": sha,
    "production_method": "SP-017",
    "production_method_name": "Modified FM (Feedback FM & Phase Modulation)",
    "source_composition": "001-balkan-lesnoto (Balkan, 7/8 2+2+3, D hijaz, 120 BPM, 16 bars, 4 sections)",
    "parameters": {
        "sample_rate": SR,
        "seed": SEED,
        "peak": PEAK,
        "post": {"highpass_hz": 20, "lowpass_hz": 16000},
        "per_voice": {str(k): {kk: vv for kk, vv in v.items() if kk != "role"}
                      for k, v in VOICE_PARAMS.items()},
        "percussion": {str(k): v for k, v in PERC.items()},
        "feedback_recurrence": "y_m[n]=cos(2*pi*fm*n*Ts + beta*y_m[n-1]); "
                               "y[n]=cos(2*pi*fc*n*Ts + I[n]*y_m[n])",
        "dynamic_index": "I[n]=index*(1+0.30*sin(2*pi*0.4*t))",
        "adsr": {"attack_s": "per-voice", "release_s": "per-voice"},
    },
    "outputs": {
        "full_mix_wav": wav_path,
        "full_mix_ogg": ogg_path,
        "stems": stem_paths,
        "midi": midi_out,
    },
    "verification": {
        "notes_parsed": len(events),
        "notes_synthesized": n_synth,
        "duration_sec": round(total_dur, 2),
        "silence_ratio": round(silent, 4),
        "rms_per_second": rms_map,
        "pitch_frames_detected": len(detected),
        "pitch_frame_total": len(t0s),
        "pitch_range_hz": [round(min(ps), 1), round(max(ps), 1)] if detected else None,
        "pitch_median_hz": round(float(np.median(ps)), 1) if detected else None,
        "note_match_windows": match_count,
        "note_match_total": matched_windows,
        "harmonic_energy_lowest_f0": round(harm_en, 4),
        "harmonic_energy_t0_8s": harm_en_all,
    },
}
prov_path = os.path.join(OUT_DIR, "provenance.json")
with open(prov_path, "w") as f:
    json.dump(prov, f, indent=2)
print(f"provenance: {prov_path}")

# render stats json
stats = {
    "file": wav_path,
    "size_bytes": os.path.getsize(wav_path),
    "duration_sec": round(total_dur, 2),
    "silence_ratio": round(silent, 4),
    "rms_per_second": rms_map,
    "pitch_frames": len(detected),
    "pitch_frame_total": len(t0s),
    "pitch_median_hz": round(float(np.median(ps)), 1) if detected else None,
    "note_match": f"{match_count}/{matched_windows}",
    "harmonic_energy": round(harm_en, 4),
    "notes_parsed": len(events),
}
stats_path = os.path.join(OUT_DIR, "Analysis", "render_stats.json")
with open(stats_path, "w") as f:
    json.dump(stats, f, indent=2)
print(f"render stats: {stats_path}")

# ------------------------------------------------------------------ grid viz
BAR = 60.0 / 120 * 7  # 3.5 s per bar (7/8, 120 BPM)
n_bars = int(total_dur / BAR)
grid_lines = ["SP-017 Modified FM (Feedback FM) - Balkan Lesnoto (001-balkan-lesnoto)",
              f"duration {total_dur:.1f}s, {n_bars} bars of 7/8 @ 120 BPM, D hijaz",
              "Legend: 16 sub-cells per bar, # = onset density, . = rest", ""]
for prog in sorted(by_prog):
    if prog == 0:
        role = "Percussion"
    else:
        role = VOICE_PARAMS.get(prog, DEFAULT_PARAMS)["role"]
    evs = by_prog[prog]
    cells = []
    for b in range(n_bars):
        t0 = b * BAR
        t1 = t0 + BAR
        onsets = [e for e in evs if t0 <= e["start"] < t1]
        density = min(len(onsets), 16)
        cells.append("#" * density + "." * (16 - density))
    grid_lines.append(f"prog {prog:3d} {role:<26} |" + "|".join(cells))
grid_lines.append("")
grid_path = os.path.join(OUT_DIR, "Analysis", "grid_visualization.txt")
with open(grid_path, "w") as f:
    f.write("\n".join(grid_lines) + "\n")
print(f"grid: {grid_path}")

print("DONE")
