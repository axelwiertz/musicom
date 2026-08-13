"""Voice allocation + modulation matrix — ECHON 6 style.

6-voice polyphonic manager with round-robin/steal allocation, and a
9x32 modulation routing matrix (sources x destinations).

Usage:
    va = VoiceAllocator(num_voices=6)
    v = va.allocate()
    va.release(v)

    mm = ModulationMatrix(num_sources=9, num_destinations=32)
    mm.set_route(0, 5, 0.5)
    result = mm.apply(sources, destinations)
"""

from typing import Dict, List, Optional, Callable

__all__ = ["VoiceAllocator", "ModulationMatrix"]


class VoiceAllocator:
    """Polyphony voice manager (round-robin, steal oldest when full)."""

    def __init__(self, num_voices: int = 6):
        self.num_voices = num_voices
        self._active: Dict[int, int] = {}  # voice_id -> age counter
        self._next = 0
        self._age = 0
        self._synths: Dict[int, Callable] = {}

    def set_voice_synth(self, voice_id: int, synth_callable: Callable):
        """Attach a synth renderer to a voice (offline)."""
        self._synths[voice_id] = synth_callable

    def allocate(self) -> Optional[int]:
        """Allocate a free voice; steal oldest if all busy."""
        # Find free voice
        free = [v for v in range(self.num_voices) if v not in self._active]
        if free:
            voice = free[0]
        else:
            # Steal oldest (smallest age)
            voice = min(self._active, key=lambda v: self._active[v])
        self._active[voice] = self._age
        self._age += 1
        return voice

    def release(self, voice_id: int):
        """Free a voice."""
        self._active.pop(voice_id, None)

    def active_voices(self) -> List[int]:
        """Currently allocated voice ids."""
        return sorted(self._active.keys())

    def is_active(self, voice_id: int) -> bool:
        return voice_id in self._active

    def render_voice(self, voice_id: int, **kwargs):
        """Render via attached synth (returns None if none attached)."""
        synth = self._synths.get(voice_id)
        if synth is None:
            return None
        return synth(**kwargs)


class ModulationMatrix:
    """Source x destination routing table (ECHON 9x32 concept)."""

    def __init__(self, num_sources: int = 9, num_destinations: int = 32):
        self.num_sources = num_sources
        self.num_destinations = num_destinations
        self._routes: Dict[tuple, float] = {}

    def set_route(self, src: int, dest: int, amount: float):
        """Route src -> dest with amount (-1.0 to 1.0)."""
        if not (0 <= src < self.num_sources):
            raise ValueError(f"Source {src} out of range")
        if not (0 <= dest < self.num_destinations):
            raise ValueError(f"Destination {dest} out of range")
        self._routes[(src, dest)] = amount

    def get_amount(self, src: int, dest: int) -> float:
        """Current route amount (0.0 if unrouted)."""
        return self._routes.get((src, dest), 0.0)

    def routes(self) -> List[tuple]:
        """All routes as [(src, dest, amount)]."""
        return [(s, d, a) for (s, d), a in self._routes.items()]

    def apply(self, sources: Dict[int, float],
              destinations: Dict[int, float]) -> Dict[int, float]:
        """Scale destination values by routed source amounts.

        dest_value = dest_value + sum(src_value * amount) over routes.
        """
        result = dict(destinations)
        for (src, dest), amount in self._routes.items():
            src_val = sources.get(src, 0.0)
            result[dest] = result.get(dest, 0.0) + src_val * amount
        return result
