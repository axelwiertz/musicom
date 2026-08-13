"""Karst-style dice variation + parameter scoping.

Dice-based variation system: perturb parameter values with configurable
probability, support parameter locking (freeze during variation) and
scoping for auto-patching.

Usage:
    dice = DiceVariation(variation_probability=0.25, seed=42)
    params = dice.vary({"cutoff": 2000, "resonance": 0.5})
"""

import random
from typing import Dict, Any, Optional, Tuple

__all__ = ["DiceVariation", "ParamScope"]


class DiceVariation:
    """Probabilistic parameter perturbation (Karst 'dice' system)."""

    def __init__(self, variation_probability: float = 0.25,
                 seed: Optional[int] = None,
                 value_ranges: Optional[Dict[str, Tuple[float, float]]] = None):
        """
        Args:
            variation_probability: Chance (0-1) each param gets perturbed.
            seed: RNG seed for reproducibility.
            value_ranges: Optional {param: (min, max)} clamps.
        """
        self.variation_probability = max(0.0, min(1.0, variation_probability))
        self._rng = random.Random(seed)
        self._locked: set = set()
        self.value_ranges = value_ranges or {}

    def lock(self, param_name: str):
        """Freeze a parameter (never varied)."""
        self._locked.add(param_name)

    def unlock(self, param_name: str):
        """Unfreeze a parameter."""
        self._locked.discard(param_name)

    def is_locked(self, param_name: str) -> bool:
        return param_name in self._locked

    def _clamp(self, param_name: str, value: float) -> float:
        if param_name in self.value_ranges:
            lo, hi = self.value_ranges[param_name]
            return max(lo, min(hi, value))
        if isinstance(value, int):
            return max(0, min(127, int(round(value))))
        return value

    def _perturb(self, value: Any) -> Any:
        """Perturb a single value (int or float)."""
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            delta = int(self._rng.gauss(0, 1.5))
            if delta == 0:
                delta = 1 if self._rng.random() < 0.5 else -1
            return value + delta
        if isinstance(value, float):
            delta = self._rng.gauss(0, 0.1 * abs(value))
            return value + delta
        return value  # non-numeric: leave untouched

    def vary(self, param_values: Dict[str, Any]) -> Dict[str, Any]:
        """Return a copy of param_values with some params perturbed.

        Locked params are never varied. Unlock them first.
        """
        result = dict(param_values)
        for name, value in param_values.items():
            if name in self._locked:
                continue
            if self._rng.random() < self.variation_probability:
                result[name] = self._clamp(name, self._perturb(value))
        return result


class ParamScope:
    """Named parameter scopes for auto-patching (Karst 'locks & scoping')."""

    def __init__(self):
        self._scopes: Dict[str, Dict[str, Any]] = {}
        self._active = "default"
        self._scopes[self._active] = {}

    def add_scope(self, name: str, params: Dict[str, Any]):
        """Create or replace a named scope."""
        self._scopes[name] = dict(params)

    def activate(self, name: str):
        """Switch active scope."""
        if name not in self._scopes:
            self._scopes[name] = {}
        self._active = name

    def set(self, name: str, params: Dict[str, Any]):
        """Set params in a scope (create if missing)."""
        self._scopes[name] = dict(params)

    def get(self, name: str) -> Dict[str, Any]:
        """Read a scope (empty dict if missing)."""
        return dict(self._scopes.get(name, {}))

    def active(self) -> Dict[str, Any]:
        """Params of the active scope."""
        return dict(self._scopes[self._active])

    def scopes(self) -> Dict[str, Dict[str, Any]]:
        return {k: dict(v) for k, v in self._scopes.items()}
