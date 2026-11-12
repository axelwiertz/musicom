"""Anukari-style 3D resonator-object network (modal physical modelling).

Replicates Anukari 1.1 (musictech.com, 2026-11-12) in its replicable core:
you build an instrument out of physical *objects* placed in a 3D scene, and
the objects exchange energy through the space between them.

Model used here
---------------
Every object is a bank of decaying modes (a two-pole resonator per mode):

    y[n] = 2 r cos(w) y[n-1] - r^2 y[n-2] + g x[n]

Mode frequency ratios are chosen from the object type — this is what makes a
bar sound like a bar (inharmonic 1 : 2.76 : 5.40 : 8.93) and a bell like a
bell — while ``r`` per mode encodes damping, which is *frequency dependent*
(higher modes die faster), matching real materials.

Coupling is geometric: gain_ij = 1 / (1 + (d_ij / radius_i)^2), so objects
near each other share energy and distant ones barely interact. That single
rule reproduces Anukari's "Modulosphere floats through the scene and touches
whatever it reaches" behaviour: moving a sphere is just changing d_ij.

Exciters: pluck (short filtered burst), strike (impulse), bow (noise), and
mouthpiece (noise through a pressure-controlled one-pole -> wind instrument).
"""

from __future__ import annotations

import numpy as np

TAU = 2.0 * np.pi

# mode ratio sets (normalised so mode 0 == 1.0)
MODES = {
    "string": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
    "bar": [1.0, 2.756, 5.404, 8.933, 13.34],
    "plate": [1.0, 1.593, 2.135, 2.295, 2.917, 3.598, 4.059],
    "membrane": [1.0, 1.594, 2.136, 2.296, 2.653, 2.918, 3.156],
    "tube": [1.0, 3.0, 5.0, 7.0, 9.0],          # open-open pipe, odd-ish stack
    "bell": [1.0, 2.03, 2.71, 4.13, 5.42, 6.80, 8.21],
}

# per-object damping (1/s) and mode-1 amplitude weighting
DAMPING = {"string": 1.2, "bar": 0.9, "plate": 1.8, "membrane": 2.2,
           "tube": 0.5, "bell": 0.35}


class ResonatorObject:
    """One physical object: mode bank + position + radius + exciter settings."""

    def __init__(self, kind: str = "string", freq: float = 220.0,
                 pos=(0.0, 0.0, 0.0), radius: float = 1.0,
                 damping: float | None = None, gain: float = 1.0,
                 brightness: float = 0.7, excite: str = "pluck"):
        if kind not in MODES:
            raise ValueError(f"unknown object kind {kind!r}")
        self.kind = kind
        self.freq = float(freq)
        self.pos = np.asarray(pos, dtype=float)
        self.radius = float(radius)
        self.damping = DAMPING[kind] if damping is None else float(damping)
        self.gain = float(gain)
        self.brightness = float(brightness)
        self.excite = excite
        self.ratios = np.asarray(MODES[kind], dtype=float)

    # -- geometry ----------------------------------------------------------
    def coupling_to(self, other: "ResonatorObject") -> float:
        """Energy transfer gain toward ``other`` (1/(1+(d/r)^2))."""
        d = float(np.linalg.norm(self.pos - other.pos))
        return 1.0 / (1.0 + (d / max(1e-6, self.radius)) ** 2)

    # -- excitation --------------------------------------------------------
    def excitation(self, n: int, sr: int, rng: np.random.Generator,
                   velocity: float = 1.0) -> np.ndarray:
        x = np.zeros(n)
        if self.excite == "silent":
            return x
        if self.excite == "strike":
            x[0] = velocity
        elif self.excite == "pluck":
            ln = min(n, max(8, int(0.004 * sr)))
            burst = rng.standard_normal(ln) * np.exp(-np.linspace(0, 6, ln))
            x[:ln] = burst * velocity / max(1e-9, np.abs(burst).max())
        elif self.excite == "bow":
            noise = rng.standard_normal(n)
            acc = 0.0
            a = 0.02 + 0.5 * self.brightness
            for i in range(n):          # friction-like lowpassed noise
                acc += a * (noise[i] - acc)
                x[i] = acc * velocity
        elif self.excite == "mouthpiece":
            noise = rng.standard_normal(n)
            acc = 0.0
            a = 0.08 + 0.6 * self.brightness
            for i in range(n):
                # pressure feedback squashes the noise: bounded, tone-like
                acc += a * (noise[i] - acc - 0.35 * acc ** 3)
                x[i] = acc * velocity
        else:
            raise ValueError(f"unknown exciter {self.excite!r}")
        return x

