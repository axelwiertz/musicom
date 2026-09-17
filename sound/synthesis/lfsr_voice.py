"""LFSR pitched-noise oscillator — Noise Engineering "AT Legio" (Ataraxic Translatron) style.

Replicable logic from the Synthtopia item on the Noise Engineering Legio
Eurorack platform (2026-09-11).  Legio is one hardware platform that loads any of
23 firmwares, among them "AT Legio — Ataraxic Translatron Legio LFSR voice"
(beside "Sinc Legio — multimode stereo oscillator", "Plus Legio — additive voice").

The mechanism, stated honestly
------------------------------
- A maximal-length **linear-feedback shift register** (Galois form) is clocked at
  a rate ``C`` and its single output bit is **held** (zero-order hold) until the
  next clock: a two-level pseudo-random signal whose transition rate is ``C``.
- A maximal register of width ``b`` emits a bit pattern that repeats after exactly
  ``2**b - 1`` clocks.  That *is* the oscillator period, so::

      f0 = C / (2**b - 1)        ->        C = f0 * (2**b - 1)

- Consequence (the honest part): to get an *audible* pitch the clock must stay
  below the sample rate, and ``C`` grows as ``2**b``.  With the default
  oversampling factor ``os = 8`` (internal rate 352.8 kHz) a **16-bit** register
  only reaches ``f0 = 176400 / 65535 = 2.7 Hz`` — i.e. sub-audio, so a long
  register at an audio clock is not a pitch, it is **pitched noise**: the
  fundamental is set by run-length statistics, not by the register period.  Only
  short registers (roughly ``b <= 10``) can be *tuned* to a musical note.  This
  module reports both cases instead of pretending otherwise:
  ``LFSRVoice.tune()`` returns ``(clock, f0_actual, playable)``.
- **Register width = character control**, and this is measurable: spectral
  flatness (geometric/arithmetic mean of the magnitude spectrum) rises from ~0
  for an 8-bit register to near 1 for a long register.  Short = hollow buzz with
  widely spaced harmonics; long = dense noise with a clear-sounding pitch from
  the clock.
- ``staircase`` combines the last k output bits as a base-2 weighted word (a cheap
  R-2R DAC) — the stepped multi-level character instead of a hard square.
- One-pole tone lowpass + DC block close the voice (the hardware output is
  post-filtered and AC-coupled).
- ``os`` oversampling: bits are generated at ``sr * os`` and box-decimated to
  ``sr``, which is what lets an 8-bit register reach musical pitches without
  aliasing the clock.

Every mask in ``LFSR_MASKS`` has a **verified** full ``2**b - 1`` period —
``LFSR.measured_period()`` walks the state cycle and re-derives it; the demo and
tests assert on the measured value, not the table.

Not replicated: the front panel, CV inputs, firmware binaries.

Usage:
    from sound.synthesis.lfsr_voice import LFSRVoice, LFSR, LFSR_MASKS

    v = LFSRVoice(sample_rate=44100, os=8)
    wav = v.render_note(midi_note=57, duration=1.0, bits=8)   # tunable buzz
    hiss = v.render_clock(clock_hz=12000.0, duration=1.0, bits=16)  # pitched noise
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "LFSR",
    "LFSRVoice",
    "LFSR_MASKS",
    "midi_to_freq",
    "generate_bits",
    "pitch_from_spectrum",
    "harmonic_error",
    "spectral_flatness",
    "dominant_period",
    "MAX_TUNABLE_BITS",
]

A440 = 440.0

# Above this register width the required clock for an audible fundamental exceeds
# any sane internal rate at 44.1 kHz -- such settings are noise sources, not
# tunable oscillators (see module docstring).
MAX_TUNABLE_BITS = 10


def midi_to_freq(note: float) -> float:
    """Equal-tempered MIDI note (A4 = 440 Hz) -> Hz."""
    return A440 * (2.0 ** ((float(note) - 69.0) / 12.0))


# Galois feedback masks (right-shift register).  Each verified to yield the full
# period 2**bits - 1 -- see LFSR.measured_period() / is_maximal().
LFSR_MASKS: Dict[int, int] = {
    8: 0xB8,          # period 255        -- bright hollow buzz, tunable
    10: 0x309,        # period 1,023      -- tunable
    16: 0xD008,       # period 65,535     -- the classic arcade/TIA buzz / noise
    17: 0x12000,      # period 131,071
    19: 0x42D6D,      # period 524,287
    23: 0x4C73A9,     # period 8,388,607  -- long-sequence pitched noise
}

_PERIOD_CACHE: Dict[Tuple[int, int], Optional[int]] = {}


class LFSR:
    """Maximal-length Galois LFSR: one output bit per clock tick.

    Right-shift form — output bit is ``state & 1`` taken *before* the shift::

        state = (state >> 1) ^ mask   if (state & 1) else (state >> 1)
    """

    def __init__(self, bits: int = 16, mask: Optional[int] = None,
                 seed: int = 0xACE1):
        self.bits = int(bits)
        if mask is None:
            if self.bits not in LFSR_MASKS:
                raise ValueError(
                    f"no verified default mask for {self.bits} bits; pass mask= "
                    f"explicitly (verified widths: {sorted(LFSR_MASKS)})")
            mask = LFSR_MASKS[self.bits]
        self.mask = int(mask) & ((1 << self.bits) - 1)
        if self.mask == 0:
            raise ValueError("mask must be non-zero")
        self.state = (int(seed) & ((1 << self.bits) - 1)) or 1

    @property
    def period(self) -> int:
        """Expected sequence period of a maximal register: 2**bits - 1."""
        return (1 << self.bits) - 1

    def measured_period(self) -> Optional[int]:
        """Walk the state cycle and return the period actually observed.

        ``None`` when the cycle fails to close within 2**bits steps (non-maximal
        mask).  Cached per (bits, mask).
        """
        key = (self.bits, self.mask)
        if key in _PERIOD_CACHE:
            return _PERIOD_CACHE[key]
        st = s0 = 1
        found: Optional[int] = None
        for k in range(1, (1 << self.bits) + 1):
            st = (st >> 1) ^ self.mask if (st & 1) else (st >> 1)
            if st == s0:
                found = k
                break
        _PERIOD_CACHE[key] = found
        return found

    def is_maximal(self) -> bool:
        """True when the measured period equals 2**bits - 1."""
        return self.measured_period() == self.period

    # ------------------------------------------------------------------ ticking
    def step(self) -> int:
        """Advance one clock tick; return the output bit (taken pre-shift)."""
        st = self.state
        out = st & 1
        self.state = (st >> 1) ^ self.mask if out else (st >> 1)
        return out

    def chunk(self, n_ticks: int) -> int:
        """Return ``n_ticks`` output bits packed into an int (LSB = first tick)."""
        st = self.state
        mask = self.mask
        v = 0
        for i in range(int(n_ticks)):
            bit = st & 1
            v |= bit << i
            st = (st >> 1) ^ mask if bit else (st >> 1)
        self.state = (st & ((1 << self.bits) - 1)) or 1
        return v

    def next_bits(self, n_ticks: int) -> np.ndarray:
        """Return the next ``n_ticks`` output bits as a uint8 array."""
        n_ticks = int(n_ticks)
        out = np.empty(n_ticks, dtype=np.uint8)
        i = 0
        while i < n_ticks:
            take = min(60, n_ticks - i)
            word = self.chunk(take)
            for j in range(take):
                out[i + j] = (word >> j) & 1
            i += take
        return out


def generate_bits(bits: int = 16, mask: Optional[int] = None,
                  n_ticks: int = 1024, seed: int = 0xACE1) -> np.ndarray:
    """Convenience: ``n_ticks`` output bits of a fresh LFSR."""
    return LFSR(bits=bits, mask=mask, seed=seed).next_bits(n_ticks)


class LFSRVoice:
    """LFSR oscillator voice: bit-stream clock, staircase DAC, tone, DC block.

    Args:
        sample_rate: output sample rate in Hz.
        bits: default register width (8/10/16/17/19/23 shipped in ``LFSR_MASKS``).
        mask: explicit feedback mask (overrides the table lookup).
        staircase: number of consecutive output bits combined as a weighted word
            (1 = plain two-level output, 2..5 = stepped R-2R ladder character).
        tone: one-pole lowpass cutoff in Hz (0 = bypass).
        os: internal oversampling factor used to generate and decimate the bit
            stream (1 = off, 4/8 = practical).  Higher ``os`` raises the maximum
            clock, hence the maximum tunable pitch.
        seed: register seed.
    """

    def __init__(self, sample_rate: int = 44100, bits: int = 8,
                 mask: Optional[int] = None, staircase: int = 1,
                 tone: float = 0.0, os: int = 8, seed: int = 0xACE1):
        self.sr = int(sample_rate)
        self.bits = int(bits)
        self.mask = int(mask) if mask is not None else LFSR_MASKS[self.bits]
        self.staircase = max(1, int(staircase))
        self.tone = float(tone)
        self.os = max(1, int(os))
        self.seed = int(seed)
        self._dc_prev_in = 0.0
        self._dc_prev_out = 0.0
        self._lp = 0.0

    # ------------------------------------------------------------------ tuning
    @staticmethod
    def lfsr_period(bits: int) -> int:
        """Oscillator period in clocks for a maximal register of ``bits``."""
        return (1 << int(bits)) - 1

    @property
    def internal_rate(self) -> int:
        """Internal (oversampled) generation rate in Hz."""
        return self.sr * self.os

    @property
    def max_clock(self) -> float:
        """Highest clock rate that stays under the internal Nyquist limit."""
        return 0.45 * self.internal_rate

    def tune(self, midi_note: float, bits: Optional[int] = None) -> Tuple[float, float, bool]:
        """Return ``(clock_hz, f0_actual_hz, playable)`` for a target note.

        ``clock = f0 * (2**bits - 1)``; when that exceeds :attr:`max_clock` the
        clock is clamped and ``playable=False`` — the register is then behaving as
        a noise source at this pitch, not a tuned oscillator.
        """
        b = self.bits if bits is None else int(bits)
        want = midi_to_freq(midi_note) * self.lfsr_period(b)
        if want <= self.max_clock:
            return want, midi_to_freq(midi_note), True
        clock = self.max_clock
        return clock, clock / self.lfsr_period(b), False

    def max_tunable_note(self, bits: Optional[int] = None) -> float:
        """Highest MIDI note this register can be *tuned* to at the current rate."""
        b = self.bits if bits is None else int(bits)
        f0 = self.max_clock / self.lfsr_period(b)
        return 69.0 + 12.0 * np.log2(max(f0, 1e-9) / A440)

    # ------------------------------------------------------------------ render
    def _bit_signal(self, clock: float, n_internal: int,
                    bits: int, seed: Optional[int]) -> np.ndarray:
        """Zero-order-held (and optionally staircase-decoded) bit stream.

        Returns a two-level (or multi-level) signal sampled at the internal rate.
        """
        step = clock / self.internal_rate                    # clocks per sample
        n_ticks = int(np.ceil(n_internal * step)) + self.staircase + 2
        lfsr = LFSR(bits, LFSR_MASKS.get(bits, self.mask),
                    self.seed if seed is None else seed)
        stream = lfsr.next_bits(n_ticks)

        idx = np.clip(np.floor(np.arange(n_internal) * step).astype(np.int64),
                      0, n_ticks - 1)
        if self.staircase == 1:
            return stream[idx].astype(np.float64) * 2.0 - 1.0
        k = self.staircase
        u = np.maximum(idx - (k - 1), 0)
        acc = np.zeros(n_internal, dtype=np.float64)
        for j in range(k):
            acc += stream[np.minimum(u + j, n_ticks - 1)].astype(np.float64) * (2.0 ** j)
        return acc / (2.0 ** k - 1.0) * 2.0 - 1.0

    def _anti_alias_downsample(self, sig: np.ndarray) -> np.ndarray:
        """Box-filter and decimate the internal-rate signal to ``sr``."""
        os = self.os
        if os == 1:
            return sig
        kern = np.ones(os) / float(os)
        filtered = np.convolve(sig, kern, mode="same")
        return filtered[::os]

    def render_clock(self, clock_hz: float, duration: float = 1.0,
                     bits: Optional[int] = None, amp: float = 0.8,
                     attack: float = 0.002, release: float = 0.05,
                     seed: Optional[int] = None) -> np.ndarray:
        """Render directly from a clock rate (the module's clock input/CV).

        Use this for the noise character: a long register at an audio clock has a
        pitch set by run-length statistics, not by ``clock / (2**bits - 1)``.
        """
        b = self.bits if bits is None else int(bits)
        n = max(1, int(duration * self.sr))
        clock = float(np.clip(clock_hz, 1.0, self.max_clock))
        sig = self._anti_alias_downsample(self._bit_signal(clock, n * self.os, b, seed))
        return self._finish(sig[:n], amp, attack, release)

    def render_note(self, midi_note: float, duration: float = 1.0,
                    bits: Optional[int] = None, amp: float = 0.8,
                    attack: float = 0.002, release: float = 0.05,
                    seed: Optional[int] = None, strict: bool = False) -> np.ndarray:
        """Render one *tuned* note via ``clock = f0 * (2**bits - 1)``.

        Raises ``ValueError`` when the register is too wide to be tuned to the note
        (unless ``strict=False``, in which case the clock clamps and the resulting
        noise character is returned).
        """
        b = self.bits if bits is None else int(bits)
        clock, f0_actual, playable = self.tune(midi_note, b)
        if not playable:
            msg = (f"{b}-bit register cannot be tuned to MIDI {midi_note:.0f} "
                   f"({midi_to_freq(midi_note):.1f} Hz) at sr={self.sr}, os={self.os}: "
                   f"needs clock {midi_to_freq(midi_note) * self.lfsr_period(b) / 1000:.1f} kHz "
                   f"> max {self.max_clock / 1000:.1f} kHz (clamps to "
                   f"{f0_actual:.2f} Hz). Use bits<={MAX_TUNABLE_BITS} or render_clock().")
            if strict:
                raise ValueError(msg)
        return self.render_clock(clock, duration, b, amp, attack, release, seed)

    def render_melody(self, notes: Sequence[Tuple[float, float, float]],
                      bits: Optional[int] = None, tail: float = 0.2) -> np.ndarray:
        """Render ``[(midi_note, start_sec, dur_sec), ...]`` to a mono mix."""
        total = max((s + d for _, s, d in notes), default=1.0) + tail
        buf = np.zeros(int(total * self.sr), dtype=np.float64)
        for m, start, dur in notes:
            seg = self.render_note(m, dur, bits=bits)
            i0 = int(start * self.sr)
            i1 = min(len(buf), i0 + len(seg))
            if i1 > i0:
                buf[i0:i1] += seg[: i1 - i0]
        return buf

    # ------------------------------------------------------------------ helpers
    def _finish(self, sig: np.ndarray, amp: float, attack: float,
                release: float) -> np.ndarray:
        n = sig.size
        if n == 0:
            return sig
        sig = sig * float(amp)

        if self.tone and self.tone > 0.0:
            a = 1.0 - np.exp(-2.0 * np.pi * min(self.tone, self.sr * 0.45) / self.sr)
            out = np.empty(n, dtype=np.float64)
            y = self._lp
            for i in range(n):
                y += a * (sig[i] - y)
                out[i] = y
            self._lp = y
            sig = out

        # DC block (the hardware output is AC-coupled)
        r = 0.999
        out = np.empty(n, dtype=np.float64)
        pi, po = self._dc_prev_in, self._dc_prev_out
        for i in range(n):
            x = sig[i]
            po = r * po + (x - pi)
            pi = x
            out[i] = po
        self._dc_prev_in, self._dc_prev_out = pi, po
        sig = out

        env = np.ones(n)
        na = min(n, max(0, int(attack * self.sr)))
        nr = min(n, max(0, int(release * self.sr)))
        if na:
            env[:na] = np.linspace(0.0, 1.0, na)
        if nr:
            env[n - nr:] = np.linspace(1.0, 0.0, nr)
        return (sig * env).astype(np.float64)


# ------------------------------------------------------------------ analysis utils
def pitch_from_spectrum(signal: np.ndarray, sr: int) -> float:
    """Frequency of the strongest spectral line (Hz), zero-padded + interpolated."""
    x = np.asarray(signal, dtype=np.float64)
    x = x - x.mean()
    n = int(x.size)
    if n < 64:
        return 0.0
    nfft = 1 << int(np.ceil(np.log2(max(4096, n))))
    spec = np.abs(np.fft.rfft(x * np.hanning(n), nfft))
    k = int(np.argmax(spec))
    if 0 < k < len(spec) - 1:
        a, b, c = spec[k - 1], spec[k], spec[k + 1]
        denom = a - 2 * b + c
        delta = 0.5 * (a - c) / denom if denom else 0.0
    else:
        delta = 0.0
    return (k + delta) * sr / nfft


def harmonic_error(freq: float, f0: float, max_harmonic: int = 64) -> float:
    """Relative error of ``freq`` from the nearest integer multiple of ``f0``."""
    h = max(1, min(int(round(freq / max(f0, 1e-9))), max_harmonic))
    return abs(freq - h * f0) / max(f0, 1e-9)


def spectral_flatness(signal: np.ndarray) -> float:
    """Geometric/arithmetic mean of the magnitude spectrum (0 = tonal, 1 = noise)."""
    x = np.asarray(signal, dtype=np.float64)
    if x.size < 64:
        return 0.0
    spec = np.abs(np.fft.rfft(x * np.hanning(x.size))) + 1e-12
    return float(np.exp(np.mean(np.log(spec))) / np.mean(spec))


def dominant_period(signal: np.ndarray, sr: int, lo: float = 40.0,
                    hi: float = 4000.0) -> float:
    """Autocorrelation-based dominant frequency (Hz) of a quasi-periodic signal."""
    x = np.asarray(signal, dtype=np.float64)
    x = x - x.mean()
    if x.size < 64:
        return 0.0
    ac = np.correlate(x, x, mode="full")[x.size - 1:]
    ac = ac / (ac[0] + 1e-12)
    lo_lag = max(1, int(sr / hi))
    hi_lag = min(len(ac) - 1, int(sr / lo))
    seg = ac[lo_lag:hi_lag]
    if seg.size == 0:
        return 0.0
    peak = lo_lag + int(np.argmax(seg))
    return sr / peak


# ------------------------------------------------------------------------ demo
def demo() -> str:
    """Prove register periods, the tuning law, and register/staircase character."""
    sr = 44100

    for bits, mask in sorted(LFSR_MASKS.items()):
        reg = LFSR(bits=bits, mask=mask)
        meas = reg.measured_period()
        print(f"{bits:2d}-bit mask {mask:#08x}: measured period={meas:8d}  "
              f"2**{bits}-1={reg.period:8d}  maximal={meas == reg.period}")
        assert meas == reg.period, f"{bits}-bit mask {mask:#x} is not maximal"

    reg = LFSR(bits=16)
    p = reg.period
    seq = LFSR(bits=16).next_bits(2 * p)
    assert np.array_equal(seq[:p], seq[p:]), "LFSR is not full period"
    print(f"period check: bits[:{p}] == bits[{p}:{2 * p}] -> True "
          f"({p} clocks = 2**16 - 1)")
    print(f"bit balance over one period: {seq[:p].sum()} ones / {p} "
          f"({100.0 * seq[:p].mean():.2f} %)")

    v = LFSRVoice(sample_rate=sr, bits=8, os=8)
    note = 57.0                                    # A3 = 220 Hz
    f0 = midi_to_freq(note)
    clock, f0_act, playable = v.tune(note)
    print(f"tune: MIDI {note:.0f} ({f0:.1f} Hz) on an 8-bit register (period "
          f"{v.lfsr_period(8)}) -> clock {clock:.1f} Hz, f0_actual "
          f"{f0_act:.1f} Hz, playable={playable}")
    assert playable and abs(f0_act - f0) < 1e-9

    audio = v.render_note(note, 1.0)
    line = pitch_from_spectrum(audio, sr)
    herr = harmonic_error(line, f0)
    print(f"render_note: len={len(audio)} peak={np.max(np.abs(audio)):.3f} "
          f"finite={np.all(np.isfinite(audio))}")
    print(f"  strongest spectral line={line:.1f} Hz ({line / f0:.3f} x f0, "
          f"{herr * 100:.2f} % off the harmonic grid)")
    assert herr < 0.01, f"line {line:.1f} Hz is not on {f0:.1f} Hz's harmonic grid"

    # harmonic comb: each of the first 8 harmonics of f0 is present
    spec = np.abs(np.fft.rfft(audio * np.hanning(audio.size)))
    fr = np.fft.rfftfreq(audio.size, 1.0 / sr)
    band = (fr > 100.0) & (fr < 8.5 * f0)
    hits = 0
    for h in range(1, 9):
        want = h * f0
        j = int(np.argmin(np.abs(fr - want)))
        near = spec[max(0, j - 3):j + 4]
        if near.size and near.max() > 0.02 * spec[band].max():
            hits += 1
    print(f"  harmonic comb: {hits}/8 harmonics of {f0:.0f} Hz present "
          f"above -34 dB")
    assert hits >= 6, f"only {hits}/8 harmonics present"

    # the bit stream is periodic at exactly one oscillator period
    per = v.lfsr_period(8)
    bits_arr = generate_bits(bits=8, n_ticks=3 * per)
    ok = np.array_equal(bits_arr[:per], bits_arr[per:2 * per])
    print(f"clock-domain periodicity: sequence repeats every {per} clocks -> {ok}")
    assert ok

    # register width = character: tunable buzz -> untunable pitched noise
    print("register width vs spectral flatness (0 = tonal, 1 = noise), "
          "clock fixed at 6 kHz:")
    flat = {}
    for b in (8, 16, 23):
        vv = LFSRVoice(sample_rate=sr, bits=b, staircase=1, tone=0.0, os=8)
        a = vv.render_clock(6000.0, 0.5, bits=b)
        flat[b] = spectral_flatness(a)
        print(f"  {b:2d} bits (period {vv.lfsr_period(b):8d}): "
              f"flatness={flat[b]:.4f}  rms={np.sqrt(np.mean(a ** 2)):.4f}")
    assert flat[8] < flat[16] < flat[23], "longer registers must read noisier"

    print("tunable range (os=8 -> internal rate "
          f"{v.internal_rate} Hz, max clock {v.max_clock:.0f} Hz):")
    for b in (8, 10, 16):
        vv = LFSRVoice(sample_rate=sr, bits=b, os=8)
        top = vv.max_tunable_note(b)
        print(f"  {b:2d}-bit register: highest tunable note = MIDI "
              f"{top:6.1f} ({midi_to_freq(top):7.1f} Hz)")
    assert LFSRVoice(sample_rate=sr, bits=8, os=8).max_tunable_note(8) > 69.0
    try:
        v.render_note(69.0, 0.1, bits=16, strict=True)
    except ValueError as exc:
        print(f"  16-bit @ A4 refused (strict): {str(exc)[:88]}...")

    stair = v.render_note(note, 0.2)
    v.staircase = 4
    stair4 = v.render_note(note, 0.2)
    n2 = len(np.unique(np.round(stair, 6)))
    n4 = len(np.unique(np.round(stair4, 6)))
    print(f"distinct levels: two-level={n2} staircase(4)={n4}")
    assert n4 > n2
    v.staircase = 1

    a1 = v.render_note(note, 0.30)
    a2 = v.render_note(note, 0.30)
    assert not np.allclose(a1, a2), "register did not advance between renders"
    print("successive renders differ (register keeps advancing): True")

    mel = v.render_melody([(52, 0.0, 0.4), (55, 0.4, 0.4), (57, 0.8, 0.6)], bits=8)
    print(f"melody: len={len(mel)} peak={np.max(np.abs(mel)):.3f}")
    assert np.max(np.abs(mel)) > 0.05
    print("  lfsr_voice demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
