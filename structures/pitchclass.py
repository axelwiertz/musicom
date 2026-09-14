# -*- coding: utf-8 -*-
"""DEPRECATED location — System A pitch-class sets MOVED to ``legacy.pitchclass``.

This module exists only so that the 76 existing scripts that import

    from structures.pitchclass import MusicPitchClassSet, PatternType

keep working after the quarantine. It re-exports the real classes from
:mod:`legacy.pitchclass` — it is an alias, not a second implementation.

Do not add code here. New code should use:

    rules/set_theory.py   kernel (normal form, prime form, ICV, Forte, Z)
    rules/patterns.py     Pattern library, catalogues, rhythm patterns
    rules/realize.py      Pattern -> MusicEvent[] realization

``MusicPitchClassSet.to_pattern()`` bridges a legacy set into that layer.

See ``legacy/__init__.py`` and ``PATTERN_ARCHITECTURE.md``.
"""

import warnings as _warnings

_warnings.warn(
    "structures.pitchclass is deprecated (System A, quarantined). "
    "Use rules.patterns + rules.realize instead; direct imports still work.",
    DeprecationWarning,
    stacklevel=2,
)

from legacy.pitchclass import (  # noqa: E402  (import after the warning)
    Cardinality,
    MusicPitchClassSet,
    PatternGraph,
    PatternRotation,
    PatternType,
    create_subpattern,
)

__all__ = [
    "MusicPitchClassSet",
    "PatternType",
    "PatternRotation",
    "PatternGraph",
    "Cardinality",
    "create_subpattern",
]
