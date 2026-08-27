# -*- coding: utf-8 -*-
"""Linear Predictive Coding (LPC) Synthesis (SP-028) — shared, reusable module.

Promoted from `Styles/Production/SP028-LPC-country-uke/produce_sp028.py`
(2026-08-27) so the method is a callable tool.

Method (methods_db.md SP-028): source-filter model. Analysis = autocorrelation
+ Levinson-Durbin → all-pole filter coefficients (formants). Synthesis =
re-excite the filter with a glottal impulse train (voiced) or noise (unvoiced).

API:
    levinson_durbin(r, order) -> (a, k, E)
    lpc_analyze(x, fs, frame_ms=30, hop_ms=10, order=14, alpha=0.97)
        -> list of frames {a, gain, pitch, voiced, time}
    lpc_synthesize(frames, fs, pitch_shift=1.0, voiced_gain=1.0,
                   unvoiced_gain=1.0, t0_boost=1.0)
        -> np.ndarray (formant-preserved, pitch-shifted audio)
    lpc_vocoder(x, fs, pitch_shift=1.0, ...)  # one-shot analyze+resynth
"""

import numpy as np


def levinson_durbin(r, order):
    """Solve Yule-Walker via Levinson-Durbin recursion. Returns a[1..p], E."""
    a = np.zeros(order + 1)
    a[0] = 1.0
    a_prev = np.zeros(order + 1)
    a_prev[0] = 1.0
    E = r[0]
    k = np.zeros(order)
    for i in range(1, order + 1):
        acc = r[i]
        for j in range(1, i):
            acc += a_prev[j] * r[i - j]
        ki = -acc / (E + 1e-20)
        k[i - 1] = ki
        a[i] = ki
        for j in range(1, i):
            a[j] = a_prev[j] + ki * a_prev[i - j]
        E = (1.0 - ki * ki) * E
        a_prev[:i + 1] = a[:i + 1].copy()
    return a, k, E


def lpc_analyze(x, fs, frame_ms=30, hop_ms=10, order=14, alpha=0.97,
                pitch_scale=1.0):
    """Per-frame LPC: a-coeffs, gain, pitch period, voicing.

    pitch_scale multiplies the detected pitch period (for downmix demos).
    """
    L = int(frame_ms * fs / 1000)
    H = int(hop_ms * fs / 1000)
    n_frames = (len(x) - L) // H + 1
    win = np.hamming(L)
    frames = []
    for m in range(n_frames):
        start = m * H
        frame = x[start:start + L].astype(np.float64)
        pre = np.zeros(L)
        pre[0] = frame[0]
        pre[1:] = frame[1:] - alpha * frame[:-1]
        xw = pre * win
        r = np.zeros(order + 1)
        for kl in range(order + 1):
            r[kl] = np.dot(xw[:L - kl], xw[kl:])
        a, kk, E = levinson_durbin(r, order)
        # residual for pitch detection
        residual = np.zeros(L)
        for n in range(L):
            residual[n] = xw[n]
            for j in range(1, order + 1):
                if n - j >= 0:
                    residual[n] += a[j] * xw[n - j]
        T_min = int(fs / 500.0)
        T_max = int(fs / 60.0)
        T_max = min(T_max, L - 1)
        voiced = False
        pitch = 0
        if T_max > T_min:
            Rr = np.correlate(residual, residual, mode='full')[L - 1:]
            if T_max < len(Rr):
                seg = Rr[T_min:T_max + 1]
                bl = T_min + int(np.argmax(seg))
                vs = Rr[bl] / (Rr[0] + 1e-20)
                voiced = vs > 0.5
                pitch = bl if voiced else 0
        frames.append({
            'a': a, 'gain': np.sqrt(max(E, 1e-20)),
            'pitch': int(pitch * pitch_scale), 'voiced': voiced,
            'time': (start + L / 2) / fs,
        })
    return frames


def lpc_synth_frame(a, excitation):
    """All-pole IIR: y[n] = e[n] - sum(a_k y[n-k])."""
    order = len(a) - 1
    y = np.zeros(len(excitation))
    for n in range(len(excitation)):
        y[n] = excitation[n]
        for j in range(1, order + 1):
            if n - j >= 0:
                y[n] -= a[j] * y[n - j]
    return y


def lpc_synthesize(frames, fs, frame_ms=30, hop_ms=10, pitch_shift=1.0,
                   voiced_gain=1.0, unvoiced_gain=1.0, t0_boost=1.0):
    """Reconstruct audio from LPC frames. Formants preserved; pitch shifted."""
    L = int(frame_ms * fs / 1000)
    H = int(hop_ms * fs / 1000)
    order = len(frames[0]['a']) - 1
    total = (len(frames) - 1) * H + L
    y = np.zeros(total)
    ws = np.zeros(total)
    win = np.hamming(L)
    rng = np.random.default_rng(42)
    for m, fr in enumerate(frames):
        a = fr['a']
        ex = np.zeros(L)
        if fr['voiced'] and fr['pitch'] > 0:
            T0 = max(1, int(fr['pitch'] / pitch_shift * t0_boost))
            amp = fr['gain'] * voiced_gain
            for n in range(L):
                if n % T0 == 0:
                    ex[n] = amp
        else:
            ex = fr['gain'] * unvoiced_gain * rng.standard_normal(L)
        fout = lpc_synth_frame(a, ex)
        fout *= win
        start = m * H
        y[start:start + L] += fout
        ws[start:start + L] += win ** 2
    nz = ws > 1e-8
    y[nz] /= ws[nz]
    pk = np.max(np.abs(y))
    if pk > 0:
        y = y / pk * 0.98
    return y


def lpc_vocoder(x, fs, pitch_shift=1.0, order=16, frame_ms=30, hop_ms=10,
                voiced_gain=1.0, unvoiced_gain=0.15, t0_boost=1.0):
    """One-shot LPC analysis + formant-preserving resynthesis."""
    frames = lpc_analyze(x, fs, frame_ms=frame_ms, hop_ms=hop_ms,
                         order=order, alpha=0.97)
    return lpc_synthesize(frames, fs, frame_ms=frame_ms, hop_ms=hop_ms,
                          pitch_shift=pitch_shift, voiced_gain=voiced_gain,
                          unvoiced_gain=unvoiced_gain, t0_boost=t0_boost)


if __name__ == "__main__":
    import os
    import tempfile

    fs = 44100
    t = np.linspace(0, 1.0, fs, endpoint=False)
    # sawtooth-ish voice-like tone (harmonic-rich)
    x = np.zeros_like(t)
    for h in range(1, 12):
        x += np.sin(2 * np.pi * 220 * h * t) / h
    x = x / np.max(np.abs(x))

    frames = lpc_analyze(x, fs, order=16)
    voiced_frac = np.mean([f['voiced'] for f in frames])
    print("frames:", len(frames), "voiced frac:", round(voiced_frac, 3))

    y = lpc_synthesize(frames, fs)
    print("resynth len:", len(y), "orig len:", len(x))
    assert abs(len(y) - len(x)) < 2 * fs // 10, "length mismatch"

    # pitch shift up a fourth (formants preserved)
    y2 = lpc_synthesize(frames, fs, pitch_shift=4.0 / 3.0)
    print("pitch-shifted len:", len(y2))

    tmp = os.path.join(tempfile.gettempdir(), "lpc_demo.wav")
    import wave
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    with wave.open(tmp, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(pcm.tobytes())
    print("wrote", tmp, os.path.getsize(tmp), "bytes")
    assert os.path.getsize(tmp) > 1000
    print("OK — SP-028 lpc_synth module works")
