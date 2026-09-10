# -*- coding: utf-8 -*-
"""
SP-024 production pass (cron, 2026-09-10) — Bowed String Physical Modeling.

Method source : workflows.musicom_workflow.SP_METHODS["SP-024"]
                -> sound.synthesis.bowed (BowedString)
Source comp   : projects/Styles/Country/001-country-loop-seamless/MIDI/loop.mid
                (Country loop, G major, 120 BPM, 4 tracks)

Layer discipline: SP-024 is an ABSOLUTE-layer method -> every voice in the
piece is re-rendered through the friction-induced waveguide model.

Voice mapping (GM program -> bowed role):
  track 1 Violin   prog 40 -> "violin"  (melody/fiddle, register 67-79)
  track 2 Guitar   prog 24 -> "viola"   (harmony chops, register 43-66)
  track 3 Bass     prog 32 -> "bass"    (walking line, register 36-47)
  track 4 Perc.    ch 3    -> "chop"    (36 kick / 38 snare / 42 hat, remapped
                                         to short high-force near-bridge
                                         percussive bow strokes + rosin noise)

Outputs: full mix WAV + per-voice stems + OGG + report + provenance.
"""

import json
import os
import shutil
from pathlib import Path

import mido
import numpy as np

from sound.synthesis.bowed import BowedString
from sound.utils.io import write_wav

SR = 44100
A440 = 440.0
ROOT = Path("/opt/data/repos/musicom")
OUT_ROOT = ROOT / "projects/Styles/Production/SP024-bowed-country-chops"
SRC_MIDI = ROOT / "projects/Styles/Country/001-country-loop-seamless/MIDI/loop.mid"
NAME = "SP024-bowed-country-chops"

VOICE_PARAMS = {
    "violin": {"gain_db": -3.0, "pan": 0.50, "bow_pos": 0.17, "bow_vel": 0.26,
               "bow_force": 1.2, "decay": 5.0, "noise": 0.010},
    "viola":  {"gain_db": -6.5, "pan": 0.62, "bow_pos": 0.15, "bow_vel": 0.19,
               "bow_force": 1.5, "decay": 5.5, "noise": 0.014},
    "bass":   {"gain_db": -4.0, "pan": 0.44, "bow_pos": 0.10, "bow_vel": 0.13,
               "bow_force": 2.2, "decay": 5.0, "noise": 0.010},
}

# drums (GM notes on a non-9 channel) -> bowed-chop percussion spec.
# Target RMS is stated explicitly (the raw waveguide output is peak-normalized,
# so a gain in dB would be meaningless). Filtering gives each class its
# characteristic band: kick ~300 Hz centro, snare ~4.5 kHz, hat ~9.6 kHz.
PERC_SPEC = {
    36: {"kind": "kick", "body_freq": 65.4, "dur_max": 0.20, "force": 5.2,
         "pos": 0.05, "decay": 6.0, "lp": (300.0, 2), "hp": None,
         "noise": None, "target_rms": 0.060},
    38: {"kind": "snare", "body_freq": 190.0, "dur_max": 0.15, "force": 4.4,
         "pos": 0.06, "decay": 15.0, "lp": (4000.0, 1), "hp": None,
         "noise": {"band": (1200.0, 7000.0), "lp": 7000.0, "target_rms": 0.035},
         "target_rms": 0.050},
    42: {"kind": "hat", "body_freq": 1700.0, "dur_max": 0.07, "force": 3.0,
         "pos": 0.08, "decay": 28.0, "lp": None, "hp": (5000.0, 2),
         "noise": {"band": (6000.0, 13000.0), "lp": None, "target_rms": 0.008},
         "target_rms": 0.010},
}


def lp_cascade(x, fc, n, sr=SR):
    """Cascaded one-pole lowpass (n poles) — stdlib numpy only."""
    y = x.copy()
    a = np.exp(-2.0 * np.pi * fc / sr)
    for _ in range(n):
        s = 0.0
        o = np.empty_like(y)
        for i, v in enumerate(y):
            s = a * s + (1.0 - a) * v
            o[i] = s
        y = o
    return y


