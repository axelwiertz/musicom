# -*- coding: utf-8 -*-
"""Style-variation gates (PLAN_vary-instrumentation-rhythm.md P0 + P1).

P0: every rhythm family exposes all 5 roles, and "pop" is byte-identical to the
legacy ROLE_FILLERS (golden-hash guard).

P1: every instrumentation palette is 5-voice (position-based role mapping),
resolves through the instrument registry, and is role-register plausible.
"""

import os
import sys

from utilities.env import repo_root

# instrument_registry is not pip-installed — live in projects/Instruments.
_instr_dir = os.path.join(repo_root(), "projects", "Instruments")
if _instr_dir not in sys.path:
    sys.path.insert(0, _instr_dir)
from instrument_registry import by_name  # noqa: E402

from workflows.cell_engine import ROLE_FILLERS  # noqa: E402
from workflows.style_instruments import (  # noqa: E402
    INSTRUMENT_ALIASES, INSTRUMENTATION_BY_STYLE, instrument_palette,
)
from workflows.style_rhythm import RHYTHM_BY_STYLE, style_fillers  # noqa: E402

# --- P0: rhythm families ----------------------------------------------------

def test_every_rhythm_family_has_all_five_roles():
    for fam, fillers in RHYTHM_BY_STYLE.items():
        assert set(fillers) == set(ROLE_FILLERS), f"{fam}: {sorted(fillers)}"


def test_pop_rhythm_is_byte_identical_to_legacy():
    # style_fillers("pop") MUST return the exact ROLE_FILLERS objects — the
    # golden-hash gates pin the pop default, so no copy may diverge.
    pop = style_fillers("pop")
    for role in ROLE_FILLERS:
        assert pop[role] is ROLE_FILLERS[role], f"pop {role} diverged from ROLE_FILLERS"


def test_unknown_style_falls_back_to_pop():
    assert style_fillers("not_a_real_style") is style_fillers("pop")


# --- P1: instrumentation palettes ------------------------------------------

def test_every_palette_is_five_voices():
    for fam, pal in INSTRUMENTATION_BY_STYLE.items():
        assert len(pal) == 5, f"{fam}: {len(pal)} voices (need lead/pad/bass/arp/drums)"


def test_every_palette_instrument_resolves():
    for fam, pal in INSTRUMENTATION_BY_STYLE.items():
        for vname, inst in pal:
            if inst == "Drum Kit":
                continue
            by_name(inst)  # raises KeyError on typo


def test_drums_voice_is_drum_kit():
    for fam, pal in INSTRUMENTATION_BY_STYLE.items():
        assert pal[4][1] == "Drum Kit", f"{fam}: drums must be 'Drum Kit' (ch9 routing)"


def test_role_register_plausibility():
    # lead/arp must reach mid-high register; bass must reach low register;
    # pad must reach the middle. Advisory (soundable-range) gate — catches
    # e.g. didgeridoo-as-lead or piccolo-as-bass.
    for fam, pal in INSTRUMENTATION_BY_STYLE.items():
        lead = by_name(pal[0][1]); pad = by_name(pal[1][1])
        bass = by_name(pal[2][1]); arp = by_name(pal[3][1])
        assert lead.range_max >= 60, f"{fam} lead {pal[0][1]} too low"
        assert arp.range_max >= 60, f"{fam} arp {pal[3][1]} too low"
        assert bass.range_min <= 40, f"{fam} bass {pal[2][1]} too high"
        assert bass.range_max >= 48, f"{fam} bass {pal[2][1]} too low"
        assert pad.range_min <= 52, f"{fam} pad {pal[1][1]} too high"


def test_every_genre_dir_resolves():
    styles_dir = os.path.join(repo_root(), "projects", "Styles")
    non_genres = {
        "AGENTS.md", "README.md", "Production", "Research", "_cron_tmp",
        "_Comparison", "_Data_Patterns", "016-genre-pattern-dataset",
    }
    genres = [d for d in os.listdir(styles_dir)
              if os.path.isdir(os.path.join(styles_dir, d)) and d not in non_genres]
    unresolved = []
    for g in genres:
        try:
            pal = instrument_palette(g)
            assert len(pal) == 5
        except Exception as e:  # noqa: BLE001
            unresolved.append((g, repr(e)))
    assert not unresolved, f"unresolved genres: {unresolved}"
    assert len(genres) >= 40, f"expected ~50 genre dirs, found {len(genres)}"
