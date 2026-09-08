# -*- coding: utf-8 -*-
"""
SP-035 GENDYN Stochastic Breakpoint Synthesis
Applied to: 073-soul-rbmpd.mid (Soul / C minor / 92 BPM)

GENDYN generates audio by placing random breakpoints in time-amplitude space,
then linearly interpolating between them. Each period gets a fresh random waveform,
producing continuously evolving, non-repeating timbres.

Parameters:
- density: breakpoints per period (higher = brighter/more complex)
- amp_variance: how wild the amplitude jumps are (0-1)
- time_variance: how irregular the time spacing is (0-1)
"""
import os
import sys
import numpy as np
import wave
import mido
import json
from pathlib import Path

# === Configuration ===
INPUT_MIDI = '/opt/data/projects/Styles/Soul/073-soul-rbmpd/MIDI/073-soul-rbmpd.mid'
OUTPUT_DIR = '/opt/data/projects/Styles/Production/SP035-gendyn-soul-rbmpd'
SR = 48000  # Sample rate

# GENDYN parameters
DENSITY = 12  # breakpoints per period
AMP_VAR = 0.7  # amplitude variance (0=constant, 1=wild)
TIME_VAR = 0.6  # time spacing variance (0=uniform, 1=chaotic)
ADSR = {'attack': 0.02, 'decay': 0.1, 'sustain': 0.6, 'release': 0.3}

def midi_to_freq(note):
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

def gendyn_period(freq, duration, density=DENSITY, amp_var=AMP_VAR, time_var=TIME_VAR, sr=SR):
    """Generate one period of GENDYN waveform."""
    n_samples = int(duration * sr)
    if n_samples == 0:
        return np.array([])
    
    # Generate random breakpoints
    n_breaks = max(2, density)
    
    # Time positions (0 to 1, then scale to period)
    if time_var > 0:
        # Random spacing with variance
        times = np.random.exponential(scale=1.0, size=n_breaks)
        times = np.cumsum(times)
        times = times / times[-1]  # normalize to 0-1
    else:
        times = np.linspace(0, 1, n_breaks)
    
    # Amplitude values
    amps = np.random.uniform(-1, 1, size=n_breaks) * amp_var
    amps[0] = amps[-1] = 0  # start/end at zero for continuity
    
    # Linear interpolation
    t_norm = np.linspace(0, 1, n_samples)
    waveform = np.interp(t_norm, times, amps)
    
    return waveform

def gendyn_note(freq, duration, sr=SR):
    """Generate a GENDYN note with ADSR envelope."""
    period = 1.0 / freq
    n_samples = int(duration * sr)
    
    # Generate multiple periods, each with fresh random breakpoints
    n_periods = int(np.ceil(duration / period))
    waveform = np.zeros(n_samples)
    
    for i in range(n_periods):
        start = int(i * period * sr)
        end = min(int((i + 1) * period * sr), n_samples)
        if start >= n_samples:
            break
        
        # Fresh random waveform for this period
        period_wave = gendyn_period(freq, period, sr=sr)
        length = min(end - start, len(period_wave))
        waveform[start:start + length] = period_wave[:length]
    
    # ADSR envelope
    attack_samples = int(ADSR['attack'] * sr)
    decay_samples = int(ADSR['decay'] * sr)
    release_samples = int(ADSR['release'] * sr)
    sustain_level = ADSR['sustain']
    
    envelope = np.ones(n_samples)
    
    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay
    decay_start = attack_samples
    decay_end = min(decay_start + decay_samples, n_samples)
    if decay_samples > 0 and decay_start < n_samples:
        envelope[decay_start:decay_end] = np.linspace(1, sustain_level, decay_end - decay_start)
    
    # Sustain (already 1.0)
    sustain_start = decay_end
    sustain_end = max(0, n_samples - release_samples)
    if sustain_start < sustain_end:
        envelope[sustain_start:sustain_end] = sustain_level
    
    # Release
    if release_samples > 0 and sustain_end < n_samples:
        envelope[sustain_end:] = np.linspace(sustain_level, 0, n_samples - sustain_end)
    
    return waveform * envelope

