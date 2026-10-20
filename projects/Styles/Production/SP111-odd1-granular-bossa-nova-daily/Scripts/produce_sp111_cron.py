# -*- coding: utf-8 -*-
"""SP-111 Odd1 Microsonic granular production pass (absolute layer).

Source : Styles/Latin/bossa-nova-daily-2026-06-15/composition.mid (A minor,
         84 BPM, 2 bars, Am7 harmony: bass A1 + Am7 guitar clave + shaker/rim).
         Zero-drift normalized copy lives in MIDI/composition.mid (all note
         tracks padded to 3840 ticks — see rework_zerodrift_20261020.py).
Method : SP-111 -> sound.synthesis.odd1_engine (Odd1Microsonic).
         ABSOLUTE layer: the WHOLE dry mix is fed as the granular source
         buffer; 2 layers x 4 playheads re-granulate it (forward time path,
         octave shimmer/sub layers, per-grain one-pole filter, varied grain
         sizes).  Two independent seeds -> L/R for natural stereo decorrelation.
Pipeline:
  dry FluidSynth render (FX off) -> Odd1Microsonic.render (whole mix, mono L/R)
  -> master() (LUFS target, -1 dBTP) -> WAV + Opus OGG
  (+ dry per-track stems via RenderPipeline as DAW import artifacts)
"""
import json
import math
import os
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.synthesis.odd1_engine import Odd1Microsonic
from sound.effects.mastering import master, target_for_style, measure_lufs

SRC = Path("/opt/data/repos/musicom/projects/Styles/Latin/bossa-nova-daily-2026-06-15/composition.mid")
NORM = Path("/opt/data/repos/musicom/projects/Styles/Production/SP111-odd1-granular-bossa-nova-daily/MIDI/composition.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP111-odd1-granular-bossa-nova-daily")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 84.0
SEED = 20261020
STYLE = "bossa nova"
TARGET_LUFS = target_for_style(STYLE)   # -14.0
CEILING_DB = -1.0

SRC_PCS = {0, 4, 7, 9}   # A C E G (Am7, non-drum)

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# ---------- 0. copy source MIDI next to the normalized one (for reference) ----
shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))

# ---------- helpers ----------
def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if nch == 1:
            audio = np.vstack([samples, samples])
        else:
            audio = samples.reshape(-1, nch).T
        return audio, sr

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

# ---------- 1. dry full mix (SP-001 reference, FX off) ----------
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix (FluidSynth, FX off)...")
cmd_dry = [FLUID, "-ni", "-g", "1.2", "-R", "0", "-C", "0",
           "-F", str(dry_full), SF, str(NORM)]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr[-500:]}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# ---------- 2. dry stems (DAW import artifacts) ----------
print("Rendering dry stems with RenderPipeline...")
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(NORM), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} stems: {list(stems_raw.keys())}")

# ---------- 3. SP-111 granular (absolute layer on whole mix) ----------
dry_audio, sr = read_wav(dry_full)          # (2, N)
# Trim the FluidSynth release tail: music = 8 beats @ 84 BPM = 5.71 s + ~0.5 s
# natural ring.  The raw render extends to ~8.8 s (low piano note release);
# the per-second RMS map shows sec 6+ is digital silence (tail-only, no gaps).
TRIM_SEC = 6.2
N_trim = int(TRIM_SEC * SR)
dry_audio = dry_audio[:, :N_trim]
write_wav(dry_full, dry_audio, sr=SR)       # trimmed dry reference
mono = (0.5 * (dry_audio[0] + dry_audio[1])).astype(np.float64)
N = len(mono)
print(f"Dry mix (trimmed to {TRIM_SEC}s): {dry_audio.shape}, mono source N={N}, dur={N/sr:.2f}s")

# per-head grain advance (hop) for 1:1 forward read speed
SPACING_MS = 40.0
HOP = int(SR * SPACING_MS / 1000.0)          # 1764 samples = 40 ms
print(f"HOP = {HOP} samples (spacing {SPACING_MS} ms)")

# playhead config: (layer, head, pitch_st, grain_size_ms, filter_cutoff)
# pitch_st in SEMITONES; engine quirk: ratio=2^(pitch_st/12), and the grain
# read uses src=arange(gsz)/ratio, so POSITIVE pitch_st => source reads slower
# => pitch DOWN an octave.  We keep shifts in {0, +/-12} so pitch CLASS is
# preserved (octave only) -> pitch verification unaffected.
HEADS = [
    (0, 0, 0,    80.0, 1.0),
    (0, 1, 0,    80.0, 0.7),
    (0, 2, -12,  50.0, 0.6),   # octave-up shimmer
    (0, 3, +12, 100.0, 0.4),   # octave-down sub layer
    (1, 0, 0,    40.0, 0.8),
    (1, 1, 0,   120.0, 0.5),
    (1, 2, -12,  60.0, 0.55),
    (1, 3, +12,  90.0, 0.4),
]

def build_engine(seed):
    om = Odd1Microsonic(SR, seed=seed)
    for l, h, pst, gms, fco in HEADS:
        om.set_playhead(l, h, pitch_st=pst, speed=HOP,
                        grain_size_ms=gms, grain_spacing_ms=SPACING_MS,
                        filter_cutoff=fco, direction=1)
    return om

