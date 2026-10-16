# -*- coding: utf-8 -*-
"""SP-099 Impulse Response Designer production pass (absolute layer).

Source : SP099-ir-designer-ballad-hitl-cand3/MIDI/cand3-pViol-ldX-ar4-pdpuls-drful-bXo0.mid
         (reworked HITL round-0 cand3, D aeolian ballad, 72 BPM, 28 bars, 5 voices)
Method : SP-099 -> sound.effects.ir_designer (Impulse Response Designer).
         ABSOLUTE layer: one convolution-reverb IR applied to the WHOLE piece.
Pipeline:
  dry FluidSynth render (FX off) -> design reverb IR -> fftconvolve (wet)
  -> dry/wet mix -> master (LUFS -14, -1 dBTP) -> WAV + Opus OGG
  (+ dry stems + per-stem wet copies for DAW import)
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
from scipy.signal import fftconvolve

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.ir_designer import design_ir
from sound.effects.mastering import master, measure_lufs

SRC = Path("/opt/data/repos/musicom/projects/Styles/Production/SP099-ir-designer-ballad-hitl-cand3/MIDI/cand3-pViol-ldX-ar4-pdpuls-drful-bXo0.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP099-ir-designer-ballad-hitl-cand3")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 72.0
SEED = 20261016
STYLE = "pop ballad"
TARGET_LUFS = -14.0        # dynamic ballad — streaming target (matches project's own master)
CEILING_DB = -1.0

# ---- SP-099 parameters (absolute layer) -----------------------------------
IR_RECIPE = "reverb"
IR_RT60 = 2.0          # ballad hall decay
IR_DURATION = 3.0      # IR length (s)
WET_GAIN = 0.35
DRY_GAIN = 0.80

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


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


# source pitch-class vocabulary (non-drum) for pitch verification
_src_pcs = set()
for _tr in mido.MidiFile(str(SRC)).tracks:
    _t = 0
    for _m in _tr:
        _t += _m.time
        if _m.type == "note_on" and _m.velocity > 0 and _m.channel != 9:
            _src_pcs.add(_m.note % 12)
SRC_PCS = sorted(_src_pcs)
print("Source PCS (non-drum):", SRC_PCS)

# 1. Dry full mix (FluidSynth, FX off)
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth (FX off)...")
cmd_dry = [FLUID, "-ni", "-g", "1.2", "-R", "0", "-C", "0", "-F", str(dry_full), SF, str(SRC)]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr[-500:]}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# 2. Dry stems
print("Rendering dry stems...")
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} stems: {list(stems_raw.keys())}")

# 3. Design IR + convolve (absolute layer)
dry_audio, sr = read_wav(dry_full)      # (2, N)
print(f"Dry mix shape: {dry_audio.shape}, sr={sr}")

rng = np.random.default_rng(SEED)
np.random.seed(SEED)   # design_ir uses np.random
ir, _ = design_ir(IR_RECIPE, duration_s=IR_DURATION, rt60_s=IR_RT60, sr=SR)
print(f"IR shape: {ir.shape}, peak={np.max(np.abs(ir)):.3f}")

wet = np.stack([fftconvolve(dry_audio[c], ir) for c in range(2)])   # (2, N+ir-1)
n_ir = len(ir)
dry_pad = np.pad(dry_audio, ((0, 0), (0, n_ir - 1)))                # (2, N+ir-1)
mix = DRY_GAIN * dry_pad + WET_GAIN * wet                           # (2, N+ir-1)
print(f"Convolved mix shape: {mix.shape}")

# 4. Master (LUFS -14, -1 dBTP) — time-major input
mix_tm = mix.T.astype(np.float32)                                   # (N+ir-1, 2)
print("Mastering (master() chain)...")
mastered_tm, rep = master(mix_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB, sample_rate=SR)
mastered = mastered_tm.T                                            # (2, N+ir-1)
print("master report:", rep.get("integrated_lufs"), "LUFS,", rep.get("true_peak_db"), "dBTP")

final_wav = OUT / "SP099-ir-designer-ballad-hitl-cand3.wav"
final_ogg = OUT / "SP099-ir-designer-ballad-hitl-cand3.ogg"
write_wav(final_wav, mastered, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# 5. Per-stem wet copies (same IR)
print("Applying same convolution to dry stems...")
for name, path in stems_raw.items():
    s_audio, s_sr = read_wav(path)
    s_wet = np.stack([fftconvolve(s_audio[c], ir) for c in range(2)])
    s_pad = np.pad(s_audio, ((0, 0), (0, n_ir - 1)))
    s_mix = DRY_GAIN * s_pad + WET_GAIN * s_wet
    write_wav(STEMS_WET / f"{name}_IR.wav", s_mix, sr=s_sr)
print(f"Wrote {len(stems_raw)} wet stems to {STEMS_WET}")

# 6. Verification
measured_lufs = float(measure_lufs(mastered_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered)))
mono_mix = 0.5 * (mastered[0] + mastered[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
L = mastered[0]; R = mastered[1]
num = np.sum(L * R); den = math.sqrt(np.sum(L * L) * np.sum(R * R)) + 1e-12
mono_corr = float(num / den)
rms = float(np.sqrt(np.mean(mono_mix ** 2)))
print(f"Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, Silence={silence_ratio:.2f}%, "
      f"RMS={rms:.4f}, MonoCorr={mono_corr:.3f}")


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


hit_rate, mean_he, valid_windows = pitch_verify(mastered, SRC_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio, SRC_PCS)
he_retention = (mean_he / dry_he) if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_retention >= 0.40) else "FAIL"
print(f"Pitch Verification: valid={valid_windows}, hits={hit_rate:.4f}, mean_HE_wet={mean_he:.4f}")
print(f"Dry reference: hit={dry_hit:.4f}, mean_HE_dry={dry_he:.4f}, HE_retention={he_retention:.3f}")
print(f"Pitch Verdict: {pitch_verdict}")

# 7. Analysis + provenance
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr, "rms": rms,
    "valid_windows": valid_windows, "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he, "pitch_verdict": pitch_verdict,
    "dry_mean_harmonic_energy": dry_he, "he_retention": he_retention,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-16",
    "seed": SEED,
    "method": "SP-099",
    "method_module": "sound.effects.ir_designer",
    "method_desc": "Impulse Response Designer — 10 algorithmic IR synthesis techniques (Convolution Playground-style)",
    "params": {"recipe": IR_RECIPE, "rt60_s": IR_RT60, "duration_s": IR_DURATION,
               "wet_gain": WET_GAIN, "dry_gain": DRY_GAIN, "fs": SR,
               "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB},
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": mean_he,
    "dry_he_mean": dry_he, "he_retention": he_retention,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(ANALYSIS / "select_20261016.json").write_text(json.dumps({
    "date": "2026-10-16", "method": "SP-099",
    "method_module": "sound.effects.ir_designer",
    "source_midi": str(SRC), "n_well_formed": 235, "registry_total": 48,
}, indent=2))

shutil.copy2(__file__, str(SCRIPTS / "produce_sp099_cron.py"))
print("Done.")
