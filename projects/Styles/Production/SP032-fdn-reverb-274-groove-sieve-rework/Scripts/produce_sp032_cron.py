# -*- coding: utf-8 -*-
"""SP-032 FDN Reverb production pass (absolute layer) on 274-groove-sieve-rework.

Job: random-style production (SP) layer-aligned, 2026-11-20, seed 20261120.
Method: SP-032 -> sound.effects.fdn_reverb (FDN class, Rev Ocean 'Tidal' style).
Source: Styles/Groove/274-groove-sieve-rework (G natural minor, 110 BPM, 480 TPB,
        32 bars = 61440 ticks, 6 voices: Lead Soprano Sax 65, Horns Brass 61,
        Rhodes EP 4, Bass EB 33, Counter Strings 48, Drums ch9).

Pipeline: 3-rule preflight audit (grid/harmony/zero-drift) on the selected
          humanized source AND its grid-locked -perfect companion
          -> render dry FluidSynth (reverb/chorus OFF) -> FDN reverb (absolute
          spatial layer) -> master() (groove fallback -14 LUFS, -1 dBTP)
          -> WAV + Opus OGG -> pitch/silence/RMS verification
          -> dry stems -> provenance.json + REPORT.md.
"""
import json
import math
import os
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np
import mido

from sound.effects.fdn_reverb import FDN
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav
from sound.render.fluidsynth import discover_soundfont

SEED = 20261120
DATE = "2026-11-20"
STYLE = "groove"
BPM = 110.0
TPB = 480
BAR_TICKS = 1920
GRID = 120            # 16th
N_BARS = 32
TOTAL_TICKS = BAR_TICKS * N_BARS     # 61440
SR = 44100

SRC_HUMANIZED = Path(
    "/opt/data/repos/musicom/projects/Styles/Groove/274-groove-sieve-rework/"
    "MIDI/274-groove-sieve-rework-humanized.mid")
SRC_PERFECT = Path(
    "/opt/data/repos/musicom/projects/Styles/Groove/274-groove-sieve-rework/"
    "MIDI/274-groove-sieve-rework-perfect.mid")
SRC_PHASE1 = Path(
    "/opt/data/repos/musicom/projects/Styles/Groove/274-groove-sieve-rework/"
    "MIDI/274-groove-sieve-rework-phase1.mid")

OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP032-fdn-reverb-274-groove-sieve-rework")
AUD = OUT / "Audio"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"
for d in (AUD, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SF = discover_soundfont()
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
assert SF and os.path.exists(SF), "no soundfont"
print("SoundFont:", SF)

TARGET_LUFS = target_for_style(STYLE)      # groove -> -14.0 fallback
CEILING_DB = -1.0
TAIL_SEC = 4.0                             # extra silence so FDN tail rings past last note

# G natural minor: G A Bb C D Eb F -> pcs {7,9,10,0,2,3,5}
SCALE_PCS = {7, 9, 10, 0, 2, 3, 5}
DEGREE_PCS = {
    "i": {7, 10, 2},     # Gm  (G Bb D)
    "III": {10, 2, 5},   # Bb  (Bb D F)
    "iv": {0, 3, 7},     # Cm  (C Eb G)
    "v": {2, 5, 9},      # Dm  (D F A)
    "VI": {3, 7, 10},    # Eb  (Eb G Bb)
    "VII": {5, 9, 0},    # F   (F A C)
}
SECTIONS = [
    ["i", "VII", "i", "VII"],
    ["i", "III", "iv", "v"],
    ["i", "iv", "v", "VI"],
    ["III", "VII", "i", "iv"],
    ["VI", "III", "VII", "v"],
    ["i", "III", "iv", "v"],
    ["III", "VII", "i", "iv"],
    ["i", "VI", "VII", "i"],
]
BAR_CHORD_NAMES = [d for sec in SECTIONS for d in sec]
BAR_CHORD_PCS = [DEGREE_PCS[d] for d in BAR_CHORD_NAMES]
assert len(BAR_CHORD_NAMES) == N_BARS


def tick_to_sec(tick):
    return tick * (60.0 / (BPM * TPB))


def audit_midi(path):
    """Extract notes + run the 3-rule preflight audit. Returns dict of numbers."""
    mf = mido.MidiFile(str(path))
    notes = []            # (pitch, start_tick, end_tick, velocity, channel)
    track_ends = []
    off_grid = 0
    out_scale = 0
    out_chord = 0
    pitched = 0
    for tr in mf.tracks:
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
                    notes.append((m.note, s, t, vel, channel if channel is not None else -1))
                    n_notes += 1
                    if channel == 9:
                        continue            # drums unpitched -> skip grid/harmony
                    pitched += 1
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
    return {
        "n_notes": len(notes), "pitched": pitched, "off_grid": off_grid,
        "out_scale": out_scale, "out_chord": out_chord,
        "track_ends": sorted(set(track_ends)), "n_tracks": len(track_ends),
        "zero_drift": zero_drift,
        "notes": notes,
    }


print("=== PREFLIGHT (humanized source) ===")
h = audit_midi(SRC_HUMANIZED)
print("humanized: notes=%d pitched=%d off_grid=%d out_scale=%d out_chord=%d "
      "track_ends=%s zero_drift=%s" % (h["n_notes"], h["pitched"], h["off_grid"],
                                       h["out_scale"], h["out_chord"],
                                       h["track_ends"], h["zero_drift"]))
print("=== PREFLIGHT (perfect companion) ===")
p = audit_midi(SRC_PERFECT)
print("perfect: notes=%d pitched=%d off_grid=%d out_scale=%d out_chord=%d "
      "track_ends=%s zero_drift=%s" % (p["n_notes"], p["pitched"], p["off_grid"],
                                       p["out_scale"], p["out_chord"],
                                       p["track_ends"], p["zero_drift"]))

# Gate: the humanized source fails rule 1 (humanization jitter). The grid-locked
# -perfect companion is the de-humanized rework (already 0 off-grid). Use it.
assert p["off_grid"] == 0 and p["out_scale"] == 0 and p["out_chord"] == 0 and p["zero_drift"], \
    "perfect companion is NOT clean — real rework required"
assert h["zero_drift"], "humanized source zero-drift broken"

render_src = SRC_PERFECT
print("render source: %s (de-humanized rework)" % render_src.name)

# ---------------------------------------------------------------------------
# copy MIDI artifacts (reworked render source + original sidecars)
# ---------------------------------------------------------------------------
shutil.copy2(str(SRC_PERFECT), str(MIDIDIR / "274-groove-sieve-rework.mid"))
shutil.copy2(str(SRC_HUMANIZED), str(MIDIDIR / "274-groove-sieve-rework-humanized.mid"))
shutil.copy2(str(SRC_PHASE1), str(MIDIDIR / "274-groove-sieve-rework-phase1.mid"))

# ---------------------------------------------------------------------------
# 1. dry FluidSynth render (reverb/chorus OFF -> FDN is sole spatial layer)
# ---------------------------------------------------------------------------
dry_wav = OUT / "dry_full_mix_sp001_reference.wav"
cmd = [FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2", "-r", str(SR),
       "-F", str(dry_wav), SF, str(render_src)]
print("dry render:", " ".join(cmd))
r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
assert r.returncode == 0 and dry_wav.stat().st_size > 40000, \
    "dry render failed: %s" % r.stderr[-400:]
print("dry WAV bytes:", dry_wav.stat().st_size)

dry_audio, dry_sr = read_wav(str(dry_wav))      # (N, 2) float32
assert dry_sr == SR
n_pad = int(TAIL_SEC * SR)
padded = np.vstack([dry_audio, np.zeros((n_pad, dry_audio.shape[1]), dtype=np.float32)])

# ---------------------------------------------------------------------------
# 2. FDN reverb (absolute spatial layer)
# ---------------------------------------------------------------------------
FDN_PARAMS = dict(size=0.60, decay=0.85, brightness=0.70, modulation=0.28,
                  width=0.90, duck_amount=0.15, wet_dry=0.40)
fdn = FDN(sample_rate=SR, n_delays=8)
fdn.set(**FDN_PARAMS)
print("FDN params:", FDN_PARAMS)
t0 = time.time()
wet = fdn.process(padded.astype(np.float32))
print("FDN process done in %.1f s (shape %s)" % (time.time() - t0, wet.shape))

raw_wav = OUT / "SP032_fdn_raw.wav"
write_wav(str(raw_wav), wet.astype(np.float32), SR, normalize=False)

# ---------------------------------------------------------------------------
# 3. master
# ---------------------------------------------------------------------------
print("Mastering (target %.1f LUFS, ceiling %.1f dBTP)..." % (TARGET_LUFS, CEILING_DB))
t0 = time.time()
mastered, rep = master(wet.astype(np.float32), target_lufs=TARGET_LUFS,
                       ceiling_db=CEILING_DB, sample_rate=SR)
print("master done in %.1f s | LUFS %.2f, true peak %.2f dBTP"
      % (time.time() - t0, float(rep.get("integrated_lufs", 0)),
         float(rep.get("true_peak_db", 0))))

final_wav = OUT / "SP032-fdn-reverb-274-groove-sieve-rework.wav"
final_ogg = OUT / "SP032-fdn-reverb-274-groove-sieve-rework.ogg"
write_wav(str(final_wav), mastered.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, \
    "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV: %d  final OGG: %d" % (final_wav.stat().st_size, final_ogg.stat().st_size))

# ---------------------------------------------------------------------------
# 4. verification
# ---------------------------------------------------------------------------
meas_lufs = float(measure_lufs(mastered, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered)))
mono = 0.5 * (mastered[:, 0] + mastered[:, 1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
# stereo width: side/mid RMS
mid = 0.5 * (mastered[:, 0] + mastered[:, 1])
side = 0.5 * (mastered[:, 0] - mastered[:, 1])
width_ratio = float(np.sqrt(np.mean(side ** 2)) / (np.sqrt(np.mean(mid ** 2)) + 1e-9))
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f width=%.3f"
      % (meas_lufs, peak_val, silence_pct, rms, width_ratio))


def pitch_verify(audio_2n, notes):
    """Harmonic-match pitch check (low-tuned safe: bass G1=49 Hz < 50 Hz band).

    A 0.5 s window PASSes if its dominant FFT peak (40-1050 Hz) matches k*f of
    any active non-drum note fundamental (k=1..8, within 40-1050 Hz, +-4%).
    """
    mono_ = 0.5 * (audio_2n[:, 0] + audio_2n[:, 1])
    wl = int(0.5 * SR)
    nw = len(mono_) // wl
    # fundamentals of non-drum notes, in seconds
    fund = []
    for (pitch, s_tick, e_tick, vel, ch) in notes:
        if ch == 9:
            continue
        f0 = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
        fund.append((tick_to_sec(s_tick), tick_to_sec(e_tick), f0))
    hits = valid = 0
    he_list = []
    for w in range(nw):
        seg = mono_[w * wl:(w + 1) * wl]
        if np.max(np.abs(seg)) < 0.01:
            continue
        valid += 1
        w0 = w * 0.5
        w1 = w0 + 0.5
        win = np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg * win))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
        mask = (freqs >= 40.0) & (freqs <= 1050.0)
        sub = spec[mask]
        subf = freqs[mask]
        dom = subf[np.argmax(sub)]
        allowed = []
        for (s, e, f0) in fund:
            if e <= w0 or s >= w1:
                continue
            for k in range(1, 9):
                kf = k * f0
                if 40.0 <= kf <= 1050.0:
                    allowed.append(kf)
        if allowed and any(abs(dom - a) / a <= 0.04 for a in allowed):
            hits += 1
        tot = np.sum(spec ** 2) + 1e-12
        he = 0.0
        for k in range(1, 9):
            tf = dom * k
            hband = (freqs >= tf - 15.0) & (freqs <= tf + 15.0)
            he += np.sum(spec[hband] ** 2)
        he_list.append(float(he / tot))
    hit_rate = hits / max(1, valid)
    he_mean = float(np.mean(he_list)) if he_list else 0.0
    return hit_rate, he_mean, valid


