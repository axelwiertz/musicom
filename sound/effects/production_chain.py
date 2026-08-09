"""
ProductionChain — reusable sound-production pipeline for musicom.

Applies professional DSP stages in order to a rendered mix, exporting each
stage for A/B verification. Implements the mastering workflow from
hermes_agent/ (MusicTech Mastering-The-Mix chain):

    1. Reverb (Schroeder algorithmic, early ambience)
    2. SVF lowpass (tame highs / warmth)
    3. Biquad peaking EQ (presence)
    4. Dynamic EQ (resonance control, e.g. 2-4 kHz harshness)
    5. Stereo imaging (mono sub-bass, widened highs)
    6. LUFS normalization (streaming target, e.g. -14 Spotify / -16 Apple)
    7. Limiter (transparent peak control, ceiling -1 dB — AFTER the gain)

Every stage is measured (peak, RMS, integrated LUFS) and written to disk so
each stage can be verified independently — the "one-by-one test" contract.

Usage:
    chain = ProductionChain(sample_rate=44100)
    report = chain.run(raw_audio, output_dir="stages/", target_lufs=-14.0)
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from ..utils.io import read_wav, write_wav
from .reverb import AlgorithmicReverb
from .filter import StateVariableFilter, BiquadFilter
from .mastering import DynamicEQ, StereoImager, Limiter, LUFSMeter, normalize_to_lufs


@dataclass
class StageResult:
    """Measurement snapshot of one production stage."""
    name: str
    peak: float
    rms: float
    lufs: float
    path: Optional[str] = None


@dataclass
class ProductionReport:
    """Full pipeline measurement report."""
    stages: List[StageResult] = field(default_factory=list)
    source_lufs: float = -70.0
    final_lufs: float = -70.0

    def summary_table(self) -> str:
        """Render a text table of stage → LUFS deltas."""
        lines = []
        lines.append("=" * 56)
        lines.append("PRODUCTION PIPELINE SUMMARY")
        lines.append("=" * 56)
        lines.append(f"{'Stage':<24} {'LUFS':>8} {'Δ LUFS':>8}")
        lines.append("-" * 56)
        prev = self.source_lufs
        for s in self.stages:
            lines.append(f"{s.name:<24} {s.lufs:>7.1f} {s.lufs - prev:>+7.1f}")
            prev = s.lufs
        lines.append("=" * 56)
        return "\n".join(lines)


class ProductionChain:
    """Sequential DSP chain with per-stage measurement + export."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.meter = LUFSMeter(sample_rate)

    # -- measurement helpers -------------------------------------------------

    def _stats(self, audio: np.ndarray) -> Tuple[float, float, float]:
        peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
        rms = float(np.sqrt(np.mean(audio ** 2))) if len(audio) else 0.0
        lufs = float(self.meter.measure(audio).integrated_lufs)
        return peak, rms, lufs

    def _export(self, audio: np.ndarray, out_dir: str, name: str) -> str:
        path = os.path.join(out_dir, f"{name}.wav")
        write_wav(path, audio, self.sample_rate, normalize=False)
        return path

    # -- stages (each is independently callable for one-by-one testing) ------

    def stage_reverb(self, audio: np.ndarray,
                     room_size: float = 0.6, damping: float = 0.4,
                     wet_dry: float = 0.25, width: float = 0.8) -> np.ndarray:
        """Schroeder algorithmic reverb — room ambience."""
        return AlgorithmicReverb(
            sample_rate=self.sample_rate,
            room_size=room_size, damping=damping, wet_dry=wet_dry, width=width,
        ).process(audio)

    def stage_lowpass(self, audio: np.ndarray,
                      cutoff: float = 8000.0, resonance: float = 0.2) -> np.ndarray:
        """SVF lowpass — warmth, tame harsh highs."""
        return StateVariableFilter(self.sample_rate).process(
            audio, cutoff=cutoff, resonance=resonance, mode='lp',
        )

    def stage_peaking(self, audio: np.ndarray,
                      freq: float = 3000.0, q: float = 1.5,
                      gain_db: float = 3.0) -> np.ndarray:
        """Biquad peaking EQ — presence boost."""
        filt = BiquadFilter(self.sample_rate)
        filt.design('peaking', freq=freq, Q=q, gain_db=gain_db)
        return filt.process(audio)

    def stage_dynamic_eq(self, audio: np.ndarray,
                         bands: Optional[List[Tuple[float, float, float, float]]] = None
                         ) -> np.ndarray:
        """Dynamic EQ — resonance control (default: 2-4 kHz harshness).

        Thresholds are ADAPTIVE when not given: each band's threshold defaults
        to 10 dB below the band's SMOOTHED-envelope peak (the envelope the
        compressor actually reacts to) so the stage always engages on real
        material. A fixed -10 dBFS threshold is a no-op on mixes whose band
        level sits lower.
        """
        from scipy.signal import butter, lfilter

        spec = bands or [(3000.0, 2.0, None, 2.5)]  # (center, q, threshold, ratio)
        deq = DynamicEQ(self.sample_rate)

        for center, q, thresh, ratio in spec:
            bw = center / q
            low = max(20, center - bw / 2)
            high = min(self.sample_rate / 2 - 1, center + bw / 2)
            bb, aa = butter(2, [low, high], btype='band', fs=self.sample_rate)
            band = lfilter(bb, aa, audio, axis=0)
            # Smoothed envelope (10ms attack / 100ms release, same as DynamicEQ)
            env = np.abs(band)
            if env.ndim == 2:
                env = env.mean(axis=1)  # fold stereo to mono envelope
            att = int(0.010 * self.sample_rate)
            rel = int(0.100 * self.sample_rate)
            smooth = np.zeros_like(env)
            smooth[0] = env[0]
            for i in range(1, len(env)):
                coeff = np.exp(-1.0 / att) if env[i] > smooth[i-1] else np.exp(-1.0 / rel)
                smooth[i] = smooth[i-1] * coeff + env[i] * (1 - coeff)
            env_peak = float(np.max(smooth)) if len(smooth) else 0.0
            if thresh is None:
                thresh = 20 * np.log10(max(env_peak, 1e-9)) - 10.0
                print(f"    [dynamic_eq] band {center:.0f}Hz env peak {20*np.log10(max(env_peak,1e-9)):.1f} dBFS → adaptive threshold {thresh:.1f} dBFS")
            deq.add_band(center, q=q, threshold_db=thresh, ratio=ratio)
        return deq.process(audio)

    def stage_stereo_imager(self, audio: np.ndarray,
                            mono_below_hz: float = 100.0,
                            widen_above_hz: float = 2000.0,
                            widen_amount: float = 1.3) -> np.ndarray:
        """Mono-safe stereo width — mono sub, widened highs."""
        imager = StereoImager(self.sample_rate)
        imager.set_width(0.0, below_hz=mono_below_hz)
        imager.set_width(widen_amount, above_hz=widen_above_hz)
        return imager.process(audio)

    def stage_limiter(self, audio: np.ndarray,
                      threshold_db: float = -1.0, release_ms: float = 100.0) -> np.ndarray:
        """Transparent peak limiter."""
        return Limiter(
            threshold_db=threshold_db, release_ms=release_ms,
            sample_rate=self.sample_rate,
        ).process(audio)

    def stage_lufs_norm(self, audio: np.ndarray,
                        target_lufs: float = -14.0) -> np.ndarray:
        """LUFS normalization to streaming target."""
        return normalize_to_lufs(audio, target_lufs, self.sample_rate)

    # -- full chain ----------------------------------------------------------

    def run(self, audio: np.ndarray, output_dir: str,
            target_lufs: float = -14.0,
            include: Optional[List[str]] = None) -> ProductionReport:
        """Run all stages sequentially, exporting + measuring each.

        Args:
            audio: Input mix (float32/64, mono or stereo).
            output_dir: Directory for stage WAV exports.
            target_lufs: Final loudness target.
            include: Optional subset of stage names to run
                     (default: all 7 stages in canonical order).

        Returns:
            ProductionReport with per-stage measurements.
        """
        os.makedirs(output_dir, exist_ok=True)

        stages = [
            ("reverb", self.stage_reverb, {}),
            ("lowpass", self.stage_lowpass, {}),
            ("peaking", self.stage_peaking, {}),
            ("dynamic_eq", self.stage_dynamic_eq, {}),
            ("stereo_imager", self.stage_stereo_imager, {}),
            ("lufs_norm", self.stage_lufs_norm, {"target_lufs": target_lufs}),
            # Limiter AFTER loudness gain: gain re-crosses ceiling, so the
            # limiter catches those peaks last (true mastering order).
            ("limiter", self.stage_limiter, {}),
        ]
        if include:
            stages = [(n, f, k) for n, f, k in stages if n in include]

        report = ProductionReport()
        report.source_lufs = self._stats(audio)[2]

        current = audio
        for name, fn, kwargs in stages:
            current = fn(current, **kwargs)
            peak, rms, lufs = self._stats(current)
            path = self._export(current, output_dir, f"{len(report.stages):02d}_{name}")
            report.stages.append(StageResult(name, peak, rms, lufs, path))

        report.final_lufs = report.stages[-1].lufs if report.stages else report.source_lufs
        return report

    def run_from_file(self, wav_path: str, output_dir: str,
                      target_lufs: float = -14.0,
                      include: Optional[List[str]] = None) -> ProductionReport:
        """Convenience: read WAV, run chain, return report."""
        audio, sr = read_wav(wav_path)
        if sr != self.sample_rate:
            # simple linear resample (per-channel for stereo)
            ratio = self.sample_rate / sr
            new_len = int(len(audio) * ratio)
            x_old = np.linspace(0, 1, len(audio))
            x_new = np.linspace(0, 1, new_len)
            if audio.ndim == 2:
                audio = np.column_stack([
                    np.interp(x_new, x_old, audio[:, 0]),
                    np.interp(x_new, x_old, audio[:, 1]),
                ])
            else:
                audio = np.interp(x_new, x_old, audio)
        return self.run(audio, output_dir, target_lufs=target_lufs, include=include)


if __name__ == '__main__':
    import sys
    # Smoke: render 3s of synthetic material, run the chain, print summary.
    sr = 44100
    t = np.linspace(0, 3.0, int(sr * 3.0), endpoint=False)
    signal = (0.25 * np.sin(2 * np.pi * 220 * t)
              + 0.15 * np.sin(2 * np.pi * 440 * t)
              + 0.10 * np.sin(2 * np.pi * 660 * t)
              + 0.05 * np.random.randn(len(t)))
    chain = ProductionChain(sample_rate=sr)
    rep = chain.run(signal, output_dir=sys.argv[1] if len(sys.argv) > 1 else '/tmp/prod_chain_smoke')
    print(rep.summary_table())
    print("✓ ProductionChain smoke passed")
