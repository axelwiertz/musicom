"""GILLA ARP-style harmonic-locked arpeggiator + response-curve mod matrix.

Replicates two mechanisms from quietformat CERNION (synthtopia, 2026-11-11):

1. GILLA ARP — "evolving patterns that hold harmonic relationships between
   notes". Implemented as a constrained walk: each new note is chosen from the
   held chord's available pitches *scored by harmonic consonance with the
   previous note and with the chord root*. The consonance score uses real
   interval ratios (2/1, 3/2, 4/3, 5/4, 6/5 ...) mapped into a period-normalised
   distance, so the arp prefers octaves/fifths/fourths but is allowed to move
   to a 9th or a major 7th with the right weight. Evolution comes from a
   recency memory plus a slow register drift, so the pattern develops instead
   of looping.
   CLASSIC ARP — plain 32-step sequencer with per-step velocity and step
   length (gate) for A/B comparison.

2. Modulation matrix with **per-assignment depth and response curve**. Each
   assignment (source -> destination) has its own depth and one of
   linear/exp/log/s-curve; a single source can therefore drive several
   destinations with different curvature. This is what the marketing copy
   means by "a single modulation source affects different parameters in
   different ways".
"""

from __future__ import annotations

import numpy as np

# just-intonation interval ratios used as the consonance reference
CONSONANCE = {
    0: 1.0,     # unison
    7: 0.94,    # perfect fifth 3/2
    5: 0.91,    # perfect fourth 4/3
    4: 0.86,    # major third 5/4
    9: 0.80,    # major sixth 5/3
    3: 0.72,    # minor third 6/5
    8: 0.62,    # minor sixth 8/5
    2: 0.45,    # major second 9/8
    10: 0.40,   # minor seventh 9/5
    11: 0.22,   # major seventh 15/8
    1: 0.15,    # minor second 16/15
    6: 0.30,    # tritone (diminished fifth)
}


def interval_class(a: int, b: int) -> int:
    return abs(a - b) % 12


def consonance(a: int, b: int) -> float:
    return CONSONANCE.get(interval_class(a, b), 0.1)


# --------------------------------------------------------------------------
# modulation matrix with response curves
# --------------------------------------------------------------------------
def response(x: np.ndarray, curve: str = "linear") -> np.ndarray:
    """Shape a normalised 0..1 modulation signal."""
    x = np.clip(np.asarray(x, dtype=float), 0.0, 1.0)
    if curve == "linear":
        return x
    if curve == "exp":
        return x ** 2.2
    if curve == "log":
        return np.log1p(9.0 * x) / np.log(10.0)
    if curve == "s-curve":
        return 0.5 - 0.5 * np.cos(np.pi * x)
    if curve == "inverse":
        return 1.0 - x
    raise ValueError(f"unknown curve {curve!r}")


class ModMatrix:
    """source -> destination assignments, each with own depth + curve."""

    def __init__(self):
        self.assignments = []       # (source, dest, depth, curve)

    def assign(self, source: str, dest: str, depth: float, curve: str = "linear"):
        self.assignments.append((source, dest, float(depth), curve))
        return self

    def apply(self, source_values: dict, base: dict) -> dict:
        """Return destination values = base + depth*response(source)."""
        out = dict(base)
        for src, dest, depth, curve in self.assignments:
            if src not in source_values:
                continue
            shaped = response(np.asarray(source_values[src], dtype=float), curve)
            out[dest] = out.get(dest, 0.0) + depth * shaped
        return out


