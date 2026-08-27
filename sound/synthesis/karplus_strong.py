# -*- coding: utf-8 -*-
"""Karplus-Strong String Synthesis (SP-011) — shared, reusable module.

Promoted from `Styles/Production/SP011-karplus-cellular-chorale/produce_sp011.py`
(2026-08-27) so the method is a callable tool, not a one-off project script.

Method (methods_db.md SP-011): "Physical modeling of plucked strings. Uses
delay line feedback loop with low-pass filter (moving average) to simulate
acoustic decay."

Key correctness note (octave): the classic Karplus-Strong loop is a SINGLE
delay with NO sign inversion, so the delay length is `D = sr / f0` — do NOT
divide by 2 (that would drop the pitch an octave). This is the documented
fix applied to the string instrument guides on 2026-08-27.

API:
    render_note(pitch, dur, vel=100, loop_gain=0.996, width=0.5, sr=44100)
        -> np.ndarray (mono float, len = dur*sr)

    render_melody(notes, roles=None, sr=44100, ...)
        -> (np.ndarray (N,2) stereo float, dict info)
      notes: list of dicts {pitch, start, end, velocity, role|program}
      roles: per-role gain/width/pan config (see VOICE_ROLES default)

Example:
    from sound.synthesis.karplus_strong import render_note
    audio = render_note(pitch=69, dur=1.0)
"""

import numpy as np

SR = 44100
A440 = 440.0

# voice design defaults (from the SP-011 production pass)
VOICE_ROLES = {
    "lead": {"gains": [1.00, 0.62, 0.52], "width": 0.55, "pan_drift": True,
             "gain_db": -2.0, "loop_gain": 0.9985},
    "bass": {"gains": [1.00], "width": 0.35, "pan_drift": False,
             "gain_db": -6.0, "loop_gain": 0.9990},
}


def midi_to_freq(m: int) -> float:
    return A440 * (2.0 ** ((m - 69) / 12.0))


def karplus_strong(pitch: int, dur: float, vel: int = 100,
                   loop_gain: float = 0.996, width: float = 0.5,
                   sr: int = SR) -> np.ndarray:
    """Render one plucked string (mono).

    y[n] = x[n] + loop_gain * 0.5 * (y[n-N] + y[n-N-1])
    N = round(sr / f0)   # full cycle period — NOT sr/(2*f0)
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
    # kill DC + gentle fade on last 10% to preserve sustain
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


def render_melody(notes, sr: int = SR, roles: dict = None):
    """Render a list of notes into a stereo mix.

    notes: list of dicts, each with keys:
        pitch (int), start (float sec), end (float sec),
        velocity (int, default 100),
        role (str: "lead"|"bass") OR program (int: 33=bass, else lead)

    Returns (stereo_audio, info_dict).
    """
    roles = roles or VOICE_ROLES
    total_dur = max((n["end"] for n in notes), default=1.0) + 3.0
    n_samples = int(total_dur * sr)

    # group by role
    stereo = {}
    per_voice = {}
    for i, n in enumerate(notes):
        role = n.get("role")
        if role is None:
            role = "bass" if n.get("program") == 33 else "lead"
        stereo.setdefault(role, {"L": np.zeros(n_samples), "R": np.zeros(n_samples)})
        per_voice.setdefault(role, []).append((i, n))

    role_info = {}
    for role, items in per_voice.items():
        cfg = roles.get(role, VOICE_ROLES["lead"])
        bufL, bufR = stereo[role]["L"], stereo[role]["R"]
        n_notes = len(items)
        for j, (i, n) in enumerate(items):
            dur = max(0.15, n["end"] - n["start"])
            f0 = midi_to_freq(n["pitch"])
            # spectral tilt: higher strings brighter -> less damping
            tilt = 0.998 + 0.002 * (f0 / 440.0)
            g = cfg["loop_gain"] * tilt
            vel = n.get("velocity", 100)
            vel_db = 20.0 * np.log10(vel / 100.0) if vel > 0 else 0.0

            if role == "lead" and cfg.get("pan_drift"):
                frac = j / max(1, n_notes - 1)
                drift = -0.55 + 1.10 * frac
                pan = 0.5 * (1.0 + np.clip(drift + cfg["width"] * 0.0, -1, 1))
            else:
                pan = 0.5

            sig = karplus_strong(n["pitch"], dur, vel=vel, loop_gain=g, sr=sr)
            g_lin = 10.0 ** ((cfg["gain_db"] + vel_db) / 20.0)
            sig = sig * g_lin

            s0 = int(n["start"] * sr)
            s1 = min(s0 + len(sig), n_samples)
            seg = sig[: s1 - s0]
            bufL[s0:s1] += seg * (1.0 - pan)
            bufR[s0:s1] += seg * pan

        role_info[role] = {"notes": n_notes, "config": {k: v for k, v in cfg.items()
                                                        if not callable(v)}}

    mixL = np.zeros(n_samples)
    mixR = np.zeros(n_samples)
    for role in stereo:
        mixL += stereo[role]["L"]
        mixR += stereo[role]["R"]
    mixL = soft_knee(mixL)
    mixR = soft_knee(mixR)

    peak = max(np.max(np.abs(mixL)), np.max(np.abs(mixR)))
    if peak > 0:
        norm = 10 ** (-1.0 / 20.0) / peak
        mixL *= norm
        mixR *= norm

    stereo_out = np.stack([mixL, mixR], axis=1)
    info = {
        "method": "SP-011",
        "method_name": "Karplus-Strong String Synthesis",
        "sample_rate": sr,
        "output_seconds": round(len(mixL) / sr, 3),
        "roles": role_info,
        "note_count": len(notes),
    }
    return stereo_out, info


def render_melody_wav(notes, path, sr: int = SR, roles: dict = None):
    """Render notes to a stereo WAV file at `path`."""
    import wave
    audio, info = render_melody(notes, sr=sr, roles=roles)
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    return audio, info


if __name__ == "__main__":
    # demo: render an A4 pluck and a short C-major arpeggio
    import os
    import tempfile

    audio, info = render_melody([
        {"pitch": 69, "start": 0.0, "end": 1.0, "velocity": 100, "role": "lead"},
        {"pitch": 72, "start": 0.5, "end": 1.0, "velocity": 90, "role": "lead"},
        {"pitch": 76, "start": 1.0, "end": 1.5, "velocity": 85, "role": "lead"},
        {"pitch": 45, "start": 0.0, "end": 2.0, "velocity": 110, "role": "bass"},
    ])
    print("stereo shape:", audio.shape)
    print("info:", info)
    tmp = os.path.join(tempfile.gettempdir(), "karplus_demo.wav")
    render_melody_wav([{"pitch": 69, "start": 0.0, "end": 1.0}], tmp)
    print("wrote", tmp, os.path.getsize(tmp), "bytes")
    assert os.path.getsize(tmp) > 1000, "demo wav too small"
    print("OK — SP-011 karplus_strong module works")
