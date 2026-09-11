#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-011 Karplus-Strong production pass — Hip-Hop Boom-Bap (cron 2026-09-11).

Source: projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid
        (Em, 90 BPM, 32 bars, 4 voices, 1792 notes)
Method: SP-011 (sound.synthesis.karplus_strong) from
        workflows.musicom_workflow.SP_METHODS — ABSOLUTE layer: every voice
        is rendered as a plucked string (no FluidSynth, no GM samples).

Voice roles by source program/channel:
  ch9 Drums (GM 36/38/42)        -> role "perc" (short damped thunk)
  prog 33 Bass                   -> role "bass" (long sustain)
  prog 1  Bright Acoustic Piano  -> role "lead" (harp-like arpeggio/lead)
  prog 88 Pad 1 (new age)        -> role "comp" (ringing chordal wash)

Outputs: full mix WAV + OGG, per-role stems (same synthesis), render_info.json,
onset grid visualization, pitch verification JSON, provenance sidecars.
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

from sound.synthesis.karplus_strong import (midi_to_freq, render_melody,
                                            render_melody_wav)
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

assert SRC_MIDI.exists() and SRC_MIDI.stat().st_size > 40, "source MIDI missing/empty"

# ---------------------------------------------------------------------------
# 1. Parse source MIDI (mido = read-only analysis)
# ---------------------------------------------------------------------------
mid = mido.MidiFile(str(SRC_MIDI))
tempo = 500000
for m in mid.tracks[0]:
    if m.type == "set_tempo":
        tempo = m.tempo
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
    at = 0
    active = {}
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
    elif n["program"] == 33:
        n["role"] = "bass"
    elif n["program"] == 88:
        n["role"] = "comp"
    else:
        n["role"] = "lead"

# Drums: single-hit decay (no long ringing percussion)
for n in notes:
    if n["role"] == "perc":
        n["end"] = n["start"] + min(0.25, max(0.06, n["end"] - n["start"]))

ROLE_COUNT = Counter(n["role"] for n in notes)
print(f"notes={len(notes)} bpm={BPM} ppq={PPQ} music_end={music_end:.2f}s roles={dict(ROLE_COUNT)}")

# ---------------------------------------------------------------------------
# 2. Voice design — per-role Karplus-Strong config (absolute layer)
# ---------------------------------------------------------------------------
ROLES = {
    # pad chords: long ring so 16th pad arpeggios overlap into a wash
    "comp": {"width": 0.60, "pan_drift": False, "gain_db": -9.0, "loop_gain": 0.9990},
    # bass: strong low fundamental, long sustain (classic KS bass)
    "bass": {"width": 0.30, "pan_drift": False, "gain_db": -5.0, "loop_gain": 0.9994},
    # lead/piano: harp-like pluck, sweeping pan across the form
    "lead": {"width": 0.55, "pan_drift": True, "gain_db": -4.0, "loop_gain": 0.9986},
    # drums: very short damped thunks
    "perc": {"width": 0.30, "pan_drift": False, "gain_db": -11.0, "loop_gain": 0.9840},
}

# ---------------------------------------------------------------------------
# 3. Render full mix + per-role stems with the SAME synthesis
# ---------------------------------------------------------------------------
def trim_wav(path, target_sec):
    with wave.open(str(path), "rb") as wf:
        sr0, nch0, sw, n0 = wf.getframerate(), wf.getnchannels(), wf.getsampwidth(), wf.getnframes()
        data = wf.readframes(n0)
    n_t = int(target_sec * sr0)
    if n_t >= n0:
        return
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(nch0)
        wf.setsampwidth(sw)
        wf.setframerate(sr0)
        wf.writeframes(data[: n_t * nch0 * sw])


mix_wav = AUDIO / "SP011-karplus-hiphop-boombap.wav"
audio, info = render_melody(notes, roles=ROLES)
render_melody_wav(notes, mix_wav, roles=ROLES)
trim_wav(mix_wav, music_end + 0.6)
print(f"mix: {mix_wav.name} {mix_wav.stat().st_size} B {info['output_seconds']}s -> trimmed {music_end + 0.6:.2f}s")

stems = {}
for role in ("lead", "comp", "bass", "perc"):
    rn = [n for n in notes if n["role"] == role]
    if not rn:
        continue
    sp = STEMS / f"track{list(ROLES).index(role):02d}_{role}.wav"
    _, sinfo = render_melody(rn, roles=ROLES)
    render_melody_wav(rn, sp, roles=ROLES)
    trim_wav(sp, music_end + 0.6)
    stems[role] = str(sp)
    print(f"stem {role}: {sp.name} {sp.stat().st_size} B ({sinfo['note_count']} notes)")

