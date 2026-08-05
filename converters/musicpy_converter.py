"""MusicPy converters."""
from structures import MusicPitchClass, MusicPitchClassSet, PatternType
from structures import MidiInstrument, MusicLinearTime
from structures import MusicUnit, MusicEvent
from sound.utils.pitch import midi_to_name
from musicpy import musicpy, structures


def pattern_to_mpscale(pattern: MusicPitchClassSet) -> structures.scale:
    mpscale = structures.scale()

    # Diatonic (7 pitch class) scale
    if pattern.definition == PatternType.HEPTATONIC:
        # MusicPy structures
        mpscale = structures.scale(MusicPitchClass.NAMES_SHARP[pattern.initial],
                                   interval=pattern.rotation_name)

    return mpscale

# Print converters
def track_to_print(track: structures.track):
    print('Name     : ' + str(track.track_name))
    print('Notes    : ' + str(track.content.notes))
    print('Duration : ' + str(track.content.duration))
    print('Interval : ' + str(track.content.interval))


def modulate_unit(unit: MusicUnit,
                  scale_source: structures.scale,
                  scale_target: structures.scale):
    # Modulate
    unit.pitch_nodes = unit_to_chord(unit).modulation(scale_source, scale_target).pitches


def unit_to_sound(unit: MusicUnit, time: MusicLinearTime, midi_instrument: int = MidiInstrument.PIANO):
    musicpy.play(unit_to_chord(unit), bpm=time.bpm, instrument=midi_instrument, wait=True)

# Unit converters
def unit_to_chord(unit: MusicUnit) -> structures.chord:
    chord = structures.chord([])
    for event in unit.events:
        note = structures.note(name=midi_to_name(event.pitch),
                               duration=event.duration,
                               volume=event.volume)
        chord.notes.append(note, event)
    return chord

def unit_to_track(unit: MusicUnit, track_name: str = 'Track') -> structures.track:
    chord = unit_to_chord(unit)
    track = structures.track(content=chord, track_name=track_name)
    return track

def chord_to_unit(chord: structures.chord) -> MusicUnit:
    unit = MusicUnit()

    pitches = [note.number for note in chord.notes]
    volumes = [note.volume for note in chord.notes]
    durations = [note.duration for note in chord.notes]
    for i in range(len(pitches)):
        start_tick = sum(chord.interval[:i]) if i < len(chord.interval) else 0
        end_tick = start_tick + durations[i] if i < len(durations) else start_tick
        event = MusicEvent(
            pitch=pitches[i],
            volume=volumes[i] if i < len(volumes) else 100,
            start_tick=start_tick,
            end_tick=end_tick
        )
        unit.add_event(event)

    return unit


def piece_play(piece: structures.piece):
    # Play piece and wait until finish, writes temp.midi
    musicpy.play(piece, wait=True)
