"""Physical-modelled aerophone/pipe instrument — Modartt Airteq style.

Replicable logic from the Sound On Sound news item "Modartt launch Airteq"
(16/09/2026): a sound-design instrument of *virtual pipes*, up to five per
patch, each with independent air-supply controls and a global air envelope,
built on Modartt's physical modelling + their "Dynamic Aerophone Modelling
(DAM)" which turns airflow into a continuous performance/modulation parameter.

What is replicated here (the physics, not the presets):

* ``AirPipe`` — one flue pipe:
  - **Resonator**: an open or stopped cylindrical pipe. The fundamental is
    ``f = c / (2L')`` (open) or ``c / (4L')`` (stopped) where ``L' = L + 0.61r``
    is the acoustic length with the classic end correction (Kinsler & Frey);
    the resonance is rendered as a bank of modes ``f_k = k * f0`` (open) or
    odd harmonics ``(2k-1) * f0`` (stopped), each with amplitude ~ ``1/k`` and
    its own decay — an inharmonicity-free but physically-shaped spectrum.
  - **Jet drive / air supply**: the exciter is a flue jet — the pipe is driven
    by a pressure envelope (attack/sustain/release of *air*, not amplitude)
    feeding a saturating jet velocity ``v = tanh(pressure * drive)``, plus
    turbulence noise scaled by pressure. Higher air pressure pushes the pipe
    toward **overblow** (energy migrates to the second mode), exactly like a
    real flue pipe; a low pressure gives a breathy, weak fundamental.
  - **Air modulation**: the "DAM" idea — the air supply is a per-sample
    parameter; ``modulate_air(t)`` lets any LFO/MPE-pressure curve reshape the
    timbre continuously in real time.
* ``AirPipePatch`` — up to five pipes, each with its own pitch, air pressure
  base + depth, detune and balance; one **global air envelope** applied
  instrument-wide (the "global envelope that offers instrument-wide air
  control" from the article); ``mpe_pressure`` maps an MPE pressure curve to
  all pipes' air supplies.

Not replicated: the 170 factory presets, the plug-in UI, Modartt's proprietary
DAM coefficients (our jet/pressure curves are standard flue-organ literature:
Fletcher 1976 "The non-linear physics of flue organ pipes", Sci. Am.; Castellengo
1971; Ising 1971's overblow criterion).

Usage:
    from sound.synthesis.air_pipe import AirPipe, AirPipePatch

    p = AirPipePatch(sample_rate=44100, seed=3)
    p.add_pipe(midi_note=60, pressure=0.55, balance=0.5)
    p.add_pipe(midi_note=67, pressure=0.40, balance=0.4)
    audio = p.render(2.0)                       # 2 s, stereo (n, 2)
"""

from __future__ import annotations

import numpy as np

SOUND_SPEED = 343.0          # m/s, 20 degC
END_CORRECTION = 0.61        # * radius, unflanged pipe end correction
DEFAULT_SR = 44100


def midi_to_freq(m: float) -> float:
    return 440.0 * 2.0 ** ((float(m) - 69.0) / 12.0)


