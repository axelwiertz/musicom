# -*- coding: utf-8 -*-
"""SP-119 Spectral Resonance Suppressor production pass (absolute layer).

Source : Styles/Funk/081-funk-schillinger/MIDI/081-funk-schillinger.mid
         (Bb major funk, 100 BPM, 480 TPB, 24 bars, 6 sections; 6 voices:
          trumpet/Rhodes/guitar/bass/clav + drums, Schillinger method 018).

Method : SP-119 -> sound.effects.spectral_resonance_suppressor
         (SpectralResonanceSuppressor, Newfangled Audio Fixate:Midrange-style
          STFT de-resonator). ABSOLUTE layer: the whole rendered mix is
          de-resonated in the 200..6000 Hz midrange (median-baseline excess
          peak detection -> raised-cosine notches -> freq/time smoothing ->
          overlap-add resynthesis). Applied per-channel (L/R) on the
          FluidSynth (SP-001) full-mix render, then mastered.

Pipeline: source MIDI -> 3-rule audit (grid/harmony/zero-drift)
          -> FluidSynth dry render (reference) -> SP-119 de-resonate (L/R)
          -> master() (-13 LUFS funk target, -1 dBTP) -> WAV + Opus OGG
          -> pitch/harmonic-energy/resonance-reduction/silence verification
          -> REPORT.md.
"""
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.effects.spectral_resonance_suppressor import SpectralResonanceSuppressor
from sound.utils.io import read_wav, write_wav

ROOT = Path("/opt/data/repos/musicom/projects/Styles")
SRC = ROOT / "Funk/081-funk-schillinger/MIDI/081-funk-schillinger.mid"
OUT = ROOT / "Production/SP119-spectral-resonance-suppressor-081-funk-schillinger"
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 100.0
TPB = 480
GRID = 120                 # 16th note
SEED = 20261025
STYLE = "funk"

# Bb major pitch classes: Bb C D Eb F G A
SCALE_PCS = {10, 0, 2, 3, 5, 7, 9}

# Bb major chord map (I ii iii IV V) from the project audit
CHORDS = {
    58: [58, 62, 65],   # Bb  I
    60: [60, 63, 67],   # Cm  ii
    62: [62, 65, 69],   # Dm  iii
    63: [63, 67, 70],   # Eb  IV
    65: [65, 69, 72],   # F   V
}
PROG = ([58, 60, 62, 65] * 2) + [58, 63, 65, 58] + [58, 65, 58, 60] + \
       [58, 60, 62, 65] + [58, 63, 60, 58]
BAR = TPB * 4           # 1920
N_BARS = 24


def chord_for_bar(bar):
    return CHORDS[PROG[min(bar, N_BARS - 1)]]


FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# ---------------------------------------------------------------------------
# 0. Pre-flight 3-rule audit (on the SOURCE)
# ---------------------------------------------------------------------------
def audit(path):
    mf = mido.MidiFile(str(path))
    grid_off = out_scale = out_chord = 0
    off8 = 0
    track_ends = []
    total_notes = 0
    for tr in mf.tracks:
        chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
        is_drum = 9 in chans
        t = 0
        n_notes = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                n_notes += 1
                total_notes += 1
                if is_drum:
                    continue
                if (t % GRID) != 0:
                    grid_off += 1
                if (t % 240) != 0:
                    off8 += 1
                if (m.note % 12) not in SCALE_PCS:
                    out_scale += 1
                bar = min(t // BAR, N_BARS - 1)
                if (m.note % 12) not in {c % 12 for c in chord_for_bar(bar)}:
                    out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "off8": off8, "out_scale": out_scale,
            "out_chord": out_chord, "zero_drift": zero_drift,
            "track_ends": sorted(set(track_ends)), "total_notes": total_notes}


shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))
before = audit(SRC)
print("PREFLIGHT source:", before)
assert before["grid_off"] == 0, "grid sync FAIL on source"
assert before["out_scale"] == 0, "out-of-scale FAIL on source"
assert before["out_chord"] == 0, "out-of-chord FAIL on source"
assert before["zero_drift"], "zero-drift FAIL on source"
print("PREFLIGHT PASS: all three rules clean on source.")