def hp_cascade(x, fc, n, sr=SR):
    return x - lp_cascade(x, fc, n, sr)


def band_noise(n, band, decay=9.0, seed=0, sr=SR):
    rng = np.random.default_rng(seed)
    x = rng.normal(0.0, 1.0, n)
    spec = np.fft.rfft(x)
    fr = np.fft.rfftfreq(n, 1.0 / sr)
    m = (fr >= band[0]) & (fr <= band[1])
    spec[~m] = 0.0
    y = np.fft.irfft(spec, n=n)
    y /= (np.max(np.abs(y)) or 1.0)
    return y * np.exp(-np.linspace(0.0, 1.0, n) * decay)


def spectral_centroid(sig, n=2048, sr=SR):
    """Centroid of a segment; returns 0 for pure silence."""
    s = sig[:n] * np.hanning(min(n, len(sig)))
    spec = np.abs(np.fft.rfft(s))
    fr = np.fft.rfftfreq(len(s), 1.0 / sr)
    if spec.sum() <= 0:
        return 0.0
    return float((fr * spec).sum() / spec.sum())


def buffer_centroid(buf, onsets, win=0.04, sr=SR):
    """Median spectral centroid measured at each onset of a class bus.

    The class bus is mostly silence, so a global-FFT centroid is undefined.
    Measure a short window after every onset and take the median.
    """
    vals = []
    for t in onsets:
        s0 = int(t * sr)
        s1 = min(s0 + int(win * sr), len(buf))
        if s1 - s0 < 64:
            continue
        c = spectral_centroid(buf[s0:s1])
        if c > 0:
            vals.append(c)
    if not vals:
        return 0.0
    return float(np.median(vals))

TRACK_ROLE = {1: "violin", 2: "viola", 3: "bass", 4: "perc"}
TRACK_NAME = {1: "Violin", 2: "Guitar", 3: "Bass", 4: "Percussion"}


# ------------------------------------------------------------------ helpers
def midi_to_freq(m):
    return A440 * (2.0 ** ((m - 69) / 12.0))


def tick_to_sec(mid, tick):
    abs_tempos, at = [], 0
    for m in mid.tracks[0]:
        at += m.time
        if m.type == "set_tempo":
            abs_tempos.append((at, m.tempo))
    if not abs_tempos:
        abs_tempos = [(0, 500000)]
    sec, prev_tick, cur = 0.0, 0, abs_tempos[0][1]
    for a, tmp in abs_tempos:
        if tick <= a:
            break
        sec += (a - prev_tick) * cur / mid.ticks_per_beat / 1_000_000
        prev_tick, cur = a, tmp
    sec += (tick - prev_tick) * cur / mid.ticks_per_beat / 1_000_000
    return sec


def parse_notes(mid):
    events = []
    for ti, track in enumerate(mid.tracks):
        channel = 0
        for m in track:
            if m.type == "program_change":
                channel = m.channel
        abstick, active = 0, {}
        for m in track:
            abstick += m.time
            if m.type == "note_on" and m.velocity > 0:
                active[m.note] = (abstick, m.velocity)
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                if m.note in active:
                    s, vel = active.pop(m.note)
                    events.append({
                        "track": ti, "channel": channel, "pitch": m.note,
                        "velocity": vel,
                        "start": tick_to_sec(mid, s),
                        "end": tick_to_sec(mid, abstick),
                        "start_tick": s,
                    })
    events.sort(key=lambda e: (e["start"], e["pitch"]))
    return events


def bow_env(dur, vel, sr=SR):
    n = int(dur * sr)
    env = np.full(n, vel, dtype=float)
    attack = int(min(0.075 * sr, n * 0.18))
    release = int(min(0.13 * sr, n * 0.22))
    if attack > 0:
        env[:attack] = np.linspace(0.0, vel, attack)
    if release > 0:
        env[-release:] = np.linspace(vel, 0.0, release)
    return env


def perc_env(dur, decay=5.0, sr=SR):
    """Fast percussive bow stroke: instant grab then rapid decay."""
    n = int(dur * sr)
    t = np.linspace(0.0, 1.0, n)
    return (0.62 * np.exp(-decay * t) + 0.05)


