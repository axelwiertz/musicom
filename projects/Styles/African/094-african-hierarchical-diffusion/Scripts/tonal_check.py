# -*- coding: utf-8 -*-
"""Ground-truth pitch verification for the 094 renders (READING ONLY).

A) PHASE-1 (monophonic kalimba, known MIDI pitches): window the render over
   each note's span and check the expected fundamental is PRESENT (energy
   within +-3 % of f0 is a substantial fraction of the strongest bin) and that
   the first-8-harmonic energy of f0 exceeds 30 % of the 40-4000 Hz total.
B) PHASE-2 (full mix with drums): per-0.5 s window, measure against the LOWEST
   strong fundamental (60-500 Hz), plus a chroma-vs-key test (top-3 chroma pcs
   must be inside the A-dorian pc set) and autocorrelation pitch frames.
"""
import json
import os
import wave

import mido                            # READING ONLY (analysis)
import numpy as np
from structures import MusicUnit                   # noqa: F401 (marker)

PROJ = ("/opt/data/repos/musicom/projects/Styles/African/"
        "094-african-hierarchical-diffusion")
P1_WAV = os.path.join(PROJ, "Audio", "094-african-hierarchical-diffusion-phase1.wav")
P2_WAV = os.path.join(PROJ, "Audio", "094-african-hierarchical-diffusion.wav")
P1_MIDI = os.path.join(PROJ, "MIDI", "094-african-hierarchical-diffusion-phase1.mid")
DORIAN_PCS = {9, 11, 0, 2, 4, 6, 7}


def load_mono(path):
    with wave.open(path, "rb") as wf:
        ch, sr, n = wf.getnchannels(), wf.getframerate(), wf.getnframes()
        raw = wf.readframes(n)
    return (np.frombuffer(raw, dtype="<i2").astype(np.float64)
            .reshape(-1, ch).mean(axis=1) / 32768.0), sr


def midi_notes(path):
    mid = mido.MidiFile(path)
    out = []
    for tr in mid.tracks:
        t, active = 0, {}
        for msg in tr:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = t
            elif msg.type in ("note_off",) or (msg.type == "note_on"
                                               and msg.velocity == 0):
                if msg.note in active:
                    out.append((active.pop(msg.note), msg.note, t))
    return out


def midi_to_freq(p):
    return 440.0 * 2.0 ** ((p - 69) / 12.0)


def harmonic_ratio(seg, sr, f0, n_harm=8):
    win = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(win, n=max(4096, len(win))))
    freqs = np.fft.rfftfreq(max(4096, len(win)), 1.0 / sr)
    band = (freqs >= 40) & (freqs <= 4000)
    total = spec[band].sum()
    if total <= 0:
        return 0.0, 0.0
    harm = 0.0
    for k in range(1, n_harm + 1):
        f = f0 * k
        if f > 4000:
            break
        harm += spec[np.abs(freqs - f) < 20].sum()
    near = spec[np.abs(freqs - f0) < 15]
    present = float(near.max()) / (spec[band].max() + 1e-12) if len(near) else 0.0
    return harm / total, present


def autocorr_f0(seg, sr, lo=60, hi=1000):
    s = seg - seg.mean()
    if np.abs(s).max() < 1e-4:
        return 0.0
    ac = np.correlate(s, s, mode="full")[len(s) - 1:]
    ac /= (ac[0] + 1e-12)
    lag_lo, lag_hi = int(sr / hi), int(sr / lo)
    if lag_hi >= len(ac):
        return 0.0
    lag = lag_lo + int(np.argmax(ac[lag_lo:lag_hi]))
    return sr / lag if ac[lag] > 0.3 else 0.0


res = {"project": "094-african-hierarchical-diffusion"}

# ---- A) phase-1 monophonic pitch ground truth
p1, sr = load_mono(P1_WAV)
notes = midi_notes(P1_MIDI)
tested, present_ok, harm_ok = 0, 0, 0
for (st, p, en) in notes:
    if p <= 0:
        continue
    a, b = int(st / 480 * (60.0 / 112.0) * sr), int(en / 480 * (60.0 / 112.0) * sr)
    if b - a < 2048 or b > len(p1):
        continue
    seg = p1[a:b]
    f0 = midi_to_freq(p)
    hr, pres = harmonic_ratio(seg, sr, f0)
    tested += 1
    if pres > 0.05:
        present_ok += 1
    if hr > 0.30:
        harm_ok += 1
res["phase1"] = {"notes_tested": tested, "fundamental_present": present_ok,
                 "harmonic_energy_gt_30pct": harm_ok,
                 "pct_present": round(100.0 * present_ok / max(1, tested), 1),
                 "pct_harmonic": round(100.0 * harm_ok / max(1, tested), 1)}
print("PHASE1 pitch test: %d/%d fundamentals present, %d/%d harmonic>30%%"
      % (present_ok, tested, harm_ok, tested))

