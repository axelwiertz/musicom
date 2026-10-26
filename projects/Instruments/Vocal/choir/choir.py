# -*- coding: utf-8 -*-
"""Choir (Choir Aahs) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM52 "Choir Aahs" is the **sampled mixed chorus** — a section of
many trained voices singing a wordless open "ah" vowel. It is not a solo
singer and not a synth pad: the sound IS the ensemble (dozens of detuned,
slightly desynchronised voices with staggered breaths and consonants).

Family distinction (important): `human_voice` (GM53 stand-in, formant-synth
source-filter model) is a SOLO synthetic singer; this is the choral SECTION.
`voice_like` members are non-vocal instruments that merely read as vocal.
Three different things — do not cross-register them.

Registry note: GM52 is FREE in the KB (GM53 = human_voice stand-in,
GM54 = Synth Voice, GM80/81 = talkbox / singing_saw stand-ins). No
`by_program` collision, no stem-label collision.
"""

MIDI_PROGRAM = 52
GM_NAME = "Choir Aahs"
# RenderPipeline stem label: GM_PROGRAMS[52] = "Choir Aahs" -> sanitized
# stem file trackXX_Choir_Aahs.wav.
STEM_LABEL = "Choir_Aahs"

# MIDI ranges. A real mixed choir (SATB) covers roughly E2 (bass bottom) to
# C6 (soprano top); the GM chorus patch plays wider but thins at the extremes.
RANGE_MIN = 40      # E2 — bass section bottom (below this the patch goes
                    #   muddy/organ-like, not choral)
RANGE_MAX = 88      # E6 — top of the sampled sopranos (above C6 the chorus
                    #   thins to a solo-ish "ooh" shimmer)
SOLO_RANGE = (55, 79)   # G3–G5 — a single voice-line inside the chorus range
SWEET_SPOT = (48, 76)   # C3–E5 — chord/voicing zone: full SATB body

# Register zones (choral voicing map)
ZONES = {
    "bass": (40, 55),     # E2–G3 — bass section (roots, pedal tones)
    "tenor": (48, 64),    # C3–E4 — tenor line (inner voice / melody at pitch)
    "alto": (53, 72),     # F3–C5 — alto (the "body" of the chord)
    "soprano": (60, 88),  # C4–E6 — soprano (top line, descant, climax)
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "ah": (72, 1.0),         # sustained open "ah" — the default choral gesture
    "legato": (70, 1.0),     # seamless syllable join — choral legato phrasing
    "swell": (60, 1.0),      # crescendo on a held chord (organ-like choral build)
    "staccato": (74, 0.3),   # short "ah" — rhythmic choral stabs
    "marcato": (88, 0.85),   # hard choral accent — "HAH" attack, anthem hit
    "decrescendo": (58, 1.0),# fading "ah" — phrase-end taper (very idiomatic)
    "hum": (52, 1.0),        # soft closed-mouth bed (low velocity = hummed pad)
}

# Synthesis engine recommendation
SYNTHESIS = "additive"   # sound/synthesis/additive.py SoundWave — a chorus IS
                         #   a formant-shaped harmonic stack, N detuned voices
                         #   wide; the string-ensemble recipe with vowel formants
# Formant-shaped harmonic weights for the open "ah" vowel (F1 730 / F2 1090 /
# F3 2440 Hz, Peterson & Barney 1952) — partials near the formants are boosted.
ADDITIVE_HARMONICS = {
    # "ah" chorus: strong fundamental, formant bump on partials 2–4, gentle top
    "choir_ah": [1.0, 0.72, 0.55, 0.60, 0.34, 0.22, 0.14, 0.09],
    # dark "oo"-ish hum bed: fundamental-heavy, almost no top
    "choir_hum": [1.0, 0.45, 0.22, 0.10, 0.05, 0.03],
}
SYNTHESIS_DEFAULTS = {
    "instrument": "choir",
    "attack": 0.18,       # 180 ms — a section breathes in together; slower
                          #   than a solo singer (0.05), faster than a pad (0.55)
    "detune": 0.009,      # ±0.9% — choir ensemble spread sits between the
                          #   string section (±0.6%) and the synth pad (±1.2%)
    "stack": 5,           # 5 detuned voices per note = section thickness
    "release": 0.45,      # the tail is breath + hall, not a hard cut
    "sustain_level": 0.88,
    "vowel": "a",
    "formants_hz": (730.0, 1090.0, 2440.0),
    "breath": 0.10,       # aspiration mix — the "many bodies breathing" cue
}
# Secondary: solo-voice engine stacked into a section (per-voice vibrato +
# jitter gives the human chorus; render N voices with small detune offsets).
SINGING_VOICE_DEFAULTS = {
    "voice_type": "alto",
    "vibrato_hz": 5.2,
    "vibrato_depth": 0.28,   # semitones — section vibrato is narrower than solo
    "breathiness": 0.22,
    "jitter": 0.012,
    "shimmer": 0.05,
    "stack": 4,
    "detune": 0.009,
}
# Tertiary: PhaseModSynth "vocal pad" alternative (formant-ish FM choir)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 2.0,
    "mod_depth": 1.6,
    "attack": 0.2,
    "release": 0.45,
    "sustain_level": 0.85,
}

# Production defaults
REVERB_TAIL = 2.8        # seconds — church/hall: between string_ensemble 2.6
                         #   and synth_pad 3.2; a choir is ALWAYS in a room
EQ_BODY = (350, -2.5)    # peaking cut Hz, dB — stacked "ah" formants pile up
                         #   in the low-mid (mud) fast
EQ_PRESENCE = (3000, 2.0)  # peaking boost Hz, dB — intelligibility/"presence"
                           #   band of the vowel; too much = strident
EQ_AIR = (7000, 1.0)     # highshelf Hz, dB — breath air (gentle: a choir is
                         #   not a cymbal)
PAN = 0.0                # center for the composed stem; ±0.35 for a wide
                         #   double-tracked chorus


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
