#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-028 LPC Synthesis production pass on 083-techno-brownian.

Source : Styles/Techno/083-techno-brownian/MIDI/083-techno-brownian.mid
         (24-bar F natural minor, 128 BPM, 6 voices + drums; Method 048 RBMPD)
Method : SP-028 -> sound.effects.lpc_synth (Linear Predictive Coding Synthesis).
         ABSOLUTE layer: one LPC vocode config applied to the WHOLE piece.

Chain: dry FluidSynth render -> LPC analyze (autocorr + Levinson-Durbin,
       order=16) -> re-excite (glottal train voiced / noise unvoiced,
       pitch_shift=1.0 = formant-preserving resynthesis) -> wet/dry blend
       (LPC dominant, dry transient support) -> normalize_to_lufs(-14)
       -> Limiter(-1 dBFS).
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
from sound.effects.lpc_synth import lpc_vocoder, lpc_analyze
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Techno/083-techno-brownian/MIDI/083-techno-brownian.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP028-lpc-synth-083-techno-brownian")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 128.0
SEED = 20261014

# ---- SP-028 parameters (absolute layer) ----------------------------------
ORDER = 16
FRAME_MS = 30
HOP_MS = 10
PITCH_SHIFT = 1.0      # formant-preserving resynthesis (no pitch change)
VOICED_GAIN = 1.0
UNVOICED_GAIN = 0.15
WET_MIX = 0.60         # LPC vocode dominant, dry transient support
DRY_MIX = 1.0 - WET_MIX

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# Source pitch-class vocabulary (non-drum) for pitch verification
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


# 1. Dry full mix (SP-001 reference, FX off)
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth (FX off)...", flush=True)
cmd_dry = [FLUID, "-ni", "-g", "1.2", "-R", "0", "-C", "0", "-F", str(dry_full), SF, str(SRC)]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr[-500:]}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes", flush=True)

# 2. Dry stems via RenderPipeline
print("Rendering dry stems with RenderPipeline...", flush=True)
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} stems: {list(stems_raw.keys())}", flush=True)

# 3. LPC vocode full mix per channel (absolute layer)
dry_audio, sr = read_wav(dry_full)      # (2, N)
print(f"Dry mix shape: {dry_audio.shape}, sr={sr}", flush=True)
N = dry_audio.shape[1]

wet = np.empty_like(dry_audio, dtype=np.float32)
for ch in range(dry_audio.shape[0]):
    print(f"LPC vocoding channel {ch} ({N} samples)...", flush=True)
    wet_ch = lpc_vocoder(
        dry_audio[ch].astype(np.float64), sr,
        pitch_shift=PITCH_SHIFT, order=ORDER,
        frame_ms=FRAME_MS, hop_ms=HOP_MS,
        voiced_gain=VOICED_GAIN, unvoiced_gain=UNVOICED_GAIN,
    ).astype(np.float32)
    # LPC resynth length = (n_frames-1)*H + L, slightly shorter than input.
    if len(wet_ch) < N:
        wet_ch = np.pad(wet_ch, (0, N - len(wet_ch)))
    else:
        wet_ch = wet_ch[:N]
    wet[ch] = wet_ch
    print(f"  channel {ch} done (aligned to {N})", flush=True)

# 4. Blend (LPC dominant, dry transient support)
print(f"Blending wet={WET_MIX} dry={DRY_MIX}...", flush=True)
final_pre = WET_MIX * wet + DRY_MIX * dry_audio

# 5. Master
print("Mastering: normalize_to_lufs(-14) + Limiter(-1 dBFS)...", flush=True)
final_pre_tm = final_pre.T.astype(np.float32)             # (N, 2)
lufs_norm = normalize_to_lufs(final_pre_tm, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_tm = limiter.process(lufs_norm)
final_master = final_tm.T                                 # (2, N)

final_wav = OUT / "SP028-lpc-synth-083-techno-brownian.wav"
final_ogg = OUT / "SP028-lpc-synth-083-techno-brownian.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)", flush=True)

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)", flush=True)

# 6. Per-stem wet copies (same LPC config)
print("Applying LPC vocode to dry stems...", flush=True)
for name, path in stems_raw.items():
    s_audio, s_sr = read_wav(path)
    sN = s_audio.shape[1]
    s_wet = np.empty_like(s_audio, dtype=np.float32)
    for ch in range(s_audio.shape[0]):
        wch = lpc_vocoder(s_audio[ch].astype(np.float64), s_sr,
                          pitch_shift=PITCH_SHIFT, order=ORDER,
                          frame_ms=FRAME_MS, hop_ms=HOP_MS,
                          voiced_gain=VOICED_GAIN, unvoiced_gain=UNVOICED_GAIN)
        wch = wch.astype(np.float32)
        if len(wch) < sN:
            wch = np.pad(wch, (0, sN - len(wch)))
        else:
            wch = wch[:sN]
        s_wet[ch] = wch
    s_blend = WET_MIX * s_wet + DRY_MIX * s_audio
    out_name = name + "_LPC"
    write_wav(STEMS_WET / f"{out_name}.wav", s_blend, sr=s_sr)
print(f"Wrote {len(stems_raw)} wet stems to {STEMS_WET}", flush=True)

# 7. Verification
measured_lufs = float(measure_lufs(final_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
L = final_master[0]; R = final_master[1]
num = np.sum(L * R); den = math.sqrt(np.sum(L * L) * np.sum(R * R)) + 1e-12
mono_corr = float(num / den)
print(f"Master Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, "
      f"Silence={silence_ratio:.2f}%, MonoCorr={mono_corr:.3f}", flush=True)


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

pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_retention >= 0.40) else "FAIL"
print(f"Pitch Verification: valid={valid_windows}, hits={hit_rate:.4f}, mean_HE_wet={mean_he:.4f}", flush=True)
print(f"Dry reference: hit={dry_hit:.4f}, mean_HE_dry={dry_he:.4f}, HE_retention={he_retention:.3f}", flush=True)
print(f"Pitch Verdict: {pitch_verdict}", flush=True)

rms = float(np.sqrt(np.mean(mono_mix ** 2)))
print(f"Overall RMS: {rms:.4f}, silence: {silence_ratio:.2f}%", flush=True)

# 8. Write analysis + provenance
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr, "rms": rms,
    "valid_windows": valid_windows, "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he, "pitch_verdict": pitch_verdict,
    "dry_mean_harmonic_energy": dry_he, "he_retention": he_retention,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-14",
    "seed": SEED,
    "method": "SP-028",
    "method_module": "sound.effects.lpc_synth",
    "method_desc": "Linear Predictive Coding Synthesis (source-filter vocoder)",
    "params": {
        "order": ORDER, "frame_ms": FRAME_MS, "hop_ms": HOP_MS,
        "pitch_shift": PITCH_SHIFT, "voiced_gain": VOICED_GAIN,
        "unvoiced_gain": UNVOICED_GAIN, "wet_mix": WET_MIX,
        "dry_mix": DRY_MIX, "fs": SR,
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
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(
    json.dumps(provenance, indent=2))

(ANALYSIS / "select_20261014.json").write_text(json.dumps({
    "date": "2026-10-14", "method": "SP-028",
    "method_module": "sound.effects.lpc_synth",
    "source_midi": str(SRC),
    "registry_total": 45,
    "n_well_formed": 231,
}, indent=2))

shutil.copy2(__file__, str(SCRIPTS / "produce_sp028_cron.py"))
print("Done.", flush=True)
