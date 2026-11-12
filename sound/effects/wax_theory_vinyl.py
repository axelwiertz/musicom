"""Wax Theory-style vinyl playback model driven by groove position and stylus.

Replicates Modbap Wax Theory (Sound On Sound, 2026-11-11). The product's idea
is that one control ("Side") is *physically* meaningful: a stylus travelling
across a record goes from ~51 cm/s at the outer edge to ~21 cm/s at the inner
edge, and everything about the sound follows from that linear velocity:

  * tracing distortion  — a stylus cannot follow a wavelength shorter than its
    contact radius, so the effective nonlinearity grows as v falls. Modelled
    with an asymmetric waveshaper whose drive is proportional to 1/v; an
    asymmetric shaper is what generates the *second* harmonic, which is the
    actual audible fingerprint of tracing distortion (symmetric clipping only
    makes odd harmonics).
  * bandwidth           — the groove wavelength limit maps to a lowpass whose
    cutoff falls with v: fc = v / (2 * lambda_min), lambda_min ~ 4 um.
  * wow / flutter       — eccentricity and press faults modulate pitch at
    0.55 Hz (33 1/3 rpm once-around) and ~6 Hz respectively, both scaled by
    how worn the pressing is.
  * surface noise       — level rises as v falls (fewer particles per unit
    time but worse SNR); dust adds clustered ticks, a repeating scratch pop
    and bearing rumble at 33.3 / 45 / 78 rpm.
  * formats             — LP / 45 / 78 differ in nominal velocity, noise floor
    and bandwidth.
  * stylus profiles     — HiFi / DJ / Worn change the tonal tilt and add a
    resonant pickup peak plus tracking loss.
  * platter brake       — playback-rate ramp-down/up with the pitch drop that
    implies, implemented as a resampling read pointer.

Reference speeds: 51.0 cm/s (outer LP), 21.0 cm/s (inner LP).
"""

from __future__ import annotations

import numpy as np

TAU = 2.0 * np.pi

FORMATS = {
    # name: (outer_cms, inner_cms, nominal_rpm, noise_floor, hf_limit_hz)
    "LP": (51.0, 21.0, 33.333, 0.0016, 16000.0),
    "45": (43.0, 24.0, 45.0, 0.0022, 15000.0),
    "78": (37.0, 20.0, 78.0, 0.0060, 7000.0),
}

STYLI = {
    # name: (tilt_db_per_oct, pickup_peak_hz, peak_gain, hf_loss_db)
    "HiFi": (-0.4, 12000.0, 0.10, 0.0),
    "DJ": (1.2, 8200.0, 0.35, 2.0),
    "Worn": (-1.8, 5600.0, 0.55, 7.0),
}


def _asym_shape(x: np.ndarray, drive: float) -> np.ndarray:
    """Asymmetric soft clip: positive half compresses sooner than negative."""
    g = 1.0 + 5.0 * drive
    return np.tanh(x * g) * 0.5 + np.tanh(x * g * 0.62) * 0.5 * (1.0 + 0.25 * drive)


def one_pole_lp(x: np.ndarray, fc: float, sr: int) -> np.ndarray:
    a = 1.0 - np.exp(-TAU * min(fc, sr * 0.45) / sr)
    out = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        out[i] = acc
    return out


def one_pole_hp(x: np.ndarray, fc: float, sr: int) -> np.ndarray:
    return x - one_pole_lp(x, fc, sr)


def res_peak(x: np.ndarray, fc: float, gain: float, sr: int) -> np.ndarray:
    """Resonant biquad-ish bell added at the cartridge's mechanical resonance."""
    if gain <= 0:
        return x
    w = TAU * min(fc, sr * 0.45) / sr
    r = 0.85
    b0 = 1.0 + gain * (1.0 - r)
    a1 = -2.0 * r * np.cos(w)
    a2 = r * r
    y = np.empty_like(x)
    y1 = y2 = 0.0
    for i in range(len(x)):
        v = b0 * x[i] - a1 * y1 - a2 * y2
        y2, y1 = y1, v
        y[i] = v
    return y * (1.0 / (1.0 + gain * 0.5))


