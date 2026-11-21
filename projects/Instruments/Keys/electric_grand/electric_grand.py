# -*- coding: utf-8 -*-
"""Electric Grand Piano (Yamaha CP-70/CP-80) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is Karplus-Strong (plucked/struck
string waveguide — sound/synthesis/karplus_strong.py). The CP-70/CP-80 is a
REAL grand piano (full-size strings, real hammers and dampers) with NO
soundboard: each string group sits over a magnetic pickup (electric-guitar
style) wired to a preamp. The string IS the sound source, so the waveguide
model is the exact physics. The missing soundboard means the strings ring
LONGER and cleaner than a concert grand, and the pickup colours the tone
bright/glassy.

Identity: GM2 = Electric Grand Piano (the 1970s amplified grand: Yamaha
CP-70/CP-80, Kawai, Helpinstill retrofit). Fully polyphonic keyboard —
melody, harmony, and bass all at once. Distinct from GM1 acoustic (soundboard
projection), GM4 Rhodes (tine, pickup-compressed, "bark"), GM5 FM EP (no
string at all). The CP is the BRIGHTEST of the electric pianos: real string +
close magnetic pickup = glassy attack, long clean sustain, huge clear bass.
"""

MIDI_PROGRAM = 2
GM_NAME = "Electric Grand Piano"
# RenderPipeline stem label: GM_PROGRAMS[2] = "Electric Grand Piano" -> stem
# file trackXX_Electric_Grand_Piano.wav (sanitized: spaces -> underscore; no
# parens, no hyphens — matches exactly, no quirk)
STEM_LABEL = "Electric_Grand_Piano"

# MIDI ranges (CP-80: full 88-key A0-C8 = 21-108; CP-70: 73 keys E1-E7 =
# 28-100). The GM patch plays the full keyboard; we cap at the piano compass.
RANGE_MIN = 21      # A0 — bottom of the 88-key CP-80
RANGE_MAX = 108     # C8 — top of the 88-key CP-80
SOLO_RANGE = (48, 84)   # C3–C6 — primary melodic + harmonic register
SWEET_SPOT = (60, 84)   # C4–C6 — the glassy attack zone, the CP signature
                        #   ("The Logical Song" melody lives here)

# Register zones
ZONES = {
    "sub": (21, 35),     # A0–B1 — huge clear sub (pickup captures the full
                         #   string vibration, no soundboard to eat it)
    "bass": (36, 47),    # C2–B2 — left-hand bass zone, round and present
    "mid": (48, 71),     # C3–B4 — primary melody + chord body
    "high": (72, 96),    # C5–C7 — glassy bell lead, cuts without harshness
    "top": (97, 108),    # C#7–C8 — thin sparkle, accents only
}

# Articulation defaults (velocity, duration_factor).
# NOTE: the CP has MORE dynamic range than the Rhodes (no tine pickup
# compression) but less than an acoustic grand — velocity 40-120 spans a
# usable pp-ff. The attack transient is the identity: bright, metallic,
# ~3-8 ms hammer strike captured close by the pickup.
ARTICULATIONS = {
    "legato_pedal": (50, 1.0),    # soft pedal, full ring — the "water"
    "touch": (70, 1.0),           # neutral finger, chord comping
    "accent": (92, 0.95),         # mid-velocity attack
    "hard_accent": (108, 0.95),   # high velocity, preamp edge
    "staccato": (75, 0.25),       # damped short, pop chop
    "glassy": (85, 0.9),          # the CP signature: bright attack hook
    "tremolo": (60, 1.0),         # sustained (chorus/phaser era effects)
    "muted": (38, 0.20),          # felt-damped strings, delicate
    "comping_chop": (78, 0.50),   # rhythmic chord stab for pop/funk
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"   # sound/synthesis/karplus_strong.py — a plucked string
                        #   waveguide IS the physical model (real piano string
                        #   through a magnetic pickup)

# Karplus-Strong defaults. loop_gain 0.9982 — HIGH, above sitar 0.9975 and
# near harp 0.9985: the CP strings have NO soundboard damping (the soundboard
# is the main energy sink of an acoustic grand), so the ring is long and
# clean, 3-8 s. The pickup transfer (lowpass ~5.5 kHz) gives the glassy
# attack without the acoustic piano's soundboard bloom.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9982,    # long clean ring — no soundboard to damp it
    "width": 0.8,           # stereo width — piano keyboard spread
    "role": "electric_grand",  # tags for synthesis routing
    "lowpass_hz": 5500,     # magnetic pickup bandwidth — bright but bounded
    "noise_component": 0.02,  # hammer felt tick transient
}

# ModalSynth fallback — struck string = near-harmonic resonator bank.
# Piano strings are near-harmonic (1:2:3:4:5, slight stretch), NOT the
# compressed inharmonic tine of the Rhodes. Decay rates are SLOW (0.9-2.2)
# for the long soundboard-less ring.
MODAL_PRESET = "string"  # closest stock bank (harmonic stack, moderate decay)

ELECTRIC_GRAND_MODES = [
    (440.0, 1.00, 0.9),    # f0 (A4) — string fundamental
    (880.0, 0.60, 1.2),    # 2x — octave, strong (pickup loves it)
    (1320.0, 0.35, 1.5),   # 3x — twelfth
    (1760.0, 0.18, 1.8),   # 4x — double octave
    (2200.0, 0.09, 2.2),   # 5x — attack edge, fast decay
]

# PhaseModSynth (FM) alternative — bright FM piano
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.0,  # 2x — the octave partial is the CP's strongest
    "mod_depth": 2.0,       # moderate — bright but not nasal (EP2 uses 2.8
                            #   for the DX bell; the CP is a real string)
    "attack": 0.003,         # felt hammer on steel — fast but not instant
    "release": 1.2,          # string ring continues after key lifts
}

# Production defaults
REVERB_TAIL = 2.2       # seconds, stage/hall — the CP was DI + amp + room;
                        #   the long clean ring blooms in a hall (Rhodes 2.2
                        #   precedent; shorter than a pad 3.2)
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — tame cabinet/body boxiness
EQ_PRESENCE = (3500, 2.5)  # peaking boost Hz, dB — the glassy attack band,
                           #   the CP signature (vs Rhodes 2.5 kHz bark)
EQ_AIR = (8500, 1.5)    # highshelf Hz, dB — subtle air; pickup noise lives
                        #   at 6-10 kHz, don't boost too much
PAN = 0.0               # center for solo; in a stage mix slightly left


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
