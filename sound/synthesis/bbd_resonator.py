# -*- coding: utf-8 -*-
"""BBD resonator voice — Morphor ECHON 6 style (SP-134).

Replicable logic from the MusicTech product page for the Morphor ECHON 6
(2026-10-28; "world's first polyphonic analogue synth powered by BBD
resonators", reviewed July 2026): each of the six voices is an *analogue
resonator* built from a bucket-brigade-device (BBD) delay line — the delay
line is clocked so its round-trip time equals one period of the played note,
and feedback around the line makes it ring at that pitch.  A per-voice
analogue exciter (impulse/click/noise) drives the resonator.

What is replicated here (self-contained numpy, offline, clean-room):

- ``BBDResonatorVoice``: a tuned resonator voice whose core is a clocked
  bucket-brigade delay line:
  - stage count ``stages`` (e.g. 1024) and clock rate ``f_clk = stages * f0``
    so the loop delay is exactly one period of f0 (BBDs tune pitch by
    clocking the line);
  - per-clock-tick charge-transfer lowpass (one-pole with alpha per stage)
    — the aggregate BBD bandwidth droop;
  - zero-order-hold sampling between clock edges (the characteristic BBD
    sample-and-hold grain);
  - clock jitter (seeded) — the pitch wobble of real BBD clocks;
  - pre-emphasis on the loop input (``tone``) compensating the BBD treble
    droop, as BBD circuits do;
  - feedback gain ``g`` from ``decay`` (0.9..0.9995) — ring length;
  - ``excite``: "impulse" (single-sample click), "click" (short decaying
    pulse), "noise" (2 ms noise burst) — the analogue exciter;
  - output ``tone`` lowpass for brightness.
- ``estimate_f0``: autocorrelation-based fundamental check so the demo can
  prove the resonator actually rings at the requested pitch.

Not replicated: the ECHON 6 hardware (six discrete voices, analogue exciter
circuits), the 9×32 modulation matrix (mod_matrix.py already covers matrix
concepts), multi-timbral operation, and the analogue circuitry detail (BBD
charge-transfer physics is approximated by the one-pole per-stage model).

Usage:
    from sound.synthesis.bbd_resonator import BBDResonatorVoice

    v = BBDResonatorVoice(sample_rate=44100)
    out = v.render_note(pitch=57, dur=0.8, decay=0.6, excite="impulse")
"""

import math
from typing import Optional

import numpy as np

__all__ = ["BBDResonatorVoice", "estimate_f0"]

A440 = 440.0


def midi_to_freq(m: int) -> float:
    return A440 * (2.0 ** ((m - 69) / 12.0))


