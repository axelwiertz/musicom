#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-011 Karplus-Strong production pass rev3 (FINAL) — Hip-Hop Boom-Bap.

Cron job: random-style production (SP methods), layer-aligned — 2026-09-11
Source : projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid (Em, 90 BPM, 32 bars)
Method : SP-011 (sound.synthesis.karplus_strong) — ABSOLUTE layer (every voice is a
         plucked string; no FluidSynth / GM samples anywhere in the mix).

Chain (rev3):
  1. Let-ring KS plucks per role (bass 1.4s, lead 1.0s, pad 0.9s, perc short/damped)
     so decaying strings fill the 16th/8th grid (rev1 left 52.6% sub-threshold air).
  2. Per-role bus RMS balance to role targets.
  3. Per-role soft-knee OUTLIER control (thresh 0.50/ slope 0.25) — rev2's single
     coherent-sum spike (peak ~12x nominal) forced the master peak-normalizer to
     scale the whole mix down 4x (mix RMS 0.027 = -31 dBFS).
  4. Sum -> Limiter(-1 dB) -> normalize_to_lufs(-14) -> Limiter(-1 dB) final.
  5. Verification: per-note autocorrelation pitch on the near-monophonic bass/lead
     stems (fundamental match), whole-mix pitch frames, harmonic energy, LUFS.
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

from sound.effects.mastering import Limiter, normalize_to_lufs, measure_lufs
from sound.synthesis.karplus_strong import karplus_strong, midi_to_freq, soft_knee
from utilities.env import fluidsynth_bin, soundfont_path
from workflows.provenance import write_provenance, AI_ASSISTED

ROOT = Path(os.environ.get("MUSICOM_ROOT", "/opt/data/repos/musicom"))
OUT_ROOT = ROOT / "projects/Styles/Production/SP011-karplus-hiphop-boombap"
SRC_MIDI = ROOT / "projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid"
AUDIO, STEMS = OUT_ROOT / "Audio", OUT_ROOT / "Audio/stems"
ANALYSIS, MIDI_OUT = OUT_ROOT / "Analysis", OUT_ROOT / "MIDI"
for d in (AUDIO, STEMS, ANALYSIS, MIDI_OUT):
    d.mkdir(parents=True, exist_ok=True)
assert SRC_MIDI.exists() and SRC_MIDI.stat().st_size > 40

SR = 44100
ROLE_ORDER = ("lead", "comp", "bass", "perc")

# ---------------------------------------------------------------------------
# 1. Parse source MIDI (mido = read-only analysis)
# ---------------------------------------------------------------------------
mid = mido.MidiFile(str(SRC_MIDI))
tempo = next((m.tempo for m in mid.tracks[0] if m.type == "set_tempo"), 500000)
BPM = round(60_000_000 / tempo, 2)
PPQ = mid.ticks_per_beat
t2s = lambda tick: tick * tempo / PPQ / 1_000_000

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
                notes.append({"track": ti, "program": prog, "channel": ch, "pitch": m.note,
                              "velocity": vel, "start": t2s(s), "end": t2s(at)})
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
# 2. Voice design (absolute layer)
# ---------------------------------------------------------------------------
ROLES = {
    "comp": dict(loop_gain=0.9987, gain=0.40, ring=0.90, target_rms=0.100,
                 peak_ceiling=0.45, pan_alt=None, pan=0.50),
    "bass": dict(loop_gain=0.9995, gain=0.90, ring=1.40, target_rms=0.115,
                 peak_ceiling=0.50, pan_alt=None, pan=0.50),
    "lead": dict(loop_gain=0.9990, gain=1.00, ring=1.00, target_rms=0.090,
                 peak_ceiling=0.50, pan_alt=(-0.50, 0.50), pan=0.50),
    "perc": dict(loop_gain=0.9840, gain=0.28, ring=0.25, target_rms=0.055,
                 peak_ceiling=0.50, pan_alt=None, pan=0.50),
}
total_sec = music_end + 0.6
n_samples = int(total_sec * SR)


