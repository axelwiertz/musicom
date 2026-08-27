import sys
import numpy as np
from pathlib import Path
from scipy.io import wavfile

# Ensure repository path is loaded
sys.path.insert(0, "/opt/data/repos/musicom")

from ai.generators.vocal_synth import FormantVocalGuide

def render_country_lead_vocals():
    """
    Renders a synthetic lyric/singing guide vocal for Project 039 (Marilou in het vakantiehuis).
    Matches the MIDI note pitches and durations from the lead vocal track:
    - 32 notes total.
    - Each note has a duration of 1 beat (equal to 480 ticks or 0.625 seconds at 96 BPM).
    - Map of syllables or vowels on each line of the song to mimic phonetics.
    """
    base_dir = Path("/opt/data/projects/Styles/Country/039-marilou-vacation")
    out_path = base_dir / "marilou_vocal_lead.wav"
    
    # 96 BPM -> 1 beat = 60 / 96 = 0.625 seconds
    bpm = 96
    beat_duration = 60.0 / bpm 
    
    synth = FormantVocalGuide()
    
    # 32 lead MIDI pitches from render_verse_chorus_long.py
    lead_pitches = [
        64, 66, 67, 69,  # Verse Line 1
        69, 67, 66, 64,  # Verse Line 2
        64, 66, 69, 71,  # Verse Line 3
        71, 69, 67, 66,  # Verse Line 4
        69, 69, 71, 72,  # Chorus Line 1
        72, 71, 69, 67,  # Chorus Line 2
        71, 72, 74, 72,  # Chorus Line 3
        72, 71, 69, 67,  # Chorus Line 4
    ]
    
    # Syllabic vowel pattern loop supporting Dutch country feel:
    # "Ma-ri-lou in het va-kan-tie-huis..."
    vowel_sequence = [
        'a', 'i', 'u', 'i',  # Ma - ri - lou - in
        'e', 'a', 'a', 'i',  # het - va - kan - tie
        'u', 'i', 'e', 'a',  # huis - is - lek - ker
        'a', 'o', 'e', 'i',  # warm - en - ge - zellig
        'o', 'o', 'i', 'e',  # Oh - oh - lie - ve
        'e', 'i', 'u', 'a',  # meid - in - de - zon
        'i', 'e', 'a', 'e',  # hier - is - va - kan
        'e', 'i', 'u', 'a'   # tie - iis - be - gon
    ]
    
    # Render loop into standard audio arrays
    track_buffer = []
    
    for i, midi_pitch in enumerate(lead_pitches):
        # Convert MIDI key to frequency
        frequency = 440.0 * (2.0 ** ((midi_pitch - 69.0) / 12.0))
        # Choose vowel mapping
        vowel = vowel_sequence[i % len(vowel_sequence)]
        
        # Segment render
        carrier = synth.generate_carrier(frequency, beat_duration, volume=0.55)
        vocal_segment = synth.apply_formant_filter(carrier, vowel)
        track_buffer.append(vocal_segment)
        
    # Concatenate total track
    full_track = np.concatenate(track_buffer)
    
    # Convert and write out to static folder destination
    audio_i16 = (full_track * 32767).astype(np.int16)
    wavfile.write(out_path, synth.sample_rate, audio_i16)
    
    print(f"SUCCESS: Rendered 32-note guide vocal track to: {out_path}")

if __name__ == "__main__":
    render_country_lead_vocals()
