"""Graph-sequenced granular warp processor — Baby Audio HyperWarp style.

Replicable DSP from the Sound On Sound item "Baby Audio announce HyperWarp"
(2026-10-07): a granular time-bending effect where the incoming signal is
broken into micro-sampled grains that are reassembled under the "sonic
imprint" of one of seven effect profiles, driven by a graph-based sequencer
(the user *draws in* speed shifts, stutter steps, direction changes).

What is replicated here (offline DSP equivalent):

* ``HyperWarpGranular`` — granular engine with a **graph sequencer**: a
  step grid (default 16 steps, tempo-synced) whose per-step lanes — speed,
  direction, grain size, pitch, filter cutoff, mix — are interpolated
  smoothly and applied to a stream of windowed grains.
* Seven effect profiles applied per-grain (the "sonic imprint" layer):
  - ``clean``       plain windowed grains, independent pitch/time;
  - ``flange``      tight grains through a short modulated comb/all-pass;
  - ``degrade``     per-grain bit-depth reduction;
  - ``filter_spam`` per-grain resonant filter, cutoff randomized per grain;
  - ``harmo_nicer`` per-grain harmonization (pitch-shifted copies mixed in);
  - ``fauxcoder``   resonant harmonic generator: comb bank tuned to the
                    grain pitch (vocoder-ish spectral shaping);
  - ``lo_fizzly``   per-grain downsampling (zero-order-hold decimation).
* Random patch generator (one-click "randomize" — deterministic per seed).

Not replicated: the VST3/AU/AAX host, the preset library, random patch
explorer UI (this is the offline render equivalent).

Usage:
    from sound.effects.hyperwarp_granular import HyperWarpGranular

    hw = HyperWarpGranular(sample_rate=44100, seed=7)
    out = hw.process(audio, profile="filter_spam", bpm=120, steps=16)
"""

from __future__ import annotations

import numpy as np

DEFAULT_SR = 44100

PROFILES = ("clean", "flange", "degrade", "filter_spam",
            "harmo_nicer", "fauxcoder", "lo_fizzly")


def _hann(n: int) -> np.ndarray:
    return np.hanning(n)


