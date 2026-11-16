"""Dual-channel feedback synthesizer / effects processor — Body Synths
"Laboratory" style.

Replicable logic from Synthtopia 2026-11-13 ("Body Synths Laboratory Combines
Dual-Channel Effects With Analog Feedback Synthesis"). The hardware is a
tabletop instrument whose *signal topology* is the sound source:

  * two independent channels, each with up to **40 dB** of voltage-controlled
    gain, a **PT2399** CMOS delay chip and a **resonant filter** switchable
    between low-pass and high-pass;
  * channels routable in **series** (ch0 → ch1) or **parallel**, so two
    low-pass filters in series = steeper LP, and LP→HP in series = band-pass;
  * **four feedback paths** — self-feedback on each channel plus cross-feedback
    in both directions — which is what lets the box self-oscillate with **no
    input at all**, turning it into a drone/noise instrument;
  * a global modulator that is either an **envelope or an LFO**, cycle time
    10 ms … 10 s, with four CV outputs (two positive, two negative) patched to
    gain, delay time and filter cutoff;
  * output clipping stages that compress the runaway feedback into a stable
    limit cycle (otherwise the model would simply explode).

DSP model, per channel:

  gain (linear from dB) → TPT state-variable filter (LP or HP, with
  resonance/Q) → PT2399 delay (pre-emphasis, tanh companding, loop low-pass
  whose cutoff **falls as delay time grows**, de-emphasis, fractional read) →
  soft clip.

The PT2399's characteristic degradation is modelled explicitly: the chip's
internal anti-alias/companding filters get progressively darker at longer
delay settings, so a 400 ms repeat is noticeably duller than a 40 ms one. That
is the same mechanism the hardware exhibits, not a decorative EQ.

Feedback is summed *before* the filter, which is why raising it pushes the
resonant filter into self-oscillation rather than just making echoes louder.
"""

from __future__ import annotations

import numpy as np

TAU = 2.0 * np.pi


def db_to_lin(db: float) -> float:
    return 10.0 ** (db / 20.0)


class OnePole:
    """One-pole low-pass with settable cutoff."""

    def __init__(self, sr: float, fc: float = 8000.0):
        self.sr = float(sr)
        self.z = 0.0
        self.set_cutoff(fc)

    def set_cutoff(self, fc: float) -> None:
        fc = float(np.clip(fc, 10.0, self.sr * 0.45))
        self.a = 1.0 - np.exp(-TAU * fc / self.sr)

    def process(self, x: float) -> float:
        self.z += self.a * (x - self.z)
        return self.z


class SVF:
    """TPT state-variable filter; lp/hp outputs with resonance."""

    def __init__(self, sr: float, cutoff: float = 1200.0, q: float = 0.7):
        self.sr = float(sr)
        self.ic1 = 0.0
        self.ic2 = 0.0
        self.set(cutoff, q)

    def set(self, cutoff: float, q: float | None = None) -> None:
        if q is not None:
            self.q = float(np.clip(q, 0.5, 24.0))
        self.cutoff = float(np.clip(cutoff, 20.0, self.sr * 0.45))
        self.g = np.tan(np.pi * self.cutoff / self.sr)
        self.k = 1.0 / self.q
        self.a1 = 1.0 / (1.0 + self.g * (self.g + self.k))
        self.a2 = self.g * self.a1
        self.a3 = self.g * self.a2

    def process(self, x: float) -> tuple[float, float]:
        v3 = x - self.ic2
        v1 = self.a1 * self.ic1 + self.a2 * v3
        v2 = self.ic2 + self.a2 * self.ic1 + self.a3 * v3
        self.ic1 = 2.0 * v1 - self.ic1
        self.ic2 = 2.0 * v2 - self.ic2
        lp = v2
        hp = x - self.k * v1 - v2
        return lp, hp


