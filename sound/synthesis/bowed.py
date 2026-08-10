"""Bowed string physical modeling — SP-024.

Friction-induced waveguide synthesis simulating the non-linear interaction
between a bow and a tensioned string.  The string is split into two
bidirectional delay-line segments (neck + bridge) at the bowing point.
A Newton-Raphson solver resolves the exponential sliding-friction model
at each sample, producing natural Helmholtz stick-slip motion.

Reference: methods_db.md SP-024.

Usage
-----
    from sound.synthesis.bowed import BowedString

    bs = BowedString(sample_rate=44100)
    audio = bs.render(freq=440.0, duration=2.0,
                      bow_velocity=0.2, bow_force=1.5)
"""

import numpy as np
from typing import Union

__all__ = ["BowedString"]


class BowedString:
    """Digital-waveguide bowed-string physical model (SP-024).

    Parameters
    ----------
    sample_rate : int
        Sampling rate in Hz.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #
    def render(
        self,
        freq: float,
        duration: float,
        bow_velocity: Union[float, np.ndarray] = 0.2,
        bow_force: Union[float, np.ndarray] = 1.5,
        bow_position: float = 0.15,
        string_impedance: float = 1.0,
        friction_decay: float = 5.0,
        nut_reflection: float = 0.99,
        bridge_reflection: float = 0.95,
        lpf_coef: float = 0.6,
        noise_level: float = 0.01,
    ) -> np.ndarray:
        """Synthesize a bowed-string tone.

        Parameters
        ----------
        freq : float
            Fundamental frequency in Hz.
        duration : float
            Duration in seconds.
        bow_velocity : float or ndarray
            Bow velocity (m/s), typically 0.05–0.4.  Scalar or envelope.
        bow_force : float or ndarray
            Bowing force (N), typically 0.1–5.0.  Scalar or envelope.
        bow_position : float
            Relative bow position from bridge (0.08–0.2 typical).
        string_impedance : float
            Characteristic impedance Z0.
        friction_decay : float
            Exponential sliding-friction decay rate *a*.
        nut_reflection : float
            Nut reflection gain (≈1.0, low loss).
        bridge_reflection : float
            Bridge reflection gain (body absorption).
        lpf_coef : float
            One-pole LPF coefficient for bridge reflection.
        noise_level : float
            Rosin jitter noise std.

        Returns
        -------
        np.ndarray
            1-D float32 audio normalized to [-1, 1].
        """
        sr = self.sr
        n_samples = int(sr * duration)

        # --- delay-line sizes ------------------------------------------------
        delay_total = max(4, int(round(sr / freq)))
        delay_neck = max(2, int(round(delay_total * bow_position)))
        delay_bridge = max(2, delay_total - delay_neck)

        # bidirectional waveguide state
        neck_left = np.zeros(delay_neck)
        neck_right = np.zeros(delay_neck)
        bridge_left = np.zeros(delay_bridge)
        bridge_right = np.zeros(delay_bridge)

        lpf_state = 0.0

        # --- envelopes -------------------------------------------------------
        if isinstance(bow_velocity, (int, float)):
            v_env = np.full(n_samples, float(bow_velocity))
            # attack / release ramps to avoid clicks
            ramp = int(min(0.05 * sr, n_samples * 0.1))
            if ramp > 0:
                v_env[:ramp] = np.linspace(0.0, bow_velocity, ramp)
                v_env[-ramp:] = np.linspace(bow_velocity, 0.0, ramp)
        else:
            v_env = np.asarray(bow_velocity, dtype=float)

        if isinstance(bow_force, (int, float)):
            f_env = np.full(n_samples, float(bow_force))
            ramp = int(min(0.05 * sr, n_samples * 0.1))
            if ramp > 0:
                f_env[:ramp] = np.linspace(0.0, bow_force, ramp)
                f_env[-ramp:] = np.linspace(bow_force, 0.0, ramp)
        else:
            f_env = np.asarray(bow_force, dtype=float)

        # rosin jitter
        rng = np.random.default_rng(seed=int(freq * 7919) % 2**31)
        bow_noise = rng.normal(0, noise_level, n_samples)
        v_bow_noisy = v_env + v_env * bow_noise

        output = np.zeros(n_samples)

        # --- sample-by-sample simulation ------------------------------------
        for n in range(n_samples):
            # 1. incoming waves at bow junction
            v_neck_in = neck_right[-1]
            v_bridge_in = bridge_left[0]
            v_incoming = v_neck_in + v_bridge_in

            # 2. Newton-Raphson for relative velocity
            v_b = v_bow_noisy[n]
            f_b = f_env[n]
            K = f_b / (2.0 * string_impedance)
            v_input = v_incoming - v_b
            v_rel = v_input  # initial guess

            for _ in range(4):
                exp_term = np.exp(-friction_decay * v_rel ** 2)
                h_val = v_rel - K * v_rel * exp_term - v_input
                h_prime = 1.0 - K * exp_term * (1.0 - 2.0 * friction_decay * v_rel ** 2)
                if abs(h_prime) < 1e-12:
                    break
                v_rel = v_rel - h_val / h_prime

            # 3. string velocity at bow
            v_string = v_rel + v_b
            delta_v = 0.5 * (v_string - v_incoming)

            # 4. wave scattering
            v_neck_out = v_bridge_in + delta_v
            v_bridge_out = v_neck_in + delta_v

            # 5. boundary reflections
            neck_right_next = -nut_reflection * neck_left[0]

            bridge_end = bridge_right[-1]
            lpf_state = lpf_coef * bridge_end + (1.0 - lpf_coef) * lpf_state
            bridge_left_next = -bridge_reflection * lpf_state

            # 6. shift delay lines (manual roll)
            neck_left = np.roll(neck_left, 1)
            neck_left[0] = v_neck_out

            neck_right = np.roll(neck_right, 1)
            neck_right[0] = neck_right_next

            bridge_left = np.roll(bridge_left, 1)
            bridge_left[0] = bridge_left_next

            bridge_right = np.roll(bridge_right, 1)
            bridge_right[0] = v_bridge_out

            # transmitted velocity through bridge = audio output
            output[n] = lpf_state

        # DC removal + normalize
        output = output - np.mean(output)
        max_val = np.max(np.abs(output))
        if max_val > 0:
            output = output / max_val

        return output.astype(np.float32)

    # ------------------------------------------------------------------ #
    # convenience: render from MIDI note
    # ------------------------------------------------------------------ #
    def render_note(
        self,
        midi_note: int,
        duration: float,
        bow_velocity: float = 0.2,
        bow_force: float = 1.5,
        **kwargs,
    ) -> np.ndarray:
        """Render from MIDI note number (A4=69=440 Hz)."""
        freq = 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
        return self.render(
            freq, duration,
            bow_velocity=bow_velocity,
            bow_force=bow_force,
            **kwargs,
        )