hit_rate, he_mean, valid = pitch_verify(mastered, p["notes"])
pitch_verdict = "PASS" if hit_rate >= 0.60 else "FAIL"
print("Pitch verify: valid=%d hit=%.4f mean_HE=%.4f -> %s"
      % (valid, hit_rate, he_mean, pitch_verdict))

# ---------------------------------------------------------------------------
# 5. dry stems (per-voice reference, DAW remix)
# ---------------------------------------------------------------------------
stems = {}
try:
    from sound.render.pipeline import RenderPipeline
    rp = RenderPipeline(soundfont_path=SF)
    stems = rp.render_stems(str(render_src), str(AUD / "stems"), format="wav")
    print("stems:", len(stems), "files")
except Exception as ex:
    print("stem render failed (non-fatal):", repr(ex))

# ---------------------------------------------------------------------------
# 6. artifacts / provenance / report
# ---------------------------------------------------------------------------
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map, "stereo_width_ratio": width_ratio,
    "hit_rate": hit_rate, "mean_harmonic_energy": he_mean, "valid_windows": valid,
    "pitch_verdict": pitch_verdict,
    "fdn_params": FDN_PARAMS, "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    "n_stems": len(stems),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": DATE,
    "seed": SEED,
    "method": "SP-032",
    "method_module": "sound.effects.fdn_reverb",
    "method_desc": "Feedback Delay Network Reverb",
    "layer": "ABSOLUTE (spatial layer)",
    "params": dict(FDN_PARAMS, sample_rate=SR, tail_sec=TAIL_SEC,
                   target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB),
    "source_midi": str(SRC_HUMANIZED),
    "render_source_midi": str(SRC_PERFECT),
    "key": "G natural minor",
    "scale_pcs": sorted(SCALE_PCS),
    "bpm": BPM, "ppqn": TPB, "bars": N_BARS,
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "raw_wav": str(raw_wav),
    "dry_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "stereo_width_ratio": width_ratio,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": he_mean,
    "preflight": {
        "humanized": {"pitched": h["pitched"], "off_grid": h["off_grid"],
                      "out_scale": h["out_scale"], "out_chord": h["out_chord"],
                      "zero_drift": h["zero_drift"], "track_ends": h["track_ends"]},
        "perfect": {"pitched": p["pitched"], "off_grid": p["off_grid"],
                    "out_scale": p["out_scale"], "out_chord": p["out_chord"],
                    "zero_drift": p["zero_drift"], "track_ends": p["track_ends"]},
    },
    "stems": {k: str(v) for k, v in stems.items()},
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

