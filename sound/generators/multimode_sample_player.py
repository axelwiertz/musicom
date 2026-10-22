"""Seven-mode sample playback engine — Elektron Model-TG firmware-mod style.

Replicable logic from the Synthtopia item "Free Firmware Mod Adds
'Incredible' Features To Elektron Model:Cycles" (2026-10-12): TinyGreg's
Model-TG alternate firmware adds a Sampler machine to any track with seven
playback modes — One shot, Loop, Slice, Granular, Stretch, Pluck and Wave
(wavetable) — slicing by equal size, transient detection or manual chopping,
plus "slide trigs" that glide any p-locked parameter from one trig to the
next, and a beat-repeat performance page.

What is replicated here (pure numpy, offline render):
- ``SevenModeSamplePlayer.play(audio, mode, ...)`` with all seven modes:
  - oneshot: play the sample once from the start.
  - loop: cycle a region of the sample.
  - slice: chop the sample (equal / transient / manual) and play the
    slices back in order with per-slice rate + gain (``slide_trigs``
    glides those trig values between consecutive slices).
  - granular: seeded grain cloud over a region (windowed overlap-add,
    jittered offsets, per-grain pitch by internal resample).
  - stretch: WSOLA-style time-stretch (cross-correlation-aligned
    overlap-add) that preserves pitch while changing duration.
  - pluck: Karplus-Strong plucked-string synthesis using the sample's
    own attack transient as the excitation.
  - wave: build a wavetable by fixed-length slicing of the sample and
    scan it with a phase accumulator (position sweep optional).
- ``slice_audio``: equal-size, spectral-flux transient and manual slicing.
- ``slide_trigs``: linear parameter glide between trig values (the
  Model-TG "slide trig" behaviour) — used for per-slice rate/gain.

Not replicated: the Elektron hardware, OS 1.13 internals, resampling of
tracks/mix/USB audio, the performance page beat-repeat and the 12 master
FX (those are device integration, not a sound-production primitive).

Usage:
    from sound.generators.multimode_sample_player import SevenModeSamplePlayer

    sp = SevenModeSamplePlayer(sample_rate=44100, seed=3)
    out = sp.play(audio, mode="stretch", factor=1.5)
    out = sp.play(audio, mode="wave", freq=220.0, dur_sec=2.0, n_frames=16)
"""

from __future__ import annotations

import random
from typing import List, Optional

import numpy as np

__all__ = ["SevenModeSamplePlayer", "slide_trigs"]

DEFAULT_SR = 44100


def slide_trigs(trigs: List[float], n_out: int) -> np.ndarray:
    """Linear glide between per-trig values (Model-TG "slide trig").

    Given ``len(trigs)`` step values, produce ``n_out`` samples where each
    trig value is held for ``n_out / len(trigs)`` samples and the transition
    to the next trig is a linear ramp (glide), exactly like p-locking a
    parameter and enabling slide.
    """
    if n_out <= 0:
        return np.zeros(0)
    if len(trigs) == 0:
        return np.zeros(n_out)
    if len(trigs) == 1:
        return np.full(n_out, float(trigs[0]))
    seg = n_out / len(trigs)
    out = np.zeros(n_out)
    for i in range(len(trigs)):
        a = trigs[i]
        b = trigs[(i + 1) % len(trigs)]
        i0 = int(round(i * seg))
        i1 = int(round((i + 1) * seg))
        i1 = min(i1, n_out)
        n = i1 - i0
        if n <= 0:
            continue
        ramp = np.linspace(a, b, n, endpoint=False)
        out[i0:i1] = ramp
    return out


