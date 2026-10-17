# -*- coding: utf-8 -*-
"""Electric Piano 2 (DX7 FM Piano) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM5 = Electric Piano 2 (Yamaha DX7 FM electric piano, usually
the iconic DX7 "E. Piano 1" preset — the bright percussive bell-like FM
electric piano that defined the 1980s). A fully polyphonic keyboard —
melody, harmony, and bass all at once.
"""

MIDI_PROGRAM = 5
GM_NAME = "Electric Piano 2"
# RenderPipeline stem label: GM_PROGRAMS[5] = "Electric Piano 2" -> stem file
# trackXX_Electric_Piano_2.wav (matches exactly, no quirk; FluidR3 preset 5 =
# "Electric Piano 2")
STEM_LABEL = "Electric_Piano_2"

# MIDI ranges (standard 88-key piano: A0-C8 = 21-108; DX7 is 61-key)
RANGE_MIN = 36      # E1 — practical low-end
RANGE_MAX = 96      # C7 — GM patch span
SOLO_RANGE = (48, 84)   # C3-C6 — primary melodic + harmonic register
SWEET_SPOT = (53, 79)   # F3-G5 — the bright bell zone

# Register zones
ZONES = {
    "low": (36, 47),     # E1-B2 — dark, thuddy fundamental
    "mid_low": (48, 59),  # C3-B3 — warm, chord comping
    "mid": (60, 79),      # C4-G5 — bright bell register, the DX7 signature
    "high": (80, 96),     # G#5-C7 — thin tinkly top, metallic sheen
}

# Articulation defaults (velocity, duration_factor).
# The DX7 FM piano has a very bright percussive attack that cuts through a mix.
# Unlike the Rhodes (GM4), the DX7's dynamic range is wider and the attack
# is more aggressive.
ARTICULATIONS = {
    "legato_pedal": (45, 1.0),       # soft pedal, full ring — mellow
    "touch": (65, 1.0),              # neutral finger, chord comping
    "accent": (88, 0.95),            # mid-velocity bell attack
    "hard_accent": (105, 0.95),      # high velocity, metallic clang
    "staccato": (70, 0.20),          # damped short, pop/funk chop
    "bell": (95, 0.9),               # the iconic DX7 bell strike
    "tremolo": (55, 1.0),            # sustained with amp tremolo
    "comping_chop": (75, 0.45),      # rhythmic chord stab for pop/funk
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"   # sound/synthesis/phase_mod.py — PhaseModSynth
                          # The DX7 IS an FM (phase modulation) synth — this
                          # is the exact physical synthesis model.

# PhaseModSynth (FM) primary — the DX7 FM algorithm 1 or the iconic
# "E. Piano 1" voice uses two sine operators in a carrier+modulator stack,
# with a bright bell-like ratio and moderate depth.
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 3.1,   # 3.1x — the classic DX7 bell (3x gives a
                              #   crystal-like upper harmonic, slightly
                              #   detuned for the FM piano signature)
    "mod_depth": 2.8,         # moderate-high — FM piano needs enough depth
                              #   for the bell "clang" without going nasal
    "attack": 0.003,          # near-instant — FM operator attack (DX7
                              #   operator EG rate 1 ~80)
    "release": 1.2,           # moderate — the FM decay is faster than a
                              #   Rhodes tine (~2-3 s total)
}

# Karplus-Strong alternative: the DX7 bell is a percussive struck metallic
# sound — waveguide model with moderate loop gain for the bright ring.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9960,     # between clavi (short) and rhodes (long)
    "width": 0.6,             # stereo width
    "role": "epiano2",        # tags for synthesis routing
    "lowpass_hz": 4000,       # FM piano has more high content than Rhodes
    "noise_component": 0.01,  # minimal — FM synthesis is clean, no hammer
}

# ModalSynth fallback — the DX7 bell approximates an inharmonic metal-bar
# modal bank (crystal-like glassy partials, fast decay)
MODAL_PRESET = "bell"

# Production defaults
REVERB_TAIL = 2.0       # seconds, hall — the 80s DX7 was drenched in
                        #   Lexicon hall reverb; the "shimmer" IS the reverb.
                        #   shorter tail (1.2-1.5 s) for pop comping
EQ_BODY = (400, -2.0)   # peaking cut Hz, dB — reduce low-mid mud
EQ_PRESENCE = (3200, 3.0)  # peaking boost Hz, dB — the bright bell/tine
                            #   articulation; DX7 cuts through a mix
EQ_AIR = (9000, 2.0)    # highshelf Hz, dB — shimmer air; FM has sparkly
                        #   upper harmonics
PAN = 0.0               # center for solo; stereo spread for sections


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)