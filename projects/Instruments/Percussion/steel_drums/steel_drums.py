# -*- coding: utf-8 -*-
"""Steel Drums — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth (impulse-excited
resonator bank — struck tuned membrane, sound/synthesis/modal.py). A steel
pan is a 55-gallon oil-drum lid hammered into a shallow concave bowl with
individual note 'islands' pounded into the dome; each island is a clamped
membrane with slightly INHARMONIC modes (f0, ~2.0x, ~2.7x, ~3.6x partials —
the classic pan overtone set) and a fast exponential decay. The ModalSynth
MODAL_PRESET 'marimba' (odd-harmonic struck-bar bank, decays 8-20) is the
closest stock preset; MODAL_PRESET 'bell' (inharmonic partials) is the
metallic-pan alternative; a custom struck-membrane bank (f0, 2.0x, 2.7x,
3.6x with decays 12-25) is the exact-pan patch. The Karplus-Strong
plucked-waveguide path (SP-011) is the fallback — a pan is struck, not
plucked, but the KS loop approximates the pingy metallic ring.

GM identity: GM114 "Steel Drums" is the TRINIDADIAN STEELPAN (pan) family —
lead tenor/′ping pong′ (soprano, ~D4-F6), double tenor, double second, guitar
pan, cello pan, six-bass. Chromatic melodic instrument — the lead pan plays
melody, harmony, and rhythmic strums; composition jobs may write single-note
lines AND 2-4 note chords (pan chords are idiomatic), but NOT bass lines
(bass pans are a separate low-register sub-family, and GM114's patch is
bright/small).
"""

MIDI_PROGRAM = 114
GM_NAME = "Steel Drums"
# RenderPipeline stem label: GM_PROGRAMS[114] = "Steel Drums" -> stem file
# trackXX_Steel_Drums.wav (matches exactly, no quirk; FluidR3 preset 114 =
# "Steel Drums")
STEM_LABEL = "Steel Drums"

# MIDI ranges (lead/tenor pan, sounding pitch)
RANGE_MIN = 55      # G3 — bottom of the lead-pan practical register
RANGE_MAX = 96      # C7 — top of the lead-pan register (some extend to E7=100)
SOLO_RANGE = (62, 88)   # D4–E6 — solo repertoire focus (lead pan)
SWEET_SPOT = (65, 86)   # F4–D6 — brightest, roundest tone, best projection

# Register zones
ZONES = {
    "low": (55, 64),     # G3–E4 — dark, warm, calypso bass-note/strum zone
    "mid": (65, 76),     # F4–E5 — bright round melody zone (lead pan core)
    "high": (77, 96),    # F5–C7 — pingy, cutting, fast decay (double-tenor top)
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "strike": (82, 1.0),      # standard mallet strike — full bowl ring + decay
    "roll": (70, 0.08),       # tremolo — rapid alternating mallets (sustain illusion)
    "staccato": (66, 0.18),   # short, dry, choked island
    "accent": (96, 0.9),      # hard rubber-mallet emphasis
    "muted": (48, 0.12),      # damped/choked stroke — hand on island
}

# Synthesis engine recommendation
SYNTHESIS = "modal"     # sound/synthesis/modal.py ModalSynth
MODAL_PRESET = "marimba"  # closest stock struck-bar bank; 'bell' = metallic alt
# Exact-pan custom modes: struck membrane with slightly inharmonic partials
PAN_MODES = [
    (440.0, 1.0, 12.0),    # f0 (A4 fundamental)
    (880.0, 0.55, 14.0),   # ~2.0x — octave
    (1188.0, 0.35, 17.0),  # ~2.7x — classic pan overtone (slightly flat 5th+oct)
    (1584.0, 0.20, 22.0),  # ~3.6x — bright ping
    (2200.0, 0.10, 28.0),  # ~5.0x — attack shimmer
]

# Karplus-Strong fallback (struck-bowl ring approximation)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9950,    # moderate damping -> bright metallic ping (~0.8-1.2 s);
                            #   between kalimba's metal tines (0.9940) and banjo's
                            #   head snap (0.9960): the pan bowl rings longer than
                            #   kalimba tines but shorter than a taut banjo head
    "width": 0.35,          # tight focus (narrower than banjo's 0.40)
    "role": "lead",
}

# Phase-mod alternative patch (cheap steel-drum ping)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.7,
    "mod_depth": 3.0,
    "attack": 0.001,
    "release": 0.25,
}

# Production defaults
REVERB_TAIL = 1.4       # seconds, room/plate — pan needs a bit of space, but
                        #   keep the attack ping clear (marimba 1.0 / koto 1.4)
EQ_BODY = (500, -2.0)   # peaking cut Hz, dB — tame bowl boxiness
EQ_PRESENCE = (3500, 2.5)  # peaking boost Hz, dB — pan ping + mallet clarity
EQ_AIR = (9000, 1.0)    # highshelf Hz, dB — subtle air (pans are already bright)
PAN = 0.0               # center for solo; +0.2..0.35 spread for pan ensembles


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
