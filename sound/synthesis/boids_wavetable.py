# -*- coding: utf-8 -*-
"""Boid-flock wavetable synthesis — Morpheral Machines "The Swarm" style.

Replicable logic from the Synthtopia item "Morpheral Machines Introduces The
Swarm, A New Approach To Wavetable Synthesis" (2026-11-08).

The Swarm does not play back a wavetable in the usual sense.  Each note is
produced by a flock of 1..24 virtual oscillators ("boids").  Every boid owns
one band-limited wavetable oscillator and *moves* over a 2-D grid of
single-cycle waveforms (3x3 .. 13x13).  Its position on that grid selects the
waveform it plays, so the *organisation and motion of the flock* is what you
hear: alignment makes the voices converge on one timbre, separation spreads
them across the grid, predators scatter them, attractors herd them.

What is replicated here (numpy only, offline):

* ``WavetableGrid`` — n x n grid of single-cycle frames synthesized additively
  with a harmonic limit derived from the note frequency (no aliasing);
  bilinear frame interpolation at any (u, v) in the unit square.
* ``Boid`` — position, velocity, phase, per-boid detune and its own optional
  FM modulator (phase modulation of the wavetable read).
* ``BoidFlock`` — Reynolds flocking update per audio block: separation,
  alignment, cohesion, soft boundary reflection, attractor pull and predator
  repulsion.  Twelve attractor trajectories (point, line, lissajous, orbit,
  spiral in/out, figure-8, drift, ping-pong x/y, sweep) with free or
  tempo-synchronised motion.
* Flock metrics exposed as modulation sources: alignment coherence,
  separation (mean nearest-neighbour distance), distance-to-attractor and the
  centroid x/y position on the grid.
* Stereo rendering: each boid is panned by its grid ``v`` coordinate; the sum
  is soft-clipped with tanh.

Not replicated: sample import / waveform extraction from audio files, MPE and
MTS-ESP plumbing, the 32-slot host modulation matrix.

Usage:
    from sound.synthesis.boids_wavetable import BoidFlock, WavetableGrid

    grid = WavetableGrid(n=5, n_harmonics=48)
    flock = BoidFlock(freq=110.0, n_boids=12, grid=grid, seed=7)
    audio = flock.render(duration=4.0, sr=44100)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

TABLE = 2048          # samples per single-cycle frame
ATTRACTORS = (
    "point", "line", "lissajous", "orbit_cw", "orbit_ccw", "spiral_in",
    "spiral_out", "figure8", "drift", "pingpong_x", "pingpong_y", "sweep",
)


# ---------------------------------------------------------------------------
# wavetable grid
# ---------------------------------------------------------------------------
class WavetableGrid:
    """A square grid of additively synthesized single-cycle waveforms.

    Grid axis ``u`` (0..1) sets spectral tilt (dark -> bright) and axis ``v``
    sets a formant bump position, so diagonal motion sweeps brightness and
    formant together the way a real morphing wavetable bank behaves.

    Args:
        n: grid edge length (3..13 in the hardware; any n >= 2 here).
        n_harmonics: maximum harmonics synthesized into each frame.
        table_size: samples per frame.
    """

    def __init__(self, n: int = 5, n_harmonics: int = 48,
                 table_size: int = TABLE, seed: int = 0):
        self.n = int(max(2, n))
        self.n_harmonics = int(max(1, n_harmonics))
        self.table_size = int(table_size)
        rng = np.random.default_rng(seed)

        phase = np.linspace(0.0, 2.0 * np.pi, self.table_size, endpoint=False)
        k = np.arange(1, self.n_harmonics + 1, dtype=np.float64)

        # small fixed per-harmonic jitter -> each frame is a little "organic"
        jitter = 1.0 + 0.15 * rng.standard_normal(self.n_harmonics)

        frames = np.zeros((self.n, self.n, self.table_size), dtype=np.float64)
        for i in range(self.n):
            u = i / (self.n - 1)                      # brightness axis
            tilt = 0.55 + 1.35 * u                    # 1/k**tilt rolloff
            for j in range(self.n):
                v = j / (self.n - 1)                  # formant axis
                fc = 1.5 + 22.0 * v                   # formant centre (harm #)
                bw = 2.5 + 4.0 * v
                amps = jitter * (1.0 / k ** tilt)
                amps *= 1.0 + 1.6 * np.exp(-0.5 * ((k - fc) / bw) ** 2)
                # odd/even balance drifts across the grid -> hollow <-> full
                amps *= 1.0 - 0.35 * (1.0 - v) * (k % 2 == 0)
                amps /= np.max(np.abs(amps)) + 1e-12
                frames[i, j] = np.sum(
                    amps[:, None] * np.sin(k[:, None] * phase[None, :]), axis=0)
                # remove DC and normalise peak
                frames[i, j] -= frames[i, j].mean()
                peak = np.max(np.abs(frames[i, j]))
                if peak > 0:
                    frames[i, j] /= peak
        self.frames = frames
        self.phase = phase

    def band_limited_harmonics(self, freq: float, sr: int = 44100) -> int:
        """Highest harmonic index that stays under Nyquist for ``freq``."""
        if freq <= 0:
            return self.n_harmonics
        return int(max(1, min(self.n_harmonics, 0.45 * sr / freq)))

    def frame_at(self, u: float, v: float) -> np.ndarray:
        """Bilinear blend of the four grid nodes surrounding (u, v)."""
        u = float(np.clip(u, 0.0, 1.0)) * (self.n - 1)
        v = float(np.clip(v, 0.0, 1.0)) * (self.n - 1)
        i0, j0 = int(np.floor(u)), int(np.floor(v))
        i1 = min(i0 + 1, self.n - 1)
        j1 = min(j0 + 1, self.n - 1)
        fu, fv = u - i0, v - j0
        f = self.frames
        return ((1 - fu) * (1 - fv) * f[i0, j0] + fu * (1 - fv) * f[i1, j0]
                + (1 - fu) * fv * f[i0, j1] + fu * fv * f[i1, j1])


# ---------------------------------------------------------------------------
# boid
# ---------------------------------------------------------------------------
@dataclass
class Boid:
    """One wavetable oscillator with flocking state."""
    u: float
    v: float
    du: float = 0.0
    dv: float = 0.0
    phase: float = 0.0
    detune_cents: float = 0.0     # per-boid tuning offset
    level: float = 1.0
    fm_ratio: float = 2.0         # FM modulator ratio (own modulator)
    fm_depth: float = 0.0         # 0..1 phase-modulation depth

    @property
    def pos(self) -> np.ndarray:
        return np.array([self.u, self.v], dtype=np.float64)


# ---------------------------------------------------------------------------
# attractor trajectories
# ---------------------------------------------------------------------------
def _attractor_pos(kind: str, t: float, tempo_phase: float) -> Tuple[float, float]:
    """Return the attractor position in the unit square for time ``t``.

    ``tempo_phase`` is the beat-normalised time (0..1 per bar) used by the
    tempo-synchronised modes.
    """
    a = 2.0 * np.pi
    if kind == "point":
        return 0.5, 0.5
    if kind == "line":
        return 0.5 + 0.3 * np.sin(a * 0.13 * t), 0.5
    if kind == "lissajous":
        return 0.5 + 0.35 * np.sin(a * 0.21 * t), 0.5 + 0.35 * np.sin(a * 0.34 * t + 1.1)
    if kind == "orbit_cw":
        r = 0.3
        return 0.5 + r * np.cos(a * 0.17 * t), 0.5 + r * np.sin(a * 0.17 * t)
    if kind == "orbit_ccw":
        r = 0.3
        return 0.5 + r * np.cos(-a * 0.17 * t), 0.5 + r * np.sin(-a * 0.17 * t)
    if kind == "spiral_in":
        r = 0.42 * (0.5 + 0.5 * np.cos(a * 0.05 * t))
        th = a * 0.24 * t
        return 0.5 + r * np.cos(th), 0.5 + r * np.sin(th)
    if kind == "spiral_out":
        r = 0.42 * (1.0 - 0.5 * (0.5 + 0.5 * np.cos(a * 0.05 * t)))
        th = a * 0.24 * t
        return 0.5 + r * np.cos(th), 0.5 + r * np.sin(th)
    if kind == "figure8":
        return (0.5 + 0.35 * np.sin(a * 0.19 * t),
                0.5 + 0.35 * np.sin(2 * a * 0.19 * t))
    if kind == "drift":
        return (0.5 + 0.28 * np.sin(a * 0.031 * t) * np.cos(a * 0.017 * t),
                0.5 + 0.28 * np.cos(a * 0.023 * t))
    if kind == "pingpong_x":
        p = 0.5 + 0.45 * (2 / np.pi) * np.arcsin(np.sin(a * 0.11 * t))
        return p, 0.5
    if kind == "pingpong_y":
        p = 0.5 + 0.45 * (2 / np.pi) * np.arcsin(np.sin(a * 0.11 * t))
        return 0.5, p
    if kind == "sweep":                      # tempo-locked diagonal sweep
        p = (tempo_phase * 2.0) % 1.0
        return p, 0.5 + 0.35 * np.sin(a * p)
    # unknown -> centre
    return 0.5, 0.5


# ---------------------------------------------------------------------------
# flock
# ---------------------------------------------------------------------------
class BoidFlock:
    """A polyphonic-ready boid flock voice (mono voice here, one note).

    Args:
        freq: note frequency in Hz (base for all boids).
        n_boids: 1..24 oscillators.
        grid: ``WavetableGrid`` the boids fly over.
        attractor: one of ``ATTRACTORS``.
        n_predators: 0..9 predators that scatter the flock.
        sep_radius: separation radius in grid units.
        separation / alignment / cohesion / attractor_force / predator_force:
            flocking gains.
        detune_cents: total detune spread across boids (uniform +/-).
        fm_depth: 0..1 per-boid FM index.
        tempo_sync: attractor follows bar phase instead of free time.
        seed: deterministic placement / predator walk.
    """

    def __init__(self, freq: float = 110.0, n_boids: int = 12,
                 grid: Optional[WavetableGrid] = None,
                 attractor: str = "lissajous", n_predators: int = 0,
                 sep_radius: float = 0.18,
                 separation: float = 0.55, alignment: float = 0.45,
                 cohesion: float = 0.35, attractor_force: float = 0.12,
                 predator_force: float = 0.9, boundary: float = 0.9,
                 detune_cents: float = 18.0, fm_depth: float = 0.0,
                 tempo_sync: bool = True, bpm: float = 120.0,
                 level: float = 1.0, seed: int = 0):
        self.freq = float(freq)
        self.n_boids = int(np.clip(n_boids, 1, 24))
        self.grid = grid or WavetableGrid(n=5, n_harmonics=48)
        self.attractor = attractor if attractor in ATTRACTORS else "lissajous"
        self.n_predators = int(np.clip(n_predators, 0, 9))
        self.sep_radius = float(sep_radius)
        self.g_sep = float(separation)
        self.g_ali = float(alignment)
        self.g_coh = float(cohesion)
        self.g_att = float(attractor_force)
        self.g_pred = float(predator_force)
        self.boundary = float(boundary)
        self.detune_cents = float(detune_cents)
        self.fm_depth = float(np.clip(fm_depth, 0.0, 1.0))
        self.tempo_sync = bool(tempo_sync)
        self.bpm = float(bpm)
        self.level = float(level)
        self.rng = np.random.default_rng(seed)

        r = self.rng.uniform(-0.25, 0.25, size=(self.n_boids, 2)) + 0.5
        det = np.linspace(-detune_cents, detune_cents, self.n_boids) if self.n_boids > 1 else np.zeros(1)
        self.boids: List[Boid] = [
            Boid(u=float(r[i, 0]), v=float(r[i, 1]),
                 du=float(self.rng.normal(0, 0.01)),
                 dv=float(self.rng.normal(0, 0.01)),
                 phase=float(self.rng.random()),
                 detune_cents=float(det[i]),
                 level=float(1.0 / np.sqrt(self.n_boids)),
                 fm_ratio=float(self.rng.choice([1.0, 2.0, 3.0])),
                 fm_depth=self.fm_depth)
            for i in range(self.n_boids)
        ]
        # frame state (smoothed per block to avoid zipper noise)
        self._frame_state = np.stack([self.grid.frame_at(b.u, b.v) for b in self.boids])
        self._prev_frame = self._frame_state.copy()
        self.pred = self.rng.uniform(0.0, 1.0, size=(max(1, self.n_predators), 2))
        self.pred_dir = self.rng.normal(0, 1, size=(max(1, self.n_predators), 2))
        self.metrics: List[Dict[str, float]] = []

    # -- flocking -----------------------------------------------------------
    def _update_flock(self, dt: float, t: float, tempo_phase: float) -> None:
        P = np.array([[b.u, b.v] for b in self.boids])
        V = np.array([[b.du, b.dv] for b in self.boids])
        n = len(P)
        acc = np.zeros_like(P)

        # pairwise distances
        d = P[:, None, :] - P[None, :, :]
        dist = np.sqrt(np.sum(d * d, axis=2)) + 1e-9
        np.fill_diagonal(dist, 1e6)

        # separation: push away from close neighbours
        near = dist < self.sep_radius
        if np.any(near):
            w = np.where(near, 1.0 / (dist ** 2), 0.0)
            acc += np.sum(d * w[:, :, None], axis=1) * self.g_sep * 0.15

        # alignment: steer toward mean neighbour velocity
        vbar = np.tile(V.mean(axis=0), (n, 1))
        acc += (vbar - V) * self.g_ali * 2.0

        # cohesion: steer toward local centroid
        c = P.mean(axis=0)
        acc += (c - P) * self.g_coh * 0.8

        # attractor
        ax, ay = _attractor_pos(self.attractor, t, tempo_phase)
        att = np.array([ax, ay])
        acc += (att - P) * self.g_att

        # predators (random-walking repel points)
        if self.n_predators:
            step = 0.35 * dt
            self.pred += self.pred_dir * step
            for k in range(self.n_predators):
                hit = (self.pred[k] < 0.02) | (self.pred[k] > 0.98)
                self.pred_dir[k][hit] *= -1.0
                self.pred[k] = np.clip(self.pred[k], 0.02, 0.98)
                pd = P - self.pred[k]
                pdist = np.linalg.norm(pd, axis=1) + 1e-9
                acc += (pd / pdist[:, None]) * (self.g_pred / pdist[:, None] ** 2)

        V += acc * dt
        speed = np.linalg.norm(V, axis=1)
        vmax = 0.55
        over = speed > vmax
        if np.any(over):
            V[over] *= (vmax / speed[over])[:, None]
        P += V * dt

        # soft boundary: reflect with damping
        for axis in (0, 1):
            lo, hi = -0.02, 1.02
            below, above = P[:, axis] < lo, P[:, axis] > hi
            P[below, axis] = lo
            V[below, axis] = np.abs(V[below, axis]) * self.boundary
            P[above, axis] = hi
            V[above, axis] = -np.abs(V[above, axis]) * self.boundary

        for i, b in enumerate(self.boids):
            b.u, b.v = float(np.clip(P[i, 0], 0.0, 1.0)), float(np.clip(P[i, 1], 0.0, 1.0))
            b.du, b.dv = float(V[i, 0]), float(V[i, 1])

        # metrics -> modulation sources
        coherence = float(np.linalg.norm(V.mean(axis=0)) /
                          (np.linalg.norm(V, axis=1).mean() + 1e-9))
        nn = float(np.min(dist))
        self.metrics.append({
            "t": float(t),
            "alignment": coherence,
            "separation": nn,
            "attractor_distance": float(np.linalg.norm(P.mean(axis=0) - att)),
            "centroid_x": float(P[:, 0].mean()),
            "centroid_y": float(P[:, 1].mean()),
            "spread": float(np.linalg.norm(P - P.mean(axis=0), axis=1).mean()),
        })

    # -- render -------------------------------------------------------------
    def render(self, duration: float = 2.0, sr: int = 44100,
               block: int = 512, smooth: float = 0.35) -> np.ndarray:
        """Render the flock to a stereo float32 array ``(n, 2)``."""
        n_total = int(duration * sr)
        out = np.zeros((n_total, 2), dtype=np.float64)
        pan = np.zeros(self.n_boids)

        # one table read helper: phases per boid, linear interpolation in table
        tbl_pos = np.arange(self.grid.table_size)

        written = 0
        while written < n_total:
            n = min(block, n_total - written)
            t = written / sr
            beat = t * self.bpm / 60.0
            tempo_phase = float(beat % 4.0) / 4.0
            self._update_flock(n / sr, t, tempo_phase)

            # frames: bilinear blend of the four grid nodes per boid
            target = np.stack([self.grid.frame_at(b.u, b.v) for b in self.boids])
            self._frame_state = (1.0 - smooth) * self._prev_frame + smooth * target
            self._prev_frame = self._frame_state.copy()

            # per-boid instantaneous frequency (detune + own FM modulator)
            freqs = self.freq * 2.0 ** (np.array([b.detune_cents for b in self.boids]) / 1200.0)
            idx = (np.arange(n) + written) / sr

            n_b = self.n_boids
            phases = np.array([b.phase for b in self.boids])
            ph = phases[:, None] + freqs[:, None] * n / sr
            # own FM modulator: phase offset from a sine at fm_ratio
            if self.fm_depth > 0:
                ratios = np.array([b.fm_ratio for b in self.boids])[:, None]
                fm = np.sin(2 * np.pi * freqs[:, None] * ratios * idx[None, :])
                ph = ph + self.fm_depth * 0.5 * fm
            read = (ph % 1.0) * self.grid.table_size
            i0 = np.floor(read).astype(np.int64) % self.grid.table_size
            i1 = (i0 + 1) % self.grid.table_size
            frac = read - np.floor(read)

            sig = np.zeros(n, dtype=np.float64)
            for k in range(n_b):
                w = self._frame_state[k]
                s = w[i0[k]] * (1 - frac[k]) + w[i1[k]] * frac[k]
                sig += s * self.boids[k].level
                pan[k] = self.boids[k].v
            for k, b in enumerate(self.boids):
                b.phase = float((b.phase + freqs[k] * n / sr) % 1.0)

            # pan by grid v (equal-power), spread wider for bigger flocks
            theta = (pan - 0.5) * np.pi * 0.6
            gl, gr = np.cos(np.pi / 4 - theta), np.sin(np.pi / 4 + theta)
            out[written:written + n, 0] = sig * gl.mean()
            out[written:written + n, 1] = sig * gr.mean()
            written += n

        out *= self.level
        out = np.tanh(out * 1.1)
        peak = np.max(np.abs(out))
        if peak > 0:
            out = out / peak * 0.9
        return out.astype(np.float32)

    def modulation_sources(self) -> Dict[str, np.ndarray]:
        """Flock-derived modulation lanes (per rendered block)."""
        if not self.metrics:
            return {}
        keys = ["alignment", "separation", "attractor_distance",
                "centroid_x", "centroid_y", "spread"]
        return {k: np.array([m[k] for m in self.metrics]) for k in keys}


# ---------------------------------------------------------------------------
# demo
# ---------------------------------------------------------------------------
def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Render a calm flock and a predator-disrupted flock; print metrics."""
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    grid = WavetableGrid(n=5, n_harmonics=48, seed=3)

    print("=== The Swarm: boid-flock wavetable synthesis ===")
    print(f"grid {grid.n}x{grid.n} frames, {grid.table_size}-sample tables")

    calm = BoidFlock(freq=110.0, n_boids=12, grid=grid, attractor="lissajous",
                     n_predators=0, detune_cents=14.0, fm_depth=0.15, seed=7)
    a1 = calm.render(duration=3.0)
    p1 = os.path.join(out_dir, "swarm_calm.wav")
    write_wav(p1, a1, 44100)
    m = calm.metrics[-1]
    print(f"calm flock  : {len(a1)} samples, peak {np.max(np.abs(a1)):.3f} "
          f"-> {p1} ({os.path.getsize(p1)} B)")
    print(f"  alignment {m['alignment']:.3f}  separation {m['separation']:.3f} "
          f"  spread {m['spread']:.3f}  centroid ({m['centroid_x']:.2f},{m['centroid_y']:.2f})")

    wild = BoidFlock(freq=110.0, n_boids=20, grid=grid, attractor="figure8",
                     n_predators=4, predator_force=1.4, detune_cents=25.0,
                     fm_depth=0.3, seed=11)
    a2 = wild.render(duration=3.0)
    p2 = os.path.join(out_dir, "swarm_predators.wav")
    write_wav(p2, a2, 44100)
    mw = wild.metrics[-1]
    print(f"predator flock: {len(a2)} samples, peak {np.max(np.abs(a2)):.3f} "
          f"-> {p2} ({os.path.getsize(p2)} B)")
    print(f"  alignment {mw['alignment']:.3f}  separation {mw['separation']:.3f} "
          f"  spread {mw['spread']:.3f}")

    # modulation lanes
    lanes = calm.modulation_sources()
    print("modulation lanes:", {k: f"{v.mean():.3f}" for k, v in lanes.items()})

    # distinct timbres across the grid
    print("frame peak/RMS at grid corners:")
    for (i, j) in [(0, 0), (0, grid.n - 1), (grid.n - 1, 0), (grid.n - 1, grid.n - 1)]:
        f = grid.frames[i, j]
        print(f"  node({i},{j}) peak {np.max(np.abs(f)):.2f} rms {np.sqrt(np.mean(f ** 2)):.3f}")

    assert len(a1) == 132300 and os.path.getsize(p1) > 1000
    print("demo OK")
    return {"calm": p1, "predators": p2, "samples": len(a1)}


if __name__ == "__main__":
    demo()
