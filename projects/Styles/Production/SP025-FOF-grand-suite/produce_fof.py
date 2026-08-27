# -*- coding: utf-8 -*-
"""
Sound Production Method SP-025: Formant-Wave-Function (FOF) Synthesis
Applied to: grand_suite_v1_3.mid (Balfolk Grand Suite)

FOF synthesis (IRCAM) triggers decaying cosine wave-packets at the fundamental
frequency of each MIDI note. Multiple formant channels sum to create vocal/
resonant timbres. Each track gets a distinct formant preset for timbral variety.
"""

import numpy as np
import mido
import wave
import os
import json
from pathlib import Path

# === Configuration ===
SR = 44100
MIDI_PATH = '/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI/grand_suite_v1_3.mid'
OUTPUT_DIR = '/opt/data/projects/Styles/Production/SP025-FOF-grand-suite'
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'stems'), exist_ok=True)

# === FOF Synthesis Engine (from methods_db.md SP-025) ===

def fof_packet(fc, bw, amp, sr, duration, t_att=0.0015):
    """Generate a single FOF wave packet prototype."""
    alpha = np.pi * bw
    beta = np.pi / t_att
    n = int(duration * sr)
    tau = np.arange(n) / sr
    
    packet = np.zeros(n)
    rise_mask = tau <= t_att
    decay_mask = ~rise_mask
    
    # Rise phase
    packet[rise_mask] = (
        amp * np.exp(-alpha * tau[rise_mask]) *
        (1.0 - np.cos(beta * tau[rise_mask])) / 2.0 *
        np.sin(2.0 * np.pi * fc * tau[rise_mask])
    )
    
    # Decay phase
    packet[decay_mask] = (
        amp * np.exp(-alpha * tau[decay_mask]) *
        np.sin(2.0 * np.pi * fc * tau[decay_mask])
    )
    
    return packet


def midi_to_freq(midi_note):
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def synthesize_fof_note(f0, formant_freqs, formant_bandwidths, formant_amps, 
                         sr, duration, jitter=0.0):
    """Synthesize a single note using multi-formant FOF synthesis."""
    n_samples = int(sr * duration)
    output = np.zeros(n_samples)
    
    if f0 < 20:
        f0 = 20.0
    
    t_period = sr / f0
    
    # Generate trigger points
    trigger_samples = []
    current = 0.0
    while current < n_samples:
        trigger_samples.append(int(round(current)))
        period_mod = t_period
        if jitter > 0:
            period_mod += np.random.normal(0, jitter * sr)
        current += max(10, period_mod)
    
    # Sum formant channels
    for fc, bw, amp in zip(formant_freqs, formant_bandwidths, formant_amps):
        alpha = np.pi * bw
        t_dur = 6.907 / alpha
        dur_samples = max(int(t_dur * sr), 100)
        
        packet = fof_packet(fc, bw, amp, sr, t_dur)
        pkt_len = len(packet)  # use actual packet length for slicing
        
        for trigger in trigger_samples:
            end = trigger + pkt_len
            if end <= n_samples:
                output[trigger:end] += packet
            else:
                rem = n_samples - trigger
                if rem > 0:
                    output[trigger:] += packet[:rem]
    
    return output


def apply_adsr(signal, sr, attack=0.01, decay=0.05, sustain_level=0.7, release=0.05):
    """Apply ADSR envelope to prevent clicks."""
    n = len(signal)
    env = np.ones(n)
    
    att_samples = min(int(attack * sr), n)
    dec_samples = min(int(decay * sr), n - att_samples)
    rel_samples = min(int(release * sr), n)
    
    # Attack
    if att_samples > 0:
        env[:att_samples] = np.linspace(0, 1, att_samples)
    
    # Decay
    if dec_samples > 0:
        start = att_samples
        env[start:start+dec_samples] = np.linspace(1, sustain_level, dec_samples)
    
    # Sustain (already 1.0 or sustain_level)
    sus_end = n - rel_samples
    if sus_end > att_samples + dec_samples:
        env[att_samples+dec_samples:sus_end] = sustain_level
    
    # Release
    if rel_samples > 0:
        env[-rel_samples:] *= np.linspace(1, 0, rel_samples)
    
    return signal * env


# === Formant Presets (vocal-like timbres for different tracks) ===

# Soprano "Ah" vowel - bright, open
FORMANT_SOPRANO_AH = {
    'freqs': [800, 1200, 2500, 3500],
    'bandwidths': [80, 90, 120, 130],
    'amps': [1.0, 0.6, 0.3, 0.15]
}

# Alto "Oh" vowel - warm, rounded
FORMANT_ALTO_OH = {
    'freqs': [500, 1000, 2400, 3300],
    'bandwidths': [60, 70, 110, 120],
    'amps': [1.0, 0.5, 0.25, 0.1]
}

# Tenor "Ee" vowel - bright, forward
FORMANT_TENOR_EE = {
    'freqs': [400, 2200, 2800, 3600],
    'bandwidths': [60, 100, 130, 140],
    'amps': [1.0, 0.7, 0.35, 0.15]
}

# Bass "Oo" vowel - dark, resonant
FORMANT_BASS_OO = {
    'freqs': [350, 700, 2400, 3200],
    'bandwidths': [40, 60, 100, 120],
    'amps': [1.0, 0.4, 0.2, 0.08]
}

# Percussive "click" - wide bandwidths, noise-like
FORMANT_PERC = {
    'freqs': [1000, 3000, 6000],
    'bandwidths': [500, 800, 1200],
    'amps': [1.0, 0.6, 0.3]
}

