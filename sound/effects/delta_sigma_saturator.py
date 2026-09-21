"""Physics-Based Delta-Sigma Converter Saturation & Circuit Strain (Mixland Grey Matter-style).

Replicates the nonlinear behavior of 1990s console DAC stages (such as early
PlayStation 1 Delta-Sigma converters) pushed beyond nominal operating specs.
Includes:
- Discrete Delta-Sigma modulator / demodulator loop with integrator leak
- Non-linear thermal strain and molecular component drift (dynamic DC bias + warm compression)
- Switched multi-stage converter profiles (Clean Hi-Fi, Vintage Console, Overdriven DAC)
- Slew-rate limiting and analog reconstruction lowpass filtering (smooth HF roll-off)
- Circuit sandbox breaking point: chaotic sub-harmonic foldback and bitstream truncation
"""

import math
from typing import Dict, Optional, Tuple

import numpy as np


class DeltaSigmaStage:
    """1st and 2nd-order Delta-Sigma converter emulation with integrator saturation."""

    def __init__(self, oversample_ratio: int = 8, leak: float = 0.995):
        self.osr = oversample_ratio
        self.leak = leak
        self.int1 = 0.0
        self.int2 = 0.0
        self.dac_state = 0.0

    def reset(self):
        self.int1 = 0.0
        self.int2 = 0.0
        self.dac_state = 0.0

    def process_sample(self, x: float, strain: float = 0.0) -> float:
        """Process a single sample at OSR rate.

        strain: 0.0 (nominal) to 1.0+ (pushed beyond specs).
        """
        # Thermal drift / DC offset induced by strain
        thermal_offset = strain * 0.08
        x_strained = x + thermal_offset

        # 2nd-order delta sigma loop
        # Integrator 1
        diff1 = x_strained - self.dac_state
        self.int1 = self.int1 * self.leak + diff1

        # Soft clip on integrator 1 (component saturation)
        sat_limit = 2.5 - min(1.5, strain * 1.2)
        if abs(self.int1) > sat_limit:
            self.int1 = math.tanh(self.int1 / sat_limit) * sat_limit

        # Integrator 2
        diff2 = self.int1 - self.dac_state
        self.int2 = self.int2 * self.leak + diff2

        # 1-bit comparator (quantizer)
        quant = 1.0 if self.int2 >= 0.0 else -1.0
        self.dac_state = quant

        return quant


class SlewLimiter:
    """Analog reconstruction slew-rate limiter."""

    def __init__(self, max_slew: float = 0.2):
        self.max_slew = max_slew
        self.last_y = 0.0

    def reset(self):
        self.last_y = 0.0

    def process(self, x: np.ndarray, strain: float = 0.0) -> np.ndarray:
        # Strain degrades slew rate (thermal load slows op-amp settling time)
        effective_slew = max(0.005, self.max_slew * (1.0 - 0.7 * strain))
        y = np.zeros_like(x)
        last = self.last_y
        for i in range(len(x)):
            delta = x[i] - last
            if delta > effective_slew:
                delta = effective_slew
            elif delta < -effective_slew:
                delta = -effective_slew
            last = last + delta
            y[i] = last
        self.last_y = last
        return y


class ReconstructionFilter:
    """Reconstruction lowpass filter (smoothing delta-sigma bitstream)."""

    def __init__(self, cutoff_fc: float = 18000.0, fs: int = 44100):
        self.fs = fs
        self.update_cutoff(cutoff_fc)
        self.s1 = 0.0
        self.s2 = 0.0

    def update_cutoff(self, fc: float):
        w0 = 2.0 * math.pi * min(fc, self.fs * 0.45) / self.fs
        # 2-pole critically damped IIR lowpass
        self.alpha = math.sin(w0) / 2.0
        self.cos_w0 = math.cos(w0)
        self.a0 = 1.0 + self.alpha
        self.b0 = (1.0 - self.cos_w0) / 2.0 / self.a0
        self.b1 = (1.0 - self.cos_w0) / self.a0
        self.b2 = self.b0
        self.a1 = (-2.0 * self.cos_w0) / self.a0
        self.a2 = (1.0 - self.alpha) / self.a0

    def reset(self):
        self.s1 = 0.0
        self.s2 = 0.0

    def process(self, x: np.ndarray) -> np.ndarray:
        y = np.zeros_like(x)
        s1, s2 = self.s1, self.s2
        b0, b1, b2, a1, a2 = self.b0, self.b1, self.b2, self.a1, self.a2
        for i in range(len(x)):
            xi = x[i]
            yi = b0 * xi + s1
            s1 = b1 * xi - a1 * yi + s2
            s2 = b2 * xi - a2 * yi
            y[i] = yi
        self.s1, self.s2 = s1, s2
        return y


