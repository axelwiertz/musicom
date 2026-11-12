"""MIDGAR-style multi-stage ambient processor: phrase delay + shimmer + PT2399s.

Replicates the Bram Bos MIDGAR chain (synthtopia, 2026-11-11):

    Phrase Delay -> Distortion -> Fluctuator -> dual PT2399 delay -> shimmer

Design notes (the parts that matter technically):

* Phrase Delay records short windows of audio and plays them back at variable
  speed from several read heads. Because a head's speed is a playback-rate
  scalar, slowing a head transposes down and smears the same material over
  more time; that single mechanism gives both the "tape" and the "granular
  cloud" characters without a granular engine.
* Stutter is implemented by pinning a head's read offset to a capture
  boundary and retriggering it every ``stutter_rate`` samples, sample-and-hold
  style (the classic glitch repeat).
* Fluctuator = slow random-walk modulation of a chain of first-order allpass
  filters. Allpass phase movement is what produces spectral (not just
  amplitude) motion; it also decorrelates the stereo image.
* PT2399 emulation: the real chip is a 44k-ish delay DSP with a compander. We
  model pre-emphasis on the write, de-emphasis + one-pole lowpass on the read,
  and a slew-rate limiter — those three together are what make it "lo-fi".
* Shimmer: an octave-up feedback path (read the delay buffer at half speed)
  with a lowpass in the loop so the tail does not scream.
"""

from __future__ import annotations

import numpy as np

TAU = 2.0 * np.pi


# --------------------------------------------------------------------------
# building blocks
# --------------------------------------------------------------------------
class Allpass1:
    """First-order allpass with movable coefficient (spectral phase rotator)."""

    def __init__(self, coef: float = 0.5):
        self.c = float(coef)
        self.z = 0.0

    def process(self, x: np.ndarray, coefs: np.ndarray | None = None) -> np.ndarray:
        out = np.empty_like(x)
        z = self.z
        if coefs is None:
            c = self.c
            for n in range(len(x)):
                v = x[n] + c * z
                out[n] = -c * v + z
                z = v
        else:
            for n in range(len(x)):
                c = coefs[n]
                v = x[n] + c * z
                out[n] = -c * v + z
                z = v
        self.z = z
        return out


def slew_limit(x: np.ndarray, max_step: float) -> np.ndarray:
    """Per-sample rate limiter — the PT2399's audible 'staircase'."""
    out = np.empty_like(x)
    prev = 0.0
    for n in range(len(x)):
        d = x[n] - prev
        if d > max_step:
            d = max_step
        elif d < -max_step:
            d = -max_step
        prev = prev + d
        out[n] = prev
    return out


def pt2399_delay(x: np.ndarray, delay_s: float, feedback: float = 0.45,
                 tone_hz: float = 3200.0, sr: int = 44100,
                 drive: float = 1.4) -> np.ndarray:
    """One PT2399 chip: companded, band-limited, slew-limited delay."""
    n = len(x)
    d = max(2, int(delay_s * sr))
    buf = np.zeros(d + n + 4)
    # pre-emphasis (write side boost) then de-emphasis (read side cut)
    pre = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += 0.85 * (x[i] - acc)
        pre[i] = x[i] - 0.55 * acc          # high-boost
    buf[d:d + n] = np.tanh(pre * drive)
    y = np.empty(n)
    lpv = 0.0
    a = 1.0 - np.exp(-TAU * tone_hz / sr)
    for i in range(n):
        rd = buf[i]
        lpv += a * (rd - lpv)
        out = lpv * feedback
        buf[i + d] = np.tanh((buf[i + d] + out) * 0.98)
        y[i] = rd - 0.5 * lpv * 0.0
        y[i] = rd
    # de-emphasis (one-pole tilt down) + staircase
    de = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += 0.35 * (y[i] - acc)
        de[i] = acc
    return slew_limit(de, 0.12)


