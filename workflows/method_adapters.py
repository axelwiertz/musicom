# -*- coding: utf-8 -*-
"""CellMethod adapters for the implemented methods (Phase 4 P1).

PLAN_vary-instrumentation-rhythm.md P2: make ``registry_method(id)`` return a
REAL ``CellMethod`` for the 9 implemented methods (001/002/003/010/012/018/
023/040/079), so a method can drive (a part of) a piece instead of every cell
routing through ``DefaultMethod``'s fixed fillers.

Each adapter's ``generate(ctx, role)`` emits RAW ``RawNote`` (pitch_index in
[0,1] + fractional onset) with the method's character. ``realize_spine.realize``
then maps pitch_index into ``ctx.register``, snaps strong beats to chord tones /
weak beats to scale, grid-locks onsets, and adds the zero-drift landmark. The
method stays independent of the realization — exactly the two-half split.

Determinism: each adapter seeds a ``random.Random`` from ``ctx.seed`` and the
role, so ``compose(..., seed=N)`` is reproducible (same contract as the
humanizer's ``seed * 101 + row``; a distinct multiplier avoids collision).
"""

from __future__ import annotations

import random
from typing import List, Sequence

from structures import MusicEvent  # noqa: F401 (re-export convenience)

from workflows.cell_engine import CellContext, default_resolve_role
from workflows.method_contract import CellMethod, RawNote

__all__ = ["ADAPTERS", "adapter_for", "ROLE_REGISTER"]

# role -> (lo, hi) MIDI register for RAW pitch_index mapping. The default
# compose() fillers hardcode these implicitly; the method spine needs them
# explicit so realize_spine maps pitch_index [0,1] into a sensible register.
ROLE_REGISTER = {
    "lead": (60, 84),
    "pad": (48, 72),
    "harmony": (48, 71),
    "bass": (36, 55),
    "arp": (60, 84),
    "counter": (55, 79),
}

_ROLE_OFFSET = {"lead": 0, "pad": 1, "harmony": 1, "bass": 2, "arp": 3, "counter": 4}


def _rng(ctx: CellContext, role: str) -> random.Random:
    # 977 multiplier keeps method seeds disjoint from the humanizer's 101.
    return random.Random(((ctx.seed or 0) * 977) + _ROLE_OFFSET.get(role, 0))


def _chord_indices(ctx: CellContext) -> List[float]:
    """Chord tones mapped into [0,1] over ctx.register (pitch_index attractors)."""
    lo, hi = ctx.register
    if hi <= lo:
        return [0.33, 0.5, 0.67]
    idx = [(t - lo) / (hi - lo) for t in ctx.chord_tones if lo <= t <= hi]
    return idx or [0.33, 0.5, 0.67]


def _n_steps(ctx: CellContext, step_ticks: int) -> int:
    return max(1, int(ctx.section_len / step_ticks))


class _BaseMethod:
    """Shared resolve_role: position-based (matches DefaultMethod)."""

    def resolve_role(self, ctx: CellContext) -> str:
        role = default_resolve_role(ctx.voice_idx, ctx.instrument_name, ctx)
        if role is None:
            raise ValueError(
                f"no role for voice {ctx.voice_idx!r} instrument {ctx.instrument_name!r}")
        return role


# --- 002 / 010 Markov (Hierarchical Diffusion aliases the same core) --------

class _MarkovMethod(_BaseMethod):
    """Markov walk over pitch_index, attracted to chord-tone indices."""

    def generate(self, ctx: CellContext, role: str) -> List[RawNote]:
        rng = _rng(ctx, role)
        targets = _chord_indices(ctx)
        step = 480  # 8th-note grid
        cur = rng.choice(targets)
        notes = []
        t = 0
        while t < ctx.section_len - step:
            if rng.random() < ctx.density:
                notes.append(RawNote(pitch_index=cur, onset=float(t),
                                     velocity=int(rng.randint(74, 100))))
            nxt = rng.choice(targets)
            cur = cur + 0.55 * (nxt - cur) + rng.uniform(-0.05, 0.05)
            cur = max(0.0, min(1.0, cur))
            t += step
        return notes