class DeltaSigmaSaturator:
    """Physics-based 90s Console DAC & Delta-Sigma Saturation Engine (SP-091).

    Simulates the warm compression, molecular component strain, and chaotic
    overdrive of vintage DAC stages pushed beyond nominal headroom.
    """

    MODES = ("clean", "console", "broken")

    def __init__(
        self,
        drive_db: float = 0.0,
        strain: float = 0.2,
        mode: str = "console",
        mix: float = 1.0,
        fs: int = 44100,
    ):
        self.fs = fs
        self.drive_db = drive_db
        self.strain = strain
        self.mode = mode if mode in self.MODES else "console"
        self.mix = mix

        self.ds_l = DeltaSigmaStage(oversample_ratio=4)
        self.ds_r = DeltaSigmaStage(oversample_ratio=4)
        self.slew_l = SlewLimiter(max_slew=0.25)
        self.slew_r = SlewLimiter(max_slew=0.25)
        self.recon_l = ReconstructionFilter(cutoff_fc=16000.0, fs=fs)
        self.recon_r = ReconstructionFilter(cutoff_fc=16000.0, fs=fs)

    def reset(self):
        self.ds_l.reset()
        self.ds_r.reset()
        self.slew_l.reset()
        self.slew_r.reset()
        self.recon_l.reset()
        self.recon_r.reset()

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process stereo or mono audio (channels, samples)."""
        if audio.ndim == 1:
            stereo = np.vstack([audio, audio])
        elif audio.shape[0] == 1:
            stereo = np.vstack([audio, audio])
        else:
            stereo = audio.copy()

        channels, num_samples = stereo.shape
        dry = stereo.copy()

        # Input gain / Drive
        gain = 10.0 ** (self.drive_db / 20.0)
        driven = stereo * gain

        # Mode configurations
        if self.mode == "clean":
            effective_strain = self.strain * 0.3
            fc = 19000.0
        elif self.mode == "console":
            effective_strain = self.strain
            fc = 15000.0 - (effective_strain * 3000.0)
        else:  # broken
            effective_strain = self.strain * 1.8
            fc = 9000.0 - min(4000.0, effective_strain * 3000.0)

        self.recon_l.update_cutoff(fc)
        self.recon_r.update_cutoff(fc)

        wet = np.zeros_like(stereo)
        for ch in range(2):
            x = driven[ch]
            ds = self.ds_l if ch == 0 else self.ds_r
            slew = self.slew_l if ch == 0 else self.slew_r
            recon = self.recon_l if ch == 0 else self.recon_r

            # Oversampled delta-sigma integration
            osr = 4
            x_os = np.repeat(x, osr)
            num_os = len(x_os)
            bits = np.zeros(num_os, dtype=np.float32)

            for i in range(num_os):
                bits[i] = ds.process_sample(x_os[i], strain=effective_strain)

            # Slew limit on analog bitstream
            slewed = slew.process(bits, strain=effective_strain)

            # Decimate back to sample rate with simple moving average filter
            decimated = np.mean(slewed.reshape(-1, osr), axis=1)

            # Analog reconstruction filter (2-pole Butterworth lowpass)
            smoothed = recon.process(decimated)

            # Asymmetric DAC ladder soft clipping & thermal compression
            # Asymmetry models component mismatch in resistor ladder DACs
            asym_bias = 0.05 * effective_strain
            clipped = np.tanh(smoothed * 0.85 + asym_bias) - asym_bias

            # Sub-harmonic foldback when driven past extreme strain
            if self.mode == "broken" and effective_strain > 0.8:
                fold_thresh = 0.95
                excess = np.maximum(0.0, np.abs(clipped) - fold_thresh)
                clipped = np.where(np.abs(clipped) > fold_thresh, np.sign(clipped) * (fold_thresh - 1.5 * excess), clipped)

            wet[ch] = clipped

        # Normalize output gain
        out = (1.0 - self.mix) * dry + self.mix * wet
        return out.astype(np.float32)


def demo():
    """Demonstrate DeltaSigmaSaturator on a synthesized drum bus signal."""
    fs = 44100
    dur = 2.0
    num_samples = int(dur * fs)
    t = np.arange(num_samples) / fs

    # Synthetic drum test: 50 Hz kick + transient click + noisy snare burst
    kick = np.sin(2 * np.pi * 50 * np.exp(-t * 8) * t) * np.exp(-t * 4)
    snare = np.random.uniform(-0.5, 0.5, num_samples) * np.exp(-((t - 0.5) % 0.5) * 12)
    sig = (kick + snare).astype(np.float32)
    stereo_in = np.vstack([sig, sig])

    saturator = DeltaSigmaSaturator(drive_db=6.0, strain=0.5, mode="console", fs=fs)
    stereo_out = saturator.process(stereo_in)

    print("DeltaSigmaSaturator Demo:")
    print(f"  Input RMS: {np.sqrt(np.mean(stereo_in**2)):.4f}, Peak: {np.max(np.abs(stereo_in)):.4f}")
    print(f"  Output RMS: {np.sqrt(np.mean(stereo_out**2)):.4f}, Peak: {np.max(np.abs(stereo_out)):.4f}")
    print(f"  Output shape: {stereo_out.shape}")
    print("  Success!")


if __name__ == "__main__":
    demo()
