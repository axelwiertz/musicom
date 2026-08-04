"""FluidSynth renderer - MIDI to WAV via SoundFont.

Wraps the fluidsynth CLI to render MIDI files to audio.
"""

import subprocess
import os
from typing import Optional


class FluidSynthRenderer:
    """Render MIDI files to WAV using FluidSynth + SoundFont."""

    def __init__(self, 
                 fluidsynth_bin: str = "fluidsynth",
                 soundfont_path: Optional[str] = None,
                 sample_rate: int = 44100,
                 gain: float = 1.2):
        """
        Args:
            fluidsynth_bin: Path to fluidsynth binary
            soundfont_path: Path to .sf2 SoundFont file
            sample_rate: Output sample rate
            gain: Gain multiplier (1.2 prevents tail truncation)
        """
        self.fluidsynth_bin = fluidsynth_bin
        self.soundfont_path = soundfont_path
        self.sample_rate = sample_rate
        self.gain = gain

    def render(self, midi_path: str, output_path: str, 
               soundfont: Optional[str] = None) -> str:
        """Render MIDI to WAV.
        
        Args:
            midi_path: Input MIDI file
            output_path: Output WAV path
            soundfont: Override SoundFont path (uses default if None)
            
        Returns:
            Path to output WAV
        """
        sf = soundfont or self.soundfont_path
        if not sf:
            raise ValueError("No SoundFont specified. Pass soundfont= or set default.")
        
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        cmd = [
            self.fluidsynth_bin,
            "-ni",
            "-g", str(self.gain),
            "-F", output_path,
            "-r", str(self.sample_rate),
            sf,
            midi_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path


if __name__ == "__main__":
    print("FluidSynthRenderer ready. Call render(midi_path, output_path, soundfont=...).")
