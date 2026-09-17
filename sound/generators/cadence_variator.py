"""Cadence Engine rhythmic variator — Emergence Audio "Envoy" style.

Replicable logic from the Sound On Sound review of Emergence Audio Envoy
(September 2026 issue, reviewed by John Walden).  Envoy is the first product built
on the new **Cadence Engine**, described by the maker as a "Rhythmic Variator":

  * **Two identical sound layers**, each holding its own preset (Envoy's library is
    ~600 analogue percussive synth / Eurorack sources sorted roughly low/mid/high).
  * Each layer has **its own sequencer, randomisation, envelope, modulation and
    effects chain**, plus a shared master effects section.
  * Each layer's sequencer can be set to a **different step count, rate, direction
    and feel** → polyrhythms fall out for free.
  * Every sequencing engine is divided into **four 'blocks' of up to eight steps,
    with the step count set independently within each block**.
  * Per step, independently settable: **velocity, pitch, length, pan, and a combi
    low-pass/high-pass filter**.
  * A master LFO whose rate can be independent of the sequencers.
  * **Flux Randomizer**: a user-defined degree of randomisation applied to *every
    parameter lane*, switchable per block (all four blocks or only selected ones)
    and independent per layer.  Low amounts = "human" variation; high = unsettling.

What is replicated here:
- ``CadenceLayer``: one layer with the four independent blocks, per-block step
  counts, per-step lanes (velocity / pitch / length / pan / LP+HP pair), direction
  (forward, reverse, ping-pong, random), playback rate multiplier and "feel"
  (straight / swing / lurch).
- ``FluxRandomizer``: applies a *depth* to every lane, with per-block enable
  flags — the published behaviour, including the "subtle variation → unsettling"
  curve implemented as depth-proportional jitter with per-lane scaling.
- ``CadenceEngine``: two layers + the master LFO (independent rate), and a
  ``render_events`` path that emits timed parameter tuples so any downstream voice
  (Envoy's percussive sources, or a musicom drum voice) can be driven.
- A combi LP+HP per step is modelled as a band window (``hp``/``lp`` in Hz).

Not replicated: the 2.5 GB Envoy sample library, the Kontakt front-end / keyswitch
mappings, the Omni/Zoned/Split variants.

Usage:
    from sound.generators.cadence_variator import CadenceEngine, FluxRandomizer

    eng = CadenceEngine(bpm=120)
    eng.add_layer("low", block_steps=[8, 8, 4, 6], rate=2)
    eng.add_layer("high", block_steps=[7, 5, 8, 8], rate=3)
    eng.flux = FluxRandomizer(depth=0.25, blocks=[0, 2])
    events = eng.render_events(loops=4)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "StepLanes",
    "CadenceBlock",
    "CadenceLayer",
    "FluxRandomizer",
    "CadenceEngine",
    "DIRECTIONS",
    "FEELS",
    "MAX_BLOCK_STEPS",
    "NUM_BLOCKS",
]

NUM_BLOCKS = 4
MAX_BLOCK_STEPS = 8
DIRECTIONS = ("forward", "reverse", "pingpong", "random")
FEELS = ("straight", "swing", "lurch")


@dataclass
class StepLanes:
    """Per-step parameter lanes for one block (the published five + filters).

    All lanes are arrays of length ``steps``.  ``pitch`` is a semitone offset from
    the layer's root, ``length`` a fraction of a step, ``pan`` in -1..+1, and
    ``lp``/``hp`` the combi filter pair in Hz (0 = wide open/off).
    """

    steps: int = 4
    velocity: np.ndarray = None       # 0..127
    pitch: np.ndarray = None          # semitone offsets
    length: np.ndarray = None         # 0..2 of a step
    pan: np.ndarray = None            # -1..+1
    lp: np.ndarray = None             # low-pass cutoff Hz
    hp: np.ndarray = None             # high-pass cutoff Hz

    def __post_init__(self):
        n = int(self.steps)
        if self.velocity is None:
            self.velocity = np.full(n, 100.0)
        if self.pitch is None:
            self.pitch = np.zeros(n)
        if self.length is None:
            self.length = np.full(n, 0.6)
        if self.pan is None:
            self.pan = np.zeros(n)
        if self.lp is None:
            self.lp = np.full(n, 12000.0)
        if self.hp is None:
            self.hp = np.full(n, 20.0)

    def resize(self, steps: int) -> None:
        """Grow/shrink every lane to ``steps`` (new entries inherit the last value)."""
        steps = int(steps)
        for name in ("velocity", "pitch", "length", "pan", "lp", "hp"):
            arr = getattr(self, name)
            if len(arr) == steps:
                continue
            if len(arr) > steps:
                setattr(self, name, arr[:steps])
            else:
                pad = np.repeat(arr[-1:], steps - len(arr)) if len(arr) else \
                    np.zeros(steps)
                setattr(self, name, np.concatenate([arr, pad]))
        self.steps = steps

    def as_dict(self, index: int) -> Dict[str, float]:
        """Lane values at ``index`` (modulo length) as a plain dict."""
        i = int(index) % max(1, self.steps)
        return {name: float(getattr(self, name)[i])
                for name in ("velocity", "pitch", "length", "pan", "lp", "hp")}


class CadenceBlock:
    """One of the four blocks: its own step count and lane set."""

    def __init__(self, steps: int = 4, lanes: Optional[StepLanes] = None):
        if not 1 <= int(steps) <= MAX_BLOCK_STEPS:
            raise ValueError(f"block steps must be 1..{MAX_BLOCK_STEPS}")
        self.lanes = lanes or StepLanes(steps)
        self.lanes.resize(int(steps))

    @property
    def steps(self) -> int:
        return self.lanes.steps

    def set_step(self, index: int, **lanes) -> None:
        """Set any subset of lanes at ``index`` (e.g. ``velocity=120, pan=0.3``)."""
        for name, value in lanes.items():
            if name not in ("velocity", "pitch", "length", "pan", "lp", "hp"):
                raise ValueError(f"unknown lane {name!r}")
            arr = getattr(self.lanes, name)
            arr[int(index) % self.steps] = float(value)

    def set_pattern(self, lane: str, values: Sequence[float]) -> None:
        """Replace one lane wholesale (resizes the block to ``len(values)``)."""
        if lane not in ("velocity", "pitch", "length", "pan", "lp", "hp"):
            raise ValueError(f"unknown lane {lane!r}")
        values = list(values)
        if not 1 <= len(values) <= MAX_BLOCK_STEPS:
            raise ValueError(f"block may hold 1..{MAX_BLOCK_STEPS} steps")
        other = {n: getattr(self.lanes, n) for n in
                 ("velocity", "pitch", "length", "pan", "lp", "hp") if n != lane}
        steps = len(values)
        new = StepLanes(steps=steps, **{k: v[:steps] if len(v) >= steps
                                        else np.repeat(v[-1:], steps)
                                        for k, v in other.items()})
        setattr(new, lane, np.array(values, dtype=float))
        self.lanes = new


class FluxRandomizer:
    """The Cadence Engine's Flux Randomizer.

    Args:
        depth: 0..1 randomisation amount applied to every lane.
        blocks: which block indices are affected (``None`` = all four).
        lane_weights: per-lane multiplier so, e.g., timing can jitter while pitch
            stays put (mirrors the "every parameter lane" control having a single
            global amount).
    """

    def __init__(self, depth: float = 0.0, blocks: Optional[Sequence[int]] = None,
                 lane_weights: Optional[Dict[str, float]] = None,
                 seed: int = 0):
        self.depth = float(min(1.0, max(0.0, depth)))
        self.blocks = None if blocks is None else sorted({int(b) for b in blocks})
        self.lane_weights = dict(lane_weights or {})
        self.seed = int(seed)

    def affects(self, block_index: int) -> bool:
        """Whether this randomizer touches ``block_index``."""
        return self.blocks is None or int(block_index) in self.blocks

    def apply(self, layer: "CadenceLayer", rng: np.random.Generator) -> int:
        """Randomise the enabled blocks in place; return the number of lanes touched.

        Jitter scales with each lane's *natural span* so a 0..127 velocity lane and
        a -1..+1 pan lane each keep musical meaning: velocity +/-``64*depth``,
        pitch +/-``12*depth`` semitones, length +/-``0.5*depth`` of a step, pan
        +/-``0.5*depth``, and the filter pair by up to a decade either way.
        """
        spans = {"velocity": 64.0, "pitch": 12.0, "length": 0.5,
                 "pan": 0.5, "lp": 6000.0, "hp": 4000.0}
        touched = 0
        if self.depth <= 0.0:
            return 0
        for bi, block in enumerate(layer.blocks):
            if not self.affects(bi):
                continue
            for lane, span in spans.items():
                w = float(self.lane_weights.get(lane, 1.0))
                if w <= 0.0:
                    continue
                arr = getattr(block.lanes, lane)
                jitter = rng.uniform(-1.0, 1.0, size=arr.size) * span * self.depth * w
                setattr(block.lanes, lane, arr + jitter)
                touched += 1
        layer.clamp_lanes()
        return touched


class CadenceLayer:
    """One of the two Envoy layers: 4 blocks, own rate/direction/feel, own LFO.

    Args:
        name: layer label ("low"/"mid"/"high" in the factory library).
        block_steps: step count for each of the four blocks (1..8 each).
        rate: step rate multiplier relative to the host grid (2 = 16ths at 1/8).
        direction: one of :data:`DIRECTIONS`.
        feel: one of :data:`FEELS`.
        root: MIDI root note of the layer.
        gain: layer gain.
    """

    def __init__(self, name: str = "layer", block_steps: Sequence[int] = (8, 8, 8, 8),
                 rate: float = 2.0, direction: str = "forward",
                 feel: str = "straight", root: int = 36, gain: float = 1.0,
                 enabled: bool = True):
        if len(block_steps) != NUM_BLOCKS:
            raise ValueError(f"exactly {NUM_BLOCKS} blocks expected")
        if direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}")
        if feel not in FEELS:
            raise ValueError(f"feel must be one of {FEELS}")
        self.name = str(name)
        self.blocks: List[CadenceBlock] = [CadenceBlock(int(s)) for s in block_steps]
        self.rate = float(rate)
        self.direction = direction
        self.feel = feel
        self.root = int(root)
        self.gain = float(gain)
        self.enabled = bool(enabled)
        self.swing = 0.5
        self.lfo_rate = 0.5
        self.lfo_depth = 0.0

    @property
    def total_steps(self) -> int:
        """All steps across the four blocks (the layer's pattern length)."""
        return sum(b.steps for b in self.blocks)

    def clamp_lanes(self) -> None:
        """Keep every lane inside its physical range after randomisation."""
        for b in self.blocks:
            L = b.lanes
            L.velocity = np.clip(L.velocity, 1.0, 127.0)
            L.pitch = np.clip(L.pitch, -36.0, 36.0)
            L.length = np.clip(L.length, 0.05, 2.0)
            L.pan = np.clip(L.pan, -1.0, 1.0)
            L.hp = np.clip(L.hp, 20.0, 8000.0)
            L.lp = np.clip(L.lp, 200.0, 20000.0)
            # keep the band sane: LP must stay above HP
            L.lp = np.maximum(L.lp, L.hp * 1.2)

    # ------------------------------------------------------------ step mapping
    def step_index(self, position: int, rng: Optional[np.random.Generator] = None) -> int:
        """Flat step index (0..total_steps-1) for playback ``position``.

        Implements the direction modes: forward, reverse, ping-pong, and random
        (the last needs an ``rng``).
        """
        n = self.total_steps
        if n == 0:
            return 0
        p = int(position) % n
        if self.direction == "forward":
            return p
        if self.direction == "reverse":
            return n - 1 - p
        if self.direction == "pingpong":
            period = max(1, 2 * n - 2)
            q = int(position) % period
            return q if q < n else period - q
        if self.direction == "random":
            if rng is None:
                rng = np.random.default_rng(0)
            return int(rng.integers(0, n))
        return p

    def lanes_at(self, flat_index: int) -> Dict[str, float]:
        """Lane values for a flat step index, mapped across the four blocks."""
        i = int(flat_index) % max(1, self.total_steps)
        for b in self.blocks:
            if i < b.steps:
                return b.lanes.as_dict(i)
            i -= b.steps
        return self.blocks[-1].lanes.as_dict(0)

    def feel_offset(self, flat_index: int) -> float:
        """Timing offset in *steps* from the layer's feel setting.

        - ``straight``: none.
        - ``swing``: odd steps delayed by the swing amount.
        - ``lurch``: a repeating 3-3-2 accent grouping (the uneven "drunk" feel).
        """
        if self.feel == "straight":
            return 0.0
        if self.feel == "swing":
            amount = (self.swing - 0.5) * 2.0
            return amount * 0.5 * (1.0 if flat_index % 2 else -0.5)
        # lurch: 3-3-2 grouping, steps pulled around within each group
        group = flat_index % 8
        table = (0.0, -0.05, 0.03, 0.0, -0.02, 0.06, 0.0, -0.04)
        return table[group]

    def lfo_value(self, t: float) -> float:
        """Master-LFO value at time ``t`` (seconds), rate independent of the grid."""
        return self.lfo_depth * np.sin(2.0 * np.pi * self.lfo_rate * t)


class CadenceEngine:
    """Two-layer Cadence Engine with a master LFO and per-layer flux.

    Args:
        bpm: tempo.
        master_lfo_rate: master LFO rate in Hz (independent of the sequencers).
        seed: RNG seed for flux and random direction.
    """

    def __init__(self, bpm: float = 120.0, master_lfo_rate: float = 0.5,
                 seed: int = 0):
        self.bpm = float(bpm)
        self.master_lfo_rate = float(master_lfo_rate)
        self.seed = int(seed)
        self.layers: List[CadenceLayer] = []
        self.flux = FluxRandomizer(depth=0.0)

    def add_layer(self, name: str = "layer",
                  block_steps: Sequence[int] = (8, 8, 8, 8),
                  **kwargs) -> CadenceLayer:
        """Add a layer (Envoy ships two)."""
        layer = CadenceLayer(name=name, block_steps=block_steps, **kwargs)
        self.layers.append(layer)
        return layer

    def layer(self, name: str) -> CadenceLayer:
        """Fetch a layer by name."""
        for L in self.layers:
            if L.name == name:
                return L
        raise KeyError(name)

    def master_lfo(self, t: float) -> float:
        """Master LFO value at time ``t``."""
        return np.sin(2.0 * np.pi * self.master_lfo_rate * t)

    # ------------------------------------------------------------------ timing
    def step_seconds(self, layer: CadenceLayer) -> float:
        """Seconds per step for a layer (rate is a multiplier on 1/8 notes)."""
        base = 60.0 / self.bpm / 2.0            # one 8th note
        return base / max(0.05, layer.rate)

    def render_events(self, loops: int = 1, seed: Optional[int] = None,
                      apply_flux: bool = True) -> List[Dict[str, object]]:
        """Render every enabled layer to timed parameter events.

        Returns dicts with ``layer``, ``start``, ``length``, ``pitch``,
        ``velocity``, ``pan``, ``hp``, ``lp``, ``lfo`` — everything a downstream
        percussive voice needs.
        """
        rng = np.random.default_rng(self.seed if seed is None else int(seed))
        if apply_flux:
            for L in self.layers:
                self.flux.apply(L, rng)

        events: List[Dict[str, object]] = []
        for L in self.layers:
            if not L.enabled:
                continue
            step_s = self.step_seconds(L)
            n = L.total_steps
            for pos in range(n * int(loops)):
                flat = L.step_index(pos, rng)
                lanes = L.lanes_at(flat)
                if lanes["velocity"] <= 0.5:
                    continue                  # velocity 0 = rest
                start = pos * step_s + L.feel_offset(flat) * step_s
                t_abs = start
                events.append({
                    "layer": L.name,
                    "step": flat,
                    "start": max(0.0, start),
                    "length": max(0.01, lanes["length"] * step_s),
                    "pitch": int(round(L.root + lanes["pitch"])),
                    "velocity": int(round(min(127.0, lanes["velocity"] * L.gain))),
                    "pan": float(lanes["pan"]),
                    "hp": float(lanes["hp"]),
                    "lp": float(lanes["lp"]),
                    "lfo": float(self.master_lfo(t_abs) + L.lfo_value(t_abs)),
                })
        events.sort(key=lambda e: e["start"])
        return events

    def block_view(self) -> List[str]:
        """Human-readable per-layer block/step layout (demo + tests)."""
        rows = []
        for L in self.layers:
            cells = " | ".join(f"b{i}:{b.steps}st" for i, b in enumerate(L.blocks))
            rows.append(f"{L.name:<6s} rate={L.rate:<4g} {L.direction:<9s} "
                        f"{L.feel:<8s} total={L.total_steps:2d}  {cells}")
        return rows


# ------------------------------------------------------------------------ demo
def demo() -> str:
    """Prove independent blocks, polyrhythm, per-step lanes and Flux behaviour."""
    eng = CadenceEngine(bpm=120, master_lfo_rate=1.3, seed=5)
    low = eng.add_layer("low", block_steps=[8, 8, 4, 6], rate=2, direction="forward",
                        feel="straight", root=36)
    high = eng.add_layer("high", block_steps=[7, 5, 8, 8], rate=3,
                         direction="pingpong", feel="swing", root=72)

    print(f"blocks per layer: {NUM_BLOCKS}, max steps per block: {MAX_BLOCK_STEPS}")
    for row in eng.block_view():
        print("  " + row)
    print(f"layer totals differ -> polyrhythm: {low.total_steps} vs "
          f"{high.total_steps} steps")
    assert low.total_steps != high.total_steps

    # per-step lanes: five published params + the combi LP/HP pair
    low.blocks[0].lanes.velocity = np.full(8, 110.0)
    low.blocks[0].set_step(0, velocity=127, pitch=0, length=0.9, pan=-0.6,
                           hp=120, lp=2000)
    low.blocks[0].set_step(4, velocity=70, pitch=5, length=0.35, pan=0.5,
                           hp=400, lp=6500)
    low.blocks[0].lanes.velocity[7] = 0.0            # a rest inside the block
    print("block 0 step 0 lanes:", low.lanes_at(0))
    print("block 0 step 4 lanes:", low.lanes_at(4))
    assert low.lanes_at(0)["pan"] == -0.6
    assert low.lanes_at(0)["hp"] == 120.0

    # a rest is honoured
    ev = eng.render_events(loops=1, seed=1, apply_flux=False)
    rest_hit = [e for e in ev if e["layer"] == "low" and e["step"] == 7]
    print(f"velocity-0 step produced {len(rest_hit)} events (expected 0)")
    assert not rest_hit

    # directions
    print("direction mapping over 6 playback positions:")
    for d in DIRECTIONS:
        low.direction = d
        print(f"   {d:9s} -> {[low.step_index(p, np.random.default_rng(p)) for p in range(6)]}")
    low.direction = "forward"
    rev = CadenceLayer("r", direction="reverse")
    print(f"   reverse of a {rev.total_steps}-step layer starts at step "
          f"{rev.step_index(0)} and ends at {rev.step_index(rev.total_steps - 1)}")
    assert rev.step_index(0) == rev.total_steps - 1

    # feels change absolute timing
    for feel in FEELS:
        low.feel = feel
        e = eng.render_events(loops=1, seed=2, apply_flux=False)
        starts = [float(x["start"]) for x in e if x["layer"] == "low"]
        unq = sorted({round(s, 6) for s in starts})
        print(f"   feel {feel:8s}: {len(unq)} distinct onset times, "
              f"range {min(starts) * 1000:7.2f}..{max(starts) * 1000:7.2f} ms")
    low.feel = "straight"

    # --- Flux Randomizer: per-block targeting, depth-proportional variation
    base = eng.render_events(loops=1, seed=3, apply_flux=False)
    base_low = [e for e in base if e["layer"] == "low"]
    base_times = [float(e["start"]) for e in base_low]
    base_vels = [float(e["velocity"]) for e in base_low]
    base_lens = [float(e["length"]) for e in base_low]
    base_pans = [float(e["pan"]) for e in base_low]

    eng.flux = FluxRandomizer(depth=0.0, blocks=[0, 2], seed=9)
    same = [e for e in eng.render_events(loops=1, seed=3, apply_flux=True)
            if e["layer"] == "low"]
    ident = all(a["start"] == b["start"] and a["velocity"] == b["velocity"]
                for a, b in zip(base_low, same))
    print(f"flux depth 0.0 leaves the pattern untouched: {ident}")
    assert ident

    def flux_stats(depth, blocks):
        """Mean |length| and |velocity| deviation after flux, plus onset spread.

        Note: the published lane set has **no timing lane**, so flux changes
        velocity / length / pan / filter but leaves step *starts* on the grid —
        the honest behaviour, and why the timing column is flat below.
        """
        eng.flux = FluxRandomizer(depth=depth, blocks=blocks, seed=11)
        ev = [x for x in eng.render_events(loops=1, seed=11, apply_flux=True)
              if x["layer"] == "low"]
        m = min(len(ev), len(base_times))
        tdev = float(np.mean([abs(float(a["start"]) - b)
                              for a, b in zip(ev[:m], base_times[:m])])) * 1000.0
        vdev = float(np.mean(np.abs(
            np.array([float(x["velocity"]) for x in ev[:m]])
            - np.array(base_vels[:m]))))
        ldev = float(np.mean(np.abs(
            np.array([float(x["length"]) for x in ev[:m]])
            - np.array(base_lens[:m])))) * 1000.0
        pdev = float(np.mean(np.abs(
            np.array([float(x["pan"]) for x in ev[:m]])
            - np.array(base_pans[:m]))))
        return tdev, vdev, ldev, pdev

    t01, v01, l01, p01 = flux_stats(0.1, [0, 2])
    t05, v05, l05, p05 = flux_stats(0.5, [0, 2])
    t10, v10, l10, p10 = flux_stats(1.0, [0, 2])
    t3, v3, l3, p3 = flux_stats(0.5, [1, 3])
    print(f"flux velocity deviation: depth 0.1 -> {v01:5.2f}, 0.5 -> {v05:5.2f}, "
          f"1.0 -> {v10:5.2f}  (low = 'human' variation, high = unsettling)")
    print(f"flux length deviation:   depth 0.1 -> {l01:5.2f} ms, 0.5 -> "
          f"{l05:5.2f} ms, 1.0 -> {l10:5.2f} ms")
    print(f"flux pan deviation:      depth 0.1 -> {p01:5.3f}, 0.5 -> {p05:5.3f}, "
          f"1.0 -> {p10:5.3f}")
    print(f"flux targets blocks 1,3 only at depth 0.5 -> velocity dev {v3:5.2f} "
          f"(vs {v05:5.2f} when targeting blocks 0,2)")
    print(f"onset deviation stays {t05:.2f} ms at every depth "
          f"(the lane set has no timing lane — starts remain on the grid)")
    assert v05 > v01 > 0.0, "deeper flux must add more velocity variation"
    assert v10 > v05, "depth 1.0 must exceed depth 0.5"
    assert l05 > l01
    assert p05 > p01
    assert abs(t05 - t01) < 1e-9, "flux must not move step starts (no timing lane)"
    assert abs(v3 - v05) > 1e-9, "targeting different blocks must change the result"

    # per-block targeting really does skip other blocks
    eng.flux = FluxRandomizer(depth=0.6, blocks=[0], seed=4)
    L2 = eng.layer("low")
    before_b1 = L2.blocks[1].lanes.velocity.copy()
    eng.render_events(loops=1, seed=4, apply_flux=True)
    print(f"block 1 untouched when flux targets only block 0: "
          f"{np.allclose(before_b1, L2.blocks[1].lanes.velocity)}")
    assert np.allclose(before_b1, L2.blocks[1].lanes.velocity)

    eng.flux = FluxRandomizer(depth=0.25, blocks=None, seed=6)
    touched = eng.flux.apply(eng.layer("low"), np.random.default_rng(6))
    print(f"flux applied to all 4 blocks: {touched} lane-arrays jittered")
    assert touched == 4 * 6

    # ranges stay legal after heavy flux
    eng.flux = FluxRandomizer(depth=1.0, blocks=None, seed=8)
    eng.flux.apply(eng.layer("low"), np.random.default_rng(8))
    L = eng.layer("low")
    for b in L.blocks:
        assert b.lanes.velocity.min() >= 1.0 and b.lanes.velocity.max() <= 127.0
        assert b.lanes.pan.min() >= -1.0 and b.lanes.pan.max() <= 1.0
        assert np.all(b.lanes.lp >= b.lanes.hp * 1.2)
    print("after depth-1.0 flux: velocity/pan in range, LP still above HP -> True")

    # independent LFO rates
    eng.flux = FluxRandomizer(depth=0.0)
    low.lfo_rate, low.lfo_depth = 0.4, 0.3
    high.lfo_rate, high.lfo_depth = 2.7, 0.3
    ev = eng.render_events(loops=2, seed=12, apply_flux=False)
    lfo_low = [e["lfo"] for e in ev if e["layer"] == "low"]
    lfo_high = [e["lfo"] for e in ev if e["layer"] == "high"]
    print(f"layer LFOs independent: low LFO sd={np.std(lfo_low):.3f} "
          f"high LFO sd={np.std(lfo_high):.3f} "
          f"(rates 0.4 vs 2.7 Hz, master {eng.master_lfo_rate} Hz)")
    assert len(ev) > 10
    print(f"render_events: {len(ev)} events over 2 loops, "
          f"{len({e['layer'] for e in ev})} layers, first={ev[0]['start']:.4f}s")
    print("  cadence_variator demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
