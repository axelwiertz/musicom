# -*- coding: utf-8 -*-
"""Per-voice gated pitch verification for the formant choir (V4).

The mix-level dominant-peak test is dominated by the C3 drone (every window
contains MIDI 48 -> 131 Hz, and the drone's uw spectrum peaks exactly there).
Gate per voice on its own wet stem:
  melody stem: windows where a melody note sounds; match dom peak vs that
    note's f0 (+harmonics 2-4, +/-2%).
  drone stem: windows where drone sounds; match vs 130.81 Hz (+harmonics).
Also harmonic energy per stem, ACF unpitched, silence/RMS on final mix.
"""
import json
import mido
import numpy as np
import wave

SR = 44100
OUT = "/opt/data/repos/musicom/projects/Styles/Production/SP036-formant-lsystem-choir"
TEMPO_US = 545455
TPB = 480


def read_mono(path):
    with wave.open(path, "r") as wf:
        n = wf.getnframes()
        ch = wf.getnchannels()
        sr = wf.getframerate()
        raw = wf.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a, sr


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def parse_tracks(path):
    mid = mido.MidiFile(path)
    out = []
    for ti, tr in enumerate(mid.tracks):
        prog = None
        for msg in tr:
            if msg.type == "program_change":
                prog = msg.program
                break
        abstick = 0
        active = {}
        notes = []
        for msg in tr:
            abstick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = abstick
            elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active:
                    s = active.pop(msg.note)
                    notes.append({"pitch": msg.note,
                                  "start": s * TEMPO_US / TPB / 1e6,
                                  "end": abstick * TEMPO_US / TPB / 1e6})
        out.append({"idx": ti, "prog": prog, "notes": sorted(notes, key=lambda e: e["start"])})
    return out


def dom_peak(seg, sr, lo=50, hi=1000):
    w = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(w))
    freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
    band = (freqs >= lo) & (freqs <= hi)
    fb, sb = freqs[band], spec[band]
    return float(fb[np.argmax(sb)]), spec, freqs


def harm_share(spec, freqs, f0, nh=8, hi=1000):
    band = (freqs >= 50) & (freqs <= hi)
    tot = float(np.sum(spec[band] ** 2)) + 1e-12
    e = 0.0
    for k in range(1, nh + 1):
        fk = f0 * k
        if fk > hi:
            break
        b = np.argmin(np.abs(freqs - fk))
        lo, hi2 = max(0, b - 2), min(len(spec), b + 3)
        e += float(np.sum(spec[lo:hi2] ** 2))
    return e / tot


tracks = parse_tracks(OUT + "/MIDI/lsystem_study.mid")
melody_notes = next(t["notes"] for t in tracks if t["prog"] == 80)
drone_notes = next(t["notes"] for t in tracks if t["prog"] == 88)
mel_stem, _ = read_mono(OUT + "/Audio/stems_wet/track01_Lead_1_square.wav")
dro_stem, _ = read_mono(OUT + "/Audio/stems_wet/track02_Pad_1_new_age.wav")
mix_st, mix_mo, _ = read_mono(OUT + "/SP036-formant-lsystem-choir.wav") if False else (None, None, None)

import wave as _w
with _w.open(OUT + "/SP036-formant-lsystem-choir.wav", "r") as wf:
    n, ch = wf.getnframes(), wf.getnchannels()
    raw = wf.readframes(n)
a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
mix_mo = a.reshape(-1, ch).mean(axis=1) if ch > 1 else a
mix_st = a.reshape(-1, ch) if ch > 1 else np.column_stack([a, a])

WIN = int(0.25 * SR)
HOP = int(0.25 * SR)


def gate_voice(stem, notes, label):
    hits = checked = 0
    ratios = []
    misses = []
    for start in range(0, len(stem) - WIN + 1, HOP):
        t0, t1 = start / SR, (start + WIN) / SR
        act = [x for x in notes if x["start"] < t1 - 0.02 and x["end"] > t0 + 0.02]
        if not act:
            continue
        seg = stem[start:start + WIN]
        if np.max(np.abs(seg)) < 1e-4:
            continue
        dom, spec, freqs = dom_peak(seg, SR)
        # expected: the note with max overlap in this window
        def overlap(x):
            return min(x["end"], t1) - max(x["start"], t0)
        lead = max(act, key=overlap)
        f0 = midi_to_freq(lead["pitch"])
        ratios.append(harm_share(spec, freqs, f0))
        ok = any(abs(dom - f0 * k) / (f0 * k) <= 0.02 for k in (1, 2, 3, 4))
        checked += 1
        hits += 1 if ok else 0
        if not ok:
            misses.append((round(t0, 2), round(dom, 1), lead["pitch"], round(f0, 1)))
    print(f"{label}: {hits}/{checked} = {hits/checked:.4f}" if checked else f"{label}: no windows")
    for m in misses[:12]:
        print(f"  miss t={m[0]}s dom={m[1]}Hz pitch={m[2]} f0={m[3]}Hz")
    return hits, checked, float(np.median(ratios)) if ratios else 0.0, misses


mh, mc, mrat, mmiss = gate_voice(mel_stem, melody_notes, "melody stem")
dh, dc, drat, dmiss = gate_voice(dro_stem, drone_notes, "drone stem")

# ACF on mix
acf_bad = 0
frames = 0
W2, H2 = int(0.5 * SR), int(0.5 * SR)
for start in range(0, len(mix_mo) - W2 + 1, H2):
    frames += 1
    seg = mix_mo[start:start + W2].astype(np.float64)
    seg = seg - seg.mean()
    if np.max(np.abs(seg)) < 1e-4:
        acf_bad += 1
        continue
    ac = np.correlate(seg, seg, mode="full")[len(seg) - 1:]
    ac = ac / (ac[0] + 1e-12)
    lo, hi = int(SR / 1000.0), int(SR / 40.0)
    if float(np.max(ac[lo:hi])) < 0.30:
        acf_bad += 1
print(f"mix ACF unpitched: {acf_bad}/{frames}")

sil = float(np.sum(np.abs(mix_mo) < 0.001) / len(mix_mo))
rms_map = [float(np.sqrt(np.mean(mix_mo[i*SR:(i+1)*SR]**2))) for i in range(int(len(mix_mo)/SR))]
print(f"mix silence={sil:.4f} dur={len(mix_mo)/SR:.2f}s peak={np.max(np.abs(mix_mo)):.4f}")
print("rms:", " ".join(f"{v:.4f}" for v in rms_map))

from sound.effects.mastering import measure_lufs
lufs = float(measure_lufs(mix_st, sample_rate=SR))
print(f"LUFS={lufs:.2f}")

res = {"melody": {"hits": mh, "checked": mc, "hit_rate": mh / mc if mc else 0,
                  "median_harmonic_ratio": mrat, "misses": mmiss[:20]},
       "drone": {"hits": dh, "checked": dc, "hit_rate": dh / dc if dc else 0,
                 "median_harmonic_ratio": drat, "misses": dmiss[:20]},
       "mix_acf_unpitched": acf_bad, "mix_acf_frames": frames,
       "silence_ratio": sil, "rms_per_sec": rms_map,
       "lufs": lufs, "peak": float(np.max(np.abs(mix_st))),
       "duration_s": len(mix_mo) / SR}
with open(OUT + "/Analysis/pitch_verification.json", "w") as f:
    json.dump(res, f, indent=2)
print("wrote Analysis/pitch_verification.json")
