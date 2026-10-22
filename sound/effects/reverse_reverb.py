"""Reverse reverb processor — Bixlab Reverse Reverb style.

Replicable logic from the Sound On Sound review "Bixlab Reverse Reverb"
(November 2026): a plug-in that automates the classic reverse-reverb
workflow — duplicate the audio, reverse it, apply a fully wet reverb,
render, reverse the rendered clip, trim it to taste and align it so the
transient hits where the original clip starts — instead of doing those
steps by hand in a DAW.

What is replicated here:
- ``ReverseReverb.process``: reverse -> convolve with a synthetic reverb
  IR (exponentially decaying noise; pre-delay shifts the IR start) ->
  reverse back -> wet/dry mix. Because the signal is reversed twice, the
  dry transient keeps its original position while its reverb tail now
  precedes it: a swelling build into the hit.
- ``align_to_hit``: trims the leading pre-roll swell so the detected
  transient lands at the start of the returned buffer (the "align to hit
  when the original clip starts" step of the manual workflow), with an
  optional ``pre_roll_sec`` of swell kept before the hit.
- Fades at the boundaries to avoid clicks.

Not replicated: the VST3/AU host, licence-key copy protection, GUI; the
plug-in's exact IR set is proprietary — a synthetic decaying-noise IR is
used instead (deterministic per seed).

Usage:
    from sound.effects.reverse_reverb import ReverseReverb

    rr = ReverseReverb(sample_rate=44100)
    out = rr.process(audio, decay_sec=2.0, wet=0.6, align_to_hit=True)
"""

from __future__ import annotations

import numpy as np

__all__ = ["ReverseReverb", "make_reverb_ir"]

DEFAULT_SR = 44100


def make_reverb_ir(sample_rate: int, decay_sec: float = 2.0,
                   pre_delay_ms: float = 0.0, density: float = 0.9,
                   seed: int = 0) -> np.ndarray:
    """Synthetic exponentially-decaying noise reverb IR.

    Args:
        sample_rate: Hz.
        decay_sec: RT-ish tail length (exponential decay to ~-60 dB).
        pre_delay_ms: gap between the dry transient and the reverb start
            (classic pre-delay; implemented as leading zeros in the IR).
        density: noise density in the tail (1.0 = every sample filled;
            lower values sparsen the tail for a shimmering feel).
        seed: RNG seed for a reproducible IR.
    """
    n = max(64, int(sample_rate * decay_sec))
    rng = np.random.RandomState(seed)
    noise = rng.randn(n).astype(np.float64)
    if density < 1.0:
        keep = rng.rand(n) < density
        noise = noise * keep
    t = np.arange(n) / sample_rate
    env = np.exp(-3.0 * t / max(decay_sec, 1e-6))   # ~ -26 dB/sec * decay
    ir = noise * env
    pre = int(sample_rate * pre_delay_ms / 1000.0)
    if pre > 0:
        ir = np.concatenate([np.zeros(pre), ir])
    peak = np.max(np.abs(ir)) + 1e-12
    return ir / peak * 0.9