# --- 023 Tendency Masking ----------------------------------------------------

class _TendencyMethod(_BaseMethod):
    """Pitch walks inside a moving corridor (bounds narrow/expand over time)."""

    def generate(self, ctx: CellContext, role: str) -> List[RawNote]:
        rng = _rng(ctx, role)
        lo0, hi0 = rng.uniform(0.05, 0.35), rng.uniform(0.65, 0.95)
        lo1, hi1 = rng.uniform(0.2, 0.5), rng.uniform(0.5, 0.8)
        step = 480
        cur = (lo0 + hi0) / 2
        notes = []
        t = 0
        total = ctx.section_len
        while t < total - step:
            p = t / total
            lo = lo0 + p * (lo1 - lo0)
            hi = hi0 + p * (hi1 - hi0)
            if rng.random() < ctx.density:
                notes.append(RawNote(pitch_index=cur, onset=float(t),
                                     velocity=int(rng.randint(70, 96))))
            cur += rng.uniform(-0.09, 0.09)
            cur = max(lo, min(hi, cur))
            t += step
        return notes


# --- 018 Schillinger ---------------------------------------------------------

class _SchillingerMethod(_BaseMethod):
    """Rhythm = algebraic resultant (a vs b); pitch cycles chord tones."""

    def generate(self, ctx: CellContext, role: str) -> List[RawNote]:
        from generators.schillinger import SchillingerGenerator
        rng = _rng(ctx, role)
        a, b = rng.choice([(3, 2), (4, 3), (5, 3), (5, 2)])
        gen = SchillingerGenerator(generator_a=a, generator_b=b)
        durs = gen.generate_resultant()
        targets = _chord_indices(ctx)
        # scale resultant durations into section-length tick budget
        unit = ctx.section_len / sum(durs)
        notes = []
        t = 0.0
        i = 0
        while t < ctx.section_len - 60 and durs:
            dur = durs[i % len(durs)] * unit
            notes.append(RawNote(pitch_index=targets[i % len(targets)],
                                 onset=t, velocity=int(rng.randint(80, 100))))
            t += dur
            i += 1
        return notes


# --- 012 Euclidean -----------------------------------------------------------