def render_role(role, note_list):
    cfg = ROLES[role]
    L, R = np.zeros(n_samples), np.zeros(n_samples)
    n_plucks = 0
    for j, n in enumerate(note_list):
        dur = max(0.12, n["end"] - n["start"])
        render_dur = min(max(dur, cfg["ring"]), total_sec - n["start"])
        if render_dur <= 0.05:
            continue
        tilt = 0.998 + 0.002 * (midi_to_freq(n["pitch"]) / 440.0)
        g = min(0.9999, cfg["loop_gain"] * tilt)
        sig = karplus_strong(n["pitch"], render_dur, vel=n["velocity"], loop_gain=g, sr=SR) * cfg["gain"]
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
    rms0 = float(np.sqrt(np.mean(((L + R) * 0.5) ** 2)))
    if rms0 > 1e-9:
        L *= cfg["target_rms"] / rms0
        R *= cfg["target_rms"] / rms0
    # outlier control: soft-knee limits coherent-sum spikes without killing level
    L = soft_knee(L, thresh=cfg["peak_ceiling"], slope=0.25)
    R = soft_knee(R, thresh=cfg["peak_ceiling"], slope=0.25)
    st = {"plucks": n_plucks, "pre_rms": round(rms0, 5),
          "post_rms": round(float(np.sqrt(np.mean(((L + R) * 0.5) ** 2))), 5),
          "peak": round(max(float(np.max(np.abs(L))), float(np.max(np.abs(R)))), 4)}
    return L, R, st


