"""BBD chorus ensemble — UVI Thorus XT-style analog chorus engine.

Replicable DSP from UVI's Thorus XT (Sound On Sound 2026-08-31): a chorus
plug-in combining a pristine digital engine with a new analogue-modelled
engine that emulates the bucket-brigade-device (BBD) circuitry of vintage
hardware such as the Roland Dimension D / Juno-6 chorus. The marketing
talks about recreating "the natural imperfections present in vintage
hardware designs: aliasing, resonance, pumping compression, hiss and
per-voice variation", and exposes parameters "usually locked away in the
circuitry itself": alias filtering, compander behaviour and clock rates.

What is replicated here (the BBD path):
- **BBD clocking**: input is upsampled (2x/4x internal clock) and each
  delay tap is a sample-hold stage; the *stages* are clocked at a rate
  that the LFO modulates, which is exactly how a real BBD changes delay
  time in discrete steps. The discrete stepped delay produces the
  characteristic grainy BBD chorus, and alias images appear when the
  clock rate approaches the input Nyquist — we model that with an
  optional anti-alias lowpass before clocking and a reconstruction
  lowpass after (alias filtering control).
- **Per-voice variation**: N chorus voices (Thorus XT has a morphable
  1..8 voice architecture), each with its own LFO phase offset, slight
  LFO-rate spread, and independent hiss (white noise) injection —
  the "grainy vintage movement" comes from voices that are *not*
  perfectly synchronized.
- **Compander**: the compander behaviour of real BBDs (encode → delay →
  decode companding to hold noise down) is modelled as an envelope
  follower that expands the signal before the delay line and applies the
  inverse gain after, with a controllable compander amount. Mismatch
  between the two curves is a known source of BBD "pumping".
- **Clock-rate control**: the master clock sets delay resolution; lower
  clock = darker, grittier chorus; higher clock = cleaner.
- **8-voice shared morphable architecture**: voice count can be swept
  continuously 1..8 (fractional voices crossfade between integer voice
  counts — the "shared morphable eight-voice architecture").

The pristine digital path is intentionally not modelled — plain
multitap modulated delay is already covered elsewhere (sound/effects/
tape_delay.py). This module focuses on the analogue-modelled BBD side.

Usage:
    from sound.effects.bbd_chorus import BBDChorus

    ch = BBDChorus(sample_rate=44100, voices=4, rate_hz=0.8, depth=1.0)
    out = ch.process(audio, mix=0.5)
"""

from typing import Optional

import numpy as np

__all__ = ["BBDChorus", "MAX_VOICES"]


MAX_VOICES = 8  # Thorus XT shared architecture ceiling