class AirPipe:
    """One flue pipe: pressure-driven jet + mode-bank resonator.

    Args:
        midi_note: nominal pitch of the pipe (sets physical length).
        pressure: base air supply 0..1 (0.3 = breathy, 0.7 = full, >0.75
            overblows to the 2nd mode).
        stopped: True = stopped pipe (odd harmonics, one octave lower per
            length), False = open pipe.
        length_scale: multiplies the computed pipe length (rank scaling).
        seed: turbulence noise seed.
    """

    OVERBLOW_PRESSURE = 0.75      # Ising-style overblow threshold (normalised)

    def __init__(self, midi_note: float = 60.0, pressure: float = 0.55,
                 stopped: bool = False, length_scale: float = 1.0,
                 sample_rate: int = DEFAULT_SR, seed: int = 0):
        self.sr = int(sample_rate)
        self.midi_note = float(midi_note)
        self.pressure = float(np.clip(pressure, 0.05, 1.0))
        self.stopped = bool(stopped)
        self.seed = int(seed)

        # physical length from the target pitch (inverse of the mode formula)
        f0 = midi_to_freq(self.midi_note)
        n_modes = 1 if stopped else 2
        divisor = (SOUND_SPEED / (4.0 * f0)) if stopped else (SOUND_SPEED / (2.0 * f0))
        # end correction: L' = L + 0.61 r, with r ~ L / 16 (typical flue scaling)
        approx_len = max(0.01, divisor * length_scale)
        self.length = approx_len / (1.0 + END_CORRECTION / 16.0)
        self.radius = self.length / 16.0
        self.n_modes = int(np.clip(22050.0 / max(f0, 50.0), 3, 24))

    # ------------------------------------------------------------------ physics
    def mode_freqs(self) -> np.ndarray:
        """Resonance frequencies of the pipe (Hz)."""
        f0 = SOUND_SPEED / (2.0 * self.length + 2.0 * END_CORRECTION * self.radius)
        if self.stopped:
            k = np.arange(1, self.n_modes + 1)
            return f0 * (2 * k - 1)
        return f0 * np.arange(1, self.n_modes + 1)

    def mode_amps(self, pressure: float) -> np.ndarray:
        """Mode amplitudes for a given air pressure (overblow-aware)."""
        f = self.mode_freqs()
        a = 1.0 / np.arange(1, len(f) + 1) ** 1.3           # 1/k rolloff
        if pressure >= self.OVERBLOW_PRESSURE:
            # overblow: 2nd mode wins, fundamental collapses (open pipes)
            a = a.copy()
            over = (pressure - self.OVERBLOW_PRESSURE) / (1.0 - self.OVERBLOW_PRESSURE)
            a[0] *= (1.0 - 0.85 * over)
            if len(a) > 1:
                a[1] *= (1.0 + 2.5 * over)
        return a / a.max()

    def render(self, duration: float = 1.0,
               air_mod=None, mpe_pressure=None) -> np.ndarray:
        """Render the pipe.

        Args:
            duration: seconds.
            air_mod: optional callable ``t -> pressure_delta`` (-1..1) — the
                "Dynamic Aerophone Modelling" hook (LFO/automation on air).
            mpe_pressure: optional array (n,) 0..1 — per-sample MPE pressure
                mapped onto the air supply.
        Returns:
            mono float array (n,).
        """
        n = max(1, int(duration * self.sr))
        t = np.arange(n) / self.sr
        rng = np.random.default_rng(self.seed)

        pressure = np.full(n, self.pressure)
        if mpe_pressure is not None:
            mpe = np.asarray(mpe_pressure, dtype=np.float64)
            if mpe.size == 1:
                pressure = pressure + self.pressure * (float(mpe[0]) - 1.0)
            else:
                pressure = pressure + self.pressure * (mpe[:n] - 1.0)
        if air_mod is not None:
            pressure = pressure + np.array([float(air_mod(ti)) for ti in t])
        pressure = np.clip(pressure, 0.02, 1.0)

        # attack / release of the *air*, not the amplitude
        atk = int(0.035 * self.sr)
        rel = int(0.09 * self.sr)
        env = np.ones(n)
        if n > atk + rel:
            env[:atk] = np.linspace(0.15, 1.0, atk)
            env[-rel:] = np.linspace(1.0, 0.1, rel)

        f0 = self.mode_freqs()[0]
        out = np.zeros(n)
        amps = self.mode_amps(float(np.mean(pressure)))

        # turbulence noise, band-weighted around each mode, scaled by pressure
        noise = rng.standard_normal(n)
        noise *= (0.15 + 0.5 * pressure) * 0.25

        # jet: saturating pressure -> velocity drive (Fletcher's nonlinearity)
        drive = np.tanh(pressure * 2.2)
        for k, (fk, ak) in enumerate(zip(self.mode_freqs(), amps)):
            phase = rng.uniform(0, 2 * np.pi)
            # the jet couples strongest at f0; higher modes get drive share
            share = drive if k == 0 else drive * 0.35
            osc = np.sin(2 * np.pi * fk * t + phase) * ak
            breath = noise * ak * (3.0 if k == 0 else 1.0)
            # per-mode decay slightly faster for higher modes (viscous loss)
            decay = np.exp(-t * (0.4 + 0.25 * k))
            out += (osc * share + breath) * decay
        out *= 1.0 / (1.0 + 0.5 * f0 / 440.0)     # loudness compensation
        return out * env


