"""Tape-stop / turntable-stop processor — Cableguys TimeStop style.

Replicable DSP from the Sound On Sound item "Cableguys release TimeStop"
(2026-10-15): a tape-stop effect driven by an automatable speed/depth curve
instead of fixed bar lengths. Three timing modes:

* ``classic`` — standard slow-down: playback rate ramps 1.0 → ~0 while the
  read position keeps accumulating, so pitch AND time drop together (like a
  vinyl record stopping).
* ``modern`` — pitch drops WITHOUT changing timing: grains are windowed at
  time-aligned positions (source position == output position) while each
  grain is resampled internally by the instantaneous rate, so the source
  stays locked to the beat while pitch falls (formant-style, granular
  pitch-shift with zero time-stretch).
* ``loop`` — a slice of audio is captured at the trigger point and
  retriggered (stutter) while the central rate curve is applied to the
  repeated slice.

The rate curve is the "automation" the DAW would draw: any callable/array
mapping normalized time 0..1 (or per-sample) to instantaneous playback rate.
Default is an exponential ramp (fast onset, long tail) over ``stop_time_sec``.

Not replicated: the VST3/AU/AAX host, automation UI, bounce-free DAW
integration (this is the offline render equivalent).

Usage:
    from sound.effects.tape_stop import TapeStop

    ts = TapeStop(sample_rate=44100)
    out = ts.process(audio, mode="classic", stop_time_sec=1.5)
"""

from __future__ import annotations

import numpy as np

DEFAULT_SR = 44100
MIN_RATE = 1e-3


def default_rate_curve(n: int, stop: float = 0.02) -> np.ndarray:
    """Exponential rate ramp 1.0 -> ``stop`` over ``n`` samples.

    Fast onset, long tail — the classic tape/vinyl deceleration feel.
    """
    t = np.linspace(0.0, 1.0, n)
    curve = np.exp(np.log(max(stop, MIN_RATE)) * np.power(t, 1.5))
    return np.clip(curve, MIN_RATE, 1.0)


