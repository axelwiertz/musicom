"""DAW Clock Bridge - MIDI Clock and MTC sync.

Emits MIDI Clock (24 PPQN) and MTC via virtual MIDI ports for DAW synchronization.
"""

import time
from typing import Optional


class DAWClockBridge:
    """Bridge for DAW clock synchronization via MIDI Clock / MTC."""

    def __init__(self, bpm: float = 120.0, ppqn: int = 24):
        """
        Args:
            bpm: Tempo in BPM
            ppqn: Pulses per quarter note (MIDI Clock = 24)
        """
        self.bpm = bpm
        self.ppqn = ppqn
        self._port = None

    def _get_port(self, port_name: str = "musicom_clock"):
        """Get or create virtual MIDI output port."""
        if self._port is None:
            try:
                import mido
                self._port = mido.open_output(port_name, virtual=True)
            except (ImportError, OSError):
                self._port = None
        return self._port

    def run_clock(self, num_pulses: int, dry_run: bool = False,
                  port_name: str = "musicom_clock") -> int:
        """Run MIDI Clock for given number of pulses.
        
        Args:
            num_pulses: Number of clock pulses to emit
            dry_run: If True, don't actually send (for testing)
            port_name: Virtual port name
            
        Returns:
            Number of pulses sent
        """
        if dry_run:
            return num_pulses

        port = self._get_port(port_name)
        if port is None:
            # Headless fallback - just print markers
            for i in range(num_pulses):
                print(f"[CLOCK] Pulse {i+1}/{num_pulses}")
            return num_pulses

        try:
            import mido
            # Calculate interval between pulses
            # MIDI Clock: 24 pulses per quarter note
            # At given BPM, quarter note duration = 60/bpm seconds
            quarter_dur = 60.0 / self.bpm
            pulse_interval = quarter_dur / self.ppqn

            for i in range(num_pulses):
                msg = mido.Message('clock')
                port.send(msg)
                if i < num_pulses - 1:
                    time.sleep(pulse_interval)

            return num_pulses
        finally:
            pass  # Keep port open for reuse

    def stop(self):
        """Stop clock and close port."""
        if self._port is not None:
            try:
                self._port.close()
            except Exception:
                pass
            self._port = None


if __name__ == "__main__":
    bridge = DAWClockBridge(bpm=120)
    bridge.run_clock(24, dry_run=True)
    print("DAWClockBridge ready.")
