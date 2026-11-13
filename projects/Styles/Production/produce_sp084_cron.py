# -*- coding: utf-8 -*-
"""SP-084 AirPipe flue-pipe physical model production pass (absolute layer).

Source : Styles/Ragtime/206-ragtime-skeleton-refinement/MIDI/206-ragtime-skeleton-refinement.mid
         (C major, 120 BPM, 480 TPB, 40 bars = 76800 ticks = 80 s,
          form Intro|A|B|A2|Trio|Coda, 3 piano voices: Melody (ch0, 60-77),
          Bass stride (ch1, 48-57), Comp stabs (ch2, 55-65), 600 notes).

Method : SP-084 -> sound.synthesis.air_pipe (AirPipe / AirPipePatch, Modartt
         Airteq-style). ABSOLUTE layer: the whole piece's timbre is
         re-synthesized as a bank of physically-modelled flue pipes. Melody +
         comp = OPEN pipes (odd+even harmonics, flute/organ), bass = STOPPED
         pipes (odd harmonics, reed/organ). Air pressure scales with MIDI
         velocity (never overblows -> clean pitch); a slow global air LFO
         (the "Dynamic Aerophone Modelling" hook) breathes the instrument
         bank. Replaces the piano production layer entirely; note material
         (pitches + 16th grid) preserved.

Pipeline: source MIDI -> 3-rule audit (grid/harmony/zero-drift)
          -> per-note AirPipe render (44100 Hz) -> overlap-add stereo
          -> master() (ragtime fallback -14 LUFS, -1 dBTP) -> WAV + Opus OGG
          -> pitch/silence/RMS verification -> provenance.json + REPORT.md.
"""
import json
import math
import os
import shutil
import subprocess
import time
import wave
from pathlib import Path

import numpy as np
import mido

from sound.synthesis.air_pipe import AirPipe, AirPipePatch, DEFAULT_SR
from sound.effects.mastering import master, target_for_style, measure_lufs

SRC = Path("/opt/data/repos/musicom/projects/Styles/Ragtime/"
           "206-ragtime-skeleton-refinement/MIDI/206-ragtime-skeleton-refinement.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP084-air-pipe-206-ragtime-skeleton-refinement")
AUD = OUT / "Audio"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = DEFAULT_SR                        # 44100
BPM = 120.0
TPB = 480
BAR_TICKS = 1920
N_BARS = 40
TOTAL_TICKS = BAR_TICKS * N_BARS       # 76800
GRID = 120                             # 16th
SEED = 20261113
STYLE = "Ragtime"
TARGET_LUFS = target_for_style(STYLE)  # -14.0 fallback
CEILING_DB = -1.0
RING_TAIL = 0.12                       # s extra render per note (breath tail)
PRESSURE_BASE = 0.32
PRESSURE_RANGE = 0.40                  # pressure = 0.32 + 0.40 * vel/127 (< overblow 0.75)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# --- key / harmony (audit) ----------------------------------------------------
# C major. Per-bar chord progression (40 bars, matches compose.py).
SCALE_PCS = {0, 2, 4, 5, 7, 9, 11}
CHORDS = {
    "C": {0, 4, 7}, "Cmaj7": {0, 4, 7, 11}, "Dm": {2, 5, 9},
    "Dm7": {2, 5, 9, 0}, "Em7": {4, 7, 11, 2}, "F": {5, 9, 0},
    "Fmaj7": {5, 9, 0, 4}, "G7": {7, 11, 2, 5}, "Am": {9, 0, 4},
    "Am7": {9, 0, 4, 7},
}
BAR_CHORD_NAMES = (
    ["G7"] * 4
    + ["C", "Cmaj7", "Am", "Dm7", "G7", "C", "F", "G7"]
    + ["F", "Fmaj7", "Dm", "G7", "Em7", "Am", "Dm7", "G7"]
    + ["C", "Cmaj7", "Am", "Dm7", "G7", "C", "G7", "C"]
    + ["F", "F", "Dm", "G7", "C", "Am", "F", "G7"]
    + ["C", "G7", "C", "C"]
)
assert len(BAR_CHORD_NAMES) == N_BARS
BAR_CHORD_PCS = [CHORDS[n] for n in BAR_CHORD_NAMES]


def tick_to_sec(tick):
    return tick * (60.0 / (BPM * TPB))


def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if nch == 1:
            return np.vstack([samples, samples]), sr
        return samples.reshape(-1, nch).T, sr


