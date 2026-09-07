"""Sub-harmonic bass generator — Penteo 8 Synthesized LFE style.

Replicable logic from Penteo 8 (Sound On Sound news, 2026-09-03): the
upmix/downmix suite added a "Synthesized LFE Sub-Harmonic Generator across
three frequency bands", each band independently mute-able and link-able.
The word *synthesized* matters: rather than pitch-shifting program audio,
the generator tracks the music's fundamental and *synthesizes* a clean
sub-octave tone that follows it, then steers it into the LFE band.

What is replicated here:
- **Per-frame pitch tracking** of the input (normalized autocorrelation in
  the 40..160 Hz range with parabolic lag interpolation), so the sub
  oscillator follows the bass line instead of sitting on one fixed pitch.
- **Three independent output bands** (default sub 20-60, low 60-120, mid
  120-240 Hz), each driven by the input band one octave above it
  (40-120 / 120-240 / 240-480 Hz).  Each band has its own depth (mix of
  synthesized sub into the band), gain, and mute — mirroring the
  "individually muted and linked" three-band UI.
- **Phase-continuous sub-octave oscillators**: for every pitched frame a
  sine at f0/2 is generated with phase accumulated across frames at the
  sub frequency, so consecutive frames join without clicks.
- **Octave-down + fifth** option (the classic sub-harmonic pedal sound,
  POG-style): adds a component at 3*f0/4 (a fifth above the sub-octave)
  at lower level for tone shaping.
- **Envelope follower per band** with fast attack / slow release so the
  synthesized sub swells and decays with the music rather than pumping.
- Optional second harmonic f0/4 of the sub for very deep material.

Not replicated: the full Penteo upmix/downmix DSP (phaseless decorrelation
across 62 formats, per-dimension decorrelation, surround divergence,
bit-exact 100% ITU downmix) and its licensed measurement data.

Reference (SoS 2026-09-03): "Synthesized LFE Sub-Harmonic Generator across
three frequency bands, each can be individually muted and linked."

Usage:
    from sound.effects.subharmonic import SubHarmonicGenerator, SubBand

    shg = SubHarmonicGenerator(sample_rate=44100)
    lfe = shg.process(bass_audio, depth=1.0)      # mono sub (LFE-style)
    shg.bands[1].muted = True                     # mute the 60-120 band
"""

from typing import List, Optional, Tuple

import numpy as np

__all__ = ["SubBand", "SubHarmonicGenerator", "pitch_frame", "demo"]


def _hann(n: int) -> np.ndarray:
    return 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(n) / max(n, 1))


def pitch_frame(frame: np.ndarray, sr: int,
                lo: float = 40.0, hi: float = 160.0) -> float:
    """Estimate the fundamental of one time-domain frame (Hz).

    Normalized autocorrelation on the band-limited frame; the ACF peak in
    the 40..160 Hz lag range gives the period (parabolic interpolation for
    sub-Hz accuracy).  Returns 0.0 when the frame is unpitched.
    """
    n = len(frame)
    x = frame - np.mean(frame)
    acf = np.correlate(x, x, mode="full")[n - 1:]
    lo_lag = max(1, int(sr / hi))
    hi_lag = min(n - 1, int(sr / lo))
    if hi_lag <= lo_lag:
        return 0.0
    seg = acf[lo_lag:hi_lag + 1] / max(acf[0], 1e-12)
    k = int(np.argmax(seg))
    if seg[k] < 0.3:  # weak periodicity -> unpitched frame
        return 0.0
    lag = float(lo_lag + k)
    if 0 < k < len(seg) - 1:
        a, b, c = seg[k - 1], seg[k], seg[k + 1]
        denom = a - 2.0 * b + c
        if abs(denom) > 1e-12:
            lag += 0.5 * (a - c) / denom
    return float(sr / lag)


class SubBand:
    """One output sub band (frequency range + gain + depth + mute).

    The band synthesizes sub content at [lo, hi] Hz from input content in
    [2*lo, 2*hi] Hz (one octave above).
    """

    def __init__(self, name: str, lo_hz: float, hi_hz: float,
                 gain: float = 1.0, depth: float = 1.0):
        self.name = name
        self.lo_hz = lo_hz
        self.hi_hz = hi_hz
        self.gain = gain
        self.depth = depth          # 0..1 sub-oscillator mix into the band
        self.muted = False

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return (f"SubBand({self.name}, {self.lo_hz:.0f}-{self.hi_hz:.0f} Hz, "
                f"gain={self.gain}, depth={self.depth})")


