# -*- coding: utf-8 -*-
"""Electric Bass (finger) — musicom instrument constants.

GM33 = Electric Bass (finger-style). The foundational bass voice in modern
popular music — plucked magnetic-pickup solidbody, fingerstyle attack, warm
round tone with a punchy midrange transient. Monophonic line instrument
(one note at a time; occasional double-stops on adjacent strings in the
groove register).

Reference range for the standard 4-string (E1–G4, 20 or 22 frets): MIDI 28–67.
The GM patch (FluidR3 preset 33) spans wider, 24–84 (C1–C5).

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 33
GM_NAME = "Electric Bass (finger)"
# RenderPipeline stem label: GM_PROGRAMS[33] = "Electric Bass (finger)"
# -> trackXX_Electric_Bass_finger.wav (labels match exactly, no quirk)
STEM_LABEL = "Electric_Bass_finger"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 24       # C1 — extended-range basses / GM patch floor
RANGE_MAX = 84       # C5 — 24-fret D-string harmonic / GM patch ceiling
SOLO_RANGE = (31, 55)   # G1–G3 — melodic bass lines, pocket where notes
                         #   speak clearly without mud
SWEET_SPOT = (40, 65)   # E2–F4 — the groove pocket: root-fifth fills,
                         #   walking lines, fingerstyle attack

# Register zones
ZONES = {
    "contrabass": (24, 35),   # C1–E2 — sub-bass fundamental zone: chest
                              #   thump, felt more than heard, single notes
                              #   only (muddy below ~40 Hz on small systems)
    "groove": (36, 50),       # E2–D3 — primary rhythm register: root-fifth
                              #   pocket, walking bass, finger/pick attack
    "mid": (51, 65),          # D#3–F4 — melodic fills, fretboard centre,
                              #   singing tone, ghost-note slaps
    "high": (66, 84),         # F#4–C5 — tenor register: bright, thin,
                              #   aggressive; slap/pop territory, solos
}

# Articulation defaults (velocity, duration_factor)
# Electric bass articulations map to fingerstyle, pick, and extended techniques
ARTICULATIONS = {
    "finger": (72, 1.0),       # fingertip pluck — warm round tone, the default
    "pick": (86, 0.85),        # plectrum — bright, aggressive attack, thinner
                               #   sustain (Vox Continental / Jamerson's P-bass)
    "slap": (94, 0.35),        # thumb slap — percussive thwack, short sustain
    "pop": (100, 0.25),        # finger pop/snap — bright harmonic click, fastest
                               #   decay in the set (Larry Graham / Flea)
    "muted": (42, 0.20),       # palm mute / ghost note — choked string, no pitch
    "legato": (68, 0.85),      # hammer-on / pull-off — smooth connected line
    "slide": (62, 1.10),       # glissando / fret slide — finger drag across
                               #   string, audible fretwire
    "accent": (90, 0.80),      # emphatic finger pluck or pick dig
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"     # sound/synthesis/karplus_strong.py (SP-011)
                          # Electric bass is a plucked stiff wire string with
                          # magnetic pickup — Karplus-Strong waveguide is the
                          # exact physical model for the string vibration,
                          # simpler than a full physical-modelling synth.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9970,      # moderate damping: bass strings are wound
                              # steel (stiffer than nylon/gut), shorter
                              # sustain than harp 0.9985; between sitar
                              # 0.9975 and shamisen 0.9955
    "width": 0.6,             # moderate stereo spread — DI bass is mono;
                              # 0.6 gives subtle ambience in the string
                              # harmonic tail
    "role": "bass",
}

# Karplus-Strong is the ONLY strong recommendation. ModalSynth 'string'
# is a weak fallback (harmonic stack, no magnetic-pickup colour).
MODAL_PRESET = "string"

# Phase-mod alternative (cheap bass emulation, not recommended)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 0.5,    # sub-octave fold gives the fundamental fatness
    "mod_depth": 2.0,
    "attack": 0.005,           # fast attack for the pick/finger transient
    "release": 0.25,           # short release — electric bass is tighter than
                               #   upright
}

# Production defaults
REVERB_TAIL = 1.4        # seconds, room — electric bass is typically dry
                          # (DI / amp close-mic); verb is a mix choice, not
                          # baked into the sound; 1.4 s room is for
                          # exposed solo passages
EQ_BODY = (250, -3.0)    # peaking cut Hz, dB — reduce mud at the 200-300 Hz
                          # box resonance (typical P-Bass / Jazz-Bass
                          # mid-bump)
EQ_PRESENCE = (800, 2.5) # peaking boost Hz, dB — finger attack and fret
                          # noise presence (the "growl" band)
EQ_AIR = (5000, 1.5)     # highshelf Hz, dB — string noise / pick click /
                          # roundwound harmonic shimmer
PAN = 0.0                # center — electric bass is almost universally
                          # mono/centered in a mix


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)