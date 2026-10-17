# -*- coding: utf-8 -*-
"""SP-092 Multiband Saturator production pass (absolute layer).

Source : Experimental/032-prime-fractal-void/MIDI/fractal_void.mid
         (single-voice sawtooth fractal lead, program 81, 144 BPM, 8.5 bars,
          96 x 16th-note events, pitch-class set {C, Eb, F, G, B}).
Method : SP-092 -> sound.effects.multiband_saturator (6-band, 15-algo, M/S).
         ABSOLUTE layer: one multiband-saturator config applied to the WHOLE piece.
Pipeline:
  dry FluidSynth render (FX off) -> MultibandSaturator.process (6 bands)
  -> master (LUFS -14, -1 dBTP) -> WAV + Opus OGG
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
from sound.effects.multiband_saturator import MultibandSaturator, BandConfig, SATURATION_NAMES
from sound.effects.mastering import master, target_for_style

SRC = Path("/opt/data/repos/musicom/projects/Styles/Experimental/032-prime-fractal-void/MIDI/fractal_void.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP092-multiband-saturator-prime-fractal-void")
AUD = OUT / "Audio"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"
for d in (AUD, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 144.0
SEED = 20261017
STYLE = "experimental"
TARGET_LUFS = target_for_style(STYLE)   # -14.0
CEILING_DB = -1.0
GLOBAL_TRIM = 0.85

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
            audio = np.vstack([samples, samples]).T   # (N, 2)
        else:
            audio = samples.reshape(-1, nch)[:, :2]   # (N, 2)
        return audio, sr


def write_wav(p, audio, sr=SR):
    audio = np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0)
    if audio.ndim == 1:
        nch = 1
        interleaved = audio
    else:
        nch = audio.shape[1]
        interleaved = audio.reshape(-1)
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

dry_audio, sr = read_wav(dry_full)   # (N, 2)
print(f"Dry mix shape: {dry_audio.shape}, sr={sr}")

# 2. SP-092 multiband saturator config (absolute layer, deterministic + musical)
BAND_CFGS = [
    BandConfig(frequency=60,    q=1.0, drive=0.8, mix=1.0, algo="bypass",       mode="stereo"),  # <120 Hz sub
    BandConfig(frequency=250,   q=1.0, drive=1.25, mix=1.0, algo="tube",        mode="stereo"),  # 120-400 fundamentals
    BandConfig(frequency=800,   q=1.0, drive=1.35, mix=1.0, algo="tanh",        mode="stereo"),  # 400-1200 fundamentals+harm
    BandConfig(frequency=2500,  q=1.0, drive=1.05, mix=1.0, algo="soft_clip",   mode="mid"),     # 1200-4000 harmonics
    BandConfig(frequency=6000,  q=1.0, drive=0.5,  mix=1.0, algo="sine_foldback", mode="stereo"),  # 4000-10000 sheen
    BandConfig(frequency=12000, q=1.0, drive=1.0, mix=1.0, algo="bypass",       mode="stereo"),  # >10000 air
]
sat = MultibandSaturator(sample_rate=SR, band_configs=BAND_CFGS, global_trim=GLOBAL_TRIM)
print(sat.summary())

saturated = sat.process(dry_audio)   # (N, 2) float
print(f"Saturated shape: {saturated.shape}, peak={np.max(np.abs(saturated)):.3f}")

# 3. Master (LUFS target, -1 dBTP)
print(f"Mastering (master() chain, target {TARGET_LUFS} LUFS)...")
mastered_tm, rep = master(saturated, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB, sample_rate=SR)
mastered = mastered_tm   # (N, 2) time-major
print("master report:", rep.get("integrated_lufs"), "LUFS,", rep.get("true_peak_db"), "dBTP")

final_wav = OUT / "SP092-multiband-saturator-prime-fractal-void.wav"
final_ogg = OUT / "SP092-multiband-saturator-prime-fractal-void.ogg"
write_wav(final_wav, mastered, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# 4. Verification
from sound.effects.mastering import measure_lufs  # noqa: E402
measured_lufs = float(measure_lufs(mastered, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered)))
mono_mix = 0.5 * (mastered[:, 0] + mastered[:, 1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
rms = float(np.sqrt(np.mean(mono_mix ** 2)))
print(f"Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, Silence={silence_ratio:.2f}%, RMS={rms:.4f}")


def pitch_verify(audio_2n, pcs):
    mono = 0.5 * (audio_2n[:, 0] + audio_2n[:, 1])
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

# 5. Analysis + provenance
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "rms": rms, "valid_windows": valid_windows, "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he, "pitch_verdict": pitch_verdict,
    "dry_mean_harmonic_energy": dry_he, "he_retention": he_retention,
    "dry_hit_rate": dry_hit,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-17",
    "seed": SEED,
    "method": "SP-092",
    "method_module": "sound.effects.multiband_saturator",
    "method_desc": "6-Band Multiband Saturator w/ 15 Selectable Algorithms & Per-Band M/S Routing (Kreuzberg Audio Oberton-style)",
    "params": {
        "sample_rate": SR, "global_trim": GLOBAL_TRIM,
        "crossover_freqs": [120.0, 400.0, 1200.0, 4000.0, 10000.0],
        "band_configs": [
            {"freq": b.frequency, "q": b.q, "drive": b.drive, "mix": b.mix,
             "algo": b.algo, "mode": b.mode} for b in BAND_CFGS
        ],
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "source_bpm": BPM,
    "source_pitch_classes": SRC_PCS,
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": mean_he,
    "dry_he_mean": dry_he, "he_retention": he_retention, "dry_hit_rate": dry_hit,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(ANALYSIS / "select_20261017.json").write_text(json.dumps({
    "date": "2026-10-17", "method": "SP-092",
    "method_module": "sound.effects.multiband_saturator",
    "source_midi": str(SRC), "n_well_formed": 237, "registry_total": 48,
}, indent=2))

try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp092_cron.py"))
except shutil.SameFileError:
    pass
print("Done.")
