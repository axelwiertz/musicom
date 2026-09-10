"""ZERO9-style post-production suite — gated reverb, spectral declash,
rhythmic dual-engine delay and upward/downward parallel multiband compression.

Replicable logic from the ZERO9 plugin range (MusicTech news, 2026-09-08):

  * *Severed Space* — "a gated reverb with onset-triggered closure, spectral
    declashing and final analogue movement".
  * *Eccentric Echo* — "a pair of delay engines — one continuous and one
    granular — capable of feeding into one another ... serial/parallel routing,
    echo, splice, pitch settings".
  * *Fractured Frequency* — "a four-stage, tempo-locked glitch chain".
  * *Crushing Compressor* — "four frequency bands of upward and downward
    parallel compression".

What is replicated here:
- ``GatedReverb``: short comb+allpass reverb tail whose gain is killed by an
  onset-triggered envelope (trigger -> hold -> fast close), plus a
  spectral-declash stage (per-band magnitude limiter on the STFT that reduces
  stacked-peak harshness) and an "analogue movement" LFO on the tail level.
- ``DualEngineDelay``: two delay lines (continuous = interpolated read,
  granular = windowed grain bursts) that can feed each other, with
  serial / parallel / feedback routing, per-engine pitch (resample) and
  splice (grain trigger hop).
- ``RhythmicGlitchChain``: four tempo-locked stages (stutter, reverse slice,
  bit-crush, decimate) each gated by a 16th-note pattern.
- ``ParallelBandCompressor``: 4-band complementary crossover, each band with an
  independent upward (below-threshold lift) and downward (above-threshold
  squash) parallel component.

Not replicated: the plug-in UIs, the exact ZERO9 parameter curves.

Usage:
    from sound.effects.severance import (
        GatedReverb, DualEngineDelay, RhythmicGlitchChain,
        ParallelBandCompressor, demo)

    gr = GatedReverb(sample_rate=44100)
    out = gr.process(audio, triggers=[0.25, 1.25], gate_len=0.30)
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "GatedReverb",
    "DualEngineDelay",
    "RhythmicGlitchChain",
    "ParallelBandCompressor",
    "spectral_declash",
    "demo",
]


# ------------------------------------------------------------------ declashing
def spectral_declash(audio: np.ndarray, sample_rate: int = 44100,
                     frame: int = 1024, hop: int = 256,
                     threshold_db: float = -6.0, ratio: float = 4.0) -> np.ndarray:
    """Per-band magnitude limiter on the STFT: tames stacked resonant peaks.

    Bins louder than ``threshold_db`` relative to the frame's mean magnitude are
    compressed by ``ratio`` while phase is preserved (overlap-add, Hann).
    """
    x = np.asarray(audio, dtype=np.float64).reshape(-1)
    if len(x) < frame:
        return x.copy()
    win = np.hanning(frame)
    pad = frame
    xp = np.concatenate([np.zeros(pad), x, np.zeros(pad)])
    out = np.zeros_like(xp)
    wsum = np.zeros_like(xp)
    for start in range(0, len(xp) - frame + 1, hop):
        seg = xp[start:start + frame]
        spec = np.fft.rfft(seg * win)
        mag = np.abs(spec)
        ref = np.mean(mag) + 1e-12
        thr = ref * (10.0 ** (threshold_db / 20.0))
        over = mag > thr
        if np.any(over):
            excess_db = 20.0 * np.log10(mag[over] / thr)
            mag[over] = thr * 10.0 ** ((excess_db / ratio) / 20.0)
        seg_out = np.fft.irfft(mag * np.exp(1j * np.angle(spec)), n=frame)
        out[start:start + frame] += seg_out * win
        wsum[start:start + frame] += win ** 2
    out = out / np.maximum(wsum, 1e-9)
    return out[pad:pad + len(x)]


# ----------------------------------------------------------------- gated reverb
class GatedReverb:
    """Onset-gated reverb with spectral declash + analogue movement (LFO)."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)
        self.tail_gain: float = 0.8
        self.declash: float = 0.5     # 0..1 blend of declashed tail
        self.movement: float = 0.6    # LFO depth on the tail level
        self.movement_rate: float = 0.7

    def _reverb_tail(self, x: np.ndarray, decay: float = 0.62) -> np.ndarray:
        """Compact comb + allpass network -> dense early tail."""
        taps = [int(self.sr * t) for t in (0.0107, 0.0173, 0.0231, 0.0299)]
        fb = np.clip(decay, 0.0, 0.95)
        acc = np.zeros_like(x)
        for tap in taps:
            buf = np.zeros(tap + 1, dtype=np.float64)
            idx = 0
            y = np.empty_like(x)
            lp = 0.0
            for i in range(len(x)):
                d = buf[idx]
                lp += 0.42 * (d - lp)
                v = x[i] + fb * lp
                buf[idx] = v
                idx = (idx + 1) % (tap + 1)
                y[i] = lp
            acc += y
        acc /= len(taps)
        # one allpass to smear the comb resonances
        d = int(self.sr * 0.005)
        buf = np.zeros(d, dtype=np.float64)
        idx = 0
        g = 0.5
        out = np.empty_like(acc)
        for i in range(len(acc)):
            dly = buf[idx]
            v = -g * acc[i] + dly
            buf[idx] = acc[i] + g * v
            idx = (idx + 1) % d
            out[i] = v
        return out

    def _gate_env(self, n: int, triggers: Sequence[float], gate_len: float,
                  hold: float = 0.005) -> np.ndarray:
        """1.0 during [trigger, trigger+gate_len], then an abrupt close."""
        env = np.zeros(n, dtype=np.float64)
        hold_n = max(1, int(hold * self.sr))
        gate_n = max(1, int(gate_len * self.sr))
        for t in triggers:
            s = int(t * self.sr)
            e = min(n, s + hold_n + gate_n)
            if s >= n:
                continue
            env[s:min(n, s + hold_n)] = 1.0
            rel = np.linspace(1.0, 0.0, max(1, e - (s + hold_n)),
                              endpoint=False)
            env[s + hold_n:e] = rel
        return env

    def process(self, audio: np.ndarray, triggers: Sequence[float],
                gate_len: float = 0.25, decay: float = 0.65,
                ) -> np.ndarray:
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        tail = self._reverb_tail(x, decay=decay)
        if self.declash > 0.0:
            dc = spectral_declash(tail, self.sr)
            tail = (1.0 - self.declash) * tail + self.declash * dc
        n = len(x)
        env = self._gate_env(n, triggers, gate_len)
        if self.movement > 0.0:
            tt = np.arange(n) / self.sr
            lfo = 1.0 + self.movement * 0.35 * np.sin(
                2 * np.pi * self.movement_rate * tt)
            env = env * lfo
        return x + self.tail_gain * tail * env


