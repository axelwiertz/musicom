# Algorithmic Indian Classical Composer: Raga Bhairavi & Teental
# Tonal Center D (Sa = D4, 62)

import os
import random
import mido
from mido import Message, MidiFile, MidiTrack

# --- INDIAN CLASSICAL THEORY ---
# Raga Bhairavi Scale Degrees:
# Swaras: Sa, Komal Re, Komal Ga, Shuddha Ma, Pa, Komal Dha, Komal Ni
# MIDI mapping centered on D4 (62):
BHAIRAVI_SWARAS = {
    'Sa': 62,     # D4
    'Re': 63,     # Eb4 (Komal)
    'Ga': 65,     # F4  (Komal)
    'Ma': 67,     # G4  (Shuddha)
    'Pa': 69,     # A4
    'Dha': 70,    # Bb4 (Komal)
    'Ni': 72,     # C5  (Komal)
    'Sa_high': 74 # D5 (Tar Sa)
}

SWARA_LIST = [62, 63, 65, 67, 69, 70, 72, 74]

# Drone (Tanpura) plays Sa and Pa:
DRONE_PITCHES = [38, 45, 50, 62] # D2, A2, D3, D4 sounding constantly

# Instruments GM:
# Channel 0: Sitar (Melody) -> GM program 104 (Sitar)
# Channel 1: Tanpura (Drone) -> GM program 104 or 107 (Koto or Sitar low)
# Channel 9: Tabla (GM percussion on channel 10 / MIDI channel 9)
SITAR_PROG = 104
TANPURA_PROG = 104

# Tabla GM mapping: we use standard kit percussion or high-contrast Indian textures:
# Tabla sound in GM is rare, so we map onto standard drum parts that mimic Tabla:
# Baya (deep bass drum sound) -> bass drum (35/36)
# Dhin (damped resonant slap) -> snare/conga (38/48)
# Tin (ringing high stroke) -> rimshot/bongo/triangle (37/60)
# Ta (sharp accent) -> side stick / tabor (31/33/42)

TABLA_MAPPING = {
    'Dha': 36, # Bass Drum
    'Dhin': 48, # High Conga / Mid Tom
    'Tin': 60, # Ringing high
    'Ta': 37,  # Rimshot/Side stick
}

# 16-beat Teental structure:
# Clap (1) | Clap (5) | Wave (9) | Clap (13)
TEENTAL_BOLS = [
    'Dha', 'Dhin', 'Dhin', 'Dha', # Vibhav 1 (Sam/Clap)
    'Dha', 'Dhin', 'Dhin', 'Dha', # Vibhav 2 (Clap)
    'Dha', 'Tin',  'Tin',  'Ta',  # Vibhav 3 (Khali/Wave)
    'Ta',  'Dhin', 'Dhin', 'Dha'  # Vibhav 4 (Clap)
]

def generate_ragas_phrase(prev_pitch=62):
    """
    Raga Bhairavi phrasing rules:
    Melody must glide, leap, or settle on Sa, Ma, Pa.
    Descent (Avrohana): Sa_high -> Ni -> Dha -> Pa -> Ma -> Ga -> Re -> Sa
    Returns lists of MIDI pitch-timings.
    """
    ticks_per_beat = 480
    cycle_beats = 16
    melody_events = []
    
    curr = prev_pitch if prev_pitch in SWARA_LIST else 62
    
    # We generate a sitar line with humanized ornamentation (meend/glides/fast triplets)
    # Average 1 to 2 notes per beat
    beat = 0
    while beat < cycle_beats:
        start_tick = beat * ticks_per_beat
        
        # Decide if playing a long note (alap style), standard gate, or double-speed taan
        div = random.choice([1, 2, 3]) # beats to hold or subbeats
        
        if div == 1: # 1 note per beat
            # Markov step constrained to Bhairavi
            idx = SWARA_LIST.index(curr)
            # Favour movements to Sa (0), Ma (3), Pa (4), or Sa_high (7)
            weights = []
            for i, p in enumerate(SWARA_LIST):
                dist = abs(i - idx)
                w = 1.0 / (dist + 0.1) # proximity
                if p in [62, 67, 69, 74]: # Raga gravity to Sa/Ma/Pa
                    w *= 1.8
                weights.append(w)
            
            curr = random.choices(SWARA_LIST, weights=weights)[0]
            melody_events.append({
                'pitch': curr,
                'tick': start_tick,
                'dur': int(ticks_per_beat * 0.85),
                'vel': random.randint(85, 105)
            })
            beat += 1
            
        elif div == 2: # Double speed notes (2 per beat)
            # Rapid steps
            sub_dur = ticks_per_beat // 2
            idx = SWARA_LIST.index(curr)
            
            # Stepwise movement for fast runs (Taan)
            step1 = random.choice([-1, 1, 0])
            idx1 = max(0, min(len(SWARA_LIST) - 1, idx + step1))
            p1 = SWARA_LIST[idx1]
            
            step2 = random.choice([-1, 1, 0])
            idx2 = max(0, min(len(SWARA_LIST) - 1, idx1 + step2))
            p2 = SWARA_LIST[idx2]
            
            melody_events.append({'pitch': p1, 'tick': start_tick, 'dur': int(sub_dur * 0.9), 'vel': random.randint(80, 100)})
            melody_events.append({'pitch': p2, 'tick': start_tick + sub_dur, 'dur': int(sub_dur * 0.9), 'vel': random.randint(90, 110)})
            curr = p2
            beat += 1
            
        else: # Syncopated triplet or ornament (takes 1 beat total)
            sub_dur = ticks_per_beat // 3
            # Grace ornament
            p1 = curr
            p2 = max(62, min(74, curr + 1)) # adjacent microtonal glide step
            p3 = curr
            melody_events.append({'pitch': p1, 'tick': start_tick, 'dur': int(sub_dur * 0.8), 'vel': 70})
            melody_events.append({'pitch': p2, 'tick': start_tick + sub_dur, 'dur': int(sub_dur * 0.8), 'vel': 80})
            melody_events.append({'pitch': p3, 'tick': start_tick + 2*sub_dur, 'dur': int(sub_dur * 0.8), 'vel': 95})
            beat += 1
            
    return melody_events, curr

