#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-032 FDN Reverb production pass on le_cercle_de_l_agent (Balfolk jig).

Source : Styles/Balfolk/005-balfolk-production/midi/le_cercle_de_l_agent.mid
         (16-bar 6/8 G-major Balfolk jig, 120 BPM, reworked phase-2:
          Violin 40 ch0 / Acoustic Guitar 25 ch1 / Piano 1 ch2, G6/9 drone)
Method : SP-032 -> sound.effects.fdn_reverb (Feedback Delay Network Reverb).
         ABSOLUTE layer: one FDN config applied to the WHOLE piece.

Chain: dry FluidSynth render (FX off) -> TRIM spurious FluidSynth tail (the
       FluidR3_GM violin/guitar patches trigger a ~20s silent tail; content is
       only 24s) -> pad 3.5s FDN tail -> FDN.process() -> normalize_to_lufs(-14)
       -> Limiter(-1 dBFS).

v2 (2026-10-15): added trim_tail() after the dry render to remove the spurious
       FluidSynth silent tail that inflated silence ratio to 41.6%.
"""
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.fdn_reverb import FDN
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter
from sound.utils.io import read_wav, write_wav

SRC = Path("/opt/data/repos/musicom/projects/Styles/Balfolk/005-balfolk-production/midi/le_cercle_de_l_agent.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP032-fdn-le-cercle-de-l-agent")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 120.0
SEED = 20261015

N_DELAYS = 8
SIZE = 0.55
DECAY = 0.80
BRIGHTNESS = 0.72
MODULATION = 0.25
WIDTH = 0.85
DUCK = 0.12
WET_DRY = 0.35

TRIM_TAIL_S = 1.5
FDN_TAIL_S = 3.5

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

_src_pcs = set()
for _tr in mido.MidiFile(str(SRC)).tracks:
    for _m in _tr:
        if _m.type == "note_on" and _m.velocity > 0 and _m.channel != 9:
            _src_pcs.add(_m.note % 12)
SRC_PCS = sorted(_src_pcs)
print("Source PCS (non-drum):", SRC_PCS, flush=True)


def trim_tail(audio, sr, tail_s=TRIM_TAIL_S, threshold=0.0005):
    """Cut the spurious FluidSynth silent tail; keep content + tail_s."""
    if audio.ndim == 1:
        mono = np.abs(audio)
    else:
        mono = np.abs(audio).max(axis=1)
    above = np.where(mono > threshold)[0]
    if len(above) == 0:
        return audio
    end = above[-1] + int(tail_s * sr)
    return audio[:min(end, len(audio))]


# 1. Dry full mix (SP-001 reference, FX off)
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth (FX off)...", flush=True)
cmd_dry = [FLUID, "-ni", "-g", "1.2", "-R", "0", "-C", "0", "-F", str(dry_full), SF, str(SRC)]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr[-500:]}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes", flush=True)

dry_audio, sr = read_wav(str(dry_full))          # [n, 2]
raw_len = dry_audio.shape[0] / sr
dry_audio = trim_tail(dry_audio, sr)
trim_len = dry_audio.shape[0] / sr
print(f"Dry: raw={raw_len:.3f}s -> trimmed={trim_len:.3f}s", flush=True)

# 2. Dry stems via RenderPipeline
print("Rendering dry stems with RenderPipeline...", flush=True)
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} stems: {list(stems_raw.keys())}", flush=True)

# 3. FDN reverb (absolute layer) on full mix
tail_pad = int(FDN_TAIL_S * SR)
padded = np.vstack([dry_audio, np.zeros((tail_pad, 2), dtype=np.float32)])

fdn = FDN(sample_rate=SR, n_delays=N_DELAYS)
fdn.set(size=SIZE, decay=DECAY, brightness=BRIGHTNESS, modulation=MODULATION,
        width=WIDTH, duck_amount=DUCK, wet_dry=WET_DRY)
print("Applying FDN reverb (absolute layer)...", flush=True)
wet_mixed = fdn.process(padded.astype(np.float32))

# 4. Master
print("Mastering: normalize_to_lufs(-14) + Limiter(-1 dBFS)...", flush=True)
lufs_norm = normalize_to_lufs(wet_mixed, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_tm = limiter.process(lufs_norm)

final_wav = OUT / "SP032-fdn-le-cercle-de-l-agent.wav"
final_ogg = OUT / "SP032-fdn-le-cercle-de-l-agent.ogg"
write_wav(str(final_wav), final_tm, SR, normalize=False)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)", flush=True)

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)", flush=True)

# 5. Per-stem wet copies (same FDN config, same trim)
print("Applying FDN to dry stems...", flush=True)
for name, path in stems_raw.items():
    s_audio, s_sr = read_wav(str(path))
    if s_audio.ndim == 1:
        s_audio = np.column_stack([s_audio, s_audio])
    s_audio = trim_tail(s_audio, s_sr)
    s_pad = int(FDN_TAIL_S * s_sr)
    s_padded = np.vstack([s_audio, np.zeros((s_pad, s_audio.shape[1]), dtype=np.float32)])
    s_fdn = FDN(sample_rate=s_sr, n_delays=N_DELAYS)
    s_fdn.set(size=SIZE, decay=DECAY, brightness=BRIGHTNESS, modulation=MODULATION,
              width=WIDTH, duck_amount=DUCK, wet_dry=WET_DRY)
    s_wet = s_fdn.process(s_padded.astype(np.float32))
    write_wav(str(STEMS_WET / f"{name}_FDN.wav"), s_wet, s_sr, normalize=False)
print(f"Wrote {len(stems_raw)} wet stems to {STEMS_WET}", flush=True)

# 6. Verification
measured_lufs = float(measure_lufs(final_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_tm)))
mono_mix = 0.5 * (final_tm[:, 0] + final_tm[:, 1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
L = final_tm[:, 0]; R = final_tm[:, 1]
num = float(np.sum(L * R)); den = math.sqrt(float(np.sum(L * L)) * float(np.sum(R * R))) + 1e-12
mono_corr = float(num / den)
print(f"Master Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, "
      f"Silence={silence_ratio:.2f}%, MonoCorr={mono_corr:.3f}", flush=True)


def pitch_verify(audio, pcs):
    if audio.ndim == 1:
        mono = audio
    else:
        mono = 0.5 * (audio[:, 0] + audio[:, 1])
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
        if not np.any(mask):
            continue
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


hit_rate, mean_he, valid_windows = pitch_verify(final_tm, SRC_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio, SRC_PCS)
he_retention = (mean_he / dry_he) if dry_he > 0 else 0.0

pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_retention >= 0.40) else "FAIL"
print(f"Pitch Verification: valid={valid_windows}, hits={hit_rate:.4f}, mean_HE_wet={mean_he:.4f}", flush=True)
print(f"Dry reference: hit={dry_hit:.4f}, mean_HE_dry={dry_he:.4f}, HE_retention={he_retention:.3f}", flush=True)
print(f"Pitch Verdict: {pitch_verdict}", flush=True)

rms = float(np.sqrt(np.mean(mono_mix ** 2)))
print(f"Overall RMS: {rms:.4f}, silence: {silence_ratio:.2f}%", flush=True)

# 7. Write analysis + provenance
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr, "rms": rms,
    "valid_windows": valid_windows, "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he, "pitch_verdict": pitch_verdict,
    "dry_mean_harmonic_energy": dry_he, "he_retention": he_retention,
    "dry_raw_s": raw_len, "dry_trimmed_s": trim_len,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-15",
    "seed": SEED,
    "method": "SP-032",
    "method_module": "sound.effects.fdn_reverb",
    "method_desc": "Feedback Delay Network Reverb (Rev Ocean Tidal-style)",
    "params": {
        "n_delays": N_DELAYS, "size": SIZE, "decay": DECAY,
        "brightness": BRIGHTNESS, "modulation": MODULATION, "width": WIDTH,
        "duck_amount": DUCK, "wet_dry": WET_DRY, "fs": SR,
        "trim_tail_s": TRIM_TAIL_S, "fdn_tail_s": FDN_TAIL_S,
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
(ANALYSIS / "select_20261015.json").write_text(json.dumps({
    "date": "2026-10-15", "method": "SP-032",
    "method_module": "sound.effects.fdn_reverb",
    "source_midi": str(SRC),
    "registry_total": 48,
}, indent=2))

print("Done.", flush=True)
