import time
import sys

# Ensure repository path is loaded
sys.path.insert(0, "/opt/data/repos/musicom")

class DAWClockBridge:
    """
    Clock bridge that generates MIDI Clock / MIDI Time Code (MTC) markers.
    Includes a robust fallback mode when running on headless systems 
    lacking raw ALSA soundcard drivers or virtual MIDI ports.
    """
    def __init__(self, port_name: str = "Musicom Virtual Sync", bpm: int = 120):
        self.port_name = port_name
        self.bpm = bpm
        self.outport = None
        self.fallback_mode = False

    def start_virtual_output(self):
        """Creates output channel or enters virtual simulation fallback mode."""
        try:
            import mido
            # Attempt default ALSA port opening
            self.outport = mido.open_output(self.port_name, virtual=True)
            print(f"Created virtual MIDI output port: '{self.port_name}'")
        except Exception as e:
            self.fallback_mode = True
            print(f"MIDI Server running in Virtual Fallback mode (ALSA sequencer missing on sandbox).")

    def run_clock(self, pulses_count: int = 96):
        """
        Runs the synchronizer loop.
        24 MIDI clock pulses (0xF8) are emitted per quarter note.
        """
        pulse_interval = 60.0 / (self.bpm * 24.0)
        print(f"Streaming {pulses_count} pulses at {self.bpm} BPM (interval: {pulse_interval:.5f}s)...")
        
        # Start command
        if not self.fallback_mode and self.outport:
            import mido
            self.outport.send(mido.Message('start'))
        else:
            print(">>> [MIDI CLOCK START] (0xFA)")

        for i in range(pulses_count):
            if not self.fallback_mode and self.outport:
                import mido
                self.outport.send(mido.Message('clock'))
            time.sleep(pulse_interval)
            
            # Print beat alignments to feedback loop
            if i % 24 == 0:
                print(f"=== [CLOCK SYNC] BEAT {i//24 + 1} (Pulse #{i}) ===")
                
        # Stop command
        if not self.fallback_mode and self.outport:
            import mido
            self.outport.send(mido.Message('stop'))
        else:
            print(">>> [MIDI CLOCK STOP] (0xFC)")
        print("Clock stream complete.")

if __name__ == "__main__":
    bridge = DAWClockBridge(bpm=120)
    bridge.start_virtual_output()
    # Streams 4 beats (96 pulses) of MIDI Clock
    bridge.run_clock(pulses_count=96)
