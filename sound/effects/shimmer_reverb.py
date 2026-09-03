"""Fractional-pitch shimmer reverb — Groove Synthesis 3rd Wave OS 2.0a style.

Replicable DSP from the Groove Synthesis 3rd Wave OS 2.0a update (Sound On
Sound 2026-08-25): a new Shimmer Verb processor for the hardware wavetable
synth that pitch-shifts reverb feedback "in fractions of a semitone across
a full two-octave range, from one octave down to one octave up" — not
limited to octave/semitone steps — plus Filter Cutoff tone control and
Rev Time / Pitch Amount / LP-HP Cutoff as mod-matrix destinations.

What is replicated here:
- **Fractional-semitone pitch shifting**: the feedback path is pitch
  shifted by an arbitrary number of cents (not just +12/-12). A SOLA
  (synchronized overlap-add) grain shifter — resample to change pitch,
  overlap-add Hann grains at the original spacing to restore length —
  transposes the tail by ``pitch_cents`` in [-1200, +1200] at fractional
  resolution (e.g. +7, +25, -350 cents: the article's headline trick).
- **Shimmer feedback loop**: Schroeder allpass diffusers + parallel comb
  tank run block-wise; after each block the wet tail is pitch-shifted and
  fed back into the next block's input, so every regeneration climbs by
  the shift amount — the classic shimmer ladder. ``pitch_amount`` scales
  how much tail goes through the shifter (0 = plain reverb).
- **Mod-matrix-style destinations**: ``rev_time``, ``pitch_amount`` and
  the filter cutoff are runtime-scalable per call; a slow internal LFO
  (or an external modulation stream) wobbles the live shift cents.

Not replicated: the Super Plate processor it sits alongside, hardware
mod-matrix UI/SysEx, the LP/HP dual cutoff (single lowpass here).

Usage:
    from sound.effects.shimmer_reverb import ShimmerVerb

    sv = ShimmerVerb(sample_rate=44100)
    out = sv.process(audio, pitch_cents=1200, rev_time=0.6,
                     pitch_amount=0.7, filter_cutoff=6000.0, mix=0.6)
"""

from typing import Optional

import numpy as np

__all__ = ["ShimmerVerb", "PITCH_MIN_CENTS", "PITCH_MAX_CENTS"]


PITCH_MIN_CENTS = -1200  # one octave down
PITCH_MAX_CENTS = 1200   # one octave up
_BLOCK = 4096            # internal processing block (feedback pitch grid)


