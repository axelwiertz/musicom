# -*- coding: utf-8 -*-
"""SP-154 Wax Theory (Groove-Velocity Vinyl Model) production pass.

Source : Styles/Experimental/052-perlin-chebyshev (Method 040 Perlin noise +
         SP-019 Chebyshev waveshaping). D natural minor, 100 BPM, 4/4,
         480 TPB, 12 bars (3 sections x 4) = 23040 ticks ~ 28.8 s. 3 voices:
         Lead flute (ch0), New Age Pad (ch1), Electric Bass (ch2). Harmony =
         static Dm7 across all bars. Pre-flight found 34/48 lead onsets
         off-chord (G/Bb/E over Dm7) -> chord-tone quantized to {D,F,A,C};
         re-audit clean (0 off-grid / 0 out-of-scale / 0 out-of-chord /
         zero-drift). Raw kept as phase1 sidecar.

Method : SP-154 -> sound.effects.wax_theory_vinyl (Modbap Wax Theory-style
         groove-velocity vinyl playback model). ABSOLUTE layer: one vinyl
         playback chain applied across the whole dry mix. side=0.3 (mid-groove
         -> 42 cm/s), HiFi stylus, dust on, wear 0.4.

Pipeline: source MIDI -> 3-rule pre-flight audit (grid/harmony/zero-drift)
          -> rework (chord-tone quantize lead) -> dry FluidSynth (FX off)
          -> SP-154 WaxTheory vinyl (per-channel) -> master() (target LUFS,
          -1 dBTP) -> WAV + Opus OGG -> pitch/silence/RMS verification ->
          provenance.json + REPORT.md.
"""
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import mido

from sound.effects.wax_theory_vinyl import WaxTheory
from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav

# ---- paths -------------------------------------------------------------
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP154-wax-theory-vinyl-052-perlin-chebyshev")
SRC = OUT / "MIDI" / "052-perlin-chebyshev.mid"   # reworked, clean
PHASE1 = OUT / "MIDI" / "052-perlin-chebyshev-phase1.mid"
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
SEED = 20261112
STYLE = "Experimental"     # -> target_for_style -> -14.0 fallback
TARGET_LUFS = target_for_style(STYLE)
CEILING_DB = -1.0

# D natural minor scale pcs (key of the source)
SCALE_PCS = {2, 4, 5, 7, 9, 10, 0}
# Dm7 chord tones (post-rework audible vocabulary) = {D,F,A,C}
CHORD_PCS = {2, 5, 9, 0}
# static Dm7 chord tones per bar (12 bars)
CHORD_TONES = [CHORD_PCS] * 12

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


# =========================================================================
# 1. Read tempo / structure
# =========================================================================
mf_src = mido.MidiFile(str(SRC))
bpm = 100.0
for tr in mf_src.tracks:
    for m in tr:
        if m.type == "set_tempo":
            bpm = round(60000000.0 / m.tempo, 2)
print("BPM =", bpm)

# =========================================================================
# 2. Pre-flight 3-rule audit on the REWORKED midi (already clean, re-verify)
# =========================================================================
def audit(path):
    mf = mido.MidiFile(str(path))
    grid_off = 0
    out_scale = 0
    out_chord = 0
    total_notes = 0
    track_ends = []
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
                if pc not in SCALE_PCS:
                    out_scale += 1
                bar = min(t // BAR, 11)
                if pc not in CHORD_TONES[bar]:
                    out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale,
            "out_chord": out_chord, "total_notes": total_notes,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends))}


before = audit(SRC)
print("== pre-flight audit (reworked MIDI) ==")
print(before)
assert before["grid_off"] == 0, "grid sync FAIL"
assert before["out_scale"] == 0, "out-of-scale FAIL"
assert before["out_chord"] == 0, "out-of-chord FAIL"
assert before["zero_drift"], "zero-drift FAIL"
print("PRE-FLIGHT PASS (grid 0 / out-of-scale 0 / out-of-chord 0 / zero-drift)")

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
# 4. SP-154 WaxTheory vinyl chain (per-channel)
# =========================================================================
VINYL_PARAMS = dict(fmt="LP", stylus="HiFi", side=0.30, dust=True,
                    wear=0.40, wow_depth=0.50, sr=SR, seed=SEED)
wx = WaxTheory(**VINYL_PARAMS)
print("== SP-154 physical state ==")
print("  velocity      = %.2f cm/s" % wx.velocity_cms())
print("  rpm           = %.3f" % wx.rpm())
print("  tracing_drive = %.4f" % wx.tracing_drive())
print("  bandwidth     = %.0f Hz" % wx.bandwidth_hz())
print("  noise_level   = %.5f" % wx.noise_level())

# same instance per channel: deterministic wow/flutter coherent across L/R,
# surface-noise RNG advances -> decorrelated L/R ticks (realistic vinyl).
wetL = wx.process(dry_audio[:, 0])
wetR = wx.process(dry_audio[:, 1])
wet = np.column_stack([wetL, wetR]).astype(np.float32)
print("wet (pre-master) peak:", float(np.max(np.abs(wet))))

# =========================================================================
# 5. Master (target LUFS, ceiling -1 dBTP)
# =========================================================================
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..."
      % (TARGET_LUFS, CEILING_DB))
mastered, rep = master(wet, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                       sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = OUT / "SP154-wax-theory-vinyl-052-perlin-chebyshev.wav"
final_ogg = OUT / "SP154-wax-theory-vinyl-052-perlin-chebyshev.ogg"
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


# wet pitch verify (against Dm7 chord-tone pcs)
wet_hit, wet_he, wet_valid = pitch_verify(mastered, CHORD_PCS)
# dry pitch verify (reference)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio, CHORD_PCS)
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
    "vinyl_params": VINYL_PARAMS,
    "velocity_cms": wx.velocity_cms(), "tracing_drive": wx.tracing_drive(),
    "bandwidth_hz": wx.bandwidth_hz(), "noise_level": wx.noise_level(),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-12",
    "seed": SEED,
    "method": "SP-154",
    "method_module": "sound.effects.wax_theory_vinyl",
    "method_desc": "Groove-Velocity Vinyl Model — Side control = 51->21 cm/s "
                   "linear velocity driving 2nd-harmonic tracing distortion, "
                   "v/(2lambda) bandwidth limit, wow/flutter, LP/45/78 formats, "
                   "HiFi/DJ/Worn stylus profiles, dust ticks + scratch pop + "
                   "bearing rumble, platter brake (Modbap Wax Theory-style)",
    "layer": "ABSOLUTE - one vinyl playback chain applied to the whole piece",
    "params": dict(VINYL_PARAMS, stop_at=None, target_lufs=TARGET_LUFS,
                   ceiling_db=CEILING_DB),
    "source_midi": str(SRC),
    "phase1_midi": str(PHASE1),
    "source_bpm": bpm,
    "source_key": "D natural minor",
    "source_pitch_classes": sorted(SCALE_PCS),
    "source_form": "ABC (3 sections x 4 bars), static Dm7 harmony",
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
