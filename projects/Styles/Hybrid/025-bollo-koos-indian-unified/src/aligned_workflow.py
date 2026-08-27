import mido
from mido import Message, MidiFile, MidiTrack

def produce_strictly_synced():
    mid = MidiFile(ticks_per_beat=480)
    
    # 4 Voices (Tracks)
    track_melody = MidiTrack()
    track_harmony = MidiTrack()
    track_rhythm = MidiTrack()
    track_drone = MidiTrack()
    mid.tracks.extend([track_melody, track_harmony, track_rhythm, track_drone])

    # Target: 64 beats * 480 = 30720 ticks
    target_ticks = 30720

    def add_note(track, pitch, start_tick, duration_tick, vel=80, channel=0):
        # Mido tracks are lists of messages with relative 'time' (delta)
        # We must keep track of current pen position
        pass

    # Better approach: calculate all messages with absolute timestamps, sort them, then convert to delta
    def build_track(events):
        # events: list of (time, message)
        events.sort(key=lambda x: x[0])
        track = MidiTrack()
        last_time = 0
        for time, msg in events:
            delta = time - last_time
            msg.time = delta
            track.append(msg)
            last_time = time
        # Force end of track
        if last_time < target_ticks:
            track.append(mido.MetaMessage('end_of_track', time=target_ticks - last_time))
        else:
            track.append(mido.MetaMessage('end_of_track', time=0))
        return track

    # 1. Melody Events
    melody_events = []
    melody_pitches = ([62, 64, 65, 62] * 4 + [60, 67, 64, 60] * 4 + 
                      [62, 63, 62, 66] * 4 + [62, 63, 65, 66] * 4)
    for i, p in enumerate(melody_pitches):
        t = i * 480
        melody_events.append((t, Message('note_on', note=p, velocity=90, time=0)))
        melody_events.append((t + 480, Message('note_off', note=p, velocity=0, time=0)))

    # 2. Harmony Events
    harmony_events = []
    chords = [([50, 53, 57], 3840), ([55, 58, 62], 3840), 
              ([48, 52, 55], 3840), ([50, 53, 57], 3840),
              ([51, 55, 58], 3840), ([50, 54, 57], 3840),
              ([46, 50, 53], 1920), ([45, 49, 52], 1920), ([50, 54, 57], 3840)]
    curr_t = 0
    for pitches, dur in chords:
        for p in pitches:
            harmony_events.append((curr_t, Message('note_on', note=p, velocity=60, time=0)))
            harmony_events.append((curr_t + dur, Message('note_off', note=p, velocity=0, time=0)))
        curr_t += dur

    # 3. Rhythm Events
    rhythm_events = []
    rhythm_pattern = [1, 0, 1, 1, 0, 1, 0, 0] * 16
    for i, strike in enumerate(rhythm_pattern):
        t = i * 240
        if strike:
            rhythm_events.append((t, Message('note_on', note=42, velocity=80, time=0, channel=9)))
            rhythm_events.append((t + 240, Message('note_off', note=42, velocity=0, time=0, channel=9)))

    # 4. Drone Events
    drone_events = [(0, Message('note_on', note=38, velocity=30, time=0)),
                    (target_ticks, Message('note_off', note=38, velocity=0, time=0))]

    # Build tracks and replace
    mid.tracks[0] = build_track(melody_events)
    mid.tracks[1] = build_track(harmony_events)
    mid.tracks[2] = build_track(rhythm_events)
    mid.tracks[3] = build_track(drone_events)

    mid.save('../MIDI/composition_expanded.mid')

if __name__ == "__main__":
    produce_strictly_synced()