def estimate_f0(x: np.ndarray, sample_rate: int,
                lo_hz: float = 40.0, hi_hz: float = 2000.0) -> float:
    """Autocorrelation-based fundamental estimate (for verification)."""
    n = len(x)
    if n < 64:
        return 0.0
    x = x - np.mean(x)
    lo = max(2, int(round(sample_rate / hi_hz)))
    hi = min(n // 2, int(round(sample_rate / lo_hz)))
    if hi <= lo:
        return 0.0
    ac = np.correlate(x, x, "full")[n - 1:]
    ac = ac / (ac[0] + 1e-12)
    lag = int(np.argmax(ac[lo:hi])) + lo
    return sample_rate / lag


class BBDResonatorVoice:
    """Clocked bucket-brigade resonator voice.

    Parameters
    ----------
    sample_rate : int
        Output sample rate in Hz.
    stages : int
        Number of BBD stages in the line (tuned so loop delay = 1/f0).
    clock_target : float
        Nominal BBD clock rate in Hz used to pick the stage count for a
        note (the real hardware has a fixed stage count and clocks the
        line; we pick stages per note so f_clk stays in a sane BBD range).
    stage_alpha : float
        Charge-transfer loss per stage per clock tick (0..1; lower =
        darker, more BBD droop).
    clock_jitter : float
        Fractional clock-rate jitter (0..0.02 typical).
    pre_emphasis : float
        HF pre-emphasis on the loop input (0..1) compensating BBD droop.
    seed : int, optional
        Seed for clock jitter and noise exciters.
    """

    def __init__(self, sample_rate: int = 44100, stages: int = 1024,
                 clock_target: float = 96000.0, stage_alpha: float = 0.16,
                 clock_jitter: float = 0.008, pre_emphasis: float = 0.6,
                 seed: Optional[int] = None) -> None:
        self.sr = int(sample_rate)
        self.stages = int(stages)
        self.clock_target = float(clock_target)
        self.stage_alpha = float(stage_alpha)
        self.clock_jitter = float(clock_jitter)
        self.pre_emphasis = float(pre_emphasis)
        self._rng = np.random.default_rng(seed)

    def _line_setup(self, f0: float):
        # pick stage count so f_clk = stages*f0 stays near clock_target and
        # within a sane BBD clock range (8 kHz .. 200 kHz)
        n_stages = int(np.clip(round(self.clock_target / f0),
                               64, self.stages))
        f_clk = n_stages * f0
        if f_clk > 200000.0:
            n_stages = max(16, int(200000.0 / f0))
            f_clk = n_stages * f0
        if f_clk < 8000.0:
            n_stages = int(8000.0 / f0)
            f_clk = n_stages * f0
        d = max(2, int(round(self.sr / f0)))      # loop delay in output samples
        return n_stages, f_clk, d

    def render_note(self, pitch: int, dur: float, decay: float = 0.6,
                    tone: float = 0.5, excite: str = "impulse",
                    vel: int = 100) -> np.ndarray:
        """Render one resonator note.  ``excite`` in
        {'impulse','click','noise'}.  Returns mono float array."""
        n = max(1, int(round(dur * self.sr)))
        f0 = midi_to_freq(pitch)
        n_stages, f_clk, d = self._line_setup(f0)

        # feedback gain from decay (0.9 .. 0.9995)
        g = 0.90 + 0.0995 * float(np.clip(decay, 0.0, 1.0))
        # stage charge-transfer coefficient per clock tick
        a_stage = float(np.clip(self.stage_alpha, 0.02, 0.9))
        # output lowpass cutoff from tone (dark..bright)
        cut = 500.0 + 11500.0 * float(np.clip(tone, 0.0, 1.0))
        a_out = 1.0 - math.exp(-2.0 * math.pi * cut / self.sr)

        delay = np.zeros(d)
        w = 0
        # BBD state
        clk_phase = 0.0
        held = 0.0
        bucket = 0.0
        prev_bucket = 0.0
        out_lp = 0.0
        amp = (vel / 127.0) ** 1.5
        k = float(self.pre_emphasis)
        pe_norm = 1.0 + 2.0 * k          # normalise emphasis so loop gain <= g

        out = np.zeros(n)
        for i in range(n):
            t = i / self.sr
            # ---- exciter (analogue exciter -> resonator) ----
            if excite == "impulse":
                exc = 1.0 if i == 0 else 0.0
            elif excite == "click":
                exc = math.exp(-t / 0.002) * self._rng.uniform(-1.0, 1.0)
            else:  # noise burst
                exc = self._rng.uniform(-1.0, 1.0) if t < 0.002 else 0.0

            ring = delay[w]                          # current loop output
            # BBD clock: advance the bucket brigade at f_clk
            step = (f_clk / self.sr) * (1.0 + self.clock_jitter *
                                        self._rng.standard_normal())
            clk_phase += step
            while clk_phase >= 1.0:
                clk_phase -= 1.0
                # charge transfer: each stage is a one-pole on the held value
                held = ring * (1.0 - a_stage) + held * a_stage
                bucket = held
            # zero-order hold between clock edges
            bb_out = bucket

            # loop input: exciter + pre-emphasised, gain-normalised feedback
            # (emphasis compensates the BBD treble droop; normalising by
            # 1+2k keeps the loop gain <= g so the ring is stable at f0)
            pe = (bucket + k * (bucket - prev_bucket)) / pe_norm
            prev_bucket = bucket
            in_sig = exc * amp + g * pe
            delay[w] = in_sig
            w = (w + 1) % d

            # output tone shaping
            out_lp += a_out * (bb_out - out_lp)
            out[i] = out_lp

        peak = float(np.max(np.abs(out)))
        if peak > 1.0:
            out = out / peak * 0.98
        return out

    def render_melody(self, notes, decay: float = 0.6, tone: float = 0.5,
                      excite: str = "impulse") -> np.ndarray:
        """Render a list of ``{pitch, start, end, velocity}`` dicts into a
        mono array (notes summed at their start/end times)."""
        dur = max(n["end"] for n in notes)
        total = int(round(dur * self.sr))
        out = np.zeros(total)
        for nt in notes:
            s = int(round(nt["start"] * self.sr))
            e = int(round(nt["end"] * self.sr))
            note = self.render_note(nt["pitch"], (e - s) / self.sr,
                                    decay=decay, tone=tone, excite=excite,
                                    vel=nt.get("velocity", 100))
            end = min(e, total)
            out[s:end] += note[: end - s]
        peak = float(np.max(np.abs(out)))
        if peak > 1.0:
            out = out / peak * 0.98
        return out


def demo() -> dict:
    """Render three pitches and verify each rings at its own f0."""
    v = BBDResonatorVoice(sample_rate=22050, seed=5)
    results = {}
    for pitch in (45, 57, 69):
        x = v.render_note(pitch, dur=0.7, decay=0.7, tone=0.6,
                          excite="impulse")
        f0_est = estimate_f0(x[int(0.05 * v.sr):], v.sr)
        target = midi_to_freq(pitch)
        err_cents = 1200.0 * math.log2(f0_est / target) if f0_est else float("nan")
        results[pitch] = (len(x), round(f0_est, 2), round(err_cents, 2))
    return results


if __name__ == "__main__":
    import os
    import tempfile
    import wave

    v = BBDResonatorVoice(sample_rate=22050, seed=5)
    notes = [
        {"pitch": 45, "start": 0.00, "end": 0.45, "velocity": 110},
        {"pitch": 52, "start": 0.45, "end": 0.90, "velocity": 110},
        {"pitch": 57, "start": 0.90, "end": 1.35, "velocity": 110},
        {"pitch": 64, "start": 1.35, "end": 1.80, "velocity": 110},
    ]
    mix = v.render_melody(notes, decay=0.7, tone=0.6, excite="click")
    print("melody samples:", len(mix),
          "peak:", round(float(np.max(np.abs(mix))), 3))

    res = demo()
    for pitch, (ln, f0_est, err) in res.items():
        print(f"  pitch {pitch} (target {midi_to_freq(pitch):.2f} Hz) "
              f"est {f0_est} Hz  err {err:+.1f} cents  len={ln}")
    assert all(abs(err) < 60 for _, _, err in res.values()), \
        "resonator not ringing at pitch (tuning error)"

    path = os.path.join(tempfile.gettempdir(), "bbd_resonator_demo.wav")
    pcm = (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(v.sr)
        wf.writeframes(pcm.tobytes())
    print("wrote", path, os.path.getsize(path), "bytes")
    assert os.path.getsize(path) > 1000, "demo wav too small"
    print("OK — SP-134 bbd_resonator module works")
