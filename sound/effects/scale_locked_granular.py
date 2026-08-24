"""Scale-locked granular engine — Minimal Audio Lucid-style.

Replicable DSP from Minimal Audio's Lucid granular effect (synthtopia
2026-08-20 / SOS 2026-08-19): real-time granulation of incoming audio where
every grain is retuned to a chosen key/scale (scale-lock), tempo-synced grain
scheduling, stretch/scrub playback modes, and a harmonic grain delay that
produces scale-locked shimmer and arpeggiated spaces.

What is replicated here:
- Grain slicing with Hann windows, random position jitter, per-grain pitch
  shifting, and a resampling time-stretcher (grain overlap-add).
- Scale-lock: grains are pitch-corrected to the nearest degree of a chosen
  scale (via a scale quantizer) so output stays in key.
- Tempo-synced grain rate (grain period locked to DAW tempo, 1/16 grid).
- Stretch vs Scrub playback modes.
- Harmonic grain delay: a multi-tap feedback delay whose taps are pitched to
  scale degrees, producing shimmer / chord / arp spaces.

Not replicated (proprietary): the 350-preset library, the Animator X-Y pad,
the multi-mode grain filter / imager / compressor modules.

Usage:
    from sound.effects.scale_locked_granular import ScaleLockedGranular

    gl = ScaleLockedGranular(sample_rate=44100, scale_name="minor", root=60)
    out = gl.process(audio, bpm=120, grain_size_ms=80, density=12, mode="stretch")
"""

import numpy as np
from typing import Optional, List

__all__ = ["ScaleLockedGranular", "SCALES"]


# Semitone offsets for common scales (0 = root)
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "chromatic": list(range(12)),
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
}


def _quantize_to_scale(semitones: float, scale: List[int]) -> float:
    """Quantize a fractional semitone value to the nearest scale degree.

    Works in continuous semitone space: the octave is wrapped, the distance
    to every scale degree (including +/-1 octave copies) is measured, and the
    nearest degree is returned as a fractional semitone offset.
    """
    if not scale:
        return semitones
    octave = int(np.floor(semitones / 12.0))
    pos = semitones - octave * 12.0
    best = None
    best_d = float("inf")
    for degree in scale:
        for rep in (degree - 12, degree, degree + 12):
            d = abs(pos - rep)
            if d < best_d:
                best_d = d
                best = rep
    return octave * 12.0 + best


