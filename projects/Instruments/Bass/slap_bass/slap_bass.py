# -*- coding: utf-8 -*-
"""Slap Bass 1 (GM36) — musicom instrument constants.

GM36 = Slap Bass 1, the FUNK/DISCO slap bass voice: the thumb-slap + finger
pop technique on the electric bass guitar (Larry Graham, Bootsy Collins,
Louis Johnson, Mark King, Victor Wooten, Flea). Slap = strike the string so
it smacks the fretboard (bright percussive thump); pop = pull the string and
release so it snaps back (harmonic-rich bright click). The sound is the
rhythm-section PUNCH voice — the most percussive, mid-forward bass in the
library.

Same instrument as Electric Bass (finger) GM33 — same body/strings/pickups,
DIFFERENT performance technique: high action + aggressive right hand. GM35
Fretless is the frets-pulled electric; GM38/39 are the oscillator voices.
GM37 "Slap Bass 2" (FluidR3 "Pop Bass") is the rounder, less aggressive
sibling patch.

Reference range for the standard 4-string (E1–G4, tuned E1 A1 D2 G2):
MIDI 28–67; 5-string adds low B0 (23). The GM patch (FluidR3 preset 36)
plays 21–84 — verified by empirical sweep (REPORT.md); hard ceiling at C6
(84), silent at 86+.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 36
GM_NAME = "Slap Bass 1"
# RenderPipeline stem label: GM_PROGRAMS[36] = "Slap Bass 1" -> sanitized
# trackXX_Slap_Bass_1.wav. FluidR3 preset 36 = "Slap Bass" (SF2 drops the
# number — cosmetic only, no routing impact).
STEM_LABEL = "Slap_Bass_1"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 24       # C1 — 5-string low B0 (23) sits one semitone below;
                     #   writing floor (the patch plays 21+ but A0–B0 is
                     #   sub-bass rumble below the real 4-string instrument)
RANGE_MAX = 84       # C6 — HARD patch ceiling (empirical sweep: audible at
                     #   84, SILENT at 86 — never write above C6)
SOLO_RANGE = (36, 60)   # C2–C4 — the slap/pop pocket where both the thumb
                        #   thump and the popped harmonics speak cleanly
SWEET_SPOT = (33, 55)   # A1–G3 — the money zone: E/A/D strings where the
                        #   thumb slap lives (funk/disco/r&b groove pocket)

# Register zones
ZONES = {
    "sub": (24, 35),     # C1–E2 — open-string/pedal zone: low thumb thump,
                         #   felt more than heard, single notes only
    "slap_zone": (36, 55),  # C2–G3 — PRIMARY register: thumb slaps on
                            #   E/A/D strings, the funk 16th-note groove
    "pop_zone": (56, 72),   # G3–C5 — popped harmonics on D/G strings:
                            #   bright snap, octave pops, solo fills
    "high": (73, 84),       # C#5–C6 — thin treble, exposed fills only
                            #   (patch ceiling at 84)
}

# Articulation defaults (velocity, duration_factor)
# Slap bass vocabulary: the percussive funk lexicon — slap, pop, ghost.
ARTICULATIONS = {
    "slap": (92, 0.30),      # thumb slap — string smacks the fretboard:
                             #   bright percussive thump (THE signature)
    "pop": (96, 0.25),       # finger pop — string snapped back: harmonic-
                             #   rich bright click, usually on D/G strings
    "finger": (74, 0.90),    # normal fingerstyle pluck — connecting notes
    "ghost": (38, 0.15),     # dead-note left-hand damp — groove filler
    "hammer_on": (66, 0.60), # left-hand hammer — connected 16th run
    "pull_off": (66, 0.50),  # left-hand pull-off — descending 16th run
    "double_thumb": (98, 0.20),  # Wooten double-thumb — two slaps per stroke
    "staccato": (70, 0.25),  # tight damped pluck — dry, cutting
    "accent": (100, 0.35),   # emphatic downbeat slap — the "1" lands hard
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"    # sound/synthesis/karplus_strong.py (SP-011)
                         # A plucked string waveguide IS the physical model:
                         # the loop low-pass IS the pickup/body voicing, a
                         # SHORT loop_gain gives the tight slap ring, and a
                         # bright lowpass keeps the fretboard clack.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9955,   # SHORT, punchy ring — the slap idiom is tight:
                           #   the muting hand stops the string fast
                           #   (0.3–1.0 s), between muted_guitar 0.9850 and
                           #   electric bass 0.9970 (the slap voice is the
                           #   most damped ring in the Bass family)
    "lowpass_hz": 5500.0,  # BRIGHTER than fingerstyle electric bass
                           #   5000: the string-on-fretboard clack adds the
                           #   top-end snap that IS the slap identity
    "width": 0.4,          # moderate spread — DI bass is mono-ish; a little
                           #   width in the body tail
    "excitation": "slap",  # hard strike excitation — the thumb knuckle
    "noise_component": 0.05,  # fretboard clack / string smack — the
                              #   percussive transient is part of the voice
    "role": "bass",
}

# PhaseModSynth is the secondary (bright plucked-FM approximation; the pop
# harmonic is an FM-style sideband).
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 2.0,   # the pop's octave-ish snap partial
    "mod_depth": 2.2,        # bright but not brassy
    "attack": 0.003,         # razor pluck transient
    "release": 0.15,
}

# ModalSynth is a weak fallback only (harmonic stack, no string physics)
MODAL_PRESET = "string"

# Production defaults
REVERB_TAIL = 1.2        # seconds, tight funk room/DI — the slap voice is
                         #   injected and dry; verb smears the 16th-note
                         #   snap (synth_bass_1 1.0 / electric_bass 1.4
                         #   bracket — the slap sits at the dry end)
EQ_BODY = (250, -2.5)    # peaking cut Hz, dB — clear the 200-300 Hz
                         #   low-mid mud against the kick (the slap THUMP
                         #   itself is LOWER, ~100 Hz, keep it)
EQ_PRESENCE = (2800, 3.0)  # peaking boost Hz, dB — THE slap EQ move:
                           #   the 2-3 kHz snap/click band where the string
                           #   meets the fretboard (funk tracks live here)
EQ_AIR = (8000, 1.5)     # highshelf Hz, dB — string clack shimmer (never
                         #   low-pass a slap bass — the top IS the voice)
PAN = 0.0                # center — bass is universally mono/centered


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
