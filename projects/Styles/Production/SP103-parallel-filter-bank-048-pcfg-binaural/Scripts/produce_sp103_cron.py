#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-103 Parallel Filter Bank production pass on 048-pcfg-binaural (reworked).

Source : Styles/Experimental/048-pcfg-binaural/MIDI/048-pcfg-binaural.mid
         (8-bar C Dorian, 100 BPM, 3 voices: Lead violin ch0, Pad ch1, Bass ch2)
Method : SP-103 -> sound.effects.parallel_filter_bank (Filtopia-style
         5-parallel SEM filter bank). ABSOLUTE layer: one filter-bank config
         applied to the WHOLE piece.
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
from sound.effects.parallel_filter_bank import ParallelSEMFilterBank, FilterSlot
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Experimental/048-pcfg-binaural/MIDI/048-pcfg-binaural.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP103-parallel-filter-bank-048-pcfg-binaural")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 100.0
SEED = 20261013

# ---- SP-103 parameters (absolute layer) -----------------------------------
# Filtopia-style 5-slot parallel filter bank. Base cutoff 1400 Hz keeps the
# fundamental band (65-784 Hz) inside the LP slots' passband (pitch-safe),
# while BP slots carve a formant cluster around 1300-1600 Hz.
BASE_CUTOFF = 1400.0
SLOTS = [
    FilterSlot(cutoff_offset=-300.0, resonance=0.50, mode="lp", mix=0.80),
    FilterSlot(cutoff_offset=-100.0, resonance=0.30, mode="bp", mix=0.60),
    FilterSlot(cutoff_offset=0.0,   resonance=0.40, mode="bp", mix=1.00),
    FilterSlot(cutoff_offset=200.0, resonance=0.30, mode="bp", mix=0.60),
    FilterSlot(cutoff_offset=500.0, resonance=0.50, mode="lp", mix=0.80),
]

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

# 3. Apply SP-103 Parallel Filter Bank to the full mix (absolute layer)
dry_audio, sr = read_wav(dry_full)      # (2, N)
print(f"Dry mix shape: {dry_audio.shape}, sr={sr}")

bank = ParallelSEMFilterBank(sample_rate=SR, slots=SLOTS)
wet = bank.process(dry_audio.astype(np.float32), base_cutoff=BASE_CUTOFF)  # (2, N)
print(f"Wet mix shape: {wet.shape}")

# 4. Master: normalize to -14 LUFS, then Limiter(-1 dBFS)
print("Mastering: normalize_to_lufs(-14) + Limiter(-1 dBFS)...")
wet_tm = wet.T.astype(np.float32)                    # (N, 2)
lufs_norm = normalize_to_lufs(wet_tm, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_tm = limiter.process(lufs_norm)                # (N, 2)
final_master = final_tm.T                            # (2, N)

final_wav = OUT / "SP103-parallel-filter-bank-048-pcfg-binaural.wav"
final_ogg = OUT / "SP103-parallel-filter-bank-048-pcfg-binaural.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# 5. Per-stem wet copies (same bank config)
print("Applying same filter-bank config to dry stems...")
for name, path in stems_raw.items():
    s_audio, s_sr = read_wav(path)
    s_wet = bank.process(s_audio.astype(np.float32), base_cutoff=BASE_CUTOFF)
    out_name = name + "_PFB"
    write_wav(STEMS_WET / f"{out_name}.wav", s_wet, sr=s_sr)
print(f"Wrote {len(stems_raw)} wet stems to {STEMS_WET}")

# 6. Verification
measured_lufs = float(measure_lufs(final_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
mono_corr = 0.0
L = final_master[0]; R = final_master[1]
num = np.sum(L * R); den = math.sqrt(np.sum(L * L) * np.sum(R * R)) + 1e-12
mono_corr = float(num / den)
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

pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_retention >= 0.40) else "FAIL"
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

slot_summary = [
    {"slot": i + 1, "cutoff_offset": s.cutoff_offset, "resonance": s.resonance,
     "mode": s.mode, "mix": s.mix}
    for i, s in enumerate(SLOTS)
]

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-13",
    "seed": SEED,
    "method": "SP-103",
    "method_module": "sound.effects.parallel_filter_bank",
    "method_desc": "Filtopia-style 5-Parallel SEM Filter Bank",
    "params": {"base_cutoff": BASE_CUTOFF, "slots": slot_summary, "fs": SR},
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

(ANALYSIS / "select_20261013.json").write_text(json.dumps({
    "date": "2026-10-13", "method": "SP-103",
    "method_module": "sound.effects.parallel_filter_bank",
    "source_midi": str(SRC),
    "registry_total": 45,
    "n_well_formed": 229,
}, indent=2))

shutil.copy2(__file__, str(SCRIPTS / "produce_sp103_cron.py"))
print("Done.")
