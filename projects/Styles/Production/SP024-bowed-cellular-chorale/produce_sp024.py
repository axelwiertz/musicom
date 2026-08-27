# -*- coding: utf-8 -*-
"""
SP-024 — Bowed String Physical Modeling production pass.

Source: 057-cellular-chorale.mid (Experimental / Cellular Automata chorale, 96 BPM, 20 s)
Method: SP-024 — Friction-Induced Waveguide Synthesis (methods_db.md SP-024)

Bowed strings sustain for the full note duration, naturally filling the
silence that Karplus-Strong plucked strings left between notes.

Pipeline:
  1. Parse source MIDI with mido (analysis-only).
  2. Render every note as a bowed string via BowedString (library code):
       - bow velocity / force envelopes for attack-sustain-release
       - per-voice bow position (timbre variation)
       - velocity-based dynamics
  3. Stereo placement: per-voice static pan + lead drift across cells.
  4. Mix: per-voice gain → soft-knee bus → stereo WAV (16-bit) → OGG.

Usage:
  python produce_sp024.py
"""

import json
import os
import sys
from pathlib import Path

import mido
import numpy as np

# library imports (editable install)
from sound.synthesis.bowed import BowedString
from sound.utils.io import write_wav

SR = 44100
A440 = 440.0

# --- voice design -----------------------------------------------------------
VOICE_PARAMS = {
    "lead": {"gain_db": -2.0, "width": 0.55, "bow_pos": 0.15, "bow_vel": 0.18, "bow_force": 1.2},
    "bass": {"gain_db": -6.0, "width": 0.35, "bow_pos": 0.12, "bow_vel": 0.12, "bow_force": 1.8},
}


# --- helpers ----------------------------------------------------------------
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
        program, channel = 0, 0
        for m in track:
            if m.type == "program_change":
                program, channel = m.program, m.channel
        abstick = 0
        active = {}
        for m in track:
            abstick += m.time
            if m.type == "note_on" and m.velocity > 0:
                active[m.note] = (abstick, m.velocity)
            elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
                if m.note in active:
                    s, vel = active.pop(m.note)
                    events.append({
                        "track": ti, "program": program, "pitch": m.note,
                        "velocity": vel,
                        "start": tick_to_sec(mid, s),
                        "end": tick_to_sec(mid, abstick),
                    })
    events.sort(key=lambda e: e["start"])
    return events


def make_bow_envelope(dur: float, bow_vel: float, sr: int = SR) -> np.ndarray:
    """Attack-sustain-release envelope for bow velocity."""
    n = int(dur * sr)
    env = np.full(n, bow_vel, dtype=float)
    attack = int(min(0.08 * sr, n * 0.15))
    release = int(min(0.12 * sr, n * 0.15))
    if attack > 0:
        env[:attack] = np.linspace(0.0, bow_vel, attack)
    if release > 0:
        env[-release:] = np.linspace(bow_vel, 0.0, release)
    return env


def soft_knee(x: np.ndarray, thresh: float = 0.82, slope: float = 0.32) -> np.ndarray:
    y = np.where(np.abs(x) <= thresh, x, thresh + (np.abs(x) - thresh) * slope)
    return np.sign(x) * y


