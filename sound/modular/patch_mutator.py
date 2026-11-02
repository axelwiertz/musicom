# -*- coding: utf-8 -*-
"""Revolt / Massive XL-style controlled patch randomization + mutation.

Replicable logic from two findings:

- Warsaw Wave Revolt (Synthtopia 2026-10-30): "a patch-randomization system
  with controls for selecting which parameters can change, excluding
  specific settings, adjusting randomization strength, and working with
  parameter groups.  This lets users generate variations while retaining
  important parts of an existing sound."
- Native Instruments Massive XL (MusicTech 2026-10-28): a **Mutator** that
  "creates variations of a patch using similarity-aware mutations" and a
  **Randomiser** that "can scramble individual modules while leaving your
  favourite elements untouched", plus Morpher/Animator for performed,
  lockable, transferable movement.

What is replicated here (pure patch-mutation logic, no ML):

- ``PatchMutator``: operates on any flat patch dict ``{"path": value}``
  (paths like ``"osc1.cutoff"``, ``"fx.reverb.mix"`` — compatible with
  ``sound/modular/patch_loader.py``'s JSON patches).
  - ``selectable``: set of paths (or module prefixes) that MAY change;
    everything else is excluded/locked ("leaving your favourite elements
    untouched").
  - ``strength`` 0..1: how far mutations may move a value.
  - ``groups``: path prefix -> group name; parameters in the same group
    receive *correlated* perturbations (the stand-in for "similarity-aware"
    mutation: related parameters move together in a musically coherent way,
    e.g. osc1.detune and osc2.detune both shift up).
  - mutation ops: offset (add a scaled random delta), scale (multiply),
    randomize (resample within a per-param range), swap-within-group,
    scramble (fully randomize a selected module, all other modules locked).
- ``ModuleScrambler``: the Randomiser — pick N modules by name and scramble
  only their parameters, leaving every other module byte-identical.
- ``Morpher``: interpolates between two patches (the Animator/Morpher
  "movement" idea): ``morph(a, b, t)`` walks each shared parameter along a
  smooth curve with per-param easing, so a performance can sweep between
  patches and the result can be locked as a new patch.

Not replicated: Massive XL's Preset Generator (audio-reference -> patch) and
stem separation (both need proprietary ML models), the GUI, MPE handling.
"""

from __future__ import annotations

import numpy as np
from typing import Callable, Dict, List, Optional, Set, Tuple


class PatchMutator:
    """Controlled randomizer for flat patch dicts with groups + locking."""

    def __init__(
        self,
        ranges: Optional[Dict[str, Tuple[float, float]]] = None,
        seed: int = 0,
    ) -> None:
        """``ranges``: param path -> (min, max) for clamp + randomize.

        Params absent from ranges are treated as normalized 0..1 if their
        value lies in 0..1, else they are mutated by relative offsets only.
        """
        self.ranges = ranges or {}
        self._rng = np.random.default_rng(seed)

    # --- config -------------------------------------------------------------
    def mutate(
        self,
        patch: Dict[str, float],
        strength: float = 0.3,
        selectable: Optional[Set[str]] = None,
        excluded: Optional[Set[str]] = None,
        groups: Optional[Dict[str, str]] = None,
        ops: Tuple[str, ...] = ("offset", "scale"),
    ) -> Tuple[Dict[str, float], List[str]]:
        """Return (new_patch, change_report).

        - ``selectable``: exact paths OR module prefixes that may change.
          If None, every param is selectable.
        - ``excluded``: paths locked even if selectable (favourites).
        - ``groups``: path -> group name; same-group params get correlated
          perturbations (similarity-aware behaviour).
        """
        new = dict(patch)
        report: List[str] = []
        # group correlation: one random factor per group, per op pass
        group_factors: Dict[str, float] = {}
        for path, val in patch.items():
            if not self._allowed(path, selectable, excluded):
                continue
            group = (groups or {}).get(path)
            if group is not None and group not in group_factors:
                # correlated factor shared by all params in this group
                group_factors[group] = self._rng.normal(0.0, strength)
            op = self._rng.choice(ops)
            if op == "randomize":
                new[path] = self._randomize(path, val)
                report.append(f"{path}: randomize {val:.3f} -> {new[path]:.3f}")
                continue
            if op == "swap":
                # swap with another param in the same group (same value range)
                partners = [p for p in patch if (groups or {}).get(p) == group
                            and p != path and self._allowed(p, selectable, excluded)]
                if partners:
                    other = self._rng.choice(partners)
                    new[path], new[other] = patch[other], patch[path]
                    report.append(f"{path} <-> {other}: swap")
                    continue
            factor = group_factors.get(group) if group is not None else \
                self._rng.normal(0.0, strength)
            if op == "offset":
                delta = factor * self._scale_for(path, val)
                new[path] = self._clamp(path, val + delta)
                report.append(f"{path}: offset {delta:+.3f}")
            else:  # scale
                s = 1.0 + factor
                new[path] = self._clamp(path, val * s)
                report.append(f"{path}: scale x{s:.3f}")
        return new, report

    # --- helpers -------------------------------------------------------------
    def _allowed(self, path: str, selectable: Optional[Set[str]],
                 excluded: Optional[Set[str]]) -> bool:
        if excluded and path in excluded:
            return False
        if selectable is None:
            return True
        if path in selectable:
            return True
        return any(path.startswith(prefix) for prefix in selectable)

    def _range_for(self, path: str, val: float) -> Tuple[float, float]:
        if path in self.ranges:
            return self.ranges[path]
        if 0.0 <= val <= 1.0:
            return (0.0, 1.0)
        return (val * 0.25, val * 4.0)

    def _clamp(self, path: str, val: float) -> float:
        lo, hi = self._range_for(path, val)
        return float(np.clip(val, lo, hi))

    def _scale_for(self, path: str, val: float) -> float:
        lo, hi = self._range_for(path, val)
        return max((hi - lo) * 0.1, abs(val) * 0.15, 0.01)

    def _randomize(self, path: str, val: float) -> float:
        lo, hi = self._range_for(path, val)
        return float(self._rng.uniform(lo, hi))


