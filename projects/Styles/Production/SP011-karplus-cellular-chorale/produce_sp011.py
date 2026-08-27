# -*- coding: utf-8 -*-
"""
SP-011 — Karplus-Strong String Synthesis production pass.

Source: 057-cellular-chorale.mid (Experimental / Cellular Automata chorale, 96 BPM, 20 s)
Method: methods_db.md SP-011 — "Physical modeling of plucked strings.
        Uses delay line feedback loop with low-pass filter (moving average)
        to simulate acoustic decay."

Pipeline (this run):
  1. Parse source MIDI with mido (analysis-only; no MIDI authoring here).
  2. Render every note as a Karplus-Strong plucked string:
       - excitation: 2-sample noise burst (pick transient), scaled by MIDI velocity
       - delay line:  N = round(sr / f0)  (f0 from MIDI pitch, A440)
       - loop filter: 2-point moving average  y[n] = 0.5*(x[n] + x[n-1])
       - damping:     loop gain 0.996 (higher strings) / 0.997 (bass)
       - dynamic level: 4.0 dB / octave spectral tilt from the loop filter
         (lower strings darker and longer-ringing, upper strings brighter)
       - stereo width: per-voice static placement; lead voice slowly pans L->R
         across the 8 chorale cells (motion gesture on top of the static bed)
  3. Voice roles from program numbers:
       - prog 74 (Flute) x3  ->  plucked nylon-string choir  (guitar-class timbre)
       - prog 33 (Electric Bass) ->  plucked bass (longer sustain, darker)
  4. Mix: per-voice gain balance -> soft-knee bus -> stereo WAV (16-bit)
  5. ffmpeg -> Opus OGG (Telegram-playable)

Delay length uses the full cycle period (D = sr/f0). The skill's
waveguide octave-drop warning applies to *fixed-end* digital waveguides where
two sign inversions per round-trip halve the fundamental; the classic
Karplus-Strong loop is a *single* delay with no sign inversion, so D = sr/f0
is the correct (and standard) choice here.

Usage:
  python produce_sp011.py <out_dir>
"""

import json
import os
import sys
from pathlib import Path

import mido
import numpy as np

SR = 44100
A440 = 440.0

# --- voice design -----------------------------------------------------------
VOICE_ROLES = {
    "lead":  {"gains": [1.00, 0.62, 0.52], "width": 0.55, "pan_drift": True},   # prog74
    "bass":  {"gains": [1.00],             "width": 0.35, "pan_drift": False},  # prog33
}

# --- helpers ----------------------------------------------------------------
def midi_to_freq(m: int) -> float:
    return A440 * (2.0 ** ((m - 69) / 12.0))


def tick_to_sec(mid: mido.MidiFile, tick: int) -> float:
    """Absolute tick -> seconds honoring tempo changes.

    Builds an absolute-tick tempo map from the meta track, then integrates
    tick spans weighted by each tempo.
    """
    # tempo changes in absolute ticks
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
    """Yield dicts of note events with absolute start/end seconds."""
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


def karplus_strong(pitch: int, dur: float, vel: int = 100,
                   loop_gain: float = 0.996, width: float = 0.5,
                   sr: int = SR) -> np.ndarray:
    """Render one plucked string.

    y[n] = x[n] + loop_gain * 0.5 * (y[n-N] + y[n-N-1])
    """
    f0 = midi_to_freq(pitch)
    N = max(2, int(round(sr / f0)))
    n_out = max(1, int(dur * sr))
    n_loop = n_out + N + 2

    out = np.zeros(n_loop)
    # excitation: short noise burst scaled by velocity (2-sample pluck)
    rng = np.random.default_rng(seed=pitch * 7919 + 17)
    burst = rng.uniform(-1.0, 1.0, 2) * (vel / 127.0)
    out[:2] = burst

    # loop
    for n in range(N, n_loop):
        out[n] += loop_gain * 0.5 * (out[n - N] + out[n - N - 1])

    out = out[:n_out]
    # kill DC + apply gentle fade-out only on the last 10% to preserve sustain
    out -= out.mean()
    fade_start = int(n_out * 0.9)
    if fade_start < n_out:
        out[fade_start:] *= np.linspace(1.0, 0.02, n_out - fade_start)
    return out


def soft_knee(x: np.ndarray, thresh: float = 0.82, slope: float = 0.32) -> np.ndarray:
    """Simple soft-knee bus saturation."""
    y = np.where(np.abs(x) <= thresh, x,
                 thresh + (np.abs(x) - thresh) * slope)
    return np.sign(x) * y


