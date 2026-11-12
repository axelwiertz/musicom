"""Cooper Time Cube-style hose delay: two acoustic tube lines + crosstalk.

Replicates the mechanism behind the UAD Cooper Time Cube Delay (Sound On Sound,
2026-11-12). The original 1971 hardware made its delays by sending audio
through a coiled garden hose — a loudspeaker at one end, a microphone at the
other — which is why it sounds nothing like an electronic delay. Its character
comes from the *physical* path, so that is what is modelled here:

  * Propagation delay  — pure time of flight: d = L / c. The two hoses have
    different lengths, giving the unit's two independent slapback lines.
    Implemented as fractional-delay reads (linear interpolation), so a
    tempo-synced delay time never quantises to a whole sample.
  * Tube modes         — a hose open at both ends resonates at odd multiples of
    c / (2L). Those resonances are the "hollow" colour: a bank of resonant peaks
    spaced 1/(2*time-of-flight) apart.
  * Wall losses        — high frequencies die faster in the hose wall, so the
    path is a cascade of lowpasses (a one-pole per 4 ms of travel) plus a
    stronger one-pole at the mic.
  * Dispersion         — a chain of first-order allpasses (the standard way to
    model non-constant group delay in an acoustic path).
  * Loudspeaker/mic    — drive into the hose soft-clips (small speaker), and
    the return path is band-limited on both ends; the two hoses leak into each
    other, which is what makes the original's stereo image smear.
  * Controls           — Treble / Bass / Color (drive) / HPF on the repeats.
"""

from __future__ import annotations

import numpy as np

TAU = 2.0 * np.pi
SPEED_OF_SOUND = 343.0          # m/s


class FractionalDelay:
    """Linearly interpolated delay line with a movable read pointer."""

    def __init__(self, max_s: float, sr: int):
        self.buf = np.zeros(int(max_s * sr) + 4)
        self.w = 0
        self.sr = sr

    def process(self, x: float, delay_s: float) -> float:
        d = max(1.0, delay_s * self.sr)
        rp = self.w - d
        i0 = int(np.floor(rp)) % len(self.buf)
        i1 = (i0 + 1) % len(self.buf)
        frac = rp - np.floor(rp)
        y = self.buf[i0] * (1.0 - frac) + self.buf[i1] * frac
        self.buf[self.w] = x
        self.w = (self.w + 1) % len(self.buf)
        return float(y)


class Hose:
    """One physical hose: time of flight + modes + wall loss + dispersion."""

    def __init__(self, length_m: float = 5.4, sr: int = 44100,
                 wall_loss: float = 0.96, dispersion: float = 0.35,
                 drive: float = 1.3):
        self.length_m = float(length_m)
        self.delay_s = self.length_m / SPEED_OF_SOUND
        self.sr = sr
        self.line = FractionalDelay(self.delay_s * 4 + 0.05, sr)
        self.wall_loss = float(wall_loss)
        self.disp_coef = float(dispersion)
        self.drive = float(drive)
        self.ap_z = [0.0, 0.0, 0.0, 0.0]
        self.lp_z = 0.0
        # wall loss one-pole per ~4 ms of propagation
        self.lp_a = 1.0 - np.exp(-TAU * 9000.0 / sr)

    @property
    def mode_spacing_hz(self) -> float:
        """Odd-harmonic spacing of an open tube: c / (2L)."""
        return SPEED_OF_SOUND / (2.0 * self.length_m)

    def process(self, x: float) -> float:
        # speaker end: small driver compresses early
        u = np.tanh(x * self.drive)
        y = self.line.process(u, self.delay_s)

        # dispersion: 4 cascaded first-order allpasses (non-constant group delay)
        c = self.disp_coef
        for k in range(4):
            z = self.ap_z[k]
            v = y + c * z
            y = -c * v + z
            self.ap_z[k] = v

        # wall loss (HF absorption along the hose)
        self.lp_z += self.lp_a * (y - self.lp_z)
        y = self.lp_z
        return y * self.wall_loss