class HyperWarpGranular:
    """Granular warp engine with graph sequencer + per-grain profiles.

    Args:
        sample_rate: audio sample rate in Hz.
        seed: RNG seed for deterministic render (per-grain randomness,
            random-patch generator).
    """

    def __init__(self, sample_rate: int = DEFAULT_SR, seed: int = 0):
        self.sample_rate = int(sample_rate)
        self.rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # graph sequencer -> per-grain parameter lanes
    # ------------------------------------------------------------------
    def _lanes(self, n_steps: int, bpm: float, seed_graph: bool = False):
        """Build per-step lanes and resample them to sample positions.

        Returns a dict of callable-lookup arrays: for each output sample
        index the active speed/dir/size/pitch/filter value.
        """
        r = self.rng if seed_graph else np.random.default_rng(0)
        if seed_graph:
            speed = 2.0 ** r.uniform(-1.0, 1.0, n_steps)      # 0.5x..2x
            size = r.uniform(10.0, 120.0, n_steps)            # ms
            pitch = r.integers(-12, 13, n_steps).astype(float)
            filt = r.uniform(0.05, 1.0, n_steps)
            direction = r.integers(0, 2, n_steps).astype(float)  # 0 fwd, 1 rev
        else:
            speed = np.full(n_steps, 1.0)
            size = np.full(n_steps, 60.0)
            pitch = np.zeros(n_steps)
            filt = np.full(n_steps, 0.5)
            direction = np.zeros(n_steps)
        step_samples = max(1, int(self.sample_rate * 60.0 / bpm / 4.0))  # 1/16
        total = n_steps * step_samples
        idx = np.arange(total)
        xi = idx / step_samples
        return {
            "speed": np.interp(xi, np.arange(n_steps), speed)[:, None],
            "size": np.interp(xi, np.arange(n_steps), size)[:, None],
            "pitch": np.interp(xi, np.arange(n_steps), pitch)[:, None],
            "filt": np.interp(xi, np.arange(n_steps), filt)[:, None],
            "dir": np.round(np.interp(xi, np.arange(n_steps), direction))[:, None],
            "step_samples": step_samples,
        }

    # ------------------------------------------------------------------
    # per-grain profile processors (each returns an equal-length window)
    # ------------------------------------------------------------------
    def _profile_grain(self, grain: np.ndarray, profile: str,
                       cutoff: float, pitch_st: float) -> np.ndarray:
        g = grain.copy()
        n = len(g)
        if profile == "clean":
            pass
        elif profile == "flange":
            # short modulated comb: grain + delayed copy of itself
            d = max(4, int(n * (0.05 + 0.25 * cutoff)))
            g = g + 0.7 * np.roll(g, d)
        elif profile == "degrade":
            bits = 2 + int(6 * cutoff)
            g = np.round(g * (2 ** bits)) / (2 ** bits)
        elif profile == "filter_spam":
            g = self._one_pole(g, max(0.01, cutoff))
        elif profile == "harmo_nicer":
            # harmonized copies: +12st and +7st (or -12) mixed in
            g = (0.6 * g
                 + 0.25 * self._resample(g, 2.0)
                 + 0.15 * self._resample(g, 1.5))
        elif profile == "fauxcoder":
            # resonant harmonic generator: sum of comb-filtered delays
            # tuned to harmonics of the grain pitch
            base = self._grain_freq(n, pitch_st)
            out = np.zeros_like(g)
            for h in range(1, 9):
                dly = max(2, int(self.sample_rate / (base * h * 2.0)))
                out += np.roll(g, dly) / h
            g = g * 0.5 + out * 0.5
        elif profile == "lo_fizzly":
            # zero-order-hold decimation
            ratio = int(np.clip(2 + int(30 * cutoff), 2, 32))
            dec = g[::ratio]
            g = np.repeat(dec, ratio)[:n]
            if len(g) < n:
                g = np.pad(g, (0, n - len(g)))
        return g

    @staticmethod
    def _one_pole(x: np.ndarray, alpha: float) -> np.ndarray:
        y = np.empty_like(x)
        acc = 0.0
        for i in range(len(x)):
            acc += alpha * (x[i] - acc)
            y[i] = acc
        return y

    @staticmethod
    def _resample(x: np.ndarray, ratio: float) -> np.ndarray:
        n = len(x)
        src = np.arange(n, dtype=np.float64) / ratio
        src = np.minimum(src, n - 1)
        return np.interp(src, np.arange(n), x)

    @staticmethod
    def _grain_freq(n: int, pitch_st: float) -> float:
        # rough fundamental of a grain of n samples at current pitch
        return 44100.0 / max(n, 2) * (2.0 ** (pitch_st / 12.0))

    # ------------------------------------------------------------------
    # main engine
    # ------------------------------------------------------------------
    def process(self, audio: np.ndarray, profile: str = "clean",
                bpm: float = 120.0, steps: int = 16,
                grains_per_step: int = 4, randomize: bool = False,
                dry_wet: float = 1.0) -> np.ndarray:
        """Warp ``audio`` through the graph-sequenced granular engine.

        Args:
            audio: mono ``(n,)`` or stereo ``(n, 2)`` float array.
            profile: one of ``PROFILES``.
            bpm: tempo that sets the per-step duration (1/16 grid).
            steps: number of sequencer graph steps.
            grains_per_step: density of grains per step.
            randomize: if True, generate a random graph (seed-graph).
            dry_wet: 0..1 mix of processed vs dry signal.

        Returns:
            Same channel count; length = min(input length, graph length).
        """
        if profile not in PROFILES:
            raise ValueError(f"unknown profile {profile!r}; choose from {PROFILES}")
        x = np.asarray(audio, dtype=np.float64)
        mono = x.ndim == 1
        if mono:
            x = x[:, None]
        lanes = self._lanes(int(steps), float(bpm), seed_graph=randomize)
        graph_len = int(len(lanes["speed"]))
        n = min(len(x), graph_len)

        hop = max(1, int(self.sample_rate * 60.0 / bpm / 4.0 / grains_per_step))

        chans = []
        for c in range(x.shape[1]):
            xc = x[:, c]
            # buffer must hold the *largest* graph grain (up to 150 ms)
            max_gsz = int(self.sample_rate * 0.15)
            wet = np.zeros(n + max_gsz, dtype=np.float64)
            acc = np.zeros(n + max_gsz, dtype=np.float64)
            pos = 0
            while pos < n:
                s = min(pos, graph_len - 1)
                size_s = float(lanes["size"][s, 0])
                gsz = max(16, int(self.sample_rate * size_s / 1000.0))
                win = _hann(gsz)
                speed = float(lanes["speed"][s, 0])
                direction = int(lanes["dir"][s, 0])
                pitch_st = float(lanes["pitch"][s, 0])
                cutoff = float(lanes["filt"][s, 0])

                # source position for this grain
                step_frac = (pos % lanes["step_samples"]) / lanes["step_samples"]
                src_pos = int((pos + step_frac * gsz) * speed)
                if direction == 1:  # reversed: read backwards from src_pos
                    src_pos = n - 1 - src_pos
                src_pos = int(np.clip(src_pos, 0, n - 1))
                seg = xc[max(0, src_pos - gsz // 2): src_pos + gsz // 2]
                if len(seg) < gsz:
                    seg = np.pad(seg, (0, gsz - len(seg)))

                # internal pitch resample (independent of time/position)
                ratio = 2.0 ** (pitch_st / 12.0) * speed
                seg = self._resample(seg, ratio)

                grain = self._profile_grain(seg, profile, cutoff, pitch_st) * win
                avail = min(gsz, max(1, n - pos))
                wet[pos:pos + avail] += grain[:avail]
                acc[pos:pos + avail] += win[:avail]
                pos += hop
            acc = np.maximum(acc, 1e-8)
            wet = wet[:n] / acc[:n]
            dry = xc[:n]
            chans.append((1.0 - dry_wet) * dry + dry_wet * wet)

        out = np.stack(chans, axis=1)
        peak = float(np.max(np.abs(out))) if out.size else 0.0
        if peak > 1.0:
            out = out / peak * 0.95
        return out[:, 0] if mono else out

    def random_patch(self) -> dict:
        """One-click random patch (graph values + random profile)."""
        return {
            "profile": str(self.rng.choice(PROFILES)),
            "steps": int(self.rng.integers(8, 33)),
            "bpm": float(self.rng.integers(70, 170)),
            "grains_per_step": int(self.rng.integers(2, 9)),
            "dry_wet": float(round(self.rng.uniform(0.3, 1.0), 2)),
        }


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: warp a saw arpeggio through every profile."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    t = np.arange(sr * 4) / sr
    # arpeggio-ish saw: step the base freq every 0.5 s
    base = np.array([110.0, 130.81, 164.81, 196.0] * 2)
    freqs = np.interp(t, np.linspace(0, 4, len(base)), base)
    saw = (2.0 / np.pi) * np.sum(
        [np.sin(2 * np.pi * freqs * k * t) / k for k in range(1, 12)], axis=0)
    saw = saw / np.max(np.abs(saw)) * 0.9

    hw = HyperWarpGranular(sr, seed=3)
    out = {}
    for prof in PROFILES:
        y = hw.process(saw, profile=prof, bpm=120, steps=16, randomize=True)
        path = os.path.join(out_dir, f"hyperwarp_{prof}.wav")
        write_wav(path, y, sr)
        assert os.path.getsize(path) > 40, f"empty/corrupt output {path}"
        out[prof] = {
            "samples": int(y.shape[0]),
            "peak": float(np.max(np.abs(y))),
            "patch": hw.random_patch(),
        }
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))