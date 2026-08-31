"""Sample slicer with auto tempo/pitch detection — Bitwig Studio 6.1 Sampler logic.

Replicable logic from the Bitwig Studio 6.1 sampler overhaul (Sound On Sound
2026-08): automatic tempo and pitch detection, automatic slicing of a
sample into regions at detected onsets, multiple play modes per slice, and
slice-trigger mapping for drum-pad style playback.

What is replicated here (all self-contained numpy — no librosa required):
- ``auto_tempo``: autocorrelation of the spectral energy envelope to
  estimate BPM (period of the energy peaks -> tempo).
- ``auto_pitch``: autocorrelation of the waveform to estimate fundamental
  frequency (pitch detection).
- ``detect_onsets``: spectral-flux onset detection (frame-wise difference
  of magnitude spectra, thresholded + local maxima).
- ``Slice`` / ``SampleSlicer``: slice audio at onsets, then render each
  slice in several play modes — ``oneshot``, ``loop``, ``forward``,
  ``reverse``, ``pingpong`` — with optional pitch (rate) per slice, the
  classic sampler play-mode set.
- ``render_grid``: place slices on a step grid (16 steps) for drum-pad
  style sequencing of the sliced sample.

Not replicated: Bitwig's grid UI, the multisample editor, audio editor
warping (phase-vocoder time-stretch), granular/microloop modes (proprietary).

Usage:
    from sound.generators.sample_slicer import SampleSlicer, auto_tempo, auto_pitch

    slicer = SampleSlicer(sr=44100)
    onsets = slicer.detect_onsets(audio)
    slices = slicer.slice_at(audio, onsets)
    out = slicer.render_grid(slices, steps=16, mode="oneshot", rate=1.0)
"""

from typing import List, Optional, Tuple

import numpy as np

__all__ = ["SampleSlicer", "Slice", "auto_tempo", "auto_pitch"]