# Track name -> formant preset mapping
TRACK_PRESETS = {
    'Violin': FORMANT_SOPRANO_AH,
    'Piano': FORMANT_ALTO_OH,
    'Acoustic Guitar': FORMANT_TENOR_EE,
    'Woodblock': FORMANT_PERC,
}

# Default for unnamed tracks
DEFAULT_PRESET = FORMANT_BASS_OO


# === Parse MIDI ===

def parse_midi_events(midi_path):
    """Parse MIDI file into absolute-tick note events per track."""
    mid = mido.MidiFile(midi_path)
    ticks_per_beat = mid.ticks_per_beat
    
    # Get tempo from track 0
    tempo = 500000  # default 120 BPM
    for msg in mid.tracks[0]:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            break
    
    bpm = mido.tempo2bpm(tempo)
    seconds_per_tick = tempo / (ticks_per_beat * 1_000_000)
    
    tracks_data = []
    
    for track_idx, track in enumerate(mid.tracks):
        if track_idx == 0:
            continue  # skip tempo track
        
        track_name = track.name or f'Track_{track_idx}'
        events = []
        abs_tick = 0
        active_notes = {}  # note -> start_tick
        
        for msg in track:
            abs_tick += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = abs_tick
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start = active_notes.pop(msg.note)
                    dur_ticks = abs_tick - start
                    dur_sec = dur_ticks * seconds_per_tick
                    start_sec = start * seconds_per_tick
                    events.append({
                        'note': msg.note,
                        'velocity': msg.velocity if msg.type == 'note_off' else 90,
                        'start_sec': start_sec,
                        'duration_sec': max(dur_sec, 0.05),
                    })
        
        if events:
            tracks_data.append({
                'name': track_name,
                'events': events,
            })
    
    return tracks_data, bpm, seconds_per_tick


# === Main Production Pipeline ===

print("=" * 60)
print("SP-025: Formant-Wave-Function (FOF) Synthesis")
print("=" * 60)

# Parse MIDI
print(f"\nParsing MIDI: {MIDI_PATH}")
tracks_data, bpm, sec_per_tick = parse_midi_events(MIDI_PATH)
print(f"BPM: {bpm:.1f}")
print(f"Tracks found: {len(tracks_data)}")
for td in tracks_data:
    print(f"  {td['name']}: {len(td['events'])} notes")

# Calculate total duration
max_end = 0
for td in tracks_data:
    for evt in td['events']:
        end = evt['start_sec'] + evt['duration_sec']
        if end > max_end:
            max_end = end

total_duration = max_end + 0.5  # 500ms tail
total_samples = int(total_duration * SR)
print(f"\nTotal duration: {total_duration:.2f}s ({total_samples} samples)")

# Master mix buffer
master_mix = np.zeros(total_samples)
stem_buffers = {}

# Synthesize each track with its formant preset
for td in tracks_data:
    track_name = td['name']
    preset = TRACK_PRESETS.get(track_name, DEFAULT_PRESET)
    
    print(f"\nRendering track: {track_name} (FOF preset: {preset['freqs'][:2]}...)")
    
    track_buffer = np.zeros(total_samples)
    
    for evt in td['events']:
        f0 = midi_to_freq(evt['note'])
        vel_scale = evt['velocity'] / 127.0
        dur = evt['duration_sec']
        start_sample = int(evt['start_sec'] * SR)
        
        # Synthesize FOF note
        note_audio = synthesize_fof_note(
            f0=f0,
            formant_freqs=preset['freqs'],
            formant_bandwidths=preset['bandwidths'],
            formant_amps=preset['amps'],
            sr=SR,
            duration=dur,
            jitter=0.002  # subtle humanization
        )
        
        # Apply ADSR envelope
        note_audio = apply_adsr(note_audio, SR, attack=0.008, decay=0.03, 
                                sustain_level=0.6, release=0.04)
        
        # Scale by velocity
        note_audio *= vel_scale * 0.3  # master gain per voice
        
        # Mix into track buffer
        end_sample = start_sample + len(note_audio)
        if end_sample > total_samples:
            note_audio = note_audio[:total_samples - start_sample]
            end_sample = total_samples
        
        if start_sample < total_samples:
            track_buffer[start_sample:end_sample] += note_audio
    
    # Normalize track stem
    peak = np.max(np.abs(track_buffer))
    if peak > 0:
        track_buffer = track_buffer / peak * 0.7
    
    stem_buffers[track_name] = track_buffer
    
    # Save individual stem WAV
    stem_path = os.path.join(OUTPUT_DIR, 'stems', f'{track_name}_fof.wav')
    with wave.open(stem_path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        audio_int16 = (np.clip(track_buffer, -1.0, 1.0) * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())
    print(f"  Stem saved: {stem_path}")
    
    # Add to master mix
    master_mix += track_buffer

# Normalize master mix
peak = np.max(np.abs(master_mix))
if peak > 0:
    master_mix = master_mix / peak * 0.89  # -1dB normalization

# Save master WAV
wav_path = os.path.join(OUTPUT_DIR, 'grand_suite_fof_synthesis.wav')
with wave.open(wav_path, 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    audio_int16 = (np.clip(master_mix, -1.0, 1.0) * 32767).astype(np.int16)
    wf.writeframes(audio_int16.tobytes())
print(f"\nMaster WAV saved: {wav_path}")
print(f"File size: {os.path.getsize(wav_path)} bytes")

# Verify non-empty
assert os.path.getsize(wav_path) > 1000, "WAV file too small!"

print("\nDone! FOF synthesis complete.")
