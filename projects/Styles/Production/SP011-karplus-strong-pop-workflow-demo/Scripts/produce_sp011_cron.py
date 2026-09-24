# -*- coding: utf-8 -*-
"""SP-011 Karplus-Strong production pass on Pop/workflow-demo (pop-001.mid).

Job: random-style production (SP) layer-aligned, 2026-09-24, seed 20260924.
Source: Styles/Pop/workflow-demo/MIDI/pop-001.mid
        Pop I-V-vi-IV framework, 120 BPM, 56 s, 491 notes across 5 tracks:
          track1 Flute(74) lead, track2 Piano(1) comp, track3 Contrabass(43)
          bass, track4 Clarinet(71) counter, track5 Drums(ch9).
Method: SP-011 -> sound.synthesis.karplus_strong
Layer : ABSOLUTE layer - every voice (melody, comp, bass, counter, drums)
        is re-rendered as a Karplus-Strong plucked string (no SoundFont
        timbres retained). Roles: lead / bass / perc (drums -> fast-decay
        percussive plucks).
"""
import json
import math
import os
import shutil
import subprocess
import wave
from pathlib import Path

import mido
import numpy as np

from sound.synthesis.karplus_strong import (
    render_melody, render_melody_wav, VOICE_ROLES, SR as KS_SR,
)
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Pop/workflow-demo/MIDI/pop-001.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP011-karplus-strong-pop-workflow-demo")
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20260924
TODAY = "2026-09-24"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# ---------------------------------------------------------------------------
# 1. Parse MIDI -> per-track note lists + global notes (absolute seconds)
# ---------------------------------------------------------------------------
BASS_PROGS = {32, 33, 43}  # acoustic bass, electric bass, contrabass
PERC_CHANNEL = 9


def parse_notes(mid_path):
    mid = mido.MidiFile(str(mid_path))
    ticks_per_beat = mid.ticks_per_beat
    tempo = 500000
    for tr in mid.tracks:
        for m in tr:
            if m.type == "set_tempo":
                tempo = m.tempo
    sec_per_tick = tempo / ticks_per_beat / 1_000_000.0

    tracks = []  # list of dicts: {name, program, channel, notes}
    for ti, tr in enumerate(mid.tracks):
        prog = None
        channel = None
        abs_tick = 0
        pending = {}
        tnotes = []
        for m in tr:
            abs_tick += m.time
            if m.type == "program_change":
                prog = m.program
                channel = m.channel
            elif m.type == "note_on":
                if m.velocity > 0:
                    pending[(m.channel, m.note)] = (abs_tick, m.velocity)
                else:
                    key = (m.channel, m.note)
                    if key in pending:
                        st, vel = pending.pop(key)
                        tnotes.append({
                            "pitch": m.note,
                            "start": st * sec_per_tick,
                            "end": abs_tick * sec_per_tick,
                            "velocity": vel,
                            "program": prog if prog is not None else 0,
                            "channel": channel if channel is not None else 0,
                        })
            elif m.type == "note_off":
                key = (m.channel, m.note)
                if key in pending:
                    st, vel = pending.pop(key)
                    tnotes.append({
                        "pitch": m.note,
                        "start": st * sec_per_tick,
                        "end": abs_tick * sec_per_tick,
                        "velocity": vel,
                        "program": prog if prog is not None else 0,
                        "channel": channel if channel is not None else 0,
                    })
        if tnotes:
            tracks.append({
                "name": tr.name or f"track{ti}",
                "program": prog if prog is not None else 0,
                "channel": channel if channel is not None else 0,
                "notes": tnotes,
            })
    return tracks, sec_per_tick


tracks, sec_per_tick = parse_notes(SRC)

all_notes = []
track_roles = []
for t in tracks:
    for n in t["notes"]:
        if n["channel"] == PERC_CHANNEL:
            role = "perc"
        elif n["program"] in BASS_PROGS:
            role = "bass"
        else:
            role = "lead"
        d = dict(n)
        d["role"] = role
        all_notes.append(d)
    track_roles.append({
        "name": t["name"],
        "program": t["program"],
        "channel": t["channel"],
        "n_notes": len(t["notes"]),
    })

global_end = max((n["end"] for n in all_notes), default=1.0)
print(f"Parsed {len(tracks)} tracks, {len(all_notes)} notes, global_end={global_end:.2f}s")
for tr in track_roles:
    print(f"  {tr}")