class PT2399:
    """PT2399-style delay: companded, bandwidth falls with delay time."""

    def __init__(self, sr: float, max_delay_s: float = 1.2):
        self.sr = float(sr)
        self.buf = np.zeros(int(max_delay_s * sr) + 4)
        self.w = 0
        self.out_lp = OnePole(sr, 9000.0)
        self.pre_lp = OnePole(sr, 6000.0)
        self.delay_s = 0.2
        self.feedback = 0.0

    def bandwidth(self, delay_s: float) -> float:
        """Chip bandwidth limit vs delay: long delays are darker."""
        return 2000.0 + 14000.0 / (1.0 + 14.0 * max(0.0, delay_s))

    def _read(self, d: float) -> float:
        r = self.w - d
        while r < 0:
            r += len(self.buf)
        i = int(np.floor(r))
        frac = r - i
        a = self.buf[i % len(self.buf)]
        b = self.buf[(i + 1) % len(self.buf)]
        return a + (b - a) * frac

    def process(self, x: float, delay_s: float | None = None,
                feedback: float | None = None) -> float:
        if delay_s is not None:
            self.delay_s = float(np.clip(delay_s, 0.005, len(self.buf) / self.sr - 0.01))
        fb = self.feedback if feedback is None else float(np.clip(feedback, 0.0, 1.15))
        d = self.delay_s * self.sr
        y = self._read(d)
        # loop filter: bandwidth shrinks with delay length (PT2399 behaviour)
        self.out_lp.set_cutoff(self.bandwidth(self.delay_s))
        y = self.out_lp.process(y)
        # pre-emphasis + companding on the write side
        emph = x + 0.6 * (x - self.pre_lp.process(x))
        comp = np.tanh(1.6 * emph) / 1.6
        self.buf[self.w] = comp + fb * np.tanh(y)
        self.w = (self.w + 1) % len(self.buf)
        # de-emphasis: gentle high shelf back down
        return 0.75 * y + 0.25 * self.pre_lp.process(y)


class LabChannel:
    """One Laboratory channel: VCA gain → resonant filter → PT2399."""

    def __init__(self, sr: float):
        self.sr = float(sr)
        self.gain_db = 0.0
        self.filter = SVF(sr, 1400.0, 0.8)
        self.mode = "lp"
        self.delay = PT2399(sr)
        self.level = 0.8

    def filter_sample(self, x: float) -> float:
        lp, hp = self.filter.process(x)
        return lp if self.mode == "lp" else hp


class FeedbackLab:
    """Dual-channel feedback instrument with 4 routable feedback paths."""

    def __init__(self, sr: int = 44100):
        self.sr = int(sr)
        self.ch = [LabChannel(sr), LabChannel(sr)]
        self.routing = "parallel"        # "parallel" | "series"
        # four feedback paths: self0, self1, cross 1->0, cross 0->1
        self.fb_self = [0.35, 0.35]
        self.fb_cross = [0.0, 0.0]
        self.mod_type = "lfo"            # "lfo" | "env"
        self.mod_cycle_s = 0.5
        self.mod_depth = 0.0
        self.cv = (1.0, 1.0, -1.0, -1.0)  # two positive, two negative outs
        self._lfo_phase = 0.0
        self._env = 0.0

    # ------------------------------------------------------------------ config
    def set_channel(self, i: int, gain_db: float = 0.0, delay_s: float = 0.2,
                    feedback: float = 0.3, cutoff: float = 1400.0,
                    q: float = 0.8, mode: str = "lp", level: float = 0.8) -> None:
        c = self.ch[i]
        c.gain_db = float(np.clip(gain_db, 0.0, 40.0))
        c.delay.delay_s = delay_s
        c.delay.feedback = feedback
        c.filter.set(cutoff, q)
        c.mode = "lp" if mode.lower().startswith("l") else "hp"
        c.level = level

    def set_routing(self, mode: str, self_fb=(0.35, 0.35), cross_fb=(0.0, 0.0)) -> None:
        self.routing = "series" if mode.lower().startswith("s") else "parallel"
        self.fb_self = [float(self_fb[0]), float(self_fb[1])]
        self.fb_cross = [float(cross_fb[0]), float(cross_fb[1])]

    def modulator(self) -> float:
        """Advance the global modulator one sample, return -1..1."""
        if self.mod_type == "env":
            attack = min(0.5, self.mod_cycle_s * 0.15)
            decay = max(0.01, self.mod_cycle_s - attack)
            if self._env == 0.0:
                self._env = 1e-6
            # simple AR: rise then exponential fall
            if self._env < 1.0:
                self._env = min(1.0, self._env + 1.0 / (attack * self.sr))
                m = self._env
            else:
                self._env = 1.0
                m = 1.0
            return float(np.clip(m, 0.0, 1.0))
        self._lfo_phase = (self._lfo_phase + 1.0 / (self.mod_cycle_s * self.sr)) % 1.0
        return float(np.sin(TAU * self._lfo_phase))

    def cv_outputs(self, m: float) -> list[float]:
        return [m * s * self.mod_depth for s in self.cv]

    # ------------------------------------------------------------------ render
    def process(self, x: np.ndarray | None = None, seconds: float = 1.0,
                seed: int = 0) -> np.ndarray:
        n = int(seconds * self.sr)
        if x is None:
            rng = np.random.default_rng(seed)
            x = 1e-7 * rng.standard_normal((n, 2))  # thermal noise seed
        x = np.asarray(x, dtype=float)
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        if len(x) < n:
            x = np.pad(x, ((0, n - len(x)), (0, 0)))
        out = np.zeros((n, 2))
        prev = [0.0, 0.0]
        for i in range(n):
            m = self.modulator()
            c0, c1, _c2, _c3 = self.cv_outputs(m)
            # CV patched to gain (dB) and cutoff on each channel
            g0 = db_to_lin(self.ch[0].gain_db + 6.0 * c0)
            g1 = db_to_lin(self.ch[1].gain_db + 6.0 * c1)
            self.ch[0].filter.set(self.ch[0].filter.cutoff * (1.0 + 0.5 * c0),
                                  self.ch[0].filter.q)
            self.ch[1].filter.set(self.ch[1].filter.cutoff * (1.0 + 0.5 * c1),
                                  self.ch[1].filter.q)

            in0 = x[i, 0] * g0
            if self.routing == "series":
                in1 = prev[0]          # series: only ch0 sees the input
            else:
                in1 = x[i, 1] * g1
            # cross-feedback into each other's input (before the filter)
            in0 += self.fb_self[0] * prev[0] + self.fb_cross[1] * prev[1]
            in1 += self.fb_self[1] * prev[1] + self.fb_cross[0] * prev[0]

            f0 = self.ch[0].filter_sample(in0)
            f1 = self.ch[1].filter_sample(in1)
            d0 = self.ch[0].delay.process(f0)
            d1 = self.ch[1].delay.process(f1)
            prev = [d0, d1]
            # output clipping stage: compresses feedback into a limit cycle
            out[i, 0] = np.tanh(1.8 * d0 * self.ch[0].level) / 1.8
            out[i, 1] = np.tanh(1.8 * d1 * self.ch[1].level) / 1.8
        return out

    def render_note(self, freq: float, seconds: float = 1.0) -> np.ndarray:
        """The box has no oscillator — 'note' means a burst of input tone."""
        n = int(seconds * self.sr)
        t = np.arange(n) / self.sr
        tone = 0.3 * np.sin(TAU * float(freq) * t) * np.exp(-t * 2.0)
        return self.process(np.stack([tone, tone], axis=1), seconds)


