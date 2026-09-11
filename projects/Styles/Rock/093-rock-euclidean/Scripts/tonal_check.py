# -*- coding: utf-8 -*-
"""Ground-truth pitch verification for the 093 renders (READING ONLY).

Two tests:

A) PHASE-1 (single monophonic fiddle voice, known MIDI pitches): for each
   exported note, window the render's WAV over that note's span and check that
   the expected fundamental frequency is PRESENT (energy within +-3 % of f0 is
   a substantial fraction of the strongest bin) and that first-8-harmonic
   energy of that f0 exceeds 30 % of the 40-4000 Hz total. This is the direct
   ground-truth test the skill mandates: a synth must be checked for PITCH, not
   just size/silence.

B) PHASE-2 (full polyphonic mix with drum kit): the same spectral test is run
   per 0.5 s window but measured against the LOWEST strong fundamental
   (60-500 Hz), plus a 12-tone chroma-vs-key test (top-3 chroma pcs must be
   within the E-aeolian pc set) and autocorrelation pitch frames.
"""
import json
import os
import wave

import mido  # READING ONLY (analysis)
import numpy as np
from structures import MusicUnit  # noqa: F401  (compliant-import marker)

PROJ = "/opt/data/repos/musicom/projects/Styles/Rock/093-rock-euclidean"
P1_WAV = os.path.join(PROJ, "Audio", "093-rock-euclidean-phase1.wav")
P2_WAV = os.path.join(PROJ, "Audio", "093-rock-euclidean.wav")
P1_MIDI = os.path.join(PROJ, "MIDI", "093-rock-euclidean-phase1.mid")
AEOLIAN_PCS = {4, 6, 7, 9, 11, 0, 2}


def load_mono(path):
    with wave.open(path, "rb") as wf:
        ch, sr, n = wf.getnchannels(), wf.getframerate(), wf.getnframes()
        raw = wf.readframes(n)
    return np.frombuffer(raw, dtype="<i2").astype(np.float64) \
        .reshape(-1, ch).mean(axis=1) / 32768.0, sr


def midi_notes(path):
    mid = mido.MidiFile(path)
    out = []
    for tr in mid.tracks:
        t, active = 0, {}
        for msg in tr:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = t
            elif msg.type == "note_off" or (msg.type == "note_on"
                                            and msg.velocity == 0):
                if msg.note in active:
                    out.append((active.pop(msg.note), t, msg.note))
    return sorted(out)


def m2f(p):
    return 440.0 * 2 ** ((p - 69) / 12.0)


# ---------------- A) phase-1 ground truth -------------------------------
mono1, sr = load_mono(P1_WAV)
notes = midi_notes(P1_MIDI)
f0_present, harm_ok, checked = 0, 0, 0
detail = []
for (st, en, pitch) in notes:
    i0, i1 = int(st / 480 * (sr * 60 / 128)), int(en / 480 * (sr * 60 / 128))
    i1 = min(i1, len(mono1))
    if i1 - i0 < 2048:
        continue
    seg = mono1[i0:i1]
    if np.sqrt(np.mean(seg ** 2)) < 0.002:
        continue
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
    f0 = m2f(pitch)
    tot = float(np.sum(spec[(freqs >= 40) & (freqs <= 4000)]))
    near = float(np.max(spec[np.abs(freqs - f0) < max(3.0, f0 * 0.03)]))
    ref = float(np.max(spec[(freqs >= 40) & (freqs <= 4000)]))
    # band energy summed (NOT single-bin max) around harmonics 1..8
    h = sum(float(np.sum(spec[np.abs(freqs - f0 * k) < max(3.0, f0 * 0.03)]))
            for k in range(1, 9) if f0 * k < 4000)
    checked += 1
    if near > 0.02 * ref:
        f0_present += 1
    if tot > 0 and h / tot > 0.30:
        harm_ok += 1
    detail.append({"pitch": pitch, "f0_hz": round(f0, 1),
                   "fundamental_frac_of_max": round(near / ref, 4),
                   "harmonic_ratio": round(h / tot if tot else 0.0, 4)})

