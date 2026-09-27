# -*- coding: utf-8 -*-
"""SP-070 Morphing Five-Character Resonant Filter — 091-baroque-genetic-allemande.

Source: Styles/Baroque/091-baroque-genetic-allemande/MIDI/091-baroque-genetic-allemande.mid
        (D aeolian, 92 BPM, 24 bars, 7 voices: violin, oboe, cello, piano
         continuo, viola, double bass, drums)
Method: SP-070 -> sound.effects.morph_filter (FusionFilter)
Layer : ABSOLUTE layer — one morphing resonant filter character applied across
        the WHOLE mix (per-track application is a later refinement).
        Five engine topologies (ladder / diode / svf / comb / scream) share one
        cutoff / resonance / drive / mix control; a continuous `position`
        crossfades (equal-power) between adjacent characters.
"""
import os
import shutil
import json
import subprocess
import wave
import math
import time
from pathlib import Path
import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.morph_filter import FusionFilter, CHARACTERS
from sound.effects.reverb import AlgorithmicReverb
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Baroque/091-baroque-genetic-allemande/MIDI/091-baroque-genetic-allemande.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP070-morph-filter-baroque-genetic-allemande")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 92.0
SEED = 20260927

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# 1. Render Dry Full Mix (SP-001 reference)
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth...")
cmd_dry = [
    FLUID, "-ni", "-g", "1.2",
    "-R", "0", "-C", "0",
    "-F", str(dry_full),
    SF, str(SRC),
]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# 2. Extract Dry Stems via RenderPipeline
print("Rendering dry stems with RenderPipeline...")
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} dry stems: {list(stems_raw.keys())}")


def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        frames = wf.getnframes()
        data = wf.readframes(frames)
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if nch == 1:
            audio = np.vstack([samples, samples])
        else:
            audio = samples.reshape(-1, nch).T
        return audio, sr


def write_wav(p, audio, sr=SR):
    audio_clipped = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio_clipped * 32767.0).astype(np.int16)
    if audio_int16.ndim == 1:
        nch = 1
        data = audio_int16.tobytes()
    else:
        if audio_int16.shape[0] == 2:
            nch = 2
            interleaved = audio_int16.T.reshape(-1)
            data = interleaved.tobytes()
        elif audio_int16.shape[1] == 2:
            nch = 2
            data = audio_int16.reshape(-1).tobytes()
        else:
            nch = audio_int16.shape[0]
            interleaved = audio_int16.T.reshape(-1)
            data = interleaved.tobytes()
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)


# 3. SP-070 Morph Filter — ABSOLUTE layer parameters (one shared character)
#    position 1.5 -> equal-power morph between `diode` (even-harmonic warmth)
#    and `svf` (clean 2-pole). This exercises the morph crossfade path while
#    keeping a baroque-appropriate warm-but-clear timbre.
MORPH_PARAMS = dict(
    cutoff=3600.0,
    resonance=0.5,
    position=1.5,
    drive=1.4,
    mix=0.6,
)
weights = FusionFilter(SR).morph_positions(MORPH_PARAMS["position"])
print("SP-070 params:", MORPH_PARAMS)
print("Engine blend weights at position 1.5:", {k: round(v, 4) for k, v in weights.items()})


def morph_process(audio):
    """Apply the absolute-layer morph filter to each channel independently."""
    ff = FusionFilter(sample_rate=SR)
    out = np.empty_like(audio)
    for ch in range(audio.shape[0]):
        out[ch] = ff.process(
            audio[ch],
            cutoff=MORPH_PARAMS["cutoff"],
            resonance=MORPH_PARAMS["resonance"],
            position=MORPH_PARAMS["position"],
            drive=MORPH_PARAMS["drive"],
            mix=MORPH_PARAMS["mix"],
        )
    return out.astype(np.float32)


# Apply morph filter to dry full mix (absolute layer)
print("Applying SP-070 morph filter to full mix...")
t0 = time.time()
dry_mix_audio, sr = read_wav(dry_full)
wet_mix = morph_process(dry_mix_audio)
print(f"  full-mix morph done in {time.time()-t0:.1f}s, "
      f"peak={np.max(np.abs(wet_mix)):.3f}")

# 4. Master: reverb (church acoustic for baroque) + LUFS -14 + Limiter -1dB
print("Applying AlgorithmicReverb (baroque hall)...")
reverb = AlgorithmicReverb(sample_rate=SR, room_size=0.55, damping=0.45,
                           wet_dry=0.14, width=0.85)
rev_out = reverb.process(wet_mix.T)  # (N, 2)