def build_hindustani_midi(num_cycles=8, path="/opt/data/projects/Genres/IndianClassical/018-hindustani-bhairavi/MIDI/bhairavi_live_render.mid"):
    mid = MidiFile()
    
    # Meta track
    meta_track = MidiTrack()
    mid.tracks.append(meta_track)
    meta_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(95))) # 95 BPM middle tempo (Madhyalaya)
    
    # Track assignments
    sitar_track = MidiTrack()
    tanpura_track = MidiTrack()
    tabla_track = MidiTrack()
    
    mid.tracks.extend([sitar_track, tanpura_track, tabla_track])
    
    # Setup channel instruments
    sitar_track.append(Message('program_change', program=SITAR_PROG, channel=0, time=0))
    tanpura_track.append(Message('program_change', program=TANPURA_PROG, channel=1, time=0))
    # Channel 10 mapping for GM drums (MIDI channel 9)
    
    ticks_per_cycle = 16 * 480
    
    # 1. CONSTANT DRONE (TANPURA) - holds drone notes across whole cycles
    for cycle in range(num_cycles):
        cycle_start = cycle * ticks_per_cycle
        # Pluck Tanpura notes Sa and Pa at slightly staggered offsets to mimic real playing
        staggers = [0, 120, 240, 360]
        for idx, pitch in enumerate(DRONE_PITCHES):
            abs_on = cycle_start + staggers[idx]
            abs_off = (cycle + 1) * ticks_per_cycle - 50
            
            # Write to tanpura track
            # Delta to previous event
            if cycle == 0 and idx == 0:
                tanpura_track.append(Message('note_on', note=pitch, velocity=60, channel=1, time=abs_on))
            else:
                pass # Need precise calculations below
                
    # Re-write with clean sequential delta-timing
    # We will build absolute timeline array first, then output ordered delta-events for each track.
    
    # Timeline generation
    sitar_timeline = []
    tanpura_timeline = []
    tabla_timeline = []
    
    # Generate melody and drone notes
    last_note = 62
    all_sitar_paths = []
    for cycle in range(num_cycles):
        cycle_start = cycle * ticks_per_cycle
        
        # Sitar Melody
        phrase_events, last_note = generate_ragas_phrase(last_note)
        all_sitar_paths.append([ev['pitch'] for ev in phrase_events if 'pitch' in ev])
        for ev in phrase_events:
            abs_on = cycle_start + ev['tick']
            abs_off = abs_on + ev['dur']
            sitar_timeline.append(('on', abs_on, ev['pitch'], ev['vel']))
            sitar_timeline.append(('off', abs_off, ev['pitch'], 0))
            
        # Tanpura Drone (Gentle continuous sweeps)
        for sub_cycle in range(4): # 4 drone cycles per Teental cycle
            sub_start = cycle_start + sub_cycle * 4 * 480
            for k, pr in enumerate(DRONE_PITCHES):
                abs_on = sub_start + k * 160
                abs_off = min((cycle + 1) * ticks_per_cycle, abs_on + 1400)
                tanpura_timeline.append(('on', abs_on, pr, 50))
                tanpura_timeline.append(('off', abs_off, pr, 0))
                
        # Tabla (Rhythm grid)
        for beat in range(16):
            abs_beat_tick = cycle_start + beat * 480
            bol = TEENTAL_BOLS[beat]
            mapped_pitch = TABLA_MAPPING[bol]
            
            # Base stroke on downbeat
            tabla_timeline.append(('on', abs_beat_tick, mapped_pitch, random.randint(90, 110)))
            tabla_timeline.append(('off', abs_beat_tick + 150, mapped_pitch, 0))
            
            # Double speed filler strokes for grooves (Dhe, Ke, Ge) on offbeats
            if beat % 2 == 0:
                tabla_timeline.append(('on', abs_beat_tick + 240, 42, 60)) # Closed hat / tabor click
                tabla_timeline.append(('off', abs_beat_tick + 350, 42, 0))

    # Convert timeline list to ordered delta MIDI tracks
    def write_timeline_to_track(track, timeline, channel):
        # Sort by tick, then action ('off' before 'on' at same tick to prevent cutoffs)
        timeline.sort(key=lambda x: (x[1], 0 if x[0] == 'off' else 1))
        curr_time = 0
        for action, tick, pitch, vel in timeline:
            delta = tick - curr_time
            if delta < 0:
                # clip overlap to zero
                delta = 0
            if action == 'on':
                track.append(Message('note_on', note=pitch, velocity=vel, channel=channel, time=delta))
            else:
                track.append(Message('note_off', note=pitch, velocity=0, channel=channel, time=delta))
            curr_time = tick

    write_timeline_to_track(sitar_track, sitar_timeline, channel=0)
    write_timeline_to_track(tanpura_track, tanpura_timeline, channel=1)
    write_timeline_to_track(tabla_track, tabla_timeline, channel=9) # Drum channel 10

    # Ensure clean directory and write
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mid.save(path)
    return all_sitar_paths

if __name__ == "__main__":
    print("Generating infinite Hinustani classical stream (Raga Bhairavi x Teental)...")
    sitar_runs = build_hindustani_midi(num_cycles=6)
    print("Successfully built Bhairavi MIDI.")
