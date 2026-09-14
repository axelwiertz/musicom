# -*- coding: utf-8 -*-
"""LEGACY — quarantined code. Do not import from new modules.

This package holds code that:

* is **not reachable** from the sanctioned composition path
  (``workflows.musicom_workflow.compose`` -> ``rules/*`` -> ``structures``), and
* is partly broken or superseded, but
* still has live consumers that would break if it were deleted.

Quarantining keeps those consumers working while making it unambiguous which
system is sanctioned. If you are writing new code, import from
``rules/patterns.py`` instead — see ``PATTERN_ARCHITECTURE.md``.

Nothing in the modern tree may import ``legacy``. The one deliberate
exception is ``structures/__init__.py``, which re-exports the old names so
existing call sites keep resolving; those re-exports are the compatibility
surface, not a recommendation.
"""

from legacy.pitchclass import (
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