print("Granular render (L and R via two seeds)...")
eng_L = build_engine(SEED)
eng_R = build_engine(SEED + 1)
L = eng_L.render(mono, mode="synth", time_path="forward", n_out=N)
R = eng_R.render(mono, mode="synth", time_path="forward", n_out=N)
L = L[:N].astype(np.float32)
R = R[:N].astype(np.float32)
wet = np.vstack([L, R])                       # (2, N)
print(f"Wet granular: shape {wet.shape}, peak={np.max(np.abs(wet)):.3f}")

# ---------- 4. master ----------
wet_tm = wet.T.astype(np.float32)             # (N, 2)
print(f"Mastering (target {TARGET_LUFS} LUFS, ceiling {CEILING_DB} dBTP)...")
mastered_tm, rep = master(wet_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report:", round(float(rep.get("integrated_lufs", 0)), 2), "LUFS,",
      round(float(rep.get("true_peak_db", 0)), 2), "dBTP")
final_master = mastered_tm.T                   # (2, N)

final_wav = OUT / "SP111-odd1-granular-bossa-nova-daily.wav"
final_ogg = OUT / "SP111-odd1-granular-bossa-nova-daily.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# ---------- 5. verification ----------
measured_lufs = float(measure_lufs(mastered_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
rms = float(np.sqrt(np.mean(mono_mix ** 2)))
Lm = final_master[0]; Rm = final_master[1]
num = np.sum(Lm * Rm); den = math.sqrt(np.sum(Lm * Lm) * np.sum(Rm * Rm)) + 1e-12
mono_corr = float(num / den)
print(f"Master Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, "
      f"Silence={silence_ratio:.2f}%, RMS={rms:.4f}, MonoCorr={mono_corr:.3f}")

def pitch_verify(audio_2n, pcs):
    mono_ = 0.5 * (audio_2n[0] + audio_2n[1])
    window_len = int(0.5 * SR)
    num_windows = len(mono_) // window_len
    fft_hits = 0
    valid_windows = 0
    harmonic_energies = []
    for w in range(num_windows):
        seg = mono_[w * window_len:(w + 1) * window_len]
        if np.max(np.abs(seg)) < 0.01:
            continue
        valid_windows += 1
        win = np.hanning(len(seg))
        fft_spec = np.abs(np.fft.rfft(seg * win))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
        mask = (freqs >= 50.0) & (freqs <= 1000.0)
        sub_spec = fft_spec[mask]
        sub_freqs = freqs[mask]
        dom_f = sub_freqs[np.argmax(sub_spec)]
        midi_val = 69.0 + 12.0 * math.log2(max(1.0, dom_f) / 440.0)
        round_midi = round(midi_val)
        midi_diff = abs(midi_val - round_midi)
        tot_energy = np.sum(fft_spec ** 2) + 1e-12
        h_energy = 0.0
        for h in range(1, 9):
            target_f = dom_f * h
            h_mask = (freqs >= target_f - 15.0) & (freqs <= target_f + 15.0)
            h_energy += np.sum(fft_spec[h_mask] ** 2)
        harmonic_energies.append(h_energy / tot_energy)
        if midi_diff < 0.45:
            pc = round_midi % 12
            if pc in pcs:
                fft_hits += 1
    hit_rate = fft_hits / max(1, valid_windows)
    mean_he = float(np.mean(harmonic_energies)) if harmonic_energies else 0.0
    return hit_rate, mean_he, valid_windows

hit_rate, mean_he, valid_windows = pitch_verify(final_master, SRC_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio, SRC_PCS)
he_retention = (mean_he / dry_he) if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_retention >= 0.40) else "FAIL"
print(f"Pitch Verification: valid={valid_windows}, hit={hit_rate:.4f}, mean_HE_wet={mean_he:.4f}")
print(f"Dry reference: hit={dry_hit:.4f}, mean_HE_dry={dry_he:.4f}, HE_retention={he_retention:.3f}")
print(f"Pitch Verdict: {pitch_verdict}")

# ---------- 6. analysis + provenance ----------
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "rms": rms, "mono_corr": mono_corr, "valid_windows": valid_windows,
    "hit_rate": hit_rate, "mean_harmonic_energy": mean_he,
    "pitch_verdict": pitch_verdict, "dry_mean_harmonic_energy": dry_he,
    "he_retention": he_retention, "dry_hit_rate": dry_hit,
    "dry_valid_windows": dry_valid,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-20",
    "seed": SEED,
    "method": "SP-111",
    "method_module": "sound.synthesis.odd1_engine",
    "method_desc": "Multi-Playhead Microsonic Granular Engine (Oddment ODD-1-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR,
        "mode": "synth", "time_path": "forward",
        "grain_spacing_ms": SPACING_MS, "hop_samples": HOP,
        "playhead_speed": HOP,
        "heads": [{"layer": l, "head": h, "pitch_st": pst,
                   "grain_size_ms": gms, "filter_cutoff": fco}
                  for (l, h, pst, gms, fco) in HEADS],
        "stereo_seeds": [SEED, SEED + 1],
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "normalized_midi": str(NORM),
    "source_bpm": BPM,
    "source_pitch_classes": sorted(SRC_PCS),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "rms": rms, "mono_corr": mono_corr,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": mean_he,
    "dry_he_mean": dry_he, "he_retention": he_retention, "dry_hit_rate": dry_hit,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(ANALYSIS / "select_20261020.json").write_text(json.dumps({
    "date": "2026-10-20", "method": "SP-111",
    "method_module": "sound.synthesis.odd1_engine",
    "source_midi": str(SRC), "n_well_formed": 245, "registry_total": 54,
}, indent=2))

for s in ("rework_zerodrift_20261020.py", "audit_source_20261020.py"):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp111_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