def write_wav(p, audio, sr=SR):
    audio = np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0)
    if audio.ndim == 1:
        nch, interleaved = 1, audio
    elif audio.shape[0] == 2:
        nch, interleaved = 2, audio.T.reshape(-1)
    else:
        nch, interleaved = audio.shape[0], audio.T.reshape(-1)
    data = (interleaved * 32767.0).astype(np.int16).tobytes()
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)


# ---------------------------------------------------------------------------
# 0. copy source MIDI for reference
# ---------------------------------------------------------------------------
shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))

# ---------------------------------------------------------------------------
# 1. extract notes + pre-flight 3-rule audit
# ---------------------------------------------------------------------------
mf = mido.MidiFile(str(SRC))
notes = []           # (pitch, start_tick, end_tick, velocity, channel)
track_ends = []
off_grid = 0
out_scale = 0
out_chord = 0
total_notes = 0
for ti, tr in enumerate(mf.tracks):
    t = 0
    pending = {}
    n_notes = 0
    channel = None
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            channel = m.channel
            pending.setdefault(m.note, []).append((t, m.velocity))
        elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
            if m.note in pending and pending[m.note]:
                s, vel = pending[m.note].pop(0)
                notes.append((m.note, s, t, vel, channel))
                n_notes += 1
                total_notes += 1
                if (s % GRID) != 0:
                    off_grid += 1
                pc = m.note % 12
                if pc not in SCALE_PCS:
                    out_scale += 1
                bar = min(s // BAR_TICKS, N_BARS - 1)
                if pc not in BAR_CHORD_PCS[bar]:
                    out_chord += 1
    if n_notes:
        track_ends.append(t)

zero_drift = len(set(track_ends)) == 1
print("PREFLIGHT: notes=%d off_grid=%d out_scale=%d out_chord=%d "
      "track_ends=%s zero_drift=%s" % (total_notes, off_grid, out_scale,
                                       out_chord, sorted(set(track_ends)), zero_drift))

if off_grid != 0 or out_scale != 0 or out_chord != 0 or not zero_drift:
    raise SystemExit("PREFLIGHT FAILED — rework required before SP-084 render")

notes.sort(key=lambda e: e[1])
print("note pitch classes:", sorted(set(n % 12 for n, *_ in notes)))
print("voices by channel:", {c: sum(1 for n in notes if n[4] == c)
                             for c in sorted(set(n[4] for n in notes))})

# ---------------------------------------------------------------------------
# 2. AirPipe render (absolute layer)
# ---------------------------------------------------------------------------
max_end = tick_to_sec(max(e[2] for e in notes))
total_len = int((max_end + 0.5) * SR)
L = np.zeros(total_len, dtype=np.float64)
R = np.zeros(total_len, dtype=np.float64)

# global air "breath" LFO (DAM hook) — slow swell, instrument-wide
def global_air(t):
    return 0.10 * np.sin(2 * np.pi * 0.15 * t) + 0.06 * np.sin(2 * np.pi * 0.37 * t)

print("Rendering %d notes into %.2f s buffer (AirPipe 44100 Hz)..." % (len(notes), total_len / SR))
t0 = time.time()
rendered = 0
for i, (pitch, s_tick, e_tick, vel, ch) in enumerate(notes):
    dur = tick_to_sec(e_tick - s_tick)
    n_samples = int((dur + RING_TAIL) * SR)
    pressure = PRESSURE_BASE + PRESSURE_RANGE * (vel / 127.0)
    stopped = (ch == 1)                    # bass -> stopped (odd harmonics)
    pipe = AirPipe(midi_note=float(pitch), pressure=pressure, stopped=stopped,
                   sample_rate=SR, seed=SEED + i * 7)
    seg = pipe.render(dur + RING_TAIL, air_mod=global_air).astype(np.float64)
    pan = float(np.clip((pitch - 56) / 14.0, -0.35, 0.35))
    lgain = 0.5 + pan
    rgain = 0.5 - pan
    s0 = int(tick_to_sec(s_tick) * SR)
    s1 = min(s0 + len(seg), total_len)
    L[s0:s1] += seg[:s1 - s0] * lgain
    R[s0:s1] += seg[:s1 - s0] * rgain
    rendered += 1
    if rendered % 120 == 0:
        print("  rendered %d/%d notes (%.1fs elapsed)" % (rendered, len(notes), time.time() - t0))

print("AirPipe render done in %.1f s" % (time.time() - t0))

stereo = np.stack([L, R], axis=0).astype(np.float32)   # (2, N)
pk = float(np.max(np.abs(stereo)))
if pk > 1.0:
    stereo *= 0.95 / pk
raw_wav = OUT / "SP084_air_pipe_raw.wav"
write_wav(raw_wav, stereo, sr=SR)
print("raw WAV:", raw_wav.stat().st_size, "bytes")

# ---------------------------------------------------------------------------
# 3. master
# ---------------------------------------------------------------------------
stereo_tm = stereo.T.astype(np.float32)          # (N, 2)
print("Mastering (target %.1f LUFS, ceiling %.1f dBTP)..." % (TARGET_LUFS, CEILING_DB))
mastered_tm, rep = master(stereo_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))
final_master = mastered_tm.T.astype(np.float32)  # (2, N)

