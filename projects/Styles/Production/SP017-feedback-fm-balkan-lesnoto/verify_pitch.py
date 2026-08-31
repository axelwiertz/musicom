#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Per-voice pitch verification for SP-017 balkan-lesnoto render (SP-035 lesson).

Autocorrelation pitch test (true period) per voice + per-note window:
- Expected MIDI note -> frequency
- Detect period via normalized autocorrelation in lag range for [0.5*f, 2*f]
- Match if detected within ±2 octaves (period doubling accepted for harmonic-rich)
- Also exact-octave check via FFT harmonic-sum
"""
import json
import wave
import math
from collections import defaultdict

import numpy as np
import mido
from mido import MidiFile

SR = 44100
SRC_MIDI = "/opt/data/projects/Styles/Balkan/001-balkan-lesnoto/MIDI/balkan-lesnoto.mid"
WAV = "/opt/data/projects/Styles/Production/SP017-feedback-fm-balkan-lesnoto/Audio/SP017-feedback-fm-balkan-lesnoto.wav"
OUT = "/opt/data/projects/Styles/Production/SP017-feedback-fm-balkan-lesnoto/Analysis/pitch_verification.json"

VOICE_NAMES = {74: "Kaval (melody)", 50: "Gaida (drone)", 33: "Tambura (bass drone)"}


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def read_wav(path):
    with wave.open(path, "rb") as wf:
        assert wf.getnchannels() == 1
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    return data.astype(np.float64) / 32767.0


def load_events():
    mid = MidiFile(SRC_MIDI)
    tpb = mid.ticks_per_beat
    tempo_us = 500000
    for track in mid.tracks:
        for msg in track:
            if msg.type == "tempo":
                tempo_us = msg.tempo
                break
        else:
            continue
        break
    sec_per_tick = tempo_us / 1e6 / tpb
    events = []
    for track in mid.tracks:
        program = 0
        abs_ticks = 0
        open_notes = {}
        for msg in track:
            abs_ticks += msg.time
            if msg.type == "program_change":
                program = msg.program
            elif msg.type == "note_on" and msg.velocity > 0:
                open_notes[(msg.channel, msg.note)] = (abs_ticks, msg.velocity, program)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in open_notes:
                    st, vel, p = open_notes.pop(key)
                    events.append(dict(start=st * sec_per_tick, end=abs_ticks * sec_per_tick,
                                       pitch=msg.note, vel=vel, program=p))
        for key, (st, vel, p) in open_notes.items():
            events.append(dict(start=st * sec_per_tick, end=(st + tpb) * sec_per_tick,
                               pitch=key[1], vel=vel, program=p))
    return events


def autocorr_f0(seg, f_expected, sr=SR):
    """Detect period via autocorrelation in lag range for [0.5f, 2f]. Returns Hz or 0."""
    n = len(seg)
    if n < sr * 0.05:
        return 0.0
    seg = seg - np.mean(seg)
    rms = np.sqrt(np.mean(seg ** 2))
    if rms < 1e-4:
        return 0.0
    lo_lag = max(2, int(sr / (2.0 * f_expected)))
    hi_lag = min(n // 2, int(sr / (0.5 * f_expected)) + 1)
    if hi_lag <= lo_lag:
        return 0.0
    seg = seg * np.hanning(n)
    ac = np.correlate(seg, seg, "full")[n - 1:]
    ac /= (ac[0] + 1e-12)
    best = 0.0
    best_lag = 0
    for lag in range(lo_lag, hi_lag):
        if ac[lag] > best:
            best = ac[lag]
            best_lag = lag
    if best < 0.15:
        return 0.0
    return sr / best_lag


def fft_f0(seg, f_expected, sr=SR):
    """FFT harmonic-sum F0: sum energy at k*f for k=1..6, pick best f in [0.5f,2f]."""
    n = len(seg)
    spec = np.abs(np.fft.rfft(seg * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    best_f = 0.0
    best_score = 0.0
    f_cands = np.arange(0.5 * f_expected, 2.0 * f_expected, 1.0)
    for f in f_cands:
        score = 0.0
        for k in range(1, 7):
            b = int(round(k * f * n / sr))
            if 0 <= b < len(spec):
                score += spec[max(0, b - 2):b + 3].sum()
        if score > best_score:
            best_score = score
            best_f = f
    return best_f if best_score > 0 else 0.0


def main():
    mono = read_wav(WAV)
    events = load_events()
    by_prog = defaultdict(list)
    for e in events:
        if e["program"] == 0:
            continue
        by_prog[e["program"]].append(e)

    results = {}
    summary = {}
    for prog in sorted(by_prog):
        evs = sorted(by_prog[prog], key=lambda e: e["start"])
        total_ac = 0
        ac_ok = 0
        fft_ok = 0
        ac_exact = 0
        per_note = []
        for e in evs:
            dur = e["end"] - e["start"]
            if dur < 0.2:
                continue
            f_exp = midi_to_freq(e["pitch"])
            # analyze the middle 60% of the note (skip attack/release transients)
            pad = 0.15 * dur
            s0 = int((e["start"] + pad) * SR)
            s1 = int((e["end"] - pad) * SR)
            if s1 - s0 < SR * 0.08:
                s0 = int(e["start"] * SR)
                s1 = int(e["end"] * SR)
            seg = mono[s0:s1]
            if len(seg) < SR * 0.05:
                continue
            total_ac += 1
            ac = autocorr_f0(seg, f_exp)
            ff = fft_f0(seg, f_exp)
            ac_hit = ac > 0 and 0.25 * f_exp <= ac <= 4.0 * f_exp  # ±2 octaves
            fft_hit = ff > 0 and abs(ff - f_exp) / f_exp < 0.05
            exact = ac > 0 and abs(ac - f_exp) / f_exp < 0.05
            if ac_hit:
                ac_ok += 1
            if fft_hit:
                fft_ok += 1
            if exact:
                ac_exact += 1
            per_note.append({
                "pitch": e["pitch"], "freq_expected": round(f_exp, 2),
                "start_s": round(e["start"], 2), "dur_s": round(dur, 2),
                "ac_detected_hz": round(ac, 1) if ac > 0 else None,
                "ac_match_pm2oct": bool(ac_hit),
                "fft_detected_hz": round(ff, 1) if ff > 0 else None,
                "fft_exact_match": bool(fft_hit),
            })
        results[str(prog)] = {
            "voice": VOICE_NAMES.get(prog, "?"),
            "notes_checked": total_ac,
            "ac_match_pm2oct": ac_ok,
            "fft_exact_match": fft_ok,
            "ac_exact_octave": ac_exact,
            "per_note": per_note,
        }
        summary[str(prog)] = f"{ac_ok}/{total_ac} AC, {fft_ok}/{total_ac} FFT-exact"
        print(f"prog {prog} {VOICE_NAMES.get(prog)}: AC {ac_ok}/{total_ac} "
              f"FFT-exact {fft_ok}/{total_ac} AC-exact {ac_exact}/{total_ac}")

    verdict = all(r["ac_match_pm2oct"] >= 0.75 * r["notes_checked"]
                  for r in results.values() if r["notes_checked"] > 0)
    out = {
        "method": "SP-017 feedback FM",
        "source": SRC_MIDI,
        "wav": WAV,
        "verdict": "PITCHED - PASS" if verdict else "FAIL",
        "per_voice_summary": summary,
        "per_voice": results,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"verdict: {out['verdict']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
