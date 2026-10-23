# -*- coding: utf-8 -*-
"""Humanization transformer — concrete → absolute imperfect timing/velocity.

The concrete layer emits perfectly-quantized ``MusicEvent`` material (on-grid
onsets, uniform velocity). A human ear reads that as machine playing. This
module converts those concrete events into absolute-tick events that carry a
believable, human-like imperfection — while preserving the two invariants the
whole engine depends on:

1. **Zero-drift** — every voice still ends exactly on its section boundary
   (the terminal landmark at ``section_len`` is untouched; no note crosses the
   seam).
2. **No backtracking** — onset jitter is forward-clamped (``ns =
   max(prev_start, ...)``) so a MIDI readback never sees a negative delta.

Determinism: seeded RNG (``numpy.random.default_rng``), so the same seed +
profile reproduces byte-identical output. Timing jitter is expressed in
milliseconds and converted to ticks via tempo, so a 10 ms slop stays 10 ms at
60 BPM or 180 BPM (physically correct — human timing error is tempo-invariant
in ms, not ticks).

Humanization is a **concrete → absolute** transform: apply it AFTER grid /
chord-tone quantization (the perfect version is the compositional truth) and
BEFORE ``validate()`` + ``to_midi()`` (the zero-drift gate still guards the
output). Phase-1 raw generative drafts are already imperfect by construction —
do not humanize them.

Profile selection is style-derived (``STYLE_HUMANIZE`` / ``profile_for_style``)
with an optional per-instrument DNA override (timing/velocity/layback/duration
from the instrument registry).
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Sequence, Tuple

from structures.unit import MusicUnit, MusicEvent
from .base import MusicTransformer

__all__ = [
    "HumanizeProfile",
    "STYLE_HUMANIZE",
    "STYLE_HUMANIZE_DEFAULT",
    "profile_for_style",
    "ticks_from_ms",
    "humanize_events",
    "humanize_unit",
    "HumanizeTransformer",
]


@dataclass
class HumanizeProfile:
    """Per-voice humanization parameters.

    All time quantities are in milliseconds and converted to ticks at
    application time (tempo-correct). ``phrase_corr`` is the fraction of the
    timing jitter that is *shared* across the notes of a phrase (a slow
    drift) vs independent per-note jitter (white noise). White per-note noise
    alone reads as mush; correlated drift reads as a hand/phrase breathing.
    """

    timing_sigma_ms: float = 7.0
    velocity_sigma: float = 6.0
    duration_scale: float = 1.0
    duration_sigma: float = 0.02
    layback_ms: float = 0.0
    phrase_corr: float = 0.40
    velocity_min: int = 20
    velocity_max: int = 127
    # subtle timing↔velocity coupling: an accented note (velocity rises by
    # more than `couple_thresh`) is pulled slightly early, like a human.
    couple_thresh: float = 15.0


# Style → humanization overrides, grouped by paradigm (see STYLE_REGISTRY +
# the paradigm→style map: rules→groove, stochastic→organic, nature→ambient).
# Substring-matched against the style name; first hit wins; miss → default.
STYLE_HUMANIZE = {
    # --- rules → groove (tight, in-the-pocket) ---
    "disco":     {"timing_sigma_ms": 3.0, "velocity_sigma": 4.0, "phrase_corr": 0.15, "layback_ms": 2.0},
    "groove":    {"timing_sigma_ms": 3.0, "velocity_sigma": 4.0, "phrase_corr": 0.15, "layback_ms": 1.0},
    "house":     {"timing_sigma_ms": 2.5, "velocity_sigma": 3.5, "phrase_corr": 0.10, "layback_ms": 1.0},
    "techno":    {"timing_sigma_ms": 2.0, "velocity_sigma": 3.0, "phrase_corr": 0.10, "layback_ms": 0.0},
    "edm":       {"timing_sigma_ms": 2.5, "velocity_sigma": 3.5, "phrase_corr": 0.10, "layback_ms": 0.0},
    "pop":       {"timing_sigma_ms": 4.0, "velocity_sigma": 5.0, "phrase_corr": 0.25, "layback_ms": 2.0},
    "hiphop":    {"timing_sigma_ms": 4.0, "velocity_sigma": 4.5, "phrase_corr": 0.30, "layback_ms": 6.0},
    "hip hop":   {"timing_sigma_ms": 4.0, "velocity_sigma": 4.5, "phrase_corr": 0.30, "layback_ms": 6.0},
    "trap":      {"timing_sigma_ms": 4.0, "velocity_sigma": 4.0, "phrase_corr": 0.25, "layback_ms": 6.0},
    "drill":     {"timing_sigma_ms": 4.0, "velocity_sigma": 4.0, "phrase_corr": 0.25, "layback_ms": 6.0},
    "amapiano":  {"timing_sigma_ms": 5.0, "velocity_sigma": 4.5, "phrase_corr": 0.25, "layback_ms": 4.0},
    # --- stochastic → organic (loose, human) ---
    "jazz":      {"timing_sigma_ms": 11.0, "velocity_sigma": 7.0, "phrase_corr": 0.55, "layback_ms": 2.0},
    "blues":     {"timing_sigma_ms": 10.0, "velocity_sigma": 7.0, "phrase_corr": 0.55, "layback_ms": 3.0},
    "folk":      {"timing_sigma_ms": 9.0, "velocity_sigma": 6.5, "phrase_corr": 0.50, "layback_ms": 1.0},
    "country":   {"timing_sigma_ms": 9.0, "velocity_sigma": 6.5, "phrase_corr": 0.50, "layback_ms": 2.0},
    "rock":      {"timing_sigma_ms": 8.0, "velocity_sigma": 6.0, "phrase_corr": 0.40, "layback_ms": 2.0},
    "soul":      {"timing_sigma_ms": 8.0, "velocity_sigma": 6.5, "phrase_corr": 0.45, "layback_ms": 4.0},
    "funk":      {"timing_sigma_ms": 4.0, "velocity_sigma": 6.0, "phrase_corr": 0.25, "layback_ms": 2.0},
    "chanson":   {"timing_sigma_ms": 8.0, "velocity_sigma": 6.0, "phrase_corr": 0.45, "layback_ms": 2.0},
    "latin":     {"timing_sigma_ms": 7.0, "velocity_sigma": 6.0, "phrase_corr": 0.40, "layback_ms": 2.0},
    "bossa":     {"timing_sigma_ms": 7.0, "velocity_sigma": 6.0, "phrase_corr": 0.40, "layback_ms": 2.0},
    "samba":     {"timing_sigma_ms": 7.0, "velocity_sigma": 6.0, "phrase_corr": 0.40, "layback_ms": 2.0},
    "flamenco":  {"timing_sigma_ms": 8.0, "velocity_sigma": 7.0, "phrase_corr": 0.45, "layback_ms": 2.0},
    "reggae":    {"timing_sigma_ms": 8.0, "velocity_sigma": 6.0, "phrase_corr": 0.45, "layback_ms": 4.0},
    # --- nature → ambient / minimal (sparse, breathing) ---
    "ambient":   {"timing_sigma_ms": 6.0, "velocity_sigma": 3.5, "phrase_corr": 0.60, "layback_ms": 0.0},
    "minimal":   {"timing_sigma_ms": 5.0, "velocity_sigma": 3.0, "phrase_corr": 0.55, "layback_ms": 0.0},
    "classical": {"timing_sigma_ms": 7.0, "velocity_sigma": 5.0, "phrase_corr": 0.60, "layback_ms": 1.0},
    "cinematic": {"timing_sigma_ms": 7.0, "velocity_sigma": 5.0, "phrase_corr": 0.60, "layback_ms": 1.0},
    "experimental": {"timing_sigma_ms": 8.0, "velocity_sigma": 6.0, "phrase_corr": 0.50, "layback_ms": 0.0},
}

STYLE_HUMANIZE_DEFAULT = {
    "timing_sigma_ms": 7.0, "velocity_sigma": 6.0,
    "phrase_corr": 0.40, "layback_ms": 1.0,
}


def ticks_from_ms(ms: float, bpm: float, tpb: int = 480) -> float:
    """Convert a millisecond offset to ticks at a given tempo/resolution."""
    if bpm <= 0:
        bpm = 120.0
    return float(ms) / (60000.0 / float(bpm) / tpb)


def profile_for_style(style: Optional[str],
                      instrument_dna=None) -> HumanizeProfile:
    """Build a HumanizeProfile from a style name + optional instrument DNA.

    ``instrument_dna`` is either a dict of HumanizeProfile field overrides or a
    4-tuple ``(timing_sigma_ms, velocity_sigma, layback_ms, duration_sigma)``
    (the shape returned by ``Instrument.humanize_dna``). ``None`` entries are
    ignored so the style value wins.
    """
    s = (style or "").lower().replace("_", " ").replace("-", " ")
    overrides = STYLE_HUMANIZE_DEFAULT
    for key, ov in STYLE_HUMANIZE.items():
        if key in s:
            overrides = ov
            break
    kwargs = dict(overrides)
    if instrument_dna:
        if isinstance(instrument_dna, dict):
            kwargs.update({k: v for k, v in instrument_dna.items() if v is not None})
        else:
            names = ("timing_sigma_ms", "velocity_sigma", "layback_ms", "duration_sigma")
            for k, v in zip(names, instrument_dna):
                if v is not None:
                    kwargs[k] = v
    return HumanizeProfile(**kwargs)


def humanize_events(events: Sequence[MusicEvent],
                    profile: HumanizeProfile,
                    rng: np.random.Generator,
                    span: int,
                    bpm: float = 120.0,
                    tpb: int = 480) -> Tuple[List[MusicEvent], dict]:
    """Humanize a list of cell-local absolute-tick events.

    Returns ``(events_out, stats)``. Audible notes (pitch > 0) get forward-
    clamped timing jitter + velocity jitter + duration breathing; the silent
    terminal landmark (pitch 0) is passed through untouched so the zero-drift
    invariant holds. No event is moved before the previous one (no backtrack)
    and no note tail crosses ``span``.
    """
    sigma_t = ticks_from_ms(profile.timing_sigma_ms, bpm, tpb)
    layback = ticks_from_ms(profile.layback_ms, bpm, tpb)

    out: List[MusicEvent] = []
    prev_start = 0
    phrase = 0.0
    n_notes = 0
    sum_abs_shift = 0.0
    max_abs_shift = 0
    sum_abs_vel = 0.0

    for e in events:
        # silent landmark / rest — pass through, keep the section boundary.
        if getattr(e, "pitch", 0) == 0:
            out.append(e)
            continue

        # Coerce to plain ints: a reconstructed MusicUnit (structured numpy
        # array) yields numpy.uint8/uint16 field values, and numpy arithmetic
        # would leak numpy scalars into the returned stats (non-JSON-serializable).
        pitch = int(e.pitch)
        volume = int(e.volume)
        start = int(e.start_tick)
        end = int(e.end_tick)

        n_notes += 1
        # correlated phrase drift (AR(1)) + independent per-note jitter
        phrase = 0.7 * phrase + float(rng.normal(0.0, sigma_t * profile.phrase_corr))
        jitter = float(rng.normal(0.0, sigma_t * (1.0 - profile.phrase_corr)))
        offset = int(round(layback + phrase + jitter))

        nv = int(round(np.clip(
            volume + float(rng.normal(0.0, profile.velocity_sigma)),
            profile.velocity_min, profile.velocity_max)))
        # accent → slightly early (timing↔velocity coupling)
        if profile.couple_thresh and (nv - volume) > profile.couple_thresh:
            offset -= 1

        ns = max(prev_start, start + offset)

        dur = end - start
        dc = profile.duration_scale + float(rng.normal(0.0, profile.duration_sigma))
        ne = ns + max(1, int(round(dur * dc)))
        if ne > span:
            ne = span
            ns = min(ns, ne - 1)
        if ns < 0:
            ns = 0

        out.append(MusicEvent(pitch=pitch, volume=nv, start_tick=ns, end_tick=ne))
        shift = ns - start
        sum_abs_shift += abs(shift)
        max_abs_shift = max(max_abs_shift, abs(shift))
        sum_abs_vel += abs(nv - volume)
        prev_start = ns

    stats = {
        "n_notes": n_notes,
        "mean_abs_shift_ticks": round(sum_abs_shift / n_notes, 3) if n_notes else 0.0,
        "max_abs_shift_ticks": max_abs_shift,
        "mean_abs_vel_delta": round(sum_abs_vel / n_notes, 3) if n_notes else 0.0,
        "timing_sigma_ticks": round(sigma_t, 3),
    }
    return out, stats


def humanize_unit(unit: MusicUnit, profile: HumanizeProfile, seed: int,
                  span: Optional[int] = None, bpm: float = 120.0,
                  tpb: int = 480) -> Tuple[MusicUnit, dict]:
    """Humanize a single MusicUnit (cell). Returns ``(new_unit, stats)``."""
    rng = np.random.default_rng(seed)
    events = unit.events
    if span is None:
        span = max((e.end_tick for e in events), default=0)
    out, stats = humanize_events(events, profile, rng, span, bpm, tpb)
    return MusicUnit(events=out), stats


class HumanizeTransformer(MusicTransformer):
    """Transformer wrapper: humanize a MusicUnit in place.

    Follows the rhythm.py transformer convention (single-unit transform,
    returns a MusicUnit). ``transform(unit=None, span=None)`` humanizes the
    bound unit (or the passed one) and returns the humanized MusicUnit.
    """

    def __init__(self, profile: Optional[HumanizeProfile] = None, seed: int = 0,
                 bpm: float = 120.0, tpb: int = 480):
        super().__init__(None)
        self.profile = profile or HumanizeProfile()
        self.seed = seed
        self.bpm = bpm
        self.tpb = tpb
        self.rng = np.random.default_rng(seed)
        self.last_stats: dict = {}

    def transform(self, unit: MusicUnit = None, span: Optional[int] = None) -> MusicUnit:
        unit = unit if unit is not None else self._unit
        events = unit.events
        if span is None:
            span = max((e.end_tick for e in events), default=0)
        out, stats = humanize_events(events, self.profile, self.rng, span,
                                     self.bpm, self.tpb)
        self.last_stats = stats
        return MusicUnit(events=out)
