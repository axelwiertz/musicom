# -*- coding: utf-8 -*-
"""
Impulse Response Designer — algorithmic IR synthesis toolbox.

Replicates the IR-design techniques from Convolution Playground
(loopop / Synthtopia 2026-10-01): ten ways to design an impulse response
without needing a real acoustic space.

Techniques implemented:
  - REVERSE_BLOOM    : reversed exponential decay → percussive attack
  - DRAWN_ECHOES     : sparse impulses at user-specified delays
  - CHORD_BODY       : sum of sine harmonics → pitched ring
  - FILTER_SWEEP     : frequency sweep (chirp) with envelope
  - VOWEL            : formant-shaped noise burst (vowel coloration)
  - SPECTRAL_DELAY   : frequency-dependent delay line impulse
  - RAIN             : dense pseudo-random impulse train
  - REVERB           : stochastic noise with exponential decay
  - METALLIC_BLOOM   : inharmonic partial sum (metallic/glass ring)
  - FM_BODY          : frequency-modulated carrier → complex ring

Each generator returns a 1-D numpy array (the IR) plus its sample rate.
All are suitable for convolution with an input signal via
scipy.signal.fftconvolve or numpy.convolve.

Usage:
    from sound.effects.ir_designer import design_ir
    ir, sr = design_ir("reverse_bloom", duration_s=0.5)
    # or list all recipes:
    from sound.effects.ir_designer import IR_RECIPES
"""

import numpy as np
from typing import Optional

# ---------------------------------------------------------------------------
# Recipe registry
# ---------------------------------------------------------------------------

IR_RECIPES = (
    "reverse_bloom", "drawn_echoes", "chord_body", "filter_sweep",
    "vowel", "spectral_delay", "rain", "reverb", "metallic_bloom", "fm_body"
)

# ---------------------------------------------------------------------------
# Core generators
# ---------------------------------------------------------------------------

def reverse_bloom_ir(
    duration_s: float = 0.3,
    decay_time_s: float = 0.05,
    sr: int = 44100,
    density: float = 1.0,
) -> np.ndarray:
    """Reverse-bloom IR: a sharp exponential decay whose envelope is reversed.

    The result is a quick attack transient with a rising (reversed) tail,
    creating a 'bloom' or 'inverse reverb' character.

    Parameters
    ----------
    duration_s : float
        Total IR length in seconds.
    decay_time_s : float
        Time constant of the underlying exponential decay (seconds).
    sr : int
        Sample rate.
    density : float
        Noise density factor (1.0 = full-spectrum noise, <1 blurs).

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    n = int(sr * duration_s)
    t = np.arange(n, dtype=np.float64) / sr
    # exponentially decaying noise burst
    noise = np.random.randn(n)
    if density < 1.0:
        # lowpass filter noise for lower density
        b = int((1.0 - density) * min(n // 4, 128))
        if b > 1:
            noise = np.convolve(noise, np.ones(b) / b, mode="same")
    env = np.exp(-t / decay_time_s)
    burst = noise * env
    # reverse
    ir = burst[::-1]
    return normalise(ir)


def drawn_echoes_ir(
    delay_ms: Optional[list] = None,
    gains: Optional[list] = None,
    sr: int = 44100,
    tail_decay_s: float = 0.0,
    duration_s: float = 0.5,
) -> np.ndarray:
    """Drawn-echoes IR: sparse impulses at user-specified delays.

    Parameters
    ----------
    delay_ms : list of float or None
        Delay times in milliseconds for each echo tap.  Defaults to
        [10, 25, 50, 100, 200].
    gains : list of float or None
        Gain per tap (0..1). Defaults to alternating decay.
    sr : int
        Sample rate.
    tail_decay_s : float
        If > 0, each impulse is replaced by a short noise burst with this
        decay time, creating diffuse echoes.
    duration_s : float
        Minimum IR duration (padded with zeros if needed).

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    if delay_ms is None:
        delay_ms = [10, 25, 50, 100, 200]
    delays_s = np.array(delay_ms, dtype=np.float64) / 1000.0
    if gains is None:
        gains = 0.8 ** np.arange(len(delays_s))
    gains = np.asarray(gains, dtype=np.float64)
    max_delay_s = float(delays_s.max()) + tail_decay_s * 3
    min_n = int(duration_s * sr) + 1
    n = max(int(sr * max_delay_s) + 1, min_n)
    ir = np.zeros(n, dtype=np.float64)
    for d, g in zip(delays_s, gains):
        idx = int(round(d * sr))
        if idx >= n:
            continue
        if tail_decay_s > 0:
            tail_len = min(int(sr * tail_decay_s * 3), n - idx)
            if tail_len > 0:
                tail = np.exp(-np.arange(tail_len, dtype=np.float64) / (sr * tail_decay_s))
                tail *= np.random.randn(tail_len) * g * 0.5
                ir[idx: idx + tail_len] += tail
        else:
            ir[idx] += g
    return normalise(ir)


