"""Multi-playhead microsonic granular engine — Oddment ODD-1 / ODD-1v style.

Replicable engine design from the Synthtopia item "Oddment ODD-1 Combines
Granular Synthesis, Live Processing And Looping" (2026-10-18). The ODD-1 is
a shared "microsonic engine" running on hardware and plugin with:

* three modes — SYNTH (build playable sounds from samples/recorded audio),
  LIVE (a 60-second rolling buffer turns incoming audio into an instrument),
  LOOPS (record separate loops with independent lengths/speeds/tuning while
  keeping them synchronized);
* two independent layers, each with **four playheads**; each playhead has
  independent pitch, speed and a **TIME PATH** setting — the read position
  can move forward, backward or *freeze* in place (grain windowing continues
  at a fixed position -> spectral/sustain texture), with playback speed and
  pitch shaped independently;
* grain spacing/size morphing smooth pitched playback -> fragmented/rhythmic
  textures;
* a frequency-selective filter applied to individual grains;
* binaural-style spatial cues (per-playhead interaural delay + pan).

What is replicated here (offline DSP equivalent):

* ``Odd1Microsonic`` — two layers x four playheads over a source buffer;
* ``TimePath`` — forward / backward / freeze position curves;
* independent pitch (resample ratio) and read-speed per playhead;
* grain spacing/size controls (smooth -> fragmented morph);
* per-grain one-pole frequency-selective filter;
* LOOPS mode: independent loop lengths/speeds scheduled on a shared clock
  (all loops retrigger on the same bar grid -> phase-locked);
* LIVE mode: rolling ring-buffer capture of incoming audio.

Not replicated: touchscreen/encoders, CV/gate inputs, 2GB factory library,
AUv3 plugin host (this is the offline render equivalent).

Usage:
    from sound.synthesis.odd1_engine import Odd1Microsonic

    om = Odd1Microsonic(sample_rate=44100)
    out = om.render(buffer, mode="synth", time_path="freeze")
"""

from __future__ import annotations

import numpy as np

DEFAULT_SR = 44100
N_PLAYHEADS = 4
N_LAYERS = 2
MAX_ROLLING_SEC = 60.0


class RollingBuffer:
    """Ring buffer for LIVE mode (60 s of incoming audio)."""

    def __init__(self, sample_rate: int, max_sec: float = MAX_ROLLING_SEC):
        self.sample_rate = sample_rate
        self.capacity = int(sample_rate * max_sec)
        self.data = np.zeros(self.capacity, dtype=np.float64)
        self.write_pos = 0
        self.filled = 0

    def write(self, chunk: np.ndarray) -> None:
        x = np.asarray(chunk, dtype=np.float64).reshape(-1)
        for sample in x:
            self.data[self.write_pos] = sample
            self.write_pos = (self.write_pos + 1) % self.capacity
        self.filled = min(self.filled + len(x), self.capacity)

    def read(self, start: int, length: int) -> np.ndarray:
        if self.filled == 0:
            return np.zeros(length)
        out = np.zeros(length)
        start = int(start) % self.capacity
        for i in range(length):
            out[i] = self.data[(start + i) % self.capacity]
        return out

    def available(self) -> int:
        return self.filled


class Playhead:
    """One independent read head: pitch, speed, time path, per-grain filter."""

    def __init__(self, sample_rate: int, seed: int = 0):
        self.sample_rate = sample_rate
        self.rng = np.random.default_rng(seed)
        self.pitch_st = 0.0          # semitones (independent of speed)
        self.speed = 1.0             # read-position speed (fwd/back)
        self.direction = 1           # +1 forward, -1 backward
        self.freeze_pos = 0.0        # position held in freeze mode
        self.filter_cutoff = 1.0     # 0..1 per-grain LP cutoff
        self.pan = 0.0               # -1..1 placement
        self.grain_size_ms = 80.0
        self.grain_spacing_ms = 40.0

    def _grain_filter(self, g: np.ndarray) -> np.ndarray:
        alpha = max(0.01, min(1.0, self.filter_cutoff * 12.0 / self.sample_rate * 1000.0))
        alpha = min(alpha, 0.9)
        y = np.empty_like(g)
        acc = 0.0
        for i in range(len(g)):
            acc += alpha * (g[i] - acc)
            y[i] = acc
        return y


