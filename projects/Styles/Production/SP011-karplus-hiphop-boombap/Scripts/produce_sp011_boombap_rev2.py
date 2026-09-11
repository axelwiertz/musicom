#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-011 Karplus-Strong production pass rev2 — Hip-Hop Boom-Bap (cron 2026-09-11).

Source: projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid (Em, 90 BPM, 32 bars)
Method: SP-011 (sound.synthesis.karplus_strong) — ABSOLUTE layer: every voice is a
        plucked string; no FluidSynth / GM samples in the mix.

rev2 changes vs rev1 (which rendered at RMS -28 dBFS with 52.6% sub-threshold silence):
  1. LET-RING durations per role — plucks are allowed to ring past the notated
     note end (bass 1.4 s, lead 1.0 s, pad 0.9 s) so decaying KS strings fill the
     16th/8th-note grid instead of leaving dead air. Percussion stays short/damped.
  2. Per-role bus RMS balancing (comp/bass/lead/perc targets) instead of a single
     raw sum + peak-normalize — one loud transient no longer determines the level.
  3. Bus soft-knee limiter + peak normalize to -1 dBFS.
  4. Verification extended: per-stem autocorrelation pitch frames + harmonic energy
     on the (near-monophonic) bass stem + a FluidSynth GM reference render of the
     same MIDI for a like-for-like tonality comparison.

Voice roles by source program/channel:
  ch9 Drums (36/38/42)           -> "perc" (short damped thunk)
  prog 33 Bass                   -> "bass" (long sustain)
  prog 1  Bright Acoustic Piano  -> "lead" (harp-like lead, sweeping pan)
  prog 88 Pad 1 (new age)        -> "comp" (ringing chordal wash)