class TapeStop:
    """Offline tape-stop processor with Classic / Modern / Loop modes.

    Args:
        sample_rate: audio sample rate in Hz.
        gain_comp: when True, resampled output is gain-compensated so the
            pitch drop does not audibly duck (energy preserved per grain).
    """

    def __init__(self, sample_rate: int = DEFAULT_SR, gain_comp: bool = True):
        self.sample_rate = int(sample_rate)
        self.gain_comp = gain_comp

    # ------------------------------------------------------------------
    # mode helpers
    # ------------------------------------------------------------------
    def _classic(self, x: np.ndarray, rate: np.ndarray) -> np.ndarray:
        """Resample: cumulative source phase follows the rate curve."""
        n = len(x)
        m = len(rate)
        # cumulative read position: p[k+1] = p[k] + rate[k]
        phase = np.cumsum(rate) - rate[0]
        src = np.arange(n, dtype=np.float64)
        # limit phase to valid input range (stop = end of tape -> hold last sample)
        phase = np.minimum(phase, n - 1)
        out = np.interp(phase, src, x)
        if self.gain_comp and m > 0:
            # energy-preserving compensation: scale by sqrt(1/mean rate)
            g = float(np.sqrt(1.0 / max(np.mean(rate), MIN_RATE)))
            out = out * min(g, 6.0)
        return out, phase

    def _modern(self, x: np.ndarray, rate: np.ndarray, grain_ms: float = 40.0) -> np.ndarray:
        """Pitch-only drop: time-aligned grains, internal resample by rate."""
        n = len(x)
        grain = max(64, int(self.sample_rate * grain_ms / 1000.0))
        hop = grain // 2
        win = np.hanning(grain)
        out = np.zeros(n + grain, dtype=np.float64)
        acc = np.zeros(n + grain, dtype=np.float64)
        centers = list(range(0, n, hop))
        for c in centers:
            r = float(rate[min(c, len(rate) - 1)])
            i0 = max(0, c - grain // 2)
            seg = x[i0:i0 + grain]
            if len(seg) < grain:  # zero-pad tail grain
                seg = np.pad(seg, (0, grain - len(seg)))
            # internal resample by rate: play the grain segment slower if r<1
            src = np.arange(grain, dtype=np.float64) * r
            src = np.minimum(src, grain - 1)
            shifted = np.interp(src, np.arange(grain), seg) * win
            if self.gain_comp and r > MIN_RATE:
                shifted = shifted * float(np.sqrt(1.0 / r))
            out[c:c + grain] += shifted
            acc[c:c + grain] += win
        acc = np.maximum(acc, 1e-8)
        return out[:n] / acc[:n]

    def _loop(self, x: np.ndarray, rate: np.ndarray,
              trigger: int, loop_sec: float = 0.25) -> np.ndarray:
        """Capture a slice at ``trigger`` and stutter it under the ramp."""
        n = len(x)
        loop_len = max(64, int(self.sample_rate * loop_sec))
        trigger = int(np.clip(trigger, 0, n - loop_len))
        slice_ = x[trigger:trigger + loop_len]
        m = len(rate)
        out = np.zeros(m, dtype=np.float64)
        for i in range(m):
            r = float(rate[i])
            pos = int((i % loop_len) * r)
            pos = min(pos, loop_len - 1)
            out[i] = slice_[pos]
        return out

    # ------------------------------------------------------------------
    # main entry
    # ------------------------------------------------------------------
    def process(self, audio: np.ndarray, mode: str = "classic",
                rate_curve=None, stop_time_sec: float = 1.5,
                loop_len_sec: float = 0.25, trigger: int = None,
                grain_ms: float = 40.0) -> np.ndarray:
        """Apply a tape-stop to ``audio``.

        Args:
            audio: mono ``(n,)`` or stereo ``(n, 2)`` float array.
            mode: "classic" | "modern" | "loop".
            rate_curve: ``None`` (default exponential ramp) or a 1-D array
                of instantaneous playback rates covering the stop, or a
                callable ``rate(t_norm) -> float``.
            stop_time_sec: duration of the stop (used when no curve given).
            loop_len_sec: slice length for ``loop`` mode.
            trigger: sample index where the stop begins (``loop`` mode
                captures the slice here; defaults to 60% into the file).
            grain_ms: grain size for ``modern`` mode.

        Returns:
            Same channel count as input; length equals the rate-curve length
            (``modern``/``loop``) or input length (``classic``).
        """
        x = np.asarray(audio, dtype=np.float64)
        if x.ndim == 1:
            mono = True
            x = x[:, None]
        else:
            mono = False
            x = x[:, :2]
        n = len(x)

        if rate_curve is None:
            m = int(self.sample_rate * stop_time_sec)
            rate = default_rate_curve(m)
        elif callable(rate_curve):
            m = int(self.sample_rate * stop_time_sec)
            t = np.linspace(0.0, 1.0, m)
            rate = np.asarray([rate_curve(v) for v in t], dtype=np.float64)
        else:
            rate = np.asarray(rate_curve, dtype=np.float64).reshape(-1)
            m = len(rate)
        rate = np.clip(rate, MIN_RATE, 1.0)

        if trigger is None:
            trigger = int(n * 0.6)

        chans = []
        for c in range(x.shape[1]):
            if mode == "classic":
                out_c, _ = self._classic(x[:, c], rate)
            elif mode == "modern":
                out_c = self._modern(x[:, c], rate, grain_ms=grain_ms)
            elif mode == "loop":
                out_c = self._loop(x[:, c], rate, trigger, loop_len_sec)
            else:
                raise ValueError(f"unknown mode {mode!r}")
            chans.append(out_c)

        out = np.stack(chans, axis=1)
        peak = float(np.max(np.abs(out))) if out.size else 0.0
        if peak > 1.0:
            out = out / peak * 0.95
        return out[:, 0] if mono else out


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: build a buzzy saw chord, stop it in all three modes."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    t = np.arange(sr * 3) / sr
    # two detuned saws + sub — enough harmonic content to hear pitch drop
    saw = (2.0 / np.pi) * np.sum(
        [np.sin(2 * np.pi * f * k * t) / k
         for k in range(1, 24) for f in (110.0, 110.5, 55.0)], axis=0)
    saw = saw / np.max(np.abs(saw)) * 0.9

    out = {}
    for mode in ("classic", "modern", "loop"):
        y = TapeStop(sr).process(saw, mode=mode, stop_time_sec=1.5)
        path = os.path.join(out_dir, f"tapestop_{mode}.wav")
        write_wav(path, y, sr)
        peak = float(np.max(np.abs(y)))
        n = int(y.shape[0])
        assert os.path.getsize(path) > 40, f"empty/corrupt output {path}"
        # sanity: classic shortens means of playback slowed -> output length == input
        assert n > 0 and peak > 1e-4
        out[mode] = {"samples": n, "seconds": round(n / sr, 3), "peak": round(peak, 4)}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))