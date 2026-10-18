# -*- coding: utf-8 -*-
"""SP-105 Spectral Brightness Panner production pass (absolute layer).

Source : Styles/Japanese/001-japanese-hirajoshi/MIDI/japanese-hirajoshi.mid
         (D hirajoshi 2-1-4-1-4, 70 BPM, 16 bars = 4 sections x 4 bars,
          4 voices: Koto ch0 GM108, Shakuhachi ch1 GM75, Shamisen ch2 GM106,
          Taiko ch9 drums.)
Method : SP-105 -> sound.effects.spectral_panner (SpectralBrightnessPanner).
         ABSOLUTE layer: one brightness->pan config applied to the WHOLE mix.
Pipeline:
  dry FluidSynth render (FX off) -> SpectralBrightnessPanner.process (full mix)
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
from sound.effects.spectral_panner import (
    SpectralBrightnessPanner, PanProfile, BrightnessMode,
)
from sound.effects.mastering import master, target_for_style

SRC = Path("/opt/data/repos/musicom/projects/Styles/Japanese/001-japanese-hirajoshi/MIDI/japanese-hirajoshi.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP105-spectral-panner-japanese-hirajoshi")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 70.0
SEED = 20261018
STYLE = "japanese"
TARGET_LUFS = target_for_style(STYLE)   # fallback -14.0 (no 'japanese' key)
CEILING_DB = -1.0

# Source pitch-class vocabulary (non-drum) for pitch verification.
SRC_PCS = set()
for _tr in mido.MidiFile(str(SRC)).tracks:
    for _m in _tr:
        if _m.type == "note_on" and _m.velocity > 0 and _m.channel != 9:
            SRC_PCS.add(_m.note % 12)
SRC_PCS = sorted(SRC_PCS)
print("Source PCS (non-drum):", SRC_PCS)

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))


def read_wav(p):
    # returns (2, N) channel-major float32
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


# 1. Dry full mix (SP-001 reference, FX off)
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth (FX off)...")
cmd_dry = [FLUID, "-ni", "-g", "1.2", "-R", "0", "-C", "0",
           "-F", str(dry_full), SF, str(SRC)]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr[-500:]}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# 2. Dry stems via RenderPipeline (DAW import artifacts; absolute layer = whole-mix processing)
print("Rendering dry stems with RenderPipeline...")
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} stems: {list(stems_raw.keys())}")

# 3. SP-105 Spectral Brightness Panner (absolute layer, one config on whole mix)
PAN_PARAMS = {
    "profile": PanProfile.CIRCULAR.value,   # continuous dark->left, bright->right
    "mode": BrightnessMode.DIRECT.value,
    "brightness_smooth": 0.85,
    "virtual_center": True,
    "virtual_center_threshold": 0.6,
    "lfo_blend": 0.20,
    "lfo_rate": 0.25,
    "lfo_waveform": "sine",
}
panner = SpectralBrightnessPanner(
    sample_rate=SR,
    profile=PanProfile.CIRCULAR,
    mode=BrightnessMode.DIRECT,
    brightness_smooth=PAN_PARAMS["brightness_smooth"],
    virtual_center=PAN_PARAMS["virtual_center"],
    virtual_center_threshold=PAN_PARAMS["virtual_center_threshold"],
    lfo_blend=PAN_PARAMS["lfo_blend"],
    lfo_rate=PAN_PARAMS["lfo_rate"],
    lfo_waveform=PAN_PARAMS["lfo_waveform"],
)

dry_audio, sr = read_wav(dry_full)          # (2, N)
print(f"Dry mix shape: {dry_audio.shape}, sr={sr}")
wet = panner.process(dry_audio.astype(np.float32))   # (2, N) float64
print(f"Wet mix shape: {wet.shape}, peak={np.max(np.abs(wet)):.3f}")

# 4. Master (full chain: HP -> glue -> stereo -> LUFS -> true-peak limit)
wet_tm = wet.T.astype(np.float32)            # (N, 2)
print(f"Mastering (master() chain, target {TARGET_LUFS} LUFS)...")
mastered_tm, rep = master(wet_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report:", rep.get("integrated_lufs"), "LUFS,", rep.get("true_peak_db"), "dBTP")
final_master = mastered_tm.T                  # (2, N)

final_wav = OUT / "SP105-spectral-panner-japanese-hirajoshi.wav"
final_ogg = OUT / "SP105-spectral-panner-japanese-hirajoshi.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# 5. Verification
from sound.effects.mastering import measure_lufs  # noqa: E402
measured_lufs = float(measure_lufs(mastered_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
rms = float(np.sqrt(np.mean(mono_mix ** 2)))
L = final_master[0]; R = final_master[1]
num = np.sum(L * R); den = math.sqrt(np.sum(L * L) * np.sum(R * R)) + 1e-12
mono_corr = float(num / den)
print(f"Master Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, "
      f"Silence={silence_ratio:.2f}%, RMS={rms:.4f}, MonoCorr={mono_corr:.3f}")


def pitch_verify(audio_2n, pcs):
    mono = 0.5 * (audio_2n[0] + audio_2n[1])
    window_len = int(0.5 * SR)
    num_windows = len(mono) // window_len
    fft_hits = 0
    valid_windows = 0
    harmonic_energies = []
    for w in range(num_windows):
        seg = mono[w * window_len:(w + 1) * window_len]
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
print(f"Pitch Verification: valid={valid_windows}, hits={hit_rate:.4f}, mean_HE_wet={mean_he:.4f}")
print(f"Dry reference: hit={dry_hit:.4f}, mean_HE_dry={dry_he:.4f}, HE_retention={he_retention:.3f}")
print(f"Pitch Verdict: {pitch_verdict}")

# 6. Analysis + provenance
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
    "date": "2026-10-18",
    "seed": SEED,
    "method": "SP-105",
    "method_module": "sound.effects.spectral_panner",
    "method_desc": "Spectral Brightness Panner - frequency-dependent auto-panner driven by spectral centroid/brightness analysis (Sound Particles Brightness Panner 2-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR,
        "pan_params": PAN_PARAMS,
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "source_bpm": BPM,
    "source_pitch_classes": SRC_PCS,
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "rms": rms, "mono_corr": mono_corr,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": mean_he,
    "dry_he_mean": dry_he, "he_retention": he_retention, "dry_hit_rate": dry_hit,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(ANALYSIS / "select_20261018.json").write_text(json.dumps({
    "date": "2026-10-18", "method": "SP-105",
    "method_module": "sound.effects.spectral_panner",
    "source_midi": str(SRC), "n_well_formed": 241, "registry_total": 48,
}, indent=2))

try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp105_cron.py"))
except shutil.SameFileError:
    pass
print("Done.")