def chord_body_ir(
    frequencies_hz: Optional[list] = None,
    gains: Optional[list] = None,
    duration_s: float = 0.5,
    sr: int = 44100,
    decay_rate: float = 8.0,
) -> np.ndarray:
    """Chord-body IR: sum of decaying sine tones at specified frequencies.

    Creates a pitched impulse response — like striking a set of tuned
    resonators.

    Parameters
    ----------
    frequencies_hz : list of float or None
        Frequencies of partials in Hz.  Defaults to a C major chord.
    gains : list of float or None
        Per-partial gain (0..1). Defaults to 1/n_partials.
    duration_s : float
        Total IR length in seconds.
    sr : int
        Sample rate.
    decay_rate : float
        Higher = faster decay (time constant = duration_s / decay_rate).

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    if frequencies_hz is None:
        frequencies_hz = [261.63, 329.63, 392.00, 523.25]  # C4 E4 G4 C5
    n = int(sr * duration_s)
    t = np.arange(n, dtype=np.float64) / sr
    ir = np.zeros(n, dtype=np.float64)
    n_partials = len(frequencies_hz)
    if gains is None:
        gains = [1.0 / n_partials] * n_partials
    for f, g in zip(frequencies_hz, gains):
        tone = np.sin(2.0 * np.pi * f * t)
        env = np.exp(-t * decay_rate / duration_s)
        ir += tone * env * g
    return normalise(ir)


def filter_sweep_ir(
    f_start_hz: float = 200.0,
    f_end_hz: float = 8000.0,
    duration_s: float = 0.3,
    sr: int = 44100,
    envelope: str = "linear",
) -> np.ndarray:
    """Filter-sweep IR: frequency sweep (chirp) with spectral envelope.

    Models the effect of a filter whose cutoff sweeps across frequency.

    Parameters
    ----------
    f_start_hz, f_end_hz : float
        Sweep frequency range.
    duration_s : float
        Sweep duration in seconds.
    sr : int
        Sample rate.
    envelope : "linear" | "exp" | "hanning"
        Amplitude envelope shape.

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    n = int(sr * duration_s)
    t = np.arange(n, dtype=np.float64) / sr
    # instantaneous frequency linear sweep
    inst_f = f_start_hz + (f_end_hz - f_start_hz) * t / duration_s
    phase = 2.0 * np.pi * np.cumsum(inst_f) / sr
    ir = np.sin(phase)
    if envelope == "exp":
        ir *= np.exp(-t * 3.0 / duration_s)
    elif envelope == "hanning":
        ir *= np.hanning(n)
    else:  # linear
        ir *= 1.0 - t / duration_s
        ir = np.maximum(ir, 0.0)
    return normalise(ir)


