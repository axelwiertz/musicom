# -*- coding: utf-8 -*-
"""SP-090 Orbital Stereo Sculptor / AutoPanner production pass (absolute layer).

Source : Styles/Country/012-country-country-uke (G major, 96 BPM, 48 bars,
         8 voices) -> reworked zero-drift/grid/chord-tone copy in
         MIDI/composition.mid (see rework_20261021.py + audit_source_20261021.py).
Method : SP-090 -> sound.effects.orbit_sculptor (OrbitalStereoSculptor).
         ABSOLUTE layer: the WHOLE dry FluidSynth mix is split into Low/Mid/High
         bands via LR4 crossover; per-band pan/width/gain + tempo-synced LFO
         autopan.  Lows stay centered mono; mids + highs get gentle tempo-synced
         orbital motion.
Pipeline: dry FluidSynth (FX off) -> OrbitalStereoSculptor (whole mix)
          -> master() (country -14 LUFS, -1 dBTP) -> WAV + Opus OGG
          (+ dry per-track stems via RenderPipeline as DAW artifacts).
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
from sound.effects.orbit_sculptor import OrbitalStereoSculptor, ModulatorConfig
from sound.effects.mastering import master, target_for_style, measure_lufs

OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-sculptor-012-country-uke")
NORM = OUT / "MIDI" / "composition.mid"
SRC = Path("/opt/data/repos/musicom/projects/Styles/Country/012-country-country-uke/MIDI/v2_country_unitmatrix.mid")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 96.0
SEED = 20261021
STYLE = "country"
TARGET_LUFS = target_for_style(STYLE)   # -14.0
CEILING_DB = -1.0

# G major (post chord-tone-quantize: every pitched note is a chord tone of
# G/D/Em/C, union = G major scale {7,9,11,0,2,4,6})
SRC_PCS = {7, 9, 11, 0, 2, 4, 6}

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# ---------- 0. copy source MIDI for reference ----------
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

# ---------- 3. SP-090 orbital stereo sculpt (absolute layer on whole mix) ----------
dry_audio, sr = read_wav(dry_full)          # (2, N)
mono = (0.5 * (dry_audio[0] + dry_audio[1])).astype(np.float64)
N = len(mono)
print(f"Dry mix: {dry_audio.shape}, dur={N/sr:.2f}s")

sculptor = OrbitalStereoSculptor(low_mid_cross=250.0, mid_high_cross=3500.0,
                                 fs=SR, bpm=BPM, seed=SEED)
# Low band: centered mono (keep bass solid)
sculptor.low_config.pan = 0.0
sculptor.low_config.width = 0.0
sculptor.low_config.gain_db = 0.0
# Mid band: gentle tempo-synced sine autopan (half note)
sculptor.mid_config.pan = 0.0
sculptor.mid_config.width = 1.15
sculptor.mid_config.gain_db = 0.0
sculptor.mid_config.pan_mod = ModulatorConfig(
    shape="sine", tempo_sync=True, division="1/2", depth=0.45, saturated=False)
# High band: faster subtle autopan (eighth note) + extra width
sculptor.high_config.pan = 0.0
sculptor.high_config.width = 1.5
sculptor.high_config.gain_db = 0.0
sculptor.high_config.pan_mod = ModulatorConfig(
    shape="sine", tempo_sync=True, division="1/8", depth=0.35, saturated=False)

print("Applying OrbitalStereoSculptor (whole mix)...")
wet = sculptor.process(dry_audio.astype(np.float32))   # (2, N)
wet = wet[:, :N]
print(f"Wet: shape {wet.shape}, peak={np.max(np.abs(wet)):.3f}")

# ---------- 4. master ----------
wet_tm = wet.T.astype(np.float32)             # (N, 2)
print(f"Mastering (target {TARGET_LUFS} LUFS, ceiling {CEILING_DB} dBTP)...")
mastered_tm, rep = master(wet_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report:", round(float(rep.get("integrated_lufs", 0)), 2), "LUFS,",
      round(float(rep.get("true_peak_db", 0)), 2), "dBTP")
final_master = mastered_tm.T                   # (2, N)

final_wav = OUT / "SP090-orbit-sculptor-012-country-uke.wav"
final_ogg = OUT / "SP090-orbit-sculptor-012-country-uke.ogg"
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
    "date": "2026-10-21",
    "seed": SEED,
    "method": "SP-090",
    "method_module": "sound.effects.orbit_sculptor",
    "method_desc": "3-Band Orbital Stereo Sculptor / AutoPanner (SoundGhost Orbit-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR,
        "low_mid_cross": 250.0, "mid_high_cross": 3500.0,
        "low": {"pan": 0.0, "width": 0.0, "gain_db": 0.0},
        "mid": {"pan": 0.0, "width": 1.15, "gain_db": 0.0,
                "pan_mod": {"shape": "sine", "division": "1/2", "depth": 0.45}},
        "high": {"pan": 0.0, "width": 1.5, "gain_db": 0.0,
                 "pan_mod": {"shape": "sine", "division": "1/8", "depth": 0.35}},
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
(ANALYSIS / "select_20261021.json").write_text(json.dumps({
    "date": "2026-10-21", "method": "SP-090",
    "method_module": "sound.effects.orbit_sculptor",
    "source_midi": str(SRC), "n_well_formed": 249, "registry_total": 54,
}, indent=2))

for s in ("select_job_20261021.py", "audit_source_20261021.py", "rework_20261021.py"):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp090_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