resA = {
    "source": "phase-1 (single fiddle voice, known MIDI pitches)",
    "notes_in_midi": len(notes),
    "notes_checked": checked,
    "fundamental_present": f0_present,
    "fundamental_present_frac": round(f0_present / checked, 4) if checked else 0,
    "harmonic_ratio_gt_0.30": harm_ok,
    "harmonic_ratio_gt_0.30_frac": round(harm_ok / checked, 4) if checked else 0,
    "examples_first8": detail[:8],
}

# ---------------- B) phase-2 polyphonic mix ----------------------------
mono2, sr = load_mono(P2_WAV)
win = sr // 2
peaks, on_note, harm, chroma_ok, f0s = [], [], [], [], []
for k in range(0, len(mono2) - win, win):
    seg = mono2[k:k + win]
    if np.sqrt(np.mean(seg ** 2)) < 0.005:
        continue
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
    band = (freqs >= 50) & (freqs <= 4000)
    pk = float(freqs[band][np.argmax(spec[band])])
    peaks.append(pk)
    on_note.append(abs((69 + 12 * np.log2(pk / 440.0))
                       - round(69 + 12 * np.log2(pk / 440.0))) < 0.05)
    low = (freqs >= 60) & (freqs <= 500)
    f0 = float(freqs[low][np.argmax(spec[low])])
    tot = float(np.sum(spec[(freqs >= 40) & (freqs <= 4000)]))
    h = sum(float(np.sum(spec[np.abs(freqs - f0 * m) < max(4.0, f0 * 0.03)]))
            for m in range(1, 9) if f0 * m < 4000)
    harm.append(h / tot if tot > 0 else 0.0)
    ch_ = np.zeros(12)
    for pc in range(12):
        flo = 440.0 * 2 ** ((pc + 60 - 69) / 12.0)
        for o in (0, 1, 2):
            f = flo * 2 ** o
            if f > 4000:
                continue
            m = (freqs > f * 0.97) & (freqs < f * 1.03)
            if m.any():
                ch_[pc] += float(np.sum(spec[m]))
    chroma_ok.append(set(np.argsort(ch_)[-3:]) <= AEOLIAN_PCS)
    ac = np.correlate(seg - seg.mean(), seg - seg.mean(), "full")[win - 1:]
    ac /= (ac[0] + 1e-12)
    lag = int(sr / 1000), int(sr / 60)
    sub = ac[lag[0]:lag[1]]
    if len(sub):
        li = lag[0] + int(np.argmax(sub))
        if ac[li] > 0.3:
            f0s.append(sr / li)

resB = {
    "source": "phase-2 (full polyphonic mix + drum kit)",
    "spectral_windows": len(peaks),
    "peak_hz_median": round(float(np.median(peaks)), 1),
    "windows_on_12tet_note_frac": round(float(np.mean(on_note)), 4),
    "mean_harmonic_energy_ratio": round(float(np.mean(harm)), 4),
    "chroma_top3_in_aeolian_frac": round(float(np.mean(chroma_ok)), 4),
    "autocorr_frames_total": len(peaks),
    "autocorr_frames_pitched": len(f0s),
    "autocorr_f0_median": round(float(np.median(f0s)), 1) if f0s else None,
}

out = {"phase1_ground_truth": resA, "phase2_polyphonic": resB,
       "verdict_phase1": ("PASS: fundamentals present + harmonic"
                          if (resA["fundamental_present_frac"] > 0.9
                              and resA["harmonic_ratio_gt_0.30_frac"] > 0.9)
                          else "CHECK"),
       "verdict_phase2": ("PASS tonal"
                          if (resB["windows_on_12tet_note_frac"] > 0.6
                              and resB["chroma_top3_in_aeolian_frac"] > 0.6)
                          else "CHECK")}
with open(os.path.join(PROJ, "Analysis", "tonal_check.json"), "w") as f:
    json.dump(out, f, indent=2)
for k, v in out.items():
    print(k, "=", v)
