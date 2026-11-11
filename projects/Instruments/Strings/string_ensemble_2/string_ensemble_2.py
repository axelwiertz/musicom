# -*- coding: utf-8 -*-
"""String Ensemble 2 — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM49 "String Ensemble 2" is the SLOW-ATTACK string ensemble — the
analog "string machine" (ARP Solina String Ensemble 1974, Mellotron string
tapes, Elka Rhapsody 610, Crumar Performer, Logan String Melody, Roland
RS-202): a divide-down keyboard whose every note fires 3 detuned saw
sub-oscillators through a band-limiting filter, a slow attack swell and a
chorus "ensemble" effect. FluidR3 preset 49 = "Slow Strings" — the SF2 name
is the literal character. It is the SLOW sibling of String Ensemble 1 GM48
(orchestral bowed section, fast attack): same ensemble-pad family, machine
timbre, slow swell, no bow.

Synthesis note: primary is the dedicated string-machine engine
`sound/synthesis/string_ensemble.py` `StringEnsembleVoice` (detuned saw
sub-osc stack at 8'/4'/2' + Streichfett-style 3-tap ensemble chorus — the
exact divide-down model). Secondary is Polysynth (polyBLEP saw stack through
a band-limiting low-pass — the classic subtractive string machine).
Additive is the tertiary pad fallback (detuned harmonic stack with slow
swell — the pad-family precedent); PhaseModSynth is the cheap FM alt.

Enum note: `structures/instrument.py` `MidiInstrument.STRING_ENSEMBLE = 49`
— the legacy enum's string-ensemble constant happens to equal GM49 (the
Slow Strings patch), unlike the GM48-vs-49 mismatch the name implies. Use
the registry (`by_name('string ensemble 2')` / `by_program(49)`) — the
registry is the full KB.
"""

MIDI_PROGRAM = 49
GM_NAME = "String Ensemble 2"
# RenderPipeline stem label: GM_PROGRAMS[49] = "String Ensemble 2" -> stem
# file trackXX_String_Ensemble_2.wav (matches exactly, no quirk; FluidR3
# preset 49 = "Slow Strings" — SF2 uses the character name, cosmetic only)
STEM_LABEL = "String_Ensemble_2"

# MIDI ranges (sounding pitch; empirical FluidR3 sweep: preset 49 audible
# 12–96 (9/9 notes, essentially flat 0.09–0.18 RMS), SILENT at 108+ —
# full-keyboard patch, never clips a composition; C1 floor matches the
# string_ensemble sibling convention, real Solina starts at C2=36)
RANGE_MIN = 28      # C1 — patch floor (real 49-key Solina starts C2=36;
                    #   below C2 the divide-down is rumble, not music)
RANGE_MAX = 96      # C7 — patch ceiling (empirical: SILENT at 108+)
SOLO_RANGE = (53, 89)   # F3–A6 — solo-pad focus (mid body + first air)
SWEET_SPOT = (60, 84)   # C4–C6 — chord-pad zone: fullest ensemble glow

# Register zones
ZONES = {
    "low": (28, 47),     # C1–B2, divide-down rumble — roots, drone bottom
                         #   (write sparingly: the machine's low is mud)
    "mid": (48, 71),     # C3–B4, primary chord-pad body — the workhorse band
    "high": (72, 96),    # C5–C7, ensemble top — melody/countermelody,
                         #   cutting but warm (NOT the new-age shimmer)
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (72, 1.0),   # slow-swelling pad — the default gesture
    "legato": (70, 1.0),    # seamless voice crossfade — chord changes
    "swell": (82, 1.0),     # crescendo swell — whole-bar build (ballad trick)
    "staccato": (66, 0.25), # short pad "blip" — rhythmic filter-pulse motif
    "marcato": (85, 0.85),  # attack override — plucked onset (machine has
                            #   no pluck; use for rhythmic accents only)
    "drone": (62, 1.0),     # static sustained harmony — ambient bed
    "accent": (88, 0.9),    # hard entrance — downbeat hit, then bloom
    "bloom": (68, 1.25),    # extra-long swell — the slow-strings signature
                            #   "bloom" tail (holds past the bar, feeds verb)
}

