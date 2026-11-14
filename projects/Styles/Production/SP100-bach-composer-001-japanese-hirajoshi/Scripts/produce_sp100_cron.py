# -*- coding: utf-8 -*-
"""SP-100 B.A.C.H. Composition Generator production pass (2026-11-14).

Source : Styles/Japanese/001-japanese-hirajoshi — Japanese hōgaku study in
         D hirajoshi (D-Eb-G-Ab-C, pcs {0,2,3,7,8}), 70 BPM, 4/4, 480 TPB,
         16 bars = 30720 ticks ~ 54.86 s.

Method : SP-100 -> sound.generators.bach_composer (Kaona B.A.C.H.-style,
         11 algorithmic composition engines). SP-100 is a GENERATOR method:
         it produces note events, not a timbral effect. As an ABSOLUTE layer
         it re-composes the whole piece in the source's key (D hirajoshi) and
         tempo (70 BPM); no source MIDI notes survive — only key/tempo/genre
         context is inherited (same convention as SP-098).

         Engine used: TINTINNABULI (Arvo Pärt-style) — a melodic voice plus
         tintinnabular voices drawn from a scale-tone triad (D-G-C quartal
         stack, all hirajoshi tones). Three tintinnabular voices (alto / high
         / bass) are derived from the SAME hirajoshi melody at different
         registers, giving a static, bell-like "ma" texture idiomatic to the
         Japanese source.

Pipeline: source MIDI -> 3-rule pre-flight audit (grid/harmony/zero-drift)
          -> B.A.C.H. TINTINNABULI generation (4 voices) -> phase1 raw export
          -> Phase-2 rules (voice-leading octave smoothing) -> final MIDI
          (zero-drift validate()) -> FluidSynth GM dry render -> master()
          (target LUFS, -1 dBTP) -> WAV + Opus OGG -> pitch/silence/RMS
          verification -> stems -> provenance.json + REPORT.md.
"""
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import mido

from sound.generators.bach_composer import tintinnabuli, BachEvent
from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.musicom_workflow import _unit_from_events

# ---- paths -------------------------------------------------------------
ROOT = Path("/opt/data/repos/musicom/projects/Styles")
OUT = ROOT / "Production" / "SP100-bach-composer-001-japanese-hirajoshi"
SRC = ROOT / "Japanese/001-japanese-hirajoshi/MIDI/japanese-hirajoshi.mid"
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
SEED = 20261114
STYLE = "Japanese"         # -> target_for_style -> fallback -14.0
TARGET_LUFS = target_for_style(STYLE)
CEILING_DB = -1.0
TOTAL_BARS = 16
TOTAL_TICKS = TOTAL_BARS * BAR   # 30720

# D hirajoshi scale pcs (key of the source)
SCALE_PCS = {0, 2, 3, 7, 8}
# Tintinnabuli triad (D-G-C quartal, all hirajoshi tones) pcs = {2,7,0}
TRIAD_PCS = {0, 2, 7}

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

R = random.Random(SEED)

# ---- source metadata ---------------------------------------------------
mf_src = mido.MidiFile(str(SRC))
bpm = 70.0
for tr in mf_src.tracks:
    for m in tr:
        if m.type == "set_tempo":
            bpm = round(60000000.0 / m.tempo, 2)
print("source BPM =", bpm, "| length_s =", round(mf_src.length, 2))


# =========================================================================
# 1. Pre-flight 3-rule audit on the SOURCE midi (informational)
# =========================================================================
def audit(path, scale_pcs, chord_tones_by_bar=None):
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
                if pc not in scale_pcs:
                    out_scale += 1
                if chord_tones_by_bar is not None:
                    bar = min(t // BAR, len(chord_tones_by_bar) - 1)
                    if pc not in chord_tones_by_bar[bar]:
                        out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale,
            "out_chord": out_chord, "total_notes": total_notes,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends))}


src_audit = audit(SRC, SCALE_PCS)
print("== source pre-flight audit ==")
print(src_audit)

# =========================================================================
# 2. B.A.C.H. TINTINNABULI generation (SP-100)
# =========================================================================
# 16-bar D hirajoshi melody (4 phrases x 4 bars = 30720 ticks exactly)
MELODY = [
    (62, 960), (67, 960), (72, 1920), (68, 960), (63, 960), (62, 1920),
    (63, 960), (68, 960), (72, 960), (74, 1920), (72, 960), (68, 960), (63, 960),
    (62, 960), (63, 480), (67, 480), (68, 960), (72, 960), (74, 480), (75, 480),
    (74, 960), (72, 960), (67, 960),
    (68, 960), (67, 960), (63, 960), (62, 1920), (74, 960), (67, 960), (62, 960),
]
assert sum(d for _, d in MELODY) == TOTAL_TICKS, sum(d for _, d in MELODY)

mel_low = [(p - 24, d) for p, d in MELODY]   # bass register melody
mel_high = [(p + 12, d) for p, d in MELODY]  # upper register melody