def _energy_envelope(audio: np.ndarray, sr: int, hop: int = 512) -> np.ndarray:
    """Framed RMS energy envelope (used for tempo autocorrelation)."""
    n = len(audio)
    frames = max(1, n // hop)
    env = np.zeros(frames)
    for i in range(frames):
        seg = audio[i * hop:(i + 1) * hop]
        env[i] = np.sqrt(np.mean(seg ** 2)) if len(seg) else 0.0
    env -= env.mean()
    return env


def auto_tempo(audio: np.ndarray, sr: int,
               bpm_range: Tuple[float, float] = (60.0, 200.0)) -> float:
    """Estimate tempo (BPM) from audio via envelope autocorrelation.

    Args:
        audio: Mono audio array.
        sr: Sample rate.
        bpm_range: (min, max) BPM to search.

    Returns:
        Estimated BPM (rounded to 1 decimal). Returns 0.0 if no clear peak.
    """
    env = _energy_envelope(audio, sr)
    if env.std() < 1e-9:
        return 0.0
    hop = 512
    # autocorrelation of the envelope
    n = len(env)
    ac = np.correlate(env, env, mode="full")[n - 1:]
    # search lags that map to the BPM range (lag in frames -> seconds)
    best_bpm, best_val = 0.0, -1.0
    min_bpm, max_bpm = bpm_range
    for lag in range(2, min(n, int(60.0 * sr / (hop * min_bpm)))):
        t = lag * hop / sr
        if t <= 0:
            continue
        bpm = 60.0 / t
        if min_bpm <= bpm <= max_bpm and ac[lag] > best_val:
            best_val = ac[lag]
            best_bpm = bpm
    return round(best_bpm, 1)


def auto_pitch(audio: np.ndarray, sr: int,
               freq_range: Tuple[float, float] = (40.0, 2000.0)) -> float:
    """Estimate fundamental frequency (Hz) via waveform autocorrelation.

    Args:
        audio: Mono audio array.
        sr: Sample rate.
        freq_range: (min, max) frequency to search.

    Returns:
        Estimated fundamental in Hz, or 0.0 if no clear peak.
    """
    x = audio - audio.mean()
    if x.std() < 1e-9:
        return 0.0
    n = len(x)
    ac = np.correlate(x, x, mode="full")[n - 1:]
    min_lag = max(1, int(sr / freq_range[1]))
    max_lag = min(n - 1, int(sr / freq_range[0]))
    best_f, best_val = 0.0, -1.0
    for lag in range(min_lag, max_lag):
        if ac[lag] > best_val:
            best_val = ac[lag]
            best_f = sr / lag
    return float(round(best_f, 1))


class Slice:
    """A region of a source sample (start/end sample indices)."""

    __slots__ = ("start", "end")

    def __init__(self, start: int, end: int):
        self.start = int(start)
        self.end = int(end)

    @property
    def length(self) -> int:
        return max(0, self.end - self.start)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Slice({self.start}:{self.end})"


class SampleSlicer:
    """Slice a sample at detected onsets and render slices in play modes.

    Parameters
    ----------
    sample_rate : int
        Sampling rate of the audio.
    fft_size : int
        FFT size for spectral-flux onset detection.
    hop : int
        Hop size (samples) for onset detection frames.
    """

    def __init__(self, sample_rate: int = 44100, fft_size: int = 1024, hop: int = 256):
        self.sr = sample_rate
        self.fft_size = fft_size
        self.hop = hop

    # -- detection ---------------------------------------------------------- #
    def detect_onsets(self, audio: np.ndarray,
                      threshold: float = 0.5) -> np.ndarray:
        """Spectral-flux onset detection.

        Computes per-frame magnitude spectra, takes the positive half-wave
        difference between consecutive frames (spectral flux), then picks
        local maxima above ``threshold * max`` as onsets (sample indices).

        Args:
            audio: Mono audio array.
            threshold: Relative flux threshold (0..1) for peak picking.

        Returns:
            Sorted numpy array of onset sample indices.
        """
        audio = np.asarray(audio, dtype=float)
        n = len(audio)
        fft = self.fft_size
        hop = self.hop
        n_frames = max(1, (n - fft) // hop)
        flux = np.zeros(n_frames)
        prev_mag = np.zeros(fft // 2 + 1)
        for i in range(n_frames):
            seg = audio[i * hop:i * hop + fft]
            if len(seg) < fft:
                seg = np.pad(seg, (0, fft - len(seg)))
            win = seg * np.hanning(fft)
            mag = np.abs(np.fft.rfft(win))
            flux[i] = np.sum(np.maximum(0.0, mag - prev_mag))
            prev_mag = mag
        peak = flux.max() if flux.size else 0.0
        if peak <= 1e-9:
            return np.array([0], dtype=int)
        thr = peak * threshold
        onsets = []
        for i in range(1, n_frames - 1):
            if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] > flux[i + 1]:
                onsets.append(i * hop)
        if not onsets:
            onsets = [0]
        if onsets[0] != 0:
            onsets.insert(0, 0)
        return np.asarray(onsets, dtype=int)

    def slice_at(self, audio: np.ndarray, onsets: np.ndarray) -> List[Slice]:
        """Cut audio into slices at the given onset sample indices.

        Args:
            audio: Mono audio array.
            onsets: Onset sample indices (from ``detect_onsets``).

        Returns:
            List of Slice regions covering [0, len(audio)).
        """
        audio = np.asarray(audio, dtype=float)
        pts = sorted(set(int(o) for o in onsets if 0 <= o < len(audio)))
        if not pts:
            return [Slice(0, len(audio))]
        slices = []
        for i, s in enumerate(pts):
            e = pts[i + 1] if i + 1 < len(pts) else len(audio)
            slices.append(Slice(s, e))
        return slices

    # -- play modes --------------------------------------------------------- #
    def render_slice(self, audio: np.ndarray, sl: Slice,
                     mode: str = "oneshot",
                     rate: float = 1.0, max_dur: float = 2.0) -> np.ndarray:
        """Render a slice in a play mode, optionally pitch-shifted by ``rate``.

        Args:
            audio: Source audio array.
            sl: Slice region.
            mode: ``oneshot`` (play once), ``loop`` (repeat), ``forward``
                (same as oneshot), ``reverse`` (play backwards), ``pingpong``
                (forward then back, looped).
            rate: Playback rate multiplier (2.0 = octave up). Affects length
                and pitch via resampling (time-stretch-free).
            max_dur: Cap on rendered output length in seconds.

        Returns:
            Rendered mono audio (float32).
        """
        seg = np.asarray(audio[sl.start:sl.end], dtype=float)
        if len(seg) == 0:
            return np.zeros(0, dtype=np.float32)
        max_n = int(max_dur * self.sr)
        if rate != 1.0:
            idx = np.arange(0, len(seg), rate, dtype=float)
            idx = np.clip(idx, 0, len(seg) - 1)
            seg = np.interp(idx, np.arange(len(seg)), seg)
        if mode in ("oneshot", "forward"):
            out = seg
        elif mode == "reverse":
            out = seg[::-1]
        elif mode == "loop":
            reps = int(np.ceil(max_n / max(1, len(seg))))
            out = np.tile(seg, reps)
        elif mode == "pingpong":
            fwd = seg
            bwd = seg[::-1]
            cycle = np.concatenate([fwd, bwd])
            reps = int(np.ceil(max_n / max(1, len(cycle))))
            out = np.tile(cycle, reps)
        else:
            raise ValueError(f"unknown play mode {mode!r}")
        return out[:max_n].astype(np.float32)

    def render_grid(self, audio: np.ndarray, slices: Optional[List[Slice]] = None,
                    steps: int = 16, mode: str = "oneshot",
                    rate: float = 1.0, step_len_sec: float = 0.125) -> np.ndarray:
        """Place slices on a step grid (drum-pad style slice sequencing).

        Slices are assigned round-robin to the first ``len(slices)`` steps;
        remaining steps are silent. This mirrors a 16-pad sampler layout
        where each slice maps to a pad/step.

        Args:
            audio: Source audio array.
            slices: Slice list (defaults to auto-detect + slice).
            steps: Number of steps in the grid.
            mode: Play mode per slice.
            rate: Playback rate multiplier.
            step_len_sec: Length of each step in seconds.

        Returns:
            Mixed mono audio (float32).
        """
        if slices is None:
            slices = self.slice_at(audio, self.detect_onsets(audio))
        step_n = int(step_len_sec * self.sr)
        out_len = steps * step_n
        out = np.zeros(out_len)
        for i, sl in enumerate(slices):
            if i >= steps:
                break
            s0 = i * step_n
            chunk = self.render_slice(audio, sl, mode=mode, rate=rate,
                                      max_dur=step_len_sec)
            c = min(step_n, len(chunk))
            out[s0:s0 + c] += chunk[:c]
        return out.astype(np.float32)


def demo() -> str:
    """Synthesize a rhythmic test signal and slice it."""
    sr = 22050
    dur = 2.0
    n = int(dur * sr)
    t = np.arange(n) / sr
    # percussive test: decaying noise bursts every 0.375 s (160 BPM)
    audio = np.zeros(n)
    for start in np.arange(0, dur, 0.375):
        i0 = int(start * sr)
        burst = np.random.default_rng(int(start * 100)).uniform(-1, 1, int(0.05 * sr))
        burst *= np.exp(-np.arange(len(burst)) / (0.015 * sr))
        audio[i0:i0 + len(burst)] += burst
    slicer = SampleSlicer(sample_rate=sr)
    onsets = slicer.detect_onsets(audio)
    slices = slicer.slice_at(audio, onsets)
    grid = slicer.render_grid(audio, slices, steps=16, mode="oneshot")
    bpm = auto_tempo(audio, sr)
    return (f"onsets={len(onsets)} slices={len(slices)} "
            f"tempo~{bpm}bpm grid_rms={np.sqrt(np.mean(grid**2)):.3f}")


if __name__ == "__main__":
    print(demo())