ogg_path = AUDIO / "SP011-karplus-hiphop-boombap.ogg"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mix_wav),
                "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                str(ogg_path)], check=True)
print(f"ogg: {ogg_path.stat().st_size} B")

# ---------------------------------------------------------------------------
# 4. Read-back analysis (mono)
# ---------------------------------------------------------------------------
def read_mono(path):
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
    return raw.reshape(-1, nch).mean(axis=1), sr


mono, SR = read_mono(mix_wav)
dur = len(mono) / SR
sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
peak = float(np.max(np.abs(mono)))
rms_per_sec = [round(float(np.sqrt(np.mean(mono[i * SR:(i + 1) * SR] ** 2))), 4)
               for i in range(int(np.floor(dur)))]
print(f"dur={dur:.2f}s peak={peak:.4f} silence={100 * sil:.1f}% rms={rms_per_sec}")

# longest silent run
thr = 0.001
mask = np.abs(mono) < thr
runs, cur = [], 0
for v in mask:
    if v:
        cur += 1
    elif cur:
        runs.append(cur)
        cur = 0
if cur:
    runs.append(cur)
max_gap_ms = round(1000.0 * max(runs) / SR, 1) if runs else 0.0
print(f"longest silent run = {max_gap_ms} ms")

# ---------------------------------------------------------------------------
# 5. Pitch verification (mandatory — size/silence does NOT catch noise)
# ---------------------------------------------------------------------------
win = int(0.5 * SR)
hop = int(0.25 * SR)
frames = []
for w0 in range(0, len(mono) - win, hop):
    seg = mono[w0:w0 + win]
    seg = seg - seg.mean()
    if float(np.sum(seg ** 2)) < 1e-8:
        frames.append({"t": round(w0 / SR, 2), "f0": None, "conf": 0.0})
        continue
    ac = np.correlate(seg, seg, "full")[win - 1:]
    ac /= ac[0]
    lo, hi = int(SR / 1000), int(SR / 50)
    region = ac[lo:hi]
    lag = lo + int(np.argmax(region))
    frames.append({"t": round(w0 / SR, 2), "f0": round(SR / lag, 1),
                   "conf": round(float(region.max()), 3)})

pitched = [f for f in frames if f["f0"] and f["conf"] > 0.35]
# expected pitch set active in each frame window
exp_all = sorted({round(midi_to_freq(n["pitch"]), 1) for n in notes if n["role"] != "perc"})
match = 0
for f in pitched:
    t = f["t"]
    near = [n for n in notes if n["role"] != "perc" and n["start"] - 0.35 <= t <= n["end"] + 0.35]
    if not near:
        continue
    # accept fundamental OR any harmonic (KS plucks ring on overtones)
    ok = False
    for n in near:
        f0 = midi_to_freq(n["pitch"])
        for h in range(1, 6):
            if abs(f0 * h - f["f0"]) / (f0 * h) < 0.06:
                ok = True
                break
        if ok:
            break
    match += int(ok)

# harmonic energy: 8 harmonics of the lowest sustained fundamental, band 50-2000 Hz
seg = mono[int(0.2 * dur * SR):int(0.8 * dur * SR)]
seg = seg * np.hanning(len(seg))
spec = np.abs(np.fft.rfft(seg))
ff = np.fft.rfftfreq(len(seg), 1 / SR)
f0min = midi_to_freq(min(n["pitch"] for n in notes if n["role"] != "perc"))
band = (ff >= 50) & (ff <= 2000)
band_e = float(np.sum(spec[band]))
h_e = 0.0
for h in range(1, 9):
    m = (ff >= f0min * h * 0.97) & (ff <= f0min * h * 1.03)
    if m.any():
        h_e += float(np.sum(spec[m]))
harm_pct = round(100 * h_e / max(band_e, 1e-12), 1)

