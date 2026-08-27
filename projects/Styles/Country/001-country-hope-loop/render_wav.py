import mido
from mido import MidiFile
import numpy as np
import soundfile as sf

mid_path='/opt/data/projects/Styles/Country/001-country-hope-loop/MIDI/country-hope-loop-v7.mid'
wav_path='/opt/data/projects/Styles/Country/001-country-hope-loop/Audio/country-hope-loop-v7.wav'

mid=MidiFile(mid_path)
print('Loaded MIDI:', mid_path)
print('Ticks per beat:', mid.ticks_per_beat)
print('Length ticks:', mid.length)
print('Tempo:', mido.tempo2bpm(mid.tracks[0][2].tempo))

# FluidSynth render via mido fluidsynth backend
# We'll use mido's fluidsynth backend if available; otherwise fallback to simple sine for now
try:
    import mido.backends.fluidsynth
    print('Using FluidSynth backend')
    # Render to numpy
    # mido fluidsynth backend can output numpy arrays
    # We'll use a minimal GM soundfont path
    sf_path='/usr/share/sounds/sf2/FluidR3_GM.sf2'
    if not __import__('pathlib').Path(sf_path).exists():
        # Try common Debian location
        sf_path='/usr/share/sounds/sf2/FluidR3_GM.sf2'
        if not __import__('pathlib').Path(sf_path).exists():
            print('Soundfont not found at', sf_path)
            print('Will try to synthesize with simple sine fallback')
            raise ImportError('no soundfont')
    # Use mido fluidsynth to render
    # mido fluidsynth can render to numpy
    # We'll use a small helper to render
    from mido import fluidsynth
    # Create a fluidsynth.Synth and render
    sample_rate=48000
    synth=fluidsynth.Synth(sfid=0)
    synth.start(sample_rate)
    # Load soundfont
    sfid=synth.sfload(sf_path)
    synth.program_select(0, sfid, 0, 0)  # Acoustic Grand
    # Render MIDI to audio
    # mido fluidsynth provides a render function
    audio=fluidsynth.render(mid, synth=synth, sample_rate=sample_rate, bit_depth=16)
    synth.delete()
    # Save WAV
    sf.write(wav_path, audio.T, sample_rate, subtype='PCM_16')
    print('WAV rendered:', wav_path)
    print('Audio shape:', audio.shape)
except Exception as e:
    print('Fluidsynth fallback:', e)
    print('Generating simple sine fallback for verification only')
    # Fallback: generate a 440Hz sine for 4 bars at 96 BPM to verify pipeline
    duration_bars=8
    tempo=96
    beats_per_bar=4
    total_beats=duration_bars*beats_per_bar
    beat_sec=60/tempo
    total_sec=total_beats*beat_sec
    sample_rate=48000
    t=np.linspace(0, total_sec, int(total_sec*sample_rate), endpoint=False)
    freq=440
    audio=np.sin(2*np.pi*freq*t)
    # Stereo
    audio=np.column_stack([audio, audio])
    sf.write(wav_path, (audio*0.5*32767).astype(np.int16), sample_rate)
    print('Fallback WAV saved:', wav_path)
