"""VST3 renderer via DawDreamer.

Loads MIDI into a VST3 plugin and renders to WAV.
Requires DawDreamer (Python 3.11 env).
"""

import os
from typing import List, Tuple, Optional


class VSTRenderer:
    """Render MIDI through VST3 plugins using DawDreamer."""

    def __init__(self, sample_rate: int = 44100, block_size: int = 512):
        """
        Args:
            sample_rate: Render sample rate
            block_size: Audio block size
        """
        self.sample_rate = sample_rate
        self.block_size = block_size

    def render(self, midi_path: str, vst3_path: str, output_path: str,
               duration_seconds: float,
               automation: Optional[List[Tuple[float, float]]] = None,
               param_index: int = 0) -> str:
        """Render MIDI through VST3 to WAV.
        
        Args:
            midi_path: Input MIDI file
            vst3_path: Path to VST3 plugin
            output_path: Output WAV path
            duration_seconds: Render duration
            automation: List of (time_seconds, value_normalized) tuples
            param_index: Parameter index to automate
            
        Returns:
            Path to output WAV
        """
        import dawdreamer as daw
        import soundfile as sf

        engine = daw.RenderEngine(self.sample_rate, self.block_size)
        synth = engine.make_plugin_processor("instrument_vst", vst3_path)
        synth.load_midi(midi_path)

        if automation:
            for t, val in automation:
                synth.set_parameter(param_index, float(val))

        engine.load_graph([(synth, [])])
        engine.render(duration_seconds)
        audio = engine.get_audio()

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        sf.write(output_path, audio.T, self.sample_rate)
        return output_path


if __name__ == "__main__":
    print("VSTRenderer ready. Requires dawdreamer (Python 3.11 env).")