# --- main -------------------------------------------------------------------
def main():
    out_root = Path("/opt/data/projects/Styles/Production/SP024-bowed-cellular-chorale")
    src_midi = Path("/opt/data/projects/Styles/Experimental/057-cellular-chorale/MIDI/057-cellular-chorale.mid")
    audio_dir = out_root / "Audio"
    analysis_dir = out_root / "Analysis"
    midi_dir = out_root / "MIDI"
    audio_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    midi_dir.mkdir(parents=True, exist_ok=True)

    # copy MIDI
    import shutil
    shutil.copy2(src_midi, midi_dir / src_midi.name)

    mid = mido.MidiFile(str(src_midi))
    events = parse_notes(mid)
    total_dur = mid.length
    print(f"notes={len(events)} total_dur={total_dur:.2f}s")

    # per-voice buffers
    voices = {}
    for e in events:
        voices.setdefault(e["track"], []).append(e)

    bs = BowedString(sample_rate=SR)

    # stereo bus
    buf_len = int((total_dur + 3.0) * SR)
    stereo = {k: {"L": np.zeros(buf_len), "R": np.zeros(buf_len)} for k in voices}

    per_voice_info = {}
    for track_idx, evs in voices.items():
        program = evs[0]["program"]
        role = "bass" if program == 33 else "lead"
        vp = VOICE_PARAMS[role]
        print(f"voice track={track_idx} program={program} role={role} notes={len(evs)}")

        bufL = stereo[track_idx]["L"]
        bufR = stereo[track_idx]["R"]
        n_notes_this = len(evs)

        for note_i, e in enumerate(evs):
            dur = max(0.2, e["end"] - e["start"])
            freq = midi_to_freq(e["pitch"])

            # bow velocity envelope (attack-sustain-release)
            v_env = make_bow_envelope(dur, vp["bow_vel"])

            # render bowed string
            sig = bs.render(
                freq=freq,
                duration=dur,
                bow_velocity=v_env,
                bow_force=vp["bow_force"],
                bow_position=vp["bow_pos"],
            )

            # gain
            vel_db = 20.0 * np.log10(e["velocity"] / 100.0) if e["velocity"] > 0 else 0.0
            g_lin = 10.0 ** ((vp["gain_db"] + vel_db) / 20.0)
            sig = sig * g_lin

            # pan: lead drifts across cells, bass center
            if role == "lead":
                frac = note_i / max(1, n_notes_this - 1)
                drift = -0.55 + 1.10 * frac
                pan = 0.5 * (1.0 + np.clip(drift + vp["width"] * (-1.0 if track_idx == 2 else 1.0 if track_idx == 1 else 0.0), -1, 1))
            else:
                pan = 0.5

            s0 = int(e["start"] * SR)
            s1 = min(s0 + len(sig), buf_len)
            seg = sig[:s1 - s0]
            bufL[s0:s1] += seg * (1.0 - pan)
            bufR[s0:s1] += seg * pan

        per_voice_info[track_idx] = {
            "role": role, "program": program, "notes": len(evs),
            "bow_velocity": vp["bow_vel"], "bow_force": vp["bow_force"],
            "bow_position": vp["bow_pos"], "gain_db": vp["gain_db"],
        }

    # ---- mix ---------------------------------------------------------------
    mixL = np.zeros(buf_len)
    mixR = np.zeros(buf_len)
    for k in stereo:
        mixL += stereo[k]["L"]
        mixR += stereo[k]["R"]

    # soft-knee bus
    mixL = soft_knee(mixL)
    mixR = soft_knee(mixR)

    # peak normalize to -1 dBFS
    peak = max(np.max(np.abs(mixL)), np.max(np.abs(mixR)))
    if peak > 0:
        norm = 10 ** (-1.0 / 20.0) / peak
        mixL *= norm
        mixR *= norm

    # write stereo WAV (use library write_wav with stereo)
    wav_path = audio_dir / "SP024-cellular-chorale-bowed-string.wav"
    stereo_out = np.stack([mixL, mixR], axis=1)
    write_wav(str(wav_path), stereo_out, SR)

    # ogg
    ogg_path = audio_dir / "SP024-cellular-chorale-bowed-string.ogg"
    os.system(
        f'ffmpeg -y -loglevel error -i "{wav_path}" '
        f'-codec:a libopus -application voip -b:a 48k "{ogg_path}"'
    )

    # ---- analysis artifacts ------------------------------------------------
    dur_out = len(mixL) / SR
    info = {
        "source_midi": str(src_midi),
        "method": "SP-024",
        "method_name": "Bowed String Physical Modeling (Friction-Induced Waveguide Synthesis)",
        "bpm": round(60_000_000 / next(
            (m.tempo for t in mid.tracks for m in t if m.type == "set_tempo"), 500000), 2),
        "total_notes": len(events),
        "output_seconds": round(dur_out, 3),
        "voices": per_voice_info,
        "parameters": {
            "sample_rate": SR,
            "synthesis_engine": "sound.synthesis.bowed.BowedString (library)",
            "bow_friction_model": "exponential sliding friction, Newton-Raphson (4 iterations)",
            "waveguide": "bidirectional delay lines, neck + bridge segments",
            "bridge_filter": "one-pole LPF (coef=0.6)",
            "bow_envelope": "attack 80ms → sustain → release 120ms",
            "pan": "static per voice; lead drift -0.55..+0.55 across 8 cells",
            "bus": "soft-knee saturation, peak -1 dBFS",
        },
    }
    (analysis_dir / "render_info.json").write_text(json.dumps(info, indent=2))

    # provenance
    prov = {
        "job": "SP-024 production pass (manual, not cron)",
        "source_midi": str(src_midi),
        "production_method": "SP-024",
        "production_method_name": "Bowed String Physical Modeling",
        "outputs": {
            "full_mix_wav": str(wav_path),
            "full_mix_ogg": str(ogg_path),
        },
    }
    (out_root / "provenance.json").write_text(json.dumps(prov, indent=2))

    # check output sizes
    for p in (wav_path, ogg_path):
        sz = p.stat().st_size
        print(f"{p.name}: {sz} bytes")
        assert sz > 1000, f"output too small: {p}"

    print("DONE", wav_path, ogg_path)


if __name__ == "__main__":
    main()