class Odd1Microsonic:
    """Two-layer x four-playhead granular engine (SYNTH/LIVE/LOOPS).

    Args:
        sample_rate: audio sample rate in Hz.
        seed: RNG seed for deterministic playhead placement.
    """

    def __init__(self, sample_rate: int = DEFAULT_SR, seed: int = 0):
        self.sample_rate = int(sample_rate)
        self.rng = np.random.default_rng(seed)
        self.rolling = RollingBuffer(self.sample_rate)
        # layers[L] = [4 playheads]
        self.layers = [
            [Playhead(self.sample_rate, seed + l * 100 + h)
             for h in range(N_PLAYHEADS)]
            for l in range(N_LAYERS)
        ]

    # ------------------------------------------------------------------
    # core renderer (one layer, one playhead stream)
    # ------------------------------------------------------------------
    def _render_layer(self, buffer: np.ndarray, layer_idx: int,
                      time_path: str, n_out: int,
                      grain_size_ms: float, spacing_ms: float,
                      blend: float) -> np.ndarray:
        heads = self.layers[layer_idx]
        n = len(buffer)
        out = np.zeros(n_out, dtype=np.float64)
        acc = np.zeros(n_out, dtype=np.float64)
        for h, ph in enumerate(heads):
            gsz = max(8, int(self.sample_rate * (ph.grain_size_ms or grain_size_ms) / 1000.0))
            hop = max(1, int(self.sample_rate * (ph.grain_spacing_ms or spacing_ms) / 1000.0))
            win = np.hanning(gsz)
            pos = float(self.rng.uniform(0, max(1, n - 1)))
            ratio = 2.0 ** (ph.pitch_st / 12.0)
            i = 0
            while i < n_out:
                # TIME PATH: forward / backward / freeze position update
                if time_path == "freeze":
                    pos = ph.freeze_pos if n else 0.0
                elif time_path == "backward":
                    pos -= ph.speed * ph.direction
                    ph.direction = -1
                else:  # forward
                    pos += ph.speed * ph.direction
                pos = float(np.clip(pos, 0, max(0, n - 1)))
                if time_path == "freeze":
                    ph.freeze_pos = pos
                # read grain (independent pitch via internal resample)
                i0 = int(pos)
                seg = buffer[max(0, i0 - gsz // 2): i0 + gsz // 2]
                if len(seg) < gsz:
                    seg = np.pad(seg, (0, gsz - len(seg)))
                src = np.arange(gsz, dtype=np.float64) / ratio
                src = np.minimum(src, gsz - 1)
                g = np.interp(src, np.arange(gsz), seg)
                g = self._apply_per_grain(layer_idx, h, g, buffer, i0)
                g = g * win * blend
                avail = min(gsz, max(1, n_out - i))
                out[i:i + avail] += g[:avail]
                acc[i:i + avail] += win[:avail]
                i += hop
        acc = np.maximum(acc, 1e-8)
        return out / acc

    def _apply_per_grain(self, layer: int, head: int, g: np.ndarray,
                         buffer: np.ndarray, i0: int) -> np.ndarray:
        """Per-grain frequency-selective filter + cross-layer processing."""
        ph = self.layers[layer][head]
        g = ph._grain_filter(g)
        # layer 1 can process layer 0's output: crude cross-layer bleed is
        # handled by the caller via `blend`; here just apply the filter.
        return g

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def render(self, buffer: np.ndarray, mode: str = "synth",
               time_path: str = "forward", n_out: int = None,
               grain_size_ms: float = 80.0, spacing_ms: float = 40.0,
               loops=None, bpm: float = 120.0) -> np.ndarray:
        """Render ``buffer`` (mono float) through the microsonic engine.

        Args:
            buffer: source audio (SYNTH: a sample; LIVE: use
                ``capture()`` first and pass its output).
            mode: "synth" | "live" | "loops".
            time_path: "forward" | "backward" | "freeze" (applies to all
                playheads; per-playhead speed/pitch stay independent).
            n_out: output length in samples (default: len(buffer)).
            loops: for mode="loops", list of (start_sec, len_sec, speed,
                tune_st) dicts; loops are scheduled phase-locked on a
                1-bar grid.
            bpm: tempo for the LOOPS synchronisation grid.

        Returns:
            Mono float array of length ``n_out``.
        """
        if mode == "live":
            if self.rolling.available() == 0:
                raise ValueError("LIVE mode needs audio captured via capture() first")
            buffer = self.rolling.read(0, self.rolling.available())
        n = len(buffer)
        n_out = n_out or n

        if mode == "loops":
            return self._render_loops(buffer, loops or [], bpm, n_out)

        out = np.zeros(n_out, dtype=np.float64)
        for l in range(N_LAYERS):
            blend = 1.0 if l == 0 else 0.6
            out += self._render_layer(buffer, l, time_path, n_out,
                                      grain_size_ms, spacing_ms, blend)
        # two-layer sum, soft-clip
        return np.tanh(out * 0.9)

    def _render_loops(self, buffer: np.ndarray, loops: list,
                      bpm: float, n_out: int) -> np.ndarray:
        """Phase-locked loops: each loop is independent in length/speed/tune
        but retriggers on the shared bar grid -> synchronization."""
        bar = int(self.sample_rate * 240.0 / bpm)  # 4/4 bar at bpm
        out = np.zeros(n_out, dtype=np.float64)
        for spec in loops:
            start = int(spec.get("start_sec", 0.0) * self.sample_rate)
            length = int(spec.get("len_sec", 1.0) * self.sample_rate)
            speed = float(spec.get("speed", 1.0))
            tune = float(spec.get("tune", 0.0))
            if start + length > len(buffer):
                length = max(8, len(buffer) - start)
            loop = buffer[start:start + length]
            ratio = 2.0 ** (tune / 12.0)
            i = 0
            while i < n_out:
                # schedule on the grid: loops retrigger at bar boundaries only
                if i % bar == 0:
                    lane = np.zeros(n_out, dtype=np.float64)
                    src = np.arange(length, dtype=np.float64) * speed
                    src = np.minimum(src, length - 1)
                    lane[i:i + length] = np.interp(src, np.arange(length), loop)
                    out += lane * 0.5
                i += bar
        return np.tanh(out)

    def capture(self, chunk: np.ndarray) -> None:
        """Feed incoming audio into the 60-second rolling buffer (LIVE mode)."""
        self.rolling.write(chunk)

    def set_playhead(self, layer: int, head: int, **kwargs) -> None:
        """Configure one playhead: pitch_st, speed, time_path params,
        filter_cutoff, pan, grain sizes."""
        ph = self.layers[layer][head]
        for k, v in kwargs.items():
            if not hasattr(ph, k):
                raise AttributeError(f"playhead has no parameter {k!r}")
            setattr(ph, k, v)


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: render a pluck sample through SYNTH (3 time paths) and
    LOOPS modes."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    # synthetic "pluck": decaying harmonic tone, 2 s
    t = np.arange(sr * 2) / sr
    pluck = (np.sin(2 * np.pi * 220 * t) * np.exp(-t * 3)
             + 0.4 * np.sin(2 * np.pi * 440 * t) * np.exp(-t * 6))
    pluck = (pluck / np.max(np.abs(pluck)) * 0.9).astype(np.float64)

    om = Odd1Microsonic(sr, seed=11)
    out = {}
    for path in ("forward", "backward", "freeze"):
        y = om.render(pluck, mode="synth", time_path=path)
        fn = os.path.join(out_dir, f"odd1_{path}.wav")
        write_wav(fn, y, sr)
        assert os.path.getsize(fn) > 40, f"empty/corrupt output {fn}"
        out[path] = {"samples": int(y.shape[0]), "peak": float(np.max(np.abs(y)))}

    # LOOPS: three loops, different lengths/speeds, phase-locked
    spec = [
        {"start_sec": 0.0, "len_sec": 1.0, "speed": 1.0, "tune": 0},
        {"start_sec": 0.0, "len_sec": 0.5, "speed": 0.5, "tune": 7},
        {"start_sec": 0.5, "len_sec": 0.75, "speed": 2.0, "tune": -5},
    ]
    yl = om.render(pluck, mode="loops", loops=spec, bpm=120)
    fn = os.path.join(out_dir, "odd1_loops.wav")
    write_wav(fn, yl, sr)
    assert os.path.getsize(fn) > 40
    out["loops"] = {"samples": int(yl.shape[0]), "peak": float(np.max(np.abs(yl)))}

    # LIVE: rolling capture then render
    chunk = pluck[:] + 0.3 * pluck
    om2 = Odd1Microsonic(sr, seed=4)
    om2.capture(chunk)
    yv = om2.render(None, mode="live", time_path="freeze")
    fn = os.path.join(out_dir, "odd1_live.wav")
    write_wav(fn, yv, sr)
    assert os.path.getsize(fn) > 40
    out["live"] = {"samples": int(yv.shape[0]), "peak": float(np.max(np.abs(yv)))}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))