print("Mastering: normalize_to_lufs(-14) + Limiter(-1 dBFS)...")
lufs_norm = normalize_to_lufs(rev_out, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_master_T = limiter.process(lufs_norm)  # (N, 2)
final_master = final_master_T.T  # (2, N)

final_wav = OUT / "SP070-morph-filter-baroque-genetic-allemande.wav"
final_ogg = OUT / "SP070-morph-filter-baroque-genetic-allemande.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = [
    "ffmpeg", "-y", "-loglevel", "error",
    "-i", str(final_wav),
    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
    str(final_ogg),
]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# 5. Wet stems (same absolute-layer morph params per stem, for DAW import)
print("Rendering wet stems (same morph params per stem)...")
stem_audios = {}
max_len = 0
for name, p in stems_raw.items():
    a, sr = read_wav(p)
    stem_audios[name] = a
    max_len = max(max_len, a.shape[1])
for name in stem_audios:
    a = stem_audios[name]
    if a.shape[1] < max_len:
        a = np.hstack([a, np.zeros((a.shape[0], max_len - a.shape[1]), dtype=np.float32)])
        stem_audios[name] = a
for name, a in stem_audios.items():
    w = morph_process(a)
    pmax = np.max(np.abs(w))
    if pmax > 1e-6:
        w = w * (0.89 / pmax)
    write_wav(STEMS_WET / f"{name}_MORPH.wav", w, sr=SR)
print("Wet stems done.")

# 6. Verification: silence / RMS / LUFS / pitch
measured_lufs = measure_lufs(final_master_T, sample_rate=SR)
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0

# per-second RMS map
rms_map = []
for s in range(len(mono_mix) // SR):
    seg = mono_mix[s * SR:(s + 1) * SR]
    rms_map.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))

print(f"Master Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, "
      f"Silence={silence_ratio:.2f}%")

# Pitch verification: D aeolian (Dm) = pcs {0,1,2,4,5,7,9,10}
#   (natural minor + harmonic-minor raised 7th C#=1)
D_MINOR_PCS = {0, 1, 2, 4, 5, 7, 9, 10}
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
    peak_idx = np.argmax(sub_spec)
    dom_f = sub_freqs[peak_idx]
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
        if pc in D_MINOR_PCS:
            fft_hits += 1

hit_rate = fft_hits / max(1, valid_windows)
mean_he = float(np.mean(harmonic_energies)) if harmonic_energies else 0.0
pitch_verdict = "PASS" if hit_rate >= 0.60 and mean_he >= 0.25 else "FAIL"

print(f"Pitch Verification: valid={valid_windows}, hit_rate={hit_rate:.4f}, "
      f"mean_HE={mean_he:.4f} -> {pitch_verdict}")

# 7. Analysis artifacts
render_stats = {
    "method": "SP-070",
    "params": MORPH_PARAMS,
    "engine_weights": {k: round(v, 4) for k, v in weights.items()},
    "characters": list(CHARACTERS),
    "lufs": measured_lufs,
    "peak": peak_val,
    "silence_pct": silence_ratio,
    "rms_per_second": rms_map,
    "valid_windows": valid_windows,
    "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he,
    "pitch_verdict": pitch_verdict,
    "median_freq_hz": float(np.median(dominant_freqs)) if dominant_freqs else 0.0,
    "duration_sec": len(mono_mix) / SR,
}
(ANALYSIS / "render_stats.json").write_text(json.dumps(render_stats, indent=2))
(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-070",
    "project": "091-baroque-genetic-allemande",
    "status": pitch_verdict,
    "hit_rate": hit_rate,
    "harmonic_energy_mean": mean_he,
    "windows_analyzed": valid_windows,
    "median_freq_hz": render_stats["median_freq_hz"],
}, indent=2))

# grid visualization (stems presence + character map)
grid_lines = [
    "SP-070 morph filter — absolute layer grid",
    f"position={MORPH_PARAMS['position']} -> engines "
    f"{ {k: round(v,3) for k,v in weights.items()} }",
    f"cutoff={MORPH_PARAMS['cutoff']}Hz resonance={MORPH_PARAMS['resonance']} "
    f"drive={MORPH_PARAMS['drive']} mix={MORPH_PARAMS['mix']}",
    "",
    "character sweep (all 5 engines, reference):",
]
for i, name in enumerate(CHARACTERS):
    bar = "█" * (i + 1) + "░" * (5 - i - 1)
    grid_lines.append(f"  pos={i} {name:8s} [{bar}]")
grid_lines.append("")
grid_lines.append("stems (wet, same absolute params):")
for name in sorted(stem_audios):
    grid_lines.append(f"  {name}_MORPH.wav")
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(grid_lines) + "\n")

# provenance
provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-09-27",
    "seed": SEED,
    "method": "SP-070",
    "method_module": "sound.effects.morph_filter",
    "method_desc": "Morphing Five-Character Resonant Filter (ZERO9 Fusion Filter-style)",
    "layer": "absolute",
    "params": MORPH_PARAMS,
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs,
    "peak": peak_val,
    "silence_pct": silence_ratio,
    "pitch_verdict": pitch_verdict,
    "hit_rate": hit_rate,
    "he_mean": mean_he,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(json.dumps(provenance, indent=2))

shutil.copy2(__file__, str(SCRIPTS / "produce_sp070_cron.py"))
print("Done. pitch_verdict=", pitch_verdict)
