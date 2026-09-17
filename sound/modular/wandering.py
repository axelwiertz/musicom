"""Non-LFO wandering modulation + "happy-drunk" modulation matrix — Sound Dust
"Drift Clouds" style.

Replicable logic from the Sound On Sound review "Sound Dust Drift Clouds"
(September 2026 issue, 4.5/5, reviewed by Dave Gale).  Drift Clouds is a Kontakt
instrument of solo viola/cello/bass played with garden twine rather than bows,
built around two partials per snapshot — an upper **Cloud** layer ("the meat and
potatoes", ADSR + poly/paraphonic + 100 static EQ settings + a five-element
effects section) and a lower **Shadow** layer (simpler, ADSR + looping) — with the
mod wheel hard-wired as a layer balance.

The two genuinely algorithmic pieces (everything else is sample content):

  * **Drift — the "Wandering Engine"**: 'offers varying forms and degrees of
    modulation, although **not with the usual predictability of LFOs**, but by
    means of the Wandering Engine.  This eschews conventional LFO orthodoxy in
    favour of **wonky waves that ebb, flow and slew, often reaching a near halt
    before starting back up again**.'
  * **Portal — "a happy drunk in control of your parameters"**: 'effectively a
    form of **modulation matrix**, but one that thrives on the element of
    surprise.'

What is replicated here:
- ``WanderingEngine``: a modulated *speed* random walk.  The key structural
  difference from an LFO is that there is **no fixed frequency**: an underlying
  Ornstein-Uhlenbeck-style velocity process (mean-reverting drift of drift) drives
  the phase, and a near-halt is produced by periodically collapsing the velocity
  toward zero (the "ebb and almost stop" behaviour).  Output is a slewed, band
  limited 0..1 control signal.  ``stall_probability`` and ``stall_length`` control
  how often and how long it goes quiet; ``wobble``/``roughness`` set the wonk.
- ``Portal``: a modulation matrix whose *routings themselves* are randomised.  It
  holds real source→destination pairs with depths, but re-rolls selected routings
  on demand and can mutate depths continuously, so the patch keeps surprising its
  author — the documented "thrives on the element of surprise".
- ``DriftCloudsVoice``: the two-partial (Cloud / Shadow) layer balance with per
  layer rebalance, drift depth per layer, and the hard-wired mod-wheel balance.

Not replicated: the 9 GB of garden-twine-bowed viola/cello/bass samples, the 22 x 2
articulations, the 100 static EQ curves, the five keyswitchable FX, and the Kontakt
host itself.

Usage:
    from sound.modular.wandering import WanderingEngine, Portal, DriftCloudsVoice

    w = WanderingEngine(seed=3)
    cv = w.process(44100 * 4)              # 4 s of 0..1 modulation
    p = Portal(seed=5)
    p.add_route("drift", "filter_cutoff", depth=0.4)
    p.surprise(amount=0.5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "WanderingEngine",
    "Portal",
    "DriftCloudsVoice",
    "ModRoute",
    "DEFAULT_DESTINATIONS",
]

# Destination names used by the Drift Clouds patch surface (Cloud layer).  Any
# string is accepted; these are the documented/typical ones.
DEFAULT_DESTINATIONS = (
    "filter_cutoff", "eq_tilt", "layer_balance", "pan", "pitch_cents",
    "attack", "release", "grain_position", "effect_mix", "volume",
)


class WanderingEngine:
    """Non-LFO "wonky" modulation source: ebb, flow, slew, near-halt.

    Structure (why this is not an LFO): the walk's *speed and direction* are
    re-drawn on exponentially distributed intervals — a random-telegraph velocity
    — at **four nested timescales** whose rate constants are octave-spaced, and a
    periodic ebb collapses the velocity toward zero for a while.  There is no
    fundamental, and the shape between reversals is warped with an ease curve
    (the "wonky wave" that ebbs and flows).

    Args:
        sample_rate: sample rate in Hz.
        rate: base direction-change rate in changes per second (not a frequency —
            each of the four timescales changes at its own multiple of it).
        wobble: how much of the movement comes from the fast timescales (0..1).
        roughness: sample-to-sample grit added to the control signal (0..1).
        stall_probability: chance per second of starting an ebb (near-halt).
        stall_length: mean duration of an ebb, in seconds.
        slew: output smoothing (0 = raw walk, 1 = heavily slewed).
        seed: RNG seed.
    """

    NESTED = 4                     # timescales: fast wobble -> slow drift

    def __init__(self, sample_rate: int = 44100, rate: float = 0.35,
                 wobble: float = 0.5, roughness: float = 0.05,
                 stall_probability: float = 0.3, stall_length: float = 0.8,
                 slew: float = 0.5, seed: int = 0):
        self.sr = int(sample_rate)
        self.rate = float(max(1e-6, rate))
        self.wobble = float(min(1.0, max(0.0, wobble)))
        self.roughness = float(min(1.0, max(0.0, roughness)))
        self.stall_probability = float(min(1.0, max(0.0, stall_probability)))
        self.stall_length = float(max(0.01, stall_length))
        self.slew = float(min(1.0, max(0.0, slew)))
        self.seed = int(seed)
        self._value = 0.5
        self._stall = 0.0
        self._rng = np.random.default_rng(self.seed)
        # per-timescale velocity + its remaining hold time (seconds)
        self._vel = np.zeros(self.NESTED)
        self._hold = np.zeros(self.NESTED)
        # weights: fast timescale is scaled by wobble, slow by (1 - wobble)
        w = np.array([self.wobble ** i for i in range(self.NESTED)])[::-1]
        self._weights = w / w.sum()

    # ------------------------------------------------------------------ single
    def next_sample(self) -> float:
        """Advance one sample and return the modulation value (0..1)."""
        dt = 1.0 / self.sr
        rng = self._rng

        # --- ebb / near-halt: a Poisson arrival that collapses every velocity
        stalling = self._stall > 0.0
        if stalling:
            self._stall -= dt
        elif rng.random() < self.stall_probability * dt:
            self._stall = float(rng.exponential(self.stall_length))
            stalling = True

        # --- random-telegraph velocity at four octave-spaced timescales
        acc = 0.0
        for k in range(self.NESTED):
            self._hold[k] -= dt
            if stalling:
                self._vel[k] *= 0.55                       # damped during the ebb
            elif self._hold[k] <= 0.0:
                self._hold[k] = float(rng.exponential(
                    1.0 / (self.rate * (2.0 ** k))))
                sigma = self.rate * (2.0 ** k) * 0.6
                self._vel[k] = float(rng.normal(0.0, sigma))
            acc += self._weights[k] * self._vel[k]

        # --- ease-warped integration gives the "ebb and flow" shape
        step = acc * dt * 6.0
        self._value += float(np.sign(step) * (abs(step) ** 0.85))
        if self._value > 1.0:
            self._value = 2.0 - self._value
        elif self._value < 0.0:
            self._value = -self._value
        self._value = float(min(1.0, max(0.0, self._value)))

        out = self._value
        if self.roughness > 0.0:
            out += rng.normal(0.0, self.roughness * 0.02)
        return float(min(1.0, max(0.0, out)))

    # ---------------------------------------------------------------- buffers
    def process(self, n_samples: int, slew: Optional[float] = None) -> np.ndarray:
        """Generate ``n_samples`` of 0..1 modulation, with the Slew control applied."""
        n = int(n_samples)
        raw = np.empty(n)
        for i in range(n):
            raw[i] = self.next_sample()
        s = self.slew if slew is None else float(slew)
        if s <= 0.0:
            return raw
        tau = max(1e-4, s * 2.0)               # slew time constant, seconds
        a = 1.0 - np.exp(-1.0 / (tau * self.sr))
        out = np.empty(n)
        y = raw[0]
        for i, v in enumerate(raw):
            y += a * (v - y)
            out[i] = y
        return out

    # ----------------------------------------------------------------- metrics
    def stall_fraction(self, cv: np.ndarray, threshold: float = 0.02) -> float:
        """Share of frames where the signal is nearly frozen (an "ebb")."""
        if cv.size < 2:
            return 0.0
        d = np.abs(np.diff(cv))
        return float(np.mean(d < threshold * max(1e-6, np.max(d))))


@dataclass
class ModRoute:
    """One source→destination connection inside the Portal matrix."""
    source: str
    destination: str
    depth: float = 0.5
    polarity: float = 1.0
    enabled: bool = True

    def sample(self, value: float) -> float:
        """Apply this route to a source value, returning the modulation offset."""
        return self.polarity * self.depth * float(value)


class Portal:
    """A 'happy drunk' modulation matrix: routings that keep changing their mind.

    Args:
        destinations: pool of destination names used when the matrix surprises you.
        drift: per-sample rate at which route depths wander.
        seed: RNG seed.
    """

    def __init__(self, destinations: Sequence[str] = DEFAULT_DESTINATIONS,
                 drift: float = 0.0, seed: int = 0):
        self.destinations: Tuple[str, ...] = tuple(destinations)
        self.routes: List[ModRoute] = []
        self.drift = float(max(0.0, drift))
        self.seed = int(seed)
        self._rng = np.random.default_rng(self.seed)

    # ---------------------------------------------------------------- editing
    def add_route(self, source: str, destination: str, depth: float = 0.5,
                  polarity: float = 1.0) -> ModRoute:
        """Add a routing (source → destination with a signed depth)."""
        r = ModRoute(source=source, destination=destination,
                     depth=float(depth), polarity=float(polarity))
        self.routes.append(r)
        return r

    def remove_route(self, index: int) -> None:
        """Delete a routing."""
        self.routes.pop(int(index))

    def reroute(self, index: int, destination: Optional[str] = None,
                source: Optional[str] = None) -> ModRoute:
        """Re-point an existing routing at a different destination/source."""
        r = self.routes[int(index)]
        if destination is not None:
            if destination not in self.destinations:
                raise ValueError(f"unknown destination {destination!r}")
            r.destination = destination
        if source is not None:
            r.source = source
        return r

    # ---------------------------------------------------------------- surprise
    def surprise(self, amount: float = 0.5, n: Optional[int] = None) -> int:
        """Randomise the matrix — the documented 'thrives on surprise' behaviour.

        ``amount`` scales how much changes: which routings move, their new
        destinations, and how far depths swing.  Returns the number of routes
        touched.  Note the matrix is never emptied — a drunk Portal still plays.
        """
        amount = float(min(1.0, max(0.0, amount)))
        if amount <= 0.0 or not self.routes:
            return 0
        n_touch = n if n is not None else max(1, int(round(amount * len(self.routes))))
        idx = self._rng.choice(len(self.routes), size=min(n_touch, len(self.routes)),
                               replace=False)
        for i in idx:
            r = self.routes[int(i)]
            if self._rng.random() < amount:
                r.destination = str(self._rng.choice(self.destinations))
            if self._rng.random() < amount:
                r.source = f"{r.source.split('#')[0]}#{int(self._rng.integers(0, 8))}"
            r.depth = float(np.clip(r.depth + self._rng.normal(0.0, 0.3 * amount),
                                    0.0, 1.0))
            if self._rng.random() < 0.3 * amount:
                r.polarity = -r.polarity
        return len(idx)

    # ------------------------------------------------------------------ apply
    def apply(self, sources: Dict[str, float]) -> Dict[str, float]:
        """Sum every enabled route per destination.

        Args:
            sources: mapping of source name -> current value (typically a
                :class:`WanderingEngine` output).

        Returns:
            ``{destination: summed modulation}``.
        """
        out: Dict[str, float] = {}
        for r in self.routes:
            if not r.enabled:
                continue
            val = sources.get(r.source)
            if val is None:
                base = r.source.split("#")[0]
                val = sources.get(base, 0.0)
            out[r.destination] = out.get(r.destination, 0.0) + r.sample(val)
        return out

    def wander_depths(self, dt: float) -> None:
        """Let every depth drift a little (call per block/sample)."""
        if self.drift <= 0.0:
            return
        for r in self.routes:
            r.depth = float(np.clip(
                r.depth + self._rng.normal(0.0, self.drift * dt), 0.0, 1.0))

    def table(self) -> List[str]:
        """Human-readable routing dump."""
        return [f"{'on ' if r.enabled else 'off'} {r.source:>10s} -> "
                f"{r.destination:<16s} depth={r.depth:.3f} "
                f"pol={r.polarity:+.0f}" for r in self.routes]


class DriftCloudsVoice:
    """Two-layer (Cloud / Shadow) voice driven by the Wandering Engine + Portal.

    Args:
        sample_rate: sample rate in Hz.
        cloud_drift / shadow_drift: how much modulation each layer receives.
        mod_wheel: the hard-wired layer balance (0 = all Shadow, 1 = all Cloud).
    """

    def __init__(self, sample_rate: int = 44100, cloud_drift: float = 1.0,
                 shadow_drift: float = 0.35, mod_wheel: float = 0.5,
                 seed: int = 0):
        self.sr = int(sample_rate)
        self.cloud_drift = float(cloud_drift)
        self.shadow_drift = float(shadow_drift)
        self.mod_wheel = float(min(1.0, max(0.0, mod_wheel)))
        self.wander = WanderingEngine(sample_rate=self.sr, seed=int(seed))
        self.portal = Portal(seed=int(seed) + 1)

    @property
    def balance(self) -> Tuple[float, float]:
        """(cloud_gain, shadow_gain) from the hard-wired mod-wheel balance."""
        return self.mod_wheel, 1.0 - self.mod_wheel

    def render(self, cloud: np.ndarray, shadow: np.ndarray,
               n_blocks: int = 32) -> np.ndarray:
        """Mix the two layers with wandering balance, pan and tone.

        The Cloud layer is modulated harder than the Shadow (as documented — the
        Cloud layer "plays host to the greatest number of controls").
        """
        cloud = np.asarray(cloud, dtype=np.float64)
        shadow = np.asarray(shadow, dtype=np.float64)
        n = max(cloud.size, shadow.size)
        if cloud.size < n:
            cloud = np.pad(cloud, (0, n - cloud.size))
        if shadow.size < n:
            shadow = np.pad(shadow, (0, n - shadow.size))

        blk = max(1, n // max(1, int(n_blocks)))
        cg, sg = self.balance
        out = np.zeros(n)
        for start in range(0, n, blk):
            end = min(n, start + blk)
            frac = (end - start) / float(self.sr)
            self.wander.process(max(1, int(frac * 40)))     # advance the wander
            cv = self.wander._value
            mods = self.portal.apply({"drift": cv, "portal": cv})
            cutoff = 0.35 + 1.3 * cv * self.cloud_drift     # normalised 0..~1.6
            balance = float(np.clip(
                cv * 0.25 * self.cloud_drift + (1.0 - cv) * 0.1 * self.shadow_drift
                + self.mod_wheel * 0.0, 0.0, 0.5))
            pan = float(np.clip(mods.get("pan", 0.0), -1.0, 1.0))
            c = cloud[start:end] * cg
            s = shadow[start:end] * sg
            # wandering balance + a one-pole tone move per block
            mix = (1.0 - balance) * c + balance * s
            if cutoff != 1.0:
                a = float(np.clip(1.0 - np.exp(-2.0 * np.pi * cutoff), 0.0, 1.0))
                lp = 0.0
                for i in range(mix.size):
                    lp += a * (mix[i] - lp)
                    mix[i] = lp
            out[start:end] = mix
        # a simple stereo placement from any pan routing
        pan = float(np.clip(self.portal.apply({"drift": self.wander._value})
                            .get("pan", 0.0), -1.0, 1.0))
        l = out * (1.0 - max(0.0, pan))
        r = out * (1.0 + min(0.0, pan))
        peak = float(np.max(np.abs(np.stack([l, r]))))
        if peak > 1e-9:
            l = l / peak * 0.9
            r = r / peak * 0.9
        return np.stack([l, r], axis=1)


def demo() -> str:
    """Prove the wander is non-LFO, that it ebbs, and that Portal surprises."""
    sr = 22050

    # --- the wander is NOT an LFO: no stable dominant frequency
    w = WanderingEngine(sample_rate=sr, rate=0.4, wobble=0.6, seed=3)
    cv = w.process(int(sr * 8.0))
    spec = np.abs(np.fft.rfft(cv - cv.mean()))
    fr = np.fft.rfftfreq(cv.size, 1.0 / sr)
    order = np.argsort(spec)[::-1][:6]
    print(f"wander ({cv.size} samples, 8 s): range {cv.min():.3f}..{cv.max():.3f} "
          f"mean {cv.mean():.3f}")
    print("  top spectral lines:", [f"{fr[i]:.3f} Hz" for i in sorted(order)])

    # The decisive test: an LFO reverses direction at perfectly regular intervals;
    # the wander's intervals are scattered (there is no period to lock onto).
    def reversal_intervals(sig, smooth=None):
        smooth = smooth or max(4, sr // 10)
        x = np.convolve(sig, np.ones(smooth) / smooth, mode="same")
        d = np.sign(np.diff(x))
        d = d[d != 0]
        idx = np.where(np.diff(d) != 0)[0]
        return np.diff(idx) / float(sr) if idx.size >= 2 else np.array([])

    t = np.arange(cv.size) / sr
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t)
    iv_w = reversal_intervals(cv)
    iv_l = reversal_intervals(lfo)
    cv_w = float(iv_w.std() / iv_w.mean()) if iv_w.size else 0.0
    cv_l = float(iv_l.std() / iv_l.mean()) if iv_l.size else 0.0
    print(f"  direction-reversal intervals — wander: {iv_w.size} reversals, "
          f"mean {iv_w.mean():.3f} s, scatter (CV) {cv_w:.3f}")
    print(f"  direction-reversal intervals — 0.4 Hz LFO: {iv_l.size} reversals, "
          f"mean {iv_l.mean():.3f} s, scatter (CV) {cv_l:.3f}")
    print(f"  -> the wander's timing is {cv_w / max(1e-9, cv_l):.0f}x less regular "
          f"than the LFO's: genuinely wonky, not periodic")
    assert cv_w > 8.0 * cv_l, "the wander must not reverse on a regular period"
    assert cv_l < 0.15, "control: an LFO's reversals are metronomic"

    # --- it ebbs: the motion collapses for a while, then resumes
    def frozen_fraction(sig, threshold=0.05):
        d = np.abs(np.diff(sig))
        return float(np.mean(d < threshold * np.percentile(d, 99)))

    cv_flow = WanderingEngine(sample_rate=sr, seed=11, stall_probability=0.0,
                              rate=0.5, wobble=0.3, slew=0.0).process(
        int(sr * 6), slew=0.0)
    cv_ebb = WanderingEngine(sample_rate=sr, seed=11, stall_probability=0.9,
                             rate=0.5, wobble=0.3, slew=0.0).process(
        int(sr * 6), slew=0.0)
    f0, f9 = frozen_fraction(cv_flow), frozen_fraction(cv_ebb)
    print(f"  ebb (near-halt) share of frames: stall_probability 0.0 -> "
          f"{f0 * 100:4.1f} %, 0.9 -> {f9 * 100:4.1f} % of the time")
    assert f9 > f0, "more stalls must mean more near-halted frames"
    speeds = np.abs(np.diff(cv))
    window = sr // 4
    blocks = speeds[: (speeds.size // window) * window].reshape(-1, window).mean(axis=1)
    print(f"  motion varies over a wide range: slowest 250 ms block is "
          f"{blocks.min() / max(1e-12, blocks.max()) * 100:.1f} % of the fastest")
    assert blocks.max() > 3.0 * blocks.min(), "speed must vary over a wide range"

    # --- controls behave as documented
    def mean_speed(**kw):
        e = WanderingEngine(sample_rate=sr, seed=11, **kw)
        v = e.process(int(sr * 4), slew=kw.pop("slew", None) or 0.0)
        return float(np.mean(np.abs(np.diff(v))))

    s_free = mean_speed(stall_probability=0.0, rate=0.5, wobble=0.3)
    s_stall = mean_speed(stall_probability=1.0, rate=0.5, wobble=0.3)
    s_slew0 = mean_speed(slew=0.0, rate=0.9, wobble=0.8)
    s_slew1 = mean_speed(slew=1.0, rate=0.9, wobble=0.8)
    print(f"  stall_probability 0.0 -> mean speed {s_free:.6f}; 1.0 -> {s_stall:.6f}")
    print(f"  slew 0.0 -> mean speed {s_slew0:.6f}; slew 1.0 -> {s_slew1:.6f} "
          f"(slewing smooths the walk)")
    assert s_stall < s_free
    assert s_slew1 < s_slew0 / 5.0

    # --- Portal: a real matrix
    p = Portal(seed=5)
    p.add_route("drift", "filter_cutoff", 0.4)
    p.add_route("drift", "pan", 0.3)
    p.add_route("portal", "eq_tilt", 0.2)
    print(f"portal: {len(p.routes)} routings -> {len({r.destination for r in p.routes})} "
          f"distinct destinations")
    for row in p.table():
        print("   " + row)
    mods = p.apply({"drift": 1.0, "portal": 0.5})
    print(f"  apply(drift=1.0) -> { {k: round(v, 3) for k, v in mods.items()} }")
    assert abs(mods["filter_cutoff"] - 0.4) < 1e-9
    assert abs(mods["eq_tilt"] - 0.1) < 1e-9

    # destinations sum when several sources hit the same one
    p.add_route("portal", "filter_cutoff", 0.5)
    mods = p.apply({"drift": 1.0, "portal": 1.0})
    print(f"  two routes onto filter_cutoff sum to {mods['filter_cutoff']:.3f}")
    assert abs(mods["filter_cutoff"] - 0.9) < 1e-9

    # --- surprise: routings change, but the matrix never empties
    before = p.table()
    n = p.surprise(amount=0.7)
    after = p.table()
    changed = sum(1 for a, b in zip(before, after) if a != b)
    print(f"  surprise(0.7) touched {n} routes, {changed} lines changed")
    assert n > 0 and changed > 0
    assert len(p.routes) == len(before), "surprise must not delete routings"
    print(f"  after surprise: {len(p.routes)} routings still live, "
          f"{len({r.destination for r in p.routes})} destinations")
    p.surprise(amount=1.0, n=len(p.routes))
    assert len(p.routes) == len(before)

    # --- disabled routes are respected, reroute works
    p2 = Portal(seed=5)
    p2.add_route("drift", "filter_cutoff", 0.4)
    p2.add_route("portal", "filter_cutoff", 0.5)
    m_on = p2.apply({"drift": 1.0, "portal": 1.0})
    p2.routes[0].enabled = False
    m_off = p2.apply({"drift": 1.0, "portal": 1.0})
    print(f"  disabling one of two filter_cutoff routes: {m_on['filter_cutoff']:.3f} "
          f"-> {m_off['filter_cutoff']:.3f} (the disabled route leaves the sum)")
    assert abs(m_on["filter_cutoff"] - 0.9) < 1e-9
    assert abs(m_off["filter_cutoff"] - 0.5) < 1e-9
    p2.reroute(1, destination="volume")
    print(f"  reroute -> {p2.routes[1].destination}")
    assert p2.routes[1].destination == "volume"

    # --- full voice: two layers, wandering balance
    rng = np.random.default_rng(2)
    tt = np.arange(int(sr * 3)) / sr
    cloud = 0.6 * np.sin(2 * np.pi * 220 * tt) * np.exp(-tt * 0.7)
    shadow = 0.4 * np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 0.5)
    v = DriftCloudsVoice(sample_rate=sr, cloud_drift=1.0, shadow_drift=0.3,
                         mod_wheel=0.5, seed=4)
    out = v.render(cloud, shadow, n_blocks=48)
    print(f"DriftCloudsVoice: shape={out.shape} peak={np.max(np.abs(out)):.3f} "
          f"finite={np.all(np.isfinite(out))}")
    assert out.shape[1] == 2 and np.all(np.isfinite(out))

    # the balance is hard-wired to the mod wheel and dominated by the Cloud layer
    v2 = DriftCloudsVoice(sample_rate=sr, mod_wheel=0.9, seed=4)
    print(f"mod wheel 0.5 -> cloud/shadow {v.balance}; 0.9 -> {v2.balance}")
    assert v.balance[0] < v2.balance[0]
    assert abs(sum(v.balance) - 1.0) < 1e-9

    # rendered output differs from a static (no-drift) mix
    stat = cloud * v.balance[0] + shadow * v.balance[1]
    static = np.stack([stat / max(1e-9, np.max(np.abs(stat))) * 0.9] * 2, axis=1)
    print(f"drifted mix differs from a static blend: {not np.allclose(out, static)}")
    assert not np.allclose(out, static)
    print("  wandering demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
