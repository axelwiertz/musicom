# -*- coding: utf-8 -*-
"""Regression tests for the pop-ballad HITL palette + multi-stem variants.

Locks in two fixes:
  1. Every instrument in every palette is playable in the register its role
     writes. The historical default (Clarinet as texture) wrote 50-60 while
     the clarinet's range starts at 52 — a real out-of-range bug.
  2. Candidates within a round vary DIFFERENT stems. The first version only
     moved the bass, so a round was four near-identical tracks.
"""
import sys
from pathlib import Path

import pytest

PROJECT = Path("/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl")
sys.path.insert(0, str(PROJECT / "Scripts"))
sys.path.insert(0, "/opt/data/projects/Instruments")

from instrument_registry import by_name            # noqa: E402
from phase1_compose import (                       # noqa: E402
    build_ballad, VariantSpec, PALETTES, PALETTE_ORDER, REGISTER,
    INSTRUMENT_POOLS, DEFAULT_PALETTE, palette_for_round,
)
from phase3_hitl import variant_set, SLOT_ROLES    # noqa: E402


def _stem_stats(composer):
    """{voice_name: (min_pitch, max_pitch, note_count)} for audible notes."""
    out = {}
    for v in composer.voices:
        row = v["row"]
        lo, hi, n = 999, 0, 0
        for col in range(len(composer.sections)):
            u = composer.matrix.get_unit((row, col))
            if u is None:
                continue
            for p in u.pitches:
                if p > 0:
                    lo, hi, n = min(lo, p), max(hi, p), n + 1
        out[v["name"]] = (lo, hi, n)
    return out


# ------------------------------------------------------------- palettes --

def test_all_palettes_are_complete():
    for name in PALETTE_ORDER:
        pal = PALETTES[name]
        assert set(pal) == {"Lead", "Pad", "Bass", "Arp", "Drums"}, name


def test_all_palette_instruments_exist_in_registry():
    for name in PALETTE_ORDER:
        for role, instr in PALETTES[name].items():
            by_name(instr)          # raises KeyError if unknown


def test_every_palette_instrument_is_in_range():
    """The bug: texture written at 50-60, below the clarinet's 52 floor."""
    for name in PALETTE_ORDER:
        pal = PALETTES[name]
        composer = build_ballad(seed=7, variant=VariantSpec(palette=pal))
        ok, msg = composer.validate()
        assert ok, f"{name}: {msg}"
        for role, (lo, hi, n) in _stem_stats(composer).items():
            if n == 0:
                continue
            inst = by_name(pal[role])
            if inst.range_min is None:
                continue
            assert lo >= inst.range_min, (
                f"{name}/{role} ({pal[role]}): {lo} below {inst.range_min}")
            assert hi <= inst.range_max, (
                f"{name}/{role} ({pal[role]}): {hi} above {inst.range_max}")


def test_pools_reference_real_instruments():
    for role, names in INSTRUMENT_POOLS.items():
        for n in names:
            by_name(n)


def test_palette_rotates_by_round():
    seen = [PALETTE_ORDER[r % len(PALETTE_ORDER)] for r in range(8)]
    assert seen[0] != seen[1], "successive rounds must differ"
    assert len(set(seen[:len(PALETTE_ORDER)])) == len(PALETTE_ORDER)


def test_palette_for_round_returns_copy():
    p = palette_for_round(0)
    p["Lead"] = "MUTATED"
    assert PALETTES[PALETTE_ORDER[0]]["Lead"] != "MUTATED"


# --------------------------------------------------------- multi-stem --

def test_variant_set_has_one_spec_per_slot():
    specs, palette = variant_set(0, seed=7, n_candidates=4)
    assert len(specs) == 4
    assert palette == PALETTES[PALETTE_ORDER[0]]


def test_candidates_vary_different_stems():
    """The complaint: 'tracks are too equal'. Slots must not be clones."""
    specs, _ = variant_set(0, seed=7, n_candidates=4)
    base = specs[0]
    # slot 1 differs on the anchor
    assert (specs[1].density, specs[1].offset) != (base.density, base.offset)
    # slot 2 differs on the lead method
    assert specs[2].lead_method != base.lead_method
    # slot 3 differs on texture AND bed
    assert (specs[3].arp_rate, specs[3].pad_style) != (base.arp_rate,
                                                       base.pad_style)


def test_each_spec_renders_and_validates():
    specs, _ = variant_set(0, seed=7, n_candidates=4)
    stats = []
    for i, spec in enumerate(specs):
        c = build_ballad(seed=7 + i * 131, variant=spec)
        ok, msg = c.validate()
        assert ok, f"spec {i}: {msg}"
        stats.append(_stem_stats(c))
    # at least three stems move across the four candidates
    moved = 0
    for stem in ("Lead", "Pad", "Bass", "Arp", "Drums"):
        vals = {s[stem][2] for s in stats}
        if len(vals) > 1:
            moved += 1
    assert moved >= 3, f"only {moved} stems varied: {stats}"


def test_slot_roles_cover_slots():
    assert SLOT_ROLES[0] == "incumbent"
    assert len(set(SLOT_ROLES)) == len(SLOT_ROLES)