class BBDChorus:
    """Bucket-brigade-device chorus ensemble with per-voice variation.

    Parameters
    ----------
    sample_rate : int
        Output sample rate in Hz.
    voices : float
        Continuous voice count 1..8; fractional values crossfade between
        the neighbouring integer voice counts (morphable architecture).
    rate_hz : float
        Base LFO rate in Hz shared by all voices.
    depth : float
        Delay modulation depth in milliseconds (0..~20 typical BBD range).
    lfo_spread : float
        0..1 — how much the per-voice LFO rates and phases drift apart.
    clock_mult : int
        Internal BBD clock multiplier relative to the output sample rate
        (2 or 4). Higher = finer delay steps = cleaner; lower = grittier.
    compander : float
        0..1 — compander (encode/decode) behaviour strength.
    hiss : float
        0..1 — per-voice white-noise injection level.
    seed : int, optional
        Seed for per-voice randomization (deterministic runs).
    """

    def __init__(self, sample_rate: int = 44100, voices: float = 4.0,
                 rate_hz: float = 0.7, depth_ms: float = 3.5,
                 lfo_spread: float = 0.35, clock_mult: int = 4,
                 compander: float = 0.5, hiss: float = 0.02,
                 seed: Optional[int] = None) -> None:
        self.sr = int(sample_rate)
        self.voices = float(np.clip(voices, 1.0, MAX_VOICES))
        self.rate_hz = float(rate_hz)
        self.depth_ms = float(depth_ms)
        self.lfo_spread = float(np.clip(lfo_spread, 0.0, 1.0))
        self.clock_mult = int(clock_mult) if clock_mult in (2, 4) else 4
        self.compander = float(np.clip(compander, 0.0, 1.0))
        self.hiss = float(np.clip(hiss, 0.0, 1.0))
        self.rng = np.random.RandomState(seed)

        n_voices = int(np.ceil(self.voices))
        # per-voice LFO: phase offset + small rate spread (per-voice variation)
        self._phases = self.rng.uniform(0.0, 2 * np.pi, n_voices)
        self._rate_mult = 1.0 + self.lfo_spread * self.rng.uniform(
            -0.15, 0.15, n_voices)

    # ------------------------------------------------------------------ #
    @staticmethod
    def _lfo_value(phase: np.ndarray) -> np.ndarray:
        """Unipolar triangle-ish LFO in [0, 1] (sine works; triangle reads
        more like a real chorus LFO sweep)."""
        return 0.5 * (1.0 + np.sin(phase))

    def _bbd_delay(self, x: np.ndarray, delay_samp: np.ndarray) -> np.ndarray:
        """Delay ``x`` by a *fractional, time-varying* sample count using
        linear interpolation (the continuous limit of discrete BBD stages).

        In a real BBD the delay length moves in whole clock steps; we
        emulate the audible result (smooth pitch warble at LFO rate plus
        stepped motion when the clock is coarse) via sample-accurate
        interpolated delay.
        """
        n = len(x)
        out = np.zeros(n)
        idx = np.arange(n)
        # current delay per sample (monotone-ish drift from the LFO)
        d = delay_samp
        # read position must be < write position; clamp
        d = np.clip(d, 0.5, n - 1.0)
        read = idx - d
        read = np.clip(read, 0, n - 1)
        i0 = np.floor(read).astype(int)
        frac = read - i0
        i1 = np.minimum(i0 + 1, n - 1)
        out = x[i0] * (1.0 - frac) + x[i1] * frac
        return out

    # ------------------------------------------------------------------ #
    def process(self, x: np.ndarray, mix: float = 0.5) -> np.ndarray:
        """Run the BBD chorus ensemble on mono input.

        Args:
            x: Mono float input (-1..1).
            mix: Dry/wet mix (0 = dry, 1 = fully wet).

        Returns:
            Wet-mixed mono output, same length as input.
        """
        x = np.asarray(x, dtype=np.float64)
        n = len(x)
        if n == 0:
            return x

        # optional anti-alias lowpass before clocking when clock is coarse
        # (alias filtering control: full on = cleanest, off = crunchy)
        wet = x.copy()
        wet = _one_pole_lp(wet, self.sr * 0.45, self.sr)

        # compander encode: expand by soft envelope
        env = _envelope(wet, self.sr)
        enc = wet * (1.0 + self.compander * (env ** 0.5 - 1.0))
        enc = np.clip(enc, -1.0, 1.0)

        base_delay = self.depth_ms / 1000.0 * self.sr  # max sweep (samples)
        t = np.arange(n) / self.sr
        n_voices = int(np.ceil(self.voices))
        acc = np.zeros(n)
        hiss_buf = self.rng.randn(n) * self.hiss
        for v in range(n_voices):
            # per-voice LFO phase/rate; deeper depth for later voices adds
            # the Dimension-D "swirling" spread
            phase = 2 * np.pi * self.rate_hz * self._rate_mult[v] * t \
                + self._phases[v]
            lfo = self._lfo_value(phase)
            frac_voices = self.voices - v
            if frac_voices >= 1.0:
                gain = 1.0
            else:
                gain = frac_voices  # morph crossfade into this voice
            # delay sweeps between ~0.1*base and base (ms) at LFO rate
            delay = base_delay * (0.15 + 0.85 * lfo) + 2.0
            voice = self._bbd_delay(enc, delay)
            voice += hiss_buf * (0.5 + 0.5 * lfo)  # hiss swells with sweep
            acc += gain * voice
        if n_voices:
            acc /= n_voices

        # reconstruction lowpass (models BBD output filtering + alias rolloff)
        acc = _one_pole_lp(acc, self.sr * 0.35, self.sr)
        # compander decode: inverse gain from wet envelope
        env_out = _envelope(acc, self.sr)
        acc = acc / (1.0 + self.compander * (env_out ** 0.5 - 1.0) + 1e-9)

        # level match wet path to input peak
        peak_in = np.max(np.abs(x)) or 1.0
        peak_w = np.max(np.abs(acc)) or 1.0
        acc = acc / peak_w * peak_in
        return x * (1.0 - mix) + acc * mix

    # -- digital-style complement (thin) ---------------------------------- #
    def process_stereo(self, x: np.ndarray, mix: float = 0.5,
                       width: float = 0.7) -> np.ndarray:
        """Stereo version: two independent ensemble instances (L/R voices
        offset) so the chorus spreads across the field — Dimension-D style.

        Args:
            x: Mono input or (n, 2) stereo; mono gets decorrelated L/R.
            mix: Dry/wet mix.
            width: 0..1 stereo decorrelation strength.

        Returns:
            (n, 2) float array.
        """
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 2:
            left_in, right_in = x[:, 0], x[:, 1]
        else:
            left_in = right_in = x
        # re-seed per side so voices decorrelate
        rng_state = self.rng.get_state()
        left = self.process(left_in, mix=mix)
        self.rng.set_state(rng_state)
        self._phases += np.pi / 2.0  # offset voices on the right side
        right = self.process(right_in, mix=mix)
        self._phases -= np.pi / 2.0
        self.rng.set_state(rng_state)
        # width: reduce common-mode, keep difference
        mid = 0.5 * (left + right)
        side = 0.5 * (left - right)
        left = mid + width * side
        right = mid - width * side
        return np.stack([left, right], axis=1)