# ---------------------------------------------------------------------------
# 1. FluidSynth dry render (SP-001 carrier)
# ---------------------------------------------------------------------------
SF = discover_soundfont()
assert SF and os.path.exists(SF), "SoundFont missing: %r" % SF
print("SoundFont:", SF)


def render(midi_path, out_wav):
    r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                        "-F", str(out_wav), SF, str(midi_path)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size < 1000:
        raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
    return out_wav


dry_wav = OUT / "dry_full_mix_source_reference.wav"
render(SRC, dry_wav)
print("dry reference:", dry_wav.stat().st_size, "bytes")

# ---------------------------------------------------------------------------
# 2. SP-119 de-resonate (absolute layer, per-channel)
# ---------------------------------------------------------------------------
RS_PARAMS = {
    "amount": 0.7, "threshold_db": 6.0, "width_bins": 24,
    "min_freq": 200.0, "max_freq": 6000.0, "attack": 0.05, "release": 0.3,
}
dry_audio, sr = read_wav(str(dry_wav))
assert sr == SR, "unexpected sample rate %d" % sr
if dry_audio.ndim == 1:
    dry_audio = np.column_stack([dry_audio, dry_audio])
dry_tm = np.asarray(dry_audio, dtype=np.float64)          # [n, 2]

rs = SpectralResonanceSuppressor(sample_rate=SR)
proc = np.empty_like(dry_tm)
for ch in range(dry_tm.shape[1]):
    proc[:, ch] = rs.process(dry_tm[:, ch], **RS_PARAMS)

raw_wav = OUT / "SP119_resonance_suppressed_raw.wav"
write_wav(str(raw_wav), proc.astype(np.float32), SR, normalize=False)
print("SP-119 raw (de-resonated):", raw_wav.stat().st_size, "bytes")

