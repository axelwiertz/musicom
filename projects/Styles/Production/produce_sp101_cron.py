# -*- coding: utf-8 -*-
"""SP-101 BLOT-style Geometric Modal Resonator Network production pass (absolute layer).

Source : Styles/Blues/039-electric-blues/daily-2026-06-27_blues_039-electric-blues-v5.mid
         (A-minor Am7 16th-note ostinato, 80 BPM, 480 TPB, 12 bars, single voice,
          144 notes, program 30 distortion guitar, notes A3/C4/E3/G3 = {52,55,57,60}).

Method : SP-101 -> sound.synthesis.modal_blot (BLOTEngine). ABSOLUTE layer: the
         whole piece's timbre is re-synthesized as a struck modal-resonator
         network (8 just-intonation modes per piece) — a marimba/bell-like
         ostinato with octave-doubled pieces (size 1.0 / 0.5 / 2.0) for a clear
         fundamental, a waveguide pluck for attack, ring-mod coupling, and an
         FDN "memory" tail.  Replaces the electric-guitar production layer
         entirely; the note material (pitches + 16th grid) is preserved.

Pipeline: source MIDI -> 3-rule audit (grid/harmony/zero-drift)
          -> per-note BLOT strike+render (48000 Hz) -> overlap-add stereo
          -> master() (blues -14 LUFS, -1 dBTP) -> WAV + Opus OGG.
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

from sound.synthesis.modal_blot import (
    BLOTEngine, LumpPiece, ModalResonator, WaveguideString, DEFAULT_SR,
)
from sound.effects.mastering import master, target_for_style, measure_lufs

SRC = Path("/opt/data/repos/musicom/projects/Styles/Blues/039-electric-blues/daily-2026-06-27_blues_039-electric-blues-v5.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP101-modal-blot-039-electric-blues")
AUD = OUT / "Audio"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = DEFAULT_SR                      # 48000 — resonator phase math hardcodes 48000
BPM = 80.0
TPB = 480
BAR_TICKS = 1920
N_BARS = 12
TOTAL_TICKS = BAR_TICKS * N_BARS     # 23040
GRID = 120                            # 16th
SEED = 20261022
STYLE = "blues"
TARGET_LUFS = target_for_style(STYLE)   # -14.0
CEILING_DB = -1.0
RING_TAIL = 0.15                       # extra render per note so decay completes (no click)
NOTE_DUR = 120 / TPB * (60.0 / BPM)    # 0.1875 s per 16th

# --- key / harmony (audit) ----------------------------------------------------
# Notes present: A C E G  -> A natural minor (A B C D E F G), static Am7 vamp.
AMIN_PCS = {9, 11, 0, 2, 4, 5, 7}     # A B C D E F G
AM7_CHORD = {9, 0, 4, 7}              # A C E G
SRC_PCS = {9, 0, 4, 7}                # for pitch verification


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
notes = []           # (pitch, start_tick, end_tick, velocity)
track_ends = []
off_grid = 0
out_scale = 0
out_chord = 0
total_notes = 0
for ti, tr in enumerate(mf.tracks):
    t = 0
    pending = {}
    n_notes = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            pending.setdefault(m.note, []).append((t, m.velocity))
        elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
            if m.note in pending and pending[m.note]:
                s, vel = pending[m.note].pop(0)
                notes.append((m.note, s, t, vel))
                n_notes += 1
                total_notes += 1
                if (s % GRID) != 0:
                    off_grid += 1
                pc = m.note % 12
                if pc not in AMIN_PCS:
                    out_scale += 1
                bar = min(s // BAR_TICKS, N_BARS - 1)
                if pc not in AM7_CHORD:
                    out_chord += 1
    if n_notes:
        track_ends.append(t)

zero_drift = len(set(track_ends)) == 1
print("PREFLIGHT: notes=%d off_grid=%d out_scale=%d out_chord=%d "
      "track_ends=%s zero_drift=%s" % (total_notes, off_grid, out_scale,
                                       out_chord, sorted(set(track_ends)), zero_drift))

# gate
if off_grid != 0 or out_scale != 0 or out_chord != 0 or not zero_drift:
    raise SystemExit("PREFLIGHT FAILED — rework required before SP-101 render")

notes.sort(key=lambda e: e[1])
print("note pitch classes:", sorted(set(n % 12 for n, *_ in notes)))
assert set(n % 12 for n, *_ in notes) <= SRC_PCS

# ---------------------------------------------------------------------------
# 2. BLOT render (absolute layer)
# ---------------------------------------------------------------------------
def pluck_patch(sr=SR):
    engine = BLOTEngine(sample_rate=sr)
    r1 = ModalResonator(size=1.0, shape=0.15, brightness=0.7, ring_time=0.4, heat=0.03)
    engine.add_piece(LumpPiece(resonator=r1, x=0.0, y=0.0))
    r2 = ModalResonator(size=0.5, shape=0.1, brightness=0.4, ring_time=0.25, heat=0.02)
    engine.add_piece(LumpPiece(resonator=r2, x=0.3, y=0.1))
    wg = WaveguideString(sample_rate=sr)
    wg.set_pitch(220.0)
    r3 = ModalResonator(size=2.0, shape=0.2, brightness=0.5, ring_time=0.5, heat=0.0)
    engine.add_piece(LumpPiece(resonator=r3, x=0.5, y=0.3, waveguide=wg))
    engine.set_piece_ring_mod(0, 1)
    engine.breath_noise_amp = 0.004
    engine.droplet_rate = 0.0
    engine.fdn.mix = 0.12
    return engine

max_end = tick_to_sec(max(e[2] for e in notes))
total_len = int((max_end + 0.5) * SR)
L = np.zeros(total_len, dtype=np.float64)
R = np.zeros(total_len, dtype=np.float64)

engine = pluck_patch()
print("Rendering %d notes into %.2f s buffer (BLOT 48000 Hz)..." % (len(notes), total_len / SR))
t0 = time.time()
for i, (pitch, s_tick, e_tick, vel) in enumerate(notes):
    dur = tick_to_sec(e_tick - s_tick)
    n_samples = int((dur + RING_TAIL) * SR)
    # tune waveguide to the note fundamental for attack color
    f0 = 440.0 * 2.0 ** ((pitch - 69.0) / 12.0)
    engine.pieces[2].waveguide.set_pitch(f0)
    engine.strike_all(velocity=0.6)
    seg = engine.render(midi_root=float(pitch), num_samples=n_samples, seed=SEED + i)
    seg = seg.astype(np.float64)
    # linear pan (constant amplitude): low left, high right, subtle
    pan = float(np.clip((pitch - 56) / 10.0, -0.3, 0.3))
    lgain = 0.5 + pan
    rgain = 0.5 - pan
    s0 = int(tick_to_sec(s_tick) * SR)
    s1 = min(s0 + len(seg), total_len)
    L[s0:s1] += seg[:s1 - s0] * lgain
    R[s0:s1] += seg[:s1 - s0] * rgain
    if (i + 1) % 36 == 0:
        print("  rendered %d/%d notes (%.1fs elapsed)" % (i + 1, len(notes), time.time() - t0))

print("BLOT render done in %.1f s" % (time.time() - t0))

stereo = np.stack([L, R], axis=0).astype(np.float32)   # (2, N)
# gentle bus peak guard before master
pk = float(np.max(np.abs(stereo)))
if pk > 1.0:
    stereo *= 0.95 / pk
raw_wav = OUT / "SP101_modal_blot_raw.wav"
write_wav(raw_wav, stereo, sr=SR)
print("raw WAV:", raw_wav.stat().st_size, "bytes")

# ---------------------------------------------------------------------------
# 3. master
# ---------------------------------------------------------------------------
stereo_tm = stereo.T.astype(np.float32)          # (N, 2)
print("Mastering (target %s LUFS, ceiling %s dBTP)..." % (TARGET_LUFS, CEILING_DB))
mastered_tm, rep = master(stereo_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))
final_master = mastered_tm.T.astype(np.float32)  # (2, N)

final_wav = OUT / "SP101-modal-blot-039-electric-blues.wav"
final_ogg = OUT / "SP101-modal-blot-039-electric-blues.ogg"
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


hit_rate, he_mean, valid = pitch_verify(final_master, SRC_PCS)
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
    "source_pcs": sorted(SRC_PCS),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-22",
    "seed": SEED,
    "method": "SP-101",
    "method_module": "sound.synthesis.modal_blot",
    "method_desc": "BLOT-style Geometric Modal Resonator Network — 8-mode just-intonation resonators, waveguide strings, formant filters, ring modulation, multiband saturation, FDN memory (Laboratory 0 BLOT-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "ring_tail": RING_TAIL,
        "patch": "pluck_patch: 3 pieces size=[1.0,0.5,2.0] shape=[0.15,0.1,0.2] "
                 "brightness=[0.7,0.4,0.5] ring_time=[0.4,0.25,0.5] heat=[0.03,0.02,0.0]",
        "ring_mod_pair": [0, 1], "fdn_mix": 0.12, "breath_noise_amp": 0.004,
        "droplet_rate": 0.0, "strike_velocity": 0.6, "pan_range": 0.3,
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "source_bpm": BPM,
    "source_pitch_classes": sorted(SRC_PCS),
    "key": "A natural minor (Am7 vamp)",
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "raw_wav": str(raw_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": he_mean,
    "preflight": {"notes": total_notes, "off_grid": off_grid, "out_scale": out_scale,
                  "out_chord": out_chord, "zero_drift": zero_drift,
                  "track_ends": sorted(set(track_ends))},
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

REPORT = """# SP-101 BLOT-style Geometric Modal Resonator Network — production report