def vowel_ir(
    vowel: str = "ah",
    duration_s: float = 0.15,
    sr: int = 44100,
    noise_level: float = 0.3,
) -> np.ndarray:
    """Vowel IR: formant-shaped noise burst producing vowel coloration.

    Implements static formant filters for five cardinal vowels using
    centre-frequency / bandwidth pairs.  The IR is a short noise burst
    shaped by a cascade of 2-pole resonators.

    Parameters
    ----------
    vowel : "ah" | "ee" | "oo" | "eh" | "oh"
        Vowel type.
    duration_s : float
        IR duration in seconds.
    sr : int
        Sample rate.
    noise_level : float
        Noise excitation level (0..1).

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    # Formant table: (F1, BW1, F2, BW2, F3, BW3) in Hz
    FORMANT_TABLE = {
        "ah": (720, 80, 1200, 120, 2600, 160),
        "ee": (310, 50, 2300, 100, 3000, 120),
        "oo": (350, 60, 900, 100, 2300, 140),
        "eh": (600, 80, 1800, 150, 2600, 180),
        "oh": (500, 70, 1000, 120, 2600, 160),
    }
    formants = FORMANT_TABLE.get(vowel, FORMANT_TABLE["ah"])
    n = int(sr * duration_s)
    # noise excitation
    exc = np.random.randn(n) * noise_level
    # apply formant cascade (simple 2-pole IIR per formant)
    ir = exc.copy()
    for i in range(0, len(formants), 2):
        fc = formants[i]
        bw = formants[i + 1]
        ir = _two_pole_resonator(ir, fc, bw, sr)
    # envelope
    ir *= np.exp(-np.arange(n, dtype=np.float64) / (sr * duration_s * 0.4))
    return normalise(ir)


def spectral_delay_ir(
    bands: int = 8,
    delay_range_ms: tuple = (0.0, 30.0),
    duration_s: float = 0.5,
    sr: int = 44100,
) -> np.ndarray:
    """Spectral-delay IR: each frequency band receives a different delay.

    Splits the spectrum into logarithmically-spaced bands using FFT bins,
    assigns an increasing delay to each band, then re-synthesises.  The
    result is an IR that smears transients differently across frequency.

    Parameters
    ----------
    bands : int
        Number of spectral bands (2–32).
    delay_range_ms : (float, float)
        (min_delay_ms, max_delay_ms).
    duration_s : float
        Total IR length.
    sr : int
        Sample rate.

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    n = int(sr * duration_s)
    # start with white noise
    noise = np.random.randn(n)
    # FFT
    X = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    n_bins = len(X)
    min_d, max_d = delay_range_ms
    delays_ms = np.linspace(min_d, max_d, bands)
    # assign bins to bands
    band_edges = np.logspace(np.log10(20), np.log10(sr / 2), bands + 1)
    for bi in range(bands):
        mask = (freqs >= band_edges[bi]) & (freqs < band_edges[bi + 1])
        delay_s = delays_ms[bi] / 1000.0
        phase_shift = -2.0 * np.pi * freqs[mask] * delay_s
        X[mask] *= np.exp(1j * phase_shift)
    ir = np.fft.irfft(X, n=n)
    # window
    ir *= np.hanning(n)
    return normalise(ir)