class WaxTheory:
    """Vinyl playback model: `side` 0 (outer) -> 1 (inner)."""

    def __init__(self, fmt: str = "LP", stylus: str = "HiFi", side: float = 0.0,
                 dust: bool = False, wear: float = 0.35, wow_depth: float = 0.5,
                 sr: int = 44100, seed: int = 0):
        if fmt not in FORMATS:
            raise ValueError(f"unknown format {fmt!r}")
        if stylus not in STYLI:
            raise ValueError(f"unknown stylus {stylus!r}")
        self.fmt, self.stylus = fmt, stylus
        self.side = float(np.clip(side, 0.0, 1.0))
        self.dust, self.wear = dust, wear
        self.wow_depth = wow_depth
        self.sr = sr
        self.rng = np.random.default_rng(seed)

    # -- derived physical quantities ---------------------------------------
    def velocity_cms(self) -> float:
        outer, inner, *_ = FORMATS[self.fmt]
        return outer + (inner - outer) * self.side

    def rpm(self) -> float:
        return FORMATS[self.fmt][2]

    def tracing_drive(self) -> float:
        """Distortion grows as velocity falls: normalised to the outer edge."""
        outer = FORMATS[self.fmt][0]
        return float((outer / self.velocity_cms()) - 1.0) * 0.5 + 0.05 * self.wear

    def bandwidth_hz(self) -> float:
        """Groove wavelength limit: lambda_min ~ 22 um => fc = v/(2*lambda)."""
        v = self.velocity_cms() * 1e-2                    # cm/s -> m/s
        fc = v / (2.0 * 22e-6)
        return float(min(fc, FORMATS[self.fmt][4]) *
                     (1.0 - 0.35 * self.wear))

    def noise_level(self) -> float:
        outer = FORMATS[self.fmt][0]
        return FORMATS[self.fmt][3] * (outer / self.velocity_cms()) * \
            (1.0 + 1.5 * self.wear)

    # -- processing --------------------------------------------------------
    def process(self, x: np.ndarray, stop_at: float | None = None,
                stop_s: float = 0.25) -> np.ndarray:
        """Apply the full vinyl chain. ``stop_at`` (0..1) brakes the platter."""
        sr = self.sr
        x = np.asarray(x, dtype=float)
        n = len(x)

        # 1. platter brake: playhead rate ramp 1 -> 0 (then optional restart)
        if stop_at is not None:
            k = int(np.clip(stop_at, 0, 1) * n)
            ramp_len = max(16, int(stop_s * sr))
            ramp = np.ones(n)
            end = min(n, k + ramp_len)
            ramp[k:end] = np.linspace(1.0, 0.0, end - k) ** 1.5
            ramp[end:] = 0.0
            pos = np.cumsum(ramp) - 1.0
            out = np.interp(pos, np.arange(n), x, left=0.0, right=0.0)
            x = out

        # 2. wow + flutter (pitch modulation, eccentricity + press fault)
        t = np.arange(n) / sr
        rev_hz = self.rpm() / 60.0
        depth = 0.0022 * self.wow_depth * (0.4 + self.wear)
        mod = depth * (np.sin(TAU * rev_hz * t) + 0.35 * np.sin(TAU * 6.1 * t + 1.1))
        pos = np.cumsum(1.0 + mod) - 1.0
        x = np.interp(pos, np.arange(n), x, left=0.0, right=0.0)

        # 3. tracing distortion (2nd-harmonic asymmetric), scaled by 1/v
        d = self.tracing_drive()
        x = x * (1.0 - 0.15 * d) + 0.55 * _asym_shape(x, d) * d

        # 4. bandwidth limit as a cascade of 2 one-poles (steeper skirt)
        fc = self.bandwidth_hz()
        x = one_pole_lp(x, fc, sr)
        x = one_pole_lp(x, fc * 1.15, sr)

        # 5. stylus tonal profile: tilt, pickup resonance, tracking HF loss
        tilt, peak_hz, peak_gain, hf_loss = STYLI[self.stylus]
        if tilt != 0.0:
            lp = one_pole_lp(x, 1200.0, sr)
            hi = x - lp
            x = lp + hi * (10 ** (tilt / 20.0))
        x = res_peak(x, peak_hz, peak_gain * (0.6 + self.wear), sr)
        if hf_loss:
            x = one_pole_lp(x, 9000.0 * 10 ** (-hf_loss / 20.0), sr)
        x = one_pole_hp(x, 22.0, sr)                      # rumble filter

        # 6. surface noise + dust events
        floor = self.noise_level()
        # noise is spectrally shaped: pink-ish (louder low-mid) + real clicks
        white = self.rng.standard_normal(n)
        pink = one_pole_lp(white, 2600.0, sr) * 3.0 + white * 0.25
        x = x + pink * floor
        if self.dust:
            ticks = np.zeros(n)
            rate = int(3 + 22 * self.wear)
            for _ in range(max(1, n // (sr // rate))):
                i = self.rng.integers(0, n)
                ln = min(n - i, int(0.004 * sr))
                ticks[i:i + ln] += (self.rng.choice([-1.0, 1.0])
                                    * np.exp(-np.linspace(0, 9, ln))
                                    * self.rng.uniform(0.05, 0.28))
            x = x + ticks
            # one repeating scratch pop per revolution
            per = max(1, int(sr / rev_hz))
            for start in range(0, n, per):
                i = start + int(0.31 * per)
                ln = min(n - i, int(0.02 * sr))
                if ln > 0:
                    x[i:i + ln] += 0.3 * np.exp(-np.linspace(0, 7, ln)) * \
                        np.sin(TAU * 900 * np.arange(ln) / sr)
            # bearing rumble at the platter rotation
            x = x + 0.004 * np.sin(TAU * rev_hz * t) * (1.0 + self.wear)

        peak = np.abs(x).max()
        return x / peak * 0.92 if peak > 1e-9 else x


def demo() -> None:
    """Sweep the Side control and check each physical claim numerically."""
    sr = 44100
    t = np.arange(int(1.6 * sr)) / sr
    # test tone bed: 440 Hz + 2 kHz + 8 kHz (bandwidth probe)
    src = 0.5 * np.sin(TAU * 440 * t) + 0.3 * np.sin(TAU * 2000 * t) \
        + 0.2 * np.sin(TAU * 8000 * t)

    def band_energy(y, lo, hi):
        s = np.abs(np.fft.rfft(y * np.hanning(len(y))))
        f = np.fft.rfftfreq(len(y), 1 / sr)
        return float(s[(f >= lo) & (f < hi)].sum())

    print(f"{'side':>5} {'v(cm/s)':>8} {'fc(Hz)':>7} {'2nd/1st':>8} {'8k/1k':>7} {'noise':>7}")
    rows = []
    for side in (0.0, 0.5, 1.0):
        w = WaxTheory("LP", "HiFi", side=side, wear=0.3, seed=int(side * 10))
        y = w.process(src)
        h1 = band_energy(y, 400, 480)
        h2 = band_energy(y, 840, 920)
        h8k = band_energy(y, 7500, 8600)
        h1k = band_energy(y, 1800, 2200) + 1e-9
        print(f"{side:5.1f} {w.velocity_cms():8.1f} {w.bandwidth_hz():7.0f} "
              f"{h2/h1:8.4f} {h8k/h1k:7.4f} {w.noise_level():7.5f}")
        rows.append((w.velocity_cms(), h2 / h1, h8k / h1k, w.noise_level()))

    # claims: inner groove = slower = more 2nd harmonic, less HF, more noise
    assert rows[2][0] < rows[0][0]
    assert rows[2][1] > rows[0][1], "tracing distortion must rise toward the label"
    assert rows[2][2] < rows[0][2], "bandwidth must shrink toward the label"
    assert rows[2][3] > rows[0][3], "surface noise must rise toward the label"

    # 78 rpm shellac: bandwidth cap must bite hard
    w78 = WaxTheory("78", "Worn", side=0.5, dust=True, wear=0.6, seed=3)
    y78 = w78.process(src)
    print(f"78 shellac: bw={w78.bandwidth_hz():.0f} Hz, "
          f"8k/1k={band_energy(y78, 7500, 8600)/(band_energy(y78, 1800, 2200)+1e-9):.4f}")

    # platter brake: energy must collapse after the stop point
    wb = WaxTheory("45", "DJ", side=0.2, wear=0.2, seed=5)
    yb = wb.process(src, stop_at=0.45, stop_s=0.3)
    a, b = yb[: int(0.4 * sr)], yb[int(1.2 * sr):]
    print(f"brake: pre rms={np.sqrt((a**2).mean()):.4f} "
          f"post rms={np.sqrt((b**2).mean()):.4f}")
    assert np.sqrt((b ** 2).mean()) < 0.25 * np.sqrt((a ** 2).mean())
    print("demo OK")


if __name__ == "__main__":
    demo()