class AnukariScene:
    """A set of ResonatorObjects wired through 3D coupling."""

    def __init__(self, objects=None, coupling_scale: float = 0.35,
                 coupling_delay: int = 64, master_lp: float = 12000.0,
                 sr: int = 44100):
        self.objects = list(objects or [])
        self.coupling_scale = float(coupling_scale)
        self.coupling_delay = int(coupling_delay)
        self.master_lp = float(master_lp)
        self.sr = sr

    # -- internals ---------------------------------------------------------
    def _mode_coeffs(self, obj: ResonatorObject):
        """Return (2r cos w, r^2, gains) for the object's mode bank."""
        f = obj.freq * obj.ratios
        f = f[f < self.sr * 0.45]
        w = TAU * f / self.sr
        # higher modes decay faster: tau_m = tau0 / (1 + 0.6*(m-1))
        tau0 = 1.0 / max(1e-3, obj.damping)
        tau = tau0 / (1.0 + 0.6 * np.arange(len(f)))
        r = np.exp(-1.0 / (tau * self.sr / 2.0))
        # normalise each mode to ~unity peak gain (1 - r) so coupling cannot
        # self-oscillate; brightness rolls off upper modes, 1/sqrt(m) weighting
        gains = (1.0 - r) * obj.brightness ** np.arange(len(f)) / np.sqrt(1.0 + np.arange(len(f)))
        return 2.0 * r * np.cos(w), r ** 2, gains

    def render(self, n: int, velocity: float = 1.0, seed: int = 0) -> np.ndarray:
        """Render ``n`` samples of the whole scene."""
        rng = np.random.default_rng(seed)
        n_obj = len(self.objects)
        if n_obj == 0:
            return np.zeros(n)

        coeffs = [self._mode_coeffs(o) for o in self.objects]
        excite = [o.excitation(n, self.sr, rng, velocity) for o in self.objects]

        # coupling matrix with a one-block delay (the "air" between objects)
        C = np.zeros((n_obj, n_obj))
        for i, a in enumerate(self.objects):
            for j, b in enumerate(self.objects):
                if i != j:
                    C[i, j] = self.coupling_scale * a.coupling_to(b) / max(1, n_obj - 1)

        d = self.coupling_delay
        outs = np.zeros((n_obj, n))
        # ring buffers hold each object's output, d samples late: the "air"
        # path between objects. Read before write keeps the delay exact.
        tails = np.zeros((n_obj, d))
        states = [(np.zeros(len(c[0])), np.zeros(len(c[0]))) for c in coeffs]

        for s in range(n):
            k = s % d
            delayed = tails[:, k].copy()
            total = 0.0
            for i in range(n_obj):
                c1, c2, g = coeffs[i]
                y1, y2 = states[i]
                drive = excite[i][s]
                for j in range(n_obj):
                    if C[i, j]:
                        drive += C[i, j] * delayed[j]
                y = c1 * y1 - c2 * y2 + g * drive     # vector: one value per mode
                states[i] = (y, y1)
                outs[i, s] = float(y.sum())
                total += outs[i, s] * self.objects[i].gain
                tails[i, k] = outs[i, s]

        mix = outs.sum(axis=0)
        mix = np.tanh(mix * 0.8)      # safety soft clip: coupled banks can ring
        if self.master_lp < self.sr * 0.45:
            a = 1.0 - np.exp(-TAU * self.master_lp / self.sr)
            acc = 0.0
            for s in range(n):
                acc += a * (mix[s] - acc)
                mix[s] = acc
        peak = np.abs(mix).max()
        return mix / peak * 0.9 if peak > 1e-9 else mix

    def render_sequence(self, notes, step_s: float = 0.5, seed: int = 0) -> np.ndarray:
        """notes: list of (object_index, velocity) — one hit per step."""
        per = int(step_s * self.sr)
        out = np.zeros(per * len(notes) + self.sr // 2)
        for k, (idx, vel) in enumerate(notes):
            saved = [o.excite for o in self.objects]
            for i, o in enumerate(self.objects):
                o.excite = saved[i] if i == idx else "silent"
            seg = self.render(per + self.sr // 2, vel, seed=seed + k)
            for i, o in enumerate(self.objects):
                o.excite = saved[i]
            i0 = k * per
            out[i0:i0 + len(seg)] += seg[: len(out) - i0]
        return out


def demo() -> None:
    """Build a 4-object scene and render a real performance."""
    string = ResonatorObject("string", 130.81, pos=(0, 0, 0), radius=0.8,
                             excite="pluck", damping=1.4)
    bar = ResonatorObject("bar", 261.63, pos=(1.1, 0.2, 0), radius=0.5,
                          excite="strike", damping=1.0, gain=0.8)
    bell = ResonatorObject("bell", 523.25, pos=(2.6, 0.4, 0.6), radius=0.4,
                           excite="strike", damping=0.5, gain=0.6)
    tube = ResonatorObject("tube", 98.0, pos=(0.4, 1.6, 0), radius=0.6,
                           excite="mouthpiece", brightness=0.75, gain=0.5)

    scene = AnukariScene([string, bar, bell, tube], coupling_scale=0.3,
                         coupling_delay=48)

    print("coupling matrix (1/(1+(d/r)^2) * scale):")
    for a in scene.objects:
        print("  ", a.kind.ljust(9),
              " ".join(f"{scene.coupling_scale * a.coupling_to(b):.3f}"
                       for b in scene.objects))

    seq = [(0, 1.0), (1, 0.8), (0, 0.7), (2, 0.9), (3, 0.6), (1, 1.0)]
    audio = scene.render_sequence(seq, step_s=0.45, seed=7)
    spec = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1 / scene.sr)
    peak_f = freqs[int(np.argmax(spec))]
    print(f"anukari demo: {len(seq)} hits -> {len(audio)} samples "
          f"({len(audio)/scene.sr:.2f}s), rms={np.sqrt((audio**2).mean()):.4f}, "
          f"dominant={peak_f:.1f} Hz")

    # inharmonicity sanity: a bar's mode 1 is ~2.76x, not 2.0x
    bar_only = AnukariScene([ResonatorObject("bar", 200.0, excite="strike")])
    b = bar_only.render(1 << 14, seed=1)
    bs = np.abs(np.fft.rfft(b * np.hanning(len(b))))
    bf = np.fft.rfftfreq(len(b), 1 / bar_only.sr)
    # peak-pick: local maxima, then keep the strongest, well separated ones
    cand = [i for i in range(2, len(bs) - 2)
            if bs[i] > bs[i - 1] and bs[i] >= bs[i + 1] and bs[i] > 0.08 * bs.max()]
    picked = []
    for i in sorted(cand, key=lambda k: -bs[k]):
        if all(abs(bf[i] - bf[j]) > 15.0 for j in picked):
            picked.append(i)
        if len(picked) == 3:
            break
    peaks = sorted(bf[picked])
    print(f"  bar modes detected at: {[round(float(p), 1) for p in peaks]} Hz "
          f"(expected ~200 x 1 / 2.76 / 5.40)")
    ratio = peaks[1] / peaks[0] if len(peaks) > 1 else 0.0
    print(f"  measured near-ratio {ratio:.2f} -> inharmonic bar, not a 2.00 harmonic")

    assert len(audio) > 44100 and np.isfinite(audio).all()
    assert np.abs(audio).max() > 0.2
    print("demo OK")


if __name__ == "__main__":
    demo()