final_wav = OUT / "SP084-air-pipe-206-ragtime-skeleton-refinement.wav"
final_ogg = OUT / "SP084-air-pipe-206-ragtime-skeleton-refinement.ogg"
write_wav(final_wav, final_master, sr=SR)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV: %d  final OGG: %d" % (final_wav.stat().st_size, final_ogg.stat().st_size))

# ---------------------------------------------------------------------------
# 4. verification
# ---------------------------------------------------------------------------
meas_lufs = float(measure_lufs(mastered_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_master)))
mono = 0.5 * (final_master[0] + final_master[1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f" % (meas_lufs, peak_val, silence_pct, rms))


def pitch_verify(audio_2n, pcs):
    mono_ = 0.5 * (audio_2n[0] + audio_2n[1])
    wl = int(0.5 * SR)
    nw = len(mono_) // wl
    hits = valid = 0
    he_list = []
    for w in range(nw):
        seg = mono_[w * wl:(w + 1) * wl]
        if np.max(np.abs(seg)) < 0.01:
            continue
        valid += 1
        win = np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg * win))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
        mask = (freqs >= 50.0) & (freqs <= 1000.0)
        sub = spec[mask]
        subf = freqs[mask]
        dom = subf[np.argmax(sub)]
        midi_val = 69.0 + 12.0 * math.log2(max(1.0, dom) / 440.0)
        pc = round(midi_val) % 12
        if pc in pcs:
            hits += 1
        tot = np.sum(spec ** 2) + 1e-12
        he = 0.0
        for h in range(1, 9):
            tf = dom * h
            hband = (freqs >= tf - 15.0) & (freqs <= tf + 15.0)
            he += np.sum(spec[hband] ** 2)
        he_list.append(float(he / tot))
    hit_rate = hits / max(1, valid)
    he_mean = float(np.mean(he_list)) if he_list else 0.0
    return hit_rate, he_mean, valid


hit_rate, he_mean, valid = pitch_verify(final_master, SCALE_PCS)
pitch_verdict = "PASS" if hit_rate >= 0.60 else "FAIL"
print("Pitch verify: valid=%d hit=%.4f mean_HE=%.4f -> %s"
      % (valid, hit_rate, he_mean, pitch_verdict))

