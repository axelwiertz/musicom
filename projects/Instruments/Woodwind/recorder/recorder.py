# -*- coding: utf-8 -*-
"""Recorder — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM74 Recorder — the Renaissance/Baroque duct flute (fipple
flute), the most prominent end-blown flute in the Western classical
tradition before the transverse flute supplanted it in the 18th c. The
GM patch is modelled on the soprano/descant recorder in C.
"""

MIDI_PROGRAM = 74
GM_NAME = "Recorder"
# RenderPipeline stem label: GM_PROGRAMS[74] = "Recorder" -> stem file
# trackXX_Recorder.wav (matches exactly; FluidR3 preset 74 = "Recorder")
STEM_LABEL = "Recorder"

# MIDI ranges (sounding pitch; standard soprano recorder compass)
# Soprano recorder: C5 (72) – D7 (98, extended via overblowing G7=103).
# Alto recorder: F4 (65) – G6 (91). The GM patch spans the full chromatic
# across both instrument sizes.
RANGE_MIN = 60       # C4 — GM patch responds below the real soprano bottom
RANGE_MAX = 100      # E7 — GM patch limit (above real soprano D7=98)
SOLO_RANGE = (72, 89)   # C5–C7 — the two-octave soprano compass
SWEET_SPOT = (76, 84)   # E5–C6 — the pure, sweet singing register

# Register zones
ZONES = {
    "low": (60, 74),     # C4–D5, breathy/soft/hollow, the bottom fourth
    "mid": (75, 84),     # D#5–C6, sweet/clear/liquid — the classic recorder voice
    "high": (85, 93),    # C#6–D7, bright/piercing, sharp articulation
    "altissimo": (94, 100),  # D#7–E7, thin/shrill, extreme overblown register
}

# Articulation defaults (velocity, duration_factor)
# The recorder's key strength is its extreme articulation variety — the
# instrument is famously flexible with single/double/triple/ flutter
# tonguing, all clearly audible because the fipple edge gives instant
# attack.
ARTICULATIONS = {
    "legato": (68, 1.0),       # smooth slurred notes, minimal tonguing
    "staccato": (62, 0.2),     # crisp single-tongue (tu-tu-tu), dry
    "accent": (92, 0.85),      # sharp sforzando tongue attack
    "double_tongue": (72, 0.07), # rapid tu-ku-tu-ku, Baroque fast passage
    "triple_tongue": (72, 0.06), # tu-tu-ku pattern, Vivaldi-style
    "flutter": (65, 1.0),      # guttural rolled-R flutter tongue
    "breath": (50, 0.85),      # very soft breathy pianissimo
    "trill": (70, 0.5),        # rapid finger trill on adjacent holes
}

# Synthesis engine recommendation
# The recorder is the definitive fipple flute (duct flute). The best
# physical model is AirPipe (stopped=False, open pipe with fipple
# excitation). PhaseModSynth produces the pure near-sine tone; Additive
# handles the odd-harmonic emphasis.
SYNTHESIS = "phase_mod"    # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,  # fundamental+mod at same pitch — pure fipple
    "mod_depth": 1.5,       # moderate — cleaner than flute 1.2, less than
                            #   ocarina 0.8; the fipple produces a purer
                            #   tone than the transverse flute's embouchure
    "attack": 0.03,         # fast — the fipple speaks instantly
    "release": 0.08,
}

# AirPipe physical aerophone model (fipple flute = duct flute)
AIR_PIPE_DEFAULTS = {
    "pressure": 0.60,        # moderate wind pressure
    "stopped": False,        # open pipe (all recorders are open at the foot)
    "length_scale": 0.45,    # soprano recorder ~33 cm, between piccolo 0.5
                             #   and concert flute 1.0
}

# Additive alternative — odd-harmonic-dominant fipple tone
ADDITIVE_DEFAULTS = {
    "partials": [(1.0, 1.00), (3.0, 0.40), (5.0, 0.22), (7.0, 0.10)],
    "attack": 0.02,          # near-instant fipple response
    "release": 0.06,
}

# Production defaults
REVERB_TAIL = 1.6        # seconds — intimate chamber/room for the
                         #   intimate Baroque sound; NOT cathedral
                         #   (the pure tone benefits from close clarity)
EQ_BODY = (600, -1.5)   # peaking cut Hz, dB — reduce slight duct/body resonance
EQ_PRESENCE = (3000, 2.5)  # peaking boost Hz, dB — articulation clarity
EQ_AIR = (9000, 1.5)    # highshelf Hz, dB — subtle fipple breath shimmer
PAN = -0.1              # slightly left (orchestral woodwind seating;
                        #   Baroque ensemble: centre)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)