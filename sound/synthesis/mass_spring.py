"""Mass-spring physical modeling — ANUKARI-style 3D physics synth core.

Objects = bodies (position/velocity), springs (Hooke + damping), exciters
(collision impulse injection), microphones (sample displacement at point).

Reference: surveillance report Aug 2026, ANUKARI.

This is the small-scale CPU implementation (numpy/Verlet), not GPU realtime.

Usage:
    from sound.synthesis.mass_spring import MassSpringSystem, Body, Spring

    system = MassSpringSystem(sample_rate=44100)
    b1 = system.add_body(pos=(0.0, 0.0, 0.0))
    b2 = system.add_body(pos=(0.1, 0.0, 0.0))
    system.add_spring(b1, b2, stiffness=1000.0, damping=0.01)
    system.excite(b1, impulse=(0.0, 0.5, 0.0))
    audio = system.render_mic(b1, duration=1.0)  # displacement of b1
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any

__all__ = ["MassSpringSystem", "Body", "Spring"]


class Body:
    """A mass point in 3D space (ANUKARI 'body')."""

    def __init__(self, pos: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 mass: float = 1.0, fixed: bool = False):
        self.pos = np.array(pos, dtype=float)
        self.vel = np.zeros(3)
        self.mass = mass
        self.fixed = fixed
        self.id: Optional[int] = None  # assigned by system


class Spring:
    """A Hooke's law spring connecting two bodies."""

    def __init__(self, a: Body, b: Body,
                 stiffness: float = 1000.0, damping: float = 0.01,
                 rest_length: Optional[float] = None):
        self.a = a
        self.b = b
        self.k = stiffness
        self.c = damping
        if rest_length is None:
            self.rest_length = float(np.linalg.norm(a.pos - b.pos))
        else:
            self.rest_length = rest_length


class MassSpringSystem:
    """Small-scale mass-spring physical modeling system.

    Integrates body motion with Verlet-like semi-implicit Euler.
    Excitation = impulse injection; microphone = displacement at point.

    Parameters
    ----------
    sample_rate : int
        Step rate (samples/second).  Each step advances the sim by 1/sr.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate
        self.bodies: List[Body] = []
        self.springs: List[Spring] = []
        self._next_id = 0

    def add_body(self, pos: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 mass: float = 1.0, fixed: bool = False) -> Body:
        """Add a body and return it."""
        body = Body(pos=pos, mass=mass, fixed=fixed)
        body.id = self._next_id
        self._next_id += 1
        self.bodies.append(body)
        return body

    def add_spring(self, a: Body, b: Body,
                   stiffness: float = 1000.0, damping: float = 0.01,
                   rest_length: Optional[float] = None) -> Spring:
        """Add a spring between two bodies."""
        spring = Spring(a, b, stiffness=stiffness, damping=damping,
                        rest_length=rest_length)
        self.springs.append(spring)
        return spring

    def excite(self, body: Body, impulse: Tuple[float, float, float],
               strength: float = 1.0):
        """Inject an impulse (excitation) into a body's velocity."""
        body.vel += np.array(impulse) * strength

    def _step(self, dt: float):
        """Advance the simulation one time step (semi-implicit Euler)."""
        # reset forces
        forces = {b.id: np.zeros(3) for b in self.bodies}

        # spring forces (Hooke + damping)
        for s in self.springs:
            delta = s.b.pos - s.a.pos
            dist = np.linalg.norm(delta)
            if dist < 1e-12:
                continue
            dir_ = delta / dist
            # Hooke: F = k * (dist - rest) along dir (restoring to rest length)
            f_hooke = s.k * (dist - s.rest_length)
            # damping along the spring axis opposes relative motion
            rel_vel = (s.b.vel - s.a.vel).dot(dir_)
            f_damp = s.c * rel_vel
            force_mag = f_hooke + f_damp
            forces[s.a.id or 0] += force_mag * dir_
            forces[s.b.id or 0] -= force_mag * dir_

        # integrate
        for b in self.bodies:
            if b.fixed:
                continue
            accel = forces[b.id or 0] / b.mass
            b.vel += accel * dt
            b.pos += b.vel * dt

    def render_mic(self, body: Body, duration: float,
                   axis: int = 1) -> np.ndarray:
        """Render audio from a 'microphone' at a body's position.

        Samples the displacement of `body` along `axis` at each step.
        Returns normalized 1D array.

        Parameters
        ----------
        body : Body
            Microphone body.
        duration : float
            Duration in seconds.
        axis : int
            Which coordinate axis to sample (0=x, 1=y, 2=z).

        Returns
        -------
        np.ndarray
            Normalized audio.
        """
        n = int(duration * self.sr)
        # initial displacement relative to start (signal = displacement delta)
        start_pos = body.pos.copy()
        out = np.zeros(n)
        for i in range(n):
            self._step(1.0 / self.sr)
            out[i] = body.pos[axis] - start_pos[axis]
        # normalize
        peak = np.max(np.abs(out)) if n else 1.0
        if peak > 1e-12:
            out = out / peak
        return out.astype(np.float32)

    def render_pluck(self, duration: float, freq: float = 440.0,
                     damping: float = 0.005) -> np.ndarray:
        """Convenience: single-string pluck (2-body + 1 spring).

        A fixed anchor + free body connected by a spring.  Free body is
        displaced and released, producing a decaying tone.

        Parameters
        ----------
        duration : float
            Duration in seconds.
        freq : float
            Approximate resonance frequency (sets spring stiffness).
        damping : float
            Spring damping coefficient.
        """
        # k = (2*pi*f)^2 * m  (for m=1)
        m = 1.0
        k = (2 * np.pi * freq) ** 2 * m
        anchor = self.add_body(pos=(0.0, 0.0, 0.0), fixed=True)
        free = self.add_body(pos=(0.0, 0.1, 0.0), mass=m)
        self.add_spring(anchor, free, stiffness=k, damping=damping,
                        rest_length=0.0)
        # displace free body along y
        free.pos[1] = 0.1
        free.vel[1] = 0.0
        return self.render_mic(free, duration, axis=1)