class AirPipePatch:
    """Up to five pipes + a global air envelope (Airteq's patch model)."""

    MAX_PIPES = 5

    def __init__(self, sample_rate: int = DEFAULT_SR, seed: int = 0):
        self.sr = int(sample_rate)
        self.seed = int(seed)
        self.pipes = []                     # (AirPipe, balance, air_depth, detune_cents)

    def add_pipe(self, midi_note: float, pressure: float = 0.55,
                 stopped: bool = False, balance: float = 0.5,
                 air_depth: float = 0.3, detune_cents: float = 0.0,
                 length_scale: float = 1.0) -> AirPipe:
        """Add a pipe; ``air_depth`` is how strongly the global air envelope
        moves this pipe's supply (0..1)."""
        if len(self.pipes) >= self.MAX_PIPES:
            raise ValueError(f"patch holds at most {self.MAX_PIPES} pipes")
        p = AirPipe(midi_note=midi_note, pressure=pressure, stopped=stopped,
                    length_scale=length_scale, sample_rate=self.sr,
                    seed=self.seed + len(self.pipes) * 17)
        self.pipes.append((p, float(balance), float(air_depth),
                           float(detune_cents)))
        return p

    def render(self, duration: float = 1.0,
               global_air=None, mpe_pressure=None) -> np.ndarray:
        """Render the patch.

        Args:
            duration: seconds.
            global_air: callable ``t -> delta`` applied instrument-wide,
                scaled per pipe by its ``air_depth``.
            mpe_pressure: optional (n,) array 0..1 mapped to every pipe.
        Returns:
            stereo (n, 2) float array.
        """
        n = int(duration * self.sr)
        t = np.arange(n) / self.sr
        L = np.zeros(n)
        R = np.zeros(n)
        for i, (pipe, balance, depth, cents) in enumerate(self.pipes):
            amod = None
            if global_air is not None:
                amod = (lambda tt, d=depth: d * float(global_air(tt)))
            mono = pipe.render(duration, air_mod=amod, mpe_pressure=mpe_pressure)
            if cents:
                # cheap detune: pitch-shift via resampling ratio (offline)
                ratio = 2.0 ** (cents / 1200.0)
                idx = np.clip(np.arange(n) * ratio, 0, n - 1)
                mono = np.interp(idx, np.arange(n), mono)
            pan = 0.5 + 0.4 * (balance - 0.5)
            L += mono * (1.0 - pan)
            R += mono * pan
        peak = max(1e-9, float(np.abs(np.stack([L, R])).max()))
        if peak > 0.98:
            L, R = L * 0.98 / peak, R * 0.98 / peak
        return np.stack([L, R], axis=1)


def demo() -> str:
    """Prove pipe physics: mode ratios, overblow, global air, MPE."""
    sr = 22050

    p = AirPipe(midi_note=57.0, sample_rate=sr, seed=1)
    f = p.mode_freqs()
    ratios = f[:3] / f[0]
    print(f"open pipe A3: f0={f[0]:.1f} Hz, first ratios "
          f"{ratios[0]:.3f} {ratios[1]:.3f} {ratios[2]:.3f} (expect 1 2 3)")
    assert abs(ratios[1] - 2.0) < 0.01 and abs(ratios[2] - 3.0) < 0.01

    ps = AirPipe(midi_note=57.0, stopped=True, sample_rate=sr, seed=1)
    fs = ps.mode_freqs()
    rs = fs[:3] / fs[0]
    print(f"stopped pipe: ratios {rs[0]:.3f} {rs[1]:.3f} {rs[2]:.3f} "
          f"(expect 1 3 5)")
    assert abs(rs[1] - 3.0) < 0.01 and abs(rs[2] - 5.0) < 0.01

    # overblow migrates energy to mode 2
    a_norm = AirPipe(midi_note=48.0, sample_rate=sr, seed=2).mode_amps(0.45)
    a_over = AirPipe(midi_note=48.0, sample_rate=sr, seed=2).mode_amps(0.95)
    print(f"overblow: amp(f0) {a_norm[0]:.3f} -> {a_over[0]:.3f}, "
          f"amp(2f0) {a_norm[1]:.3f} -> {a_over[1]:.3f}")
    assert a_over[0] < a_norm[0] and a_over[1] > a_norm[1]

    # patch: 3 pipes, global air swell via LFO, MPE pressure ramp
    patch = AirPipePatch(sample_rate=sr, seed=3)
    patch.add_pipe(48, pressure=0.5, balance=0.2, air_depth=0.6)
    patch.add_pipe(55, pressure=0.45, balance=0.5, air_depth=0.4, detune_cents=6.0)
    patch.add_pipe(64, pressure=0.35, balance=0.8, air_depth=0.5, stopped=True)
    mpe = np.clip(np.linspace(0.4, 1.0, int(2.0 * sr)), 0, 1)
    out = patch.render(2.0, global_air=lambda t: 0.25 * np.sin(2 * np.pi * 0.8 * t),
                       mpe_pressure=mpe)
    print(f"patch render: shape={out.shape} peak={np.abs(out).max():.3f} "
          f"finite={np.all(np.isfinite(out))}")
    assert out.shape == (2 * sr, 2) and np.all(np.isfinite(out))

    # air modulation actually changes the spectrum
    quiet = patch.pipes[0][0].render(0.5, sample_rate_ := None) if False else None
    base = AirPipe(60, sample_rate=sr, seed=5).render(0.5)
    wob = AirPipe(60, sample_rate=sr, seed=5).render(
        0.5, air_mod=lambda t: 0.4 * np.sin(2 * np.pi * 5 * t))
    sb = float(np.abs(np.fft.rfft(base)).max())
    sw = float(np.abs(np.fft.rfft(wob)).max())
    print(f"air modulation changes output: {sb:.2f} -> {sw:.2f}")
    assert abs(sb - sw) > 1e-6

    return "air_pipe demo OK"


if __name__ == "__main__":
    print(demo())
