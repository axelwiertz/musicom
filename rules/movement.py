"""Deprecated shim — heptatonic degree/movement classes moved to
rules/progression.py (merged 2026-09). Kept so existing imports keep
working; new code should import from rules.progression directly.
"""
from rules.progression import (  # noqa: F401
    Scale7DegreeFunction,
    Scale7PitchDegree,
)
