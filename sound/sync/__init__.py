"""DAW synchronization - clock and timing bridges.

Includes MIDI Clock and MTC bridge for DAW integration.
"""

from .clock import DAWClockBridge

__all__ = ["DAWClockBridge"]