def rain_ir(
    density: float = 50.0,
    duration_s: float = 0.5,
    sr: int = 44100,
    scatter: float = 0.02,
) -> np.ndarray:
    """Rain IR: a dense train of tiny impulses at pseudo-random times.

    Models the acoustic effect of many small impacts.  Each impulse is a
    short exponentially-decaying noise burst (<1 ms).

    Parameters
    ----------
    density : float
        Average number of impulses per second.
    duration_s : float
        IR length in seconds.
    sr : int
        Sample rate.
    scatter : float
        Temporal jitter as fraction of mean inter-impulse interval.

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    n = int(sr * duration_s)
    ir = np.zeros(n, dtype=np.float64)
    mean_interval = 1.0 / max(density, 1.0)
    t = 0.0
    while t < duration_s:
        jitter = np.random.uniform(-scatter, scatter) * mean_interval
        t += max(0.0, mean_interval + jitter)
        idx = int(round(t * sr))
        if idx >= n:
            break
        # each drop: a tiny decaying burst (~1 ms)
        burst_len = min(int(0.001 * sr), n - idx)
        if burst_len > 0:
            burst = np.random.randn(burst_len)
            burst *= np.exp(-np.arange(burst_len, dtype=np.float64) / (sr * 0.0003))
            ir[idx: idx + burst_len] += burst * 0.3
    return normalise(ir)


def reverb_ir(
    rt60_s: float = 1.5,
    duration_s: float = 2.0,
    sr: int = 44100,
    density: str = "full",
) -> np.ndarray:
    """Reverb IR: stochastic noise with exponential decay.

    A simple noise-burst reverb IR (Schroeder-style).  The decay envelope
    follows the specified RT60.

    Parameters
    ----------
    rt60_s : float
        Time for the envelope to decay -60 dB (seconds).
    duration_s : float
        Total IR length in seconds.
    sr : int
        Sample rate.
    density : "full" | "half" | "sparse"
        Controls early reflection density.

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    n = int(sr * duration_s)
    noise = np.random.randn(n)
    # decay envelope: -60 dB at rt60_s
    decay_rate = np.log(1000.0) / rt60_s
    env = np.exp(-np.arange(n, dtype=np.float64) / sr * decay_rate)
    if density == "half":
        # zero out every other sample
        env[1::2] = 0.0
    elif density == "sparse":
        # keep only 1 in 10 samples (noise-like)
        mask = np.random.random(n) < 0.1
        env = env * mask
    ir = noise * env
    # early reflections: first 10 ms are louder
    early_n = int(0.01 * sr)
    if early_n < n:
        ir[:early_n] *= 2.0
    return normalise(ir)