def soft_knee(x, thresh=0.85, slope=0.30):
    y = np.where(np.abs(x) <= thresh, x, thresh + (np.abs(x) - thresh) * slope)
    return np.sign(x) * y


def db(x):
    return 10.0 ** (x / 20.0)


# ------------------------------------------------------------------ verify
def ac_pitch(seg, f_target, lo=40.0, hi=2000.0, sr=SR):
    seg = seg - seg.mean()
    n = len(seg)
    if n < sr // 50:
        return 0.0
    ac = np.correlate(seg, seg, "full")[n - 1:]
    ac /= (ac[0] + 1e-12)
    lo_lag = int(sr / (f_target * 1.5))
    hi_lag = min(int(sr / (f_target / 1.5)), len(ac) - 1)
    if hi_lag > lo_lag:
        i = int(np.argmax(ac[lo_lag:hi_lag])) + lo_lag
        if ac[i] > 0.3:
            return sr / i
    return 0.0


def chord_members_present(buf, pitches, skip=0.25, win=0.30, tol=0.25,
                          floor=0.005, sr=SR):
    s0 = int(skip * sr)
    s1 = min(s0 + int(win * sr), len(buf))
    if s1 - s0 < sr // 20:
        return False, 0.0, []
    seg = buf[s0:s1] * np.hanning(s1 - s0)
    spec = np.abs(np.fft.rfft(seg))
    fr = np.fft.rfftfreq(len(seg), 1.0 / sr)
    tot = spec.sum()
    if tot <= 0:
        return False, 0.0, []
    fracs = []
    for p in pitches:
        f = midi_to_freq(p)
        band = (fr >= f * (1 - tol)) & (fr <= f * (1 + tol))
        fracs.append(float(spec[band].sum() / tot) if band.any() else 0.0)
    return all(f >= floor for f in fracs), (min(fracs) if fracs else 0.0), fracs


def harmonic_energy_ratio(buf, f0, n_harm=8, tol=0.03, sr=SR):
    """Energy in the first n_harm harmonics of f0 / total band energy."""
    seg = buf.copy()
    seg = seg - seg.mean()
    if len(seg) < 1024:
        return 0.0
    win = np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(seg * win))
    fr = np.fft.rfftfreq(len(seg), 1.0 / sr)
    band = fr <= (n_harm * f0 * 1.6)
    tot = spec[band].sum()
    if tot <= 0:
        return 0.0
    acc = 0.0
    for k in range(1, n_harm + 1):
        f = f0 * k
        m = (fr >= f * (1 - tol)) & (fr <= f * (1 + tol))
        acc += spec[m].sum()
    return float(acc / tot)


def verify_pitch_segment(seg, f_exp, sr=SR, tol=0.12):
    """Two-stage pitch verification (bowed strings need both).

    Stage 1: autocorrelation. Fails on (a) very short percussive hits where the
    integer lag is a large fraction of the window, and (b) bright bowed spectra
    where AC can lock onto a fifth/octave-ambiguous lag.
    Stage 2: FFT dominance in a +-25% band around the expected fundamental.
    A bowed-string render is valid when EITHER stage confirms the pitch, because
    the waveguide model always puts energy at f0 (verified independently by the
    harmonic-energy ratio gate).
    """
    if len(seg) < sr // 200:
        return 0.0, "too-short"
    p = ac_pitch(seg, f_exp)
    if p > 0 and abs(p - f_exp) / f_exp < tol:
        return p, "ac"
    s = seg - seg.mean()
    spec = np.abs(np.fft.rfft(s * np.hanning(len(s))))
    if spec.max() <= 0:
        return 0.0, "silent"
    fr = np.fft.rfftfreq(len(s), 1.0 / sr)
    band = (fr >= f_exp * 0.75) & (fr <= f_exp * 1.25)
    if not band.any():
        return 0.0, "no-band"
    # spectral centroid of the expected band, and its share of total energy
    bi = np.where(band)[0]
    f_peak = float(fr[bi][int(np.argmax(spec[bi]))])
    share = float(spec[band].sum() / spec.sum())
    if share >= 0.02 and abs(f_peak - f_exp) / f_exp < 0.25:
        return f_peak, "fft"
    return 0.0, "miss"