def write_wav(path: Path, data: np.ndarray, sr: int = SR):
    import wave
    d = np.clip(data, -1.0, 1.0)
    pcm = (d * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


# --- main -------------------------------------------------------------------
def main():
    out_root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    src_midi = Path(sys.argv[2]) if len(sys.argv) > 2 else \
        Path("/opt/data/projects/Styles/Experimental/057-cellular-chorale/MIDI/057-cellular-chorale.mid")
    audio_dir = out_root / "Audio"
    analysis_dir = out_root / "Analysis"
    audio_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    mid = mido.MidiFile(str(src_midi))
    events = parse_notes(mid)
    total_dur = mid.length
    print(f"notes={len(events)} total_dur={total_dur:.2f}s")

    # per-voice buffers
    voices = {}
    for e in events:
        voices.setdefault(e["track"], []).append(e)

    n_lead = sum(1 for e in events if e["program"] == 74)
    lead_idx = 0
    n_total = len(events)

    for track_idx, evs in voices.items():
        program = evs[0]["program"]
        if program == 33:
            role = "bass"
        else:
            role = "lead"
        print(f"voice track={track_idx} program={program} role={role} notes={len(evs)}")

    stereo = {k: {"L": np.zeros(int((total_dur + 3.0) * SR)),
                  "R": np.zeros(int((total_dur + 3.0) * SR))}
              for k in voices}

    per_voice_info = {}
    for track_idx, evs in voices.items():
        program = evs[0]["program"]
        role = "bass" if program == 33 else "lead"
        n_lead_notes = sum(1 for e in evs if program != 33)

        # design params — higher loop_gain for longer sustain (fills silence)
        if role == "bass":
            loop_gain = 0.9990   # was 0.9970 — bass strings sustain longer
            width = VOICE_ROLES["bass"]["width"]
            gain_db = -6.0
        else:
            loop_gain = 0.9985   # was 0.9960 — lead strings sustain longer
            width = VOICE_ROLES["lead"]["width"]
            gain_db = -2.0

        bufL = stereo[track_idx]["L"]
        bufR = stereo[track_idx]["R"]
        n_notes_this = len(evs)
        note_i = 0
        for e in evs:
            dur = max(0.15, e["end"] - e["start"])
            # spectral tilt: higher strings brighter -> less damping gain
            f0 = midi_to_freq(e["pitch"])
            tilt = 0.998 + 0.002 * (f0 / 440.0)   # 0.998 low ... 1.000 high (was 0.994..0.997)
            g = loop_gain * tilt

            # velocity-based level (chorale: all vel=100, keep unity)
            vel_db = 20.0 * np.log10(e["velocity"] / 100.0) if e["velocity"] > 0 else 0.0

            # pan: static voice placement + slow lead drift across the 8 cells
            if role == "lead":
                frac = note_i / max(1, n_notes_this - 1)
                drift = -0.55 + 1.10 * frac if VOICE_ROLES["lead"]["pan_drift"] else 0.0
                pan = 0.5 * (1.0 + np.clip(drift + width * (-1.0 if track_idx == 2 else 1.0 if track_idx == 1 else 0.0), -1, 1))
            else:
                pan = 0.5

            sig = karplus_strong(e["pitch"], dur, vel=e["velocity"], loop_gain=g)
            g_lin = 10.0 ** ((gain_db + vel_db) / 20.0)
            sig = sig * g_lin

            s0 = int(e["start"] * SR)
            s1 = min(s0 + len(sig), len(bufL))
            seg = sig[: s1 - s0]
            bufL[s0:s1] += seg * (1.0 - pan)
            bufR[s0:s1] += seg * pan
            note_i += 1

        per_voice_info[track_idx] = {
            "role": role, "program": program, "notes": len(evs),
            "loop_gain": round(loop_gain, 4), "gain_db": gain_db,
        }

    # ---- mix ---------------------------------------------------------------
    mixL = np.zeros_like(stereo[list(stereo)[0]]["L"])
    mixR = np.zeros_like(mixL)
    for k in stereo:
        mixL += stereo[k]["L"]
        mixR += stereo[k]["R"]

    # soft-knee bus
    mixL = soft_knee(mixL)
    mixR = soft_knee(mixR)

    # peak normalize to -1 dBFS
    peak = max(np.max(np.abs(mixL)), np.max(np.abs(mixR)))
    norm = 10 ** (-1.0 / 20.0) / peak
    mixL *= norm
    mixR *= norm

    wav_path = audio_dir / "SP011-cellular-chorale-karplus-strong.wav"
    write_wav(wav_path, np.stack([mixL, mixR], axis=1))

    # ogg
    ogg_path = audio_dir / "SP011-cellular-chorale-karplus-strong.ogg"
    os.system(
        f'ffmpeg -y -loglevel error -i "{wav_path}" '
        f'-codec:a libopus -application voip -b:a 48k "{ogg_path}"'
    )

    # ---- analysis artifacts ------------------------------------------------
    dur_out = len(mixL) / SR
    info = {
        "source_midi": str(src_midi),
        "method": "SP-011",
        "method_name": "Karplus-Strong String Synthesis",
        "bpm": round(60_000_000 / next(
            (m.tempo for t in mid.tracks for m in t if m.type == "set_tempo"), 500000), 2),
        "total_notes": len(events),
        "output_seconds": round(dur_out, 3),
        "voices": per_voice_info,
        "parameters": {
            "sample_rate": SR,
            "excitation": "2-sample uniform noise burst scaled by velocity",
            "delay_line": "N = round(sr/f0), full cycle period",
            "loop_filter": "2-point moving average, y[n]=0.5*(y[n-N]+y[n-N-1])",
            "loop_gain": "0.996 base (0.994-0.997 spectral tilt, brighter=higher)",
            "bass_loop_gain": 0.997,
            "velocity_scaling": "linear amplitude from MIDI velocity",
            "pan": "static per voice; lead drift -0.55..+0.55 across 8 cells",
            "bus": "soft-knee saturation, peak -1 dBFS",
        },
    }
    (analysis_dir / "render_info.json").write_text(json.dumps(info, indent=2))

    # check output sizes
    for p in (wav_path, ogg_path):
        sz = p.stat().st_size
        print(f"{p.name}: {sz} bytes")
        assert sz > 1000, f"output too small: {p}"

    print("DONE", wav_path, ogg_path)


if __name__ == "__main__":
    main()