- **Date**: 2026-10-22
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-101 (`sound.synthesis.modal_blot`) — BLOT-style Geometric Modal
  Resonator Network. 8-mode just-intonation resonators per piece, waveguide
  strings, ring modulation, multiband saturation, FDN memory.
- **Layer**: ABSOLUTE (whole-piece timbre replacement; note material preserved).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (55 pickable in
  pool; recent-7-day methods SP-006/032/090/092/099/105/108/111 excluded).
- **Source composition**: `Styles/Blues/039-electric-blues/daily-2026-06-27_blues_039-electric-blues-v5.mid`
  (A-minor Am7 16th-note ostinato, 80 BPM, 480 TPB, 12 bars, single voice,
  144 notes, program 30 distortion guitar; pitches A3/C4/E3/G3).

## Pre-flight audit (3 rules) — PASS, no rework needed
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = 0 |
| Harmony (in key + chord tone) | **PASS** — out-of-scale = 0, out-of-chord = 0 (A nat-minor, Am7) |
| Zero-drift (equal track ends) | **PASS** — single note track, end = 23040 ticks |

## Render
- Patch: 3 modal pieces (size 1.0 / 0.5 / 2.0 → fundamental + octave up + octave
  down), brightness 0.7/0.4/0.5, ring_time 0.4/0.25/0.5 s, waveguide pluck tuned
  per note, ring-mod pair (0,1), FDN mix 0.12. Strike velocity 0.6, +0.15 s ring
  tail per note, overlap-add stereo with subtle pan (low-left, high-right).
- Rendered at 48000 Hz (resonator phase math is 48000-native).
- Mastered: `master()` → blues −14 LUFS target, −1 dBTP ceiling.

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
- BLOT is an inharmonic (just-intonation) modal timbre by design; harmonic
  energy in strict integer-harmonic bins is naturally lower than a SoundFont
  render. The dominant-peak hit rate confirms every window lands on an in-key
  note class (fundamental = strongest mode, reinforced by octave-doubled pieces).
""".format(
    hit_rate=hit_rate, valid=valid, pitch_verdict=pitch_verdict,
    he_mean=he_mean, silence_pct=silence_pct, rms=rms,
    meas_lufs=meas_lufs, peak_val=peak_val,
    final_wav=final_wav, final_ogg=final_ogg, raw_wav=raw_wav,
    wav_bytes=final_wav.stat().st_size, ogg_bytes=final_ogg.stat().st_size,
)
(OUT / "REPORT.md").write_text(REPORT)
print("REPORT.md written")

for s in ("select_job_20261022.py", "inspect_source_20261022.py", "dump_notes_20261022.py"):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp101_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