# ---------------------------------------------------------------------------
# 2. Role configs (lead/bass from VOICE_ROLES + custom perc for drums)
# ---------------------------------------------------------------------------
ROLES = dict(VOICE_ROLES)
ROLES["perc"] = {
    "gains": [1.0], "width": 0.20, "pan_drift": False,
    "gain_db": -8.0, "loop_gain": 0.970,  # fast decay -> percussive
}

# ---------------------------------------------------------------------------
# 3. Render full mix (Karplus-Strong, all voices)
# ---------------------------------------------------------------------------
stereo_full, info = render_melody(all_notes, sr=SR, roles=ROLES)
# render_melody returns (N, 2) float in [-1,1], already peak-normalized -1 dB
print(f"Full mix shape: {stereo_full.shape}, note_count={info['note_count']}")
print(f"roles: {json.dumps(info['roles'], indent=2)}")

# ---------------------------------------------------------------------------
# 4. Render per-track stems (time-aligned via silent tail pad to global_end)
# ---------------------------------------------------------------------------
stem_paths = {}
for t in tracks:
    stem_notes = []
    for n in t["notes"]:
        d = dict(n)
        if n["channel"] == PERC_CHANNEL:
            d["role"] = "perc"
        elif n["program"] in BASS_PROGS:
            d["role"] = "bass"
        else:
            d["role"] = "lead"
        stem_notes.append(d)
    # silent dummy note to force identical total length (time-aligned stems)
    stem_notes.append({
        "pitch": 60, "start": global_end, "end": global_end + 0.01,
        "velocity": 0, "role": "lead",
    })
    stem_audio, _ = render_melody(stem_notes, sr=SR, roles=ROLES)
    stem_audio = stem_audio[: stereo_full.shape[0]]
    if stem_audio.shape[0] < stereo_full.shape[0]:
        pad = np.zeros((stereo_full.shape[0] - stem_audio.shape[0], 2),
                       dtype=np.float32)
        stem_audio = np.vstack([stem_audio, pad])
    label = f"track{len(stem_paths):02d}_{t['name'].replace(' ', '_')}"
    stem_path = STEMS / f"{label}.wav"
    pcm = (np.clip(stem_audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(stem_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    stem_paths[label] = str(stem_path)
print(f"Wrote {len(stem_paths)} stems")

# ---------------------------------------------------------------------------
# 5. Master: normalize -14 LUFS, Limiter(-1 dBFS)  (mastering wants (N,2))
# ---------------------------------------------------------------------------
normed = normalize_to_lufs(stereo_full, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
limited = limiter.process(normed)  # (N, 2)

final_wav = OUT / "SP011-karplus-strong-pop-workflow-demo.wav"
final_ogg = OUT / "SP011-karplus-strong-pop-workflow-demo.ogg"

pcm = (np.clip(limited, -1, 1) * 32767).astype(np.int16)
with wave.open(str(final_wav), "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm.tobytes())
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

r2 = subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
     "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)],
    capture_output=True, text=True)
if r2.returncode != 0:
    raise RuntimeError(f"ffmpeg failed: {r2.stderr[-300:]}")
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# ---------------------------------------------------------------------------
# 6. Verification: LUFS / peak / silence / RMS / pitch
# ---------------------------------------------------------------------------
measured_lufs = measure_lufs(limited, sample_rate=SR)
peak_val = float(np.max(np.abs(limited)))
mono_mix = 0.5 * (limited[:, 0] + limited[:, 1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
mono_corr = float(np.corrcoef(limited[:, 0], limited[:, 1])[0, 1])

n_sec = len(mono_mix) // SR
rms_per_sec = [float(np.sqrt(np.mean(mono_mix[s * SR:(s + 1) * SR] ** 2) + 1e-12))
               for s in range(n_sec)]

# --- pitch verification: dominant FFT peak vs SOURCE sounding notes ---------
# reference = source note (pitch, start, end). Check dominant freq matches a
# sounding note's fundamental or an integer harmonic (catches octave drop).
window_len = int(0.5 * SR)
num_windows = len(mono_mix) // window_len
hits = 0
valid_windows = 0
harmonic_energies = []
dominant_freqs = []


def sounding_freqs(t_center):
    """Fundamental frequencies of notes sounding at time t_center."""
    out = []
    for n in all_notes:
        if n["start"] <= t_center < n["end"]:
            f = 440.0 * (2.0 ** ((n["pitch"] - 69) / 12.0))
            out.append(f)
    return out


for w in range(num_windows):
    seg = mono_mix[w * window_len:(w + 1) * window_len]
    if np.max(np.abs(seg)) < 0.005:
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
    dom_f = float(sub_freqs[np.argmax(sub_spec)])
    dominant_freqs.append(dom_f)

    # harmonic energy in first 8 harmonics of dom_f (fundamental+overtones)
    tot_energy = float(np.sum(fft_spec ** 2)) + 1e-12
    h_energy = 0.0
    for h in range(1, 9):
        tf = dom_f * h
        hm = (freqs >= tf - 15.0) & (freqs <= tf + 15.0)
        h_energy += float(np.sum(fft_spec[hm] ** 2))
    harmonic_energies.append(h_energy / tot_energy)

    # match dom_f to a sounding note fundamental or integer harmonic
    t_center = (w + 0.5) * window_len / SR
    s_freqs = sounding_freqs(t_center)
    matched = False
    if s_freqs:
        for sf in s_freqs:
            for h in range(1, 9):
                if abs(dom_f - sf * h) <= 15.0:
                    matched = True
                    break
            if matched:
                break
    if matched:
        hits += 1

hit_rate = hits / max(1, valid_windows)
mean_he = float(np.mean(harmonic_energies)) if harmonic_energies else 0.0
median_freq = float(np.median(dominant_freqs)) if dominant_freqs else 0.0

# Independent noise gate: normalized autocorrelation pitch detection per window.
# A pitched pluck -> a strong ACF peak in the lag range; noise -> 0 Hz frame.
def acf_pitch(seg, lo=50.0, hi=1000.0):
    n = len(seg)
    x = seg - np.mean(seg)
    acf = np.correlate(x, x, mode="full")[n - 1:]
    lo_lag = max(1, int(SR / hi))
    hi_lag = min(n - 1, int(SR / lo))
    if hi_lag <= lo_lag:
        return 0.0
    seg_acf = acf[lo_lag:hi_lag + 1] / max(acf[0], 1e-12)
    k = int(np.argmax(seg_acf))
    if seg_acf[k] < 0.25:
        return 0.0
    return float(SR / (lo_lag + k))

pitched_windows = 0
for w in range(num_windows):
    seg = mono_mix[w * window_len:(w + 1) * window_len]
    if np.max(np.abs(seg)) < 0.005:
        continue
    if acf_pitch(seg) > 0.0:
        pitched_windows += 1
acf_frac = pitched_windows / max(1, valid_windows)

# Verdict: hit_rate is decisive (noise -> dominant peak matches no source note,
# giving hit_rate ~ 0). mean_HE confirms harmonic content (noise -> < 0.05).
pitch_verdict = "PASS" if (hit_rate >= 0.60 and acf_frac >= 0.90) else "FAIL"
print(f"Pitch Verification: valid={valid_windows}, hits={hits}, "
      f"hit_rate={hit_rate:.4f}, mean_HE={mean_he:.4f}, median_f={median_freq:.1f}Hz, "
      f"acf_pitched_frac={acf_frac:.4f}")
print(f"Master: LUFS={measured_lufs:.2f}, peak={peak_val:.4f}, "
      f"silence={silence_ratio:.2f}%, mono_corr={mono_corr:.3f}")
print(f"RMS/s (first 20): {[round(r,3) for r in rms_per_sec[:20]]}")

# ---------------------------------------------------------------------------
# 7. Grid visualization (rhythm DNA: onset matrix per track)
# ---------------------------------------------------------------------------
BAR_SEC = 4 * 60.0 / 120.0  # 4/4 @ 120 BPM = 2.0 s
n_bars = int(math.ceil(global_end / BAR_SEC))
n_steps = 16  # 16th-note grid per bar
step_sec = BAR_SEC / n_steps
grid_lines = []
grid_lines.append(f"SP-011 rhythm DNA grid — {SRC.name} (120 BPM, 4/4)")
grid_lines.append("rows = tracks, cols = 16th-note steps; # = onset, . = rest")
grid_lines.append("")
header = "track".ljust(24) + " |" + "".join(str(b % 10) for b in range(n_bars))
grid_lines.append(header)
grid_lines.append("-" * len(header))
for ti, t in enumerate(tracks):
    onset_cells = [0] * (n_bars * n_steps)
    for n in t["notes"]:
        idx = int(n["start"] / step_sec)
        if 0 <= idx < len(onset_cells):
            onset_cells[idx] = 1
    row = t["name"].ljust(24) + " |" + "".join("#" if c else "." for c in onset_cells)
    grid_lines.append(row)
grid_lines.append("")
grid_lines.append(f"bar = {BAR_SEC:.2f}s, step = {step_sec*1000:.0f}ms, "
                  f"bars = {n_bars}")
grid_text = "\n".join(grid_lines)
(ANALYSIS / "grid_visualization.txt").write_text(grid_text)
print("Wrote grid_visualization.txt")

# ---------------------------------------------------------------------------
# 8. Artifacts (render_stats / pitch / provenance / select / cron)
# ---------------------------------------------------------------------------
render_stats = {
    "method": "SP-011",
    "module": "sound.synthesis.karplus_strong",
    "method_desc": "Karplus-Strong String Synthesis",
    "seed": SEED,
    "source_midi": str(SRC),
    "source_project": "Pop/workflow-demo",
    "bpm": 120,
    "duration_sec": round(global_end, 2),
    "note_count": len(all_notes),
    "tracks": track_roles,
    "roles_used": sorted(set(n["role"] for n in all_notes)),
    "loop_gain_default": VOICE_ROLES["lead"]["loop_gain"],
    "lufs": measured_lufs,
    "peak": peak_val,
    "silence_pct": silence_ratio,
    "mono_correlation": mono_corr,
    "rms_per_sec": rms_per_sec,
    "valid_windows": valid_windows,
    "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he,
    "median_freq_hz": median_freq,
    "acf_pitched_frac": acf_frac,
    "pitch_verdict": pitch_verdict,
}
(ANALYSIS / "render_stats.json").write_text(json.dumps(render_stats, indent=2))

# source pitch-class histogram (for the report)
pc_hist = {}
for n in all_notes:
    pc_hist[n["pitch"] % 12] = pc_hist.get(n["pitch"] % 12, 0) + 1
top_pcs = sorted(pc_hist, key=pc_hist.get, reverse=True)

pitch_json = {
    "method": "SP-011",
    "project": "Pop/workflow-demo",
    "source_pc_histogram": {str(k): v for k, v in sorted(pc_hist.items())},
    "top_pitch_classes": top_pcs,
    "status": pitch_verdict,
    "hit_rate": hit_rate,
    "harmonic_energy_mean": mean_he,
    "acf_pitched_frac": acf_frac,
    "windows_analyzed": valid_windows,
    "median_freq_hz": median_freq,
}
(ANALYSIS / "pitch_verification.json").write_text(json.dumps(pitch_json, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": TODAY,
    "seed": SEED,
    "method": "SP-011",
    "method_module": "sound.synthesis.karplus_strong",
    "method_desc": "Karplus-Strong String Synthesis",
    "source_midi": str(SRC),
    "source_project": "Pop/workflow-demo",
    "excluded_recent_methods": sorted(RECENT := {"SP-069", "SP-090", "SP-033",
                                                "SP-080", "SP-083", "SP-084",
                                                "SP-072"}),
    "baseline_excluded": ["SP-001"],
    "roles_used": sorted(set(n["role"] for n in all_notes)),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs,
    "peak": peak_val,
    "silence_pct": silence_ratio,
    "mono_correlation": mono_corr,
    "pitch_verdict": pitch_verdict,
    "hit_rate": hit_rate,
    "he_mean": mean_he,
    "acf_pitched_frac": acf_frac,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(
    json.dumps(provenance, indent=2))

select_json = {
    "date": TODAY,
    "seed": SEED,
    "method": "SP-011",
    "method_module": "sound.synthesis.karplus_strong",
    "source_midi": str(SRC),
    "excluded_recent_methods": ["SP-069", "SP-090", "SP-033", "SP-080",
                                "SP-083", "SP-084", "SP-072"],
    "baseline_excluded": ["SP-001"],
}
(ANALYSIS / "select_20260924.json").write_text(json.dumps(select_json, indent=2))

# self-copy script
try:
    if os.path.abspath(__file__) != os.path.abspath(str(SCRIPTS / "produce_sp011_cron.py")):
        shutil.copy2(__file__, str(SCRIPTS / "produce_sp011_cron.py"))
except Exception as e:
    print(f"note: script self-copy skipped: {e}")

print("DONE. pitch_verdict=", pitch_verdict, "hit_rate=", round(hit_rate, 4),
      "silence=", round(silence_ratio, 2), "%")