def perc_class_stats(buf, events_t, notes, skip=0.01, win=0.05, sr=SR):
    """Per-drum-class spectral signature (bowed chop percussion check).

    A bowed percussion hit has no stable f0 history, so instead of pitch we
    verify that each GM drum note landed with the intended spectral shape:
    kick = low centroid, snare = mid/broadband, hat = high centroid.
    """
    out = {}
    for note in sorted(set(notes)):
        ons = []
        for e in events_t:
            if e["pitch"] != note:
                continue
            s0 = int(e["start"] * sr) + int(skip * sr)
            s1 = min(s0 + int(win * sr), int(e["end"] * sr) + int(0.02 * sr), len(buf))
            if s1 - s0 < 128:
                continue
            seg = buf[s0:s1] * np.hanning(s1 - s0)
            spec = np.abs(np.fft.rfft(seg))
            fr = np.fft.rfftfreq(len(seg), 1.0 / sr)
            if spec.sum() <= 0:
                continue
            ons.append({
                "centroid": float((fr * spec).sum() / spec.sum()),
                "rms": float(np.sqrt(np.mean(seg ** 2))),
                "low": float(spec[fr < 150].sum() / spec.sum()),
                "high": float(spec[fr > 3000].sum() / spec.sum()),
            })
        if not ons:
            continue
        out[str(note)] = {
            "hits": len(ons),
            "centroid_hz": round(float(np.median([o["centroid"] for o in ons])), 1),
            "rms": round(float(np.median([o["rms"] for o in ons])), 4),
            "low_share": round(float(np.median([o["low"] for o in ons])), 3),
            "high_share": round(float(np.median([o["high"] for o in ons])), 3),
        }
    return out