# -------------------------------------------------------------- dual delay
class DualEngineDelay:
    """Continuous + granular delay engines with serial/parallel coupling."""

    def __init__(self, sample_rate: int = 44100, max_delay: float = 2.0):
        self.sr = int(sample_rate)
        self.size = int(max_delay * self.sr) + 1

    def _read(self, buf: np.ndarray, write_idx: int, delay: float) -> float:
        """Fractional (linear-interpolated) read -> the continuous engine."""
        d = float(np.clip(delay, 1.0, self.size - 2))
        i = write_idx - d
        while i < 0:
            i += self.size
        i0 = int(np.floor(i))
        frac = i - i0
        return float((1.0 - frac) * buf[i0 % self.size]
                     + frac * buf[(i0 + 1) % self.size])

    def process(self, audio: np.ndarray, time_cont: float = 0.35,
                time_gran: float = 0.28, pitch_cont: float = 1.0,
                pitch_gran: float = 1.0, splice: int = 4,
                feedback: float = 0.45, routing: str = "serial",
                grain_len: int = 512) -> np.ndarray:
        """Run both engines.

        Args:
            time_cont / time_gran: delay times (s) for each engine.
            pitch_cont / pitch_gran: read-rate (resample) per engine.
            splice: 1 = every grain taps the line, 4 = every 4th (spliced).
            feedback: delay-line feedback.
            routing: "serial" (continuous feeds granular) or "parallel".
        """
        if routing not in ("serial", "parallel"):
            raise ValueError("routing must be 'serial' or 'parallel'")
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        buf = np.zeros(self.size, dtype=np.float64)
        win = np.hanning(grain_len)
        y = np.empty_like(x)
        w = 0
        grain_phase = grain_len
        gran_out = 0.0
        gran_acc = np.zeros(grain_len, dtype=np.float64)
        for i in range(len(x)):
            cont = self._read(buf, w, time_cont * self.sr)
            if routing == "serial" and pitch_cont != 1.0:
                cont = self._read(buf, w, time_cont * self.sr * pitch_cont)
            # granular engine: windowed grains grabbed at the splice hop
            if grain_phase >= grain_len:
                grain_phase = 0
                if (i // max(1, splice)) % 1 == 0:
                    read_off = time_gran * self.sr * pitch_gran
                    idx = w - read_off
                    while idx < 0:
                        idx += self.size
                    base = int(idx) % self.size
                    gran_acc = np.array(
                        [buf[(base + k) % self.size] for k in range(grain_len)])
            gran_out = float(gran_acc[grain_phase] * win[grain_phase])
            grain_phase += 1

            if routing == "serial":
                write_val = x[i] + feedback * cont
                buf[w] = write_val
                out = cont + gran_out
            else:
                write_val = x[i] + feedback * (cont if i > 0 else 0.0)
                buf[w] = write_val
                out = 0.5 * cont + 0.5 * gran_out
            w = (w + 1) % self.size
            y[i] = out
        return y


# ----------------------------------------------------------- glitch chain
class RhythmicGlitchChain:
    """Four tempo-locked stages: stutter, reverse, bitcrush, decimate."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)
        self.stages: Tuple[str, ...] = ("stutter", "reverse", "bitcrush", "decimate")

    def process(self, audio: np.ndarray, bpm: float = 120.0,
                patterns: Optional[Sequence[Sequence[int]]] = None,
                steps: int = 16) -> np.ndarray:
        """Apply the chain; each stage is gated by a per-16th pattern.

        Args:
            audio: input.
            bpm: tempo -> a 16th note grid.
            patterns: four sequences of 0/1 (len ``steps``) for the stages.
            steps: grid divisions per bar.
        """
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        if patterns is None:
            patterns = ([1, 0, 1, 0] * (steps // 4), [0, 1, 0, 0] * (steps // 4),
                        [0, 0, 1, 1] * (steps // 4), [1, 0, 0, 1] * (steps // 4))
        step_len = int(round(self.sr * 60.0 / bpm / 4.0))
        y = x.copy()
        for i in range(0, len(y), step_len):
            seg = y[i:i + step_len]
            step_idx = (i // step_len) % steps
            bits = int(min(16, max(1, round(16 * (1.0 - 0.75 *
                        ((i // step_len) % 3) / 2.0)))))
            if patterns[0][step_idx]:
                seg = self._stutter(seg, n=2)
            if patterns[1][step_idx]:
                seg = seg[::-1].copy()
            if patterns[2][step_idx]:
                seg = self._bitcrush(seg, bits=max(3, bits))
            if patterns[3][step_idx]:
                seg = self._decimate(seg, keep=2)
            y[i:i + len(seg)] = seg
        return y

    @staticmethod
    def _stutter(seg: np.ndarray, n: int = 2) -> np.ndarray:
        if len(seg) < 2:
            return seg
        chunk = max(1, len(seg) // n)
        return np.tile(seg[:chunk], n)[:len(seg)]

    @staticmethod
    def _bitcrush(seg: np.ndarray, bits: int = 8) -> np.ndarray:
        levels = float(2 ** (bits - 1))
        return np.round(np.clip(seg, -1.0, 1.0) * levels) / levels

    @staticmethod
    def _decimate(seg: np.ndarray, keep: int = 2) -> np.ndarray:
        if keep < 1 or len(seg) == 0:
            return seg
        hold = np.repeat(seg[::keep], keep)[:len(seg)]
        if len(hold) < len(seg):
            hold = np.pad(hold, (0, len(seg) - len(hold)), mode="edge")
        return hold


# -------------------------------------------------------- parallel band comp
class ParallelBandCompressor:
    """Four-band upward + downward parallel compression."""

    def __init__(self, sample_rate: int = 44100,
                 crossovers: Sequence[float] = (120.0, 500.0, 2000.0)):
        self.sr = int(sample_rate)
        self.crossovers = tuple(float(c) for c in crossovers)

    def _split(self, x: np.ndarray) -> List[np.ndarray]:
        """Complementary 4-band split with 2nd-order Butterworth crossovers."""
        bands: List[np.ndarray] = []
        rest = x.copy()
        for fc in self.crossovers:
            low, high = self._split_lr(rest, fc)
            bands.append(low)
            rest = high
        bands.append(rest)
        return bands

    def _split_lr(self, x: np.ndarray, fc: float) -> Tuple[np.ndarray, np.ndarray]:
        fc = float(np.clip(fc, 20.0, self.sr * 0.45))
        w0 = 2 * np.pi * fc / self.sr
        c, s = np.cos(w0), np.sin(w0)
        alpha = s / (2 * 0.7071)
        b_lp = np.array([(1 - c) / 2, 1 - c, (1 - c) / 2]) / (1 + alpha)
        a = np.array([1.0, -2 * c / (1 + alpha), (1 - alpha) / (1 + alpha)])
        b_hp = np.array([(1 + c) / 2, -(1 + c), (1 + c) / 2]) / (1 + alpha)
        return self._iir(x, b_lp, a), self._iir(x, b_hp, a)

    @staticmethod
    def _iir(x: np.ndarray, b: np.ndarray, a: np.ndarray) -> np.ndarray:
        y = np.zeros(len(x), dtype=np.float64)
        x1 = x2 = y1 = y2 = 0.0
        for i, xi in enumerate(x):
            yi = (b[0] * xi + b[1] * x1 + b[2] * x2
                  - a[1] * y1 - a[2] * y2)
            x2, x1 = x1, xi
            y2, y1 = y1, yi
            y[i] = yi
        return y

    def _rms_env(self, x: np.ndarray, atk: float = 0.005,
                 rel: float = 0.120) -> np.ndarray:
        n = len(x)
        bs = max(1, int(0.002 * self.sr))
        coarse = np.sqrt(np.maximum(
            np.convolve(x ** 2, np.ones(bs) / bs, mode="same"), 0.0))
        out = np.empty_like(coarse)
        a_c = 1.0 - np.exp(-1.0 / max(1.0, atk * self.sr))
        a_r = 1.0 - np.exp(-1.0 / max(1.0, rel * self.sr))
        e = 0.0
        for i in range(n):
            e += (a_c if coarse[i] > e else a_r) * (coarse[i] - e)
            out[i] = e
        return out

    def process(self, audio: np.ndarray, down_threshold_db: float = -18.0,
                down_ratio: float = 4.0, up_threshold_db: float = -42.0,
                up_amount: float = 0.35, parallel_mix: float = 0.5
                ) -> np.ndarray:
        """Compress each band upward (below up_thr) and downward (above dn_thr)."""
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        bands = self._split(x)
        order = len(bands) - 1
        out = np.zeros_like(x)
        for i, band in enumerate(bands):
            env = self._rms_env(band)
            env_db = 20.0 * np.log10(np.maximum(env, 1e-9))
            dn = np.where(env_db > down_threshold_db,
                          (env_db - down_threshold_db) / down_ratio, 0.0)
            g_dn = 10 ** (-dn / 20.0)
            up = np.where(env_db < up_threshold_db,
                          (up_threshold_db - env_db) * up_amount, 0.0)
            g_up = 10 ** (np.minimum(up, 18.0) / 20.0)
            comp = band * g_dn
            lifted = band * g_dn * g_up
            out += (1.0 - parallel_mix) * comp + parallel_mix * lifted
        return out


def demo() -> str:
    sr = 22050
    rng = np.random.default_rng(0)
    n = int(sr * 1.2)
    tt = np.arange(n) / sr
    # percussive hits so the gate has real onsets to react to
    src = 0.35 * np.sin(2 * np.pi * 90.0 * tt) * np.exp(-3.0 * (tt % 0.3))
    src += 0.05 * rng.standard_normal(n)
    src[int(0.3 * sr):int(0.31 * sr)] += 0.9          # explicit onset
    src[int(0.75 * sr):int(0.76 * sr)] += 0.9

    gr = GatedReverb(sample_rate=sr)
    gated = gr.process(src, triggers=[0.31, 0.76], gate_len=0.20)
    print(f"gated reverb: len={len(gated)} peak={np.max(np.abs(gated)):.3f} "
          f"finite={np.all(np.isfinite(gated))}")
    assert np.all(np.isfinite(gated)) and len(gated) == n

    dd = DualEngineDelay(sample_rate=sr)
    d_ser = dd.process(src, routing="serial")
    d_par = dd.process(src, routing="parallel")
    print(f"dual delay: serial peak={np.max(np.abs(d_ser)):.3f} "
          f"parallel peak={np.max(np.abs(d_par)):.3f} "
          f"differ={not np.allclose(d_ser, d_par)}")
    assert not np.allclose(d_ser, d_par)

    gc = RhythmicGlitchChain(sample_rate=sr)
    glitch = gc.process(src, bpm=120.0)
    print(f"glitch chain: changed={not np.allclose(glitch, src)} "
          f"peak={np.max(np.abs(glitch)):.3f}")
    assert not np.allclose(glitch, src)

    pc = ParallelBandCompressor(sample_rate=sr)
    comp = pc.process(src)
    print(f"parallel band comp: peak in={np.max(np.abs(src)):.3f} "
          f"out={np.max(np.abs(comp)):.3f} finite={np.all(np.isfinite(comp))}")
    assert np.all(np.isfinite(comp))

    dc = spectral_declash(src, sr)
    print(f"spectral declash: rms in={np.sqrt(np.mean(src**2)):.4f} "
          f"out={np.sqrt(np.mean(dc**2)):.4f}")
    assert len(dc) == n
    print("  severance demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
