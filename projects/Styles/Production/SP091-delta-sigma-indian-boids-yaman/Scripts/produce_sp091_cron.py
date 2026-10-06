# -*- coding: utf-8 -*-
"""SP-091 Delta-Sigma Converter Saturation production pass on 212-indian-boids-yaman.

Source: Styles/IndianClassical/212-indian-boids-yaman/MIDI/212-indian-boids-yaman.mid
        (Indian classical Yaman raga in C = Lydian, 90 BPM, 4 tracks:
         ch0 Church Organ drone C-G, ch1 Sitar 104, ch2 Flute 74, ch9 Tabla/perc)
Method: SP-091 -> sound.effects.delta_sigma_saturator
Layer : ABSOLUTE layer - Physics-Based Delta-Sigma Converter Saturation & Circuit
        Strain (Mixland Grey Matter-style). Emulates a 1990s console DAC stage
        pushed past nominal spec: 2nd-order delta-sigma loop, thermal strain,
        slew limiting, analog reconstruction lowpass, asymmetric DAC ladder clip.
"""
import os
import shutil
import json
import subprocess
import wave
import math
from pathlib import Path
import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.delta_sigma_saturator import DeltaSigmaSaturator
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/IndianClassical/212-indian-boids-yaman/MIDI/212-indian-boids-yaman.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP091-delta-sigma-indian-boids-yaman")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 90.0
SEED = 20261006

# SP-091 parameters (absolute layer, applied to whole mix)
DRIVE_DB = 4.0
STRAIN = 0.28
MODE = "console"
MIX = 1.0

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

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
    audio = np.clip(audio, -1.0, 1.0)
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
print("Rendering dry full mix with FluidSynth...")
cmd_dry = [FLUID, "-ni", "-g", "1.2", "-R", "0", "-C", "0", "-F", str(dry_full), SF, str(SRC)]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# 2. Dry stems via RenderPipeline
print("Rendering dry stems with RenderPipeline...")
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} stems: {list(stems_raw.keys())}")

# 3. Apply SP-091 Delta-Sigma Saturation to the full mix (absolute layer)
dry_audio, sr = read_wav(dry_full)
print(f"Dry mix shape: {dry_audio.shape}, sr={sr}")

saturator = DeltaSigmaSaturator(drive_db=DRIVE_DB, strain=STRAIN, mode=MODE, mix=MIX, fs=SR)
print(f"Applying DeltaSigmaSaturator(mode={MODE}, drive_db={DRIVE_DB}, strain={STRAIN}, mix={MIX})...")
wet_audio = saturator.process(dry_audio)  # (2, N) float32
print(f"Wet mix shape: {wet_audio.shape}")

# 4. Master: normalize to -14 LUFS, then Limiter(-1 dBFS)
print("Mastering: normalize_to_lufs(-14) + Limiter(-1 dBFS)...")
wet_tm = wet_audio.T  # (N, 2) time-major
lufs_norm = normalize_to_lufs(wet_tm, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_tm = limiter.process(lufs_norm)  # (N, 2)
final_master = final_tm.T  # (2, N)

final_wav = OUT / "SP091-delta-sigma-indian-boids-yaman.wav"
final_ogg = OUT / "SP091-delta-sigma-indian-boids-yaman.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# 5. Verification
measured_lufs = measure_lufs(final_tm, sample_rate=SR)
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
mono_corr = mono_correlation(final_master)
print(f"Master Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, Silence={silence_ratio:.2f}%, MonoCorr={mono_corr:.3f}")

# Pitch verification: Yaman raga in C = Lydian, PCS {0,2,4,6,7,9,11} (F# = raised 4th)
YAMAN_C_PCS = {0, 2, 4, 6, 7, 9, 11}
window_len = int(0.5 * SR)
num_windows = len(mono_mix) // window_len
fft_hits = 0
valid_windows = 0
harmonic_energies = []
dominant_freqs = []

for w in range(num_windows):
    seg = mono_mix[w * window_len:(w + 1) * window_len]
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
        if pc in YAMAN_C_PCS:
            fft_hits += 1

hit_rate = fft_hits / max(1, valid_windows)
mean_he = float(np.mean(harmonic_energies)) if harmonic_energies else 0.0
pitch_verdict = "PASS" if hit_rate >= 0.60 and mean_he >= 0.25 else "FAIL"
print(f"Pitch Verification: valid_windows={valid_windows}, hits={fft_hits}, hit_rate={hit_rate:.4f}, mean_HE={mean_he:.4f}")
print(f"Pitch Verdict: {pitch_verdict}")

# Silence/RMS profile
rms = np.sqrt(np.mean(mono_mix ** 2))
mid_gap_ratio = silence_ratio
print(f"Overall RMS: {rms:.4f}, silence: {silence_ratio:.2f}%")

# 6. Write analysis + provenance
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr, "rms": rms,
    "valid_windows": valid_windows, "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he, "pitch_verdict": pitch_verdict,
}, indent=2))

(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-091", "project": "212-indian-boids-yaman",
    "scale": "Yaman raga (C Lydian)", "pcs": sorted(YAMAN_C_PCS),
    "status": pitch_verdict, "hit_rate": hit_rate,
    "harmonic_energy_mean": mean_he, "windows_analyzed": valid_windows,
    "median_freq_hz": float(np.median(dominant_freqs)) if dominant_freqs else 0.0,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-06",
    "seed": SEED,
    "method": "SP-091",
    "method_module": "sound.effects.delta_sigma_saturator",
    "method_desc": "Physics-Based Delta-Sigma Converter Saturation & Circuit Strain (Mixland Grey Matter-style)",
    "params": {"drive_db": DRIVE_DB, "strain": STRAIN, "mode": MODE, "mix": MIX, "fs": SR},
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": mean_he,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(json.dumps(provenance, indent=2))

# selection record
(ANALYSIS / "select_20261006.json").write_text(json.dumps({
    "date": "2026-10-06", "method": "SP-091",
    "method_module": "sound.effects.delta_sigma_saturator",
    "source_midi": str(SRC),
    "recent_excluded": ["SP021", "SP072", "SP075", "SP079", "SP080", "SP081", "SP083", "SP086"],
    "registry_total": 40,
}, indent=2))

shutil.copy2(__file__, str(SCRIPTS / "produce_sp091_cron.py"))
print("Done.")
