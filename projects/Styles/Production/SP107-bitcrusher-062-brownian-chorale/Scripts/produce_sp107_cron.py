# -*- coding: utf-8 -*-
"""SP-107 Bit Crusher / Fidelity Reducer production pass (absolute layer).

Source : Styles/Experimental/062-brownian-chorale/MIDI/062-brownian-chorale.mid
         (8-bar 4-voice Brownian chorale, C natural minor, 84 BPM, 4/4,
          480 TPB, 3 flute voices (prog 74, ch 0/1/2) + fingered bass
          (prog 33, ch 3), 96 notes = 12/bar, all duration 456 ticks).
Method : SP-107 -> sound.effects.bit_crusher (BitCrusher, Modbap Fidelity
         Theory-style). ABSOLUTE layer: linked sample-rate/bit-depth "fidelity
         coordinate" applied to the whole FluidSynth dry render; no new notes.

Pre-flight: 3-rule audit -> already clean (0 off-grid, 0 out-of-scale,
         0 out-of-chord, zero-drift 15360 tick tracks) -> NO rework needed.
"""
import hashlib
import json
import os
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.bit_crusher import BitCrusher
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter, target_for_style

SRC = Path("/opt/data/repos/musicom/projects/Styles/Experimental/"
           "062-brownian-chorale/MIDI/062-brownian-chorale.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP107-bitcrusher-062-brownian-chorale")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
TPB = 480
BPM = 84.0
BAR = 1920
N_BARS = 8
TOTAL_TICKS = BAR * N_BARS          # 15360
SEED = 20261103
GRID = 240                          # 8th note

# C natural minor scale pitch classes: C D Eb F G Ab Bb
CMIN = {0, 2, 3, 5, 7, 8, 10}

# per-bar chord (from the 4-voice sonority) — root, chord tones
PROG = {
    0: ("Cm", {0, 3, 7}),
    1: ("Ab", {0, 3, 8}),
    2: ("Eb", {3, 7, 10}),
    3: ("Bb", {5, 10}),
    4: ("Cm", {0, 3, 7}),
    5: ("Ab", {3, 8}),
    6: ("Eb", {3, 7}),
    7: ("Cm", {0, 3, 7}),
}

SF = discover_soundfont()
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


def parse_notes(path):
    mid = mido.MidiFile(str(path))
    tpb = mid.ticks_per_beat
    notes = []
    for tr in mid.tracks:
        t = 0
        active = {}
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                active[m.note] = (t, m.velocity)
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                if m.note in active:
                    st, vel = active.pop(m.note)
                    if m.note > 0:
                        notes.append({"pitch": m.note, "vel": vel, "start": st, "end": t})
    return tpb, notes


def audit(notes):
    grid_off = out_scale = out_chord = 0
    for n in notes:
        p, st = n["pitch"], n["start"]
        pc = p % 12
        bar = min(st // BAR, N_BARS - 1)
        if st % GRID != 0:
            grid_off += 1
        if pc not in CMIN:
            out_scale += 1
        if pc not in PROG[bar][1]:
            out_chord += 1
    return {"grid_off": grid_off, "out_scale": out_scale, "out_chord": out_chord,
            "total_notes": len(notes)}


def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
        x = np.frombuffer(data, dtype=np.int16).astype(np.float64) / 32768.0
        if nch == 1:
            return np.vstack([x, x]), sr
        return x.reshape(-1, nch).T, sr


def write_wav(p, audio, sr=SR):
    audio = np.clip(np.asarray(audio, dtype=np.float64), -1.0, 1.0)
    if audio.ndim == 1:
        nch, inter = 1, audio
    elif audio.shape[0] == 2:
        nch, inter = 2, audio.T.reshape(-1)      # channel-major (2, N)
    else:
        nch, inter = 2, audio.reshape(-1)        # time-major (N, 2)
    data = (inter * 32767.0).astype(np.int16).tobytes()
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)


def sha256(p):
    h = hashlib.sha256()
    with open(str(p), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ===========================================================================
# 1. Pre-flight audit (before) + copy source
# ===========================================================================
shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))
shutil.copy2(str(SRC), str(MIDIDIR / "composition.mid"))  # already clean, no rework
tpb, src_notes = parse_notes(SRC)
before = audit(src_notes)
print("PREFLIGHT before:", before)

# NO rework needed — assert the clean state.
assert before["grid_off"] == 0, "unexpected off-grid onsets"
assert before["out_scale"] == 0, "unexpected out-of-scale notes"
assert before["out_chord"] == 0, "unexpected out-of-chord notes"

# zero-drift: all note tracks equal length
track_lens = []
mid = mido.MidiFile(str(SRC))
for tr in mid.tracks:
    t = 0
    for m in tr:
        t += m.time
    track_lens.append(t)
note_lens = track_lens[1:]
print("track lengths (ticks):", track_lens, "note tracks equal:", len(set(note_lens)) == 1)
assert len(set(note_lens)) == 1, "zero-drift violation"

after = dict(before)
(ANALYSIS / "rework_audit.json").write_text(json.dumps({
    "before": before, "after": after,
    "rework": "NONE — source 062-brownian-chorale already passes the 3-rule "
              "gate (0 off-grid, 0 out-of-scale, 0 out-of-chord, zero-drift "
              "15360-tick tracks). composition.mid is a byte copy of source.",
}, indent=2))

# ===========================================================================
# 2. Dry render (FluidSynth) + stems
# ===========================================================================
print("SoundFont:", SF)


def render(midi_path, out_wav):
    r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                        "-F", str(out_wav), SF, str(midi_path)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size < 1000:
        raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
    return out_wav


dry_wav = OUT / "dry_full_mix_reference.wav"
render(MIDIDIR / "composition.mid", dry_wav)
print("dry reference:", dry_wav.stat().st_size, "bytes")