# Synthesis engine recommendation
SYNTHESIS = "string_ensemble"  # sound/synthesis/string_ensemble.py
                                # StringEnsembleVoice — the dedicated
                                # divide-down string-machine model
STRING_ENSEMBLE_DEFAULTS = {
    "instrument": "string_ensemble_2",
    "n_voices": 3,               # 3 detuned saw sub-oscillators per note
                                 #   (Solina divide-down: 3 VCO sources)
    "octave_mix": (0.6, 0.35, 0.15),  # 8' / 4' / 2' gains — the classic
                                 #   octave-stack blend (8' dominant)
    "detune_cents": 8.0,         # WIDE ensemble drift (Solina chorus
                                 #   spread; warm_pad uses ±7c on saws)
    "drift_rate": 0.4,           # slow random-walk drift (ensemble "swell")
    "attack_s": 0.8,             # SLOW attack — the patch's literal name;
                                 #   the swell IS the identity
    "release_s": 1.5,            # long release — the machine blooms into
                                 #   the reverb after key-up
    "layer_mix": 0.2,            # mostly saw core, subtle wavetable sheen
    "flavour": 0.35,             # per-note pitch/phase jitter (Flavour)
}
# Classic subtractive string machine (secondary): saw stack + low-pass
POLYSYNTH_DEFAULTS = {
    "osc1_waveform": "saw",      # the string machine IS saws (vs warm_pad's
                                 #   triangle core — the machine is brighter)
    "osc2_waveform": "saw",
    "osc2_detune_cents": 8.0,
    "osc3_waveform": "saw",
    "osc3_detune_cents": -8.0,
    "osc3_level": 0.8,
    "filter_cutoff": 2200.0,     # band-limiting — divide-down machines are
                                 #   NOT bright (between warm_pad 1400 and
                                 #   synth_brass_1 2800)
    "filter_resonance": 0.3,     # gentle peak — body, not squelch
    "env_attack": 0.8,           # slow swell (the slow-strings onset)
    "env_decay": 0.3,
    "env_sustain": 0.85,
    "env_release": 0.8,
    "unison_voices": 3,          # 3 detuned voices = the chorus blur
}
# Additive pad fallback (tertiary): detuned harmonic stack, slow swell
ADDITIVE_HARMONICS = {
    # Saw-ish dense stack — brighter than warm_pad's 0.78/0.58/0.40 rolloff,
    # darker than string_ensemble's section_full (machine ≠ bowed section).
    # Weights are RELATIVE; normalize to sum 1.0 before apply_overtones().
    "slow_strings": [1.0, 0.85, 0.62, 0.42, 0.28, 0.18, 0.11],
}
SYNTHESIS_DEFAULTS = {
    "instrument": "string_ensemble_2",
    "attack": 0.8,       # slow swell — the identity
    "detune": 0.010,     # ±1.0% per voice — ensemble chorus
    "stack": 3,          # 3 detuned voices per note
    "release": 0.8,
    "sustain_level": 0.9,
    "decay_S": 1e-4,     # the 2026-10-12 additive quirk: pad recipes MUST
                         #   use decay_S ~1e-4 to hold a long chord
}
# PhaseModSynth alt — the cheap FM string machine (string_ensemble FM recipe)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.8,
    "attack": 0.5,
    "release": 0.6,
    "sustain_level": 0.85,
}

# Production defaults
REVERB_TAIL = 2.8       # seconds — between string_ensemble 2.6 and warm_pad
                        #   3.0: the machine blooms in a hall but keeps more
                        #   body than the new-age shimmer
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — the saw stack + octave mix
                        #   piles the low-mid FAST (300 like the pads; the
                        #   divide-down rumble lives 200–400 Hz)
EQ_PRESENCE = (2800, 2.0)  # peaking boost Hz, dB — ensemble clarity /
                           #   chorus edge band (the machine speaks in the
                           #   upper-mid, not the 3.8k new-age shimmer)
EQ_AIR = (8000, 1.5)    # highshelf Hz, dB — GENTLE top air (chorus sheen,
                        #   NOT the new-age 9.5k sparkle)
PAN = 0.0               # center for the composed stem; ±0.4 L/R spread on
                        #   wide stereo swells (the ensemble chorus widens
                        #   in production)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
