#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-092 Multiband Saturator production pass on HipHop/boom-bap/v1.

Source: Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid
        (Boom-bap hip-hop, 90 BPM, Em, 32 bars = 2 x 16, 4 voices:
         Drums ch9, Bass ch0 GM33, Lead ch1 GM1, Pad ch2 GM88;
         methods 011 Euclidean + 002 Markov + 026 DPSM)
Method: SP-092 -> sound.effects.multiband_saturator (Kreuzberg Oberton-style)
Layer : ABSOLUTE layer - 6-band multiband saturator replaces the
        timbre/saturation layer for the WHOLE piece. Per-band saturation
        algorithm + M/S routing, 15 selectable algorithms.
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
from sound.effects.multiband_saturator import MultibandSaturator, BandConfig
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP092-multiband-sat-hiphop-boom-bap")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 90.0
SEED = 20261008

# ---- SP-092 parameters (absolute layer) ---------------------------------
# Curated 6-band config: warm low-end, open top. Crossovers [120,400,1200,4000,10000].
BAND_CONFIGS = [
    BandConfig(frequency=60,    q=0.7, drive=0.60, mix=1.0, algo="germanium",  mode="mid"),
    BandConfig(frequency=250,   q=0.8, drive=1.10, mix=0.9, algo="tube",       mode="stereo"),
    BandConfig(frequency=700,   q=1.0, drive=1.00, mix=0.8, algo="silicon",    mode="stereo"),
    BandConfig(frequency=2000,  q=1.0, drive=0.90, mix=0.6, algo="tanh",       mode="sides"),
    BandConfig(frequency=6000,  q=1.1, drive=0.80, mix=0.5, algo="soft_clip",  mode="stereo"),
    BandConfig(frequency=12000, q=1.0, drive=0.50, mix=0.3, algo="bypass",     mode="stereo"),
]
GLOBAL_TRIM = 1.0

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# Source pitch-class vocabulary from non-drum notes (for pitch verification)
_src_pcs = set()
for _tr in mido.MidiFile(str(SRC)).tracks:
    for _m in _tr:
        if _m.type == "note_on" and _m.velocity > 0 and _m.channel != 9:
            _src_pcs.add(_m.note % 12)
SRC_PCS = sorted(_src_pcs)
print("Source PCS (non-drum):", SRC_PCS)


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
    audio = np.clip(np.asarray(audio), -1.0, 1.0)
    if audio.ndim == 1:
        nch = 1
        interleaved = audio
    elif audio.shape[0] == 2:
        nch = 2
        interleaved = audio.T.reshape(-1)
    else:
        nch = audio.shape[0]
        interleaved = audio.T.reshape(-1)
    data = (interleaved * 32767.0).astype(np.int16).tobytes()
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)


def mono_correlation(audio2n):
    L = audio2n[0]
    R = audio2n[1]
    num = np.sum(L * R)
    den = math.sqrt(np.sum(L * L) * np.sum(R * R)) + 1e-12
    return float(num / den)


# 1. Dry full mix (SP-001 reference)
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth (FX off)...")
cmd_dry = [FLUID, "-ni", "-g", "1.2", "-R", "0", "-C", "0", "-F", str(dry_full), SF, str(SRC)]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr[-500:]}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# 2. Dry stems via RenderPipeline
print("Rendering dry stems with RenderPipeline...")
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} stems: {list(stems_raw.keys())}")

# 3. Apply SP-092 Multiband Saturator to the full mix (absolute layer)
dry_audio, sr = read_wav(dry_full)      # (2, N)
print(f"Dry mix shape: {dry_audio.shape}, sr={sr}")

sat = MultibandSaturator(sample_rate=SR, band_configs=BAND_CONFIGS, global_trim=GLOBAL_TRIM)
print(sat.summary())

dry_tm = np.asarray(dry_audio).T.astype(np.float32)   # (N, 2) time-major
wet_tm = sat.process(dry_tm)                          # (N, 2)
print(f"Wet mix shape: {wet_tm.shape}")

