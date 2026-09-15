# -*- coding: utf-8 -*-
"""Ground-truth pitch verification for the 096 renders (READING ONLY)."""
import json
import os
import wave

import mido  # READING ONLY (analysis)
import numpy as np
from structures import MusicUnit  # noqa: F401  (compliant-import marker)

PROJ = "/opt/data/repos/musicom/projects/Styles/Trap/096-trap-skeleton-seoul"
P1_WAV = os.path.join(PROJ, "Audio", "096-trap-skeleton-seoul-phase1.wav")
P2_WAV = os.path.join(PROJ, "Audio", "096-trap-skeleton-seoul.wav")
P1_MIDI = os.path.join(PROJ, "MIDI", "096-trap-skeleton-seoul-phase1.mid")
PHRYGIAN_PCS = {0, 1, 3, 5, 7, 8, 10}
BPM = 140


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


mono1, sr = load_mono(P1_WAV)
notes = midi_notes(P1_MIDI)
f0_present, harm_ok, checked = 0, 0, 0
detail = []
for (st, en, pitch) in notes:
    i0, i1 = int(st / 480 * (sr * 60 / BPM)), int(en / 480 * (sr * 60 / BPM))
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
    "source": "phase-1 (single marimba voice, known MIDI pitches)",
    "notes_in_midi": len(notes),
    "notes_checked": checked,
    "fundamental_present": f0_present,
    "fundamental_present_frac": round(f0_present / checked, 4) if checked else 0,
    "harmonic_ratio_gt_0.30": harm_ok,
    "harmonic_ratio_gt_0.30_frac": round(harm_ok / checked, 4) if checked else 0,
    "examples_first8": detail[:8],
}

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
    chroma_ok.append(set(np.argsort(ch_)[-3:]) <= PHRYGIAN_PCS)
    ac = np.correlate(seg - seg.mean(), seg - seg.mean(), "full")[win - 1:]
    ac /= (ac[0] + 1e-12)
    lag = int(sr / 1000), int(sr / 60)
    sub = ac[lag[0]:lag[1]]
    f0s.append(sub.argmax() + lag[0] if sub.max() > 0.25 else 0)

nPitched = sum(1 for x in f0s if x)
resB = {
    "source": "phase-2 (full trap mix, FluidSynth)",
    "windows": len(peaks),
    "frac_windows_on_12tet_note": round(sum(on_note) / len(on_note), 4) if on_note else 0,
    "median_harmonic_ratio": round(float(np.median(harm)), 4) if harm else 0,
    "frac_windows_harm_gt_0.30": round(sum(h > 0.30 for h in harm) / len(harm), 4) if harm else 0,
    "frac_windows_chroma_top3_in_key": round(sum(chroma_ok) / len(chroma_ok), 4) if chroma_ok else 0,
    "autocorr_frames_pitched": nPitched,
    "autocorr_frames_total": len(f0s),
}

verdictA = ("PASS" if checked and f0_present / checked > 0.9
            and harm_ok / checked > 0.9 else "CHECK")
verdictB = ("PASS" if resB["frac_windows_harm_gt_0.30"] > 0.5
            and resB["frac_windows_chroma_top3_in_key"] > 0.5
            else "CHECK")

out = {"phase1_ground_truth": resA, "verdict_phase1": verdictA,
       "phase2_polyphonic": resB, "verdict_phase2": verdictB}
with open(os.path.join(PROJ, "Analysis", "tonal_check.json"), "w") as f:
    json.dump(out, f, indent=2)
print("PHASE1: %d/%d fundamentals, %d/%d harmonic>0.30 -> %s" %
      (f0_present, checked, harm_ok, checked, verdictA))
print("PHASE2: on-note %.3f harm_med %.3f chroma %.3f pitched %d/%d -> %s" %
      (resB["frac_windows_on_12tet_note"], resB["median_harmonic_ratio"],
       resB["frac_windows_chroma_top3_in_key"], nPitched, len(f0s), verdictB))