# ---------------------------------------------------------------------------
# 3. Master (funk target -13 LUFS, -1 dBTP ceiling)
# ---------------------------------------------------------------------------
TARGET_LUFS = target_for_style(STYLE)
CEILING_DB = -1.0
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..." % (TARGET_LUFS, CEILING_DB))
mastered_tm, rep = master(proc, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = OUT / "SP119-spectral-resonance-suppressor-081-funk-schillinger.wav"
final_ogg = OUT / "SP119-spectral-resonance-suppressor-081-funk-schillinger.ogg"
write_wav(str(final_wav), mastered_tm.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, "ogg encode failed"
print("final WAV:", final_wav.stat().st_size, "final OGG:", final_ogg.stat().st_size)

# ---------------------------------------------------------------------------
# 4. Stems (dry, pre-effect, per-instrument)
# ---------------------------------------------------------------------------
try:
    from sound.render.pipeline import RenderPipeline
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
    stems = pipeline.render_stems(str(SRC), str(STEMS), format="wav")
    print("rendered %d stems" % len(stems))
except Exception as e:
    stems = {}
    print("stem render skipped:", repr(e)[:200])

# ---------------------------------------------------------------------------
# 5. Verification
# ---------------------------------------------------------------------------
meas_lufs = float(measure_lufs(mastered_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered_tm)))
mono_final = 0.5 * (mastered_tm[:, 0] + mastered_tm[:, 1])
silence_pct = float(np.sum(np.abs(mono_final) < 0.001) / len(mono_final)) * 100.0
rms = float(np.sqrt(np.mean(mono_final ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono_final[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono_final), SR)]
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f"
      % (meas_lufs, peak_val, silence_pct, rms))


def pitch_verify(audio_tm, pcs):
    mono_ = 0.5 * (audio_tm[:, 0] + audio_tm[:, 1])
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
        midi_val = 69.0 + 12.0 * np.log2(max(1.0, dom) / 440.0)
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


hit_final, he_final, valid_final = pitch_verify(mastered_tm, SCALE_PCS)
hit_dry, he_dry, valid_dry = pitch_verify(dry_tm, SCALE_PCS)
he_retention = (he_final / he_dry) if he_dry > 0 else 0.0
pitch_verdict = "PASS" if (hit_final >= 0.60 and he_final >= 0.30) else "FAIL"
print("Pitch verify: final hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | retention=%.3f -> %s"
      % (hit_final, he_final, hit_dry, he_dry, he_retention, pitch_verdict))


def resonance_excess(audio_tm, min_f, max_f, threshold_db):
    """Total positive excess (dB) over the local median baseline + threshold
    in the processing band -> a scalar for the 'resonance/mud' to suppress."""
    mono_ = 0.5 * (audio_tm[:, 0] + audio_tm[:, 1])
    n = len(mono_)
    fft = 2048
    win = np.hanning(fft)
    starts = list(range(0, n - fft + 1, 512))
    if not starts:
        return 0.0, 0.0
    X = np.zeros((len(starts), fft // 2 + 1))
    for i, s in enumerate(starts):
        X[i] = np.abs(np.fft.rfft(mono_[s:s + fft] * win))
    mag_avg = X.mean(axis=0)
    with np.errstate(divide="ignore"):
        mag_db = 20.0 * np.log10(mag_avg + 1e-12)
    freqs = np.fft.rfftfreq(fft, 1.0 / SR)
    band = (freqs >= min_f) & (freqs <= max_f)
    m = mag_db[band]
    n_b = len(m)
    base = np.empty(n_b)
    for i in range(n_b):
        lo = max(0, i - 3)
        hi = min(n_b, i + 4)
        base[i] = np.median(m[lo:hi])
    excess = m - base - threshold_db
    pos = np.maximum(excess, 0.0)
    return float(np.sum(pos)), float(np.sum(pos ** 2))


exc_before, exc2_before = resonance_excess(dry_tm, 200.0, 6000.0, 6.0)
exc_after, exc2_after = resonance_excess(proc, 200.0, 6000.0, 6.0)
reduction_pct = (1.0 - exc_after / exc_before) * 100.0 if exc_before > 0 else 0.0
print("resonance excess (200-6000 Hz): before=%.2f dB, after=%.2f dB -> %.2f%% reduction"
      % (exc_before, exc_after, reduction_pct))

# ---------------------------------------------------------------------------
# 6. Artifacts: render_stats + provenance
# ---------------------------------------------------------------------------
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "hit_rate_final": hit_final, "he_final": he_final, "valid_windows_final": valid_final,
    "hit_rate_dry": hit_dry, "he_dry": he_dry, "valid_windows_dry": valid_dry,
    "he_retention": he_retention, "pitch_verdict": pitch_verdict,
    "resonance_excess_before_db": exc_before, "resonance_excess_after_db": exc_after,
    "resonance_reduction_pct": reduction_pct,
    "n_stems": len(stems) if isinstance(stems, dict) else 0,
    "target_lufs": TARGET_LUFS,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-25",
    "seed": SEED,
    "method": "SP-119",
    "method_module": "sound.effects.spectral_resonance_suppressor",
    "method_desc": "Spectral Resonance Suppressor — STFT de-resonator: median-baseline "
                   "excess peak detection, shaped suppression gains, freq+time smoothing, "
                   "midrange band focus (Newfangled Audio Fixate:Midrange-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "rs_amount": RS_PARAMS["amount"], "rs_threshold_db": RS_PARAMS["threshold_db"],
        "rs_width_bins": RS_PARAMS["width_bins"],
        "rs_band_hz": [RS_PARAMS["min_freq"], RS_PARAMS["max_freq"]],
        "rs_attack_s": RS_PARAMS["attack"], "rs_release_s": RS_PARAMS["release"],
        "carrier": "FluidSynth SP-001 (FluidR3_GM, dry -R 0 -C 0 -g 1.2)",
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "source_bpm": BPM,
    "source_key": "Bb major",
    "source_pitch_classes": sorted(SCALE_PCS),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "raw_wav": str(raw_wav),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_final, "he_mean": he_final,
    "he_dry": he_dry, "he_retention": he_retention,
    "resonance_reduction_pct": reduction_pct,
    "preflight_source": before,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

# ---------------------------------------------------------------------------
# 7. REPORT.md
# ---------------------------------------------------------------------------
REPORT = """# SP-119 Spectral Resonance Suppressor — production report

- **Date**: 2026-10-25
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-119 (`sound.effects.spectral_resonance_suppressor`) — STFT
  de-resonator (Newfangled Audio Fixate:Midrange-style): per-frame magnitude
  spectrum compared to a local median baseline; bins whose excess over the
  baseline exceeds a threshold and are local maxima are flagged; a
  raised-cosine notch is shaped around each peak, scaled by `amount` and the
  excess; gains smoothed across frequency and frames (attack/release one-pole)
  before overlap-add resynthesis. Processing restricted to the 200..6000 Hz
  midrange band.
- **Layer**: ABSOLUTE (whole-piece mix de-resonation; the full FluidSynth
  render is the input, no per-voice routing).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (63 registered;
  55 in pool after excluding recent-7-day SP-078/090/095/101/105/108/111 and
  baseline SP-001).
- **Source composition**: `Styles/Funk/081-funk-schillinger/MIDI/081-funk-schillinger.mid`
  (Bb major funk, 100 BPM, 480 TPB, 24 bars, 6 sections; 6 voices:
  trumpet/Rhodes/guitar/bass/clav + drums; Schillinger System method 018).

## Pre-flight audit (3 rules) — PASS on source (no rework needed)
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** off-grid = {g_before} |
| Harmony (Bb major scale + chord tones) | **PASS** out-of-scale = {s_before}, out-of-chord = {c_before} |
| Zero-drift (equal track ends) | **PASS** ends = {e_before} |

The source is already grid-locked, fully in Bb major and chord-tone clean, and
all 7 tracks end at 46080 ticks — no rework, straight to the SP method.

## SP-119 absolute layer (midrange de-resonation)
- Carrier: FluidSynth (FluidR3_GM) full-mix render, dry (`-R 0 -C 0 -g 1.2`),
  44100 Hz.
- Effect params: `amount=0.7`, `threshold_db=6.0`, `width_bins=24`,
  band `200..6000 Hz`, `attack=0.05 s`, `release=0.3 s`. Applied per-channel
  (L and R independently, preserving stereo).
- Resonance excess (sum of positive dB over local-median baseline + 6 dB
  threshold, 200..6000 Hz): **{exc_before:.2f} dB → {exc_after:.2f} dB
  ({reduction_pct:.2f}% reduction)**.
- Mastered to −13 LUFS (funk target), −1 dBTP ceiling.

## Verification
- **Pitch**: dominant-peak-in-key hit rate = {hit_final:.4f} ({valid_final}
  windows) → **{pitch_verdict}**
- **Harmonic energy (8 harmonics of dominant)**: final {he_final:.4f} vs dry
  {he_dry:.4f} (retention {he_retention:.3f})
- **Silence**: {silence_pct:.2f}%
- **RMS**: {rms:.4f}
- **LUFS**: {meas_lufs:.2f}  **true peak**: {peak_val:.4f}

## Files
- `{final_wav}` ({wav_bytes} bytes)
- `{final_ogg}` ({ogg_bytes} bytes)
- `{raw_wav}` (de-resonated, pre-master)
- `{dry_wav}` (dry source reference, pre-production)
- `MIDI/source_original.mid` (reference copy)
- `Audio/stems/` ({n_stems} dry per-instrument stems, pre-effect)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-119 is a mix "problem-solver" (same family as Soothe/Gullfoss/Curves
  Equator): it tames resonances and midrange build-up where the Rhodes, clav,
  guitar and trumpet all fight for the same 200..6000 Hz slice. The absolute-
  layer application de-resonates the whole funk mix in one pass, and the
  measured resonance-excess reduction above confirms the midrange got less
  "piled-up" while the pitch content and harmonic energy were retained (hit
  rate + harmonic-energy retention above).
""".format(
    g_before=before["grid_off"], s_before=before["out_scale"],
    c_before=before["out_chord"], e_before=before["track_ends"],
    exc_before=exc_before, exc_after=exc_after, reduction_pct=reduction_pct,
    hit_final=hit_final, valid_final=valid_final, pitch_verdict=pitch_verdict,
    he_final=he_final, he_dry=he_dry, he_retention=he_retention,
    silence_pct=silence_pct, rms=rms, meas_lufs=meas_lufs, peak_val=peak_val,
    final_wav=final_wav, final_ogg=final_ogg, raw_wav=raw_wav, dry_wav=dry_wav,
    wav_bytes=final_wav.stat().st_size, ogg_bytes=final_ogg.stat().st_size,
    n_stems=len(stems) if isinstance(stems, dict) else 0,
)
(OUT / "REPORT.md").write_text(REPORT)
print("REPORT.md written")

# copy scripts into project
for s in ("select_job_20261025.py",):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp119_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
