# -*- coding: utf-8 -*-
"""Converters for the LEGACY (System A) music pattern to MIDI note numbers.

PARTLY BROKEN, QUARANTINED, AND UNUSED
--------------------------------------
This module historically called ``pattern.modes`` and ``pattern.modes_helix``,
attributes that do not exist on ``legacy.pitchclass.MusicPitchClassSet`` — so
it raised ``AttributeError`` on every call. It has **zero callers** anywhere
in the repo (verified), which is why the breakage went unnoticed.

It is kept rather than deleted so the quarantine is reversible, but two things
are now true:

1. The non-existent attributes are gone. ``rotation_table`` reads the real
   ``PatternRotation.rotation_names`` mapping instead, so the module actually
   runs.
2. It writes through ``Config.DEFAULT_PATH`` — an Excel export path. That is
   side-effecting I/O with no validation, which is exactly why this is legacy
   and not on the sanctioned path.

New code must not use this. Use ``rules/patterns.py`` for pattern content and
``rules/realize.py`` to turn a pattern into concrete events.
"""

import pandas as pd

from utilities import Config
from legacy.pitchclass import MusicPitchClassSet, PatternRotation


def rotation_table() -> pd.DataFrame:
    """The mode/rotation name table as a DataFrame (was ``pattern.modes``).

    ``MusicPitchClassSet`` never had a ``modes`` attribute; the rotation
    names live on ``PatternRotation``. This returns the real data.
    """
    names = PatternRotation.rotation_names
    return pd.DataFrame(
        {"mode": list(names.keys()), "rotation_index": list(names.values())}
    )


def pattern_to_excel(pattern: MusicPitchClassSet,
                     path: str = None,
                     sheet_name: str = "MusicPitchClassSet"):
    """Write the rotation table to an Excel workbook.

    Kept for parity with the original module's intent. *path* defaults to the
    configured ``Config.DEFAULT_PATH``; pass an explicit path to avoid
    environment-dependent writes.
    """
    table = rotation_table()
    target = (path or Config.DEFAULT_PATH) + "interval_PatternRotations.xlsx"
    table.to_excel(target, index=True, sheet_name=sheet_name)
    return target


__all__ = ["rotation_table", "pattern_to_excel"]
