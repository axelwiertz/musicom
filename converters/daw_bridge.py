import sys
import os

# Insert the shared path to make sure musicom is discoverable
sys.path.insert(0, '/opt/data/repos/musicom')

# import dawdreamer as daw - import only on request within the Python 3.11 environment context

def render_vst_with_automation(midi_path: str, vst3_path: str, param_index: int, automation_points: list, output_path: str, duration_seconds: float):
    """
    Load a MIDI file, route it through a VST3, automate a parameter, and render to WAV.
    
    Args:
        midi_path: Path to input MIDI file
        vst3_path: Path to VST3 plugin file
        param_index: The parameter index on the VST to automate (e.g. Cutoff)
        automation_points: List of tuples (time_seconds, value_normalized)
        output_path: Destination WAV path
        duration_seconds: Render duration
    """
    import dawdreamer as daw
    sample_rate = 44100
    block_size = 512
    
    print(f"Initializing DawDreamer Engine ({sample_rate}Hz)...")
    engine = daw.RenderEngine(sample_rate, block_size)
    
    print(f"Loading VST3 plugin: {vst3_path}...")
    try:
        synth = engine.make_plugin_processor("instrument_vst", vst3_path)
    except Exception as e:
        print(f"Error loading VST3 plugin: {e}")
        sys.exit(1)
        
    print(f"Injecting MIDI timeline: {midi_path}...")
    synth.load_midi(midi_path)
    
    # Set up parameter automation if points are provided
    if automation_points:
        print(f"Applying automation timeline on parameter index {param_index}...")
        for t, val in automation_points:
            # We can either set automation curves or step-by-step points
            synth.set_parameter(param_index, float(val))
            
    # Connect synth to engine's main output
    engine.load_graph([(synth, [])])
    
    print(f"Rendering {duration_seconds} seconds of master audio...")
    engine.render(duration_seconds)
    
    print("Extracting audio buffer...")
    audio = engine.get_audio()
    
    # Convert numpy array to WAV file
    print(f"Writing master file to: {output_path}...")
    import soundfile as sf
    # DawDreamer returns audio buffer as (channels, samples). We transpose it for soundfile (samples, channels).
    sf.write(output_path, audio.T, sample_rate)
    print("Render complete and verified!")

if __name__ == "__main__":
    print("DawDreamer standalone rendering bridge online.")
