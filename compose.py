"""
Musicom
Music Composition Assistant
"""
import random

from constants import TwelveTET, MIDIpercussion, MIDIinstrument
from structures import MusicComposition, MusicUnit, MusicVoice
from converters import unit_to_sound, unit_to_chord, unit_to_stream
from converters import units_to_part, voices_to_parts, part_to_unit
from converters import parts_to_voices, comp_to_visual, file_to_comp, comp_to_file, comp_to_midifile, comp_to_sound

# Musical datastructures
from theory import MusicScale, Diatonic, PitchRegister
from rhythm import MusicTime
from harmony import Scale7Triad
from analysis import analyze


# Music21 modules: music notation and analysis
from music21 import stream, roman, percussion, note, chord, key, clef, harmony, serial
# MusicPy modules: computational music structures and algorithms


def compose_unit ():
    # Create a musical unit
    time = MusicTime(16, 4, 4, 120)
    reg = PitchRegister()
    unit = MusicUnit(time, reg,
                        [0, reg.index_of(TwelveTET.C,4),
                                    reg.index_of(TwelveTET.E,4)],
                        [0, 4],
                        [8, 3, 5],
                        [0, 3, 5],
                        [0, 100, 100])
    voice = MusicVoice('Compose voice', [unit], MIDIinstrument.PIANO)
    # Create a composition
    comp = MusicComposition('Composition',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                            [voice],
                            [1,4,5,1],
                            [0]
            )
    # Add several new notes in m21 stream
    unit.add_pitch(89, 2, 4, 100)
    unit.add_pitch(93, 2, 4, 100)

    triads = Scale7Triad()
    print (triads)
    # triads.pattern_major.pitch_intervals

    unit_to_chord(unit)
    unit_to_sound(unit)

    units_to_part(voice)
    voices_to_parts(comp)
    comp_to_visual(comp)




def percussion_load ():
    # Load
    comp = MusicComposition('Percussion')
    file_to_comp(comp, 'midipercussionmidi.mid')
    file_to_comp(comp, 'r_son.mid')
    comp.score.parts[0].insert(0, clef.PercussionClef())
    comp_to_visual(comp)

    # To unit
    parts_to_voices(comp)
    part_to_unit(comp.voices[0])



def create_percussion ():
    # Meter 4/4, 8 timesteps, 0,5 beat per timestep
    time = MusicTime(8, 4, 4, 100)
    reg = PitchRegister()
    unit_bass = MusicUnit (
        time, reg,
        # Onset lines
        # bass drum on beats 1 & 3), snare on 2 & 4,
        [MIDIpercussion.BASS_DRUM, MIDIpercussion.ACOUSTIC_SNARE, MIDIpercussion.BASS_DRUM, MIDIpercussion.ACOUSTIC_SNARE],
        [],
        [2, 2, 2, 2],
        [1, 1, 1, 1],
        [110, 110, 110, 110, 110, 110, 110, 110])

    unit_hihat = MusicUnit (
        time, reg,
        # hh on every eighth
        [MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT,
                         MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT],
        [],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [70, 70, 70, 70, 70, 70, 70, 70])

    voice = MusicVoice('Percussion voice', [unit_bass, unit_hihat], MIDIinstrument.PERCUSSION)


    # Create
    comp = MusicComposition('Percussion')

    pchord = percussion.PercussionChord()

    unit_to_stream(unit_bass)
    unit_to_stream(unit_hihat)

    units_to_part(voice)
    voices_to_parts(comp)

    comp_to_visual(comp)

    comp_to_midifile(comp)


class ChordSet:
    """
    Set of chords
    """
    def __init__(self, chords):
        self.chords = chords
        
        ch = chord.Chord()
        
        h = harmony.ChordSymbol('maj7', 'C')
        h.romanNumeral = roman.RomanNumeral('I', 'C')
        h.romanNumeral = roman.RomanNumeral('IV', 'A')

        self.chords.append(harmony.ChordSymbol('sus4', 'D'))
        self.chords[1].romanNumeral = 'III'
        self.chords[1].romanNumeral.key = key.Key('B')




def project_big_yellow_taxi():
    # Big Yellow Taxi

    t = TwelveTET()
    helix = PitchRegister()

    time = MusicTime(8,4,4)
    comp = MusicComposition('Big yellow taxi',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.B_FLAT, Diatonic.major_mode))


    # Create unit
    unit = MusicUnit(time,
        t.name_to_midi (name=['B3', 'C#4', 'E4', 'E4', 'F#4', 'C#4', 'E4', 'E4', 'F#4', 'E4', 'G#3', 'B3', 'B3', 'C#4',
        'E4', 'F#4', 'B3', 'B3', 'F#4', 'F#4', 'F#4', 'G#4', 'F#4', 'E4', 'E4'])
        )

    analyze(comp)
    comp_to_visual(comp)


def project_berendans():
    # Berendans
    reg = PitchRegister()
    time = MusicTime(8,4,4)
    # Create units
    unit1 = MusicUnit(time,reg)
    unit2 = MusicUnit(time,reg)
    # Create voices
    voice1 = MusicVoice('Melody voice', [unit1], MIDIinstrument.FLUTE)
    voice2 = MusicVoice('Accompaniment voice', [unit2], MIDIinstrument.PIANO)
    # Create composition
    comp = MusicComposition('Berendans',
                       MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.B_FLAT, Diatonic.major_mode),
                [voice1, voice2])

    analyze(comp)
    comp_to_visual(comp)


