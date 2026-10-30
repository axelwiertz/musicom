# -*- coding: utf-8 -*-
"""SP-092 Multiband Saturator (Kreuzberg Oberton-style) production pass.

Source : Styles/Experimental/032-prime-fractal-full
         daily-2026-06-26_experimental_032-prime-fractal-v6.mid
         (monophonic Acoustic Grand Piano prime-fractal line, ABCBA form,
          120 BPM, 4/4, 480 TPB, 65 notes, 10200 ticks = ~10.62 s; three
          harmonic centres A:[60,63,67,71,72] C-based, B:[65,68,72,76,77]
          F-based, C:[55,59,62,66,67] G-based; pitch-class union
          {0,2,3,4,5,6,7,8,11} = no C#/A/A#).

Method : SP-092 -> sound.effects.multiband_saturator (6-Band Multiband
         Saturator, 15 algos, per-band M/S routing). ABSOLUTE layer: one
         6-band saturator applied across the whole piece (memoryless
         nonlinearity - preserves pitch, adds harmonics).

Pipeline: source MIDI -> 3-rule pre-flight audit (grid/harmony/zero-drift)
          -> dry FluidSynth (FX off -R 0 -C 0 -g 1.2) -> SP-092 6-band
          saturator -> master() (-14 LUFS experimental fallback, -1 dBTP)
          -> WAV + Opus OGG -> pitch/silence/RMS verification -> REPORT.md.
"""
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import mido

from sound.effects.multiband_saturator import MultibandSaturator, BandConfig
from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav

# ---- paths -------------------------------------------------------------
SRC = Path("/opt/data/repos/musicom/projects/Styles/Experimental/"
           "032-prime-fractal-full/"
           "daily-2026-06-26_experimental_032-prime-fractal-v6.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP092-multiband-saturator-032-prime-fractal-full")
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

# ---- constants ---------------------------------------------------------
SR = 44100
TPB = 480
BAR = 1920                 # 4/4 bar
GRID = 120                 # 16th note
SEED = 20261030
STYLE = "Experimental"     # -> GENRE_LUFS has no "experimental" key -> -14.0
TARGET_LUFS = target_for_style(STYLE)   # -14.0 fallback
CEILING_DB = -1.0

# pitch-class union of the piece's 3 harmonic centres (no C#/A/A#)
UNION_PCS = {0, 2, 3, 4, 5, 6, 7, 8, 11}

# section harmonic sets (by bar) - A/B/C centres (transitions noted)
SECTION_PCS = {  # bar_index -> pitch classes of that section's harmonic centre
    0: {0, 3, 7, 11},      # A  C-based  [60,63,67,71,72]
    1: {5, 8, 0, 4},       # B  F-based  [65,68,72,76,77]
    2: {7, 11, 2, 6},      # C  G-based  [55,59,62,66,67]
    3: {5, 8, 0, 4},       # B  F-based
    4: {0, 3, 7, 11},      # A  C-based
    5: {0, 3, 7, 11},      # A  tail (bar 5 partial)
}

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


# =========================================================================
# 1. Read tempo / structure
# =========================================================================
mf_src = mido.MidiFile(str(SRC))
bpm = 120.0
for tr in mf_src.tracks:
    for m in tr:
        if m.type == "set_tempo":
            bpm = round(60000000.0 / m.tempo, 2)
print("BPM =", bpm, "(set_tempo)" if bpm != 120.0 else "(default 120)")

# =========================================================================
# 2. Pre-flight 3-rule audit (grid sync / harmony / zero-drift)
# =========================================================================
def audit(path):
    mf = mido.MidiFile(str(path))
    grid_off = 0
    out_scale = 0
    out_section = 0
    total_notes = 0
    track_ends = []
    pcs_seen = set()
    for tr in mf.tracks:
        chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
        is_drum = 9 in chans
        t = 0
        n_notes = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                n_notes += 1
                total_notes += 1
                if is_drum:
                    continue
                if (t % GRID) != 0:
                    grid_off += 1
                pc = m.note % 12
                pcs_seen.add(pc)
                if pc not in UNION_PCS:
                    out_scale += 1
                bar = min(t // BAR, 5)
                if pc not in SECTION_PCS[bar]:
                    # transitional note - only counts if also off the
                    # piece-wide vocabulary (already caught above)
                    out_section += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale,
            "out_section": out_section, "total_notes": total_notes,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends)),
            "pcs_seen": sorted(pcs_seen)}