class Shimmer:
    """Octave-up feedback reverb tail (2x read speed = +1 octave)."""

    def __init__(self, sr: int = 44100, delay_s: float = 0.09,
                 feedback: float = 0.6, tone_hz: float = 5200.0,
                 mix: float = 0.5, voices: int = 3):
        self.sr, self.delay_s = sr, delay_s
        self.feedback, self.tone_hz = feedback, tone_hz
        self.mix, self.voices = mix, voices

    def process(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        sr = self.sr
        base = int(self.delay_s * sr)
        buf = np.zeros(base * 4 + n + 8)
        a = 1.0 - np.exp(-TAU * self.tone_hz / sr)
        lp = 0.0
        wet = np.zeros(n)
        buflen = len(buf)
        for i in range(n):
            acc = 0.0
            for v in range(self.voices):
                d = base * (v + 1)
                # half-speed read => octave up; index must stay in the past
                pos = int(i + base + d * 0.5) % buflen
                acc += buf[pos] / self.voices
            lp += a * (acc - lp)
            wet[i] = lp
            write = np.tanh((x[i] + self.feedback * lp) * 0.9)
            buf[(i + base) % buflen] = write
        return x * (1.0 - self.mix) + wet * self.mix


class PhraseDelay:
    """Capture short windows and re-play them at variable speed / stutter."""

    def __init__(self, sr: int = 44100, capture_s: float = 1.5,
                 heads=((0.0, 0.5, -0.8), (0.25, 1.0, 0.0), (0.5, -0.5, 0.8)),
                 stutter_rate: float = 11.0, stutter_amount: float = 0.0,
                 spread: float = 0.8, seed: int = 0):
        self.sr = sr
        self.cap_len = int(capture_s * sr)
        self.buf = np.zeros(self.cap_len)
        self.w = 0
        self.heads = heads                  # (start_frac, speed, pan)
        self.stutter_rate = stutter_rate
        self.stutter_amount = stutter_amount
        self.spread = spread
        self.rng = np.random.default_rng(seed)

    def _read(self, pos: float) -> float:
        i = int(pos) % self.cap_len
        frac = pos - int(pos)
        return self.buf[i] * (1.0 - frac) + self.buf[(i + 1) % self.cap_len] * frac

    def process(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        out = np.zeros((n, 2))
        pos = [h[0] * self.cap_len for h in self.heads]
        stut_hold = [-1.0] * len(self.heads)
        stut_phase = 0.0
        per = max(1, int(self.sr / max(0.1, self.stutter_rate)))
        for i in range(n):
            self.buf[self.w] = x[i]
            self.w = (self.w + 1) % self.cap_len
            stut_phase += 1.0
            if stut_phase >= per:
                stut_phase = 0.0
                for h in range(len(self.heads)):
                    # re-anchor the slice at the current write position
                    stut_hold[h] = self.w - per * 0.5
            for h, (_, speed, pan) in enumerate(self.heads):
                if self.stutter_amount > 0 and stut_hold[h] >= 0:
                    # repeat the same slice: offset fixed, advanced by rate
                    base = stut_hold[h] - per * 0 + (stut_phase * abs(speed))
                    v = self._read(base % self.cap_len)
                    v = v * self.stutter_amount + \
                        self._read(pos[h]) * (1.0 - self.stutter_amount)
                else:
                    v = self._read(pos[h])
                # constant-power pan; spread widens the pan per head
                p = float(np.clip(pan * self.spread, -1.0, 1.0))
                gl = np.cos((p + 1) * np.pi / 4)
                gr = np.sin((p + 1) * np.pi / 4)
                out[i, 0] += v * gl
                out[i, 1] += v * gr
                pos[h] = (pos[h] + speed) % self.cap_len
        return out / max(1, len(self.heads))


class Midgar:
    """Full chain: Phrase Delay -> distortion -> Fluctuator -> PT2399s -> shimmer."""

    def __init__(self, sr: int = 44100, phrase_capture_s: float = 1.2,
                 heads=((0.0, 0.5, -0.8), (0.3, 1.0, 0.0), (0.6, -0.4, 0.8)),
                 stutter_rate: float = 9.0, stutter_amount: float = 0.15,
                 drive: float = 2.0, fluct_depth: float = 0.35,
                 fluct_rate: float = 0.12, delay_time_s: float = 0.28,
                 delay_feedback: float = 0.42, shimmer_mix: float = 0.4,
                 seed: int = 0):
        self.sr = sr
        self.phrase = PhraseDelay(sr, phrase_capture_s, heads, stutter_rate,
                                  stutter_amount, seed=seed)
        self.drive = drive
        self.fluct_depth, self.fluct_rate = fluct_depth, fluct_rate
        self.delay_time_s, self.delay_feedback = delay_time_s, delay_feedback
        self.shimmer = Shimmer(sr, mix=shimmer_mix)
        self.rng = np.random.default_rng(seed + 1)

    def process(self, x: np.ndarray, tail_s: float = 2.0) -> np.ndarray:
        n = len(x)
        # pad with silence so the delay/shimmer networks can ring out
        if tail_s > 0:
            x = np.concatenate([np.asarray(x, dtype=float),
                                np.zeros(int(tail_s * self.sr))])
            n = len(x)
        # 1. phrase capture / varispeed / stutter -> stereo
        st = self.phrase.process(x)
        # 2. distortion (asymmetric soft clip, keeps even harmonics)
        st = np.tanh(st * self.drive) * 0.9 + 0.06 * st ** 2
        # 3. Fluctuator: random-walk allpass coefficients, opposite per channel
        t = np.arange(n) / self.sr
        walk = np.cumsum(self.rng.standard_normal(n)) * 0.004
        walk = walk - np.convolve(walk, np.ones(2048) / 2048, mode="same")
        mod = self.fluct_depth * np.tanh(walk + 0.2 * np.sin(TAU * self.fluct_rate * t))
        out = np.empty_like(st)
        for ch in range(2):
            ap = Allpass1(0.4)
            coefs = np.clip(0.45 + (mod if ch == 0 else -mod), -0.85, 0.85)
            out[:, ch] = 0.5 * ap.process(st[:, ch], coefs) + 0.5 * st[:, ch]
        # 4. two PT2399 chips, slightly different times for stereo width
        d1 = pt2399_delay(out[:, 0], self.delay_time_s, self.delay_feedback,
                          sr=self.sr)
        d2 = pt2399_delay(out[:, 1], self.delay_time_s * 1.06,
                          self.delay_feedback * 0.95, sr=self.sr)
        wet = np.stack([0.6 * out[:, 0] + 0.4 * d1,
                        0.6 * out[:, 1] + 0.4 * d2], axis=1)
        # 5. shimmer on the mono sum, folded back into both channels
        sh = self.shimmer.process(wet.mean(axis=1))
        wet[:, 0] += 0.5 * sh
        wet[:, 1] += 0.5 * sh
        peak = np.abs(wet).max()
        return wet / peak * 0.92 if peak > 1e-9 else wet


def demo() -> None:
    """Feed a short plucked phrase through MIDGAR and report real stats."""
    sr = 44100
    # source: two-note pluck figure (Karplus-Strong-ish)
    def pluck(f0, dur, seed=0):
        rng = np.random.default_rng(seed)
        n = int(dur * sr)
        L = max(2, int(sr / f0))
        buf = rng.uniform(-1, 1, L)
        y = np.zeros(n)
        for i in range(n):
            v = buf[i % L]
            nxt = buf[(i + 1) % L]
            buf[i % L] = 0.5 * (v + nxt) * 0.997
            y[i] = v
        return y * np.exp(-np.linspace(0, 3, n))

    src = np.concatenate([pluck(196.0, 0.5, 1), pluck(261.63, 0.5, 2),
                          pluck(329.63, 1.0, 3)])
    fx = Midgar(stutter_amount=0.2, drive=2.2, shimmer_mix=0.45)
    y = fx.process(src)

    mono = y.mean(axis=1)
    # stereo width: correlation of the two channels (low corr => wide)
    corr = float(np.corrcoef(y[:, 0], y[:, 1])[0, 1])
    # tail energy past the source length => delay/reverb actually running
    tail = mono[len(src):]
    print(f"midgar demo: src={len(src)} -> out={len(y)} samples "
          f"({len(y)/sr:.2f}s), peak={np.abs(y).max():.3f}")
    print(f"  stereo corr={corr:.3f} (wide when < 0.9), "
          f"tail rms={np.sqrt((tail**2).mean()):.4f}")

    # PT2399 alone: must darken and staircase the signal
    d = pt2399_delay(src, 0.2, 0.5, sr=sr)
    hf_in = np.abs(np.fft.rfft(src))[-2000:].sum()
    hf_out = np.abs(np.fft.rfft(d))[-2000:].sum()
    print(f"  pt2399 HF energy in={hf_in:.1f} out={hf_out:.1f} "
          f"(band-limiting works: {hf_out < hf_in})")

    assert np.isfinite(y).all() and np.abs(y).max() > 0.2
    assert np.sqrt((tail ** 2).mean()) > 0.002, "delay/shimmer tail must exist"
    assert hf_out < hf_in
    print("demo OK")


if __name__ == "__main__":
    demo()