# ---------------------------------------------------------------------------
# 5. artifacts
# ---------------------------------------------------------------------------
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "hit_rate": hit_rate, "mean_harmonic_energy": he_mean, "valid_windows": valid,
    "pitch_verdict": pitch_verdict,
    "n_notes": len(notes), "note_pitch_classes": sorted(set(n % 12 for n, *_ in notes)),
    "render_seconds": round(total_len / SR, 3),
    "pressure_base": PRESSURE_BASE, "pressure_range": PRESSURE_RANGE,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-13",
    "seed": SEED,
    "method": "SP-084",
    "method_module": "sound.synthesis.air_pipe",
    "method_desc": "Flue-Pipe Physical Model w/ Air-Supply Modulation — "
                   "open/stopped cylindrical pipe resonators (c/2L, c/4L with "
                   "end correction), saturating flue-jet drive, turbulence "
                   "breath, overblow migration, DAM air-supply modulation "
                   "(Modartt Airteq-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "ring_tail": RING_TAIL, "pressure_base": PRESSURE_BASE,
        "pressure_range": PRESSURE_RANGE, "overblow_threshold": 0.75,
        "voice_map": "melody=open, comp=open, bass=stopped (odd harmonics)",
        "global_air": "0.10*sin(2pi*0.15t) + 0.06*sin(2pi*0.37t)",
        "pan_range": 0.35, "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "source_bpm": BPM,
    "source_pitch_classes": sorted(SCALE_PCS),
    "key": "C major",
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "raw_wav": str(raw_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": he_mean,
    "preflight": {"notes": total_notes, "off_grid": off_grid, "out_scale": out_scale,
                  "out_chord": out_chord, "zero_drift": zero_drift,
                  "track_ends": sorted(set(track_ends))},
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

REPORT = """# SP-084 AirPipe flue-pipe physical model — production report

- **Date**: 2026-11-13
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-084 (`sound.synthesis.air_pipe`) — physical-modelled flue-pipe
  bank with air-supply modulation (Modartt Airteq-style). Open/stopped
  cylindrical resonators, saturating flue-jet drive, turbulence breath,
  overblow migration, DAM air modulation.
- **Layer**: ABSOLUTE (whole-piece timbre replacement; note material preserved).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (93 registered,
  85 in pool; recent-7-day methods SP-069/097/113/119/138/146/154 excluded,
  SP-138 already used on this source).
- **Source composition**: `Styles/Ragtime/206-ragtime-skeleton-refinement/MIDI/206-ragtime-skeleton-refinement.mid`
  (C major, 120 BPM, 480 TPB, 40 bars = 80 s, Introduction|A|B|A2|Trio|Coda,
  3 piano voices — Melody 60-77, stride Bass 48-57, Comp stabs 55-65, 600 notes).

## Pre-flight audit (3 rules) — PASS (no rework needed)
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = {off_grid} |
| Harmony (in key + chord tone) | **PASS** — out-of-scale = {out_scale}, out-of-chord = {out_chord} (C major, per-bar diatonic progression) |
| Zero-drift (equal track ends) | **PASS** — track_ends = {track_ends} |

## Render
- Per-note AirPipe at 44100 Hz. Melody + comp = OPEN pipes (flute/organ, even +
  odd harmonics); bass = STOPPED pipes (odd-harmonic reed/organ). Air pressure
  = {PRESSURE_BASE} + {PRESSURE_RANGE} * vel/127 (never exceeds the 0.75
  overblow threshold -> clean pitch, brighter accents).
- Global "air" LFO (DAM) breathes the whole instrument bank: 0.10 sin(0.15 Hz)
  + 0.06 sin(0.37 Hz).
- Register-based stereo pan (low-left, high-right, ±0.35), overlap-add with
  +{RING_TAIL}s breath tail per note.
- Mastered: `master()` → {STYLE_LUFS} LUFS target, -1 dBTP ceiling.

## Verification
- **Pitch**: dominant-peak-in-key hit rate = {hit_rate:.4f} ({valid} windows) → **{pitch_verdict}**
- **Harmonic energy (8 harmonics of dominant)**: {he_mean:.4f}
- **Silence**: {silence_pct:.2f}%
- **RMS**: {rms:.4f}
- **LUFS**: {meas_lufs:.2f}  **true peak**: {peak_val:.4f}

## Files
- `{final_wav}` ({wav_bytes} bytes)
- `{final_ogg}` ({ogg_bytes} bytes)
- `{raw_wav}` (pre-master)
- `MIDI/source_original.mid` (reference copy)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- AirPipe is a physical model: the low mode-count means harmonic energy is
  naturally concentrated in the first few integer harmonics of the fundamental,
  giving a clean flute/organ tonal signature (high HE, unlike inharmonic
  synthesis). Stopped bass pipes add odd-harmonic richness for a reed-organ low
  end. Overblow deliberately avoided to keep pitch-verification exact.
""".format(
    off_grid=off_grid, out_scale=out_scale, out_chord=out_chord,
    track_ends=sorted(set(track_ends)),
    PRESSURE_BASE=PRESSURE_BASE, PRESSURE_RANGE=PRESSURE_RANGE,
    RING_TAIL=RING_TAIL, STYLE_LUFS=TARGET_LUFS,
    hit_rate=hit_rate, valid=valid, pitch_verdict=pitch_verdict,
    he_mean=he_mean, silence_pct=silence_pct, rms=rms,
    meas_lufs=meas_lufs, peak_val=peak_val,
    final_wav=final_wav, final_ogg=final_ogg, raw_wav=raw_wav,
    wav_bytes=final_wav.stat().st_size, ogg_bytes=final_ogg.stat().st_size,
)
(OUT / "REPORT.md").write_text(REPORT)
print("REPORT.md written")

for s in ("select_job_20261113.py", "_inspect_206.py"):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp084_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")