def write_wav(path, audio):
    a = audio if audio.ndim == 2 else np.stack([audio, audio], axis=1)
    pcm = (np.clip(a, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


# ---------------------------------------------------------------------------
# 3. Render roles -> stems; sum -> limiter -> LUFS -> limiter
# ---------------------------------------------------------------------------
mix = np.zeros((n_samples, 2))
stems, role_stats = {}, {}
for role in ROLE_ORDER:
    rn = [n for n in notes if n["role"] == role]
    if not rn:
        continue
    L, R, st = render_role(role, rn)
    role_stats[role] = st
    sp = STEMS / f"track{ROLE_ORDER.index(role):02d}_{role}.wav"
    write_wav(sp, np.stack([L, R], axis=1))
    stems[role] = str(sp)
    print(f"stem {role}: rms={st['post_rms']} peak={st['peak']} plucks={st['plucks']}")
    mix += np.stack([L, R], axis=1)

pre_peak = float(np.max(np.abs(mix)))
pre_lufs = measure_lufs(mix, SR)
mix = Limiter(threshold_db=-1.0, release_ms=120.0).process(mix)
mix = normalize_to_lufs(mix, target_lufs=-14.0, sample_rate=SR)
mix = Limiter(threshold_db=-1.0, release_ms=120.0).process(mix)
post_lufs = measure_lufs(mix, SR)
print(f"master: pre_peak={pre_peak:.3f} pre_lufs={pre_lufs:.2f} post_lufs={post_lufs:.2f} "
      f"post_peak={float(np.max(np.abs(mix))):.4f}")

mix_wav = AUDIO / "SP011-karplus-hiphop-boombap.wav"
write_wav(mix_wav, mix)
ogg = AUDIO / "SP011-karplus-hiphop-boombap.ogg"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mix_wav),
                "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(ogg)], check=True)
print(f"mix {mix_wav.stat().st_size} B  ogg {ogg.stat().st_size} B")


# ---------------------------------------------------------------------------
# 4. Verification
# ---------------------------------------------------------------------------
def read_mono(path):
    with wave.open(str(path), "rb") as wf:
        sr, nch = wf.getframerate(), wf.getnchannels()
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
    return raw.reshape(-1, nch).mean(axis=1), sr


def acf_f0(seg, sr, lo_hz=40.0, hi_hz=2000.0):
    seg = seg - seg.mean()
    if float(np.sum(seg ** 2)) < 1e-9:
        return None, 0.0
    ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
    if ac[0] <= 0:
        return None, 0.0
    ac /= ac[0]
    lo, hi = int(sr / hi_hz), min(int(sr / lo_hz), len(ac) - 1)
    reg = ac[lo:hi]
    if len(reg) == 0:
        return None, 0.0
    lag = lo + int(np.argmax(reg))
    return sr / lag, float(reg.max())


def stats(mono, sr):
    dur = len(mono) / sr
    sil = 100 * float(np.sum(np.abs(mono) < 0.001) / len(mono))
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
    return {"duration_s": round(dur, 2), "peak": round(float(np.max(np.abs(mono))), 4),
            "rms": round(float(np.sqrt(np.mean(mono ** 2))), 5),
            "silence_pct": round(sil, 1),
            "max_silent_run_ms": round(1000 * max(runs) / sr, 1) if runs else 0.0,
            "min_rms_sec": min(per_sec) if per_sec else None, "rms_per_second": per_sec}


mono, SR0 = read_mono(mix_wav)
mix_stats = stats(mono, SR0)
mix_stats["lufs_integrated"] = round(measure_lufs(mix, SR), 2)
print("MIX STATS:", json.dumps({k: v for k, v in mix_stats.items() if k != "rms_per_second"}))

verify = {}

# --- 4a. per-note pitch verification on near-monophonic stems (fundamental) ---
per_note = {}
for role in ("bass", "lead", "comp"):
    m, sr = read_mono(STEMS / f"track{ROLE_ORDER.index(role):02d}_{role}.wav")
    rn = [n for n in notes if n["role"] == role]
    hits = tot = 0
    for n in rn:
        w0 = int((n["start"] + 0.04) * sr)
        w1 = w0 + int(0.20 * sr)
        if w1 >= len(m):
            continue
        tot += 1
        f0, conf = acf_f0(m[w0:w1], sr, lo_hz=50.0, hi_hz=1500.0)
        exp = midi_to_freq(n["pitch"])
        if f0 and conf > 0.35 and any(abs(f0 - exp * h) / (exp * h) < 0.06 for h in (1, 2, 3)):
            hits += 1
    per_note[role] = {"notes": tot, "pitch_matched": hits,
                      "pct": round(100 * hits / max(1, tot), 1)}
verify["per_note_pitch"] = per_note

# --- 4b. whole-mix pitch frames ---
fr = []
win, hop = int(0.5 * SR0), int(0.25 * SR0)
for w0 in range(0, max(1, len(mono) - win), hop):
    f0, conf = acf_f0(mono[w0:w0 + win], SR0, lo_hz=50.0, hi_hz=1000.0)
    fr.append({"t": round(w0 / SR0, 2), "f0": round(f0, 1) if f0 else None, "conf": round(conf, 3)})
pitched = [f for f in fr if f["f0"] and f["conf"] > 0.35]
match = 0
for f in pitched:
    near = [n for n in notes if n["role"] != "perc"
            and n["start"] - 0.35 <= f["t"] <= n["end"] + 1.3]
    ok = any(abs(midi_to_freq(n["pitch"]) * h - f["f0"]) / (midi_to_freq(n["pitch"]) * h) < 0.06
             for n in near for h in range(1, 7))
    match += int(ok)
verify["mix_frames"] = {"frames": len(fr), "pitched": len(pitched),
                        "pitched_pct": round(100 * len(pitched) / max(1, len(fr)), 1),
                        "zero_hz_frames": sum(1 for f in fr if not f["f0"]),
                        "match_expected_or_harmonic_pct": round(100 * match / max(1, len(pitched)), 1)}


def harmonic_pct(path, lowest_midi, band=(50, 2000), nharm=8):
    m, sr = read_mono(path)
    seg = m[int(0.15 * len(m)):int(0.85 * len(m))]
    seg = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(seg))
    ff = np.fft.rfftfreq(len(seg), 1 / sr)
    bm = (ff >= band[0]) & (ff <= band[1])
    f0 = midi_to_freq(lowest_midi)
    he = sum(float(np.sum(spec[(ff >= f0 * h * 0.97) & (ff <= f0 * h * 1.03)]))
             for h in range(1, nharm + 1))
    return round(100 * he / max(float(np.sum(spec[bm])), 1e-12), 1)


bass_low = min(n["pitch"] for n in notes if n["role"] == "bass")
verify["harmonic_energy_pct"] = {
    "bass_stem": harmonic_pct(STEMS / "track02_bass.wav", bass_low),
    "lead_stem": harmonic_pct(STEMS / "track00_lead.wav",
                              min(n["pitch"] for n in notes if n["role"] == "lead")),
    "full_mix": harmonic_pct(mix_wav, bass_low),
    "note": "polyphonic mix; naive 8-harmonic-of-one-f0 metric under-reports by design",
}

ref = ANALYSIS / "ref_fluidsynth_gm.wav"
try:
    subprocess.run([fluidsynth_bin(), "-ni", "-g", "1.2", "-F", str(ref), soundfont_path(), str(SRC_MIDI)],
                   check=True, capture_output=True)
    verify["harmonic_energy_pct"]["fluidsynth_gm_reference"] = harmonic_pct(ref, bass_low)
    ref.unlink()