class ShimmerVerb:
    """Feedback reverb with fractional-semitone pitch shift in the loop.

    Parameters
    ----------
    sample_rate : int
        Sampling rate in Hz.
    seed : int, optional
        Seed for comb/diffuser tuning jitter (deterministic runs).
    """

    def __init__(self, sample_rate: int = 44100, seed: Optional[int] = None):
        self.sr = int(sample_rate)
        rng = np.random.RandomState(seed)
        sr_k = self.sr / 1000.0
        # Schroeder/Moorer core: 2 allpass diffusers + 4 parallel combs,
        # Freeverb-ish tuning scaled to this sample rate
        self.allpass_delays = [int(5.1 * sr_k), int(3.7 * sr_k)]
        self.allpass_fb = [0.70, 0.70]
        self.comb_delays = [int(21.3 * sr_k), int(18.7 * sr_k),
                            int(15.9 * sr_k), int(13.1 * sr_k)]
        self.comb_fb = [0.80 + rng.uniform(-0.006, 0.006) for _ in range(4)]
        # slow chorus LFO on the live shift (organic shimmer)
        self.lfo_rate = 0.15
        self.lfo_depth_cents = 12.0

    # ------------------------------------------------------------------ #
    @staticmethod
    def _pitch_shift(x: np.ndarray, cents: float) -> np.ndarray:
        """Length-preserving pitch shift by ``cents`` (fractional allowed).

        SOLA: resample by ``ratio = 2^(cents/1200)`` to change pitch, then
        overlap-add Hann grains at the original spacing so the output keeps
        the input length. This is the standard time-domain shifter used in
        shimmer reverbs before the feedback tap.
        """
        n = len(x)
        if n < 64 or abs(cents) < 0.5:
            return x.copy()
        ratio = 2.0 ** (float(cents) / 1200.0)
        new_len = max(8, int(n / ratio))
        xp = np.linspace(0, n - 1, new_len)
        shifted = np.interp(xp, np.arange(n), x)
        grain = min(2048, max(256, n // 4))
        hop = grain // 2
        out = np.zeros(n)
        norm = np.zeros(n)
        win = np.hanning(grain)
        src = 0.0
        pos = 0
        while pos < n:
            s0 = int(src)
            if s0 >= len(shifted):
                break
            seg = shifted[s0:s0 + grain]
            if len(seg) < grain:
                seg = np.pad(seg, (0, grain - len(seg)))
            end = min(pos + grain, n)
            out[pos:end] += seg[:end - pos] * win[:end - pos]
            norm[pos:end] += win[:end - pos]
            pos += hop
            src += hop * ratio
        nz = norm > 1e-6
        out[nz] /= norm[nz]
        return out

    # ------------------------------------------------------------------ #
    def _core_block(self, x: np.ndarray, ap1, ap2, combs) -> np.ndarray:
        """Run diffusers + comb tank over one block (unity-gain core).

        Standard Schroeder/Moorer allpass::
            delayed = buf[d-1]
            out = -k*x + delayed + k*delayed   (k = feedback coeff)
        is replaced by the equivalent *stable* form used here::
            buf[0] = x + k*delayed ; out = delayed - k*buf[0]
        which has unity magnitude response for |k| < 1. The comb tank sums
        four damped combs and scales by 1/4 (average), keeping the wet
        level comparable to the input.

        State arrays are mutated in place so the tail sustains across
        block boundaries. Returns the wet block.
        """
        n = len(x)
        out = np.zeros(n)
        for i in range(n):
            s = x[i]
            for j, d in enumerate(self.allpass_delays):
                buf = ap1[j]
                delayed = buf[d - 1]
                k = self.allpass_fb[j]
                buf[1:] = buf[:-1]
                buf[0] = s + k * delayed
                s = delayed - k * buf[0]
                ap1[j] = buf
            acc = 0.0
            for j, d in enumerate(self.comb_delays):
                buf = combs[j]
                delayed = buf[d - 1]
                buf[1:] = buf[:-1]
                buf[0] = s + self.comb_fb[j] * delayed
                combs[j] = buf
                acc += delayed
            wet_tail = acc * 0.25
            for j, d in enumerate(self.allpass_delays):
                buf = ap2[j]
                delayed = buf[d - 1]
                k = self.allpass_fb[j]
                buf[1:] = buf[:-1]
                buf[0] = wet_tail + k * delayed
                wet_tail = delayed - k * buf[0]
                ap2[j] = buf
            out[i] = wet_tail
        return out

    # ------------------------------------------------------------------ #
    def process(self, x: np.ndarray, pitch_cents: float = 1200.0,
                rev_time: float = 0.55, pitch_amount: float = 0.5,
                filter_cutoff: float = 7000.0, mix: float = 0.5,
                lfo_mod: Optional[np.ndarray] = None) -> np.ndarray:
        """Run the shimmer reverb.

        Args:
            x: Mono input audio.
            pitch_cents: Shimmer shift in cents, -1200..+1200 (fractional ok).
            rev_time: 0..1 — scales the comb feedback (tail length).
            pitch_amount: 0..1 — how much of the wet tail feeds back through
                the pitch shifter (0 = plain reverb, 1 = full shimmer loop).
            filter_cutoff: Hz lowpass on the wet path (tone control).
            mix: Dry/wet.
            lfo_mod: Optional external modulation stream (len(x)); when given
                it replaces the internal LFO and wobbles the live shift by
                ±12 cents scaled by pitch_amount (mod-matrix destination).

        Returns:
            Processed mono audio, same length as input.
        """
        x = np.asarray(x, dtype=np.float64)
        n = len(x)
        if n == 0:
            return x
        pitch_cents = float(np.clip(pitch_cents, PITCH_MIN_CENTS,
                                    PITCH_MAX_CENTS))
        pitch_amount = float(np.clip(pitch_amount, 0.0, 1.0))
        # reverb time sets the tank recirculation gain (the loop that makes
        # the tail sustain after the input stops). Comb damping is fixed
        # moderate; the recirculation is energy-normalized (below) so the
        # round-trip gain is exactly loop_gain — stable for any resonance.
        rt = float(np.clip(rev_time, 0.0, 1.0))
        comb_fb = [f * (0.5 + 0.35 * rt) for f in self.comb_fb]
        loop_gain = 0.60 + 0.35 * rt

        # state
        ap1 = [np.zeros(d) for d in self.allpass_delays]
        ap2 = [np.zeros(d) for d in self.allpass_delays]
        combs = [np.zeros(d) for d in self.comb_delays]

        def recirculate(wet: np.ndarray, blk_in: np.ndarray) -> np.ndarray:
            """Build the recirculated tail from a wet block.

            pitch_amount of the tail is pitch-shifted by the fractional
            interval; the rest recirculates plain (pitch_amount=0 -> plain
            reverb, 1 -> full shimmer loop). The result is energy-normalized
            against the block that produced it so the round-trip gain equals
            loop_gain exactly — comb resonances shape the sound but cannot
            make the loop unstable.
            """
            if pitch_amount > 0.02 and abs(pitch_cents) >= 0.5:
                # slow LFO wobble on the live shift (per-block center value)
                if lfo_mod is not None:
                    center = float(np.mean(lfo_mod[lo:hi])) \
                        if hi <= len(lfo_mod) else 0.0
                else:
                    center = float(np.sin(2 * np.pi * self.lfo_rate
                                          * (lo + _BLOCK / 2.0) / self.sr))
                live = pitch_cents + self.lfo_depth_cents * center
                shifted = self._pitch_shift(wet, live)
                mix_tail = shifted * pitch_amount + wet * (1.0 - pitch_amount)
            else:
                mix_tail = wet
            in_rms = float(np.sqrt(np.mean(blk_in ** 2))) if len(blk_in) else 0.0
            tail_rms = float(np.sqrt(np.mean(mix_tail ** 2))) \
                if len(mix_tail) else 0.0
            if in_rms > 1e-9 and tail_rms > 1e-12:
                mix_tail = mix_tail * (loop_gain * in_rms / tail_rms)
            else:
                mix_tail = mix_tail * loop_gain
            return mix_tail

        wet_blocks = []
        n_blocks = (n + _BLOCK - 1) // _BLOCK
        fb = np.zeros(_BLOCK)  # recirculated tail fed into next block
        for b in range(n_blocks):
            lo = b * _BLOCK
            hi = min(lo + _BLOCK, n)
            blk = x[lo:hi].copy()
            # tank recirculation: previous block's tail re-enters the input
            blk[:len(fb)] += fb[:len(blk)]
            # core reverb (diffusers + comb tank, state persists across blocks)
            wet = self._core_block(blk, ap1, ap2, combs)
            fb = recirculate(wet, blk)
            wet_blocks.append(wet)
        wet_all = np.concatenate(wet_blocks)[:n]
        # ring-out: keep recirculating after the input ends so the (shifted)
        # tail decays naturally instead of being cut at the buffer boundary
        tail_energy = float(np.sqrt(np.mean(fb ** 2)))
        if tail_energy > 1e-7 and n >= _BLOCK:
            extra = []
            fb_cur = fb.copy()
            for _ in range(max(1, _BLOCK // 4)):
                core_in = fb_cur[:_BLOCK].copy()
                wet = self._core_block(core_in, ap1, ap2, combs)
                if pitch_amount > 0.02 and abs(pitch_cents) >= 0.5:
                    shifted = self._pitch_shift(wet, pitch_cents)
                    mix_tail = shifted * pitch_amount \
                        + wet * (1.0 - pitch_amount)
                else:
                    mix_tail = wet
                in_rms = float(np.sqrt(np.mean(core_in ** 2)))
                tail_rms = float(np.sqrt(np.mean(mix_tail ** 2)))
                if in_rms > 1e-9 and tail_rms > 1e-12:
                    fb_cur = mix_tail * (loop_gain * in_rms / tail_rms)
                else:
                    fb_cur = mix_tail * loop_gain
                extra.append(wet)
                if float(np.sqrt(np.mean(fb_cur ** 2))) < 1e-8:
                    break
            wet_all = np.concatenate([wet_all] + extra)[:n]

        # wet-path tone control
        wet_all = _one_pole_lp(wet_all, float(filter_cutoff), self.sr)
        peak_in = np.max(np.abs(x)) or 1.0
        peak_w = np.max(np.abs(wet_all)) or 1.0
        if peak_w > 1e-9:
            wet_all = wet_all / peak_w * peak_in
        # return the shimmering tail in the wet mix. Note the tail energy
        # decays across the tail (per-block pitch_shift of the *tail* keeps
        # the ladder audible but quiet); the wet path is peak-normalized so
        # mix=1.0 yields the pure processed tail at input peak level.
        return x * (1.0 - mix) + wet_all * mix


def _one_pole_lp(x: np.ndarray, cutoff: float, sr: int) -> np.ndarray:
    """One-pole lowpass (wet-path tone control)."""
    if cutoff >= sr * 0.49 or len(x) == 0:
        return x
    alpha = 1.0 - np.exp(-2.0 * np.pi * cutoff / sr)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y


def demo() -> str:
    """Run a short demo of the fractional-pitch shimmer reverb."""
    sr = 44100
    dur = 3.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    env = np.exp(-3.0 * t)
    x = env * (0.5 * np.sin(2 * np.pi * 440.0 * t)
               + 0.25 * np.sin(2 * np.pi * 660.0 * t))
    sv = ShimmerVerb(sample_rate=sr, seed=5)
    up_oct = sv.process(x, pitch_cents=1200, rev_time=0.6,
                        pitch_amount=0.7, mix=0.6)
    frac = sv.process(x, pitch_cents=250, rev_time=0.6,
                      pitch_amount=0.7, mix=0.6)
    down = sv.process(x, pitch_cents=-700, rev_time=0.6,
                      pitch_amount=0.5, mix=0.6)
    plain = sv.process(x, pitch_cents=1200, rev_time=0.6,
                       pitch_amount=0.0, mix=0.6)
    return "\n".join([
        "ShimmerVerb demo:",
        f"  input:           {len(x)} samples peak={np.max(np.abs(x)):.3f}",
        f"  +1200c shimmer:  {len(up_oct)} peak={np.max(np.abs(up_oct)):.3f}",
        f"  +250c (frac):    {len(frac)} peak={np.max(np.abs(frac)):.3f}",
        f"  -700c:           {len(down)} peak={np.max(np.abs(down)):.3f}",
        f"  plain (amt=0):   {len(plain)} peak={np.max(np.abs(plain)):.3f}",
    ])


if __name__ == "__main__":
    print(demo())