pipe = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
dry_stems_raw = pipe.render_stems(str(MIDIDIR / "composition.mid"), str(STEMS_DRY), format="wav")
print("dry stems:", sorted(dry_stems_raw.keys()))

# ===========================================================================
# 3. SP-107 Bit Crusher — absolute layer over the full dry mix
# ===========================================================================
dry_audio, _sr = read_wav(dry_wav)
print("dry mix shape", dry_audio.shape, "dur %.2fs" % (dry_audio.shape[1] / SR))

# fidelity coordinate (linked SR/bit-depth): 0.30 -> 18.6 kHz / 9-bit
FIDELITY = 0.30
MODE = "worn"
RING = 0.15

crush = BitCrusher(sample_rate=SR)
crush.fidelity = FIDELITY
crush.config.mode = MODE
crush.config.ring = RING
crush.config.mix = 1.0
print("fidelity coordinate:", crush.fidelity,
      "-> sample_rate_hz=%d bit_depth=%d" % (crush.config.sample_rate_hz, crush.config.bit_depth))

# process expects time-major (N,2); read_wav gives channel-major (2,N)
x_tm = dry_audio.T.copy()
wet_tm = crush.process(x_tm)
wet = np.column_stack([wet_tm[:, 0], wet_tm[:, 1]]).T   # back to (2, N)

wet_stem = STEMS_DRY / "full_mix_CRUSH.wav"
write_wav(wet_stem, wet)
print("crushed wav:", wet_stem.stat().st_size, "bytes")

# ===========================================================================
# 4. Master bus
# ===========================================================================
TARGET_LUFS = target_for_style("experimental")
wet_tm = wet.T                                      # time-major (N, 2)
mix_lufs = normalize_to_lufs(wet_tm, target_lufs=TARGET_LUFS, sample_rate=SR)
final = Limiter(threshold_db=-1.0, release_ms=80.0).process(mix_lufs)   # (N, 2)
lufs_val = float(measure_lufs(final, SR))
peak_val = float(np.max(np.abs(final)))
print("LUFS=%.2f peak=%.4f dur=%.2fs" % (lufs_val, peak_val, final.shape[0] / SR))

WET_WAV = OUT / "SP107-bitcrusher-062-brownian-chorale.wav"
write_wav(WET_WAV, final)
print("wet WAV %d B" % WET_WAV.stat().st_size)

WET_OGG = OUT / "SP107-bitcrusher-062-brownian-chorale.ogg"
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(WET_WAV),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(WET_OGG)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and WET_OGG.stat().st_size > 10000, "ogg encode failed"
print("OGG %d B" % WET_OGG.stat().st_size)

# ===========================================================================
# 5. Verification
# ===========================================================================
final_cm = final.T                                  # (2, N)
mono = 0.5 * (final_cm[0] + final_cm[1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print("silence=%.2f%% rms=%.4f" % (silence_pct, rms))


def pitch_verify(audio_2n, pcs):
    m = 0.5 * (audio_2n[0] + audio_2n[1])
    wl = int(0.5 * SR)
    nw = len(m) // wl
    hits = valid = 0
    he_list = []
    for w in range(nw):
        seg = m[w * wl:(w + 1) * wl]
        if np.max(np.abs(seg)) < 0.01:
            continue
        valid += 1
        win = np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg * win))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
        mask = (freqs >= 50.0) & (freqs <= 1000.0)
        sub, subf = spec[mask], freqs[mask]
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


dry_audio_mix, _sr2 = read_wav(dry_wav)
hit_rate, he_mean, valid = pitch_verify(final_cm, CMIN)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio_mix, CMIN)
he_retention = (he_mean / dry_he) if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.30) else "FAIL"
print("Pitch verify: valid=%d hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | retention=%.3f -> %s"
      % (valid, hit_rate, he_mean, dry_hit, dry_he, he_retention, pitch_verdict))

# ===========================================================================
# 6. Provenance + stats
# ===========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": lufs_val, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "hit_rate": hit_rate, "mean_harmonic_energy": he_mean, "valid_windows": valid,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
    "pitch_verdict": pitch_verdict,
    "fidelity": FIDELITY, "mode": MODE, "ring": RING,
    "crush_sr_hz": int(crush.config.sample_rate_hz),
    "crush_bit_depth": int(crush.config.bit_depth),
    "n_stems": len(dry_stems_raw),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-03",
    "seed": SEED,
    "method": "SP-107",
    "method_module": "sound.effects.bit_crusher",
    "method_desc": "Bit Crusher / Fidelity Reducer — linked sample-rate/bit-depth macro, Iron/Worn character voicing, aliasing foldover emphasis (Modbap Fidelity Theory-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "fidelity": FIDELITY, "mode": MODE, "ring": RING, "mix": 1.0,
        "crush_sample_rate_hz": int(crush.config.sample_rate_hz),
        "crush_bit_depth": int(crush.config.bit_depth),
        "carrier": "FluidSynth SP-001 (3x flute 74 + fingered bass 33)",
        "target_lufs": TARGET_LUFS, "ceiling_db": -1.0,
    },
    "source_midi": str(SRC),
    "normalized_midi": str(MIDIDIR / "composition.mid"),
    "source_bpm": BPM,
    "source_pitch_classes": sorted(CMIN),
    "progression": [PROG[b][0] for b in range(N_BARS)],
    "rework": "NONE (source already clean)",
    "output_wav": str(WET_WAV),
    "output_ogg": str(WET_OGG),
    "lufs": lufs_val, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": he_mean,
    "dry_he": dry_he, "he_retention": he_retention,
    "preflight_before": before, "preflight_after": after,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp107_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")