#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-085 GlitchChopper production pass on Blues/blues-delta-daily-2026-06-24.

Source: Styles/Blues/blues-delta-daily-2026-06-24/MIDI/blues-delta-daily-2026-06-24.mid
        (Delta Blues, 72 BPM, 12-bar grid, 4 voices:
         Resonator Slide lead GM25 ch0 (290 notes),
         Acoustic Rhythm GM26 ch1 (83 notes),
         Fingerstyle Bass GM32 ch2 (47 notes),
         Stomp & Clap ch9 (101 onsets))
Method: SP-085 -> sound.effects.glitch_chopper (GlitchShredder-style)
Layer : ABSOLUTE layer - transient-snapped 16-slot segment chopper with
        glitch/reverse recombination replaces the time/timbre layer for the
        WHOLE piece (full mix + per-stem convenience passes).
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
from sound.effects.glitch_chopper import GlitchChopper, detect_transients
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Blues/blues-delta-daily-2026-06-24/MIDI/blues-delta-daily-2026-06-24.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP085-glitch-chopper-blues-delta-daily")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20261009

# ---- read BPM from conductor track ---------------------------------------
_tempo_us = 500000  # default 120 bpm
for _tr in mido.MidiFile(str(SRC)).tracks:
    for _m in _tr:
        if _m.type == "set_tempo":
            _tempo_us = _m.tempo
BPM = 60_000_000.0 / _tempo_us
print(f"Tempo: {BPM:.2f} BPM (raw {_tempo_us} us/beat)")

# ---- SP-085 parameters (absolute layer) -----------------------------------
GLITCH_P = 0.30    # probability a quantized step is replaced by a random slot
REVERSE_P = 0.25   # probability a slot plays backwards
QUANT = 8          # stutter grid = 8 quantized jumps per bar (8th-note feel)
SLOTS = 16         # segment slots per channel (per GlitchChopper default)

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

# 3. Apply SP-085 GlitchChopper to the full mix (absolute layer)
dry_audio, sr = read_wav(dry_full)          # (2, N) channel-major
print(f"Dry mix shape: {dry_audio.shape}, sr={sr}")

dry_tm = np.asarray(dry_audio).T.astype(np.float64)   # (N, 2) time-major
gc = GlitchChopper(sample_rate=SR, bpm=BPM, slots=SLOTS, seed=SEED)
wet_tm = gc.process(dry_tm, glitch_p=GLITCH_P, reverse_p=REVERSE_P, quant=QUANT)
wet_tm = np.asarray(wet_tm, dtype=np.float32)
print(f"Wet mix shape: {wet_tm.shape}")

# transient census on the dry mono mix (documents the chopper's snap grid)
dry_mono = 0.5 * (dry_audio[0] + dry_audio[1])
trans = detect_transients(dry_mono, SR)
print(f"Transients detected on dry mix: {len(trans)}")

# 4. Master: normalize to -14 LUFS, then Limiter(-1 dBFS)
print("Mastering: normalize_to_lufs(-14) + Limiter(-1 dBFS)...")
lufs_norm = normalize_to_lufs(wet_tm, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_tm = limiter.process(lufs_norm)          # (N, 2)
final_master = final_tm.T                       # (2, N)

final_wav = OUT / "SP085-glitch-chopper-blues-delta-daily.wav"
final_ogg = OUT / "SP085-glitch-chopper-blues-delta-daily.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# 5. Per-stem wet passes (same params, independent glitch RNG per stem)
print("Applying same GlitchChopper params to dry stems...")
for name, path in stems_raw.items():
    s_audio, s_sr = read_wav(path)
    s_tm = np.asarray(s_audio).T.astype(np.float64)
    s_wet = gc.process(s_tm, glitch_p=GLITCH_P, reverse_p=REVERSE_P, quant=QUANT)
    s_wet = np.asarray(s_wet, dtype=np.float32)
    out_name = name + "_GLITCH"
    write_wav(STEMS_WET / f"{out_name}.wav", s_wet.T, sr=s_sr)
print(f"Wrote {len(stems_raw)} wet stems to {STEMS_WET}")

# 6. Verification
measured_lufs = float(measure_lufs(final_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
rms = float(np.sqrt(np.mean(mono_mix ** 2)))
dry_mono_mix = 0.5 * (dry_audio[0] + dry_audio[1])
dry_silence = float(np.sum(np.abs(dry_mono_mix) < 0.001) / len(dry_mono_mix)) * 100.0
dry_rms = float(np.sqrt(np.mean(dry_mono_mix ** 2)))
print(f"Overall RMS: {rms:.4f}, silence: {silence_ratio:.2f}% (dry silence {dry_silence:.2f}%, dry RMS {dry_rms:.4f})")


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

# 7. Write analysis + provenance
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "rms": rms,
    "dry_silence_pct": dry_silence, "dry_rms": dry_rms,
    "valid_windows": valid_windows, "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he, "pitch_verdict": pitch_verdict,
    "dry_mean_harmonic_energy": dry_he, "he_retention": he_retention,
    "transients_detected": len(trans),
    "bpm": BPM,
}, indent=2))

(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-085", "project": "Blues/blues-delta-daily-2026-06-24",
    "scale": "A blues hexatonic (source PCS, non-drum)", "pcs": SRC_PCS,
    "status": pitch_verdict, "hit_rate": hit_rate,
    "harmonic_energy_mean": mean_he, "dry_harmonic_energy_mean": dry_he,
    "he_retention": he_retention, "windows_analyzed": valid_windows,
    "median_freq_hz": float(np.median(dominant_freqs)) if dominant_freqs else 0.0,
    "transients_detected": len(trans),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-09",
    "seed": SEED,
    "method": "SP-085",
    "method_module": "sound.effects.glitch_chopper",
    "method_desc": "Transient-Snapped Segment Chopper w/ Glitch/Reverse Probability (GlitchShredder-style)",
    "params": {
        "bpm": BPM,
        "glitch_p": GLITCH_P,
        "reverse_p": REVERSE_P,
        "quant": QUANT,
        "slots": SLOTS,
        "sample_rate": SR,
    },
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "rms": rms,
    "dry_silence_pct": dry_silence, "dry_rms": dry_rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": mean_he,
    "dry_he_mean": dry_he, "he_retention": he_retention,
    "fix": "glitch_chopper.render_pass slot padding bug: bank rows are bar-length "
           "with only the first step samples filled, but render_pass sliced the "
           "full row -> every quant<16 window was ~50% zero padding (~60% silence). "
           "Fixed: slice seg = bank[cur_slot][:step] so the slot content tiles over "
           "the window as the docstring/comments intend.",
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(json.dumps(provenance, indent=2))

(ANALYSIS / "select_20261009.json").write_text(json.dumps({
    "date": "2026-10-09", "method": "SP-085",
    "method_module": "sound.effects.glitch_chopper",
    "source_midi": str(SRC),
    "recent_excluded": sorted(["SP-021", "SP-069", "SP-080", "SP-083", "SP-086", "SP-091", "SP-092"]),
    "registry_total": 42,
    "n_well_formed": 221,
    "note": "first draw SP-074 x blues-delta-daily-2026-06-24 == existing "
            "Production/SP074-drummachine-delta-blues (exact source+method dup) "
            "-> re-rolled method to SP-085",
}, indent=2))

shutil.copy2(__file__, str(SCRIPTS / "produce_sp085_cron.py")) if str(__file__) != str(SCRIPTS / "produce_sp085_cron.py") else None
print("Done.")