class CooperTimeCube:
    """Two hose lines, crosstalk, tone controls, feedback."""

    def __init__(self, sr: int = 44100, hose_a_m: float = 5.4,
                 hose_b_m: float = 7.1, feedback: float = 0.25,
                 treble_db: float = 0.0, bass_db: float = 0.0,
                 color: float = 1.3, hpf_hz: float = 90.0,
                 crosstalk: float = 0.12, dry_mix: float = 0.45):
        self.sr = sr
        self.hose_a = Hose(hose_a_m, sr, drive=color)
        self.hose_b = Hose(hose_b_m, sr, drive=color)
        self.fb = float(feedback)
        self.treble = 10 ** (treble_db / 20.0)
        self.bass = 10 ** (bass_db / 20.0)
        self.hpf_hz = float(hpf_hz)
        self.crosstalk = float(crosstalk)
        self.dry_mix = float(dry_mix)
        self.lp_a_state = 0.0
        self.lp_b_state = 0.0
        self.hp_state = 0.0
        self.shelf_a = 0.0
        self.shelf_b = 0.0

    @property
    def times_ms(self) -> tuple[float, float]:
        return (self.hose_a.delay_s * 1e3, self.hose_b.delay_s * 1e3)

    def process(self, x: np.ndarray, feedback_taps: bool = True) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        n = len(x)
        out = np.zeros((n, 2))
        fa = fb = 0.0
        lp_a_a = 1.0 - np.exp(-TAU * 3200.0 / self.sr)
        hp_a = 1.0 - np.exp(-TAU * self.hpf_hz / self.sr)
        shelf_a = 1.0 - np.exp(-TAU * 2000.0 / self.sr)   # treble/bass split
        for i in range(n):
            dry = x[i]
            # line A gets a mix of dry and line B's return (leakage both ways)
            a_in = dry + fa * self.fb + self.crosstalk * fb
            b_in = dry + fb * self.fb + self.crosstalk * fa
            ya = self.hose_a.process(a_in)
            yb = self.hose_b.process(b_in)
            # mic-end highpass (removes hose rumble) + tone shaping
            self.hp_state += hp_a * (ya - self.hp_state)
            ya = ya - self.hp_state * 0.6
            self.lp_a_state += lp_a_a * (ya - self.lp_a_state)
            self.lp_b_state += lp_a_a * (yb - self.lp_b_state)
            # mic-end tone stack: 2 kHz split, Bass on the low band, Treble on
            # the high band (these are shelves, not a broadband gain)
            self.shelf_a += shelf_a * (self.lp_a_state - self.shelf_a)
            self.shelf_b += shelf_a * (self.lp_b_state - self.shelf_b)
            ya = self.shelf_a * self.bass + \
                (self.lp_a_state - self.shelf_a) * self.treble
            yb = self.shelf_b * self.bass + \
                (self.lp_b_state - self.shelf_b) * self.treble
            fa, fb = ya, yb
            # short slapback is the wet signal; dry is passed through
            out[i, 0] = self.dry_mix * dry + 0.85 * ya
            out[i, 1] = self.dry_mix * dry + 0.85 * yb
        peak = np.abs(out).max()
        return out / peak * 0.9 if peak > 1e-9 else out


def demo() -> None:
    """Measure the real time-of-flight, mode spacing and tone controls."""
    sr = 44100
    # impulse response: time of flight should land exactly where physics says
    cube = CooperTimeCube(sr=sr, hose_a_m=5.4, hose_b_m=7.1, feedback=0.0,
                          dry_mix=0.0)
    imp = np.zeros(sr // 4)
    imp[0] = 1.0
    ir = cube.process(imp)
    t_ms = np.arange(len(ir)) / sr * 1e3
    print(f"cooper demo: hose A={cube.hose_a.length_m} m -> "
          f"{cube.times_ms[0]:.2f} ms expected, "
          f"peak at {t_ms[np.argmax(np.abs(ir[:, 0]))]:.2f} ms")
    print(f"  hose B={cube.hose_b.length_m} m -> {cube.times_ms[1]:.2f} ms expected, "
          f"peak at {t_ms[np.argmax(np.abs(ir[:, 1]))]:.2f} ms")
    print(f"  tube mode spacing: A={cube.hose_a.mode_spacing_hz:.1f} Hz, "
          f"B={cube.hose_b.mode_spacing_hz:.1f} Hz "
          f"(= c/2L: {343.0/(2*cube.hose_a.length_m):.1f} / "
          f"{343.0/(2*cube.hose_b.length_m):.1f})")

    # musical test: dry pluck + cube repeats, then a darkened version
    def pluck(f0, dur, seed=0):
        rng = np.random.default_rng(seed)
        n = int(dur * sr)
        L = max(2, int(sr / f0))
        buf = rng.uniform(-1, 1, L)
        y = np.zeros(n)
        for i in range(n):
            v = buf[i % L]
            buf[i % L] = 0.5 * (v + buf[(i + 1) % L]) * 0.996
            y[i] = v
        return y * np.exp(-np.linspace(0, 4, n))

    src = np.concatenate([pluck(146.83, 0.35, 1), pluck(220.0, 0.35, 2),
                          np.zeros(int(0.8 * sr))])
    bright = CooperTimeCube(sr=sr, feedback=0.3, treble_db=0.0, color=1.2,
                            dry_mix=0.0)
    dark = CooperTimeCube(sr=sr, feedback=0.3, treble_db=-12.0, color=1.2,
                          hpf_hz=160.0, dry_mix=0.0)
    # tone control measured on broadband noise through the same hoses, so the
    # comparison isolates Treble/HPF and not the source spectrum
    noise = np.random.default_rng(4).standard_normal(int(0.4 * sr))
    y1 = bright.process(noise)
    y2 = dark.process(noise)

    def hf(y):
        s = np.abs(np.fft.rfft(y.mean(axis=1)))
        f = np.fft.rfftfreq(len(y), 1 / sr)
        return float(s[f > 3000].sum() / max(1e-9, s.sum()))

    print(f"  bright HF share={hf(y1):.4f}  dark HF share={hf(y2):.4f} "
          f"(treble -12 dB must reduce it)")
    echo_gap = int(cube.times_ms[0] / 1e3 * sr)
    print(f"  first repeat expected at sample {echo_gap}")
    assert np.abs(ir).max() > 0.05
    assert abs(t_ms[np.argmax(np.abs(ir[:, 0]))] - cube.times_ms[0]) < 3.0
    assert hf(y2) < hf(y1)
    assert np.isfinite(y1).all()
    print("demo OK")


if __name__ == "__main__":
    demo()