class ModuleScrambler:
    """Massive-XL Randomiser: scramble whole modules, lock everything else."""

    def __init__(self, seed: int = 0) -> None:
        self._rng = np.random.default_rng(seed)

    def scramble(self, patch: Dict[str, float], modules: List[str],
                 keep: Optional[Set[str]] = None) -> Tuple[Dict[str, float], List[str]]:
        """Fully randomize params whose path starts with a name in ``modules``.

        ``keep``: paths inside the scrambled modules that stay locked.
        Returns (new_patch, report).
        """
        keep = keep or set()
        new = dict(patch)
        report: List[str] = []
        mut = PatchMutator(seed=int(self._rng.integers(0, 2 ** 31)))
        for path, val in patch.items():
            if path in keep:
                continue
            if any(path.startswith(m) for m in modules):
                new[path] = mut._randomize(path, val)
                report.append(f"{path}: scrambled {val:.3f} -> {new[path]:.3f}")
        return new, report


class Morpher:
    """Animator/Morpher: interpolate between two patches with per-param ease."""

    EASINGS: Dict[str, Callable[[float], float]] = {
        "linear": lambda t: t,
        "in": lambda t: t * t,
        "out": lambda t: 1.0 - (1.0 - t) ** 2,
        "inout": lambda t: 0.5 - 0.5 * np.cos(np.pi * t),
        "bounce": lambda t: 4.0 * t * (1.0 - t),
    }

    def __init__(self, easing: str = "inout") -> None:
        assert easing in self.EASINGS
        self.easing = easing

    def morph(self, a: Dict[str, float], b: Dict[str, float],
              t: float) -> Dict[str, float]:
        """Blend patch ``a`` into patch ``b`` at position ``t`` (0..1)."""
        e = float(self.EASINGS[self.easing](float(np.clip(t, 0.0, 1.0))))
        out: Dict[str, float] = {}
        for path in set(a) | set(b):
            va = a.get(path, 0.0)
            vb = b.get(path, va)
            out[path] = va + e * (vb - va)
        return out

    def animate(self, a: Dict[str, float], b: Dict[str, float],
                frames: int = 16) -> List[Dict[str, float]]:
        """Return ``frames`` intermediate patches (a..b), lockable as new."""
        return [self.morph(a, b, i / (frames - 1)) for i in range(frames)]


def demo() -> None:
    """Mutate a small synth patch and report what changed."""
    patch = {
        "osc1.wave": 0.5, "osc1.detune": 0.05, "osc1.level": 0.8,
        "osc2.wave": 0.2, "osc2.detune": 0.08, "osc2.level": 0.6,
        "filter.cutoff": 0.7, "filter.res": 0.3,
        "env.attack": 0.1, "env.release": 0.4,
        "fx.reverb.mix": 0.25,
    }
    m = PatchMutator(seed=3)
    groups = {"osc1.detune": "detune", "osc2.detune": "detune",
              "osc1.level": "level", "osc2.level": "level"}
    new, report = m.mutate(patch, strength=0.4,
                           selectable={"osc1", "osc2", "filter.cutoff"},
                           excluded={"osc1.wave"},
                           groups=groups)
    changed = [p for p in patch if patch[p] != new[p]]
    locked_ok = new["osc1.wave"] == patch["osc1.wave"]
    print(f"patch_mutator demo: {len(changed)}/{len(patch)} params changed")
    print(f"  changed: {changed}")
    print(f"  excluded osc1.wave locked: {locked_ok}")
    print(f"  report sample: {report[0] if report else '(none)'}")
    sc = ModuleScrambler(seed=5)
    sc_new, sc_report = sc.scramble(patch, modules=["fx"], keep={"fx.reverb.mix"})
    print(f"  scrambler (fx only): {len(sc_report)} params, "
          f"fx.reverb.mix kept: {sc_new['fx.reverb.mix'] == patch['fx.reverb.mix']}")
    morph = Morpher(easing="inout")
    mid = morph.morph(patch, new, 0.5)
    frames = morph.animate(patch, new, 5)
    print(f"  morph: mid filter.cutoff={mid['filter.cutoff']:.3f}, "
          f"{len(frames)} lockable frames")
    assert locked_ok
    assert len(changed) >= 3
    assert len(frames) == 5
    print("demo OK")


if __name__ == "__main__":
    demo()