# voice 0: melody (D hirajoshi)
m_ev = tintinnabuli(melody=MELODY, triad=(0, 5, 10), root_pitch=62,
                    num_voices=1, r=R)
# voice 1: tintinnabular alto (D/G/C near melody)
a_ev = tintinnabuli(melody=MELODY, triad=(0, 5, 10), root_pitch=62,
                    num_voices=2, r=R)
# voice 2: tintinnabular high (D/G/C octave up)
h_ev = tintinnabuli(melody=mel_high, triad=(0, 5, 10), root_pitch=74,
                    num_voices=2, r=R)
# voice 3: tintinnabular bass (D/G/C low)
b_ev = tintinnabuli(melody=mel_low, triad=(0, 5, 10), root_pitch=38,
                    num_voices=2, r=R)

voice_raw = {}
for e in m_ev:
    if e.voice == 0:
        voice_raw.setdefault(0, []).append(e)
for e in a_ev:
    if e.voice == 1:
        voice_raw.setdefault(1, []).append(e)
for e in h_ev:
    if e.voice == 1:
        voice_raw.setdefault(2, []).append(e)
for e in b_ev:
    if e.voice == 1:
        voice_raw.setdefault(3, []).append(e)

for v in range(4):
    print("voice %d raw notes=%d pcs=%s" % (
        v, len(voice_raw[v]),
        sorted(set(e.pitch % 12 for e in voice_raw[v]))))

INSTRUMENTS = [
    ("Shakuhachi", 77, 0),   # GM 77 Shakuhachi — melody
    ("Koto", 107, 1),        # GM 107 Koto — tintinnabular alto
    ("Strings", 49, 2),      # GM 49 String Ensemble 2 — tintinnabular high
    ("Bass", 43, 3),         # GM 43 Contrabass — tintinnabular bass
]


def events_to_musicevents(bach_events, voice_idx):
    out = []
    for e in sorted(bach_events, key=lambda x: x.start_tick):
        out.append(MusicEvent(pitch=int(e.pitch), volume=int(e.velocity),
                              start_tick=int(e.start_tick),
                              end_tick=int(e.start_tick + e.duration_ticks)))
    return out


def build_midi(voice_events, out_path):
    """voice_events: {voice_idx: [MusicEvent]}. Zero-drift via _unit_from_events."""
    comp = UnitMatrixComposer(bpm=round(bpm), ticks_per_beat=TPB, beats_per_bar=4)
    comp.create_matrix(num_voices=4, num_sections=1)
    for name, prog, ch in INSTRUMENTS:
        comp.add_voice(name, program=prog, channel=ch)
    comp.add_section("Piece", bars=TOTAL_BARS)
    for vi in range(4):
        evs = events_to_musicevents(voice_events[vi], vi)
        comp.fill_voice_section(
            INSTRUMENTS[vi][0], "Piece",
            _unit_from_events(evs, TOTAL_TICKS))
    ok, msg = comp.validate()
    assert ok, "zero-drift FAIL: %s" % msg
    comp.to_midi(str(out_path))
    return comp


# ---- phase1: raw engine output (pre voice-leading) ----------------------
build_midi(voice_raw, MIDIDIR / "001-japanese-hirajoshi-phase1.mid")
print("phase1 MIDI written")

# ---- phase2: voice-leading octave smoothing (rules post-processing) -----
def smooth_voice_leading(voice_events):
    smoothed = {}
    for vi in range(4):
        prev = None
        out = []
        for e in sorted(voice_events[vi], key=lambda x: x.start_tick):
            p = e.pitch
            if prev is not None:
                while p - prev > 12:
                    p -= 12
                while prev - p > 12:
                    p += 12
            e2 = BachEvent(pitch=max(0, min(127, p)), start_tick=e.start_tick,
                           duration_ticks=e.duration_ticks, velocity=e.velocity,
                           voice=vi)
            out.append(e2)
            prev = p
        smoothed[vi] = out
    return smoothed


voice_final = smooth_voice_leading(voice_raw)
build_midi(voice_final, MIDIDIR / "001-japanese-hirajoshi.mid")
print("final MIDI written")

# =========================================================================
# 3. Re-audit final MIDI (3-rule gate — MUST be clean)
# =========================================================================
# static D-root chord context: every bar allows D-G-C tintinnabular tones plus
# hirajoshi melody tones -> the full hirajoshi scale. Chord tones per bar =
# hirajoshi scale itself (single static tonic region, 16 bars).
CHORD_TONES = [SCALE_PCS] * TOTAL_BARS
final_audit = audit(MIDIDIR / "001-japanese-hirajoshi.mid", SCALE_PCS, CHORD_TONES)
phase1_audit = audit(MIDIDIR / "001-japanese-hirajoshi-phase1.mid", SCALE_PCS,
                     CHORD_TONES)