class _EuclideanMethod(_BaseMethod):
    """Euclidean onset grid; pitch cycles chord tones."""

    def generate(self, ctx: CellContext, role: str) -> List[RawNote]:
        rng = _rng(ctx, role)
        steps = 16
        onsets = rng.choice([3, 4, 5, 6])
        # Bjorklund positions (even spacing), onset in 16th ticks
        pos = sorted({i * steps // onsets for i in range(onsets)})
        targets = _chord_indices(ctx)
        step = ctx.section_len / steps
        notes = []
        for i in range(steps):
            if i in pos:
                notes.append(RawNote(pitch_index=targets[i % len(targets)],
                                     onset=i * step, velocity=int(rng.randint(80, 100))))
        return notes


# --- 040 Perlin --------------------------------------------------------------

class _PerlinMethod(_BaseMethod):
    """Smoothed (interpolated) random walk — Perlin-ish pitch contour."""

    def generate(self, ctx: CellContext, role: str) -> List[RawNote]:
        rng = _rng(ctx, role)
        step = 240  # 16th-note density
        anchors = [rng.uniform(0.0, 1.0) for _ in range(6)]
        notes = []
        n = _n_steps(ctx, step)
        for i in range(n):
            t = i * step
            if t >= ctx.section_len - step:
                break
            # cosine interpolation between two anchors
            f = (i / max(1, n - 1)) * (len(anchors) - 1)
            a0 = anchors[int(f)]
            a1 = anchors[min(int(f) + 1, len(anchors) - 1)]
            u = f - int(f)
            smooth = (1 - (__import__("math").cos(u * __import__("math").pi))) / 2
            pi = a0 + (a1 - a0) * smooth
            if rng.random() < ctx.density:
                notes.append(RawNote(pitch_index=pi, onset=float(t),
                                     velocity=int(rng.randint(70, 96))))
        return notes


# --- 079 Tintinnabuli --------------------------------------------------------

class _TintinnabuliMethod(_BaseMethod):
    """Stepwise (conjunct) mode walk — the M-voice's inherent stepwise drift."""

    def generate(self, ctx: CellContext, role: str) -> List[RawNote]:
        rng = _rng(ctx, role)
        targets = _chord_indices(ctx)
        step = 480
        cur = rng.choice(targets)
        notes = []
        t = 0
        while t < ctx.section_len - step:
            if rng.random() < ctx.density:
                notes.append(RawNote(pitch_index=cur, onset=float(t),
                                     velocity=int(rng.randint(76, 98))))
            # small step toward the nearest target (stepwise tendency)
            nearest = min(targets, key=lambda x: abs(x - cur))
            cur += rng.choice([-1, 1]) * min(0.06, abs(nearest - cur))
            cur = max(0.0, min(1.0, cur))
            t += step
        return notes


# --- 001 Skeleton-First ------------------------------------------------------

class _SkeletonMethod(_BaseMethod):
    """Framework skeleton: chord tones on strong beats, passing on weak."""

    def generate(self, ctx: CellContext, role: str) -> List[RawNote]:
        rng = _rng(ctx, role)
        targets = _chord_indices(ctx)
        step = 480  # 8ths; strong = beat 1 & 3
        notes = []
        t = 0
        while t < ctx.section_len - step:
            beat_in_bar = int(t) % ctx.bar_ticks
            strong = beat_in_bar in (0, 960)
            if strong:
                pi = targets[(int(t) // ctx.bar_ticks) % len(targets)]
            else:
                pi = rng.choice(targets)
            if rng.random() < ctx.density:
                notes.append(RawNote(pitch_index=pi, onset=float(t),
                                     velocity=int(rng.randint(78, 100))))
            t += step
        return notes


# --- 003 Genetic -------------------------------------------------------------

class _GeneticMethod(_BaseMethod):
    """Seeded population; select the pitch_index nearest a chord-tone index."""

    def generate(self, ctx: CellContext, role: str) -> List[RawNote]:
        rng = _rng(ctx, role)
        targets = _chord_indices(ctx)
        step = 480
        notes = []
        t = 0
        while t < ctx.section_len - step:
            if rng.random() < ctx.density:
                # small "population" of candidates, keep the fittest (closest
                # to a chord tone) — a tiny evolutionary selection step.
                pop = [rng.uniform(0.0, 1.0) for _ in range(5)]
                best = min(pop, key=lambda p: min(abs(p - c) for c in targets))
                notes.append(RawNote(pitch_index=best, onset=float(t),
                                     velocity=int(rng.randint(75, 100))))
            t += step
        return notes


# --- registry ----------------------------------------------------------------

ADAPTERS = {
    "001": _SkeletonMethod,
    "002": _MarkovMethod,
    "003": _GeneticMethod,
    "010": _MarkovMethod,     # Hierarchical Diffusion — Markov base
    "012": _EuclideanMethod,
    "018": _SchillingerMethod,
    "023": _TendencyMethod,
    "040": _PerlinMethod,
    "079": _TintinnabuliMethod,
}


def adapter_for(method_id: str) -> CellMethod:
    """Return a CellMethod adapter, or explain why not (spec-only / gap)."""
    if method_id in ADAPTERS:
        return ADAPTERS[method_id]()

    from generators.generator_registry import GENERATOR_REGISTRY
    if method_id not in GENERATOR_REGISTRY:
        raise KeyError(
            f"method {method_id!r} is not in generator_registry (spec-only, no "
            f"shared code). The composition cron's bespoke generate() is the "
            f"realization for these methods.")
    mod_path, _cls, _ = GENERATOR_REGISTRY[method_id]
    if mod_path is None:
        raise NotImplementedError(
            f"method {method_id!r} is spec-only (no code) — cannot adapt to a CellMethod.")
    raise NotImplementedError(
        f"method {method_id!r} has code but no CellMethod adapter yet.")