# 4. Master: normalize to -14 LUFS, then Limiter(-1 dBFS)
print("Mastering: normalize_to_lufs(-14) + Limiter(-1 dBFS)...")
lufs_norm = normalize_to_lufs(wet_tm, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_tm = limiter.process(lufs_norm)                 # (N, 2)
final_master = final_tm.T                             # (2, N)

final_wav = OUT / "SP092-multiband-sat-hiphop-boom-bap.wav"
final_ogg = OUT / "SP092-multiband-sat-hiphop-boom-bap.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# 5. Per-stem wet copies (same band config per voice, DAW import convenience)
print("Applying same multiband config to dry stems...")
for name, path in stems_raw.items():
    s_audio, s_sr = read_wav(path)
    s_tm = np.asarray(s_audio).T.astype(np.float32)
    s_wet = sat.process(s_tm)
    out_name = name + "_MBSAT"
    write_wav(STEMS_WET / f"{out_name}.wav", s_wet.T, sr=s_sr)
print(f"Wrote {len(stems_raw)} wet stems to {STEMS_WET}")

# 6. Verification
measured_lufs = float(measure_lufs(final_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
mono_corr = mono_correlation(final_master)
print(f"Master Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, "
      f"Silence={silence_ratio:.2f}%, MonoCorr={mono_corr:.3f}")


def pitch_verify(audio_2n, pcs):
    mono = 0.5 * (audio_2n[0] + audio_2n[1])
    window_len = int(0.5 * SR)
    num_windows = len(mono) // window_len
    fft_hits = 0
    valid_windows = 0
    harmonic_energies = []
    dominant_freqs = []
    for w in range(num_windows):
        seg = mono[w * window_len:(w + 1) * window_len]
        if np.max(np.abs(seg)) < 0.01:
            continue
        valid_windows += 1
        win = np.hanning(len(seg))
        fft_spec = np.abs(np.fft.rfft(seg * win))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
        mask = (freqs >= 50.0) & (freqs <= 1000.0)
        if not np.any(mask):
            continue
        sub_spec = fft_spec[mask]
        sub_freqs = freqs[mask]
        dom_f = sub_freqs[np.argmax(sub_spec)]
        dominant_freqs.append(float(dom_f))
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
    return hit_rate, mean_he, valid_windows, dominant_freqs


hit_rate, mean_he, valid_windows, dominant_freqs = pitch_verify(final_master, SRC_PCS)
dry_hit, dry_he, dry_valid, _ = pitch_verify(dry_audio, SRC_PCS)
he_retention = (mean_he / dry_he) if dry_he > 0 else 0.0

pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_retention >= 0.50) else "FAIL"
print(f"Pitch Verification: valid={valid_windows}, hits={hit_rate:.4f}, mean_HE_wet={mean_he:.4f}")
print(f"Dry reference: hit={dry_hit:.4f}, mean_HE_dry={dry_he:.4f}, HE_retention={he_retention:.3f}")
print(f"Pitch Verdict: {pitch_verdict}")

rms = float(np.sqrt(np.mean(mono_mix ** 2)))
print(f"Overall RMS: {rms:.4f}, silence: {silence_ratio:.2f}%")

# 7. Write analysis + provenance
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr, "rms": rms,
    "valid_windows": valid_windows, "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he, "pitch_verdict": pitch_verdict,
    "dry_mean_harmonic_energy": dry_he, "he_retention": he_retention,
}, indent=2))

(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-092", "project": "HipHop/boom-bap/v1",
    "scale": "Em (source PCS, non-drum)", "pcs": SRC_PCS,
    "status": pitch_verdict, "hit_rate": hit_rate,
    "harmonic_energy_mean": mean_he, "dry_harmonic_energy_mean": dry_he,
    "he_retention": he_retention, "windows_analyzed": valid_windows,
    "median_freq_hz": float(np.median(dominant_freqs)) if dominant_freqs else 0.0,
}, indent=2))

band_summary = [
    {"band": i + 1, "freq": int(bc.frequency), "q": bc.q, "drive": bc.drive,
     "mix": bc.mix, "algo": bc.algo, "mode": bc.mode}
    for i, bc in enumerate(BAND_CONFIGS)
]

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-08",
    "seed": SEED,
    "method": "SP-092",
    "method_module": "sound.effects.multiband_saturator",
    "method_desc": "6-Band Multiband Saturator w/ 15 Selectable Algorithms & Per-Band M/S Routing (Kreuzberg Audio Oberton-style)",
    "params": {
        "band_configs": band_summary,
        "global_trim": GLOBAL_TRIM,
        "crossover_freqs": [120.0, 400.0, 1200.0, 4000.0, 10000.0],
        "fs": SR,
    },
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": mean_he,
    "dry_he_mean": dry_he, "he_retention": he_retention,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(json.dumps(provenance, indent=2))

(ANALYSIS / "select_20261008.json").write_text(json.dumps({
    "date": "2026-10-08", "method": "SP-092",
    "method_module": "sound.effects.multiband_saturator",
    "source_midi": str(SRC),
    "recent_excluded": sorted(["SP-021", "SP-069", "SP-072", "SP-080", "SP-083", "SP-086", "SP-091"]),
    "registry_total": 42,
    "n_well_formed": 219,
    "note": "first draw landed on Country/001-country-hope-loop/MIDI/country-hope-loop-v7.mid "
            "(degenerate: mido delta-time bug -> 7916 ticks/bar, 82.5s for 8-bar 96 BPM loop, "
            "no program changes) -> re-rolled to well-formed candidate",
}, indent=2))

shutil.copy2(__file__, str(SCRIPTS / "produce_sp092_cron.py"))
print("Done.")