before = audit(SRC)
print("== pre-flight audit ==")
print(before)
assert before["grid_off"] == 0, "grid sync FAIL"
assert before["out_scale"] == 0, "out-of-scale FAIL"
assert before["zero_drift"], "zero-drift FAIL"
# out_section counts transition notes that are still in the piece-wide
# vocabulary (bridge notes at section seams) - NOT violations. Report them,
# but they must be a small minority and always in-scale.
print("PRE-FLIGHT PASS (grid 0 / out-of-scale 0 / zero-drift; out_section=%d "
      "transitional notes, all in-piece-vocabulary)." % before["out_section"])

import shutil
shutil.copy2(str(SRC), str(MIDIDIR / "source.mid"))

# =========================================================================
# 3. Dry FluidSynth render (FX off) - SP-001 reference
# =========================================================================
SF = discover_soundfont()
assert SF and os.path.exists(SF), "SoundFont missing: %r" % SF
print("SoundFont:", SF)

dry_wav = OUT / "dry_full_mix_sp001_reference.wav"


def fluidsynth_render(midi_path, out_wav):
    r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                        "-F", str(out_wav), SF, str(midi_path)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size < 1000:
        raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
    return out_wav


fluidsynth_render(SRC, dry_wav)
print("dry WAV:", dry_wav.stat().st_size, "bytes")

dry_audio, _sr = read_wav(str(dry_wav))
if dry_audio.ndim == 1:
    dry_audio = np.column_stack([dry_audio, dry_audio])
dry_audio = np.asarray(dry_audio, dtype=np.float32)
assert _sr == SR, "unexpected sample rate %r" % _sr
print("dry audio shape:", dry_audio.shape,
      "peak", float(np.max(np.abs(dry_audio))))

# =========================================================================
# 4. SP-092 multiband saturator (piano-tuned 6-band config)
# =========================================================================
CROSSOVERS = [120.0, 400.0, 1200.0, 4000.0, 10000.0]
BAND_CONFIGS = [
    # sub band - piano lowest note G3=196Hz sits above this; bypass
    BandConfig(frequency=60, q=1.0, drive=1.0, mix=1.0, algo="bypass",
               mode="stereo"),
    # 120-400: low fundamentals (G3 196, C4 262, Eb4 311) - tube warmth
    BandConfig(frequency=250, q=1.0, drive=1.20, mix=1.0, algo="tube",
               mode="stereo"),
    # 400-1200: mid fundamentals + 1st harmonics - tanh
    BandConfig(frequency=800, q=1.0, drive=1.30, mix=1.0, algo="tanh",
               mode="stereo"),
    # 1200-4000: hammer-attack harmonics - soft clip on Mid (keep centre)
    BandConfig(frequency=2500, q=1.0, drive=1.10, mix=1.0, algo="soft_clip",
               mode="mid"),
    # 4000-10000: string/action sheen - light sine foldback
    BandConfig(frequency=6000, q=1.0, drive=0.45, mix=1.0,
               algo="sine_foldback", mode="stereo"),
    # >10000: air - bypass
    BandConfig(frequency=12000, q=1.0, drive=1.0, mix=1.0, algo="bypass",
               mode="stereo"),
]
sat = MultibandSaturator(sample_rate=SR, crossover_freqs=CROSSOVERS,
                         band_configs=BAND_CONFIGS, global_trim=0.85)
print("== SP-092 band config ==")
print(sat.summary())

wet = sat.process(dry_audio)
print("wet (pre-master) peak:", float(np.max(np.abs(wet))))

# =========================================================================
# 5. Master (target LUFS, ceiling -1 dBTP)
# =========================================================================
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..." %
      (TARGET_LUFS, CEILING_DB))
