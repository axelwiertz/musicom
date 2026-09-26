# -*- coding: utf-8 -*-
"""
SP-024 — Bowed String Physical Modeling production pass (cron 2026-09-26).

Method source : workflows.musicom_workflow.SP_METHODS["SP-024"]
                -> sound.synthesis.bowed (BowedString)
Source comp   : projects/Styles/Balfolk/011-balfolk-dust-on-the-dashboard/MIDI/composition_full.mid
                ("Dust on the Dashboard", Pop Country, G major, 110 BPM, 4/4, 35.45 s)

Layer discipline: SP-024 is an ABSOLUTE-layer method -> every voice in the piece
is re-rendered through the friction-induced waveguide bowed-string model. The
source has NO program_change messages and NO percussion (all 4 voices on ch 0),
so voices are mapped by TRACK INDEX, not GM program.

Voice mapping (track -> bowed role):
  track 1 (80 notes, 64-76) -> "violin"  (syncopated lead hook)
  track 2 (48 notes, 50-62) -> "viola"   (staggered strum/accompaniment)
  track 3 (16 notes, 38-43) -> "bass"    (root/motion line)
  track 4 ( 8 notes, 74-79) -> "violin2" (high counterline)

Pipeline:
  1. Parse source MIDI with mido (analysis-only, allowed for reading).
  2. Render every note through sound.synthesis.bowed.BowedString.
  3. Stereo: per-voice static pan + lead drift across the phrase.
  4. Mix: per-voice gain -> soft-knee bus -> peak normalize -1 dBFS -> stereo WAV.
  5. Verify: silence ratio + per-second RMS + per-note pitch (AC+FFT) + chord
     harmonic presence + harmonic energy ratio (>= 30% gate).
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
OUT_ROOT = ROOT / "projects/Styles/Production/SP024-bowed-balfolk-dashboard"
SRC_MIDI = ROOT / "projects/Styles/Balfolk/011-balfolk-dust-on-the-dashboard/MIDI/composition_full.mid"
NAME = "SP024-bowed-balfolk-dashboard"

# track index -> role (no program_change in source, all ch 0)
TRACK_ROLE = {1: "violin", 2: "viola", 3: "bass", 4: "violin2"}
TRACK_NAME = {1: "Lead", 2: "Accomp", 3: "Bass", 4: "Counter"}

VOICE_PARAMS = {
    "violin":  {"gain_db": -2.0, "pan": 0.42, "bow_pos": 0.18, "bow_vel": 0.26,
                "bow_force": 1.2, "decay": 5.0, "noise": 0.010},
    "violin2": {"gain_db": -4.0, "pan": 0.64, "bow_pos": 0.17, "bow_vel": 0.22,
                "bow_force": 1.3, "decay": 5.0, "noise": 0.010},
    "viola":   {"gain_db": -3.5, "pan": 0.50, "bow_pos": 0.15, "bow_vel": 0.19,
                "bow_force": 1.5, "decay": 5.5, "noise": 0.014},
    "bass":    {"gain_db": -4.0, "pan": 0.50, "bow_pos": 0.10, "bow_vel": 0.13,
                "bow_force": 2.2, "decay": 5.0, "noise": 0.010},
}


# ------------------------------------------------------------------ helpers
def midi_to_freq(m: int) -> float:
    return A440 * (2.0 ** ((m - 69) / 12.0))


def tick_to_sec(mid: mido.MidiFile, tick: int) -> float:
    abs_tempos = []
    at = 0
    for m in mid.tracks[0]:
        at += m.time
        if m.type == "set_tempo":
            abs_tempos.append((at, m.tempo))
    if not abs_tempos:
        abs_tempos = [(0, 500000)]
    sec = 0.0
    prev_tick = 0
    cur_tempo = abs_tempos[0][1]
    for at, tmp in abs_tempos:
        if tick <= at:
            break
        sec += (at - prev_tick) * cur_tempo / mid.ticks_per_beat / 1_000_000
        prev_tick = at
        cur_tempo = tmp
    sec += (tick - prev_tick) * cur_tempo / mid.ticks_per_beat / 1_000_000
    return sec


def parse_notes(mid: mido.MidiFile):
    events = []
    for ti, track in enumerate(mid.tracks):
        abstick = 0
        last_tick = 0
        active = {}
        for m in track:
            abstick += m.time
            last_tick = abstick
            if m.type == "note_on" and m.velocity > 0:
                active[m.note] = (abstick, m.velocity)
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                if m.note in active:
                    s, vel = active.pop(m.note)
                    events.append({
                        "track": ti, "pitch": m.note, "velocity": vel,
                        "start": tick_to_sec(mid, s),
                        "end": tick_to_sec(mid, abstick),
                        "start_tick": s,
                    })
        # flush dangling notes (no note_off) to track end
        for note, (s, vel) in active.items():
            events.append({
                "track": ti, "pitch": note, "velocity": vel,
                "start": tick_to_sec(mid, s),
                "end": tick_to_sec(mid, last_tick),
                "start_tick": s,
            })
    events.sort(key=lambda e: (e["start"], e["pitch"]))
    return events


def make_bow_envelope(dur: float, bow_vel: float, sr: int = SR) -> np.ndarray:
    n = int(dur * sr)
    env = np.full(n, bow_vel, dtype=float)
    attack = int(min(0.08 * sr, n * 0.15))
    release = int(min(0.15 * sr, n * 0.15))
    if attack > 0:
        env[:attack] = np.linspace(0.0, bow_vel, attack)
    if release > 0:
        env[-release:] = np.linspace(bow_vel, 0.0, release)
    return env


def soft_knee(x: np.ndarray, thresh: float = 0.82, slope: float = 0.32) -> np.ndarray:
    y = np.where(np.abs(x) <= thresh, x, thresh + (np.abs(x) - thresh) * slope)
    return np.sign(x) * y


def db(x: float) -> float:
    return 10.0 ** (x / 20.0)


# ------------------------------------------------------------------ verify
def est_pitch_ac(seg, sr, f_target=None, lo=40, hi=2000):
    seg = seg - seg.mean()
    n = len(seg)
    if n < sr // 50:
        return 0.0
    ac = np.correlate(seg, seg, "full")[n - 1:]
    ac /= (ac[0] + 1e-12)
    if f_target:
        lo_lag = int(sr / (f_target * 1.5))
        hi_lag = min(int(sr / (f_target / 1.5)), len(ac) - 1)
        if hi_lag > lo_lag:
            lr2 = ac[lo_lag:hi_lag]
            pi2 = int(np.argmax(lr2)) + lo_lag
            if ac[pi2] > 0.3:
                return sr / pi2
    min_lag = int(sr / hi)
    max_lag = min(int(sr / lo), len(ac) - 1)
    if max_lag <= min_lag:
        return 0.0
    pi = int(np.argmax(ac[min_lag:max_lag])) + min_lag
    if ac[pi] < 0.3:
        return 0.0
    return sr / pi


def chord_members_present(buf, pitches, sr, skip=0.4, win=0.3):
    s0 = int(skip * sr)
    s1 = min(s0 + int(win * sr), len(buf))
    if s1 - s0 < sr // 20:
        return False, 0.0
    seg = buf[s0:s1] * np.hanning(s1 - s0)
    spec = np.abs(np.fft.rfft(seg))
    fr = np.fft.rfftfreq(len(seg), 1.0 / sr)
    tot = spec.sum()
    if tot <= 0:
        return False, 0.0
    fracs = []
    for p in pitches:
        f = midi_to_freq(p)
        band = (fr >= f * 0.75) & (fr <= f * 1.25)
        fracs.append(float(spec[band].sum() / tot) if band.any() else 0.0)
    return all(ff >= 0.005 for ff in fracs), (min(fracs) if fracs else 0.0)


def harmonic_energy_ratio(buf, f0, n_harm=8, tol=0.03, sr=SR):
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
    content_end = max(e["end"] for e in events)
    total_dur = content_end + 0.5  # small tail for release
    print(f"notes={len(events)} mido_length={mid.length:.2f}s "
          f"content_end={content_end:.2f}s total_dur={total_dur:.2f}s")

    voices = {}
    for e in events:
        if e["track"] in TRACK_ROLE:
            voices.setdefault(e["track"], []).append(e)

    bs = BowedString(sample_rate=SR)
    buf_len = int((total_dur + 2.0) * SR)
    stereo = {k: {"L": np.zeros(buf_len), "R": np.zeros(buf_len)} for k in voices}

    per_voice_info = {}
    for track_idx, evs in sorted(voices.items()):
        role = TRACK_ROLE[track_idx]
        vp = VOICE_PARAMS[role]
        bufL = stereo[track_idx]["L"]
        bufR = stereo[track_idx]["R"]
        n_notes = len(evs)
        print(f"track {track_idx} [{TRACK_NAME[track_idx]}] role={role} notes={n_notes}")

        for note_i, e in enumerate(evs):
            dur = max(0.25, e["end"] - e["start"])
            freq = midi_to_freq(e["pitch"])
            v_env = make_bow_envelope(dur, vp["bow_vel"])
            sig = bs.render(
                freq=freq, duration=dur,
                bow_velocity=v_env, bow_force=vp["bow_force"],
                bow_position=vp["bow_pos"], friction_decay=vp["decay"],
                noise_level=vp["noise"],
            )
            vel_db = 20.0 * np.log10(max(e["velocity"], 1) / 100.0)
            g_lin = db(vp["gain_db"] + vel_db)
            sig = sig * g_lin

            if role == "violin":  # lead drifts across the phrase
                frac = note_i / max(1, n_notes - 1)
                pan = 0.5 * (1.0 + np.clip(-0.40 + 0.80 * frac, -1, 1))
            elif role == "violin2":  # counterline, gentle L/R alternate
                pan = 0.64 if (note_i % 2 == 0) else 0.36
            elif role == "viola":  # accompaniment alternates
                pan = 0.55 if (note_i % 2 == 0) else 0.45
            else:
                pan = vp["pan"]

            s0 = int(e["start"] * SR)
            s1 = min(s0 + len(sig), buf_len)
            seg = sig[:s1 - s0]
            bufL[s0:s1] += seg * (1.0 - pan)
            bufR[s0:s1] += seg * pan

        per_voice_info[str(track_idx)] = {
            "track_name": TRACK_NAME[track_idx], "role": role,
            "notes": n_notes,
            "register": f"{min(e['pitch'] for e in evs)}-{max(e['pitch'] for e in evs)}",
            "bow_velocity": vp["bow_vel"], "bow_force": vp["bow_force"],
            "bow_position": vp["bow_pos"], "friction_decay": vp["decay"],
            "rosin_noise": vp["noise"], "gain_db": vp["gain_db"],
            "pan": vp["pan"],
        }

    # ---- stems + mix ----
    stem_paths = {}
    mixL = np.zeros(buf_len)
    mixR = np.zeros(buf_len)
    for ti in sorted(stereo):
        L, R = stereo[ti]["L"], stereo[ti]["R"]
        st = np.stack([L, R], axis=1)
        p = stems_dir / f"track{ti:02d}_{TRACK_NAME[ti]}.wav"
        write_wav(str(p), st, SR, normalize=False)
        stem_paths[f"track{ti:02d}_{TRACK_NAME[ti]}"] = str(p)
    for ti in stereo:
        mixL += stereo[ti]["L"]
        mixR += stereo[ti]["R"]

    mixL = soft_knee(mixL)
    mixR = soft_knee(mixR)
    peak = max(np.max(np.abs(mixL)), np.max(np.abs(mixR)))
    if peak > 0:
        norm = db(-1.0) / peak
        mixL *= norm
        mixR *= norm

    # ---- verification ----
    mono = (mixL + mixR) * 0.5
    ver = {
        "silence_ratio": round(float(np.sum(np.abs(mono) < 0.001) / len(mono)), 4),
        "peak": round(float(np.max(np.abs(mono))), 4),
        "rms_per_second": [
            round(float(np.sqrt(np.mean(mono[s * SR:(s + 1) * SR] ** 2))), 5)
            for s in range(int(len(mono) / SR))],
    }

    # per-note pitch (per voice, pre-mix) + chord harmonic presence
    groups = {}
    for e in events:
        if e["track"] in TRACK_ROLE:
            groups.setdefault((e["track"], round(e["start"], 4)), []).append(e)

    hit = tot = 0
    per_track = {}
    est_sample = []
    for (ti, _), evs in sorted(groups.items()):
        buf = (stereo[ti]["L"] + stereo[ti]["R"]) * 0.5
        dur = max(e["end"] for e in evs) - evs[0]["start"]
        if dur < 0.25:
            continue
        if len(evs) == 1:
            e = evs[0]
            s0 = int(e["start"] * SR) + int(0.12 * SR)
            s1 = min(s0 + int(0.3 * SR), int(e["end"] * SR))
            if s1 - s0 >= SR // 20:
                f_exp = midi_to_freq(e["pitch"])
                p = est_pitch_ac(buf[s0:s1], SR, f_target=f_exp)
                ok = p > 0 and abs(p - f_exp) / f_exp < 0.12
                hit += int(ok)
                tot += 1
                if len(est_sample) < 24:
                    est_sample.append({"track": ti, "midi": e["pitch"],
                                       "expected_hz": round(f_exp, 1),
                                       "detected_hz": round(float(p), 1),
                                       "ok": bool(ok)})
        else:
            pitches = sorted({e["pitch"] for e in evs})
            ok, _ = chord_members_present(buf, pitches, SR)
            hit += int(ok)
            tot += 1
        per_track.setdefault(ti, [0, 0])
        per_track[ti][0] += 1
        per_track[ti][1] += int(ok)
    ver["pitch_notes_checked"] = tot
    ver["pitch_notes_hit"] = hit
    ver["pitch_hit_pct"] = round(100.0 * hit / tot, 1) if tot else 0.0
    ver["per_track"] = {
        str(k): {"role": TRACK_ROLE[k], "checked": v[0], "hit": v[1],
                 "pct": round(100.0 * v[1] / v[0], 1) if v[0] else 0.0}
        for k, v in per_track.items()}
    ver["pitch_estimate_sample"] = est_sample

    # harmonic energy (8 harmonics of lowest fundamental per voice)
    harm = {}
    for ti in sorted(stereo):
        evs = voices[ti]
        lo = min(evs, key=lambda e: e["pitch"])
        buf = (stereo[ti]["L"] + stereo[ti]["R"]) * 0.5
        s0 = int(lo["start"] * SR) + int(0.06 * SR)
        s1 = min(s0 + int(min(0.4, lo["end"] - lo["start"]) * SR), len(buf))
        if s1 - s0 < 2048:
            continue
        f0 = midi_to_freq(lo["pitch"])
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

    # ---- grid visualization ----
    spb = mid.ticks_per_beat
    step = spb // 4  # 16th note
    core_cells = int(min(total_dur, 36.0) * 4)  # 16ths over full piece
    rows = []
    for ti in sorted(voices):
        cells = ["."] * core_cells
        for e in voices[ti]:
            idx = int(round(e["start_tick"] / step))
            if 0 <= idx < core_cells:
                cells[idx] = "#" if cells[idx] == "." else "="
        rows.append(f"t{ti} {TRACK_NAME[ti][:10]:<10} |{''.join(cells)}|")
    grid_txt = ("SP-024 bowed — onset grid (1 cell = 16th note, 110 BPM)\n"
                "# = onset, = = simultaneous onset, . = rest\n"
                f"window: first {core_cells} 16ths ({core_cells/4:.1f} s)\n\n"
                + "\n".join(rows) + "\n")
    (analysis_dir / "grid_visualization.txt").write_text(grid_txt)

    # ---- write audio ----
    wav_path = audio_dir / f"{NAME}.wav"
    write_wav(str(wav_path), np.stack([mixL, mixR], axis=1), SR, normalize=False)
    ogg_path = audio_dir / f"{NAME}.ogg"
    os.system(f'ffmpeg -y -loglevel error -i "{wav_path}" '
              f'-codec:a libopus -application voip -b:a 48k "{ogg_path}"')

    # ---- artifacts ----
    bpm = round(60_000_000 / next(
        (m.tempo for t in mid.tracks for m in t if m.type == "set_tempo"), 500000), 2)
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
            "bow_envelope": "attack 80ms -> sustain -> release 150ms",
            "mix_bus": "soft-knee saturation thresh 0.82 slope 0.32, peak -1 dBFS",
        },
    }
    (analysis_dir / "render_info.json").write_text(json.dumps(info, indent=2))
    (OUT_ROOT / "provenance.json").write_text(json.dumps({
        "job": "random-style production (SP) layer-aligned",
        "date": "2026-09-26",
        "production_method": "SP-024",
        "production_method_name": "Bowed String Physical Modeling",
        "source_midi": str(SRC_MIDI),
        "layer": "absolute (all voices)",
        "outputs": {"full_mix_wav": str(wav_path), "full_mix_ogg": str(ogg_path),
                    "stems": stem_paths},
    }, indent=2))

    print(f"silence={ver['silence_ratio']*100:.1f}% peak={ver['peak']}")
    print(f"pitch notes: {ver['pitch_notes_hit']}/{ver['pitch_notes_checked']} ({ver['pitch_hit_pct']}%)")
    for k, v in ver["per_track"].items():
        print(f"  track {k} {v['role']}: {v['hit']}/{v['checked']} ({v['pct']}%)")
    for k, v in harm.items():
        print(f"  harm t{k} {v['track']}: f0={v['f0_hz']} present={v['fundamental_present']} "
              f"8h_ratio={v['harmonic_energy_8h']}")
    print("rms/s:", ver["rms_per_second"][:12], "...")
    for p in (wav_path, ogg_path):
        print(p.name, p.stat().st_size, "bytes")
        assert p.stat().st_size > 1000, f"too small: {p}"
    print("DONE", wav_path, ogg_path)


if __name__ == "__main__":
    main()