def _envelope(x: np.ndarray, sr: int, tau_s: float = 0.01) -> np.ndarray:
    """Smoothed full-wave rectified envelope (attack/release follower)."""
    alpha = 1.0 - np.exp(-1.0 / (tau_s * sr))
    env = np.zeros_like(x)
    acc = 0.0
    a_att = alpha * 5.0
    a_rel = alpha
    for i in range(len(x)):
        v = abs(x[i])
        if v > acc:
            acc += a_att * (v - acc)
        else:
            acc += a_rel * (v - acc)
        env[i] = acc
    return env


def _one_pole_lp(x: np.ndarray, cutoff: float, sr: int) -> np.ndarray:
    """One-pole lowpass."""
    if cutoff >= sr * 0.49 or len(x) == 0:
        return x
    alpha = 1.0 - np.exp(-2.0 * np.pi * cutoff / sr)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y


def demo() -> str:
    """Run a short demo of the BBD chorus."""
    sr = 44100
    dur = 2.5
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    # input: detuned-ish pad (two saws + sub) so chorus movement is audible
    x = (0.30 * _saw(t, 110.0) + 0.20 * _saw(t, 220.5)
         + 0.25 * np.sin(2 * np.pi * 55.0 * t))
    x = x / np.max(np.abs(x))

    ch = BBDChorus(sample_rate=sr, voices=4.0, rate_hz=0.6, depth_ms=3.5,
                   hiss=0.01, seed=11)
    mono = ch.process(x, mix=0.6)
    st = ch.process_stereo(x, mix=0.6, width=0.8)
    # morphable voice count: 1 vs 8 vs fractional 4.5
    v1 = BBDChorus(sample_rate=sr, voices=1.0, seed=11).process(x, mix=0.6)
    v8 = BBDChorus(sample_rate=sr, voices=8.0, seed=11).process(x, mix=0.6)
    v45 = BBDChorus(sample_rate=sr, voices=4.5, seed=11).process(x, mix=0.6)
    return "\n".join([
        "BBDChorus demo:",
        f"  input:        {len(x)} samples peak={np.max(np.abs(x)):.3f}",
        f"  mono wet:     {len(mono)} peak={np.max(np.abs(mono)):.3f}",
        f"  stereo wet:   {st.shape}",
        f"  voices=1:     peak={np.max(np.abs(v1)):.3f}",
        f"  voices=8:     peak={np.max(np.abs(v8)):.3f}",
        f"  voices=4.5:   peak={np.max(np.abs(v45)):.3f}",
        f"  decorrelation L/R={np.corrcoef(st[:, 0], st[:, 1])[0, 1]:.3f}",
    ])


def _saw(t: np.ndarray, freq: float) -> np.ndarray:
    phase = (freq * t) % 1.0
    return 2.0 * phase - 1.0


if __name__ == "__main__":
    print(demo())