def metallic_bloom_ir(
    duration_s: float = 0.4,
    sr: int = 44100,
    n_partials: int = 12,
    stretch: float = 1.0,
    decay_rate: float = 15.0,
) -> np.ndarray:
    """Metallic-bloom IR: inharmonic partial sum → metallic/glass ring.

    Uses partials at frequencies following a stretched harmonic series
    (f_n = f0 * n^(stretch)), which is characteristic of metal bars,
    bells, and glass.

    Parameters
    ----------
    duration_s : float
        IR length in seconds.
    sr : int
        Sample rate.
    n_partials : int
        Number of inharmonic partials.
    stretch : float
        Stretch factor (1.0 = harmonic, ~1.4 = bell-like, >2 = extreme).
    decay_rate : float
        Higher = faster decay (time constant = duration_s / decay_rate).

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    n = int(sr * duration_s)
    t = np.arange(n, dtype=np.float64) / sr
    ir = np.zeros(n, dtype=np.float64)
    f0 = 220.0  # fundamental (adjustable via modulating)
    for h in range(1, n_partials + 1):
        f = f0 * (h ** stretch)
        amp = 1.0 / h
        tone = np.sin(2.0 * np.pi * f * t + np.random.uniform(0, 2 * np.pi))
        env = np.exp(-t * decay_rate * h / duration_s)
        ir += tone * amp * env * 0.5
    return normalise(ir)


def fm_body_ir(
    duration_s: float = 0.3,
    sr: int = 44100,
    carrier_hz: float = 800.0,
    modulator_hz: float = 120.0,
    mod_index: float = 2.0,
    feedback: float = 0.0,
) -> np.ndarray:
    """FM-body IR: frequency-modulated carrier → complex ring.

    A single FM operator as IR — the instantaneous frequency of a carrier
    is modulated by a slower sinusoidal modulator, creating sidebands.
    Adding feedback creates chaos.

    Parameters
    ----------
    duration_s : float
        IR length in seconds.
    sr : int
        Sample rate.
    carrier_hz : float
        Carrier frequency.
    modulator_hz : float
        Modulator frequency.
    mod_index : float
        Modulation index (deviation / modulator frequency).
    feedback : float
        Self-feedback gain (0..0.9).  When > 0 the modulated output feeds
        back into the modulator phase, producing chaotic/nonlinear spectra.

    Returns
    -------
    ir : ndarray, shape (N,)
    """
    n = int(sr * duration_s)
    t = np.arange(n, dtype=np.float64) / sr
    # modulator
    mod_phase = 2.0 * np.pi * modulator_hz * t
    # carrier with FM
    fb = 0.0
    ir = np.zeros(n, dtype=np.float64)
    for i in range(n):
        deviation = mod_index * modulator_hz * np.sin(mod_phase[i] + fb)
        inst_f = carrier_hz + deviation
        if i == 0:
            phase = 0.0
        else:
            phase += 2.0 * np.pi * inst_f / sr
        val = np.sin(phase)
        ir[i] = val
        fb = val * feedback
    env = np.exp(-t * 4.0 / duration_s)
    ir *= env
    return normalise(ir)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalise(x: np.ndarray) -> np.ndarray:
    """Normalise to peak = 0.95."""
    peak = np.max(np.abs(x))
    if peak > 0:
        x = x / peak * 0.95
    return x


def _two_pole_resonator(x: np.ndarray, fc: float, bw: float, sr: int) -> np.ndarray:
    """Apply a 2-pole resonator (digital formant filter)."""
    w0 = 2.0 * np.pi * fc / sr
    r = np.exp(-np.pi * bw / sr)
    a1 = -2.0 * r * np.cos(w0)
    a2 = r * r
    b0 = (1.0 - r) * (1.0 - 2.0 * r * np.cos(w0) + r * r) ** 0.5
    y = np.empty_like(x)
    s1 = s2 = 0.0
    for i in range(len(x)):
        y[i] = b0 * x[i] - a1 * s1 - a2 * s2
        s2 = s1
        s1 = y[i]
    return y


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def design_ir(
    recipe: str,
    duration_s: float = 0.5,
    sr: int = 44100,
    **kwargs,
) -> tuple:
    """Design an impulse response using a named recipe.

    Parameters
    ----------
    recipe : str
        One of IR_RECIPES.
    duration_s : float
        Target IR length in seconds (used by most generators).
    sr : int
        Sample rate.
    **kwargs
        Passed to the generator function (see each for options).

    Returns
    -------
    (ir, sr) : (ndarray, int)

    Raises
    ------
    ValueError if recipe unknown.
    """
    recipe = recipe.lower().replace("-", "_")
    gen_map = {
        "reverse_bloom": reverse_bloom_ir,
        "drawn_echoes": drawn_echoes_ir,
        "chord_body": chord_body_ir,
        "filter_sweep": filter_sweep_ir,
        "vowel": vowel_ir,
        "spectral_delay": spectral_delay_ir,
        "rain": rain_ir,
        "reverb": reverb_ir,
        "metallic_bloom": metallic_bloom_ir,
        "fm_body": fm_body_ir,
    }
    fn = gen_map.get(recipe)
    if fn is None:
        raise ValueError(
            f"Unknown IR recipe {recipe!r}.  Choose from: {IR_RECIPES}"
        )
    ir = fn(duration_s=duration_s, sr=sr, **kwargs)
    return ir, sr


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo(output_dir: str = "/tmp", sr: int = 44100):
    """Generate one example IR per recipe and write WAV files + a summary."""
    import os, time
    t0 = time.time()
    written = []
    for recipe in IR_RECIPES:
        ir, _ = design_ir(recipe, duration_s=0.4, sr=sr)
        path = os.path.join(output_dir, f"ir_{recipe}.wav")
        _write_wav(path, ir, sr)
        written.append((recipe, path, len(ir)))
    elapsed = time.time() - t0
    print(f"IR Designer demo — {len(written)} IRs in {elapsed:.2f}s")
    for name, path, n in written:
        print(f"  {name:20s}  {path}  ({n} samples)")
    return written


def _write_wav(path: str, data: np.ndarray, sr: int):
    """Write a mono WAV file (no external deps)."""
    import struct, wave
    data = np.clip(data * 32767, -32768, 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data.tobytes())


if __name__ == "__main__":
    demo()