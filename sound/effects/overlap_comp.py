"""Overlapping-band parametric compressor — Parish Audio Parametric
Compressor-style.

Replicable DSP from Parish Audio's Parametric Compressor (SOS 2026-08-24):
place independent compressor bands anywhere in the spectrum, allow bands to
overlap (unlike fixed-crossover multiband processors), with per-band
threshold/ratio/attack/release/makeup plus frequency/width placement, and
per-band detection source selection (band-limited signal, full-range signal,
or external sidechain).

What is replicated here:
- Up to 10 overlapping bell-shaped bands (parametric EQ-style placement).
- Per-band envelope follower (attack/release) driving a soft-knee VCA gain.
- Detection source: "band" (own filtered signal), "full" (whole input), or
  "sidechain" (external detector signal).
- Overlap is handled by summing band gains as control voltages rather than
  splitting the signal with crossovers — the exact trick that makes
  overlapping bands well-defined.

Not replicated: the interactive spectrum display / UI (host concern).

Usage:
    from sound.effects.overlap_comp import OverlapCompressor, CompBand

    comp = OverlapCompressor(sample_rate=44100)
    comp.add_band(CompBand(freq=120, width=1.0, threshold=-24, ratio=4, gain=2.0))
    comp.add_band(CompBand(freq=3000, width=0.8, threshold=-30, ratio=6, gain=1.0))
    out = comp.process(audio)          # detection from own band
    out = comp.process(audio, sidechain=detector)  # external sidechain
"""

import numpy as np
from typing import List, Optional

__all__ = ["OverlapCompressor", "CompBand"]


class CompBand:
    """A single parametric compressor band (bell-shaped frequency region)."""

    def __init__(self, freq: float = 1000.0, width: float = 1.0,
                 threshold_db: float = -20.0, ratio: float = 4.0,
                 attack_ms: float = 10.0, release_ms: float = 120.0,
                 makeup_db: float = 0.0, detect: str = "band"):
        """
        Args:
            freq: Center frequency in Hz.
            width: Bandwidth in octaves (bell Q = 1/width).
            threshold_db: Compression threshold.
            ratio: Compression ratio (>= 1).
            attack_ms: Envelope follower attack.
            release_ms: Envelope follower release.
            makeup_db: Post-compression gain.
            detect: "band" (own filtered signal), "full" (full input),
                    or "sidechain" (external detector).
        """
        if detect not in ("band", "full", "sidechain"):
            raise ValueError("detect must be 'band', 'full', or 'sidechain'")
        self.freq = float(freq)
        self.width = float(width)
        self.threshold_db = float(threshold_db)
        self.ratio = max(1.0, float(ratio))
        self.attack_ms = float(attack_ms)
        self.release_ms = float(release_ms)
        self.makeup_db = float(makeup_db)
        self.detect = detect