pitch_res = {
    "frames": len(frames),
    "pitched_frames": len(pitched),
    "pitched_pct": round(100 * len(pitched) / max(1, len(frames)), 1),
    "zero_hz_frames": sum(1 for f in frames if not f["f0"]),
    "frames_matching_expected_f0_or_harmonic": match,
    "match_pct": round(100 * match / max(1, len(pitched)), 1),
    "harmonic_energy_vs_band_50_2000_pct": harm_pct,
    "lowest_sustained_f0_hz": round(f0min, 1),
    "verdict": ("Pitched (plucked-string harmonics), NOT noise"
                if len(pitched) / max(1, len(frames)) > 0.8 and harm_pct >= 20
                else "SUSPECT — inspect"),
}
print("PITCH:", json.dumps(pitch_res))
(ANALYSIS / "pitch_verification.json").write_text(json.dumps(pitch_res, indent=2))

render_stats = {
    "duration_s": round(dur, 3),
    "peak": round(peak, 4),
    "silence_pct": round(100 * sil, 1),
    "max_silent_run_ms": max_gap_ms,
    "rms_per_second": rms_per_sec,
    "min_rms_sec": min(rms_per_sec) if rms_per_sec else None,
}
(ANALYSIS / "render_stats.json").write_text(json.dumps(render_stats, indent=2))

# ---------------------------------------------------------------------------
# 6. Onset grid visualization (16th-note grid, music core)
# ---------------------------------------------------------------------------
BAR = PPQ * 4
step_ticks = BAR // 4
n_steps = int(np.ceil(music_end / (step_ticks * tempo / PPQ / 1_000_000)))
n_steps = min(n_steps, 272)
grid_lines = [f"SP-011 Karplus-Strong — source: {SRC_MIDI.name} ({BPM} BPM, {music_end:.1f}s, {len(notes)} notes)",
              f"16th-note grid, {n_steps} steps (col = 16th); X = onset", ""]
for role in ("lead", "comp", "bass", "perc"):
    cells = [""] * n_steps
    for n in notes:
        if n["role"] != role:
            continue
        c = int(round(n["start"] / (step_ticks * tempo / PPQ / 1_000_000)))
        if 0 <= c < n_steps:
            cells[c] = "X"
    grid_lines.append(f"{role:5s} " + "".join("\u2588" if c else "\u2591" for c in cells))
grid_lines.append("")
grid_lines.append("| 0.25s per cell | drums dense on 8ths, pad on 16ths, bass 8ths")
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(grid_lines))

# ---------------------------------------------------------------------------
# 7. render_info + provenance + MIDI copy + size asserts
# ---------------------------------------------------------------------------
info.update({
    "source_midi": str(SRC_MIDI),
    "source_name": SRC_MIDI.name,
    "bpm": BPM,
    "ticks_per_beat": PPQ,
    "bars": int(round(music_end / (4 * 60.0 / BPM))),
    "total_notes": len(notes),
    "role_counts": dict(ROLE_COUNT),
    "stems": stems,
    "parameters": {
        "excitation": "2-sample uniform noise burst scaled by velocity",
        "delay_line": "N = round(sr/f0), full cycle period (no octave drop)",
        "loop_filter": "2-point moving average y[n]=0.5*(y[n-N]+y[n-N-1])",
        "loop_gain_by_role": {r: ROLES[r]["loop_gain"] for r in ROLES},
        "gain_db_by_role": {r: ROLES[r]["gain_db"] for r in ROLES},
        "pan": "lead drift -0.55..+0.55 across form; comp/bass/perc center",
        "bus": "soft-knee saturation, peak-normalized -1 dBFS",
    },
    "pitch_verification": pitch_res,
    "render_stats": render_stats,
})
(ANALYSIS / "render_info.json").write_text(json.dumps(info, indent=2))

shutil.copy2(SRC_MIDI, MIDI_OUT / SRC_MIDI.name)

write_provenance(str(mix_wav), AI_ASSISTED, "SP-011 Karplus-Strong production pass",
                 sources=[str(SRC_MIDI)], parameters={"method": "SP-011", "roles": list(ROLES)})
write_provenance(str(ogg_path), AI_ASSISTED, "SP-011 Karplus-Strong production pass",
                 sources=[str(SRC_MIDI)], parameters={"method": "SP-011", "roles": list(ROLES)})
for role, sp in stems.items():
    write_provenance(sp, AI_ASSISTED, "SP-011 Karplus-Strong stem",
                     sources=[str(SRC_MIDI)], parameters={"role": role, "method": "SP-011"})

for p in [mix_wav, ogg_path] + [Path(v) for v in stems.values()]:
    assert p.stat().st_size > 1000, f"too small: {p}"

print("PRODUCE OK")
print(json.dumps({"mix": str(mix_wav), "ogg": str(ogg_path), "stems": stems,
                  "pitch": pitch_res, "stats": render_stats}, indent=1))