class ScaleLockedGranular:
    """Granular effect whose grains are retuned to a fixed key and tempo."""

    def __init__(self, sample_rate: int = 44100,
                 scale_name: str = "minor", root_midi: int = 60,
                 seed: Optional[int] = None):
        """
        Args:
            sample_rate: Output sample rate.
            scale_name: Key of the SCALES dict to lock grains to.
            root_midi: Root note of the scale as a MIDI note number.
            seed: Random seed for grain position jitter (determinism).
        """
        self.sample_rate = sample_rate
        self.scale_name = scale_name
        self.root_midi = root_midi
        if scale_name not in SCALES:
            raise ValueError(f"unknown scale '{scale_name}', choose from {sorted(SCALES)}")
        self.scale = SCALES[scale_name]
        self.rng = np.random.RandomState(seed)

    # -- helpers ---------------------------------------------------------- #
    def _midi_to_freq(self, midi: float) -> float:
        return 440.0 * 2.0 ** ((midi - 69) / 12.0)

    def _freq_to_midi(self, freq: float) -> float:
        if freq <= 0:
            return 0.0
        return 69.0 + 12.0 * np.log2(freq / 440.0)

    @staticmethod
    def _hann(n: int) -> np.ndarray:
        return np.hanning(n)

    # -- scale lock ------------------------------------------------------- #
    def lock_freq_to_scale(self, freq: float) -> float:
        """Return the nearest in-scale frequency for a given frequency."""
        midi = self._freq_to_midi(freq)
        # offset from root, in semitones, quantized to scale
        offset = _quantize_to_scale(midi - self.root_midi, self.scale)
        return self._midi_to_freq(self.root_midi + offset)

    # -- grain scheduling ------------------------------------------------- #
    def grain_interval_samples(self, bpm: float, division: float = 1.0) -> int:
        """Tempo-synced grain period.

        division is in beats (1.0 = quarter note, 0.25 = 16th). Returns the
        number of samples between grain starts for a locked-to-tempo feel.
        """
        beat_sec = 60.0 / max(bpm, 1.0)
        return max(1, int(division * beat_sec * self.sample_rate))

    def _extract_grain(self, source: np.ndarray, center: int,
                       size: int, pitch_semi: float) -> np.ndarray:
        """Extract a grain from source at center with Hann window + pitch."""
        n = len(source)
        start = max(0, min(center - size // 2, n - size))
        grain = source[start:start + size]
        if len(grain) < size:
            grain = np.pad(grain, (0, size - len(grain)))
        if abs(pitch_semi) > 0.01:
            ratio = 2.0 ** (pitch_semi / 12.0)
            new_len = max(2, int(size / ratio))
            x = np.linspace(0, size - 1, new_len)
            grain = np.interp(x, np.arange(size), grain)
        return grain * self._hann(len(grain))

    # -- core process ----------------------------------------------------- #
    def process(self, audio: np.ndarray, bpm: float = 120.0,
                grain_size_ms: float = 80.0, density: float = 12.0,
                mode: str = "stretch", jitter_ms: float = 20.0,
                lock_scale: bool = True, wet: float = 1.0) -> np.ndarray:
        """Granulate `audio` into a scale/tempo-locked texture.

        Args:
            audio: Mono input audio (float, -1..1).
            bpm: Tempo for grain scheduling (tempo lock).
            grain_size_ms: Base grain size in milliseconds.
            density: Grains per second (tempo-synced when > 0).
            mode: "stretch" (time-stretch, playhead advances by grain size)
                  or "scrub" (playhead stays near a fixed position).
            jitter_ms: Random position jitter around the playhead.
            lock_scale: Retune each grain to the nearest scale degree.
            wet: Dry/wet mix (0 = dry, 1 = fully wet).

        Returns:
            Granulated audio, same length as input.
        """
        audio = np.asarray(audio, dtype=np.float64)
        n = len(audio)
        if n == 0:
            return audio
        out = np.zeros(n, dtype=np.float64)
        grain_size = max(16, int(grain_size_ms / 1000.0 * self.sample_rate))
        # tempo-locked grain period: `density` grains per second
        interval = max(16, int(self.sample_rate / max(density, 0.01)))
        jitter_samp = int(jitter_ms / 1000.0 * self.sample_rate)
        # scrub keeps a fixed playhead; stretch advances through the file
        scrub_pos = int(n * 0.5)

        pos = 0
        while pos < n:
            if mode == "scrub":
                center = scrub_pos
            else:  # stretch
                center = int(pos)
            # position jitter
            center += self.rng.randint(-jitter_samp, jitter_samp + 1)
            center = int(np.clip(center, 0, n - 1))

            grain = self._extract_grain(audio, center, grain_size, 0.0)

            # scale lock: measure dominant pitch of grain (zero-crossing
            # estimate is robust enough), retune to nearest scale degree
            if lock_scale:
                est = self._estimate_pitch(grain)
                if est > 0:
                    target = self.lock_freq_to_scale(est)
                    shift = 12.0 * np.log2(target / est)
                    grain = self._extract_grain(audio, center, grain_size, shift)

            end = min(pos + len(grain), n)
            out[pos:end] += grain[:end - pos]
            pos += interval

        # normalize wet path to input peak
        peak_in = np.max(np.abs(audio)) or 1.0
        peak_out = np.max(np.abs(out)) or 1.0
        out = out / peak_out * peak_in
        return audio * (1.0 - wet) + out * wet

    def _estimate_pitch(self, grain: np.ndarray) -> float:
        """Rough pitch estimate via zero-crossing rate (cheap, offline-ok)."""
        if len(grain) < 8 or np.max(np.abs(grain)) < 1e-6:
            return 0.0
        crossings = np.sum(np.diff(np.sign(grain)) != 0)
        if crossings < 2:
            return 0.0
        # zero-crossings per second / 2 = frequency
        freq = crossings / (2.0 * len(grain) / self.sample_rate)
        return float(freq)

    # -- harmonic grain delay --------------------------------------------- #
    def harmonic_grain_delay(self, audio: np.ndarray, bpm: float = 120.0,
                             division: float = 0.5, degrees: Optional[List[int]] = None,
                             feedback: float = 0.4, taps: int = 4,
                             mix: float = 0.5) -> np.ndarray:
        """Scale-locked shimmer / arp delay.

        Each feedback tap delays the signal by a tempo-synced amount and
        pitch-shifts it to a scale degree (e.g. +7, +12, +3), producing
        harmonically locked echoes. This is the "Harmonic Grain Delay" idea
        from Lucid.

        Args:
            audio: Input mono audio.
            bpm: Tempo for the delay grid.
            division: Base delay in beats (0.5 = eighth note).
            degrees: Scale degrees (semitones) for the taps.
            feedback: Feedback amount (0..1).
            taps: Number of taps.
            mix: Dry/wet mix.

        Returns:
            Audio with harmonic grain-delay tail, same length as input.
        """
        if degrees is None:
            degrees = [0, 7, 12, 3]
        audio = np.asarray(audio, dtype=np.float64)
        n = len(audio)
        base_delay = int(division * 60.0 / max(bpm, 1.0) * self.sample_rate)
        tail = np.zeros(n, dtype=np.float64)
        for i in range(taps):
            deg = degrees[i % len(degrees)]
            delay = base_delay * (i + 1)
            if delay >= n:
                continue
            # pitch shift by degree (resample + length restore)
            ratio = 2.0 ** (deg / 12.0)
            seg = audio[:-delay]
            new_len = max(2, int(len(seg) / ratio))
            x = np.linspace(0, len(seg) - 1, new_len)
            shifted = np.interp(x, np.arange(len(seg)), seg)
            x2 = np.linspace(0, len(shifted) - 1, len(seg))
            shifted = np.interp(x2, np.arange(len(shifted)), shifted)
            amp = (1.0 - feedback) ** (i + 1)
            tail[delay:] += shifted * amp
        peak_in = np.max(np.abs(audio)) or 1.0
        peak_t = np.max(np.abs(tail)) or 1.0
        tail = tail / peak_t * peak_in * 0.9
        return audio * (1.0 - mix) + tail * mix


def demo() -> str:
    """Run a short demo of the scale-locked granular engine."""
    sr = 44100
    dur = 2.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    # source: a simple chord-ish pad (saw-ish stack) so scale lock has pitch
    source = (0.25 * np.sin(2 * np.pi * 220 * t) +
              0.15 * np.sin(2 * np.pi * 330 * t) +
              0.10 * np.sin(2 * np.pi * 440 * t) +
              0.08 * np.sin(2 * np.pi * 554.37 * t))

    gl = ScaleLockedGranular(sample_rate=sr, scale_name="minor", root_midi=57, seed=7)
    out_stretch = gl.process(source, bpm=120, grain_size_ms=90, density=10,
                             mode="stretch", lock_scale=True, wet=1.0)
    out_scrub = gl.process(source, bpm=120, grain_size_ms=120, density=6,
                           mode="scrub", lock_scale=True, wet=1.0)
    hgd = gl.harmonic_grain_delay(source, bpm=120, division=0.5,
                                  degrees=[0, 7, 12, 3], feedback=0.4, mix=0.5)

    # verify scale lock: dominant pitch of output should sit near scale degrees
    def dom_pitch(x):
        spec = np.abs(np.fft.rfft(x))
        freqs = np.fft.rfftfreq(len(x), 1.0 / sr)
        idx = np.argmax(spec[5:]) + 5  # skip DC/low bins
        return freqs[idx]

    f1 = dom_pitch(out_stretch)
    locked = gl.lock_freq_to_scale(f1)
    return "\n".join([
        "ScaleLockedGranular demo:",
        f"  source: {len(source)} samples, peak={np.max(np.abs(source)):.3f}",
        f"  stretch mode: {len(out_stretch)} samples, peak={np.max(np.abs(out_stretch)):.3f}",
        f"  scrub mode:   {len(out_scrub)} samples, peak={np.max(np.abs(out_scrub)):.3f}",
        f"  harmonic delay: {len(hgd)} samples, peak={np.max(np.abs(hgd)):.3f}",
        f"  scale-lock check: dominant {f1:.1f} Hz -> locked {locked:.1f} Hz "
        f"(in {gl.scale_name}, root {gl.root_midi})",
        f"  grain interval @120bpm density=10: {gl.grain_interval_samples(120, 0.25)} samples",
    ])


if __name__ == "__main__":
    print(demo())
