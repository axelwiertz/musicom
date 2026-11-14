# -*- coding: utf-8 -*-
"""Electric Bass (pick) — musicom instrument constants.

GM34 = Electric Bass (pick). The PLECTRUM voice of the same solidbody electric
bass as GM33 (Electric Bass (finger)) — one instrument, a different right-hand
tool. A hard plastic/nylon pick strikes the string at a sharper angle with a
stiffer contact than a fingertip: the attack is a bright broadband CLICK
(measured spectral centroid +34% to +88% vs the fingered patch), the
fundamental is leaner, the note-to-note dynamics are more even, and palm
muting becomes a first-class articulation (the heel of the hand rests on the
bridge saddles). The definitive rock/punk/metal/new-wave bass attack — Chris
Squire (Yes), Paul McCartney (post-1966), Dee Dee Ramone, Mike Dirnt,
Peter Hook (the melodic pick-bass hook), Justin Chancellor, Lemmy.

Reference range for the standard 4-string (E1–G4, 20/22 frets): MIDI 28–67.
The GM patch (FluidR3 preset 34 "Picked Bass") is measured audible from
21 (A0) to 84 (C6) and SILENT from 87 up — the empirical ceiling.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 34
GM_NAME = "Electric Bass (pick)"
# RenderPipeline stem label: GM_PROGRAMS[34] = "Electric Bass (pick)"
# -> trackXX_Electric_Bass_pick.wav (parens stripped, inner word kept;
#    same convention as GM33 -> Electric_Bass_finger — no quirk)
STEM_LABEL = "Electric_Bass_pick"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 21       # A0 — empirical FluidR3 floor (sweep: 21 audible, RMS flat)
RANGE_MAX = 84       # C6 — empirical ceiling: patch SILENT from 87 up
SOLO_RANGE = (36, 57)   # C2–A3 — melodic pick-bass lines (Peter Hook hooks,
                        #   Chris Squire counterlines) cut clearly here
SWEET_SPOT = (40, 55)   # E2–G3 — the groove pocket: root-fifth eighths,
                        #   driving 16ths, palm-muted chugs

# Register zones
ZONES = {
    "sub": (21, 35),      # A0–B1 — sub-bass fundamental: felt > heard,
                          #   single notes only (muddy on small systems)
    "groove": (36, 50),   # C2–D3 — PRIMARY register: pick 8ths/16ths,
                          #   root-fifth pocket, palm-mute chug band
    "mid": (51, 64),      # D#3–E4 — melodic fills, pick-bass hooks, the
                          #   D/G-string cut-through zone
    "high": (65, 84),     # F4–C6 — thin aggressive treble: accents and
                          #   exposed fills only (patch ceiling at 84)
}

# Articulation defaults (velocity, duration_factor)
# Pick bass articulations are right-hand plectrum gestures + the palm mute.
ARTICULATIONS = {
    "pick": (84, 0.90),        # default plectrum stroke — bright click,
                               #   even dynamics, slightly shorter than finger
    "alt_pick": (80, 0.85),    # strict alternate picking — the driving
                               #   16th-note engine of rock/punk bass
    "downstroke": (92, 0.80),  # down-only aggressive stroke — punk/metal
                               #   weight on every beat
    "palm_mute": (48, 0.25),   # heel of hand on the saddles — choked "chug",
                               #   no sustain, pitch implied not sung
    "staccato": (86, 0.30),    # tight gated pick note — funk/rock stabs
    "ghost": (36, 0.18),       # muted filler tick between accented notes
    "slide": (64, 1.05),       # pick attack + fretboard slide — audible
                               #   fretwire zip into the target note
    "accent": (96, 0.75),      # hard downstroke dig — downbeat emphasis,
                               #   the pick's widest dynamic margin
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"     # sound/synthesis/karplus_strong.py (SP-011)
                          # Plucked waveguide is the exact physical model of
                          # the string; the PICK is modelled by the excitation
                          # (stiffer, brighter burst) + a higher loop low-pass.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9965,      # slightly SHORTER ring than fingerstyle 0.9970:
                              #   the pick's sharper excitation dumps energy
                              #   faster into the upper partials, and pick
                              #   players palm-rest more; still longer than
                              #   slap 0.9955 (the most damped Bass ring)
    "lowpass_hz": 5600.0,     # BRIGHTER than fingerstyle 5000: the pick click
                              #   and roundwound top-end ARE the identity
                              #   (measured centroid +34–88% vs GM33)
    "width": 0.5,             # narrower than finger 0.6 — DI pick bass is
                              #   mixed mono; width only in the harmonic tail
    "excitation": "pick",     # stiff plectrum burst (brighter than "pluck")
    "role": "bass",
}

# ModalSynth 'string' is the fallback bank (harmonic stack, no pickup colour).
MODAL_PRESET = "string"

# Phase-mod alternative (cheap pick-bass emulation, not recommended)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 1.0,    # pick click sits IN the harmonic series, not
                              #   sub-octave like the finger patch's 0.5
    "mod_depth": 2.4,
    "attack": 0.003,           # 3 ms plectrum transient (faster than finger
                              #   0.005 — the pick is the sharper onset)
    "release": 0.20,           # tighter than finger 0.25 — pick bass is dry
}

# Production defaults
REVERB_TAIL = 1.2        # seconds, small room — DRIER than finger 1.4:
                          #   pick bass is tracked DI/amp close-mic and the
                          #   click needs to stay upfront; verb is a mix
                          #   choice, never baked in
EQ_BODY = (200, -2.5)    # peaking cut Hz, dB — remove the low-mid box
                          #   resonance; the pick leaves less 250 Hz bloom
                          #   than fingers, so a slightly deeper, lower cut
EQ_PRESENCE = (1200, 3.0)  # peaking boost Hz, dB — the pick CLICK band
                          #   (higher and stronger than the finger growl at
                          #   800 Hz); this is what makes the bass cut
EQ_AIR = (6000, 2.0)     # highshelf Hz, dB — plectrum scrape + roundwound
                          #   sizzle, above the finger patch's 5 kHz shelf
PAN = 0.0                # center — bass is mixed mono in every idiom


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
