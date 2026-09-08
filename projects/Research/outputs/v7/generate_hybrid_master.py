import mido
import os

# Create directories
os.makedirs("/opt/data/projects/Research/outputs/v7", exist_ok=True)

mid = mido.MidiFile(ticks_per_beat=960)

# Track 0: Tempo and Time Signature
track_meta = mido.MidiTrack()
mid.tracks.append(track_meta)
track_meta.append(mido.MetaMessage('track_name', name='Meta Track', time=0))
# Time Signature 4/4
track_meta.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))

# Convert BPM to MIDI tempo (microseconds per beat)
# 92 BPM = 652173 microseconds per beat
tempo_92 = mido.bpm2tempo(92)
# 140 BPM = 428571 microseconds per beat
tempo_140 = mido.bpm2tempo(140)

# Add 92 BPM at start (tick 0)
track_meta.append(mido.MetaMessage('set_tempo', tempo=tempo_92, time=0))

# 8 bars at 92 BPM = 32 beats * 960 ticks = 30720 ticks
# At tick 30720, change tempo to 140 BPM
track_meta.append(mido.MetaMessage('set_tempo', tempo=tempo_140, time=30720))

# End of track anchor (tick 69120)
# 8 bars (ballad) + 2 bars (build) + 8 bars (drop) = 18 bars total = 72 beats = 69120 ticks
track_meta.append(mido.MetaMessage('end_of_track', time=38400)) # delta time from last event (30720 + 38400 = 69120)


def create_track(name, program, channel=0):
    t = mido.MidiTrack()
    t.append(mido.MetaMessage('track_name', name=name, time=0))
    t.append(mido.Message('program_change', program=program, channel=channel, time=0))
    return t

# Create active tracks
track_lead = create_track('Lead', 73, channel=0)      # Flute (ballad) -> Banjo (drop)
track_chords = create_track('Chords', 21, channel=1)  # Accordion (ballad) -> Synth Pad (drop)
track_bass = create_track('Bass', 32, channel=2)      # Acoustic Bass -> Synth Bass
track_perc = create_track('Percussion', 0, channel=9) # General MIDI Drums (channel 10)

mid.tracks.extend([track_lead, track_chords, track_bass, track_perc])

# We write absolute tick events first, then convert them to delta times
events_lead = []
events_chords = []
events_bass = []
events_perc = []

TPB = 960  # Ticks Per Beat
BAR = 4 * TPB

# --- BALLAD SECTION (Bars 1-8, Ticks 0 to 30720) ---
# Chords and Bass notes
ballad_chords = [
    [55, 59, 62, 67], # G Major (Bar 1)
    [52, 55, 59, 64], # E Minor (Bar 2)
    [55, 59, 62, 67], # G Major (Bar 3)
    [52, 55, 59, 64], # E Minor (Bar 4)
    [57, 60, 64, 69], # A Minor (Bar 5)
    [50, 54, 57, 62], # D Major (Bar 6)
    [50, 54, 60, 62], # D7 (Bar 7)
    [55, 59, 62, 67]  # G Major (Bar 8)
]

ballad_bass = [
    55, 52, 55, 52, 57, 50, 50, 55
]

# Melody notes
ballad_melody = [
    # Bar 1: B4 (half), A4 (quarter), G4 (quarter)
    (0, 71, 2*TPB), (2*TPB, 69, TPB), (3*TPB, 67, TPB),
    # Bar 2: G4 (half), E4 (half)
    (4*TPB, 67, 2*TPB), (6*TPB, 64, 2*TPB),
    # Bar 3: B4 (half), A4 (quarter), G4 (quarter)
    (8*TPB, 71, 2*TPB), (10*TPB, 69, TPB), (11*TPB, 67, TPB),
    # Bar 4: G4 (half), E4 (half)
    (12*TPB, 67, 2*TPB), (14*TPB, 64, 2*TPB),
    # Bar 5: C5 (half), B4 (quarter), A4 (quarter)
    (16*TPB, 72, 2*TPB), (18*TPB, 71, TPB), (19*TPB, 69, TPB),
    # Bar 6: A4 (half), F#4 (half)
    (20*TPB, 69, 2*TPB), (22*TPB, 66, 2*TPB),
    # Bar 7: A4 (half), B4 (quarter), C5 (quarter)
    (24*TPB, 69, 2*TPB), (26*TPB, 71, TPB), (27*TPB, 72, TPB),
    # Bar 8: B4 (whole)
    (28*TPB, 71, 4*TPB)
]

# Add ballad melody events
for start, pitch, dur in ballad_melody:
    events_lead.append((start, 'note_on', pitch, 95))
    events_lead.append((start + dur, 'note_off', pitch, 0))

