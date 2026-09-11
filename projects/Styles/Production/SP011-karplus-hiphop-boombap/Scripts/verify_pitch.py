#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-011 boom-bap pitch verification — two independent methods per note.

Method A (autocorrelation, 50-1500 Hz): octave-tolerant match to the expected f0.
Method B (spectral, expected-guided): the expected fundamental OR one of its first
  6 harmonics must be among the top-6 spectral peaks in 50-2000 Hz (4% tolerance),
  AND the harmonic series energy share of the 50-2000 Hz band is reported.
Also prints raw debug for failing notes so the failure mode is visible.
"""
import json
import wave
from collections import Counter
from pathlib import Path

import mido
import numpy as np

from sound.synthesis.karplus_strong import midi_to_freq

ROOT = Path("/opt/data/repos/musicom")
OUT = ROOT / "projects/Styles/Production/SP011-karplus-hiphop-boombap"
SRC = ROOT / "projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid"
STEMS = OUT / "Audio/stems"
ORDER = ("lead", "comp", "bass", "perc")


def read_mono(p):
    with wave.open(str(p), "rb") as wf:
        sr, nch = wf.getframerate(), wf.getnchannels()
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
    return raw.reshape(-1, nch).mean(axis=1), sr


mid = mido.MidiFile(str(SRC))
tempo = next((m.tempo for m in mid.tracks[0] if m.type == "set_tempo"), 500000)
PPQ = mid.ticks_per_beat
t2s = lambda t: t * tempo / PPQ / 1_000_000

notes = []
for ti, tr in enumerate(mid.tracks):
    prog = next((m.program for m in tr if m.type == "program_change"), 0)
    at, active = 0, {}
    for m in tr:
        at += m.time
        if m.type == "note_on" and m.velocity > 0:
            active.setdefault(m.note, []).append((at, m.velocity, m.channel))
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            if active.get(m.note):
                s, vel, ch = active[m.note].pop(0)
                notes.append({"program": prog, "channel": ch, "pitch": m.note,
                              "start": t2s(s), "end": t2s(at)})
for n in notes:
    n["role"] = "perc" if n["channel"] == 9 else ("bass" if n["program"] == 33 else ("comp" if n["program"] == 88 else "lead"))

res = {"per_note": {}, "debug": {}}
for role in ("bass", "lead", "comp"):
    m, sr = read_mono(STEMS / f"track{ORDER.index(role):02d}_{role}.wav")
    rn = sorted([n for n in notes if n["role"] == role], key=lambda x: x["start"])
    acf_hits = spec_hits = tot = 0
    acf_oct = Counter()
    harm_shares = []
    dbg = []
    for n in rn:
        w0 = int((n["start"] + 0.03) * sr)
        wl = int(min(0.22, max(0.10, n["end"] - n["start"])) * sr)
        if w0 + wl >= len(m):
            continue
        tot += 1
        seg = m[w0:w0 + wl]
        exp = midi_to_freq(n["pitch"])
        # --- A: autocorrelation ---
        s = seg - seg.mean()
        ac = np.correlate(s, s, "full")[len(s) - 1:]
        ac = ac / ac[0] if ac[0] > 0 else ac
        lo, hi = int(sr / 1500), min(int(sr / 50), len(ac) - 1)
        lag = lo + int(np.argmax(ac[lo:hi]))
        f0 = sr / lag
        conf = float(ac[lo:hi].max())
        ratios = [f0 / exp]
        best_h = min((1, 2, 3, 4, 0.5), key=lambda h: abs(f0 - exp * h))
        ok_a = conf > 0.35 and abs(f0 - exp * best_h) / (exp * best_h) < 0.06
        acf_hits += int(ok_a)
        if ok_a:
            acf_oct[best_h] += 1
        # --- B: spectral, expected-guided ---
        w = seg * np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(w))
        ff = np.fft.rfftfreq(len(w), 1 / sr)
        bm = (ff >= 50) & (ff <= 2000)
        ffb, spb = ff[bm], spec[bm]
        top_idx = np.argsort(spb)[::-1][:6]
        top_f = [float(ffb[i]) for i in top_idx]
        ok_b = any(abs(tf - exp * h) / (exp * h) < 0.04 for tf in top_f for h in range(1, 7))
        spec_hits += int(ok_b)
        hsum = sum(float(np.sum(spec[(ff >= exp * h * 0.97) & (ff <= exp * h * 1.03)]))
                   for h in range(1, 7))
        share = 100 * hsum / max(float(np.sum(spec[bm])), 1e-12)
        harm_shares.append(share)
        if not ok_b and len(dbg) < 8:
            dbg.append({"t": round(n["start"], 2), "midi": n["pitch"], "exp_f0": round(exp, 1),
                        "acf_f0": round(f0, 1), "acf_conf": round(conf, 3),
                        "top6_peaks": [round(x, 1) for x in top_f], "harm_share_pct": round(share, 1)})
    res["per_note"][role] = {
        "notes": tot,
        "acf_hit": acf_hits, "acf_pct": round(100 * acf_hits / max(1, tot), 1),
        "acf_octave_ratio_hist": {str(k): v for k, v in sorted(acf_oct.items())},
        "spectral_hit": spec_hits, "spectral_pct": round(100 * spec_hits / max(1, tot), 1),
        "harm_share_mean_pct": round(float(np.mean(harm_shares)), 1) if harm_shares else None,
        "harm_share_pct": round(100 * spec_hits / max(1, tot), 1),
    }
    res["debug"][role] = dbg

# --- full mix: expected-guided spectral frames + ACF frames ---
mix, sr = read_mono(OUT / "Audio/SP011-karplus-hiphop-boombap.wav")
frames = []
win, hop = int(0.5 * sr), int(0.25 * sr)
for w0 in range(0, max(1, len(mix) - win), hop):
    seg = mix[w0:w0 + win]
    t0 = w0 / sr
    s = seg - seg.mean()
    ac = np.correlate(s, s, "full")[len(s) - 1:]
    ac = ac / ac[0] if ac[0] > 0 else ac
    lo, hi = int(sr / 1000), min(int(sr / 50), len(ac) - 1)
    lag = lo + int(np.argmax(ac[lo:hi]))
    near = [n for n in notes if n["role"] != "perc" and n["start"] - 0.4 <= t0 <= n["end"] + 1.3]
    w = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(w))
    ff = np.fft.rfftfreq(len(w), 1 / sr)
    top_idx = np.argsort(spec)[::-1][:8]
    top_f = [float(ff[i]) for i in top_idx if 50 <= ff[i] <= 2000]
    hits = sum(1 for n in near
               if any(abs(tf - midi_to_freq(n["pitch"]) * h) / (midi_to_freq(n["pitch"]) * h) < 0.03
                      for tf in top_f for h in range(1, 7)))
    frames.append({"t": round(t0, 2), "acf_f0": round(sr / lag, 1), "acf_conf": round(float(ac[lo:hi].max()), 3),
                   "n_expected_near": len(near), "n_hit": hits})
pitched = [f for f in frames if f["acf_conf"] > 0.35]
res["mix_frames"] = {
    "frames": len(frames), "acf_pitched": len(pitched),
    "acf_pitched_pct": round(100 * len(pitched) / max(1, len(frames)), 1),
    "frames_with_all_expected_notes_spectrally_present": sum(1 for f in frames if f["n_expected_near"] and f["n_hit"] == f["n_expected_near"]),
    "frames_with_any_expected_note_spectrally_present": sum(1 for f in frames if f["n_hit"] > 0),
}

(OUT / "Analysis/pitch_verification.json").write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2)[:4000])
