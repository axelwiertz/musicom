"""FluidSynth renderer - MIDI to WAV via SoundFont.

Wraps the fluidsynth CLI to render MIDI files to audio.
"""

import glob
import subprocess
import os
from typing import Optional

# SoundFont discovery — prefer the best available, fall back to TimGM6mb.
# FluidR3_GM.sf2 (141MB) has proper woodwind/brass/strings patches; the
# bundled TimGM6mb (~6MB) is a minimal GM set whose oboe/bassoon/flute
# patches are thin and buzzy. If a larger GM set is present, use it.
_SOUNDFONT_CANDIDATES = [
    "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2",
    "/opt/data/soundfonts/FluidR3_GM.sf2",
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    "/usr/share/sounds/sf3/FluidR3_GM.sf3",
]


def discover_soundfont(prefer: Optional[str] = None) -> Optional[str]:
    """Return the best available SoundFont path, or None if none found.

    Order: explicit `prefer` arg → FluidR3 candidates → any TimGM6mb on disk.
    """
    if prefer and os.path.exists(prefer):
        return prefer
    for p in _SOUNDFONT_CANDIDATES:
        if os.path.exists(p):
            return p
    # fall back to the bundled minimal GM set (pretty_midi ships TimGM6mb)
    for pat in (
        "/opt/data/micromamba/envs/musicom/**/TimGM6mb.sf2",
        "/opt/data/.local/**/TimGM6mb.sf2",
        "/usr/share/sounds/sf2/TimGM6mb.sf2",
        "/usr/share/sounds/sf3/TimGM6mb.sf3",
    ):
        hits = glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    return None


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
