# -*- coding: utf-8 -*-
"""Vibraphone — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth (impulse-excited
resonator bank — sound/synthesis/modal.py). A vibraphone bar is a struck
aluminium alloy bar, softened by an arch ground into its underside; that arch
retunes the bar's partials from the raw free-free bar ratios
(1 : 6.27 : 17.55 : 34.39 — see sound/synthesis/music_box.py TINE_RATIOS)
to the consonant, arch-tuned set 1 : 4 : 10 (fundamental, two octaves above,
then an octave + major third above that). That is why a vibraphone reads as a
mellow pitched tone rather than a metallic clang, and why marimba (same arch
recipe, wooden bars) and vibraphone share the 1 : 4 : 10 tuning.

The vibraphone's defining difference from the marimba is DECAY, not partials:
aluminium bars ring for several seconds (resonator tubes amplify the
fundamental only, and are tuned slightly off-pitch to trade loudness for
sustain), and the instrument has a PIANO-STYLE SUSTAIN PEDAL — pedal down =
notes ring on, pedal up = felt damper stops them. The motor (fans rotating in
the resonator tube tops, 1-12 Hz) adds a tremolo amplitude modulation
(MOTOR_DEFAULTS) that is part of the instrument's signature in jazz.

The Karplus-Strong plucked-waveguide path is a fallback only (vibraphone is
struck, not plucked) and ModalSynth MODAL_PRESET 'bell' is the closest stock
bank — neither has the long arch-tuned ring; VIBRAPHONE_MODES is the exact
bank.
"""

MIDI_PROGRAM = 11
GM_NAME = "Vibraphone"
# RenderPipeline stem label: GM_PROGRAMS[11] = "Vibraphone" -> stem file
# trackXX_Vibraphone.wav (matches exactly, no quirk; FluidR3 preset 11 =
# "Vibraphone", phdr-verified)
STEM_LABEL = "Vibraphone"

# MIDI ranges (sounding pitch; non-transposing, written at concert pitch)
RANGE_MIN = 48      # C3 — 4-octave models ("C to F / C", now common); the
                    #   standard instrument starts at F3=53
RANGE_MAX = 89      # F6 — standard 3-octave top (large 4-octave models also
                    #   end on F6; a few custom instruments reach C7=96)
SOLO_RANGE = (53, 89)   # F3–F6 — the standard 3-octave instrument
SWEET_SPOT = (60, 84)   # C4–C6 — roundest, most singing register; fullest
                        #   resonator bloom and clearest pitch

# Register zones
ZONES = {
    "low": (48, 59),     # C3–B3, 4-octave model bass bars — dark, mellow,
                         #   long tube bloom
    "mid": (60, 77),     # C4–F5, principal melodic/vocal register (the
                         #   Jazz-standards and ballad zone)
    "high": (78, 89),    # F#5–F6, bright, metallic, shorter bar ring; the
                         #   clang zone (hard mallets) and bowed glass
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "strike": (82, 1.0),       # standard yarn/rattan mallet — full bar ring
    "hard_mallet": (92, 0.9),  # hard mallet — bright metallic clang, attack
    "soft_mallet": (62, 1.0),  # soft mallet — mellow ring, no obvious attack
    "motor": (78, 1.0),        # motor ON — tremolo AM on the sustained bar
    "roll": (70, 0.08),        # rapid mallet alternation (single notes only)
    "dead_stroke": (66, 0.12), # mallet pressed onto the bar — choked
    "damped": (54, 0.10),      # pedal up / hand (finger) damping — dry stop
    "bowed": (60, 1.0),        # bowed bar (double-bass bow) — glassy, no
                               #   attack, higher harmonics emphasized
    "bend": (72, 0.8),         # mallet slide nodal point -> center — lowers
                               #   pitch by about a semitone
}

# Synthesis engine recommendation
SYNTHESIS = "modal"       # sound/synthesis/modal.py ModalSynth
MODAL_PRESET = "bell"     # closest STOCK bank (inharmonic-ish partials, slow
                          #   decay) — use VIBRAPHONE_MODES for the true tone
# Exact vibraphone custom modes: arch-tuned aluminium bar, 1 : 4 : 10.
# (freq, amp, decay) — decay is a RATE (higher = faster), so these are very
# LOW: a vibraphone bar rings for seconds. Reference note A4=440; scale the
# frequencies by the played note. The fundamental dominates because the
# resonator tubes amplify the fundamental and not the upper partials.
VIBRAPHONE_MODES = [
    (440.0, 1.00, 0.30),    # f0 (A4) — the tuned pitch, long ring
    (1760.0, 0.14, 0.60),   # 4.0x — two octaves (first overtone)
    (4400.0, 0.05, 1.10),   # 10.0x — octave + major third above that, the
                            #   last of the arch-tuned partials
]

# Motor: rotating fans in the resonator tube tops (tremolo AM).
MOTOR_DEFAULTS = {
    "rate_hz": 5.0,          # classic jazz vibe speed (motor range 1-12 Hz)
    "depth": 0.35,           # amplitude-modulation depth (0-1)
    "rate_range_hz": (1.0, 12.0),  # variable-speed AC motor span
}

# Karplus-Strong fallback (struck-bar ring approximation — NOT physical:
# the vibraphone is struck, there is no string; documented as a last resort)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9975,    # very low damping -> long ring, matching the
                            #   bars' multi-second sustain (sitar-class
                            #   value; vibraphone out-rings every mallet
                            #   instrument)
    "width": 0.30,          # tight stereo focus (single resonator per bar)
    "role": "lead",
}

# Phase-mod alternative patch (cheap vibraphone)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 4.0,  # the arch-tuned 2-octave partial
    "mod_depth": 1.6,       # modest depth — the real bar is mellow, not bell
    "attack": 0.004,
    "release": 1.6,
}

# Production defaults
REVERB_TAIL = 1.8       # seconds, hall/plate — the bars' own sustain plus
                        #   a moderate room; shorter than timpani 2.2 (the
                        #   instrument is already a sustaining voice)
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — tame resonator-tube boom/mud
EQ_PRESENCE = (4000, 2.0)  # peaking boost Hz, dB — bar ping + mallet clarity
EQ_AIR = (9000, 1.5)    # highshelf Hz, dB — aluminium shimmer (only air the
                        #   bars actually produce)
PAN = 0.0               # center solo; +-0.25 spread for ensemble/comping


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