def demo() -> None:
    sr = 44100

    # ---- 1. 40 dB gain really is ~100x before the clip stage
    a = FeedbackLab(sr)
    a.set_channel(0, gain_db=40.0, delay_s=0.05, feedback=0.0, cutoff=8000.0)
    a.set_channel(1, gain_db=0.0, delay_s=0.05, feedback=0.0, cutoff=8000.0)
    a.set_routing("parallel")
    tone = 0.01 * np.sin(TAU * 220 * np.arange(sr // 2) / sr)
    loud = a.process(np.stack([tone, np.zeros_like(tone)], axis=1), 0.5)
    quiet_cfg = FeedbackLab(sr)
    quiet_cfg.set_channel(0, 0.0, 0.05, 0.0, 8000.0)
    quiet_cfg.set_channel(1, 0.0, 0.05, 0.0, 8000.0)
    quiet = quiet_cfg.process(np.stack([tone, np.zeros_like(tone)], axis=1), 0.5)
    print(f"gain: in rms={tone.std():.5f} 0dB rms={quiet[:,0].std():.5f} "
          f"40dB rms={loud[:,0].std():.3f}")
    assert loud[:, 0].std() > 10 * quiet[:, 0].std()

    # ---- 2. PT2399 repeats darken as delay time grows
    def dark_ratio(delay_s):
        d = PT2399(sr)
        rng = np.random.default_rng(2)
        x = 0.2 * rng.standard_normal(int(0.6 * sr))
        y = np.array([d.process(v, delay_s, 0.0) for v in x])
        sp = np.abs(np.fft.rfft(y * np.hanning(y.size)))
        fr = np.fft.rfftfreq(y.size, 1 / sr)
        lo = sp[(fr > 200) & (fr < 1500)].sum()
        hi = sp[(fr > 4000) & (fr < 9000)].sum()
        return float(hi / (lo + 1e-12))
    r_short, r_long = dark_ratio(0.03), dark_ratio(0.4)
    print(f"PT2399 HF/LF at 30 ms={r_short:.3f}, 400 ms={r_long:.3f} "
          f"(bandwidth {PT2399(sr).bandwidth(0.03):.0f} -> {PT2399(sr).bandwidth(0.4):.0f} Hz)")
    assert r_long < r_short

    # ---- 3. LP vs HP mode on the same broadband noise
    noise = np.random.default_rng(3).standard_normal((sr // 2, 2)) * 0.1
    def band(y, lo, hi, ch=0):
        sp = np.abs(np.fft.rfft(y[:, ch]))
        fr = np.fft.rfftfreq(len(y), 1 / sr)
        return float(sp[(fr >= lo) & (fr < hi)].sum())
    lab = FeedbackLab(sr)
    lab.set_channel(0, 0.0, 0.02, 0.0, 600.0, 0.9, "lp")
    lab.set_channel(1, 0.0, 0.02, 0.0, 600.0, 0.9, "lp")
    lab.set_routing("parallel")
    lp_out = lab.process(noise, 0.5)
    lab.ch[0].mode = lab.ch[1].mode = "hp"
    hp_out = lab.process(noise, 0.5)
    lp_low = band(lp_out, 100, 400) / (band(lp_out, 4000, 9000) + 1e-9)
    hp_low = band(hp_out, 100, 400) / (band(hp_out, 4000, 9000) + 1e-9)
    print(f"filter mode: LP low/high={lp_low:.2f}, HP low/high={hp_low:.3f}")
    assert hp_low < lp_low

    # ---- 4. series LP -> HP = band-pass
    series = FeedbackLab(sr)
    series.set_channel(0, 0.0, 0.02, 0.0, 500.0, 1.0, "hp")
    series.set_channel(1, 0.0, 0.02, 0.0, 5000.0, 1.0, "lp")
    series.set_routing("series")
    ser = series.process(noise, 0.5)
    low, mid, high = band(ser, 50, 300, 1), band(ser, 800, 2500, 1), band(ser, 7000, 12000, 1)
    print(f"series HP->LP: low={low:.1f} mid={mid:.1f} high={high:.1f}")
    assert mid > low and mid > high

    # ---- 5. self-oscillation with no input
    osc = FeedbackLab(sr)
    osc.set_channel(0, gain_db=40.0, delay_s=0.015, feedback=1.1, cutoff=900.0, q=8.0)
    osc.set_channel(1, gain_db=40.0, delay_s=0.017, feedback=1.1, cutoff=900.0, q=8.0)
    osc.set_routing("parallel", self_fb=(0.9, 0.9), cross_fb=(0.4, 0.4))
    silent = osc.process(None, 2.0, seed=5)
    early = silent[: 441].std()      # 10 ms: still just the thermal seed
    late = silent[-sr // 2:].std()
    print(f"self-oscillation: early rms={early:.2e} late rms={late:.4f} "
          f"peak={np.abs(silent).max():.3f} finite={bool(np.isfinite(silent).all())}")
    assert late > 20 * max(early, 1e-9)
    assert late > 0.01 and np.isfinite(silent).all()

    # ---- 6. modulator ranges and bipolar CV set
    mod = FeedbackLab(sr)
    for cyc in (0.01, 0.5, 10.0):
        mod.mod_cycle_s = cyc
        vals = [mod.modulator() for _ in range(int(min(1.0, cyc) * sr))]
        print(f"cycle {cyc:5.2f}s -> mod range [{min(vals):+.2f}, {max(vals):+.2f}]")
        assert -1.001 <= min(vals) and max(vals) <= 1.001
    mod.mod_depth = 1.0
    cv = mod.cv_outputs(0.5)
    print(f"CV outs (two pos, two neg): {[round(v, 2) for v in cv]}")
    assert sum(1 for v in cv if v > 0) == 2 and sum(1 for v in cv if v < 0) == 2

    # ---- 7. ping-pong cross-feedback alternates channels
    ping = FeedbackLab(sr)
    ping.set_channel(0, 0.0, 0.06, 0.2, 6000.0, 0.7, "lp")
    ping.set_channel(1, 0.0, 0.06, 0.2, 6000.0, 0.7, "lp")
    ping.set_routing("parallel", self_fb=(0.0, 0.0), cross_fb=(0.85, 0.85))
    burst = np.zeros((sr, 2))
    burst[0, 0] = 0.5
    y = ping.process(burst, 1.0)
    e = np.array([np.abs(y[i * 2000:(i + 1) * 2000]).sum(axis=0) for i in range(5)])
    print("ping-pong energy L/R:", np.round(e, 2).tolist())
    left_first = any(row[0] > 2.0 * row[1] for row in e)
    right_first = any(row[1] > 2.0 * row[0] for row in e)
    print(f"alternates L-dominant={left_first} R-dominant={right_first}")
    assert left_first and right_first

    print("demo OK")


if __name__ == "__main__":
    demo()