class SubHarmonicGenerator:
    """Pitch-tracked three-band sub-octave (LFE) synthesizer.

    Parameters
    ----------
    sample_rate : int
        Audio sample rate.
    frame_size : int
        Analysis frame size (pitch + band RMS measurement).
    hop : int
        Frame hop; also the sub-oscillator synthesis granularity.
    """

    def __init__(self, sample_rate: int = 44100, frame_size: int = 2048,
                 hop: int = 512):
        self.sr = int(sample_rate)
        self.frame_size = int(frame_size)
        self.hop = int(hop)
        # three LFE-style output bands (defaults mirror the product UI)
        self.bands: List[SubBand] = [
            SubBand("sub", 20.0, 60.0, gain=1.0, depth=1.0),
            SubBand("low", 60.0, 120.0, gain=0.8, depth=0.9),
            SubBand("mid", 120.0, 240.0, gain=0.5, depth=0.7),
        ]

    # -- analysis -----------------------------------------------------------
    def _bin_range(self, lo_hz: float, hi_hz: float) -> Tuple[int, int]:
        n = self.frame_size
        return (max(1, int(lo_hz * n / self.sr)),
                min(n // 2 - 1, int(hi_hz * n / self.sr) + 1))

    def analyze(self, audio: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """STFT + per-frame pitch track + per-frame band RMS.

        Returns (pitch, band_rms) where
          pitch[m]      = fundamental of frame m in Hz (0 = unpitched),
          band_rms[m, i]= RMS of frame m inside input band i
                          ([2*lo, 2*hi] of self.bands[i]).
        """
        x = np.asarray(audio, dtype=np.float64)
        if x.ndim > 1:
            x = np.mean(x, axis=1)
        n = self.frame_size
        n_frames = max(1, 1 + (len(x) - n) // self.hop)
        win = _hann(n)
        pitch = np.zeros(n_frames)
        band_rms = np.zeros((n_frames, len(self.bands)))
        for m in range(n_frames):
            s = m * self.hop
            frame = x[s:s + n]
            if len(frame) < n:
                frame = np.pad(frame, (0, n - len(frame)))
            pitch[m] = pitch_frame(frame, self.sr)
            spec = np.fft.rfft(frame * win)
            mag = np.abs(spec)
            for bi, band in enumerate(self.bands):
                k0, k1 = self._bin_range(band.lo_hz * 2.0,
                                         band.hi_hz * 2.0)
                e = float(np.sum(mag[k0:k1] ** 2))
                band_rms[m, bi] = np.sqrt(e) / n
        return pitch, band_rms

    # -- synthesis -----------------------------------------------------------
    def process(self, audio: np.ndarray, depth: Optional[float] = None,
                add_fifth: bool = False, sub_sub: bool = False) -> np.ndarray:
        """Synthesize a mono sub-octave (LFE-style) signal from the input.

        Parameters
        ----------
        audio : np.ndarray
            Mono or stereo input (stereo downmixed for analysis).
        depth : float, optional
            Master depth 0..1; scales each band's depth.
        add_fifth : bool
            Add the 3*f0/4 component (fifth above the sub-octave).
        sub_sub : bool
            Add the f0/4 component (two octaves down) at low level.

        Returns
        -------
        np.ndarray
            Mono float64 sub signal, same length as the downmixed input.
        """
        x = np.asarray(audio, dtype=np.float64)
        if x.ndim > 1:
            x = np.mean(x, axis=1)
        pitch, band_rms = self.analyze(x)
        n_out = len(x)
        out = np.zeros(n_out)
        hop = self.hop
        sr = self.sr
        # per-band phase of the sub oscillator (phase-continuous across
        # frames) and smoothed envelope state
        phase = np.zeros(len(self.bands))
        env = np.zeros(len(self.bands))
        att = np.exp(-1.0 / (0.005 * sr / hop))    # ~5 ms attack (per frame)
        rel = np.exp(-1.0 / (0.120 * sr / hop))    # ~120 ms release
        for m in range(len(pitch)):
            f0 = pitch[m]
            start = m * hop
            nseg = min(hop, n_out - start)
            if nseg <= 0:
                break
            tt = np.arange(nseg) / sr
            for bi, band in enumerate(self.bands):
                if band.muted or band.depth <= 0.0 or band.gain <= 0.0:
                    env[bi] *= rel
                    continue
                # band gate: the tracked pitch must sit one octave above
                # the band (input band [2*lo, 2*hi])
                if not (band.lo_hz * 2.0 <= f0 < band.hi_hz * 2.0):
                    env[bi] *= rel
                    continue
                # envelope follower on the input band RMS
                target = float(band_rms[m, bi])
                if target > env[bi]:
                    env[bi] += (target - env[bi]) * (1.0 - att)
                else:
                    env[bi] += (target - env[bi]) * (1.0 - rel)
                if env[bi] < 1e-6:
                    continue
                f_sub = f0 / 2.0
                d = band.depth * (depth if depth is not None else 1.0)
                # sub-octave sine, phase-continuous from the previous frame
                w = 2.0 * np.pi * f_sub / sr
                ph = phase[bi] + w * np.arange(nseg)
                seg = np.sin(ph)
                # tone shaping: fifth above sub-octave (3*f0/4)
                if add_fifth:
                    seg += 0.35 * np.sin(ph * 1.5)
                # very deep: two octaves down (f0/4)
                if sub_sub:
                    seg += 0.2 * np.sin(ph * 0.5)
                amp = env[bi] * d * band.gain * 2.0
                out[start:start + nseg] += seg * amp
                phase[bi] = (phase[bi] + w * hop) % (2.0 * np.pi)
        peak = np.max(np.abs(out))
        if peak > 1.0:
            out /= peak
        return out


def demo() -> None:
    """Sub-octave synthesis on a synthetic bass line; print evidence."""
    sr = 44100
    dur = 2.0
    parts = []
    for f0, seg_dur in ((55.0, 0.7), (110.0, 0.7), (82.41, 0.6)):
        n = int(sr * seg_dur)
        tt = np.arange(n) / sr
        parts.append(np.sin(2 * np.pi * f0 * tt)
                     + 0.5 * np.sin(2 * np.pi * 2 * f0 * tt)
                     + 0.25 * np.sin(2 * np.pi * 3 * f0 * tt))
    bass = np.concatenate(parts)
    t = np.arange(int(sr * dur)) / sr
    bass = bass[:len(t)] if len(bass) > len(t) else np.pad(
        bass, (0, len(t) - len(bass)))

    shg = SubHarmonicGenerator(sample_rate=sr)
    sub = shg.process(bass, depth=1.0)

    def band_energy(x, lo, hi):
        spec = np.abs(np.fft.rfft(x * _hann(len(x))))
        fr = np.fft.rfftfreq(len(x), 1.0 / sr)
        m = (fr >= lo) & (fr <= hi)
        return float(np.sum(spec[m] ** 2))

    e_20_60 = band_energy(sub, 20, 60)
    e_in_20_60 = band_energy(bass, 20, 60)
    # The source bass sits at 55/110/82 Hz + harmonics: very little energy
    # below 60 Hz.  The synthesized sub must put real energy at 27.5/41/55 Hz.
    print(f"source 20-60Hz energy: {e_in_20_60:.1f}")
    print(f"sub    20-60Hz energy: {e_20_60:.1f}  "
          f"(generated sub-octave content)")
    print(f"sub length={len(sub)} peak={np.max(np.abs(sub)):.3f} "
          f"rms={np.sqrt(np.mean(sub ** 2)):.3f}")
    # The generated sub must add real energy in the 20-60 band beyond what
    # the source already carries (its 55 Hz fundamental is in-band).
    assert e_20_60 > 2.0 * e_in_20_60

    # three independent bands + mutes: use a bass in the 120-240 input band
    # (fundamental 150 Hz -> sub-octave 75 Hz in the 'low' output band)
    hi_parts = []
    for f0, seg_dur in ((150.0, 0.6), (170.0, 0.6)):
        n = int(sr * seg_dur)
        tt = np.arange(n) / sr
        hi_parts.append(np.sin(2 * np.pi * f0 * tt))
    hi_bass = np.concatenate(hi_parts)
    hi_bass = np.pad(hi_bass, (0, max(0, len(bass) - len(hi_bass))))
    n0 = len(bass)
    shg.bands[1].muted = True
    subA = shg.process(hi_bass, depth=1.0)
    shg.bands[1].muted = False
    subB = shg.process(hi_bass, depth=1.0)
    changed = not np.allclose(subA[:n0], subB[:n0])
    print(f"muting 'low' band changes output (150 Hz bass): {changed}")
    assert changed
    # fifth + sub-sub modes produce extra low energy, still finite
    sub3 = shg.process(bass, depth=1.0, add_fifth=True, sub_sub=True)
    print(f"add_fifth+sub_sub: peak={np.max(np.abs(sub3)):.3f} "
          f"len={len(sub3)} finite={np.all(np.isfinite(sub3))}")
    print("  subharmonic demo OK")


if __name__ == "__main__":
    demo()