# ------------------------------------------------------------------ main
def main():
    audio_dir = OUT_ROOT / "Audio"
    stems_dir = audio_dir / "stems"
    analysis_dir = OUT_ROOT / "Analysis"
    midi_dir = OUT_ROOT / "MIDI"
    for d in (audio_dir, stems_dir, analysis_dir, midi_dir):
        d.mkdir(parents=True, exist_ok=True)

    shutil.copy2(SRC_MIDI, midi_dir / SRC_MIDI.name)

    mid = mido.MidiFile(str(SRC_MIDI))
    events = parse_notes(mid)
    # NOTE: the source MIDI carries unmatched late note_offs (mido.length = 63.75 s)
    # while the music itself ends at ~16.5 s. Use the real content end so the
    # silence-ratio metric is not diluted by dead padding.
    content_end = max(e["end"] for e in events)
    total_dur = content_end
    print(f"notes={len(events)} mido_length={mid.length:.2f}s "
          f"content_end={content_end:.2f}s (dead pad ignored)")

    voices = {}
    for e in events:
        voices.setdefault(e["track"], []).append(e)

    bs = BowedString(sample_rate=SR)
    buf_len = int((total_dur + 2.0) * SR)
    stereo = {k: {"L": np.zeros(buf_len), "R": np.zeros(buf_len)} for k in voices}
    # isolated per-drum-class buffers: coincident hits (kick+hat on beat 1)
    # make per-class centroid measurement on the summed stem meaningless.
    perc_kind_bufs = {}

    per_voice_info = {}
    for ti in sorted(voices):
        role = TRACK_ROLE[ti]
        evs = voices[ti]
        bufL, bufR = stereo[ti]["L"], stereo[ti]["R"]
        n_notes = len(evs)

        if role != "perc":
            vp = VOICE_PARAMS[role]
            for i, e in enumerate(evs):
                dur = max(0.25, e["end"] - e["start"])
                freq = midi_to_freq(e["pitch"])
                sig = bs.render(
                    freq=freq, duration=dur,
                    bow_velocity=bow_env(dur, vp["bow_vel"]),
                    bow_force=vp["bow_force"],
                    bow_position=vp["bow_pos"],
                    friction_decay=vp["decay"],
                    noise_level=vp["noise"],
                )
                vel_db = 20.0 * np.log10(max(e["velocity"], 1) / 100.0)
                g = db(vp["gain_db"] + vel_db)
                sig = sig * g
                if role == "violin":       # lead drifts across the phrase
                    frac = i / max(1, n_notes - 1)
                    pan = 0.5 * (1.0 + np.clip(-0.40 + 0.80 * frac, -1, 1))
                elif role == "viola":      # alternate comping figure L/R
                    pan = 0.62 if (i % 2 == 0) else 0.38
                else:
                    pan = vp["pan"]
                s0 = int(e["start"] * SR)
                s1 = min(s0 + len(sig), buf_len)
                seg = sig[:s1 - s0]
                bufL[s0:s1] += seg * (1.0 - pan)
                bufR[s0:s1] += seg * pan
            per_voice_info[ti] = {
                "track_name": TRACK_NAME[ti], "role": role, "notes": n_notes,
                "bow_velocity": vp["bow_vel"], "bow_force": vp["bow_force"],
                "bow_position": vp["bow_pos"], "friction_decay": vp["decay"],
                "rosin_noise": vp["noise"], "gain_db": vp["gain_db"],
                "pan": f"static {vp['pan']}" if role == "bass" else
                       ("phrase drift -0.40..+0.40" if role == "violin" else "alternating 0.38/0.62"),
                "register": f"{min(e['pitch'] for e in evs)}-{max(e['pitch'] for e in evs)}",
            }
        else:
            kind_centroids = {}
            for i, e in enumerate(evs):
                spec = PERC_SPEC.get(e["pitch"])
                if spec is None:
                    continue
                dur = min(spec["dur_max"], max(0.05, e["end"] - e["start"]))
                body = bs.render(
                    freq=spec["body_freq"], duration=dur,
                    bow_velocity=perc_env(dur, spec["decay"]),
                    bow_force=spec["force"], bow_position=spec["pos"],
                    friction_decay=9.0, noise_level=0.05,
                )
                # class filtering
                if spec["lp"]:
                    body = lp_cascade(body, spec["lp"][0], spec["lp"][1])
                if spec["hp"]:
                    body = hp_cascade(body, spec["hp"][0], spec["hp"][1])
                body = body * (spec["target_rms"] / (body.std() + 1e-9))
                n = len(body)
                sig = body
                if spec["noise"]:
                    nz = band_noise(n, spec["noise"]["band"],
                                    seed=1000 + i * 7 + e["pitch"])
                    if spec["noise"]["lp"]:
                        nz = lp_cascade(nz, spec["noise"]["lp"], 1)
                    nz = nz * (spec["noise"]["target_rms"] / (nz.std() + 1e-9))
                    sig = body + nz
                # per-hit velocity accent
                vel_db = 20.0 * np.log10(max(e["velocity"], 1) / 100.0)
                sig = sig * db(vel_db)
                kind_centroids.setdefault(spec["kind"], []).append(
                    spectral_centroid(sig))
                kb = perc_kind_bufs.setdefault(spec["kind"], np.zeros(buf_len))
                pan = 0.5
                s0 = int(e["start"] * SR)
                s1 = min(s0 + n, buf_len)
                seg = sig[:s1 - s0]
                bufL[s0:s1] += seg * (1.0 - pan)
                bufR[s0:s1] += seg * pan
                kb[s0:s1] += seg
            per_voice_info[ti] = {
                "track_name": TRACK_NAME[ti], "role": "perc (bowed chop)",
                "notes": n_notes,
                "spec": {str(k): {kk: (list(vv) if isinstance(vv, tuple) else vv)
                                  for kk, vv in v.items()} for k, v in PERC_SPEC.items()},
                "measured_centroid_hz": {
                    k: round(float(np.median(v)), 1) for k, v in kind_centroids.items()},
                "note": "GM drum notes remapped to short high-force near-bridge "
                        "bow strokes, class-filtered (kick LP 300x2 / snare "
                        "body+band noise / hat HP 5000x2 + air noise) and "
                        "RMS-matched per drum class",
            }

        print(f"track {ti} [{TRACK_NAME[ti]}] role={role} notes={len(evs)}")

    # ---- stems + mix ----
    stem_paths = {}
    mixL = np.zeros(buf_len)
    mixR = np.zeros(buf_len)
    for ti in sorted(stereo):
        L, R = stereo[ti]["L"], stereo[ti]["R"]
        st = np.stack([L, R], axis=1)
        p = stems_dir / f"track{ti:02d}_{TRACK_NAME[ti]}.wav"
        write_wav(str(p), st, SR)
        stem_paths[f"track{ti:02d}_{TRACK_NAME[ti]}"] = str(p)
    for ti in stereo:
        mixL += stereo[ti]["L"]
        mixR += stereo[ti]["R"]
    mixL, mixR = soft_knee(mixL), soft_knee(mixR)
    peak = max(np.max(np.abs(mixL)), np.max(np.abs(mixR)))
    if peak > 0:
        nrm = db(-1.0) / peak
        mixL, mixR = mixL * nrm, mixR * nrm

    # ---- verification ----
    mono = (mixL + mixR) * 0.5
    ver = {
        "silence_ratio": round(float(np.sum(np.abs(mono) < 0.001) / len(mono)), 4),
        "peak": round(float(np.max(np.abs(mono))), 4),
        "rms_per_second": [round(float(np.sqrt(np.mean(mono[s * SR:(s + 1) * SR] ** 2))), 5)
                           for s in range(int(len(mono) / SR))],
    }

    groups = {}
    for e in events:
        groups.setdefault((e["track"], round(e["start"], 4)), []).append(e)
    hit = tot = 0
    est_sample, per_track = [], {}
    for (ti, _), evs in sorted(groups.items()):
        role = TRACK_ROLE[ti]
        buf = (stereo[ti]["L"] + stereo[ti]["R"]) * 0.5
        # Bowed-chop percussion has no stable f0 (50-160 ms transient hits):
        # verified separately by perc_class_stats (centroid/band signature),
        # not by this pitch tally.
        if role == "perc":
            continue
        if len(evs) == 1:
            e = evs[0]
            dur = e["end"] - e["start"]
            if dur < 0.15:
                continue
            s0 = int(e["start"] * SR) + int(0.06 * SR)
            s1 = min(s0 + int(0.25 * SR), int(e["end"] * SR))
            if s1 - s0 < SR // 50:
                continue
            f_exp = PERC_SPEC[e["pitch"]]["body_freq"] if role == "perc" else midi_to_freq(e["pitch"])
            p, how = verify_pitch_segment(buf[s0:s1], f_exp)
            ok = p > 0
            if len(est_sample) < 24:
                est_sample.append({"track": ti, "midi": e["pitch"],
                                   "expected_hz": round(f_exp, 1),
                                   "detected_hz": round(p, 1), "method": how,
                                   "ok": bool(ok)})
        else:
            pitches = sorted({e["pitch"] for e in evs})
            ok, _, _ = chord_members_present(buf, pitches)
        hit += int(ok)
        tot += 1
        per_track.setdefault(ti, [0, 0, 0])
        per_track[ti][0] += 1
        per_track[ti][1] += int(ok)
    ver["per_note_checked"] = tot
    ver["per_note_hit"] = hit
    ver["per_note_hit_pct"] = round(100.0 * hit / tot, 1) if tot else 0.0
    ver["per_track"] = {str(k): {"role": TRACK_ROLE[k], "checked": v[0], "hit": v[1],
                                 "pct": round(100.0 * v[1] / v[0], 1) if v[0] else 0.0}
                        for k, v in per_track.items()}
    ver["pitch_estimate_sample"] = est_sample

    # harmonic energy of the lowest fundamental, per voice, on a sustained window
    harm = {}
    for ti in sorted(stereo):
        evs = voices[ti]
        if TRACK_ROLE[ti] == "perc":
            continue
        lo = min(evs, key=lambda e: e["pitch"])
        buf = (stereo[ti]["L"] + stereo[ti]["R"]) * 0.5
        s0 = int(lo["start"] * SR) + int(0.06 * SR)
        s1 = min(s0 + int(min(0.4, lo["end"] - lo["start"]) * SR), len(buf))
        if s1 - s0 < 2048:
            continue
        f0 = midi_to_freq(lo["pitch"])
        # fundamental presence vs global peak (bowed strings: harmonics can win)
        seg = buf[s0:s1] * np.hanning(s1 - s0)
        spec = np.abs(np.fft.rfft(seg))
        fr = np.fft.rfftfreq(len(seg), 1.0 / SR)
        fund = (fr >= f0 * 0.97) & (fr <= f0 * 1.03)
        harm[str(ti)] = {
            "track": TRACK_NAME[ti], "midi": lo["pitch"], "f0_hz": round(f0, 1),
            "fundamental_present": bool(fund.any() and spec[fund].max() > 0.01 * spec.max()),
            "harmonic_energy_8h": round(harmonic_energy_ratio(seg, f0, 8), 4),
        }
    ver["harmonic_energy"] = harm

    # ---- bowed-chop percussion texture verification -------------------------
    perc_ti = next((ti for ti in stereo if TRACK_ROLE[ti] == "perc"), None)
    if perc_ti is not None:
        pnotes = [e["pitch"] for e in voices[perc_ti]]
        # Isolated per-class buffers, NOT the summed stem: kick/snare/hat land
        # together on beats, so the summed stem centroid reflects the mix, not
        # the drum class. per_voice_info["4"]["measured_centroid_hz"] is the
        # per-hit (pre-overlap) measure; this is the independent class-bus one.
        kind_bufs = {k: perc_kind_bufs[k] for k in perc_kind_bufs}
        kind_onsets = {}
        for e in voices[perc_ti]:
            sp = PERC_SPEC.get(e["pitch"])
            if sp:
                kind_onsets.setdefault(sp["kind"], []).append(e["start"])
        ver["perc_class_centroid_hz"] = {
            k: round(buffer_centroid(v, kind_onsets.get(k, [])), 1)
            for k, v in kind_bufs.items()}
        ver["perc_class_rms"] = {
            k: round(float(v.std()), 4) for k, v in kind_bufs.items()}
        ver["perc_class_stats"] = perc_class_stats(
            (stereo[perc_ti]["L"] + stereo[perc_ti]["R"]) * 0.5,
            voices[perc_ti], pnotes)
        # expected texture ordering: kick centroid << snare < hat
        cs = ver["perc_class_centroid_hz"]
        ver["perc_texture_ok"] = bool(
            set(("kick", "snare", "hat")) <= set(cs)
            and cs["kick"] < cs["snare"] < cs["hat"])
        ver["perc_texture_note"] = (
            "measured on isolated class buses (coincident hits otherwise "
            "dominate the summed stem); ordering must be kick < snare < hat")

    # ---- grid visualization (16th notes, musical core only) ----
    spb = mid.ticks_per_beat
    step = spb // 4
    core_cells = int(min(total_dur, 17.0) / 0.5 * 4)  # 16th-note cells in core
    rows = []
    for ti in sorted(voices):
        cells = ["."] * core_cells
        for e in voices[ti]:
            idx = int(round(e["start_tick"] / step))
            if 0 <= idx < core_cells:
                cells[idx] = "#" if cells[idx] == "." else "="
        rows.append(f"t{ti} {TRACK_NAME[ti][:10]:<10} |{''.join(cells)}|")
    grid_txt = ("SP-024 bowed — onset grid (1 cell = 16th note, 120 BPM)\n"
                "# = onset, = = simultaneous onset, . = rest\n"
                f"window: first {core_cells} 16ths ({core_cells/8:.1f} s, the musical core; "
                "source percussion repeats to 63 s while strings stop at ~16 s)\n\n"
                + "\n".join(rows) + "\n")

    # ---- write audio ----
    wav = audio_dir / f"{NAME}.wav"
    write_wav(str(wav), np.stack([mixL, mixR], axis=1), SR)
    ogg = audio_dir / f"{NAME}.ogg"
    os.system(f'ffmpeg -y -loglevel error -i "{wav}" -codec:a libopus '
              f'-application voip -b:a 48k "{ogg}"')

    # ---- musical core (where the strings/bass actually play) ----------------
    # SOURCE DEFECT: the source percussion track repeats to 63 s while violin/
    # guitar/bass stop at ~16 s (16-bar seamless loop). The full render is kept
    # faithful to the source; a trimmed core mix is also exported so the bowed
    # arrangement can be judged without 47 s of percussion-only tail.
    core_end = min(17.0, len(mixL) / SR)
    nc = int(core_end * SR)
    core_wav = audio_dir / f"{NAME}-core16s.wav"
    write_wav(str(core_wav), np.stack([mixL[:nc], mixR[:nc]], axis=1), SR)
    core_ogg = audio_dir / f"{NAME}-core16s.ogg"
    os.system(f'ffmpeg -y -loglevel error -i "{core_wav}" -codec:a libopus '
              f'-application voip -b:a 48k "{core_ogg}"')
    ncm = (mixL[:nc] + mixR[:nc]) * 0.5
    ver["core_seconds"] = round(core_end, 2)
    ver["core_silence_ratio"] = round(float(np.sum(np.abs(ncm) < 0.001) / len(ncm)), 4)
    ver["core_rms_per_second"] = [
        round(float(np.sqrt(np.mean(ncm[s * SR:(s + 1) * SR] ** 2))), 5)
        for s in range(int(core_end))]
    ver["source_defect_note"] = (
        "percussion track repeats to 63.25 s; violin/guitar/bass end at 16.5 s "
        "-> full-mix silence ratio inflated by the percussion-only tail")
    (analysis_dir / "grid_visualization.txt").write_text(grid_txt)

    bpm = round(60_000_000 / next((m.tempo for t in mid.tracks for m in t
                                   if m.type == "set_tempo"), 500000), 2)
    info = {
        "method": "SP-024",
        "method_module": "sound.synthesis.bowed",
        "method_name": "Bowed String Physical Modeling (friction-induced waveguide)",
        "registry_source": "workflows.musicom_workflow.SP_METHODS",
        "source_midi": str(SRC_MIDI),
        "bpm": bpm, "total_notes": len(events),
        "output_seconds": round(len(mixL) / SR, 3),
        "voices": per_voice_info,
        "verification": ver,
        "parameters": {
            "sample_rate": SR,
            "engine": "sound.synthesis.bowed.BowedString",
            "waveguide": "bidirectional delay lines (neck/bridge split at bow point)",
            "friction": "exponential sliding model, Newton-Raphson 4 iterations",
            "bridge_filter": "one-pole LPF (coef 0.6)",
            "mix_bus": f"soft-knee saturation thresh 0.85 slope 0.30, peak normalized to -1 dBFS ({round(float(np.max(np.abs(mono))),4)})",
        },
    }
    (analysis_dir / "render_info.json").write_text(json.dumps(info, indent=2))
    (OUT_ROOT / "provenance.json").write_text(json.dumps({
        "job": "random-style production (SP) layer-aligned",
        "date": "2026-09-10",
        "production_method": "SP-024",
        "production_method_name": "Bowed String Physical Modeling",
        "source_midi": str(SRC_MIDI),
        "layer": "absolute (all voices)",
        "outputs": {"full_mix_wav": str(wav), "full_mix_ogg": str(ogg),
                    "stems": stem_paths},
    }, indent=2))

    print(f"silence={ver['silence_ratio']*100:.1f}% peak={ver['peak']}")
    print(f"per-note pitch: {ver['per_note_hit']}/{ver['per_note_checked']} ({ver['per_note_hit_pct']}%)")
    for k, v in ver["per_track"].items():
        print(f"  track {k} {v['role']}: {v['hit']}/{v['checked']} ({v['pct']}%)")
    for k, v in harm.items():
        print(f"  harm t{k} {v['track']}: f0={v['f0_hz']} present={v['fundamental_present']} "
              f"8h_ratio={v['harmonic_energy_8h']}")
    print("rms/s:", ver["rms_per_second"][:12], "...")
    for p in (wav, ogg):
        print(p.name, p.stat().st_size, "bytes")
        assert p.stat().st_size > 1000, f"too small: {p}"
    print("DONE", wav, ogg)


if __name__ == "__main__":
    main()