mastered, rep = master(wet, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                       sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = OUT / "SP092-multiband-saturator-032-prime-fractal-full.wav"
final_ogg = OUT / "SP092-multiband-saturator-032-prime-fractal-full.ogg"
write_wav(str(final_wav), mastered.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, \
    "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV:", final_wav.stat().st_size,
      "final OGG:", final_ogg.stat().st_size)

# =========================================================================
# 6. Verification
# =========================================================================
meas_lufs = float(measure_lufs(mastered, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered)))
mono = 0.5 * (mastered[:, 0] + mastered[:, 1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f"
      % (meas_lufs, peak_val, silence_pct, rms))


def pitch_verify(audio_tm, pcs):
    wl = int(0.5 * SR)
    nw = len(audio_tm) // wl
    hits = valid = 0
    he_list = []
    for w in range(nw):
        seg = audio_tm[w * wl:(w + 1) * wl]
        if seg.ndim > 1:
            seg = 0.5 * (seg[:, 0] + seg[:, 1])
        if np.max(np.abs(seg)) < 0.01:
            continue
        valid += 1
        win = np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg * win))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
        mask = (freqs >= 50.0) & (freqs <= 1000.0)
        sub = spec[mask]
        subf = freqs[mask]
        dom = subf[np.argmax(sub)]
        midi_val = 69.0 + 12.0 * np.log2(max(1.0, dom) / 440.0)
        pc = round(midi_val) % 12
        if pc in pcs:
            hits += 1
        tot = np.sum(spec ** 2) + 1e-12
        he = 0.0
        for h in range(1, 9):
            tf = dom * h
            hband = (freqs >= tf - 15.0) & (freqs <= tf + 15.0)
            he += np.sum(spec[hband] ** 2)
        he_list.append(float(he / tot))
    hit_rate = hits / max(1, valid)
    he_mean = float(np.mean(he_list)) if he_list else 0.0
    return hit_rate, he_mean, valid


# wet pitch verify
wet_hit, wet_he, wet_valid = pitch_verify(mastered, UNION_PCS)
# dry pitch verify (reference)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio, UNION_PCS)
he_retention = wet_he / dry_he if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (wet_hit >= 0.60 and he_retention >= 0.40) else "FAIL"
print("pitch verify: wet hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | "
      "HE retention=%.3f -> %s"
      % (wet_hit, wet_he, dry_hit, dry_he, he_retention, pitch_verdict))

# =========================================================================
# 7. Artifacts
# =========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "wet_hit_rate": wet_hit, "wet_mean_harmonic_energy": wet_he,
    "dry_hit_rate": dry_hit, "dry_mean_harmonic_energy": dry_he,
    "he_retention": he_retention,
    "valid_windows": wet_valid, "pitch_verdict": pitch_verdict,
    "target_lufs": TARGET_LUFS, "bpm": bpm,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-30",
    "seed": SEED,
    "method": "SP-092",
    "method_module": "sound.effects.multiband_saturator",
    "method_desc": "6-Band Multiband Saturator w/ 15 Selectable Algorithms & "
                   "Per-Band M/S Routing (Kreuzberg Audio Oberton-style)",
    "layer": "ABSOLUTE - one 6-band saturator applied to the whole piece",
    "params": {
        "sample_rate": SR, "bpm": bpm, "ppqn": TPB,
        "meter": "4/4", "bar_ticks": BAR,
        "crossover_freqs": CROSSOVERS,
        "global_trim": 0.85,
        "band_configs": [
            {"freq": bc.frequency, "q": bc.q, "drive": bc.drive,
             "mix": bc.mix, "algo": bc.algo, "mode": bc.mode}
            for bc in BAND_CONFIGS
        ],
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "source_bpm": bpm,
    "source_key": "prime-fractal (3 harmonic centres A/B/C; no C#/A/A#)",
    "source_pitch_classes": sorted(UNION_PCS),
    "source_form": "ABCBA",
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict,
    "wet_hit_rate": wet_hit, "wet_he": wet_he,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
    "preflight": before,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

print("DONE")