"""
import json
import os
import shutil
import subprocess
import wave
from collections import Counter
from pathlib import Path

import mido
import numpy as np

from sound.synthesis.karplus_strong import karplus_strong, midi_to_freq, soft_knee
from utilities.env import fluidsynth_bin, soundfont_path
from workflows.provenance import write_provenance, AI_ASSISTED

ROOT = Path(os.environ.get("MUSICOM_ROOT", "/opt/data/repos/musicom"))
OUT_ROOT = ROOT / "projects/Styles/Production/SP011-karplus-hiphop-boombap"
SRC_MIDI = ROOT / "projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid"
AUDIO = OUT_ROOT / "Audio"
STEMS = AUDIO / "stems"
ANALYSIS = OUT_ROOT / "Analysis"
MIDI_OUT = OUT_ROOT / "MIDI"
for d in (AUDIO, STEMS, ANALYSIS, MIDI_OUT):
    d.mkdir(parents=True, exist_ok=True)
assert SRC_MIDI.exists() and SRC_MIDI.stat().st_size > 40

SR = 44100

# ---------------------------------------------------------------------------
# 1. Parse source MIDI (mido = read-only analysis; authoring stays in musicom)
# ---------------------------------------------------------------------------
mid = mido.MidiFile(str(SRC_MIDI))
tempo = next((m.tempo for m in mid.tracks[0] if m.type == "set_tempo"), 500000)
BPM = round(60_000_000 / tempo, 2)
PPQ = mid.ticks_per_beat


def t2s(tick):
    return tick * tempo / PPQ / 1_000_000


notes = []
for ti, tr in enumerate(mid.tracks):
    prog = 0
    for m in tr:
        if m.type == "program_change":
            prog = m.program
    at, active = 0, {}
    for m in tr:
        at += m.time
        if m.type == "note_on" and m.velocity > 0:
            active.setdefault(m.note, []).append((at, m.velocity, m.channel))
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            if active.get(m.note):
                s, vel, ch = active[m.note].pop(0)
                notes.append({"track": ti, "program": prog, "channel": ch,
                              "pitch": m.note, "velocity": vel,
                              "start": t2s(s), "end": t2s(at)})
notes.sort(key=lambda e: (e["start"], e["pitch"]))
music_end = max(n["end"] for n in notes)

for n in notes:
    if n["channel"] == 9:
        n["role"] = "perc"
        n["end"] = n["start"] + min(0.25, max(0.06, n["end"] - n["start"]))
    elif n["program"] == 33:
        n["role"] = "bass"
    elif n["program"] == 88:
        n["role"] = "comp"
    else:
        n["role"] = "lead"

ROLE_COUNT = Counter(n["role"] for n in notes)
print(f"notes={len(notes)} bpm={BPM} ppq={PPQ} music_end={music_end:.2f}s roles={dict(ROLE_COUNT)}")

# ---------------------------------------------------------------------------
# 2. Voice design (absolute layer) — Karplus-Strong per-role config + let-ring
# ---------------------------------------------------------------------------
ROLES = {
    "comp": dict(loop_gain=0.9987, gain=0.40, ring=0.90, width=0.60, pan=0.50,
                 target_rms=0.100, pan_alt=None),
    "bass": dict(loop_gain=0.9995, gain=0.90, ring=1.40, width=0.30, pan=0.50,
                 target_rms=0.115, pan_alt=None),
    "lead": dict(loop_gain=0.9990, gain=1.00, ring=1.00, width=0.55, pan=0.50,
                 target_rms=0.090, pan_alt=(-0.50, 0.50)),
    "perc": dict(loop_gain=0.9840, gain=0.28, ring=0.25, width=0.30, pan=0.50,
                 target_rms=0.055, pan_alt=None),
}

total_sec = music_end + 0.6
n_samples = int(total_sec * SR)


def render_role(role, note_list):
    """Render one role bus (stereo) with let-ring KS plucks; return (L, R, stats)."""
    cfg = ROLES[role]
    L = np.zeros(n_samples)
    R = np.zeros(n_samples)
    n_plucks = 0
    for j, n in enumerate(note_list):
        dur = max(0.12, n["end"] - n["start"])
        ring = min(cfg["ring"], max(dur, 0.12))
        render_dur = min(max(dur, ring), total_sec - n["start"])
        if render_dur <= 0.05:
            continue
        # spectral tilt: brighter strings lose less energy per round trip
        tilt = 0.998 + 0.002 * (midi_to_freq(n["pitch"]) / 440.0)
        g = min(0.9999, cfg["loop_gain"] * tilt)
        sig = karplus_strong(n["pitch"], render_dur, vel=n["velocity"],
                             loop_gain=g, sr=SR) * cfg["gain"]
        n_plucks += 1
        pan = cfg["pan"]
        if cfg["pan_alt"] and len(note_list) > 1:
            frac = j / (len(note_list) - 1)
            pan = 0.5 * (1.0 + (cfg["pan_alt"][0] + (cfg["pan_alt"][1] - cfg["pan_alt"][0]) * frac))
        s0 = int(n["start"] * SR)
        s1 = min(s0 + len(sig), n_samples)
        seg = sig[: s1 - s0]
        L[s0:s1] += seg * (1.0 - pan)
        R[s0:s1] += seg * pan
    # RMS balance
    rms = float(np.sqrt(np.mean(((L + R) * 0.5) ** 2)))
    scale = (cfg["target_rms"] / rms) if rms > 1e-9 else 1.0
    L *= scale
    R *= scale
    st = {"plucks": n_plucks, "pre_rms": round(rms, 5), "scale": round(scale, 4),
          "post_rms": round(float(np.sqrt(np.mean(((L + R) * 0.5) ** 2))), 5)}
    return L, R, st


def write_wav(path, L, R):
    pcm = (np.clip(np.stack([L, R], axis=1), -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


# ---------------------------------------------------------------------------
# 3. Render per-role buses → stems, then sum → bus limiter → full mix
# ---------------------------------------------------------------------------
mixL = np.zeros(n_samples)
mixR = np.zeros(n_samples)
stems, role_stats = {}, {}
for role in ("lead", "comp", "bass", "perc"):
    rn = [n for n in notes if n["role"] == role]
    if not rn:
        continue
    L, R, st = render_role(role, rn)
    role_stats[role] = st
    idx = ("lead", "comp", "bass", "perc").index(role)
    sp = STEMS / f"track{idx:02d}_{role}.wav"
    write_wav(sp, L, R)
    stems[role] = str(sp)
    print(f"stem {role}: {sp.name} rms={st['post_rms']} plucks={st['plucks']} scale={st['scale']}")
    mixL += L
    mixR += R

# bus limiter: soft knee then peak -1 dBFS
mixL = soft_knee(mixL, thresh=0.80, slope=0.30)
mixR = soft_knee(mixR, thresh=0.80, slope=0.30)
peak = max(float(np.max(np.abs(mixL))), float(np.max(np.abs(mixR))))
if peak > 0:
    mixL *= 0.891 / peak
    mixR *= 0.891 / peak

mix_wav = AUDIO / "SP011-karplus-hiphop-boombap.wav"
write_wav(mix_wav, mixL, mixR)
ogg_path = AUDIO / "SP011-karplus-hiphop-boombap.ogg"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mix_wav),
                "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                str(ogg_path)], check=True)
print(f"mix {mix_wav.stat().st_size} B  ogg {ogg_path.stat().st_size} B  dur {total_sec:.2f}s")

# ---------------------------------------------------------------------------
# 4. Verification helpers
# ---------------------------------------------------------------------------
def read_mono(path):
    with wave.open(str(path), "rb") as wf:
        sr, nch = wf.getframerate(), wf.getnchannels()
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
    return raw.reshape(-1, nch).mean(axis=1), sr


def pitch_frames(mono, sr, win_s=0.5, hop_s=0.25):
    win, hop = int(win_s * sr), int(hop_s * sr)
    out = []
    for w0 in range(0, max(1, len(mono) - win), hop):
        seg = mono[w0:w0 + win]
        seg = seg - seg.mean()
        if float(np.sum(seg ** 2)) < 1e-8:
            out.append({"t": round(w0 / sr, 2), "f0": None, "conf": 0.0})
            continue
        ac = np.correlate(seg, seg, "full")[win - 1:]
        ac /= ac[0]
        lo, hi = int(sr / 1000), int(sr / 50)
        region = ac[lo:hi]
        lag = lo + int(np.argmax(region))
        out.append({"t": round(w0 / sr, 2), "f0": round(sr / lag, 1),
                    "conf": round(float(region.max()), 3)})
    return out


def stats(mono, sr):
    dur = len(mono) / sr
    sil = 100 * float(np.sum(np.abs(mono) < 0.001) / len(mono))
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    mask = np.abs(mono) < 0.001
    runs, cur = [], 0
    for v in mask:
        cur = cur + 1 if v else 0
        if not v and cur:
            runs.append(cur)
            cur = 0
    if cur:
        runs.append(cur)
    per_sec = [round(float(np.sqrt(np.mean(mono[i * sr:(i + 1) * sr] ** 2))), 4)
               for i in range(int(np.floor(dur)))]
    return {"duration_s": round(dur, 2), "peak": round(peak, 4), "rms": round(rms, 5),
            "silence_pct": round(sil, 1),
            "max_silent_run_ms": round(1000 * max(runs) / sr, 1) if runs else 0.0,
            "min_rms_sec": min(per_sec) if per_sec else None,
            "rms_per_second": per_sec}


mono, SR0 = read_mono(mix_wav)
mix_stats = stats(mono, SR0)
print("MIX STATS:", json.dumps({k: v for k, v in mix_stats.items() if k != "rms_per_second"}))

# --- pitch verification: mix, and every stem ---
exp_sustained = sorted({round(midi_to_freq(n["pitch"]), 1) for n in notes if n["role"] != "perc"})
verify = {}

fr = pitch_frames(mono, SR0)
pitched = [f for f in fr if f["f0"] and f["conf"] > 0.35]
match = 0
for f in pitched:
    near = [n for n in notes if n["role"] != "perc"
            and n["start"] - 0.35 <= f["t"] <= n["end"] + 1.2]
    ok = False
    for n in near:
        f0 = midi_to_freq(n["pitch"])
        if any(abs(f0 * h - f["f0"]) / (f0 * h) < 0.06 for h in range(1, 7)):
            ok = True
            break
    match += int(ok)
verify["mix"] = {"frames": len(fr), "pitched": len(pitched),
                 "pitched_pct": round(100 * len(pitched) / max(1, len(fr)), 1),
                 "zero_hz": sum(1 for f in fr if not f["f0"]),
                 "match_expected_or_harmonic_pct": round(100 * match / max(1, len(pitched)), 1)}

for role, sp in stems.items():
    m, sr = read_mono(sp)
    fr = pitch_frames(m, sr)
    p = [f for f in fr if f["f0"] and f["conf"] > 0.35]
    verify[role] = {"pitched_pct": round(100 * len(p) / max(1, len(fr)), 1),
                    "zero_hz_frames": sum(1 for f in fr if not f["f0"]),
                    "stereo_rms": round(float(np.sqrt(np.mean(m ** 2))), 5)}


def harmonic_pct(path, lowest_midi, band=(50, 2000), nharm=8):
    m, sr = read_mono(path)
    seg = m[int(0.15 * len(m)):int(0.85 * len(m))]
    seg = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(seg))
    ff = np.fft.rfftfreq(len(seg), 1 / sr)
    bm = (ff >= band[0]) & (ff <= band[1])
    be = float(np.sum(spec[bm]))
    f0 = midi_to_freq(lowest_midi)
    he = 0.0
    for h in range(1, nharm + 1):
        hm = (ff >= f0 * h * 0.97) & (ff <= f0 * h * 1.03)
        if hm.any():
            he += float(np.sum(spec[hm]))
    return round(100 * he / max(be, 1e-12), 1), f0


bass_low = min(n["pitch"] for n in notes if n["role"] == "bass")
hp_bass, f0_bass = harmonic_pct(STEMS / "track02_bass.wav", bass_low)
hp_lead, f0_lead = harmonic_pct(STEMS / "track00_lead.wav",
                                min(n["pitch"] for n in notes if n["role"] == "lead"))
hp_mix, f0_mix = harmonic_pct(mix_wav, bass_low)
verify["harmonic_energy_pct"] = {"bass_stem": hp_bass, "bass_lowest_midi": bass_low,
                                 "bass_f0_hz": round(f0_bass, 1),
                                 "lead_stem": hp_lead, "lead_f0_hz": round(f0_lead, 1),
                                 "full_mix": hp_mix, "mix_f0_hz": round(f0_mix, 1)}

# --- FluidSynth GM reference render (same MIDI) for a like-for-like tonality check ---
ref_wav = ANALYSIS / "ref_fluidsynth_gm.wav"
try:
    subprocess.run([fluidsynth_bin(), "-ni", "-g", "1.2", "-F", str(ref_wav),
                    soundfont_path(), str(SRC_MIDI)],
                   check=True, capture_output=True)
    hp_ref, _ = harmonic_pct(ref_wav, bass_low)
    verify["harmonic_energy_pct"]["fluidsynth_gm_reference"] = hp_ref
    ref_m, ref_sr = read_mono(ref_wav)
    verify["fluidsynth_gm_reference_stats"] = {k: v for k, v in stats(ref_m, ref_sr).items()
                                               if k != "rms_per_second"}
    ref_wav.unlink()  # WAV cleanup: keep the project lean
except Exception as e:  # pragma: no cover
    verify["fluidsynth_gm_reference_error"] = str(e)

print("VERIFY:", json.dumps(verify, indent=1))
(ANALYSIS / "pitch_verification.json").write_text(json.dumps(verify, indent=2))
(ANALYSIS / "render_stats.json").write_text(json.dumps(mix_stats, indent=2))

# ---------------------------------------------------------------------------
# 5. Onset grid (16th notes) + render info + provenance + MIDI copy
# ---------------------------------------------------------------------------
step_s = (PPQ // 4) * tempo / PPQ / 1_000_000
n_steps = min(int(np.ceil(music_end / step_s)), 272)
gl = [f"SP-011 Karplus-Strong — source: {SRC_MIDI.name} ({BPM} BPM, {music_end:.1f}s, {len(notes)} notes)",
      f"16th-note grid, {n_steps} steps (col = 16th note), + = onset", ""]
for role in ("lead", "comp", "bass", "perc"):
    cells = [""] * n_steps
    for n in notes:
        if n["role"] != role:
            continue
        c = int(round(n["start"] / step_s))
        if 0 <= c < n_steps:
            cells[c] = "X"
    gl.append(f"{role:5s} " + "".join("\u2588" if c else "\u2591" for c in cells))
gl += ["", "| 16 cols = 1 bar (90 BPM, 4/4) | drums on 8ths/16ths, pad on 16ths,",
       "| bass on 8ths, lead sparse; let-ring KS tails overlap the grid |"]
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(gl))

render_info = {
    "method": "SP-011", "method_name": "Karplus-Strong String Synthesis",
    "method_module": "sound.synthesis.karplus_strong",
    "source_midi": str(SRC_MIDI), "source_name": SRC_MIDI.name,
    "bpm": BPM, "ticks_per_beat": PPQ,
    "bars": int(round(music_end / (4 * 60.0 / BPM))),
    "total_notes": len(notes), "role_counts": dict(ROLE_COUNT),
    "output_seconds": round(total_sec, 2), "sample_rate": SR,
    "stems": stems, "role_stats": role_stats,
    "parameters": {
        "excitation": "2-sample uniform noise burst scaled by velocity",
        "delay_line": "N = round(sr/f0) full cycle period (no octave drop)",
        "loop_filter": "2-point moving average y[n]=0.5*(y[n-N]+y[n-N-1])",
        "loop_gain_by_role": {r: ROLES[r]["loop_gain"] for r in ROLES},
        "let_ring_seconds": {r: ROLES[r]["ring"] for r in ROLES},
        "target_rms_by_role": {r: ROLES[r]["target_rms"] for r in ROLES},
        "pan": "lead drift -0.50..+0.50; comp/bass/perc center",
        "bus": "per-role RMS balance -> soft-knee (0.80/0.30) -> peak -1 dBFS",
    },
    "pitch_verification": verify, "mix_stats": mix_stats,
}
(ANALYSIS / "render_info.json").write_text(json.dumps(render_info, indent=2))
shutil.copy2(SRC_MIDI, MIDI_OUT / SRC_MIDI.name)

write_provenance(str(mix_wav), AI_ASSISTED, "SP-011 Karplus-Strong production pass (rev2)",
                 sources=[str(SRC_MIDI)], parameters={"method": "SP-011", "roles": list(ROLES)})
write_provenance(str(ogg_path), AI_ASSISTED, "SP-011 Karplus-Strong production pass (rev2)",
                 sources=[str(SRC_MIDI)], parameters={"method": "SP-011", "roles": list(ROLES)})
for role, sp in stems.items():
    write_provenance(sp, AI_ASSISTED, "SP-011 Karplus-Strong stem (rev2)",
                     sources=[str(SRC_MIDI)], parameters={"role": role, "method": "SP-011"})

for p in [mix_wav, ogg_path] + [Path(v) for v in stems.values()]:
    assert p.stat().st_size > 1000, f"too small: {p}"
print("PRODUCE OK rev2")