def create_new ():
    tt = TwelveTET()
    # New composition
    time = MusicTime(4,4,4)
    reg = PitchRegister()
    unit1a = MusicUnit(time,reg,
                      tt.name_to_midi(['C5', 'D5', 'E5', 'F5']),
                      [1,1,1,1],
                      [1, 1, 1, 1],
                      [100, 100, 100,100])
    unit1b = MusicUnit(time,reg,
                      tt.name_to_midi(['G5', 'A5', 'B4', 'C5']),
                      [1,1,1,1],
                      [1, 1, 1, 1],
                      [100, 100, 100,100])

    unit2a = MusicUnit(time,reg,
                      tt.name_to_midi(['C4', 'E4', 'G4']),
                        [1,1,2],
                        [1, 1, 1],
                        [100, 100, 100])
    unit2b = MusicUnit(time,reg,
                      tt.name_to_midi(['F4', 'A4', 'C5']),
                        [1,1,2],
                        [1, 1, 1],
                        [100, 100, 100])

    unit3 = MusicUnit(time,reg,
                      tt.name_to_midi(['C3', 'G3']),
                        [2,2],
                        [2,2],
                        [100, 100])

    # Patterns in scales
    # 3 Tria patterns:
    scale3 = MusicScale (Diatonic.TRIA, Diatonic.MAJOR)
    # 4 Tetra patterns:
    scale4 = MusicScale(Diatonic.TETRA, Diatonic.MAJOR7)
    # 5 Penta patterns:
    scale5 = MusicScale(Diatonic.PENTA, Diatonic.SCALE)


    # Create three voices for melody and accompaniment
    voice1 = MusicVoice('Voice 1', [unit1a, unit1b], MIDIinstrument.FLUTE)
    voice2 = MusicVoice('Voice 2', [unit2a, unit2b], MIDIinstrument.VIOLIN)
    voice3 = MusicVoice('Accomp', [unit3], MIDIinstrument.BASS)

    comp = MusicComposition('New',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                            [voice1, voice2, voice3],
                       [],
                       [0, 0, 1, 0])

    pitches_list = [comp.main_scale.m21scale.pitches[0:3],
                    ["G4", "A4", "B4", "C5"]]

    for v in comp.voices:
        units_to_part(v)

    # Analyze score
    analyze(comp)
    comp_to_visual(comp)
    # Save score
    comp_to_file(comp, "new.mid")


def create_balfolk ():
    tt = TwelveTET()
    # Style : Balfolk
    # Parts:  melody and bass
    reg = PitchRegister()
    # typical Balfolk rhythm
    time = MusicTime(6, 6, 8, 120)
    unit = MusicUnit(time,reg)
    # C major/A minor
    scale7aminor = MusicScale(Diatonic.HEPTA, Diatonic.SCALE, tt.A, Diatonic.minor_mode)

    melody_voice = MusicVoice()
    bass_voice = MusicVoice()
    comp = MusicComposition('Balfolk',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, tt.C, Diatonic.major_mode),
                            [melody_voice, bass_voice],
                            [1,2,3,4],
                            [0, 1, 2, 3]
                            )

    # Bourrée-inspired melody

    # Create notes with Balfolk-style rhythm
    melody_notes = [
        ['C4', 'E4', 'G4'],
        ['D4', 'F4', 'A4'],
        ['E4', 'G4', 'B4'],
        ['F4', 'A4', 'C5']
    ]
    melody_intervals = [1, 1, 1]
    melody_onsets = [1, 1, 1]
    melody_durations = [1, 1, 1]

    # Create melody with rhythmic variation
    for i in range(16):  # 4 measures
        # Choose a random melodic fragment
        fragment = random.choice(melody_notes)

        # Arpeggiate chords
        for note_name in fragment:
            n = note.Note(note_name)
            n.duration.type = 'eighth'
            melody_voice.part.append(n)

    # Create accompaniment (drone/rhythmic support)
    bass_notes = ['C3', 'G3']
    for i in range(32):  # matching melody length
        bass_note = note.Note(random.choice(bass_notes))
        bass_note.duration.type = 'eighth'
        bass_voice.part.append(bass_note)

    # Analyze score
    analyze(comp)
    comp_to_visual(comp)
    # Save score
    comp_to_file(comp, "balfolk.mid")





"""
Creation
"""

def idea_tonerow():
    # Music 21 ToneRow
    chromaticrow = serial.TwelveToneRow(TwelveTET.PITCH_CLASS_NUMBERS)
    matrixobj = chromaticrow.matrix()

    unit = MusicUnit()
    unit.pitch_nodes = chromaticrow.pitches
    unit.nodes_to_intervals()

    unit.transform (unit.PRIME, 0)


def tonerow_create(tonerow_base: serial.ToneRow = serial.ToneRow(row=[0, 4, 7, 4]),
                   octave : int = 4
                   ) -> stream.Stream:
    stream_out = stream.Stream()
    # Tonerow
    for pcs in enumerate(tonerow_base):
        pcs.octave = octave
        stream_out.append(pcs)

    return stream_out




def main():
    # Main: create or load, analyze or transform

    #comp = load_and_analyze('Sousta.mid')
    #comp.score_show()

    #create_rhythm()
    #create_new()

    #create_harmonic()

    percussion_load()
    #create_percussion()
    #create_balfolk()
    #create_counterpoint()

#    create_Population()
#    create_key_library(key.Key('C', 'major'))


if __name__ == '__main__':
    main()