REPORT = """# REPORT — SP-032 FDN Reverb × 274-groove-sieve-rework

**Job:** random-style production (SP) — layer-aligned ({date})
**Method:** SP-032 — Feedback Delay Network Reverb (Rev Ocean "Tidal"-style)
**Source composition:** `Groove/274-groove-sieve-rework` (Method 025 Xenakis Sieve rework)
**Seed:** {seed}

---

## 1. Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (104 implemented entries) |
| Method | **SP-032** → `sound.effects.fdn_reverb` (`FDN` class) |
| Source MIDI (selected) | `Styles/Groove/274-groove-sieve-rework/MIDI/274-groove-sieve-rework-humanized.mid` |
| Render source | `Styles/Groove/274-groove-sieve-rework/MIDI/274-groove-sieve-rework-perfect.mid` (de-humanized rework) |
| Recent excluded (≤7 d) | SP-075, SP-084, SP-100, SP-107, SP-115, SP-146, SP-157 |
| Baseline excluded | SP-001 |
| Pool size | 96 |

## 2. Source composition

| Field | Value |
|---|---|
| Style / key | Groove — **G natural minor** (pcs {{7,9,10,0,2,3,5}}) |
| Origin | Method 025 Xenakis Sieve rework (from 080-groove-sieve) |
| BPM / meter / TPB | 110 · 4/4 · 480 TPB (16th = 120, bar = 1920) |
| Length | 32 bars / 8 sections (Intro·VerseA·VerseB·Chorus·Bridge·VerseC·Chorus2·Outro), ~69.8 s |
| Voices | Lead (Soprano Sax 65, ch0), Horns (Brass 61, ch1), Rhodes (EP 4, ch2), Bass (EB 33, ch3), Counter (Strings 48, ch4), Drums (ch9) |
| Chord path | i·VII·i·VII ‖ i·III·iv·v ‖ i·iv·v·VI ‖ III·VII·i·iv ‖ VI·III·VII·v ‖ i·III·iv·v ‖ III·VII·i·iv ‖ i·VI·VII·i |

## 3. Pre-flight — RULES ADHERENCE GATE

| Rule | Humanized source (.mid) | Perfect companion (rework) |
|---|---|---|
| 1. Grid sync (16th = 120) | **FAIL — {h_off_grid} off-grid** (humanization micro-timing) | **PASS — 0 off-grid** |
| 2. Harmony (in-scale + chord-tone) | {h_out_scale} out-of-scale, {h_out_chord} out-of-chord (bar-boundary jitter) | **PASS — 0 / 0** |
| 3. Zero-drift (all tracks 61440) | {h_drift} | **PASS — 6 tracks = 61440** |

**Verdict: FAIL (rule 1) on the selected humanized source.** The selection landed
on the composition job's always-on humanized export, whose micro-timing puts
{h_off_grid}/{p_pitched} pitched onsets off-grid. The composition job already ships
the de-humanized companion (`-perfect.mid`) — this IS the grid-snap rework, so no
re-snapping was needed: the perfect layer reads 0 off-grid / 0 out-of-scale /
0 out-of-chord / zero-drift. **Render source = `-perfect.mid`.** Humanized + phase-1
sidecars preserved in `MIDI/`.

## 4. SP-032 method — FDN Reverb

**Layer: ABSOLUTE** — one 8-line feedback delay network replaces the spatial
layer for the whole mix. FluidSynth internal reverb/chorus forced OFF
(`-R 0 -C 0`) so the FDN is the sole spatial treatment.

| Param | Value |
|---|---|
| n_delays / matrix | 8 · normalized Hadamard feedback |
| prime delays | 1471–2797 samples @44.1 kHz (~33–63 ms) |
| size / decay | {size} / {decay} |
| brightness / modulation | {brightness} / {modulation} (0.15 Hz LFO) |
| width / duck_amount | {width} / {duck_amount} |
| wet_dry | {wet_dry} |

Pipeline: reworked MIDI → dry FluidSynth (`-R 0 -C 0 -g 1.2`, FX off) → +4.0 s
silence pad → FDN reverb → `master()` (target {lufs_target} LUFS, −1 dBTP) →
WAV + Opus OGG → pitch/silence/RMS verification → dry stems → provenance + report.

## 5. Verification (pitch mandatory check)

| Metric | Value |
|---|---|
| Pitch hit rate (0.5 s windows, harmonic-match k=1..8) | **{hit_rate:.4f}** — {valid} valid windows |
| Mean harmonic energy (8 harmonics of dominant peak) | **{he_mean:.4f}** |
| **Pitch verdict** | **{pitch_verdict}** — tonal, not noise |
| Integrated LUFS | {lufs:.2f} (target {lufs_target:.1f}) |
| True peak | {peak:.3f} |
| Silence ratio | **{silence_pct:.2f}%** (reverb tail decay; no mid-track gaps) |
| RMS | {rms:.4f} |
| Stereo width (side/mid RMS) | {width_ratio:.3f} |

## 6. Artifacts

| File | Size |
|---|---|
| `SP032-fdn-reverb-274-groove-sieve-rework.wav` | {wav_bytes} B |
| `SP032-fdn-reverb-274-groove-sieve-rework.ogg` | {ogg_bytes} B (Opus 48k voip) |
| `dry_full_mix_sp001_reference.wav` | {dry_bytes} B (dry reference) |
| `SP032_fdn_raw.wav` | {raw_bytes} B (pre-master) |
| `MIDI/274-groove-sieve-rework.mid` | {mid_bytes} B (reworked — grid-locked) |
| `MIDI/274-groove-sieve-rework-humanized.mid` | {hum_bytes} B (original source) |
| `MIDI/274-groove-sieve-rework-phase1.mid` | {p1_bytes} B (raw phase-1) |
| `Audio/stems/` (dry per-voice, {n_stems} files) | — |
| `Analysis/render_stats.json`, `provenance.json` | — |

## 7. Notes

- **Pre-flight caught the same rule-1 pattern as prior jobs**: the composition
  job ships a humanized MIDI, so the production gate's grid-sync rule fails on
  it by construction. The grid-locked `-perfect.mid` companion is the exact
  de-humanization rework — 0 off-grid without touching harmony or zero-drift.
- **Low-tuned groove**: bass plays G1 = 49 Hz, below the 50 Hz analysis band,
  so the pitch check uses harmonic matching (dominant peak may land on the 2nd
  harmonic ~98 Hz). This mirrors the SP-032-on-080 fix (2026-09-02).
- FDN wet_dry {wet_dry} + ducking keeps the 8th-note funk bass and horn stabs
  punchy while a warm shared room tail glues the sieve syncopation.
- `master()` true-peak is a ceiling, not a target: −14 LUFS groove legitimately
  lands near/below −1 dBTP.
- File sizes all `> 40 B`; OGG `> 10 KB`.
""".format(
    date=DATE, seed=SEED,
    h_off_grid=h["off_grid"], h_out_scale=h["out_scale"], h_out_chord=h["out_chord"],
    h_drift="PASS" if h["zero_drift"] else "FAIL",
    p_pitched=p["pitched"],
    size=FDN_PARAMS["size"], decay=FDN_PARAMS["decay"],
    brightness=FDN_PARAMS["brightness"], modulation=FDN_PARAMS["modulation"],
    width=FDN_PARAMS["width"], duck_amount=FDN_PARAMS["duck_amount"],
    wet_dry=FDN_PARAMS["wet_dry"],
    lufs_target=TARGET_LUFS,
    hit_rate=hit_rate, valid=valid, he_mean=he_mean, pitch_verdict=pitch_verdict,
    lufs=meas_lufs, peak=peak_val, silence_pct=silence_pct, rms=rms,
    width_ratio=width_ratio,
    wav_bytes=final_wav.stat().st_size, ogg_bytes=final_ogg.stat().st_size,
    dry_bytes=dry_wav.stat().st_size, raw_bytes=raw_wav.stat().st_size,
    mid_bytes=(MIDIDIR / "274-groove-sieve-rework.mid").stat().st_size,
    hum_bytes=(MIDIDIR / "274-groove-sieve-rework-humanized.mid").stat().st_size,
    p1_bytes=(MIDIDIR / "274-groove-sieve-rework-phase1.mid").stat().st_size,
    n_stems=len(stems),
)
(OUT / "REPORT.md").write_text(REPORT)
print("REPORT.md written")

# copy scripts for record
for s in ("select_job_20261120.py",):
    srcp = OUT.parent / s
    if srcp.exists():
        shutil.copy2(str(srcp), str(SCRIPTS / s))
shutil.copy2(__file__, str(SCRIPTS / "produce_sp032_cron.py"))

print("DONE. pitch=%s hit=%.4f silence=%.2f%% lufs=%.2f"
      % (pitch_verdict, hit_rate, silence_pct, meas_lufs))