print("== final re-audit ==")
print(final_audit)
assert final_audit["grid_off"] == 0, "grid sync FAIL"
assert final_audit["out_scale"] == 0, "out-of-scale FAIL"
assert final_audit["out_chord"] == 0, "out-of-chord FAIL"
assert final_audit["zero_drift"], "zero-drift FAIL"
print("RE-AUDIT PASS (grid 0 / out-of-scale 0 / out-of-chord 0 / zero-drift)")

# =========================================================================
# 4. FluidSynth dry render (SP-001 carrier)
# =========================================================================
SF = discover_soundfont()
assert SF and os.path.exists(SF), "SoundFont missing: %r" % SF
print("SoundFont:", SF)

final_midi = MIDIDIR / "001-japanese-hirajoshi.mid"
dry_wav = AUD / "dry_full_mix_sp001_reference.wav"


def fluidsynth_render(midi_path, out_wav):
    r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                        "-F", str(out_wav), SF, str(midi_path)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size < 1000:
        raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
    return out_wav


fluidsynth_render(final_midi, dry_wav)
print("dry WAV:", dry_wav.stat().st_size, "bytes")

dry_audio, _sr = read_wav(str(dry_wav))
if dry_audio.ndim == 1:
    dry_audio = np.column_stack([dry_audio, dry_audio])
dry_audio = np.asarray(dry_audio, dtype=np.float32)
assert _sr == SR, "unexpected sample rate %r" % _sr
print("dry audio shape:", dry_audio.shape,
      "peak", float(np.max(np.abs(dry_audio))))

# =========================================================================
# 5. Master (target LUFS, ceiling -1 dBTP)
# =========================================================================
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..."
      % (TARGET_LUFS, CEILING_DB))
mastered, rep = master(dry_audio, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                       sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = AUD / "SP100-bach-composer-001-japanese-hirajoshi.wav"
final_ogg = AUD / "SP100-bach-composer-001-japanese-hirajoshi.ogg"
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


final_hit, final_he, final_valid = pitch_verify(mastered, SCALE_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio, SCALE_PCS)
he_retention = final_he / dry_he if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (final_hit >= 0.60 and final_he >= 0.30) else "FAIL"
print("pitch verify: final hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | "
      "HE retention=%.3f -> %s"
      % (final_hit, final_he, dry_hit, dry_he, he_retention, pitch_verdict))

# =========================================================================
# 7. Stems (per-track WAV)
# =========================================================================
try:
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID,
                              sample_rate=SR)
    stems = pipeline.render_stems(str(final_midi), str(STEMS), format="wav")
    print("stems:", list(stems))
    stems_ok = True
except Exception as exc:
    print("stems FAILED:", exc)
    stems = {}
    stems_ok = False

# =========================================================================
# 8. Artifacts
# =========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "final_hit_rate": final_hit, "final_mean_harmonic_energy": final_he,
    "dry_hit_rate": dry_hit, "dry_mean_harmonic_energy": dry_he,
    "he_retention": he_retention,
    "valid_windows": final_valid, "pitch_verdict": pitch_verdict,
    "target_lufs": TARGET_LUFS, "bpm": bpm,
    "stems_ok": stems_ok, "n_stems": len(stems),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-14",
    "seed": SEED,
    "method": "SP-100",
    "method_module": "sound.generators.bach_composer",
    "method_desc": "B.A.C.H. Composition Generator — 11 algorithmic composition "
                   "engines: FUGUE/CANON/PROBA/TINTINNABULI/MINIMAL/CELLULAR/"
                   "TREE/MOTIF/HYBRID/GROOVE/GROOVE_MIX (Kaona B.A.C.H.-style)",
    "layer": "ABSOLUTE - generator re-composes the whole piece in the source's "
             "key/tempo; TINTINNABULI engine (Arvo Pärt-style) drives 4 voices",
    "engine": "tintinnabuli",
    "engine_params": {"triad": [0, 5, 10], "triad_desc": "D-G-C quartal (all hirajoshi)",
                      "melody_pcs": sorted(SCALE_PCS), "total_ticks": TOTAL_TICKS,
                      "total_bars": TOTAL_BARS},
    "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    "source_midi": str(SRC),
    "source_bpm": bpm,
    "source_key": "D hirajoshi (D-Eb-G-Ab-C)",
    "source_pitch_classes": sorted(SCALE_PCS),
    "source_form": "16 bars (4 phrases x 4 bars), static D-root hirajoshi region",
    "output_midi": str(final_midi),
    "phase1_midi": str(MIDIDIR / "001-japanese-hirajoshi-phase1.mid"),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict,
    "final_hit_rate": final_hit, "final_he": final_he,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
    "source_preflight": src_audit,
    "phase1_audit": phase1_audit,
    "final_audit": final_audit,
    "stems_ok": stems_ok, "n_stems": len(stems),
    "instruments": INSTRUMENTS,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

# copy this script for reproducibility
import shutil
shutil.copy(__file__, SCRIPTS / "produce_sp100_cron.py")

print("DONE")