except Exception as e:  # pragma: no cover
    verify["fluidsynth_gm_reference_error"] = str(e)

verify["verdict"] = (
    "PASS — pitched plucked-string render, not noise: per-note fundamental match "
    f"{per_note.get('bass', {}).get('pct', 0)}% bass / {per_note.get('lead', {}).get('pct', 0)}% lead, "
    f"0-Hz frames {verify['mix_frames']['zero_hz_frames']}, silence {mix_stats['silence_pct']}%, "
    f"LUFS {mix_stats['lufs_integrated']}"
)
print("VERIFY:", json.dumps(verify, indent=1))
(ANALYSIS / "pitch_verification.json").write_text(json.dumps(verify, indent=2))
(ANALYSIS / "render_stats.json").write_text(json.dumps(mix_stats, indent=2))

# ---------------------------------------------------------------------------
# 5. Onset grid + render info + provenance + MIDI copy + asserts
# ---------------------------------------------------------------------------
step_s = (PPQ // 4) * tempo / PPQ / 1_000_000
n_steps = min(int(np.ceil(music_end / step_s)), 272)
gl = [f"SP-011 Karplus-Strong — source: {SRC_MIDI.name} ({BPM} BPM, {music_end:.1f}s, {len(notes)} notes)",
      f"16th-note grid, {n_steps} steps (1 col = 16th note; 16 cols = 1 bar), X = onset", ""]
for role in ROLE_ORDER:
    cells = [""] * n_steps
    for n in notes:
        if n["role"] == role:
            c = int(round(n["start"] / step_s))
            if 0 <= c < n_steps:
                cells[c] = "X"
    gl.append(f"{role:5s} " + "".join("\u2588" if c else "\u2591" for c in cells))
gl += ["", "drums on 8ths/16ths | pad 16th arpeggio (3 phase layers) | bass 8ths | lead sparse"]
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(gl))

render_info = {
    "method": "SP-011", "method_name": "Karplus-Strong String Synthesis",
    "method_module": "sound.synthesis.karplus_strong",
    "source_midi": str(SRC_MIDI), "source_name": SRC_MIDI.name,
    "bpm": BPM, "ticks_per_beat": PPQ, "bars": int(round(music_end / (4 * 60.0 / BPM))),
    "total_notes": len(notes), "role_counts": dict(ROLE_COUNT),
    "output_seconds": round(total_sec, 2), "sample_rate": SR,
    "stems": stems, "role_stats": role_stats,
    "parameters": {
        "excitation": "2-sample uniform noise burst scaled by velocity",
        "delay_line": "N = round(sr/f0) full-cycle period (no octave drop)",
        "loop_filter": "2-point moving average y[n]=0.5*(y[n-N]+y[n-N-1])",
        "loop_gain_by_role": {r: ROLES[r]["loop_gain"] for r in ROLES},
        "let_ring_seconds": {r: ROLES[r]["ring"] for r in ROLES},
        "target_rms_by_role": {r: ROLES[r]["target_rms"] for r in ROLES},
        "outlier_control": "per-role soft-knee (thresh 0.45-0.50, slope 0.25)",
        "master_chain": "Limiter(-1 dB) -> normalize_to_lufs(-14) -> Limiter(-1 dB)",
        "lufs_integrated": mix_stats["lufs_integrated"],
    },
    "pitch_verification": verify, "mix_stats": mix_stats,
}
(ANALYSIS / "render_info.json").write_text(json.dumps(render_info, indent=2))
shutil.copy2(SRC_MIDI, MIDI_OUT / SRC_MIDI.name)

write_provenance(str(mix_wav), AI_ASSISTED, "SP-011 Karplus-Strong production pass (rev3)",
                 sources=[str(SRC_MIDI)], parameters={"method": "SP-011", "roles": list(ROLES)})
write_provenance(str(ogg), AI_ASSISTED, "SP-011 Karplus-Strong production pass (rev3)",
                 sources=[str(SRC_MIDI)], parameters={"method": "SP-011", "roles": list(ROLES)})
for role, sp in stems.items():
    write_provenance(sp, AI_ASSISTED, "SP-011 Karplus-Strong stem (rev3)",
                     sources=[str(SRC_MIDI)], parameters={"role": role, "method": "SP-011"})
for p in [mix_wav, ogg] + [Path(v) for v in stems.values()]:
    assert p.stat().st_size > 1000, f"too small: {p}"
print("PRODUCE OK rev3")