def render_midi_to_gendyn(midi_path, output_wav):
    """Read MIDI, synthesize with GENDYN, write WAV."""
    mid = mido.MidiFile(midi_path)
    ticks_per_beat = mid.ticks_per_beat

    # Get tempo from MIDI
    tempo = 500000  # default 120 BPM
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break

    # seconds per tick: tempo (us/beat) / (ticks_per_beat * 1e6)
    seconds_per_tick = tempo / (ticks_per_beat * 1e6)

    print(f"MIDI: {midi_path}")
    print(f"Tempo: {mido.tempo2bpm(tempo):.0f} BPM")

    # Collect all note events (per track, absolute ticks)
    events = []
    max_end_tick = 0
    for track_idx, track in enumerate(mid.tracks):
        abs_tick = 0
        pending = {}  # note -> (start_tick, velocity)
        for msg in track:
            abs_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                pending[msg.note] = (abs_tick, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in pending:
                    start_tick, vel = pending.pop(msg.note)
                    max_end_tick = max(max_end_tick, abs_tick)
                    events.append({
                        'pitch': msg.note,
                        'velocity': vel,
                        'start': start_tick * seconds_per_tick,
                        'duration': max(0.05, (abs_tick - start_tick) * seconds_per_tick)
                    })
        # close dangling notes
        for note, (start_tick, vel) in pending.items():
            events.append({
                'pitch': note,
                'velocity': vel,
                'start': start_tick * seconds_per_tick,
                'duration': 0.05
            })
    total_ticks = max_end_tick
    total_duration = total_ticks * seconds_per_tick
    
    print(f"Events: {len(events)} notes")
    
    # Render to audio
    n_samples = int(total_duration * SR) + int(ADSR['release'] * SR)
    audio = np.zeros(n_samples, dtype=np.float32)
    
    for i, evt in enumerate(events):
        freq = midi_to_freq(evt['pitch'])
        amp = evt['velocity'] / 127.0
        
        note_audio = gendyn_note(freq, evt['duration'])
        note_audio *= amp * 0.3  # scale down to avoid clipping
        
        start_sample = int(evt['start'] * SR)
        end_sample = start_sample + len(note_audio)
        
        if end_sample > n_samples:
            note_audio = note_audio[:n_samples - start_sample]
            end_sample = n_samples
        
        if start_sample < n_samples:
            audio[start_sample:end_sample] += note_audio[:end_sample - start_sample]
        
        if (i + 1) % 20 == 0:
            print(f"  Rendered {i+1}/{len(events)} notes")
    
    # Normalize
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (0.89 / peak)
    
    # Convert to int16
    audio_int16 = (audio * 32767).astype(np.int16)
    
    # Write WAV
    os.makedirs(os.path.dirname(output_wav), exist_ok=True)
    with wave.open(output_wav, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(audio_int16.tobytes())
    
    print(f"WAV written: {output_wav}")
    print(f"Size: {os.path.getsize(output_wav)} bytes")
    
    return output_wav

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    output_wav = os.path.join(OUTPUT_DIR, '073-soul-rbmpd-gendyn.wav')
    output_ogg = os.path.join(OUTPUT_DIR, '073-soul-rbmpd-gendyn.ogg')
    
    # Render
    render_midi_to_gendyn(INPUT_MIDI, output_wav)
    
    # Convert to OGG
    os.system(f'ffmpeg -y -i "{output_wav}" -codec:a libopus -application audio -b:a 128k "{output_ogg}" 2>/dev/null')
    
    print(f"OGG written: {output_ogg}")
    print(f"Size: {os.path.getsize(output_ogg)} bytes")
    
    # Write provenance
    provenance = {
        'source_midi': INPUT_MIDI,
        'production_method': 'SP-035',
        'method_name': 'GENDYN Stochastic Breakpoint Synthesis',
        'parameters': {
            'density': DENSITY,
            'amp_variance': AMP_VAR,
            'time_variance': TIME_VAR,
            'adsr': ADSR
        },
        'output_wav': output_wav,
        'output_ogg': output_ogg,
        'sample_rate': SR,
        'description': 'Stochastic breakpoint synthesis: random time-amplitude breakpoints per period, linear interpolation, evolving non-repeating timbres'
    }
    
    prov_path = os.path.join(OUTPUT_DIR, 'provenance.json')
    with open(prov_path, 'w') as f:
        json.dump(provenance, f, indent=2)
    
    print(f"Provenance: {prov_path}")

if __name__ == '__main__':
    main()
