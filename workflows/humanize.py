# -*- coding: utf-8 -*-
"""Composer-level humanization orchestration.

Wraps ``transformers.humanize`` for a ``UnitMatrixComposer``: iterate every
filled voice × section cell, humanize it in place (cell-local ticks), and
return per-voice statistics. Kept in ``workflows/`` (not ``transformers/``)
because it knows the composer's ``voices``/``sections``/``matrix`` shape.

Always-on by convention: ``compose()`` calls this before ``validate()`` +
``to_midi()``. Deterministic given ``seed`` (each voice gets a derived child
seed). Style-derived profiles, overridable per-voice by instrument DNA.
"""

from __future__ import annotations

import numpy as np
from dataclasses import asdict
from typing import Dict, Optional

from structures import MusicUnit
from transformers.humanize import (
    HumanizeProfile,
    humanize_events,
    profile_for_style,
)

__all__ = ["humanize_composer", "export_dual"]


def humanize_composer(composer, style: Optional[str] = None, seed: int = 0,
                      bpm: Optional[float] = None,
                      profiles: Optional[Dict[str, HumanizeProfile]] = None,
                      instruments: Optional[Dict[str, object]] = None) -> dict:
    """Humanize every filled cell of a UnitMatrixComposer in place.

    Args:
        composer: UnitMatrixComposer (duck-typed: needs ``.voices``,
            ``.sections``, ``.matrix``, ``.ticks_per_bar``, ``.ticks_per_beat``,
            and an optional ``.bpm``).
        style: style name for profile derivation (ignored if ``profiles`` given).
        seed: master seed. Each voice derives ``seed * 101 + row`` so voices
            get independent (but reproducible) jitter streams.
        bpm: tempo (defaults to ``composer.bpm``).
        profiles: optional explicit ``{voice_name: HumanizeProfile}`` — wins
            over style/instrument derivation.
        instruments: optional ``{voice_name: dna}`` where ``dna`` is a
            4-tuple ``(timing_sigma_ms, velocity_sigma, layback_ms,
            duration_sigma)`` or a dict of profile overrides (the shape of
            ``Instrument.humanize_dna``).

    Returns:
        ``{voice_name: {seed, profile, n_notes, mean_abs_shift_ticks,
        max_abs_shift_ticks, mean_abs_vel_delta, timing_sigma_ticks}}``.
    """
    bpm = bpm if bpm is not None else getattr(composer, "bpm", 120.0)
    tpb = getattr(composer, "ticks_per_beat", 480)

    summary: dict = {}
    for voice in composer.voices:
        row = voice["row"]
        name = voice["name"]
        dna = (instruments or {}).get(name)
        prof = (profiles or {}).get(name) or profile_for_style(style, dna)

        vseed = int(seed) * 101 + row
        vrng = np.random.default_rng(vseed)

        agg = {"n_notes": 0, "sum_abs_shift": 0.0, "max_abs_shift": 0,
               "sum_abs_vel": 0.0, "timing_sigma_ticks": 0.0}
        for section in composer.sections:
            col = section["column"]
            span = int(section["bars"]) * int(composer.ticks_per_bar)
            unit = composer.matrix.get_unit((row, col))
            if unit is None:
                continue
            hevents, stats = humanize_events(unit.events, prof, vrng, span,
                                             bpm, tpb)
            composer.matrix.set_unit((row, col), MusicUnit(events=hevents))
            agg["n_notes"] += stats["n_notes"]
            agg["sum_abs_shift"] += stats["mean_abs_shift_ticks"] * stats["n_notes"]
            agg["max_abs_shift"] = max(agg["max_abs_shift"], stats["max_abs_shift_ticks"])
            agg["sum_abs_vel"] += stats["mean_abs_vel_delta"] * stats["n_notes"]
            agg["timing_sigma_ticks"] = stats["timing_sigma_ticks"]

        n = agg["n_notes"]
        summary[name] = {
            "seed": vseed,
            "profile": asdict(prof),
            "n_notes": n,
            "mean_abs_shift_ticks": round(agg["sum_abs_shift"] / n, 3) if n else 0.0,
            "max_abs_shift_ticks": agg["max_abs_shift"],
            "mean_abs_vel_delta": round(agg["sum_abs_vel"] / n, 3) if n else 0.0,
            "timing_sigma_ticks": agg["timing_sigma_ticks"],
        }
    return summary


def export_dual(composer, perfect_path, humanized_path, style: Optional[str] = None,
                seed: int = 0, bpm: Optional[float] = None,
                instruments: Optional[Dict[str, object]] = None) -> dict:
    """Export a filled composer as BOTH perfect and humanized MIDI.

    The standard dual-version contract (2026-10-17): every composition ships
    a grid-locked `-perfect` artifact (the compositional truth) AND a
    humanized `-humanized` artifact, so the listener can A/B the humanization.

    Order is load-bearing: the composer is validated + exported while still
    grid-perfect, THEN humanized in place, re-validated, and exported a second
    time. Both exports go through the zero-drift gate (`validate()`).

    Args:
        composer: a filled UnitMatrixComposer (duck-typed, as humanize_composer).
        perfect_path: output path for the grid-locked (pre-humanization) MIDI.
        humanized_path: output path for the humanized MIDI.
        style, seed, bpm, instruments: forwarded to humanize_composer.

    Returns:
        The humanize_composer summary (per-voice stats dict).
    """
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"validate() failed (perfect): {msg}")
    composer.to_midi(str(perfect_path))

    hz = humanize_composer(composer, style=style, seed=seed, bpm=bpm,
                           instruments=instruments)

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"validate() failed (humanized): {msg}")
    composer.to_midi(str(humanized_path))
    return hz