# Add ballad chord/bass and percussion events
for bar_idx in range(8):
    start_tick = bar_idx * BAR
    # Bass on Beats 1 and 3
    events_bass.append((start_tick, 'note_on', ballad_bass[bar_idx] - 12, 90))
    events_bass.append((start_tick + TPB, 'note_off', ballad_bass[bar_idx] - 12, 0))
    events_bass.append((start_tick + 2*TPB, 'note_on', ballad_bass[bar_idx], 85))
    events_bass.append((start_tick + 3*TPB, 'note_off', ballad_bass[bar_idx], 0))
    
    # Accordion Chord Pad sustained
    for pitch in ballad_chords[bar_idx]:
        events_chords.append((start_tick, 'note_on', pitch, 75))
        events_chords.append((start_tick + 4*TPB - 10, 'note_off', pitch, 0)) # slight gap before next bar
        
    # Brush Snare (GM note 40 or 38) on beats 2 and 4
    events_perc.append((start_tick + TPB, 'note_on', 40, 70))
    events_perc.append((start_tick + TPB + 100, 'note_off', 40, 0))
    events_perc.append((start_tick + 3*TPB, 'note_on', 40, 70))
    events_perc.append((start_tick + 3*TPB + 100, 'note_off', 40, 0))


# --- BUILD SECTION (Bars 9-10, Ticks 30720 to 32640 in tempo 92 time -> wait, actually ticks 30720 to 38400) ---
# Ticks 30720 to 38400 is exactly 8 beats (2 bars of 4/4) in MIDI tick time.
# Bar 9: C Major, Bar 10: D Major
build_chords = [
    (30720, [48, 52, 55, 60]), # C Major (Bar 9)
    (30720 + BAR, [50, 54, 57, 62]) # D Major (Bar 10)
]

# Banjo roll starts in build section (16th notes: 240 ticks per note)
# Melody in Build:
# Bar 9: C5 (half), D5 (quarter), E5 (quarter)
# Bar 10: D5 (half), then silence on beats 3 & 4
build_melody = [
    # Bar 9
    (30720, 72, 2*TPB), (30720 + 2*TPB, 74, TPB), (30720 + 3*TPB, 76, TPB),
    # Bar 10
    (30720 + BAR, 74, 2*TPB)
]

for start, pitch, dur in build_melody:
    # Program change to Banjo (105) at the start of build for Lead Track
    if start == 30720:
        events_lead.append((30720 - 1, 'program_change', 105, 0)) # brief program change event
    events_lead.append((start, 'note_on', pitch, 100))
    events_lead.append((start + dur, 'note_off', pitch, 0))

# Add chords and bass for build
for start, pitches in build_chords:
    # Sustained chords
    for p in pitches:
        events_chords.append((start, 'note_on', p, 80))
        # For Bar 10, cut chords on beat 3 (silent pre-drop)
        cut_time = start + BAR - 10 if start == 30720 else start + 2*TPB - 10
        events_chords.append((cut_time, 'note_off', p, 0))
    # Bass root note
    root = pitches[0]
    events_bass.append((start, 'note_on', root - 12, 95))
    events_bass.append((cut_time, 'note_off', root - 12, 0))

# Snare build percussion crescendo!
# Bar 9 (beats 1, 2, 3, 4): quarter and eighth snare hits
snare_times_9 = [
    30720, 30720 + TPB, 30720 + 2*TPB, 30720 + 2*TPB + 480, 30720 + 3*TPB, 30720 + 3*TPB + 480
]
for idx, t in enumerate(snare_times_9):
    vel = int(60 + idx * 6)
    events_perc.append((t, 'note_on', 38, vel)) # Snare (38)
    events_perc.append((t + 120, 'note_off', 38, 0))

# Bar 10: Accelerating snare roll on beats 1 and 2, then complete silence on beats 3 and 4!
# Beats 1 & 2 are subdivided into sixteenth notes (8 hits) with crescendo!
start_10 = 30720 + BAR
for idx in range(8):
    t = start_10 + idx * 240
    vel = int(75 + idx * 4)
    events_perc.append((t, 'note_on', 38, vel))
    events_perc.append((t + 120, 'note_off', 38, 0))

# Add a long ringing Crash Cymbal (49) and reverse sweep trigger on Bar 10 Beat 3 to bleed into the drop
events_perc.append((start_10 + 2*TPB, 'note_on', 49, 110))
events_perc.append((start_10 + 4*TPB, 'note_off', 49, 0))


# --- DROP SECTION (Bars 11-18, Ticks 38400 to 69120) ---
drop_start = 38400

# Chords: G -> Em -> G -> Bm -> C -> D -> D7 -> G
drop_chords = [
    [55, 59, 62, 67], # G (Bar 11)
    [52, 55, 59, 64], # Em (Bar 12)
    [55, 59, 62, 67], # G (Bar 13)
    [47, 50, 54, 59], # Bm (Bar 14)
    [48, 52, 55, 60], # C (Bar 15)
    [50, 54, 57, 62], # D (Bar 16)
    [50, 54, 60, 62], # D7 (Bar 17)
    [55, 59, 62, 67]  # G (Bar 18)
]

drop_bass = [
    55, 52, 55, 47, 48, 50, 50, 55
]