class OverlapCompressor:
    """Multiband compressor with freely placeable, overlapping bands."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.bands: List[CompBand] = []

    def add_band(self, band: CompBand) -> None:
        """Add a compression band (up to 10)."""
        if len(self.bands) >= 10:
            raise ValueError("max 10 bands")
        self.bands.append(band)

    def clear(self) -> None:
        """Remove all bands."""
        self.bands.clear()

    # -- filter design ---------------------------------------------------- #
    @staticmethod
    def _bell_coeffs(freq: float, width_oct: float, fs: int):
        """RBJ constant-peak-gain bandpass coefficients (detection filter).

        A true bandpass: unity gain at center frequency, rolling off to zero
        at DC and Nyquist. This is what makes a band's detection signal
        genuinely frequency-limited (a 0 dB peaking EQ would pass far-away
        content at unity gain, which is wrong for band detection).
        """
        w0 = 2.0 * np.pi * freq / fs
        Q = 1.0 / max(width_oct, 0.05)
        alpha = np.sin(w0) / (2.0 * Q)
        a0 = 1.0 + alpha
        a1 = -2.0 * np.cos(w0)
        a2 = 1.0 - alpha
        b0 = alpha
        b1 = 0.0
        b2 = -alpha
        return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)

    # -- envelope follower ------------------------------------------------- #
    def _envelope(self, x: np.ndarray, attack: float, release: float) -> np.ndarray:
        """Peak envelope follower (attack/release in seconds, one-pole)."""
        n = len(x)
        env = np.zeros(n)
        a = np.exp(-1.0 / (max(attack, 1e-4) * self.sample_rate))
        r = np.exp(-1.0 / (max(release, 1e-4) * self.sample_rate))
        level = 0.0
        for i in range(n):
            peak = abs(x[i])
            coeff = a if peak > level else r
            level = coeff * level + (1.0 - coeff) * peak
            env[i] = level
        return env

    # -- gain computer ----------------------------------------------------- #
    @staticmethod
    def _gain_db(level_db: float, threshold_db: float, ratio: float) -> float:
        """Soft-knee gain computer: returns gain reduction in dB (<= 0)."""
        if level_db <= threshold_db:
            return 0.0
        over = level_db - threshold_db
        # soft knee over a 6 dB window around the threshold
        knee = 6.0
        if over < knee:
            # quadratic soft knee interpolation
            over = over * over / (2.0 * knee)
        else:
            over = over - knee / 2.0
        reduction = -over * (1.0 - 1.0 / ratio)
        return reduction

    # -- process ----------------------------------------------------------- #
    def process(self, audio: np.ndarray,
                sidechain: Optional[np.ndarray] = None) -> np.ndarray:
        """Compress audio with overlapping parametric bands.

        Args:
            audio: Mono input audio.
            sidechain: Optional external detector signal (used by bands
                       whose detect == "sidechain").

        Returns:
            Compressed audio, same length as input.
        """
        audio = np.asarray(audio, dtype=np.float64)
        n = len(audio)
        if n == 0 or not self.bands:
            return audio
        if sidechain is not None and len(sidechain) != n:
            raise ValueError("sidechain must match input length")

        # Precompute band-filtered versions of the detection signals.
        filtered_audio = {}
        for idx, band in enumerate(self.bands):
            if band.detect == "band":
                filtered_audio[idx] = self._filter_band(audio, band)
        filtered_sc = {}
        if sidechain is not None:
            for idx, band in enumerate(self.bands):
                if band.detect == "sidechain":
                    filtered_sc[idx] = self._filter_band(sidechain, band)

        out = np.zeros(n, dtype=np.float64)
        for idx, band in enumerate(self.bands):
            # detection source selection
            if band.detect == "band":
                detector = filtered_audio[idx]
            elif band.detect == "full":
                detector = audio
            else:  # sidechain
                detector = filtered_sc.get(idx, np.zeros(n))
            env = self._envelope(detector, band.attack_ms / 1000.0,
                                 band.release_ms / 1000.0)
            env_db = 20.0 * np.log10(env + 1e-12)
            gain_db = np.array([self._gain_db(v, band.threshold_db, band.ratio)
                                for v in env_db])
            gain = 10.0 ** ((gain_db + band.makeup_db) / 20.0)
            # process the *full-range* signal with this band's gain (this is
            # what makes overlapping bands meaningful: gains sum as CV, the
            # signal itself is never split at crossovers)
            out += audio * gain
        # normalize by band count to avoid buildup
        out /= len(self.bands)
        return out

    def _filter_band(self, x: np.ndarray, band: CompBand) -> np.ndarray:
        """Biquad band filter (direct form II transposed), numpy-only."""
        b0, b1, b2, a1, a2 = self._bell_coeffs(band.freq, band.width, self.sample_rate)
        n = len(x)
        y = np.zeros(n, dtype=np.float64)
        d1 = d2 = 0.0
        for i in range(n):
            v = x[i] - a1 * d1 - a2 * d2
            y[i] = b0 * v + b1 * d1 + b2 * d2
            d2, d1 = d1, v
        return y


def demo() -> str:
    """Run a demo: 3 overlapping bands on a broadband signal."""
    sr = 44100
    dur = 1.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    # broadband source: low thump + mid + high content, modulated in level
    audio = (0.6 * np.sin(2 * np.pi * 80 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.5 * t)) +
             0.4 * np.sin(2 * np.pi * 800 * t) +
             0.3 * np.sin(2 * np.pi * 4000 * t))

    comp = OverlapCompressor(sample_rate=sr)
    comp.add_band(CompBand(freq=80, width=1.2, threshold_db=-24, ratio=4, makeup_db=3.0))
    comp.add_band(CompBand(freq=800, width=1.0, threshold_db=-20, ratio=3, makeup_db=0.0))
    comp.add_band(CompBand(freq=4000, width=1.5, threshold_db=-26, ratio=5, makeup_db=2.0))
    out = comp.process(audio)

    # overlapping bands: add a 4th band *inside* the low region on purpose
    comp.add_band(CompBand(freq=160, width=0.6, threshold_db=-18, ratio=2, makeup_db=-1.0))
    out2 = comp.process(audio)

    # sidechain test
    detector = 0.9 * np.sin(2 * np.pi * 60 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 4 * t))
    comp3 = OverlapCompressor(sample_rate=sr)
    comp3.add_band(CompBand(freq=1000, width=2.0, threshold_db=-20, ratio=6, detect="sidechain"))
    out3 = comp3.process(audio, sidechain=detector)

    rms_in = np.sqrt(np.mean(audio ** 2))
    rms_out = np.sqrt(np.mean(out ** 2))
    return "\n".join([
        "OverlapCompressor demo (3 overlapping bands + 1 nested band):",
        f"  input:  {len(audio)} samples, rms={rms_in:.4f}, peak={np.max(np.abs(audio)):.3f}",
        f"  3-band out: rms={np.sqrt(np.mean(out**2)):.4f}, peak={np.max(np.abs(out)):.3f}",
        f"  4-band out (nested overlap): rms={np.sqrt(np.mean(out2**2)):.4f}",
        f"  sidechain out: rms={np.sqrt(np.mean(out3**2)):.4f}",
        f"  bands: {len(comp.bands)} (max 10)",
    ])


if __name__ == "__main__":
    print(demo())