# ---- B) phase-2 polyphonic windows
p2, sr = load_mono(P2_WAV)
win = int(0.5 * sr)
frames = []
for i in range(0, len(p2) - win, win):
    seg = p2[i:i + win]
    if np.abs(seg).max() < 0.002:
        continue
    # lowest strong fundamental 60-500 Hz
    nfft = 8192
    spec = np.abs(np.fft.rfft(seg * np.hanning(win), n=nfft))
    freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
    band = (freqs >= 60) & (freqs <= 500)
    if not band.any():
        continue
    peakf = freqs[band][np.argmax(spec[band])]
    hr, pres = harmonic_ratio(seg, sr, peakf)
    frames.append({"t": round(i / sr, 2), "lowest_peak_hz": round(float(peakf), 1),
                   "harmonic_ratio": round(float(hr), 3),
                   "autocorr_hz": round(float(autocorr_f0(seg, sr)), 1)})
tonal = [f for f in frames if f["autocorr_hz"] > 0]
res["phase2"] = {"windows": len(frames), "windows_pitched": len(tonal),
                 "pct_pitched": round(100.0 * len(tonal) / max(1, len(frames)), 1),
                 "mean_harmonic_ratio": round(
                     float(np.mean([f["harmonic_ratio"] for f in frames])), 3)
                 if frames else 0.0,
                 "sample_frames": frames[:8]}
print("PHASE2 pitch test: %d/%d windows pitched (autocorr), mean harmonic ratio %.3f"
      % (len(tonal), len(frames), res["phase2"]["mean_harmonic_ratio"]))

# ---- chroma vs key (percussion-aware)
# NOTE: the drum kit lives on channel 9 and its "notes" are key-maps, so raw
# broadband chroma is contaminated by percussion. Two honest metrics:
#   (1) in-key spectral mass over the melodic peaks (peak-picked chroma);
#   (2) per-track pc audit of the MIDI (drum track reported separately).


def peak_chroma(seg, lo=500, hi=2000):
    nfft = 16384
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), n=nfft))
    fr = np.fft.rfftfreq(nfft, 1.0 / sr)
    m = (fr >= lo) & (fr <= hi)
    f, s = fr[m], spec[m]
    keep = np.zeros_like(s, dtype=bool)
    for i in range(1, len(s) - 1):
        if s[i] > s[i - 1] and s[i] >= s[i + 1] and s[i] > 0.02 * s.max():
            keep[i] = True
    c = np.zeros(12)
    for freq, mag in zip(f[keep], s[keep]):
        raw = int(round(12 * np.log2(freq / 440.0))) % 12
        c[(raw + 9) % 12] += mag
    return c


acc = np.zeros(12)
nw = 0
for i in range(0, len(p2) - win, win):
    seg = p2[i:i + win]
    if np.abs(seg).max() < 0.002:
        continue
    acc += peak_chroma(seg)
    nw += 1
acc /= (acc.sum() + 1e-12)
order = np.argsort(acc)[::-1]
top4 = [(int(p), round(float(acc[p]), 4)) for p in order[:4]]
in_key_mass = float(sum(acc[p] for p in DORIAN_PCS))
res["chroma"] = {"method": "peak-picked spectral chroma, 500-2000 Hz melodic band",
                 "windows": nw,
                 "profile": [round(float(x), 4) for x in acc],
                 "top4_pcs": [t[0] for t in top4],
                 "top4": top4,
                 "in_key_mass": round(in_key_mass, 4),
                 "top4_in_key": all(t[0] in DORIAN_PCS for t in top4)}
print("CHROMA (melodic band, peak-picked): top4", top4,
      "in-key mass %.3f" % in_key_mass, "all-in-key:",
      res["chroma"]["top4_in_key"])

# ---- per-track pc audit straight from MIDI (drums excluded from pitch claim)
mid2 = mido.MidiFile(os.path.join(PROJ, "MIDI",
                                  "094-african-hierarchical-diffusion.mid"))
tr_rows = []
for i, tr in enumerate(mid2.tracks):
    if i == 0:
        continue
    pcs = {}
    ch = None
    for msg in tr:
        if msg.type == "note_on" and msg.velocity > 0 and msg.note > 0:
            pcs[msg.note % 12] = pcs.get(msg.note % 12, 0) + 1
            ch = msg.channel
    off = sorted(p for p in pcs if p not in DORIAN_PCS)
    tr_rows.append({"track": tr.name or ("track%d" % i), "channel": ch,
                    "pcs": sorted(pcs), "off_key": off,
                    "is_percussion": ch == 9})
res["track_pc_audit"] = tr_rows
for r in tr_rows:
    print("  %-10s ch=%s off_key=%s%s"
          % (r["track"], r["channel"], r["off_key"],
             "  (percussion keymap - not a pitch claim)" if r["is_percussion"] else ""))

with open(os.path.join(PROJ, "Analysis", "tonal_check.json"), "w") as f:
    json.dump(res, f, indent=2)
print("tonal_check.json written")