# Drop Chorus Melody notes (Triumphant Banjo Roll/Synthesizer)
# Bar 11: D5, D5, E5, D5
# Bar 12: B4 (half), G4 (half)
# Bar 13: C5, C5, D5, C5
# Bar 14: A4 (half), F#4 (half)
# Bar 15: B4, B4, C5, B4
# Bar 16: G4 (half), E4 (half)
# Bar 17: A4 (half), B4, C5
# Bar 18: G4 (whole)
drop_melody = [
    # Bar 11
    (0, 74, TPB), (TPB, 74, TPB), (2*TPB, 76, TPB), (3*TPB, 74, TPB),
    # Bar 12
    (4*TPB, 71, 2*TPB), (6*TPB, 67, 2*TPB),
    # Bar 13
    (8*TPB, 72, TPB), (9*TPB, 72, TPB), (10*TPB, 74, TPB), (11*TPB, 72, TPB),
    # Bar 14
    (12*TPB, 69, 2*TPB), (14*TPB, 66, 2*TPB),
    # Bar 15
    (16*TPB, 71, TPB), (17*TPB, 71, TPB), (18*TPB, 72, TPB), (19*TPB, 71, TPB),
    # Bar 16
    (20*TPB, 67, 2*TPB), (22*TPB, 64, 2*TPB),
    # Bar 17
    (24*TPB, 69, 2*TPB), (26*TPB, 71, TPB), (27*TPB, 72, TPB),
    # Bar 18
    (28*TPB, 67, 4*TPB)
]

for rel_start, pitch, dur in drop_melody:
    events_lead.append((drop_start + rel_start, 'note_on', pitch, 110))
    events_lead.append((drop_start + rel_start + dur, 'note_off', pitch, 0))

# Program change Bass track to Synth Bass (80 - Synth Bass 1) at drop start
events_bass.append((drop_start - 1, 'program_change', 80, 0))
# Program change Chords track to Saw Lead/PolySynth (81 - Lead 2) at drop start
events_chords.append((drop_start - 1, 'program_change', 81, 0))

for bar_idx in range(8):
    start_tick = drop_start + bar_idx * BAR
    
    # 1. Four-on-the-floor Gated Hardstyle Kick! (Channel 10, note 36)
    for beat in range(4):
        t = start_tick + beat * TPB
        events_perc.append((t, 'note_on', 36, 120))
        events_perc.append((t + 480, 'note_off', 36, 0))
        
        # Heavy gated offbeat hi-hat (GM note 42 - Closed Hi-Hat) on offbeats
        events_perc.append((t + 480, 'note_on', 42, 90))
        events_perc.append((t + 720, 'note_off', 42, 0))

    # Heavy Crash on Beat 1 of the Drop (Bar 11)
    if bar_idx == 0:
        events_perc.append((start_tick, 'note_on', 49, 127))
        events_perc.append((start_tick + 4*TPB, 'note_off', 49, 0))

    # 2. Roaring Saw Synth Chords sustained
    for pitch in drop_chords[bar_idx]:
        events_chords.append((start_tick, 'note_on', pitch + 12, 85)) # Transposed +12 for high energy
        events_chords.append((start_tick + BAR - 10, 'note_off', pitch + 12, 0))

    # 3. Offbeat Synth Bass driving!
    # Kick triggers on beats, Synth Bass pumps on the offbeats (eighth notes)
    root = drop_bass[bar_idx] - 24 # Transposed -24 for thick, heavy sub feel
    for beat in range(4):
        # Offbeat is 480 ticks after beat start
        t_off = start_tick + beat * TPB + 480
        events_bass.append((t_off, 'note_on', root, 115))
        events_bass.append((t_off + 400, 'note_off', root, 0))


# --- CONVERT ABSOLUTE TICK EVENTS TO DELTA TIMES FOR EACH MIDO TRACK ---
def compile_mido_track(track, events):
    # Sort events by absolute tick
    # If ticks are equal, make sure note_off comes before note_on
    def event_sort_key(ev):
        # Type hierarchy: program_change < note_off < note_on
        type_weight = 0
        if ev[1] == 'program_change':
            type_weight = 0
        elif ev[1] == 'note_off':
            type_weight = 1
        else:
            type_weight = 2
        return (ev[0], type_weight)
        
    events_sorted = sorted(events, key=event_sort_key)
    
    current_tick = 0
    for tick, type, note_or_prog, vel in events_sorted:
        delta = tick - current_tick
        current_tick = tick
        if type == 'program_change':
            track.append(mido.Message('program_change', program=note_or_prog, time=delta))
        elif type == 'note_on':
            track.append(mido.Message('note_on', note=note_or_prog, velocity=vel, time=delta))
        elif type == 'note_off':
            track.append(mido.Message('note_off', note=note_or_prog, velocity=vel, time=delta))
            
    track.append(mido.MetaMessage('end_of_track', time=0))

compile_mido_track(track_lead, events_lead)
compile_mido_track(track_chords, events_chords)
compile_mido_track(track_bass, events_bass)
compile_mido_track(track_perc, events_perc)

# Save MIDI file
midi_path = "/opt/data/projects/Research/outputs/v7/authentic_het_dorp_climax_hybrid.mid"
mid.save(midi_path)
print("MIDI file compiled successfully:", midi_path)