# --------------------------------------------------------------------------
# arpeggiators
# --------------------------------------------------------------------------
class GillaArp:
    """Harmonic-relationship-preserving evolving arpeggiator."""

    def __init__(self, seed: int = 0, memory: float = 0.55,
                 drift: float = 0.5, rest_prob: float = 0.06,
                 octave_chance: float = 0.18):
        self.rng = np.random.default_rng(seed)
        self.memory = memory          # how strongly recent notes are avoided
        self.drift = drift            # register drift strength
        self.rest_prob = rest_prob
        self.octave_chance = octave_chance

    def generate(self, chord: list[int], steps: int = 16, root: int | None = None,
                 direction: str = "up") -> list[tuple[int, float, float]]:
        """Return [(midi_note, velocity, gate_fraction), ...]."""
        root = chord[0] if root is None else root
        # candidate pool: chord tones over three octaves
        pool = sorted({n + 12 * o for n in chord for o in range(3)})
        hist: list[int] = []
        out = []
        cur = pool[0]
        drift_oct = 0
        for i in range(steps):
            if i % 6 == 5:
                drift_oct = int(np.sign(self.rng.standard_normal()) *
                                (1 if self.rng.random() < self.drift else 0))
                drift_oct = int(np.clip(drift_oct, -1, 1))
            scores = []
            for n in pool:
                s = consonance(n % 12, cur % 12) * 1.0
                s += 0.6 * consonance(n % 12, root % 12)        # stay in chord
                s += 0.35 * (1.0 if n > cur else -0.15) if direction == "up" else 0.0
                for h in hist[-4:]:
                    if n == h:
                        s -= self.memory                   # escape repetition
                if n in hist[-2:]:
                    s -= 0.4
                s -= 0.12 * abs(n - (cur + drift_oct * 12)) / 12.0
                if self.rng.random() < self.octave_chance:
                    s += 0.1
                scores.append(s + self.rng.normal(0, 0.05))
            order = np.argsort(scores)[::-1]
            # softmax-ish pick over the top candidates so it evolves, not loops
            top = order[: max(2, len(order) // 3)]
            w = np.exp(np.array([scores[t] for t in top]) * 3.0)
            w /= w.sum()
            nxt = pool[int(self.rng.choice(top, p=w))]
            vel = float(np.clip(0.55 + 0.4 * consonance(nxt % 12, root % 12)
                                + self.rng.normal(0, 0.05), 0.2, 1.0))
            gate = 0.9 if interval_class(nxt, cur) in (0, 7, 5) else 0.6
            if self.rng.random() < self.rest_prob:
                out.append((int(nxt), 0.0, 0.0))            # rest, keeps phase
            else:
                out.append((int(nxt), vel, gate))
            hist.append(nxt)
            cur = nxt
        return out


class ClassicArp:
    """32-step arpeggiator with per-step velocity and step length."""

    def __init__(self, pattern=None, velocity=None, gate=None, length: int = 32,
                 mode: str = "up", octaves: int = 2):
        self.pattern = pattern            # optional list of pool indices
        self.velocity = velocity or [0.8] * length
        self.gate = gate or [0.5] * length
        self.length = length
        self.mode, self.octaves = mode, octaves

    def generate(self, chord: list[int], steps: int = 32):
        pool = sorted({n + 12 * o for n in chord for o in range(self.octaves)})
        if self.mode == "down":
            seq = pool[::-1]
        elif self.mode == "updown":
            seq = pool + pool[-2:0:-1]
        else:
            seq = pool
        out = []
        for i in range(steps):
            idx = self.pattern[i] if self.pattern else i
            n = seq[idx % len(seq)]
            v = float(self.velocity[i % len(self.velocity)])
            g = float(self.gate[i % len(self.gate)])
            out.append((int(n), v, g))
        return out


# --------------------------------------------------------------------------
# rendering (so the arps are audible, not just data)
# --------------------------------------------------------------------------
def render_arp(notes, sr: int = 44100, step_s: float = 0.125,
               wave: str = "saw", detune_cents: float = 6.0,
               cutoff_env: float = 1.0) -> np.ndarray:
    """Simple 2-osc subtractive render of an arp note list."""
    total = int((len(notes) + 2) * step_s * sr)
    out = np.zeros(total)
    for i, (pitch, vel, gate) in enumerate(notes):
        if vel <= 0 or gate <= 0:
            continue
        dur = step_s * min(1.0, gate) * 1.15
        n = int(dur * sr)
        t = np.arange(n) / sr
        f0 = 440.0 * 2 ** ((pitch - 69) / 12.0)
        det = 2 ** (detune_cents / 1200.0)
        sig = 0.5 * np.sin(2 * np.pi * f0 * t) + 0.35 * np.sin(2 * np.pi * f0 * det * t) \
            + 0.15 * np.sin(2 * np.pi * f0 * 2 * t)
        env = np.exp(-t * (6.0 / max(0.05, cutoff_env)))
        seg = sig * env * vel
        i0 = int(i * step_s * sr)
        out[i0:i0 + n] += seg[: max(0, total - i0)]
    peak = np.abs(out).max()
    return out / peak * 0.9 if peak > 1e-9 else out


def demo() -> None:
    chord = [60, 64, 67, 71]          # Cmaj7
    g = GillaArp(seed=11)
    gilla = g.generate(chord, steps=16)
    classic = ClassicArp(mode="up", octaves=2).generate(chord, steps=16)

    ic_g = [interval_class(gilla[i][0], gilla[max(0, i - 1)][0]) for i in range(len(gilla))]
    ic_c = [interval_class(classic[i][0], classic[max(0, i - 1)][0]) for i in range(len(classic))]
    cons_g = float(np.mean([consonance(0, i) for i in ic_g]))
    cons_c = float(np.mean([consonance(0, i) for i in ic_c]))
    print(f"gilla demo: gilla={[n for n, _, _ in gilla]}")
    print(f"  classic={[n for n, _, _ in classic]}")
    print(f"  mean consonance gilla={cons_g:.3f} classic={cons_c:.3f}")
    print(f"  distinct pitches gilla={len(set(n for n, _, _ in gilla))} "
          f"classic={len(set(n for n, _, _ in classic))}")

    a = render_arp(gilla)
    b = render_arp(classic, wave="sine")
    print(f"  rendered gilla={len(a)} samples rms={np.sqrt((a**2).mean()):.4f}, "
          f"classic={len(b)} samples rms={np.sqrt((b**2).mean()):.4f}")

    # modulation matrix: one LFO, three destinations, three curvatures
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * np.arange(2048) / 44100)
    mm = ModMatrix().assign("lfo", "cutoff", 2000, "exp") \
                    .assign("lfo", "pan", 0.5, "s-curve") \
                    .assign("lfo", "fold", 1.0, "log")
    res = mm.apply({"lfo": lfo}, {"cutoff": 400.0, "pan": 0.0, "fold": 0.0})
    print(f"  matrix: cutoff {res['cutoff'].min():.0f}..{res['cutoff'].max():.0f} Hz, "
          f"pan {res['pan'].min():.2f}..{res['pan'].max():.2f}, "
          f"fold {res['fold'].min():.2f}..{res['fold'].max():.2f}")
    # exp vs log must differ at mid-scale: same depth, different curvature
    assert abs(res["cutoff"][512] - 400.0 - 1000.0) > 100.0
    assert cons_g >= cons_c, "gilla arp must be at least as consonant as the plain arp"
    assert len(set(n for n, _, _ in gilla)) >= 3
    assert np.abs(a).max() > 0.5
    print("demo OK")


if __name__ == "__main__":
    demo()