class SevenModeSamplePlayer:
    """Offline seven-mode sample playback / processing engine.

    Args:
        sample_rate: audio sample rate in Hz.
        seed: RNG seed for granular jitter and other stochastic parts.
    """

    MODES = ("oneshot", "loop", "slice", "granular", "stretch", "pluck", "wave")

    def __init__(self, sample_rate: int = DEFAULT_SR, seed: int = 0):
        self.sample_rate = int(sample_rate)
        self.seed = int(seed)

    # ------------------------------------------------------------------
    # slicing
    # ------------------------------------------------------------------
    def slice_audio(self, audio: np.ndarray, method: str = "transient",
                    n_slices: int = 8, onsets: Optional[List[int]] = None,
                    flux_threshold: float = 0.35) -> List[np.ndarray]:
        """Chop ``audio`` into slices.

        Args:
            method: "equal" (n equal parts), "transient" (spectral-flux
                onset detection), "manual" (boundaries given by ``onsets``).
            n_slices: number of slices for "equal".
            onsets: slice boundary sample indices for "manual".
            flux_threshold: onset sensitivity for "transient" (0..1).

        Returns:
            List of 1-D slices (non-empty).
        """
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        n = len(x)
        if n == 0:
            return []
        if method == "equal":
            n_slices = max(1, int(n_slices))
            edges = np.linspace(0, n, n_slices + 1, dtype=int)
            return [x[edges[i]:edges[i + 1]] for i in range(n_slices)
                    if edges[i + 1] > edges[i]]
        if method == "manual":
            if not onsets:
                raise ValueError("manual slicing needs onsets")
            bounds = sorted(set(int(o) for o in onsets if 0 <= int(o) < n))
            edges = [0] + bounds + [n]
            return [x[edges[i]:edges[i + 1]] for i in range(len(edges) - 1)
                    if edges[i + 1] > edges[i]]
        # transient: spectral-flux onset detection (frame-wise magnitude diff)
        fft_size = 1024
        hop = 256
        win = np.hanning(fft_size)
        frames = []
        for i in range(0, n - fft_size, hop):
            seg = x[i:i + fft_size]
            if len(seg) < fft_size:
                break
            mag = np.abs(np.fft.rfft(seg * win))
            frames.append(mag)
        if len(frames) < 2:
            return [x]
        frames = np.array(frames)
        flux = np.maximum(frames[1:] - frames[:-1], 0.0).sum(axis=1)
        flux = flux / (flux.max() + 1e-12)
        # onsets: flux peaks above threshold, minimum distance = 1/8 of file
        min_dist = max(1, n // (8 * max(1, len(flux))))
        peaks = []
        for i, v in enumerate(flux):
            if v < flux_threshold:
                continue
            if peaks and i - peaks[-1] < min_dist:
                if v > flux[peaks[-1]]:
                    peaks[-1] = i
            else:
                peaks.append(i)
        edges = [0] + [int((p + 1) * hop) for p in peaks] + [n]
        return [x[edges[i]:edges[i + 1]] for i in range(len(edges) - 1)
                if edges[i + 1] > edges[i]]

    # ------------------------------------------------------------------
    # modes
    # ------------------------------------------------------------------
    def _oneshot(self, x: np.ndarray, rate: float = 1.0) -> np.ndarray:
        if abs(rate - 1.0) < 1e-6:
            return x.copy()
        n = len(x)
        m = max(1, int(n / rate))
        src = np.arange(m, dtype=np.float64) * rate
        src = np.minimum(src, n - 1)
        return np.interp(src, np.arange(n), x)

    def _loop(self, x: np.ndarray, loop_start: Optional[int] = None,
              loop_end: Optional[int] = None, times: Optional[int] = None,
              dur_sec: Optional[float] = None) -> np.ndarray:
        n = len(x)
        start = 0 if loop_start is None else int(np.clip(loop_start, 0, n - 1))
        end = n if loop_end is None else int(np.clip(loop_end, start + 1, n))
        loop = x[start:end]
        if len(loop) == 0:
            return np.zeros(0)
        m = int(self.sample_rate * dur_sec) if dur_sec is not None else None
        if m is not None:
            reps = int(np.ceil(m / len(loop)))
        else:
            reps = int(times) if times else 4
        out = np.tile(loop, reps)
        if m is not None:
            out = out[:m]
        return out

    def _slice(self, x: np.ndarray, method: str = "equal", n_slices: int = 8,
               onsets: Optional[List[int]] = None, order: Optional[List[int]] = None,
               rates: Optional[List[float]] = None,
               gains: Optional[List[float]] = None,
               gap_sec: float = 0.0) -> np.ndarray:
        slices = self.slice_audio(x, method=method, n_slices=n_slices,
                                  onsets=onsets)
        if not slices:
            return np.zeros(0)
        idx = list(range(len(slices)))
        if order is not None:
            idx = [int(i) % len(slices) for i in order]
        # slide trigs: glide rate/gain values across the trig sequence
        rate_curve = None
        if rates is not None:
            rate_curve = slide_trigs([float(r) for r in rates], len(idx))
        gain_curve = None
        if gains is not None:
            gain_curve = slide_trigs([float(g) for g in gains], len(idx))
        gap = int(self.sample_rate * gap_sec)
        pieces = []
        for k, i in enumerate(idx):
            seg = slices[i]
            r = 1.0 if rate_curve is None else float(rate_curve[k])
            g = 1.0 if gain_curve is None else float(gain_curve[k])
            if abs(r - 1.0) > 1e-6:
                seg = self._oneshot(seg, rate=r)
            pieces.append(seg * g)
            if gap:
                pieces.append(np.zeros(gap))
        return np.concatenate(pieces) if pieces else np.zeros(0)

    def _granular(self, x: np.ndarray, grain_ms: float = 80.0,
                  spacing_ms: float = 40.0, jitter: float = 0.5,
                  pitch: float = 1.0, start_frac: float = 0.0,
                  end_frac: float = 1.0, dur_sec: Optional[float] = None) -> np.ndarray:
        n = len(x)
        grain = max(32, int(self.sample_rate * grain_ms / 1000.0))
        hop = max(8, int(self.sample_rate * spacing_ms / 1000.0))
        lo = int(start_frac * n)
        hi = int(end_frac * n)
        hi = max(lo + grain, min(hi, n))
        rng = random.Random(self.seed)
        if dur_sec is None:
            m = n
        else:
            m = int(self.sample_rate * dur_sec)
        out = np.zeros(m + grain, dtype=np.float64)
        acc = np.zeros(m + grain, dtype=np.float64)
        win = np.hanning(grain)
        pos = lo
        while pos < hi and pos < m:
            # jittered grain start
            j = int(rng.uniform(-jitter, jitter) * grain)
            g0 = int(np.clip(pos + j, lo, hi - grain))
            seg = x[g0:g0 + grain]
            if len(seg) < grain:
                seg = np.pad(seg, (0, grain - len(seg)))
            if abs(pitch - 1.0) > 1e-6:
                src = np.arange(grain, dtype=np.float64) * pitch
                src = np.minimum(src, grain - 1)
                seg = np.interp(src, np.arange(grain), seg)
            out[pos:pos + grain] += seg * win
            acc[pos:pos + grain] += win
            pos += hop
        acc = np.maximum(acc, 1e-8)
        return out[:m] / acc[:m]

    def _stretch(self, x: np.ndarray, factor: float = 1.5,
                 grain: int = 1024, search: int = 128) -> np.ndarray:
        """WSOLA-lite time-stretch preserving pitch (Model-TG Stretch)."""
        n = len(x)
        if n <= grain:
            return x.copy()
        a_hop = grain // 2
        s_hop = max(1, int(round(a_hop * factor)))
        m = int(n * factor)
        out = np.zeros(m + grain, dtype=np.float64)
        acc = np.zeros(m + grain, dtype=np.float64)
        win = np.hanning(grain)
        a_pos = 0
        s_pos = 0
        prev_tail = np.zeros(grain // 2)
        while a_pos + grain <= n and s_pos + grain <= m:
            base = x[a_pos:a_pos + grain]
            # search for best-aligned analysis position
            best = 0
            best_corr = -1.0
            lo = max(0, a_pos - search)
            hi = min(n - grain, a_pos + search)
            for cand in range(lo, hi + 1, 8):
                seg = x[cand:cand + grain]
                corr = float(np.dot(seg[:grain // 2], prev_tail))
                if corr > best_corr:
                    best_corr = corr
                    best = cand - a_pos
            seg = x[a_pos + best:a_pos + best + grain]
            out[s_pos:s_pos + grain] += seg * win
            acc[s_pos:s_pos + grain] += win
            prev_tail = seg[grain // 2:]
            a_pos += a_hop
            s_pos += s_hop
        acc = np.maximum(acc, 1e-8)
        return out[:m] / acc[:m]

    def _pluck(self, x: np.ndarray, freq: float = 110.0, dur_sec: float = 2.0,
               damping: float = 0.5, exc_len: int = 512) -> np.ndarray:
        """Karplus-Strong pluck using the sample's attack as excitation."""
        n = len(x)
        if n == 0:
            return np.zeros(0)
        exc = x[:min(exc_len, n)].copy()
        if np.max(np.abs(exc)) < 1e-9:
            exc[0] = 1.0
        L = max(2, int(round(self.sample_rate / max(freq, 1.0))))
        m = int(self.sample_rate * dur_sec)
        out = np.zeros(m)
        buf = np.zeros(L)
        for i in range(m):
            if i < len(exc):
                out[i] = exc[i]
                buf[i % L] = exc[i]
            else:
                v = damping * 0.5 * (buf[(i - 1) % L] + buf[(i - 2) % L])
                out[i] = v
                buf[i % L] = v
        return out

    def _wave(self, x: np.ndarray, freq: float = 220.0, dur_sec: float = 2.0,
              n_frames: int = 16, sweep: float = 0.0) -> np.ndarray:
        """Wavetable scan: fixed-length slice frames -> phase-accumulator scan."""
        n = len(x)
        n_frames = max(2, int(n_frames))
        wave_len = max(64, n // n_frames)
        frames = []
        for i in range(n_frames):
            seg = x[i * wave_len:(i + 1) * wave_len]
            if len(seg) < wave_len:
                seg = np.pad(seg, (0, wave_len - len(seg)))
            seg = seg - seg.mean()
            peak = np.max(np.abs(seg)) + 1e-9
            frames.append(seg / peak * 0.8)
        wt = np.array(frames)  # (n_frames, wave_len)
        m = int(self.sample_rate * dur_sec)
        phase = np.cumsum(2.0 * np.pi * freq / self.sample_rate * np.ones(m))
        idx = (phase / (2.0 * np.pi) * wave_len).astype(np.int64) % wave_len
        if sweep > 0:
            frame_pos = np.linspace(0.0, n_frames - 1, m)
        else:
            frame_pos = np.full(m, 0.0)
        out = np.zeros(m)
        for k in range(m):
            f0 = int(frame_pos[k])
            f1 = min(f0 + 1, n_frames - 1)
            frac = frame_pos[k] - f0
            a = wt[f0, idx[k]]
            b = wt[f1, idx[k]]
            out[k] = a * (1 - frac) + b * frac
        return out

    # ------------------------------------------------------------------
    # main entry
    # ------------------------------------------------------------------
    def play(self, audio: np.ndarray, mode: str = "oneshot", **kw) -> np.ndarray:
        """Run one of the seven playback modes on ``audio``.

        Args:
            audio: mono 1-D float array (stereo is looped per-channel by
                the caller; the engine itself is mono).
            mode: oneshot | loop | slice | granular | stretch | pluck | wave.
            **kw: mode-specific kwargs, e.g. ``factor`` (stretch),
                ``freq``/``dur_sec`` (pluck, wave), ``grain_ms`` (granular),
                ``rates``/``gains`` (slice — with slide-trig glide).

        Returns:
            Rendered 1-D float array.
        """
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        if x.size == 0:
            raise ValueError("empty audio")
        if mode == "oneshot":
            out = self._oneshot(x, kw.get("rate", 1.0))
        elif mode == "loop":
            out = self._loop(x, kw.get("loop_start"), kw.get("loop_end"),
                             kw.get("times"), kw.get("dur_sec"))
        elif mode == "slice":
            out = self._slice(x, method=kw.get("method", "equal"),
                              n_slices=kw.get("n_slices", 8),
                              onsets=kw.get("onsets"),
                              order=kw.get("order"),
                              rates=kw.get("rates"),
                              gains=kw.get("gains"),
                              gap_sec=kw.get("gap_sec", 0.0))
        elif mode == "granular":
            out = self._granular(x, grain_ms=kw.get("grain_ms", 80.0),
                                 spacing_ms=kw.get("spacing_ms", 40.0),
                                 jitter=kw.get("jitter", 0.5),
                                 pitch=kw.get("pitch", 1.0),
                                 start_frac=kw.get("start_frac", 0.0),
                                 end_frac=kw.get("end_frac", 1.0),
                                 dur_sec=kw.get("dur_sec"))
        elif mode == "stretch":
            out = self._stretch(x, factor=kw.get("factor", 1.5))
        elif mode == "pluck":
            out = self._pluck(x, freq=kw.get("freq", 110.0),
                              dur_sec=kw.get("dur_sec", 2.0),
                              damping=kw.get("damping", 0.5),
                              exc_len=kw.get("exc_len", 512))
        elif mode == "wave":
            out = self._wave(x, freq=kw.get("freq", 220.0),
                             dur_sec=kw.get("dur_sec", 2.0),
                             n_frames=kw.get("n_frames", 16),
                             sweep=kw.get("sweep", 0.0))
        else:
            raise ValueError(f"unknown mode {mode!r}; choose from {self.MODES}")
        peak = float(np.max(np.abs(out))) if out.size else 0.0
        if peak > 1.0:
            out = out / peak * 0.95
        return out


def _test_signal(sr: int, dur: float = 3.0) -> np.ndarray:
    """Saw chord with a few click transients — enough texture for all modes."""
    t = np.arange(int(sr * dur)) / sr
    saw = np.zeros_like(t)
    for f in (110.0, 165.0, 220.0):
        for k in range(1, 16):
            saw += np.sin(2 * np.pi * f * k * t) / k
    saw = saw / np.max(np.abs(saw))
    # click transients every 0.5 s
    for i in range(6):
        at = int(i * 0.5 * sr)
        saw[at:at + 256] += 0.8 * np.hanning(256) * np.sign(np.random.RandomState(i).randn())
    return saw


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: run all seven modes on a synthetic sample, write WAVs."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    x = _test_signal(sr)
    sp = SevenModeSamplePlayer(sample_rate=sr, seed=5)

    calls = {
        "oneshot": dict(mode="oneshot"),
        "loop": dict(mode="loop", loop_start=int(0.5 * sr),
                     loop_end=int(1.5 * sr), dur_sec=2.0),
        "slice": dict(mode="slice", method="transient", rates=[1.0, 0.8, 1.2, 0.7],
                      gains=[1.0, 0.9, 1.1, 0.8]),
        "granular": dict(mode="granular", grain_ms=80.0, spacing_ms=40.0,
                         pitch=1.0, dur_sec=2.0),
        "stretch": dict(mode="stretch", factor=1.5),
        "pluck": dict(mode="pluck", freq=110.0, dur_sec=1.5),
        "wave": dict(mode="wave", freq=220.0, dur_sec=1.5, n_frames=16, sweep=1.0),
    }
    out = {}
    for name, kw in calls.items():
        y = sp.play(x, **kw)
        path = os.path.join(out_dir, f"mmplayer_{name}.wav")
        write_wav(path, y, sr)
        assert os.path.getsize(path) > 40, f"empty/corrupt {path}"
        assert y.size > 0 and float(np.max(np.abs(y))) > 1e-4, f"silent {name}"
        out[name] = {"samples": int(y.shape[0]),
                     "seconds": round(y.shape[0] / sr, 3),
                     "peak": round(float(np.max(np.abs(y))), 4)}
    # slide-trig glide sanity: cyclic glide 1.0 -> 0.5 -> 0.0 -> back to 1.0
    gl = slide_trigs([1.0, 0.5, 0.0], 12)
    assert abs(gl[0] - 1.0) < 1e-6, "glide must start at first trig value"
    assert gl[1] < gl[0], "glide must ramp downward through the trigs"
    assert gl[6] < gl[5], "second segment glides 0.5 -> 0.0"
    out["slide_trigs"] = [round(float(v), 4) for v in gl]
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