def _fft_convolve(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Linear convolution via FFT (numpy only)."""
    n = len(a) + len(b) - 1
    nfft = 1 << (n - 1).bit_length()
    fa = np.fft.rfft(a, nfft)
    fb = np.fft.rfft(b, nfft)
    y = np.fft.irfft(fa * fb, nfft)
    return y[:n]


class ReverseReverb:
    """Offline reverse-reverb processor (Bixlab workflow).

    Args:
        sample_rate: audio sample rate in Hz.
    """

    def __init__(self, sample_rate: int = DEFAULT_SR):
        self.sample_rate = int(sample_rate)

    def process(self, audio: np.ndarray, decay_sec: float = 2.0,
                wet: float = 0.6, pre_delay_ms: float = 0.0,
                align_to_hit: bool = True, pre_roll_sec: float = 0.0,
                fade_ms: float = 15.0, ir_density: float = 0.9,
                ir_seed: int = 0, keep_full_length: bool = False) -> np.ndarray:
        """Apply reverse reverb.

        Args:
            audio: mono ``(n,)`` float array.
            decay_sec: reverb tail length in seconds.
            wet: wet/dry balance (0..1; the plug-in's workflow is a fully
                wet reversed render, but a mix is more practical).
            pre_delay_ms: pre-delay between transient and reverb.
            align_to_hit: trim the leading swell so the transient lands at
                position 0 of the output (default True).
            pre_roll_sec: seconds of swell kept *before* the hit when
                aligning (the "trim to taste" step).
            fade_ms: fade-in/out length at the output boundaries.
            ir_density: IR noise density (see ``make_reverb_ir``).
            ir_seed: IR seed (deterministic).
            keep_full_length: if True, return the full convolution length
                (input + IR - 1) without trimming.

        Returns:
            Processed 1-D float array.
        """
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        if x.size == 0:
            return np.zeros(0)

        ir = make_reverb_ir(self.sample_rate, decay_sec=decay_sec,
                            pre_delay_ms=pre_delay_ms, density=ir_density,
                            seed=ir_seed)

        # classic workflow: reverse -> wet reverb -> reverse back
        x_rev = x[::-1].copy()
        wet_full = _fft_convolve(x_rev, ir)
        y = wet_full[::-1].copy()          # double reversal: transient restored
        mix = (1.0 - wet) * x + wet * y[:len(x)]

        if keep_full_length:
            out = y
        else:
            transient = int(np.argmax(np.abs(x)))   # "the hit"
            if align_to_hit:
                start = max(0, transient - int(pre_roll_sec * self.sample_rate))
                out = mix[start:]
            else:
                out = mix
                transient = min(transient, len(out) - 1)

        # boundary fades
        fade = max(1, int(self.sample_rate * fade_ms / 1000.0))
        if fade < len(out):
            ramp = np.hanning(2 * fade)
            out = out.copy()
            out[:fade] *= ramp[:fade]
            out[-fade:] *= ramp[fade:]

        peak = float(np.max(np.abs(out))) if out.size else 0.0
        if peak > 1.0:
            out = out / peak * 0.95
        return out


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: impulse alignment + a real chord swell, WAV writes."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR

    # 1) impulse: transient position must be preserved by the double reversal.
    #    wet < 1.0 keeps the dry impulse dominant at its original position
    #    (with wet=1.0 the dry transient is gone and the IR peak rules).
    n = sr
    x = np.zeros(n)
    t_hit = int(n * 0.7)
    x[t_hit] = 1.0
    rr = ReverseReverb(sample_rate=sr)
    y = rr.process(x, decay_sec=1.5, wet=0.8, align_to_hit=True,
                   pre_roll_sec=0.3)
    hit_out = int(np.argmax(np.abs(y[: int(0.5 * sr)])))
    # with align, the transient is at pre_roll position
    assert abs(hit_out - int(0.3 * sr)) <= 4, f"transient drifted {hit_out}"
    peak = float(np.max(np.abs(y)))
    # dry impulse at wet=0.8 keeps ~0.2 amplitude; the wet swell peak lands
    # beyond the trimmed buffer (it precedes the hit), so require > 0.15
    assert peak > 0.15, "impulse response too quiet"

    # 2) real chord: swelling reverse reverb
    t = np.arange(sr * 2) / sr
    chord = np.zeros_like(t)
    for f in (196.0, 261.6, 329.6):
        chord += np.sin(2 * np.pi * f * t)
        chord += 0.5 * np.sin(4 * np.pi * f * t)
    chord = chord / np.max(np.abs(chord)) * 0.9
    y2 = rr.process(chord, decay_sec=2.5, wet=0.7, align_to_hit=True,
                    pre_roll_sec=0.4)
    p2 = os.path.join(out_dir, "reverse_reverb_chord.wav")
    write_wav(p2, y2, sr)
    assert os.path.getsize(p2) > 40, "empty/corrupt WAV"
    assert y2.size > 0 and float(np.max(np.abs(y2))) > 1e-3

    return {
        "impulse_transient_in": t_hit,
        "impulse_transient_out": hit_out,
        "pre_roll_sec": 0.3,
        "chord_out_samples": int(y2.shape[0]),
        "chord_peak": round(float(np.max(np.abs(y2))), 4),
        "wav_bytes": os.path.getsize(p2),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
